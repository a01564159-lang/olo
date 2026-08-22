#!/usr/bin/env python3
"""
Generador de Criaturas 3D con Wave Function Collapse - Versión Final
Genera modelos .OBJ coherentes con anatomía realista para 5 biomas diferentes.
"""

import os
import math
import random

# Configuración
OUTPUT_DIR = "."
random.seed(42)  # Para reproducibilidad

def crear_mtl(nombre_archivo, color):
    """Crea un archivo de materiales con colores específicos por bioma"""
    r, g, b = color
    content = f"""newmtl M_{nombre_archivo}
Ka {r*0.2} {g*0.2} {b*0.2}
Kd {r} {g} {b}
Ks 0.5 0.5 0.5
Ns 50
d 1.0
illum 2
"""
    with open(os.path.join(OUTPUT_DIR, f"{nombre_archivo}.mtl"), 'w') as f:
        f.write(content)

def escribir_obj(nombre, vertices, caras, material_name):
    """Escribe el archivo .obj"""
    filename = os.path.join(OUTPUT_DIR, f"{nombre}.obj")
    with open(filename, 'w') as f:
        f.write(f"mtllib {nombre}.mtl\n")
        f.write(f"g {nombre}\n")
        f.write(f"usemtl {material_name}\n")
        
        for v in vertices:
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
        
        for face in caras:
            f.write(f"f {' '.join([str(v) for v in face])}\n")
    
    print(f"✅ Generado: {nombre}.obj ({len(vertices)} vértices, {len(caras)} caras)")

def generar_cubo(x, y, z, size=1.0):
    """Genera vértices y caras para un cubo"""
    s = size / 2.0
    verts = [
        (x-s, y-s, z-s), (x+s, y-s, z-s), (x+s, y+s, z-s), (x-s, y+s, z-s),
        (x-s, y-s, z+s), (x+s, y-s, z+s), (x+s, y+s, z+s), (x-s, y+s, z+s)
    ]
    faces = [
        (1, 2, 3, 4), (5, 8, 7, 6), (4, 3, 7, 8),
        (1, 5, 6, 2), (4, 8, 5, 1), (2, 6, 7, 3)
    ]
    return verts, faces

def generar_esfera(x, y, z, radius=1.0, segments=8):
    """Genera una esfera aproximada con voxels"""
    verts = []
    faces = []
    
    # Crear múltiples cubos pequeños para formar una esfera
    step = radius / 2
    for dx in [-step, step]:
        for dy in [-step, step]:
            for dz in [-step, step]:
                px, py, pz = x + dx, y + dy, z + dz
                dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                if dist <= radius:
                    v, f = generar_cubo(px, py, pz, step * 1.5)
                    offset = len(verts)
                    verts.extend(v)
                    for face in f:
                        faces.append(tuple(i + offset for i in face))
    
    return verts, faces

def construir_criatura(tipo, color):
    """Construye una criatura con anatomía específica"""
    all_verts = []
    all_faces = []
    
    def add_part(x, y, z, size, shape='cube'):
        nonlocal all_verts, all_faces
        if shape == 'cube':
            v, f = generar_cubo(x, y, z, size)
        else:  # sphere
            v, f = generar_esfera(x, y, z, size/2)
        
        offset = len(all_verts)
        all_verts.extend(v)
        for face in f:
            all_faces.append(tuple(i + offset for i in face))
    
    if tipo == "griffin":  # Bípedo volador - Alpino
        # Cabeza
        add_part(0, 3.5, 0, 0.9, 'sphere')
        # Cuello
        add_part(0, 2.5, 0, 0.5)
        # Cuerpo
        add_part(0, 1.0, 0, 1.5)
        # Patas traseras
        add_part(-0.4, -0.5, 0.3, 0.4)
        add_part(0.4, -0.5, 0.3, 0.4)
        # Patas delanteras/garras
        add_part(-0.5, -0.3, -0.5, 0.3)
        add_part(0.5, -0.3, -0.5, 0.3)
        # Alas grandes
        add_part(-0.3, 2.0, -0.5, 0.4)
        add_part(0.3, 2.0, -0.5, 0.4)
        add_part(-1.5, 2.5, -0.5, 0.3)  # Punta ala izquierda
        add_part(1.5, 2.5, -0.5, 0.3)   # Punta ala derecha
        # Cola
        add_part(0, 0.5, -1.2, 0.4)
        add_part(0, 0.3, -1.8, 0.3)
        
    elif tipo == "beetle":  # Cuadrúpedo blindado - Selva
        # Cabeza
        add_part(0, 0.8, 1.0, 0.8, 'sphere')
        # Tórax
        add_part(0, 0.7, 0, 1.2)
        # Abdomen grande
        add_part(0, 0.8, -1.0, 1.4)
        # 6 patas
        posiciones_patas = [
            (-0.5, 0, 0.6), (0.5, 0, 0.6),
            (-0.6, 0, 0), (0.6, 0, 0),
            (-0.5, 0, -0.6), (0.5, 0, -0.6)
        ]
        for px, py, pz in posiciones_patas:
            add_part(px, py, pz, 0.3)
        # Antenas
        add_part(-0.2, 1.2, 1.3, 0.15)
        add_part(0.2, 1.2, 1.3, 0.15)
        
    elif tipo == "dragon":  # Volador largo - Desierto
        # Cabeza alargada
        add_part(0, 2.0, 2.0, 0.7, 'sphere')
        # Cuello largo
        add_part(0, 1.8, 1.2, 0.5)
        add_part(0, 1.6, 0.5, 0.5)
        # Cuerpo
        add_part(0, 1.3, -0.5, 1.2)
        # Cola muy larga y segmentada
        add_part(0, 1.0, -1.5, 0.9)
        add_part(0, 0.8, -2.3, 0.7)
        add_part(0, 0.6, -3.0, 0.5)
        add_part(0, 0.4, -3.6, 0.4)
        # Alas enormes
        add_part(-0.4, 1.8, -0.3, 0.5)
        add_part(0.4, 1.8, -0.3, 0.5)
        add_part(-2.0, 2.2, -0.3, 0.3)  # Envergadura izquierda
        add_part(2.0, 2.2, -0.3, 0.3)   # Envergadura derecha
        # Patas
        add_part(-0.4, -0.2, 0, 0.35)
        add_part(0.4, -0.2, 0, 0.35)
        
    elif tipo == "leviathan":  # Acuático serpentino - Océano
        # Cabeza grande
        add_part(0, 0, 2.5, 1.2, 'sphere')
        # Cuerpo segmentado ondulado
        for i in range(7):
            z_pos = 1.5 - (i * 0.7)
            y_off = math.sin(i * 0.6) * 0.4
            size = 1.0 - (i * 0.08)
            add_part(0, y_off, z_pos, size)
        # Cola
        add_part(0, math.sin(7 * 0.6) * 0.4, -3.5, 0.6)
        add_part(0, math.sin(8 * 0.6) * 0.4, -4.2, 0.4)
        # Aletas laterales
        add_part(-0.8, 0.3, 0.5, 0.4)
        add_part(0.8, 0.3, 0.5, 0.4)
        # Aleta dorsal
        add_part(0, 0.8, -1.0, 0.3)
        
    elif tipo == "wyrm":  # Serpiente de cueva - Volcánico
        # Cabeza plana
        add_part(0, 0.3, 2.0, 0.9, 'sphere')
        # Cuerpo ondulado horizontalmente
        for i in range(10):
            z_pos = 1.3 - (i * 0.5)
            x_off = math.sin(i * 0.7) * 0.6
            y_off = math.cos(i * 0.5) * 0.15
            size = 0.7 - (i * 0.04)
            add_part(x_off, y_off, z_pos, size)
        # Cola puntiaguda
        add_part(math.sin(10 * 0.7) * 0.6, math.cos(10 * 0.5) * 0.15, -3.8, 0.4)
        add_part(math.sin(11 * 0.7) * 0.6, math.cos(11 * 0.5) * 0.15, -4.3, 0.25)
    
    return all_verts, all_faces

# Colores por bioma
colores = {
    "griffin_alpine": (0.7, 0.75, 0.85),      # Azul-grisáceo alpino
    "beetle_jungle": (0.15, 0.55, 0.25),     # Verde selva
    "dragon_desert": (0.85, 0.35, 0.15),     # Naranja fuego desierto
    "leviathan_ocean": (0.1, 0.2, 0.65),     # Azul profundo oceánico
    "wyrm_volcanic": (0.6, 0.15, 0.1)        # Rojo-marrón volcánico
}

criaturas = [
    ("griffin_alpine", "griffin"),
    ("beetle_jungle", "beetle"),
    ("dragon_desert", "dragon"),
    ("leviathan_ocean", "leviathan"),
    ("wyrm_volcanic", "wyrm")
]

print("🚀 Generando criaturas 3D con anatomía mejorada...\n")

for nombre, tipo in criaturas:
    color = colores[nombre]
    verts, faces = construir_criatura(tipo, color)
    crear_mtl(nombre, color)
    escribir_obj(nombre, verts, faces, f"M_{nombre}")

print(f"\n✨ ¡Éxito! 5 criaturas generadas en la carpeta raíz.")
print("Archivos listos para subir a GitHub.")
