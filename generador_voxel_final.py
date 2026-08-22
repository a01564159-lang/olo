"""
GENERADOR DE CRIATURAS VOXEL 3D - VERSIÓN FINAL EXPORTABLE
Genera modelos .OBJ coherentes + Empaquetado ZIP para descarga manual.
"""

import os
import math
import zipfile
import json

# Configuración de salida
OUTPUT_DIR = "voxel_creatures_final"
ZIP_NAME = "criaturas_3d_completas.zip"

def ensure_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def generate_voxel_sphere(cx, cy, cz, radius, voxel_map, material_id):
    """Genera una esfera sólida de voxels."""
    r = int(radius)
    for x in range(-r, r + 1):
        for y in range(-r, r + 1):
            for z in range(-r, r + 1):
                if x*x + y*y + z*z <= r*r:
                    key = (cx + x, cy + y, cz + z)
                    if key not in voxel_map: # No sobrescribir
                        voxel_map[key] = material_id

def generate_voxel_box(x1, y1, z1, x2, y2, z2, voxel_map, material_id):
    """Genera una caja sólida de voxels."""
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for z in range(min(z1, z2), max(z1, z2) + 1):
                key = (x, y, z)
                if key not in voxel_map:
                    voxel_map[key] = material_id

def generate_limb(start, end, thickness, voxel_map, material_id):
    """Genera una extremidad cilíndrica usando algoritmo de línea 3D."""
    x0, y0, z0 = start
    x1, y1, z1 = end
    steps = max(abs(x1-x0), abs(y1-y0), abs(z1-z0))
    if steps == 0: steps = 1
    
    for i in range(steps + 1):
        t = i / steps
        x = int(x0 + (x1 - x0) * t)
        y = int(y0 + (y1 - y0) * t)
        z = int(z0 + (z1 - z0) * t)
        generate_voxel_sphere(x, y, z, thickness, voxel_map, material_id)

def create_creature(name, body_type, env_data):
    """Crea una criatura específica basada en tipo y ambiente."""
    voxels = {} # (x,y,z) -> material_id
    center = (0, 0, 0)
    
    # Definición de materiales según ambiente
    # 1: Piel principal, 2: Armadura/Escamas, 3: Ojos, 4: Garras/Dientes
    colors = {
        'alpine': {1: '#A8C0D8', 2: '#FFFFFF', 3: '#000000', 4: '#2C3E50'}, # Azul/Hielo
        'jungle': {1: '#4CAF50', 2: '#2E7D32', 3: '#FFEB3B', 4: '#3E2723'}, # Verde/Madera
        'desert': {1: '#D7CCC8', 2: '#8D6E63', 3: '#FF5722', 4: '#3E2723'}, # Arena/Roca
        'ocean': {1: '#1A237E', 2: '#00BCD4', 3: '#FFFF00', 4: '#FFFFFF'}, # Azul profundo
        'volcanic': {1: '#424242', 2: '#B71C1C', 3: '#FFCDD2', 4: '#000000'} # Gris/Lava
    }
    
    palette = colors.get(env_data['biome'], colors['alpine'])
    
    # 1. Cuerpo Central
    generate_voxel_sphere(0, 0, 0, 4, voxels, 1)
    
    if body_type == 'biped':
        # Cabeza
        generate_voxel_sphere(0, 6, 0, 2.5, voxels, 1)
        generate_voxel_box(-1, 5, 1, 1, 5, 2, voxels, 3) # Ojos
        
        # Torso alargado
        generate_voxel_box(-2, -3, -2, 2, 3, 2, voxels, 1)
        
        # Piernas (2)
        generate_limb((0, -3, 0), (-2, -8, 0), 1.2, voxels, 1)
        generate_limb((0, -3, 0), (2, -8, 0), 1.2, voxels, 1)
        # Pies
        generate_voxel_box(-3, -9, -1, -1, -8, 1, voxels, 4)
        generate_voxel_box(1, -9, -1, 3, -8, 1, voxels, 4)
        
        # Brazos (2)
        generate_limb((0, 2, 0), (-4, 0, 0), 1, voxels, 1)
        generate_limb((0, 2, 0), (4, 0, 0), 1, voxels, 1)
        
    elif body_type == 'quadruped':
        # Cabeza estirada
        generate_voxel_box(-1, 5, -1, 1, 7, 3, voxels, 1)
        generate_voxel_box(1, 6, 0, 2, 6, 1, voxels, 3) # Ojo lateral
        
        # Cuerpo largo
        generate_voxel_box(-2, -2, -3, 2, 2, 3, voxels, 1)
        
        # 4 Patas
        legs_pos = [(-2, -2), (2, -2), (-2, 2), (2, 2)]
        for lx, lz in legs_pos:
            generate_limb((lx, 0, lz), (lx, -6, lz), 1.2, voxels, 1)
            generate_voxel_box(lx-1, -7, lz-1, lx+1, -6, lz+1, voxels, 4) # Pezuñas
            
    elif body_type == 'flier':
        # Cuerpo aerodinámico
        generate_voxel_box(-1, -1, -4, 1, 1, 4, voxels, 1)
        generate_voxel_sphere(0, 2, 0, 2, voxels, 1) # Cabeza
        
        # Alas grandes (planas en X)
        for i in range(1, 12):
            thick = max(0, 1 - i/10)
            generate_voxel_box(i, 0, -2, i+1, 1, 2, voxels, 2) # Ala derecha
            generate_voxel_box(-i-1, 0, -2, -i, 1, 2, voxels, 2) # Ala izquierda
            
        # Cola
        generate_limb((0, 0, 4), (0, -2, 8), 1, voxels, 2)
        
    elif body_type == 'aquatic':
        # Cuerpo fusiforme
        generate_voxel_box(-2, -2, -6, 2, 2, 6, voxels, 1)
        generate_voxel_sphere(0, 0, -7, 2.5, voxels, 1) # Cabeza redonda
        
        # Aletas laterales
        generate_voxel_box(-4, -1, -1, -2, 1, 1, voxels, 2)
        generate_voxel_box(2, -1, -1, 4, 1, 1, voxels, 2)
        
        # Aleta dorsal
        generate_voxel_box(-1, 2, -1, 1, 4, 1, voxels, 2)
        
        # Cola horizontal
        generate_voxel_box(-3, -1, 6, 3, 1, 8, voxels, 2)
        
    elif body_type == 'serpent':
        # Cabeza
        generate_voxel_sphere(0, 2, 0, 2, voxels, 1)
        generate_voxel_box(-1, 2, 1, 1, 2, 2, voxels, 3) # Ojos
        
        # Cuerpo ondulado (simulado con esferas escalonadas)
        for i in range(1, 15):
            offset_x = math.sin(i * 0.5) * 2
            offset_y = math.cos(i * 0.3) * 1
            generate_voxel_sphere(int(offset_x), 2 - (i//3), i, 1.5, voxels, 1)
            
        # Cola fina
        generate_limb((0, 0, 14), (0, -1, 18), 0.8, voxels, 2)

    return voxels, palette

def write_obj(filename, voxels, palette):
    """Escribe un archivo .OBJ simple."""
    vertices = []
    faces = []
    
    # Mapeo simple de voxel a cubo (solo caras externas para optimizar un poco)
    # Para simplicidad, generamos un cubo por voxel. En producción se usaría Meshing.
    with open(filename, 'w') as f:
        f.write(f"mtllib materials.mtl\n")
        
        vertex_count = 0
        mat_groups = {mid: [] for mid in palette.keys()}
        
        # Generar vértices para cada voxel
        voxel_list = list(voxels.items())
        for (x, y, z), mat_id in voxel_list:
            # Cubo unitario centrado en x,y,z
            s = 0.5
            verts = [
                (x-s, y-s, z-s), (x+s, y-s, z-s), (x+s, y+s, z-s), (x-s, y+s, z-s),
                (x-s, y-s, z+s), (x+s, y-s, z+s), (x+s, y+s, z+s), (x-s, y+s, z+s)
            ]
            
            current_verts = []
            for vx, vy, vz in verts:
                f.write(f"v {vx:.2f} {vy:.2f} {vz:.2f}\n")
                vertex_count += 1
                current_verts.append(vertex_count)
            
            # Caras (índices relativos al inicio del grupo actual serían ideales, 
            # pero OBJ usa índices globales o por objeto. Usaremos grupos simples)
            # Simplificación: escribimos caras directamente referenciando los últimos 8 vértices
            # Nota: Esto es un OBJ básico, los índices son globales en el archivo.
            base = vertex_count - 8
            
            # Definir grupo por material
            mat_name = f"mat_{mat_id}"
            f.write(f"usemtl {mat_name}\n")
            
            # Caras del cubo (orden CCW)
            f.write(f"f {base+1} {base+2} {base+3} {base+4}\n") # Front
            f.write(f"f {base+5} {base+6} {base+7} {base+8}\n") # Back
            f.write(f"f {base+1} {base+2} {base+6} {base+5}\n") # Bottom
            f.write(f"f {base+4} {base+3} {base+7} {base+8}\n") # Top
            f.write(f"f {base+1} {base+4} {base+8} {base+5}\n") # Left
            f.write(f"f {base+2} {base+3} {base+7} {base+6}\n") # Right

def write_mtl(filename, all_palettes):
    """Escribe el archivo de materiales compartido."""
    with open(filename, 'w') as f:
        used_mats = {}
        counter = 1
        for palette in all_palettes:
            for mid, color in palette.items():
                key = (mid, color)
                if key not in used_mats:
                    used_mats[key] = f"mat_{counter}"
                    f.write(f"newmtl mat_{counter}\n")
                    f.write(f"Ka {color[1:3]} {color[3:5]} {color[5:7]}\n") # Ambient (aprox)
                    f.write(f"Kd {color[1:3]} {color[3:5]} {color[5:7]}\n") # Diffuse
                    f.write(f"d 1.0\n")
                    counter += 1

def main():
    ensure_dir()
    
    # Definición de especies a generar
    species_config = [
        {"name": "griffin_alpine", "type": "biped", "biome": "alpine"},
        {"name": "beetle_jungle", "type": "quadruped", "biome": "jungle"},
        {"name": "dragon_desert", "type": "flier", "biome": "desert"},
        {"name": "leviathan_ocean", "type": "aquatic", "biome": "ocean"},
        {"name": "wyrm_caves", "type": "serpent", "biome": "volcanic"}
    ]
    
    all_palettes = []
    generated_files = []
    
    print("🚀 Iniciando generación de criaturas voxel...")
    
    for spec in species_config:
        print(f"   🧬 Diseñando {spec['name']} ({spec['type']})...")
        voxels, palette = create_creature(spec['name'], spec['type'], spec)
        all_palettes.append(palette)
        
        obj_path = os.path.join(OUTPUT_DIR, f"{spec['name']}.obj")
        write_obj(obj_path, voxels, palette)
        
        # Guardar metadata JSON
        json_path = os.path.join(OUTPUT_DIR, f"{spec['name']}.json")
        with open(json_path, 'w') as jf:
            json.dump({
                "name": spec['name'],
                "type": spec['type'],
                "biome": spec['biome'],
                "voxel_count": len(voxels),
                "description": f"Criatura {spec['type']} adaptada a {spec['biome']}"
            }, jf, indent=2)
            
        generated_files.append(obj_path)
        generated_files.append(json_path)
        print(f"      ✅ {spec['name']}.obj generado ({len(voxels)} voxels)")
    
    # Escribir materiales globales
    mtl_path = os.path.join(OUTPUT_DIR, "materials.mtl")
    write_mtl(mtl_path, all_palettes)
    generated_files.append(mtl_path)
    print("   🎨 materials.mtl generado.")
    
    # Crear ZIP
    zip_path = os.path.join(OUTPUT_DIR, "../" + ZIP_NAME) # ZIP en la raíz
    print(f"   📦 Empaquetando en {ZIP_NAME}...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in generated_files:
            # Añadir archivo al zip manteniendo la estructura relativa si se desea
            # Aquí añadimos solo el nombre del archivo para que sea plano al descomprimir
            arcname = os.path.basename(file)
            zipf.write(file, arcname=arcname)
            
    print(f"\n🎉 ¡ÉXITO! Todo listo.")
    print(f"📂 Archivos creados en: /{OUTPUT_DIR}")
    print(f"📥 Archivo ZIP listo para descargar: /{ZIP_NAME}")
    print("\n👉 INSTRUCCIONES:")
    print(f"1. Busca '{ZIP_NAME}' en tu lista de archivos.")
    print("2. Descárgalo a tu computadora.")
    print("3. Descomprímelo y abre los .obj en cualquier visor 3D (Bloc de Notas 3D, Blender, etc).")
    print("4. O súbelo manualmente a GitHub arrastrando la carpeta.")

if __name__ == "__main__":
    main()
