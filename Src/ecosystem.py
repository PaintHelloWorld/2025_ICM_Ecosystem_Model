class AgroEcosystem:
    """Agricultural Ecosystem Model (Simplified Version)"""

    # Initial state constants
    INITIAL_STATES = {
        'crop': 0.0, 'weed': 30.0, 'pest': 5.0,
        'bird': 0.0, 'bat': 0.0, 'soil_nutrient': 50.0,
        'soil_health': 50.0, 'herbicide_residue': 0.0,
        'pesticide_residue': 0.0
    }

    # Base parameter constants
    PARAMS = {
        # Growth rates
        'r_crop': 0.8, 'r_weed': 0.6, 'r_pest': 0.5,
        'r_bird': 0.1, 'r_bat': 0.08,

        # Carrying capacities
        'K_crop': 300, 'K_weed': 100, 'K_pest': 80,
        'K_bird': 20, 'K_bat': 15,

        # Interaction coefficients
        'pest_on_crop': -0.5, 'bird_on_pest': -1.5,
        'bat_on_pest': -1.2, 'crop_weed_comp': -2.0,

        # Chemical parameters
        'herbicide_decay': 0.3, 'pesticide_decay': 0.25,
        'organic_fertilizer_effect': 0.2, 'chemical_fertilizer_effect': 0.3,
        'herbicide_effect': 0.7, 'pesticide_effect': 0.6,
        'predator_pesticide_mortality': 0.3
    }

    # Season factors
    SEASON_FACTORS = {'spring': 0.8, 'summer': 1.2, 'autumn': 0.9, 'winter': 0.3}

    def __init__(self, scenario_config):
        self.scenario = scenario_config
        self.year = 0
        self.states = self.INITIAL_STATES.copy()
        self.history = {key: [] for key in self.states.keys()}
        self.history['year'] = []
        self.history['season'] = []

    def simulate_year(self):
        """Simulate one year (four seasons)"""
        for season in ['spring', 'summer', 'autumn', 'winter']:
            self.seasonal_operations(season)
            self.update_populations(season)
            self.update_chemicals()
            self.record_state(season)
        self.year += 1

    def seasonal_operations(self, season):
        """Execute farming operations based on season"""
        if season == 'spring':
            self.handle_spring_operations()
        elif season == 'summer':
            self.handle_summer_operations()

    def handle_spring_operations(self):
        """Handle spring farming operations"""
        self.states['crop'] = 80.0

        if self.scenario['use_fertilizer']:
            self.apply_fertilizer()

    def apply_fertilizer(self):
        """Apply fertilizer"""
        is_organic = self.scenario.get('use_organic_fertilizer', False)

        if is_organic:
            self.states['soil_nutrient'] += 15
            self.states['soil_health'] = min(100, self.states['soil_health'] + 2)
        else:
            self.states['soil_nutrient'] += 30
            self.states['soil_health'] = max(0, self.states['soil_health'] - 1)

    def handle_summer_operations(self):
        """Handle summer farming operations"""
        if self.should_apply_chemical('pesticide'):
            self.apply_chemical('pesticide')
        if self.should_apply_chemical('herbicide'):
            self.apply_chemical('herbicide')
        else:
            self.apply_organic_weed_control()

    def should_apply_chemical(self, chemical_type):
        """Determine whether to apply chemical"""
        stop_year = self.scenario.get(f'{chemical_type}_stop_year')
        threshold = {'pesticide': 8, 'herbicide': 15}[chemical_type]
        state_key = 'pest' if chemical_type == 'pesticide' else 'weed'

        return (self.scenario[f'use_{chemical_type}'] and
                self.states[state_key] > threshold and
                (stop_year is None or self.year < stop_year))

    def apply_chemical(self, chemical_type):
        """Apply chemical (pesticide or herbicide)"""
        params = {
            'pesticide': {'residue': 'pesticide_residue', 'target': 'pest',
                          'effect': self.PARAMS['pesticide_effect']},
            'herbicide': {'residue': 'herbicide_residue', 'target': 'weed',
                          'effect': self.PARAMS['herbicide_effect']}
        }[chemical_type]

        # Set residue concentration
        self.states[params['residue']] = 50 if chemical_type == 'pesticide' else 40

        # Target population mortality
        self.states[params['target']] *= (1 - params['effect'])

        # Pesticide side effects on predators
        if chemical_type == 'pesticide':
            mortality = self.PARAMS['predator_pesticide_mortality']
            self.states['bird'] *= (1 - mortality)
            self.states['bat'] *= (1 - mortality)

    def apply_organic_weed_control(self):
        """Organic weed control methods"""
        weed = self.states['weed']

        # 1. Manual/mechanical weeding
        if weed > 20:
            efficiency = min(0.5, 0.25 + 0.03 * min(8, self.year))
            self.states['weed'] *= (1 - efficiency)

        # 2. Cover crop competition
        if self.scenario.get('use_cover_crop', False):
            self.states['weed'] *= 0.8

        # 3. Crop density suppression
        crop_density_effect = min(0.3, self.states['crop'] * 0.001)
        self.states['weed'] *= (1 - crop_density_effect)

        self.states['weed'] = max(0, self.states['weed'])

    def update_populations(self, season):
        """Update all populations"""
        growth_rates = self.calculate_growth_rates(season)

        for species, rate in growth_rates.items():
            if species in self.states:
                self.states[species] = max(0, self.states[species] + rate)

        self.handle_predator_recovery()

    def calculate_growth_rates(self, season):
        """Calculate growth rates"""
        C, W, P, B, T = (self.states['crop'], self.states['weed'],
                         self.states['pest'], self.states['bird'],
                         self.states['bat'])

        rates = {}

        # Crop growth rate
        rates['crop'] = self.calculate_crop_growth(C, W, P, season)

        # Weed growth rate
        rates['weed'] = self.calculate_weed_growth(W, C)

        # Pest growth rate
        rates['pest'] = self.calculate_pest_growth(P, B, T)

        # Bird growth rate
        rates['bird'] = self.calculate_bird_growth(B, P) if B > 0 else 0

        # Bat growth rate
        rates['bat'] = self.calculate_bat_growth(T, P) if T > 0 else 0

        # Apply season factors
        for key in ['crop', 'weed', 'pest', 'bird', 'bat']:
            if key in rates:
                rates[key] *= self.SEASON_FACTORS[season]

        return rates

    def calculate_crop_growth(self, C, W, P, season):
        """Calculate crop growth rate"""
        # Base logistic growth
        base = self.PARAMS['r_crop'] * C * (1 - C / self.PARAMS['K_crop'])

        # Negative effects (pests and weeds)
        pest_effect = min(0.6, abs(self.PARAMS['pest_on_crop']) * P * 0.02)
        weed_effect = min(0.5, abs(self.PARAMS['crop_weed_comp']) * W * 0.03)

        # Net growth rate
        net = max(0.05, base * (1 - pest_effect - weed_effect))

        # Soil health factor
        soil_factor = 0.5 + (self.states['soil_health'] / 100) * 0.5

        # Fertilizer bonus
        fertilizer_bonus = 0
        if self.scenario['use_fertilizer']:
            effect_type = 'organic' if self.scenario.get('use_organic_fertilizer') else 'chemical'
            effect = self.PARAMS[f'{effect_type}_fertilizer_effect']
            fertilizer_bonus = effect * self.states['soil_nutrient'] * 0.01

        return net * soil_factor + fertilizer_bonus

    def calculate_weed_growth(self, W, C):
        """Calculate weed growth rate"""
        base = self.PARAMS['r_weed'] * W * (1 - W / self.PARAMS['K_weed'])
        crop_competition = min(0.5, 0.05 + C * 0.001)
        herbicide_effect = -0.05 * self.states['herbicide_residue']

        return base * (1 - crop_competition) + herbicide_effect

    def calculate_pest_growth(self, P, B, T):
        """Calculate pest growth rate"""
        base = self.PARAMS['r_pest'] * P * (1 - P / self.PARAMS['K_pest'])

        # Predator predation efficiency
        bird_efficiency = min(0.6, 0.3 + 0.02 * self.year)
        bat_efficiency = min(0.5, 0.25 + 0.015 * self.year)

        predation = bird_efficiency * B * 0.05 + bat_efficiency * T * 0.04
        pesticide_effect = -0.01 * self.states['pesticide_residue']

        return base * (1 - predation) + pesticide_effect

    def calculate_bird_growth(self, B, P):
        """Calculate bird growth rate"""
        food_effect = min(0.2, P / 50.0)
        growth = self.PARAMS['r_bird'] * B * (1 - B / self.PARAMS['K_bird'])

        # Birds consume weed seeds
        self.states['weed'] *= (1 - min(0.1, B * 0.005))

        return growth * (1 + 0.5 * food_effect)

    def calculate_bat_growth(self, T, P):
        """Calculate bat growth rate"""
        food_effect = min(0.2, P / 50.0)
        return self.PARAMS['r_bat'] * T * (1 - T / self.PARAMS['K_bat']) * (1 + 0.4 * food_effect)

    def handle_predator_recovery(self):
        """Handle natural recovery or introduction of predators"""
        for predator in ['bird', 'bat']:
            if self.scenario[f'introduce_{predator}s']:
                self.update_predator_population(predator)

    def update_predator_population(self, predator):
        """Update specific predator population"""
        if self.states[predator] == 0:
            # Initial introduction
            self.states[predator] = 2.0 if predator == 'bird' else 1.5
        else:
            # Logistic growth
            current = self.states[predator]
            r = self.PARAMS[f'r_{predator}']
            K = self.PARAMS[f'K_{predator}']
            pest_effect = min(0.3, self.states['pest'] / 100.0)

            growth = r * current * (1 - current / K) * (1 + pest_effect)
            self.states[predator] += growth * 0.5  # Quarterly growth rate

    def update_chemicals(self):
        """Update chemical residues"""
        # Pesticide degradation
        self.states['pesticide_residue'] *= (1 - self.PARAMS['pesticide_decay'])
        self.states['herbicide_residue'] *= (1 - self.PARAMS['herbicide_decay'])

        # Nutrient consumption
        self.states['soil_nutrient'] *= 0.9

    def record_state(self, season):
        """Record current state"""
        for key in self.states:
            self.history[key].append(self.states[key])
        self.history['year'].append(self.year)
        self.history['season'].append(season)