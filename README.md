# Survival Grounds

Survival Grounds is a fullscreen first-person survival prototype built with Python and Pygame-ce.

## Version

Current development version: **0.3.0**

This is a development release. The game is playable, but terrain, rendering, and enemy behavior are still being refined.

## Requirements

- Python 3.14 or compatible Python 3
- `pygame-ce`

Install the dependency with:

```powershell
python -m pip install pygame-ce
```

## Run

From the project folder, run:

```powershell
python ".\Survival Grounds.py"
```

You can also press **Run Python File** in VS Code while `Survival Grounds.py` is open. `game.py` also forwards direct execution to the Pygame engine.

## Controls

- Up / Down: select a menu option
- Enter: confirm
- W / A / S / D: move
- Mouse: look around
- Left mouse button: fire pistol
- Space: jump
- Shift: sprint at 1.5x speed
- Ctrl: activate machine-gun mode
- Escape: return to the start menu
- R: respawn after game over
- Delete: exit the game

## Game Modes

- Terrain B: the playable map with enemies
- Test Map: the same style of map without enemies
- Plains: currently available biome
- Desert and Mountains: marked as not available

## Current Gameplay

- 40x40 terrain grid
- Smoothed terrain with sloped tile surfaces
- Four grass color variations
- Enemy grunts and purple elite enemies
- Ranged purple enemy laser attacks
- Player health, scoring, jumping, sprinting, and machine-gun mode
- Pink/purple map boundary wall
- Pygame accelerated rendering with configurable render distance

## Project Files

- `Survival Grounds.py`: recommended launcher
- `pygame_game.py`: active Pygame game engine
- `game.py`: legacy Tkinter prototype and direct-run forwarder
- `terrain.py`: terrain generation
- `enemy.py`: enemy movement, health, and attack state
- `config.py`: gameplay and rendering settings
- `PATCH_NOTES.md`: development history
