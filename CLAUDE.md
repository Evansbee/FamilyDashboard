# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FamilyDashboard is a Python-based e-ink display dashboard generator for family information. It creates 1600x1200 images optimized for Spectra E6 e-ink displays, showing date, weather, daily schedule, and school lunch menus.

## Development Setup

This project uses `uv` for Python dependency management.

### Commands

```bash
# Install dependencies
uv sync

# Run the dashboard generator
uv run python src/familydashboard/main.py

# Add new dependencies
uv add <package-name>
```

## Project Structure

```
src/familydashboard/
├── __init__.py              # Package initialization
├── main.py                  # Main entry point for dashboard generation
├── dashboard.py             # Core dashboard layout and rendering logic
├── providers/               # Data providers module
│   ├── __init__.py
│   └── data_providers.py   # Mock data providers for date, weather, schedule, lunch
└── components/              # Future: reusable UI components

output/                      # Generated dashboard images
fonts/                       # Custom fonts (when added)
```

## Architecture

### Dashboard Layout (dashboard.py)
- `DashboardLayout`: Main class for rendering 1600x1200 e-ink display
- Defines regions: header (date), weather, lunch menu, daily schedule, footer
- Supports Spectra E6 colors: white, black, red, gray
- Uses PIL (Pillow) for image generation

### Data Providers (providers/data_providers.py)
- `DateProvider`: Date formatting and school day detection
- `WeatherProvider`: Weather data (currently mock, ready for API integration)
- `ScheduleProvider`: Daily schedule by day of week
- `LunchMenuProvider`: School lunch menu for weekdays
- `DashboardDataProvider`: Aggregates all data sources

### Display Specifications
- Resolution: 1600x1200 pixels
- Target: Spectra E6 e-ink display
- Color support: Black, White, Red, Gray

## Key Dependencies

- `pillow`: Image generation and manipulation
- `python-dateutil`: Date/time utilities

## Future Integration Points

- Weather API integration to replace mock data
- School lunch menu API/scraping
- Calendar integration for dynamic schedules
- E-ink display driver integration
- Custom font support for better typography