import networkx as nx
import json
import random
import numpy as np
import heapq as hq

from World import World

if __name__ == "__main__":
  contents = """7
  5
  _#a____
  ___#__#
  *__#_*_
  _______
  ____*__
  """

  world = World(contents)
  world.search("DFS")

  for r in world.grid:
    print(r)