import sys
import random
from World import World


def main(contents: str):
    if len(sys.argv) != 5:
        print("Usage: python3 planner.py <world_spec_filename> <algorithm>")
        sys.exit(1)

    # Load the world from the provided contents
    # rows = int(sys.argv[1])
    # cols = int(sys.argv[2])
    # blocked_fraction = float(sys.argv[3])
    # num_dirty = int(sys.argv[4])

    world = World(contents)
    return world.search("DFS")

if __name__ == "__main__":
  output = main(
      contents="""7
      5
      _#a____
      ___#__#
      *__#_*_
      _______
      ____*__
      """
  )

  for r in output["path"]:
    print(r)
  print("Total nodes generated:", output["nodes_generated"])
  print("Total nodes expanded:", output["nodes_expanded"])