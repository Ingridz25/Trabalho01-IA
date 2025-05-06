import pygame
from environment import Environment
from agents.reativo import ReactiveAgent
from agents.baseadoEmEstados import StateBasedAgent
from agents.baseadoEmObjetivos import GoalBasedAgent
from agents.cooperativo import CooperativeAgent
from agents.bdi import BDIAgent

from utils.resource_manager import resources_remaining

def main():
    # 1) Inicializa o Pygame
    pygame.init()

    # 2) Cria a janela e o clock
    cols, rows, cell_size = 20, 15, 30
    screen = pygame.display.set_mode((cols * cell_size, rows * cell_size))
    pygame.display.set_caption("Simulação Multiagente")
    clock = pygame.time.Clock()

    # 3) Configura o ambiente e os agentes (incluindo BDI)
    env = Environment(cols, rows, cell_size)
    BDI_ID = 5
    env.agents = [
        ReactiveAgent(1,        (1, 1),           env),
        StateBasedAgent(2,       (cols-2, 1),      env),
        GoalBasedAgent(3,        (1, rows-2),      env),
        CooperativeAgent(4,      (cols-2, rows-2), env),
        BDIAgent(BDI_ID,              (cols//2, 1),     env)
    ]

    # 4) Loop principal com condições de parada
    running = True
    while running and not env.done and resources_remaining(env):
        # tratar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # atualizar ambiente
        env.update()
        print(f"Turno: {env.turn_counter}")

        # executar lógica de cada agente
        for agent in env.agents:
            agent.perceive()
            agent.decide()
            agent.act()

        # desenhar cenário
        screen.fill((0, 0, 0))
        env.draw(screen)
        for agent in env.agents:
            agent.draw(screen)

        # mostrar turno na barra de título
        pygame.display.set_caption(f"Simulação – Turno {env.turn_counter}")

        # atualizar display e controlar FPS
        pygame.display.flip()
        clock.tick(10)

    # 5) Finaliza
    pygame.quit()

if __name__ == "__main__":
    main()