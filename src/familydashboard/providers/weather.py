"""Real weather provider using Open-Meteo API."""

import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class OpenMeteoWeatherProvider:
    """Weather provider using Open-Meteo free weather API."""

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    # Font Awesome 7 weather icon mappings (Unicode points for FA7 Duotone)
    WEATHER_ICONS = {
        # WMO Weather codes to Font Awesome 7 Duotone icons
        0: "\ue28f",    # Clear sky - sun-bright (duotone)
        1: "\ue37d",    # Mainly clear - sun-cloud (duotone)
        2: "\ue37d",    # Partly cloudy - sun-cloud (duotone)
        3: "\ue312",    # Overcast - clouds (duotone)
        45: "\ue3c4",   # Foggy - fog (duotone)
        48: "\ue3c4",   # Depositing rime fog - fog (duotone)
        51: "\ue318",   # Light drizzle - cloud-drizzle (duotone)
        53: "\ue318",   # Moderate drizzle - cloud-drizzle (duotone)
        55: "\ue313",   # Dense drizzle - cloud-rain (duotone)
        56: "\ue318",   # Light freezing drizzle
        57: "\ue313",   # Dense freezing drizzle
        61: "\ue318",   # Slight rain - cloud-drizzle (duotone)
        63: "\ue313",   # Moderate rain - cloud-rain (duotone)
        65: "\ue314",   # Heavy rain - cloud-showers-heavy (duotone)
        66: "\ue313",   # Light freezing rain
        67: "\ue314",   # Heavy freezing rain
        71: "\ue31a",   # Slight snow - cloud-snow (duotone)
        73: "\ue31a",   # Moderate snow - cloud-snow (duotone)
        75: "\ue31a",   # Heavy snow - cloud-snow (duotone)
        77: "\ue31a",   # Snow grains - cloud-snow (duotone)
        80: "\ue318",   # Slight rain showers - cloud-drizzle (duotone)
        81: "\ue313",   # Moderate rain showers - cloud-rain (duotone)
        82: "\ue314",   # Violent rain showers - cloud-showers-heavy (duotone)
        85: "\ue31a",   # Slight snow showers - cloud-snow (duotone)
        86: "\ue31a",   # Heavy snow showers - cloud-snow (duotone)
        95: "\ue31d",   # Thunderstorm - cloud-bolt (duotone)
        96: "\ue31d",   # Thunderstorm with slight hail - cloud-bolt (duotone)
        99: "\ue31d",   # Thunderstorm with heavy hail - cloud-bolt (duotone)
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
                'icon': self.WEATHER_ICONS.get(most_common_code, "\ue28f"),  # Default to sun-bright
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
        return self.WEATHER_ICONS.get(weather_code, "\ue28f")  # Default to sun-bright