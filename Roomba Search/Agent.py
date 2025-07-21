from WorldModel import WorldModel
from GameTreeNode import GameTreeNode
from Action import Action
from config import offset_map

class Agent:
  def __init__(self,
               world: WorldModel,
               initial_pos: tuple[int, int]):
    # vars for tracking position within game tree for DFS and UCS
    self.visited = set()
    self.path = list()
    self.pos = initial_pos

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
      proposed_move = Action(move, GameTreeNode(new_pos))
      # check if the move is legal
      if proposed_move.is_legal(self.world, self.pos):
        self.tree_node.acts_available.add(proposed_move)
        self.nodes_generated += 1


  def execute_action(self, action: Action):
    """
    Execute the action by updating the agent's position and the world state.
    """
    if not action.is_legal(self.world, self.pos):
      raise ValueError(f"Proposed action {action.act_type} to {action.end_state.pos} is illegal from current position {self.pos}.")
    if action.act_type not in offset_map and action.act_type != "V":
      raise ValueError("Invalid action type")
    
    self.path.append(action.act_type)
    # if the action is vacuuming, check if the cell is dirty
    # and update the world model accordingly
    if action.act_type == "V":
        self.world.remove_dirty_cell(self.pos)
    
    # if the action is a move, update the agent's set of visited nodes and position
    else:
        # add the action to the move sequence
        self.path.append(action.act_type)
        # add the current node to the set of visited nodes
        self.visited.add(self.pos)
        # update the agent's position
        self.pos = action.end_state.pos
        # update the world model
        self.tree_node = action.end_state