from agent_base import Agent
from utils.communication import send, receive
from collections import deque

class BDIAgent(Agent):
    def __init__(self, id, position, env):
        super().__init__(id, position, env)
        # Crenças: mapa { (x,y): resource_type }
        self.beliefs = {}
        # Desejos: lista de tuplas (position, value)
        self.desires = []
        # Intenções: tupla target (x,y)
        self.intentions = None
        # Plano de movimentação (lista de passos)
        self.plan = []

    def perceive(self):
        super().perceive()
        # Ler mensagens e atualizar crenças
        messages = receive(self.id)
        for msg in messages:
            content = msg['content']
            if content.get('type') == 'report':
                pos = tuple(content['position'])
                res = content['resource']
                self.beliefs[pos] = res

        # Relatar à base/local ou a outros agentes?
        # Exemplos: enviar descobertas
        # send(self.id, other_id, {'type':'report', ...})

    def decide(self):
        # Gerar desejos a partir das crenças:
        # valor = 10|20|50 conforme tipo
        value_map = {'C':10, 'M':20, 'E':50}
        self.desires = [ (pos, value_map[res]) for pos,res in self.beliefs.items() ]
        # Ordenar por valor desc
        self.desires.sort(key=lambda x: x[1], reverse=True)

        # Definir intenções: o recurso de maior valor ainda disponível
        # Verificar se crença ainda é válida (recurso não coletado)
        for pos, val in self.desires:
            x,y = pos
            if self.env.grid[y][x] == self.beliefs[pos]:
                self.intentions = pos
                break
        else:
            self.intentions = None

        # Planejar rota para intenção ou base se estiver carregando
        x0,y0 = self.position
        if self.carrying:
            goal = self.env.base_position
        else:
            goal = self.intentions
        if goal:
            self.plan = self.find_path((x0,y0), goal)

        # Definir próxima ação a partir do plano
        if self.carrying and (x0,y0) == self.env.base_position:
            self.next_action = ('deliver', None)
        elif goal and (x0,y0) == goal and not self.carrying:
            self.next_action = ('collect', None)
        elif self.plan:
            nx,ny = self.plan.pop(0)
            self.next_action = ('move', (nx-x0, ny-y0))
        else:
            self.next_action = ('move', (0,0))

    def act(self):
        super().act()
        # Após coletar E, enviar mensagem a um agente cooperativo
        if self.carrying == 'E':
            # encontra um colega livre
            for ag in self.env.agents:
                if ag.id != self.id and ag.carrying is None:
                    send(self.id, ag.id, {'type':'request_help', 'position': self.position})
                    break

    def find_path(self, start, goal):
        # copia de BFS do GoalBasedAgent
        queue = deque([start])
        visited = {start: None}
        dirs = [(1,0),(-1,0),(0,1),(0,-1)]
        while queue:
            cx, cy = queue.popleft()
            if (cx,cy) == goal:
                break
            for dx,dy in dirs:
                nx, ny = cx+dx, cy+dy
                if (0 <= nx < self.env.cols and 0 <= ny < self.env.rows
                    and self.env.is_free(nx, ny)
                    and (nx,ny) not in visited):
                    visited[(nx,ny)] = (cx,cy)
                    queue.append((nx,ny))
        # Reconstruir caminho
        path = []
        node = goal
        while node and node != start:
            path.append(node)
            node = visited.get(node)
        path.reverse()
        return path