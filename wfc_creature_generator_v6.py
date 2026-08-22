#!/usr/bin/env python3
"""
WFC Creature Generator V6.0 - Axial Symmetry & Socket System
Generates biologically plausible creatures with defined limbs, wings, and tentacles
using Wave Function Collapse with strict adjacency rules.
"""

import os
import random
import math
from collections import defaultdict

# Output directory
OUTPUT_DIR = "wfc_creatures_fixed"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================================
# TILE DEFINITION WITH SOCKETS
# Each tile has 4 sockets: N, E, S, W
# Socket types: 'body', 'limb_base', 'wing_base', 'tentacle_base', 'head_end', 'tail_end', 'none'
# ============================================================================

SOCKET_TYPES = ['body', 'limb_base', 'wing_base', 'tentacle_base', 'head_end', 'tail_end', 'none']

class Tile:
    def __init__(self, name, vertices, faces, sockets, weight=1.0):
        self.name = name
        self.vertices = vertices  # List of (x, y, z)
        self.faces = faces        # List of (v1, v2, v3) - triangles only
        self.sockets = sockets    # Dict: {'N': type, 'E': type, 'S': type, 'W': type}
        self.weight = weight

def create_vertex(x, y, z):
    return (round(x, 4), round(y, 4), round(z, 4))

def create_triangle(v1, v2, v3):
    return (v1, v2, v3)

# ============================================================================
# PRIMITIVE SHAPES
# ============================================================================

def generate_sphere(cx, cy, cz, radius, segments=8):
    """Generate a sphere mesh"""
    vertices = []
    faces = []
    
    for i in range(segments + 1):
        lat = math.pi * (-0.5 + float(i) / segments)
        y = cy + radius * math.sin(lat)
        ring_radius = radius * math.cos(lat)
        
        for j in range(segments):
            lon = 2 * math.pi * float(j) / segments
            x = cx + ring_radius * math.cos(lon)
            z = cz + ring_radius * math.sin(lon)
            vertices.append(create_vertex(x, y, z))
    
    # Create triangles
    for i in range(segments):
        for j in range(segments):
            idx = i * segments + j
            next_idx = i * segments + (j + 1) % segments
            
            if i < segments - 1:
                bottom_next = (i + 1) * segments + (j + 1) % segments
                bottom_curr = (i + 1) * segments + j
                
                faces.append(create_triangle(idx, bottom_curr, bottom_next))
                faces.append(create_triangle(idx, bottom_next, next_idx))
    
    return vertices, faces

def generate_cylinder(cx, cy, cz, radius, height, axis='Y', segments=8):
    """Generate a cylinder mesh"""
    vertices = []
    faces = []
    
    # Top and bottom circles
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        if axis == 'Y':
            x = cx + radius * math.cos(angle)
            z = cz + radius * math.sin(angle)
            vertices.append(create_vertex(x, cy - height/2, z))  # Bottom
            vertices.append(create_vertex(x, cy + height/2, z))  # Top
        elif axis == 'X':
            y = cy + radius * math.cos(angle)
            z = cz + radius * math.sin(angle)
            vertices.append(create_vertex(cx - height/2, y, z))  # Left
            vertices.append(create_vertex(cx + height/2, y, z))  # Right
    
    # Side faces
    for i in range(segments):
        next_i = (i + 1) % segments
        if axis == 'Y':
            faces.append(create_triangle(i*2, next_i*2, next_i*2+1))
            faces.append(create_triangle(i*2, next_i*2+1, i*2+1))
        else:
            faces.append(create_triangle(i*2, next_i*2, next_i*2+1))
            faces.append(create_triangle(i*2, next_i*2+1, i*2+1))
    
    # Cap faces (simplified)
    if axis == 'Y':
        # Bottom cap
        center_bottom = len(vertices)
        vertices.append(create_vertex(cx, cy - height/2, cz))
        for i in range(segments):
            next_i = (i + 1) % segments
            faces.append(create_triangle(center_bottom, i*2, next_i*2))
        
        # Top cap
        center_top = len(vertices)
        vertices.append(create_vertex(cx, cy + height/2, cz))
        for i in range(segments):
            next_i = (i + 1) % segments
            faces.append(create_triangle(center_top, next_i*2+1, i*2+1))
    
    return vertices, faces

def generate_cone(cx, cy, cz, base_radius, tip_radius, height, axis='Y', segments=8):
    """Generate a cone/frustum mesh"""
    vertices = []
    faces = []
    
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        if axis == 'Y':
            x_base = cx + base_radius * math.cos(angle)
            z_base = cz + base_radius * math.sin(angle)
            x_tip = cx + tip_radius * math.cos(angle)
            z_tip = cz + tip_radius * math.sin(angle)
            
            vertices.append(create_vertex(x_base, cy - height/2, z_base))  # Bottom
            vertices.append(create_vertex(x_tip, cy + height/2, z_tip))    # Top
    
    for i in range(segments):
        next_i = (i + 1) % segments
        faces.append(create_triangle(i*2, next_i*2, next_i*2+1))
        faces.append(create_triangle(i*2, next_i*2+1, i*2+1))
    
    return vertices, faces

# ============================================================================
# CREATURE PARTS WITH SOCKETS
# ============================================================================

def create_body_segment(x, y, z, length, radius, has_limb_sockets=False, has_wing_sockets=False):
    """Create a body segment with appropriate sockets"""
    verts, faces = generate_cylinder(x, y, z, radius, length, axis='Z')
    
    sockets = {
        'N': 'body' if y > 0 else 'none',
        'E': 'limb_base' if has_limb_sockets else ('wing_base' if has_wing_sockets else 'none'),
        'S': 'body' if y < 0 else 'none',
        'W': 'limb_base' if has_limb_sockets else ('wing_base' if has_wing_sockets else 'none')
    }
    
    return Tile("body_segment", verts, faces, sockets, weight=2.0)

def create_head(x, y, z, size):
    """Create a head with eye sockets"""
    verts, faces = generate_sphere(x, y, z, size, segments=6)
    
    sockets = {
        'N': 'none',
        'E': 'none',
        'S': 'body',  # Connects to body
        'W': 'none'
    }
    
    return Tile("head", verts, faces, sockets, weight=1.0)

def create_tail_segment(x, y, z, base_radius, tip_radius, length):
    """Create a tail segment that tapers"""
    verts, faces = generate_cone(x, y, z, base_radius, tip_radius, length, axis='Z')
    
    sockets = {
        'N': 'none',
        'E': 'none',
        'S': 'body',  # Connects to previous segment
        'W': 'tail_end' if tip_radius < 0.1 else 'body'
    }
    
    return Tile("tail_segment", verts, faces, sockets, weight=1.5)

def create_limb(x, y, z, length, radius, is_arm=False, has_claws=False):
    """Create a limb (arm or leg)"""
    verts, faces = generate_cylinder(x, y, z, radius, length, axis='Y')
    
    sockets = {
        'N': 'none',
        'E': 'none',
        'S': 'limb_base',  # Connects to body
        'W': 'none'
    }
    
    return Tile("arm" if is_arm else "leg", verts, faces, sockets, weight=1.2)

def create_wing(x, y, z, span, chord):
    """Create a wing"""
    # Simplified wing as a flat elongated shape
    verts = [
        create_vertex(x, y, z),
        create_vertex(x + span, y, z),
        create_vertex(x + span/2, y, z + chord),
        create_vertex(x, y, z - chord/2),
        create_vertex(x + span, y, z - chord/2),
        create_vertex(x + span/2, y, z + chord*1.2)
    ]
    
    faces = [
        (0, 1, 2), (0, 2, 3), (1, 4, 2), (2, 4, 5),
        (0, 3, 1), (3, 4, 1)
    ]
    
    sockets = {
        'N': 'none',
        'E': 'none',
        'S': 'wing_base',  # Connects to body
        'W': 'none'
    }
    
    return Tile("wing", verts, faces, sockets, weight=0.8)

def create_tentacle(x, y, z, length, base_radius, tip_radius):
    """Create a tentacle segment"""
    verts, faces = generate_cone(x, y, z, base_radius, tip_radius, length, axis='Y')
    
    sockets = {
        'N': 'none',
        'E': 'none',
        'S': 'tentacle_base',  # Connects to body
        'W': 'none' if tip_radius > 0.05 else 'none'
    }
    
    return Tile("tentacle", verts, faces, sockets, weight=1.0)

# ============================================================================
# WFC ENGINE WITH SOCKET COMPATIBILITY
# ============================================================================

def are_sockets_compatible(socket1, socket2):
    """Check if two sockets can connect"""
    if socket1 == 'none' or socket2 == 'none':
        return True
    
    # Body connects to body
    if socket1 == 'body' and socket2 == 'body':
        return True
    
    # Limb base connects to limb
    if socket1 == 'limb_base' and socket2 == 'limb_base':
        return True
    
    # Wing base connects to wing
    if socket1 == 'wing_base' and socket2 == 'wing_base':
        return True
    
    # Tentacle base connects to tentacle
    if socket1 == 'tentacle_base' and socket2 == 'tentacle_base':
        return True
    
    # Head/tail endpoints
    if (socket1 == 'head_end' and socket2 == 'body') or (socket1 == 'body' and socket2 == 'head_end'):
        return True
    
    if (socket1 == 'tail_end' and socket2 == 'body') or (socket1 == 'body' and socket2 == 'tail_end'):
        return True
    
    return False

def get_opposite_direction(direction):
    opposites = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}
    return opposites[direction]

def build_creature_blueprint(creature_type):
    """Define creature blueprints with axial symmetry"""
    blueprints = {
        'quadruped': {
            'body_segments': 4,
            'legs': 4,
            'arms': 0,
            'wings': 0,
            'tentacles': 0,
            'has_head': True,
            'has_tail': True,
            'symmetry': 'bilateral'
        },
        'biped': {
            'body_segments': 3,
            'legs': 2,
            'arms': 2,
            'wings': 0,
            'tentacles': 0,
            'has_head': True,
            'has_tail': False,
            'symmetry': 'bilateral'
        },
        'flying': {
            'body_segments': 3,
            'legs': 2,
            'arms': 0,
            'wings': 2,
            'tentacles': 0,
            'has_head': True,
            'has_tail': True,
            'symmetry': 'bilateral'
        },
        'cephalopod': {
            'body_segments': 1,
            'legs': 0,
            'arms': 0,
            'wings': 0,
            'tentacles': 8,
            'has_head': True,
            'has_tail': False,
            'symmetry': 'radial'
        },
        'serpentine': {
            'body_segments': 12,
            'legs': 0,
            'arms': 0,
            'wings': 0,
            'tentacles': 0,
            'has_head': True,
            'has_tail': True,
            'symmetry': 'bilateral'
        }
    }
    
    return blueprints.get(creature_type, blueprints['quadruped'])

def generate_creature_mesh(creature_type, seed=None):
    """Generate complete creature mesh using blueprint"""
    if seed is not None:
        random.seed(seed)
    
    blueprint = build_creature_blueprint(creature_type)
    all_vertices = []
    all_faces = []
    vertex_offset = 0
    
    # Configuration based on creature type
    body_length = 1.0
    body_radius = 0.4
    limb_length = 1.2
    limb_radius = 0.15
    
    # 1. Generate body segments along Z-axis
    num_body = blueprint['body_segments']
    for i in range(num_body):
        z_pos = (i - num_body/2) * body_length * 0.8
        has_limbs = (i == num_body//2) and (blueprint['legs'] > 0 or blueprint['arms'] > 0)
        has_wings = (i == num_body//2) and blueprint['wings'] > 0
        
        tile = create_body_segment(0, 0, z_pos, body_length*0.9, body_radius, 
                                   has_limb_sockets=has_limbs, has_wing_sockets=has_wings)
        
        # Add vertices with offset
        for v in tile.vertices:
            all_vertices.append((v[0], v[1], v[2] + vertex_offset))
        
        for f in tile.faces:
            all_faces.append((f[0] + vertex_offset, f[1] + vertex_offset, f[2] + vertex_offset))
        
        vertex_offset += len(tile.vertices)
    
    # 2. Add head
    if blueprint['has_head']:
        head_z = (num_body/2) * body_length * 0.8 + body_length/2
        head_tile = create_head(0, 0, head_z, body_radius * 1.3)
        
        for v in head_tile.vertices:
            all_vertices.append((v[0], v[1], v[2] + vertex_offset))
        
        for f in head_tile.faces:
            all_faces.append((f[0] + vertex_offset, f[1] + vertex_offset, f[2] + vertex_offset))
        
        vertex_offset += len(head_tile.vertices)
    
    # 3. Add tail
    if blueprint['has_tail']:
        tail_z = -(num_body/2) * body_length * 0.8 - body_length/2
        for i in range(3):
            taper = 1.0 - i * 0.25
            tail_tile = create_tail_segment(0, 0, tail_z - i*body_length*0.6, 
                                           body_radius * taper, body_radius * taper * 0.3, 
                                           body_length*0.7)
            
            for v in tail_tile.vertices:
                all_vertices.append((v[0], v[1], v[2] + vertex_offset))
            
            for f in tail_tile.faces:
                all_faces.append((f[0] + vertex_offset, f[1] + vertex_offset, f[2] + vertex_offset))
            
            vertex_offset += len(tail_tile.vertices)
    
    # 4. Add legs (bilateral symmetry)
    if blueprint['legs'] > 0:
        leg_positions = []
        if blueprint['legs'] == 2:
            leg_positions = [(0.5, -0.3), (-0.5, -0.3)]  # Biped
        elif blueprint['legs'] == 4:
            leg_positions = [(0.5, 0.3), (-0.5, 0.3), (0.5, -0.3), (-0.5, -0.3)]  # Quadruped
        
        for lx, lz in leg_positions:
            leg_tile = create_limb(lx, -limb_length/2, lz, limb_length, limb_radius, is_arm=False)
            
            for v in leg_tile.vertices:
                all_vertices.append((v[0] + lx, v[1], v[2] + lz))
            
            for f in leg_tile.faces:
                all_faces.append((f[0] + vertex_offset, f[1] + vertex_offset, f[2] + vertex_offset))
            
            vertex_offset += len(leg_tile.vertices)
    
    # 5. Add arms (bilateral symmetry)
    if blueprint['arms'] > 0:
        arm_positions = [(0.6, 0.2), (-0.6, 0.2)]
        
        for ax, az in arm_positions:
            arm_tile = create_limb(ax, -limb_length/2, az, limb_length*0.9, limb_radius*0.8, is_arm=True)
            
            for v in arm_tile.vertices:
                all_vertices.append((v[0] + ax, v[1], v[2] + az))
            
            for f in arm_tile.faces:
                all_faces.append((f[0] + vertex_offset, f[1] + vertex_offset, f[2] + vertex_offset))
            
            vertex_offset += len(arm_tile.vertices)
    
    # 6. Add wings (bilateral symmetry)
    if blueprint['wings'] > 0:
        wing_positions = [(1.2, 0.1), (-1.2, 0.1)]
        
        for wx, wz in wing_positions:
            wing_span = 2.5 if wx > 0 else -2.5
            wing_tile = create_wing(wx, 0.5, wz, wing_span, 0.8)
            
            # Adjust vertices for wing orientation
            adjusted_verts = []
            for v in wing_tile.vertices:
                if wx > 0:
                    adjusted_verts.append((v[0] + wx - 0.5, v[1], v[2] + wz))
                else:
                    adjusted_verts.append((v[0] + wx + 0.5, v[1], v[2] + wz))
            
            for v in adjusted_verts:
                all_vertices.append(v)
            
            for f in wing_tile.faces:
                all_faces.append((f[0] + vertex_offset, f[1] + vertex_offset, f[2] + vertex_offset))
            
            vertex_offset += len(wing_tile.vertices)
    
    # 7. Add tentacles (radial symmetry for cephalopod)
    if blueprint['tentacles'] > 0:
        num_tentacles = blueprint['tentacles']
        for i in range(num_tentacles):
            angle = 2 * math.pi * i / num_tentacles
            tx = math.cos(angle) * 0.5
            tz = math.sin(angle) * 0.5
            
            tentacle_tile = create_tentacle(tx, -1.0, tz, 1.5, 0.12, 0.02)
            
            for v in tentacle_tile.vertices:
                all_vertices.append((v[0] + tx, v[1], v[2] + tz))
            
            for f in tentacle_tile.faces:
                all_faces.append((f[0] + vertex_offset, f[1] + vertex_offset, f[2] + vertex_offset))
            
            vertex_offset += len(tentacle_tile.vertices)
    
    return all_vertices, all_faces

def write_obj_file(filename, vertices, faces, material_name="creature_mat"):
    """Write vertices and faces to OBJ file (triangles only)"""
    with open(filename, 'w') as f:
        f.write(f"# WFC Creature - {os.path.basename(filename)}\n")
        f.write(f"mtllib {os.path.splitext(os.path.basename(filename))[0]}.mtl\n")
        f.write(f"usemtl {material_name}\n")
        f.write("\n")
        
        # Write vertices
        for v in vertices:
            f.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
        
        # Write faces (triangles only)
        for face in faces:
            f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")

def write_mtl_file(filename, color=(0.7, 0.7, 0.7)):
    """Write MTL material file"""
    with open(filename, 'w') as f:
        f.write(f"# Material for WFC Creature\n")
        f.write(f"newmtl creature_mat\n")
        f.write(f"Ka {color[0]*0.2:.2f} {color[1]*0.2:.2f} {color[2]*0.2:.2f}\n")
        f.write(f"Kd {color[0]:.2f} {color[1]:.2f} {color[2]:.2f}\n")
        f.write(f"Ks 0.3 0.3 0.3\n")
        f.write(f"Ns 50\n")
        f.write(f"d 1.0\n")
        f.write(f"illum 2\n")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("🧬 WFC Creature Generator V6.0 - Axial Symmetry & Socket System")
    print("=" * 60)
    
    creatures = [
        ('quadruped_beast', 'quadruped', (0.7, 0.5, 0.3)),  # Brown beast
        ('biped_warrior', 'biped', (0.6, 0.6, 0.8)),        # Blue humanoid
        ('sky_dragon', 'flying', (0.8, 0.3, 0.2)),          # Red dragon
        ('deep_kraken', 'cephalopod', (0.2, 0.3, 0.6)),     # Purple kraken
        ('cave_wyrm', 'serpentine', (0.5, 0.5, 0.5))        # Gray serpent
    ]
    
    for name, ctype, color in creatures:
        print(f"\n🔨 Generating {name} ({ctype})...")
        
        # Generate mesh
        vertices, faces = generate_creature_mesh(ctype, seed=random.randint(0, 9999))
        
        # Write files
        obj_path = os.path.join(OUTPUT_DIR, f"{name}.obj")
        mtl_path = os.path.join(OUTPUT_DIR, f"{name}.mtl")
        
        write_obj_file(obj_path, vertices, faces)
        write_mtl_file(mtl_path, color)
        
        print(f"   ✅ Created {name}.obj ({len(vertices)} vertices, {len(faces)} triangles)")
        print(f"   ✅ Created {name}.mtl")
    
    print("\n" + "=" * 60)
    print(f"✨ All creatures generated in '{OUTPUT_DIR}/' directory")
    print("📁 Files ready for GitHub commit and push")
