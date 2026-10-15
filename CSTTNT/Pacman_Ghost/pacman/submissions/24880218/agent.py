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
        # Memory for limited observation mode
        self.last_known_enemy_pos = None
    
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
        
        # Update memory if enemy is visible
        #if enemy_position is not None:
        #    self.last_known_enemy_pos = enemy_position
        
        # Use current sighting, fallback to last known, or move randomly
        #threat = enemy_position or self.last_known_enemy_pos
        
        #if threat is None:
        #    # No information about enemy - move randomly
        #    for move in [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]:
        #        if self._is_valid_move(my_position, move, map_state):
        #            return move
        #    return Move.STAY
        
        # Example: Simple evasive approach (replace with your algorithm)
        #row_diff = my_position[0] - threat[0]
        #col_diff = my_position[1] - threat[1]
        
        # Try to move away from Pacman
        #if abs(row_diff) > abs(col_diff):
        #    move = Move.DOWN if row_diff > 0 else Move.UP
        #else:
        #    move = Move.RIGHT if col_diff > 0 else Move.LEFT
        
        return self._move_decision_bfs(map_state, my_position, enemy_position)
    
        # Check if move is valid
        #if self._is_valid_move(my_position, move, map_state):
        #    return move
        
        # If not valid, try other moves
        #for move in [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]:
        #    if self._is_valid_move(my_position, move, map_state):
        #        return move

        #return Move.STAY
    
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

    def _get_neighbors(self, map_state: np.ndarray, pos: tuple) -> list[tuple]:
        """Hàm trả về danh sách các ô kề hợp lệ có thể đi được"""
        # Lấy vị trí (r, c) của pos
        row, col = pos
        # Tạo list vị trí kề
        adjacents = [(row - 1, col), (row, col - 1), (row, col + 1), (row + 1, col)]        

        # Return list các ô kề hợp lệ (Không out khỏi maze và không đụng tường)
        return [position for position in adjacents if self._is_valid_position(position, map_state)] 

    def _distance_bfs(self, map_state: np.ndarray, start, end):
        """
        Trả về list chứa đường đi từ start đến end position
        """
        # YOUR CODE HERE
        queue = deque([start])  # Queue dùng cho BFS
        trace = {start: None}   # Dict dùng để truy vết ngược đường đi từ start -> end
        moves = [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]

        def get_path():
            """Hàm trả về path từ start đến end"""
            path = [end]
            while path[-1] != start:
                path.append(trace[path[-1]])
            return path[::-1]

        # Loop đến khi Queue empty
        while queue:
            # Lấy node đầu Queue - FIFO
            current_pos = queue.popleft()
            # Tìm các position hợp lệ xung quanh
            posible_moves = [move for move in moves if self._is_valid_move(current_pos, move, map_state)]

            # Duyệt qua các position kề xung quanh
            for next_pos in self._get_neighbors(map_state, current_pos):
                # Bỏ qua nếu đã xét ô này
                if next_pos in trace:
                    continue
                # Đánh dấu ô đã được xét
                trace[next_pos] = current_pos
                # Trả về path khi tìm thấy End
                if next_pos == end:
                    return get_path()
                # Thêm các ô đi được vào Queue
                queue.append(next_pos)

        # Không tìm thấy đường đi -> Trả về None
        return None

    def _move_decision_bfs(self, map_state: np.ndarray,
                            my_position: tuple,
                            enemy_position: tuple) -> Move:
        # Tính khoảng cách với Pacman hiện tại
        current_dist = len(self._distance_bfs(map_state, my_position, enemy_position))

        # Tính BFS distance với Pacman nếu đi theo hướng hợp lệ
        for move in [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]:
            delta_row, delta_col = move.value
            new_pos = (my_position[0] + delta_row, my_position[1] + delta_col)

            if self._is_valid_position(new_pos, map_state):
                # Chọn hướng đi nếu BFS distance tăng lên
                if len(self._distance_bfs(map_state, new_pos, enemy_position)) > current_dist:
                    return move
            
        return Move.STAY
