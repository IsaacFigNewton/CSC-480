import sys
import random
from World import World


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 planner.py [algorithm] [world-file]")
        sys.exit(1)
    algorithm = sys.argv[1]
    world_file = sys.argv[2]

    # Load the world file's contents
    with open(world_file, 'r') as file:
        contents = file.read().strip()

    world = World(contents)
    output = world.search("DFS")
    
    for r in output["path"]:
      print(r)
    print(f"{output['nodes_generated']} nodes generated.")
    print(f"{output['nodes_expanded']} nodes expanded.")

if __name__ == "__main__":
  main()