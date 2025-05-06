# utils/resource_manager.py
collected = {}
delivered = {}
points_map = {'C':10, 'M':20, 'E':50}

def register_collection(agent_id, resource_type):
    collected.setdefault(agent_id, {'C':0,'M':0,'E':0})
    collected[agent_id][resource_type] += 1

def register_delivery(agent_id, resource_type):
    collected.setdefault(agent_id, {'C':0,'M':0,'E':0})
    delivered.setdefault(agent_id, {'C':0,'M':0,'E':0})
    if collected[agent_id][resource_type] > 0:
        collected[agent_id][resource_type] -= 1
    delivered[agent_id][resource_type] += 1

def get_agent_score(agent_id):
    delivered.setdefault(agent_id, {'C':0,'M':0,'E':0})
    return sum(delivered[agent_id][r] * points_map[r] for r in delivered[agent_id])

def get_total_score():
    return sum(get_agent_score(a) for a in delivered)

def resources_remaining(env):
    return any(
        cell in ('C','M','E')
        for row in env.grid
        for cell in row
    )
