"""
Configurações para os sprites do jogo
"""

# Configurações do Player (Sung Jin-Woo)
PLAYER_SPRITE = {
    "dimensions": {
        "width": 50,  # Largura base de cada frame (será multiplicada pelo scale)
        "height": 37,  # Altura base de cada frame (será multiplicada pelo scale)
        "rows": 6,    # Total de linhas no sprite sheet
        "columns": 10,  # Total de colunas no sprite sheet
        "scale": 2.0   # Aumentado para 2.0 para sprites maiores
    },
    "animations": {
        "idle": {
            "row": 0,
            "frames": 4,
            "duration": 120  # Reduzido para ser mais responsivo
        },
        "running": {
            "row": 1,
            "frames": 6,
            "duration": 80   # Mais rápido para movimento mais fluido
        },
        "jumping": {
            "row": 2,
            "frames": 2,
            "duration": 100
        },
        "falling": {
            "row": 2,
            "frames": 2,
            "duration": 100
        },
        "attacking": {
            "row": 4,    # Trocado com magia (era 3)
            "frames": 4,
            "duration": 80   # Mais rápido para ataques mais responsivos
        },
        "magic": {
            "row": 3,    # Trocado com ataque (era 4)
            "frames": 4,
            "duration": 100
        },
        "hurt": {
            "row": 5,
            "frames": 2,
            "duration": 100
        },
        "death": {
            "row": 5,
            "frames": 4,
            "duration": 150
        },
        "dash": {
            "row": 6,
            "frames": 3,
            "duration": 80
        }
    },
    "colors": {
        "primary": (40, 40, 40),     # Preto/Cinza escuro para roupas
        "secondary": (128, 0, 255),   # Roxo para detalhes mágicos
        "skin": (255, 220, 177),      # Tom de pele
        "hair": (40, 40, 40),         # Cabelo preto
        "effects": (128, 0, 255)      # Roxo para efeitos de sombra
    },
    "effects": {
        "attack": {
            "color": (128, 0, 255),    # Roxo para ataque corpo a corpo
            "alpha": 200,              # Transparência mais alta
            "particles": True,         # Efeito de partículas
            "trail_length": 5,         # Rastro mais longo
            "glow": True              # Efeito de brilho
        },
        "magic": {
            "color": (255, 255, 100),  # Amarelo brilhante para magia
            "alpha": 180,              # Transparência
            "particles": True,         # Efeito de partículas
            "trail_length": 3,         # Rastro mais curto
            "glow": False             # Sem efeito de brilho
        }
    }
}

# Configurações do Inimigo
ENEMY_SPRITE = {
    "dimensions": {
        "width": 120,
        "height": 80,
        "scale": 1.0,
        "columns": 8,
        "rows": 1
    },
    "animations": {
        "idle": {
            "row": 0,
            "frames": 4,
            "duration": 200
        },
        "walking": {
            "row": 0,
            "frames": 6,
            "duration": 150
        },
        "running": {
            "row": 0,
            "frames": 6,
            "duration": 120
        },
        "jumping": {
            "row": 0,
            "frames": 4,
            "duration": 150
        },
        "attacking": {
            "row": 0,
            "frames": 6,
            "duration": 120
        },
        "attacking2": {
            "row": 0,
            "frames": 6,
            "duration": 120
        },
        "attacking3": {
            "row": 0,
            "frames": 6,
            "duration": 120
        },
        "hurt": {
            "row": 0,
            "frames": 3,
            "duration": 150
        },
        "death": {
            "row": 0,
            "frames": 4,
            "duration": 200
        }
    },
    "behavior": {
        "speed": 3,
        "jump_force": 10,
        "attack_range": 60,
        "aggro_range": 300,
        "attack_damage": 8,
        "attack_duration": 30,
        "knockback": 5,
        "howl_cooldown": 90,
        "random_movement": {
            "enabled": True,
            "change_direction_chance": 0.02,
            "idle_chance": 0.01
        }
    },
    "effects": {
        "attack": {
            "color": (255, 50, 50),
            "alpha": 160,
            "size": [60, 40],
            "particles": True,
            "particle_count": 5
        },
        "hurt": {
            "color": (255, 255, 255),
            "alpha": 160,
            "particles": True,
            "particle_count": 5
        }
    }
} 