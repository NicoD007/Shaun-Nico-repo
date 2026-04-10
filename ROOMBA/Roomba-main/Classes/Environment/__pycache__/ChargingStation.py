from Core.CleaningModule import CleaningModule


class ChargingStation:
    "Represents the robot's charging station."

    def __init__(self, stationPos: tuple[int, int], chargeRate: float = 5.0) -> None:
        # stationPos is the fixed map position where the robot can charge.
        self.stationPos = stationPos
        # chargeRate is the amount of battery percentage added per second.
        self._chargeRate = chargeRate

    def getChargeRate(self) -> float:
        # Simple accessor for the charging speed.
        return self._chargeRate

    def charge(self, cleaningModule: CleaningModule, duration: float = 1.0) -> int:
        # Ignore non-positive durations so we do not accidentally change the battery.
        if duration <= 0:
            return cleaningModule.readBattery()

        # Read the current battery, add charge based on elapsed time, and cap at 100%.
        current_level = cleaningModule.readBattery()
        charged_level = min(100, int(round(current_level + (self._chargeRate * duration))))
        # Write the new battery level back into the cleaning module.
        cleaningModule.setBatteryLevel(charged_level)
        return charged_level

    def atStation(self, position: tuple[int, int]) -> bool:
        # The robot is considered at the station only when its position exactly matches.
        return position == self.stationPos
