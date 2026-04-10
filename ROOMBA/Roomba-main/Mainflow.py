import sys
import os

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("Classes"))

from Classes.Environment.SimulationEnvironment import SimulationEnvironment
from Classes.Environment.RoomMap import RoomMap
from Classes.Core.CleaningModule import CleaningModule
from Classes.Environment.ChargingStation import ChargingStation


def main() -> None:
    # Create room map
    room_map = RoomMap(width=22, height=25, objects=[], numOfRooms=6)
    room_map.generate()
    print("Room map generated")

    # Calculate cell size based on map dimensions and make the window square
    window_width = 900
    window_height = 650
    blueprint = getattr(room_map, '_blueprint', None)
    if blueprint:
        rows = len(blueprint)
        cols = len(blueprint[0]) if blueprint[0] else 0
        max_dim = max(rows, cols)
        cell_size = min(window_width // max_dim, window_height // max_dim)
        window_width = cell_size * max_dim
        window_height = cell_size * max_dim
    else:
        cell_size = 30  # fallback

    # Create cleaning module
    cleaning_module = CleaningModule(x=cell_size//5, y=cell_size//2, size=cell_size, initial_battery=30)
    print("Cleaning module created with starting battery at 30%")

    # Create charging station
    charging_station = ChargingStation(stationPos=(0, 0))
    print("Charging station created")

    # Create simulation environment with the components
    env = SimulationEnvironment(
        window_width=window_width,
        window_height=window_height,
        fps=60,
        charging_station=charging_station,
        room_map=room_map,
        cleaning_module=cleaning_module
    )

    # Initialize and connect before entering the main loop
    if not env.initialize():
        print("Failed to initialize simulation environment")
        return

    env.connect_mqtt()
    env.publish_start_command()

    while env.handle_events():
        env.clear((20, 20, 20))
        env.draw_room_map()
        if env._window is not None:
            env._sprites.draw(env._window)
        env.draw_battery_status()
        dt = env.update()
        env._step_cleaning_cycle(dt)

    env.stop()


if __name__ == "__main__":
    main()
