#!/usr/bin/env python3
"""
Visual Creature Generator with Wave Function Collapse
Generates and displays procedural creatures using WFC algorithm
"""

import json
import random
import math
import os
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# ============================================================================
# CONFIGURACIÓN VISUAL - Estilos de renderizado
# ============================================================================

class VisualStyle(Enum):
    ASCII = "ascii"
    UNICODE_BLOCKS = "unicode_blocks"
    BRILLE = "braille"
    COLORED_ASCII = "colored_ascii"

@dataclass
class ColorCodes:
    """Códigos de color ANSI para terminal"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"

COLORS = ColorCodes()

# ============================================================================
# FASE 1: MOTOR DE DEFINICIÓN ECOLÓGICA
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

class EcologicalEngine:
    """Motor que genera tarjetas de criatura desde variables ecológicas"""
    
    BODY_TYPES = ["serpentine", "quadruped", "biped", "hexapod", "amorphous", "radial"]
    ARMOR_TYPES = ["none", "scales", "chitin", "bone_plates", "fur", "feathers", "crystalline"]
    SENSORY_ORGANS = ["eyes", "antennae", "heat_sensors", "echolocation", "chemical_receptors", "electroreceptors"]
    ENERGY_SOURCES = ["photosynthesis", "chemosynthesis", "predation", "scavenging", "filter_feeding", "geothermal"]
    
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
            habitat_weights=weights
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
            return random.choice(["serpentine", "amorphous"])
        
        if score >= 2:
            return random.choice(["quadruped", "radial"])
        elif score <= 0:
            return random.choice(["serpentine", "biped"])
        else:
            return random.choice(self.BODY_TYPES)
    
    def _determine_armor_type(self, env: EcologicalVariables) -> str:
        """Determina el tipo de coraza"""
        if env.temperature < -30:
            return random.choice(["fur", "bone_plates"])
        elif env.temperature > 35:
            return random.choice(["scales", "crystalline"])
        elif env.humidity > 85:
            return random.choice(["scales", "none"])
        elif env.resources < 3:
            return random.choice(["chitin", "none"])
        else:
            return random.choice(self.ARMOR_TYPES)
    
    def _calculate_limbs(self, env: EcologicalVariables, body_type: str) -> int:
        """Calcula número de extremidades"""
        if body_type == "serpentine":
            return random.randint(0, 2)
        elif body_type == "amorphous":
            return 0
        elif body_type == "radial":
            return random.randint(5, 8)
        elif body_type == "hexapod":
            return 6
        elif body_type == "quadruped":
            return 4
        elif body_type == "biped":
            return 2
        
        # Base calculation
        base_limbs = 4
        if env.altitude > 5000:
            base_limbs = max(2, base_limbs - 1)
        if env.humidity > 90:
            base_limbs = max(0, base_limbs - 2)
        
        return base_limbs
    
    def _determine_sensory_organs(self, env: EcologicalVariables) -> List[str]:
        """Determina órganos sensoriales"""
        organs = []
        
        # Visión básica casi siempre presente
        if env.pressure > 500:  # No en profundidades extremas
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
        
        return organs if organs else ["chemical_receptors"]
    
    def _determine_size_class(self, env: EcologicalVariables) -> str:
        """Determina clase de tamaño"""
        # Recursos disponibles afectan tamaño máximo
        if env.resources < 3:
            return random.choice(["tiny", "small"])
        elif env.resources < 6:
            return random.choice(["small", "medium"])
        elif env.resources < 8:
            return random.choice(["medium", "large"])
        else:
            return random.choice(["large", "huge"])
    
    def _calculate_climate_tolerance(self, env: EcologicalVariables) -> Dict[str, float]:
        """Calcula tolerancias climáticas"""
        base_temp = env.temperature
        base_humidity = env.humidity
        
        return {
            "min_temperature": base_temp - random.uniform(10, 25),
            "max_temperature": base_temp + random.uniform(10, 25),
            "min_humidity": max(0, base_humidity - random.uniform(20, 40)),
            "max_humidity": min(100, base_humidity + random.uniform(10, 30)),
            "min_pressure": max(300, env.pressure - random.uniform(100, 200)),
            "max_pressure": min(1013, env.pressure + random.uniform(50, 150))
        }
    
    def _determine_energy_source(self, env: EcologicalVariables) -> str:
        """Determina fuente de energía"""
        if env.temperature > 25 and env.humidity > 60:
            return "photosynthesis"
        elif env.pressure < 400 or env.resources < 2:
            return "chemosynthesis"
        elif env.resources > 7:
            return random.choice(["predation", "scavenging"])
        elif env.humidity > 80:
            return "filter_feeding"
        elif env.altitude > 3000 and env.temperature > 40:
            return "geothermal"
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
            adaptations.append("gill_slits")
        if env.resources < 2:
            adaptations.append("metabolic_stasis")
        if env.resources > 8:
            adaptations.append("rapid_regeneration")
        
        return adaptations if adaptations else ["generalist_metabolism"]
    
    def _generate_wfc_rules(self, env: EcologicalVariables, body_type: str, armor_type: str) -> Tuple:
        """Genera reglas de adyacencia para WFC"""
        # Tipos de tiles posibles
        tile_types = ["head", "body", "limb", "tail", "organ", "habitat", "empty"]
        
        # Reglas de adyacencia básicas
        adjacency_rules = {
            "head": ["body", "organ"],
            "body": ["head", "body", "limb", "tail", "organ"],
            "limb": ["body"],
            "tail": ["body"],
            "organ": ["body", "head"],
            "habitat": ["habitat", "body", "organ"],
            "empty": ["empty", "habitat"]
        }
        
        # Vecinos requeridos según tipo de cuerpo
        required = []
        if body_type in ["quadruped", "hexapod"]:
            required = ["habitat"]
        elif body_type == "serpentine":
            required = ["habitat", "body"]
        elif body_type == "amorphous":
            required = ["habitat"]
        
        # Vecinos prohibidos
        forbidden = []
        if armor_type == "crystalline" and env.humidity > 80:
            forbidden = ["water_deep"]
        if env.temperature > 40:
            forbidden = ["ice"]
        if env.temperature < -20:
            forbidden = ["lava", "hot_spring"]
        
        # Pesos de hábitat
        weights = {
            "head": 0.3,
            "body": 0.5,
            "limb": 0.4 if body_type not in ["serpentine", "amorphous"] else 0.1,
            "tail": 0.2,
            "organ": 0.25,
            "habitat": 0.6,
            "empty": 0.8
        }
        
        # Ajustar pesos según ambiente
        if env.resources < 3:
            weights["habitat"] *= 0.7
            weights["empty"] *= 1.3
        elif env.resources > 7:
            weights["body"] *= 1.2
            weights["organ"] *= 1.3
        
        return adjacency_rules, required, forbidden, weights
    
    def _generate_creature_name(self, env: EcologicalVariables, body_type: str, armor_type: str) -> str:
        """Genera un nombre descriptivo para la criatura"""
        prefixes = {
            "cold": ["Frost", "Ice", "Glacial", "Arctic"],
            "hot": ["Blaze", "Ember", "Solar", "Magma"],
            "wet": ["Aqua", "Marine", "River", "Ocean"],
            "dry": ["Dust", "Sand", "Arid", "Desert"],
            "high": ["Sky", "Cloud", "Peak", "Alpine"],
            "low": ["Deep", "Abyss", "Trench", "Sub"]
        }
        
        body_names = {
            "serpentine": ["Snake", "Wyrm", "Serpent", "Drake"],
            "quadruped": ["Stalker", "Runner", "Beast", "Strider"],
            "biped": ["Walker", "Hunter", "Lurker", "Stalker"],
            "hexapod": ["Skitterer", "Crawler", "Weaver", "Spinner"],
            "amorphous": ["Ooze", "Blob", "Mass", "Slime"],
            "radial": ["Bloom", "Star", "Flower", "Medusa"]
        }
        
        armor_suffixes = {
            "none": "",
            "scales": "scale",
            "chitin": "shell",
            "bone_plates": "bone",
            "fur": "mane",
            "feathers": "plume",
            "crystalline": "crystal"
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
        elif env.altitude < 500:
            prefix_list.extend(prefixes["low"])
        
        prefix = random.choice(prefix_list) if prefix_list else "Wild"
        body_name = random.choice(body_names.get(body_type, ["Creature"]))
        suffix = armor_suffixes.get(armor_type, "")
        
        if suffix:
            return f"{prefix}{body_name}{suffix.capitalize()}"
        else:
            return f"{prefix}{body_name}"

# ============================================================================
# FASE 2: WAVE FUNCTION COLLAPSE VISUAL
# ============================================================================

@dataclass
class Tile:
    """Representa un tile en la grilla WFC"""
    x: int
    y: int
    possibilities: List[str] = field(default_factory=list)
    collapsed: bool = False
    value: Optional[str] = None

class VisualWFC:
    """Implementación visual de Wave Function Collapse para criaturas"""
    
    def __init__(self, width: int = 40, height: int = 25, style: VisualStyle = VisualStyle.COLORED_ASCII):
        self.width = width
        self.height = height
        self.style = style
        self.grid: List[List[Tile]] = []
        self.creature_card: Optional[CreatureCard] = None
        
        # Definición visual de cada tipo de tile
        self.tile_visuals = self._initialize_tile_visuals()
    
    def _initialize_tile_visuals(self) -> Dict[str, Dict]:
        """Inicializa la representación visual de cada tile"""
        return {
            "head": {
                "ascii": "H",
                "unicode": "◉",
                "braille": "⣿",
                "color": COLORS.RED,
                "description": "Head/Cephalic region"
            },
            "body": {
                "ascii": "B",
                "unicode": "█",
                "braille": "⣶",
                "color": COLORS.GREEN,
                "description": "Body segment"
            },
            "limb": {
                "ascii": "L",
                "unicode": "▌",
                "braille": "⢸",
                "color": COLORS.YELLOW,
                "description": "Limb/Appendage"
            },
            "tail": {
                "ascii": "T",
                "unicode": "▽",
                "braille": "⢄",
                "color": COLORS.MAGENTA,
                "description": "Tail/Caudal region"
            },
            "organ": {
                "ascii": "O",
                "unicode": "●",
                "braille": "⣤",
                "color": COLORS.CYAN,
                "description": "Organ/Special structure"
            },
            "habitat": {
                "ascii": "·",
                "unicode": "░",
                "braille": "⢒",
                "color": COLORS.BLUE,
                "description": "Habitat terrain"
            },
            "empty": {
                "ascii": " ",
                "unicode": " ",
                "braille": " ",
                "color": COLORS.RESET,
                "description": "Empty space"
            }
        }
    
    def initialize_grid(self, creature_card: CreatureCard):
        """Inicializa la grilla con las posibilidades basadas en la tarjeta"""
        self.creature_card = creature_card
        self.grid = []
        
        all_tiles = list(creature_card.adjacency_rules.keys())
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Calcular distancia al centro
                center_x = self.width // 2
                center_y = self.height // 2
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                max_dist = math.sqrt(center_x**2 + center_y**2)
                
                # Probabilidad inicial basada en distancia y pesos
                possibilities = []
                weights = creature_card.habitat_weights
                
                for tile_type in all_tiles:
                    weight = weights.get(tile_type, 0.5)
                    
                    # Tiles de criatura más probables cerca del centro
                    if tile_type in ["head", "body", "limb", "tail", "organ"]:
                        probability = weight * (1 - dist / max_dist) * 1.5
                    else:
                        probability = weight * (dist / max_dist) * 0.8
                    
                    # Añadir múltiples veces según probabilidad
                    n_copies = max(1, int(probability * 10))
                    possibilities.extend([tile_type] * n_copies)
                
                # Asegurar al menos algunas posibilidades
                if not possibilities:
                    possibilities = ["empty", "habitat"]
                
                tile = Tile(x=x, y=y, possibilities=possibilities)
                row.append(tile)
            self.grid.append(row)
    
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
            return unique_possibilities + random.uniform(0, 0.1)
    
    def find_lowest_entropy_tile(self) -> Optional[Tile]:
        """Encuentra el tile con menor entropía no colapsado"""
        min_entropy = float('inf')
        candidates = []
        
        for row in self.grid:
            for tile in row:
                if not tile.collapsed:
                    entropy = self.get_entropy(tile)
                    if entropy < min_entropy:
                        min_entropy = entropy
                        candidates = [tile]
                    elif entropy == min_entropy:
                        candidates.append(tile)
        
        if candidates:
            return random.choice(candidates)
        return None
    
    def collapse_tile(self, tile: Tile):
        """Colapsa un tile a un valor específico"""
        if not tile.possibilities:
            tile.value = "empty"
        else:
            # Elegir basado en pesos de la tarjeta
            weights = self.creature_card.habitat_weights
            weighted_choices = []
            
            for poss in tile.possibilities:
                weight = weights.get(poss, 0.5)
                weighted_choices.extend([poss] * int(weight * 10))
            
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
                    # Verificar si este tipo puede estar adyacente al tile actual
                    can_be_adjacent = False
                    
                    # Regla directa: ¿el tile actual permite al vecino?
                    if poss in allowed_neighbors:
                        can_be_adjacent = True
                    
                    # Regla inversa: ¿el vecino permite al tile actual?
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
    
    def run_wfc(self, max_iterations: int = 1000) -> bool:
        """Ejecuta el algoritmo WFC hasta completar o alcanzar iteraciones máximas"""
        iteration = 0
        
        while iteration < max_iterations:
            # Encontrar tile con menor entropía
            tile = self.find_lowest_entropy_tile()
            
            if tile is None:
                return True  # Completado exitosamente
            
            # Colapsar tile
            self.collapse_tile(tile)
            
            # Propagar restricciones
            self.propagate_constraints(tile)
            
            iteration += 1
            
            # Verificar progreso ocasionalmente
            if iteration % 100 == 0:
                remaining = sum(1 for row in self.grid for t in row if not t.collapsed)
                if remaining == 0:
                    return True
        
        return iteration < max_iterations
    
    def render(self) -> str:
        """Renderiza la grilla como string visual"""
        output_lines = []
        
        # Línea superior
        output_lines.append(COLORS.CYAN + "╔" + "═" * (self.width * 2 - 1) + "╗" + COLORS.RESET)
        
        for row in self.grid:
            line = COLORS.CYAN + "║" + COLORS.RESET
            for tile in row:
                visual = self.get_tile_visual(tile.value)
                line += visual
            line += COLORS.CYAN + "║" + COLORS.RESET
            output_lines.append(line)
        
        # Línea inferior
        output_lines.append(COLORS.CYAN + "╚" + "═" * (self.width * 2 - 1) + "╝" + COLORS.RESET)
        
        return "\n".join(output_lines)
    
    def get_tile_visual(self, tile_type: str) -> str:
        """Obtiene la representación visual de un tile"""
        if tile_type is None:
            tile_type = "empty"
        
        visual_data = self.tile_visuals.get(tile_type, self.tile_visuals["empty"])
        
        if self.style == VisualStyle.ASCII:
            char = visual_data["ascii"]
            return f"{char} "
        elif self.style == VisualStyle.UNICODE_BLOCKS:
            char = visual_data["unicode"]
            color = visual_data["color"]
            return f"{color}{char}{char}{COLORS.RESET}"
        elif self.style == VisualStyle.BRILLE:
            char = visual_data["braille"]
            color = visual_data["color"]
            return f"{color}{char}{COLORS.RESET}"
        elif self.style == VisualStyle.COLORED_ASCII:
            char = visual_data["ascii"]
            color = visual_data["color"]
            return f"{color}{char}{char}{COLORS.RESET}"
        else:
            return visual_data["ascii"] + " "
    
    def render_legend(self) -> str:
        """Renderiza la leyenda de tiles"""
        legend_lines = [COLORS.BOLD + "\n📊 TILE LEGEND:" + COLORS.RESET]
        
        for tile_type, visual_data in self.tile_visuals.items():
            if tile_type == "empty":
                continue
            
            color = visual_data["color"]
            if self.style in [VisualStyle.UNICODE_BLOCKS, VisualStyle.COLORED_ASCII]:
                symbol = f"{color}{visual_data['unicode']}{COLORS.RESET}"
            else:
                symbol = f"{color}{visual_data['ascii']}{COLORS.RESET}"
            
            desc = visual_data["description"]
            legend_lines.append(f"  {symbol} {desc}")
        
        return "\n".join(legend_lines)

# ============================================================================
# SISTEMA PRINCIPAL DE GENERACIÓN VISUAL
# ============================================================================

class VisualCreatureGenerator:
    """Sistema principal que integra generación ecológica con WFC visual"""
    
    def __init__(self, width: int = 50, height: int = 30, style: VisualStyle = VisualStyle.COLORED_ASCII):
        self.ecological_engine = EcologicalEngine()
        self.width = width
        self.height = height
        self.style = style
    
    def generate_and_display(self, env_vars: EcologicalVariables, show_details: bool = True):
        """Genera y muestra una criatura completa"""
        print("\n" + "="*80)
        print(COLORS.BOLD + COLORS.CYAN + "🧬 PROCEDURAL CREATURE GENERATION SYSTEM" + COLORS.RESET)
        print("="*80)
        
        # Fase 1: Generar tarjeta de criatura
        print(COLORS.YELLOW + "\n📋 PHASE 1: ECOLOGICAL ANALYSIS & CREATURE CARD GENERATION" + COLORS.RESET)
        print("-" * 80)
        
        creature_card = self.ecological_engine.generate_creature_card(env_vars)
        
        if show_details:
            self._display_creature_card(creature_card)
        
        # Fase 2: WFC Visual
        print(COLORS.GREEN + "\n🎨 PHASE 2: WAVE FUNCTION COLLAPSE - VISUAL GENERATION" + COLORS.RESET)
        print("-" * 80)
        
        wfc = VisualWFC(width=self.width, height=self.height, style=self.style)
        wfc.initialize_grid(creature_card)
        
        print(f"Grid initialized: {self.width}x{self.height}")
        print("Running WFC algorithm...")
        
        success = wfc.run_wfc(max_iterations=2000)
        
        if success:
            print(COLORS.GREEN + "✓ WFC completed successfully!" + COLORS.RESET)
        else:
            print(COLORS.YELLOW + "⚠ WFC reached maximum iterations (result may be incomplete)" + COLORS.RESET)
        
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
        print(f"  Body Type: {card.body_type}")
        print(f"  Limbs: {card.limbs}")
        print(f"  Armor: {card.armor_type}")
        print(f"  Size Class: {card.size_class}")
        print(f"  Sensory Organs: {', '.join(card.sensory_organs)}")
        
        print(f"\n{COLORS.BOLD}⚙️ SURVIVAL MECHANISMS:{COLORS.RESET}")
        print(f"  Energy Source: {card.energy_source}")
        print(f"  Climate Tolerance:")
        print(f"    Temp Range: {card.climate_tolerance['min_temperature']:.1f}°C to {card.climate_tolerance['max_temperature']:.1f}°C")
        print(f"    Humidity Range: {card.climate_tolerance['min_humidity']:.1f}% to {card.climate_tolerance['max_humidity']:.1f}%")
        print(f"  Special Adaptations: {', '.join(card.special_adaptations)}")
        
        print(f"\n{COLORS.BOLD}🔗 WFC CONSTRAINTS:{COLORS.RESET}")
        print(f"  Required Neighbors: {', '.join(card.required_neighbors) if card.required_neighbors else 'None'}")
        print(f"  Forbidden Neighbors: {', '.join(card.forbidden_neighbors) if card.forbidden_neighbors else 'None'}")
    
    def _display_generation_stats(self, card: CreatureCard, wfc: VisualWFC):
        """Muestra estadísticas de la generación"""
        print(f"\n{COLORS.BOLD}📈 GENERATION STATISTICS:{COLORS.RESET}")
        
        # Contar tiles por tipo
        tile_counts = {}
        for row in wfc.grid:
            for tile in row:
                if tile.value:
                    tile_counts[tile.value] = tile_counts.get(tile.value, 0) + 1
        
        total_tiles = sum(tile_counts.values())
        creature_tiles = sum(count for tile_type, count in tile_counts.items() 
                           if tile_type in ["head", "body", "limb", "tail", "organ"])
        habitat_ratio = creature_tiles / total_tiles * 100 if total_tiles > 0 else 0
        
        print(f"  Total Tiles: {total_tiles}")
        print(f"  Creature Tiles: {creature_tiles} ({habitat_ratio:.1f}%)")
        print(f"  Habitat Tiles: {tile_counts.get('habitat', 0)}")
        print(f"  Empty Space: {tile_counts.get('empty', 0)}")
        
        print(f"\n  Tile Distribution:")
        for tile_type, count in sorted(tile_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = count / total_tiles * 100 if total_tiles > 0 else 0
            bar = "█" * int(percentage / 2)
            print(f"    {tile_type:10}: {count:4} ({percentage:5.1f}%) {bar}")

# ============================================================================
# DEMOSTRACIÓN Y EJEMPLOS DE USO
# ============================================================================

def demo_multiple_environments():
    """Demuestra generación en múltiples ambientes"""
    generator = VisualCreatureGenerator(width=50, height=28, style=VisualStyle.COLORED_ASCII)
    
    environments = [
        EcologicalVariables(
            temperature=-25, humidity=30, altitude=5500, pressure=450, resources=4,
        ),
        EcologicalVariables(
            temperature=35, humidity=85, altitude=100, pressure=1010, resources=8,
        ),
        EcologicalVariables(
            temperature=45, humidity=15, altitude=200, pressure=1000, resources=3,
        ),
        EcologicalVariables(
            temperature=5, humidity=95, altitude=-200, pressure=1100, resources=6,
        ),
    ]
    
    env_names = [
        "❄️ ALPINE EXTREME (Cold, High Altitude)",
        "🌴 TROPICAL JUNGLE (Hot, Humid, Resource-Rich)",
        "🏜️ ARID DESERT (Very Hot, Dry, Scarce Resources)",
        "🌊 DEEP OCEANIC TRENCH (Cold, High Pressure, Wet)"
    ]
    
    for i, (env, name) in enumerate(zip(environments, env_names)):
        print("\n\n" + "="*80)
        print(COLORS.BOLD + COLORS.MAGENTA + f"ENVIRONMENT {i+1}: {name}" + COLORS.RESET)
        print("="*80)
        
        generator.generate_and_display(env, show_details=(i == 0))
        
        if i < len(environments) - 1:
            input(COLORS.CYAN + "\n⏎ Press Enter to generate next creature..." + COLORS.RESET)
            os.system('clear' if os.name == 'posix' else 'cls')

def interactive_mode():
    """Modo interactivo para generar criaturas personalizadas"""
    generator = VisualCreatureGenerator(width=50, height=28, style=VisualStyle.COLORED_ASCII)
    
    print(COLORS.BOLD + "\n🎮 INTERACTIVE CREATURE GENERATOR" + COLORS.RESET)
    print("Enter environmental parameters (or press Enter for random values):\n")
    
    try:
        temp_input = input(f"Temperature (-50 to 50°C) [random]: ")
        temp = float(temp_input) if temp_input else random.uniform(-30, 40)
        
        humid_input = input(f"Humidity (0 to 100%) [random]: ")
        humid = float(humid_input) if humid_input else random.uniform(20, 90)
        
        alt_input = input(f"Altitude (0 to 8000m) [random]: ")
        alt = float(alt_input) if alt_input else random.uniform(0, 5000)
        
        press_input = input(f"Pressure (300 to 1013 hPa) [random]: ")
        press = float(press_input) if press_input else random.uniform(500, 1013)
        
        res_input = input(f"Resources (0 to 10) [random]: ")
        res = float(res_input) if res_input else random.uniform(2, 9)
        
        env = EcologicalVariables(
            temperature=temp,
            humidity=humid,
            altitude=alt,
            pressure=press,
            resources=res
        )
        
        generator.generate_and_display(env, show_details=True)
        
    except KeyboardInterrupt:
        print("\n\nGeneration cancelled.")
    except Exception as e:
        print(f"\nError: {e}")
        print("Using default random environment...")
        env = EcologicalVariables(
            temperature=random.uniform(-30, 40),
            humidity=random.uniform(20, 90),
            altitude=random.uniform(0, 5000),
            pressure=random.uniform(500, 1013),
            resources=random.uniform(2, 9)
        )
        generator.generate_and_display(env, show_details=True)

# ============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Limpiar pantalla
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print(COLORS.BOLD + COLORS.CYAN + """
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║     🧬 PROCEDURAL CREATURE GENERATOR with WAVE FUNCTION COLLAPSE ║
    ║                                                                   ║
    ║     Generates unique creatures based on ecological conditions    ║
    ║     and renders them using WFC algorithm                         ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    print(COLORS.YELLOW + "Choose mode:")
    print("  1. Demo (multiple predefined environments)")
    print("  2. Interactive (custom parameters)")
    print("  3. Quick single generation")
    print(COLORS.RESET)
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("Enter choice (1-3) [1]: ").strip() or "1"
    
    if choice == "1":
        demo_multiple_environments()
    elif choice == "2":
        interactive_mode()
    else:
        # Generación rápida aleatoria
        generator = VisualCreatureGenerator(width=50, height=28, style=VisualStyle.COLORED_ASCII)
        env = EcologicalVariables(
            temperature=random.uniform(-30, 40),
            humidity=random.uniform(20, 90),
            altitude=random.uniform(0, 5000),
            pressure=random.uniform(500, 1013),
            resources=random.uniform(2, 9)
        )
        generator.generate_and_display(env, show_details=True)
    
    print("\n" + COLORS.GREEN + "✨ Generation complete!" + COLORS.RESET)
    print(COLORS.CYAN + "Tip: Run with different parameters to see varied creatures." + COLORS.RESET)
    print(COLORS.RESET)
