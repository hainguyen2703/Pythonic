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
        self.previous_move = Move.STAY
    
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
        return self._move_decision_bfs(map_state, my_position, enemy_position)

    
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


    def _distance_bfs(self, map_state: np.ndarray, start, end):
        """
        Trả về khoảng cách tử start đến end position
        """
        if start == end:
            return 0

        queue = deque([(start, 0)])
        visited = {start}
        while queue:
            current_pos, distance = queue.popleft()
            for next_pos, _ in self._get_neighbors(current_pos, map_state):
                if next_pos in visited:
                    continue
                if next_pos == end:
                    return distance + 1
                visited.add(next_pos)
                queue.append((next_pos, distance + 1))

        # Không tìm thấy đường đi
        return float('inf')


    def _dfs(self, map_state: np.ndarray, start, depth: int, visited=None) -> bool:
        """
        Sử dụng DFS để kiểm tra xem từ start có lối thoát trong depth bước tiếp theo không.
        Trả về True nếu có lối thoát, False nếu dẫn tới dead end.
        visited: các ô đã đi qua trên đường hiện tại, tránh đi qua đi lại giữa 2 ô
        """
        if visited is None:
            visited = {start}
        if depth == 0:
            return True
        for next_pos, _ in self._get_neighbors(start, map_state):
            # Bỏ qua ô đã đi qua trên đường hiện tại
            if next_pos in visited:
                continue
            if self._dfs(map_state, next_pos, depth - 1, visited | {next_pos}):
                return True
        return False


    def _move_decision_bfs(self, map_state: np.ndarray,
                            my_position: tuple,
                            enemy_position: tuple) -> Move:
        # Tính khoảng cách với Pacman hiện tại
        current_dist = self._distance_bfs(map_state, my_position, enemy_position)  # Lưu khoảng cách hiện tại từ my_position đến enemy_position
        if current_dist == float('inf'):
            self.previous_move = Move.STAY
            return Move.STAY
        
        # Danh sách các hướng đi hợp lệ
        possible_move = []
        # Tính BFS distance đến Pacman nếu đi theo hướng hợp lệ
        for pos, move in self._get_neighbors(my_position, map_state):
            predict_dist = self._distance_bfs(map_state, pos, enemy_position)
            # Lọc các hướng đi tắng distance với Pacman hiện tại hoặc đảo hướng
            if predict_dist > current_dist:
                possible_move.append(move)
            
        # Chọn hướng đi tốt: ưu tiên rẽ nhánh -> di chuyển -> stay
        if not possible_move:
            self.previous_move = Move.STAY
            return Move.STAY
        # ưu tiên rẽ nhánh
        for move in possible_move:
            if move != self.previous_move and not self._is_backward_move(move):
                # Thử di chuyển sang vị trí move
                # Kiểm tra xem hướng đi này có dẫn tới dead end trong 6 bước tiếp theo không
                # Sử dụng DFS để kiểm tra trong 6 bước tiếp theo có lối thoát không
                # visited gồm cả my_position để DFS không quay lại ô hiện tại rồi coi đó là lối thoát
                next_pos = self._apply_move(my_position, move)
                if self._dfs(map_state, next_pos, 6, {my_position, next_pos}):
                    self.previous_move = move
                    return move

        # Không có rẽ nhánh thì đi thẳng hoặc lùi
        self.previous_move = possible_move[0]
        return possible_move[0]

    def _is_backward_move(self, move: Move) -> bool:
        """Kiểm tra hướng đi có phải là đi ngược về"""
        if move == Move.UP:
            return self.previous_move == Move.DOWN
        if move == Move.DOWN:
            return self.previous_move == Move.UP
        if move == Move.LEFT:
            return self.previous_move == Move.RIGHT
        if move == Move.RIGHT:
            return self.previous_move == Move.LEFT
        return False
