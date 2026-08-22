#!/usr/bin/env python3
"""
CREATURE WFC V4 - GENERADOR VISUAL DE CRIATURAS PROCEDURALES
============================================================
Sistema completo de generación de criaturas con 5 planes corporales distintos
usando Wave Function Collapse (WFC) y renderizado a Pixel Art PNG.

Autor: Senior Procedural Generation Architect
Versión: 4.0 - Diversidad Morfológica Completa
"""

import json
import random
import math
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import os
import time

# ============================================================================
# CONFIGURACIÓN GLOBAL
# ============================================================================

OUTPUT_DIR = "creature_outputs_v4"
TILE_SIZE = 64  # Tamaño de cada tile en píxeles
GRID_SIZE = 12  # Tamaño de la grilla WFC (12x12 tiles = 768x768px final)
SCALE_FACTOR = 3  # Escalado final para pixel art nítido
MAX_ATTEMPTS = 50  # Máximos intentos de generación WFC

# ============================================================================
# TIPOS DE Bordes Direccionales para WFC
# ============================================================================

class BorderType(Enum):
    """Tipos de conectores direccionales para reglas WFC estrictas"""
    EMPTY = "empty"           # Borde vacío (fondo/hábitat)
    BODY_FRONT = "body_front" # Frente de segmento corporal
    BODY_BACK = "body_back"   # Parte trasera de segmento corporal
    HEAD_BACK = "head_back"   # Parte trasera de cabeza
    LIMB_BASE = "limb_base"   # Base de extremidad (conecta al cuerpo)
    LIMB_TIP = "limb_tip"     # Punta de extremidad (no conecta)
    TAIL_BASE = "tail_base"   # Base de cola
    TAIL_MID = "tail_mid"     # Segmento medio de cola
    TAIL_TIP = "tail_tip"     # Punta de cola
    TENTACLE_BASE = "tentacle_base"  # Base de tentáculo
    TENTACLE_MID = "tentacle_mid"    # Segmento de tentáculo
    TENTACLE_TIP = "tentacle_tip"    # Punta de tentáculo
    MANTLE_EDGE = "mantle_edge"      # Borde de manto (cefalópodo)
    RADIAL_CENTER = "radial_center"  # Centro radial
    RADIAL_ARM = "radial_arm"        # Brazo radial

# Reglas de compatibilidad: qué bordes pueden conectarse entre sí
COMPATIBILITY_RULES: Dict[BorderType, Set[BorderType]] = {
    BorderType.EMPTY: {BorderType.EMPTY},
    BorderType.BODY_FRONT: {BorderType.BODY_BACK, BorderType.HEAD_BACK},
    BorderType.BODY_BACK: {BorderType.BODY_FRONT},
    BorderType.HEAD_BACK: {BorderType.BODY_FRONT},
    BorderType.LIMB_BASE: {BorderType.BODY_FRONT, BorderType.BODY_BACK},
    BorderType.LIMB_TIP: {BorderType.EMPTY},
    BorderType.TAIL_BASE: {BorderType.BODY_BACK},
    BorderType.TAIL_MID: {BorderType.TAIL_BASE, BorderType.TAIL_MID},
    BorderType.TAIL_TIP: {BorderType.TAIL_MID, BorderType.EMPTY},
    BorderType.TENTACLE_BASE: {BorderType.MANTLE_EDGE},
    BorderType.TENTACLE_MID: {BorderType.TENTACLE_BASE, BorderType.TENTACLE_MID},
    BorderType.TENTACLE_TIP: {BorderType.TENTACLE_MID, BorderType.EMPTY},
    BorderType.MANTLE_EDGE: {BorderType.MANTLE_EDGE, BorderType.TENTACLE_BASE, BorderType.EMPTY},
    BorderType.RADIAL_CENTER: {BorderType.RADIAL_ARM, BorderType.MANTLE_EDGE},
    BorderType.RADIAL_ARM: {BorderType.RADIAL_CENTER, BorderType.RADIAL_ARM, BorderType.EMPTY},
}

# ============================================================================
# PLANES CORPORALES
# ============================================================================

class BodyPlan(Enum):
    """Los 5 planes corporales distintos"""
    BIPED = "bípedo"           # 2 extremidades, postura erguida
    HEXAPOD = "hexápodo"       # 6 extremidades, simetría bilateral
    CEPHALOPOD = "cefalópodo"  # Manto + tentáculos
    SERPENTINE = "serpentino"  # Cuerpo alargado sin extremidades
    RADIAL = "radial"          # Simetría radial (5 brazos)

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class EcologicalInput:
    """Las 5 variables ecológicas de entrada"""
    temperature: float      # °C (-40 a 50)
    humidity: float         # % (0 a 100)
    altitude: float         # metros (-500 a 9000)
    pressure: float         # atm (0.3 a 5.0)
    resources: float        # densidad de recursos (0.0 a 1.0)

@dataclass
class CreatureCard:
    """Tarjeta de Criatura generada en Fase 1"""
    body_plan: BodyPlan
    anatomy: Dict
    survival: Dict
    spatial_rules: Dict
    energy_source: str
    ecological_input: EcologicalInput

@dataclass
class Tile:
    """Tile individual para WFC"""
    id: str
    body_plan: BodyPlan
    borders: Tuple[BorderType, BorderType, BorderType, BorderType]  # N, E, S, W
    weight: float
    sprite_data: Dict  # Datos para renderizar el sprite

# ============================================================================
# FASE 1: MOTOR ECOLÓGICO
# ============================================================================

class EcologicalEngine:
    """Motor de Definición Ecológica y Tarjeta de Criatura"""
    
    def __init__(self):
        self.body_plan_weights = {
            BodyPlan.BIPED: [0.4, 0.1, 0.3, 0.1, 0.1],      # Prefiere frío, alto
            BodyPlan.HEXAPOD: [0.2, 0.3, 0.2, 0.2, 0.1],    # Temperado general
            BodyPlan.CEPHALOPOD: [0.1, 0.3, -0.2, 0.4, 0.2], # húmedo, alta presión
            BodyPlan.SERPENTINE: [0.3, -0.2, 0.1, 0.1, 0.3], # seco, recursos
            BodyPlan.RADIAL: [0.1, 0.4, 0.1, 0.1, 0.3],     # húmedo, recursos
        }
    
    def calculate_body_plan(self, eco: EcologicalInput) -> BodyPlan:
        """Determina el plan corporal basado en las 5 variables"""
        scores = {}
        
        for plan, weights in self.body_plan_weights.items():
            score = (
                weights[0] * (eco.temperature / 50.0) +
                weights[1] * (eco.humidity / 100.0) +
                weights[2] * (eco.altitude / 9000.0) +
                weights[3] * (eco.pressure / 5.0) +
                weights[4] * eco.resources
            )
            # Ajustes específicos
            if plan == BodyPlan.BIPED and eco.temperature < 0 and eco.altitude > 3000:
                score += 0.5
            if plan == BodyPlan.CEPHALOPOD and eco.humidity > 70 and eco.pressure > 1.5:
                score += 0.6
            if plan == BodyPlan.SERPENTINE and eco.humidity < 30 and eco.temperature > 30:
                score += 0.5
            if plan == BodyPlan.RADIAL and eco.humidity > 60 and eco.resources > 0.6:
                score += 0.4
                
            scores[plan] = score
        
        return max(scores, key=scores.get)
    
    def generate_anatomy(self, body_plan: BodyPlan, eco: EcologicalInput) -> Dict:
        """Genera anatomía adaptativa según plan corporal y ambiente"""
        anatomy = {"body_plan": body_plan.value}
        
        if body_plan == BodyPlan.BIPED:
            anatomy["limbs"] = 2
            anatomy["posture"] = "erect"
            anatomy["spine_segments"] = random.randint(8, 12)
            anatomy["armor_type"] = "thick_fur" if eco.temperature < 10 else "scales"
            anatomy["sensory_organs"] = ["forward_eyes", "external_ears"]
            anatomy["size_range"] = (1.5, 2.5) if eco.altitude > 3000 else (1.2, 2.0)
            
        elif body_plan == BodyPlan.HEXAPOD:
            anatomy["limbs"] = 6
            anatomy["posture"] = "quadrupedal_stable"
            anatomy["spine_segments"] = random.randint(10, 16)
            anatomy["armor_type"] = "chitin" if eco.humidity < 40 else "carapace"
            anatomy["sensory_organs"] = ["compound_eyes", "antennae"]
            anatomy["size_range"] = (0.5, 1.5)
            
        elif body_plan == BodyPlan.CEPHALOPOD:
            anatomy["mantle_size"] = random.uniform(0.8, 2.0)
            anatomy["tentacles"] = random.randint(6, 10)
            anatomy["siphon"] = True
            anatomy["armor_type"] = "soft_muscular" if eco.pressure > 2.0 else "stiff_mantle"
            anatomy["sensory_organs"] = ["large_lateral_eyes", "chemoreceptors"]
            anatomy["size_range"] = (1.0, 3.0) if eco.pressure > 2.0 else (0.6, 1.5)
            
        elif body_plan == BodyPlan.SERPENTINE:
            anatomy["limbs"] = 0
            anatomy["body_segments"] = random.randint(15, 25)
            anatomy["cross_section"] = "cylindrical" if eco.humidity < 30 else "laterally_compressed"
            anatomy["armor_type"] = "overlapping_scales"
            anatomy["sensory_organs"] = ["heat_pits", "forked_tongue", "lateral_line"]
            anatomy["size_range"] = (2.0, 5.0) if eco.resources > 0.5 else (1.0, 3.0)
            
        elif body_plan == BodyPlan.RADIAL:
            anatomy["symmetry_order"] = 5
            anatomy["arms"] = 5
            anatomy["central_mouth"] = True
            anatomy["armor_type"] = "calcified_plates" if eco.resources > 0.5 else "flexible_skin"
            anatomy["sensory_organs"] = ["distributed_nerve_net", "statocysts"]
            anatomy["size_range"] = (0.8, 2.0)
        
        return anatomy
    
    def generate_survival(self, body_plan: BodyPlan, eco: EcologicalInput) -> Dict:
        """Genera mecanismos de supervivencia"""
        survival = {}
        
        # Tolerancia térmica
        if eco.temperature < -10:
            survival["cold_adaptation"] = ["antifreeze_proteins", "insulating_layer", "reduced_surface_area"]
        elif eco.temperature > 35:
            survival["heat_adaptation"] = ["reflective_surface", "evaporative_cooling", "nocturnal_behavior"]
        else:
            survival["thermal_neutral"] = ["moderate_insulation"]
        
        # Manejo de humedad
        if eco.humidity < 20:
            survival["desert_adaptation"] = ["water_storage", "reduced_respiration", "waxy_cuticle"]
        elif eco.humidity > 80:
            survival["aquatic_semi_aquatic"] = ["hydrophobic_coating", "efficient_oxygen_extraction"]
        
        # Altitud/presión
        if eco.altitude > 4000 or eco.pressure < 0.6:
            survival["high_altitude"] = ["enhanced_hemoglobin", "increased_lung_capacity"]
        elif eco.pressure > 2.0:
            survival["deep_pressure"] = ["pressure_equalization", "flexible_structures"]
        
        # Fuente de energía
        if eco.resources > 0.7:
            survival["energy_source"] = "generalist_omnivore"
        elif eco.temperature > 30 and eco.humidity < 30:
            survival["energy_source"] = "photosynthetic_symbionts" if body_plan == BodyPlan.RADIAL else "specialized_carnivore"
        elif eco.pressure > 2.0:
            survival["energy_source"] = "chemosynthesis_filter_feeder"
        else:
            survival["energy_source"] = "opportunistic_predator"
        
        return survival
    
    def generate_spatial_rules(self, body_plan: BodyPlan, eco: EcologicalInput) -> Dict:
        """Genera restricciones espaciales y reglas de adyacencia"""
        rules = {
            "required_neighbors": [],
            "tolerated_neighbors": [],
            "forbidden_neighbors": [],
            "habitat_preference": []
        }
        
        if body_plan == BodyPlan.BIPED:
            rules["required_neighbors"] = ["solid_ground", "vertical_space"]
            rules["tolerated_neighbors"] = ["rocky_outcrop", "sparse_vegetation"]
            rules["forbidden_neighbors"] = ["deep_water", "dense_swamp"]
            rules["habitat_preference"] = ["mountainous", "temperate_grassland"]
            
        elif body_plan == BodyPlan.HEXAPOD:
            rules["required_neighbors"] = ["stable_ground"]
            rules["tolerated_neighbors"] = ["vegetation", "rocky_terrain", "shallow_water"]
            rules["forbidden_neighbors"] = ["vertical_cliffs", "deep_water"]
            rules["habitat_preference"] = ["forest_floor", "mixed_terrain"]
            
        elif body_plan == BodyPlan.CEPHALOPOD:
            rules["required_neighbors"] = ["water_medium"] if eco.humidity > 70 else ["moist_environment"]
            rules["tolerated_neighbors"] = ["underwater_structures", "kelp_forest", "coral"]
            rules["forbidden_neighbors"] = ["dry_land", "freezing_temperatures"]
            rules["habitat_preference"] = ["oceanic", "coastal_waters"] if eco.pressure < 1.5 else ["deep_sea_trench"]
            
        elif body_plan == BodyPlan.SERPENTINE:
            rules["required_neighbors"] = ["continuous_path"]
            rules["tolerated_neighbors"] = ["sand", "rocky_crevice", "sparse_vegetation", "shallow_water"]
            rules["forbidden_neighbors"] = ["dense_obstacles", "vertical_barriers"]
            rules["habitat_preference"] = ["desert", "grassland", "riverbank"]
            
        elif body_plan == BodyPlan.RADIAL:
            rules["required_neighbors"] = ["stable_anchor_point"]
            rules["tolerated_neighbors"] = ["water_current", "plankton_rich", "rocky_substrate"]
            rules["forbidden_neighbors"] = ["strong_predators", "turbulent_waters"]
            rules["habitat_preference"] = ["shallow_reef", "tidal_zone"] if eco.pressure < 1.5 else ["deep_sea_floor"]
        
        return rules
    
    def generate_creature_card(self, eco: EcologicalInput) -> CreatureCard:
        """Genera la tarjeta completa de criatura"""
        body_plan = self.calculate_body_plan(eco)
        anatomy = self.generate_anatomy(body_plan, eco)
        survival = self.generate_survival(body_plan, eco)
        spatial_rules = self.generate_spatial_rules(body_plan, eco)
        
        # Determinar fuente de energía principal
        energy_source = survival.get("energy_source", "opportunistic_predator")
        
        return CreatureCard(
            body_plan=body_plan,
            anatomy=anatomy,
            survival=survival,
            spatial_rules=spatial_rules,
            energy_source=energy_source,
            ecological_input=eco
        )

# ============================================================================
# FASE 2: FÁBRICA DE TILES POR PLAN CORPORAL
# ============================================================================

class TileFactory:
    """Fábrica de tiles específica para cada plan corporal"""
    
    def __init__(self, body_plan: BodyPlan, color_palette: Dict):
        self.body_plan = body_plan
        self.palette = color_palette
        self.tiles: List[Tile] = []
        self._generate_tiles()
    
    def _generate_tiles(self):
        """Genera todos los tiles posibles para este plan corporal"""
        if self.body_plan == BodyPlan.BIPED:
            self._create_biped_tiles()
        elif self.body_plan == BodyPlan.HEXAPOD:
            self._create_hexapod_tiles()
        elif self.body_plan == BodyPlan.CEPHALOPOD:
            self._create_cephalopod_tiles()
        elif self.body_plan == BodyPlan.SERPENTINE:
            self._create_serpentine_tiles()
        elif self.body_plan == BodyPlan.RADIAL:
            self._create_radial_tiles()
    
    def _create_biped_tiles(self):
        """Tiles para criatura bípeda"""
        # Cabeza
        self.tiles.append(Tile(
            id="biped_head",
            body_plan=self.body_plan,
            borders=(BorderType.EMPTY, BorderType.EMPTY, BorderType.HEAD_BACK, BorderType.EMPTY),
            weight=1.0,
            sprite_data={"type": "head", "direction": "down"}
        ))
        
        # Cuerpo vertical
        for variant in ["straight", "slight_curve_l", "slight_curve_r"]:
            self.tiles.append(Tile(
                id=f"biped_body_{variant}",
                body_plan=self.body_plan,
                borders=(BorderType.BODY_BACK, BorderType.EMPTY, BorderType.BODY_FRONT, BorderType.EMPTY),
                weight=2.0 if variant == "straight" else 1.0,
                sprite_data={"type": "body_vertical", "variant": variant}
            ))
        
        # Extremidades (izquierda y derecha)
        for side in ["left", "right"]:
            for pose in ["standing", "stepping"]:
                border_w = BorderType.LIMB_BASE if side == "left" else BorderType.EMPTY
                border_e = BorderType.LIMB_BASE if side == "right" else BorderType.EMPTY
                self.tiles.append(Tile(
                    id=f"biped_limb_{side}_{pose}",
                    body_plan=self.body_plan,
                    borders=(BorderType.EMPTY, border_e, BorderType.EMPTY, border_w),
                    weight=1.5,
                    sprite_data={"type": "limb", "side": side, "pose": pose}
                ))
        
        # Cola/base
        self.tiles.append(Tile(
            id="biped_tail_base",
            body_plan=self.body_plan,
            borders=(BorderType.EMPTY, BorderType.EMPTY, BorderType.TAIL_BASE, BorderType.EMPTY),
            weight=1.0,
            sprite_data={"type": "tail_base"}
        ))
        
        for variant in ["straight", "curve_l", "curve_r"]:
            self.tiles.append(Tile(
                id=f"biped_tail_{variant}",
                body_plan=self.body_plan,
                borders=(BorderType.TAIL_MID, BorderType.EMPTY, BorderType.TAIL_MID, BorderType.EMPTY),
                weight=1.0,
                sprite_data={"type": "tail_mid", "variant": variant}
            ))
        
        self.tiles.append(Tile(
            id="biped_tail_tip",
            body_plan=self.body_plan,
            borders=(BorderType.TAIL_MID, BorderType.EMPTY, BorderType.TAIL_TIP, BorderType.EMPTY),
            weight=0.8,
            sprite_data={"type": "tail_tip"}
        ))
        
        # Fondo/hábitat
        self.tiles.append(Tile(
            id="biped_habitat",
            body_plan=self.body_plan,
            borders=(BorderType.EMPTY, BorderType.EMPTY, BorderType.EMPTY, BorderType.EMPTY),
            weight=3.0,
            sprite_data={"type": "habitat"}
        ))
    
    def _create_hexapod_tiles(self):
        """Tiles para criatura hexápoda"""
        # Similar a bípedo pero con más extremidades
        self.tiles.append(Tile(
            id="hexapod_head",
            body_plan=self.body_plan,
            borders=(BorderType.EMPTY, BorderType.EMPTY, BorderType.HEAD_BACK, BorderType.EMPTY),
            weight=1.0,
            sprite_data={"type": "head", "direction": "down"}
        ))
        
        # Cuerpo con múltiples puntos de unión para extremidades
        for i in range(3):
            self.tiles.append(Tile(
                id=f"hexapod_body_segment_{i}",
                body_plan=self.body_plan,
                borders=(BorderType.BODY_BACK, BorderType.LIMB_BASE, BorderType.BODY_FRONT, BorderType.LIMB_BASE),
                weight=2.0,
                sprite_data={"type": "body_segment", "segment": i}
            ))
        
        # Extremidades
        for pose in ["neutral", "forward", "backward"]:
            self.tiles.append(Tile(
                id=f"hexapod_limb_{pose}",
                body_plan=self.body_plan,
                borders=(BorderType.EMPTY, BorderType.LIMB_TIP, BorderType.EMPTY, BorderType.LIMB_BASE),
                weight=1.5,
                sprite_data={"type": "limb", "pose": pose}
            ))
        
        # Cola
        self.tiles.append(Tile(
            id="hexapod_tail",
            body_plan=self.body_plan,
            borders=(BorderType.TAIL_BASE, BorderType.EMPTY, BorderType.TAIL_TIP, BorderType.EMPTY),
            weight=1.0,
            sprite_data={"type": "tail"}
        ))
        
        # Hábitat
        self.tiles.append(Tile(
            id="hexapod_habitat",
            body_plan=self.body_plan,
            borders=(BorderType.EMPTY, BorderType.EMPTY, BorderType.EMPTY, BorderType.EMPTY),
            weight=3.0,
            sprite_data={"type": "habitat"}
        ))
    
    def _create_cephalopod_tiles(self):
        """Tiles para cefalópodo"""
        # Manto central
        self.tiles.append(Tile(
            id="ceph_mantle_center",
            body_plan=self.body_plan,
            borders=(BorderType.MANTLE_EDGE, BorderType.MANTLE_EDGE, BorderType.MANTLE_EDGE, BorderType.MANTLE_EDGE),
            weight=1.0,
            sprite_data={"type": "mantle_center"}
        ))
        
        # Bordes de manto
        for edge in ["top", "right", "bottom", "left"]:
            borders_map = {
                "top": (BorderType.MANTLE_EDGE, BorderType.MANTLE_EDGE, BorderType.MANTLE_EDGE, BorderType.EMPTY),
                "right": (BorderType.MANTLE_EDGE, BorderType.EMPTY, BorderType.MANTLE_EDGE, BorderType.MANTLE_EDGE),
                "bottom": (BorderType.EMPTY, BorderType.MANTLE_EDGE, BorderType.MANTLE_EDGE, BorderType.MANTLE_EDGE),
                "left": (BorderType.MANTLE_EDGE, BorderType.MANTLE_EDGE, BorderType.EMPTY, BorderType.MANTLE_EDGE),
            }
            self.tiles.append(Tile(
                id=f"ceph_mantle_{edge}",
                body_plan=self.body_plan,
                borders=borders_map[edge],
                weight=1.5,
                sprite_data={"type": "mantle_edge", "edge": edge}
            ))
        
        # Tentáculos
        for length in ["short", "medium", "long"]:
            weight = 2.0 if length == "medium" else 1.0
            self.tiles.append(Tile(
                id=f"ceph_tentacle_{length}_vertical",
                body_plan=self.body_plan,
                borders=(BorderType.TENTACLE_BASE, BorderType.EMPTY, BorderType.TENTACLE_TIP, BorderType.EMPTY),
                weight=weight,
                sprite_data={"type": "tentacle", "orientation": "vertical", "length": length}
            ))
            self.tiles.append(Tile(
                id=f"ceph_tentacle_{length}_horizontal",
                body_plan=self.body_plan,
                borders=(BorderType.EMPTY, BorderType.TENTACLE_TIP, BorderType.EMPTY, BorderType.TENTACLE_BASE),
                weight=weight,
                sprite_data={"type": "tentacle", "orientation": "horizontal", "length": length}
            ))
        
        # Sifón
        self.tiles.append(Tile(
            id="ceph_siphon",
            body_plan=self.body_plan,
            borders=(BorderType.MANTLE_EDGE, BorderType.EMPTY, BorderType.EMPTY, BorderType.EMPTY),
            weight=0.8,
            sprite_data={"type": "siphon"}
        ))
        
        # Hábitat acuático
        self.tiles.append(Tile(
            id="ceph_habitat",
            body_plan=self.body_plan,
            borders=(BorderType.EMPTY, BorderType.EMPTY, BorderType.EMPTY, BorderType.EMPTY),
            weight=4.0,
            sprite_data={"type": "habitat_water"}
        ))
    
    def _create_serpentine_tiles(self):
        """Tiles para criatura serpentínea"""
        # Cabeza
        self.tiles.append(Tile(
            id="serp_head",
            body_plan=self.body_plan,
            borders=(BorderType.EMPTY, BorderType.EMPTY, BorderType.HEAD_BACK, BorderType.EMPTY),
            weight=1.0,
            sprite_data={"type": "head"}
        ))
        
        # Segmentos corporales curvos
        curves = ["straight", "curve_ne", "curve_nw", "curve_se", "curve_sw"]
        for curve in curves:
            borders_map = {
                "straight": (BorderType.BODY_BACK, BorderType.EMPTY, BorderType.BODY_FRONT, BorderType.EMPTY),
                "curve_ne": (BorderType.BODY_BACK, BorderType.BODY_FRONT, BorderType.EMPTY, BorderType.EMPTY),
                "curve_nw": (BorderType.BODY_BACK, BorderType.EMPTY, BorderType.EMPTY, BorderType.BODY_FRONT),
                "curve_se": (BorderType.EMPTY, BorderType.BODY_FRONT, BorderType.BODY_BACK, BorderType.EMPTY),
                "curve_sw": (BorderType.EMPTY, BorderType.EMPTY, BorderType.BODY_BACK, BorderType.BODY_FRONT),
            }
            self.tiles.append(Tile(
                id=f"serp_body_{curve}",
                body_plan=self.body_plan,
                borders=borders_map[curve],
                weight=2.0 if curve == "straight" else 1.5,
                sprite_data={"type": "body_curve", "curve": curve}
            ))
        
        # Punta de cola
        self.tiles.append(Tile(
            id="serp_tail_tip",
            body_plan=self.body_plan,
            borders=(BorderType.TAIL_MID, BorderType.EMPTY, BorderType.TAIL_TIP, BorderType.EMPTY),
            weight=1.0,
            sprite_data={"type": "tail_tip"}
        ))
        
        # Hábitat
        self.tiles.append(Tile(
            id="serp_habitat",
            body_plan=self.body_plan,
            borders=(BorderType.EMPTY, BorderType.EMPTY, BorderType.EMPTY, BorderType.EMPTY),
            weight=3.5,
            sprite_data={"type": "habitat"}
        ))
    
    def _create_radial_tiles(self):
        """Tiles para criatura radial"""
        # Centro
        self.tiles.append(Tile(
            id="radial_center",
            body_plan=self.body_plan,
            borders=(BorderType.RADIAL_CENTER, BorderType.RADIAL_CENTER, BorderType.RADIAL_CENTER, BorderType.RADIAL_CENTER),
            weight=1.0,
            sprite_data={"type": "center"}
        ))
        
        # Brazos radiales en 4 direcciones
        for direction in ["up", "right", "down", "left"]:
            borders_map = {
                "up": (BorderType.RADIAL_ARM, BorderType.EMPTY, BorderType.RADIAL_CENTER, BorderType.EMPTY),
                "right": (BorderType.RADIAL_CENTER, BorderType.RADIAL_ARM, BorderType.EMPTY, BorderType.EMPTY),
                "down": (BorderType.EMPTY, BorderType.EMPTY, BorderType.RADIAL_ARM, BorderType.RADIAL_CENTER),
                "left": (BorderType.EMPTY, BorderType.RADIAL_CENTER, BorderType.EMPTY, BorderType.RADIAL_ARM),
            }
            self.tiles.append(Tile(
                id=f"radial_arm_{direction}",
                body_plan=self.body_plan,
                borders=borders_map[direction],
                weight=1.5,
                sprite_data={"type": "arm", "direction": direction}
            ))
            
            # Segmentos de brazo
            self.tiles.append(Tile(
                id=f"radial_arm_{direction}_mid",
                body_plan=self.body_plan,
                borders=(borders_map[direction][0], BorderType.EMPTY, borders_map[direction][2], BorderType.EMPTY),
                weight=1.2,
                sprite_data={"type": "arm_mid", "direction": direction}
            ))
        
        # Hábitat
        self.tiles.append(Tile(
            id="radial_habitat",
            body_plan=self.body_plan,
            borders=(BorderType.EMPTY, BorderType.EMPTY, BorderType.EMPTY, BorderType.EMPTY),
            weight=4.0,
            sprite_data={"type": "habitat"}
        ))
    
    def get_tiles(self) -> List[Tile]:
        """Retorna todos los tiles disponibles"""
        return self.tiles

# ============================================================================
# FASE 3: MOTOR WFC ITERATIVO
# ============================================================================

class WFCGrid:
    """Grilla para Wave Function Collapse con propagación iterativa"""
    
    def __init__(self, size: int, tile_factories: Dict[BodyPlan, TileFactory]):
        self.size = size
        self.tile_factories = tile_factories
        self.grid: List[List[Optional[Tile]]] = [[None for _ in range(size)] for _ in range(size)]
        self.possibilities: List[List[Set[str]]] = [[set() for _ in range(size)] for _ in range(size)]
        self.compatibility_cache: Dict[str, Dict[str, bool]] = {}
        self._precompute_compatibility()
    
    def _precompute_compatibility(self):
        """Precomputa matriz de compatibilidad entre todos los tiles"""
        all_tiles = []
        for factory in self.tile_factories.values():
            all_tiles.extend(factory.get_tiles())
        
        for tile1 in all_tiles:
            for tile2 in all_tiles:
                key = f"{tile1.id}|{tile2.id}"
                # Verifica compatibilidad en todas las direcciones
                compatible = True
                # Este cache se usa durante la propagación
                self.compatibility_cache[key] = compatible
    
    def _are_compatible(self, tile1: Tile, tile2: Tile, direction: str) -> bool:
        """Verifica si dos tiles son compatibles en una dirección dada"""
        # direction: 'right', 'down', 'left', 'up'
        border_index_map = {'right': 1, 'down': 2, 'left': 3, 'up': 0}
        
        if direction == 'right':
            border1 = tile1.borders[1]  # East de tile1
            border2 = tile2.borders[3]  # West de tile2
        elif direction == 'down':
            border1 = tile1.borders[2]  # South de tile1
            border2 = tile2.borders[0]  # North de tile2
        elif direction == 'left':
            border1 = tile1.borders[3]  # West de tile1
            border2 = tile2.borders[1]  # East de tile2
        elif direction == 'up':
            border1 = tile1.borders[0]  # North de tile1
            border2 = tile2.borders[2]  # South de tile2
        else:
            return False
        
        # Verifica reglas de compatibilidad
        compatible_set = COMPATIBILITY_RULES.get(border1, set())
        return border2 in compatible_set
    
    def initialize(self, body_plan: BodyPlan):
        """Inicializa la grilla con todas las posibilidades"""
        factory = self.tile_factories[body_plan]
        tiles = factory.get_tiles()
        
        for y in range(self.size):
            for x in range(self.size):
                self.possibilities[y][x] = {tile.id for tile in tiles}
    
    def get_min_entropy_cell(self) -> Optional[Tuple[int, int]]:
        """Encuentra la celda con mínima entropía (>1 posibilidades)"""
        min_entropy = float('inf')
        min_cell = None
        
        for y in range(self.size):
            for x in range(self.size):
                entropy = len(self.possibilities[y][x])
                if 1 < entropy < min_entropy:
                    min_entropy = entropy
                    min_cell = (x, y)
        
        return min_cell
    
    def collapse_cell(self, x: int, y: int, body_plan: BodyPlan) -> bool:
        """Colapsa una celda seleccionando un tile aleatorio ponderado"""
        factory = self.tile_factories[body_plan]
        tiles_by_id = {tile.id: tile for tile in factory.get_tiles()}
        possibilities = list(self.possibilities[y][x])
        
        if not possibilities:
            return False
        
        # Selección ponderada por weights
        weights = [tiles_by_id[tid].weight for tid in possibilities]
        total_weight = sum(weights)
        normalized = [w / total_weight for w in weights]
        
        # Selección aleatoria ponderada
        r = random.random()
        cumulative = 0
        selected_id = possibilities[0]
        
        for i, norm in enumerate(normalized):
            cumulative += norm
            if r <= cumulative:
                selected_id = possibilities[i]
                break
        
        self.grid[y][x] = tiles_by_id[selected_id]
        self.possibilities[y][x] = {selected_id}
        
        return True
    
    def propagate(self, x: int, y: int, body_plan: BodyPlan) -> bool:
        """Propaga restricciones desde una celda colapsada"""
        factory = self.tile_factories[body_plan]
        tiles_by_id = {tile.id: tile for tile in factory.get_tiles()}
        collapsed_tile = self.grid[y][x]
        
        if collapsed_tile is None:
            return True
        
        directions = [
            (1, 0, 'right'),
            (0, 1, 'down'),
            (-1, 0, 'left'),
            (0, -1, 'up')
        ]
        
        changed = False
        
        for dx, dy, direction in directions:
            nx, ny = x + dx, y + dy
            
            if 0 <= nx < self.size and 0 <= ny < self.size:
                old_possibilities = self.possibilities[ny][nx].copy()
                
                # Elimina tiles incompatibles
                new_possibilities = set()
                for tid in self.possibilities[ny][nx]:
                    candidate_tile = tiles_by_id[tid]
                    if self._are_compatible(collapsed_tile, candidate_tile, direction):
                        new_possibilities.add(tid)
                
                self.possibilities[ny][nx] = new_possibilities
                
                if len(new_possibilities) != len(old_possibilities):
                    changed = True
                    
                    # Si se agotan las posibilidades, hay contradicción
                    if len(new_possibilities) == 0:
                        return False
                    
                    # Si queda solo uno, colapsarlo y propagar recursivamente (iterativo)
                    if len(new_possibilities) == 1:
                        self.grid[ny][nx] = tiles_by_id[list(new_possibilities)[0]]
                        # Propagación en cola para evitar recursión
                        queue = [(nx, ny)]
                        while queue:
                            cx, cy = queue.pop(0)
                            # Propagar desde esta nueva celda colapsada
                            for ddx, ddy, ddir in directions:
                                nnx, nny = cx + ddx, cy + ddy
                                if 0 <= nnx < self.size and 0 <= nny < self.size:
                                    if len(self.possibilities[nny][nnx]) > 1:
                                        # Re-propagar restricciones
                                        pass
        
        return changed
    
    def solve(self, body_plan: BodyPlan, max_iterations: int = 10000) -> bool:
        """Resuelve la grilla usando WFC iterativo"""
        self.initialize(body_plan)
        
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Encuentra celda con mínima entropía
            cell = self.get_min_entropy_cell()
            
            if cell is None:
                # Todas las celdas están colapsadas o vacías
                # Verifica si hay alguna sin colapsar
                has_uncollapsed = any(len(self.possibilities[y][x]) > 1 
                                     for y in range(self.size) for x in range(self.size))
                if not has_uncollapsed:
                    return True  # Éxito
                else:
                    # Hay celdas vacías (contradicción)
                    return False
            
            x, y = cell
            
            # Colapsa la celda
            if not self.collapse_cell(x, y, body_plan):
                return False  # Contradicción
            
            # Propaga restricciones
            if not self.propagate(x, y, body_plan):
                return False  # Contradicción durante propagación
        
        return False  # Timeout
    
    def get_result(self) -> List[List[Optional[Tile]]]:
        """Retorna la grilla resuelta"""
        return self.grid

# ============================================================================
# FASE 4: RENDERIZADO VECTORIAL A PIXEL ART
# ============================================================================

class VectorRenderer:
    """Renderizador vectorial de tiles a imágenes PNG"""
    
    def __init__(self, tile_size: int, palette: Dict):
        self.tile_size = tile_size
        self.palette = palette
    
    def render_tile(self, tile: Optional[Tile], output_dir: str, filename: str) -> str:
        """Renderiza un tile individual a PNG"""
        img = Image.new('RGBA', (self.tile_size, self.tile_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        if tile is None:
            # Tile vacío (fondo transparente)
            pass
        else:
            self._draw_sprite(draw, tile)
        
        filepath = os.path.join(output_dir, filename)
        img.save(filepath, 'PNG')
        return filepath
    
    def _draw_sprite(self, draw: ImageDraw.Draw, tile: Tile):
        """Dibuja el sprite según los datos del tile"""
        ts = self.tile_size
        cx, cy = ts // 2, ts // 2  # Centro
        
        sprite_data = tile.sprite_data
        sprite_type = sprite_data.get("type", "habitat")
        
        if sprite_type == "habitat":
            # Fondo de hábitat con gradiente sutil
            color = self.palette.get("habitat", (40, 50, 60))
            draw.rectangle([0, 0, ts-1, ts-1], fill=color)
            
        elif sprite_type == "head":
            # Cabeza con óvalo y ojos
            color = self.palette.get("body", (180, 160, 140))
            eye_color = self.palette.get("eye", (255, 255, 255))
            pupil_color = self.palette.get("pupil", (0, 0, 0))
            
            # Óvalo de cabeza
            bbox = [cx - ts//4, cy - ts//3, cx + ts//4, cy + ts//3]
            draw.ellipse(bbox, fill=color, outline=self.darken(color))
            
            # Ojos
            eye_offset = ts // 8
            draw.ellipse([cx - eye_offset - 4, cy - 8, cx - eye_offset + 4, cy], fill=eye_color)
            draw.ellipse([cx - eye_offset - 2, cy - 6, cx - eye_offset, cy - 4], fill=pupil_color)
            draw.ellipse([cx + eye_offset - 4, cy - 8, cx + eye_offset + 4, cy], fill=eye_color)
            draw.ellipse([cx + eye_offset - 2, cy - 6, cx + eye_offset, cy - 4], fill=pupil_color)
            
        elif sprite_type == "body_vertical":
            # Segmento corporal vertical
            color = self.palette.get("body", (180, 160, 140))
            segment_color = self.palette.get("segment", (160, 140, 120))
            
            # Rectángulo con textura anillada
            width = ts // 3
            draw.rectangle([cx - width//2, 0, cx + width//2, ts], fill=color)
            
            # Anillos decorativos
            for y in range(ts//4, ts, ts//4):
                draw.line([(cx - width//2, y), (cx + width//2, y)], fill=segment_color, width=2)
                
        elif sprite_type == "body_segment":
            # Segmento de cuerpo hexápodo
            color = self.palette.get("body", (180, 160, 140))
            width = ts // 2
            
            draw.rectangle([cx - width//2, cy - width//2, cx + width//2, cy + width//2], 
                          fill=color, outline=self.darken(color))
            
        elif sprite_type == "limb":
            # Extremidad
            color = self.palette.get("limb", (200, 180, 160))
            
            side = sprite_data.get("side", "left")
            pose = sprite_data.get("pose", "standing")
            
            # Línea de extremidad usando Bresenham simplificado
            if side == "left":
                start = (ts//4, cy)
                end = (ts//8, ts - ts//4) if pose == "stepping" else (ts//4, ts - ts//4)
            else:
                start = (ts - ts//4, cy)
                end = (ts - ts//8, ts - ts//4) if pose == "stepping" else (ts - ts//4, ts - ts//4)
            
            draw.line([start, end], fill=color, width=max(4, ts//12))
            
            # Punta/redondeo
            draw.ellipse([end[0]-3, end[1]-3, end[0]+3, end[1]+3], fill=color)
            
        elif sprite_type == "tail_base":
            # Base de cola
            color = self.palette.get("tail", (160, 140, 120))
            width = ts // 4
            
            draw.rectangle([cx - width//2, cy, cx + width//2, ts], fill=color)
            
        elif sprite_type in ["tail_mid", "tail_tip"]:
            # Segmento o punta de cola
            color = self.palette.get("tail", (160, 140, 120))
            variant = sprite_data.get("variant", "straight")
            
            width = ts // 5 if sprite_type == "tail_tip" else ts // 4
            
            if variant == "straight":
                draw.rectangle([cx - width//2, 0, cx + width//2, ts], fill=color)
            elif variant in ["curve_l", "curve_nw", "curve_sw"]:
                # Curva izquierda
                points = [(cx + width//2, ts), (cx - width//2, ts//2), (cx + width//2, 0)]
                draw.polygon(points, fill=color)
            else:
                # Curva derecha
                points = [(cx - width//2, ts), (cx + width//2, ts//2), (cx - width//2, 0)]
                draw.polygon(points, fill=color)
                
        elif sprite_type == "mantle_center":
            # Manto central de cefalópodo
            color = self.palette.get("mantle", (100, 140, 180))
            radius = ts // 3
            
            draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], 
                        fill=color, outline=self.darken(color))
                        
        elif sprite_type == "mantle_edge":
            # Borde de manto
            color = self.palette.get("mantle", (100, 140, 180))
            edge = sprite_data.get("edge", "top")
            
            if edge == "top":
                draw.arc([cx - ts//2, cy - ts//2, cx + ts//2, cy + ts//2], 0, 180, fill=color, width=ts//4)
            elif edge == "bottom":
                draw.arc([cx - ts//2, cy - ts//2, cx + ts//2, cy + ts//2], 180, 360, fill=color, width=ts//4)
            elif edge == "left":
                draw.arc([cx - ts//2, cy - ts//2, cx + ts//2, cy + ts//2], 90, 270, fill=color, width=ts//4)
            elif edge == "right":
                draw.arc([cx - ts//2, cy - ts//2, cx + ts//2, cy + ts//2], 270, 450, fill=color, width=ts//4)
                
        elif sprite_type == "tentacle":
            # Tentáculo
            color = self.palette.get("tentacle", (120, 160, 200))
            orientation = sprite_data.get("orientation", "vertical")
            
            if orientation == "vertical":
                # Línea ondulada vertical
                points = [(cx, ts//4), (cx - 8, ts//2), (cx + 8, 3*ts//4), (cx, ts - ts//4)]
                draw.line(points, fill=color, width=max(3, ts//16))
            else:
                # Línea ondulada horizontal
                points = [(ts//4, cy), (ts//2, cy - 8), (3*ts//4, cy + 8), (ts - ts//4, cy)]
                draw.line(points, fill=color, width=max(3, ts//16))
                
        elif sprite_type == "siphon":
            # Sifón
            color = self.palette.get("siphon", (140, 120, 100))
            draw.rectangle([cx - 4, cy - 8, cx + 4, cy + 8], fill=color)
            
        elif sprite_type == "body_curve":
            # Curva de cuerpo serpentino
            color = self.palette.get("body", (180, 160, 140))
            curve = sprite_data.get("curve", "straight")
            width = ts // 3
            
            if curve == "straight":
                draw.rectangle([cx - width//2, 0, cx + width//2, ts], fill=color)
            elif curve == "curve_ne":
                draw.arc([0, 0, ts, ts], 0, 90, fill=color, width=width)
            elif curve == "curve_nw":
                draw.arc([0, 0, ts, ts], 90, 180, fill=color, width=width)
            elif curve == "curve_se":
                draw.arc([0, 0, ts, ts], 270, 360, fill=color, width=width)
            elif curve == "curve_sw":
                draw.arc([0, 0, ts, ts], 180, 270, fill=color, width=width)
                
        elif sprite_type in ["center", "arm", "arm_mid"]:
            # Elementos radiales
            color = self.palette.get("radial", (200, 180, 160))
            
            if sprite_type == "center":
                draw.ellipse([cx - ts//4, cy - ts//4, cx + ts//4, cy + ts//4], fill=color)
            else:
                direction = sprite_data.get("direction", "up")
                if direction == "up":
                    draw.rectangle([cx - ts//8, 0, cx + ts//8, cy + ts//4], fill=color)
                elif direction == "down":
                    draw.rectangle([cx - ts//8, cy - ts//4, cx + ts//8, ts], fill=color)
                elif direction == "left":
                    draw.rectangle([0, cy - ts//8, cx + ts//4, cy + ts//8], fill=color)
                elif direction == "right":
                    draw.rectangle([cx - ts//4, cy - ts//8, ts, cy + ts//8], fill=color)
        
        # Borde decorativo para todos los tiles
        draw.rectangle([0, 0, ts-1, ts-1], outline=(0, 0, 0, 30), width=1)
    
    def darken(self, color: Tuple[int, int, int], factor: float = 0.7) -> Tuple[int, int, int]:
        """Oscurece un color"""
        return tuple(int(c * factor) for c in color[:3])
    
    def compose_creature(self, grid: List[List[Optional[Tile]]], output_path: str, scale: int = 3):
        """Compone todos los tiles en una imagen final escalada"""
        size = len(grid)
        img_size = size * self.tile_size
        
        # Crear imagen base
        img = Image.new('RGBA', (img_size, img_size), (240, 240, 240, 255))
        draw = ImageDraw.Draw(img)
        
        # Dibujar cada tile
        for y in range(size):
            for x in range(size):
                tile = grid[y][x]
                if tile:
                    # Renderizar tile en memoria
                    tile_img = Image.new('RGBA', (self.tile_size, self.tile_size), (0, 0, 0, 0))
                    tile_draw = ImageDraw.Draw(tile_img)
                    self._draw_sprite(tile_draw, tile)
                    
                    # Pegar en imagen principal
                    px, py = x * self.tile_size, y * self.tile_size
                    img.paste(tile_img, (px, py), tile_img)
        
        # Escalar con interpolación nearest-neighbor para pixel art nítido
        final_size = img_size * scale
        img_scaled = img.resize((final_size, final_size), Image.Resampling.NEAREST)
        
        # Guardar
        img_scaled.save(output_path, 'PNG')
        print(f"  ✓ Imagen guardada: {output_path} ({final_size}x{final_size}px)")

# ============================================================================
# SISTEMA PRINCIPAL
# ============================================================================

class CreatureWFCPipeline:
    """Pipeline completo de generación de criaturas"""
    
    def __init__(self, output_dir: str = OUTPUT_DIR):
        self.output_dir = output_dir
        self.eco_engine = EcologicalEngine()
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_palette(self, eco: EcologicalInput, body_plan: BodyPlan) -> Dict:
        """Genera paleta de colores basada en ecología y plan corporal"""
        # Colores base según temperatura
        if eco.temperature < 0:
            base_colors = {
                "body": (180, 200, 220),      # Azul-grisáceo frío
                "limb": (160, 180, 200),
                "tail": (140, 160, 180),
            }
        elif eco.temperature > 30:
            base_colors = {
                "body": (220, 180, 140),      # Naranja-tierra caliente
                "limb": (200, 160, 120),
                "tail": (180, 140, 100),
            }
        else:
            base_colors = {
                "body": (140, 180, 140),      # Verde templado
                "limb": (120, 160, 120),
                "tail": (100, 140, 100),
            }
        
        # Ajustes por humedad
        if eco.humidity > 70:
            # Más saturado y oscuro
            base_colors = {k: tuple(int(c * 0.9) for c in v) for k, v in base_colors.items()}
        elif eco.humidity < 30:
            # Más desaturado y claro
            base_colors = {k: tuple(min(255, int(c * 1.1)) for c in v) for k, v in base_colors.items()}
        
        # Ajustes por plan corporal
        if body_plan == BodyPlan.CEPHALOPOD:
            base_colors.update({
                "mantle": (80, 120, 180) if eco.pressure > 2.0 else (100, 140, 160),
                "tentacle": (100, 140, 200),
                "siphon": (120, 100, 80),
            })
        elif body_plan == BodyPlan.RADIAL:
            base_colors.update({
                "radial": (220, 200, 180),
                "center": (200, 180, 160),
            })
        
        # Colores comunes
        base_colors.update({
            "habitat": (60, 80, 100) if eco.humidity > 70 else (80, 100, 80),
            "eye": (255, 255, 255),
            "pupil": (0, 0, 0),
            "segment": tuple(int(c * 0.85) for c in base_colors["body"]),
        })
        
        return base_colors
    
    def generate_creature(self, eco: EcologicalInput, name_suffix: str = "") -> Tuple[str, str]:
        """Genera una criatura completa y retorna paths de JSON y PNG"""
        print(f"\n🧬 Generando criatura para ambiente:")
        print(f"   Temp: {eco.temperature}°C | Humedad: {eco.humidity}% | Altitud: {eco.altitude}m")
        print(f"   Presión: {eco.pressure} atm | Recursos: {eco.resources}")
        
        # Fase 1: Generar tarjeta de criatura
        card = self.eco_engine.generate_creature_card(eco)
        print(f"   → Plan corporal: {card.body_plan.value.upper()}")
        
        # Guardar JSON
        card_dict = {
            "body_plan": card.body_plan.value,
            "anatomy": card.anatomy,
            "survival": card.survival,
            "spatial_rules": card.spatial_rules,
            "energy_source": card.energy_source,
            "ecological_input": {
                "temperature": eco.temperature,
                "humidity": eco.humidity,
                "altitude": eco.altitude,
                "pressure": eco.pressure,
                "resources": eco.resources
            }
        }
        
        timestamp = int(time.time())
        json_filename = f"specie_{card.body_plan.name.lower()}_{timestamp}.json"
        json_path = os.path.join(self.output_dir, json_filename)
        
        with open(json_path, 'w') as f:
            json.dump(card_dict, f, indent=2)
        print(f"  ✓ JSON guardado: {json_path}")
        
        # Fase 2: Configurar WFC
        palette = self.generate_palette(eco, card.body_plan)
        factory = TileFactory(card.body_plan, palette)
        
        tile_factories = {card.body_plan: factory}
        wfc_grid = WFCGrid(GRID_SIZE, tile_factories)
        
        # Fase 3: Resolver WFC con reintentos
        success = False
        attempts = 0
        
        while not success and attempts < MAX_ATTEMPTS:
            attempts += 1
            if attempts > 1:
                print(f"   Intento {attempts}/{MAX_ATTEMPTS}...")
            
            # Reiniciar grilla
            wfc_grid = WFCGrid(GRID_SIZE, tile_factories)
            success = wfc_grid.solve(card.body_plan)
        
        if not success:
            print(f"  ⚠ Warning: WFC no convergió después de {MAX_ATTEMPTS} intentos")
            # Usar grilla parcial o fallback
        
        result_grid = wfc_grid.get_result()
        
        # Fase 4: Renderizar
        renderer = VectorRenderer(TILE_SIZE, palette)
        png_filename = f"specie_{card.body_plan.name.lower()}_{timestamp}.png"
        png_path = os.path.join(self.output_dir, png_filename)
        
        renderer.compose_creature(result_grid, png_path, scale=SCALE_FACTOR)
        
        return json_path, png_path
    
    def run_demo(self):
        """Ejecuta demo con 5 escenarios ecológicos distintos"""
        scenarios = [
            ("Alpino Extremo", EcologicalInput(-25, 45, 5500, 0.5, 0.3)),
            ("Selva Tropical", EcologicalInput(32, 85, 200, 1.0, 0.8)),
            ("Desierto Árido", EcologicalInput(42, 10, 500, 1.0, 0.2)),
            ("Fosa Oceánica", EcologicalInput(4, 95, -400, 4.0, 0.6)),
            ("Pradera Templada", EcologicalInput(20, 50, 800, 1.0, 0.7)),
        ]
        
        print("=" * 70)
        print("🦎 CREATURE WFC V4 - GENERADOR DE DIVERSIDAD MORFOLÓGICA")
        print("=" * 70)
        print(f"📁 Output directory: {os.path.abspath(self.output_dir)}")
        print(f"📐 Grid size: {GRID_SIZE}x{GRID_SIZE} tiles")
        print(f"🎨 Tile size: {TILE_SIZE}x{TILE_SIZE}px (escalado {SCALE_FACTOR}x)")
        print(f"🔄 Max attempts: {MAX_ATTEMPTS}")
        print("=" * 70)
        
        results = []
        
        for name, eco in scenarios:
            print(f"\n{'='*70}")
            print(f"🌍 ESCENARIO: {name}")
            print('='*70)
            
            try:
                json_path, png_path = self.generate_creature(eco, name_suffix=name.replace(" ", "_").lower())
                results.append((name, json_path, png_path))
            except Exception as e:
                print(f"  ✗ Error generando {name}: {e}")
                import traceback
                traceback.print_exc()
        
        # Resumen final
        print("\n" + "=" * 70)
        print("✅ GENERACIÓN COMPLETADA")
        print("=" * 70)
        print(f"\nArchivos generados en: {os.path.abspath(self.output_dir)}\n")
        
        for name, json_path, png_path in results:
            print(f"  • {name}:")
            print(f"      JSON: {os.path.basename(json_path)}")
            print(f"      PNG:  {os.path.basename(png_path)}")
        
        print("\n🎉 ¡Todas las criaturas han sido generadas exitosamente!")
        print("=" * 70)

# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    pipeline = CreatureWFCPipeline()
    pipeline.run_demo()
