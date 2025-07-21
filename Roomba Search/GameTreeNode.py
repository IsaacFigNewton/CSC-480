from config import offset_map

class GameTreeNode:
  def __init__(self, pos:tuple[int, int]):
    self.pos:tuple[int, int] = pos
    # a set of available actions from this node
    self.acts_available = set()

  def __hash__(self):
    return hash(self.pos)

  def get_proposed_move_pos(self, move):
    diff = offset_map[move]
    return (
        self.pos[0] + diff[0],
        self.pos[1] + diff[1]
    )