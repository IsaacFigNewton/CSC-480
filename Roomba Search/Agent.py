from WorldModel import WorldModel
from GameTreeNode import GameTreeNode
from Action import Action
from config import offset_map, opposite_map, get_offset, is_adjacent

class Agent:
  def __init__(self,
               world: WorldModel,
               initial_pos: tuple[int, int]):
    # vars for tracking position within game tree for DFS and UCS
    self.path = list()
    self.move_seq = list()
    self.pos = initial_pos

    self.world = world
    self.tree_node = GameTreeNode(self.pos)
    self.nodes_generated = 0
    self.nodes_expanded = 0


  def get_move_pos(self, move):
    diff = offset_map[move]
    return (
        self.pos[0] + diff[0],
        self.pos[1] + diff[1]
    )
  

  def expand_children(self):
    """
    Expand the children of this agent's current GameTreeNode by checking all possible moves
    and adding them to the set of children if they are legal moves.
    """

    self.nodes_expanded += 1
    # create a list of possible moves
    possible_moves = {
        move: self.get_move_pos(move)
        for move in offset_map.keys()
    }
    # filter it down to a list of legal moves
    for move, new_pos in possible_moves.items():
      proposed_move = Action(move, GameTreeNode(new_pos))
      # check if the move is legal and not already visited
      if proposed_move.is_legal(self.world, self.pos)\
        and proposed_move.end_state.pos not in self.path:
        # give the child a reference to the parent node
        proposed_move.end_state.parent = Action(opposite_map[move], self.tree_node)
        # add the proposed move to the set of available actions
        self.tree_node.available_acts.append(proposed_move)
        self.nodes_generated += 1


  def backtrack(self):
    """
    Backtrack to the previous node in the path.
    """
    if self.tree_node.parent is not None:
      # move the agent back to the parent node
      move_that_brought_us_here = opposite_map[self.tree_node.parent.act_type]
      self.execute_action(self.tree_node.parent)

      # prune this branch from the set of available actions
      new_act_list = list()
      for act in self.tree_node.available_acts:
        if act.act_type != move_that_brought_us_here:
          new_act_list.append(act)
      self.tree_node.available_acts = new_act_list

    else:
      raise ValueError("Cannot backtrack from the root node.")


  def execute_action(self, action: Action):
    """
    Execute the action by updating the agent's position and the world state.
    """
    if not action.is_legal(self.world, self.pos):
      raise ValueError(f"Proposed action {action.act_type} to {action.end_state.pos} is illegal from current position {self.pos}.")
    if action.act_type not in offset_map and action.act_type != "V":
      raise ValueError("Invalid action type")
    
    self.move_seq.append(action.act_type)
    # if the action is vacuuming, check if the cell is dirty
    # and update the world model accordingly
    if action.act_type == "V":
        self.world.remove_dirty_cell(self.pos)
    
    # if the action is a move, update the agent's set of visited nodes and position
    else:
        # add the current node to the set of visited nodes
        self.path.append(self.pos)
        # update the agent's position
        self.pos = action.end_state.pos
        # update the world model
        self.tree_node = action.end_state