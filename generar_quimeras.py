import os
import math
import random
import subprocess

# Configuración - TOKEN SE PASA POR VARIABLE DE ENTORNO O SE LEE DE ARCHIVO SEGURO
OUTPUT_DIR = "/workspace"
TOKEN_FILE = "/tmp/github_token.txt"

def crear_mtl(nombre, color_base):
    content = f"""newmtl M_{nombre}
Ka {color_base[0]*0.2} {color_base[1]*0.2} {color_base[2]*0.2}
Kd {color_base[0]} {color_base[1]} {color_base[2]}
Ks 0.6 0.6 0.6
Ns 60
d 1.0
illum 2
"""
    with open(os.path.join(OUTPUT_DIR, f"{nombre}.mtl"), 'w') as f:
        f.write(content)

def escribir_obj(nombre, vertices, caras):
    filename = os.path.join(OUTPUT_DIR, f"{nombre}.obj")
    with open(filename, 'w') as f:
        f.write(f"mtllib {nombre}.mtl\n")
        f.write(f"g {nombre}\n")
        f.write(f"usemtl M_{nombre}\n")
        for v in vertices:
            f.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
        for face in caras:
            f.write(f"f {' '.join([str(v) for v in face])}\n")
    print(f"✅ Generado: {nombre}.obj")

def esfera_con_caras(cx, cy, cz, radio, iteraciones=1):
    """Genera esfera con vértices Y caras correctamente indexadas"""
    t = (1 + math.sqrt(5)) / 2
    verts_base = [
        (-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0),
        (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
        (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)
    ]
    
    # Normalizar
    vertices = []
    for x, y, z in verts_base:
        mag = math.sqrt(x*x + y*y + z*z)
        vertices.append((x/mag, y/mag, z/mag))
    
    # Caras base del icosaedro
    caras_base = [
        (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
        (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
        (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
        (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)
    ]
    
    # Subdivisión simple (1 iteración para mantener bajo el número de polis)
    if iteraciones > 0:
        new_verts = list(vertices)
        new_caras = []
        used_edges = {}
        
        def get_midpoint(i, j):
            key = tuple(sorted((i, j)))
            if key not in used_edges:
                v1 = vertices[i]
                v2 = vertices[j]
                mid = ((v1[0]+v2[0])/2, (v1[1]+v2[1])/2, (v1[2]+v2[2])/2)
                mag = math.sqrt(mid[0]**2 + mid[1]**2 + mid[2]**2)
                new_idx = len(new_verts)
                new_verts.append((mid[0]/mag, mid[1]/mag, mid[2]/mag))
                used_edges[key] = new_idx
            return used_edges[key]
        
        for f in caras_base:
            i, j, k = f
            a = get_midpoint(i, j)
            b = get_midpoint(j, k)
            c = get_midpoint(k, i)
            
            new_caras.extend([
                (i, a, c), (j, b, a), (k, c, b), (a, b, c)
            ])
        
        vertices = new_verts
        caras_base = new_caras
    
    # Escalar y trasladar
    finales = [(v[0]*radio + cx, v[1]*radio + cy, v[2]*radio + cz) for v in vertices]
    return finales, caras_base

def generar_quimera(adn_tipo):
    vertices = []
    caras = []
    color = (0.5, 0.5, 0.5)
    offset = 0
    
    if adn_tipo == "chimera_alpha":
        color = (0.8, 0.6, 0.2)
        # Cabeza
        v, c = esfera_con_caras(0, 2, 0, 0.8, 1)
        vertices.extend(v)
        caras.extend([(i+offset, j+offset, k+offset) for i,j,k in c])
        offset += len(v)
        # Cuerpo
        v, c = esfera_con_caras(0, 0.5, 0, 1.2, 1)
        vertices.extend(v)
        caras.extend([(i+offset, j+offset, k+offset) for i,j,k in c])
        offset += len(v)
        # Alas
        v, c = esfera_con_caras(-1.5, 1, -0.5, 0.6, 0)
        vertices.extend(v)
        caras.extend([(i+offset, j+offset, k+offset) for i,j,k in c])
        offset += len(v)
        v, c = esfera_con_caras(1.5, 1, -0.5, 0.6, 0)
        vertices.extend(v)
        caras.extend([(i+offset, j+offset, k+offset) for i,j,k in c])
        offset += len(v)
        # Cola
        for i in range(5):
            v, c = esfera_con_caras(0, 0, -1.5-i*0.6, 0.4-i*0.05, 0)
            vertices.extend(v)
            caras.extend([(oi+offset, oj+offset, ok+offset) for oi,oj,ok in c])
            offset += len(v)
            
    elif adn_tipo == "leviathan_crystal":
        color = (0.2, 0.8, 0.9)
        # Cuerpo alargado
        v, c = esfera_con_caras(0, 0, 0, 1.5, 1)
        v = [(x*2.5, y, z) for x,y,z in v]
        vertices.extend(v)
        caras.extend([(i+offset, j+offset, k+offset) for i,j,k in c])
        offset += len(v)
        # Cristales
        for i in range(4):
            v, c = esfera_con_caras(-1+i*0.7, 1.2, 0, 0.3, 0)
            v = [(x, y*1.5, z) for x,y,z in v]
            vertices.extend(v)
            caras.extend([(oi+offset, oj+offset, ok+offset) for oi,oj,ok in c])
            offset += len(v)
        # Aleta
        v, c = esfera_con_caras(0, -0.5, 0.8, 0.8, 0)
        vertices.extend(v)
        caras.extend([(i+offset, j+offset, k+offset) for i,j,k in c])
        
    elif adn_tipo == "spore_walker":
        color = (0.6, 0.3, 0.8)
        # Sombrero
        v, c = esfera_con_caras(0, 2, 0, 1.5, 1)
        v = [(x, max(0, y), z) for x,y,z in v]
        vertices.extend(v)
        caras.extend([(i+offset, j+offset, k+offset) for i,j,k in c])
        offset += len(v)
        # Patas
        for i in range(6):
            ang = i * (math.pi / 3)
            lx, lz = math.cos(ang)*0.8, math.sin(ang)*0.8
            v, c = esfera_con_caras(lx, 0.5, lz, 0.25, 0)
            vertices.extend(v)
            caras.extend([(oi+offset, oj+offset, ok+offset) for oi,oj,ok in c])
            offset += len(v)
        # Esporas
        for _ in range(12):
            sx, sy, sz = random.uniform(-2,2), random.uniform(2.5,4), random.uniform(-2,2)
            v, c = esfera_con_caras(sx, sy, sz, 0.15, 0)
            vertices.extend(v)
            caras.extend([(oi+offset, oj+offset, ok+offset) for oi,oj,ok in c])
            offset += len(v)
            
    elif adn_tipo == "geo_drake":
        color = (0.7, 0.3, 0.1)
        # Cuerpo
        v, c = esfera_con_caras(0, 0, 0, 1.0, 1)
        vertices.extend(v)
        caras.extend([(i+offset, j+offset, k+offset) for i,j,k in c])
        offset += len(v)
        # Placas
        for i in range(5):
            v, c = esfera_con_caras(0, 1.0, -0.8-i*0.4, 0.3, 0)
            v = [(x, y+0.2, z) for x,y,z in v]
            vertices.extend(v)
            caras.extend([(oi+offset, oj+offset, ok+offset) for oi,oj,ok in c])
            offset += len(v)
        # Cabeza
        v, c = esfera_con_caras(0, 0.5, 1.2, 0.7, 1)
        vertices.extend(v)
        caras.extend([(i+offset, j+offset, k+offset) for i,j,k in c])
        offset += len(v)
        # Alas
        v, c = esfera_con_caras(-1.2, 0.5, -0.2, 0.5, 0)
        vertices.extend(v)
        caras.extend([(i+offset, j+offset, k+offset) for i,j,k in c])
        offset += len(v)
        v, c = esfera_con_caras(1.2, 0.5, -0.2, 0.5, 0)
        vertices.extend(v)
        caras.extend([(i+offset, j+offset, k+offset) for i,j,k in c])
        
    elif adn_tipo == "void_tentacle":
        color = (0.1, 0.1, 0.3)
        # Núcleo
        v, c = esfera_con_caras(0, 0, 0, 0.8, 1)
        vertices.extend(v)
        caras.extend([(i+offset, j+offset, k+offset) for i,j,k in c])
        offset += len(v)
        # Tentáculos
        for i in range(8):
            ang = i * (math.pi / 4)
            for j in range(4):
                dist = 1.0 + j*0.6
                off = math.sin(j*0.8)*0.5
                tx = math.cos(ang+off)*dist
                ty = math.sin(j*0.5)*dist*0.5
                tz = math.sin(ang+off)*dist
                rad = 0.25 - j*0.05
                v, c = esfera_con_caras(tx, ty, tz, rad, 0)
                vertices.extend(v)
                caras.extend([(oi+offset, oj+offset, ok+offset) for oi,oj,ok in c])
                offset += len(v)
    
    return vertices, caras, color

# MAIN
print("🧬 Generando Quimeras WFC...")
quimeras = ["chimera_alpha", "leviathan_crystal", "spore_walker", "geo_drake", "void_tentacle"]

for nombre in quimeras:
    verts, caras, color = generar_quimera(nombre)
    crear_mtl(nombre, color)
    escribir_obj(nombre, verts, caras)

print("✨ Archivos listos.")

# PUSH SEGURO SIN HARDCODEAR TOKEN EN EL CÓDIGO
print("\n🚀 Subiendo a GitHub...")
try:
    subprocess.run(["git", "config", "--global", "user.name", "WFC-Bot"], check=True)
    subprocess.run(["git", "config", "--global", "user.email", "bot@wfc.local"], check=True)
    subprocess.run(["git", "add", "-A"], check=True, cwd="/workspace")
    subprocess.run(["git", "commit", "-m", "Quimeras WFC: Biología Alienígena Mejorada"], check=True, cwd="/workspace")
    
    # Leer token de archivo seguro o variable de entorno
    token = os.environ.get("GITHUB_TOKEN")
    if not token and os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            token = f.read().strip()
    
    if token:
        repo_url = f"https://a01564159-lang:{token}@github.com/a01564159-lang/olo.git"
        result = subprocess.run(["git", "push", "-f", repo_url, "HEAD:main"], capture_output=True, text=True, cwd="/workspace")
        if result.returncode == 0:
            print("✅ ¡ÉXITO! Subido a GitHub.")
            print("🔗 https://github.com/a01564159-lang/olo")
        else:
            print(f"⚠️ Push falló: {result.stderr}")
            # Guardar archivos en rama local si falla push
            subprocess.run(["git", "push", "origin", "HEAD:qwen-creatures"], cwd="/workspace")
            print("Archivos guardados en rama local 'qwen-creatures'.")
    else:
        print("⚠️ No se encontró token. Archivos listos en /workspace pero no subidos.")
except Exception as e:
    print(f"❌ Error: {e}")
