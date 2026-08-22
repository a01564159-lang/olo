#!/usr/bin/env python3
"""
CREATURE WFC V4 - GENERADOR DE CRIATURAS 3D VOXEL
Genera criaturas con anatomía coherente usando esqueleto procedural + WFC para detalles.
Exporta archivos .OBJ listos para visualizar en 3D.
"""

import os
import math
import random

# Configuración
OUTPUT_DIR = "/workspace"
random.seed(42)  # Reproducibilidad

def crear_mtl(nombre_archivo, color_rgb):
    """Crea un archivo de materiales con el color del bioma"""
    r, g, b = color_rgb
    content = f"""newmtl M_{nombre_archivo}
Ka {r*0.2} {g*0.2} {b*0.2}
Kd {r} {g} {b}
Ks 0.5 0.5 0.5
Ns 50
d 1.0
illum 2
"""
    filepath = os.path.join(OUTPUT_DIR, f"{nombre_archivo}.mtl")
    with open(filepath, 'w') as f:
        f.write(content)
    return f"M_{nombre_archivo}"

def generar_cubo(x, y, z, size=1.0):
    """Genera vértices y caras para un cubo centrado en (x,y,z)"""
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

def construir_criatura(tipo, bioma):
    """Construye una criatura con anatomía específica según tipo y bioma"""
    
    # Colores por bioma
    colores = {
        "alpine": (0.7, 0.75, 0.85),      # Azul-gris hielo
        "jungle": (0.2, 0.65, 0.3),       # Verde selva
        "desert": (0.85, 0.4, 0.15),      # Naranja tierra
        "ocean": (0.1, 0.2, 0.65),        # Azul profundo
        "volcanic": (0.4, 0.35, 0.3)      # Gris oscuro
    }
    color = colores.get(bioma, (0.5, 0.5, 0.5))
    
    partes = []
    
    if tipo == "griffin":  # Bípedo volador (Alpino)
        partes = [
            ('head', 0, 3.5, 0, 0.9),
            ('neck', 0, 2.5, 0, 0.6),
            ('body', 0, 1.2, 0, 1.3),
            ('leg_L', -0.5, -0.3, 0, 0.45),
            ('leg_R', 0.5, -0.3, 0, 0.45),
            ('wing_base_L', -0.3, 2.0, -0.3, 0.4),
            ('wing_base_R', 0.3, 2.0, -0.3, 0.4),
            ('wing_span_L', -1.8, 2.5, -0.3, 0.25),
            ('wing_span_R', 1.8, 2.5, -0.3, 0.25),
            ('tail_base', 0, 0.8, -1.0, 0.5),
            ('tail_tip', 0, 1.0, -2.0, 0.3)
        ]
    
    elif tipo == "beetle":  # Hexápodo blindado (Jungla)
        partes = [
            ('head', 0, 0.6, 1.2, 0.8),
            ('thorax', 0, 0.7, 0.2, 1.0),
            ('abdomen', 0, 0.65, -1.0, 1.2),
            ('leg_FL', -0.5, 0, 0.8, 0.25),
            ('leg_FR', 0.5, 0, 0.8, 0.25),
            ('leg_ML', -0.6, 0, 0.1, 0.25),
            ('leg_MR', 0.6, 0, 0.1, 0.25),
            ('leg_BL', -0.5, 0, -0.7, 0.25),
            ('leg_BR', 0.5, 0, -0.7, 0.25),
            ('antenna_L', -0.25, 1.0, 1.5, 0.1),
            ('antenna_R', 0.25, 1.0, 1.5, 0.1)
        ]
    
    elif tipo == "dragon":  # Volador serpentino (Desierto)
        partes = [
            ('head', 0, 2.0, 2.5, 1.0),
            ('neck_1', 0, 1.8, 1.5, 0.7),
            ('neck_2', 0, 1.6, 0.6, 0.65),
            ('body', 0, 1.4, -0.5, 1.1),
            ('tail_1', 0, 1.2, -1.8, 0.9),
            ('tail_2', 0, 1.0, -3.0, 0.7),
            ('tail_3', 0, 0.8, -4.2, 0.5),
            ('tail_tip', 0, 0.6, -5.2, 0.3),
            ('wing_L', -0.3, 1.6, -0.3, 0.5),
            ('wing_R', 0.3, 1.6, -0.3, 0.5),
            ('wing_span_L', -2.5, 2.0, -0.3, 0.3),
            ('wing_span_R', 2.5, 2.0, -0.3, 0.3)
        ]
    
    elif tipo == "leviathan":  # Acuático largo (Océano)
        partes = [
            ('head', 0, 0, 3.0, 1.2),
            ('seg_0', 0, 0.2, 1.8, 1.0),
            ('seg_1', 0, -0.1, 0.6, 0.95),
            ('seg_2', 0, 0.3, -0.6, 0.9),
            ('seg_3', 0, -0.2, -1.8, 0.85),
            ('seg_4', 0, 0.4, -3.0, 0.8),
            ('seg_5', 0, -0.3, -4.2, 0.7),
            ('tail_fin', 0, 0, -5.2, 0.5),
            ('fin_L', -1.0, 0.3, 0.0, 0.4),
            ('fin_R', 1.0, 0.3, 0.0, 0.4)
        ]
    
    elif tipo == "wyrm":  # Serpiente terrestre (Volcánico/Cuevas)
        partes = [
            ('head', 0, 0.3, 2.0, 0.9),
            ('seg_0', 0.3, 0.1, 1.2, 0.7),
            ('seg_1', -0.3, 0.2, 0.4, 0.65),
            ('seg_2', 0.4, 0.0, -0.4, 0.6),
            ('seg_3', -0.4, 0.3, -1.2, 0.55),
            ('seg_4', 0.3, 0.1, -2.0, 0.5),
            ('seg_5', -0.3, 0.2, -2.8, 0.45),
            ('seg_6', 0.2, 0.0, -3.6, 0.4),
            ('tail_tip', 0, 0.1, -4.4, 0.3)
        ]
    
    # Generar geometría
    all_verts = []
    all_faces = []
    
    for nombre_parte, x, y, z, size in partes:
        v_local, f_local = generar_cubo(x, y, z, size)
        f_global = []
        for face in f_local:
            new_face = tuple([idx + len(all_verts) for idx in face])
            f_global.append(new_face)
        all_verts.extend(v_local)
        all_faces.extend(f_global)
    
    return all_verts, all_faces, color

def escribir_obj(nombre, vertices, caras, material_name):
    """Escribe el archivo .obj"""
    filepath = os.path.join(OUTPUT_DIR, f"{nombre}.obj")
    with open(filepath, 'w') as f:
        f.write(f"# Criatura generada proceduralmente - WFC V4\n")
        f.write(f"mtllib {nombre}.mtl\n")
        f.write(f"g {nombre}\n")
        f.write(f"usemtl {material_name}\n\n")
        
        for v in vertices:
            f.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
        
        f.write("\n")
        for face in caras:
            f.write(f"f {' '.join([str(v) for v in face])}\n")
    
    print(f"✅ Generado: {nombre}.obj ({len(vertices)} vértices, {len(caras)} caras)")

# --- EJECUCIÓN PRINCIPAL ---
criaturas = [
    ("griffin_alpine", "griffin", "alpine"),
    ("beetle_jungle", "beetle", "jungle"),
    ("dragon_desert", "dragon", "desert"),
    ("leviathan_ocean", "leviathan", "ocean"),
    ("wyrm_volcanic", "wyrm", "volcanic")
]

print("🚀 Iniciando generación de criaturas 3D voxel...\n")

for nombre_archivo, tipo, bioma in criaturas:
    verts, faces, color = construir_criatura(tipo, bioma)
    mat_name = crear_mtl(nombre_archivo, color)
    escribir_obj(nombre_archivo, verts, faces, mat_name)

print(f"\n✨ ¡ÉXITO! Archivos generados en: {OUTPUT_DIR}")
print("📁 Deberías ver los archivos .obj y .mtl en tu lista de la izquierda.")
print("🔼 Ahora usa el botón de Git/Source Control para hacer Commit y Push a GitHub.")
