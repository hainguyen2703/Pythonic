# Review GhostAgent "bản đồ thời gian Pacman" v2 — 2026-10-16

- **File được review:** [pacman/submissions/24880218/agent.py](../pacman/submissions/24880218/agent.py), thay đổi chưa commit. Phần chính là `step` ([dòng 186-213](../pacman/submissions/24880218/agent.py#L186-L213)).
- **Thay đổi so với [bản trước](2026-10-16_ghost-pacman-time-review.md):** Ghost xét cả các ô kề có thời gian Pacman (T) **bằng** ô hiện tại. Nếu nhiều ô cùng đạt T tốt nhất thì chọn ngẫu nhiên một ô.
- **Câu hỏi của tác giả:** khi mọi ô kề đều có T nhỏ hơn ô hiện tại (ví dụ hai ô kề có T bằng nhau và đều nhỏ hơn), Ghost sẽ đứng yên. Điều đó có phải vấn đề không?
- **Cấu hình test:** map mặc định, speed 2, bị bắt khi Manhattan ≤ 1, 200 bước, nhìn thấy toàn bộ map.

## Cách đánh giá

Ngoài benchmark ([scripts/bench_ghost.py](scripts/bench_ghost.py)), review này còn chấm **từng quyết định** bằng bảng giải tối ưu `D[ghost, pacman]`, là số bước Ghost sống được nếu cả hai bên chơi hoàn hảo (xem [review đầu tiên](2026-10-16_ghost-agent-review.md)). Với mỗi trạng thái, ta biết mỗi nước đi giữ được bao nhiêu bước sống. Một quyết định là **kém** nếu nó giữ được ít bước hơn nước tốt nhất. Toàn bộ khoảng 41 nghìn trạng thái của map đều được chấm.

## Kết quả benchmark

Bản này có yếu tố ngẫu nhiên, nên mình chạy 6 lần với 6 seed khác nhau và ghi lại khoảng dao động.

| Phiên bản | Pacman tham lam: thắng /29 | Pacman BFS: xuất phát cố định | Pacman BFS: sống TB | Chết trong ngõ cụt (2.274 ván quanh hàng 9) |
|---|---|---|---|---|
| Bản trước (điều kiện `>`) | 23 | 7 | 17,7 | 367 |
| **Bản này** | 21–25 | 11–13 | 22,2–22,9 | **388** (sống TB 12,4) |
| Sửa 1 + Sửa 2 của review trước (không ngẫu nhiên) | 22 | 11 | 22,9 | 0 (sống TB 12,8) |

Bản này đã sửa được lỗi "đóng băng" của bản trước: sống trung bình từ 17,7 lên khoảng 22,7 bước. Kết quả ngang với Sửa 1 của review trước. **Ngõ cụt thì vẫn chưa được xử lý.**

## Trả lời câu hỏi: Ghost đứng yên khi mọi ô kề có T nhỏ hơn

**Cơ chế thì đúng.** `max_pacman_time` bắt đầu từ `current_pacman_time`. Nếu mọi ô kề đều có T nhỏ hơn thì `move_set` rỗng, `final_move` giữ giá trị `Move.STAY`.

**Nhưng đứng yên ở đó phần lớn là đúng.** Ghost đang ở chỗ Pacman cần lâu nhất để tới; bước sang bất kỳ ô nào cũng là tự đến gần Pacman hơn.

| Kết quả chấm 462 trạng thái "mọi ô kề T nhỏ hơn" | Số trạng thái |
|---|---|
| STAY là nước tốt nhất | 224 (48%) |
| STAY hòa với nước tốt nhất | 174 (38%) |
| STAY kém hơn (mất **đúng 1 bước** trong mọi trường hợp) | 64 (14%) |

- **Ví dụ:** xuất phát cố định, Ghost ở (9,10), Pacman ở (15,10). T hiện tại = 7, LEFT = 6, RIGHT = 6, nên Ghost STAY. Theo bảng tối ưu: STAY sống được **11** bước, còn đi LEFT hoặc RIGHT chỉ **10**. Đứng yên chính là nước tối ưu.
- **Ví dụ STAY kém:** Ghost ở (19,16), Pacman ở (3,8). T kề = 15 và 15, T hiện tại = 16. STAY sống 21 bước, đi LEFT sống 22.
- Tình huống này chỉ chiếm **0,9%** tổng số bước sống bị mất (xem bảng dưới). Nếu ép Ghost phải đi thì sẽ làm hỏng 224 trường hợp mà STAY đang đúng. **Không nên sửa chỗ này.**

## Mất mát thực sự nằm ở đâu

| Tình huống | Số trạng thái | Quyết định kém | Phần trong tổng mất mát |
|---|---|---|---|
| Mọi ô kề T nhỏ hơn → STAY *(điều tác giả lo)* | 462 | 13,9% | **0,9%** |
| Có đúng 1 ô kề T lớn hơn | 10.866 | 6,4% | 15,7% |
| Nhiều ô kề cùng T lớn hơn → chọn ngẫu nhiên | 5.070 | 33,3% | 19,4% |
| … trong đó có ô ngõ cụt | 380 | **78,9%** | 3,1% |
| Ô kề tốt nhất có T **bằng** ô hiện tại → đi sang đó | 22.144 | 10,7% | **53,8%** |
| … nhiều ô cùng T bằng → chọn ngẫu nhiên | 2.042 | 30,0% | 7,0% |

### Điểm yếu 1 — đi sang ô có T bằng nhau (chiếm 61% mất mát)

Đi sang ô có T bằng nhau là đúng trong khoảng 89% trường hợp; đó chính là điều đã giải quyết lỗi đóng băng. Khi sai, nước đúng thường là:

| Nước đúng | Số ca (lấy mẫu 2.500 trạng thái) |
|---|---|
| Đi sang ô có T **nhỏ hơn** | 117 (68%) |
| Đi sang một ô T bằng khác | 29 |
| STAY | 27 |

Nghĩa là: đôi khi Ghost phải **tạm thời đi về phía gần Pacman hơn** để tránh bị dồn vào góc. Quy tắc "chọn T lớn nhất" không bao giờ chọn được nước như vậy.

**Ví dụ — "ngõ cụt động":** Ghost ở (13,16), Pacman ở (19,16). T hiện tại = 8, RIGHT = 8, LEFT = 7, nên Ghost đi RIGHT.

```
#.........#.....G...#   ← hàng 13
#.###.###.#.###.###.#
#...#...........#...#
###.#.#.#####.#.#.###
#.....#...#...#.....#
#.#######.#.#######.#
#...............P...#   ← hàng 19
```

Bảng tối ưu cho số bước sống: LEFT **12**, STAY 11, RIGHT **10**. Đi RIGHT dẫn vào khu (13,17)–(15,19), nơi lối ra duy nhất đi xuống phía Pacman. Khu này không phải ngõ cụt cố định (nó có lối ra), nên cách bóc ô của Sửa 2 cũng không phát hiện được. Đi LEFT thì tới (13,14), từ đó lên được nửa trên rộng rãi của map.

### Điểm yếu 2 — vẫn đi vào ngõ cụt cố định

- 388/2.274 ván Ghost bị bắt trong ngõ cụt hàng 9, gần như không đổi so với bản trước (367).
- Ví dụ quen thuộc: ở ngã ba (9,5), DOWN và LEFT cùng có T = 10. Giờ Ghost chọn ngẫu nhiên, nên có 50% khả năng đi LEFT vào ngõ cụt.
- Trong các ca hòa mà có ô ngõ cụt, 78,9% quyết định là kém.
- **Cách sửa:** mục "Sửa 2" trong [review trước](2026-10-16_ghost-pacman-time-review.md). Đặt "không bước vào ô ngõ cụt" làm tiêu chí đầu tiên, rồi mới xét T. Đã đo: 388 → 0.

### Điểm yếu 3 — chọn ngẫu nhiên khi hòa

- **Không tốt hơn mà cũng không tệ hơn** so với chọn cố định theo thứ tự (22,2–22,9 so với 22,9 bước). Thông tin bị bỏ qua vẫn như nhau; chỉ là thay "luôn chọn hướng đứng đầu" bằng "chọn hú họa".
- **Làm kết quả khó lặp lại:** cùng một vị trí xuất phát, Ghost sống 11 hoặc 13 bước tùy lần chạy; số ván thắng Pacman tham lam dao động 21–25/29. Muốn biết một thay đổi có thực sự tốt lên hay không thì phải chạy nhiều lần.
- Ghost dùng chung bộ sinh số ngẫu nhiên `random` của Python với Pacman tham lam (Pacman này cũng gọi `random.shuffle`). Vì vậy kết quả còn phụ thuộc vào thứ tự gọi giữa hai agent.
- **Gợi ý:**
  - Ưu tiên các tiêu chí có ý nghĩa (ngõ cụt trước, rồi T), ngẫu nhiên chỉ để phá hòa cuối cùng.
  - Dùng bộ sinh số riêng `self.rng = random.Random(seed)` trong `__init__` để chạy lại được đúng một ván.

### Thử các cách phá hòa khác — không đủ

Mình chấm thêm vài cách phá hòa thay cho ngẫu nhiên, trên toàn bộ trạng thái:

| Quy tắc | Quyết định kém | Mất TB / quyết định |
|---|---|---|
| Bản hiện tại (ngẫu nhiên) | 14,0% | 0,172 bước |
| + tránh ngõ cụt | 13,4% | 0,167 |
| + phá hòa bằng T tốt nhất sau 2 bước đi của Ghost | 13,9% | 0,171 |
| + cả hai | 13,2% | 0,166 |
| **Nhìn trước 2 lượt** (bước 3 [hướng dẫn](2026-10-16_ghost-improvement-guide.md), mẫu 2.500 trạng thái) | **9,4%** | 0,151 |

Mọi quy tắc chỉ dựa trên T đều dừng ở khoảng 13–14% quyết định kém. Nguyên nhân: T chỉ được tính từ vị trí **hiện tại** của Pacman, nên không thấy vùng nào sắp bị chặn. Đây là giới hạn của việc chỉ nhìn 1 lượt, không phải lỗi phá hòa.

## Code

Logic đúng: `move_set` gom các ô có T ≥ max tạm thời, sau đó [dòng 206](../pacman/submissions/24880218/agent.py#L206) lọc lại đúng các ô bằng max. Có thể viết gọn hơn, với cùng hành vi:

```python
pacman_time_map = self._pacman_move_time(map_state, enemy_position)
current_time = pacman_time_map.get(my_position, float('inf'))
neighbors = self._get_neighbors(my_position, map_state)
if not neighbors:
    return Move.STAY

best_time = max(pacman_time_map.get(pos, float('inf')) for pos, _ in neighbors)
if best_time < current_time:          # đang ở đỉnh: đứng yên thường là tối ưu
    return Move.STAY
best_moves = [move for pos, move in neighbors
              if pacman_time_map.get(pos, float('inf')) == best_time]
return random.choice(best_moves)
```

Điểm nhỏ: `self.previous_move` không còn được dùng.

## Đề xuất theo thứ tự

1. **Giữ nguyên** việc STAY khi mọi ô kề có T nhỏ hơn.
2. **Thêm tránh ngõ cụt** (Sửa 2 của review trước). Đây là lỗi duy nhất còn lại có số liệu rõ ràng: 388 → 0.
3. Dùng `random.Random(seed)` riêng cho Ghost để benchmark ổn định.
4. Muốn giảm tiếp mất mát lớn nhất (đi sang ô cùng T, ngõ cụt động) thì cần **nhìn trước**: bước 3 của [hướng dẫn](2026-10-16_ghost-improvement-guide.md).
