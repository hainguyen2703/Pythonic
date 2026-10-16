# Review GhostAgent bản thử nghiệm "bản đồ thời gian Pacman" — 2026-10-16

- **File được review:** [pacman/submissions/24880218/agent.py](../pacman/submissions/24880218/agent.py), thay đổi chưa commit, đè lên `3a7cba5`. Gồm hàm `step` mới ([dòng 184-197](../pacman/submissions/24880218/agent.py#L184-L197)) và hàm `_pacman_move_time` ([dòng 238-256](../pacman/submissions/24880218/agent.py#L238-L256)).
- **Ý tưởng của tác giả:** tính số lượt Pacman cần để tới mọi ô, rồi cho Ghost đi về phía ô mà Pacman tốn nhiều thời gian nhất. Tác giả nghi ngờ cách này không nhận biết được ngõ cụt.
- **Cấu hình test:** map mặc định, speed 2, bị bắt khi Manhattan ≤ 1, 200 bước, nhìn thấy toàn bộ map. Đo bằng [scripts/bench_ghost.py](scripts/bench_ghost.py).

## Đánh giá chung

Hướng đi **đúng**: thời gian của Pacman là thước đo chuẩn hơn số ô BFS (xem điểm yếu 2 của [review trước](2026-10-16_ghost-agent-review.md)). `_pacman_move_time` cài đúng, và chỉ cần 1 BFS mỗi lượt thay vì 5 như bản cũ.

Vấn đề nằm ở **cách chọn nước đi**: điều kiện `>` (lớn hơn hẳn) và cách phá hòa. Lỗi này khiến Ghost gần như luôn đứng yên, và đúng là nó không nhận ra ngõ cụt.

## Kết quả đo

| Phiên bản | Pacman tham lam: thắng /29 | Pacman BFS: xuất phát cố định | Pacman BFS: sống TB | Bị bắt trong ngõ cụt (2.274 ván quanh hàng 9) |
|---|---|---|---|---|
| Bản cũ (BFS + DFS, `3a7cba5`) | 20 | 11 | 21,7 | — |
| **Bản thử nghiệm này** | 23 | **7** | **17,7** | **367** (sống TB 7,2) |
| + Sửa 1: lấy max, hòa thì vẫn đi | 22 | 11 | **22,9** | 12 (nhờ may về thứ tự hướng; đảo thứ tự → 936) |
| + Sửa 1 + Sửa 2: tránh ô ngõ cụt | 22 | 11 | **22,9** | **0** (sống TB 12,8) |

Ghi chú:
- 23/29 ván thắng Pacman tham lam **không phải là điểm mạnh**. Trong 29 ván, Ghost chỉ di chuyển tổng cộng 14 lần; nó thắng vì Pacman tham lam bị kẹt sau tường còn Ghost thì đứng yên.
- Bộ 2.274 ván: Ghost xuất phát ở các ô gần hai ngõ cụt hàng 9 (cột 5–8, 12–15, cùng các ô (8,5), (10,5), (8,15), (10,15)); Pacman xuất phát ở mọi ô còn lại cách Ghost ít nhất 4. Đối thủ là Pacman BFS.

## Các điểm yếu

### 1. Điều kiện `>` khiến Ghost đứng yên trên "cao nguyên" — [agent.py:193](../pacman/submissions/24880218/agent.py#L193) (nặng nhất)

Pacman đi 2 ô mỗi lượt, nên trên đường thẳng **từng cặp ô liền nhau có cùng thời gian**. Ví dụ, Pacman ở (9,13) thì thời gian tới các ô hàng 9 là:

```
cột:  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19
T  :  6  6  5  5  4  4  3  3  2  2  1  1  0  1  1  2  2  3  3
```

Khi Ghost đứng ở ô mà ô phía trước có **cùng** T, điều kiện `next > current` loại mất nước đi đó, nên Ghost STAY. Một lượt sau, Pacman tới gần thêm, T của mọi ô đều giảm, và lại hòa. Ghost bị "đóng băng".

- **Số liệu:** trước Pacman BFS có 480 lần STAY, tất cả đều do gặp ô kề có T bằng nhau, trong khi chỉ có 32 lần di chuyển (cộng cả 29 ván).
- **Ví dụ (xuất phát cố định):** Ghost ở (9,10). T hiện tại là 6, ô RIGHT cũng là 6, nên Ghost STAY suốt lượt 1–6. Đến lượt 7 nó mới chạy, nhưng đã muộn, bị bắt ở bước 7 (bản cũ sống tới bước 11):
  ```
  t2: G (9,10) T=6 kề={LEFT: 5, RIGHT: 6} -> STAY
  t3: G (9,10) T=5 kề={LEFT: 4, RIGHT: 5} -> STAY
  ...
  t7: G (9,10) T=1 kề={LEFT: 1, RIGHT: 2} -> RIGHT  → bị bắt
  ```

### 2. Phá hòa theo thứ tự hướng — [agent.py:190-194](../pacman/submissions/24880218/agent.py#L190-L194)

- Hai ô kề nhau có T chênh nhau **tối đa 1**. Vì vậy mọi nước thỏa `>` đều có đúng T+1, tức là luôn hòa nhau.
- Vòng lặp ghi đè `final_move`, nên nước được chọn là hướng **cuối cùng** thỏa điều kiện theo thứ tự UP → DOWN → LEFT → RIGHT. Lựa chọn hoàn toàn phụ thuộc vào thứ tự hướng, không liên quan tới bản đồ.

### 3. Không nhận biết ngõ cụt — đúng như tác giả nghi ngờ

**Vì sao:**
- T chỉ trả lời câu hỏi "Pacman cần bao lâu để tới đây", không trả lời "từ đây có lối ra không".
- Đi sâu vào ngõ cụt thì T vẫn tăng đều, giống hệt như đi vào một hành lang thông.
- Ô cuối ngõ cụt là **đỉnh cục bộ** của T, tức chính là đích mà thuật toán "leo lên chỗ T cao nhất" hướng tới.

Map mặc định có 2 ngõ cụt thật: (9,1)–(9,4) và (9,16)–(9,19). Các ô bậc 1 khác đều nằm trong những ô kín không đi vào được.

**Ví dụ:** Ghost ở ngã ba (9,5), Pacman ở (1,15). Ghost tối ưu sống được 17 bước.
```
t1: G (9,5) T=9 kề={UP: 9, DOWN: 10, LEFT: 10, RIGHT: 9} -> LEFT   ← DOWN và LEFT hòa, LEFT đứng sau nên được chọn
t2-t5: G (9,4) STAY (cao nguyên, xem điểm yếu 1)
t6-t10: đi sâu dần (9,3) → (9,2) → (9,1), xen kẽ STAY
t13: bị bắt ở (9,1)
#G..................#      ← hàng 9 lúc bị bắt
```
Ghost sống 13 bước, thay vì 17. Chỉ riêng nước LEFT ở lượt 1 đã làm mất 2 bước sống so với tối ưu; mỗi lượt STAY sau đó mất thêm 1 bước.

**Số liệu:** 367/2.274 ván Ghost tự đi vào ngõ cụt rồi bị bắt trong đó.

### 4. Vẫn chỉ nhìn 1 lượt

T được tính từ vị trí **hiện tại** của Pacman, trong khi Pacman đi cùng lượt. Ghost không thấy được vùng nào sẽ bị Pacman chặn đầu. Đây là điểm yếu 4 của review trước, vẫn còn nguyên.

### 5. Các điểm nhỏ

- Tốc độ `2` bị gán cứng trong `_pacman_move_time`. Với cấu hình mặc định thì đúng, nhưng Ghost không được arena báo tốc độ. Nếu thầy cô đổi `--pacman-speed`, nên tự suy ra tốc độ (xem bước 1 trong [hướng dẫn](2026-10-16_ghost-improvement-guide.md)).
- `self.previous_move` không còn được cập nhật. `_move_decision_bfs`, `_distance_bfs`, `_dfs` và `_is_backward_move` không còn được dùng, có thể xóa.

## Cách sửa (đã đo)

### Sửa 1 — lấy max, hòa thì vẫn đi (sửa điểm yếu 1 và 2)

Thay đoạn [dòng 188-197](../pacman/submissions/24880218/agent.py#L188-L197):

```python
pacman_time_map = self._pacman_move_time(map_state, enemy_position)
options = [(my_position, Move.STAY)] + self._get_neighbors(my_position, map_state)
# Chọn ô Pacman cần lâu nhất để tới; hòa thì ưu tiên di chuyển hơn đứng yên
_, final_move = max(options, key=lambda o: (pacman_time_map.get(o[0], float('inf')),
                                            o[1] != Move.STAY))
return final_move
```

**Kết quả:** sống trước Pacman BFS tăng từ 17,7 lên 22,9 bước; xuất phát cố định từ 7 lên 11 (bằng mức tối ưu lý thuyết).

**Cần lưu ý:** số ván chết trong ngõ cụt giảm từ 367 xuống 12, nhưng chỉ vì `max()` lấy phần tử **đầu tiên** đạt max, nên DOWN tình cờ đứng trước LEFT. Đảo thứ tự hướng thì con số này tăng lên 936. Vì vậy vẫn cần sửa 2.

### Sửa 2 — đánh dấu sẵn ô ngõ cụt và tránh đi vào (sửa điểm yếu 3)

Map không đổi trong suốt ván, nên chỉ cần tính một lần. Cách làm: liên tục "bóc" các ô chỉ có ≤ 1 ô kề, cho tới khi không còn ô nào như vậy. Các ô đã bị bóc chính là các nhánh cụt.

```python
def _dead_end_cells(self, map_state):
    """Các ô thuộc nhánh cụt: bóc dần các ô chỉ có <= 1 ô kề"""
    cells = [(r, c) for r in range(map_state.shape[0])
             for c in range(map_state.shape[1]) if map_state[r, c] == 0]
    degree = {c: len(self._get_neighbors(c, map_state)) for c in cells}
    queue = deque(c for c in cells if degree[c] <= 1)
    dead = set(queue)
    while queue:
        cur = queue.popleft()
        for nxt, _ in self._get_neighbors(cur, map_state):
            if nxt not in dead:
                degree[nxt] -= 1
                if degree[nxt] <= 1:
                    dead.add(nxt)
                    queue.append(nxt)
    return dead
```

Trên map mặc định, hàm này tìm đúng (9,1)–(9,4) và (9,16)–(9,19), cùng các ô kín.

Dùng trong `step` (thêm `self.dead_ends = None` vào `__init__`):

```python
if self.dead_ends is None:
    self.dead_ends = self._dead_end_cells(map_state)

def score(option):
    pos, move = option
    enters_dead_end = pos in self.dead_ends and my_position not in self.dead_ends
    return (not enters_dead_end,                       # 1. không bước vào ngõ cụt
            pacman_time_map.get(pos, float('inf')),    # 2. Pacman cần lâu nhất
            move != Move.STAY)                         # 3. hòa thì di chuyển

_, final_move = max(options, key=score)
```

**Kết quả:** 0/2.274 ván bị bắt trong ngõ cụt, bất kể thứ tự hướng. Sống trung bình trong vùng này đạt 12,8 bước (bản thử nghiệm: 7,2).

**Giới hạn của sửa 2:**
- Cách bóc ô chỉ tìm được **ngõ cụt cố định** (những nhánh hình cây). Nó không phát hiện được **"ngõ cụt động"**: một vùng có lối ra, nhưng Pacman tới lối ra trước Ghost. Muốn bắt được trường hợp đó cần vùng an toàn hoặc nhìn trước (bước 2–3 trong [hướng dẫn](2026-10-16_ghost-improvement-guide.md)).
- Nếu Ghost **đã ở sẵn** trong ngõ cụt, cả ba điều kiện trên không giúp nó thoát ra (T tăng dần về phía cuối ngõ). Trường hợp này hiếm, vì chỉ xảy ra khi Ghost xuất phát ở đó.

## Bước tiếp theo

Sau sửa 1 + sửa 2, bản này tương đương bước 1 của [hướng dẫn](2026-10-16_ghost-improvement-guide.md), có thêm phần tránh ngõ cụt cố định. Mức cải thiện lớn tiếp theo là **nhìn trước 2 lượt** (bước 3 của hướng dẫn). Trong benchmark, bước đó đạt 24/29 trước Pacman tham lam và 24,5 bước trước Pacman BFS.
