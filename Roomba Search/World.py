from WorldModel import WorldModel
from Agent import Agent
from searches import dfs, ucs

class World(WorldModel):
    def __init__(self, file_contents:str):
        world_lst = file_contents.split("\n")
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


    def search(self, algorithm:str) -> dict:
        if algorithm not in {"depth-first", "uniform-cost"}:
            raise ValueError(f"Unknown algorithm: {algorithm}. Supported algorithms: depth-first, uniform-cost.")

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

        match algorithm:
            # Depth-First Search
            case "depth-first":
                current_agent = dfs(current_agent)
                output["nodes_expanded"] = current_agent.nodes_expanded
                output["nodes_generated"] = current_agent.nodes_generated
            # Uniform Cost Search (basically BFS)
            case "uniform-cost":
                nodes_expanded, nodes_generated, current_agent = ucs(current_agent)
                output["nodes_expanded"] = nodes_expanded
                output["nodes_generated"] = nodes_generated

        output["path"] = current_agent.move_seq
        return output