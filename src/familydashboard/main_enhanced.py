"""Enhanced main script with real weather data and temperature graphs."""

import sys
from pathlib import Path
from datetime import datetime
import logging

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from familydashboard.dashboard_enhanced import EnhancedDashboardLayout
from familydashboard.providers.data_providers import (
    DateProvider,
    ScheduleProvider,
    LunchMenuProvider
)
from familydashboard.providers.weather import OpenMeteoWeatherProvider

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_enhanced_dashboard(
    latitude: float = None,
    longitude: float = None,
    location_name: str = "Home",
    output_filename: str = None
):
    """Generate an enhanced dashboard with real weather data.

    Args:
        latitude: Location latitude (will prompt if not provided)
        longitude: Location longitude (will prompt if not provided)
        location_name: Name for the location
        output_filename: Optional output filename
    """
    # Get location if not provided
    if latitude is None or longitude is None:
        print("For accurate weather, please provide your location.")
        print("You can find your coordinates at: https://www.latlong.net/")
        print("Or use default location (New York City)? [y/n]")

        use_default = input().strip().lower() == 'y'

        if use_default:
            latitude = 40.7128
            longitude = -74.0060
            location_name = "New York City"
        else:
            try:
                latitude = float(input("Enter latitude: ").strip())
                longitude = float(input("Enter longitude: ").strip())
                location_name = input("Enter location name (e.g., 'Home'): ").strip() or "Home"
            except ValueError:
                print("Invalid coordinates. Using default (NYC).")
                latitude = 40.7128
                longitude = -74.0060
                location_name = "New York City"

    # Initialize providers
    date_provider = DateProvider()
    schedule_provider = ScheduleProvider()
    lunch_provider = LunchMenuProvider()
    weather_provider = OpenMeteoWeatherProvider(
        latitude=latitude,
        longitude=longitude,
        temperature_unit="fahrenheit"
    )

    # Initialize dashboard
    dashboard = EnhancedDashboardLayout()

    # Get data
    print(f"Fetching weather data for {location_name}...")
    weather_forecast = weather_provider.get_daily_forecast()

    if weather_forecast:
        print(f"✓ Weather: {weather_forecast['description']}")
        print(f"  High: {weather_forecast['temperature_high']:.0f}°F")
        print(f"  Low: {weather_forecast['temperature_low']:.0f}°F")
        print(f"  Precipitation: {weather_forecast['precipitation_probability']}%")
    else:
        print("✗ Weather data unavailable (using mock data)")
        # Fallback to mock data
        weather_forecast = {
            'description': 'Partly Cloudy',
            'icon': '\uf0c2',
            'temperature_high': 75,
            'temperature_low': 60,
            'precipitation_probability': 20,
            'hourly_temperatures': [60, 58, 57, 56, 56, 57, 59, 62, 65, 68, 71, 73,
                                   75, 75, 74, 73, 71, 69, 67, 65, 63, 62, 61, 60],
            'hourly_times': list(range(24)),
            'unit': '°F'
        }

    # Prepare dashboard data
    data = {
        'date': date_provider.get_current_date(),
        'weather_forecast': weather_forecast,
        'schedule': schedule_provider.get_daily_schedule(),
        'lunch': lunch_provider.get_lunch_menu(),
        'is_school_day': date_provider.is_school_day(),
        'announcements': [
            "Library books due Friday",
            "Soccer practice 5pm Tuesday",
            "Piano recital next Saturday",
            "Parent-teacher conferences next week"
        ] if date_provider.is_school_day() else [
            "Family movie night 7pm",
            "Park visit if weather permits",
            "Meal prep for the week",
            "Board game tournament!"
        ]
    }

    # Render and save the dashboard
    print("Generating dashboard image...")
    original_path, dithered_path, preview_path = dashboard.render_enhanced_dashboard(data, create_dithered=True)

    print(f"\n✓ Dashboard generated successfully!")
    print(f"  Original: {original_path}")
    if dithered_path:
        print(f"  E6 Dithered: {dithered_path}")
        print(f"  Preview: {preview_path}")
    print(f"  Display: {dashboard.DISPLAY_WIDTH}x{dashboard.DISPLAY_HEIGHT}")
    print(f"  Date: {data['date']}")
    print(f"  Location: {location_name} ({latitude:.4f}, {longitude:.4f})")
    print(f"  School day: {'Yes' if data['is_school_day'] else 'No (Weekend)'}")
    print(f"\nThe dithered version is optimized for your Spectra E6 display with 6 colors:")
    print(f"  Black, White, Red, Yellow, Green, Blue")


if __name__ == "__main__":
    # You can hardcode your location here:
    # generate_enhanced_dashboard(latitude=YOUR_LAT, longitude=YOUR_LON, location_name="Home")

    generate_enhanced_dashboard()