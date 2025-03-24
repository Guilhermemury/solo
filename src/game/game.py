import pygame
import time
from ..menus.menu import Menu, OptionsMenu, CreditsMenu
from ..sprites.sprite_config import PLAYER_SPRITE, ENEMY_SPRITE
from ..sprites.sprite_manager import SpriteSheet
from ..utils.effects import EffectManager

class Game:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Configurações do tutorial
        self.tutorial_font = pygame.font.SysFont("Arial", 20)
        self.tutorial_start_time = time.time()
        self.tutorial_duration = 30
        self.tutorial_alpha = 255
        self.tutorial_fade_speed = 5
        
        # Comandos do tutorial
        self.tutorial_commands = [
            "Comandos:",
            "Setas ← → - Mover",
            "Espaço - Pular",
            "X - Atacar",
            "C - Magia",
            "Shift - Dash",
            "V - Escudo",
            "ESC - Menu"
        ]
        
        # Pré-renderizar textos do tutorial
        self.tutorial_texts = []
        self.tutorial_shadows = []
        for command in self.tutorial_commands:
            # Título em vermelho, outros textos em branco
            color = (200, 40, 40) if command == "Comandos:" else (220, 220, 220)
            text = self.tutorial_font.render(command, True, color)
            shadow = self.tutorial_font.render(command, True, (20, 20, 20))
            self.tutorial_texts.append(text)
            self.tutorial_shadows.append(shadow)
        
        # Superfície do fundo do tutorial
        self.tutorial_bg = pygame.Surface((200, 200))  # Aumentado para acomodar mais linhas
        self.tutorial_bg.fill((30, 30, 30))
        
        # Resto das inicializações do jogo aqui...
    
    def update(self):
        # Atualizar tutorial
        elapsed_time = time.time() - self.tutorial_start_time
        if elapsed_time >= self.tutorial_duration - 3:  # Começar fade out 3 segundos antes
            self.tutorial_alpha = max(0, self.tutorial_alpha - self.tutorial_fade_speed)
        
        # Resto das atualizações do jogo aqui...
    
    def draw(self, surface):
        # Desenhar elementos do jogo primeiro...
        
        # Desenhar tutorial se ainda estiver visível
        if self.tutorial_alpha > 0:
            # Desenhar fundo semi-transparente
            tutorial_bg_copy = self.tutorial_bg.copy()
            tutorial_bg_copy.set_alpha(int(self.tutorial_alpha * 0.6))
            surface.blit(tutorial_bg_copy, (10, 10))
            
            # Desenhar textos do tutorial
            y = 20
            for i, (text, shadow) in enumerate(zip(self.tutorial_texts, self.tutorial_shadows)):
                # Criar cópias para aplicar transparência
                text_copy = text.copy()
                shadow_copy = shadow.copy()
                text_copy.set_alpha(self.tutorial_alpha)
                shadow_copy.set_alpha(self.tutorial_alpha)
                
                # Desenhar sombra e texto
                surface.blit(shadow_copy, (22, y + 2))
                surface.blit(text_copy, (20, y))
                y += 25  # Espaçamento entre linhas 