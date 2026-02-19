from ecosystem import AgroEcosystem
from visualization import plot_scenario_comparison, plot_all_scenarios_together
from evaluation import evaluate_scenario_results, plot_result_evaluation

import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)


def create_scenarios():
    """Create configurations for 6 scenarios"""
    scenarios = [
        # ============ Baseline Scenario ============
        {
            'id': 'scenario1',
            'name': 'Conventional Agriculture (High Chemical Input)',
            'use_herbicide': True, 'use_pesticide': True, 'use_fertilizer': True,
            'introduce_bats': False, 'introduce_birds': False,
            'herbicide_stop_year': None, 'pesticide_stop_year': None,
            'use_organic_fertilizer': False, 'use_cover_crop': False
        },

        # ============ Single Intervention Tests ============
        {
            'id': 'scenario2',
            'name': 'Chemical Removal Only (No Natural Predators)',
            'use_herbicide': True, 'use_pesticide': True, 'use_fertilizer': True,
            'introduce_bats': False, 'introduce_birds': False,
            'herbicide_stop_year': 3, 'pesticide_stop_year': 2,
            'use_organic_fertilizer': False, 'use_cover_crop': False
        },
        {
            'id': 'scenario3',
            'name': 'Chemical Removal + Bat Introduction',
            'use_herbicide': True, 'use_pesticide': True, 'use_fertilizer': True,
            'introduce_bats': True, 'introduce_birds': False,
            'herbicide_stop_year': 3, 'pesticide_stop_year': 2,
            'use_organic_fertilizer': False, 'use_cover_crop': True
        },
        {
            'id': 'scenario4',
            'name': 'Chemical Removal + Bird Introduction',
            'use_herbicide': True, 'use_pesticide': True, 'use_fertilizer': True,
            'introduce_bats': False, 'introduce_birds': True,
            'herbicide_stop_year': 3, 'pesticide_stop_year': 2,
            'use_organic_fertilizer': False, 'use_cover_crop': True
        },

        # ============ Complete Organic Farming Solutions ============
        {
            'id': 'scenario5',
            'name': 'Gradual Organic Transition',
            'use_herbicide': True, 'use_pesticide': True, 'use_fertilizer': True,
            'introduce_bats': True, 'introduce_birds': True,
            'herbicide_stop_year': 4, 'pesticide_stop_year': 2,
            'use_organic_fertilizer': True, 'use_cover_crop': True
        },
        {
            'id': 'scenario6',
            'name': 'Radical Organic (From Beginning)',
            'use_herbicide': False, 'use_pesticide': False, 'use_fertilizer': False,
            'introduce_bats': True, 'introduce_birds': True,
            'herbicide_stop_year': None, 'pesticide_stop_year': None,
            'use_organic_fertilizer': True, 'use_cover_crop': True
        }
    ]
    return {s['id']: s for s in scenarios}


def run_simulation(scenario_config, years=30):
    """Run simulation for a single scenario"""
    ecosystem = AgroEcosystem(scenario_config)
    for year in range(years):
        ecosystem.simulate_year()
    return ecosystem.history


def print_simulation_progress(scenario_name, history):
    """Print simulation progress information"""
    print(f"✓ Completed: {scenario_name}")
    print(f"  Final Crop Yield: {history['crop'][-1]:.1f}")
    print(f"  Final Bird Density: {history['bird'][-1]:.1f}")
    print(f"  Final Bat Density: {history['bat'][-1]:.1f}")
    print("-" * 40)


def print_final_summary(results, scenarios):
    """Print final results summary"""
    print("Final Results Summary (30th Year):")
    print("-" * 80)
    print(f"{'Scenario Name':<35} {'Crop Yield':<12} {'Bird Density':<12} {'Bat Density':<12} {'Pest Density':<12}")
    print("-" * 80)

    for key, config in scenarios.items():
        h = results[key]
        print(f"{config['name']:<35} {h['crop'][-1]:<12.1f} {h['bird'][-1]:<12.1f} "
              f"{h['bat'][-1]:<12.1f} {h['pest'][-1]:<12.1f}")


def main():
    """Main function: Run six scenarios and generate visualizations"""
    scenarios = create_scenarios()
    results = {}
    evaluations = []

    # Run all scenarios
    print("=" * 60)
    print("Starting Agricultural Ecosystem Scenario Simulations...")

    for key, config in scenarios.items():
        print(f"\nSimulating: {config['name']}")
        results[key] = run_simulation(config)
        print_simulation_progress(config['name'], results[key])

        # Evaluate current scenario
        eval_result = evaluate_scenario_results(results[key], config['name'], config)
        evaluations.append(eval_result)

    # Generate visualizations
    print("\n" + "=" * 60)
    print("Simulation completed! Generating visualization charts...")
    print("\n1. Generating six-scenario comparison plot (one subplot per scenario)...")
    plot_scenario_comparison(results, scenarios)

    print("\n2. Generating variable comparison plot (same variable across scenarios)...")
    plot_all_scenarios_together(results, scenarios)

    print("\n3. Generating result evaluation plot...")
    plot_result_evaluation(evaluations)

    # Print final summary
    print_final_summary(results, scenarios)
    print("\n" + "=" * 60)
    print("All analyses completed!")


if __name__ == "__main__":
    main()