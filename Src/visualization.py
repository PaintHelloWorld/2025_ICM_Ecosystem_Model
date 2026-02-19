# visualization.py
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def _setup_plotting_configs():
    """Initialize plotting configurations"""
    variables = ['crop', 'weed', 'pest', 'bird', 'bat', 'soil_health']

    variable_names = {
        'crop': 'Crop Biomass',
        'weed': 'Weed Biomass',
        'pest': 'Pest Density',
        'bird': 'Bird Density',
        'bat': 'Bat Density',
        'soil_health': 'Soil Health Index'
    }

    variable_colors = {
        'crop': '#2E7D32',      # dark green
        'weed': '#C62828',      # dark red
        'pest': '#FF8F00',      # orange
        'bird': '#1565C0',      # dark blue
        'bat': '#6A1B9A',       # purple
        'soil_health': '#795548' # brown
    }

    scenario_colors = {
        'scenario1': '#1f77b4',  # blue
        'scenario2': '#ff7f0e',  # orange
        'scenario3': '#2ca02c',  # green
        'scenario4': '#d62728',  # red
        'scenario5': '#9467bd',  # purple
        'scenario6': '#8c564b'   # brown
    }

    return variables, variable_names, variable_colors, scenario_colors


def _plot_variables(ax, history, variables, variable_names, variable_colors):
    """Plot time series for multiple variables"""
    for var in variables:
        if var in history:
            data = history[var]
            time_points = np.arange(len(data)) / 4.0  # convert to years
            ax.plot(time_points, data,
                    label=variable_names[var],
                    color=variable_colors[var],
                    linewidth=1.5)


def _add_chemical_stop_lines(ax, config):
    """Add vertical lines for chemical discontinuation years"""
    # Herbicide discontinuation year
    if config['herbicide_stop_year'] is not None:
        ax.axvline(x=config['herbicide_stop_year'],
                   color='red',
                   linestyle=':',
                   linewidth=1,
                   alpha=0.6)

    # Pesticide discontinuation year
    if config['pesticide_stop_year'] is not None:
        ax.axvline(x=config['pesticide_stop_year'],
                   color='blue',
                   linestyle=':',
                   linewidth=1,
                   alpha=0.6)


def _setup_axis_common(ax):
    """Set common axis properties"""
    ax.set_xlabel('Year', fontsize=10)
    ax.set_ylabel('Value', fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(0, 30)


def plot_scenario_comparison(results_dict, scenario_configs):
    """
    Plot comparison of key variables across 6 scenarios over 30 years.

    Parameters:
        results_dict: Dictionary containing simulation results for 6 scenarios
        scenario_configs: Dictionary of scenario configurations
    """
    # Get configurations
    variables, variable_names, variable_colors, _ = _setup_plotting_configs()

    # Create 6 subplots (one for each scenario)
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    fig.suptitle('30-Year Simulation Results: Comparison of 6 Agricultural Ecosystem Scenarios',
                 fontsize=16, fontweight='bold')

    # Iterate through 6 scenarios
    for idx, (scenario_key, history) in enumerate(results_dict.items()):
        # Determine subplot position
        row = idx // 3
        col = idx % 3

        ax = axes[row, col]
        scenario_name = scenario_configs[scenario_key]['name']

        # Plot variables
        _plot_variables(ax, history, variables, variable_names, variable_colors)

        # Add scenario name as subplot title
        ax.set_title(scenario_name, fontsize=12, fontweight='bold', pad=10)

        # Set axis properties
        _setup_axis_common(ax)

        # Add vertical lines for chemical discontinuation years
        config = scenario_configs[scenario_key]
        _add_chemical_stop_lines(ax, config)

        # Show legend only in the first subplot
        if idx == 0:
            ax.legend(loc='upper left', fontsize=9, framealpha=0.9)

    # Adjust layout and save
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig('scenario_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()


def plot_all_scenarios_together(results_dict, scenario_configs):
    """
    Compare the same variable across all 6 scenarios in a single plot.
    6 plots total, each showing one variable under all scenarios.
    """
    # Get configurations
    variables, variable_names, _, scenario_colors = _setup_plotting_configs()

    # Create 6 subplots
    fig, axes = plt.subplots(3, 2, figsize=(16, 14))
    fig.suptitle('Variable-wise Comparison Across 6 Scenarios',
                 fontsize=16, fontweight='bold')

    # Iterate through each variable
    for idx, var in enumerate(variables):
        row = idx // 2
        col = idx % 2
        ax = axes[row, col]

        # Plot this variable for each scenario
        for scenario_key, history in results_dict.items():
            if var in history:
                data = history[var]
                time_points = np.arange(len(data)) / 4.0
                scenario_name = scenario_configs[scenario_key]['name']

                ax.plot(time_points, data,
                        label=scenario_name,
                        color=scenario_colors.get(scenario_key, 'black'),
                        linewidth=1.5)

        ax.set_title(variable_names[var], fontsize=12, fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel(variable_names[var])
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 30)

        # Show legend only in the first subplot
        if idx == 0:
            ax.legend(loc='upper left', fontsize=8, framealpha=0.9)

    # Adjust layout and save
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig('all_scenarios_comparison_by_variable.png', dpi=300, bbox_inches='tight')
    plt.show()