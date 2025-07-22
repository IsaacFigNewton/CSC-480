import re
from copy import deepcopy
import heapq as hq

from WorldModel import WorldModel
from Agent import Agent
from Action import Action


class World(WorldModel):
    def __init__(self, file_contents:str):
        world_lst = file_contents.split("\n")
        print(world_lst)
        self.num_rows = int(world_lst[1])
        self.num_cols = int(world_lst[0])

        self.grid:list[list[str]] = list()
        self.dirty_cells = set()
        for i, row in enumerate(world_lst[2:]):
            self.grid.append(list())
            for j, c in enumerate(row):
                self.grid[i].append(c)
                if c == "*":
                    self.dirty_cells.add((i, j))
        print("Successfully loaded world:")
        for row in self.grid:
            print(row)


    def dfs(self, agent: Agent) -> Agent:
        # Base case: if there are no dirty cells, we're done
        if not agent.world.dirty_cells:
            return agent

        # If the agent is on a dirty cell, clean it and recurse
        if agent.world.is_dirty(agent.pos):
            agent.execute_action(Action("V", agent.tree_node))
            return self.dfs(agent)

        # Expand children if not already expanded
        agent.expand_children()

        # While there are actions to try
        while agent.tree_node.available_acts:
            action = agent.tree_node.available_acts.pop()
            agent.execute_action(action)
            agent = self.dfs(agent)
        
        # If all actions are exhausted, backtrack to the previous node
        if agent.tree_node.parent is not None:
            agent.backtrack()
            return agent
        
        # If no valid path found, return None
        raise ValueError("No valid path found in DFS.")

    def ucs(self, start_agent: Agent) -> tuple[int, int, Agent]:
        nodes_expanded = 0
        nodes_generated = 0

        # Priority queue: (cost, agent_id, agent)
        pq: list[tuple[int, Agent]] = list()
        # Initialize the priority queue with the starting agent
        hq.heapify(pq)
        hq.heappush(pq, start_agent)

        while pq:
            agent = hq.heappop(pq)

            # If the agent has found a path to clean all dirty cells, return it
            if not agent.world.dirty_cells:
                return nodes_expanded, nodes_generated, agent

            # If the agent is on a dirty cell, clean it
            if agent.world.is_dirty(agent.pos):
                agent.execute_action(Action("V", agent.tree_node))
                hq.heappush(pq, deepcopy(agent))
            
            # If the agent has available actions, expand them
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


    # depth-first search
    def search(self, algorithm:str = "DFS") -> dict:
        if algorithm not in {"DFS", "UCS"}:
            raise ValueError(f"Unknown algorithm: {algorithm}. Supported algorithms: DFS, UCS.")

        output = {
            "path": [],
            "nodes_generated": 0,
            "nodes_expanded": 0
        }

        # create an agent to explore the world
        current_agent = Agent(
            # pass the world model to the agent
            world=self,
            # get the initial position of the bot from the grid
            initial_pos=self.get_bot_pos_from_grid()
        )

        # Depth-First Search (DFS) algorithm
        if algorithm == "DFS":
            current_agent = self.dfs(current_agent)
            output["nodes_expanded"] = current_agent.nodes_expanded
            output["nodes_generated"] = current_agent.nodes_generated

        # Uniform Cost Search (UCS) algorithm (basically BFS)
        elif algorithm == "UCS":
            nodes_expanded, nodes_generated, current_agent = self.ucs(current_agent)
            output["nodes_expanded"] = nodes_expanded
            output["nodes_generated"] = nodes_generated

        output["path"] = current_agent.move_seq
        return output