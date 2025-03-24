import pygame
import sys
import random
import math
import os
from src.menus.menu import Menu, OptionsMenu, CreditsMenu
from src.sprites.sprite_config import PLAYER_SPRITE, ENEMY_SPRITE
from src.sprites.sprite_manager import SpriteSheet
from src.utils.effects import EffectManager

# Função para resolver caminhos de recursos
def get_resource_path(relative_path):
    try:
        # PyInstaller cria um temp folder e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Inicialização do Pygame
pygame.init()

# Configurações da tela
WIDTH, HEIGHT = 800, 600
SECTION_WIDTH = WIDTH * 3  # Largura total do mapa (3 seções em vez de 2)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Solo Leveling - Demo")

# Estados do jogo
MENU = 'menu'
OPTIONS = 'options'
CREDITS = 'credits'
CONTROLS = 'controls'
PLAYING = 'playing'
GAME_OVER = 'game_over'

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
DARK_RED = (139, 0, 0)
DARK_GREEN = (0, 100, 0)

# Criar menus
main_menu = Menu(WIDTH, HEIGHT)
options_menu = OptionsMenu(WIDTH, HEIGHT)
credits_menu = CreditsMenu(WIDTH, HEIGHT)

# Estado atual do jogo
current_state = MENU

# Carregar tileset do Oak Woods
try:
    # Carregar o tileset do Oak Woods
    oak_woods_tileset = pygame.image.load(get_resource_path("assets/oak_woods_v1.0/oak_woods_tileset.png")).convert_alpha()
    
    # Extrair tiles para plataforma (segunda imagem do sprite sheet)
    platform_tile_left = oak_woods_tileset.subsurface((0, 16, 16, 16))  # Tile esquerdo
    platform_tile_middle = oak_woods_tileset.subsurface((16, 16, 16, 16))  # Tile do meio
    platform_tile_right = oak_woods_tileset.subsurface((32, 16, 16, 16))  # Tile direito
    
    # Extrair tiles para o chão (tiles de terra)
    ground_tile_top = oak_woods_tileset.subsurface((16, 32, 16, 16))  # Tile de terra superior
    ground_tile_bottom = oak_woods_tileset.subsurface((16, 48, 16, 16))  # Tile de terra inferior
    
    # Escalar os tiles para o tamanho desejado
    TILE_SCALE = 2
    platform_tile_left = pygame.transform.scale(platform_tile_left, (16 * TILE_SCALE, 16 * TILE_SCALE))
    platform_tile_middle = pygame.transform.scale(platform_tile_middle, (16 * TILE_SCALE, 16 * TILE_SCALE))
    platform_tile_right = pygame.transform.scale(platform_tile_right, (16 * TILE_SCALE, 16 * TILE_SCALE))
    ground_tile_top = pygame.transform.scale(ground_tile_top, (16 * TILE_SCALE, 16 * TILE_SCALE))
    ground_tile_bottom = pygame.transform.scale(ground_tile_bottom, (16 * TILE_SCALE, 16 * TILE_SCALE))
except Exception as e:
    print(f"Erro ao carregar o tileset do Oak Woods: {e}")
    # Fallback para cores sólidas
    platform_image = pygame.Surface((120, 30))
    platform_image.fill((40, 40, 60))
    ground_image = pygame.Surface((WIDTH, 50))
    ground_image.fill(BROWN)

# Variáveis globais
camera_scroll = 0  # Posição da câmera
MAX_SCROLL = SECTION_WIDTH - WIDTH  # Máximo que a câmera pode rolar

# Carregar background
try:
    background = pygame.image.load(get_resource_path("assets/backgrounds/city 1/1.png")).convert()
    # Redimensionar o background para caber na tela
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except:
    # Fallback para um background simples
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill((100, 150, 200))  # Azul claro

# Carregar sprite sheets
try:
    player_sprite_sheet = SpriteSheet(get_resource_path("assets/player.png"))
    print("Carregando sprite sheet do inimigo...")
    enemy_sprite_sheet = SpriteSheet(get_resource_path("assets/enemy/Idle.png"))
    print("Sprite sheet do inimigo carregado com sucesso")
    
    # Configurar dimensões do sprite sheet do inimigo
    ENEMY_SPRITE["dimensions"]["width"] = 64
    ENEMY_SPRITE["dimensions"]["height"] = 64
    ENEMY_SPRITE["dimensions"]["scale"] = 1.5
    platform_image = pygame.image.load(get_resource_path("assets/dark_stone_platform.png")).convert_alpha()
    platform_image = pygame.transform.scale(platform_image, (120, 30))
except Exception as e:
    print(f"Erro ao carregar sprite sheets: {str(e)}")
    print("Usando fallback para o sprite do inimigo")
    # Fallback para sprites básicos caso os arquivos não existam
    scaled_width = int(PLAYER_SPRITE["dimensions"]["width"] * PLAYER_SPRITE["dimensions"]["scale"])
    scaled_height = int(PLAYER_SPRITE["dimensions"]["height"] * PLAYER_SPRITE["dimensions"]["scale"])
    player_image = pygame.Surface((scaled_width, scaled_height))
    player_image.fill(BLUE)
    
    scaled_width = int(ENEMY_SPRITE["dimensions"]["width"] * ENEMY_SPRITE["dimensions"]["scale"])
    scaled_height = int(ENEMY_SPRITE["dimensions"]["height"] * ENEMY_SPRITE["dimensions"]["scale"])
    enemy_image = pygame.Surface((scaled_width, scaled_height))
    enemy_image.fill(RED)
    
    # Fallback para plataforma
    platform_image = pygame.Surface((120, 30))
    platform_image.fill((40, 40, 60))  # Cor escura para representar pedra obscura
    
    # Adicionar alguns detalhes à plataforma
    pygame.draw.line(platform_image, (60, 60, 80), (0, 0), (120, 0), 2)  # Borda superior
    pygame.draw.line(platform_image, (20, 20, 40), (0, 29), (120, 29), 2)  # Borda inferior
    for x in range(0, 120, 20):  # Adicionar alguns detalhes
        pygame.draw.circle(platform_image, (50, 50, 70), (x + 10, 15), 3)

ground_image = pygame.Surface((WIDTH, 50))
ground_image.fill(BROWN)

attack_image = pygame.Surface((70, 20))
attack_image.fill(YELLOW)

# Criar gerenciador de efeitos
effect_manager = EffectManager()

# Classe do Jogador
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Obter dimensões e escala do config
        self.frame_width = PLAYER_SPRITE["dimensions"]["width"]
        self.frame_height = PLAYER_SPRITE["dimensions"]["height"]
        self.scale = PLAYER_SPRITE["dimensions"]["scale"]
        
        # Adicionar referência ao effect_manager
        self.effect_manager = effect_manager
        
        self.load_animations()
        self.current_frame = 0
        self.animation_timer = pygame.time.get_ticks()
        self.animation_speed = 0.2  # Velocidade base da animação
        self.state = "idle"
        self.previous_state = "idle"
        self.image = self.animations["idle"][0].copy()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Ajustar velocidades baseado na escala
        self.speed = 5 * self.scale
        self.vel_y = 0
        self.gravity = 0.5 * self.scale
        
        self.facing_right = True
        self.attacking = False
        self.casting = False
        self.dashing = False
        self.attack_cooldown = 0
        self.cast_cooldown = 0
        self.dash_cooldown = 0
        self.health = 150  # Aumentado de 100 para 150
        self.max_health = 150  # Aumentado de 100 para 150
        
        # Sistema de mana
        self.mana = 120  # Aumentado de 100 para 120
        self.max_mana = 120  # Aumentado de 100 para 120
        self.mana_regen = 0.15  # Aumentado de 0.1 para 0.15
        self.magic_cost = 30
        self.dash_cost = 20
        self.shield_cost = 35  # Reduzido de 40 para 35
        
        # Sistema de escudo
        self.shield_active = False
        self.shield_cooldown = 0
        self.shield_duration = 180  # 3 segundos a 60 FPS
        self.shield_alpha = 0
        self.shield_radius = 40
        
        # Sistema de pontuação
        self.score = 0
        
        # Posição real no mundo (para scroll)
        self.world_x = x
        
        # Criar trail para dash
        effect_manager.create_trail('player_dash', PLAYER_SPRITE["effects"]["magic"]["color"])
        
        # Limites do mapa
        self.map_limits = {
            'left': 0,
            'right': SECTION_WIDTH - self.rect.width
        }

        # Atributos do efeito mágico
        self.magic_shield_cost = 35
        self.magic_shield_active = False
        self.magic_shield_cooldown = 0
        self.magic_shield_duration = 600  # 10 segundos (60 FPS * 10)
        self.magic_shield_radius = 70
        self.magic_shield_color = (100, 180, 255)
        self.magic_shield_alpha = 100
        self.magic_shield_pulse = 0
        self.magic_shield_pulse_speed = 1.5
        self.magic_shield_wave = 0
        self.magic_shield_wave_speed = 0.05
        self.magic_shield_layers = 5
        self.magic_shield_damage_reduction = 0.5  # Reduz 50% do dano

    def update_animation(self):
        # Atualizar animation_speed baseado no estado atual
        self.animation_speed = PLAYER_SPRITE["animations"][self.state]["duration"] / 1000  # Converter para segundos
        
        # Incrementar o timer de animação
        self.animation_timer += 1
        
        # Atualizar frame se o timer atingir o limite
        if self.animation_timer >= self.animation_speed * 60:  # 60 FPS
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.animations[self.state])
            
            # Obter o próximo frame
            self.image = self.animations[self.state][self.current_frame]
            
            # Aplicar flip se necessário
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
            
            # Ajustar escala
            self.image = pygame.transform.scale(
                self.image,
                (int(self.frame_width * self.scale),
                 int(self.frame_height * self.scale))
            )

    def load_animations(self):
        try:
            # Pré-carregar e armazenar todas as animações com suas cópias
            animations_temp = {}
            for state, config in PLAYER_SPRITE["animations"].items():
                frames = player_sprite_sheet.get_animation_frames(
                    config["row"],
                    config["frames"],
                    self.frame_width,
                    self.frame_height,
                    self.scale
                )
                # Criar cópias de cada frame
                animations_temp[state] = [frame.copy() for frame in frames]
            self.animations = animations_temp
            
        except Exception as e:
            print(f"Erro ao carregar animações: {e}")
            # Fallback para sprite básico
            scaled_width = int(self.frame_width * self.scale)
            scaled_height = int(self.frame_height * self.scale)
            basic_sprite = pygame.Surface((scaled_width, scaled_height))
            basic_sprite.fill(BLUE)
            self.animations = {state: [basic_sprite.copy()] for state in PLAYER_SPRITE["animations"].keys()}

    def update(self, keys, platforms, ground, enemies):
        global camera_scroll
        
        # Regenerar mana
        if self.mana < self.max_mana:
            self.mana = min(self.max_mana, self.mana + self.mana_regen)

        # Determinar estado da animação
        if self.dashing:
            self.state = "dash"
        elif self.attacking:
            self.state = "attacking"
        elif self.casting:
            self.state = "magic"
        elif self.vel_y != 0:
            self.state = "jumping"
        elif keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
            self.state = "running"
        else:
            self.state = "idle"

        # Atualizar animação
        self.update_animation()

        # Atualizar cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            if self.attack_cooldown == 0:
                self.attacking = False

        if self.cast_cooldown > 0:
            self.cast_cooldown -= 1
            if self.cast_cooldown == 0:
                self.casting = False

        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
            if self.dash_cooldown == 0:
                self.dashing = False

        # Gravidade
        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        # Movimento lateral (apenas se não estiver atacando ou lançando magia)
        if not self.attacking and not self.casting:
            old_x = self.rect.x
            if keys[pygame.K_LEFT]:
                self.rect.x -= self.speed
                self.facing_right = False
                self.world_x -= self.speed
            if keys[pygame.K_RIGHT]:
                self.rect.x += self.speed
                self.facing_right = True
                self.world_x += self.speed

            # Atualizar scroll da câmera
            if self.rect.centerx > WIDTH * 0.7 and camera_scroll < MAX_SCROLL:
                diff = self.rect.x - old_x
                camera_scroll = min(camera_scroll + diff, MAX_SCROLL)
                self.rect.x = old_x
            elif self.rect.centerx < WIDTH * 0.3 and camera_scroll > 0:
                diff = old_x - self.rect.x
                camera_scroll = max(camera_scroll - diff, 0)
                self.rect.x = old_x

        # Limites do mapa com scroll
        if self.world_x < self.map_limits['left']:
            self.world_x = self.map_limits['left']
            self.rect.x = self.world_x - camera_scroll
        elif self.world_x > self.map_limits['right']:
            self.world_x = self.map_limits['right']
            self.rect.x = self.world_x - camera_scroll

        # Dash (esquiva rápida)
        if keys[pygame.K_LSHIFT] and self.dash_cooldown == 0 and not self.attacking and not self.casting and self.mana >= self.dash_cost:
            self.dashing = True
            self.dash_cooldown = 45
            self.mana -= self.dash_cost
            dash_speed = 15 * self.scale
            
            # Calcular nova posição após o dash
            new_world_x = self.world_x + (dash_speed if self.facing_right else -dash_speed)
            
            # Verificar limites antes de aplicar o dash
            if self.map_limits['left'] <= new_world_x <= self.map_limits['right']:
                self.world_x = new_world_x
            else:
                self.world_x = self.map_limits['left'] if new_world_x < self.map_limits['left'] else self.map_limits['right']
            
            # Atualizar posição na tela
            self.rect.x = self.world_x - camera_scroll

        # Verificar colisão com plataformas e chão
        for platform in platforms:
            if self.rect.colliderect(platform.collision_rect) and self.vel_y > 0:
                self.rect.bottom = platform.collision_rect.top
                self.vel_y = 0

        if self.rect.colliderect(ground.rect) and self.vel_y > 0:
            self.rect.bottom = ground.rect.top
            self.vel_y = 0

        # Pular
        if keys[pygame.K_SPACE] and self.vel_y == 0:
            self.vel_y = -10 * self.scale

        # Ataque corpo a corpo
        if keys[pygame.K_x] and self.attack_cooldown == 0 and not self.casting and not self.dashing:
            self.attack(enemies)

        # Ataque mágico (poderes das sombras)
        if keys[pygame.K_c] and self.cast_cooldown == 0 and not self.attacking and not self.dashing and self.mana >= self.magic_cost:
            self.cast_magic(enemies)
            self.mana -= self.magic_cost

        # Atualizar trail do dash
        if self.dashing:
            effect_manager.update_trail('player_dash', self.rect.centerx, self.rect.centery)

        # Coletar power-ups
        for power_up in pygame.sprite.spritecollide(self, power_ups, True):
            if power_up.tipo == "vida":
                self.health = min(self.max_health, self.health + power_up.valor)
                # Efeito de cura
                effect_manager.create_particles(
                    self.rect.centerx,
                    self.rect.centery,
                    (220, 40, 40),  # Vermelho
                    count=5,
                    alpha=160,
                    size=3
                )
            elif power_up.tipo == "mana":
                self.mana = min(self.max_mana, self.mana + power_up.valor)
                # Efeito de mana
                effect_manager.create_particles(
                    self.rect.centerx,
                    self.rect.centery,
                    (40, 40, 220),  # Azul
                    count=5,
                    alpha=160,
                    size=3
                )

        # Atualizar cooldown do efeito mágico
        if self.magic_shield_cooldown > 0:
            self.magic_shield_cooldown -= 1
        
        # Atualizar efeito mágico se estiver ativo
        if self.magic_shield_active:
            self.magic_shield_duration -= 1
            
            # Efeito de pulsar mais suave
            self.magic_shield_pulse = (self.magic_shield_pulse + self.magic_shield_pulse_speed) % 360
            pulse_factor = abs(math.sin(math.radians(self.magic_shield_pulse)))
            self.magic_shield_alpha = int(60 + (40 * pulse_factor))  # Variação de transparência mais sutil
            
            # Desativar quando acabar a duração
            if self.magic_shield_duration <= 0:
                self.magic_shield_active = False
                self.magic_shield_cooldown = 90  # 1.5 segundos de cooldown
        
        # Ativar efeito mágico
        if keys[pygame.K_v] and not self.magic_shield_active and self.magic_shield_cooldown == 0 and self.mana >= self.magic_shield_cost:
            self.magic_shield_active = True
            self.magic_shield_duration = 600  # Reseta duração para 10 segundos
            self.mana -= self.magic_shield_cost
            
            # Criar efeito de partículas ao ativar
            for _ in range(20):  # Mais partículas
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(2, 4)
                self.effect_manager.create_particles(
                    self.rect.centerx,
                    self.rect.centery,
                    (150, 200, 255),  # Cor mais clara para as partículas
                    count=1,
                    speed=speed,
                    alpha=180,
                    size=3
                )

    def attack(self, enemies):
        self.attacking = True
        self.attack_cooldown = 30  # ~0.5 segundos a 60 FPS

        # Criar um retângulo de ataque na direção que o personagem está olhando
        attack_width = int(70 * self.scale)
        attack_height = int(50 * self.scale)
        attack_rect = pygame.Rect(0, 0, attack_width, attack_height)
        
        # Posicionar o retângulo de ataque
        if self.facing_right:
            attack_rect.midleft = self.rect.midright
        else:
            attack_rect.midright = self.rect.midleft

        # Criar efeito de rastro do ataque
        attack_points = []
        num_points = 8
        if self.facing_right:
            start_x = self.rect.right
            end_x = start_x + attack_width
        else:
            start_x = self.rect.left
            end_x = start_x - attack_width
            
        for i in range(num_points):
            progress = i / (num_points - 1)
            x = start_x + (end_x - start_x) * progress
            y = self.rect.centery + math.sin(progress * math.pi) * 20
            attack_points.append((x, y))
            
            # Criar partículas ao longo do arco do ataque
            effect_manager.create_particles(
                x, y,
                PLAYER_SPRITE["effects"]["attack"]["color"],
                count=3,
                alpha=200,
                size=3,
                speed=2
            )

        # Verificar colisões do ataque com inimigos
        for enemy in enemies:
            if attack_rect.colliderect(enemy.rect):
                enemy.take_damage(30)
                # Criar explosão de partículas no ponto de impacto
                for _ in range(3):  # Três conjuntos de partículas para mais impacto
                    effect_manager.create_particles(
                        enemy.rect.centerx + random.randint(-15, 15),
                        enemy.rect.centery + random.randint(-15, 15),
                        PLAYER_SPRITE["effects"]["attack"]["color"],
                        count=12,  # Mais partículas
                        alpha=230,  # Alpha mais alto
                        size=5,  # Partículas maiores
                        speed=6  # Velocidade maior
                    )

    def cast_magic(self, enemies):
        self.casting = True
        self.cast_cooldown = 45  # ~0.75 segundos

        # Criar um retângulo de ataque maior que o ataque corpo a corpo
        attack_width = int(100 * self.scale)
        attack_height = int(80 * self.scale)
        attack_rect = pygame.Rect(0, 0, attack_width, attack_height)
        
        if self.facing_right:
            attack_rect.midleft = self.rect.midright
        else:
            attack_rect.midright = self.rect.midleft

        # Criar efeito de energia mágica em espiral
        center_x = attack_rect.centerx
        center_y = attack_rect.centery
        radius = 30
        num_points = 12
        for i in range(num_points):
            angle = (i / num_points) * math.pi * 2
            for r in range(0, radius, 5):
                x = center_x + math.cos(angle) * r
                y = center_y + math.sin(angle) * r
                effect_manager.create_particles(
                    x, y,
                    PLAYER_SPRITE["effects"]["magic"]["color"],
                    count=2,
                    alpha=200,
                    size=4,
                    speed=3
                )

        # Verificar colisões do ataque com inimigos
        for enemy in enemies:
            if attack_rect.colliderect(enemy.rect):
                enemy.take_damage(45)
                # Criar explosão mágica no ponto de impacto
                for _ in range(3):  # Três camadas de efeitos
                    # Círculo interno de partículas
                    effect_manager.create_particles(
                        enemy.rect.centerx,
                        enemy.rect.centery,
                        PLAYER_SPRITE["effects"]["magic"]["color"],
                        count=15,  # Mais partículas
                        alpha=230,  # Alpha mais alto
                        size=6,  # Partículas maiores
                        speed=7  # Velocidade maior
                    )
                    
                    # Círculo externo com cor mais clara
                    bright_color = tuple(min(c + 50, 255) for c in PLAYER_SPRITE["effects"]["magic"]["color"])
                    effect_manager.create_particles(
                        enemy.rect.centerx,
                        enemy.rect.centery,
                        bright_color,
                        count=10,
                        alpha=180,
                        size=4,
                        speed=5
                    )

    def draw_health_bar(self, surface):
        # Configurações das barras
        bar_width = 200
        bar_height = 20
        padding = 10
        
        # Posições das barras
        health_pos = (padding + 35, padding)  # Deslocado para direita para acomodar o texto
        mana_pos = (padding + 35, padding + bar_height + 5)  # Deslocado para direita para acomodar o texto
        
        # Função auxiliar para desenhar barra arredondada
        def draw_rounded_bar(pos, width, height, color, progress):
            full_rect = pygame.Rect(pos[0], pos[1], width, height)
            progress_width = int(width * progress)
            progress_rect = pygame.Rect(pos[0], pos[1], progress_width, height)
            
            # Desenhar fundo escuro
            pygame.draw.rect(surface, (40, 40, 40), full_rect, border_radius=height//2)
            # Desenhar barra de progresso
            if progress_width > 0:
                pygame.draw.rect(surface, color, progress_rect, border_radius=height//2)
            # Desenhar borda
            pygame.draw.rect(surface, (100, 100, 100), full_rect, 2, border_radius=height//2)
        
        # Função auxiliar para desenhar texto com sombra
        def draw_text_with_shadow(text, pos, color=(255, 255, 255)):
            font = pygame.font.Font(None, 24)
            # Sombra
            shadow = font.render(text, True, (0, 0, 0))
            surface.blit(shadow, (pos[0] + 1, pos[1] + 1))
            # Texto
            rendered = font.render(text, True, color)
            surface.blit(rendered, pos)
        
        # Desenhar indicadores HP e MP primeiro
        hp_text_pos = (padding, health_pos[1] + 2)  # +2 para alinhar verticalmente
        mp_text_pos = (padding, mana_pos[1] + 2)
        draw_text_with_shadow("HP", hp_text_pos, (220, 50, 50))
        draw_text_with_shadow("MP", mp_text_pos, (50, 50, 220))
        
        # Desenhar barras
        draw_rounded_bar(health_pos, bar_width, bar_height,
                        (200, 50, 50), self.health / self.max_health)
        draw_rounded_bar(mana_pos, bar_width, bar_height,
                        (50, 50, 200), self.mana / self.max_mana)
        
        # Textos dos valores
        health_text = f"{int(self.health)}/{self.max_health}"
        mana_text = f"{int(self.mana)}/{self.max_mana}"
        
        # Posições dos textos de valores (à direita das barras)
        text_padding = 5
        health_text_pos = (health_pos[0] + bar_width + text_padding, health_pos[1])
        mana_text_pos = (mana_pos[0] + bar_width + text_padding, mana_pos[1])
        
        # Desenhar textos dos valores
        draw_text_with_shadow(health_text, health_text_pos)
        draw_text_with_shadow(mana_text, mana_text_pos)

    def draw(self, surface, camera_offset):
        # Desenhar efeito mágico
        if self.magic_shield_active:
            # Criar superfície para a bolha com gradiente
            shield_surface = pygame.Surface((self.magic_shield_radius * 2, self.magic_shield_radius * 2), pygame.SRCALPHA)
            
            # Atualizar efeito de ondulação
            self.magic_shield_wave += self.magic_shield_wave_speed
            
            # Desenhar múltiplas camadas para criar efeito de aura
            for i in range(self.magic_shield_layers):
                # Calcular raio e ondulação para cada camada
                layer_radius = self.magic_shield_radius - (i * 8)
                wave_offset = math.sin(self.magic_shield_wave + i * math.pi/2) * 4
                
                # Desenhar círculos concêntricos com ondulação
                for r in range(layer_radius, 0, -2):
                    # Calcular alpha baseado na distância do centro
                    alpha = int(self.magic_shield_alpha * (r / layer_radius) * 0.9)
                    current_radius = r + wave_offset
                    
                    # Desenhar círculo com cor variável baseada na distância
                    color = (
                        int(self.magic_shield_color[0] * (0.8 + 0.2 * (r / layer_radius))),
                        int(self.magic_shield_color[1] * (0.8 + 0.2 * (r / layer_radius))),
                        int(self.magic_shield_color[2] * (0.8 + 0.2 * (r / layer_radius)))
                    )
                    
                    pygame.draw.circle(shield_surface, (*color, alpha),
                                     (self.magic_shield_radius, self.magic_shield_radius),
                                     current_radius)
            
            # Adicionar brilho externo mais intenso
            glow_radius = self.magic_shield_radius + 8
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            
            # Criar gradiente de brilho mais suave
            for r in range(glow_radius, 0, -1):
                alpha = int((r / glow_radius) * self.magic_shield_alpha * 0.5)
                glow_color = (
                    int(self.magic_shield_color[0] * 1.2),
                    int(self.magic_shield_color[1] * 1.2),
                    int(self.magic_shield_color[2] * 1.2)
                )
                pygame.draw.circle(glow_surface, (*glow_color, alpha),
                                 (glow_radius, glow_radius),
                                 r)
            
            # Posicionar os efeitos
            shield_pos = (self.rect.centerx - self.magic_shield_radius - camera_offset,
                        self.rect.centery - self.magic_shield_radius)
            glow_pos = (self.rect.centerx - glow_radius - camera_offset,
                       self.rect.centery - glow_radius)
            
            # Desenhar os efeitos
            surface.blit(glow_surface, glow_pos)
            surface.blit(shield_surface, shield_pos)
            
            # Criar partículas de proteção mais frequentes
            if random.random() < 0.4:  # 40% de chance de criar partículas a cada frame
                angle = random.uniform(0, math.pi * 2)
                x = self.rect.centerx + math.cos(angle) * self.magic_shield_radius
                y = self.rect.centery + math.sin(angle) * self.magic_shield_radius
                self.effect_manager.create_particles(
                    x, y,
                    (150, 200, 255),  # Cor mais clara para as partículas
                    count=2,  # Mais partículas
                    speed=1.5,  # Velocidade um pouco maior
                    alpha=150,  # Alpha mais alto
                    size=3  # Tamanho um pouco maior
                )

    def take_damage(self, damage):
        # Reduzir dano se o escudo estiver ativo
        if self.magic_shield_active:
            damage = int(damage * self.magic_shield_damage_reduction)
            # Criar efeito de partículas ao receber dano com escudo
            self.effect_manager.create_particles(
                self.rect.centerx,
                self.rect.centery,
                (150, 200, 255),
                count=8,
                alpha=150,
                size=2
            )
        
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.is_dead = True
            self.current_state = "death"
            self.current_frame = 0


# Classe da Plataforma
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Criar superfície para a plataforma
        self.width = 120
        self.height = 32  # Altura ajustada para o novo tile
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        try:
            # Desenhar os tiles na plataforma
            num_middle_tiles = (self.width - 64) // 32  # Número de tiles do meio necessários
            
            # Desenhar tile esquerdo
            self.image.blit(platform_tile_left, (0, 0))
            
            # Desenhar tiles do meio
            for i in range(num_middle_tiles):
                self.image.blit(platform_tile_middle, ((i + 1) * 32, 0))
            
            # Desenhar tile direito
            self.image.blit(platform_tile_right, (self.width - 32, 0))
            
        except:
            self.image.fill((40, 40, 60))
            pygame.draw.line(self.image, (60, 60, 80), (0, 0), (self.width, 0), 2)
            pygame.draw.line(self.image, (20, 20, 40), (0, self.height-1), (self.width, self.height-1), 2)
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.initial_x = x
        self.world_x = x  # Adicionar posição mundial
        
        # Criar uma hitbox mais precisa para colisões
        self.collision_rect = pygame.Rect(x, y + 5, self.width, self.height - 10)
    
    def update(self):
        # Atualizar a hitbox de colisão junto com a posição da plataforma
        self.collision_rect.x = self.rect.x
        self.collision_rect.y = self.rect.y + 5
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # Desenhar a hitbox apenas em modo debug (opcional)
        # pygame.draw.rect(surface, (255, 0, 0), self.collision_rect, 1)


# Classe do Chão
class Ground(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((SECTION_WIDTH, 64))  # Altura ajustada para os tiles
        self.image.set_colorkey((0, 0, 0))  # Tornar o fundo transparente
        
        try:
            # Preencher o chão com os tiles de terra
            for x in range(0, SECTION_WIDTH, 32):  # 32 é a largura do tile escalado
                # Primeira fileira (superior)
                self.image.blit(ground_tile_top, (x, 0))
                # Segunda fileira (inferior)
                self.image.blit(ground_tile_bottom, (x, 32))
        except:
            self.image.fill(BROWN)
        
        self.rect = self.image.get_rect(topleft=(0, HEIGHT - 64))
        self.initial_x = 0
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)


# Classe da Tela de Game Over
class GameOverScreen:
    def __init__(self):
        self.font_big = pygame.font.SysFont(None, 72)
        self.font_small = pygame.font.SysFont(None, 36)
        
        # Textos
        self.text_game_over = self.font_big.render("GAME OVER", True, RED)
        self.text_continue = self.font_small.render("Pressione ENTER para continuar", True, WHITE)
        self.text_quit = self.font_small.render("Pressione ESC para sair", True, WHITE)
        
        # Posições
        self.game_over_pos = (WIDTH // 2 - self.text_game_over.get_width() // 2, HEIGHT // 3)
        self.continue_pos = (WIDTH // 2 - self.text_continue.get_width() // 2, HEIGHT // 2)
        self.quit_pos = (WIDTH // 2 - self.text_quit.get_width() // 2, HEIGHT // 2 + 50)
        
        # Overlay semi-transparente
        self.overlay = pygame.Surface((WIDTH, HEIGHT))
        self.overlay.fill(BLACK)
        self.overlay.set_alpha(180)
    
    def draw(self, surface):
        # Desenhar overlay
        surface.blit(self.overlay, (0, 0))
        
        # Desenhar textos
        surface.blit(self.text_game_over, self.game_over_pos)
        surface.blit(self.text_continue, self.continue_pos)
        surface.blit(self.text_quit, self.quit_pos)


# Classe do Inimigo
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, player, platforms):
        super().__init__()
        self.player = player
        self.platforms = platforms
        
        # Configurações do sprite
        self.sprite_config = {
            "width": ENEMY_SPRITE["dimensions"]["width"],
            "height": ENEMY_SPRITE["dimensions"]["height"],
            "scale": ENEMY_SPRITE["dimensions"]["scale"],
            "columns": ENEMY_SPRITE["dimensions"]["columns"]
        }
        
        # Configurações de vida e pontos
        self.health = 100
        self.max_health = 100
        self.points_value = 50  # Pontos que o jogador ganha ao derrotar este inimigo
        
        # Limites do mapa
        self.map_limits = {
            'left': 0,
            'right': SECTION_WIDTH - int(self.sprite_config["width"] * self.sprite_config["scale"])
        }
        
        # Criar sprite de fallback
        self.fallback_sprite = pygame.Surface((self.sprite_config["width"], self.sprite_config["height"]))
        self.fallback_sprite.fill((255, 0, 0))  # Vermelho para fallback
        self.fallback_sprite = pygame.transform.scale(
            self.fallback_sprite, 
            (int(self.sprite_config["width"] * self.sprite_config["scale"]),
             int(self.sprite_config["height"] * self.sprite_config["scale"]))
        )
        
        # Inicializar animações
        self.animations = {}
        self.load_animations()
        
        # Estado inicial
        self.current_state = "idle"
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.2
        self.direction = 1  # 1 para direita, -1 para esquerda
        
        # Configurações de movimento
        self.speed = 3
        self.gravity = 0.8
        self.velocity_y = 0
        self.jump_force = -15
        
        # Posição inicial
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y  # Usar bottom em vez de y para alinhar com o chão
        self.world_x = x
        
        # Configurações de ataque
        self.attack_range = 100
        self.attack_cooldown = 60
        self.current_cooldown = 0
        
        # Configurações de morte
        self.is_dead = False
        self.death_timer = 0
        self.death_duration = 60
        
        # Trail effect
        self.trail = []
        self.trail_length = 5
        self.trail_timer = 0
        self.trail_interval = 5

    def load_animations(self):
        try:
            print("Iniciando carregamento das animações do inimigo...")
            self.animations = {
                "idle": [],
                "walking": [],
                "running": [],
                "jumping": [],
                "attacking": [],
                "attacking2": [],
                "attacking3": [],
                "hurt": [],
                "death": []
            }

            # Configurações específicas para cada animação
            animation_configs = {
                "idle": {"frames": 4, "width": 128, "height": 128},
                "walking": {"frames": 6, "width": 128, "height": 128},
                "running": {"frames": 6, "width": 128, "height": 128},
                "jumping": {"frames": 4, "width": 128, "height": 128},
                "attacking": {"frames": 6, "width": 128, "height": 128},
                "attacking2": {"frames": 6, "width": 128, "height": 128},
                "attacking3": {"frames": 6, "width": 128, "height": 128},
                "hurt": {"frames": 3, "width": 128, "height": 128},
                "death": {"frames": 4, "width": 128, "height": 128}
            }

            # Carregar cada sprite individual
            sprite_files = {
                "idle": get_resource_path("assets/enemy/Idle.png"),
                "walking": get_resource_path("assets/enemy/Walk.png"),
                "running": get_resource_path("assets/enemy/Run.png"),
                "jumping": get_resource_path("assets/enemy/Jump.png"),
                "attacking": get_resource_path("assets/enemy/Attack_1.png"),
                "attacking2": get_resource_path("assets/enemy/Attack_2.png"),
                "attacking3": get_resource_path("assets/enemy/Attack_3.png"),
                "hurt": get_resource_path("assets/enemy/Hurt.png"),
                "death": get_resource_path("assets/enemy/Dead.png")
            }

            for state, file_path in sprite_files.items():
                try:
                    # Carregar o sprite sheet completo
                    sprite_sheet = pygame.image.load(file_path).convert_alpha()
                    config = animation_configs[state]
                    frames = []
                    
                    # Calcular o número total de frames na imagem
                    sheet_width = sprite_sheet.get_width()
                    frame_width = config["width"]
                    
                    # Extrair cada frame do sprite sheet
                    for i in range(config["frames"]):
                        # Criar uma nova superfície para o frame
                        frame_surface = pygame.Surface((frame_width, config["height"]), pygame.SRCALPHA)
                        
                        # Copiar a região do frame do sprite sheet
                        frame_surface.blit(sprite_sheet, 
                                         (0, 0),  # Destino na nova superfície
                                         (i * frame_width, 0, frame_width, config["height"]))  # Área do sprite sheet
                        
                        # Escalar o frame se necessário
                        scaled_frame = pygame.transform.scale(
                            frame_surface,
                            (int(frame_width * self.sprite_config["scale"]),
                             int(config["height"] * self.sprite_config["scale"]))
                        )
                        
                        frames.append(scaled_frame)
                    
                    if frames:
                        self.animations[state] = frames
                        print(f"Carregados {len(frames)} frames para {state}")
                    else:
                        print(f"Falha ao carregar frames para {state}")
                        self.animations[state] = [self.fallback_sprite]
                        
                except Exception as e:
                    print(f"Erro ao carregar {state}: {e}")
                    self.animations[state] = [self.fallback_sprite]

            print("Carregamento das animações do inimigo concluído!")
            
            # Definir sprite inicial
            self.image = self.animations["idle"][0]
            self.rect = self.image.get_rect()
            
        except Exception as e:
            print(f"Erro ao carregar animações do inimigo: {e}")
            # Usar fallback para todas as animações em caso de erro
            for state in self.animations.keys():
                self.animations[state] = [self.fallback_sprite]
            self.image = self.fallback_sprite
            self.rect = self.image.get_rect()

    def update_animation(self):
        try:
            # Atualizar animation_speed baseado no estado atual
            self.animation_speed = ENEMY_SPRITE["animations"][self.current_state]["duration"] / 1000  # Converter para segundos
            
            # Incrementar o timer de animação
            self.animation_timer += 1
            
            # Atualizar frame se o timer atingir o limite
            if self.animation_timer >= self.animation_speed * 60:  # 60 FPS
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.animations[self.current_state])
                
                # Obter o próximo frame
                self.image = self.animations[self.current_state][self.current_frame].copy()
                
                # Virar o sprite baseado na direção do movimento
                if self.direction == -1:  # Movendo para a esquerda
                    self.image = pygame.transform.flip(self.image, True, False)
                
                # Manter o retângulo na mesma posição
                old_center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = old_center
                
        except Exception as e:
            print(f"Erro na animação do inimigo: {e}")
            # Em caso de erro, usar o fallback
            self.image = self.fallback_sprite

    def update(self, player, ground, platforms):
        if self.is_dead:
            self.current_state = "death"
            self.death_timer += 1
            if self.death_timer >= self.death_duration:
                self.kill()
            self.update_animation()
            return

        # Atualizar cooldowns
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

        # Aplicar gravidade
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        # Colisão com o chão
        if self.rect.colliderect(ground.rect):
            self.rect.bottom = ground.rect.top
            self.velocity_y = 0

        # Colisão com plataformas
        for platform in self.platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:  # Caindo
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                elif self.velocity_y < 0:  # Subindo
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0

        # Movimento e comportamento
        dist_to_player = abs(self.world_x - self.player.world_x)  # Usar world_x em vez de rect.centerx
        
        if dist_to_player < self.attack_range and self.current_cooldown == 0:
            # Atacar - Escolher aleatoriamente entre os três tipos de ataque
            attack_type = random.choice(["attacking", "attacking2", "attacking3"])
            self.current_state = attack_type
            self.current_cooldown = self.attack_cooldown
            
            # Causar dano ao jogador se estiver no alcance
            if abs(self.rect.centerx - self.player.rect.centerx) < self.attack_range and \
               abs(self.rect.centery - self.player.rect.centery) < 50:  # Verificar também a altura
                self.player.health -= 10  # Dano do inimigo
                # Criar efeito de dano
                effect_manager.create_particles(
                    self.player.rect.centerx,
                    self.player.rect.centery,
                    (220, 40, 40),  # Vermelho
                    count=5,
                    alpha=160,
                    size=3
                )
        else:
            # Mover em direção ao jogador
            if self.world_x < self.player.world_x:
                self.direction = 1
                new_x = self.world_x + self.speed
                # Verificar limite direito
                if new_x <= self.map_limits['right']:
                    self.world_x = new_x
                # Alternar entre correr e andar baseado na distância
                self.current_state = "running" if dist_to_player < 200 else "walking"
            else:
                self.direction = -1
                new_x = self.world_x - self.speed
                # Verificar limite esquerdo
                if new_x >= self.map_limits['left']:
                    self.world_x = new_x
                # Alternar entre correr e andar baseado na distância
                self.current_state = "running" if dist_to_player < 200 else "walking"

        # Atualizar posição na tela baseado na posição mundial
        self.rect.x = self.world_x - camera_scroll

        # Atualizar trail effect
        if self.trail_timer >= self.trail_interval:
            self.trail.append((self.rect.centerx, self.rect.centery))
            if len(self.trail) > self.trail_length:
                self.trail.pop(0)
            self.trail_timer = 0
        self.trail_timer += 1

        # Atualizar animação
        self.update_animation()

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.is_dead = True
            self.current_state = "death"
            self.current_frame = 0
            # Aumentar chance de drop para 60%
            if random.random() < 0.6:  # 60% de chance de drop
                power_up_type = "vida" if random.random() < 0.7 else "mana"  # 70% vida, 30% mana
                power_up = PowerUp(self.rect.centerx, self.rect.centery, power_up_type)
                power_ups.add(power_up)
                all_sprites.add(power_up)

    def draw_health_bar(self, surface):
        if not self.is_dead:
            bar_width = 40
            bar_height = 5
            bar_position = [self.rect.centerx - bar_width//2, self.rect.top - 10]
            
            # Desenhar fundo da barra (vermelho)
            pygame.draw.rect(surface, RED, (*bar_position, bar_width, bar_height))
            
            # Desenhar barra de vida atual (verde)
            health_width = int(bar_width * (self.health / 100))
            if health_width > 0:
                pygame.draw.rect(surface, GREEN, (*bar_position, health_width, bar_height))
            
            # Desenhar borda da barra
            pygame.draw.rect(surface, WHITE, (*bar_position, bar_width, bar_height), 1)
            
            # Desenhar trail effect
            if len(self.trail) > 1:
                for i in range(len(self.trail) - 1):
                    alpha = int(255 * (i / len(self.trail)))
                    color = (*RED, alpha)
                    start_pos = self.trail[i]
                    end_pos = self.trail[i + 1]
                    pygame.draw.line(surface, color, start_pos, end_pos, 2)


# Grupos de sprites
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()
attack_sprites = pygame.sprite.Group()
magic_sprites = pygame.sprite.Group()
shield_sprites = pygame.sprite.Group()  # Novo grupo para sprites do escudo

# Criar plataformas com posições refinadas
platform_positions = [
    (200, HEIGHT - 200),   # Plataforma inicial mais baixa
    (450, HEIGHT - 280),   # Segunda plataforma um pouco mais alta
    (700, HEIGHT - 340),   # Terceira plataforma ainda mais alta
    (950, HEIGHT - 260),   # Plataforma de descanso antes da próxima seção
    
    # Seção 2 - Plataformas com mais variação de altura
    (1200, HEIGHT - 310),  # Primeira plataforma da segunda seção
    (1450, HEIGHT - 380),  # Plataforma mais alta para desafio
    (1700, HEIGHT - 280),  # Plataforma mais baixa para variedade
    (1950, HEIGHT - 340)   # Plataforma final
]

for pos in platform_positions:
    platform = Platform(pos[0], pos[1])
    platforms.add(platform)
    all_sprites.add(platform)

# Criar chão
ground = Ground()
all_sprites.add(ground)

# Criar jogador em uma posição mais segura
player = Player(100, HEIGHT - 60)
all_sprites.add(player)

# Criar tela de game over
game_over_screen = GameOverScreen()

# Criar inimigos (quantidade reduzida e melhor posicionada)
enemy_positions = [
    (platform_positions[1][0], HEIGHT - 100),  # Inimigo no chão na primeira seção
    (platform_positions[5][0], HEIGHT - 100),  # Inimigo no chão na segunda seção
]

# Sistema de respawn de inimigos
class EnemySpawner:
    def __init__(self, positions, platforms, player):
        self.positions = positions
        self.platforms = platforms
        self.player = player
        self.spawn_timer = {}  # Dicionário para controlar tempo de respawn por posição
        self.respawn_delay = 1800  # 30 segundos (60 FPS * 30)
        self.max_enemies = 3  # Número máximo de inimigos simultâneos
        
        # Inicializar timers
        for pos in self.positions:
            self.spawn_timer[str(pos)] = 0
    
    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Se já tiver o número máximo de inimigos, não spawnar mais
        if len(enemies) >= self.max_enemies:
            return
        
        # Verificar cada posição de spawn
        for pos in self.positions:
            pos_key = str(pos)
            
            # Verificar se há inimigo vivo nesta posição
            enemy_present = False
            for enemy in enemies:
                if abs(enemy.world_x - pos[0]) < 50:
                    enemy_present = True
                    break
            
            # Se não há inimigo e o timer zerou, criar novo inimigo
            if not enemy_present and current_time > self.spawn_timer[pos_key]:
                new_enemy = Enemy(pos[0], pos[1], self.player, self.platforms)
                enemies.add(new_enemy)
                all_sprites.add(new_enemy)
                self.spawn_timer[pos_key] = current_time + self.respawn_delay

# Criar spawner de inimigos (atualizar a inicialização)
enemy_spawner = EnemySpawner(enemy_positions, platforms, player)

# Loop principal do jogo
running = True
game_over = False
clock = pygame.time.Clock()

def reset_game():
    global player, enemies, camera_scroll
    # Resetar câmera
    camera_scroll = 0
    
    # Resetar jogador em posição segura
    player.health = player.max_health
    player.mana = player.max_mana
    player.world_x = 100
    player.rect.centerx = 100
    player.rect.bottom = HEIGHT - 60
    
    # Remover inimigos antigos
    for enemy in enemies:
        enemy.kill()
    
    # Criar novos inimigos nas posições definidas
    for pos in enemy_positions:
        enemy = Enemy(pos[0], pos[1], player, platforms)
        enemies.add(enemy)
        all_sprites.add(enemy)

# Inicializar posições iniciais das plataformas
for platform in platforms:
    platform.initial_x = platform.rect.x

def update_world_positions():
    # Atualizar posições dos sprites baseado no scroll
    for sprite in all_sprites:
        if isinstance(sprite, (Player, Enemy)):
            # Atualizar posição na tela baseado na posição mundial
            sprite.rect.x = sprite.world_x - camera_scroll
        elif isinstance(sprite, Platform):
            # Atualizar posição da plataforma mantendo sua posição mundial
            sprite.rect.x = sprite.initial_x - camera_scroll
        elif isinstance(sprite, Ground):
            # O chão sempre segue a câmera
            sprite.rect.x = -camera_scroll
        elif isinstance(sprite, PowerUp):
            # Power-ups seguem o scroll mantendo sua posição mundial
            sprite.rect.centerx = sprite.initial_x - camera_scroll

def sync_world_positions():
    # Sincronizar posições mundiais com posições na tela
    for sprite in all_sprites:
        if isinstance(sprite, (Player, Enemy)):
            # Atualizar posição na tela baseado na posição mundial
            sprite.rect.x = sprite.world_x - camera_scroll
        elif isinstance(sprite, Platform):
            # Garantir que a plataforma mantenha sua posição relativa ao mundo
            sprite.rect.x = sprite.initial_x - camera_scroll

# Classe da Seta Indicativa
class Arrow:
    def __init__(self):
        self.width = 40
        self.height = 30
        self.color = YELLOW
        self.pulse_speed = 0.05
        self.pulse_min = 0.7
        self.pulse_max = 1.0
        self.pulse_scale = self.pulse_min
        self.pulse_growing = True
        self.visible = False
        
        # Criar superfície da seta
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        points = [
            (0, self.height//2),  # Ponta esquerda
            (self.width*0.7, self.height//2),  # Corpo
            (self.width*0.7, 0),  # Topo da ponta
            (self.width, self.height//2),  # Ponta direita
            (self.width*0.7, self.height),  # Base da ponta
            (self.width*0.7, self.height//2)  # Volta ao corpo
        ]
        pygame.draw.polygon(self.image, self.color, points)
    
    def update(self):
        # Efeito de pulsar
        if self.pulse_growing:
            self.pulse_scale += self.pulse_speed
            if self.pulse_scale >= self.pulse_max:
                self.pulse_growing = False
        else:
            self.pulse_scale -= self.pulse_speed
            if self.pulse_scale <= self.pulse_min:
                self.pulse_growing = True
    
    def draw(self, surface, x, y):
        if self.visible:
            # Criar uma cópia escalada da imagem
            scaled_width = int(self.width * self.pulse_scale)
            scaled_height = int(self.height * self.pulse_scale)
            scaled_image = pygame.transform.scale(self.image, (scaled_width, scaled_height))
            
            # Centralizar a seta na posição original
            offset_x = (scaled_width - self.width) // 2
            offset_y = (scaled_height - self.height) // 2
            
            surface.blit(scaled_image, (x - offset_x, y - offset_y))

# Criar seta indicativa
arrow = Arrow()

def check_section_cleared():
    # Verificar se há inimigos vivos na seção atual
    section_width = WIDTH
    current_section = int(camera_scroll / section_width)
    section_start = current_section * section_width
    section_end = section_start + section_width
    
    enemies_in_section = False
    for enemy in enemies:
        if section_start <= enemy.world_x <= section_end:
            enemies_in_section = True
            break
    
    # Mostrar seta se não houver inimigos na seção atual
    arrow.visible = not enemies_in_section

# Classe do PowerUp
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, tipo):
        super().__init__()
        self.tipo = tipo
        self.width = 24  # Aumentado o tamanho
        self.height = 24
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Definir aparência baseada no tipo
        if tipo == "vida":
            self.color = (220, 40, 40)  # Vermelho para vida
            self.glow_color = (255, 150, 150)  # Cor do brilho para vida
            self.valor = 35  # Aumentado o valor de cura
        else:  # tipo == "mana"
            self.color = (40, 40, 220)  # Azul para mana
            self.glow_color = (150, 150, 255)  # Cor do brilho para mana
            self.valor = 50
        
        # Desenhar o power-up com efeito de brilho
        # Primeiro o brilho externo
        pygame.draw.circle(self.image, self.glow_color, (self.width//2, self.height//2), self.width//2)
        # Depois o círculo interno
        pygame.draw.circle(self.image, self.color, (self.width//2, self.height//2), self.width//2 - 2)
        # Adicionar um símbolo baseado no tipo
        if tipo == "vida":
            # Desenhar um símbolo de "+" para vida
            cross_color = (255, 255, 255)
            thickness = 3
            # Linha vertical
            pygame.draw.rect(self.image, cross_color, 
                           (self.width//2 - thickness//2, self.height//4,
                            thickness, self.height//2))
            # Linha horizontal
            pygame.draw.rect(self.image, cross_color,
                           (self.width//4, self.height//2 - thickness//2,
                            self.width//2, thickness))
        else:
            # Desenhar um símbolo de "M" para mana
            pygame.draw.lines(self.image, (255, 255, 255), False, [
                (self.width//4, self.height//4),  # Início do M
                (self.width//3, self.height*3//4),  # Primeira perna
                (self.width//2, self.height//4),  # Meio
                (self.width*2//3, self.height*3//4),  # Segunda perna
                (self.width*3//4, self.height//4)  # Fim do M
            ], 2)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.initial_x = x
        self.initial_y = y
        self.float_offset = 0
        self.float_speed = 0.08  # Velocidade reduzida para movimento mais suave
        self.pulse_scale = 1.0
        self.pulse_speed = 0.04
        self.pulse_min = 0.85
        self.pulse_max = 1.15
        self.pulse_growing = True
        
    def update(self):
        # Efeito de flutuação suave
        self.float_offset = math.sin(pygame.time.get_ticks() * self.float_speed) * 6
        self.rect.y = self.initial_y + self.float_offset
        
        # Efeito de pulsar
        if self.pulse_growing:
            self.pulse_scale += self.pulse_speed
            if self.pulse_scale >= self.pulse_max:
                self.pulse_growing = False
        else:
            self.pulse_scale -= self.pulse_speed
            if self.pulse_scale <= self.pulse_min:
                self.pulse_growing = True
        
        # Atualizar posição x baseado no scroll
        self.rect.centerx = self.initial_x - camera_scroll

    def draw(self, surface):
        # Criar uma cópia escalada da imagem para o efeito de pulsar
        current_width = int(self.width * self.pulse_scale)
        current_height = int(self.height * self.pulse_scale)
        scaled_image = pygame.transform.scale(self.image, (current_width, current_height))
        
        # Centralizar a imagem escalada
        scaled_rect = scaled_image.get_rect(center=self.rect.center)
        surface.blit(scaled_image, scaled_rect)

# Adicionar grupo de power-ups
power_ups = pygame.sprite.Group()

def main():
    # Inicializar estado do jogo
    global current_state
    current_state = MENU
    
    # Loop principal do jogo
    running = True
    game_over = False
    clock = pygame.time.Clock()
    
    while running:
        # Controle de FPS
        clock.tick(60)
        
        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Tratamento de eventos baseado no estado atual
            if current_state == MENU:
                action = main_menu.handle_input(event)
                if action == 'iniciar':
                    current_state = PLAYING
                elif action == 'opcoes':
                    current_state = OPTIONS
                elif action == 'creditos':
                    current_state = CREDITS
                elif action == 'controles':
                    current_state = CONTROLS
                elif action == 'sair':
                    running = False
                    
            elif current_state == OPTIONS:
                action = options_menu.handle_input(event)
                if action == 'voltar':
                    current_state = MENU
                    
            elif current_state == CREDITS:
                action = credits_menu.handle_input(event)
                if action == 'voltar':
                    current_state = MENU
                    
            elif current_state == CONTROLS:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    current_state = MENU
                    
            elif current_state == PLAYING:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    current_state = MENU
                    
            elif current_state == GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        current_state = PLAYING
                        game_over = False
                        reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        current_state = MENU
                        game_over = False
                        reset_game()
        
        # Atualizar baseado no estado atual
        if current_state == MENU:
            main_menu.update()
            main_menu.draw(screen)
            
        elif current_state == OPTIONS:
            options_menu.draw(screen)
            
        elif current_state == CREDITS:
            credits_menu.draw(screen)
            
        elif current_state == CONTROLS:
            draw_controls_screen(screen)
            
        elif current_state == PLAYING:
            # Verificar se o jogador morreu
            if player.health <= 0:
                current_state = GAME_OVER
                game_over = True
            
            # Input e atualização apenas se não estiver em game over
            if not game_over:
                # Input
                keys = pygame.key.get_pressed()
                
                # Atualizar
                player.update(keys, platforms, ground, enemies)
                
                # Atualizar inimigos
                for enemy in enemies:
                    enemy.update(player, ground, platforms)
                
                # Sincronizar posições do mundo
                sync_world_positions()
                
                # Atualizar posições do mundo baseado no scroll
                update_world_positions()
                
                # Atualizar plataformas
                for platform in platforms:
                    platform.update()
                
                # Verificar se a seção atual foi limpa
                check_section_cleared()
                
                # Atualizar seta
                arrow.update()
                
                # Remover inimigos mortos e adicionar pontos
                for enemy in enemies:
                    if enemy.health <= 0:
                        player.score += enemy.points_value
                        enemy.kill()
                
                # Atualizar efeitos
                effect_manager.update()
                
                # Atualizar power-ups
                for power_up in power_ups:
                    power_up.draw(screen)
                
                # Atualizar spawner de inimigos
                enemy_spawner.update()
            
            # Desenhar
            screen.blit(background, (0, 0))
            
            # Desenhar chão
            ground.draw(screen)
            
            # Desenhar plataformas com seus efeitos
            for platform in platforms:
                platform.draw(screen)
            
            # Desenhar outros sprites
            all_sprites.draw(screen)
            attack_sprites.draw(screen)
            magic_sprites.draw(screen)
            shield_sprites.draw(screen)  # Desenhar escudo por último para ficar visível
            
            # Desenhar efeitos
            effect_manager.draw(screen)
            
            # Desenhar barras de vida
            player.draw_health_bar(screen)
            for enemy in enemies:
                enemy.draw_health_bar(screen)
            
            # Desenhar seta indicativa
            if arrow.visible:
                arrow_x = WIDTH - 100  # Posição da seta próxima à borda direita
                arrow_y = HEIGHT // 2  # Centralizada verticalmente
                arrow.draw(screen, arrow_x, arrow_y)
            
            # Desenhar tela de game over se necessário
            if game_over:
                game_over_screen.draw(screen)
        
        # Atualizar tela
        pygame.display.flip()
    
    # Encerrar Pygame
    pygame.quit()

def draw_controls_screen(screen):
    # Fundo escuro semi-transparente
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(180)
    screen.blit(overlay, (0, 0))
    
    # Fonte para os textos
    font_big = pygame.font.SysFont("Arial", 36)
    font_small = pygame.font.SysFont("Arial", 24)
    
    # Título
    title = font_big.render("Controles", True, (255, 255, 255))
    title_pos = (WIDTH // 2 - title.get_width() // 2, 50)
    screen.blit(title, title_pos)
    
    # Lista de controles
    controls = [
        ("Movimento", "Setas ← →"),
        ("Pular", "Espaço"),
        ("Atacar", "X"),
        ("Magia", "C"),
        ("Dash", "Shift"),
        ("Escudo", "V"),
        ("Menu", "ESC")
    ]
    
    # Desenhar controles
    y = 150
    for action, key in controls:
        action_text = font_small.render(action, True, (200, 200, 200))
        key_text = font_small.render(key, True, (255, 255, 255))
        
        screen.blit(action_text, (WIDTH // 2 - 150, y))
        screen.blit(key_text, (WIDTH // 2 + 50, y))
        y += 40
    
    # Texto para voltar
    back_text = font_small.render("Pressione ESC para voltar", True, (150, 150, 150))
    back_pos = (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 100)
    screen.blit(back_text, back_pos)

if __name__ == '__main__':
    main()