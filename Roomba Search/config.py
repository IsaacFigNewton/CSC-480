# save a move:offset map
# idx 0 => row offset
# idx 1 => col offset
offset_map = {
    "N": (-1, 0),
    "S": (1, 0),
    "E": (0, 1),
    "W": (0, -1)
}

opposite_map = {
    "N": "S",
    "S": "N",
    "E": "W",
    "W": "E"
}

def get_offset(pos1: tuple[int, int], pos2: tuple[int, int]) -> tuple[int, int]:
    """
    Calculate the offset from pos1 to pos2.
    """
    return (pos2[0] - pos1[0], pos2[1] - pos1[1])

def is_adjacent(pos1: tuple[int, int], pos2: tuple[int, int]) -> bool:
    """
    Check if two positions are adjacent in the grid.
    """
    return get_offset(pos1, pos2) in offset_map.values()