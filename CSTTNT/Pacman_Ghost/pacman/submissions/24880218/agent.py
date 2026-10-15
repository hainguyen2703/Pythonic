"""
Template for student agent implementation.

INSTRUCTIONS:
1. Copy this file to submissions/<your_student_id>/agent.py
2. Implement the PacmanAgent and/or GhostAgent classes
3. Replace the simple logic with your search algorithm
4. Test your agent using: python arena.py --seek <your_id> --hide example_student

IMPORTANT:
- Do NOT change the class names (PacmanAgent, GhostAgent)
- Do NOT change the method signatures (step, __init__)
- Pacman step must return either a Move or a (Move, steps) tuple where
    1 <= steps <= pacman_speed (provided via kwargs)
- Ghost step must return a Move enum value
- You CAN add your own helper methods
- You CAN import additional Python standard libraries
- Agents are STATEFUL - you can store memory across steps
- enemy_position may be None when limited observation is enabled
- map_state cells: 1=wall, 0=empty, -1=unseen (fog)
"""

import sys
from pathlib import Path

# Add src to path to import the interface
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from agent_interface import PacmanAgent as BasePacmanAgent
from agent_interface import GhostAgent as BaseGhostAgent
from environment import Move
import numpy as np
import time


class PacmanAgent(BasePacmanAgent):
    """
    Pacman (Seeker) Agent - Goal: Catch the Ghost
    
    Implement your search algorithm to find and catch the ghost.
    Suggested algorithms: BFS, DFS, A*, Greedy Best-First
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pacman_speed = max(1, int(kwargs.get("pacman_speed", 1)))
        # TODO: Initialize any data structures you need
        # Examples:
        # - self.path = []  # Store planned path
        # - self.visited = set()  # Track visited positions
        self.name = "Template Pacman"
        # Memory for limited observation mode
        self.last_known_enemy_pos = None
    
    def step(self, map_state: np.ndarray, 
             my_position: tuple, 
             enemy_position: tuple,
             step_number: int):
        """
        Decide the next move.
        
        Args:
            map_state: 2D numpy array where 1=wall, 0=empty, -1=unseen (fog)
            my_position: Your current (row, col) in absolute coordinates
            enemy_position: Ghost's (row, col) if visible, None otherwise
            step_number: Current step number (starts at 1)
            
        Returns:
            Move or (Move, steps): Direction to move (optionally with step count)
        """
        # TODO: Implement your search algorithm here
        
        # Update memory if enemy is visible
        if enemy_position is not None:
            self.last_known_enemy_pos = enemy_position
        
        # Use current sighting, fallback to last known, or explore
        target = enemy_position or self.last_known_enemy_pos
        
        if target is None:
            # No information about enemy - explore randomly
            for move in [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]:
                if self._is_valid_move(my_position, move, map_state):
                    return (move, 1)
            return (Move.STAY, 1)
        
        # Example: Simple greedy approach (replace with your algorithm)
        row_diff = target[0] - my_position[0]
        col_diff = target[1] - my_position[1]
        
        # Try to move towards ghost
        if abs(row_diff) > abs(col_diff):
            primary_move = Move.DOWN if row_diff > 0 else Move.UP
            desired_steps = abs(row_diff)
        else:
            primary_move = Move.RIGHT if col_diff > 0 else Move.LEFT
            desired_steps = abs(col_diff)

        action = self._choose_action(
            my_position,
            [primary_move],
            map_state,
            desired_steps
        )
        if action:
            return action

        # If the primary direction is blocked, try other moves
        fallback_moves = [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]
        action = self._choose_action(my_position, fallback_moves, map_state, self.pacman_speed)
        if action:
            return action
        
        return (Move.STAY, 1)
    
    # Helper methods (you can add more)
    
    def _choose_action(self, pos: tuple, moves, map_state: np.ndarray, desired_steps: int):
        for move in moves:
            max_steps = min(self.pacman_speed, max(1, desired_steps))
            steps = self._max_valid_steps(pos, move, map_state, max_steps)
            if steps > 0:
                return (move, steps)
        return None

    def _max_valid_steps(self, pos: tuple, move: Move, map_state: np.ndarray, max_steps: int) -> int:
        steps = 0
        current = pos
        for _ in range(max_steps):
            delta_row, delta_col = move.value
            next_pos = (current[0] + delta_row, current[1] + delta_col)
            if not self._is_valid_position(next_pos, map_state):
                break
            steps += 1
            current = next_pos
        return steps
    
    def _is_valid_move(self, pos: tuple, move: Move, map_state: np.ndarray) -> bool:
        """Check if a move from pos is valid for at least one step."""
        return self._max_valid_steps(pos, move, map_state, 1) == 1
    
    def _is_valid_position(self, pos: tuple, map_state: np.ndarray) -> bool:
        """Check if a position is valid (not a wall and within bounds)."""
        row, col = pos
        height, width = map_state.shape
        
        if row < 0 or row >= height or col < 0 or col >= width:
            return False
        
        return map_state[row, col] == 0


# ---------------------------------------------------------------------------
# Ghost
# ---------------------------------------------------------------------------

# Game rules assumed by the Ghost (taken from the assignment statement).
PACMAN_SPEED = 2        # Pacman moves up to 2 cells in a straight line per turn
CAPTURE_DISTANCE = 2    # Ghost is caught when Manhattan distance < 2
MAX_STEPS = 200         # Ghost wins after surviving this many steps
STEP_TIME_BUDGET = 0.7  # seconds of solving allowed per step (limit is 1s)

# Opponent modelling: trust a Pacman model once it predicted at least this
# share of Pacman's recent moves, then search this many rounds ahead with it.
MODEL_MIN_OBSERVATIONS = 3
MODEL_CONFIDENCE = 0.8
MODEL_DECAY = 0.9
LOOKAHEAD_DEPTH = 8

GHOST_MOVES = [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT, Move.STAY]
PACMAN_MODELS = ("chaser", "greedy_vertical", "greedy_major_axis")


class PursuitGame:
    """
    Fully solved minimax model of the chase on one map.

    A state is (ghost cell g, pacman cell p). Both agents move at the same
    time, so the Ghost plays the worst case: it assumes Pacman sees the
    Ghost's move and answers it optimally. value[g, p] is the number of
    rounds the Ghost is guaranteed to survive from (g, p), computed by
    backward induction (retrograde minimax over every state):

        outcome[g', p'] = 0 if captured(g', p') else 1 + value[g', p']
        value[g, p]     = max over ghost move g'  of
                          min over pacman move p' of outcome[g', p']

    Each round is evaluated for all ~46k states at once with numpy, so the
    whole 200-round game tree is solved in well under a second.
    """

    def __init__(self, open_mask: np.ndarray, pacman_speed: int,
                 capture_distance: int, horizon: int):
        self.cells = [tuple(int(v) for v in rc) for rc in np.argwhere(open_mask)]
        self.index = {cell: i for i, cell in enumerate(self.cells)}
        self.horizon = horizon
        n = len(self.cells)

        # Successor tables: next_cell[action, cell] -> cell index.
        self.ghost_next = np.array([
            [self._slide(cell, move, 1, open_mask) for cell in self.cells]
            for move in GHOST_MOVES
        ])
        self.pacman_speed = pacman_speed
        self.pacman_actions = [(Move.STAY, 1)] + [
            (move, steps) for move in GHOST_MOVES[:4]
            for steps in range(1, pacman_speed + 1)
        ]
        self.pacman_next = np.array([
            [self._slide(cell, move, steps, open_mask) for cell in self.cells]
            for move, steps in self.pacman_actions
        ])

        coords = np.array(self.cells)
        manhattan = (np.abs(coords[:, None, 0] - coords[None, :, 0]) +
                     np.abs(coords[:, None, 1] - coords[None, :, 1]))
        self.captured = manhattan < capture_distance   # [g, p]

        # Tie-break helpers: ghost_dist[t, s] = ghost steps from s to t,
        # capture_dist[g, p] = Pacman turns from p to catch a Ghost at g.
        self.ghost_dist = self._distances(self.ghost_next, np.eye(n, dtype=bool))
        self.capture_dist = self._distances(self.pacman_next, self.captured)

        self.value = np.zeros((n, n), dtype=np.int16)
        self.outcome = self._outcome()
        self.solved_rounds = 0
        self.converged = False

    def _slide(self, cell, move, steps, open_mask):
        """Index of the cell reached by moving `steps` cells, stopping at walls."""
        height, width = open_mask.shape
        row, col = cell
        delta_row, delta_col = move.value
        for _ in range(steps):
            next_row, next_col = row + delta_row, col + delta_col
            if not (0 <= next_row < height and 0 <= next_col < width):
                break
            if not open_mask[next_row, next_col]:
                break
            row, col = next_row, next_col
        return self.index[(row, col)]

    @staticmethod
    def _distances(successors: np.ndarray, reached: np.ndarray) -> np.ndarray:
        """
        dist[t, s] = fewest actions for a mover at s to reach a cell where
        reached[t, s'] holds (BFS for all pairs at once, layer by layer).
        """
        unreachable = 10 ** 4
        dist = np.where(reached, 0, unreachable).astype(np.int32)
        while True:
            best_next = dist[:, successors[0]]
            for nxt in successors[1:]:
                best_next = np.minimum(best_next, dist[:, nxt])
            new_dist = np.minimum(dist, best_next + 1)
            if np.array_equal(new_dist, dist):
                return dist
            dist = new_dist

    def _outcome(self) -> np.ndarray:
        return np.where(self.captured, 0, self.value + 1).astype(np.int16)

    def solve(self, deadline: float):
        """Run backward-induction rounds until solved or out of time."""
        while (not self.converged and self.solved_rounds < self.horizon
               and time.perf_counter() < deadline):
            outcome = self.outcome
            # Pacman's best reply to each ghost cell: min over pacman moves.
            reply = outcome[:, self.pacman_next[0]]
            for nxt in self.pacman_next[1:]:
                reply = np.minimum(reply, outcome[:, nxt])
            # Ghost's best move: max over ghost moves.
            new_value = reply[self.ghost_next[0]]
            for nxt in self.ghost_next[1:]:
                new_value = np.maximum(new_value, reply[nxt])

            self.converged = np.array_equal(new_value, self.value)
            self.value = new_value
            self.outcome = self._outcome()
            self.solved_rounds += 1

    def predict(self, model: str, g: int, p: int) -> frozenset:
        """
        Pacman cells after one move of a typical Pacman strategy, given
        only the current state (Pacman cannot see the Ghost's move).
        Empty when the strategy has no clear choice.
        """
        replies = self.pacman_next[:, p]
        if model == "chaser":
            # BFS / A*: shortest path to the Ghost's current cell.
            turns = self.capture_dist[g, replies]
            return frozenset(replies[turns == turns.min()].tolist())

        row_diff = self.cells[g][0] - self.cells[p][0]
        col_diff = self.cells[g][1] - self.cells[p][1]
        vertical = (Move.DOWN if row_diff > 0 else Move.UP, abs(row_diff))
        horizontal = (Move.RIGHT if col_diff > 0 else Move.LEFT, abs(col_diff))
        if model == "greedy_vertical":
            preferences = [vertical, horizontal]
        else:   # greedy_major_axis: close the larger gap first
            preferences = sorted([vertical, horizontal], key=lambda m: -m[1])
        for move, gap in preferences:
            if gap == 0:
                continue
            steps = min(self.pacman_speed, gap)
            nxt = self.pacman_next[self.pacman_actions.index((move, steps)), p]
            if nxt != p:
                return frozenset([int(nxt)])
        return frozenset()

    def lookahead(self, g: int, p: int, model: str, depth: int,
                  rounds_left: int, deadline: float, memo: dict) -> int:
        """
        Rounds the Ghost survives when Pacman follows `model` for `depth`
        rounds; beyond that (or when out of time) fall back to the
        worst-case value.
        """
        if depth == 0 or rounds_left <= 0 or time.perf_counter() > deadline:
            return min(int(self.value[g, p]), max(rounds_left, 0))
        key = (g, p, depth)
        if key in memo:
            return memo[key]

        replies = self.predict(model, g, p) or self.pacman_next[:, p].tolist()
        best = 0
        for nxt in self.ghost_next:
            g2 = int(nxt[g])
            worst = min(0 if self.captured[g2, q] else
                        1 + self.lookahead(g2, q, model, depth - 1,
                                           rounds_left - 1, deadline, memo)
                        for q in replies)
            best = max(best, worst)
        memo[key] = best
        return best

    def best_move(self, ghost_pos: tuple, pacman_pos: tuple, rounds_left: int,
                  model: str = None, deadline: float = None) -> Move:
        """
        Pick the ghost move with the best guaranteed survival. Ties (common
        when every move is safe, or every move is lost against perfect play)
        are broken in favour of moves that beat more Pacman replies and keep
        a larger region the Ghost can reach before Pacman.

        When `model` is given, Pacman is predictable: survival against that
        model (searched LOOKAHEAD_DEPTH rounds ahead) is compared first, so
        the Ghost can exploit a weak Pacman instead of fearing a perfect one.
        """
        g = self.index[ghost_pos]
        p = self.index[pacman_pos]
        outcome = np.minimum(self.outcome, rounds_left)
        pacman_replies = self.pacman_next[:, p]
        capture_time = self.capture_dist[:, p]
        predicted = self.predict(model, g, p) if model else frozenset()
        memo = {}

        best_key, best_move = None, Move.STAY
        for move, nxt in zip(GHOST_MOVES, self.ghost_next):
            g2 = int(nxt[g])
            if g2 == g and move != Move.STAY:
                continue   # blocked by a wall
            results = outcome[g2, pacman_replies]
            safe_area = np.count_nonzero(self.ghost_dist[g2] < capture_time - 1)
            key = (int(results.min()),          # guaranteed survival
                   float(results.mean()),       # survival vs. a random reply
                   int(safe_area),              # room left to run
                   int(capture_time[g2]))       # distance from Pacman
            if predicted:
                vs_model = min(0 if self.captured[g2, q] else
                               1 + self.lookahead(g2, q, model, LOOKAHEAD_DEPTH - 1,
                                                  rounds_left - 1, deadline, memo)
                               for q in predicted)
                key = (vs_model,) + key
            if best_key is None or key > best_key:
                best_key, best_move = key, move
        return best_move


class GhostAgent(BaseGhostAgent):
    """
    Ghost (Hider) Agent - Goal: Avoid being caught

    Solves the whole pursuit game by retrograde minimax (see PursuitGame)
    on the first step, then plays the move with the longest guaranteed
    survival against an optimal, faster Pacman. Meanwhile it checks which
    typical Pacman strategy (BFS chaser, greedy) explains Pacman's moves;
    once one does, it searches ahead against that strategy to exploit it.
    """

    # Solved games shared between games on the same map.
    _games = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "Retrograde Minimax Ghost"
        self.game = None
        # Opponent modelling: decayed counts of predictions made / correct.
        self.model_hits = {model: 0.0 for model in PACMAN_MODELS}
        self.model_tries = {model: 0.0 for model in PACMAN_MODELS}
        self.model_samples = {model: 0 for model in PACMAN_MODELS}
        self.previous_state = None
        # Memory for limited observation mode
        self.last_known_enemy_pos = None

    def step(self, map_state: np.ndarray,
             my_position: tuple,
             enemy_position: tuple,
             step_number: int) -> Move:
        """
        Decide the next move.

        Args:
            map_state: 2D numpy array where 1=wall, 0=empty, -1=unseen (fog)
            my_position: Your current (row, col) in absolute coordinates
            enemy_position: Pacman's (row, col) if visible, None otherwise
            step_number: Current step number (starts at 1)

        Returns:
            Move: One of Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT, Move.STAY
        """
        deadline = time.perf_counter() + STEP_TIME_BUDGET

        if enemy_position is not None:
            self.last_known_enemy_pos = enemy_position
        threat = enemy_position or self.last_known_enemy_pos

        if self.game is None:
            self.game = self._load_game(map_state)
        # Finishes on the first step; keeps solving later if time ran out.
        self.game.solve(deadline)

        if threat is None:
            self.previous_state = None
            return self._fallback_move(my_position, map_state)

        g = self.game.index[tuple(my_position)]
        p = self.game.index[tuple(threat)]
        if enemy_position is not None:
            self._observe_pacman(p)
            self.previous_state = (g, p)
        else:
            self.previous_state = None

        if step_number <= MAX_STEPS:
            rounds_left = MAX_STEPS - step_number + 1
        else:
            rounds_left = self.game.horizon
        return self.game.best_move(tuple(my_position), tuple(threat), rounds_left,
                                   self._trusted_model(), deadline)

    def _observe_pacman(self, p: int):
        """Score every Pacman model on the move Pacman just made."""
        if self.previous_state is None:
            return
        for model in PACMAN_MODELS:
            predicted = self.game.predict(model, *self.previous_state)
            if not predicted:
                continue   # the model has no opinion here (e.g. random fallback)
            self.model_samples[model] += 1
            self.model_tries[model] = self.model_tries[model] * MODEL_DECAY + 1
            self.model_hits[model] = (self.model_hits[model] * MODEL_DECAY +
                                      (p in predicted))

    def _trusted_model(self):
        """The most accurate Pacman model on recent moves, if accurate enough."""
        best_model, best_accuracy = None, MODEL_CONFIDENCE
        for model in PACMAN_MODELS:
            if self.model_samples[model] < MODEL_MIN_OBSERVATIONS:
                continue
            accuracy = self.model_hits[model] / self.model_tries[model]
            if accuracy >= best_accuracy:
                best_model, best_accuracy = model, accuracy
        return best_model

    def _load_game(self, map_state: np.ndarray) -> PursuitGame:
        # Walls are always visible, so fog (-1) cells are still open cells.
        open_mask = map_state != 1
        key = (open_mask.shape, open_mask.tobytes())
        if key not in GhostAgent._games:
            GhostAgent._games[key] = PursuitGame(
                open_mask, PACMAN_SPEED, CAPTURE_DISTANCE, MAX_STEPS)
        return GhostAgent._games[key]

    def _fallback_move(self, pos: tuple, map_state: np.ndarray) -> Move:
        """Pacman unknown: move to the neighbour with the most exits."""
        best_move, best_exits = Move.STAY, -1
        for move in GHOST_MOVES[:4]:
            if not self._is_valid_move(pos, move, map_state):
                continue
            next_pos = (pos[0] + move.value[0], pos[1] + move.value[1])
            exits = sum(self._is_valid_move(next_pos, m, map_state) for m in GHOST_MOVES[:4])
            if exits > best_exits:
                best_move, best_exits = move, exits
        return best_move

    # Helper methods (you can add more)

    def _is_valid_move(self, pos: tuple, move: Move, map_state: np.ndarray) -> bool:
        """Check if a move from pos is valid."""
        delta_row, delta_col = move.value                   # Lấy hướng muốn đi (Up, down, left, right, stay)
        new_pos = (pos[0] + delta_row, pos[1] + delta_col)  # Tính vị trí sau khi di chuyển (Up, down, left, right)
        return self._is_valid_position(new_pos, map_state)  # Trả về True nếu hướng này có thể đi, ngược lại trả về False

    def _is_valid_position(self, pos: tuple, map_state: np.ndarray) -> bool:
        """Check if a position is valid (not a wall and within bounds)."""
        row, col = pos                   # Lấy dòng, cột của vị trí đang xét
        height, width = map_state.shape  # Lấy kích thước maze

        if row < 0 or row >= height or col < 0 or col >= width:
            return False  # Trả về False nếu vị trí đang xét out khỏi maze

        return map_state[row, col] != 1  # Trả về True nếu vị trí là path, False nếu vị trí là tường
