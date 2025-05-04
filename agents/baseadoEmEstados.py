from agent_base import Agent
import random
from utils.communication import send

# ID do seu agente BDI
BDI_ID = 5

class StateBasedAgent(Agent):
    def __init__(self, id, position, env):
        super().__init__(id, position, env)
        self.visited = set()

    def perceive(self):
        super().perceive()
        # marca posição atual como visitada
        self.visited.add(self.position)

        # REPORT: se há recurso na célula atual, envia ao BDI
        x, y = self.position
        cell = self.env.grid[y][x]
        if cell in ('C', 'M', 'E'):
            send(self.id, BDI_ID, {
                'type': 'report',
                'position': (x, y),
                'resource': cell
            })

    def decide(self):
        x, y = self.position
        cell = self.env.grid[y][x]

        # se está sobre um recurso e não carrega nada, coleta
        if cell in ['C', 'M'] and self.carrying is None:
            self.next_action = ('collect', None)
            return

        # tenta mover para vizinho não visitado
        neighbors = [(x+dx, y+dy) for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]]
        random.shuffle(neighbors)
        for nx, ny in neighbors:
            if (0 <= nx < self.env.cols and 0 <= ny < self.env.rows
                and self.env.is_free(nx, ny)
                and (nx, ny) not in self.visited):
                self.next_action = ('move', (nx-x, ny-y))
                return

        # fallback: mover aleatoriamente para qualquer célula livre
        for nx, ny in neighbors:
            if (0 <= nx < self.env.cols and 0 <= ny < self.env.rows
                and self.env.is_free(nx, ny)):
                self.next_action = ('move', (nx-x, ny-y))
                return

        # se nada válido, fica parado
        self.next_action = ('move', (0, 0))

    def act(self):
        super().act()
