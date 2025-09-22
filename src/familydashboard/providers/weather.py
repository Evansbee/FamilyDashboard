"""Real weather provider using Open-Meteo API."""

import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class OpenMeteoWeatherProvider:
    """Weather provider using Open-Meteo free weather API."""

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    # Font Awesome weather icon mappings (Unicode points for FA6)
    WEATHER_ICONS = {
        # WMO Weather codes to Font Awesome icons
        0: "\uf185",    # Clear sky - sun
        1: "\uf6c4",    # Mainly clear - sun-cloud
        2: "\uf6c4",    # Partly cloudy - sun-cloud
        3: "\uf0c2",    # Overcast - cloud
        45: "\uf75f",   # Foggy - smog
        48: "\uf75f",   # Depositing rime fog - smog
        51: "\uf743",   # Light drizzle - cloud-drizzle
        53: "\uf743",   # Moderate drizzle - cloud-drizzle
        55: "\uf740",   # Dense drizzle - cloud-rain
        56: "\uf740",   # Light freezing drizzle
        57: "\uf740",   # Dense freezing drizzle
        61: "\uf743",   # Slight rain - cloud-drizzle
        63: "\uf740",   # Moderate rain - cloud-rain
        65: "\uf73d",   # Heavy rain - cloud-showers-heavy
        66: "\uf73d",   # Light freezing rain
        67: "\uf73d",   # Heavy freezing rain
        71: "\uf2dc",   # Slight snow - snowflake
        73: "\uf2dc",   # Moderate snow - snowflake
        75: "\uf2dc",   # Heavy snow - snowflake
        77: "\uf2dc",   # Snow grains - snowflake
        80: "\uf743",   # Slight rain showers - cloud-drizzle
        81: "\uf740",   # Moderate rain showers - cloud-rain
        82: "\uf73d",   # Violent rain showers - cloud-showers-heavy
        85: "\uf2dc",   # Slight snow showers - snowflake
        86: "\uf2dc",   # Heavy snow showers - snowflake
        95: "\uf0e7",   # Thunderstorm - bolt
        96: "\uf76c",   # Thunderstorm with slight hail - cloud-bolt
        99: "\uf76c",   # Thunderstorm with heavy hail - cloud-bolt
    }

    # Weather code descriptions
    WEATHER_DESCRIPTIONS = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }

    def __init__(self, latitude: float = 40.7128, longitude: float = -74.0060,
                 timezone_str: str = "America/New_York", temperature_unit: str = "fahrenheit"):
        """Initialize the weather provider.

        Args:
            latitude: Location latitude (default: NYC)
            longitude: Location longitude (default: NYC)
            timezone_str: Timezone string (default: America/New_York)
            temperature_unit: celsius or fahrenheit (default: fahrenheit)
        """
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone_str
        self.temperature_unit = temperature_unit

    def get_daily_forecast(self) -> Optional[Dict]:
        """Fetch daily weather forecast with hourly data.

        Returns:
            Dictionary with weather data including hourly temperatures for graphing
        """
        try:
            params = {
                'latitude': self.latitude,
                'longitude': self.longitude,
                'hourly': 'temperature_2m,weather_code,precipitation_probability',
                'daily': 'weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max',
                'temperature_unit': self.temperature_unit,
                'timezone': self.timezone,
                'forecast_days': 1
            }

            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Process the data
            hourly_data = data.get('hourly', {})
            daily_data = data.get('daily', {})

            # Get today's data
            today_weather_code = daily_data['weather_code'][0] if daily_data.get('weather_code') else 0

            # Extract hourly temperatures for today (24 hours)
            hourly_temps = hourly_data.get('temperature_2m', [])[:24]
            hourly_times = hourly_data.get('time', [])[:24]
            hourly_weather_codes = hourly_data.get('weather_code', [])[:24]
            hourly_precip_prob = hourly_data.get('precipitation_probability', [])[:24]

            # Convert times to hour labels
            hours = []
            for time_str in hourly_times:
                dt = datetime.fromisoformat(time_str)
                hours.append(dt.hour)

            # Find the predominant weather condition for the day
            if hourly_weather_codes:
                # Use the most common weather code during daylight hours (6am-6pm)
                daylight_codes = hourly_weather_codes[6:18] if len(hourly_weather_codes) > 18 else hourly_weather_codes
                most_common_code = max(set(daylight_codes), key=daylight_codes.count) if daylight_codes else today_weather_code
            else:
                most_common_code = today_weather_code

            return {
                'weather_code': most_common_code,
                'description': self.WEATHER_DESCRIPTIONS.get(most_common_code, "Unknown"),
                'icon': self.WEATHER_ICONS.get(most_common_code, "\uf185"),  # Default to sun
                'temperature_high': daily_data['temperature_2m_max'][0] if daily_data.get('temperature_2m_max') else None,
                'temperature_low': daily_data['temperature_2m_min'][0] if daily_data.get('temperature_2m_min') else None,
                'precipitation_sum': daily_data['precipitation_sum'][0] if daily_data.get('precipitation_sum') else 0,
                'precipitation_probability': daily_data['precipitation_probability_max'][0] if daily_data.get('precipitation_probability_max') else 0,
                'hourly_temperatures': hourly_temps,
                'hourly_times': hours,
                'hourly_precipitation': hourly_precip_prob,
                'unit': '°F' if self.temperature_unit == 'fahrenheit' else '°C'
            }

        except requests.RequestException as e:
            logger.error(f"Failed to fetch weather data: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing weather data: {e}")
            return None

    def get_weather_icon(self, weather_code: int) -> str:
        """Get Font Awesome icon for weather code.

        Args:
            weather_code: WMO weather code

        Returns:
            Font Awesome unicode character
        """
        return self.WEATHER_ICONS.get(weather_code, "\uf185")  # Default to sun