# Review lỗi kiểm tra ngõ cụt trong GhostAgent — 2026-10-16

- **File được review:** [pacman/submissions/24880218/agent.py](../pacman/submissions/24880218/agent.py), thay đổi chưa commit. Gồm `step` ([dòng 195-207](../pacman/submissions/24880218/agent.py#L195-L207)) và `_is_dead_end` ([dòng 268-287](../pacman/submissions/24880218/agent.py#L268-L287)).
- **Thay đổi so với [review v2](2026-10-16_ghost-pacman-time-v2-review.md):** tác giả viết gọn `step` như gợi ý của review v2, và thêm `_is_dead_end` để loại các nước dẫn vào ngõ cụt.
- **Câu hỏi của tác giả:** đoạn dòng 195-203 đang gặp lỗi gì?
- **Cấu hình test:** map mặc định, speed 2, bị bắt khi Manhattan ≤ 1, 200 bước, nhìn thấy toàn bộ map.

## Lỗi 1 — crash khi tách cặp `(pos, move)` (dòng 196 → 200)

`best_moves = [move for pos, move in neighbors if ...]` chỉ giữ lại `move`. Vì vậy `best_moves` là danh sách `Move`, không phải các cặp `(pos, move)`. Dòng 200 `for pos, move in best_moves_copy` cố tách một `Move` thành hai biến:

```
TypeError: cannot unpack non-iterable Move object
```

- Lỗi chỉ xảy ra khi Ghost không `return STAY` sớm ở dòng 194. Ví dụ: Ghost ở (9,5), Pacman ở (9,13). Ở xuất phát cố định thì lượt đầu không lỗi, vì Ghost đứng yên và thoát hàm sớm.
- Trong arena, Ghost văng exception đồng nghĩa với **Pacman được xử thắng ngay**.
- Dòng 203 `best_moves.remove((pos, move))` và dòng 207 `random.choice(best_moves)` cũng phải sửa theo. Nếu list chứa tuple thì phải trả về phần tử `[1]`; nếu không, arena nhận được một tuple, coi là nước đi không hợp lệ, và Ghost thua.

**Sửa:**

```python
best_moves = [(pos, move) for pos, move in neighbors
              if pacman_time_map.get(pos, float('inf')) == best_time]
# Bỏ các ô dẫn vào ngõ cụt
best_moves = [(pos, move) for pos, move in best_moves
              if not self._is_dead_end(pos, move, map_state)]
if not best_moves:
    return Move.STAY
return random.choice(best_moves)[1]      # [1] = lấy Move
```

## Lỗi 2 — `_is_dead_end` báo nhầm góc rẽ là ngõ cụt

Mình so sánh hàm này với tập ngõ cụt thật, tìm bằng cách bóc dần các ô chỉ có ≤ 1 ô kề, trên mọi cặp (ô không thuộc ngõ cụt → ô kề) của map mặc định:

| | Số trường hợp |
|---|---|
| Bỏ sót ngõ cụt thật | 0 |
| **Báo nhầm là ngõ cụt** | **84** |

**Nguyên nhân 1 — chỉ quét đường thẳng, nên góc rẽ bị coi là ngõ cụt.** Ví dụ Ghost ở (1,2) đi LEFT sang (1,1):
- `path = [(1,1)]`. Ô (1,1) có 2 ô kề là (1,2) và (2,1), không thỏa `> 2`, nên hàm trả về `True`.
- Thực tế hành lang rẽ xuống (2,1), (3,1) và nối vào ngã ba ở hàng 3.
- Hệ quả: Ghost không dám rẽ ở các góc. Nếu nước tốt nhất duy nhất là rẽ góc thì nó bị loại, và Ghost lại đứng yên.

**Nguyên nhân 2 — quét xuyên tường (lỗi tiềm ẩn).** `range(pos[1], 0, -1)` và các `range` khác chạy tới mép map mà không dừng khi gặp tường. `_get_neighbors` của một ô tường vẫn đếm các ô trống xung quanh nó, nên hàm có thể nhận nhầm "lối rẽ" ở bên kia tường. Trên map mặc định chưa gây sai (0 bỏ sót), vì hai ngõ cụt thật ở hàng 9 chạy thẳng ra tới mép. Trên map khác thì có thể sai.

**Ảnh hưởng đo được** (sau khi đã sửa lỗi 1):

| Phiên bản | Pacman tham lam: thắng /29 | Pacman tham lam: xuất phát cố định | Pacman BFS: sống TB | Pacman BFS: xuất phát cố định |
|---|---|---|---|---|
| Dùng `_is_dead_end` hiện tại | 15 | thua ở bước 20 | 20,3 | 15 |
| Bản v2 (chưa kiểm tra ngõ cụt) | 21–25 | thắng | 22,2–22,9 | 11–13 |
| Dùng tập ngõ cụt tìm bằng cách bóc ô | 22 | thắng | 22,7 | 13 |

Với `_is_dead_end` hiện tại, Ghost còn tệ hơn so với khi không kiểm tra ngõ cụt.

**Sửa:** thay phần thân hàm bằng tập ngõ cụt tính một lần. Hàm `_dead_end_cells` có trong [review trước](2026-10-16_ghost-pacman-time-review.md), mục "Sửa 2". Giữ nguyên chữ ký để không phải sửa chỗ gọi:

```python
# trong __init__
self.dead_ends = None

def _is_dead_end(self, pos, move, map_state) -> bool:
    if self.dead_ends is None:                      # map không đổi → tính 1 lần
        self.dead_ends = self._dead_end_cells(map_state)
    return pos in self.dead_ends
```

## Lưu ý nhỏ

Khi mọi nước tốt nhất đều bị loại vì dẫn vào ngõ cụt, Ghost STAY. Lúc đó có thể vẫn còn một nước khác có T thấp hơn nhưng không dẫn vào ngõ cụt. Trên map mặc định, trường hợp này hiếm, vì các ngõ cụt chỉ nằm ở hai đầu hàng 9.
