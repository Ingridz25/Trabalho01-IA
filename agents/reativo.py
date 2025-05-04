# agents/reactive.py

from agent_base import Agent
import random
from utils.communication import send

# id do seu agente BDI
BDI_ID = 5

class ReactiveAgent(Agent):
    def perceive(self):
        # 1) coleta percepções padrão (vizinhança, carregando, etc)
        super().perceive()

        # 2) reporta ao BDI tudo o que enxerga de recurso
        for (nx, ny), cell in self.perception['neighbors'].items():
            if cell in ('C', 'M', 'E'):
                send(self.id, BDI_ID, {
                    'type': 'report',
                    'position': (nx, ny),
                    'resource': cell
                })

    def decide(self):
        x, y = self.position
        cell = self.env.grid[y][x]
        # se há cristal aqui e não está carregando, coleta
        if cell == 'C' and self.carrying is None:
            self.next_action = ('collect', None)
        else:
            # caso contrário, movimento aleatório
            dx, dy = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
            self.next_action = ('move', (dx, dy))

    def act(self):
        super().act()
