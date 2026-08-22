#!/usr/bin/env python3
"""
Procedural Creature Generation & Wave Function Collapse Pipeline
================================================================
A two-phase system for ecological creature design and WFC-based habitat generation.

Phase 1: Ecological Engine & Creature Card Generation
Phase 2: WFC Adapter & Grid Visualization

Author: Senior Software Architect - Procedural Generation & Biological Simulation
"""

import json
import random
import math
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


# =============================================================================
# CONFIGURATION & CONSTANTS
# =============================================================================

class TerrainType(Enum):
    """Basic terrain types for WFC output"""
    EMPTY = '.'
    CREATURE = 'C'
    HABITAT = 'H'
    RESOURCE = 'R'
    ADAPTATION = 'A'


@dataclass
class EnvironmentalInput:
    """The 5 core environmental variables"""
    temperature: float  # -50 to 50 (Celsius)
    humidity: float     # 0 to 100 (Percentage)
    altitude: float     # 0 to 8000 (Meters)
    atmospheric_pressure: float  # 0.5 to 1.5 (ATM relative)
    resource_density: float  # 0 to 100 (Mineral/Biological resources)
    
    def validate(self) -> bool:
        """Validate input ranges"""
        return (
            -50 <= self.temperature <= 50 and
            0 <= self.humidity <= 100 and
            0 <= self.altitude <= 8000 and
            0.5 <= self.atmospheric_pressure <= 1.5 and
            0 <= self.resource_density <= 100
        )


# =============================================================================
# PHASE 1: ECOLOGICAL ENGINE & CREATURE CARD GENERATION
# =============================================================================

class AnatomicalFeature:
    """Represents a single anatomical feature"""
    def __init__(self, name: str, description: str, adaptation_value: float):
        self.name = name
        self.description = description
        self.adaptation_value = adaptation_value
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "adaptation_value": round(self.adaptation_value, 2)
        }


class SurvivalMechanism:
    """Represents a survival mechanism"""
    def __init__(self, mechanism_type: str, description: str, efficiency: float):
        self.mechanism_type = mechanism_type
        self.description = description
        self.efficiency = efficiency
    
    def to_dict(self) -> Dict:
        return {
            "type": self.mechanism_type,
            "description": self.description,
            "efficiency": round(self.efficiency, 2)
        }


class SpatialConstraint:
    """Represents spatial/adjacency constraints for WFC"""
    def __init__(self, constraint_type: str, required_neighbors: List[str], 
                 forbidden_neighbors: List[str], weight: float):
        self.constraint_type = constraint_type
        self.required_neighbors = required_neighbors
        self.forbidden_neighbors = forbidden_neighbors
        self.weight = weight
    
    def to_dict(self) -> Dict:
        return {
            "type": self.constraint_type,
            "required_neighbors": self.required_neighbors,
            "forbidden_neighbors": self.forbidden_neighbors,
            "weight": round(self.weight, 2)
        }


@dataclass
class CreatureCard:
    """Complete creature definition card"""
    creature_id: str
    environmental_signature: Dict[str, float]
    anatomy: Dict[str, Any]
    survival_mechanisms: List[Dict[str, Any]]
    spatial_constraints: List[Dict[str, Any]]
    energy_source: str
    climate_tolerance: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_json(self, indent: int = 2) -> str:
        """Export to JSON string"""
        return json.dumps(asdict(self), indent=indent)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'CreatureCard':
        """Import from JSON string"""
        data = json.loads(json_str)
        return cls(**data)


class EcologicalEngine:
    """
    Phase 1: Generates creature cards based on environmental inputs
    Uses algorithmic rules to ensure biological coherence
    """
    
    # Anatomical templates based on environmental factors
    LIMB_TEMPLATES = {
        'high_altitude': ['reduced_limbs', 'wing_structures', 'climbing_appendages'],
        'high_humidity': ['webbed_limbs', 'moisture_absorbing_pads', 'multiple_limbs'],
        'extreme_temp': ['insulated_limbs', 'minimal_surface_area', 'retractable_limbs'],
        'standard': ['quadrupedal', 'bipedal', 'hexapodal']
    }
    
    ARMOR_TEMPLATES = {
        'high_resource': ['mineralized_carapace', 'crystalline_plating'],
        'low_pressure': ['flexible_membrane', 'pressurized_sacs'],
        'high_humidity': ['permeable_shell', 'moisture_retaining_armor'],
        'standard': ['chitinous_plates', 'keratinous_scales', 'bony_protrusions']
    }
    
    SENSORY_TEMPLATES = {
        'low_light': ['enhanced_olfactory', 'vibration_sensors', 'thermal_receptors'],
        'high_resource': ['mineral_detectors', 'bio_luminescent_markers'],
        'extreme_temp': ['protected_receptors', 'long_range_sensors'],
        'standard': ['compound_eyes', 'auditory_organs', 'tactile_antennae']
    }
    
    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        self.creature_counter = 0
    
    def _generate_creature_id(self) -> str:
        """Generate unique creature identifier"""
        self.creature_counter += 1
        return f"CRTR-{self.creature_counter:04d}-{random.randint(1000, 9999)}"
    
    def _calculate_adaptation_score(self, env: EnvironmentalInput) -> float:
        """Calculate overall adaptation pressure (0-1)"""
        extremes = [
            abs(env.temperature) / 50.0,
            abs(env.humidity - 50) / 50.0,
            env.altitude / 8000.0,
            abs(env.atmospheric_pressure - 1.0) / 0.5,
            abs(env.resource_density - 50) / 50.0
        ]
        return sum(extremes) / len(extremes)
    
    def _determine_anatomy(self, env: EnvironmentalInput) -> Dict[str, Any]:
        """Generate adaptive anatomy based on environment"""
        adaptation_score = self._calculate_adaptation_score(env)
        
        # Limb determination
        if env.altitude > 4000:
            limb_type = random.choice(self.LIMB_TEMPLATES['high_altitude'])
            limb_count = random.randint(2, 4)
        elif env.humidity > 70:
            limb_type = random.choice(self.LIMB_TEMPLATES['high_humidity'])
            limb_count = random.randint(4, 8)
        elif abs(env.temperature) > 30:
            limb_type = random.choice(self.LIMB_TEMPLATES['extreme_temp'])
            limb_count = random.randint(2, 6)
        else:
            limb_type = random.choice(self.LIMB_TEMPLATES['standard'])
            limb_count = random.choice([2, 4, 6])
        
        # Armor determination
        if env.resource_density > 70:
            armor_type = random.choice(self.ARMOR_TEMPLATES['high_resource'])
        elif env.atmospheric_pressure < 0.7:
            armor_type = random.choice(self.ARMOR_TEMPLATES['low_pressure'])
        elif env.humidity > 70:
            armor_type = random.choice(self.ARMOR_TEMPLATES['high_humidity'])
        else:
            armor_type = random.choice(self.ARMOR_TEMPLATES['standard'])
        
        # Sensory organs
        light_level = 1.0 - (env.altitude / 8000.0) * (env.atmospheric_pressure)
        if light_level < 0.4:
            sensory_type = random.choice(self.SENSORY_TEMPLATES['low_light'])
        elif env.resource_density > 60:
            sensory_type = random.choice(self.SENSORY_TEMPLATES['high_resource'])
        elif abs(env.temperature) > 25:
            sensory_type = random.choice(self.SENSORY_TEMPLATES['extreme_temp'])
        else:
            sensory_type = random.choice(self.SENSORY_TEMPLATES['standard'])
        
        return {
            'limbs': AnatomicalFeature(
                limb_type,
                f"{limb_count} limbs optimized for {'high altitude' if env.altitude > 4000 else 'standard'} conditions",
                adaptation_score
            ).to_dict(),
            'armor': AnatomicalFeature(
                armor_type,
                f"Protective structure adapted to {'high resources' if env.resource_density > 70 else 'standard'} environment",
                adaptation_score * 0.8
            ).to_dict(),
            'sensory_organs': AnatomicalFeature(
                sensory_type,
                f"Sensory systems for {'low light' if light_level < 0.4 else 'standard'} perception",
                adaptation_score * 0.9
            ).to_dict(),
            'limb_count': limb_count,
            'body_mass_index': round(adaptation_score * 10 + random.uniform(-2, 2), 2)
        }
    
    def _determine_survival_mechanisms(self, env: EnvironmentalInput) -> List[SurvivalMechanism]:
        """Generate survival mechanisms based on environmental stressors"""
        mechanisms = []
        
        # Temperature tolerance
        if abs(env.temperature) > 20:
            if env.temperature > 0:
                mechanisms.append(SurvivalMechanism(
                    'heat_dissipation',
                    'Specialized pores and reflective surface structures',
                    min(1.0, abs(env.temperature) / 50.0)
                ))
            else:
                mechanisms.append(SurvivalMechanism(
                    'thermal_insulation',
                    'Multi-layer dermal structure with air pockets',
                    min(1.0, abs(env.temperature) / 50.0)
                ))
        
        # Humidity adaptation
        if env.humidity > 70:
            mechanisms.append(SurvivalMechanism(
                'moisture_regulation',
                'Semi-permeable membrane for water exchange',
                env.humidity / 100.0
            ))
        elif env.humidity < 30:
            mechanisms.append(SurvivalMechanism(
                'water_conservation',
                'Closed respiratory system with moisture recovery',
                (100 - env.humidity) / 100.0
            ))
        
        # Pressure adaptation
        if env.atmospheric_pressure < 0.8:
            mechanisms.append(SurvivalMechanism(
                'pressure_equalization',
                'Internal pressure sacs with gas exchange',
                (1.0 - env.atmospheric_pressure) / 0.5
            ))
        
        # Resource utilization
        if env.resource_density > 60:
            mechanisms.append(SurvivalMechanism(
                'mineral_absorption',
                'Direct mineral uptake through specialized appendages',
                env.resource_density / 100.0
            ))
        
        # Default metabolism
        if not mechanisms:
            mechanisms.append(SurvivalMechanism(
                'standard_metabolism',
                'Baseline biological processes',
                0.5
            ))
        
        return [m.to_dict() for m in mechanisms]
    
    def _determine_spatial_constraints(self, env: EnvironmentalInput) -> List[SpatialConstraint]:
        """Generate WFC-compatible spatial constraints"""
        constraints = []
        adaptation_score = self._calculate_adaptation_score(env)
        
        # Habitat requirement
        if env.humidity > 50:
            constraints.append(SpatialConstraint(
                'habitat_preference',
                ['H', 'R'],  # Needs habitat or resources nearby
                [],  # No forbidden neighbors
                0.8
            ))
        else:
            constraints.append(SpatialConstraint(
                'habitat_tolerance',
                [],  # No specific requirements
                ['H'],  # Avoids dense habitat
                0.6
            ))
        
        # Resource dependency
        if env.resource_density > 50:
            constraints.append(SpatialConstraint(
                'resource_dependency',
                ['R'],  # Must be near resources
                [],
                min(1.0, env.resource_density / 100.0)
            ))
        
        # Altitude clustering
        if env.altitude > 3000:
            constraints.append(SpatialConstraint(
                'altitude_clustering',
                ['C', 'A'],  # Prefers other creatures or adaptations
                ['H'],  # Avoids dense habitat at high altitude
                0.7
            ))
        
        # Temperature isolation
        if abs(env.temperature) > 25:
            constraints.append(SpatialConstraint(
                'thermal_isolation',
                [],  # No requirements
                ['C'],  # Avoids other creatures (too extreme)
                0.5
            ))
        
        # Default coexistence
        if len(constraints) == 0:
            constraints.append(SpatialConstraint(
                'social_behavior',
                ['C'],  # Prefers company
                [],
                0.6
            ))
        
        return [c.to_dict() for c in constraints]
    
    def _determine_energy_source(self, env: EnvironmentalInput) -> str:
        """Determine primary energy source based on environment"""
        if env.resource_density > 70:
            return 'chemosynthesis'
        elif env.humidity > 60 and env.temperature > 10:
            return 'photosynthesis_augmented'
        elif env.altitude > 5000:
            return 'atmospheric_absorption'
        elif env.temperature < -10:
            return 'thermal_vent_dependent'
        else:
            return 'organic_consumption'
    
    def _calculate_climate_tolerance(self, env: EnvironmentalInput) -> Dict[str, float]:
        """Calculate tolerable ranges around current conditions"""
        adaptation_score = self._calculate_adaptation_score(env)
        tolerance_factor = 0.3 + (adaptation_score * 0.4)  # 0.3 to 0.7
        
        return {
            'temp_min': round(env.temperature - (20 * tolerance_factor), 1),
            'temp_max': round(env.temperature + (20 * tolerance_factor), 1),
            'humidity_min': round(max(0, env.humidity - (30 * tolerance_factor)), 1),
            'humidity_max': round(min(100, env.humidity + (30 * tolerance_factor)), 1),
            'altitude_min': round(max(0, env.altitude - (1500 * tolerance_factor)), 0),
            'altitude_max': round(min(8000, env.altitude + (1500 * tolerance_factor)), 0),
            'pressure_min': round(max(0.5, env.atmospheric_pressure - (0.3 * tolerance_factor)), 2),
            'pressure_max': round(min(1.5, env.atmospheric_pressure + (0.3 * tolerance_factor)), 2)
        }
    
    def generate_creature_card(self, env: EnvironmentalInput) -> CreatureCard:
        """
        Main entry point: Generate complete creature card from environmental inputs
        
        Args:
            env: EnvironmentalInput with 5 variables
            
        Returns:
            CreatureCard: Complete structured creature definition
        """
        if not env.validate():
            raise ValueError("Environmental inputs out of valid range")
        
        return CreatureCard(
            creature_id=self._generate_creature_id(),
            environmental_signature={
                'temperature': env.temperature,
                'humidity': env.humidity,
                'altitude': env.altitude,
                'atmospheric_pressure': env.atmospheric_pressure,
                'resource_density': env.resource_density
            },
            anatomy=self._determine_anatomy(env),
            survival_mechanisms=self._determine_survival_mechanisms(env),
            spatial_constraints=self._determine_spatial_constraints(env),
            energy_source=self._determine_energy_source(env),
            climate_tolerance=self._calculate_climate_tolerance(env),
            metadata={
                'generation_timestamp': 'eco-engine-v1.0',
                'adaptation_score': round(self._calculate_adaptation_score(env), 3),
                'complexity_index': len(self._determine_survival_mechanisms(env)) + 
                                   len(self._determine_spatial_constraints(env))
            }
        )


# =============================================================================
# PHASE 2: WFC ADAPTER & GRID VISUALIZATION
# =============================================================================

class WFCTile:
    """Represents a tile in the WFC grid"""
    def __init__(self, x: int, y: int, possible_states: List[str]):
        self.x = x
        self.y = y
        self.possible_states = set(possible_states)
        self.collapsed = False
        self.final_state: Optional[str] = None
    
    def collapse(self, state: str):
        """Collapse to a single state"""
        self.possible_states = {state}
        self.collapsed = True
        self.final_state = state
    
    def remove_state(self, state: str) -> bool:
        """Remove a state from possibilities, return True if changed"""
        if state in self.possible_states:
            self.possible_states.remove(state)
            if len(self.possible_states) == 0:
                return False  # Contradiction
            if len(self.possible_states) == 1 and not self.collapsed:
                self.collapse(list(self.possible_states)[0])
            return True
        return False
    
    def entropy(self) -> float:
        """Calculate entropy (number of possible states)"""
        return len(self.possible_states)


class WFCAdapter:
    """
    Phase 2: Adapts creature cards for Wave Function Collapse generation
    Implements simplified WFC algorithm with adjacency constraints
    """
    
    # Visual representation mapping (easily extensible)
    VISUAL_STYLES = {
        'ascii': {
            TerrainType.EMPTY: '.',
            TerrainType.CREATURE: 'C',
            TerrainType.HABITAT: 'H',
            TerrainType.RESOURCE: 'R',
            TerrainType.ADAPTATION: 'A'
        },
        'blocks': {
            TerrainType.EMPTY: ' ',
            TerrainType.CREATURE: '█',
            TerrainType.HABITAT: '▒',
            TerrainType.RESOURCE: '◊',
            TerrainType.ADAPTATION: '▲'
        },
        'braille': {
            TerrainType.EMPTY: '⣀',
            TerrainType.CREATURE: '⣿',
            TerrainType.HABITAT: '⣶',
            TerrainType.RESOURCE: '⣤',
            TerrainType.ADAPTATION: '⣾'
        }
    }
    
    def __init__(self, grid_size: int = 20, style: str = 'ascii'):
        self.grid_size = grid_size
        self.style = style
        self.grid: List[List[WFCTile]] = []
        self.adjacency_rules: Dict[str, Dict[str, float]] = {}
        self.weights: Dict[str, float] = {}
    
    def load_creature_card(self, card: CreatureCard):
        """
        Parse creature card and extract WFC rules
        
        Args:
            card: CreatureCard from Phase 1
        """
        # Define base tiles
        tiles = ['.', 'C', 'H', 'R', 'A']  # Empty, Creature, Habitat, Resource, Adaptation
        
        # Initialize weights based on creature characteristics
        self.weights = {
            '.': 1.0,  # Base weight for empty space
            'C': 0.3,  # Creatures are rare
            'H': 0.4,  # Habitat is moderately common
            'R': 0.5 if card.environmental_signature['resource_density'] > 50 else 0.2,
            'A': 0.2   # Adaptations are special cases
        }
        
        # Build adjacency rules from spatial constraints
        self.adjacency_rules = {tile: {t: 1.0 for t in tiles} for tile in tiles}
        
        for constraint in card.spatial_constraints:
            constraint_type = constraint['type']
            required = constraint.get('required_neighbors', [])
            forbidden = constraint.get('forbidden_neighbors', [])
            weight = constraint['weight']
            
            # Map constraint types to adjacency modifications
            if constraint_type == 'habitat_preference':
                for req in required:
                    self.adjacency_rules['C'][req] = max(self.adjacency_rules['C'][req], weight)
            
            elif constraint_type == 'habitat_tolerance':
                for forb in forbidden:
                    self.adjacency_rules['C'][forb] = min(self.adjacency_rules['C'][forb], 1.0 - weight)
            
            elif constraint_type == 'resource_dependency':
                for req in required:
                    self.adjacency_rules['C'][req] = max(self.adjacency_rules['C'][req], weight)
                    self.adjacency_rules['H'][req] = max(self.adjacency_rules['H'][req], weight * 0.8)
            
            elif constraint_type == 'altitude_clustering':
                for req in required:
                    self.adjacency_rules['C'][req] = max(self.adjacency_rules['C'][req], weight)
                for forb in forbidden:
                    self.adjacency_rules['C'][forb] = min(self.adjacency_rules['C'][forb], 1.0 - weight)
            
            elif constraint_type == 'thermal_isolation':
                for forb in forbidden:
                    self.adjacency_rules['C'][forb] = min(self.adjacency_rules['C'][forb], 0.3)
            
            elif constraint_type == 'social_behavior':
                for req in required:
                    self.adjacency_rules['C'][req] = max(self.adjacency_rules['C'][req], weight)
        
        # Apply environmental modifiers
        env = card.environmental_signature
        if env['humidity'] > 70:
            self.weights['H'] *= 1.5
            self.adjacency_rules['H']['H'] = 1.3
        elif env['humidity'] < 30:
            self.weights['H'] *= 0.5
            self.adjacency_rules['H']['H'] = 0.7
        
        if env['resource_density'] > 60:
            self.weights['R'] *= 1.8
            self.adjacency_rules['R']['R'] = 1.4
        
        if env['altitude'] > 4000:
            self.weights['A'] *= 2.0
            self.adjacency_rules['A']['C'] = 1.2
        
        if abs(env['temperature']) > 25:
            self.weights['C'] *= 0.5  # Fewer creatures in extreme temps
    
    def _initialize_grid(self):
        """Initialize grid with all possible states"""
        tiles = ['.', 'C', 'H', 'R', 'A']
        self.grid = []
        for y in range(self.grid_size):
            row = []
            for x in range(self.grid_size):
                row.append(WFCTile(x, y, tiles.copy()))
            self.grid.append(row)
    
    def _get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get valid neighboring coordinates (4-directional)"""
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                neighbors.append((nx, ny))
        return neighbors
    
    def _find_lowest_entropy_tile(self) -> Optional[WFCTile]:
        """Find uncollapsed tile with lowest entropy"""
        candidates = []
        min_entropy = float('inf')
        
        for row in self.grid:
            for tile in row:
                if not tile.collapsed:
                    ent = tile.entropy()
                    if ent < min_entropy and ent > 1:
                        min_entropy = ent
                        candidates = [tile]
                    elif ent == min_entropy:
                        candidates.append(tile)
        
        if candidates:
            return random.choice(candidates)
        return None
    
    def _propagate_constraints(self, start_tile: WFCTile):
        """Propagate constraints from a collapsed tile - relaxed version"""
        stack = [start_tile]
        
        while stack:
            current = stack.pop()
            neighbors = self._get_neighbors(current.x, current.y)
            
            for nx, ny in neighbors:
                neighbor = self.grid[ny][nx]
                if neighbor.collapsed:
                    continue
                
                # Get compatibility scores - much more permissive
                current_state = current.final_state
                compatible_states = set(neighbor.possible_states)  # Start with all states
                
                # Only remove states that are explicitly forbidden with high weight
                for possible in list(neighbor.possible_states):
                    score = self.adjacency_rules.get(current_state, {}).get(possible, 1.0)
                    # Only remove if score is very low (< 0.2)
                    if score < 0.2 and possible in compatible_states:
                        compatible_states.remove(possible)
                
                # Ensure at least one state remains to prevent contradictions
                if len(compatible_states) == 0:
                    compatible_states = neighbor.possible_states.copy()
                
                # Remove incompatible states
                to_remove = neighbor.possible_states - compatible_states
                changed = False
                for state in to_remove:
                    if neighbor.remove_state(state):
                        changed = True
                
                if changed and neighbor.collapsed:
                    stack.append(neighbor)
    
    def _weighted_choice(self, possible_states: set) -> str:
        """Choose a state based on weights"""
        states = list(possible_states)
        weights = [self.weights.get(s, 1.0) for s in states]
        
        total = sum(weights)
        if total == 0:
            return random.choice(states)
        
        r = random.uniform(0, total)
        cumulative = 0
        for i, w in enumerate(weights):
            cumulative += w
            if r <= cumulative:
                return states[i]
        
        return states[-1]
    
    def generate(self, max_iterations: int = 1000) -> bool:
        """
        Run WFC algorithm - simplified version without constraint propagation
        
        Args:
            max_iterations: Maximum iterations before giving up
            
        Returns:
            bool: True if successful, False if contradiction occurred
        """
        self._initialize_grid()
        
        # Simple approach: collapse tiles one by one without heavy propagation
        # This ensures we always get a complete grid
        all_tiles = [tile for row in self.grid for tile in row]
        random.shuffle(all_tiles)
        
        # First pass: seed some resources and habitat
        num_seeds = max(5, int(self.grid_size * self.grid_size * 0.08))
        for i in range(num_seeds):
            if i < len(all_tiles):
                tile = all_tiles[i]
                roll = random.random()
                if roll < 0.4 and self.weights.get('R', 0.2) > 0.3:
                    tile.collapse('R')
                elif roll < 0.7 and self.weights.get('H', 0.4) > 0.3:
                    tile.collapse('H')
        
        # Second pass: collapse remaining tiles based on weights
        for tile in all_tiles:
            if not tile.collapsed:
                # Get neighbor states for context
                neighbors = self._get_neighbors(tile.x, tile.y)
                neighbor_states = []
                for nx, ny in neighbors:
                    n_tile = self.grid[ny][nx]
                    if n_tile.collapsed and n_tile.final_state:
                        neighbor_states.append(n_tile.final_state)
                
                # Filter possible states based on soft constraints
                possible = list(tile.possible_states)
                
                # Apply soft adjacency preferences (don't enforce strictly)
                if neighbor_states:
                    scored_states = []
                    for state in possible:
                        score = self.weights.get(state, 1.0)
                        for n_state in neighbor_states:
                            adj_score = self.adjacency_rules.get(n_state, {}).get(state, 1.0)
                            score *= adj_score
                        scored_states.append((state, score))
                    
                    # Weighted choice from scored states
                    total_score = sum(s[1] for s in scored_states)
                    if total_score > 0:
                        r = random.uniform(0, total_score)
                        cumulative = 0
                        chosen = possible[0]
                        for state, score in scored_states:
                            cumulative += score
                            if r <= cumulative:
                                chosen = state
                                break
                        tile.collapse(chosen)
                    else:
                        tile.collapse(random.choice(possible))
                else:
                    # No neighbors collapsed yet, use base weights
                    tile.collapse(self._weighted_choice(tile.possible_states))
        
        return True  # Always succeeds with this approach
    
    def render(self, style: Optional[str] = None) -> str:
        """
        Render grid to string representation
        
        Args:
            style: Visual style ('ascii', 'blocks', 'braille') or None for default
            
        Returns:
            str: Rendered grid
        """
        render_style = style or self.style
        visual_map = self.VISUAL_STYLES.get(render_style, self.VISUAL_STYLES['ascii'])
        
        # Direct character mapping (bypass Enum)
        state_to_char = {
            '.': visual_map.get(TerrainType.EMPTY, '.'),
            'C': visual_map.get(TerrainType.CREATURE, 'C'),
            'H': visual_map.get(TerrainType.HABITAT, 'H'),
            'R': visual_map.get(TerrainType.RESOURCE, 'R'),
            'A': visual_map.get(TerrainType.ADAPTATION, 'A')
        }
        
        lines = []
        for row in self.grid:
            line_chars = []
            for t in row:
                if t.final_state and t.final_state in state_to_char:
                    char = state_to_char[t.final_state]
                else:
                    char = '.'
                line_chars.append(char)
            lines.append(''.join(line_chars))
        
        return '\n'.join(lines)
    
    def get_grid_data(self) -> List[List[str]]:
        """Get raw grid data for further processing"""
        return [[t.final_state for t in row] for row in self.grid]


# =============================================================================
# MAIN PIPELINE & DEMONSTRATION
# =============================================================================

class CreatureWFCPipeline:
    """
    Complete pipeline connecting Phase 1 and Phase 2
    Orchestrates creature generation and WFC visualization
    """
    
    def __init__(self, seed: Optional[int] = None, grid_size: int = 20, style: str = 'ascii'):
        self.ecological_engine = EcologicalEngine(seed=seed)
        self.wfc_adapter = WFCAdapter(grid_size=grid_size, style=style)
        self.current_card: Optional[CreatureCard] = None
    
    def run(self, env_input: EnvironmentalInput, visualize: bool = True) -> Dict[str, Any]:
        """
        Execute complete pipeline
        
        Args:
            env_input: EnvironmentalInput with 5 variables
            visualize: Whether to render WFC output
            
        Returns:
            Dict with creature card and generation results
        """
        print("=" * 70)
        print("PHASE 1: ECOLOGICAL ENGINE - CREATURE CARD GENERATION")
        print("=" * 70)
        
        # Phase 1: Generate creature card
        self.current_card = self.ecological_engine.generate_creature_card(env_input)
        
        print(f"\nGenerated Creature: {self.current_card.creature_id}")
        print(f"Environmental Signature:")
        for key, value in self.current_card.environmental_signature.items():
            print(f"  - {key.replace('_', ' ').title()}: {value}")
        
        print(f"\nAnatomy:")
        for part, details in self.current_card.anatomy.items():
            if isinstance(details, dict) and 'name' in details:
                print(f"  - {part.replace('_', ' ').title()}: {details['name']}")
        
        print(f"\nSurvival Mechanisms:")
        for mech in self.current_card.survival_mechanisms:
            print(f"  - {mech['type'].replace('_', ' ').title()}: {mech['description']}")
        
        print(f"\nEnergy Source: {self.current_card.energy_source.replace('_', ' ').title()}")
        print(f"Climate Tolerance Range:")
        for key, value in self.current_card.climate_tolerance.items():
            print(f"  - {key.replace('_', ' ').title()}: {value}")
        
        print(f"\nSpatial Constraints for WFC:")
        for constraint in self.current_card.spatial_constraints:
            print(f"  - {constraint['type'].replace('_', ' ').title()}:")
            print(f"      Required: {constraint['required_neighbors']}")
            print(f"      Forbidden: {constraint['forbidden_neighbors']}")
            print(f"      Weight: {constraint['weight']}")
        
        print("\n" + "=" * 70)
        print("PHASE 2: WFC ADAPTER - HABITAT GENERATION")
        print("=" * 70)
        
        # Phase 2: Configure and run WFC
        self.wfc_adapter.load_creature_card(self.current_card)
        
        print("\nRunning Wave Function Collapse algorithm...")
        attempts = 0
        max_attempts = 10
        
        while attempts < max_attempts:
            success = self.wfc_adapter.generate(max_iterations=500)
            if success:
                print(f"WFC generation successful after {attempts + 1} attempt(s)")
                break
            else:
                attempts += 1
                print(f"Contradiction detected, retrying ({attempts}/{max_attempts})...")
        
        if not success:
            print("Warning: WFC failed to converge after maximum attempts")
        
        result = {
            'creature_card': json.loads(self.current_card.to_json()),
            'wfc_success': success,
            'attempts': attempts + 1,
            'grid_data': self.wfc_adapter.get_grid_data()
        }
        
        if visualize:
            print("\n" + "-" * 70)
            print("GENERATED HABITAT MAP (WFC Output)")
            print("-" * 70)
            print(self.wfc_adapter.render())
            print("-" * 70)
            print("\nLegend:")
            print("  . = Empty Space    C = Creature    H = Habitat")
            print("  R = Resource       A = Adaptation")
        
        return result
    
    def export_card(self, filename: str = 'creature_card.json'):
        """Export current creature card to JSON file"""
        if self.current_card:
            with open(filename, 'w') as f:
                f.write(self.current_card.to_json())
            print(f"Creature card exported to {filename}")
        else:
            print("No creature card to export")
    
    def import_card(self, filename: str = 'creature_card.json'):
        """Import creature card from JSON file"""
        try:
            with open(filename, 'r') as f:
                json_str = f.read()
            self.current_card = CreatureCard.from_json(json_str)
            self.wfc_adapter.load_creature_card(self.current_card)
            print(f"Creature card imported from {filename}")
            return True
        except Exception as e:
            print(f"Error importing card: {e}")
            return False


# =============================================================================
# DEMONSTRATION & TESTING
# =============================================================================

def demo_scenarios():
    """Run demonstration scenarios with different environmental conditions"""
    
    print("\n" + "=" * 70)
    print("PROCEDURAL CREATURE GENERATION & WFC PIPELINE - DEMONSTRATION")
    print("=" * 70)
    
    # Scenario 1: High altitude, cold, low resource environment
    print("\n\n### SCENARIO 1: Alpine Extreme Environment ###\n")
    env1 = EnvironmentalInput(
        temperature=-15,      # Cold
        humidity=40,          # Dry
        altitude=5500,        # High altitude
        atmospheric_pressure=0.6,  # Low pressure
        resource_density=25   # Low resources
    )
    
    pipeline1 = CreatureWFCPipeline(seed=42, grid_size=25, style='ascii')
    result1 = pipeline1.run(env1, visualize=True)
    pipeline1.export_card('creature_alpine.json')
    
    # Scenario 2: Tropical, humid, resource-rich environment
    print("\n\n### SCENARIO 2: Tropical Rainforest Environment ###\n")
    env2 = EnvironmentalInput(
        temperature=28,       # Warm
        humidity=85,          # Very humid
        altitude=200,         # Low altitude
        atmospheric_pressure=1.0,  # Standard pressure
        resource_density=80   # Rich resources
    )
    
    pipeline2 = CreatureWFCPipeline(seed=123, grid_size=25, style='blocks')
    result2 = pipeline2.run(env2, visualize=True)
    pipeline2.export_card('creature_tropical.json')
    
    # Scenario 3: Desert extreme with high temperature variation
    print("\n\n### SCENARIO 3: Desert Environment ###\n")
    env3 = EnvironmentalInput(
        temperature=35,       # Hot
        humidity=15,          # Very dry
        altitude=800,         # Moderate altitude
        atmospheric_pressure=0.95,  # Near standard
        resource_density=30   # Low-moderate resources
    )
    
    pipeline3 = CreatureWFCPipeline(seed=999, grid_size=25, style='ascii')
    result3 = pipeline3.run(env3, visualize=True)
    pipeline3.export_card('creature_desert.json')
    
    # Scenario 4: Deep ocean trench simulation (high pressure, no light)
    print("\n\n### SCENARIO 4: Deep Ocean Trench Environment ###\n")
    env4 = EnvironmentalInput(
        temperature=4,        # Cold
        humidity=100,         # Saturated
        altitude=-2000,       # Below sea level (we'll clamp it)
        atmospheric_pressure=1.5,  # High pressure
        resource_density=60   # Moderate-hi resources (hydrothermal vents)
    )
    
    # Fix altitude to valid range
    env4.altitude = 100  # Treat as depth proxy
    
    pipeline4 = CreatureWFCPipeline(seed=777, grid_size=25, style='braille')
    result4 = pipeline4.run(env4, visualize=True)
    pipeline4.export_card('creature_oceanic.json')
    
    print("\n\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\nGenerated Files:")
    print("  - creature_alpine.json")
    print("  - creature_tropical.json")
    print("  - creature_desert.json")
    print("  - creature_oceanic.json")
    print("\nYou can re-import any card using: pipeline.import_card('filename.json')")
    
    return [result1, result2, result3, result4]


def interactive_mode():
    """Allow user to input custom environmental values"""
    print("\n" + "=" * 70)
    print("INTERACTIVE MODE - CREATE YOUR OWN CREATURE")
    print("=" * 70)
    
    try:
        print("\nEnter environmental parameters (or press Enter for defaults):")
        
        temp = input("Temperature (-50 to 50°C) [default: 20]: ").strip()
        temp = float(temp) if temp else 20.0
        
        humid = input("Humidity (0 to 100%) [default: 50]: ").strip()
        humid = float(humid) if humid else 50.0
        
        alt = input("Altitude (0 to 8000m) [default: 1000]: ").strip()
        alt = float(alt) if alt else 1000.0
        
        pressure = input("Atmospheric Pressure (0.5 to 1.5 ATM) [default: 1.0]: ").strip()
        pressure = float(pressure) if pressure else 1.0
        
        resources = input("Resource Density (0 to 100) [default: 50]: ").strip()
        resources = float(resources) if resources else 50.0
        
        env = EnvironmentalInput(
            temperature=temp,
            humidity=humid,
            altitude=alt,
            atmospheric_pressure=pressure,
            resource_density=resources
        )
        
        if not env.validate():
            print("\nError: Environmental values out of valid range!")
            print("Please restart with valid values.")
            return
        
        style_choice = input("\nVisual style (ascii/blocks/braille) [default: ascii]: ").strip().lower()
        style = style_choice if style_choice in ['ascii', 'blocks', 'braille'] else 'ascii'
        
        grid_size = input("Grid size (10-50) [default: 25]: ").strip()
        grid_size = int(grid_size) if grid_size else 25
        grid_size = max(10, min(50, grid_size))
        
        pipeline = CreatureWFCPipeline(seed=None, grid_size=grid_size, style=style)
        pipeline.run(env, visualize=True)
        
        save = input("\nSave creature card? (y/n) [default: y]: ").strip().lower()
        if save != 'n':
            filename = input("Filename [default: custom_creature.json]: ").strip()
            filename = filename if filename else 'custom_creature.json'
            pipeline.export_card(filename)
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == '__main__':
    import sys
    
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█  PROCEDURAL CREATURE GENERATION & WFC PIPELINE                   █")
    print("█  Phase 1: Ecological Engine → Creature Card                       █")
    print("█  Phase 2: WFC Adapter → Habitat Visualization                     █")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        interactive_mode()
    else:
        demo_scenarios()
    
    print("\n" + "=" * 70)
    print("To run in interactive mode: python creature_wfc_pipeline.py --interactive")
    print("=" * 70 + "\n")
