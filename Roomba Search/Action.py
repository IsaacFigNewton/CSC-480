from WorldModel import WorldModel
from GameTreeNode import GameTreeNode
from config import offset_map

class Action:
  def __init__(self,
               act_type:str,
               end_state:GameTreeNode):
    self.act_type = act_type
    self.end_state = end_state

  def __hash__(self):
    return hash(self.end_state.pos)

  def __lt__(self, other):
      return self.end_state.pos < other.end_state.pos

  def __gt__(self, other):
      return self.end_state.pos > other.end_state.pos
  
  def is_legal(self, world:WorldModel, current_pos):
    new_pos = self.end_state.pos
    proposed_offset = (new_pos[0] - current_pos[0], new_pos[1] - current_pos[1])

    try:
      # check if the proposed move is vaccuuming
      if self.act_type == "V" and proposed_offset == (0, 0):
        if not world.is_dirty(new_pos):
          print(f"Cannot vacuum a clean cell at {new_pos}.")
          return False
        else:
          return True
      # check adjacency
      if proposed_offset not in offset_map.values():
        return False
      # check if the row idx is OOB
      if new_pos[0] < 0 or new_pos[0] >= world.num_rows:
        return False
      # check if the row idx is OOB
      if new_pos[1] < 0 or new_pos[1] >= world.num_cols:
        return False
      # check for obstacles
      if world.grid[new_pos[0]][new_pos[1]] == "#":
        return False
      return True
    
    except IndexError:
      raise ValueError(f"Proposed position is OOB: {new_pos}.\nWorld size: {world.num_rows}x{world.num_cols}.")