# save an offset map
offset_map = {
    # idx 0 => row offset
    # idx 1 => col offset
    "N": (-1, 0),
    "S": (1, 0),
    "E": (0, 1),
    "W": (0, -1)
}

# ensure the move is not OOB and not blocked by an obstacle
def is_legal_move(world, current_pos, proposed_pos):
  # check adjacency
  if not (proposed_pos[0] - current_pos[0], proposed_pos[1] - current_pos[1]) in offset_map.values():
    return False
  # check if the row idx is OOB
  if proposed_pos[0] < 0 or proposed_pos[0] >= world.num_rows:
    return False
  # check if the row idx is OOB
  if proposed_pos[1] < 0 or proposed_pos[1] >= world.num_cols:
    return False
  # check for obstacles
  if world.grid[proposed_pos[0]][proposed_pos[1]] == "#":
    return False
  return True