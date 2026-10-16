"""
Benchmark một GhostAgent trên map mặc định (speed 2, capture < 2, 200 bước).

Cách dùng (từ thư mục Pacman_Ghost):
    python3 Review/scripts/bench_ghost.py pacman/submissions/24880218/agent.py
    python3 Review/scripts/bench_ghost.py <agent.py> --kw level=3     # truyền kwargs cho GhostAgent

Đối thủ:
    greedy : PacmanAgent của submissions/example_student (tham lam theo Manhattan)
    bfs    : Pacman tìm đường ngắn nhất theo số LƯỢT (đi thẳng 1-2 ô mỗi lượt)

Seed 16 bị bỏ qua vì Ghost xuất phát trong ô kín (7,1) nên luôn thắng.
"""

import argparse
import importlib.util
import random
import sys
import time
from collections import deque
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2] / "pacman"
sys.path.insert(0, str(ROOT / "src"))
from environment import Environment, Move  # noqa: E402

DIRS = [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BfsPacman:
    """Đuổi theo đường ngắn nhất tính bằng số lượt, dừng khi tới ô cách Ghost Manhattan <= 1."""

    def __init__(self, speed=2):
        self.speed = speed

    def step(self, m, me, enemy, step_number):
        height, width = m.shape
        ok = lambda p: 0 <= p[0] < height and 0 <= p[1] < width and m[p] != 1
        prev = {me: None}
        queue = deque([me])
        while queue:
            cur = queue.popleft()
            if abs(cur[0] - enemy[0]) + abs(cur[1] - enemy[1]) <= 1:
                break
            for mv in DIRS:
                p = cur
                for k in range(1, self.speed + 1):
                    n = (p[0] + mv.value[0], p[1] + mv.value[1])
                    if not ok(n):
                        break
                    p = n
                    if p not in prev:
                        prev[p] = (cur, mv, k)
                        queue.append(p)
        target = min(prev, key=lambda p: abs(p[0] - enemy[0]) + abs(p[1] - enemy[1]))
        action = None
        while prev[target] is not None:
            cur, mv, k = prev[target]
            action = (mv, k)
            target = cur
        return action or (Move.STAY, 1)


def play(pacman, ghost, env, max_steps=200):
    env.reset()
    worst_step_time = 0.0
    for t in range(1, max_steps + 1):
        p_obs, p_pos, p_enemy = env.get_observation('pacman', 0, 0)
        g_obs, g_pos, g_enemy = env.get_observation('ghost', 0, 0)
        p_action = pacman.step(p_obs, p_pos, p_enemy, t)
        start = time.time()
        g_action = ghost.step(g_obs, g_pos, g_enemy, t)
        worst_step_time = max(worst_step_time, time.time() - start)
        over, result, _ = env.step(p_action, g_action)
        if over:
            return result, t, worst_step_time
    return 'ghost_wins', max_steps, worst_step_time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("agent", help="đường dẫn tới file agent.py chứa GhostAgent")
    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--kw", action="append", default=[], help="kwargs cho GhostAgent, dạng key=int")
    args = parser.parse_args()

    ghost_module = load_module(args.agent, "ghost_under_test")
    example = load_module(ROOT / "submissions" / "example_student" / "agent.py", "example_student")
    kwargs = {k: int(v) for k, v in (item.split("=") for item in args.kw)}
    opponents = {
        "greedy": lambda: example.PacmanAgent(pacman_speed=2),
        "bfs": lambda: BfsPacman(),
    }

    for name, make_pacman in opponents.items():
        random.seed(0)
        env = Environment(capture_distance_threshold=2, pacman_speed=2)
        _, det_steps, worst = play(make_pacman(), ghost_module.GhostAgent(**kwargs), env)

        wins, lengths = 0, []
        for seed in range(args.seeds):
            if seed == 16:
                continue
            random.seed(seed)
            np.random.seed(seed)
            env = Environment(capture_distance_threshold=2, pacman_speed=2, deterministic_starts=False)
            result, steps, step_time = play(make_pacman(), ghost_module.GhostAgent(**kwargs), env)
            wins += result == 'ghost_wins'
            lengths.append(steps)
            worst = max(worst, step_time)

        print(f"{name:6s} | xuất phát cố định: {det_steps:3d} bước | "
              f"ngẫu nhiên: thắng {wins}/{len(lengths)}, sống TB {sum(lengths) / len(lengths):.1f} bước | "
              f"bước chậm nhất {worst * 1000:.0f} ms")


if __name__ == "__main__":
    main()
