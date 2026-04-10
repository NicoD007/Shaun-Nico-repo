# Autonomous Cleaning Module Simulator

## Overview
This project simulates an autonomous cleaning module in a bounded indoor environment with obstacles, charging behavior, and MQTT command support. The simulation is implemented in Python with `pygame` for visualization.

## Implemented Features
- Object-oriented architecture with 10+ classes.
- Encapsulation of robot internals (battery, sensor, map, planner).
- Formal state machine for robot lifecycle (embedded in `CleaningModule`):
  - `IDLE -> CLEANING -> RETURNING -> CHARGING -> CLEANING`
  - plus `STOPPED` and `ERROR` states.
- Distributed communication hook using MQTT (`roomba/command`).
- Interactive visualization with keyboard control.

## Controls
- `S`: start cleaning cycle.
- `ESC`: exit simulation.

## Project Structure
- `Mainflow.py`: application entry point.
- `Classes/Environment/SimulationEnvironment.py`: main runtime loop, drawing, event handling.
- `Classes/Core/CleaningModule.py`: robot entity and embedded state machine logic.
- `Classes/Core/NavigationController.py`: movement and path progression.
- `Classes/Core/PathPlanner.py`: path planning logic.
- `Classes/Communication/MQTTClient.py`: MQTT publish/subscribe adapter.

## Setup (Windows)
1. Install Python 3.10+.
2. Open terminal in the project root.
3. Install dependencies:
   - `py -m pip install -r requirements.txt`
4. Start MQTT broker (recommended via Docker Compose):
   - `docker compose up -d mqtt`

If you prefer local Mosquitto instead of Docker:
- `mosquitto -v`

## Run
- `py Mainflow.py`

If MQTT broker is unavailable, the simulator still starts cleaning locally when you press `S`.

## MQTT Quick Check
- Show broker logs: `docker compose logs -f mqtt`
- Stop broker: `docker compose down`
- The app connects to `localhost:1883` by default.

## Assignment Alignment Summary
- Problem definition and user stories: prepared externally (as provided by the author).
- Class design: implemented with 10+ classes.
- State machine: implemented in code (`CleaningModule`) and integrated in runtime.
- Sequence/architecture behavior: reflected by simulation loop + MQTT command path.

## Notes
- The visual map uses tile encoding managed by `ModuleMap` constants.
- Charging station tile is used as the robot dock/home location.
