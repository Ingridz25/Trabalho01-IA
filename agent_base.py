import pygame

class Agent:
    def __init__(self, id, position, env):
        self.id = id
        self.position = position  # (x, y)
        self.env = env
        self.carrying = None      # tipo de recurso
        self.next_action = None   # armazenar decisão
        self.perception = {}      # células vizinhas e estado interno

    def perceive(self):
        """
        Atualiza self.perception com:
        - conteúdo das células adjacentes
        - distância até base
        - recurso carregado
        """
        x, y = self.position
        neighbors = {}
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < self.env.cols and 0 <= ny < self.env.rows:
                neighbors[(nx,ny)] = self.env.grid[ny][nx]
        self.perception['neighbors'] = neighbors
        bx, by = self.env.base_position
        self.perception['dist_to_base'] = abs(bx-x) + abs(by-y)
        self.perception['carrying'] = self.carrying

    def decide(self):
        """
        Define self.next_action como tupla:
        ('move', (dx,dy)) ou ('collect', None) ou ('deliver', None)
        Implementar lógica específica em subclasses.
        """
        self.next_action = ('move', (0,0))  # padrao: ficar parado

    def act(self):
        """
        Executa a ação definida em self.next_action:
        - move o agente
        - coleta recurso
        - entrega recurso na base
        """
        action, param = self.next_action
        x, y = self.position
        if action == 'move':
            dx, dy = param
            nx, ny = x+dx, y+dy
            if self.env.is_free(nx, ny):
                self.position = (nx, ny)
        elif action == 'collect':
            cx, cy = self.position
            if self.env.grid[cy][cx] in ['C','M','E'] and self.carrying is None:
                self.carrying = self.env.grid[cy][cx]
                self.env.remove_resource(cx, cy)
        elif action == 'deliver':
            if self.position == self.env.base_position and self.carrying:
                # ponto pra quem coletou (usar resource_manager)
                from utils.resource_manager import register_delivery
                register_delivery(self.id, self.carrying)
                self.carrying = None

    def draw(self, screen):
        """
        Desenha o agente como um círculo:
        - cor vermelha se carregando algo; verde se não.
        """
        x, y = self.position
        size = self.env.cell_size
        center = (x*size + size//2, y*size + size//2)
        radius = size//2 - 4
        color = (255,0,0) if self.carrying else (0,255,0)
        pygame.draw.circle(screen, color, center, radius)
