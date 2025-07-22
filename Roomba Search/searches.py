from copy import deepcopy
import heapq as hq

from Agent import Agent
from Action import Action

def dfs(agent: Agent) -> Agent:
    # if there're no dirty cells left, return the agent
    if not agent.world.dirty_cells:
        return agent

    # if the agent is on a dirty cell, clean it and recurse
    if agent.world.is_dirty(agent.pos):
        agent.execute_action(Action("V", agent.tree_node))
        return dfs(agent)

    # expand children if not already expanded
    agent.expand_children()

    # while there are actions to try
    while agent.tree_node.available_acts:
        action = agent.tree_node.available_acts.pop()
        agent.execute_action(action)
        agent = dfs(agent)
    
    # if all actions are exhausted, backtrack to the previous node
    if agent.tree_node.parent is not None:
        agent.backtrack()
        return agent
    
    # if no valid path found, return None
    raise ValueError("No valid path found in DFS.")

def ucs(agent: Agent) -> tuple[int, int, Agent]:
    nodes_expanded = 0
    nodes_generated = 0

    # use a priority queue
    pq: list[tuple[int, Agent]] = list()
    hq.heapify(pq)
    hq.heappush(pq, agent)

    while pq:
        agent = hq.heappop(pq)

        # if the agent has found a path to clean all dirty cells, return it
        if not agent.world.dirty_cells:
            return nodes_expanded, nodes_generated, agent

        # if the agent is on a dirty cell, clean it
        if agent.world.is_dirty(agent.pos):
            agent.execute_action(Action("V", agent.tree_node))
            hq.heappush(pq, deepcopy(agent))
        
        # if the agent has available actions, expand them
        else:
            agent.expand_children()
            if not agent.tree_node.available_acts:
                agent.backtrack()
                hq.heappush(pq, deepcopy(agent))
            else:
                nodes_expanded += 1
                nodes_generated += len(agent.tree_node.available_acts)
                # for each available action, create a new agent and push it to the priority queue
                #    using the length of the path as the cost
                for action in agent.tree_node.available_acts:
                    new_agent = deepcopy(agent)
                    new_agent.execute_action(action)
                    hq.heappush(pq, new_agent)

    raise ValueError("No valid path found in UCS.")