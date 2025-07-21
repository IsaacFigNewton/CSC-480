from WorldModel import WorldModel
from GameTreeNode import GameTreeNode
from Action import Action
from config import offset_map, is_legal_move

class Agent:
  def __init__(self,
               world: WorldModel,
               initial_pos: tuple[int, int]):
    # vars for tracking position within game tree for DFS and UCS
    self.path = list()
    self.pos = initial_pos
    self.stack = list()

    self.world = world
    self.tree_node = GameTreeNode(self.pos)
    self.nodes_generated = 0
    self.nodes_expanded = 0

  
  def expand_children(self):
    """
    Expand the children of this agent's current GameTreeNode by checking all possible moves
    and adding them to the set of children if they are legal moves.
    """

    self.nodes_expanded += 1
    # create a list of possible moves
    possible_moves = {
        move: self.tree_node.get_proposed_move_pos(move)
        for move in offset_map.keys()
    }
    # filter it down to a list of legal moves
    for move, new_pos in possible_moves.items():
      if is_legal_move(self.world, self.pos, new_pos):
        self.tree_node.children.add(Action(move, GameTreeNode(new_pos)))
        self.nodes_generated += 1


  def current_cell_dirty(self):
    """
    Check if the current cell is dirty.
    """
    return self.world.grid[self.pos[0]][self.pos[1]] == "*"

  def execute_action(self, action: Action):
    """
    Execute the action by updating the agent's position and the world state.
    """
    if not is_legal_move(self.world, self.pos, action.end_state.pos):
      raise ValueError("Proposed action is not legal")
    if action.act_type not in offset_map and action.act_type != "V":
      raise ValueError("Invalid action type")
    
    # if the action is vacuuming, check if the cell is dirty
    # and update the world model accordingly
    if action.act_type == "V":
        if not self.current_cell_dirty():
            raise ValueError("Cannot clean a cell that is not dirty")
        else:
            print("V")
            self.world.dirty_cells.remove(self.pos)
            self.world.grid[self.pos[0]][self.pos[1]] = "_"
            return
    
    # if the action is a move, update the agent's path and position
    else:
        # add the current node to the path
        self.path.append(self.pos)
        # update the agent's position
        self.pos = action.end_state.pos
        # update the world model
        self.tree_node = action.end_state


  def select_action(self, action:Action|None=None):
    """
    Select the next action to take based on the current state of the world.
    If an action is provided, it will be executed immediately.
    Otherwise, the agent will expand its current node and select the next action
    based on the decision process.
    """
    # if a legal action is provided, execute it
    if action:
        self.execute_action(action)
        return

    # if the bot is on dirt, clean it
    if self.current_cell_dirty():
        self.execute_action(Action("V", self.tree_node))
        return

    # expand all the current node's children
    self.expand_children()
    for child in self.tree_node.children:
        # add new, unexplored children to the set under consideration
        if child.end_state.pos not in self.path:
            self.stack.append(child)

    # take the first available new move
    next_move = self.stack.pop()
    print(next_move.act_type)
    # print(next_move[0], next_move[1].pos)
    self.pos = next_move.end_state.pos
    self.tree_node = next_move.end_state