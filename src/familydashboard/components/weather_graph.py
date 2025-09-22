"""Temperature graph component for weather display."""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import io
import numpy as np
from typing import List, Tuple, Optional


class TemperatureGraph:
    """Creates a temperature graph for the day."""

    def __init__(self, width: int = 700, height: int = 200, dpi: int = 100):
        """Initialize the temperature graph.

        Args:
            width: Width in pixels
            height: Height in pixels
            dpi: DPI for the graph
        """
        self.width = width
        self.height = height
        self.dpi = dpi

    def create_graph(self, hours: List[int], temperatures: List[float],
                    precipitation: Optional[List[float]] = None,
                    unit: str = "°F") -> Image.Image:
        """Create a temperature graph with optional precipitation overlay.

        Args:
            hours: List of hours (0-23)
            temperatures: List of temperatures for each hour
            precipitation: Optional list of precipitation probabilities (0-100)
            unit: Temperature unit string

        Returns:
            PIL Image object containing the graph
        """
        # Create figure with specified size
        fig_width = self.width / self.dpi
        fig_height = self.height / self.dpi
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=self.dpi)

        # Style the plot for e-ink display
        ax.set_facecolor('white')
        fig.patch.set_facecolor('white')

        # Plot temperature line
        ax.plot(hours, temperatures, color='black', linewidth=2, marker='o',
                markersize=4, markerfacecolor='white', markeredgecolor='black')

        # Fill under the curve with a light pattern
        ax.fill_between(hours, temperatures, min(temperatures) - 5,
                       alpha=0.1, color='black', hatch='///')

        # Add precipitation bars if provided
        if precipitation:
            ax2 = ax.twinx()
            # Create bar chart for precipitation
            bars = ax2.bar(hours, precipitation, alpha=0.3, color='gray',
                          width=0.8, label='Precip %')
            # Add pattern to bars
            for bar in bars:
                bar.set_hatch('...')
            ax2.set_ylabel('Precipitation %', fontsize=9)
            ax2.set_ylim(0, 100)
            ax2.set_yticks([0, 50, 100])
            ax2.grid(False)

        # Customize the main axis
        ax.set_xlabel('Hour of Day', fontsize=10)
        ax.set_ylabel(f'Temperature ({unit})', fontsize=10)
        ax.set_title('Today\'s Temperature Forecast', fontsize=12, fontweight='bold')

        # Set x-axis to show every 3 hours
        ax.set_xticks(range(0, 24, 3))
        ax.set_xticklabels([f'{h:02d}:00' for h in range(0, 24, 3)], fontsize=8)

        # Add grid
        ax.grid(True, linestyle='--', alpha=0.3, color='gray')
        ax.set_axisbelow(True)

        # Add min/max annotations
        if temperatures:
            max_temp = max(temperatures)
            min_temp = min(temperatures)
            max_idx = temperatures.index(max_temp)
            min_idx = temperatures.index(min_temp)

            # Annotate maximum
            ax.annotate(f'{max_temp:.0f}{unit}',
                       xy=(hours[max_idx], max_temp),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=9, fontweight='bold')

            # Annotate minimum
            ax.annotate(f'{min_temp:.0f}{unit}',
                       xy=(hours[min_idx], min_temp),
                       xytext=(5, -15), textcoords='offset points',
                       fontsize=9, fontweight='bold')

        # Highlight current hour
        current_hour = datetime.now().hour
        if current_hour in hours:
            ax.axvline(x=current_hour, color='red', linestyle=':', linewidth=2, alpha=0.7)
            ax.text(current_hour, ax.get_ylim()[1] * 0.95, 'NOW',
                   ha='center', fontsize=8, color='red', fontweight='bold')

        # Set reasonable y-axis limits
        if temperatures:
            temp_range = max(temperatures) - min(temperatures)
            ax.set_ylim(min(temperatures) - temp_range * 0.2,
                       max(temperatures) + temp_range * 0.2)

        # Tight layout
        plt.tight_layout()

        # Convert to PIL Image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', facecolor='white', edgecolor='none')
        buffer.seek(0)
        image = Image.open(buffer)

        # Clean up
        plt.close(fig)

        return image

    def create_simple_graph(self, hours: List[int], temperatures: List[float],
                          unit: str = "°F") -> Image.Image:
        """Create a simplified temperature graph for e-ink display.

        Args:
            hours: List of hours (0-23)
            temperatures: List of temperatures for each hour
            unit: Temperature unit string

        Returns:
            PIL Image object containing the graph
        """
        from datetime import datetime

        # Create figure with specified size
        fig_width = self.width / self.dpi
        fig_height = self.height / self.dpi
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=self.dpi)

        # Clean white background
        ax.set_facecolor('white')
        fig.patch.set_facecolor('white')

        # Simple black line plot
        ax.plot(hours, temperatures, color='black', linewidth=3)

        # Minimal styling
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(1)
        ax.spines['bottom'].set_linewidth(1)

        # X-axis: show key hours
        ax.set_xticks([0, 6, 12, 18, 23])
        ax.set_xticklabels(['12am', '6am', '12pm', '6pm', '11pm'], fontsize=10)

        # Y-axis: temperature
        ax.set_ylabel(f'Temp ({unit})', fontsize=11)

        # Add horizontal line at current hour
        current_hour = datetime.now().hour
        if current_hour in hours:
            temp_at_hour = temperatures[hours.index(current_hour)]
            ax.plot(current_hour, temp_at_hour, 'ro', markersize=8)

        # Add max/min labels
        if temperatures:
            max_temp = max(temperatures)
            min_temp = min(temperatures)
            ax.text(0.02, 0.98, f'High: {max_temp:.0f}{unit}',
                   transform=ax.transAxes, fontsize=10,
                   verticalalignment='top')
            ax.text(0.02, 0.88, f'Low: {min_temp:.0f}{unit}',
                   transform=ax.transAxes, fontsize=10,
                   verticalalignment='top')

        # Minimal grid
        ax.grid(True, axis='y', linestyle=':', alpha=0.3)
        ax.set_axisbelow(True)

        # Tight layout
        plt.tight_layout(pad=0.5)

        # Convert to PIL Image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', facecolor='white', edgecolor='none', dpi=self.dpi)
        buffer.seek(0)
        image = Image.open(buffer)

        # Clean up
        plt.close(fig)

        return image