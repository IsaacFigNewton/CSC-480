import heapq as hq
from Action import Action

class DecisionProcess:
  def __init__(self,
               act_store_type:str="stack"):
    if act_store_type == "stack":
      self.act_store = list()
    elif act_store_type == "priority queue":
      self.act_store = list()
      hq.heapify(self.act_store)

    self.act_store_type = act_store_type


  def push(self, action:Action, heuristic):
    match self.act_store_type:
      case "stack":
        self.act_store.append(action)
      case "priority queue":
        hq.heappush(
            self.act_store,
            (heuristic(action.end_state.pos), action)
        )


  def pop(self):
    match self.act_store_type:
      case "stack":
        return self.act_store.pop()
      case "priority queue":
        return hq.heappop(self.act_store)[1]


  def remove(self, action:Action):
    match self.act_store_type:
      case "stack":
        self.act_store.pop(action)
      case "priority queue":
        self.act_store = hq.heapify([
            a for a in self.act_store
            if a[1] != action
        ])