from types import Any
import heapq as hq

from WorldModel import WorldModel
from Agent import Agent


class World(WorldModel):
  def __init__(self, file_contents:str):
    world_lst = file_contents.split("\n")
    self.num_rows = int(world_lst[1])
    self.num_cols = int(world_lst[0])

    self.grid = list()
    self.dirty_cells = set()
    for i, row in enumerate(world_lst[2:-1]):
      self.grid.append(list())
      for j, c in enumerate(row):
        self.grid[i].append(c)
        if c == "*":
          self.dirty_cells.add((i, j))
    print("Successfully loaded world:")
    for row in self.grid:
      print(row)
  

  # depth-first search
  def search(self, algorithm:str = "DFS") -> dict[str, Any]:
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
        while current_agent.world.dirty_cells:
            current_agent.select_action()
        
        output["nodes_expanded"] = current_agent.nodes_expanded
        output["nodes_generated"] = current_agent.nodes_generated

    # Uniform Cost Search (UCS) algorithm (basically BFS)
    elif algorithm == "UCS":
        # create a priority queue for agents
        # each agent will explore a different path
        agents = list()
        hq.heapify(agents)
        hq.heappush(agents, (0, current_agent))
        
        # while there are agents in the priority queue
        while agents:
            # pop the agent with the lowest cost
            _, current_agent = hq.heappop(agents)
            
            # if the agent has no more dirty cells, it has found the shortest path
            if not current_agent.world.dirty_cells:
                break
            
            # otherwise, expand the current agent's available actions
            current_agent.expand_children()
            output["nodes_expanded"] += 1
            output["nodes_generated"] += len(current_agent.children)
            for action in current_agent.tree_node.children:
                # create a new agent
                new_agent = Agent(
                    world=current_agent.world,
                    initial_pos=current_agent.pos
                )
                # have the new agent execute the action, then add it to the priority queue
                new_agent.execute_action(action)
                hq.heappush(agents, (len(new_agent.path), new_agent))

    output["path"] = current_agent.path
    return output