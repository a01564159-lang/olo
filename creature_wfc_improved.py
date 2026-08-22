#!/usr/bin/env python3
"""
WFC Creature Generator - Versión Mejorada con Reglas Explícitas
Genera pixel art de criaturas usando Wave Function Collapse con reglas direccionales precisas
"""

import json
import random
import math
from PIL import Image
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# ============================================================================
# CONFIGURACIÓN Y CONSTANTES
# ============================================================================

TILE_SIZE = 16  # Tamaño de cada tile en píxeles
GRID_SIZE = 12  # Tamaño de la grilla WFC (12x12 tiles)
OUTPUT_SIZE = TILE_SIZE * GRID_SIZE

# Direcciones cardinales
class Direction(Enum):
    N = 0  # Norte
    E = 1  # Este
    S = 2  # Sur
    W = 3  # Oeste
    
    @property
    def opposite(self):
        opposites = {Direction.N: Direction.S, Direction.S: Direction.N, 
                    Direction.E: Direction.W, Direction.W: Direction.E}
        return opposites[self]

# ============================================================================
# SISTEMA DE TILES CON Bordes Específicos
# ============================================================================

@dataclass
class EdgePattern:
    """Define el patrón de borde de un tile en una dirección específica"""
    connector_type: str  # Tipo de conector: 'head', 'body', 'limb', 'tail', 'empty'
    color_hint: Tuple[int, int, int]  # Color sugerido para debugging
    weight: float = 1.0  # Peso probabilístico

@dataclass
class WfcTile:
    """Tile con reglas de conexión explícitas por dirección"""
    id: str
    name: str
    edges: Dict[Direction, EdgePattern]  # Borde para cada dirección
    base_color: Tuple[int, int, int]
    category: str  # 'head', 'body', 'limb', 'tail', 'background'
    symmetry: List[str] = None  # Simetrías válidas: ['H', 'V', 'D'] horizontal, vertical, diagonal
    
    def __post_init__(self):
        if self.symmetry is None:
            self.symmetry = []

# ============================================================================
# FÁBRICA DE TILES BIOLÓGICOS
# ============================================================================

class BiologicalTileFactory:
    """Genera tiles con reglas anatómicamente correctas"""
    
    @staticmethod
    def create_creature_tiles(biome_data: dict) -> List[WfcTile]:
        """Crea el set completo de tiles para una criatura"""
        
        # Colores base según bioma
        colors = BiologicalTileFactory._get_biome_colors(biome_data)
        
        tiles = []
        
        # === CABEZA (solo puede conectar cuerpo por atrás) ===
        head_front = WfcTile(
            id="head_front",
            name="Cabeza Frontal",
            edges={
                Direction.N: EdgePattern("empty", colors['bg']),
                Direction.E: EdgePattern("empty", colors['bg']),
                Direction.S: EdgePattern("body_back", colors['body'], weight=1.0),
                Direction.W: EdgePattern("empty", colors['bg'])
            },
            base_color=colors['head'],
            category="head"
        )
        tiles.append(head_front)
        
        # Cabeza mirando hacia otros lados (rotaciones)
        for direction in [Direction.E, Direction.S, Direction.W]:
            rotated_edges = {}
            for d in Direction:
                # Rotar las conexiones
                offset = direction.value
                new_d = Direction((d.value + offset) % 4)
                rotated_edges[new_d] = head_front.edges[d]
            
            tiles.append(WfcTile(
                id=f"head_{direction.name.lower()}",
                name=f"Cabeza {direction.name}",
                edges=rotated_edges,
                base_color=colors['head'],
                category="head"
            ))
        
        # === TORSO / CUERPO (conecta por todos lados) ===
        body_straight_h = WfcTile(
            id="body_straight_h",
            name="Torso Horizontal",
            edges={
                Direction.N: EdgePattern("empty", colors['bg']),
                Direction.E: EdgePattern("body_front", colors['body'], weight=2.0),
                Direction.S: EdgePattern("empty", colors['bg']),
                Direction.W: EdgePattern("body_back", colors['body'], weight=2.0)
            },
            base_color=colors['body'],
            category="body"
        )
        tiles.append(body_straight_h)
        
        body_straight_v = WfcTile(
            id="body_straight_v",
            name="Torso Vertical",
            edges={
                Direction.N: EdgePattern("body_front", colors['body'], weight=2.0),
                Direction.E: EdgePattern("empty", colors['bg']),
                Direction.S: EdgePattern("body_back", colors['body'], weight=2.0),
                Direction.W: EdgePattern("empty", colors['bg'])
            },
            base_color=colors['body'],
            category="body"
        )
        tiles.append(body_straight_v)
        
        # Curvas del cuerpo
        curve_ne = WfcTile(
            id="body_curve_ne",
            name="Curva NE",
            edges={
                Direction.N: EdgePattern("body_front", colors['body'], weight=1.5),
                Direction.E: EdgePattern("body_back", colors['body'], weight=1.5),
                Direction.S: EdgePattern("empty", colors['bg']),
                Direction.W: EdgePattern("empty", colors['bg'])
            },
            base_color=colors['body'],
            category="body"
        )
        tiles.append(curve_ne)
        
        # Generar todas las rotaciones de curvas
        for i, direction in enumerate([Direction.E, Direction.S, Direction.W]):
            curve_name = f"body_curve_{['ne', 'se', 'sw', 'nw'][i]}"
            rotated_edges = {}
            for d in Direction:
                new_d = Direction((d.value + direction.value) % 4)
                rotated_edges[new_d] = curve_ne.edges[d]
            
            tiles.append(WfcTile(
                id=curve_name,
                name=f"Curva {['NE', 'SE', 'SW', 'NW'][i]}",
                edges=rotated_edges,
                base_color=colors['body'],
                category="body"
            ))
        
        # Cruce (opcional, menos frecuente)
        body_cross = WfcTile(
            id="body_cross",
            name="Cruce",
            edges={
                Direction.N: EdgePattern("body_front", colors['body'], weight=0.5),
                Direction.E: EdgePattern("body_back", colors['body'], weight=0.5),
                Direction.S: EdgePattern("body_back", colors['body'], weight=0.5),
                Direction.W: EdgePattern("body_back", colors['body'], weight=0.5)
            },
            base_color=colors['body'],
            category="body"
        )
        tiles.append(body_cross)
        
        # === EXTREMIDADES (conectan solo por un lado) ===
        limb_variants = ["limb_up", "limb_down", "limb_left", "limb_right"]
        limb_dirs = [Direction.N, Direction.S, Direction.W, Direction.E]
        
        for variant, direction in zip(limb_variants, limb_dirs):
            edges = {d: EdgePattern("empty", colors['bg']) for d in Direction}
            edges[direction.opposite] = EdgePattern("limb_base", colors['limb'], weight=1.0)
            edges[direction] = EdgePattern("limb_tip", colors['limb'], weight=1.0)
            
            tiles.append(WfcTile(
                id=variant,
                name=f"Extremidad {variant.replace('limb_', '')}",
                edges=edges,
                base_color=colors['limb'],
                category="limb"
            ))
        
        # Extremidad en ángulo (para variedad)
        limb_angle_ne = WfcTile(
            id="limb_angle_ne",
            name="Extremidad Ángulo NE",
            edges={
                Direction.N: EdgePattern("limb_tip", colors['limb'], weight=0.8),
                Direction.E: EdgePattern("limb_tip", colors['limb'], weight=0.8),
                Direction.S: EdgePattern("limb_base", colors['limb'], weight=1.0),
                Direction.W: EdgePattern("empty", colors['bg'])
            },
            base_color=colors['limb'],
            category="limb"
        )
        tiles.append(limb_angle_ne)
        
        # Rotaciones de extremidad en ángulo
        for i, direction in enumerate([Direction.E, Direction.S, Direction.W]):
            angle_name = f"limb_angle_{['ne', 'se', 'sw', 'nw'][i]}"
            rotated_edges = {}
            for d in Direction:
                new_d = Direction((d.value + direction.value) % 4)
                rotated_edges[new_d] = limb_angle_ne.edges[d]
            
            tiles.append(WfcTile(
                id=angle_name,
                name=f"Extremidad Ángulo {['NE', 'SE', 'SW', 'NW'][i]}",
                edges=rotated_edges,
                base_color=colors['limb'],
                category="limb"
            ))
        
        # === COLA (similar al cuerpo pero termina en punta) ===
        tail_straight_h = WfcTile(
            id="tail_straight_h",
            name="Cola Horizontal",
            edges={
                Direction.N: EdgePattern("empty", colors['bg']),
                Direction.E: EdgePattern("tail_tip", colors['tail'], weight=1.0),
                Direction.S: EdgePattern("empty", colors['bg']),
                Direction.W: EdgePattern("tail_base", colors['tail'], weight=1.0)
            },
            base_color=colors['tail'],
            category="tail"
        )
        tiles.append(tail_straight_h)
        
        tail_straight_v = WfcTile(
            id="tail_straight_v",
            name="Cola Vertical",
            edges={
                Direction.N: EdgePattern("tail_tip", colors['tail'], weight=1.0),
                Direction.E: EdgePattern("empty", colors['bg']),
                Direction.S: EdgePattern("tail_base", colors['tail'], weight=1.0),
                Direction.W: EdgePattern("empty", colors['bg'])
            },
            base_color=colors['tail'],
            category="tail"
        )
        tiles.append(tail_straight_v)
        
        # Curvas de cola
        tail_curve_ne = WfcTile(
            id="tail_curve_ne",
            name="Curva Cola NE",
            edges={
                Direction.N: EdgePattern("tail_tip", colors['tail'], weight=1.0),
                Direction.E: EdgePattern("tail_tip", colors['tail'], weight=1.0),
                Direction.S: EdgePattern("empty", colors['bg']),
                Direction.W: EdgePattern("tail_base", colors['tail'], weight=1.0)
            },
            base_color=colors['tail'],
            category="tail"
        )
        tiles.append(tail_curve_ne)
        
        for i, direction in enumerate([Direction.E, Direction.S, Direction.W]):
            tail_curve_name = f"tail_curve_{['ne', 'se', 'sw', 'nw'][i]}"
            rotated_edges = {}
            for d in Direction:
                new_d = Direction((d.value + direction.value) % 4)
                rotated_edges[new_d] = tail_curve_ne.edges[d]
            
            tiles.append(WfcTile(
                id=tail_curve_name,
                name=f"Curva Cola {['NE', 'SE', 'SW', 'NW'][i]}",
                edges=rotated_edges,
                base_color=colors['tail'],
                category="tail"
            ))
        
        # Punta de cola
        tail_tip_variants = ["tail_tip_n", "tail_tip_e", "tail_tip_s", "tail_tip_w"]
        for variant, direction in zip(tail_tip_variants, Direction):
            edges = {d: EdgePattern("empty", colors['bg']) for d in Direction}
            edges[direction.opposite] = EdgePattern("tail_base", colors['tail'], weight=1.0)
            edges[direction] = EdgePattern("empty", colors['bg'], weight=0.1)  # Terminación
            
            tiles.append(WfcTile(
                id=variant,
                name=f"Punta Cola {direction.name}",
                edges=edges,
                base_color=colors['tail'],
                category="tail"
            ))
        
        # === FONDO / AMBIENTE ===
        bg_empty = WfcTile(
            id="bg_empty",
            name="Fondo Vacío",
            edges={
                d: EdgePattern("empty", colors['bg'], weight=3.0) for d in Direction
            },
            base_color=colors['bg'],
            category="background"
        )
        tiles.append(bg_empty)
        
        # Fondo con textura ambiental
        bg_texture = WfcTile(
            id="bg_texture",
            name="Fondo Texturizado",
            edges={
                d: EdgePattern("empty", colors['bg_alt'], weight=2.0) for d in Direction
            },
            base_color=colors['bg_alt'],
            category="background"
        )
        tiles.append(bg_texture)
        
        return tiles
    
    @staticmethod
    def _get_biome_colors(biome_data: dict) -> dict:
        """Determina paleta de colores basada en el bioma"""
        temp = biome_data.get('temperature', 20)
        humidity = biome_data.get('humidity', 50)
        altitude = biome_data.get('altitude', 0)
        
        # Lógica de color adaptativa
        if temp < 0:  # Frío extremo
            base_body = (100, 150, 200)  # Azul grisáceo
            base_limb = (80, 130, 180)
            base_tail = (90, 140, 190)
            bg_main = (200, 220, 255)  # Azul muy claro
            bg_alt = (180, 200, 240)
        elif temp > 35:  # Calor extremo
            base_body = (200, 150, 100)  # Naranja tierra
            base_limb = (180, 130, 80)
            base_tail = (190, 140, 90)
            bg_main = (255, 240, 200)  # Arena claro
            bg_alt = (240, 220, 180)
        elif humidity > 70:  # Húmedo
            base_body = (50, 150, 50)  # Verde
            base_limb = (40, 130, 40)
            base_tail = (45, 140, 45)
            bg_main = (200, 240, 200)  # Verde claro
            bg_alt = (180, 220, 180)
        else:  # Templado
            base_body = (150, 100, 50)  # Marrón
            base_limb = (130, 80, 40)
            base_tail = (140, 90, 45)
            bg_main = (240, 230, 200)  # Beige
            bg_alt = (220, 210, 180)
        
        # Ajustes por altitud
        if altitude > 3000:
            base_body = tuple(min(255, c + 30) for c in base_body)  # Más claro
            bg_main = tuple(min(255, c + 40) for c in bg_main)
        
        # Cabeza ligeramente diferente del cuerpo
        base_head = tuple(max(0, min(255, c + 20)) for c in base_body)
        
        return {
            'body': base_body,
            'limb': base_limb,
            'tail': base_tail,
            'head': base_head,
            'bg': bg_main,
            'bg_alt': bg_alt
        }

# ============================================================================
# RENDERIZADOR DE TILES PROCEDURAL
# ============================================================================

class TileRenderer:
    """Renderiza cada tile con gráficos procedurales detallados"""
    
    @staticmethod
    def render_tile(tile: WfcTile, size: int = TILE_SIZE) -> Image.Image:
        """Crea una imagen PIL para un tile específico"""
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        pixels = img.load()
        
        base_color = tile.base_color
        
        # Dibujar fondo con gradiente sutil
        TileRenderer._draw_background(pixels, size, base_color, tile.category)
        
        # Dibujar contenido según categoría
        if tile.category == "head":
            TileRenderer._draw_head(pixels, size, base_color, tile.edges)
        elif tile.category == "body":
            TileRenderer._draw_body(pixels, size, base_color, tile.edges)
        elif tile.category == "limb":
            TileRenderer._draw_limb(pixels, size, base_color, tile.edges)
        elif tile.category == "tail":
            TileRenderer._draw_tail(pixels, size, base_color, tile.edges)
        elif tile.category == "background":
            TileRenderer._draw_background_detail(pixels, size, base_color)
        
        return img
    
    @staticmethod
    def _draw_background(pixels, size: int, base_color: tuple, category: str):
        """Dibuja fondo con variación sutil"""
        for y in range(size):
            for x in range(size):
                # Gradiente radial sutil
                dx = x - size // 2
                dy = y - size // 2
                dist = math.sqrt(dx*dx + dy*dy) / (size // 2)
                
                # Variación de color
                variation = int(15 * (1 - dist))
                r = max(0, min(255, base_color[0] + variation))
                g = max(0, min(255, base_color[1] + variation))
                b = max(0, min(255, base_color[2] + variation))
                
                # Transparencia para background
                if category == "background":
                    alpha = 180
                else:
                    alpha = 255
                
                pixels[x, y] = (r, g, b, alpha)
    
    @staticmethod
    def _draw_head(pixels, size: int, color: tuple, edges: dict):
        """Dibuja una cabeza con ojos y detalles"""
        center_x, center_y = size // 2, size // 2
        
        # Determinar dirección principal
        main_dir = None
        for d, edge in edges.items():
            if edge.connector_type.startswith('body'):
                main_dir = d
                break
        
        if main_dir is None:
            main_dir = Direction.S  # Por defecto mira hacia abajo
        
        # Dibujar forma básica de cabeza (óvalo)
        for y in range(size):
            for x in range(size):
                dx = x - center_x
                dy = y - center_y
                
                # Óvalo alargado en dirección opuesta a la conexión
                stretch_x = 1.0 if main_dir in [Direction.N, Direction.S] else 1.3
                stretch_y = 1.3 if main_dir in [Direction.N, Direction.S] else 1.0
                
                normalized_dist = math.sqrt((dx/stretch_x)**2 + **(dy/stretch_y)2) / (size // 3)
                
                if normalized_dist < 1.0:
                    # Color más oscuro para la cabeza
                    r = max(0, min(255, color[0] - 20))
                    g = max(0, min(255, color[1] - 20))
                    b = max(0, min(255, color[2] - 20))
                    
                    # Añadir brillo
                    if normalized_dist < 0.3:
                        r = min(255, r + 30)
                        g = min(255, g + 30)
                        b = min(255, b + 30)
                    
                    pixels[x, y] = (r, g, b, 255)
        
        # Dibujar ojos
        eye_offset_x = 3 if main_dir in [Direction.N, Direction.S] else 0
        eye_offset_y = 0 if main_dir in [Direction.N, Direction.S] else 3
        
        eye1_x = center_x - 2 + eye_offset_x
        eye1_y = center_y - 2 + eye_offset_y
        eye2_x = center_x + 2 + eye_offset_x
        eye2_y = center_y - 2 + eye_offset_y
        
        for ex, ey in [(eye1_x, eye1_y), (eye2_x, eye2_y)]:
            if 0 <= ex < size and 0 <= ey < size:
                pixels[ex, ey] = (255, 255, 255, 255)  # Blanco del ojo
                if ex+1 < size:
                    pixels[ex+1, ey] = (0, 0, 0, 255)  # Pupila
    
    @staticmethod
    def _draw_body(pixels, size: int, color: tuple, edges: dict):
        """Dibuja segmento de cuerpo con textura orgánica"""
        center_x, center_y = size // 2, size // 2
        
        # Identificar direcciones de conexión
        connected_dirs = [d for d, e in edges.items() if e.connector_type.startswith('body')]
        
        for y in range(size):
            for x in range(size):
                dx = x - center_x
                dy = y - center_y
                dist = math.sqrt(dx*dx + dy*dy)
                
                # Forma cilíndrica/ovalada
                if len(connected_dirs) == 2:
                    # Segmento recto - alargar en dirección de conexión
                    if Direction.N in connected_dirs or Direction.S in connected_dirs:
                        stretch = abs(dy) * 1.2 + abs(dx) * 0.8
                    else:
                        stretch = abs(dx) * 1.2 + abs(dy) * 0.8
                    
                    if stretch < size // 2.5:
                        # Textura segmentada
                        segment = int(y / (size // 4)) % 2
                        variation = 15 if segment == 0 else -10
                        
                        r = max(0, min(255, color[0] + variation))
                        g = max(0, min(255, color[1] + variation))
                        b = max(0, min(255, color[2] + variation))
                        
                        pixels[x, y] = (r, g, b, 255)
                else:
                    # Curva o cruce - forma más redondeada
                    if dist < size // 2.5:
                        variation = int(10 * math.sin(dist * 0.5))
                        r = max(0, min(255, color[0] + variation))
                        g = max(0, min(255, color[1] + variation))
                        b = max(0, min(255, color[2] + variation))
                        pixels[x, y] = (r, g, b, 255)
    
    @staticmethod
    def _draw_limb(pixels, size: int, color: tuple, edges: dict):
        """Dibuja extremidad articulada"""
        # Encontrar base y punta
        base_dir = None
        tip_dir = None
        
        for d, edge in edges.items():
            if edge.connector_type == "limb_base":
                base_dir = d
            elif edge.connector_type == "limb_tip":
                tip_dir = d
        
        if base_dir is None:
            return
        
        # Dirección del vector base->punta
        if tip_dir is None:
            tip_dir = base_dir.opposite
        
        # Dibujar línea/curva desde base hasta punta
        start_x, start_y = size // 2, size // 2
        end_x, end_y = size // 2, size // 2
        
        # Ajustar posiciones según direcciones
        if base_dir == Direction.N:
            start_y = size - 2
        elif base_dir == Direction.S:
            start_y = 2
        elif base_dir == Direction.E:
            start_x = 2
        elif base_dir == Direction.W:
            start_x = size - 2
        
        if tip_dir == Direction.N:
            end_y = 2
        elif tip_dir == Direction.S:
            end_y = size - 2
        elif tip_dir == Direction.E:
            end_x = size - 2
        elif tip_dir == Direction.W:
            end_x = 2
        
        # Algoritmo de línea de Bresenham
        dx = abs(end_x - start_x)
        dy = abs(end_y - start_y)
        sx = 1 if start_x < end_x else -1
        sy = 1 if start_y < end_y else -1
        err = dx - dy
        
        x, y = start_x, start_y
        while True:
            # Grosor de la extremidad
            for ox in range(-2, 3):
                for oy in range(-2, 3):
                    if ox*ox + oy*oy <= 4:  # Círculo de radio 2
                        px, py = x + ox, y + oy
                        if 0 <= px < size and 0 <= py < size:
                            # Variación para parecer orgánico
                            variation = int(8 * math.sin((x + y) * 0.3))
                            r = max(0, min(255, color[0] + variation))
                            g = max(0, min(255, color[1] + variation))
                            b = max(0, min(255, color[2] + variation))
                            pixels[px, py] = (r, g, b, 255)
            
            if x == end_x and y == end_y:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
    
    @staticmethod
    def _draw_tail(pixels, size: int, color: tuple, edges: dict):
        """Dibuja segmento de cola que se afina"""
        center_x, center_y = size // 2, size // 2
        
        # Identificar base y punta
        has_base = any(e.connector_type == "tail_base" for e in edges.values())
        has_tip = any(e.connector_type == "tail_tip" for e in edges.values())
        
        for y in range(size):
            for x in range(size):
                dx = x - center_x
                dy = y - center_y
                dist = math.sqrt(dx*dx + dy*dy)
                
                # La cola se afina hacia la punta
                taper_factor = 0.9 if has_tip else 1.0
                
                if dist < (size // 2.5) * taper_factor:
                    # Textura anillada
                    ring = int(dist * 0.8) % 3
                    variation = 10 - ring * 5
                    
                    r = max(0, min(255, color[0] + variation))
                    g = max(0, min(255, color[1] + variation))
                    b = max(0, min(255, color[2] + variation))
                    
                    pixels[x, y] = (r, g, b, 255)
    
    @staticmethod
    def _draw_background_detail(pixels, size: int, color: tuple):
        """Añade detalles sutiles al fondo"""
        for y in range(size):
            for x in range(size):
                # Patrón de ruido suave
                noise = int(10 * math.sin(x * 0.3) * math.cos(y * 0.3))
                r = max(0, min(255, color[0] + noise))
                g = max(0, min(255, color[1] + noise))
                b = max(0, min(255, color[2] + noise))
                pixels[x, y] = (r, g, b, 180)  # Semi-transparente

# ============================================================================
# MOTOR WFC CON REGLAS DIRECCIONALES
# ============================================================================

class WfcEngine:
    """Motor Wave Function Collapse con reglas direccionales explícitas"""
    
    def __init__(self, tiles: List[WfcTile], grid_size: int = GRID_SIZE):
        self.tiles = tiles
        self.grid_size = grid_size
        self.tile_index = {tile.id: i for i, tile in enumerate(tiles)}
        
        # Precomputar matriz de compatibilidad
        self.compatibility_matrix = self._build_compatibility_matrix()
    
    def _build_compatibility_matrix(self) -> Dict[str, Dict[Direction, List[str]]]:
        """Construye matriz de tiles compatibles por dirección"""
        compatibility = {}
        
        for tile in self.tiles:
            compatibility[tile.id] = {}
            
            for direction in Direction:
                compatible_tiles = []
                required_edge = tile.edges[direction]
                
                for other_tile in self.tiles:
                    opposite_edge = other_tile.edges[direction.opposite]
                    
                    # Verificar compatibilidad de conectores
                    if self._edges_compatible(required_edge, opposite_edge):
                        compatible_tiles.append(other_tile.id)
                
                compatibility[tile.id][direction] = compatible_tiles
        
        return compatibility
    
    def _edges_compatible(self, edge1: EdgePattern, edge2: EdgePattern) -> bool:
        """Verifica si dos bordes son compatibles"""
        # Reglas de compatibilidad específicas
        compatible_pairs = {
            ('empty', 'empty'),
            ('body_front', 'body_back'),
            ('body_back', 'body_front'),
            ('limb_base', 'body_front'),
            ('limb_base', 'body_back'),
            ('limb_base', 'body_side'),
            ('limb_tip', 'empty'),
            ('tail_base', 'body_front'),
            ('tail_base', 'body_back'),
            ('tail_tip', 'empty'),
        }
        
        return (edge1.connector_type, edge2.connector_type) in compatible_pairs or \
               (edge2.connector_type, edge1.connector_type) in compatible_pairs or \
               (edge1.connector_type == 'empty' and edge2.connector_type == 'empty')
    
    def generate(self, seed: int = None, max_iterations: int = 1000) -> Optional[List[List[str]]]:
        """Ejecuta el algoritmo WFC"""
        if seed is not None:
            random.seed(seed)
        
        # Inicializar grilla con todos los tiles posibles
        grid = [[set(self.tile_index.keys()) for _ in range(self.grid_size)] 
                for _ in range(self.grid_size)]
        
        # Forzar al menos una cabeza en el centro para comenzar
        center = self.grid_size // 2
        head_tiles = [t.id for t in self.tiles if t.category == "head"]
        if head_tiles:
            grid[center][center] = set(random.sample(head_tiles, min(2, len(head_tiles))))
        
        iterations = 0
        while iterations < max_iterations:
            iterations += 1
            
            # Encontrar celda con menor entropía (menor número de opciones)
            min_entropy = float('inf')
            min_cell = None
            
            for y in range(self.grid_size):
                for x in range(self.grid_size):
                    entropy = len(grid[y][x])
                    if 1 < entropy < min_entropy:
                        min_entropy = entropy
                        min_cell = (x, y)
            
            # Si todas las celdas tienen 0 o 1 opción, terminar
            if min_cell is None:
                break
            
            x, y = min_cell
            
            # Colapsar: elegir un tile aleatorio de las opciones
            options = list(grid[y][x])
            if not options:
                return None  # Fallo - backtracking necesario (simplificado: reiniciar)
            
            # Ponderar por weights de los tiles
            weights = []
            for tile_id in options:
                tile = self.tiles[self.tile_index[tile_id]]
                total_weight = sum(
                    edge.weight for edge in tile.edges.values()
                )
                weights.append(total_weight)
            
            chosen_tile = random.choices(options, weights=weights)[0]
            grid[y][x] = {chosen_tile}
            
            # Propagar restricciones
            if not self._propagate(grid, x, y):
                # Propagación falló - intentar de nuevo con otra semilla
                return None
        
        # Verificar solución válida
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if len(grid[y][x]) != 1:
                    return None
        
        return [[list(options)[0] for options in row] for row in grid]
    
    def _propagate(self, grid: List[List[set]], start_x: int, start_y: int) -> bool:
        """Propaga restricciones desde una celda colapsada"""
        stack = [(start_x, start_y)]
        visited = set()
        
        while stack:
            x, y = stack.pop()
            
            if (x, y) in visited:
                continue
            visited.add((x, y))
            
            current_options = grid[y][x]
            
            # Propagar a vecinos
            for dx, dy, direction in [(0, -1, Direction.N), (1, 0, Direction.E), 
                                       (0, 1, Direction.S), (-1, 0, Direction.W)]:
                nx, ny = x + dx, y + dy
                
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                    neighbor_options = grid[ny][nx]
                    
                    # Filtrar opciones incompatibles
                    new_options = set()
                    for neighbor_id in neighbor_options:
                        for current_id in current_options:
                            if neighbor_id in self.compatibility_matrix[current_id][direction]:
                                new_options.add(neighbor_id)
                                break
                    
                    if new_options != neighbor_options:
                        grid[ny][nx] = new_options
                        
                        if not new_options:
                            return False  # Contradicción
                        
                        if len(new_options) > 1:
                            stack.append((nx, ny))
        
        return True

# ============================================================================
# GENERADOR PRINCIPAL DE CRIATURAS
# ============================================================================

class CreatureGenerator:
    """Orquesta todo el pipeline de generación"""
    
    def __init__(self):
        self.tile_factory = BiologicalTileFactory()
        self.renderer = TileRenderer()
    
    def generate_creature(self, biome_data: dict, seed: int = None) -> Optional[Image.Image]:
        """Genera una criatura completa basada en datos del bioma"""
        
        print(f"🧬 Generando criatura para bioma:")
        print(f"   Temperatura: {biome_data.get('temperature', 20)}°C")
        print(f"   Humedad: {biome_data.get('humidity', 50)}%")
        print(f"   Altitud: {biome_data.get('altitude', 0)}m")
        
        # Crear tiles específicos para este bioma
        tiles = self.tile_factory.create_creature_tiles(biome_data)
        print(f"   📦 {len(tiles)} tiles generados")
        
        # Crear motor WFC
        wfc = WfcEngine(tiles, GRID_SIZE)
        
        # Intentar generar múltiples veces hasta obtener resultado válido
        max_attempts = 20
        for attempt in range(max_attempts):
            attempt_seed = seed if seed is not None else random.randint(0, 1000000)
            
            print(f"   🔄 Intento {attempt + 1}/{max_attempts} (seed: {attempt_seed})...")
            
            result_grid = wfc.generate(seed=attempt_seed)
            
            if result_grid is not None:
                print(f"   ✅ ¡Éxito en el intento {attempt + 1}!")
                return self._render_creature(result_grid, tiles, wfc.tile_index)
        
        print(f"   ❌ No se pudo generar después de {max_attempts} intentos")
        return None
    
    def _render_creature(self, grid: List[List[str]], tiles: List[WfcTile], 
                        tile_index: dict) -> Image.Image:
        """Renderiza la grilla completa de tiles en una imagen"""
        
        total_size = GRID_SIZE * TILE_SIZE
        final_image = Image.new('RGBA', (total_size, total_size), (255, 255, 255, 255))
        
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                tile_id = grid[y][x]
                tile = tiles[tile_index[tile_id]]
                
                # Renderizar tile individual
                tile_img = self.renderer.render_tile(tile, TILE_SIZE)
                
                # Pegar en la imagen final
                final_image.paste(tile_img, (x * TILE_SIZE, y * TILE_SIZE), tile_img)
        
        # Escalar para mejor visualización (pixel art nítido)
        scale_factor = 4
        scaled_size = total_size * scale_factor
        final_image = final_image.resize((scaled_size, scaled_size), Image.Resampling.NEAREST)
        
        return final_image

# ============================================================================
# DEMOSTRACIÓN
# ============================================================================

def main():
    """Demostración con diferentes biomas"""
    
    generator = CreatureGenerator()
    
    # Biomas de ejemplo
    biomes = [
        {
            "name": "Alpino Extremo",
            "data": {"temperature": -25, "humidity": 30, "altitude": 5500, "pressure": 500, "resources": 20}
        },
        {
            "name": "Selva Tropical",
            "data": {"temperature": 35, "humidity": 85, "altitude": 200, "pressure": 1010, "resources": 90}
        },
        {
            "name": "Desierto Árido",
            "data": {"temperature": 45, "humidity": 15, "altitude": 400, "pressure": 1005, "resources": 30}
        },
        {
            "name": "Fosa Oceánica",
            "data": {"temperature": 5, "humidity": 95, "altitude": -200, "pressure": 1200, "resources": 60}
        }
    ]
    
    print("=" * 60)
    print("🎨 WFC Creature Generator - Versión Mejorada")
    print("=" * 60)
    
    for i, biome in enumerate(biomes):
        print(f"\n{'='*60}")
        print(f"🌍 Generando criatura #{i+1}: {biome['name']}")
        print(f"{'='*60}")
        
        creature_img = generator.generate_creature(biome['data'], seed=42+i*100)
        
        if creature_img:
            filename = f"creature_{biome['name'].lower().replace(' ', '_')}.png"
            creature_img.save(filename)
            print(f"💾 Guardado: {filename} ({creature_img.size[0]}x{creature_img.size[1]}px)")
        else:
            print(f"⚠️  No se pudo generar la criatura para {biome['name']}")
    
    print(f"\n{'='*60}")
    print("✅ ¡Generación completada!")
    print(f"{'='*60}")
    print("\nArchivos generados:")
    print("  • creature_alpino_extremo.png")
    print("  • creature_selva_tropical.png")
    print("  • creature_desierto_arido.png")
    print("  • creature_fosa_oceanica.png")
    print("\nCada criatura es única y adaptada a su ambiente!")

if __name__ == "__main__":
    main()
