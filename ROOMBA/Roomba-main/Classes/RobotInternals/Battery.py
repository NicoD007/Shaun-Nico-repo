class Battery:
    "Represents the robot's battery."

    def __init__(self, joules: int, batteryPercentage: int) -> None:
        self._joules = joules
        self._battery_percentage = batteryPercentage

    def checkBattery(self) -> int:
        "Return the current battery percentage."
        return self._battery_percentage

    def setBattery(self, percentage: int) -> None:
        "Set the battery percentage, clamped between 0 and 100."
        self._battery_percentage = max(0, min(100, percentage))
