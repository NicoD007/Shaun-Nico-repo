
#remove update dirt from diagrams
#change cleanedCell to cleanedCells
#remove grid from diagram and code, not sure of its porpuse
#request map added to code and diagram

class ModuleMap: #Didn't implement arrows yet sorry          #what are arrows? 
    "Represents the robot's internal map."

    TILE_WALL = 0
    TILE_UNCLEANED = 1
    TILE_DIRT = 2
    TILE_OBSTACLE = 6
    TILE_CLEANED = 3
    TILE_ROBOT = 4
    TILE_CHARGER = 5

    def __init__(self, cleanedCells, mapData) -> None:
        self._cleaned_cell = cleanedCells
        self.map = mapData

    def updateObstacles(self, obstacleLocation) -> None:
        x, y = obstacleLocation
        self.map[x][y] = self.TILE_OBSTACLE

    def updateCell(self, Location, value) -> None:
        x, y = Location
        self.map[x][y] = value

    def mapComplete(self) -> bool:
        return not any(
            (self.TILE_UNCLEANED in row) or (self.TILE_DIRT in row)
            for row in self.map
        )
    
    def requestMap(self):
        return self.map