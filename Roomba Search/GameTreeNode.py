from config import offset_map, is_legal_move
from WorldModel import WorldModel

class GameTreeNode:
  def __init__(self, pos:tuple[int, int]):
    self.pos = pos
    # a set of child game states of the form:
    #   (<edge type (N, S, E, W)>, <new GameTreeNode>)
    self.children = set()

  def __hash__(self):
    return hash(self.pos)

  def get_proposed_move_pos(self, move):
    diff = offset_map[move]
    return (
        self.pos[0] + diff[0],
        self.pos[1] + diff[1]
    )