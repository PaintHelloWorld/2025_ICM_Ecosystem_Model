import numpy as np
from matplotlib import pyplot as plt

plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# Constant definitions
SCORING_PARAMS = {
    'weights': {'ecological': 0.4, 'economic': 0.3, 'sustainability': 0.3},
    'cost_factors': {'herbicide': 15, 'pesticide': 20, 'bird': 5, 'bat': 3, 'labor': 10},
    'thresholds': {'high_stability': 80, 'low_stability': 60, 'high_biodiversity': 70, 'low_biodiversity': 40}
}


def extract_annual_data(history, n_years=30):
    """Extract annual data from quarterly data"""
    return {k: [v[i * 4 + 3] for i in range(n_years)] for k, v in history.items()}


def calculate_ecological_scores(annual_data):
    """Calculate ecological dimension scores"""
    last_5 = {k: v[-5:] for k, v in annual_data.items()}
    last_10 = {k: v[-10:] for k, v in annual_data.items()}

    stability = 100 - (np.std(last_10['crop']) / np.mean(last_10['crop']) * 100)
    biodiversity = min(100, (np.mean(last_5['bird']) * 2 + np.mean(last_5['bat']) * 3) / 50 * 100)
    pest_control = max(0, 100 - np.mean(last_5['pest']) / 80 * 100)
    weed_management = max(0, 100 - np.mean(last_5['weed']) / 100 * 100)

    return {
        'productivity_stability': stability,
        'biodiversity': biodiversity,
        'pest_control': pest_control,
        'weed_management': weed_management,
        'soil_health': annual_data['soil_health'][-1],
        'chemical_free': 100 - min(100, (annual_data['herbicide_residue'][-1] +
                                         annual_data['pesticide_residue'][-1]) / 50 * 100)
    }


def calculate_economic_scores(annual_data, config):
    """Calculate economic dimension scores"""
    avg_yield = np.mean(annual_data['crop'][-10:])

    # Cost calculation
    costs = sum([
        SCORING_PARAMS['cost_factors']['herbicide'] if config['use_herbicide'] else 0,
        SCORING_PARAMS['cost_factors']['pesticide'] if config['use_pesticide'] else 0,
        SCORING_PARAMS['cost_factors']['bird'] if config['introduce_birds'] else 0,
        SCORING_PARAMS['cost_factors']['bat'] if config['introduce_bats'] else 0,
        SCORING_PARAMS['cost_factors']['labor'] if not config['use_herbicide'] and annual_data['weed'][-1] > 20 else 0
    ])

    cost_efficiency = (avg_yield / costs * 10) if costs > 0 else (avg_yield * 15)

    return {
        'yield': avg_yield,
        'cost_efficiency': min(100, cost_efficiency)
    }


def calculate_sustainability_scores(annual_data):
    """Calculate sustainability dimension scores"""
    crop_series = annual_data['crop']
    soil_series = annual_data['soil_health'][::4]  # One point per year

    return {
        'soil_trend': calculate_trend(soil_series),
        'resilience': calculate_resilience(crop_series[-5:]),
        'long_term_productivity': calculate_productivity_change(crop_series),
        'equilibrium': 100 - (np.std(crop_series[-5:]) / 50 * 100)
    }


def calculate_trend(data):
    """Calculate trend of data"""
    if len(data) < 2:
        return 0
    slope, _ = np.polyfit(range(len(data)), data, 1)
    return slope * 10


def calculate_resilience(data):
    """Calculate system resilience"""
    if len(data) < 3:
        return 50
    corr = np.corrcoef(data[:-1], data[1:])[0, 1]
    return ((corr + 1) / 2 * 100) if not np.isnan(corr) else 50


def calculate_productivity_change(crop_series):
    """Calculate long-term productivity change"""
    first_10, last_10 = crop_series[:10], crop_series[-10:]
    return (np.mean(last_10) / np.mean(first_10) * 100) if np.mean(first_10) > 0 else 0


def generate_evaluation_summary(scores):
    """Generate text summary"""
    summaries = []
    thresholds = SCORING_PARAMS['thresholds']

    stability = scores['ecological']['productivity_stability']
    biodiversity = scores['ecological']['biodiversity']
    soil_trend = scores['sustainability']['soil_trend']

    if stability > thresholds['high_stability']:
        summaries.append("Highly stable yield")
    elif stability < thresholds['low_stability']:
        summaries.append("Significant yield fluctuation")

    if biodiversity > thresholds['high_biodiversity']:
        summaries.append("Good biodiversity")
    elif biodiversity < thresholds['low_biodiversity']:
        summaries.append("Insufficient biodiversity")

    if soil_trend > 0.5:
        summaries.append("Soil health improving")
    elif soil_trend < -0.5:
        summaries.append("Soil degradation")

    return "; ".join(summaries) if summaries else "System status average"


def evaluate_scenario_results(history, scenario_name="", config=None):
    """Perform multi-dimensional evaluation of simulation results"""
    annual_data = extract_annual_data(history)

    # Calculate dimension scores
    ecological = calculate_ecological_scores(annual_data)
    economic = calculate_economic_scores(annual_data, config) if config else {'yield': 0, 'cost_efficiency': 0}
    sustainability = calculate_sustainability_scores(annual_data)

    # Calculate comprehensive score
    scores = {
        'ecological': np.mean(list(ecological.values())) / 100,
        'economic': economic['cost_efficiency'] / 100,
        'sustainability': np.mean(list(sustainability.values())) / 100
    }

    overall_score = sum(scores[k] * SCORING_PARAMS['weights'][k]
                        for k in SCORING_PARAMS['weights']) * 100

    return {
        'scenario_name': scenario_name,
        'ecological': ecological,
        'economic': economic,
        'sustainability': sustainability,
        'overall_score': min(100, overall_score),
        'summary': generate_evaluation_summary({'ecological': ecological, 'sustainability': sustainability})
    }


def plot_result_evaluation(evaluation_results):
    """Visualize result evaluation"""
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.suptitle('Scenario Evaluation Results Comparison', fontsize=16, fontweight='bold')

    # Extract data
    names = [r['scenario_name'] for r in evaluation_results]
    scores = [r['overall_score'] for r in evaluation_results]

    # Create bar chart
    colors = plt.cm.Set3(np.linspace(0, 1, len(names)))
    bars = ax.bar(range(len(names)), scores, color=colors)

    # Set chart properties
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, ha='right')
    ax.set_ylabel('Comprehensive Score (0-100)')
    ax.set_title('Comprehensive Score Comparison', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    # Add value labels
    for bar, score in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f'{score:.1f}', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig('scenario_evaluation.png', dpi=300, bbox_inches='tight')
    plt.show()