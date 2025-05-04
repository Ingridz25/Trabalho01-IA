# agents/cooperative.py

from agent_base import Agent
from collections import deque
from utils.communication import send

# ID do BDI Agent
BDI_ID = 5

class CooperativeAgent(Agent):
    def __init__(self, id, position, env):
        super().__init__(id, position, env)
        self.plan = []
        self.target = None

    def perceive(self):
        super().perceive()
        # localizar todas as estruturas E
        E_positions = [
            (x, y)
            for y in range(self.env.rows)
            for x in range(self.env.cols)
            if self.env.grid[y][x] == 'E'
        ]
        self.perception['E_positions'] = E_positions

        # positions de agentes livres
        free_agents = [
            agent.position
            for agent in self.env.agents
            if agent.id != self.id and agent.carrying is None
        ]
        self.perception['free_agents'] = free_agents

        # REPORT: envia ao BDI cada estrutura E vista
        for (nx, ny) in E_positions:
            send(self.id, BDI_ID, {
                'type': 'report',
                'position': (nx, ny),
                'resource': 'E'
            })

    def decide(self):
        x, y = self.position

        # Se carregando E, direcionar para base
        if self.carrying == 'E':
            if (x, y) == self.env.base_position:
                self.next_action = ('deliver', None)
                self.plan = []
            else:
                if not self.plan or self.target != self.env.base_position:
                    self.plan = self.find_path((x, y), self.env.base_position)
                    self.target = self.env.base_position
                nx, ny = self.plan.pop(0)
                self.next_action = ('move', (nx - x, ny - y))
            return

        E_list = self.perception.get('E_positions', [])
        if not E_list:
            self.next_action = ('move', (0, 0))
            return

        # calcular utilidade para cada E
        utilities = []
        for tx, ty in E_list:
            dist = abs(tx - x) + abs(ty - y)
            available = len(self.perception.get('free_agents', []))
            util = 50 / (dist + 1) * (1 if available >= 1 else 0)
            utilities.append(((tx, ty), util))

        target_pos, _ = max(utilities, key=lambda item: item[1])

        if (x, y) == target_pos:
            self.next_action = ('collect', None)
            self.plan = []
            self.target = None
        else:
            if not self.plan or self.target != target_pos:
                self.plan = self.find_path((x, y), target_pos)
                self.target = target_pos
            nx, ny = self.plan.pop(0)
            self.next_action = ('move', (nx - x, ny - y))

    def find_path(self, start, goal):
        queue = deque([start])
        visited = {start: None}
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
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
        path = []
        node = goal
        while node and node != start:
            path.append(node)
            node = visited.get(node)
        path.reverse()
        return path
