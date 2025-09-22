"""Floyd-Steinberg dithering for Spectra E6 e-ink display with text preservation."""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, List, Optional
import logging

logger = logging.getLogger(__name__)


class SpectraE6Dithering:
    """Floyd-Steinberg dithering for Spectra E6 6-color e-ink display with text preservation."""

    # Spectra E6 color palette
    E6_PALETTE = {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'red': (255, 0, 0),
        'yellow': (255, 255, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
    }

    # Convert palette to numpy array for faster processing
    PALETTE_ARRAY = np.array(list(E6_PALETTE.values()), dtype=np.float32)
    PALETTE_NAMES = list(E6_PALETTE.keys())

    # Thresholds for preserving black and white
    BLACK_THRESHOLD = 30   # Pixels darker than this are kept as pure black
    WHITE_THRESHOLD = 225  # Pixels brighter than this are kept as pure white

    def __init__(self, preserve_bw: bool = True, bw_tolerance: float = 10.0):
        """Initialize the dithering processor.

        Args:
            preserve_bw: Whether to preserve black and white pixels without dithering
            bw_tolerance: Tolerance for exact color matching (0 = exact match only)
        """
        self.palette_rgb = self.PALETTE_ARRAY.copy()
        self.preserve_bw = preserve_bw
        self.bw_tolerance = bw_tolerance

    def is_exact_palette_match(self, pixel: np.ndarray, tolerance: float = 0.0) -> Tuple[bool, Optional[int], Optional[np.ndarray]]:
        """Check if a pixel exactly matches a palette color.

        Args:
            pixel: RGB pixel values
            tolerance: Allowed deviation from exact match

        Returns:
            Tuple of (is_match, palette_index, palette_color) or (False, None, None)
        """
        for idx, palette_color in enumerate(self.palette_rgb):
            distance = np.sqrt(np.sum((palette_color - pixel) ** 2))
            if distance <= tolerance:
                return True, idx, palette_color
        return False, None, None

    def should_preserve_pixel(self, pixel: np.ndarray) -> Tuple[bool, Optional[np.ndarray]]:
        """Check if a pixel should be preserved without dithering.

        Args:
            pixel: RGB pixel values

        Returns:
            Tuple of (should_preserve, target_color) or (False, None)
        """
        if not self.preserve_bw:
            return False, None

        # Check if it's near black
        if np.all(pixel <= self.BLACK_THRESHOLD):
            return True, np.array([0, 0, 0], dtype=np.float32)

        # Check if it's near white
        if np.all(pixel >= self.WHITE_THRESHOLD):
            return True, np.array([255, 255, 255], dtype=np.float32)

        # Check for exact palette matches (with tolerance)
        is_match, _, color = self.is_exact_palette_match(pixel, self.bw_tolerance)
        if is_match:
            return True, color

        return False, None

    @staticmethod
    def find_nearest_palette_color(pixel: np.ndarray, palette: np.ndarray) -> Tuple[int, np.ndarray]:
        """Find the nearest color in the palette using Euclidean distance.

        Args:
            pixel: RGB pixel values
            palette: Array of palette colors

        Returns:
            Tuple of (palette index, palette RGB values)
        """
        # Calculate Euclidean distance to each palette color
        distances = np.sqrt(np.sum((palette - pixel) ** 2, axis=1))
        nearest_idx = np.argmin(distances)
        return nearest_idx, palette[nearest_idx]

    def floyd_steinberg_dither(self, image: Image.Image) -> Tuple[Image.Image, np.ndarray]:
        """Apply Floyd-Steinberg dithering to an image using E6 palette with text preservation.

        The Floyd-Steinberg algorithm distributes quantization error to neighboring pixels:
        - 7/16 to the right
        - 3/16 to the bottom-left
        - 5/16 to the bottom
        - 1/16 to the bottom-right

        Args:
            image: Input PIL Image

        Returns:
            Tuple of (dithered image, palette index array)
        """
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Convert to numpy array with float type for error diffusion
        img_array = np.array(image, dtype=np.float32)
        original_array = img_array.copy()  # Keep original for reference
        height, width = img_array.shape[:2]

        # Create output arrays
        dithered = np.zeros_like(img_array, dtype=np.uint8)
        palette_indices = np.zeros((height, width), dtype=np.uint8)

        # Process each pixel
        for y in range(height):
            for x in range(width):
                # Get current pixel
                old_pixel = img_array[y, x].copy()

                # Check if this pixel should be preserved (black/white/exact match)
                should_preserve, preserved_color = self.should_preserve_pixel(original_array[y, x])

                if should_preserve and preserved_color is not None:
                    # Use the preserved color without dithering
                    new_pixel = preserved_color
                    # Find the palette index for this color
                    palette_idx = 0
                    for idx, pc in enumerate(self.palette_rgb):
                        if np.allclose(pc, new_pixel, rtol=0, atol=1):
                            palette_idx = idx
                            break
                    # No error diffusion for preserved pixels
                    error = np.zeros(3, dtype=np.float32)
                else:
                    # Find nearest palette color normally
                    palette_idx, new_pixel = self.find_nearest_palette_color(old_pixel, self.palette_rgb)
                    # Calculate error for diffusion
                    error = old_pixel - new_pixel

                # Set output pixel
                dithered[y, x] = new_pixel.astype(np.uint8)
                palette_indices[y, x] = palette_idx

                # Only distribute error if we didn't preserve the pixel
                if not should_preserve:
                    # Distribute error to neighboring pixels (Floyd-Steinberg coefficients)
                    if x < width - 1:
                        # Right pixel: 7/16
                        img_array[y, x + 1] += error * (7.0 / 16.0)

                    if y < height - 1:
                        # Bottom pixel: 5/16
                        img_array[y + 1, x] += error * (5.0 / 16.0)

                        if x > 0:
                            # Bottom-left pixel: 3/16
                            img_array[y + 1, x - 1] += error * (3.0 / 16.0)

                        if x < width - 1:
                            # Bottom-right pixel: 1/16
                            img_array[y + 1, x + 1] += error * (1.0 / 16.0)

        # Convert back to PIL Image
        dithered_image = Image.fromarray(dithered, mode='RGB')

        return dithered_image, palette_indices

    def analyze_color_distribution(self, image: Image.Image) -> dict:
        """Analyze which E6 colors will be used after dithering.

        Args:
            image: Original image to analyze

        Returns:
            Dictionary of color statistics
        """
        # Apply dithering to get the color distribution
        dithered_img, _ = self.floyd_steinberg_dither(image)

        # Count colors in dithered image
        img_array = np.array(dithered_img)
        height, width = img_array.shape[:2]
        total_pixels = height * width

        color_counts = {}
        for color_name, color_rgb in self.E6_PALETTE.items():
            # Count pixels matching this color (with small tolerance for rounding)
            mask = np.all(np.abs(img_array - color_rgb) < 2, axis=2)
            count = np.sum(mask)
            percentage = (count / total_pixels) * 100
            color_counts[color_name] = (count, percentage)

        return color_counts

    def create_preview_with_original(self, original_image: Image.Image, color_stats: dict) -> Image.Image:
        """Create a preview showing the ORIGINAL image with color statistics.

        Args:
            original_image: Original undithered image
            color_stats: Dictionary of color usage statistics

        Returns:
            Preview image with original + statistics
        """
        # Use the original image, not dithered
        height, width = original_image.size[1], original_image.size[0]

        # Add space for statistics bar at bottom
        preview_height = height + 100
        preview = Image.new('RGB', (width, preview_height), (255, 255, 255))
        preview.paste(original_image, (0, 0))

        # Draw color distribution info
        draw = ImageDraw.Draw(preview)

        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
        except:
            font = ImageFont.load_default()

        # Draw title
        draw.text((10, height + 5),
                 "E6 Color Distribution (after dithering):",
                 fill=(0, 0, 0), font=font)

        # Draw color bars and percentages
        bar_y = height + 25
        x = 10

        for color_name, (count, percentage) in color_stats.items():
            if percentage > 0.1:  # Only show colors that are actually used
                # Draw color square
                color_rgb = self.E6_PALETTE[color_name]
                draw.rectangle([x, bar_y, x + 15, bar_y + 15], fill=color_rgb, outline=(0, 0, 0))

                # Draw label
                text = f"{color_name}: {percentage:.1f}%"
                draw.text((x + 20, bar_y), text, fill=(0, 0, 0), font=font)
                x += 150

                if x > width - 150:  # Wrap to next line
                    x = 10
                    bar_y += 25

        # Add info text
        draw.text((10, preview_height - 20),
                 "Original image - Will be dithered for Spectra E6 Display",
                 fill=(128, 128, 128), font=font)

        return preview

    def process_dashboard(self, input_image: Image.Image, output_dir: str = "output") -> Tuple[str, str]:
        """Process a dashboard image with dithering.

        Args:
            input_image: Original dashboard image
            output_dir: Directory for output files

        Returns:
            Tuple of (dithered image path, preview image path)
        """
        from pathlib import Path
        from datetime import datetime

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # First, analyze what colors will be used
        logger.info("Analyzing color distribution...")
        color_stats = self.analyze_color_distribution(input_image)

        # Apply dithering
        logger.info("Applying Floyd-Steinberg dithering with text preservation...")
        dithered_image, palette_indices = self.floyd_steinberg_dither(input_image)

        # Create preview with ORIGINAL image and statistics
        preview = self.create_preview_with_original(input_image, color_stats)

        # Save files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        dithered_path = output_path / f"dashboard_e6_dithered_{timestamp}.png"
        dithered_image.save(dithered_path)

        preview_path = output_path / f"dashboard_e6_preview_{timestamp}.png"
        preview.save(preview_path)

        # Also save the palette index image for e-ink display driver
        palette_path = output_path / f"dashboard_e6_palette_{timestamp}.png"
        palette_indices_img = Image.fromarray((palette_indices * 42).astype(np.uint8), mode='L')  # Scale for visibility
        palette_indices_img.save(palette_path)

        logger.info(f"Saved dithered image: {dithered_path}")
        logger.info(f"Saved preview image: {preview_path}")
        logger.info(f"Saved palette indices: {palette_path}")

        return str(dithered_path), str(preview_path)


class OptimizedE6Dithering(SpectraE6Dithering):
    """Optimized dithering with enhanced text preservation."""

    def __init__(self, preserve_text: bool = True, text_threshold: int = 40):
        """Initialize optimized dithering.

        Args:
            preserve_text: Whether to preserve black/white text without dithering
            text_threshold: Threshold for text detection (higher = more aggressive preservation)
        """
        # Always preserve black/white for text
        super().__init__(preserve_bw=preserve_text, bw_tolerance=5.0)
        self.preserve_text = preserve_text
        self.text_threshold = text_threshold

        # Adjust thresholds for more aggressive text preservation
        if preserve_text:
            self.BLACK_THRESHOLD = text_threshold
            self.WHITE_THRESHOLD = 255 - text_threshold

    def preprocess_for_e6(self, image: Image.Image) -> Image.Image:
        """Preprocess image to better map to E6 colors while preserving text.

        Args:
            image: Input image

        Returns:
            Preprocessed image
        """
        img_array = np.array(image, dtype=np.float32)

        # Don't enhance contrast for text areas
        # Just ensure blacks are black and whites are white

        # Force near-black to pure black (text preservation)
        black_mask = np.all(img_array <= self.BLACK_THRESHOLD, axis=2)
        img_array[black_mask] = [0, 0, 0]

        # Force near-white to pure white (background preservation)
        white_mask = np.all(img_array >= self.WHITE_THRESHOLD, axis=2)
        img_array[white_mask] = [255, 255, 255]

        # For grays that aren't text, apply light processing
        gray_mask = np.all(np.abs(img_array - img_array.mean(axis=2, keepdims=True)) < 20, axis=2)
        gray_mask = gray_mask & ~black_mask & ~white_mask

        for y in range(img_array.shape[0]):
            for x in range(img_array.shape[1]):
                if gray_mask[y, x]:
                    brightness = img_array[y, x].mean()
                    # Push grays toward black or white for cleaner text
                    if brightness < 128:
                        img_array[y, x] = [0, 0, 0]
                    else:
                        img_array[y, x] = [255, 255, 255]

        return Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8), mode='RGB')

    def smart_color_assignment(self, image: Image.Image) -> Image.Image:
        """Apply smart color assignment based on content type.

        Args:
            image: Input image

        Returns:
            Image with colors reassigned for better E6 display
        """
        # Just return the image - color assignment is handled in preprocessing
        return image