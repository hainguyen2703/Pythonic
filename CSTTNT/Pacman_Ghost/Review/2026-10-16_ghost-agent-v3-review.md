# Review GhostAgent v3 (bản đồ thời gian Pacman + kiểm tra ngõ cụt) — 2026-10-16

- **File được review:** [pacman/submissions/24880218/agent.py](../pacman/submissions/24880218/agent.py), thay đổi chưa commit, đè lên `3a7cba5`. Gồm `step` ([dòng 186-207](../pacman/submissions/24880218/agent.py#L186-L207)) và `_is_dead_end` ([dòng 268-287](../pacman/submissions/24880218/agent.py#L268-L287)).
- **Thay đổi so với [review lỗi ngõ cụt](2026-10-16_ghost-dead-end-bug-review.md):** đã sửa lỗi crash; `best_moves` giữ cặp `(pos, move)` và hàm trả về `move`. `_is_dead_end` vẫn giữ nguyên.
- **Cấu hình test:** map mặc định, speed 2, bị bắt khi Manhattan ≤ 1, 200 bước, nhìn thấy toàn bộ map. Mỗi phép đo chạy 6 lần với 6 seed khác nhau, vì Ghost chọn ngẫu nhiên khi hòa.

## Tóm tắt

| | Kết quả |
|---|---|
| Chạy thật trong arena (`arena.py --seek example_student --hide 24880218`) | Không còn crash. Thua ở bước 42 (xuất phát cố định). |
| Ngõ cụt cố định | **Đã giải quyết:** 0/2.274 ván bị bắt trong ngõ cụt (v2: 388) |
| Hiệu quả tổng thể | **Đi lùi so với v2**, do `_is_dead_end` báo nhầm góc rẽ là ngõ cụt |

## Diễn biến qua các phiên bản

| Phiên bản | Pacman tham lam: thắng /29 | Pacman BFS: sống TB | Pacman BFS: xuất phát cố định | Chết trong ngõ cụt /2.274 |
|---|---|---|---|---|
| Gốc: BFS + DFS (`3a7cba5`) | 20 | 21,7 | 11 | — |
| T-map v1 (điều kiện `>`) | 23 | 17,7 | 7 | 367 |
| T-map v2 (`>=`, ngẫu nhiên) | 21–25 | 22,2–22,9 | 11–13 | 388 |
| **v3 hiện tại** (+ `_is_dead_end`) | **11–19** | **19,8–20,5** | 11–15 | **0** |
| v3, thay `_is_dead_end` bằng tập ngõ cụt bóc ô | **21–24** | **22,3–22,8** | — | **0** |
| Nhìn trước 2 lượt ([hướng dẫn](2026-10-16_ghost-improvement-guide.md) bước 3) | 24 | 24,5 | 10 | — |
| Trần lý thuyết (bảng tối ưu) | 27 | 25,3 | 11 | — |

Hai dòng "v3" là phép thử A/B: cùng code, cùng seed, chỉ khác hàm kiểm tra ngõ cụt. Toàn bộ khoảng cách giữa hai dòng đến từ `_is_dead_end`.

## Điểm yếu 1 — `_is_dead_end` báo nhầm góc rẽ là ngõ cụt (nặng nhất)

**Cơ chế:**
- Hàm chỉ quét **theo đường thẳng** của hướng đi, và coi đó là ngõ cụt nếu không ô nào trên đường đó có > 2 ô kề.
- Một hành lang **rẽ góc** thì mọi ô trên đoạn thẳng đều có đúng 2 ô kề, nên bị báo là ngõ cụt, dù hành lang vẫn tiếp tục sau góc rẽ.

**Số liệu** (chấm trên toàn bộ khoảng 41 nghìn trạng thái của map bằng bảng tối ưu):

| | `_is_dead_end` hiện tại | Tập ngõ cụt bóc ô |
|---|---|---|
| Cặp (ô → ô kề) bị báo nhầm là ngõ cụt | 84 | 0 |
| Ngõ cụt thật bị bỏ sót | 0 | 0 |
| Trạng thái Ghost STAY chỉ vì mọi nước tốt nhất bị báo ngõ cụt | **11.920** (~29%) | 0 |
| Quyết định kém hơn nước tốt nhất | 17,9% | 13,4% |

**Ví dụ (seed 3, Pacman tham lam):** ở lượt 9, Ghost ở góc trái (3,1), Pacman ở (15,11).

```
#.........#   ← hàng 1
#.###.###.#
#G.........   ← hàng 3
#.###.#.###
```

| Nước | Ô tới | T | `_is_dead_end` |
|---|---|---|---|
| UP | (2,1) | **12** (tốt nhất) | **True** — quét (2,1), (1,1), mỗi ô 2 ô kề; thực ra (1,1) rẽ sang hàng 1 |
| DOWN | (4,1) | 11 | **True** — tương tự, thực ra (5,1) thông sang hàng 5 |
| RIGHT | (3,2) | 11 | False |

UP bị loại nên `best_moves` rỗng, và Ghost STAY. Lượt sau tình huống y hệt, nên Ghost đứng yên liền 8 lượt trở lên rồi bị bắt ở bước 27. Bản dùng tập ngõ cụt bóc ô đi UP ở lượt 9 và sống đủ 200 bước.

**Lỗi tiềm ẩn đi kèm:** `range(...)` quét tới mép map mà không dừng ở tường. `_get_neighbors` của một ô tường vẫn đếm các ô trống xung quanh, nên hàm có thể thấy "lối rẽ" ở bên kia tường. Trên map mặc định chưa gây sai, nhưng trên map khác thì có thể.

**Sửa (đã đo):** thay thân hàm bằng tập ngõ cụt tính một lần, giữ nguyên chữ ký để `step` không phải đổi.

```python
# trong __init__
self.dead_ends = None

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

def _is_dead_end(self, pos, move, map_state) -> bool:
    if self.dead_ends is None:                      # map không đổi → tính 1 lần
        self.dead_ends = self._dead_end_cells(map_state)
    return pos in self.dead_ends
```

Trên map mặc định, tập này gồm đúng (9,1)–(9,4), (9,16)–(9,19) và các ô kín không đi vào được.

Mình cũng đã thử đổi thứ tự trong `step`: lọc ngõ cụt trước rồi mới tìm T tốt nhất, để Ghost không STAY khi vẫn còn nước khác. Kết quả **giống hệt** (21–24/29, 22,3–22,8 bước): khi đã phát hiện ngõ cụt đúng thì trường hợp này gần như không xảy ra. Không cần đổi.

## Điểm yếu 2 — giới hạn của việc chỉ nhìn 1 lượt (không đổi so với v2)

Đây là phần mất mát còn lại sau khi sửa điểm yếu 1. Nó đến từ chính cách tiếp cận "đi tới ô có T lớn nhất", nên không sửa được bằng cách tinh chỉnh quy tắc.

- **Chạy dọc hành lang thẳng.** Ví dụ ván xuất phát cố định gặp Pacman tham lam (thua ở bước 30): từ lượt 24, Ghost chạy dọc cột 5 từ (9,5) xuống (15,5), một hành lang thẳng dài 7 ô. Pacman đi song song rồi chặn đầu ở (13,5)→(15,5). Ở mỗi lượt, T của ô phía trước vẫn lớn nhất, nên Ghost không thấy mình đang bị dồn.
- **Ngõ cụt động.** Một khu có lối ra, nhưng lối ra lại hướng về phía Pacman. Ví dụ Ghost ở (13,16), Pacman ở (19,16): Ghost đi RIGHT (sống 10 bước) thay vì LEFT (sống 12). Xem [review v2](2026-10-16_ghost-pacman-time-v2-review.md).
- Cách sửa duy nhất có số liệu là **nhìn trước 2 lượt**: 13,6% → 9,4% quyết định kém; 24/29 và 24,5 bước.

## Điểm nhỏ

- Ghost vẫn dùng `random` chung với Pacman tham lam (Pacman này gọi `random.shuffle`). Kết quả vì vậy dao động mạnh giữa các lần chạy (11–19/29). Dùng `self.rng = random.Random(seed)` riêng thì sẽ chạy lại được đúng một ván để debug.
- [Dòng 199-203](../pacman/submissions/24880218/agent.py#L199-L203): copy rồi `remove` chạy đúng, nhưng một list comprehension `[(p, m) for p, m in best_moves if not self._is_dead_end(p, m, map_state)]` thì gọn hơn.
- Docstring của `_is_dead_end` ghi "only one valid move" nhưng code kiểm tra một điều khác. Các dòng `# TODO` cũ có thể xóa.

## Đề xuất

1. **Thay thân `_is_dead_end` bằng tập ngõ cụt bóc ô.** Chỉ sửa một hàm, đưa kết quả về mức v2 mà vẫn giữ 0 ván chết trong ngõ cụt: 21–24/29 và khoảng 22,5 bước.
2. Dùng bộ sinh số ngẫu nhiên riêng cho Ghost.
3. Bước cải thiện lớn tiếp theo: nhìn trước 2 lượt ([hướng dẫn](2026-10-16_ghost-improvement-guide.md) bước 3).
