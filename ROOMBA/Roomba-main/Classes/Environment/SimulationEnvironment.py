import sys
import os

# Add Classes directory to sys.path for absolute imports
classes_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if classes_path not in sys.path:
    sys.path.insert(0, classes_path)

import pygame

from Environment.ChargingStation import ChargingStation
from Environment.RoomMap import RoomMap
from Core.CleaningModule import CleaningModule
from Core.ModuleMap import ModuleMap
from Core.PathPlanner import PathPlanner
from Core.NavigationController import NavigationController
from Communication.MQTTClient import MQTTClient


class SimulationEnvironment:
    def __init__(
        self,
        window_width: int = 800,
        window_height: int = 600,
        fps: int = 30,
        title: str = "Simulation Environment",
        charging_station: ChargingStation | None = None,
        room_map: RoomMap | None = None,
        cleaning_module: CleaningModule | None = None,
    ) -> None:
        self._window = None
        self._window_width = window_width
        self._window_height = window_height
        self._fps = fps
        self._title = title
        self._clock = None
        self._running = False
        self._charging_station = charging_station
        self._room_map = room_map
        self._cleaning_module = cleaning_module
        self._sprites = pygame.sprite.Group()
        self._mqtt_client = None
        self._mqtt_connected = False
        self._module_map: ModuleMap | None = None
        self._path_planner: PathPlanner | None = None
        self._navigation: NavigationController | None = None
        self._font: pygame.font.Font | None = None
        self._battery_tick_accumulator: float = 0.0

    def initialize(self) -> bool:
        pygame.init()
        self._window = pygame.display.set_mode(
            (self._window_width, self._window_height)
        )
        pygame.display.set_caption(self._title)
        self._clock = pygame.time.Clock()
        self._font = pygame.font.SysFont("Arial", 18)
        self._running = True
        
        # Calculate tile size based on the room map's maximum dimension
        blueprint = getattr(self._room_map, '_blueprint', None)
        if blueprint:
            rows = len(blueprint)
            cols = len(blueprint[0]) if blueprint[0] else 0
            max_dim = max(rows, cols)
            cell_width = self._window_width // max_dim if max_dim else 20
            cell_height = self._window_height // max_dim if max_dim else 20
            self._cell_size = min(cell_width, cell_height)
        else:
            self._cell_size = 30  # fallback

        # Add cleaning module to sprites if provided
        if self._cleaning_module is not None:
            self._sprites.add(self._cleaning_module)

        if blueprint:
            self._module_map = self._room_map.pushMap(blueprint)
            self._path_planner = PathPlanner(currentPath=[], moduleMap=self._module_map)
            self._navigation = NavigationController(self._module_map, self._path_planner)

            start_tile = self._find_tile(ModuleMap.TILE_CHARGER) or (0, 0)
            self._navigation.currentPosition = start_tile
            if self._cleaning_module is not None:
                self._cleaning_module.setGridPosition(start_tile, self._cell_size)

        return True

    def connect_mqtt(self) -> bool:
        if self._cleaning_module is None:
            self._mqtt_connected = False
            return False

        self._mqtt_client = MQTTClient(self._cleaning_module)
        self._mqtt_connected = self._mqtt_client.connect()
        return self._mqtt_connected

    def publish_start_command(self) -> bool:
        if self._mqtt_client is None or not self._mqtt_connected:
            if self._cleaning_module is not None:
                self._cleaning_module.startCleaning()
                if self._navigation is not None:
                    self._navigation.startNav(self._cleaning_module.currentLocation)
                print("Fallback start: cleaning started locally.")
                return True
            return False

        published = self._mqtt_client.publish_command("start")
        if self._cleaning_module is not None:
            self._cleaning_module.startCleaning()
        if not published and self._cleaning_module is not None:
            if self._navigation is not None:
                self._navigation.startNav(self._cleaning_module.currentLocation)
            print("Fallback start: cleaning started locally.")
            return True

        if published and self._navigation is not None and self._cleaning_module is not None:
            self._navigation.startNav(self._cleaning_module.currentLocation)
        return published

    def stop(self) -> bool:
        if self._mqtt_client is not None:
            self._mqtt_client.disconnect()
        self._running = False
        pygame.quit()
        return True

    def set_fps(self, fps: int) -> None:
        self._fps = fps

    def clear(self, color=(30, 30, 30)) -> None:
        if self._window is not None:
            self._window.fill(color)

    def draw_room_map(self) -> None:
        if self._window is None or self._room_map is None:
            return
        
        # Get the blueprint from room map
        blueprint = getattr(self._room_map, '_blueprint', None)
        if not blueprint:
            return
            
        # Calculate cell size to fit the map in the window
        cell_width = self._window_width // len(blueprint)
        cell_height = self._window_height // len(blueprint[0]) if blueprint[0] else 20
        cell_size = min(cell_width, cell_height)
        
        # Draw each cell
        for x, column in enumerate(blueprint):
            for y, cell in enumerate(column):
                rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
                if cell == ModuleMap.TILE_UNCLEANED:  # Room floor
                    pygame.draw.rect(self._window, (100, 100, 100), rect)
                    pygame.draw.rect(self._window, (150, 150, 150), rect, 1)  # Border
                elif cell == ModuleMap.TILE_DIRT:  # Dirt tile
                    pygame.draw.rect(self._window, (200, 50, 50), rect)  # Red for dirt
                    pygame.draw.rect(self._window, (255, 100, 100), rect, 1)
                elif cell == ModuleMap.TILE_WALL:  #wall
                    pygame.draw.rect(self._window, (20, 20, 20), rect)  # Gray for walls
                    pygame.draw.rect(self._window, (50, 50, 50), rect, 1)
                elif cell == ModuleMap.TILE_CLEANED:  #cleaned tile
                    pygame.draw.rect(self._window, (255, 182, 193), rect)  # pink
                    pygame.draw.rect(self._window, (50, 50, 50), rect, 1)
                elif cell == ModuleMap.TILE_ROBOT:  #cleaning module                                                       #place roomba sprite on top of it
                    pygame.draw.rect(self._window, (146, 41, 82), rect)  # por por a
                    pygame.draw.rect(self._window, (150, 150, 150), rect, 1)
                elif cell == ModuleMap.TILE_CHARGER:  #charging station
                    pygame.draw.rect(self._window, (245, 217, 10), rect)  # yollowww
                    pygame.draw.rect(self._window, (50, 50, 150), rect, 1)

    def draw_battery_status(self) -> None:
        if self._window is None or self._cleaning_module is None:
            return

        battery_level = self._cleaning_module.readBattery()
        state = self._cleaning_module.getState()
        bar_width = 180
        bar_height = 18
        x = 12
        y = 12

        pygame.draw.rect(self._window, (25, 25, 25), (x - 4, y - 4, bar_width + 8, bar_height + 40), border_radius=8)
        pygame.draw.rect(self._window, (40, 40, 40), (x, y, bar_width, bar_height), border_radius=6)

        if state == CleaningModule.STATE_CHARGING:
            level_color = (60, 170, 240)
            status_text = "Charging"
        elif state == CleaningModule.STATE_RETURNING:
            level_color = (230, 190, 20)
            status_text = "Returning"
        elif state == CleaningModule.STATE_CLEANING:
            level_color = (80, 220, 80) if battery_level > 50 else (230, 190, 20) if battery_level > 20 else (220, 60, 60)
            status_text = "Cleaning"
        else:
            level_color = (160, 160, 160)
            status_text = state.capitalize()

        fill_width = max(0, min(bar_width, int(bar_width * (battery_level / 100))))
        pygame.draw.rect(self._window, level_color, (x, y, fill_width, bar_height), border_radius=6)

        info_text = f"Battery: {battery_level}%  [{status_text}]"
        if self._font is None:
            self._font = pygame.font.SysFont("Arial", 18)
        text_surface = self._font.render(info_text, True, (240, 240, 240))
        self._window.blit(text_surface, (x, y + bar_height + 8))

        if state == CleaningModule.STATE_CHARGING:
            charge_text = self._font.render("Charging at station...", True, (160, 220, 255))
            self._window.blit(charge_text, (x, y + bar_height + 26))

    def _find_tile(self, tile_value: int) -> tuple[int, int] | None:
        if self._room_map is None:
            return None

        blueprint = getattr(self._room_map, '_blueprint', None)
        if not blueprint:
            return None

        for x in range(len(blueprint)):
            for y in range(len(blueprint[0])):
                if blueprint[x][y] == tile_value:
                    return (x, y)
        return None

    def _step_cleaning_cycle(self, dt: float) -> None:
        if self._cleaning_module is None or self._navigation is None or self._charging_station is None:
            return

        state = self._cleaning_module.getState()

        if state == CleaningModule.STATE_CLEANING:
            if self._cleaning_module.requestCharging():
                self._navigation.go_to_charge()
                self._cleaning_module.triggerEvent("battery_low")
                return

            next_move = self._navigation.get_next_move()
            if next_move is None:
                if self._navigation.is_done_cleaning():
                    self._navigation.go_to_charge()
                    self._cleaning_module.triggerEvent("battery_low")
                return

            self._cleaning_module.setGridPosition(next_move, self._cell_size)
            self._drain_battery(dt)

        elif state == CleaningModule.STATE_RETURNING:
            if not self._navigation.chargingMode:
                self._navigation.go_to_charge()

            next_move = self._navigation.get_next_move()
            if next_move is not None:
                self._cleaning_module.setGridPosition(next_move, self._cell_size)
                self._drain_battery(dt)

            if self._charging_station.atStation(self._navigation.currentPosition):
                self._cleaning_module.triggerEvent("docked")

        elif state == CleaningModule.STATE_CHARGING:
            level = self._charging_station.charge(self._cleaning_module, dt)
            if level >= 80:
                self._navigation.stop_charging_mode()
                self._navigation.requestPath(self._navigation.choose_target())
                self._cleaning_module.triggerEvent("charged")

    def _drain_battery(self, dt: float) -> None:
        self._battery_tick_accumulator += dt
        if self._battery_tick_accumulator < 1.0:
            return

        current_battery = self._cleaning_module.readBattery()
        self._cleaning_module.setBatteryLevel(current_battery - 1)
        self._battery_tick_accumulator = 0.0


    def update(self) -> float:
        if self._window is None or self._clock is None:
            return 0.0

        pygame.display.flip()
        delta_ms = self._clock.tick(self._fps)
        return delta_ms / 1000.0

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._running = False
                elif event.key == pygame.K_s:
                    if self.publish_start_command():
                        print("Published: start")
        return self._running
