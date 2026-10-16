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

import random
import sys
from pathlib import Path

from sklearn import neighbors

# Add src to path to import the interface
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from agent_interface import PacmanAgent as BasePacmanAgent
from agent_interface import GhostAgent as BaseGhostAgent
from environment import Move
import numpy as np
from collections import deque


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


class GhostAgent(BaseGhostAgent):
    """
    Ghost (Hider) Agent - Goal: Avoid being caught
    
    Implement your search algorithm to evade Pacman as long as possible.
    Suggested algorithms: BFS (find furthest point), Minimax, Monte Carlo
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # TODO: Initialize any data structures you need
    
    def step(self, map_state: np.ndarray,   # [] 2 chiều, chứa các giá trị 0, 1. O là ok, 1 là tường
             my_position: tuple,            # (row, col)
             enemy_position: tuple,         # (row, col)
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
        # TODO: Implement your search algorithm here
        # Vẽ map của pacman
        pacman_time_map = self._pacman_move_time(map_state, enemy_position)
        current_pacman_time = pacman_time_map.get(my_position, float('inf'))

        # Tìm pacman time tốt nhất quanh vị trí hiện tại
        neighbors = self._get_neighbors(my_position, map_state)
        best_time = max(pacman_time_map.get(pos, float('inf')) for pos, _ in neighbors)
        if best_time < current_pacman_time:  # đang ở vị trí tốt: đứng yên thường là tối ưu
            return Move.STAY
        # Chọn move tăng pacman time
        best_moves = [(pos, move) for pos, move in neighbors 
                      if pacman_time_map.get(pos, float('inf')) == best_time]
        # Kiểm tra ngõ cụt
        best_moves_copy = best_moves.copy()
        for pos, move in best_moves_copy:
            # Xoá nếu vị trí dẫn đến ngõ cụt
            if self._is_dead_end(pos, move, map_state):
                best_moves.remove((pos, move))

        if len(best_moves) == 0:
            return Move.STAY
        return random.choice([move for _, move in best_moves])

    
    # Helper methods (you can add more)
    
    def _is_valid_move(self, pos: tuple, move: Move, map_state: np.ndarray) -> bool:
        """Check if a move from pos is valid."""
        delta_row, delta_col = move.value
        new_pos = (pos[0] + delta_row, pos[1] + delta_col)
        return self._is_valid_position(new_pos, map_state)
    
    def _is_valid_position(self, pos: tuple, map_state: np.ndarray) -> bool:
        """Check if a position is valid (not a wall and within bounds)."""
        row, col = pos
        height, width = map_state.shape
        
        if row < 0 or row >= height or col < 0 or col >= width:
            return False
        
        return map_state[row, col] == 0


    def _apply_move(self, pos, move) -> tuple:
        """Apply a move to a position, return new position."""
        delta_row, delta_col = move.value
        return (pos[0] + delta_row, pos[1] + delta_col)


    def _get_neighbors(self, pos, map_state) -> list[tuple[tuple, Move]]:
        """Get all valid neighboring positions and their moves."""
        neighbors = []

        # Duyệt qua 4 hướng di chuyển từ vị trí hiện tại (pos)
        for move in [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]:
            next_pos = self._apply_move(pos, move)  # Đổi move thành vị trí kế tiếp
            if self._is_valid_position(next_pos, map_state):
                neighbors.append((next_pos, move))
        # Trả về danh sách các ô kề hợp lệ cùng với move tương ứng
        return neighbors


    def _pacman_move_time(self, map_state, start) -> dict[tuple, int]:
        """Số lượt Pacman cần để tới mỗi ô trên map từ vị trí hiện tại"""
        time = {start: 0}
        # Sử dụng BFS để vẽ bản đồ thời gian di chuyển của Pacman
        queue = deque([start])
        while queue:
            cur = queue.popleft()
            for move in [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]:
                pos = cur
                # Pacman có thể đi tối đa 2 ô trên đường thẳng trong 1 lượt
                for _ in range(2):
                    nxt = (pos[0] + move.value[0], pos[1] + move.value[1])
                    if not self._is_valid_position(nxt, map_state):
                        break
                    pos = nxt
                    if pos not in time:
                        time[pos] = time[cur] + 1
                        queue.append(pos)
        return time

    def _is_dead_end(self, pos: tuple, move: Move, map_state: np.ndarray) -> bool:
        """Check if a position is a dead end (only one valid move)."""
        path = []
        # Kiểm tra hướng đang muốn đi
        if move == Move.LEFT:
            path = [(pos[0], c) for c in range(pos[1], 0, -1)]
        elif move == Move.RIGHT:
            path = [(pos[0], c) for c in range(pos[1], len(map_state[0]) - 1)]
        elif move == Move.UP:
            path = [(r, pos[1]) for r in range(pos[0], 0, -1)]
        elif move == Move.DOWN:
            path = [(r, pos[1]) for r in range(pos[0], len(map_state) - 1)]

        # Duyệt theo từng ô trong hướng đi, nếu không có ô nào có ô kề hợp lệ thì đây là dead end
        # Sô ô kề phải lớn hon 2 vì trong đó có 1 ô là vị trí cũ, 1 ô là đi tiếp
        for position in path:
            # Chỉ cần 1 ô có thể rẽ
            if len(self._get_neighbors(position, map_state)) > 2:
                return False
        return True
