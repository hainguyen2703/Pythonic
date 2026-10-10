# Câu hỏi thảo luận – Bài toán N-Queens

> **Câu hỏi:** Tại sao bài toán N-Queens trở nên rất khó (tốn nhiều thời gian) khi N tăng lên? Độ phức tạp lý thuyết là bao nhiêu?

## 1. Không gian trạng thái tăng theo hàm mũ / giai thừa

Với mô hình "mỗi cột đặt đúng 1 quân hậu, trạng thái là tuple vị trí hàng", cây tìm kiếm có:

- **Độ sâu** $d = N$ (đặt lần lượt N cột).
- **Hệ số phân nhánh** $b = N$ (mỗi cột có N hàng để chọn).

Số trạng thái cần xét tùy theo mức ràng buộc:

| Cách mô hình hóa | Số trạng thái đầy đủ | N = 8 |
|---|---|---|
| Đặt N quân bất kỳ trên N² ô | $\binom{N^2}{N}$ | 4 426 165 368 |
| Mỗi cột 1 quân (không pruning) | $N^N$ | 16 777 216 |
| Mỗi cột 1 quân, khác hàng (có pruning theo hàng) | $N!$ | 40 320 |
| **Số lời giải thật sự** | — | **92** |

So sánh tốc độ tăng khi N tăng:

| N | $N^N$ | $N!$ | Số lời giải |
|---|---|---|---|
| 4 | 256 | 24 | 2 |
| 6 | 46 656 | 720 | 4 |
| 8 | 16 777 216 | 40 320 | 92 |
| 10 | $10^{10}$ | 3 628 800 | 724 |
| 12 | ≈ $8.9 \times 10^{12}$ | 479 001 600 | 14 200 |

Chỉ cần tăng N thêm 1, không gian $N^N$ tăng khoảng $e \cdot N$ lần. Trong khi đó, tỉ lệ lời giải trên tổng số trạng thái giảm rất nhanh, nên thuật toán tìm kiếm mù phải duyệt qua rất nhiều trạng thái "vô ích" trước khi gặp lời giải.

## 2. Độ phức tạp lý thuyết

### Thời gian

| Thuật toán | Số nút tối đa | Chi phí mỗi nút | Độ phức tạp thời gian |
|---|---|---|---|
| BFS / UCS / DFS **có pruning** (`is_safe`) | $O(N!)$ | $N$ lần gọi `is_safe`, mỗi lần $O(N)$ | $O(N^2 \cdot N!)$ |
| Greedy / A* **không pruning** (trường hợp xấu nhất) | $O(N^N)$ | `count_conflicts` $O(N^2)$ | $O(N^2 \cdot N^N)$ |

- Với pruning: ở cột thứ k chỉ còn tối đa $N - k$ hàng chưa bị chiếm, nên số nút bị chặn trên bởi $N!$. Thực tế còn nhỏ hơn nhiều vì ràng buộc đường chéo loại thêm nhánh.
- Không pruning: cây có $\sum_{k=0}^{N} N^k = O(N^N)$ nút, vì trạng thái có xung đột vẫn được sinh ra và đưa vào hàng đợi.

### Bộ nhớ

| Thuật toán | Bộ nhớ |
|---|---|
| DFS | $O(N^2)$ – stack giữ tối đa N con cho mỗi tầng trên một nhánh |
| BFS / UCS | $O(b^d)$ – phải lưu toàn bộ tầng sâu nhất (với pruning: cỡ $O(N!)$) |
| Greedy / A* | $O(N^N)$ trong trường hợp xấu nhất – frontier chứa cả trạng thái có xung đột |

Tóm lại, với tìm kiếm có hệ thống trên cây trạng thái, độ phức tạp là **hàm mũ**: $O(N^N)$ nếu không cắt nhánh và $O(N!)$ nếu có cắt nhánh.

## 3. Minh họa bằng thực nghiệm

Thời gian chạy (giây) của các hàm trong `lab3.ipynb` để tìm **một** lời giải:

| N | DFS | BFS | UCS | Greedy | A* |
|---|---|---|---|---|---|
| 6 | 0.0000 | 0.0002 | 0.0002 | 0.0002 | 0.0054 |
| 7 | 0.0000 | 0.0006 | 0.0008 | 0.0001 | 0.0290 |
| 8 | 0.0001 | 0.0027 | 0.0032 | 0.0011 | 0.2896 |
| 9 | 0.0001 | 0.0133 | 0.0168 | 0.0005 | 3.0181 |
| 10 | 0.0002 | 0.0688 | 0.0868 | 0.0016 | ≈ 58 |

Nhận xét:

- **BFS và UCS** tăng khoảng 5 lần mỗi khi N tăng 1. Với $g(n)$ = số quân đã đặt, UCS duyệt theo đúng thứ tự tầng như BFS, nên phải mở rộng hết các tầng nông trước khi chạm tới tầng N.
- **DFS** rất nhanh vì đi thẳng xuống sâu và lời giải đầu tiên thường nằm khá sớm theo thứ tự duyệt. Tuy vậy, trường hợp xấu nhất vẫn là $O(N!)$.
- **Greedy** nhanh vì mọi trạng thái an toàn đều có $h = 0$; hàng đợi ưu tiên luôn mở rộng chúng trước, nên thuật toán hoạt động gần giống DFS. Các trạng thái có xung đột được sinh ra nhưng nằm lại trong hàng đợi, làm tốn bộ nhớ.
- **A\*** chậm nhất và tăng khoảng 10–20 lần mỗi khi N tăng 1. Lý do là $g$ tăng 1 với mỗi quân được đặt, trong khi $h$ ở các tầng nông còn nhỏ. Ví dụ trạng thái 2 quân có 1 xung đột có $f = 3$, nhỏ hơn $f = 4$ của trạng thái 4 quân an toàn. A\* vì vậy ưu tiên các trạng thái nông (kể cả có xung đột) và duyệt gần giống BFS trên không gian $N^N$ chưa được cắt nhánh.

## 4. Ghi chú

Độ khó ở trên là độ khó của **phương pháp tìm kiếm có hệ thống**, không phải giới hạn của bản thân bài toán:

- Tìm **một** lời giải bất kỳ (với N ≥ 4) có thể làm trong $O(N)$ bằng công thức xây dựng tường minh, hoặc gần tuyến tính bằng tìm kiếm cục bộ Min-Conflicts.
- Các biến thể khó hơn nhiều: bài toán **N-Queens Completion** (cho sẵn một số quân, hỏi có hoàn thành được không) đã được chứng minh là **NP-đầy đủ** (Gent, Jefferson & Nightingale, 2017). **Đếm tất cả lời giải** chưa có công thức đóng; số lời giải tăng xấp xỉ $(0.143N)^N$ (Simkin, 2021), nên mọi thuật toán liệt kê đều phải tốn thời gian hàm mũ.
