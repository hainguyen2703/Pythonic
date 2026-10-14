# Pacman vs Ghost Arena

An educational framework for teaching **AI search algorithms** through a competitive, synchronous two-agent game. Students implement a **Pacman** agent (seeker) and/or a **Ghost** agent (hider) as Python classes, then compete against each other on a classic Pacman-style maze.

## Overview

- **Pacman (Seeker)**: catches the Ghost by moving within the configured capture distance.
- **Ghost (Hider)**: evades Pacman for as long as possible (survives until `max_steps`).
- Both agents move **simultaneously** each step — neither sees the other's decision before moving.
- The framework supports full visibility or a configurable **fog of war** (limited observation radius), plus an optional **speed multiplier** for Pacman on straight paths.
- Agents are **stateful** in-process objects when run locally (`--no-sandbox`), or isolated subprocesses during instructor tournament runs (`--sandbox`).

---

## Game Rules & Mechanics

### Map

The game runs on a fixed 21×21 grid maze (`#` = wall, `.` = empty). Student agents receive the map as a 2D NumPy array of integers:

| Value | Meaning |
|-------|---------|
| `0` | Empty (can move here) |
| `1` | Wall (cannot move here) |
| `-1` | Unseen / fog of war (only when limited observation is enabled) |

Walls are always visible even under fog of war; non-visible empty cells are reported as `-1`.

### Movement

Agents return one of the `Move` enum values (`from environment import Move`):

```python
Move.UP      # (row - 1, col)
Move.DOWN    # (row + 1, col)
Move.LEFT    # (row, col - 1)
Move.RIGHT   # (row, col + 1)
Move.STAY    # stay in place
```

**Pacman multi-step movement**: when the arena is configured with `--pacman-speed > 1`, a Pacman agent may return a tuple `(Move, steps)` with `1 <= steps <= pacman_speed` to advance multiple tiles in one straight direction in a single turn. Ghost agents must always return a plain `Move`.

### Win Conditions

- **Pacman wins**: Manhattan distance between the two agents drops below `--capture-distance` (default: `2`).
- **Ghost wins**: `--max-steps` is reached without capture (default: `200`).

### Synchronous (Simultaneous) Execution

At every step both agents receive the **same** state (`map_state`, their own position, and the enemy's position if visible), decide their moves independently, and then both moves are applied at once. This means agents cannot react instantly to an opponent's move — they must predict it.

### Fog of War (Limited Observation)

When `--pacman-obs-radius` / `--ghost-obs-radius` are set to a positive radius, each agent only sees a **cross-shaped** area around itself: rays extend up to `radius` tiles in the four cardinal directions and stop at walls. The enemy's position is passed as `None` when it is not within the visible cells.

---

## Repository Structure

```
pacman/
├── README.md              # This file
├── STUDENT_GUIDE.md       # Detailed student tutorial
├── requirements.txt       # Python dependencies (numpy)
├── run_game.sh            # Quick-start runner (uses conda 'ml' env if present)
├── src/                   # Core framework (instructor-owned)
│   ├── environment.py     # Game map, positions, movement, rules, observations
│   ├── agent_interface.py # Abstract base classes students must extend
│   ├── agent_loader.py    # In-process agent loading + move validation
│   ├── arena.py           # Game orchestrator + CLI
│   └── visualizer.py      # Terminal visualization (ANSI colors)
├── submissions/           # Student work (STUDENT EDITABLE)
│   ├── TEMPLATE_agent.py  # Starter template to copy
│   ├── example_student/   # Working baseline (greedy Pacman + evasive Ghost)
│   ├── simple_agent/      # Random-move test agent
│   ├── slow_agent/        # Sleeps 5 s per step (timeout test)
│   ├── broken_agent/      # Raises after 5 steps (error-logging test)
│   └── exit_test/         # Calls sys.exit() (sandbox EOF test)
└── instructors/           # Tournament / sandbox tooling (instructor-owned)
    ├── agent_loader.py    # Sandbox loader (AgentProxy over subprocess)
    ├── agent_runner.py    # Sandboxed subprocess agent runner
    ├── evaluate.py        # Round-robin tournament evaluator
    ├── INSTRUCTOR_NOTES.md
    ├── ERROR_LOGGING.md
    ├── Pacman-Runner.ipynb / Pacman-Runner Updated.ipynb
    └── legacy/            # Archived pre-merge reference files
```

---

## Setup & Installation

### Prerequisites

- Python 3.7+ (recommended 3.11)
- `numpy`

### Install

```bash
conda activate ml
pip install -r requirements.txt
```

`requirements.txt` contains: `numpy>=1.20.0`

### Verify

```bash
# From src/ (direct invocation)
cd src
python arena.py --seek example_student --hide example_student

# From pacman/ (shell wrapper; uses conda 'ml' if conda is available)
./run_game.sh example_student example_student
```

---

## Student Interface

Students create `submissions/<student_id>/agent.py` and define one or both classes:

```python
import sys
from pathlib import Path

src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from agent_interface import PacmanAgent as BasePacmanAgent
from agent_interface import GhostAgent as BaseGhostAgent
from environment import Move
import numpy as np


class PacmanAgent(BasePacmanAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pacman_speed = max(1, int(kwargs.get("pacman_speed", 1)))

    def step(self, map_state, my_position, enemy_position, step_number):
        # map_state:   2D numpy array, 0=empty, 1=wall, -1=unseen
        # my_position: (row, col)
        # enemy_position: (row, col) or None if hidden by fog of war
        # step_number:  starts at 1
        return Move.UP  # or (Move.UP, steps) for Pacman if pacman_speed > 1


class GhostAgent(BaseGhostAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def step(self, map_state, my_position, enemy_position, step_number):
        return Move.UP
```

Requirements:
- Class must be named **exactly** `PacmanAgent` or `GhostAgent` and inherit from the corresponding base class.
- `step()` must return a `Move` (Ghost), or a `Move` / `(Move, steps)` tuple (Pacman).
- Agents are stateful — data can persist across steps via `self`.
- `enemy_position` may be `None` when fog of war hides the enemy.

See `STUDENT_GUIDE.md` and `submissions/TEMPLATE_agent.py` for the full student instructions and helper functions.

---

## Running Games

### Basic Usage (`src/arena.py`)

```bash
cd src
python arena.py --seek <pacman_id> --hide <ghost_id> [options]
```

### Command-Line Options

| Argument | Default | Description |
|----------|---------|-------------|
| `--seek`, `--pacman` | required | Student ID for the Pacman (seeker) agent |
| `--hide`, `--ghost` | required | Student ID for the Ghost (hider) agent |
| `--submissions-dir` | `../submissions` | Directory containing student submissions |
| `--max-steps` | `200` | Maximum steps before Ghost wins by default |
| `--no-viz` | off | Disable terminal visualization |
| `--delay` | `0.1` | Delay (s) between visualized steps |
| `--step-timeout` | `1.0` | Max seconds per agent step (`<=0` disables) |
| `--start-mode` | `deterministic` | `deterministic` (classic P/G starts) or `stochastic` (random) |
| `--capture-distance` | `2` | Capture when Manhattan distance is below this value |
| `--pacman-speed` | `2` | Max tiles Pacman can advance in one straight direction |
| `--pacman-obs-radius` | `0` | Pacman observation radius (`0` = full visibility) |
| `--ghost-obs-radius` | `0` | Ghost observation radius (`0` = full visibility) |
| `--sandbox` | off | Run agents in sandboxed subprocesses (instructor evaluation) |

### Examples

```bash
# Standard game with visualization
python arena.py --seek alice --hide bob

# Fast testing (no visualization)
python arena.py --seek alice --hide bob --no-viz

# Slower debugging
python arena.py --seek alice --hide bob --delay 1.0

# Longer game / stochastic starts / different capture threshold
python arena.py --seek alice --hide bob --max-steps 300 --start-mode stochastic --capture-distance 3

# Pacman speed multiplier
python arena.py --seek alice --hide bob --pacman-speed 2

# Fog of war
python arena.py --seek alice --hide bob --pacman-obs-radius 5 --ghost-obs-radius 3
```

### Shell Wrapper (`run_game.sh`)

```bash
# From pacman/
./run_game.sh <seek_id> <hide_id> [arena options]
```

The script automatically uses `conda run -n ml python` when a conda installation is available, otherwise plain `python`.

---

## Tournament Evaluation (`instructors/evaluate.py`)

Runs a full round-robin tournament between all agents found in `submissions/` (each agent must be a subfolder containing `agent.py`). Games are launched as `run_game.sh <p> <g> --no-viz --sandbox ...` subprocesses and parallelized with a process pool.

```bash
cd pacman/instructors
python evaluate.py --num-threads 8 --output-csv results.csv --error-log error_audit.txt
```

### Options

| Argument | Default | Description |
|----------|---------|-------------|
| `--num-threads` | `4` | Parallel games to run |
| `--submissions-dir` | `submissions` | Submissions directory |
| `--output-csv` | `results.csv` | Detailed game results |
| `--max-steps` | `200` | Steps per game |
| `--step-timeout` | `1.0` | Seconds allowed per agent step |
| `--error-log` | `error_log.txt` | Audit log of all errors |
| `--start-mode` | `deterministic` | Start mode |
| `--capture-distance` | `2` | Capture distance threshold |
| `--pacman-speed` | `2` | Pacman speed multiplier |
| `--pacman-obs-radius` | `0` | Pacman observation radius |
| `--ghost-obs-radius` | `0` | Ghost observation radius |
| `--single` | off | Single-role mode (see below) |

**Single-role mode (`--single`)**: odd numeric IDs in agent folder names play only as Pacman (seeker); even numeric IDs play only as Ghost (hider). All pairs (Pacman × Ghost) are played. Agents whose names contain no digits are skipped.

**Outputs**:
- `results.csv` — one row per game (pacman, ghost, winner, role, total steps, error flag).
- `error_log.txt` — timestamped error records (EXECUTION_ERROR, AGENT_ERROR, AGENT_TIMEOUT, GAME_TIMEOUT, UNEXPECTED_ERROR, EXECUTOR_ERROR).
- Terminal summary: per-agent wins, games, and a `step_diff` tie-breaker (steps as Pacman minus steps as Ghost; lower is better).

---

## Sandboxed Subprocess Execution (`--sandbox`)

When run with `--sandbox`, each agent executes inside an isolated `agent_runner.py` subprocess instead of in-process. This prevents student code from monkey-patching instructor modules, polluting `sys.path`, or suppressing the SIGALRM step timeout.

Protocol (newline-delimited JSON on stdin/stdout):

```
Parent → Runner (observation):  {"map_state": [[...]], "my_position": [r,c],
                                 "enemy_position": [r,c]|null, "step_number": N}
Runner → Parent (ready):        "READY"
Runner → Parent (move):         {"move": "UP"}          # or {"move": "UP", "steps": 2}
Runner → Parent (error):        {"error": "Type: msg"}
```

Security properties (from `instructors/agent_runner.py`):
- Instructor modules are imported and cached in `sys.modules` before the student directory is added to `sys.path` (prevents module shadowing).
- `os.chdir(student_dir)` restricts relative path traversal to the student's own folder.
- The parent's SIGALRM fires during its blocking `readline()`, so student code cannot suppress it.
- Background student threads are killed when the subprocess is terminated by the parent's `atexit` handler.
- A student `sys.exit()`/`SystemExit` only kills the subprocess; the parent detects EOF and gives the opponent the win.

---

## Troubleshooting

| Error | Cause / Fix |
|-------|-------------|
| `Agent file not found for student <id>` | Folder name must match the ID passed to `--seek`/`--hide` exactly. |
| `agent.py ... must define a 'PacmanAgent' class` | Class must be named exactly `PacmanAgent` or `GhostAgent` and inherit from the matching base class. |
| `returned invalid move type` | Must return a `Move` enum (not a string, tuple of coordinates, or `None`). |
| `requested N steps which exceeds the maximum speed` | Pacman `(Move, steps)` must satisfy `1 <= steps <= --pacman-speed`. |
| Agent crashes with `IndexError` | Accessing map cells without validating bounds. Always check `0 <= r < h and 0 <= c < w`. |
| `TypeError` on distances | `enemy_position` became `None` (fog of war). Guard with `if enemy_position is not None:`. |
| Agent times out | Inefficient / non-terminating search. Use a visited set, limit depth, prefer `deque`/`heap`. |

---

## Teaching Notes

Suggested student algorithms:
- **Pacman**: BFS, A* (Manhattan heuristic), Greedy Best-First, path caching/replanning, predictive interception.
- **Ghost**: greedy max-distance movement, BFS to the furthest reachable tile, minimax/expectimax, alpha-beta pruning.

See `instructors/INSTRUCTOR_NOTES.md` for a week-by-week curriculum, grading criteria, and assignment ideas.

---

## License

Provided for educational purposes.
