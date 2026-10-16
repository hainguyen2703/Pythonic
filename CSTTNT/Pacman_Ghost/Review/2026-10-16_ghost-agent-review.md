# Review GhostAgent — 2026-10-16

- **File được review:** [pacman/submissions/24880218/agent.py](../pacman/submissions/24880218/agent.py) (commit `3a7cba5 BFS Ghost`)
- **Luật tham chiếu:** [pacman/src/environment.py](../pacman/src/environment.py), [pacman/src/arena.py](../pacman/src/arena.py)
- **Cấu hình test:** map mặc định, `--pacman-speed 2`, `--capture-distance 2` (bị bắt khi Manhattan ≤ 1), `--max-steps 200`
- **Phạm vi:** chỉ chế độ nhìn thấy toàn bộ map. Chế độ sương mù (fog of war) không nằm trong yêu cầu đề bài nên không được xét.

## Tóm tắt thuật toán hiện tại

Ghost chỉ nhìn 1 bước. Nó giữ lại các nước làm **khoảng cách BFS tới vị trí hiện tại của Pacman** tăng lên. Trong số đó, nó ưu tiên nước rẽ, với điều kiện DFS tìm được một đường đi dài 6 ô. Nếu không có nước nào tăng khoảng cách thì nó đứng yên (STAY).

## Kết quả đo

| Đối thủ Pacman | Xuất phát cố định | Xuất phát ngẫu nhiên (30 ván) |
|---|---|---|
| Tham lam theo Manhattan (`example_student`) | Ghost thắng 200 bước | Ghost thắng 20/30 |
| BFS theo đúng luật tốc độ (tự viết để test) | Thua ở bước 11 | Thắng 1/30, sống trung bình 21 bước |

Để tham khảo, `agent_ai.py` (hướng giải bảng) đấu với Pacman BFS: xuất phát cố định thua ở bước 15, ngẫu nhiên thắng 1/30.

## Phát hiện quan trọng: trò chơi đã được giải

Phân tích ngược (retrograde) trên toàn bộ 40.964 trạng thái `(ghost, pacman)` của map mặc định cho thấy một Pacman chơi hoàn hảo **luôn bắt được Ghost**:

| Mô hình thông tin | Từ vị trí xuất phát | Tối đa, từ mọi trạng thái | Trạng thái Ghost sống mãi |
|---|---|---|---|
| Pacman thấy nước của Ghost (bất lợi cho Ghost) | 11 bước | 23 bước | 0 |
| Ghost thấy nước của Pacman (có lợi cho Ghost) | 12 bước | 24 bước | 0 |

Hai mô hình này kẹp chặn trên và dưới của luật "hai bên đi cùng lúc", nên kết luận đúng với luật thật.

Hệ quả:
- Ván thua ở bước 11 (xuất phát cố định, gặp Pacman BFS) là mức tối ưu, không phải lỗi của thuật toán.
- Ghost chỉ thắng được 200 bước khi **Pacman chơi không hoàn hảo**. Mục tiêu thực tế là (1) kéo dài thời gian sống tối đa và (2) khai thác lỗi của đối thủ.
- Kế hoạch Minimax trong `Note.txt` chấm trạng thái thua là −∞. Khi gặp Pacman giỏi, mọi nhánh đều −∞ nên Ghost sẽ chọn bừa. Cần chấm theo "số bước đến khi bị bắt".
- 20 ván "thắng" trước Pacman tham lam không đáng tin: Ghost đứng yên khoảng 190/200 bước. Nó thắng chỉ vì Pacman tham lam bị kẹt đi qua đi lại sau tường.

## Các điểm yếu

### 1. Đứng yên khi ở "đỉnh cục bộ" của khoảng cách — [agent.py:286-288](../pacman/submissions/24880218/agent.py#L286-L288)

Trên lưới ô vuông, hai ô kề nhau luôn có khoảng cách BFS hơn kém **đúng ±1**. Vậy điều kiện `predict_dist > current_dist` thực chất là "đi ra xa thêm 1 ô". Ở góc tường, hoặc khi Pacman đối xứng hai phía, mọi ô kề đều gần Pacman hơn, nên Ghost STAY. Mỗi lượt STAY, Pacman áp sát thêm tối đa 2 ô.

- **Ví dụ (seed 12, đối thủ là Pacman tham lam):** Ghost chạy vào góc (1,1) rồi đứng yên 9 lượt liền (bước 3–11). Khi Pacman tới (1,3), Ghost mới chạy xuống cột 1, một đoạn thẳng. Pacman đi xuống 2 ô và bắt được ở bước 14.
  ```
  sau bước 11            sau bước 14
  #G...P....#            #.........#
  #.###.###.#            #.###.###.#
  #.........             #PG........
  ```
- **Ví dụ (xuất phát cố định, bước 1):** Ghost ở (9,10), Pacman ở (15,10). Hai đường sang trái và phải dài bằng nhau, nên cả hai ô kề đều gần hơn. Ghost STAY và mất một lượt miễn phí.

### 2. Đo khoảng cách sai đơn vị: số ô BFS không phải số lượt Pacman cần

Pacman đi 2 ô mỗi lượt trên đường thẳng. 10 ô thẳng chỉ tốn 5 lượt, nhưng 10 ô zigzag tốn tới 10 lượt. Hai đường này có cùng khoảng cách BFS nên Ghost coi chúng như nhau.

- **Ví dụ (xuất phát cố định, bước 6–11):** Ghost đi dọc hàng 7 trong khi Pacman lao ngang hàng 9, một hành lang thẳng, mỗi lượt +2 ô. Ở bước 9, Ghost rẽ UP vào đoạn dọc (6,11)→(5,11). Pacman thẳng hàng ngay phía sau, đi 2 ô và bắt được ở bước 11.
- Việc "ưu tiên rẽ" chỉ xét **một** lần rẽ ngay trước mắt. Nó không biết nhánh vừa rẽ vào có phải một hành lang thẳng dài hay không.

### 3. Kiểm tra ngõ cụt DFS(6) bị sai — [agent.py:248-264](../pacman/submissions/24880218/agent.py#L248-L264), [297](../pacman/submissions/24880218/agent.py#L297)

- **Câu hỏi sai:** "có một đường đi dài 6 ô" không có nghĩa là "có lối thoát". Một ngõ cụt dài từ 7 ô trở lên vẫn qua được kiểm tra.
  - Kiểm chứng trên map tự dựng có một ngõ cụt dài 7 ô ở cột 7, phía bên phải là một vòng lặp lớn. `_dfs(m, (2,7), 6, {(1,7),(2,7)})` trả về `True`. Ghost rẽ DOWN vào ngõ cụt và bị bắt ở bước 4, trong khi đi RIGHT thì vào được vòng lặp.
- **Lỗ hổng:** nước dự phòng `possible_move[0]` ở [dòng 302](../pacman/submissions/24880218/agent.py#L302) **không hề được kiểm tra** ngõ cụt.
- **Bỏ qua Pacman:** một "lối thoát" mà Pacman tới cửa ra trước thì không còn là lối thoát.

### 4. Tham lam 1 bước, không mô phỏng hai bên đi cùng lúc

Ghost so với vị trí Pacman **hiện tại**, trong khi Pacman đi cùng lượt. Ghost không biết vùng nào Pacman sẽ tới trước để chặn đầu (cắt đường).

### 5. Các điểm nhỏ

- Thứ tự UP/DOWN/LEFT/RIGHT cố định, nên Ghost luôn hành xử giống nhau trong cùng tình huống.
- Sau một lượt STAY, `previous_move = STAY`, nên mọi nước tiếp theo đều bị tính là "rẽ".
- Nếu chạy với `--capture-distance 3`, Ghost có thể bị bắt **xuyên tường** theo Manhattan, mà BFS không thấy điều này.

## Hướng mở rộng (từ rẻ đến mạnh)

### A. Sửa nhanh

- Không bao giờ STAY nếu còn nước đi. Khi mọi nước đều làm khoảng cách giảm, chọn nước giữ được "vùng an toàn" lớn nhất (xem mục B).
- Tìm ngõ cụt đúng cách: lặp lại việc bóc các ô chỉ có 1 ô kề, cho đến khi không còn ô nào như vậy. Những ô bị bóc nằm trên các nhánh cụt, chỉ nên vào khi Pacman còn rất xa.

### B. Đổi thước đo sang số lượt Pacman cần (giải quyết điểm yếu 1, 2, 4)

```python
def _pacman_time(self, m, start, speed=2):
    H, W = m.shape; T = {start: 0}; q = deque([start])
    while q:
        c = q.popleft()
        for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
            p = c
            for _ in range(speed):
                n = (p[0]+dr, p[1]+dc)
                if not (0 <= n[0] < H and 0 <= n[1] < W) or m[n] == 1: break
                p = n
                if p not in T: T[p] = T[c] + 1; q.append(p)
    return T
```

- Tính `Tp` cho Pacman và `Tg` (BFS thường) cho Ghost.
- Ô an toàn là ô Ghost tới trước Pacman với một khoảng dư cho bán kính bắt: `Tg[x] + 1 < Tp[x]`.
- Với mỗi nước đi, đếm số ô an toàn còn tới được và chọn nước cho con số lớn nhất. Hòa thì chọn nước có `Tp` lớn hơn.
- Cách này tự động tránh hành lang thẳng và nhánh mà Pacman chặn được đầu.

### C. Minimax có giới hạn độ sâu (theo Note.txt, nhưng sửa 2 chỗ)

- Mô hình đúng luật: Pacman có tới 8 nước (4 hướng × 1–2 ô) cộng STAY. Bắt khi Manhattan ≤ 1 **sau khi cả hai cùng đi**.
- Giá trị lá là **số bước sống sót**, không phải −∞. Khi mọi nhánh đều thua, Ghost chọn nhánh thua muộn nhất.
- Hàm đánh giá: thay khoảng cách BFS bằng `Tp`, và thay Mobility bằng kích thước vùng an toàn ở mục B.

### D. Giải bảng trước + mô hình hóa đối thủ (mạnh nhất)

- Map có khoảng 200 ô, tức khoảng 40 nghìn trạng thái. Có thể tính sẵn bảng `D[g,p]` = số bước sống sót tối ưu.
- Thời gian tính cần vector hóa bằng numpy, hoặc chia nhỏ ra qua nhiều lượt, vì mỗi bước chỉ được 1 giây. [agent_ai.py](../pacman/submissions/24880218/agent_ai.py) đang đi theo hướng này.
- Vì Pacman hoàn hảo luôn thắng, cách duy nhất để sống đủ 200 bước là **đoán kiểu Pacman** dựa trên lịch sử nước đi (tham lam Manhattan, BFS, …). Sau đó, trong các nước có `D` tốt, chọn nước dẫn tới vị trí mà kiểu Pacman đó bị kẹt.

## Phạm vi và giới hạn của review

- Các con số chỉ áp dụng cho map mặc định với tham số mặc định.
- "Pacman BFS" là đối thủ tự viết để test: mỗi lượt nó tìm đường ngắn nhất về số lượt theo luật tốc độ 2. Đây không phải đối thủ của người chấm.
- Script test và script giải trò chơi chạy trong thư mục tạm của phiên làm việc, chưa được lưu vào repo.
