import pygame
import random
import time

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.SysFont("Arial", 24)  # Fonte um pouco menor
        self.normal_color = (40, 40, 40)  # Cor escura para o botão
        self.hover_color = (60, 60, 60)  # Cor quando o mouse passa por cima
        self.text_color = (220, 220, 220)  # Cor do texto
        self.border_radius = 10  # Bordas arredondadas
        self.current_color = self.normal_color
        self.alpha = 180  # Transparência um pouco maior
        self.glow_alpha = 0
        self.glow_direction = 2  # Velocidade do efeito aumentada
        self.is_hovered = False  # Estado do hover

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            # Atualiza o estado do hover
            self.is_hovered = self.rect.collidepoint(event.pos)
            self.current_color = self.hover_color if self.is_hovered else self.normal_color
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Retorna True se o botão foi clicado
            if event.button == 1 and self.rect.collidepoint(event.pos):
                return True
        return False
        
    def draw(self, surface):
        # Criar superfície para o botão com suporte a transparência
        button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Atualizar efeito de brilho
        self.glow_alpha += self.glow_direction
        if self.glow_alpha >= 30 or self.glow_alpha <= 0:
            self.glow_direction *= -1
        
        # Desenhar o efeito de brilho se o botão estiver com hover
        if self.is_hovered:
            glow_rect = self.rect.inflate(10, 10)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*self.hover_color, 30 + self.glow_alpha),
                           (0, 0, glow_rect.width, glow_rect.height),
                           border_radius=self.border_radius)
            surface.blit(glow_surface, glow_rect)
        
        # Desenhar o fundo do botão
        pygame.draw.rect(button_surface, (*self.current_color, self.alpha),
                        (0, 0, self.rect.width, self.rect.height),
                        border_radius=self.border_radius)
        
        # Renderizar o texto
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.rect.width/2, self.rect.height/2))
        
        # Adicionar sombra ao texto
        shadow_surface = self.font.render(self.text, True, (20, 20, 20))
        shadow_rect = shadow_surface.get_rect(center=(text_rect.centerx + 1, text_rect.centery + 1))
        button_surface.blit(shadow_surface, shadow_rect)
        button_surface.blit(text_surface, text_rect)
        
        # Desenhar o botão na superfície principal
        surface.blit(button_surface, self.rect)

class Tutorial:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont("Arial", 20)  # Fonte menor
        self.start_time = time.time()
        self.duration = 30  # Duração em segundos
        self.alpha = 255
        self.fade_speed = 5
        
        # Comandos do jogo
        self.commands = [
            "Comandos:",  # Título mais curto
            "W,A,S,D - Mover",  # Textos mais concisos
            "Espaço - Atacar",
            "E - Interagir",
            "ESC - Menu",
            "Shift - Correr"
        ]
        
        # Renderizar textos com sombra
        self.text_surfaces = []
        self.shadow_surfaces = []
        for command in self.commands:
            text = self.font.render(command, True, (220, 220, 220))
            shadow = self.font.render(command, True, (20, 20, 20))
            self.text_surfaces.append(text)
            self.shadow_surfaces.append(shadow)
        
        # Criar superfície semi-transparente para o fundo menor
        self.background = pygame.Surface((200, 160))  # Reduzido o tamanho
        self.background.fill((30, 30, 30))
        self.background.set_alpha(150)
        
        # Posição do tutorial (canto superior esquerdo, mais compacto)
        self.x = 10
        self.y = 10
    
    def update(self):
        # Calcular tempo restante
        elapsed_time = time.time() - self.start_time
        if elapsed_time >= self.duration - 3:  # Começar a desaparecer 3 segundos antes
            self.alpha = max(0, self.alpha - self.fade_speed)
    
    def draw(self, surface):
        if self.alpha <= 0:
            return False  # Tutorial completamente invisível
        
        # Desenhar fundo semi-transparente
        background_copy = self.background.copy()
        background_copy.set_alpha(int(self.alpha * 0.6))  # 60% da opacidade do texto
        surface.blit(background_copy, (self.x - 10, self.y - 10))
        
        # Desenhar textos com sombra
        y_offset = self.y
        for i, (text, shadow) in enumerate(zip(self.text_surfaces, self.shadow_surfaces)):
            # Título em vermelho
            if i == 0:
                text = self.font.render(self.commands[i], True, (200, 40, 40))
            
            # Aplicar alpha
            text_copy = text.copy()
            shadow_copy = shadow.copy()
            text_copy.set_alpha(self.alpha)
            shadow_copy.set_alpha(self.alpha)
            
            # Desenhar com sombra
            surface.blit(shadow_copy, (self.x + 2, y_offset + 2))
            surface.blit(text_copy, (self.x, y_offset))
            y_offset += 30
        
        return True  # Tutorial ainda visível

class Menu:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.buttons = []
        self.particles = []
        
        # Título do jogo com fonte personalizada
        self.title_font = pygame.font.SysFont("Arial", 100, bold=True)
        self.subtitle_font = pygame.font.SysFont("Arial", 24)
        self.author_font = pygame.font.SysFont("Arial", 16)
        
        # Cores refinadas
        self.title_color = (200, 40, 40)  # Vermelho mais suave
        self.subtitle_color = (180, 180, 180)  # Cinza claro
        self.author_color = (160, 160, 160)  # Cinza mais claro
        
        # Renderizar textos
        self.title = self.title_font.render("Solo Leveling", True, self.title_color)
        self.subtitle = self.subtitle_font.render("A Ascensão do Caçador das Sombras", True, self.subtitle_color)
        self.author = self.author_font.render("Desenvolvido por: Guilherme Ferreira Mury", True, self.author_color)
        self.ru = self.author_font.render("RU: 4551362", True, self.author_color)
        
        # Posicionar textos (título mais para cima)
        self.title_rect = self.title.get_rect(center=(width//2, height//6))  # Ajustado de height//5 para height//6
        self.subtitle_rect = self.subtitle.get_rect(center=(width//2, height//6 + 80))
        
        # Posicionar informações do autor no canto superior direito
        padding = 10
        self.author_rect = self.author.get_rect(topright=(width - padding, padding))
        self.ru_rect = self.ru.get_rect(topright=(width - padding, self.author_rect.bottom + 5))
        
        # Sombras para os textos
        self.title_shadow = self.title_font.render("Solo Leveling", True, (20, 20, 20))
        self.subtitle_shadow = self.subtitle_font.render("A Ascensão do Caçador das Sombras", True, (20, 20, 20))
        self.title_shadow_rect = self.title_shadow.get_rect(center=(width//2 + 3, height//6 + 3))
        self.subtitle_shadow_rect = self.subtitle_shadow.get_rect(center=(width//2 + 2, height//6 + 82))
        
        # Criar background com gradiente mais elegante
        self.background = pygame.Surface((width, height))
        for y in range(height):
            color_value = int(30 + (y / height) * 25)  # Gradiente mais suave
            pygame.draw.line(self.background, (color_value, color_value, color_value + 10), 
                           (0, y), (width, y))
        
        # Efeito de fade mais suave
        self.overlay = pygame.Surface((width, height))
        self.overlay.fill((0, 0, 0))
        self.fade_alpha = 255
        self.fade_speed = 5
        
        self.create_buttons()
        self.create_particles()
    
    def create_buttons(self):
        button_width = 180  # Largura dos botões
        button_height = 35  # Altura reduzida
        spacing = 10  # Espaçamento reduzido
        total_height = 5 * (button_height + spacing)  # Altura total para todos os botões
        
        # Ajustar posição inicial para mais abaixo
        start_y = (self.height - total_height) // 2 + 50  # Adicionado offset de 50 pixels
        
        button_x = (self.width - button_width) // 2  # Centralizar horizontalmente
        
        # Criar botões com as novas dimensões
        self.buttons = [
            Button(button_x, start_y, button_width, button_height, "Iniciar Jogo"),
            Button(button_x, start_y + (button_height + spacing), button_width, button_height, "Controles"),
            Button(button_x, start_y + 2 * (button_height + spacing), button_width, button_height, "Opções"),
            Button(button_x, start_y + 3 * (button_height + spacing), button_width, button_height, "Créditos"),
            Button(button_x, start_y + 4 * (button_height + spacing), button_width, button_height, "Sair")
        ]
    
    def create_particles(self):
        # Partículas de fundo melhoradas
        self.particles = []
        for _ in range(30):  # Reduzido número de partículas
            self.particles.append({
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height),
                'size': random.randint(1, 2),  # Tamanho reduzido
                'speed': random.uniform(0.8, 2.0),  # Velocidade aumentada
                'alpha': random.randint(30, 100),  # Menos opaco
                'color': (random.randint(180, 220), 40, 40)
            })
    
    def handle_input(self, event):
        for button in self.buttons:
            if button.handle_event(event):
                if button.text == "Iniciar Jogo":
                    return 'iniciar'
                elif button.text == "Controles":
                    return 'controles'
                elif button.text == "Opções":
                    return 'opcoes'
                elif button.text == "Créditos":
                    return 'creditos'
                elif button.text == "Sair":
                    return 'sair'
        return None
    
    def update(self):
        # Atualizar fade
        if self.fade_alpha > 0:
            self.fade_alpha = max(0, self.fade_alpha - self.fade_speed)
        
        # Atualizar partículas
        for particle in self.particles:
            particle['y'] += particle['speed']
            if particle['y'] > self.height:
                particle['y'] = 0
                particle['x'] = random.randint(0, self.width)
    
    def draw(self, surface):
        # Desenhar fundo com gradiente
        surface.blit(self.background, (0, 0))
        
        # Desenhar partículas com efeito de brilho
        for particle in self.particles:
            color_with_alpha = (*particle['color'], particle['alpha'])
            pygame.draw.circle(surface, color_with_alpha,
                             (int(particle['x']), int(particle['y'])),
                             particle['size'])
            # Adicionar brilho
            glow = pygame.Surface((particle['size'] * 4, particle['size'] * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*particle['color'], particle['alpha'] // 3),
                             (glow.get_width() // 2, glow.get_height() // 2),
                             particle['size'] * 2)
            surface.blit(glow, (int(particle['x'] - glow.get_width() // 2),
                               int(particle['y'] - glow.get_height() // 2)))
        
        # Desenhar título e subtítulo com sombra
        surface.blit(self.title_shadow, self.title_shadow_rect)
        surface.blit(self.title, self.title_rect)
        surface.blit(self.subtitle_shadow, self.subtitle_shadow_rect)
        surface.blit(self.subtitle, self.subtitle_rect)
        
        # Desenhar informações do autor
        surface.blit(self.author, self.author_rect)
        surface.blit(self.ru, self.ru_rect)
        
        # Desenhar botões
        for button in self.buttons:
            button.draw(surface)
        
        # Aplicar fade
        if self.fade_alpha > 0:
            self.overlay.set_alpha(self.fade_alpha)
            surface.blit(self.overlay, (0, 0))

class OptionsMenu:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Criar background com gradiente mais elegante
        self.background = pygame.Surface((width, height))
        for y in range(height):
            color_value = int(30 + (y / height) * 25)  # Gradiente mais suave
            pygame.draw.line(self.background, (color_value, color_value, color_value + 10), 
                           (0, y), (width, y))
        
        # Título e subtítulo
        self.title_font = pygame.font.SysFont("Arial", 72, bold=True)
        self.subtitle_font = pygame.font.SysFont("Arial", 24)
        self.author_font = pygame.font.SysFont("Arial", 16)
        
        # Cores refinadas
        self.title_color = (200, 40, 40)
        self.subtitle_color = (180, 180, 180)
        self.author_color = (160, 160, 160)
        
        # Renderizar textos
        self.title = self.title_font.render("Opções", True, self.title_color)
        self.subtitle = self.subtitle_font.render("Configurações do Jogo", True, self.subtitle_color)
        self.author = self.author_font.render("Desenvolvido por: Guilherme Ferreira Mury", True, self.author_color)
        self.ru = self.author_font.render("RU: 4551362", True, self.author_color)
        
        # Posicionar textos
        self.title_rect = self.title.get_rect(center=(width//2, height//5))
        self.subtitle_rect = self.subtitle.get_rect(center=(width//2, height//5 + 80))
        
        # Posicionar informações do autor no canto superior direito
        padding = 10
        self.author_rect = self.author.get_rect(topright=(width - padding, padding))
        self.ru_rect = self.ru.get_rect(topright=(width - padding, self.author_rect.bottom + 5))
        
        # Sombras para os textos
        self.title_shadow = self.title_font.render("Opções", True, (20, 20, 20))
        self.subtitle_shadow = self.subtitle_font.render("Configurações do Jogo", True, (20, 20, 20))
        self.title_shadow_rect = self.title_shadow.get_rect(center=(width//2 + 3, height//5 + 3))
        self.subtitle_shadow_rect = self.subtitle_shadow.get_rect(center=(width//2 + 2, height//5 + 82))
        
        # Criar botões com as mesmas dimensões do menu principal
        button_width = 180
        button_height = 35
        button_x = width//2 - button_width//2
        start_y = height//2 + 20
        spacing = 10
        
        self.buttons = {
            'som': Button(button_x, start_y, button_width, button_height, "Som: Ligado"),
            'dificuldade': Button(button_x, start_y + spacing + button_height, button_width, button_height, "Dificuldade: Normal"),
            'voltar': Button(button_x, start_y + (spacing + button_height) * 2, button_width, button_height, "Voltar")
        }
        
        # Partículas de fundo
        self.particles = []
        for _ in range(20):  # Menos partículas
            self.particles.append({
                'x': random.randint(0, width),
                'y': random.randint(0, height),
                'size': random.randint(1, 2),
                'speed': random.uniform(0.8, 2.0),
                'alpha': random.randint(30, 80),
                'color': (random.randint(180, 220), 40, 40)
            })
    
    def handle_input(self, event):
        for button_name, button in self.buttons.items():
            if button.handle_event(event):
                return button_name
        return None
    
    def update(self):
        # Atualizar partículas
        for particle in self.particles:
            particle['y'] += particle['speed']
            if particle['y'] > self.height:
                particle['y'] = 0
                particle['x'] = random.randint(0, self.width)
    
    def draw(self, surface):
        # Desenhar fundo
        surface.blit(self.background, (0, 0))
        
        # Desenhar partículas com efeito de brilho
        for particle in self.particles:
            color_with_alpha = (*particle['color'], particle['alpha'])
            pygame.draw.circle(surface, color_with_alpha,
                             (int(particle['x']), int(particle['y'])),
                             particle['size'])
            # Adicionar brilho
            glow = pygame.Surface((particle['size'] * 4, particle['size'] * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*particle['color'], particle['alpha'] // 3),
                             (glow.get_width() // 2, glow.get_height() // 2),
                             particle['size'] * 2)
            surface.blit(glow, (int(particle['x'] - glow.get_width() // 2),
                               int(particle['y'] - glow.get_height() // 2)))
        
        # Desenhar título e subtítulo com sombra
        surface.blit(self.title_shadow, self.title_shadow_rect)
        surface.blit(self.title, self.title_rect)
        surface.blit(self.subtitle_shadow, self.subtitle_shadow_rect)
        surface.blit(self.subtitle, self.subtitle_rect)
        
        # Desenhar informações do autor
        surface.blit(self.author, self.author_rect)
        surface.blit(self.ru, self.ru_rect)
        
        # Desenhar botões
        for button in self.buttons.values():
            button.draw(surface)

class CreditsMenu:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Criar background com gradiente mais elegante
        self.background = pygame.Surface((width, height))
        for y in range(height):
            color_value = int(30 + (y / height) * 25)  # Gradiente mais suave
            pygame.draw.line(self.background, (color_value, color_value, color_value + 10), 
                           (0, y), (width, y))
        
        # Configurações de scroll
        self.scroll_offset = 0
        self.scroll_speed = 0.5
        
        # Botão de voltar com as mesmas dimensões
        button_width = 180
        button_height = 35
        self.button = Button(width//2 - button_width//2, height - 80, button_width, button_height, "Voltar")
        
        # Título e subtítulo
        self.title_font = pygame.font.SysFont("Arial", 36, bold=True)
        self.subtitle_font = pygame.font.SysFont("Arial", 24)
        self.text_font = pygame.font.SysFont("Arial", 20)
        
        # Cores refinadas
        self.title_color = (220, 220, 220)
        self.subtitle_color = (200, 200, 200)
        self.text_color = (180, 180, 180)
        
        # Renderizar textos
        self.title = self.title_font.render("Créditos", True, self.title_color)
        self.subtitle = self.subtitle_font.render("Equipe e Agradecimentos", True, self.subtitle_color)
        
        # Textos dos créditos
        self.credits_texts = [
            ("Desenvolvedor", ["Guilherme Ferreira Mury"]),
            ("Professores e Colegas", ["Obrigado pelo apoio e orientação"]),
            ("Recursos", [
                "Pygame - Framework de jogos",
                "Sprites e Assets - Diversos artistas",
                "Música e Sons - Efeitos sonoros livres"
            ])
        ]
        
        # Renderizar textos dos créditos
        self.rendered_credits = []
        for section, items in self.credits_texts:
            self.rendered_credits.append(self.subtitle_font.render(section, True, self.subtitle_color))
            for item in items:
                self.rendered_credits.append(self.text_font.render(item, True, self.text_color))
            self.rendered_credits.append(self.text_font.render("", True, self.text_color))  # Espaço entre seções
        
        # Informações do autor
        self.author_font = pygame.font.SysFont("Arial", 16)
        self.author = self.author_font.render("Desenvolvido por: Guilherme Ferreira Mury", True, (160, 160, 160))
        self.ru = self.author_font.render("RU: 4551362", True, (160, 160, 160))
        
        # Posicionar informações do autor no canto superior direito
        padding = 10
        self.author_rect = self.author.get_rect(topright=(width - padding, padding))
        self.ru_rect = self.ru.get_rect(topright=(width - padding, self.author_rect.bottom + 5))
        
        # Efeitos visuais
        self.particles = []
        for _ in range(20):
            self.particles.append({
                'x': random.randint(0, width),
                'y': random.randint(0, height),
                'size': random.randint(1, 2),
                'speed': random.uniform(0.8, 2.0),
                'alpha': random.randint(30, 80),
                'color': (random.randint(180, 220), 40, 40)
            })
    
    def handle_input(self, event):
        if self.button.handle_event(event):
            return 'voltar'
        return None
    
    def update(self):
        # Atualizar scroll com limite
        self.scroll_offset -= self.scroll_speed
        total_height = len(self.rendered_credits) * 50
        if self.scroll_offset < -total_height + self.height//2:  # Limita o scroll
            self.scroll_offset = 0
    
    def draw(self, surface):
        # Desenhar fundo
        surface.blit(self.background, (0, 0))
        
        # Desenhar partículas com efeito de brilho
        for particle in self.particles:
            color_with_alpha = (*particle['color'], particle['alpha'])
            pygame.draw.circle(surface, color_with_alpha,
                             (int(particle['x']), int(particle['y'])),
                             particle['size'])
            # Adicionar brilho
            glow = pygame.Surface((particle['size'] * 4, particle['size'] * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*particle['color'], particle['alpha'] // 3),
                             (glow.get_width() // 2, glow.get_height() // 2),
                             particle['size'] * 2)
            surface.blit(glow, (int(particle['x'] - glow.get_width() // 2),
                               int(particle['y'] - glow.get_height() // 2)))
        
        # Desenhar título e subtítulo com sombra
        surface.blit(self.title_font.render("Créditos", True, (20, 20, 20)), self.title.get_rect(center=(self.width//2, self.height//6)))
        surface.blit(self.subtitle_font.render("Equipe e Agradecimentos", True, (20, 20, 20)), self.subtitle.get_rect(center=(self.width//2, self.height//6 + 70)))
        surface.blit(self.title, self.title.get_rect(center=(self.width//2, self.height//6)))
        surface.blit(self.subtitle, self.subtitle.get_rect(center=(self.width//2, self.height//6 + 70)))
        
        # Desenhar texto dos créditos com efeito de scroll e sombra
        y = self.height//2.5 + self.scroll_offset  # Começar mais acima
        for i, text in enumerate(self.rendered_credits):
            if 0 < y < self.height - 120:  # Evitar sobreposição com o botão
                text_rect = text.get_rect(center=(self.width//2, y))
                shadow_rect = text.get_rect(center=(self.width//2 + 2, y + 2))
                
                surface.blit(text, text_rect)
            y += 60  # Aumentado o espaçamento entre linhas
        
        # Desenhar botão de voltar
        self.button.draw(surface)

class ControlsMenu:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Fontes
        self.title_font = pygame.font.SysFont("Arial", 72, bold=True)
        self.subtitle_font = pygame.font.SysFont("Arial", 24)
        self.controls_font = pygame.font.SysFont("Arial", 32)
        self.author_font = pygame.font.SysFont("Arial", 16)
        
        # Textos
        self.title = self.title_font.render("Controles", True, (200, 40, 40))
        self.subtitle = self.subtitle_font.render("Como Jogar", True, (220, 220, 220))
        
        # Informações do autor
        self.author = self.author_font.render("Desenvolvido por: Guilherme Ferreira Mury", True, (180, 180, 180))
        self.ru = self.author_font.render("RU: 4551362", True, (180, 180, 180))
        
        # Lista de controles
        self.controls = [
            ("Movimentação", "W, A, S, D"),
            ("Ataque", "Barra de Espaço"),
            ("Interagir", "E"),
            ("Menu/Pausar", "ESC"),
            ("Correr", "Shift")
        ]
        
        # Renderizar controles
        self.control_texts = []
        self.control_descriptions = []
        for action, key in self.controls:
            text = self.controls_font.render(action + ":", True, (200, 40, 40))
            desc = self.controls_font.render(key, True, (220, 220, 220))
            self.control_texts.append(text)
            self.control_descriptions.append(desc)
        
        # Posicionar textos
        self.title_rect = self.title.get_rect(center=(width//2, height//6))
        self.subtitle_rect = self.subtitle.get_rect(center=(width//2, height//6 + 70))
        
        # Posicionar informações do autor
        padding = 10
        self.author_rect = self.author.get_rect(topright=(width - padding, padding))
        self.ru_rect = self.ru.get_rect(topright=(width - padding, self.author_rect.bottom + 5))
        
        # Botão de voltar com as mesmas dimensões
        button_width = 180
        button_height = 35
        self.button = Button(width//2 - button_width//2, height - 80, button_width, button_height, "Voltar")
        
        # Efeitos visuais
        self.particles = []
        for _ in range(20):
            self.particles.append({
                'x': random.randint(0, width),
                'y': random.randint(0, height),
                'size': random.randint(1, 2),
                'speed': random.uniform(0.8, 2.0),
                'alpha': random.randint(30, 80),
                'color': (random.randint(180, 220), 40, 40)
            })
    
    def handle_input(self, event):
        if self.button.handle_event(event):
            return 'voltar'
        return None
    
    def update(self):
        # Atualizar partículas
        for particle in self.particles:
            particle['y'] += particle['speed']
            if particle['y'] > self.height:
                particle['y'] = 0
                particle['x'] = random.randint(0, self.width)
    
    def draw(self, surface):
        # Desenhar gradiente de fundo
        for y in range(0, self.height, 2):
            alpha = 255 - int((y / self.height) * 100)
            color = (30, 30, 35, alpha)
            pygame.draw.rect(surface, color, (0, y, self.width, 2))
        
        # Desenhar partículas
        for particle in self.particles:
            pygame.draw.circle(surface, particle['color'], 
                             (int(particle['x']), int(particle['y'])), 
                             particle['size'])
        
        # Desenhar título e subtítulo com sombra
        shadow_offset = 3
        title_shadow = self.title_font.render("Controles", True, (20, 20, 20))
        subtitle_shadow = self.subtitle_font.render("Como Jogar", True, (20, 20, 20))
        
        surface.blit(title_shadow, (self.title_rect.x + shadow_offset, self.title_rect.y + shadow_offset))
        surface.blit(subtitle_shadow, (self.subtitle_rect.x + shadow_offset, self.subtitle_rect.y + shadow_offset))
        surface.blit(self.title, self.title_rect)
        surface.blit(self.subtitle, self.subtitle_rect)
        
        # Desenhar controles
        start_y = self.height//2 - (len(self.controls) * 40)
        for i, (text, desc) in enumerate(zip(self.control_texts, self.control_descriptions)):
            # Calcular posições
            text_rect = text.get_rect(right=self.width//2 - 20, centery=start_y + i * 80)
            desc_rect = desc.get_rect(left=self.width//2 + 20, centery=start_y + i * 80)
            
            # Desenhar com sombra
            shadow_color = (20, 20, 20)
            text_shadow = self.controls_font.render(text.get_rect().width * " ", True, shadow_color)
            desc_shadow = self.controls_font.render(desc.get_rect().width * " ", True, shadow_color)
            
            surface.blit(text_shadow, (text_rect.x + 2, text_rect.y + 2))
            surface.blit(desc_shadow, (desc_rect.x + 2, desc_rect.y + 2))
            surface.blit(text, text_rect)
            surface.blit(desc, desc_rect)
        
        # Desenhar informações do autor
        surface.blit(self.author, self.author_rect)
        surface.blit(self.ru, self.ru_rect)
        
        # Desenhar botão
        self.button.draw(surface) 