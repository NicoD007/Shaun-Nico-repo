import pygame
from typing import Optional, Tuple
from RobotInternals.Sensor import Sensor
from Core.ModuleMap import ModuleMap
from RobotInternals.Battery import Battery


class CleaningModule(pygame.sprite.Sprite):
    STATE_IDLE = "idle"
    STATE_CLEANING = "cleaning"
    STATE_RETURNING = "returning"
    STATE_CHARGING = "charging"
    STATE_STOPPED = "stopped"
    STATE_ERROR = "error"

    def __init__(self, x: int, y: int, size: int = 50, initial_battery: int = 30):
        super().__init__()

        self.moduleID: int = None
        self.currentLocation: Tuple[int, int] = (x, y)
        self.speed: int = 0
        self.direction: str = ""
        self.isActive: bool = False
        self.unFinishedCleaning: bool = False
        self._sensor = Sensor(1)
        self._battery = Battery(joules=100, batteryPercentage=initial_battery)
        self._state = self.STATE_IDLE
        self._transitions = {
            self.STATE_IDLE: {
                "start": self.STATE_CLEANING,
                "stop": self.STATE_STOPPED,
                "fail": self.STATE_ERROR,
            },
            self.STATE_CLEANING: {
                "battery_low": self.STATE_RETURNING,
                "stop": self.STATE_STOPPED,
                "fail": self.STATE_ERROR,
            },
            self.STATE_RETURNING: {
                "docked": self.STATE_CHARGING,
                "stop": self.STATE_STOPPED,
                "fail": self.STATE_ERROR,
            },
            self.STATE_CHARGING: {
                "charged": self.STATE_CLEANING,
                "stop": self.STATE_STOPPED,
                "fail": self.STATE_ERROR,
            },
            self.STATE_STOPPED: {
                "start": self.STATE_CLEANING,
            },
            self.STATE_ERROR: {
                "stop": self.STATE_STOPPED,
            },
        }

        self.size = size
        self.image = self._draw_roomba(size)
        self.rect = self.image.get_rect(center=(x, y))

    def _draw_roomba(self, size: int) -> pygame.Surface:
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        radius = size // 2 - 2

        # Body
        pygame.draw.circle(surface, (60, 60, 60), (cx, cy), radius)

        # Inner ring
        pygame.draw.circle(surface, (80, 80, 80), (cx, cy), int(radius * 0.75), 1)

        # Bumper arc (front = top)
        bumper_rect = pygame.Rect(cx - int(radius * 0.85), cy - int(radius * 0.85),
                                  int(radius * 1.7), int(radius * 1.7))
        pygame.draw.arc(surface, (120, 120, 120), bumper_rect,
                        pygame.math.Vector2(0, -1).angle_to(pygame.math.Vector2(1, 0)) * 3.14159 / 180,
                        3.14159, 4)

        # Center button
        btn_r = max(size // 8, 4)
        pygame.draw.circle(surface, (40, 40, 40), (cx, cy), btn_r)
        pygame.draw.circle(surface, (100, 100, 100), (cx, cy), btn_r, 1)

        # Sensor eyes
        eye_offset = size // 7
        eye_r = max(size // 14, 2)
        for ex in [cx - eye_offset, cx + eye_offset]:
            ey = cy - size // 6
            pygame.draw.circle(surface, (30, 30, 30), (ex, ey), eye_r)
            pygame.draw.circle(surface, (200, 200, 200), (ex - 1, ey - 1), max(eye_r // 2, 1))

        # Side brushes
        brush_color = (90, 90, 90)
        brush_len = size // 6
        for side in [-1, 1]:
            bx = cx + side * (radius - 2)
            by = cy + size // 8
            for angle_offset in [-15, 0, 15]:
                import math
                angle = math.radians(90 + angle_offset)
                ex2 = int(bx + side * brush_len * math.cos(angle))
                ey2 = int(by + brush_len * math.sin(angle))
                pygame.draw.line(surface, brush_color, (bx, by), (ex2, ey2), 1)

        # Outline
        pygame.draw.circle(surface, (100, 100, 100), (cx, cy), radius, 1)

        return surface

    def setPosition(self, x: int, y: int) -> None:
        self.currentLocation = (x, y)
        self.rect.center = (x, y)

    def startCleaning(self) -> bool:
        transitioned = self.triggerEvent("start")
        self.isActive = transitioned or self._state == self.STATE_CLEANING
        return self.isActive

    def stop(self) -> bool:
        self.triggerEvent("stop")
        self.isActive = False
        return not self.isActive

    def scan(self) -> None:
        
        Sensor(1)
        Sensor.Scan(self.currentLocation, ModuleMap.requestMap())

        pass

    def getBatteryLevel(self) -> float:
        return float(self._battery.checkBattery())

    def noActionTimer(self) -> None:
        pass

    def readBattery(self) -> int:
        return self._battery.checkBattery()

    def setBatteryLevel(self, batteryPercentage: int) -> None:
        self._battery.setBattery(batteryPercentage)

    def requestCharging(self) -> bool:
        return self.readBattery() <= 20

    def shutDown(self) -> bool:
        return self.stop()

    def moveTo(self, target: Tuple[int, int]) -> None:
        self.setPosition(target[0], target[1])

    def setGridPosition(self, grid_pos: Tuple[int, int], cell_size: int) -> None:
        self.currentLocation = grid_pos
        pixel_x = (grid_pos[0] * cell_size) + (cell_size // 2)
        pixel_y = (grid_pos[1] * cell_size) + (cell_size // 2)
        self.rect.center = (pixel_x, pixel_y)

    def getState(self) -> str:
        return self._state

    def triggerEvent(self, event: str) -> bool:
        transitions = self._transitions.get(self._state, {})
        if event not in transitions:
            return False

        self._state = transitions[event]
        self.isActive = self._state in [self.STATE_CLEANING, self.STATE_RETURNING, self.STATE_CHARGING]
        return True