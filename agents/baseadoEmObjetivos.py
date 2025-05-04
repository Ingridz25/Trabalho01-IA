# agents/goal_based.py

from agent_base import Agent
from collections import deque
from utils.communication import send

# ID do seu agente BDI
BDI_ID = 5

class GoalBasedAgent(Agent):
    def __init__(self, id, position, env):
        super().__init__(id, position, env)
        self.plan = []
        self.target = None

    def perceive(self):
        super().perceive()
        # coleta todos os recursos visíveis
        resources = []
        for y in range(self.env.rows):
            for x in range(self.env.cols):
                cell = self.env.grid[y][x]
                if cell in ['C','M','E']:
                    resources.append((x, y, cell))
        self.perception['resources'] = resources

        # REPORT: envia ao BDI todas as posições de recurso detectadas
        for (nx, ny, cell) in resources:
            send(self.id, BDI_ID, {
                'type': 'report',
                'position': (nx, ny),
                'resource': cell
            })

    def decide(self):
        x, y = self.position

        # se já está carregando, volta à base
        if self.carrying:
            if (x, y) == self.env.base_position:
                self.next_action = ('deliver', None)
                self.plan = []
            else:
                if not self.plan or self.target != self.env.base_position:
                    self.plan   = self.find_path((x, y), self.env.base_position)
                    self.target = self.env.base_position
                nx, ny = self.plan.pop(0)
                self.next_action = ('move', (nx - x, ny - y))
            return

        # sem recurso carregado, escolhe o melhor alvo
        resources = self.perception.get('resources', [])
        if not resources:
            self.next_action = ('move', (0, 0))
            return

        values = {'E':50, 'M':20, 'C':10}
        # ordena por valor desc e distância asc
        sorted_res = sorted(
            resources,
            key=lambda rc: (-values[rc[2]], abs(rc[0]-x) + abs(rc[1]-y))
        )
        tx, ty, _ = sorted_res[0]
        target_pos = (tx, ty)

        if (x, y) == target_pos:
            self.next_action = ('collect', None)
            self.plan = []
            self.target = None
        else:
            if not self.plan or self.target != target_pos:
                self.plan   = self.find_path((x, y), target_pos)
                self.target = target_pos
            nx, ny = self.plan.pop(0)
            self.next_action = ('move', (nx - x, ny - y))

    def find_path(self, start, goal):
        queue = deque([start])
        visited = {start: None}
        dirs = [(1,0),(-1,0),(0,1),(0,-1)]
        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) == goal:
                break
            for dx, dy in dirs:
                nx, ny = cx + dx, cy + dy
                if (0 <= nx < self.env.cols and 0 <= ny < self.env.rows
                        and self.env.is_free(nx, ny)
                        and (nx, ny) not in visited):
                    visited[(nx, ny)] = (cx, cy)
                    queue.append((nx, ny))
        # reconstrói o caminho
        path = []
        node = goal
        while node and node != start:
            path.append(node)
            node = visited.get(node)
        path.reverse()
        return path
