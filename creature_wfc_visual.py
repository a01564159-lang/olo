#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIPELINE DE GENERACIÓN DE CRIATURAS: WFC VISUAL (PIXEL ART)
----------------------------------------------------------
Autor: Senior Procedural Architect
Descripción: 
    Genera criaturas procedurales basadas en 5 variables ecológicas,
    utiliza Wave Function Collapse (WFC) para ensamblar tiles de pixel art
    y exporta el resultado a imágenes PNG reales.

Requisitos:
    pip install pillow
"""

import random
import math
import json
import os
from PIL import Image, ImageDraw, ImageEnhance

# ==============================================================================
# CONFIGURACIÓN GLOBAL
# ==============================================================================
TILE_SIZE = 16  # Tamaño de cada tile en píxeles (resolución base)
GRID_W, GRID_H = 12, 12  # Tamaño de la grilla lógica WFC
OUTPUT_SCALE = 4  # Escala final para ver el pixel art (16x4 = 64px por tile)
PALETTE = {
    'void': (0, 0, 0, 0),          # Transparente
    'skin_cold': (100, 149, 237),  # Azul cornflower (frío)
    'skin_hot': (205, 92, 92),     # Rojo indio (calor)
    'skin_humid': (34, 139, 34),   # Verde bosque (húmedo)
    'skin_dry': (210, 180, 140),   # Tan (seco)
    'armor': (128, 128, 128),      # Gris piedra
    'glow': (255, 215, 0),         # Dorado (órganos/bio-luz)
    'bone': (245, 245, 220),       # Blanco hueso
    'eye': (255, 0, 0),            # Rojo ojo
}

# ==============================================================================
# FASE 0: GENERADOR DE ASSETS (TILES PROCEDURALES)
# ==============================================================================
class TileFactory:
    """Genera dinámicamente los tiles de pixel art basados en el bioma."""
    
    def __init__(self, eco_profile):
        self.eco = eco_profile
        self.tiles = {}
        self._generate_tileset()

    def _get_skin_color(self):
        """Determina el color de piel dominante según las 5 variables."""
        t = self.eco['temperature']
        h = self.eco['humidity']
        
        if t < 10: return PALETTE['skin_cold']
        if t > 35: return PALETTE['skin_hot']
        if h > 70: return PALETTE['skin_humid']
        return PALETTE['skin_dry']

    def _draw_pixel(self, img, x, y, color):
        if 0 <= x < TILE_SIZE and 0 <= y < TILE_SIZE:
            img.putpixel((x, y), color)

    def _draw_shape_circle(self, draw, color, scale=1.0):
        center = TILE_SIZE // 2
        radius = int((TILE_SIZE // 2 - 1) * scale)
        draw.ellipse([center-radius, center-radius, center+radius, center+radius], fill=color)

    def _add_noise(self, img, intensity=20):
        """Añade ruido visual para textura orgánica."""
        pixels = img.load()
        for i in range(img.width):
            for j in range(img.height):
                if random.random() < 0.3:
                    rgba = pixels[i, j]
                    r, g, b = rgba[0], rgba[1], rgba[2]
                    a = rgba[3] if len(rgba) > 3 else 255
                    noise = random.randint(-intensity, intensity)
                    pixels[i, j] = (max(0, min(255, r+noise)), 
                                    max(0, min(255, g+noise)), 
                                    max(0, min(255, b+noise)),
                                    a)

    def _generate_tileset(self):
        skin_color = self._get_skin_color()
        armor_color = PALETTE['armor']
        glow_color = PALETTE['glow']
        
        # Determinar características visuales basadas en la tarjeta
        has_armor = self.eco.get('anatomy', {}).get('armor_level', 0) > 5
        is_bio_luminescent = self.eco.get('survival', {}).get('energy_source') == 'quimiosintesis' or self.eco['pressure'] > 80

        base_types = ['center', 'head', 'tail', 'limb_up', 'limb_down', 'limb_left', 'limb_right', 'joint', 'empty']
        
        for btype in base_types:
            img = Image.new('RGBA', (TILE_SIZE, TILE_SIZE), (0,0,0,0))
            draw = ImageDraw.Draw(img)
            
            # Lógica de dibujo procedural simple pero efectiva
            if btype == 'center':
                self._draw_shape_circle(draw, skin_color, 0.9)
                if has_armor:
                    self._draw_shape_circle(draw, armor_color, 0.5)
                if is_bio_luminescent:
                    self._draw_shape_circle(draw, glow_color, 0.2)
            
            elif btype == 'head':
                # Forma asimétrica para indicar dirección
                draw.polygon([(2,2), (14,8), (2,14)], fill=skin_color)
                draw.point((10, 6), fill=PALETTE['eye'])
                draw.point((10, 10), fill=PALETTE['eye'])
                if has_armor:
                    draw.arc([4, 4, 10, 10], 0, 180, fill=armor_color, width=2)

            elif btype == 'tail':
                draw.polygon([(2,4), (14,8), (2,12)], fill=skin_color)
                if is_bio_luminescent:
                    draw.line([(10,8), (14,8)], fill=glow_color, width=2)

            elif 'limb' in btype:
                color = armor_color if has_armor else skin_color
                if btype == 'limb_up':
                    draw.rectangle([6, 2, 10, 10], fill=color)
                elif btype == 'limb_down':
                    draw.rectangle([6, 6, 10, 14], fill=color)
                elif btype == 'limb_left':
                    draw.rectangle([2, 6, 10, 10], fill=color)
                elif btype == 'limb_right':
                    draw.rectangle([6, 6, 14, 10], fill=color)
            
            elif btype == 'joint':
                self._draw_shape_circle(draw, armor_color if has_armor else skin_color, 0.4)
            
            elif btype == 'empty':
                # Ruido ambiental sutil
                if random.random() > 0.8:
                    self._draw_pixel(img, random.randint(0,15), random.randint(0,15), (50,50,50, 50))

            # Aplicar textura
            self._add_noise(img)
            self.tiles[btype] = img

    def get_tile(self, name):
        return self.tiles.get(name, self.tiles['empty'])

# ==============================================================================
# FASE 1: MOTOR ECOLÓGICO (Generador de Tarjetas)
# ==============================================================================
def generate_creature_card(temp, humidity, altitude, pressure, resources):
    """
    Calcula la biología de la criatura basada en 5 inputs.
    Retorna un diccionario (JSON-like) con la definición.
    """
    card = {
        "inputs": {"temp": temp, "humidity": humidity, "altitude": altitude, "pressure": pressure, "resources": resources},
        "temperature": temp,  # Necesario para TileFactory
        "humidity": humidity, # Necesario para TileFactory
        "pressure": pressure, # Necesario para TileFactory
        "anatomy": {},
        "survival": {},
        "wfc_rules": {}
    }

    # 1. Anatomía Adaptativa
    limbs = 6 if altitude > 3000 else (4 if temp > 20 else 8) # Más patas en altura o calor extremo
    armor = min(10, max(0, (100 - humidity) / 5 + (resources / 10))) # Más armadura si es seco y hay minerales
    
    card["anatomy"] = {
        "limb_count": limbs,
        "armor_level": armor,
        "size_class": "gigante" if pressure > 90 else "pequeño" if altitude > 4000 else "mediano"
    }

    # 2. Supervivencia
    energy = "fotosintesis" if humidity > 60 and temp > 15 else "carnivoro" if temp > 10 else "quimiosintesis"
    tolerance = "extrema" if abs(temp - 25) > 20 or pressure > 80 else "estandar"
    
    card["survival"] = {
        "energy_source": energy,
        "climate_tolerance": tolerance,
        "metabolism": "lento" if temp < 5 else "rapido"
    }

    # 3. Reglas WFC (Probabilidades de aparición de tiles)
    # Esto define cómo el WFC construirá la forma
    weights = {
        "center": 1.0,
        "head": 0.2,
        "tail": 0.2,
        "limb_up": limbs / 10.0,
        "limb_down": limbs / 10.0,
        "limb_left": limbs / 10.0,
        "limb_right": limbs / 10.0,
        "joint": 0.5,
        "empty": 0.1
    }
    
    # Ajustes por entorno
    if pressure > 80: # Profundidad: formas más compactas
        weights["limb_up"] *= 0.5
        weights["limb_down"] *= 0.5
        weights["center"] *= 1.5
    
    card["wfc_rules"] = {
        "weights": weights,
        "adjacency": {
            "center": ["head", "tail", "limb_up", "limb_down", "limb_left", "limb_right", "joint", "center"],
            "head": ["center", "joint"],
            "tail": ["center", "joint"],
            "limb_up": ["center", "joint"],
            "limb_down": ["center", "joint"],
            "joint": ["center", "head", "tail", "limb_up", "limb_down", "limb_left", "limb_right", "joint"],
            "empty": ["empty", "center", "tail"] # El vacío puede tocar bordes o colas
        }
    }

    return card

# ==============================================================================
# FASE 2: WFC ENGINE (Motor de Colapso de Ondas)
# ==============================================================================
class WFC_Engine:
    def __init__(self, width, height, rules, weights):
        self.width = width
        self.height = height
        self.rules = rules
        self.weights = weights
        
        # Inicializar entropía: cada celda puede ser cualquier tile al inicio
        self.grid = [[set(weights.keys()) for _ in range(width)] for _ in range(height)]
        self.final_grid = [[None for _ in range(width)] for _ in range(height)]
        
    def get_entropy(self, x, y):
        if self.final_grid[y][x] is not None:
            return 0
        return len(self.grid[y][x])

    def find_lowest_entropy_cell(self):
        min_entropy = float('inf')
        candidates = []
        
        for y in range(self.height):
            for x in range(self.width):
                if self.final_grid[y][x] is None:
                    ent = len(self.grid[y][x])
                    if ent < min_entropy:
                        min_entropy = ent
                        candidates = [(x, y)]
                    elif ent == min_entropy:
                        candidates.append((x, y))
        
        if not candidates:
            return None
        return random.choice(candidates)

    def collapse_cell(self, x, y):
        possibilities = list(self.grid[y][x])
        if not possibilities:
            return False # Contradicción (en una implementación completa, haríamos backtrack)
        
        # Ponderar selección
        total_weight = sum(self.weights[p] for p in possibilities)
        r = random.uniform(0, total_weight)
        cumulative = 0
        selected = possibilities[0]
        
        for p in possibilities:
            cumulative += self.weights[p]
            if r <= cumulative:
                selected = p
                break
        
        self.final_grid[y][x] = selected
        
        # Propagar restricciones a vecinos
        neighbors = [
            (x, y-1, 'limb_down'), (x, y+1, 'limb_up'),
            (x-1, y, 'limb_right'), (x+1, y, 'limb_left')
        ]
        
        for nx, ny, direction in neighbors:
            if 0 <= nx < self.width and 0 <= ny < self.height and self.final_grid[ny][nx] is None:
                allowed = self.rules.get(selected, [])
                # Filtrar posibilidades del vecino
                old_len = len(self.grid[ny][nx])
                self.grid[ny][nx] = self.grid[ny][nx].intersection(set(allowed))
                
                # Si se vació, forzamos un colapso seguro (fallback simple para evitar crash)
                if not self.grid[ny][nx]:
                    self.grid[ny][nx] = {'empty'} 

        return True

    def run(self, max_iterations=200):
        for _ in range(max_iterations):
            cell = self.find_lowest_entropy_cell()
            if cell is None:
                break # Terminado
            
            x, y = cell
            if not self.collapse_cell(x, y):
                # Reinicio parcial si hay contradicción grave (simplificado)
                pass 
        return self.final_grid

# ==============================================================================
# FASE 3: RENDERIZADO Y EXPORTACIÓN
# ==============================================================================
def render_to_image(grid, tile_factory, filename_base):
    w = len(grid[0])
    h = len(grid)
    
    # Crear imagen final
    final_img = Image.new('RGBA', (w * TILE_SIZE, h * TILE_SIZE), (0, 0, 0, 0))
    
    for y in range(h):
        for x in range(w):
            tile_name = grid[y][x]
            tile_img = tile_factory.get_tile(tile_name)
            final_img.paste(tile_img, (x * TILE_SIZE, y * TILE_SIZE))
    
    # Guardar versión base
    final_img.save(f"{filename_base}.png")
    
    # Escalar para estilo Pixel Art nítido (Nearest Neighbor)
    scaled_img = final_img.resize(
        (w * TILE_SIZE * OUTPUT_SCALE, h * TILE_SIZE * OUTPUT_SCALE), 
        resample=Image.NEAREST
    )
    scaled_img.save(f"{filename_base}_2x.png")
    
    print(f"✅ Imagen generada: {filename_base}.png ({w}x{h} tiles)")
    print(f"✅ Imagen escalada: {filename_base}_2x.png (Listo para usar)")

# ==============================================================================
# MAIN PIPELINE
# ==============================================================================
def main():
    print("🧬 INICIANDO PIPELINE DE DISEÑO DE CRIATURAS (WFC VISUAL)")
    print("="*50)
    
    # 1. Definir Ambientes de Prueba (Las 5 variables)
    environments = [
        {"name": "Alpino_Extremo", "temp": -10, "hum": 30, "alt": 5000, "pres": 50, "res": 20},
        {"name": "Selva_Tropical", "temp": 32, "hum": 90, "alt": 200, "pres": 100, "res": 80},
        {"name": "Deserto_Arido", "temp": 45, "hum": 10, "alt": 100, "pres": 98, "res": 60},
        {"name": "Fosa_Oceanica", "temp": 4, "hum": 100, "alt": -4000, "pres": 99, "res": 30}
    ]
    
    for env in environments:
        print(f"\n🌍 Generando criatura para: {env['name']}...")
        print(f"   Variables: T={env['temp']}°C, H={env['hum']}%, Alt={env['alt']}m")
        
        # Fase 1: Tarjeta Ecológica
        card = generate_creature_card(
            env['temp'], env['hum'], env['alt'], env['pres'], env['res']
        )
        
        # Guardar JSON de la tarjeta para referencia
        with open(f"card_{env['name']}.json", 'w') as f:
            json.dump(card, f, indent=2)
            
        # Fase 2: Preparar WFC
        factory = TileFactory(card)
        wfc = WFC_Engine(
            GRID_W, GRID_H, 
            card['wfc_rules']['adjacency'], 
            card['wfc_rules']['weights']
        )
        
        # Ejecutar WFC
        grid_result = wfc.run()
        
        # Fase 3: Renderizar
        render_to_image(grid_result, factory, f"creature_{env['name']}")
        
        # Resumen biológico
        print(f"   👉 Anatomía: {card['anatomy']['limb_count']} extremidades, Armadura {card['anatomy']['armor_level']}/10")
        print(f"   👉 Energía: {card['survival']['energy_source']}")

    print("\n🎉 PROCESO COMPLETADO. Revisa los archivos PNG generados.")

if __name__ == "__main__":
    try:
        main()
    except ImportError:
        print("❌ Error: Necesitas instalar Pillow. Ejecuta: pip install pillow")
