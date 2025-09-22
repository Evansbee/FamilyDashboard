"""Mock data providers for dashboard content."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random

class DateProvider:
    """Provides formatted date and time information."""

    @staticmethod
    def get_current_date() -> str:
        """Get formatted current date.

        Returns:
            Formatted date string
        """
        now = datetime.now()
        return now.strftime("%A, %B %d, %Y")

    @staticmethod
    def is_school_day() -> bool:
        """Check if today is a school day.

        Returns:
            True if it's a weekday (Mon-Fri)
        """
        return datetime.now().weekday() < 5  # Monday = 0, Sunday = 6


class WeatherProvider:
    """Provides weather information (mock data for now)."""

    @staticmethod
    def get_weather() -> Dict[str, str]:
        """Get current weather information.

        Returns:
            Dictionary with weather data
        """
        # Mock weather data - replace with actual API later
        conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Light Rain", "Clear"]
        temps = range(60, 85)

        temp = random.choice(list(temps))
        return {
            'location': 'Home',
            'temperature': f"{temp}°F",
            'conditions': random.choice(conditions),
            'high': f"{temp + random.randint(5, 10)}°F",
            'low': f"{temp - random.randint(5, 10)}°F",
            'humidity': f"{random.randint(40, 70)}%",
            'wind': f"{random.randint(5, 15)} mph"
        }


class ScheduleProvider:
    """Provides daily schedule information."""

    @staticmethod
    def get_daily_schedule() -> List[str]:
        """Get today's schedule.

        Returns:
            List of schedule items
        """
        day = datetime.now().weekday()

        # Mock schedules for different days
        if day == 0:  # Monday
            return [
                "7:00 AM - Wake up / Breakfast",
                "8:00 AM - School drop-off",
                "9:00 AM - Work from home",
                "12:00 PM - Lunch",
                "3:30 PM - School pickup",
                "5:00 PM - Soccer practice (Sam)",
                "6:30 PM - Dinner",
                "8:00 PM - Bedtime routine"
            ]
        elif day == 1:  # Tuesday
            return [
                "7:00 AM - Wake up / Breakfast",
                "8:00 AM - School drop-off",
                "9:00 AM - Work from home",
                "12:00 PM - Lunch",
                "3:30 PM - School pickup",
                "4:00 PM - Piano lessons (Emma)",
                "6:00 PM - Dinner",
                "7:30 PM - Family game night",
                "8:30 PM - Bedtime routine"
            ]
        elif day == 2:  # Wednesday
            return [
                "7:00 AM - Wake up / Breakfast",
                "8:00 AM - School drop-off",
                "9:00 AM - Office day",
                "12:30 PM - Team lunch",
                "3:30 PM - School pickup (Grandma)",
                "6:30 PM - Dinner",
                "8:00 PM - Bedtime routine"
            ]
        elif day == 3:  # Thursday
            return [
                "7:00 AM - Wake up / Breakfast",
                "8:00 AM - School drop-off",
                "9:00 AM - Work from home",
                "11:00 AM - Parent-teacher conference",
                "12:00 PM - Lunch",
                "3:30 PM - School pickup",
                "4:30 PM - Library trip",
                "6:00 PM - Dinner",
                "8:00 PM - Bedtime routine"
            ]
        elif day == 4:  # Friday
            return [
                "7:00 AM - Wake up / Breakfast",
                "8:00 AM - School drop-off",
                "9:00 AM - Work from home",
                "12:00 PM - Lunch",
                "3:30 PM - School pickup",
                "5:00 PM - Movie night prep",
                "6:00 PM - Pizza dinner",
                "7:00 PM - Family movie night",
                "9:00 PM - Bedtime routine"
            ]
        elif day == 5:  # Saturday
            return [
                "8:00 AM - Weekend breakfast",
                "9:30 AM - Soccer game (Sam)",
                "11:00 AM - Farmers market",
                "12:30 PM - Lunch",
                "2:00 PM - Park / Playground",
                "4:00 PM - Free time",
                "6:00 PM - Dinner",
                "8:00 PM - Bedtime routine"
            ]
        else:  # Sunday
            return [
                "8:30 AM - Weekend breakfast",
                "10:00 AM - Family walk",
                "11:30 AM - Meal prep",
                "12:30 PM - Lunch",
                "2:00 PM - Quiet time / Naps",
                "3:30 PM - Board games",
                "5:00 PM - Early dinner",
                "6:00 PM - Bath time",
                "7:30 PM - Story time",
                "8:00 PM - Bedtime"
            ]


class LunchMenuProvider:
    """Provides school lunch menu information."""

    @staticmethod
    def get_lunch_menu() -> Optional[List[str]]:
        """Get today's school lunch menu.

        Returns:
            List of menu items, or None if not a school day
        """
        if not DateProvider.is_school_day():
            return None

        # Mock lunch menus for each weekday
        day = datetime.now().weekday()
        menus = {
            0: [  # Monday
                "Main: Chicken Nuggets",
                "Side: Tater Tots",
                "Vegetable: Carrots & Ranch",
                "Fruit: Apple Slices",
                "Drink: Milk or Juice"
            ],
            1: [  # Tuesday
                "Main: Cheese Pizza",
                "Side: Garden Salad",
                "Vegetable: Cucumber Slices",
                "Fruit: Orange Wedges",
                "Drink: Milk or Juice"
            ],
            2: [  # Wednesday
                "Main: Spaghetti & Meatballs",
                "Side: Garlic Bread",
                "Vegetable: Green Beans",
                "Fruit: Fruit Cup",
                "Drink: Milk or Juice"
            ],
            3: [  # Thursday
                "Main: Turkey & Cheese Sandwich",
                "Side: Pretzels",
                "Vegetable: Baby Carrots",
                "Fruit: Banana",
                "Drink: Milk or Juice"
            ],
            4: [  # Friday
                "Main: Fish Sticks",
                "Side: Mac & Cheese",
                "Vegetable: Corn",
                "Fruit: Strawberries",
                "Drink: Milk or Juice"
            ]
        }

        return menus.get(day, ["Menu not available"])


class DashboardDataProvider:
    """Aggregates all data for the dashboard."""

    def __init__(self):
        """Initialize the data provider."""
        self.date_provider = DateProvider()
        self.weather_provider = WeatherProvider()
        self.schedule_provider = ScheduleProvider()
        self.lunch_provider = LunchMenuProvider()

    def get_dashboard_data(self) -> Dict:
        """Get all data needed for the dashboard.

        Returns:
            Dictionary containing all dashboard data
        """
        return {
            'date': self.date_provider.get_current_date(),
            'weather': self.weather_provider.get_weather(),
            'schedule': self.schedule_provider.get_daily_schedule(),
            'lunch': self.lunch_provider.get_lunch_menu(),
            'is_school_day': self.date_provider.is_school_day()
        }