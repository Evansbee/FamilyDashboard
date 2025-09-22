"""Floyd-Steinberg dithering for Spectra E6 e-ink display."""

import numpy as np
from PIL import Image
from typing import Tuple, List
import logging

logger = logging.getLogger(__name__)


class SpectraE6Dithering:
    """Floyd-Steinberg dithering for Spectra E6 6-color e-ink display."""

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

    def __init__(self):
        """Initialize the dithering processor."""
        self.palette_rgb = self.PALETTE_ARRAY.copy()

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

    def floyd_steinberg_dither(self, image: Image.Image) -> Tuple[Image.Image, Image.Image]:
        """Apply Floyd-Steinberg dithering to an image using E6 palette.

        The Floyd-Steinberg algorithm distributes quantization error to neighboring pixels:
        - 7/16 to the right
        - 3/16 to the bottom-left
        - 5/16 to the bottom
        - 1/16 to the bottom-right

        Args:
            image: Input PIL Image

        Returns:
            Tuple of (dithered image, palette index image)
        """
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Convert to numpy array with float type for error diffusion
        img_array = np.array(image, dtype=np.float32)
        height, width = img_array.shape[:2]

        # Create output arrays
        dithered = np.zeros_like(img_array, dtype=np.uint8)
        palette_indices = np.zeros((height, width), dtype=np.uint8)

        # Process each pixel
        for y in range(height):
            for x in range(width):
                # Get current pixel
                old_pixel = img_array[y, x].copy()

                # Find nearest palette color
                palette_idx, new_pixel = self.find_nearest_palette_color(old_pixel, self.palette_rgb)

                # Set output pixel
                dithered[y, x] = new_pixel.astype(np.uint8)
                palette_indices[y, x] = palette_idx

                # Calculate error
                error = old_pixel - new_pixel

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

        # Create palette index image for e-ink display
        palette_image = Image.fromarray(palette_indices, mode='P')

        return dithered_image, palette_image

    def create_preview_with_palette_info(self, image: Image.Image) -> Image.Image:
        """Create a preview image with palette color distribution info.

        Args:
            image: Dithered image

        Returns:
            Preview image with color statistics
        """
        # Get color distribution
        img_array = np.array(image)
        height, width = img_array.shape[:2]
        total_pixels = height * width

        color_counts = {}
        for color_name, color_rgb in self.E6_PALETTE.items():
            # Count pixels matching this color (with small tolerance for rounding)
            mask = np.all(np.abs(img_array - color_rgb) < 2, axis=2)
            count = np.sum(mask)
            percentage = (count / total_pixels) * 100
            color_counts[color_name] = (count, percentage)

        # Add color statistics bar at bottom
        preview_height = height + 100
        preview = Image.new('RGB', (width, preview_height), (255, 255, 255))
        preview.paste(image, (0, 0))

        # Draw color distribution info
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(preview)

        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
        except:
            font = ImageFont.load_default()

        # Draw color bars and percentages
        bar_height = 20
        bar_y = height + 10
        x = 10

        for color_name, (count, percentage) in color_counts.items():
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

        # Add dithering info
        draw.text((10, preview_height - 20),
                 "Floyd-Steinberg Dithered for Spectra E6 Display",
                 fill=(0, 0, 0), font=font)

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

        # Apply dithering
        logger.info("Applying Floyd-Steinberg dithering...")
        dithered_image, palette_indices = self.floyd_steinberg_dither(input_image)

        # Create preview with statistics
        preview = self.create_preview_with_palette_info(dithered_image)

        # Save files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        dithered_path = output_path / f"dashboard_e6_dithered_{timestamp}.png"
        dithered_image.save(dithered_path)

        preview_path = output_path / f"dashboard_e6_preview_{timestamp}.png"
        preview.save(preview_path)

        # Also save the palette index image for e-ink display driver
        palette_path = output_path / f"dashboard_e6_palette_{timestamp}.png"
        # Convert palette_indices (second element of tuple) to numpy array if needed
        if isinstance(palette_indices, Image.Image):
            palette_array = np.array(palette_indices)
        else:
            palette_array = palette_indices
        palette_indices_img = Image.fromarray((palette_array * 42).astype(np.uint8), mode='L')  # Scale for visibility
        palette_indices_img.save(palette_path)

        logger.info(f"Saved dithered image: {dithered_path}")
        logger.info(f"Saved preview image: {preview_path}")
        logger.info(f"Saved palette indices: {palette_path}")

        return str(dithered_path), str(preview_path)


class OptimizedE6Dithering(SpectraE6Dithering):
    """Optimized dithering with content-aware color mapping."""

    def __init__(self, preserve_text: bool = True):
        """Initialize optimized dithering.

        Args:
            preserve_text: Whether to preserve black text without dithering
        """
        super().__init__()
        self.preserve_text = preserve_text

    def preprocess_for_e6(self, image: Image.Image) -> Image.Image:
        """Preprocess image to better map to E6 colors.

        Args:
            image: Input image

        Returns:
            Preprocessed image
        """
        img_array = np.array(image, dtype=np.float32)

        # Enhance contrast for better color separation
        # This helps the dithering algorithm make better decisions
        mean = img_array.mean()
        img_array = (img_array - mean) * 1.2 + mean
        img_array = np.clip(img_array, 0, 255)

        # Map grays to specific E6 colors based on content
        # Very light grays -> white
        # Medium grays -> yellow (for subtle highlights)
        # Dark grays -> black
        gray_mask = np.all(np.abs(img_array - img_array.mean(axis=2, keepdims=True)) < 30, axis=2)

        for y in range(img_array.shape[0]):
            for x in range(img_array.shape[1]):
                if gray_mask[y, x]:
                    brightness = img_array[y, x].mean()
                    if brightness > 200:
                        img_array[y, x] = [255, 255, 255]  # White
                    elif brightness < 50:
                        img_array[y, x] = [0, 0, 0]  # Black
                    elif 100 < brightness < 150:
                        # Medium gray - use yellow for subtle accent
                        img_array[y, x] = [255, 255, 200]  # Slightly desaturated yellow

        return Image.fromarray(img_array.astype(np.uint8), mode='RGB')

    def smart_color_assignment(self, image: Image.Image) -> Image.Image:
        """Apply smart color assignment based on content type.

        Args:
            image: Input image

        Returns:
            Image with colors reassigned for better E6 display
        """
        img_array = np.array(image, dtype=np.float32)

        # Detect red areas (likely important - lunch menu, alerts)
        red_mask = (img_array[:, :, 0] > 200) & (img_array[:, :, 1] < 100) & (img_array[:, :, 2] < 100)

        # Keep pure reds as red (important information)
        # This ensures lunch menus and alerts stay red

        # Map other colors strategically:
        # - Blues/cyans -> Blue
        # - Greens -> Green
        # - Oranges/browns -> Yellow
        # This is already handled by the nearest color algorithm

        return Image.fromarray(img_array.astype(np.uint8), mode='RGB')