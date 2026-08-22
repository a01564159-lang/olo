#!/usr/bin/env python3
"""
Fast Visual Creature Generator with Optimized WFC
Quick generation of procedural creatures using streamlined WFC
"""

import random
import math
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# ============================================================================
# CONFIGURACIÓN VISUAL
# ============================================================================

@dataclass
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    ORANGE = "\033[38;5;208m"

C = Colors()

# ============================================================================
# FASE 1: MOTOR ECOLÓGICO SIMPLIFICADO
# ============================================================================

@dataclass
class EnvVars:
    temperature: float
    humidity: float
    altitude: float
    pressure: float
    resources: float

@dataclass
class CreatureCard:
    id: str
    name: str
    body_type: str
    limbs: int
    armor_type: str
    energy_source: str
    adaptations: List[str]
    adjacency_rules: Dict[str, List[str]]
    weights: Dict[str, float]

class EcoEngine:
    BODY_TYPES = ["serpentine", "quadruped", "biped", "hexapod", "radial"]
    ARMOR_TYPES = ["scales", "chitin", "bone_plates", "fur", "crystalline"]
    
    def __init__(self):
        self.counter = 0
    
    def generate(self, env: EnvVars) -> CreatureCard:
        self.counter += 1
        
        # Determinar tipo de cuerpo
        if env.humidity > 80:
            body_type = random.choice(["serpentine", "radial"])
        elif env.temperature < -20:
            body_type = random.choice(["quadruped", "biped"])
        elif env.resources > 7:
            body_type = random.choice(["hexapod", "quadruped"])
        else:
            body_type = random.choice(self.BODY_TYPES)
        
        # Determinar armadura
        if env.temperature < -30:
            armor = random.choice(["fur", "bone_plates"])
        elif env.temperature > 35:
            armor = random.choice(["scales", "crystalline"])
        else:
            armor = random.choice(self.ARMOR_TYPES)
        
        # Calcular extremidades
        limb_map = {"serpentine": 0, "radial": random.randint(5,8), "hexapod": 6, "quadruped": 4, "biped": 2}
        limbs = limb_map.get(body_type, 4)
        
        # Fuente de energía
        if env.temperature > 25 and env.humidity > 60:
            energy = "photosynthesis"
        elif env.pressure < 400:
            energy = "chemosynthesis"
        elif env.resources > 7:
            energy = random.choice(["predation", "scavenging"])
        else:
            energy = "scavenging"
        
        # Adaptaciones
        adaptations = []
        if env.temperature < -20: adaptations.append("antifreeze_blood")
        if env.temperature > 40: adaptations.append("heat_dissipation")
        if env.altitude > 5000: adaptations.append("enhanced_oxygen")
        if env.humidity > 90: adaptations.append("gill_slits")
        if not adaptations: adaptations.append("generalist")
        
        # Reglas WFC simplificadas
        rules = {
            "head": ["body", "spine"],
            "body": ["head", "body", "limb", "tail", "spine"],
            "limb": ["body"],
            "tail": ["body"],
            "spine": ["head", "body", "tail"],
            "habitat": ["habitat", "body"],
            "empty": ["empty", "habitat"]
        }
        
        # Pesos
        weights = {
            "head": 0.1, "body": 0.4, "limb": 0.3 if limbs > 0 else 0.05,
            "tail": 0.15, "spine": 0.25, "habitat": 0.5, "empty": 0.7
        }
        
        # Nombre
        prefixes = {"cold": "Frost", "hot": "Blaze", "wet": "Aqua", "dry": "Dust", "high": "Peak", "low": "Deep"}
        bodies = {"serpentine": "Wyrm", "quadruped": "Beast", "biped": "Walker", "hexapod": "Skitterer", "radial": "Bloom"}
        
        prefix = "Wild"
        if env.temperature < 0: prefix = "Frost"
        elif env.temperature > 30: prefix = "Blaze"
        elif env.humidity > 70: prefix = "Aqua"
        
        name = f"{prefix}{bodies.get(body_type, 'Creature')}{armor.capitalize()}"
        
        return CreatureCard(
            id=f"CRE_{self.counter:04d}", name=name, body_type=body_type,
            limbs=limbs, armor_type=armor, energy_source=energy,
            adaptations=adaptations, adjacency_rules=rules, weights=weights
        )

# ============================================================================
# FASE 2: WFC RÁPIDO
# ============================================================================

class FastWFC:
    def __init__(self, width=40, height=25):
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)]
        self.possibilities = [[set() for _ in range(width)] for _ in range(height)]
        self.collapsed = [[False for _ in range(width)] for _ in range(height)]
    
    def initialize(self, card: CreatureCard):
        """Inicializar con semillas"""
        all_tiles = list(card.adjacency_rules.keys())
        cx, cy = self.width // 2, self.height // 2
        
        for y in range(self.height):
            for x in range(self.width):
                dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                max_dist = math.sqrt(cx**2 + cy**2)
                
                probs = set()
                for tile in all_tiles:
                    weight = card.weights.get(tile, 0.5)
                    if tile in ["head", "body", "limb", "tail", "spine"]:
                        prob = weight * (1 - dist/max_dist) * 2
                    else:
                        prob = weight * (dist/max_dist) * 0.8
                    
                    if prob > 0.3 or random.random() < 0.3:
                        probs.add(tile)
                
                self.possibilities[y][x] = probs if probs else {"empty", "habitat"}
    
    def get_entropy(self, x: int, y: int) -> float:
        if self.collapsed[y][x]: return 0
        n = len(self.possibilities[y][x])
        return n if n > 0 else float('inf')
    
    def find_min_entropy(self) -> Optional[Tuple[int, int]]:
        min_ent = float('inf')
        candidates = []
        
        for y in range(self.height):
            for x in range(self.width):
                if not self.collapsed[y][x]:
                    ent = self.get_entropy(x, y)
                    if ent < min_ent:
                        min_ent = ent
                        candidates = [(x, y)]
                    elif ent == min_ent:
                        candidates.append((x, y))
        
        return random.choice(candidates) if candidates else None
    
    def collapse(self, x: int, y: int, card: CreatureCard):
        poss = list(self.possibilities[y][x])
        if not poss:
            self.grid[y][x] = "empty"
        else:
            weights = [card.weights.get(p, 0.5) for p in poss]
            total = sum(weights)
            r = random.random() * total
            cumsum = 0
            chosen = poss[-1]
            for p, w in zip(poss, weights):
                cumsum += w
                if r <= cumsum:
                    chosen = p
                    break
            self.grid[y][x] = chosen
        
        self.collapsed[y][x] = True
        self.possibilities[y][x] = {self.grid[y][x]}
    
    def propagate(self, start_x: int, start_y: int, card: CreatureCard):
        stack = [(start_x, start_y)]
        visited = set()
        
        while stack and len(visited) < 100:
            x, y = stack.pop()
            if (x, y) in visited: continue
            visited.add((x, y))
            
            if not self.collapsed[y][x]: continue
            
            value = self.grid[y][x]
            allowed = set(card.adjacency_rules.get(value, []))
            
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and not self.collapsed[ny][nx]:
                    old = self.possibilities[ny][nx].copy()
                    new = old & (allowed | {tile for tile in card.adjacency_rules if value in card.adjacency_rules.get(tile, [])})
                    
                    if new != old:
                        self.possibilities[ny][nx] = new if new else {"empty"}
                        stack.append((nx, ny))
    
    def run(self, card: CreatureCard, max_iter=800) -> bool:
        for i in range(max_iter):
            pos = self.find_min_entropy()
            if not pos: return True
            
            x, y = pos
            self.collapse(x, y, card)
            self.propagate(x, y, card)
            
            if i % 100 == 0:
                remaining = sum(1 for row in self.collapsed for c in row if not c)
                if remaining == 0: return True
        
        return True
    
    def render(self) -> str:
        visuals = {
            "head": (C.RED, "◉"), "body": (C.GREEN, "█"), "limb": (C.YELLOW, "▌"),
            "tail": (C.MAGENTA, "▼"), "spine": (C.WHITE, "║"),
            "habitat": (C.BLUE, "·"), "empty": (C.RESET, " ")
        }
        
        lines = [C.CYAN + "╔" + "═" * (self.width*2-1) + "╗" + C.RESET]
        
        for row in self.grid:
            line = C.CYAN + "║" + C.RESET
            for tile in row:
                color, char = visuals.get(tile or "empty", (C.RESET, " "))
                line += f"{color}{char}{C.RESET} "
            line += C.CYAN + "║" + C.RESET
            lines.append(line)
        
        lines.append(C.CYAN + "╚" + "═" * (self.width*2-1) + "╝" + C.RESET)
        return "\n".join(lines)

# ============================================================================
# SISTEMA PRINCIPAL
# ============================================================================

def generate_creature(env: EnvVars):
    engine = EcoEngine()
    card = engine.generate(env)
    
    print(f"\n{C.BOLD}{C.CYAN}🧬 CREATURE GENERATED{C.RESET}")
    print(f"{C.BOLD}Name:{C.RESET} {C.CYAN}{card.name}{C.RESET}")
    print(f"{C.BOLD}Type:{C.RESET} {card.body_type} | {C.BOLD}Limbs:{C.RESET} {card.limbs}")
    print(f"{C.BOLD}Armor:{C.RESET} {card.armor_type} | {C.BOLD}Energy:{C.RESET} {card.energy_source}")
    print(f"{C.BOLD}Adaptations:{C.RESET} {', '.join(card.adaptations)}")
    
    print(f"\n{C.GREEN}🎨 Running WFC...{C.RESET}")
    wfc = FastWFC(width=40, height=22)
    wfc.initialize(card)
    wfc.run(card)
    
    print(f"\n{C.BOLD}🦎 VISUALIZATION:{C.RESET}")
    print(wfc.render())
    
    print(f"\n{C.BOLD}📊 LEGEND:{C.RESET}")
    print(f"  {C.RED}◉{C.RESET} Head  {C.GREEN}█{C.RESET} Body  {C.YELLOW}▌{C.RESET} Limb  {C.MAGENTA}▼{C.RESET} Tail  {C.WHITE}║{C.RESET} Spine  {C.BLUE}·{C.RESET} Habitat")
    
    return card, wfc

def demo():
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print(f"{C.BOLD}{C.CYAN}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║   FAST CREATURE GENERATOR with WAVE FUNCTION COLLAPSE    ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{C.RESET}\n")
    
    environments = [
        ("❄️ Alpine", EnvVars(-25, 30, 5500, 450, 4)),
        ("🌴 Jungle", EnvVars(35, 85, 100, 1010, 8)),
        ("🏜️ Desert", EnvVars(45, 15, 200, 1000, 3)),
        ("🌊 Ocean", EnvVars(5, 95, -200, 1100, 6)),
    ]
    
    for name, env in environments:
        print(f"\n{C.BOLD}{C.MAGENTA}{'='*60}{C.RESET}")
        print(f"{C.BOLD}{name} Environment:{C.RESET}")
        print(f"  Temp: {env.temperature}°C | Humidity: {env.humidity}% | Alt: {env.altitude}m")
        print(f"  Pressure: {env.pressure} hPa | Resources: {env.resources}/10")
        
        generate_creature(env)
        
        #input(f"\n{C.CYAN}⏎ Press Enter for next creature...{C.RESET}")
        os.system('clear' if os.name == 'posix' else 'cls')
    
    print(f"\n{C.GREEN}✨ Demo complete!{C.RESET}\n")

if __name__ == "__main__":
    demo()
