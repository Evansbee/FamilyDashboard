"""Generate a test image with gradients and colors for dithering demonstration."""

from PIL import Image, ImageDraw
import numpy as np


def create_test_pattern(width: int = 400, height: int = 300) -> Image.Image:
    """Create a test pattern with gradients and color patches.

    Args:
        width: Width of test image
        height: Height of test image

    Returns:
        PIL Image with test pattern
    """
    # Create base image
    img = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Create color gradient bars (top section)
    gradient_height = height // 3

    # Red to white gradient
    for x in range(width // 3):
        intensity = int(255 * (x / (width // 3)))
        color = (255, intensity, intensity)
        draw.rectangle([x, 0, x + 1, gradient_height], fill=color)

    # Green to white gradient
    for x in range(width // 3, 2 * width // 3):
        intensity = int(255 * ((x - width // 3) / (width // 3)))
        color = (intensity, 255, intensity)
        draw.rectangle([x, 0, x + 1, gradient_height], fill=color)

    # Blue to white gradient
    for x in range(2 * width // 3, width):
        intensity = int(255 * ((x - 2 * width // 3) / (width // 3)))
        color = (intensity, intensity, 255)
        draw.rectangle([x, 0, x + 1, gradient_height], fill=color)

    # Middle section - color patches
    patch_y = gradient_height
    patch_height = height // 3
    patch_width = width // 6

    colors = [
        (255, 0, 0),      # Pure red
        (255, 128, 0),    # Orange
        (255, 255, 0),    # Yellow
        (0, 255, 0),      # Green
        (0, 0, 255),      # Blue
        (128, 0, 255),    # Purple
    ]

    for i, color in enumerate(colors):
        x = i * patch_width
        draw.rectangle([x, patch_y, x + patch_width, patch_y + patch_height], fill=color)

    # Bottom section - grayscale gradient
    gray_y = patch_y + patch_height
    gray_height = height - gray_y

    for x in range(width):
        gray_value = int(255 * (x / width))
        color = (gray_value, gray_value, gray_value)
        draw.rectangle([x, gray_y, x + 1, height], fill=color)

    return img


def create_photo_like_image(width: int = 400, height: int = 300) -> Image.Image:
    """Create a photo-like test image with smooth color transitions.

    Args:
        width: Width of test image
        height: Height of test image

    Returns:
        PIL Image with photo-like content
    """
    # Create numpy array for smooth gradients
    img_array = np.zeros((height, width, 3), dtype=np.uint8)

    # Create circular gradient (like a sunset)
    center_x, center_y = width // 2, height // 3

    for y in range(height):
        for x in range(width):
            # Distance from center
            dist = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            max_dist = np.sqrt(center_x ** 2 + center_y ** 2)

            # Normalize distance
            norm_dist = min(dist / max_dist, 1.0)

            # Create sunset-like colors
            if y < height // 2:
                # Sky colors
                r = int(255 * (1 - norm_dist * 0.3))  # Light orange to yellow
                g = int(200 * (1 - norm_dist * 0.4))  # Orange to red
                b = int(100 + 155 * norm_dist)        # Blue gradient
            else:
                # Ground colors
                r = int(100 * (1 - norm_dist * 0.5))
                g = int(150 * (1 - norm_dist * 0.3))
                b = int(80 * (1 - norm_dist * 0.4))

            img_array[y, x] = [min(255, r), min(255, g), min(255, b)]

    # Add some "clouds" (white patches with soft edges)
    for _ in range(3):
        cloud_x = np.random.randint(width // 4, 3 * width // 4)
        cloud_y = np.random.randint(height // 6, height // 3)
        cloud_radius = np.random.randint(20, 40)

        for y in range(max(0, cloud_y - cloud_radius), min(height, cloud_y + cloud_radius)):
            for x in range(max(0, cloud_x - cloud_radius), min(width, cloud_x + cloud_radius)):
                dist = np.sqrt((x - cloud_x) ** 2 + (y - cloud_y) ** 2)
                if dist < cloud_radius:
                    alpha = 1 - (dist / cloud_radius)
                    alpha = alpha ** 2  # Soft edge
                    current = img_array[y, x].astype(float)
                    white = np.array([255, 255, 255])
                    img_array[y, x] = (current * (1 - alpha) + white * alpha).astype(np.uint8)

    return Image.fromarray(img_array)