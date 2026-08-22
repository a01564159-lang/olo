#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CREATURE WFC PIPELINE V3.0 - MORPHOLOGICAL DIVERSITY EDITION
------------------------------------------------------------
Arquitectura Senior de Generación Procedural.

Mejoras clave en esta versión:
1. Sistema de 'Body Plans' (Planes Corporales): Define arquitecturas base radicalmente distintas
   antes de aplicar WFC (Bípedo, Hexápodo, Cefalópodo, Radial, Serpentino).
2. Fábricas de Tiles Contextuales: Los sprites se generan según la anatomía específica.
3. Reglas de Adyacencia Estrictas por Arquetipo: Evita híbridos imposibles.
4. Renderizado Vectorial/Pixel-Art Híbrido: Líneas limpias y formas orgánicas definidas.

Sin dependencias externas pesadas. Solo Pillow (PIL) para la imagen final.
"""

import random
import math
import json
import os
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# Intentar importar PIL, si no existe, ofrecer modo consola fallback
try:
    from PIL import Image, ImageDraw, ImageFilter
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("⚠️  AVISO: Pillow no encontrado. Ejecuta: pip install Pillow")
    print("   El script generará datos JSON y preview en consola, pero no imágenes PNG.")

# ==============================================================================
# CONFIGURACIÓN Y CONSTANTES
# ==============================================================================

GRID_SIZE = 16  # Tamaño de la grilla WFC (16x16 tiles)
TILE_SIZE = 32  # Tamaño en píxeles de cada tile (escalable)
OUTPUT_SCALE = 4 # Escala final de salida (32 * 4 = 128px por tile visualmente)

class BodyPlanType(Enum):
    BIPED = "biped"
    HEXAPOD = "hexapod"
    CEPHALOPOD = "cephalopod"
    RADIAL = "radial"
    SERPENTINE = "serpentine"

@dataclass
class EcoVariables:
    temperature: float  # -50 to 50
    humidity: float     # 0 to 100
    altitude: float     # 0 to 10000
    pressure: float     # 0.5 to 2.0 atm
    resources: float    # 0 to 100

@dataclass
class CreatureCard:
    id: str
    body_plan: BodyPlanType
    eco_vars: EcoVariables
    anatomy: Dict[str, Any]
    survival: Dict[str, Any]
    palette: List[str]

# ==============================================================================
# FASE 1: MOTOR DE DEFINICIÓN ECOLÓGICA Y PLAN CORPORAL
# ==============================================================================

class EcologicalEngine:
    """Determina la biología y el plan corporal basado en 5 variables."""

    def generate_creature(self, eco_vars: EcoVariables) -> CreatureCard:
        # 1. Determinar Plan Corporal (Lógica evolutiva simplificada)
        body_plan = self._determine_body_plan(eco_vars)
        
        # 2. Generar Anatomía Específica para ese Plan
        anatomy = self._generate_anatomy(body_plan, eco_vars)
        
        # 3. Mecanismos de Supervivencia
        survival = self._generate_survival(eco_vars)
        
        # 4. Paleta de Colores Adaptativa
        palette = self._generate_palette(eco_vars, body_plan)

        return CreatureCard(
            id=f"specie_{body_plan.value}_{random.randint(1000,9999)}",
            body_plan=body_plan,
            eco_vars=eco_vars,
            anatomy=anatomy,
            survival=survival,
            palette=palette
        )

    def _determine_body_plan(self, eco: EcoVariables) -> BodyPlanType:
        # Lógica heurística para diversidad
        if eco.pressure > 1.5 or eco.humidity > 90:
            return BodyPlanType.CEPHALOPOD  # Flotabilidad necesaria
        elif eco.altitude > 4000 and eco.temperature < 10:
            return BodyPlanType.BIPED      # Eficiencia térmica y visión
        elif eco.resources < 30 and eco.temperature > 30:
            return BodyPlanType.SERPENTINE # Bajo costo energético
        elif eco.humidity < 20:
            return BodyPlanType.HEXAPOD    # Estabilidad en terreno seco
        else:
            # Aleatoriedad controlada para zonas templadas
            return random.choice([BodyPlanType.RADIAL, BodyPlanType.HEXAPOD, BodyPlanType.BIPED])

    def _generate_anatomy(self, plan: BodyPlanType, eco: EcoVariables) -> Dict:
        base = {"plan": plan.value}
        
        if plan == BodyPlanType.BIPED:
            base.update({
                "limbs": 2,
                "arms": 2 if eco.resources > 40 else 0,
                "posture": "erect",
                "head_position": "top",
                "spine_segments": random.randint(5, 8)
            })
        elif plan == BodyPlanType.HEXAPOD:
            base.update({
                "limbs": 6,
                "exoskeleton": eco.temperature > 25,
                "head_position": "front",
                "tail": random.choice([True, False])
            })
        elif plan == BodyPlanType.CEPHALOPOD:
            base.update({
                "mantle_size": "large",
                "tentacles": random.randint(6, 12),
                "eyes": "complex" if eco.resources > 50 else "simple",
                "siphon": True
            })
        elif plan == BodyPlanType.RADIAL:
            base.update({
                "symmetry_order": random.choice([4, 5, 6]),
                "central_mouth": True,
                "appendages": "radiating"
            })
        elif plan == BodyPlanType.SERPENTINE:
            base.update({
                "segments": random.randint(12, 20),
                "limbs": 0,
                "fins": True if eco.humidity > 60 else False
            })
        return base

    def _generate_survival(self, eco: EcoVariables) -> Dict:
        mechanisms = []
        if eco.temperature < 0: mechanisms.append("thick_fur" if random.random() > 0.5 else "blubber")
        if eco.temperature > 35: mechanisms.append("heat_dissipation_plates")
        if eco.humidity < 20: mechanisms.append("water_retention_sacs")
        if eco.altitude > 3000: mechanisms.append("expanded_lung_capacity")
        if eco.pressure > 1.5: mechanisms.append("pressure_resistant_shell")
        
        return {
            "mechanisms": mechanisms,
            "energy_source": "chemosynthesis" if eco.resources < 10 else "omnivore",
            "lifespan_estimate": random.randint(5, 100)
        }

    def _generate_palette(self, eco: EcoVariables, plan: BodyPlanType) -> List[str]:
        # Colores base hexadecimales
        if eco.temperature < 0:
            base_colors = ["#E0F7FA", "#B2EBF2", "#81D4FA", "#FFFFFF"] # Hielo
        elif eco.humidity > 80:
            base_colors = ["#1B5E20", "#2E7D32", "#4CAF50", "#81C784"] # Selva
        elif eco.temperature > 35:
            base_colors = ["#E65100", "#EF6C00", "#F57F17", "#FFF3E0"] # Desierto
        elif eco.pressure > 1.5:
            base_colors = ["#0D47A1", "#1565C0", "#1976D2", "#BBDEFB"] # Profundidad
        else:
            base_colors = ["#4E342E", "#5D4037", "#795548", "#A1887F"] # Tierra
            
        # Añadir variación por plan corporal (ej: colores de advertencia si es venenoso)
        if eco.resources < 20 and random.random() > 0.7:
            base_colors.append("#FFEB3B") # Toques amarillos de advertencia
            
        return base_colors

# ==============================================================================
# FASE 2: SISTEMA WFC CON ARQUETIPOS MORFOLÓGICOS
# ==============================================================================

class TileType(Enum):
    EMPTY = "empty"
    HEAD = "head"
    BODY_STRAIGHT = "body_straight"
    BODY_CURVE = "body_curve"
    BODY_JOINT = "body_joint"
    LIMB_BASE = "limb_base"
    LIMB_MID = "limb_mid"
    LIMB_END = "limb_end"
    TAIL_START = "tail_start"
    TAIL_END = "tail_end"
    CENTER_RADIAL = "center_radial"
    ARM_RADIAL = "arm_radial"

# Definición de bordes: N, E, S, W
# Conectores: 'conn_body', 'conn_limb', 'conn_tail', 'conn_head', 'none'
class Edge(Enum):
    NONE = 0
    CONN_BODY = 1
    CONN_LIMB = 2
    CONN_TAIL = 3
    CONN_HEAD = 4
    CONN_CENTER = 5

@dataclass
class WFCTile:
    id: str
    type: TileType
    edges: Tuple[Edge, Edge, Edge, Edge] # N, E, S, W
    weight: float
    sprite_data: Dict # Instrucciones de dibujo

class WFCGenerator:
    def __init__(self, creature_card: CreatureCard):
        self.card = creature_card
        self.tiles: List[WFCTile] = []
        self.grid: List[List[Optional[WFCTile]]] = []
        self.width = GRID_SIZE
        self.height = GRID_SIZE
        self._build_tileset()

    def _build_tileset(self):
        """Construye el set de tiles basado EXCLUSIVAMENTE en el Body Plan."""
        plan = self.card.body_plan
        p = self.card.palette
        
        # Factory de tiles específica por plan
        if plan == BodyPlanType.BIPED:
            self._create_biped_tiles(p)
        elif plan == BodyPlanType.HEXAPOD:
            self._create_hexapod_tiles(p)
        elif plan == BodyPlanType.CEPHALOPOD:
            self._create_cephalopod_tiles(p)
        elif plan == BodyPlanType.RADIAL:
            self._create_radial_tiles(p)
        elif plan == BodyPlanType.SERPENTINE:
            self._create_serpentine_tiles(p)
            
        # Añadir tile vacío siempre
        self.tiles.append(WFCTile(
            id="empty", type=TileType.EMPTY,
            edges=(Edge.NONE, Edge.NONE, Edge.NONE, Edge.NONE),
            weight=1.0,
            sprite_data={"type": "background"}
        ))

    # --- FÁBRICAS DE TILES POR ARQUETIPO ---

    def _create_biped_tiles(self, p):
        # Cabeza: Conecta cuerpo abajo
        self.tiles.append(WFCTile("head", TileType.HEAD, (Edge.NONE, Edge.NONE, Edge.CONN_BODY, Edge.NONE), 1.0, {"part": "head", "dir": "up"}))
        # Torso recto
        self.tiles.append(WFCTile("body_v", TileType.BODY_STRAIGHT, (Edge.CONN_BODY, Edge.NONE, Edge.CONN_BODY, Edge.NONE), 3.0, {"part": "torso", "shape": "rect"}))
        # Torso con brazos
        self.tiles.append(WFCTile("body_arms", TileType.BODY_JOINT, (Edge.CONN_BODY, Edge.CONN_LIMB, Edge.CONN_BODY, Edge.CONN_LIMB), 2.0, {"part": "torso", "shape": "with_arms"}))
        # Pierna superior
        self.tiles.append(WFCTile("leg_top", TileType.LIMB_BASE, (Edge.CONN_BODY, Edge.NONE, Edge.CONN_LIMB, Edge.NONE), 2.0, {"part": "leg", "seg": "upper"}))
        # Pierna inferior
        self.tiles.append(WFCTile("leg_bot", TileType.LIMB_MID, (Edge.CONN_LIMB, Edge.NONE, Edge.CONN_LIMB, Edge.NONE), 2.0, {"part": "leg", "seg": "lower"}))
        # Pie
        self.tiles.append(WFCTile("foot", TileType.LIMB_END, (Edge.CONN_LIMB, Edge.NONE, Edge.NONE, Edge.NONE), 1.5, {"part": "foot"}))

    def _create_hexapod_tiles(self, p):
        # Cabeza frontal
        self.tiles.append(WFCTile("head_fwd", TileType.HEAD, (Edge.NONE, Edge.NONE, Edge.CONN_BODY, Edge.NONE), 1.0, {"part": "head", "dir": "right"}))
        # Segmento cuerpo
        self.tiles.append(WFCTile("seg_straight", TileType.BODY_STRAIGHT, (Edge.NONE, Edge.CONN_BODY, Edge.NONE, Edge.CONN_BODY), 3.0, {"part": "abdomen", "shape": "seg"}))
        # Segmento con patas (N/S)
        self.tiles.append(WFCTile("seg_legs_ns", TileType.BODY_JOINT, (Edge.CONN_LIMB, Edge.CONN_BODY, Edge.CONN_LIMB, Edge.CONN_BODY), 2.5, {"part": "thorax", "legs": "ns"}))
        # Pata
        self.tiles.append(WFCTile("leg_joint", TileType.LIMB_BASE, (Edge.CONN_LIMB, Edge.NONE, Edge.NONE, Edge.NONE), 2.0, {"part": "leg", "joint": "knee"}))
        self.tiles.append(WFCTile("leg_end", TileType.LIMB_END, (Edge.CONN_LIMB, Edge.NONE, Edge.NONE, Edge.NONE), 1.5, {"part": "claw"}))
        # Cola
        self.tiles.append(WFCTile("tail_start", TileType.TAIL_START, (Edge.NONE, Edge.NONE, Edge.NONE, Edge.CONN_BODY), 1.0, {"part": "tail_base"}))
        self.tiles.append(WFCTile("tail_end", TileType.TAIL_END, (Edge.NONE, Edge.NONE, Edge.NONE, Edge.CONN_TAIL), 1.0, {"part": "tail_tip"}))

    def _create_cephalopod_tiles(self, p):
        # Manto/Cabeza grande (Conecta tentáculos abajo)
        self.tiles.append(WFCTile("mantle", TileType.HEAD, (Edge.NONE, Edge.NONE, Edge.CONN_LIMB, Edge.NONE), 1.0, {"part": "mantle", "shape": "oval"}))
        # Ojo/Sensor lateral
        self.tiles.append(WFCTile("eye_cluster", TileType.BODY_JOINT, (Edge.NONE, Edge.CONN_LIMB, Edge.CONN_LIMB, Edge.NONE), 1.5, {"part": "sensor"}))
        # Tentáculo segmento 1
        self.tiles.append(WFCTile("tent_1", TileType.LIMB_BASE, (Edge.CONN_LIMB, Edge.NONE, Edge.CONN_LIMB, Edge.NONE), 2.0, {"part": "tentacle", "seg": 1}))
        # Tentáculo segmento 2
        self.tiles.append(WFCTile("tent_2", TileType.LIMB_MID, (Edge.CONN_LIMB, Edge.NONE, Edge.CONN_LIMB, Edge.NONE), 2.0, {"part": "tentacle", "seg": 2}))
        # Punta tentáculo
        self.tiles.append(WFCTile("tent_tip", TileType.LIMB_END, (Edge.CONN_LIMB, Edge.NONE, Edge.NONE, Edge.NONE), 1.5, {"part": "tentacle_tip"}))

    def _create_radial_tiles(self, p):
        # Centro
        self.tiles.append(WFCTile("core", TileType.CENTER_RADIAL, (Edge.CONN_CENTER, Edge.CONN_CENTER, Edge.CONN_CENTER, Edge.CONN_CENTER), 1.0, {"part": "core"}))
        # Brazo radial
        self.tiles.append(WFCTile("arm_1", TileType.ARM_RADIAL, (Edge.NONE, Edge.NONE, Edge.NONE, Edge.CONN_CENTER), 2.0, {"part": "arm", "pos": "left"}))
        self.tiles.append(WFCTile("arm_2", TileType.ARM_RADIAL, (Edge.NONE, Edge.CONN_CENTER, Edge.NONE, Edge.NONE), 2.0, {"part": "arm", "pos": "up"}))
        self.tiles.append(WFCTile("arm_3", TileType.ARM_RADIAL, (Edge.NONE, Edge.NONE, Edge.CONN_CENTER, Edge.NONE), 2.0, {"part": "arm", "pos": "right"}))
        self.tiles.append(WFCTile("arm_4", TileType.ARM_RADIAL, (Edge.CONN_CENTER, Edge.NONE, Edge.NONE, Edge.NONE), 2.0, {"part": "arm", "pos": "down"}))
        # Punta brazo
        self.tiles.append(WFCTile("arm_tip", TileType.LIMB_END, (Edge.CONN_CENTER, Edge.NONE, Edge.NONE, Edge.NONE), 1.5, {"part": "arm_tip"}))

    def _create_serpentine_tiles(self, p):
        # Cabeza
        self.tiles.append(WFCTile("snake_head", TileType.HEAD, (Edge.NONE, Edge.NONE, Edge.CONN_BODY, Edge.NONE), 1.0, {"part": "head_snake"}))
        # Cuerpo recto V
        self.tiles.append(WFCTile("snake_v", TileType.BODY_STRAIGHT, (Edge.CONN_BODY, Edge.NONE, Edge.CONN_BODY, Edge.NONE), 3.0, {"part": "body_seg", "shape": "v"}))
        # Cuerpo recto H
        self.tiles.append(WFCTile("snake_h", TileType.BODY_STRAIGHT, (Edge.NONE, Edge.CONN_BODY, Edge.NONE, Edge.CONN_BODY), 3.0, {"part": "body_seg", "shape": "h"}))
        # Curva
        self.tiles.append(WFCTile("snake_curve_ne", TileType.BODY_CURVE, (Edge.NONE, Edge.CONN_BODY, Edge.CONN_BODY, Edge.NONE), 2.0, {"part": "body_seg", "curve": "ne"}))
        self.tiles.append(WFCTile("snake_curve_se", TileType.BODY_CURVE, (Edge.CONN_BODY, Edge.CONN_BODY, Edge.NONE, Edge.NONE), 2.0, {"part": "body_seg", "curve": "se"}))
        self.tiles.append(WFCTile("snake_curve_sw", TileType.BODY_CURVE, (Edge.NONE, Edge.NONE, Edge.CONN_BODY, Edge.CONN_BODY), 2.0, {"part": "body_seg", "curve": "sw"}))
        self.tiles.append(WFCTile("snake_curve_nw", TileType.BODY_CURVE, (Edge.CONN_BODY, Edge.NONE, Edge.NONE, Edge.CONN_BODY), 2.0, {"part": "body_seg", "curve": "nw"}))
        # Cola
        self.tiles.append(WFCTile("snake_tail", TileType.TAIL_END, (Edge.CONN_BODY, Edge.NONE, Edge.NONE, Edge.NONE), 1.0, {"part": "tail_tip"}))

    def _is_compatible(self, t1: WFCTile, t2: WFCTile, direction: str) -> bool:
        """Verifica compatibilidad de bordes entre dos tiles adyacentes."""
        # Direcciones: 'N' (t2 está al norte de t1), 'S', 'E', 'W'
        # Si t2 está al NORTE de t1, comparamos Borde N de t1 con Borde S de t2
        
        map_dir_to_edge = {
            'N': (0, 2), # t1.top vs t2.bottom
            'S': (2, 0), # t1.bottom vs t2.top
            'E': (1, 3), # t1.right vs t2.left
            'W': (3, 1)  # t1.left vs t2.right
        }
        
        idx1, idx2 = map_dir_to_edge[direction]
        edge1 = t1.edges[idx1]
        edge2 = t2.edges[idx2]
        
        if edge1 == Edge.NONE and edge2 == Edge.NONE:
            return True
        if edge1 == Edge.NONE or edge2 == Edge.NONE:
            return False
            
        # Lógica de conexión específica
        # CONN_BODY conecta con CONN_BODY
        # CONN_LIMB conecta con CONN_LIMB (o CONN_CENTER en radiales)
        # CONN_TAIL conecta con CONN_TAIL o CONN_BODY (si es inicio)
        
        if edge1 == edge2:
            return True
            
        # Casos especiales de simetría radial
        if edge1 == Edge.CONN_CENTER and edge2 == Edge.CONN_CENTER:
            return True
            
        # Cola conecta con cuerpo
        if {edge1, edge2} == {Edge.CONN_TAIL, Edge.CONN_BODY}:
            return True
            
        return False

    def _run_with_restart(self) -> List[List[Optional[WFCTile]]]:
        """Reinicia la generación desde cero."""
        print("   ⚠️  Contradicción detectada, reiniciando WFC...")
        return self.generate()
    
    def generate(self) -> List[List[Optional[WFCTile]]]:
        """Ejecuta el algoritmo WFC."""
        # Inicializar grilla con todos los tiles posibles
        self.grid = [[self.tiles[:] for _ in range(self.width)] for _ in range(self.height)]
        
        observed = [] # Pila de celdas para propagar
        
        # Semilla inicial: Colocar una parte central aleatoria en el centro
        center_x, center_y = self.width // 2, self.height // 2
        possible_centers = [t for t in self.tiles if t.type in [TileType.HEAD, TileType.CENTER_RADIAL, TileType.BODY_STRAIGHT]]
        if not possible_centers: possible_centers = self.tiles
        
        seed_tile = random.choice(possible_centers)
        self.grid[center_y][center_x] = [seed_tile]
        observed.append((center_x, center_y))
        
        iterations = 0
        max_iterations = 2000
        
        while observed and iterations < max_iterations:
            iterations += 1
            
            # 1. Propagación
            if observed:
                x, y = observed.pop(0)
                current_options = self.grid[y][x]
                
                # Verificar vecinos
                neighbors = [
                    ((x, y-1), 'N'), ((x, y+1), 'S'),
                    ((x-1, y), 'W'), ((x+1, y), 'E')
                ]
                
                for (nx, ny), direction in neighbors:
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        neighbor_options = self.grid[ny][nx]
                        if len(neighbor_options) == 1: continue # Ya colapsado
                        
                        # Filtrar opciones incompatibles
                        new_options = []
                        for opt in neighbor_options:
                            # ¿Existe al menos un tile en la celda actual compatible con opt?
                            is_valid = False
                            for curr in current_options:
                                # Nota: La dirección se invierte para la comprobación desde el vecino
                                # Si estamos mirando al vecino Norte (N), verificamos compatibilidad N de curr con S de opt
                                # Pero la función _is_compatible espera (tile_referencia, tile_vecino, direccion_desde_referencia)
                                # Aquí 'curr' es referencia, 'opt' es vecino en dirección 'direction'
                                if self._is_compatible(curr, opt, direction):
                                    is_valid = True
                                    break
                            if is_valid:
                                new_options.append(opt)
                        
                        if len(new_options) != len(neighbor_options):
                            self.grid[ny][nx] = new_options
                            if len(new_options) == 1 and (nx, ny) not in observed:
                                observed.append((nx, ny))
                            elif len(new_options) == 0:
                                # Contradicción - Reinicio completo (para demo)
                                return self._run_with_restart()

            # 2. Colapso (Elegir la celda con menor entropía)
            min_entropy = 9999
            candidates = []
            
            for y in range(self.height):
                for x in range(self.width):
                    opts = self.grid[y][x]
                    if len(opts) > 1:
                        # Entropía simple = número de opciones + peso inverso
                        entropy = len(opts)
                        if entropy < min_entropy:
                            min_entropy = entropy
                            candidates = [(x, y)]
                        elif entropy == min_entropy:
                            candidates.append((x, y))
            
            if not candidates:
                break # Terminado
                
            # Elegir uno aleatorio de los candidatos
            cx, cy = random.choice(candidates)
            options = self.grid[cy][cx]
            
            # Ponderar selección
            total_weight = sum(t.weight for t in options)
            r = random.uniform(0, total_weight)
            selected = None
            for t in options:
                r -= t.weight
                if r <= 0:
                    selected = t
                    break
            if not selected: selected = options[-1]
            
            self.grid[cy][cx] = [selected]
            observed.append((cx, cy))
            
        return self.grid

# ==============================================================================
# FASE 3: RENDERIZADO VISUAL (PIXEL ART PROCEDURAL)
# ==============================================================================

class PixelArtRenderer:
    def __init__(self, grid: List[List[Optional[WFCTile]]], palette: List[str]):
        self.grid = grid
        self.palette = palette
        self.rows = len(grid)
        self.cols = len(grid[0]) if grid else 0
        
    def create_image(self) -> Image.Image:
        if not HAS_PIL:
            return None
            
        width_px = self.cols * TILE_SIZE
        height_px = self.rows * TILE_SIZE
        
        # Fondo transparente o gradiente suave
        img = Image.new('RGBA', (width_px, height_px), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Dibujar fondo de bioma sutil
        bg_color = self.palette[0] + "40" # 25% opacity
        draw.rectangle([0, 0, width_px, height_px], fill=bg_color)
        
        for y in range(self.rows):
            for x in range(self.cols):
                cell = self.grid[y][x]
                if not cell or len(cell) != 1:
                    continue
                    
                tile = cell[0]
                if tile.type == TileType.EMPTY:
                    continue
                    
                px = x * TILE_SIZE
                py = y * TILE_SIZE
                
                self._draw_tile_sprite(draw, tile, px, py)
                
        return img

    def _draw_tile_sprite(self, draw: ImageDraw.Draw, tile: WFCTile, x: int, y: int):
        """Dibuja el sprite procedural basado en las instrucciones del tile."""
        color_main = self.palette[1]
        color_sec = self.palette[2]
        color_detail = self.palette[3]
        
        # Coordenadas relativas al tile (0-32)
        cx, cy = x + TILE_SIZE//2, y + TILE_SIZE//2
        
        data = tile.sprite_data
        part = data.get("part", "")
        
        # Funciones auxiliares de dibujo
        def draw_circle(r, fill, outline=None):
            draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill, outline=outline)
            
        def draw_rect(w, h, fill, outline=None):
            draw.rectangle([cx-w//2, cy-h//2, cx+w//2, cy+h//2], fill=fill, outline=outline)
            
        def draw_line_angle(angle, length, width=3, fill=color_sec):
            rad = math.radians(angle)
            ex = cx + math.cos(rad) * length
            ey = cy + math.sin(rad) * length
            draw.line([(cx, cy), (ex, ey)], fill=fill, width=width)

        # Lógica de dibujo por tipo de parte
        if part == "head":
            dir_val = data.get("dir", "up")
            angle = {"up": -90, "down": 90, "right": 0, "left": 180}.get(dir_val, -90)
            # Dibujar cabeza ovalada rotada
            draw.ellipse([cx-10, cy-10, cx+10, cy+10], fill=color_main, outline=color_sec)
            # Ojo
            eye_off_x = math.cos(math.radians(angle)) * 6
            eye_off_y = math.sin(math.radians(angle)) * 6
            draw.circle((int(cx+eye_off_x), int(cy+eye_off_y)), radius=3, fill="#000000")
            
        elif part == "torso":
            shape = data.get("shape", "rect")
            if shape == "rect":
                draw_rect(14, 20, color_main, color_sec)
                # Detalle columna
                draw.line([(cx, cy-8), (cx, cy+8)], fill=color_detail, width=2)
            elif shape == "with_arms":
                draw_rect(14, 18, color_main, color_sec)
                # Brazos
                draw_line_angle(0, 12, width=4, fill=color_sec)
                draw_line_angle(180, 12, width=4, fill=color_sec)
                
        elif part == "leg":
            seg = data.get("seg", "upper")
            # Pierna articulada simple
            if seg == "upper":
                draw.line([(cx, cy-10), (cx+4, cy+10)], fill=color_sec, width=5)
            else:
                draw.line([(cx-4, cy-10), (cx, cy+10)], fill=color_sec, width=4)
                
        elif part == "foot" or part == "claw":
            draw.polygon([(cx-4, cy-5), (cx+4, cy-5), (cx, cy+8)], fill=color_detail)
            
        elif part == "abdomen" or part == "body_seg":
            shape = data.get("shape", "seg")
            if shape == "seg":
                draw.ellipse([cx-8, cy-10, cx+8, cy+10], fill=color_main, outline=color_sec)
                # Textura anillos
                draw.arc([cx-6, cy-8, cx+6, cy+8], 0, 360, fill=color_detail, width=1)
            elif shape in ["v", "h"]:
                w, h = (10, 20) if shape == "v" else (20, 10)
                draw.ellipse([cx-w, cy-h, cx+w, cy+h], fill=color_main, outline=color_sec)
                
        elif part == "mantle":
            draw.ellipse([cx-12, cy-14, cx+12, cy+10], fill=color_main, outline=color_sec)
            # Ojos grandes
            draw.circle((cx-6, cy-6), 4, fill="#FFF")
            draw.circle((cx+6, cy-6), 4, fill="#FFF")
            draw.circle((cx-6, cy-6), 2, fill="#000")
            draw.circle((cx+6, cy-6), 2, fill="#000")
            
        elif part == "tentacle":
            # Curva bezier simulada con líneas
            offset = 5 if data.get("seg", 1) % 2 == 0 else -5
            draw.line([(cx, cy-10), (cx+offset, cy+10)], fill=color_sec, width=4)
            
        elif part == "core":
            draw.polygon([(cx, cy-10), (cx+10, cy), (cx, cy+10), (cx-10, cy)], fill=color_main, outline=color_sec)
            draw.circle((cx, cy), 4, fill=color_detail)
            
        elif part == "arm":
            pos = data.get("pos", "up")
            if pos == "up": draw.line([(cx, cy), (cx, cy-12)], fill=color_sec, width=4)
            elif pos == "down": draw.line([(cx, cy), (cx, cy+12)], fill=color_sec, width=4)
            elif pos == "left": draw.line([(cx, cy), (cx-12, cy)], fill=color_sec, width=4)
            elif pos == "right": draw.line([(cx, cy), (cx+12, cy)], fill=color_sec, width=4)
            
        elif part == "head_snake":
            draw.ellipse([cx-8, cy-6, cx+8, cy+6], fill=color_main, outline=color_sec)
            # Lengua/boca
            draw.line([(cx+8, cy), (cx+12, cy)], fill="#FF0000", width=1)

# ==============================================================================
# MAIN & DEMO
# ==============================================================================

def run_simulation():
    print("🧬 INICIANDO PIPELINE DE GENERACIÓN DE CRIATURAS V3.0")
    print("="*50)
    
    # 1. Definir Escenarios Ecológicos Distintos
    scenarios = [
        EcoVariables(-25, 40, 5500, 0.6, 30),   # Alpino Extremo -> Esperado: Bípedo o Serpentino pequeño
        EcoVariables(32, 85, 100, 1.0, 80),     # Selva Tropical -> Esperado: Hexápodo o Cefalópodo arbóreo
        EcoVariables(42, 10, 200, 1.0, 15),     # Desierto Árido -> Esperado: Serpentino o Hexápodo blindado
        EcoVariables(4, 95, -400, 1.8, 40),     # Fosa Oceánica -> Esperado: Cefalópodo o Radial
        EcoVariables(20, 50, 0, 1.0, 90)        # Pradera Templada -> Esperado: Radial o Bípedo
    ]
    
    engine = EcologicalEngine()
    
    output_dir = "creature_outputs_v3"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i, eco in enumerate(scenarios):
        print(f"\n🌍 Generando ecosistema #{i+1}...")
        print(f"   Temp: {eco.temperature}°C | Hum: {eco.humidity}% | Alt: {eco.altitude}m")
        
        # Fase 1: Tarjeta de Criatura
        card = engine.generate_creature(eco)
        print(f"   🧬 Especie: {card.id}")
        print(f"   🏛️  Plan Corporal: {card.body_plan.value.upper()}")
        print(f"   🎨 Paleta: {card.palette}")
        
        # Guardar JSON de la tarjeta
        card_json = {
            "id": card.id,
            "body_plan": card.body_plan.value,
            "eco_vars": vars(eco),
            "anatomy": card.anatomy,
            "survival": card.survival,
            "palette": card.palette
        }
        with open(f"{output_dir}/{card.id}.json", "w") as f:
            json.dump(card_json, f, indent=2)
            
        # Fase 2: WFC
        print(f"   🔄 Ejecutando Wave Function Collapse ({GRID_SIZE}x{GRID_SIZE})...")
        wfc = WFCGenerator(card)
        grid = wfc.generate()
        
        # Verificar éxito
        collapsed_count = sum(1 for row in grid for cell in row if len(cell) == 1)
        total_cells = GRID_SIZE * GRID_SIZE
        print(f"   ✅ Colapso completado: {collapsed_count}/{total_cells} celdas definidas.")
        
        # Fase 3: Renderizado
        if HAS_PIL:
            renderer = PixelArtRenderer(grid, card.palette)
            img = renderer.create_image()
            
            if img:
                # Escalar para mejor visibilidad (Pixel Art look)
                final_size = (GRID_SIZE * TILE_SIZE * 4, GRID_SIZE * TILE_SIZE * 4)
                img_scaled = img.resize(final_size, Image.NEAREST)
                
                filename = f"{output_dir}/{card.id}.png"
                img_scaled.save(filename)
                print(f"   🖼️  Imagen guardada: {filename}")
                
                # Mostrar miniatura en consola (ASCII art básico)
                print("   👁️  Vista previa (ASCII):")
                thumb_w, thumb_h = 40, 20
                img_thumb = img_scaled.resize((thumb_w, thumb_h), Image.NEAREST)
                # Convertir a escala de grises para ASCII
                img_gray = img_thumb.convert('L')
                chars = " .:-=+*#%@"
                for y in range(thumb_h):
                    line = ""
                    for x in range(thumb_w):
                        p = img_gray.getpixel((x, y))
                        # Invertir porque fondo suele ser claro en PNG transparente renderizado
                        char_idx = min(int(p / 255 * len(chars)), len(chars)-1)
                        line += chars[char_idx]
                    print(f"      {line}")
        else:
            print("   ⚠️  Saltando generación de imagen (Instale Pillow)")

    print("\n" + "="*50)
    print("✅ PROCESO FINALIZADO. Revise la carpeta 'creature_outputs_v3'")

if __name__ == "__main__":
    run_simulation()
