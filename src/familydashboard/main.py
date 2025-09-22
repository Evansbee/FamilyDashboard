"""Main script to generate the family dashboard image."""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from familydashboard.dashboard import DashboardLayout
from familydashboard.providers.data_providers import DashboardDataProvider


def generate_dashboard(output_filename: str = None):
    """Generate a dashboard image with current data.

    Args:
        output_filename: Optional output filename
    """
    # Initialize data provider and dashboard
    data_provider = DashboardDataProvider()
    dashboard = DashboardLayout()

    # Get current data
    data = data_provider.get_dashboard_data()

    # Render and save the dashboard
    output_path = dashboard.render_dashboard(data)

    print(f"Dashboard generated successfully!")
    print(f"Output: {output_path}")
    print(f"Date: {data['date']}")
    print(f"School day: {'Yes' if data['is_school_day'] else 'No (Weekend)'}")
    print(f"Display dimensions: {dashboard.DISPLAY_WIDTH}x{dashboard.DISPLAY_HEIGHT}")


if __name__ == "__main__":
    generate_dashboard()