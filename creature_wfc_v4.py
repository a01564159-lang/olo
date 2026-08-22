#!/usr/bin/env python3
"""
CREATURE WFC PIPELINE - VERSIÓN CORREGIDA V4.0
Generación procedural de criaturas con Wave Function Collapse
- Algoritmo WFC iterativo (sin recursión)
- Reglas de adyacencia mejoradas para todos los planes corporales
- Renderizado vectorial de alta calidad
"""

import random
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum
from PIL import Image, ImageDraw

# ============================================================================
# CONFIGURACIÓN
# ============================================================================
OUTPUT_DIR = "creature_outputs_v4"
TILE_SIZE = 64
GRID_SIZE = 12  # Grilla más pequeña para mayor convergencia
MAX_RESTARTS = 50  # Máximo de reinicios antes de fallar
MAX_ITERATIONS = 5000  # Máximo de iteraciones por intento

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================================
# ENUMERACIONES Y TIPOS
# ============================================================================
class TileType(Enum):
    HEAD = "head"
    BODY_STRAIGHT = "body_straight"
    BODY_CURVE = "body_curve"
    BODY_TJUNCTION = "body_tjunction"
    BODY_CROSS = "body_cross"
    LIMB_BASE = "limb_base"
    LIMB_MID = "limb_mid"
    LIMB_END = "limb_end"
    TAIL_BASE = "tail_base"
    TAIL_MID = "tail_mid"
    TAIL_TIP = "tail_tip"
    CENTER_RADIAL = "center_radial"
    ARM_RADIAL = "arm_radial"
    EMPTY = "empty"

class BodyPlan(Enum):
    BIPED = "biped"
    HEXAPOD = "hexapod"
    CEPHALOPOD = "cephalopod"
    SERPENTINE = "serpentine"
    RADIAL = "radial"

class Direction(Enum):
    N = 0  # Norte (arriba)
    E = 1  # Este (derecha)
    S = 2  # Sur (abajo)
    W = 3  # Oeste (izquierda)

OPPOSITE = {Direction.N: Direction.S, Direction.S: Direction.N, 
            Direction.E: Direction.W, Direction.W: Direction.E}

# ============================================================================
# TILE WFC
# ============================================================================
class WFCTile:
    def __init__(self, id: str, type: TileType, body_plan: BodyPlan, 
                 edges: Dict[Direction, str], weight: float = 1.0):
        self.id = id
        self.type = type
        self.body_plan = body_plan
        self.edges = edges  # {'N': 'connector_type', 'E': ..., 'S': ..., 'W': ...}
        self.weight = weight
    
    def get_edge(self, dir: Direction) -> str:
        return self.edges.get(dir, 'empty')
    
    def __repr__(self):
        return f"Tile({self.id}, {self.type.value})"

# ============================================================================
# FÁBRICA DE TILES POR PLAN CORPORAL
# ============================================================================
class TileFactory:
    @staticmethod
    def create_biped_tiles() -> List[WFCTile]:
        tiles = []
        # Cabeza - solo conecta cuerpo por abajo
        tiles.append(WFCTile("head", TileType.HEAD, BodyPlan.BIPED,
                            {'N': 'empty', 'E': 'empty', 'S': 'body_back', 'W': 'empty'}, weight=1.0))
        
        # Cuerpo recto vertical
        tiles.append(WFCTile("body_straight_v", TileType.BODY_STRAIGHT, BodyPlan.BIPED,
                            {'N': 'body_front', 'E': 'empty', 'S': 'body_back', 'W': 'empty'}, weight=3.0))
        
        # Cuerpo con curva
        tiles.append(WFCTile("body_curve_se", TileType.BODY_CURVE, BodyPlan.BIPED,
                            {'N': 'body_front', 'E': 'empty', 'S': 'empty', 'W': 'body_back'}, weight=1.5))
        tiles.append(WFCTile("body_curve_sw", TileType.BODY_CURVE, BodyPlan.BIPED,
                            {'N': 'body_front', 'E': 'body_back', 'S': 'empty', 'W': 'empty'}, weight=1.5))
        
        # Extremidad base (conecta cuerpo arriba, pierna abajo)
        tiles.append(WFCTile("limb_base_l", TileType.LIMB_BASE, BodyPlan.BIPED,
                            {'N': 'body_front', 'E': 'empty', 'S': 'limb_top', 'W': 'empty'}, weight=1.5))
        tiles.append(WFCTile("limb_base_r", TileType.LIMB_BASE, BodyPlan.BIPED,
                            {'N': 'body_front', 'E': 'limb_top', 'S': 'empty', 'W': 'empty'}, weight=1.5))
        
        # Extremidad medio
        tiles.append(WFCTile("limb_mid", TileType.LIMB_MID, BodyPlan.BIPED,
                            {'N': 'limb_bottom', 'E': 'empty', 'S': 'limb_top', 'W': 'empty'}, weight=2.0))
        
        # Extremidad punta (pie)
        tiles.append(WFCTile("limb_end", TileType.LIMB_END, BodyPlan.BIPED,
                            {'N': 'limb_bottom', 'E': 'empty', 'S': 'empty', 'W': 'empty'}, weight=1.0))
        
        # Cola base
        tiles.append(WFCTile("tail_base", TileType.TAIL_BASE, BodyPlan.BIPED,
                            {'N': 'body_front', 'E': 'empty', 'S': 'tail_top', 'W': 'empty'}, weight=1.0))
        
        # Cola segmentos
        tiles.append(WFCTile("tail_mid", TileType.TAIL_MID, BodyPlan.BIPED,
                            {'N': 'tail_bottom', 'E': 'empty', 'S': 'tail_top', 'W': 'empty'}, weight=2.0))
        tiles.append(WFCTile("tail_tip", TileType.TAIL_TIP, BodyPlan.BIPED,
                            {'N': 'tail_bottom', 'E': 'empty', 'S': 'empty', 'W': 'empty'}, weight=1.0))
        
        # Vacío
        tiles.append(WFCTile("empty", TileType.EMPTY, BodyPlan.BIPED,
                            {'N': 'empty', 'E': 'empty', 'S': 'empty', 'W': 'empty'}, weight=5.0))
        
        return tiles
    
    @staticmethod
    def create_hexapod_tiles() -> List[WFCTile]:
        tiles = []
        # Cabeza
        tiles.append(WFCTile("head", TileType.HEAD, BodyPlan.HEXAPOD,
                            {'N': 'empty', 'E': 'empty', 'S': 'body_back', 'W': 'empty'}, weight=1.0))
        
        # Cuerpo recto
        tiles.append(WFCTile("body_straight_v", TileType.BODY_STRAIGHT, BodyPlan.HEXAPOD,
                            {'N': 'body_front', 'E': 'empty', 'S': 'body_back', 'W': 'empty'}, weight=3.0))
        
        # Cuerpo con extremidades (3 pares)
        tiles.append(WFCTile("body_legs_front", TileType.LIMB_BASE, BodyPlan.HEXAPOD,
                            {'N': 'body_front', 'E': 'limb_side', 'S': 'body_back', 'W': 'limb_side'}, weight=2.0))
        tiles.append(WFCTile("body_legs_mid", TileType.LIMB_BASE, BodyPlan.HEXAPOD,
                            {'N': 'body_front', 'E': 'limb_side', 'S': 'body_back', 'W': 'limb_side'}, weight=2.0))
        tiles.append(WFCTile("body_legs_rear", TileType.LIMB_BASE, BodyPlan.HEXAPOD,
                            {'N': 'body_front', 'E': 'limb_side', 'S': 'body_back', 'W': 'limb_side'}, weight=2.0))
        
        # Extremidad lateral
        tiles.append(WFCTile("limb_side_outer", TileType.LIMB_MID, BodyPlan.HEXAPOD,
                            {'N': 'empty', 'E': 'limb_inner', 'S': 'empty', 'W': 'empty'}, weight=1.5))
        tiles.append(WFCTile("limb_side_mid", TileType.LIMB_MID, BodyPlan.HEXAPOD,
                            {'N': 'empty', 'E': 'limb_inner', 'S': 'empty', 'W': 'limb_outer'}, weight=1.5))
        tiles.append(WFCTile("limb_side_end", TileType.LIMB_END, BodyPlan.HEXAPOD,
                            {'N': 'empty', 'E': 'empty', 'S': 'empty', 'W': 'limb_outer'}, weight=1.0))
        
        # Cola
        tiles.append(WFCTile("tail_base", TileType.TAIL_BASE, BodyPlan.HEXAPOD,
                            {'N': 'body_front', 'E': 'empty', 'S': 'tail_top', 'W': 'empty'}, weight=1.0))
        tiles.append(WFCTile("tail_tip", TileType.TAIL_TIP, BodyPlan.HEXAPOD,
                            {'N': 'tail_bottom', 'E': 'empty', 'S': 'empty', 'W': 'empty'}, weight=1.0))
        
        # Vacío
        tiles.append(WFCTile("empty", TileType.EMPTY, BodyPlan.HEXAPOD,
                            {'N': 'empty', 'E': 'empty', 'S': 'empty', 'W': 'empty'}, weight=8.0))
        
        return tiles
    
    @staticmethod
    def create_serpentine_tiles() -> List[WFCTile]:
        tiles = []
        # Cabeza
        tiles.append(WFCTile("head", TileType.HEAD, BodyPlan.SERPENTINE,
                            {'N': 'empty', 'E': 'empty', 'S': 'body_back', 'W': 'empty'}, weight=1.0))
        
        # Cuerpo recto vertical
        tiles.append(WFCTile("body_straight_v", TileType.BODY_STRAIGHT, BodyPlan.SERPENTINE,
                            {'N': 'body_front', 'E': 'empty', 'S': 'body_back', 'W': 'empty'}, weight=2.0))
        
        # Cuerpo recto horizontal
        tiles.append(WFCTile("body_straight_h", TileType.BODY_STRAIGHT, BodyPlan.SERPENTINE,
                            {'N': 'empty', 'E': 'body_back', 'S': 'empty', 'W': 'body_front'}, weight=2.0))
        
        # Curvas
        tiles.append(WFCTile("body_curve_ne", TileType.BODY_CURVE, BodyPlan.SERPENTINE,
                            {'N': 'empty', 'E': 'body_back', 'S': 'body_front', 'W': 'empty'}, weight=2.0))
        tiles.append(WFCTile("body_curve_nw", TileType.BODY_CURVE, BodyPlan.SERPENTINE,
                            {'N': 'empty', 'E': 'empty', 'S': 'body_front', 'W': 'body_back'}, weight=2.0))
        tiles.append(WFCTile("body_curve_se", TileType.BODY_CURVE, BodyPlan.SERPENTINE,
                            {'N': 'body_front', 'E': 'body_back', 'S': 'empty', 'W': 'empty'}, weight=2.0))
        tiles.append(WFCTile("body_curve_sw", TileType.BODY_CURVE, BodyPlan.SERPENTINE,
                            {'N': 'body_front', 'E': 'empty', 'S': 'empty', 'W': 'body_back'}, weight=2.0))
        
        # Cola
        tiles.append(WFCTile("tail_tip", TileType.TAIL_TIP, BodyPlan.SERPENTINE,
                            {'N': 'body_front', 'E': 'empty', 'S': 'empty', 'W': 'empty'}, weight=1.0))
        
        # Vacío
        tiles.append(WFCTile("empty", TileType.EMPTY, BodyPlan.SERPENTINE,
                            {'N': 'empty', 'E': 'empty', 'S': 'empty', 'W': 'empty'}, weight=6.0))
        
        return tiles
    
    @staticmethod
    def create_cephalopod_tiles() -> List[WFCTile]:
        tiles = []
        # Manto/cabeza grande (ocupa centro, conecta tentáculos alrededor)
        tiles.append(WFCTile("mantle_center", TileType.CENTER_RADIAL, BodyPlan.CEPHALOPOD,
                            {'N': 'tentacle_top', 'E': 'tentacle_top', 'S': 'body_back', 'W': 'tentacle_top'}, weight=1.0))
        
        # Tentáculo segmento superior
        tiles.append(WFCTile("tentacle_upper", TileType.ARM_RADIAL, BodyPlan.CEPHALOPOD,
                            {'N': 'empty', 'E': 'empty', 'S': 'tentacle_bottom', 'W': 'empty'}, weight=2.0))
        
        # Tentáculo segmento medio
        tiles.append(WFCTile("tentacle_mid", TileType.ARM_RADIAL, BodyPlan.CEPHALOPOD,
                            {'N': 'tentacle_top', 'E': 'empty', 'S': 'tentacle_bottom', 'W': 'empty'}, weight=2.0))
        
        # Tentáculo punta
        tiles.append(WFCTile("tentacle_tip", TileType.ARM_RADIAL, BodyPlan.CEPHALOPOD,
                            {'N': 'tentacle_top', 'E': 'empty', 'S': 'empty', 'W': 'empty'}, weight=1.5))
        
        # Sifón/cola
        tiles.append(WFCTile("siphon", TileType.TAIL_TIP, BodyPlan.CEPHALOPOD,
                            {'N': 'body_front', 'E': 'empty', 'S': 'empty', 'W': 'empty'}, weight=1.0))
        
        # Vacío
        tiles.append(WFCTile("empty", TileType.EMPTY, BodyPlan.CEPHALOPOD,
                            {'N': 'empty', 'E': 'empty', 'S': 'empty', 'W': 'empty'}, weight=10.0))
        
        return tiles
    
    @staticmethod
    def create_radial_tiles() -> List[WFCTile]:
        tiles = []
        # Centro radial (5 brazos)
        tiles.append(WFCTile("center_5arm", TileType.CENTER_RADIAL, BodyPlan.RADIAL,
                            {'N': 'arm_top', 'E': 'arm_top', 'S': 'arm_top', 'W': 'arm_top'}, weight=1.0))
        
        # Brazo segmento
        tiles.append(WFCTile("arm_segment", TileType.ARM_RADIAL, BodyPlan.RADIAL,
                            {'N': 'arm_top', 'E': 'empty', 'S': 'arm_bottom', 'W': 'empty'}, weight=2.0))
        
        # Brazo punta
        tiles.append(WFCTile("arm_tip", TileType.ARM_RADIAL, BodyPlan.RADIAL,
                            {'N': 'arm_top', 'E': 'empty', 'S': 'empty', 'W': 'empty'}, weight=1.5))
        
        # Vacío
        tiles.append(WFCTile("empty", TileType.EMPTY, BodyPlan.RADIAL,
                            {'N': 'empty', 'E': 'empty', 'S': 'empty', 'W': 'empty'}, weight=12.0))
        
        return tiles
    
    @classmethod
    def create_tiles_for_plan(cls, plan: BodyPlan) -> List[WFCTile]:
        factories = {
            BodyPlan.BIPED: cls.create_biped_tiles,
            BodyPlan.HEXAPOD: cls.create_hexapod_tiles,
            BodyPlan.SERPENTINE: cls.create_serpentine_tiles,
            BodyPlan.CEPHALOPOD: cls.create_cephalopod_tiles,
            BodyPlan.RADIAL: cls.create_radial_tiles,
        }
        return factories[plan]()

# ============================================================================
# MOTOR WFC ITERATIVO
# ============================================================================
class WFCEngine:
    def __init__(self, tiles: List[WFCTile], width: int = GRID_SIZE, height: int = GRID_SIZE):
        self.tiles = tiles
        self.width = width
        self.height = height
        self.grid: List[List[Set[int]]] = []  # Índices de tiles posibles
        self.collapsed: List[List[bool]] = []
        self.tile_map = {i: t for i, t in enumerate(tiles)}
        
        # Precomputar compatibilidades
        self.compatibility = self._precompute_compatibility()
    
    def _precompute_compatibility(self) -> Dict[Tuple[int, int, Direction], bool]:
        """Precomputa qué tiles son compatibles en cada dirección."""
        compat = {}
        for i, tile_a in enumerate(self.tiles):
            for j, tile_b in enumerate(self.tiles):
                for dir in Direction:
                    edge_a = tile_a.get_edge(dir)
                    edge_b = tile_b.get_edge(OPPOSITE[dir])
                    
                    # Compatibilidad: ambos empty, o conectores opuestos coinciden
                    is_compat = (edge_a == 'empty' and edge_b == 'empty') or \
                               (edge_a != 'empty' and edge_b != 'empty' and 
                                self._connectors_match(edge_a, edge_b))
                    compat[(i, j, dir)] = is_compat
        return compat
    
    def _connectors_match(self, edge_a: str, edge_b: str) -> bool:
        """Verifica si dos conectores pueden unirse."""
        # Conectores que coinciden
        matches = {
            'body_front': ['body_back'],
            'body_back': ['body_front'],
            'limb_top': ['limb_bottom'],
            'limb_bottom': ['limb_top'],
            'limb_side': ['limb_inner'],
            'limb_inner': ['limb_side', 'limb_outer'],
            'limb_outer': ['limb_inner'],
            'tail_top': ['tail_bottom'],
            'tail_bottom': ['tail_top'],
            'tentacle_top': ['tentacle_bottom'],
            'tentacle_bottom': ['tentacle_top'],
            'arm_top': ['arm_bottom'],
            'arm_bottom': ['arm_top'],
        }
        return edge_b in matches.get(edge_a, [])
    
    def generate(self) -> Optional[List[List[int]]]:
        """Ejecuta WFC de forma iterativa. Retorna índices de tiles o None si falla."""
        # Inicializar
        self.grid = [[set(range(len(self.tiles))) for _ in range(self.width)] for _ in range(self.height)]
        self.collapsed = [[False for _ in range(self.width)] for _ in range(self.height)]
        
        to_propagate = []
        
        # Semilla inicial en el centro
        center_x, center_y = self.width // 2, self.height // 2
        center_types = [TileType.HEAD, TileType.CENTER_RADIAL, TileType.BODY_STRAIGHT]
        possible_centers = [i for i, t in self.tile_map.items() if t.type in center_types]
        
        if not possible_centers:
            possible_centers = list(range(len(self.tiles)))
        
        seed_idx = random.choice(possible_centers)
        self.grid[center_y][center_x] = {seed_idx}
        self.collapsed[center_y][center_x] = True
        to_propagate.append((center_x, center_y))
        
        iterations = 0
        
        while to_propagate and iterations < MAX_ITERATIONS:
            iterations += 1
            
            # Propagación
            x, y = to_propagate.pop(0)
            current_options = self.grid[y][x]
            
            for dx, dy, dir in [(0, -1, Direction.N), (0, 1, Direction.S), 
                                (-1, 0, Direction.W), (1, 0, Direction.E)]:
                nx, ny = x + dx, y + dy
                
                if 0 <= nx < self.width and 0 <= ny < self.height and not self.collapsed[ny][nx]:
                    neighbor_options = self.grid[ny][nx]
                    
                    # Filtrar opciones incompatibles
                    new_options = set()
                    for n_idx in neighbor_options:
                        for c_idx in current_options:
                            if self.compatibility.get((c_idx, n_idx, dir), False):
                                new_options.add(n_idx)
                                break
                    
                    if new_options != neighbor_options:
                        self.grid[ny][nx] = new_options
                        
                        if len(new_options) == 1 and not self.collapsed[ny][nx]:
                            self.collapsed[ny][nx] = True
                            to_propagate.append((nx, ny))
                        elif len(new_options) == 0:
                            return None  # Contradicción
            
            # Colapso: elegir celda con menor entropía
            if not to_propagate:
                min_entropy = float('inf')
                candidates = []
                
                for y in range(self.height):
                    for x in range(self.width):
                        if not self.collapsed[y][x] and len(self.grid[y][x]) > 1:
                            entropy = len(self.grid[y][x])
                            if entropy < min_entropy:
                                min_entropy = entropy
                                candidates = [(x, y)]
                            elif entropy == min_entropy:
                                candidates.append((x, y))
                
                if candidates:
                    x, y = random.choice(candidates)
                    options = list(self.grid[y][x])
                    
                    # Peso por probabilidad
                    weights = [self.tile_map[i].weight for i in options]
                    chosen = random.choices(options, weights=weights, k=1)[0]
                    
                    self.grid[y][x] = {chosen}
                    self.collapsed[y][x] = True
                    to_propagate.append((x, y))
        
        # Verificar éxito
        if all(self.collapsed[y][x] for x in range(self.width) for y in range(self.height)):
            return [[list(self.grid[y][x])[0] for x in range(self.width)] for y in range(self.height)]
        
        return None

# ============================================================================
# RENDERIZADO VECTORIAL
# ============================================================================
class CreatureRenderer:
    def __init__(self, tiles: List[WFCTile], grid_result: List[List[int]], palette: List[str]):
        self.tiles = tiles
        self.grid = grid_result
        self.palette = palette
        self.tile_size = TILE_SIZE
    
    def render(self) -> Image.Image:
        width = len(self.grid[0]) * self.tile_size
        height = len(self.grid) * self.tile_size
        
        img = Image.new('RGB', (width, height), self.palette[0])
        draw = ImageDraw.Draw(img)
        
        for y, row in enumerate(self.grid):
            for x, tile_idx in enumerate(row):
                tile = self.tiles[tile_idx]
                px, py = x * self.tile_size, y * self.tile_size
                self._draw_tile(draw, tile, px, py)
        
        return img
    
    def _draw_tile(self, draw: ImageDraw.Draw, tile: WFCTile, x: int, y: int):
        ts = self.tile_size
        colors = {
            TileType.HEAD: self.palette[1],
            TileType.BODY_STRAIGHT: self.palette[2],
            TileType.BODY_CURVE: self.palette[2],
            TileType.LIMB_BASE: self.palette[2],
            TileType.LIMB_MID: self.palette[2],
            TileType.LIMB_END: self.palette[2],
            TileType.TAIL_BASE: self.palette[3],
            TileType.TAIL_MID: self.palette[3],
            TileType.TAIL_TIP: self.palette[3],
            TileType.CENTER_RADIAL: self.palette[1],
            TileType.ARM_RADIAL: self.palette[2],
            TileType.EMPTY: self.palette[0],
        }
        
        color = colors.get(tile.type, self.palette[0])
        
        if tile.type == TileType.EMPTY:
            return  # No dibujar nada
        
        # Dibujar forma básica según tipo
        if tile.type in [TileType.HEAD, TileType.CENTER_RADIAL]:
            # Óvalo/círculo
            margin = ts // 8
            draw.ellipse([x+margin, y+margin, x+ts-margin, y+ts-margin], fill=color)
            # Ojos
            eye_color = '#FFFFFF'
            eye_size = ts // 10
            draw.ellipse([x+ts//3-eye_size, y+ts//3-eye_size, x+ts//3+eye_size, y+ts//3+eye_size], fill=eye_color)
            draw.ellipse([x+2*ts//3-eye_size, y+ts//3-eye_size, x+2*ts//3+eye_size, y+ts//3+eye_size], fill=eye_color)
        
        elif tile.type in [TileType.BODY_STRAIGHT, TileType.BODY_CURVE, TileType.LIMB_MID, TileType.ARM_RADIAL]:
            # Rectángulo con textura
            margin = ts // 6
            draw.rectangle([x+margin, y+margin, x+ts-margin, y+ts-margin], fill=color)
            # Líneas de segmento
            line_y = y + ts // 2
            draw.line([x+margin, line_y, x+ts-margin, line_y], fill=self.palette[0], width=2)
        
        elif tile.type in [TileType.LIMB_BASE, TileType.LIMB_END, TileType.TAIL_BASE, TileType.TAIL_MID, TileType.TAIL_TIP]:
            # Forma estrecha
            margin_x = ts // 3
            margin_y = ts // 8
            draw.rectangle([x+margin_x, y+margin_y, x+ts-margin_x, y+ts-margin_y], fill=color)

# ============================================================================
# GENERADOR ECOLÓGICO
# ============================================================================
def generate_creature_card(temp: float, humidity: float, altitude: float, 
                          pressure: float, resources: float) -> Tuple[Dict, BodyPlan]:
    """Genera tarjeta de criatura basada en variables ecológicas."""
    
    # Determinar plan corporal
    if altitude > 3000:
        body_plan = BodyPlan.BIPED  # Eficiente en altura
    elif humidity > 80 and altitude < 500:
        body_plan = BodyPlan.CEPHALOPOD  # Acuático
    elif humidity < 20:
        body_plan = BodyPlan.SERPENTINE  # Conserva agua
    elif temp > 25 and humidity > 60:
        body_plan = BodyPlan.HEXAPOD  # Tropical
    else:
        body_plan = BodyPlan.RADIAL  # Generalista
    
    # Paleta de colores basada en ambiente
    if temp < 0:
        palette = ['#E0F7FA', '#B2EBF2', '#81D4FA', '#FFFFFF']  # Hielo
    elif temp > 35:
        palette = ['#FFF3E0', '#FFE0B2', '#FFCA28', '#E65100']  # Desierto
    elif altitude < 0:
        palette = ['#0D47A1', '#1565C0', '#1976D2', '#42A5F5']  # Oceánico
    elif humidity > 70:
        palette = ['#1B5E20', '#2E7D32', '#4CAF50', '#81C784']  # Selva
    else:
        palette = ['#4E342E', '#5D4037', '#795548', '#A1887F']  # Tierra
    
    # Adaptaciones
    adaptations = []
    if temp < 0:
        adaptations.append("capa_antifreeze")
        adaptations.append("metabolismo_lento")
    elif temp > 35:
        adaptations.append("refrigeracion_activa")
        adaptations.append("conservacion_agua")
    
    if humidity > 80:
        adaptations.append("branquias")
        adaptations.append("piel_permeable")
    elif humidity < 20:
        adaptations.append("exoesqueleto_impermeable")
        adaptations.append("almacenamiento_agua")
    
    if altitude > 3000:
        adaptations.append("hemoglobina_eficiente")
        adaptations.append("pulmones_amplios")
    
    if pressure < 0.8:
        adaptations.append("cuerpo_presurizado")
    
    card = {
        "species_id": f"specie_{body_plan.value}_{random.randint(1000, 9999)}",
        "body_plan": body_plan.value,
        "ecological_params": {
            "temperature": temp,
            "humidity": humidity,
            "altitude": altitude,
            "pressure": pressure,
            "resources": resources
        },
        "adaptations": adaptations,
        "palette": palette,
        "energy_source": "quimiosintesis" if altitude < 0 else "heterotrofo",
        "locomotion": "bipedal" if body_plan == BodyPlan.BIPED else 
                     "hexapedal" if body_plan == BodyPlan.HEXAPOD else
                     "undulatory" if body_plan == BodyPlan.SERPENTINE else
                     "jet_propulsion" if body_plan == BodyPlan.CEPHALOPOD else
                     "radial_crawling",
        "timestamp": datetime.now().isoformat()
    }
    
    return card, body_plan

# ============================================================================
# SIMULACIÓN PRINCIPAL
# ============================================================================
def run_simulation():
    print("🧬 INICIANDO PIPELINE DE GENERACIÓN DE CRIATURAS V4.0")
    print("=" * 60)
    
    # Escenarios ecológicos
    scenarios = [
        {"name": "Alpino Extremo", "temp": -25, "hum": 40, "alt": 5500, "press": 0.5, "res": 0.3},
        {"name": "Selva Tropical", "temp": 32, "hum": 85, "alt": 100, "press": 1.0, "res": 0.9},
        {"name": "Desierto Árido", "temp": 42, "hum": 10, "alt": 200, "press": 1.0, "res": 0.2},
        {"name": "Fosa Oceánica", "temp": 4, "hum": 95, "alt": -400, "press": 1.4, "res": 0.6},
        {"name": "Pradera Templada", "temp": 20, "hum": 50, "alt": 0, "press": 1.0, "res": 0.7},
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🌍 Generando ecosistema #{i}: {scenario['name']}...")
        print(f"   Temp: {scenario['temp']}°C | Hum: {scenario['hum']}% | Alt: {scenario['alt']}m")
        
        # Generar tarjeta
        card, body_plan = generate_creature_card(
            scenario['temp'], scenario['hum'], scenario['alt'], 
            scenario['press'], scenario['res']
        )
        
        print(f"   🧬 Especie: {card['species_id']}")
        print(f"   🏛️  Plan Corporal: {body_plan.value.upper()}")
        print(f"   🎨 Paleta: {card['palette']}")
        
        # Crear tiles
        tiles = TileFactory.create_tiles_for_plan(body_plan)
        print(f"   📦 Tiles generados: {len(tiles)}")
        
        # Ejecutar WFC con reintentos
        wfc = WFCEngine(tiles, GRID_SIZE, GRID_SIZE)
        result = None
        attempts = 0
        
        print(f"   🔄 Ejecutando Wave Function Collapse ({GRID_SIZE}x{GRID_SIZE})...")
        
        while attempts < MAX_RESTARTS and result is None:
            attempts += 1
            result = wfc.generate()
            
            if result is None and attempts % 10 == 0:
                print(f"      Intento {attempts}/{MAX_RESTARTS}...")
        
        if result is None:
            print(f"   ❌ Falló después de {MAX_RESTARTS} intentos. Saltando...")
            continue
        
        print(f"   ✅ Colapso completado: {len(result)}x{len(result[0])} celdas definidas.")
        
        # Renderizar
        renderer = CreatureRenderer(tiles, result, card['palette'])
        img = renderer.render()
        
        # Guardar
        filename = f"{OUTPUT_DIR}/{card['species_id']}.png"
        img.save(filename)
        print(f"   🖼️  Imagen guardada: {filename}")
        
        # Guardar JSON
        json_filename = f"{OUTPUT_DIR}/{card['species_id']}.json"
        with open(json_filename, 'w') as f:
            json.dump(card, f, indent=2)
        
        # Vista previa ASCII
        print(f"   👁️  Vista previa (ASCII):")
        ascii_chars = {
            TileType.HEAD: '@',
            TileType.BODY_STRAIGHT: '#',
            TileType.BODY_CURVE: '%',
            TileType.LIMB_BASE: '&',
            TileType.LIMB_MID: '*',
            TileType.LIMB_END: '+',
            TileType.TAIL_BASE: '~',
            TileType.TAIL_MID: '-',
            TileType.TAIL_TIP: '=',
            TileType.CENTER_RADIAL: '●',
            TileType.ARM_RADIAL: '│',
            TileType.EMPTY: ' ',
        }
        
        for row in result:
            line = ''.join([ascii_chars.get(tiles[idx].type, '?') for idx in row])
            print(f"      {line}")

if __name__ == "__main__":
    run_simulation()
