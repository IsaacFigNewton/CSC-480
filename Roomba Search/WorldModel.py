class WorldModel:
    def __init__(self,
                 grid: list[list[str]],
                 dirty_cells: set[tuple[int, int]],):
        self.grid = grid
        self.num_rows = len(grid)
        self.num_cols = len(grid[0]) if self.num_rows > 0 else 0
        self.dirty_cells = dirty_cells

    def get_bot_pos_from_grid(self):
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if self.grid[row][col] == "@":
                    return (row, col)
        raise ValueError("No bot found in the grid")
    
    def is_dirty(self, pos: tuple[int, int]) -> bool:
        """
        Check if the cell at the given position is dirty.
        """
        return pos in self.dirty_cells
    
    def remove_dirty_cell(self, pos: tuple[int, int]):
        """
        Remove a dirty cell from the world model.
        """
        if pos in self.dirty_cells:
            self.dirty_cells.remove(pos)
            self.grid[pos[0]][pos[1]] = "_"
        else:
            raise ValueError(f"Cell {pos} is not dirty.")