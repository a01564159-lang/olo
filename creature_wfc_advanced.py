#!/usr/bin/env python3
"""
Advanced Visual Creature Generator with Organic WFC
Generates more organic, creature-like shapes using improved WFC with growth patterns
"""

import json
import random
import math
import os
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

# ============================================================================
# CONFIGURACIÓN VISUAL - Estilos de renderizado avanzados
# ============================================================================

class VisualStyle(Enum):
    COLORED = "colored"           # Colored ASCII with box drawing
    UNICODE_CREATURE = "unicode_creature"  # Unicode blocks optimized for creatures
    BRILLE_ART = "braille_art"    # High-resolution braille
    RETRO = "retro"               # Classic ASCII art style

@dataclass
class ColorCodes:
    """Códigos de color ANSI para terminal"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    ORANGE = "\033[38;5;208m"
    PURPLE = "\033[38;5;129m"
    TEAL = "\033[38;5;51m"
    
    # Background colors for extra visual pop
    BG_DARK = "\033[48;5;235m"
    BG_RED = "\033[48;5;52m"
    BG_GREEN = "\033[48;5;22m"
    BG_BLUE = "\033[48;5;17m"

COLORS = ColorCodes()

# ============================================================================
# FASE 1: MOTOR DE DEFINICIÓN ECOLÓGICA (Mejorado)
# ============================================================================

@dataclass
class EcologicalVariables:
    """Las 5 variables de geografía/clima"""
    temperature: float  # -50 a 50 °C
    humidity: float     # 0 a 100%
    altitude: float     # 0 a 8000 m
    pressure: float     # 300 a 1013 hPa
    resources: float    # 0 a 10 (escala de abundancia)

@dataclass
class CreatureCard:
    """Tarjeta de Criatura generada"""
    id: str
    name: str
    environment: Dict[str, float]
    
    # Anatomía y morfología
    limbs: int
    body_type: str
    armor_type: str
    sensory_organs: List[str]
    size_class: str
    
    # Mecanismos de supervivencia
    climate_tolerance: Dict[str, float]
    energy_source: str
    special_adaptations: List[str]
    
    # Restricciones espaciales para WFC
    adjacency_rules: Dict[str, List[str]]
    required_neighbors: List[str]
    forbidden_neighbors: List[str]
    habitat_weights: Dict[str, float]
    
    # Nuevos parámetros para crecimiento orgánico
    growth_pattern: str
    symmetry: str
    segment_count: int

class EcologicalEngine:
    """Motor que genera tarjetas de criatura desde variables ecológicas"""
    
    BODY_TYPES = ["serpentine", "quadruped", "biped", "hexapod", "amorphous", "radial", "crab", "centipede"]
    ARMOR_TYPES = ["none", "scales", "chitin", "bone_plates", "fur", "feathers", "crystalline", "exoskeleton"]
    SENSORY_ORGANS = ["eyes", "antennae", "heat_sensors", "echolocation", "chemical_receptors", 
                      "electroreceptors", "lateral_line", "pit_organs"]
    ENERGY_SOURCES = ["photosynthesis", "chemosynthesis", "predation", "scavenging", "filter_feeding", 
                      "geothermal", "parasitic", "symbiotic"]
    GROWTH_PATTERNS = ["linear", "branching", "radial", "spiral", "segmented", "clustered"]
    SYMMETRIES = ["bilateral", "radial", "asymmetric", "spherical"]
    
    def __init__(self):
        self.creature_counter = 0
    
    def generate_creature_card(self, env: EcologicalVariables) -> CreatureCard:
        """Genera una tarjeta de criatura basada en las variables ecológicas"""
        self.creature_counter += 1
        
        # Calcular adaptaciones basadas en el ambiente
        body_type = self._determine_body_type(env)
        armor_type = self._determine_armor_type(env)
        limbs = self._calculate_limbs(env, body_type)
        sensory_organs = self._determine_sensory_organs(env)
        size_class = self._determine_size_class(env)
        
        climate_tolerance = self._calculate_climate_tolerance(env)
        energy_source = self._determine_energy_source(env)
        special_adaptations = self._generate_adaptations(env)
        
        # Generar reglas de adyacencia para WFC
        adjacency_rules, required, forbidden, weights = self._generate_wfc_rules(env, body_type, armor_type)
        
        # Parámetros de crecimiento orgánico
        growth_pattern = self._determine_growth_pattern(env, body_type)
        symmetry = self._determine_symmetry(body_type)
        segment_count = self._calculate_segments(env, body_type)
        
        name = self._generate_creature_name(env, body_type, armor_type)
        
        return CreatureCard(
            id=f"CRE_{self.creature_counter:04d}",
            name=name,
            environment={
                "temperature": env.temperature,
                "humidity": env.humidity,
                "altitude": env.altitude,
                "pressure": env.pressure,
                "resources": env.resources
            },
            limbs=limbs,
            body_type=body_type,
            armor_type=armor_type,
            sensory_organs=sensory_organs,
            size_class=size_class,
            climate_tolerance=climate_tolerance,
            energy_source=energy_source,
            special_adaptations=special_adaptations,
            adjacency_rules=adjacency_rules,
            required_neighbors=required,
            forbidden_neighbors=forbidden,
            habitat_weights=weights,
            growth_pattern=growth_pattern,
            symmetry=symmetry,
            segment_count=segment_count
        )
    
    def _determine_body_type(self, env: EcologicalVariables) -> str:
        """Determina el tipo de cuerpo basado en el ambiente"""
        score = 0
        
        # Temperatura afecta metabolismo y forma
        if env.temperature < -20:
            score += 2  # Formas compactas
        elif env.temperature > 30:
            score -= 1  # Formas alargadas para disipar calor
        
        # Altitud afecta movilidad
        if env.altitude > 4000:
            score += 1  # Formas más estables
        
        # Humedad afecta tipo de locomoción
        if env.humidity > 80:
            return random.choice(["serpentine", "amorphous", "crab"])
        
        if env.resources > 7:
            return random.choice(["hexapod", "quadruped", "crab"])
        
        if score >= 2:
            return random.choice(["quadruped", "radial", "crab"])
        elif score <= 0:
            return random.choice(["serpentine", "biped", "centipede"])
        else:
            return random.choice(self.BODY_TYPES[:6])
    
    def _determine_armor_type(self, env: EcologicalVariables) -> str:
        """Determina el tipo de coraza"""
        if env.temperature < -30:
            return random.choice(["fur", "bone_plates", "exoskeleton"])
        elif env.temperature > 35:
            return random.choice(["scales", "crystalline", "exoskeleton"])
        elif env.humidity > 85:
            return random.choice(["scales", "none", "exoskeleton"])
        elif env.resources < 3:
            return random.choice(["chitin", "none", "exoskeleton"])
        elif env.pressure > 900:
            return random.choice(["bone_plates", "exoskeleton", "crystalline"])
        else:
            return random.choice(self.ARMOR_TYPES)
    
    def _calculate_limbs(self, env: EcologicalVariables, body_type: str) -> int:
        """Calcula número de extremidades"""
        limb_map = {
            "serpentine": random.randint(0, 2),
            "amorphous": 0,
            "radial": random.randint(5, 8),
            "hexapod": 6,
            "quadruped": 4,
            "biped": 2,
            "crab": random.randint(6, 10),
            "centipede": random.randint(20, 40)
        }
        
        base_limbs = limb_map.get(body_type, 4)
        
        if env.altitude > 5000 and base_limbs > 2:
            base_limbs = max(2, base_limbs - 2)
        if env.humidity > 90 and body_type not in ["serpentine", "amorphous"]:
            base_limbs = max(0, base_limbs - 1)
        
        return base_limbs
    
    def _determine_sensory_organs(self, env: EcologicalVariables) -> List[str]:
        """Determina órganos sensoriales"""
        organs = []
        
        # Visión básica casi siempre presente
        if env.pressure > 500:
            organs.append("eyes")
        
        # Sensores de calor en ambientes fríos o oscuros
        if env.temperature < 0 or env.pressure < 400:
            organs.append("heat_sensors")
        
        # Antenas en alta humedad
        if env.humidity > 70:
            organs.append("antennae")
        
        # Eco-localización en baja presión/poca luz
        if env.pressure < 600 or env.resources < 3:
            organs.append("echolocation")
        
        # Receptores químicos siempre útiles
        organs.append("chemical_receptors")
        
        # Electro-receptores en alta humedad/agua
        if env.humidity > 85:
            organs.append("electroreceptors")
        
        # Línea lateral en criaturas acuáticas
        if env.humidity > 90 or env.pressure > 1000:
            organs.append("lateral_line")
        
        # Órganos pit en depredadores de sangre caliente
        if env.temperature > 20 and env.resources > 5:
            organs.append("pit_organs")
        
        return organs if organs else ["chemical_receptors"]
    
    def _determine_size_class(self, env: EcologicalVariables) -> str:
        """Determina clase de tamaño"""
        if env.resources < 3:
            return random.choice(["tiny", "small"])
        elif env.resources < 6:
            return random.choice(["small", "medium"])
        elif env.resources < 8:
            return random.choice(["medium", "large"])
        else:
            return random.choice(["large", "huge", "gigantic"])
    
    def _calculate_climate_tolerance(self, env: EcologicalVariables) -> Dict[str, float]:
        """Calcula tolerancias climáticas"""
        base_temp = env.temperature
        base_humidity = env.humidity
        
        # Mayor diversidad de recursos = mayor tolerancia
        resource_factor = env.resources / 10
        
        return {
            "min_temperature": base_temp - random.uniform(10, 25) * (1 + resource_factor),
            "max_temperature": base_temp + random.uniform(10, 25) * (1 + resource_factor),
            "min_humidity": max(0, base_humidity - random.uniform(20, 40) * (1 + resource_factor)),
            "max_humidity": min(100, base_humidity + random.uniform(10, 30) * (1 + resource_factor)),
            "min_pressure": max(300, env.pressure - random.uniform(100, 200)),
            "max_pressure": min(1013, env.pressure + random.uniform(50, 150))
        }
    
    def _determine_energy_source(self, env: EcologicalVariables) -> str:
        """Determina fuente de energía"""
        if env.temperature > 25 and env.humidity > 60 and env.altitude < 3000:
            return "photosynthesis"
        elif env.pressure < 400 or env.resources < 2:
            return "chemosynthesis"
        elif env.resources > 7 and env.temperature > 10:
            return random.choice(["predation", "scavenging"])
        elif env.humidity > 80:
            return "filter_feeding"
        elif env.altitude > 3000 and env.temperature > 40:
            return "geothermal"
        elif env.pressure > 900:
            return random.choice(["chemosynthesis", "filter_feeding"])
        else:
            return "scavenging"
    
    def _generate_adaptations(self, env: EcologicalVariables) -> List[str]:
        """Genera adaptaciones especiales"""
        adaptations = []
        
        if env.temperature < -20:
            adaptations.append("antifreeze_blood")
        if env.temperature > 40:
            adaptations.append("heat_dissipation_fins")
        if env.altitude > 5000:
            adaptations.append("enhanced_oxygen_extraction")
        if env.pressure < 400:
            adaptations.append("pressure_resistant_membrane")
        if env.pressure > 900:
            adaptations.append("compression_resistant_skeleton")
        if env.humidity < 20:
            adaptations.append("water_retention_bladder")
        if env.humidity > 90:
            adaptations.extend(["gill_slits", "permeable_skin"])
        if env.resources < 2:
            adaptations.append("metabolic_stasis")
        if env.resources > 8:
            adaptations.append("rapid_regeneration")
        if env.temperature > 30 and env.humidity < 30:
            adaptations.append("nocturnal_metabolism")
        if env.altitude > 4000 and env.temperature < 0:
            adaptations.append("hibernation_capability")
        
        return adaptations if adaptations else ["generalist_metabolism"]
    
    def _generate_wfc_rules(self, env: EcologicalVariables, body_type: str, armor_type: str) -> Tuple:
        """Genera reglas de adyacencia para WFC"""
        # Tipos de tiles posibles - más detallados para formas orgánicas
        tile_types = ["head", "neck", "body", "limb_joint", "limb", "tail_base", "tail", 
                      "organ_heart", "organ_brain", "spine", "habitat", "empty"]
        
        # Reglas de adyacencia más orgánicas
        adjacency_rules = {
            "head": ["neck", "body", "organ_brain"],
            "neck": ["head", "body", "spine"],
            "body": ["neck", "body", "limb_joint", "tail_base", "spine", "organ_heart"],
            "limb_joint": ["body", "limb"],
            "limb": ["limb_joint", "limb"],
            "tail_base": ["body", "tail"],
            "tail": ["tail_base", "tail"],
            "organ_heart": ["body", "spine"],
            "organ_brain": ["head", "neck"],
            "spine": ["neck", "body", "tail_base", "organ_heart", "organ_brain"],
            "habitat": ["habitat", "body", "tail", "limb"],
            "empty": ["empty", "habitat"]
        }
        
        # Vecinos requeridos según tipo de cuerpo
        required = []
        if body_type in ["quadruped", "hexapod", "crab"]:
            required = ["habitat", "limb"]
        elif body_type == "serpentine":
            required = ["habitat", "body", "tail"]
        elif body_type == "amorphous":
            required = ["habitat"]
        elif body_type == "centipede":
            required = ["habitat", "body", "limb"]
        elif body_type == "radial":
            required = ["habitat", "body"]
        
        # Vecinos prohibidos
        forbidden = []
        if armor_type == "crystalline" and env.humidity > 80:
            forbidden = ["water_deep"]
        if env.temperature > 40:
            forbidden = ["ice"]
        if env.temperature < -20:
            forbidden = ["lava", "hot_spring"]
        if env.pressure < 400:
            forbidden = ["water_surface"]
        
        # Pesos de hábitat ajustados para formas orgánicas
        weights = {
            "head": 0.15,
            "neck": 0.2,
            "body": 0.4,
            "limb_joint": 0.25,
            "limb": 0.3 if body_type not in ["serpentine", "amorphous"] else 0.05,
            "tail_base": 0.15,
            "tail": 0.2,
            "organ_heart": 0.1,
            "organ_brain": 0.08,
            "spine": 0.3,
            "habitat": 0.5,
            "empty": 0.7
        }
        
        # Ajustar pesos según ambiente y tipo de cuerpo
        if env.resources < 3:
            weights["habitat"] *= 0.6
            weights["empty"] *= 1.4
        elif env.resources > 7:
            weights["body"] *= 1.3
            weights["organ_heart"] *= 1.5
            weights["organ_brain"] *= 1.5
        
        if body_type == "serpentine":
            weights["body"] *= 1.5
            weights["tail"] *= 1.3
        elif body_type == "radial":
            weights["limb"] *= 2.0
            weights["body"] *= 0.7
        
        return adjacency_rules, required, forbidden, weights
    
    def _determine_growth_pattern(self, env: EcologicalVariables, body_type: str) -> str:
        """Determina patrón de crecimiento"""
        if body_type in ["serpentine", "centipede"]:
            return "linear"
        elif body_type == "radial":
            return "radial"
        elif body_type in ["hexapod", "crab"]:
            return "segmented"
        elif env.resources > 7:
            return random.choice(["branching", "clustered"])
        elif env.temperature < 0:
            return "compact"
        else:
            return random.choice(self.GROWTH_PATTERNS)
    
    def _determine_symmetry(self, body_type: str) -> str:
        """Determina tipo de simetría"""
        if body_type == "radial":
            return "radial"
        elif body_type == "amorphous":
            return "asymmetric"
        else:
            return "bilateral"
    
    def _calculate_segments(self, env: EcologicalVariables, body_type: str) -> int:
        """Calcula número de segmentos corporales"""
        if body_type in ["serpentine", "centipede"]:
            base = random.randint(8, 30) if body_type == "centipede" else random.randint(3, 8)
            if env.resources > 6:
                base += random.randint(2, 5)
            return base
        elif body_type == "radial":
            return random.randint(5, 12)
        else:
            return random.randint(3, 6)
    
    def _generate_creature_name(self, env: EcologicalVariables, body_type: str, armor_type: str) -> str:
        """Genera un nombre descriptivo para la criatura"""
        prefixes = {
            "cold": ["Frost", "Ice", "Glacial", "Arctic", "Cryo"],
            "hot": ["Blaze", "Ember", "Solar", "Magma", "Pyro"],
            "wet": ["Aqua", "Marine", "River", "Ocean", "Hydro"],
            "dry": ["Dust", "Sand", "Arid", "Desert", "Xero"],
            "high": ["Sky", "Cloud", "Peak", "Alpine", "Aero"],
            "low": ["Deep", "Abyss", "Trench", "Sub", "Bathy"]
        }
        
        body_names = {
            "serpentine": ["Snake", "Wyrm", "Serpent", "Drake", "Naga"],
            "quadruped": ["Stalker", "Runner", "Beast", "Strider", "Prowler"],
            "biped": ["Walker", "Hunter", "Lurker", "Stalker", "Strider"],
            "hexapod": ["Skitterer", "Crawler", "Weaver", "Spinner", "Hex"],
            "amorphous": ["Ooze", "Blob", "Mass", "Slime", "Gel"],
            "radial": ["Bloom", "Star", "Flower", "Medusa", "Radiant"],
            "crab": ["Crusher", "Pincher", "Scuttler", "Armored", "Carapace"],
            "centipede": ["Milli", "Segment", "Crawler", "Many-leg", "Vermis"]
        }
        
        armor_suffixes = {
            "none": "",
            "scales": "scale",
            "chitin": "shell",
            "bone_plates": "bone",
            "fur": "mane",
            "feathers": "plume",
            "crystalline": "crystal",
            "exoskeleton": "exo"
        }
        
        # Seleccionar prefijo basado en ambiente
        prefix_list = []
        if env.temperature < 0:
            prefix_list.extend(prefixes["cold"])
        elif env.temperature > 30:
            prefix_list.extend(prefixes["hot"])
        
        if env.humidity < 30:
            prefix_list.extend(prefixes["dry"])
        elif env.humidity > 70:
            prefix_list.extend(prefixes["wet"])
        
        if env.altitude > 4000:
            prefix_list.extend(prefixes["high"])
        elif env.altitude < 500 or env.pressure > 900:
            prefix_list.extend(prefixes["low"])
        
        prefix = random.choice(prefix_list) if prefix_list else "Wild"
        body_name = random.choice(body_names.get(body_type, ["Creature"]))
        suffix = armor_suffixes.get(armor_type, "")
        
        if suffix:
            return f"{prefix}{body_name}{suffix.capitalize()}"
        else:
            return f"{prefix}{body_name}"

# ============================================================================
# FASE 2: WAVE FUNCTION COLLAPSE ORGÁNICO MEJORADO
# ============================================================================

@dataclass
class Tile:
    """Representa un tile en la grilla WFC"""
    x: int
    y: int
    possibilities: List[str] = field(default_factory=list)
    collapsed: bool = False
    value: Optional[str] = None
    entropy: float = float('inf')

class OrganicWFC:
    """Implementación mejorada de WFC para formas orgánicas de criaturas"""
    
    def __init__(self, width: int = 45, height: int = 28, style: VisualStyle = VisualStyle.COLORED):
        self.width = width
        self.height = height
        self.style = style
        self.grid: List[List[Tile]] = []
        self.creature_card: Optional[CreatureCard] = None
        
        # Semilla de crecimiento para forma orgánica
        self.seed_points: List[Tuple[int, int]] = []
        self.growth_directions: List[Tuple[int, int]] = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        # Definición visual de cada tipo de tile
        self.tile_visuals = self._initialize_tile_visuals()
    
    def _initialize_tile_visuals(self) -> Dict[str, Dict]:
        """Inicializa la representación visual de cada tile"""
        return {
            "head": {
                "colored": "◉",
                "unicode_creature": "◈",
                "braille_art": "⣿",
                "retro": "H",
                "color": COLORS.RED,
                "glow_color": COLORS.BG_RED,
                "description": "Head/Cephalic region"
            },
            "neck": {
                "colored": "│",
                "unicode_creature": "╽",
                "braille_art": "⢸",
                "retro": "|",
                "color": COLORS.ORANGE,
                "glow_color": "",
                "description": "Neck/Cervical"
            },
            "body": {
                "colored": "█",
                "unicode_creature": "▓",
                "braille_art": "⣶",
                "retro": "B",
                "color": COLORS.GREEN,
                "glow_color": COLORS.BG_GREEN,
                "description": "Body/Torso"
            },
            "limb_joint": {
                "colored": "●",
                "unicode_creature": "◉",
                "braille_art": "⣤",
                "retro": "J",
                "color": COLORS.YELLOW,
                "glow_color": "",
                "description": "Joint/Articulation"
            },
            "limb": {
                "colored": "▌",
                "unicode_creature": "╿",
                "braille_art": "⢿",
                "retro": "L",
                "color": COLORS.YELLOW,
                "glow_color": "",
                "description": "Limb/Appendage"
            },
            "tail_base": {
                "colored": "▼",
                "unicode_creature": "▽",
                "braille_art": "⢄",
                "retro": "T",
                "color": COLORS.MAGENTA,
                "glow_color": "",
                "description": "Tail base"
            },
            "tail": {
                "colored": "╲",
                "unicode_creature": "╲",
                "braille_art": "⡇",
                "retro": "t",
                "color": COLORS.MAGENTA,
                "glow_color": "",
                "description": "Tail/Caudal"
            },
            "organ_heart": {
                "colored": "♥",
                "unicode_creature": "❤",
                "braille_art": "⣠",
                "retro": "*",
                "color": COLORS.RED,
                "glow_color": COLORS.BG_RED,
                "description": "Heart/Vital organ"
            },
            "organ_brain": {
                "colored": "☯",
                "unicode_creature": "◐",
                "braille_art": "⣦",
                "retro": "@",
                "color": COLORS.CYAN,
                "glow_color": "",
                "description": "Brain/Neural center"
            },
            "spine": {
                "colored": "║",
                "unicode_creature": "┃",
                "braille_art": "⢻",
                "retro": "=",
                "color": COLORS.WHITE,
                "glow_color": "",
                "description": "Spine/Vertebrae"
            },
            "habitat": {
                "colored": "·",
                "unicode_creature": "░",
                "braille_art": "⢒",
                "retro": ".",
                "color": COLORS.BLUE,
                "glow_color": COLORS.BG_BLUE,
                "description": "Habitat terrain"
            },
            "empty": {
                "colored": " ",
                "unicode_creature": " ",
                "braille_art": " ",
                "retro": " ",
                "color": COLORS.RESET,
                "glow_color": "",
                "description": "Empty space"
            }
        }
    
    def initialize_grid(self, creature_card: CreatureCard):
        """Inicializa la grilla con semillas de crecimiento orgánico"""
        self.creature_card = creature_card
        self.grid = []
        
        all_tiles = list(creature_card.adjacency_rules.keys())
        
        # Crear semillas de crecimiento basadas en el patrón
        self._generate_seed_points(creature_card)
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Calcular distancia al punto de semilla más cercano
                min_dist_to_seed = float('inf')
                for seed_x, seed_y in self.seed_points:
                    dist = math.sqrt((x - seed_x)**2 + (y - seed_y)**2)
                    min_dist_to_seed = min(min_dist_to_seed, dist)
                
                # Probabilidad inicial basada en distancia a semillas y pesos
                possibilities = []
                weights = creature_card.habitat_weights
                
                for tile_type in all_tiles:
                    weight = weights.get(tile_type, 0.5)
                    
                    # Tiles de criatura más probables cerca de semillas
                    if tile_type in ["head", "neck", "body", "limb_joint", "limb", "tail_base", "tail", 
                                    "organ_heart", "organ_brain", "spine"]:
                        # Probabilidad decae con distancia
                        probability = weight * max(0, 1 - min_dist_to_seed / (self.width / 3)) * 2.0
                    else:
                        probability = weight * min(1, min_dist_to_seed / (self.width / 4)) * 0.8
                    
                    # Añadir múltiples veces según probabilidad
                    n_copies = max(1, int(probability * 10))
                    possibilities.extend([tile_type] * n_copies)
                
                # Asegurar al menos algunas posibilidades
                if not possibilities:
                    possibilities = ["empty", "habitat"]
                
                tile = Tile(x=x, y=y, possibilities=possibilities)
                row.append(tile)
            self.grid.append(row)
    
    def _generate_seed_points(self, creature_card: CreatureCard):
        """Genera puntos de semilla para crecimiento orgánico"""
        self.seed_points = []
        
        # Punto central principal (siempre existe)
        center_x = self.width // 2
        center_y = self.height // 2
        self.seed_points.append((center_x, center_y))
        
        # Puntos adicionales basados en tipo de cuerpo
        body_type = creature_card.body_type
        segment_count = creature_card.segment_count
        
        if body_type in ["serpentine", "centipede"]:
            # Múltiples puntos a lo largo de una línea
            direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            for i in range(min(segment_count, 15)):
                offset = i * 2
                new_x = center_x + direction[0] * offset
                new_y = center_y + direction[1] * offset
                if 2 <= new_x < self.width - 2 and 2 <= new_y < self.height - 2:
                    self.seed_points.append((new_x, new_y))
        
        elif body_type in ["quadruped", "hexapod", "crab"]:
            # Puntos para extremidades
            limb_positions = [
                (center_x - 3, center_y - 2),
                (center_x + 3, center_y - 2),
                (center_x - 3, center_y + 2),
                (center_x + 3, center_y + 2),
            ]
            if body_type in ["hexapod", "crab"]:
                limb_positions.extend([
                    (center_x - 3, center_y),
                    (center_x + 3, center_y),
                ])
            
            for px, py in limb_positions:
                if 2 <= px < self.width - 2 and 2 <= py < self.height - 2:
                    self.seed_points.append((px, py))
        
        elif body_type == "radial":
            # Puntos en círculo
            radius = 5
            for i in range(creature_card.limbs):
                angle = (2 * math.pi * i) / creature_card.limbs
                px = int(center_x + radius * math.cos(angle))
                py = int(center_y + radius * math.sin(angle))
                if 2 <= px < self.width - 2 and 2 <= py < self.height - 2:
                    self.seed_points.append((px, py))
        
        # Limitar número de semillas
        self.seed_points = self.seed_points[:min(len(self.seed_points), 20)]
    
    def get_entropy(self, tile: Tile) -> float:
        """Calcula la entropía de un tile (menor = más restringido)"""
        if tile.collapsed:
            return 0
        
        unique_possibilities = len(set(tile.possibilities))
        if unique_possibilities == 0:
            return float('inf')
        elif unique_possibilities == 1:
            return 0
        else:
            # Añadir pequeña variación aleatoria para romper empates
            return unique_possibilities + random.uniform(0, 0.01)
    
    def find_lowest_entropy_tile(self) -> Optional[Tile]:
        """Encuentra el tile con menor entropía no colapsado"""
        min_entropy = float('inf')
        candidates = []
        
        # Priorizar tiles cerca de semillas ya colapsadas
        collapsed_tiles = [(t.x, t.y) for row in self.grid for t in row if t.collapsed]
        
        for row in self.grid:
            for tile in row:
                if not tile.collapsed:
                    entropy = self.get_entropy(tile)
                    
                    # Bonus para tiles adyacentes a tiles colapsados
                    if collapsed_tiles:
                        min_dist = min(math.sqrt((tile.x - cx)**2 + (tile.y - cy)**2) 
                                      for cx, cy in collapsed_tiles)
                        if min_dist < 2:
                            entropy -= 0.5  # Prioridad adicional
                    
                    if entropy < min_entropy:
                        min_entropy = entropy
                        candidates = [tile]
                    elif abs(entropy - min_entropy) < 0.001:
                        candidates.append(tile)
        
        if candidates:
            return random.choice(candidates)
        return None
    
    def collapse_tile(self, tile: Tile):
        """Colapsa un tile a un valor específico"""
        if not tile.possibilities:
            tile.value = "empty"
        else:
            # Elegir basado en pesos de la tarjeta y contexto local
            weights = self.creature_card.habitat_weights
            
            # Obtener vecinos colapsados
            neighbors = self.get_neighbors(tile)
            collapsed_neighbors = [n for n in neighbors if n.collapsed]
            
            # Calcular pesos ajustados por contexto
            adjusted_weights = {}
            for poss in set(tile.possibilities):
                base_weight = weights.get(poss, 0.5)
                
                # Bonus si es compatible con vecinos
                compatibility_bonus = 0
                for neighbor in collapsed_neighbors:
                    allowed = self.creature_card.adjacency_rules.get(neighbor.value, [])
                    if poss in allowed:
                        compatibility_bonus += 0.3
                    neighbor_allows = self.creature_card.adjacency_rules.get(poss, [])
                    if neighbor.value in neighbor_allows:
                        compatibility_bonus += 0.3
                
                adjusted_weights[poss] = base_weight + compatibility_bonus
            
            # Selección ponderada
            weighted_choices = []
            for poss, weight in adjusted_weights.items():
                n_copies = max(1, int(weight * 10))
                weighted_choices.extend([poss] * n_copies)
            
            if weighted_choices:
                tile.value = random.choice(weighted_choices)
            else:
                tile.value = random.choice(tile.possibilities)
        
        tile.collapsed = True
        tile.possibilities = [tile.value]
    
    def propagate_constraints(self, start_tile: Tile):
        """Propaga restricciones desde un tile colapsado"""
        stack = [start_tile]
        visited = set()
        
        while stack:
            current = stack.pop()
            if (current.x, current.y) in visited:
                continue
            visited.add((current.x, current.y))
            
            if not current.collapsed:
                continue
            
            # Obtener vecinos
            neighbors = self.get_neighbors(current)
            
            for neighbor in neighbors:
                if neighbor.collapsed:
                    continue
                
                # Obtener reglas de adyacencia
                allowed_neighbors = self.creature_card.adjacency_rules.get(current.value, [])
                
                # Filtrar posibilidades del vecino
                old_possibilities = set(neighbor.possibilities)
                new_possibilities = set()
                
                for poss in neighbor.possibilities:
                    can_be_adjacent = False
                    
                    # Regla directa
                    if poss in allowed_neighbors:
                        can_be_adjacent = True
                    
                    # Regla inversa
                    neighbor_allows = self.creature_card.adjacency_rules.get(poss, [])
                    if current.value in neighbor_allows:
                        can_be_adjacent = True
                    
                    if can_be_adjacent:
                        new_possibilities.add(poss)
                
                # Si se eliminaron posibilidades, añadir a la pila
                if new_possibilities != old_possibilities:
                    neighbor.possibilities = list(new_possibilities) if new_possibilities else ["empty"]
                    if not neighbor.collapsed and neighbor.possibilities:
                        stack.append(neighbor)
    
    def get_neighbors(self, tile: Tile) -> List[Tile]:
        """Obtiene los vecinos ortogonales de un tile"""
        neighbors = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dx, dy in directions:
            nx, ny = tile.x + dx, tile.y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbors.append(self.grid[ny][nx])
        
        return neighbors
    
    def run_wfc(self, max_iterations: int = 3000) -> bool:
        """Ejecuta el algoritmo WFC hasta completar"""
        iteration = 0
        
        while iteration < max_iterations:
            tile = self.find_lowest_entropy_tile()
            
            if tile is None:
                return True
            
            self.collapse_tile(tile)
            self.propagate_constraints(tile)
            
            iteration += 1
            
            if iteration % 200 == 0:
                remaining = sum(1 for row in self.grid for t in row if not t.collapsed)
                if remaining == 0:
                    return True
        
        return iteration < max_iterations
    
    def render(self) -> str:
        """Renderiza la grilla como string visual"""
        output_lines = []
        
        # Marco decorativo
        top_border = "╔" + "═" * (self.width * 2 - 1) + "╗"
        bottom_border = "╚" + "═" * (self.width * 2 - 1) + "╝"
        
        output_lines.append(COLORS.CYAN + top_border + COLORS.RESET)
        
        for row in self.grid:
            line = COLORS.CYAN + "║" + COLORS.RESET
            for tile in row:
                visual = self.get_tile_visual(tile.value)
                line += visual
            line += COLORS.CYAN + "║" + COLORS.RESET
            output_lines.append(line)
        
        output_lines.append(COLORS.CYAN + bottom_border + COLORS.RESET)
        
        return "\n".join(output_lines)
    
    def get_tile_visual(self, tile_type: str) -> str:
        """Obtiene la representación visual de un tile"""
        if tile_type is None:
            tile_type = "empty"
        
        visual_data = self.tile_visuals.get(tile_type, self.tile_visuals["empty"])
        char = visual_data.get(self.style.value, visual_data.get("colored", " "))
        color = visual_data.get("color", COLORS.RESET)
        
        if self.style == VisualStyle.COLORED:
            return f"{color}{char}{COLORS.RESET} "
        elif self.style == VisualStyle.UNICODE_CREATURE:
            return f"{color}{char}{char}{COLORS.RESET}"
        elif self.style == VisualStyle.BRILLE_ART:
            return f"{color}{char}{COLORS.RESET}"
        elif self.style == VisualStyle.RETRO:
            return f"{color}{char}{COLORS.RESET} "
        else:
            return f"{char} "
    
    def render_legend(self) -> str:
        """Renderiza la leyenda de tiles"""
        legend_lines = [COLORS.BOLD + "\n📊 ANATOMY LEGEND:" + COLORS.RESET]
        
        for tile_type, visual_data in self.tile_visuals.items():
            if tile_type == "empty":
                continue
            
            color = visual_data["color"]
            char = visual_data.get(self.style.value, visual_data.get("colored", "?"))
            symbol = f"{color}{char}{COLORS.RESET}"
            desc = visual_data["description"]
            legend_lines.append(f"  {symbol} {desc}")
        
        return "\n".join(legend_lines)

# ============================================================================
# SISTEMA PRINCIPAL DE GENERACIÓN VISUAL
# ============================================================================

class VisualCreatureGenerator:
    """Sistema principal que integra generación ecológica con WFC visual orgánico"""
    
    def __init__(self, width: int = 45, height: int = 28, style: VisualStyle = VisualStyle.COLORED):
        self.ecological_engine = EcologicalEngine()
        self.width = width
        self.height = height
        self.style = style
    
    def generate_and_display(self, env_vars: EcologicalVariables, show_details: bool = True):
        """Genera y muestra una criatura completa"""
        print("\n" + "="*100)
        print(COLORS.BOLD + COLORS.CYAN + "🧬 ADVANCED PROCEDURAL CREATURE GENERATION SYSTEM" + COLORS.RESET)
        print("="*100)
        
        # Fase 1: Generar tarjeta de criatura
        print(COLORS.YELLOW + "\n📋 PHASE 1: ECOLOGICAL ANALYSIS & CREATURE CARD GENERATION" + COLORS.RESET)
        print("-" * 100)
        
        creature_card = self.ecological_engine.generate_creature_card(env_vars)
        
        if show_details:
            self._display_creature_card(creature_card)
        
        # Fase 2: WFC Visual Orgánico
        print(COLORS.GREEN + "\n🎨 PHASE 2: ORGANIC WAVE FUNCTION COLLAPSE - VISUAL GENERATION" + COLORS.RESET)
        print("-" * 100)
        
        wfc = OrganicWFC(width=45, height=28, style=self.style)
        wfc.initialize_grid(creature_card)
        
        print(f"Grid initialized: {self.width}x{self.height}")
        print(f"Growth pattern: {creature_card.growth_pattern}")
        print(f"Seed points: {len(wfc.seed_points)}")
        print("Running organic WFC algorithm...")
        
        success = wfc.run_wfc(max_iterations=1500)
        
        if success:
            print(COLORS.GREEN + "✓ WFC completed successfully!" + COLORS.RESET)
        else:
            print(COLORS.YELLOW + "⚠ WFC reached maximum iterations" + COLORS.RESET)
        
        # Renderizar resultado
        print("\n" + COLORS.BOLD + "🦎 GENERATED CREATURE VISUALIZATION:" + COLORS.RESET)
        print(wfc.render())
        print(wfc.render_legend())
        
        # Información adicional
        if show_details:
            self._display_generation_stats(creature_card, wfc)
        
        return creature_card, wfc
    
    def _display_creature_card(self, card: CreatureCard):
        """Muestra los detalles de la tarjeta de criatura"""
        print(f"\n{COLORS.BOLD}Creature ID:{COLORS.RESET} {card.id}")
        print(f"{COLORS.BOLD}Name:{COLORS.RESET} {COLORS.CYAN}{card.name}{COLORS.RESET}")
        
        print(f"\n{COLORS.BOLD}🌍 ENVIRONMENTAL CONDITIONS:{COLORS.RESET}")
        print(f"  Temperature: {card.environment['temperature']:.1f}°C")
        print(f"  Humidity: {card.environment['humidity']:.1f}%")
        print(f"  Altitude: {card.environment['altitude']:.0f}m")
        print(f"  Pressure: {card.environment['pressure']:.0f} hPa")
        print(f"  Resources: {card.environment['resources']:.1f}/10")
        
        print(f"\n{COLORS.BOLD}🧬 ANATOMY & MORPHOLOGY:{COLORS.RESET}")
        print(f"  Body Type: {COLORS.YELLOW}{card.body_type}{COLORS.RESET}")
        print(f"  Limbs: {card.limbs}")
        print(f"  Armor: {card.armor_type}")
        print(f"  Size Class: {card.size_class}")
        print(f"  Symmetry: {card.symmetry}")
        print(f"  Growth Pattern: {card.growth_pattern}")
        print(f"  Segments: {card.segment_count}")
        print(f"  Sensory Organs: {', '.join(card.sensory_organs)}")
        
        print(f"\n{COLORS.BOLD}⚙️ SURVIVAL MECHANISMS:{COLORS.RESET}")
        print(f"  Energy Source: {COLORS.YELLOW}{card.energy_source}{COLORS.RESET}")
        print(f"  Climate Tolerance:")
        print(f"    Temp Range: {card.climate_tolerance['min_temperature']:.1f}°C to {card.climate_tolerance['max_temperature']:.1f}°C")
        print(f"    Humidity Range: {card.climate_tolerance['min_humidity']:.1f}% to {card.climate_tolerance['max_humidity']:.1f}%")
        print(f"  Special Adaptations: {', '.join(card.special_adaptations)}")
    
    def _display_generation_stats(self, card: CreatureCard, wfc: OrganicWFC):
        """Muestra estadísticas de la generación"""
        print(f"\n{COLORS.BOLD}📈 GENERATION STATISTICS:{COLORS.RESET}")
        
        # Contar tiles por tipo
        tile_counts = {}
        for row in wfc.grid:
            for tile in row:
                if tile.value:
                    tile_counts[tile.value] = tile_counts.get(tile.value, 0) + 1
        
        total_tiles = sum(tile_counts.values())
        creature_parts = ["head", "neck", "body", "limb_joint", "limb", "tail_base", "tail", 
                         "organ_heart", "organ_brain", "spine"]
        creature_tiles = sum(count for tile_type, count in tile_counts.items() 
                           if tile_type in creature_parts)
        habitat_ratio = creature_tiles / total_tiles * 100 if total_tiles > 0 else 0
        
        print(f"  Total Tiles: {total_tiles}")
        print(f"  Creature Tiles: {creature_tiles} ({habitat_ratio:.1f}%)")
        print(f"  Habitat Tiles: {tile_counts.get('habitat', 0)}")
        print(f"  Empty Space: {tile_counts.get('empty', 0)}")
        
        print(f"\n  Anatomy Distribution:")
        for tile_type, count in sorted(tile_counts.items(), key=lambda x: x[1], reverse=True):
            if tile_type == "empty":
                continue
            percentage = count / total_tiles * 100 if total_tiles > 0 else 0
            bar = "█" * int(percentage / 2)
            print(f"    {tile_type:15}: {count:4} ({percentage:5.1f}%) {bar}")

# ============================================================================
# DEMOSTRACIÓN
# ============================================================================

def quick_demo():
    """Demostración rápida con un ambiente aleatorio"""
    generator = VisualCreatureGenerator(width=60, height=35, style=VisualStyle.COLORED)
    
    env = EcologicalVariables(
        temperature=random.uniform(-30, 40),
        humidity=random.uniform(20, 90),
        altitude=random.uniform(0, 5000),
        pressure=random.uniform(500, 1013),
        resources=random.uniform(2, 9)
    )
    
    generator.generate_and_display(env, show_details=True)

def multi_environment_demo():
    """Demostración con múltiples ambientes"""
    generator = VisualCreatureGenerator(width=60, height=35, style=VisualStyle.COLORED)
    
    environments = [
        ("❄️ ALPINE EXTREME", EcologicalVariables(-25, 30, 5500, 450, 4)),
        ("🌴 TROPICAL JUNGLE", EcologicalVariables(35, 85, 100, 1010, 8)),
        ("🏜️ ARID DESERT", EcologicalVariables(45, 15, 200, 1000, 3)),
        ("🌊 DEEP OCEANIC", EcologicalVariables(5, 95, -200, 1100, 6)),
        ("🌋 VOLCANIC ZONE", EcologicalVariables(50, 40, 800, 950, 7)),
    ]
    
    for name, env in environments:
        print("\n\n" + "="*100)
        print(COLORS.BOLD + COLORS.MAGENTA + f"ENVIRONMENT: {name}" + COLORS.RESET)
        print("="*100)
        
        generator.generate_and_display(env, show_details=False)
        input(COLORS.CYAN + "\n⏎ Press Enter for next creature..." + COLORS.RESET)
        os.system('clear' if os.name == 'posix' else 'cls')

if __name__ == "__main__":
    import sys
    
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print(COLORS.BOLD + COLORS.CYAN + """
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║     🧬 ORGANIC CREATURE GENERATOR with WAVE FUNCTION COLLAPSE    ║
    ║                                                                   ║
    ║     Advanced procedural generation with organic growth patterns  ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    print(COLORS.YELLOW + "Choose mode:")
    print("  1. Quick single generation")
    print("  2. Multi-environment demo")
    print(COLORS.RESET)
    
    choice = sys.argv[1] if len(sys.argv) > 1 else input("Enter choice (1-2) [1]: ").strip() or "1"
    
    if choice == "2":
        multi_environment_demo()
    else:
        quick_demo()
    
    print("\n" + COLORS.GREEN + "✨ Generation complete!" + COLORS.RESET)
    print(COLORS.CYAN + "Tip: Run again to see different creatures." + COLORS.RESET)
    print(COLORS.RESET)
