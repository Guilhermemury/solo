import pygame
import random
import math

class Particle:
    def __init__(self, x, y, color, alpha=255, size=3, speed=2, lifetime=30):
        self.x = x
        self.y = y
        self.color = color
        self.alpha = alpha
        self.size = size
        self.speed = speed
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.angle = random.uniform(0, 2 * math.pi)
        self.dx = math.cos(self.angle) * self.speed
        self.dy = math.sin(self.angle) * self.speed

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1
        # Suavizar a diminuição do alpha
        progress = self.lifetime / self.max_lifetime
        self.alpha = max(0, int(255 * progress * progress))
        return self.lifetime > 0

    def draw(self, surface):
        if self.alpha > 0:
            particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            # Criar um gradiente circular para cada partícula
            for r in range(self.size, 0, -1):
                alpha = int(self.alpha * (r / self.size))
                pygame.draw.circle(particle_surface, (*self.color, alpha), (self.size, self.size), r)
            surface.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))

class Trail:
    def __init__(self, color, alpha=255, length=5):
        self.color = color
        self.alpha = alpha
        self.length = length
        self.points = []

    def add_point(self, x, y):
        self.points.append((x, y))
        if len(self.points) > self.length:
            self.points.pop(0)

    def draw(self, surface):
        if len(self.points) >= 2:
            # Criar uma superfície para o trail com transparência
            trail_surface = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
            
            # Desenhar segmentos do trail com gradiente
            for i in range(len(self.points) - 1):
                progress = i / (len(self.points) - 1)
                current_alpha = int(self.alpha * progress)
                width = int(5 * progress + 2)  # Largura diminui gradualmente
                
                start_pos = self.points[i]
                end_pos = self.points[i + 1]
                
                # Desenhar linha com gradiente
                pygame.draw.line(trail_surface, (*self.color, current_alpha),
                               start_pos, end_pos, width)
            
            surface.blit(trail_surface, (0, 0))

class EffectManager:
    def __init__(self):
        self.particles = []
        self.trails = {}

    def create_particles(self, x, y, color, count=5, speed=2, alpha=255, size=3, lifetime=None):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed_x = math.cos(angle) * speed
            speed_y = math.sin(angle) * speed
            # Tempo de vida um pouco maior para efeitos de ataque
            particle_lifetime = lifetime if lifetime is not None else random.randint(6, 10)
            
            # Criar partícula com tamanho aleatório para mais dinamismo
            particle_size = random.uniform(size * 0.8, size * 1.2)
            
            # Adicionar variação de cor para mais dinamismo
            color_variation = 20
            varied_color = tuple(
                min(255, max(0, c + random.randint(-color_variation, color_variation)))
                for c in color
            )
            
            self.particles.append({
                'x': x,
                'y': y,
                'speed_x': speed_x,
                'speed_y': speed_y,
                'color': varied_color,
                'alpha': min(alpha, 250),  # Permitir alpha mais alto inicialmente
                'size': particle_size,
                'lifetime': particle_lifetime,
                'original_size': particle_size,  # Guardar tamanho original para efeito de encolhimento
                'glow_size': particle_size * 2  # Tamanho do brilho externo
            })

    def create_trail(self, name, color):
        self.trails[name] = {
            'positions': [],
            'max_length': 3,  # Aumentado para 3 para trail mais visível
            'color': color,
            'fade_speed': 20
        }

    def update(self):
        # Atualizar partículas com fade e encolhimento
        for particle in self.particles[:]:
            particle['x'] += particle['speed_x']
            particle['y'] += particle['speed_y']
            particle['lifetime'] -= 1
            
            # Fade mais suave no início e mais rápido no final
            life_ratio = particle['lifetime'] / 10  # Assumindo tempo de vida máximo de 10
            particle['alpha'] = int(particle['alpha'] * (0.7 + life_ratio * 0.3))
            
            # Encolher partícula conforme envelhece, mas manter tamanho mínimo
            size_ratio = 0.3 + (life_ratio * 0.7)  # Manter pelo menos 30% do tamanho
            particle['size'] = particle['original_size'] * size_ratio
            particle['glow_size'] = particle['size'] * (1.5 + life_ratio)  # Brilho diminui mais rápido
            
            # Adicionar movimento aleatório sutil
            particle['speed_x'] += random.uniform(-0.1, 0.1)
            particle['speed_y'] += random.uniform(-0.1, 0.1)
            
            # Remover partículas
            if particle['lifetime'] <= 0 or particle['alpha'] < 30:
                self.particles.remove(particle)

    def update_trail(self, name, x, y):
        if name in self.trails:
            self.trails[name]['positions'].append((x, y))
            if len(self.trails[name]['positions']) > self.trails[name]['max_length']:
                self.trails[name]['positions'].pop(0)

    def draw(self, surface):
        # Desenhar partículas com efeito de brilho melhorado
        for particle in self.particles:
            # Desenhar brilho externo com gradiente
            glow_radius = int(particle['glow_size'])
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            
            # Criar gradiente de brilho
            for r in range(glow_radius, 0, -1):
                alpha = int((r / glow_radius) * particle['alpha'] * 0.3)
                pygame.draw.circle(glow_surface, (*particle['color'], alpha),
                                (glow_radius, glow_radius), r)
            
            # Posicionar o brilho
            glow_pos = (int(particle['x'] - glow_radius), int(particle['y'] - glow_radius))
            surface.blit(glow_surface, glow_pos)
            
            # Desenhar partícula principal com brilho interno
            core_size = int(particle['size'])
            if core_size > 0:
                # Brilho interno mais intenso
                pygame.draw.circle(surface, (*particle['color'], particle['alpha']),
                                (int(particle['x']), int(particle['y'])),
                                core_size)
                # Centro mais brilhante
                bright_color = tuple(min(c + 50, 255) for c in particle['color'])
                pygame.draw.circle(surface, (*bright_color, particle['alpha']),
                                (int(particle['x']), int(particle['y'])),
                                max(1, core_size // 2))

    def create_attack_effect(self, rect, config, direction="right"):
        surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        color = config.get("color", (255, 255, 0))
        
        # Criar menos partículas para o efeito de ataque
        for _ in range(3):  # Reduzido de 5 para 3
            x = random.randint(0, rect.width)
            y = random.randint(0, rect.height)
            size = random.randint(2, 4)
            alpha = random.randint(40, 80)  # Reduzido o alpha
            pygame.draw.circle(surface, (*color, alpha), (x, y), size)
        
        return surface

    def create_magic_effect(self, rect, config):
        surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        color = config.get("color", (0, 0, 255))
        
        # Criar menos partículas para o efeito mágico
        for _ in range(4):  # Reduzido de 8 para 4
            x = random.randint(0, rect.width)
            y = random.randint(0, rect.height)
            size = random.randint(3, 5)
            alpha = random.randint(30, 60)  # Reduzido o alpha
            pygame.draw.circle(surface, (*color, alpha), (x, y), size)
        
        return surface 