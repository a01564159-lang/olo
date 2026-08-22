import os
import math
import random

# Configuración
OUTPUT_DIR = "criaturas_3d_v5"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generar_cubo(x, y, z, size):
    """Genera vértices y caras para un cubo centrado en (x,y,z)"""
    s = size / 2.0
    verts = [
        (x-s, y-s, z-s), (x+s, y-s, z-s), (x+s, y+s, z-s), (x-s, y+s, z-s),
        (x-s, y-s, z+s), (x+s, y-s, z+s), (x+s, y+s, z+s), (x-s, y+s, z+s)
    ]
    # Caras ordenadas correctamente para normales exteriores
    faces = [
        (1, 2, 3, 4), (5, 8, 7, 6), # Front, Back
        (4, 3, 7, 8), (1, 5, 6, 2), # Right, Left
        (3, 2, 6, 7), (1, 4, 8, 5)  # Top, Bottom
    ]
    return verts, faces

def construir_esqueleto(tipo):
    """Define la estructura ósea básica según el tipo de criatura"""
    partes = []
    
    if tipo == "bipedo": # Humanoide/Griffin
        # Cabeza, Torso, 2 Brazos, 2 Patas
        partes = [
            ('cabeza', 0, 1.8, 0, 0.5),
            ('torso', 0, 0.8, 0, 0.7),
            ('brazo_izq', -0.6, 1.2, 0, 0.25),
            ('brazo_der', 0.6, 1.2, 0, 0.25),
            ('antebrazo_izq', -0.9, 0.8, 0, 0.2),
            ('antebrazo_der', 0.9, 0.8, 0, 0.2),
            ('pierna_izq', -0.3, -0.4, 0, 0.3),
            ('pierna_der', 0.3, -0.4, 0, 0.3),
            ('pie_izq', -0.3, -0.9, 0.2, 0.25),
            ('pie_der', 0.3, -0.9, 0.2, 0.25),
        ]
    elif tipo == "cuadrupedo": # Lobo/Escarabajo
        # Cabeza, Cuerpo largo, 4 patas, cola
        partes = [
            ('cabeza', 0, 0.6, 1.2, 0.6),
            ('cuerpo', 0, 0.5, 0, 0.8),
            ('cadera', 0, 0.5, -0.8, 0.6),
            ('pata_del_izq', -0.4, 0.2, 0.8, 0.2),
            ('pata_del_der', 0.4, 0.2, 0.8, 0.2),
            ('pata_tra_izq', -0.4, 0.2, -0.6, 0.25),
            ('pata_tra_der', 0.4, 0.2, -0.6, 0.25),
            ('cola_1', 0, 0.4, -1.4, 0.3),
            ('cola_2', 0, 0.3, -1.9, 0.2),
        ]
    elif tipo == "serpentino": # Dragón sin patas
        # Cabeza + muchos segmentos
        partes = [('cabeza', 0, 0.5, 2.0, 0.7)]
        for i in range(8):
            z = 1.2 - (i * 0.4)
            y = math.sin(i * 0.5) * 0.3
            sz = 0.6 - (i * 0.05)
            partes.append((f'seg_{i}', 0, y, z, sz))
        # Alas pequeñas
        partes.extend([
            ('ala_izq', -0.3, 0.8, 1.0, 0.2),
            ('ala_der', 0.3, 0.8, 1.0, 0.2),
            ('ala_ext_izq', -1.0, 1.0, 1.0, 0.1),
            ('ala_ext_der', 1.0, 1.0, 1.0, 0.1),
        ])
    elif tipo == "volador": # Ave gigante
        partes = [
            ('cabeza', 0, 1.5, 0.5, 0.5),
            ('cuerpo', 0, 1.0, -0.2, 0.6),
            ('ala_grande_izq', -0.2, 1.2, -0.2, 0.3),
            ('ala_grande_der', 0.2, 1.2, -0.2, 0.3),
            ('pluma_1_izq', -0.8, 1.5, -0.2, 0.1),
            ('pluma_2_izq', -1.2, 1.3, -0.2, 0.1),
            ('pluma_1_der', 0.8, 1.5, -0.2, 0.1),
            ('pluma_2_der', 1.2, 1.3, -0.2, 0.1),
            ('pata_izq', -0.2, -0.2, 0, 0.15),
            ('pata_der', 0.2, -0.2, 0, 0.15),
        ]
    elif tipo == "acuatico": # Leviatán
        partes = [('cabeza', 0, 0, 2.5, 0.9)]
        for i in range(6):
            z = 1.5 - (i * 0.5)
            y = math.cos(i * 0.4) * 0.4
            partes.append((f'seg_{i}', 0, y, z, 0.7))
        # Aletas laterales
        partes.extend([
            ('aleta_izq', -0.6, 0.2, 0.5, 0.3),
            ('aleta_der', 0.6, 0.2, 0.5, 0.3),
            ('aleta_caudal', 0, 0.5, -1.5, 0.4),
        ])
        
    return partes

def guardar_obj(nombre, partes, color):
    vertices = []
    caras = []
    
    for _, x, y, z, size in partes:
        v_local, f_local = generar_cubo(x, y, z, size)
        offset = len(vertices)
        vertices.extend(v_local)
        for face in f_local:
            caras.append(tuple(i + offset for i in face))
    
    # Escribir MTL
    mtl_name = f"mat_{nombre}"
    with open(os.path.join(OUTPUT_DIR, f"{nombre}.mtl"), 'w') as f:
        f.write(f"newmtl {mtl_name}\n")
        f.write(f"Ka {color[0]*0.2} {color[1]*0.2} {color[2]*0.2}\n")
        f.write(f"Kd {color[0]} {color[1]} {color[2]}\n")
        f.write("Ks 0.3 0.3 0.3\nNs 30\nd 1.0\nillum 2\n")
    
    # Escribir OBJ
    with open(os.path.join(OUTPUT_DIR, f"{nombre}.obj"), 'w') as f:
        f.write(f"mtllib {nombre}.mtl\n")
        f.write(f"g {nombre}\n")
        f.write(f"usemtl {mtl_name}\n")
        for v in vertices:
            f.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
        for face in caras:
            f.write(f"f {' '.join(str(i) for i in face)}\n")
    
    print(f"✅ Generada: {nombre}")

# Definición de especies
especies = [
    ("griffin_alpine", "bipedo", (0.8, 0.85, 0.9)), # Azul hielo
    ("beetle_jungle", "cuadrupedo", (0.2, 0.6, 0.2)), # Verde
    ("dragon_desert", "serpentino", (0.8, 0.3, 0.1)), # Naranja
    ("bird_volcanic", "volador", (0.4, 0.4, 0.4)), # Gris ceniza
    ("leviathan_ocean", "acuatico", (0.1, 0.1, 0.7)) # Azul marino
]

print("🚀 Generando modelos 3D coherentes...")
for nombre, tipo, color in especies:
    partes = construir_esqueleto(tipo)
    guardar_obj(nombre, partes, color)

print(f"\n✨ ¡Listo! Archivos en carpeta: {OUTPUT_DIR}")
print("Archivos creados:")
for f in os.listdir(OUTPUT_DIR):
    print(f" - {f}")
