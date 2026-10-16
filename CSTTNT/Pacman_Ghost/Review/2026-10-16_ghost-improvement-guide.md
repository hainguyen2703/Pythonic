# Hướng dẫn cải thiện GhostAgent từng bước — 2026-10-16

Tiếp nối [review GhostAgent](2026-10-16_ghost-agent-review.md). Mỗi bước dưới đây đều đã được code thử và đo bằng [scripts/bench_ghost.py](scripts/bench_ghost.py). Kết quả ghi trong tài liệu là số đo thật, không phải ước đoán.

Phạm vi: chỉ chế độ **nhìn thấy toàn bộ map**. Chế độ sương mù (fog of war) không nằm trong yêu cầu đề bài nên không được xét.

## Kết quả tổng hợp

Điều kiện đo: map mặc định, speed 2, bị bắt khi Manhattan ≤ 1, 200 bước. Có 29 vị trí xuất phát ngẫu nhiên; seed 16 bị bỏ vì Ghost xuất phát trong ô kín nên luôn thắng.

| Phiên bản | Pacman tham lam: thắng /29 | Pacman tham lam: xuất phát cố định | Pacman BFS: sống TB | Pacman BFS: xuất phát cố định | Lượt chậm nhất |
|---|---|---|---|---|---|
| Gốc (`agent.py` hiện tại) | 20 | thắng | 21,7 | 11 | 2 ms |
| + Bước 1: thước đo theo lượt | 19 | thắng | 21,9 | 11 | 3 ms |
| + Bước 2: vùng an toàn (1 lượt) | **14** ↓ | thua ở bước 21 | 22,9 | 8 | 2 ms |
| + Bước 3: nhìn trước 2 lượt | **24** | thắng | **24,5** | 10 | ~80 ms |
| Trần lý thuyết (bảng tối ưu, bước 4) | 27 | thắng | 25,3 | 11 | — |

Cách đọc bảng:
- **Pacman BFS gần như hoàn hảo**, nên không Ghost nào thắng được nó trên map này (xem review). Với đối thủ này, thước đo đúng là **số bước sống sót**. Bước 3 đạt 24,5, đã sát trần 25,3.
- **Bước 1 không làm điểm tăng**, nhưng là nền móng bắt buộc cho bước 2–3.
- **Bước 2 đứng riêng thì làm tệ đi.** Đây là bài học quan trọng, giải thích ở dưới. Đừng dừng ở bước 2.

## Bước 0 — Đo trước khi sửa

Từ thư mục `Pacman_Ghost`:

```bash
python3 Review/scripts/bench_ghost.py pacman/submissions/24880218/agent.py
```

Nên lưu một bản sao `agent.py` gốc (git đã có commit `3a7cba5`) để so sánh lại sau mỗi bước. Chạy lại lệnh trên sau mỗi bước sửa.

Nguyên tắc: **chỉ giữ thay đổi nào làm số liệu tốt lên**, hoặc là nền móng cho bước sau.

## Bước 1 — Đo khoảng cách bằng số LƯỢT của Pacman

**Vì sao:** 10 ô thẳng thì Pacman chỉ mất 5 lượt, nhưng 10 ô zigzag mất 10 lượt. BFS theo số ô coi hai đường này như nhau. Xem điểm yếu 2 trong review.

**Chuẩn bị — biết tốc độ Pacman.** Arena chỉ truyền `pacman_speed` cho Pacman, không truyền cho Ghost. Vì vậy Ghost giả định tốc độ là 2, rồi tự cập nhật theo bước nhảy xa nhất từng thấy:

```python
# trong __init__
self.pacman_speed = 2          # Ghost không được báo, tự suy ra
self.last_enemy = None

def _update_speed(self, enemy_position):
    if self.last_enemy is not None:
        jump = (abs(enemy_position[0] - self.last_enemy[0])
                + abs(enemy_position[1] - self.last_enemy[1]))
        self.pacman_speed = max(self.pacman_speed, jump)
    self.last_enemy = enemy_position
```

Gọi `self._update_speed(enemy_position)` ở đầu hàm `step`.

Hàm này **thay thế** `_distance_bfs`. Chỉ cần chạy **1 BFS từ Pacman** cho mọi ô, thay vì 5 BFS mỗi lượt như hiện tại:

```python
def _pacman_time(self, map_state, start):
    """Số lượt Pacman cần để tới mỗi ô (mỗi lượt đi thẳng 1..speed ô)"""
    time = {start: 0}
    queue = deque([start])
    while queue:
        cur = queue.popleft()
        for move in [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]:
            pos = cur
            for _ in range(self.pacman_speed):
                nxt = (pos[0] + move.value[0], pos[1] + move.value[1])
                if not self._is_valid_position(nxt, map_state):
                    break
                pos = nxt
                if pos not in time:
                    time[pos] = time[cur] + 1
                    queue.append(pos)
    return time
```

Luật bắt là Manhattan ≤ 1, nên điều đáng sợ không phải "Pacman tới ô x" mà là "Pacman tới **sát** ô x". Hàm sau tính lượt sớm nhất điều đó xảy ra:

```python
INF = 10**9

def _danger_time(self, map_state, pacman_time):
    """Lượt sớm nhất Pacman đứng cách ô đó Manhattan <= 1 (đủ để bắt)"""
    danger = {}
    for cell, t in pacman_time.items():
        for x in [cell] + [n for n, _ in self._get_neighbors(cell, map_state)]:
            if t < danger.get(x, INF):
                danger[x] = t
    return danger
```

**Kiểm tra nhanh:** Pacman ở (9,1) trên hàng 9 thẳng thì `_pacman_time(...)[(9,9)]` phải bằng 4 (8 ô / 2), còn BFS thường cho 8.

**Kết quả:** đứng riêng thì không đổi (21,9 so với 21,7). Đây là nguyên liệu cho bước 2–3.

## Bước 2 — Vùng an toàn (Voronoi)

**Ý tưởng:** ô x **an toàn** nếu Ghost tới được x trước khi Pacman đe dọa x. Đếm số ô an toàn Ghost còn tới được; càng nhiều càng tốt. Cách đếm này tự động phạt ngõ cụt (bên trong có ít ô) và các nhánh mà Pacman chặn được đầu. Vì vậy nó **thay thế** hoàn toàn `_dfs` 6 bước.

```python
def _safe_region(self, map_state, start, danger):
    """Số ô Ghost (đứng ở start sau 1 lượt) tới được TRƯỚC khi Pacman đe dọa ô đó"""
    if danger.get(start, INF) <= 1:
        return 0
    arrive = {start: 1}
    queue = deque([start])
    while queue:
        cur = queue.popleft()
        for nxt, _ in self._get_neighbors(cur, map_state):
            t = arrive[cur] + 1
            if nxt not in arrive and t < danger.get(nxt, INF):
                arrive[nxt] = t
                queue.append(nxt)
    return len(arrive)
```

Để phá hòa cần thêm một BFS thường (số ô) từ Pacman tới mọi ô:

```python
def _bfs_all(self, map_state, start):
    """Khoảng cách (số ô) từ start tới mọi ô"""
    dist = {start: 0}
    queue = deque([start])
    while queue:
        cur = queue.popleft()
        for nxt, _ in self._get_neighbors(cur, map_state):
            if nxt not in dist:
                dist[nxt] = dist[cur] + 1
                queue.append(nxt)
    return dist
```

Chọn nước đi: so các nước theo bộ điểm `(vùng an toàn, danger, khoảng cách BFS)`, ưu tiên phần tử đầu, hòa thì xét phần tử sau. Có tính cả STAY, nhưng khi hòa điểm thì ưu tiên di chuyển.

```python
ptime = self._pacman_time(map_state, target)
danger = self._danger_time(map_state, ptime)
dist = self._bfs_all(map_state, target)     # BFS thường từ Pacman, để phá hòa
score = lambda c: (self._safe_region(map_state, c, danger), danger.get(c, INF), dist.get(c, INF))
options = [(my_position, Move.STAY)] + self._get_neighbors(my_position, map_state)
move = max(options, key=lambda o: (score(o[0]), o[1] != Move.STAY))[1]
```

**⚠️ Kết quả: tệ hơn** (14/29 so với 20/29 trước Pacman tham lam; xuất phát cố định thì thua ở bước 21).

Trace ván thua (xuất phát cố định, bước 17–21): Ghost ở (3,5) thấy vùng an toàn phía trên rộng nên chạy UP→UP lên hàng 1, rồi chạy LEFT dọc hàng 1. Hàng 1 là hành lang thẳng; Pacman vào cùng hàng phía sau và rút ngắn 2 ô mỗi lượt:

```
#..G.P....#     ← bước 20; bước 21 Pacman nhảy 2 ô → bắt
#.###.###.#
```

Nguyên nhân: điểm số chỉ chụp **một khoảnh khắc**. Nó không thấy vùng an toàn sẽ co lại thế nào sau khi Pacman đi. **Bài học:** hàm đánh giá tốt đến đâu cũng cần đi kèm **tìm kiếm nhìn trước**.

## Bước 3 — Nhìn trước 2 lượt, hai bên đi cùng lúc

**Ý tưởng:** đây là Minimax trong `Note.txt`, nhưng sửa 3 chỗ:
1. Pacman có tới 9 nước: 4 hướng × 1–2 ô, cộng STAY. Bắt được khi Manhattan ≤ 1 **sau khi cả hai cùng đi**.
2. Giả định bi quan: Pacman nhìn thấy nước của Ghost rồi mới đáp trả. Trên lưới này, giả định đó chỉ làm Ghost mất tối đa 1 bước so với luật thật.
3. Bị bắt cho điểm `-1000 - depth`, không phải −∞, để **thua muộn vẫn tốt hơn thua sớm**. Ở lá thì dùng vùng an toàn của bước 2.

```python
def _pacman_moves(self, map_state, pos):
    """Mọi ô Pacman có thể đứng sau 1 lượt"""
    result = {pos}
    for move in [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]:
        cur = pos
        for _ in range(self.pacman_speed):
            nxt = (cur[0] + move.value[0], cur[1] + move.value[1])
            if not self._is_valid_position(nxt, map_state):
                break
            cur = nxt
            result.add(cur)
    return result

def _caught(self, g, p):
    return abs(g[0] - p[0]) + abs(g[1] - p[1]) <= 1

def _leaf_value(self, map_state, g, p):
    if p not in self._danger_cache:      # nhiều lá có chung vị trí Pacman → cache lại
        self._danger_cache[p] = self._danger_time(map_state, self._pacman_time(map_state, p))
    danger = self._danger_cache[p]
    return self._safe_region(map_state, g, danger) + 0.01 * danger.get(g, 0)

def _ghost_value(self, map_state, g, p, depth):
    """Ghost chọn max, Pacman trả lời min"""
    best = -INF
    for g2 in [g] + [n for n, _ in self._get_neighbors(g, map_state)]:
        worst = INF
        for p2 in self._pacman_moves(map_state, p):
            if self._caught(g2, p2):
                value = -1000 - depth             # bị bắt càng muộn càng tốt
            elif depth == 1:
                value = self._leaf_value(map_state, g2, p2)
            else:
                value = self._ghost_value(map_state, g2, p2, depth - 1)
            worst = min(worst, value)
            if worst <= best:                     # cắt tỉa: nhánh này không thể tốt hơn
                break
        best = max(best, worst)
    return best

def _lookahead_move(self, map_state, my_position, target):
    self._danger_cache = {}
    options = [(my_position, Move.STAY)] + self._get_neighbors(my_position, map_state)
    best_move, best_value = Move.STAY, -INF
    for g2, move in options:
        worst = INF
        for p2 in self._pacman_moves(map_state, target):
            if self._caught(g2, p2):
                value = -1000 - self.search_depth
            elif self.search_depth == 1:
                value = self._leaf_value(map_state, g2, p2)
            else:
                value = self._ghost_value(map_state, g2, p2, self.search_depth - 1)
            worst = min(worst, value)
        if (worst, move != Move.STAY) > (best_value, best_move != Move.STAY):
            best_move, best_value = move, worst
    return best_move
```

Trong `__init__` thêm `self.search_depth = 2`. Hàm `step` cuối cùng:

```python
def step(self, map_state, my_position, enemy_position, step_number):
    self._update_speed(enemy_position)
    move = self._lookahead_move(map_state, my_position, enemy_position)
    self.previous_move = move
    return move
```

Sau bước này có thể xóa `_move_decision_bfs`, `_distance_bfs`, `_dfs` và `_is_backward_move`.

**Kết quả:** thắng 24/29 trước Pacman tham lam (gốc: 20) và sống trung bình 24,5 bước trước Pacman BFS (gốc: 21,7; trần: 25,3). Mỗi lượt mất khoảng 30–80 ms.

**Về độ sâu:**
- Độ sâu 3 tốn tới **0,71 giây** một lượt, quá sát giới hạn 1 giây của arena. Máy chấm có thể chậm hơn.
- Nếu muốn sâu hơn, dùng **iterative deepening**: chạy độ sâu 1, rồi 2, rồi 3…; mỗi vòng kiểm tra `time.time()` và dừng khi đã dùng khoảng 0,5 giây, giữ kết quả của độ sâu cuối cùng chạy xong.

## Bước 4 (tùy chọn) — Giải bảng trước

- Có thể tính `D[g][p]` = số bước sống sót tối ưu cho mọi cặp vị trí (khoảng 40 nghìn trạng thái) bằng phân tích ngược. Mỗi lượt, Ghost chọn nước có `D` lớn nhất.
- Đây chính là "trần" trong bảng tổng hợp: 27/29 và 25,3 bước. So với bước 3, chỉ hơn thêm khoảng 3 ván trước Pacman tham lam.
- **Khó khăn:** bản Python thuần mất khoảng 3 giây, vượt giới hạn 1 giây/lượt. Cần vector hóa bằng numpy, hoặc chia việc tính ra nhiều lượt và dùng bước 3 trong lúc bảng chưa xong. [agent_ai.py](../pacman/submissions/24880218/agent_ai.py) đã có khung `PursuitGame.solve(deadline)` theo hướng này.

## Bước 5 (tùy chọn, chưa kiểm chứng) — Mô hình hóa đối thủ

Vì Pacman hoàn hảo luôn thắng, cách duy nhất để vượt trần là **khai thác lỗi của đối thủ cụ thể**:

1. Mỗi lượt, cho vài mô hình Pacman (tham lam Manhattan, BFS theo lượt, …) dự đoán nước đi. Ghi lại mô hình nào đoán đúng nước Pacman thật vừa đi.
2. Khi một mô hình đoán đúng ổn định (ví dụ trên 90% trong 10 lượt gần nhất), thay nước "Pacman tệ nhất" trong bước 3 bằng nước mô hình đó dự đoán. Như vậy Ghost tìm được chỗ mà Pacman đó bị kẹt, ví dụ Pacman tham lam đi qua đi lại sau tường.
3. Khi chưa chắc thì quay về bước 3 bi quan.

Phần này chưa được code thử, nên chưa có số liệu.

## Lưu ý khi đưa vào `agent.py`

- Các đoạn code ở trên được trích từ một bản Ghost đầy đủ đã chạy benchmark. Bản đó có thêm tham số `level` để chuyển giữa các bước khi đo; khi nộp bài chỉ giữ bước 3.
- Benchmark chỉ dùng map mặc định và 2 đối thủ. Pacman của người chấm có thể khác; nếu thầy cô chấm trên map khác, nên tự tạo thêm map để thử.
- Kiểm tra lại giới hạn thời gian (cột "bước chậm nhất" của benchmark) sau mỗi lần thay đổi.
