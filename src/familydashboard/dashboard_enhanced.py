"""Enhanced dashboard generator with weather graphs and icons."""

from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import logging

from familydashboard.components.weather_graph import TemperatureGraph
from familydashboard.components.dithering import OptimizedE6Dithering
from familydashboard.components.test_image import create_test_pattern, create_photo_like_image

logger = logging.getLogger(__name__)


class EnhancedDashboardLayout:
    """Enhanced dashboard layout with weather graphics for a 1600x1200 e-ink display."""

    DISPLAY_WIDTH = 1600
    DISPLAY_HEIGHT = 1200

    # Color constants for e-ink (Spectra E6 supports red)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GRAY = (128, 128, 128)

    def __init__(self, output_dir: Path = Path("output")):
        """Initialize the enhanced dashboard layout.

        Args:
            output_dir: Directory to save generated images
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)

        # Create the base image (white background)
        self.image = Image.new('RGB', (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT), self.WHITE)
        self.draw = ImageDraw.Draw(self.image)

        # Enhanced layout regions - adjusted for weather graph and test image
        self.regions = {
            'header': (0, 0, self.DISPLAY_WIDTH, 100),  # Date header (smaller)
            'weather_icon': (20, 110, 170, 260),  # Weather icon area
            'weather_info': (180, 110, 500, 260),  # Weather text info
            'weather_graph': (520, 110, 1580, 360),  # Temperature graph
            'test_image': (20, 380, 420, 680),  # Test image for dithering demo
            'lunch': (440, 380, 1000, 680),  # Lunch menu (middle)
            'announcements': (1020, 380, 1580, 680),  # Announcements/notes (right)
            'schedule': (20, 700, 1580, 1150),  # Daily schedule
            'footer': (0, 1150, self.DISPLAY_WIDTH, 1200)  # Status/update time
        }

        # Font settings
        self.fonts = self._load_fonts()

        # Temperature graph generator
        self.temp_graph = TemperatureGraph(width=1060, height=250, dpi=100)

    def _load_fonts(self) -> Dict[str, ImageFont.FreeTypeFont]:
        """Load fonts for different text sizes.

        Returns:
            Dictionary of font objects by size name
        """
        fonts = {}

        # Try to load Font Awesome 7 Duotone for icons
        try:
            fonts['icon'] = ImageFont.truetype("fonts/Font Awesome 7 Duotone-Solid-900.otf", 100)
            fonts['icon_small'] = ImageFont.truetype("fonts/Font Awesome 7 Duotone-Solid-900.otf", 48)
            fonts['icon_medium'] = ImageFont.truetype("fonts/Font Awesome 7 Duotone-Solid-900.otf", 72)
        except Exception as e:
            logger.warning(f"Font Awesome 7 Duotone not found: {e}, icons will not display")
            fonts['icon'] = ImageFont.load_default()
            fonts['icon_small'] = ImageFont.load_default()
            fonts['icon_medium'] = ImageFont.load_default()

        # Load regular fonts
        try:
            fonts.update({
                'title': ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 56),
                'header': ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 42),
                'subheader': ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32),
                'body': ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 26),
                'small': ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20),
                'tiny': ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16),
            })
        except:
            # Fallback to default font
            default = ImageFont.load_default()
            fonts.update({
                'title': default,
                'header': default,
                'subheader': default,
                'body': default,
                'small': default,
                'tiny': default,
            })

        return fonts

    def draw_border(self, region_name: str, color: Tuple[int, int, int] = GRAY, width: int = 1):
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

        if align == 'center':
            x = x1 + (x2 - x1 - text_width) // 2
        elif align == 'right':
            x = x2 - text_width - padding
        else:  # left
            x = x1 + padding

        y = y1 + padding

        self.draw.text((x, y), text, font=font, fill=color)

    def draw_multiline_text(self, region_name: str, lines: list, font_size: str = 'body',
                           color: Tuple[int, int, int] = BLACK, line_spacing: int = 8,
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

    def draw_weather_icon(self, icon_unicode: str, color: Tuple[int, int, int] = BLACK):
        """Draw a weather icon in the weather_icon region.

        Args:
            icon_unicode: Font Awesome unicode character
            color: Icon color
        """
        if 'weather_icon' not in self.regions:
            return

        x1, y1, x2, y2 = self.regions['weather_icon']
        font = self.fonts.get('icon', self.fonts['body'])

        # Center the icon in the region
        text_bbox = self.draw.textbbox((0, 0), icon_unicode, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        x = x1 + (x2 - x1 - text_width) // 2
        y = y1 + (y2 - y1 - text_height) // 2

        self.draw.text((x, y), icon_unicode, font=font, fill=color)

    def paste_graph(self, graph_image: Image.Image, region_name: str = 'weather_graph'):
        """Paste a graph image into a region.

        Args:
            graph_image: PIL Image to paste
            region_name: Name of the region to paste into
        """
        if region_name not in self.regions:
            return

        x1, y1, x2, y2 = self.regions[region_name]

        # Resize graph to fit region if needed
        region_width = x2 - x1
        region_height = y2 - y1

        if graph_image.width != region_width or graph_image.height != region_height:
            graph_image = graph_image.resize((region_width, region_height), Image.Resampling.LANCZOS)

        # Paste the graph
        self.image.paste(graph_image, (x1, y1))

    def clear(self):
        """Clear the dashboard to white background."""
        self.draw.rectangle([0, 0, self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT], fill=self.WHITE)

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

    def render_enhanced_dashboard(self, data: Dict[str, Any], create_dithered: bool = True) -> Tuple[Path, Optional[Path], Optional[Path]]:
        """Render the enhanced dashboard with weather graph and icons.

        Args:
            data: Dictionary containing dashboard data including weather forecast
            create_dithered: Whether to create dithered version for e-ink

        Returns:
            Tuple of (original image path, dithered image path, preview path)
        """
        self.clear()

        # Draw subtle borders for structure
        for region in self.regions:
            if region != 'weather_graph':  # Don't border the graph
                self.draw_border(region, self.GRAY, 1)

        # Render date header
        if 'date' in data:
            self.draw_text_in_region('header', data['date'], 'title', self.BLACK)

        # Render weather with enhanced features
        if 'weather_forecast' in data and data['weather_forecast']:
            forecast = data['weather_forecast']

            # Draw weather icon
            if 'icon' in forecast:
                self.draw_weather_icon(forecast['icon'], self.BLACK)

            # Weather info text
            weather_lines = [
                f"{forecast.get('description', 'Unknown')}",
                f"High: {forecast.get('temperature_high', 'N/A'):.0f}{forecast.get('unit', '')}",
                f"Low: {forecast.get('temperature_low', 'N/A'):.0f}{forecast.get('unit', '')}",
                f"Rain: {forecast.get('precipitation_probability', 0)}%"
            ]
            self.draw_multiline_text('weather_info', weather_lines, 'body')

            # Create and paste temperature graph
            if 'hourly_temperatures' in forecast and 'hourly_times' in forecast:
                graph = self.temp_graph.create_simple_graph(
                    forecast['hourly_times'],
                    forecast['hourly_temperatures'],
                    forecast.get('unit', '°F')
                )
                self.paste_graph(graph)

        # Add test image for dithering demonstration
        try:
            # Create a colorful test pattern
            test_img = create_test_pattern(400, 300)
            # Resize to fit the region
            x1, y1, x2, y2 = self.regions['test_image']
            test_img = test_img.resize((x2 - x1, y2 - y1), Image.Resampling.LANCZOS)
            self.image.paste(test_img, (x1, y1))

            # Add label
            self.draw.text((x1 + 10, y1 + 10), "Color Test Pattern",
                          font=self.fonts.get('small', self.fonts['body']), fill=self.WHITE)
        except Exception as e:
            logger.warning(f"Could not add test image: {e}")

        # Render lunch menu (if school day)
        if 'lunch' in data and data['lunch']:
            lunch_lines = ["School Lunch:"] + data['lunch'][:8]  # Limit lines to fit smaller space
            self.draw_multiline_text('lunch', lunch_lines, 'small', self.RED)
        else:
            # Weekend message
            self.draw_multiline_text('lunch',
                                    ["Weekend - No School",
                                     "",
                                     "Enjoy family meals!"],
                                    'small', self.GRAY)

        # Render announcements/reminders (smaller text to fit)
        if 'announcements' in data:
            self.draw_multiline_text('announcements',
                                    ["Reminders:"] + data.get('announcements', [])[:5],
                                    'small')
        else:
            self.draw_multiline_text('announcements',
                                    ["Reminders:",
                                     "• Check backpacks",
                                     "• Water bottles",
                                     "• Homework done"],
                                    'small', self.GRAY)

        # Render schedule
        if 'schedule' in data:
            schedule_lines = ["Today's Schedule:"] + data['schedule']
            self.draw_multiline_text('schedule', schedule_lines, 'body')

        # Footer with update time
        update_time = f"Updated: {datetime.now().strftime('%A %H:%M')} | Next update: Tomorrow 6:00 AM"
        self.draw_text_in_region('footer', update_time, 'small', self.GRAY, align='center')

        # Save original image
        original_path = self.save()

        # Create dithered version if requested
        dithered_path = None
        preview_path = None
        if create_dithered:
            try:
                ditherer = OptimizedE6Dithering(preserve_text=True)
                # Preprocess the image for better E6 color mapping
                preprocessed = ditherer.preprocess_for_e6(self.image)
                # Apply dithering
                dithered_path, preview_path = ditherer.process_dashboard(preprocessed, str(self.output_dir))
                logger.info(f"Created dithered version: {dithered_path}")
            except Exception as e:
                logger.error(f"Failed to create dithered version: {e}")

        return original_path, dithered_path, preview_path