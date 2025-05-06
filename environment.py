import pygame
import random

class Environment:
    def __init__(self, cols, rows, cell_size,
                 obstacle_ratio=0.1,
                 resource_counts=None,
                 max_turns=200):
        self.cols = cols
        self.rows = rows
        self.cell_size = cell_size
        self.turn_counter = 0
        self.max_turns = max_turns
        # garante atributo `done`
        self.done = False

        # inicializa grid vazio
        self.grid = [['.' for _ in range(cols)] for _ in range(rows)]

        # posicionar obstáculos
        for y in range(rows):
            for x in range(cols):
                if random.random() < obstacle_ratio:
                    self.grid[y][x] = '#'

        # definir recursos padrão se não informado
        if resource_counts is None:
            resource_counts = {'C': 10, 'M': 5, 'E': 2}
        # posicionar recursos
        for resource, count in resource_counts.items():
            placed = 0
            while placed < count:
                x = random.randrange(cols)
                y = random.randrange(rows)
                if self.grid[y][x] == '.':
                    self.grid[y][x] = resource
                    placed += 1

        # definir base no centro
        cx, cy = cols // 2, rows // 2
        self.base_position = (cx, cy)
        self.grid[cy][cx] = 'B'

    def update(self):
        """
        Incrementa contador de turnos e atualiza `done`.
        """
        self.turn_counter += 1
        self.done = self.turn_counter >= self.max_turns

    def draw(self, screen):
        """
        Desenha cada célula do grid:
        . livre, # obstáculo, C cristal, M metal, E estrutura, B base
        """
        colors = {'.': (200, 200, 200), '#': (80, 80, 80),
                  'C': (0, 0, 255), 'M': (192, 192, 192),
                  'E': (255, 215, 0), 'B': (0, 255, 0)}
        for y in range(self.rows):
            for x in range(self.cols):
                cell = self.grid[y][x]
                rect = pygame.Rect(
                    x * self.cell_size, y * self.cell_size,
                    self.cell_size, self.cell_size
                )
                pygame.draw.rect(screen, colors.get(cell, (200,200,200)), rect)
                pygame.draw.rect(screen, (0,0,0), rect, 1)

    def is_free(self, x, y):
        """Retorna True se célula não é obstáculo nem base."""
        if 0 <= x < self.cols and 0 <= y < self.rows:
            return self.grid[y][x] in ['.', 'C', 'M', 'E']
        return False

    def remove_resource(self, x, y):
        """Remove o recurso na célula (após coleta)."""
        if self.grid[y][x] in ['C', 'M', 'E']:
            self.grid[y][x] = '.'