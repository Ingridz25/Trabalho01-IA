_queues = {}

def send(sender_id: int, receiver_id: int, content: dict):
    """
    Envia uma mensagem do agente sender_id para receiver_id.
    content pode conter, por exemplo:
      {'type':'report', 'position':(x,y), 'resource': 'C'}
    """
    if receiver_id not in _queues:
        _queues[receiver_id] = []
    # anexar remetente e conteúdo
    _queues[receiver_id].append({'from': sender_id, 'content': content})


def receive(agent_id: int) -> list:
    """
    Retorna e limpa a lista de mensagens para agent_id.
    """
    msgs = _queues.get(agent_id, [])
    _queues[agent_id] = []
    return msgs