# 3.1. Mô hình hóa bài toán N-Queens

Bài toán được mô hình hóa theo cách **đặt dần từng quân hậu theo cột, từ trái sang phải**: mỗi cột có đúng một quân hậu, nên ràng buộc "không cùng cột" luôn được thỏa mãn và chỉ cần xét ràng buộc hàng và đường chéo.

## 1. Trạng thái

Một trạng thái là một bộ (tuple) gồm vị trí hàng của các quân hậu đã đặt:

$$s = (r_0, r_1, \dots, r_{k-1}), \quad 0 \le k \le N, \quad r_i \in \{0, 1, \dots, N-1\}$$

- $r_i$ là **hàng** của quân hậu ở **cột** $i$.
- $k = |s|$ là số quân hậu đã đặt; cột tiếp theo cần đặt là cột $k$.

Không gian trạng thái:

$$S = \bigcup_{k=0}^{N} \{0, 1, \dots, N-1\}^k$$

Ví dụ với N = 4: $s = (1, 3)$ nghĩa là đã đặt hậu tại ô (hàng 1, cột 0) và (hàng 3, cột 1).


## 2. Trạng thái đầu

$$s_0 = () \quad \text{(bàn cờ trống, chưa đặt quân nào)}$$

## 3. Phép chuyển (Hành động)

Từ trạng thái $s = (r_0, \dots, r_{k-1})$ với $k < N$, hành động là chọn một hàng $r$ để đặt quân hậu vào cột $k$:

$$\text{Actions}(s) = \{0, 1, \dots, N-1\}$$

$$\text{Result}(s, r) = (r_0, \dots, r_{k-1}, r)$$

Trạng thái có $|s| = N$ không có phép chuyển nào (không đặt quá N cột).

**Biến thể có cắt nhánh (dùng cho BFS, DFS, UCS):** chỉ cho phép những hàng an toàn so với các quân đã đặt:

$$\text{Actions}_{\text{safe}}(s) = \{\, r \mid \forall i < k:\ r \ne r_i \ \land\ |r - r_i| \ne k - i \,\}$$

Đây chính là điều kiện của hàm `is_safe(state, row, col)` với `col = k`.

## 4. Chi phí đường đi

Mỗi lần đặt một quân hậu có chi phí bằng 1:

$$c(s, r, s') = 1 \quad \Rightarrow \quad g(s) = |s| = \text{số quân hậu đã đặt}$$

## 5. Heuristic

$h(s)$ là **số cặp quân hậu tấn công nhau** trong trạng thái $s$ (hàm `count_conflicts`):

$$h(s) = \left|\{\, (i, j) \mid 0 \le i < j < |s|,\ r_i = r_j \ \lor\ |r_i - r_j| = j - i \,\}\right|$$

- Điều kiện $r_i = r_j$: hai quân cùng hàng.
- Điều kiện $|r_i - r_j| = j - i$: hai quân cùng đường chéo.
- Không cần xét cùng cột vì mỗi cột chỉ có một quân.

Tính chất của heuristic:

- $h(s) \ge 0$, và $h(s) = 0$ khi và chỉ khi không có cặp hậu nào tấn công nhau.
- **Không giảm** dọc theo đường đi: thêm quân hậu chỉ có thể tạo thêm xung đột, không xóa được xung đột cũ. Vì vậy trạng thái có $h(s) > 0$ không bao giờ dẫn tới đích.
- **Chấp nhận được (admissible):** chi phí thật để tới đích là $h^*(s) = N - |s|$ nếu $s$ còn mở rộng được thành lời giải, và $h^*(s) = \infty$ nếu không. Trong cả hai trường hợp $h(s) \le h^*(s)$. Tuy nhiên heuristic này khá "yếu": mọi trạng thái an toàn đều có $h = 0$, nên nó chỉ phân biệt được trạng thái an toàn / có xung đột.

## 6. Kiểm tra đích

$$\text{Goal}(s) \iff |s| = N \ \land\ h(s) = 0$$

Tức là đã đặt đủ N quân hậu và không có cặp nào tấn công nhau. Với các thuật toán có cắt nhánh, mọi trạng thái được sinh ra đều có $h = 0$, nên chỉ cần kiểm tra $|s| = N$.

Lời giải được trả về dưới dạng danh sách tọa độ:

$$\text{Output}(s) = [(r_0, 0), (r_1, 1), \dots, (r_{N-1}, N-1)]$$

## 7. Hàm đánh giá của từng thuật toán

| Thuật toán | Cấu trúc dữ liệu | Thứ tự mở rộng | Cắt nhánh |
|---|---|---|---|
| BFS | Queue (FIFO) | Theo tầng | Có (`is_safe`) |
| DFS | Stack (LIFO) | Đi sâu trước | Có (`is_safe`) |
| UCS | Priority Queue | $f(s) = g(s)$ | Có (`is_safe`) |
| Greedy | Priority Queue | $f(s) = h(s)$ | Không |
| A\* | Priority Queue | $f(s) = g(s) + h(s)$ | Không |

## 8. Ví dụ với N = 4

```
s0 = ()                       g = 0, h = 0
 └─ (1,)                      g = 1, h = 0
     └─ (1, 3)                g = 2, h = 0
         └─ (1, 3, 0)         g = 3, h = 0
             └─ (1, 3, 0, 2)  g = 4, h = 0   ← đích
```

Bàn cờ tương ứng (Q là quân hậu):

```
      c0 c1 c2 c3
r0     .  .  Q  .
r1     Q  .  .  .
r2     .  .  .  Q
r3     .  Q  .  .
```

Output: `[(1, 0), (3, 1), (0, 2), (2, 3)]`.
