from Classes.Core.ModuleMap import ModuleMap
from Core.PathPlanner import PathPlanner

class NavigationController:
    def __init__(self, moduleMap, pathPlanner):
        self.moduleMap = moduleMap
        self.pathPlanner = pathPlanner

        self.startLocation = None
        self.currentPosition = (0,0)
        self.targetLocation = None

        self.path = []
        self.pathIndex = 0

        self.chargingMode = False

    # -------------------------------
    # INIT
    # -------------------------------
    def startNav(self, startLocation):
        self.startLocation = startLocation
        self.currentPosition = startLocation

        self.targetLocation = self.choose_target()

        if self.targetLocation:
            self.requestPath(self.targetLocation)
            return True
        return False

    # -------------------------------
    # PATH REQUEST
    # -------------------------------
    def requestPath(self, target):
        if target is None:
            self.path = []
            return

        self.targetLocation = target
        self.path = self.pathPlanner.generatePath(self.currentPosition, target)
        self.pathIndex = 0

    # -------------------------------
    # UPDATE POSITION
    # -------------------------------
    def updatePosition(self, new_position):
        if self.currentPosition == self.startLocation:
            x, y = self.currentPosition
            self.moduleMap.map[x][y] = self.moduleMap.TILE_CHARGER #leave charging station alone
        else:
            x, y = self.currentPosition
            self.moduleMap.map[x][y] = self.moduleMap.TILE_CLEANED #place clean tile
        
        self.currentPosition = new_position

        x, y = new_position
        if self.moduleMap.map[x][y] in [self.moduleMap.TILE_UNCLEANED, self.moduleMap.TILE_DIRT, self.moduleMap.TILE_CLEANED]:
            self.moduleMap.map[x][y] = self.moduleMap.TILE_ROBOT  # move

    # -------------------------------
    # HANDLE OBSTACLE
    # -------------------------------
    def handle_obstacle(self, pos):     #isnt it belong in sensor and cleaning module?
        x, y = pos

        if self.moduleMap.map[x][y] not in [self.moduleMap.TILE_WALL, self.moduleMap.TILE_OBSTACLE]:
            self.moduleMap.map[x][y] = self.moduleMap.TILE_OBSTACLE

            # update planner map
            self.pathPlanner.updateMap(self.moduleMap.map)

            # Replan ONLY if obstacle affects remaining path
            if pos in self.path[self.pathIndex:]:
                self.requestPath(self.targetLocation)

    # -------------------------------
    # TARGET SELECTION
    # -------------------------------
    def choose_target(self):            #isnt it belong in cleaning module?
        cx, cy = self.currentPosition
        
        best = None
        best_dist = float('inf')

        for x in range(len(self.moduleMap.map)):
            for y in range(len(self.moduleMap.map[0])):
                if self.moduleMap.map[x][y] in [self.moduleMap.TILE_DIRT, self.moduleMap.TILE_UNCLEANED]:
                    dist = abs(cx - x) + abs(cy - y)

                    if dist < best_dist:
                        best_dist = dist
                        best = (x, y)

        return best

    # -------------------------------
    # CHARGING
    # -------------------------------
    def find_charger(self):
        for x in range(len(self.moduleMap.map)):
            for y in range(len(self.moduleMap.map[0])):
                if self.moduleMap.map[x][y] == self.moduleMap.TILE_CHARGER:
                    return (x, y)
        return None

    def go_to_charge(self):
        charger = self.find_charger()
        if charger:
            self.chargingMode = True
            self.requestPath(charger)

    def stop_charging_mode(self):
        self.chargingMode = False

    # -------------------------------
    # PATH MANAGEMENT
    # -------------------------------
    def ensure_path(self):
        if self.chargingMode:
            return

        if not self.path or self.pathIndex >= len(self.path):
            self.targetLocation = self.choose_target()

            if self.targetLocation:
                self.requestPath(self.targetLocation)

    # -------------------------------
    # MAIN STEP
    # -------------------------------
    def get_next_move(self):
        self.ensure_path()

        if not self.path or self.pathIndex >= len(self.path):
            return None

        next_tile = self.path[self.pathIndex]

        x, y = next_tile

        if self.moduleMap.map[x][y] == self.moduleMap.TILE_WALL:
            self.requestPath(self.targetLocation)
            return None

        self.updatePosition(next_tile)
        self.pathIndex += 1
        return next_tile

    # -------------------------------
    # STATUS
    # -------------------------------
    def is_done_cleaning(self):
        return not any(
            (self.moduleMap.TILE_UNCLEANED in row) or (self.moduleMap.TILE_DIRT in row)
            for row in self.moduleMap.map
        )