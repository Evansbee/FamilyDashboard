"""Main dashboard generator using PIL for e-ink display."""

from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Optional, Dict, Any
from pathlib import Path
from datetime import datetime

class DashboardLayout:
    """Manages the layout for a 1600x1200 e-ink display dashboard."""

    DISPLAY_WIDTH = 1600
    DISPLAY_HEIGHT = 1200

    # Color constants for e-ink (Spectra E6 supports red)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GRAY = (128, 128, 128)

    def __init__(self, output_dir: Path = Path("output")):
        """Initialize the dashboard layout.

        Args:
            output_dir: Directory to save generated images
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)

        # Create the base image (white background)
        self.image = Image.new('RGB', (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT), self.WHITE)
        self.draw = ImageDraw.Draw(self.image)

        # Define layout regions
        self.regions = {
            'header': (0, 0, self.DISPLAY_WIDTH, 150),  # Date and time
            'weather': (0, 150, 800, 450),  # Weather section (left)
            'lunch': (800, 150, self.DISPLAY_WIDTH, 450),  # Lunch menu (right)
            'schedule': (0, 450, self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT - 50),  # Daily schedule
            'footer': (0, self.DISPLAY_HEIGHT - 50, self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT)  # Status/update time
        }

        # Font settings (will use default for now)
        self.fonts = self._load_fonts()

    def _load_fonts(self) -> Dict[str, ImageFont.FreeTypeFont]:
        """Load fonts for different text sizes.

        Returns:
            Dictionary of font objects by size name
        """
        # For now, use default font - can be replaced with TTF fonts later
        try:
            return {
                'title': ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 72),
                'header': ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48),
                'subheader': ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36),
                'body': ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28),
                'small': ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20),
            }
        except:
            # Fallback to default font
            default = ImageFont.load_default()
            return {
                'title': default,
                'header': default,
                'subheader': default,
                'body': default,
                'small': default,
            }

    def draw_border(self, region_name: str, color: Tuple[int, int, int] = BLACK, width: int = 2):
        """Draw a border around a region.

        Args:
            region_name: Name of the region to border
            color: Border color
            width: Border width in pixels
        """
        if region_name not in self.regions:
            return

        x1, y1, x2, y2 = self.regions[region_name]
        self.draw.rectangle([x1, y1, x2-1, y2-1], outline=color, width=width)

    def draw_text_in_region(self, region_name: str, text: str, font_size: str = 'body',
                           color: Tuple[int, int, int] = BLACK,
                           align: str = 'center', padding: int = 20):
        """Draw text within a region.

        Args:
            region_name: Name of the region to draw in
            text: Text to draw
            font_size: Font size key
            color: Text color
            align: Text alignment (left, center, right)
            padding: Padding from region borders
        """
        if region_name not in self.regions:
            return

        x1, y1, x2, y2 = self.regions[region_name]
        font = self.fonts.get(font_size, self.fonts['body'])

        # Calculate text position based on alignment
        text_bbox = self.draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        if align == 'center':
            x = x1 + (x2 - x1 - text_width) // 2
        elif align == 'right':
            x = x2 - text_width - padding
        else:  # left
            x = x1 + padding

        y = y1 + padding

        self.draw.text((x, y), text, font=font, fill=color)

    def draw_multiline_text(self, region_name: str, lines: list, font_size: str = 'body',
                           color: Tuple[int, int, int] = BLACK, line_spacing: int = 10,
                           padding: int = 20):
        """Draw multiple lines of text in a region.

        Args:
            region_name: Name of the region to draw in
            lines: List of text lines
            font_size: Font size key
            color: Text color
            line_spacing: Space between lines
            padding: Padding from region borders
        """
        if region_name not in self.regions or not lines:
            return

        x1, y1, x2, y2 = self.regions[region_name]
        font = self.fonts.get(font_size, self.fonts['body'])

        y = y1 + padding
        for line in lines:
            if y >= y2 - padding:
                break

            self.draw.text((x1 + padding, y), line, font=font, fill=color)

            # Calculate line height
            bbox = self.draw.textbbox((0, 0), line or "M", font=font)
            line_height = bbox[3] - bbox[1]
            y += line_height + line_spacing

    def save(self, filename: Optional[str] = None) -> Path:
        """Save the dashboard image.

        Args:
            filename: Output filename (defaults to timestamp)

        Returns:
            Path to saved image
        """
        if filename is None:
            filename = f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        output_path = self.output_dir / filename
        self.image.save(output_path, 'PNG')
        return output_path

    def clear(self):
        """Clear the dashboard to white background."""
        self.draw.rectangle([0, 0, self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT], fill=self.WHITE)

    def render_dashboard(self, data: Dict[str, Any]) -> Path:
        """Render the complete dashboard with provided data.

        Args:
            data: Dictionary containing dashboard data
                - date: Current date string
                - weather: Weather information dict
                - schedule: List of schedule items
                - lunch: Lunch menu (if school day)

        Returns:
            Path to saved image
        """
        self.clear()

        # Draw borders for visual structure
        for region in self.regions:
            self.draw_border(region, self.GRAY, 1)

        # Render date header
        if 'date' in data:
            self.draw_text_in_region('header', data['date'], 'title', self.BLACK)

        # Render weather
        if 'weather' in data:
            weather_lines = [
                f"Weather for {data['weather'].get('location', 'Unknown')}",
                f"Temperature: {data['weather'].get('temperature', 'N/A')}",
                f"Conditions: {data['weather'].get('conditions', 'N/A')}",
                f"High/Low: {data['weather'].get('high', 'N/A')}/{data['weather'].get('low', 'N/A')}",
            ]
            self.draw_multiline_text('weather', weather_lines, 'subheader')

        # Render lunch menu (if school day)
        if 'lunch' in data and data['lunch']:
            lunch_lines = ["Today's Lunch Menu:"] + data['lunch']
            self.draw_multiline_text('lunch', lunch_lines, 'body', self.RED)

        # Render schedule
        if 'schedule' in data:
            schedule_lines = ["Daily Schedule:"] + data['schedule']
            self.draw_multiline_text('schedule', schedule_lines, 'body')

        # Footer with update time
        update_time = f"Updated: {datetime.now().strftime('%H:%M')}"
        self.draw_text_in_region('footer', update_time, 'small', self.GRAY, align='right')

        return self.save()