import pygame

class SpriteSheet:
    def __init__(self, filename):
        """
        Inicializa o sprite sheet
        :param filename: Caminho para a imagem do sprite sheet
        """
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
        except pygame.error as e:
            print(f"Não foi possível carregar o sprite sheet: {filename}")
            print(f"Erro: {e}")
            # Criar uma superfície vazia como fallback
            self.sheet = pygame.Surface((32, 32))
            self.sheet.fill((255, 0, 0))

    def get_image(self, x, y, width, height, scale=1, colorkey=None):
        try:
            # Criar uma nova superfície com o tamanho especificado
            image = pygame.Surface((width, height), pygame.SRCALPHA)
            
            # Copiar a parte específica do sprite sheet
            image.blit(self.sheet, (0, 0), (x, y, width, height))
            
            # Escalar a imagem se necessário
            if scale != 1:
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = pygame.transform.scale(image, (new_width, new_height))
            
            # Definir colorkey se especificado
            if colorkey is not None:
                if colorkey == -1:
                    colorkey = image.get_at((0, 0))
                image.set_colorkey(colorkey)
            
            return image
        except Exception as e:
            print(f"Erro ao obter imagem do sprite sheet: {e}")
            # Retornar uma superfície vermelha como fallback
            fallback = pygame.Surface((width, height), pygame.SRCALPHA)
            fallback.fill((255, 0, 0))
            return fallback

    def get_animation_frames(self, row, num_frames, frame_width, frame_height, scale=1):
        """
        Obtém uma sequência de frames para animação
        :param row: Linha do sprite sheet (Y)
        :param num_frames: Número de frames na animação
        :param frame_width: Largura de cada frame
        :param frame_height: Altura de cada frame
        :param scale: Fator de escala para redimensionar os frames
        :return: Lista de frames da animação
        """
        frames = []
        for frame in range(num_frames):
            x = frame * frame_width
            y = row * frame_height
            frames.append(self.get_image(x, y, frame_width, frame_height, scale))
        return frames 