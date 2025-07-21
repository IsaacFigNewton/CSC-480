class Heuristic:
  def __init__(self, current_pos: tuple[int, int], function):
    self.pos = current_pos
    self.function = function

  def __call__(self, goal_pos):
    return self.function(self.pos, goal_pos)