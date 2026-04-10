class Sensor:
    def __init__(self, sensorRadius):
        self.sensorRadius = sensorRadius

    # -------------------------------
    # GET CELLS IN RADIUS
    # -------------------------------
    def _get_cells_in_radius(self, position, grid):
        cx, cy = position
        cells = []

        for x in range(len(grid)):
            for y in range(len(grid[0])):
                dist = abs(cx - x) + abs(cy - y)

                if dist <= self.sensorRadius:
                    cells.append((x, y))

        return cells
    '''
    # -------------------------------
    # DIRT SCAN
    # -------------------------------
    def dirtScan(self, position, grid):
        cells = self._get_cells_in_radius(position, grid)

        dirt_cells = []
        for (x, y) in cells:
            if grid[x][y] == 1:  # uncleaned
                dirt_cells.append((x, y))

        return dirt_cells
    '''
    # -------------------------------
    # OBSTACLE SCAN
    # -------------------------------
    def Scan(self, position, grid):
        cells = self._get_cells_in_radius(position, grid)

        obstacle_cells = []
        for (x, y) in cells:
            if grid[x][y] in [0, 2]:  # wall or obstacle
                obstacle_cells.append((x, y))

        return obstacle_cells