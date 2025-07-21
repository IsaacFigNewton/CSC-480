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
  def search(self, algorithm:str = "DFS"):
    if algorithm not in {"DFS", "UCS"}:
        raise ValueError(f"Unknown algorithm: {algorithm}. Supported algorithms: DFS, UCS.")

    if algorithm == "DFS":
        print("Using Depth-First Search (DFS) algorithm.")
        agent = Agent(
            # pass the world model to the agent
            world=self,
            # get the initial position of the bot from the grid
            initial_pos=self.get_bot_pos_from_grid()
        )
        
        while self.dirty_cells:
            agent.select_action()
            # print([node[1].pos for node in agent.stack])
            # print(agent.world.dirt_count)

    elif algorithm == "UCS":
        print("Using Uniform Cost Search (UCS) algorithm.")
        # create a priority queue for agents
        # each agent will explore a different path
        agents = list()
        hq.heapify(agents)
        agent = Agent(
            # pass the world model to the agent
            world=self,
            # get the initial position of the bot from the grid
            initial_pos=self.get_bot_pos_from_grid()
        )

        # TODO: Implement Djikstra's algorithm for UCS, with each agent action having a cost of 1.
        #       each agent should store a different path exploring all nodes
        #       until all dirty cells are cleaned.
        

    print(f"{agent.nodes_generated} nodes generated.")
    print(f"{agent.nodes_expanded} nodes expanded.")