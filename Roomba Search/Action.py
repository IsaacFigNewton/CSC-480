from GameTreeNode import GameTreeNode

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