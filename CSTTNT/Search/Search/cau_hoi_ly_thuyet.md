**So sánh BFS và DFS trên đồ thị vô hạn hoặc rất lớn**

Ký hiệu: *b* là số nhánh (số đỉnh kề trung bình), *d* là độ sâu của lời giải nông nhất, *m* là độ sâu tối đa của đồ thị (có thể là ∞).

| Tiêu chí | BFS | DFS |
|---|---|---|
| Tính đầy đủ (chắc chắn tìm được lời giải nếu có) | **Có**, miễn là *b* hữu hạn | **Không**: có thể đi mãi vào một nhánh vô hạn |
| Tính tối ưu | Tối ưu theo **số cạnh** (mọi cạnh có chi phí bằng nhau) | Không tối ưu: trả về đường đi tìm thấy đầu tiên, có thể rất dài |
| Thời gian | O(b^d) | O(b^m), với *m* = ∞ thì không có giới hạn |
| Bộ nhớ | O(b^d): phải lưu toàn bộ một tầng | O(b·m): chỉ lưu đường đi hiện tại và các nhánh anh em |

**BFS**
- *Ưu điểm:*
  - Duyệt theo từng tầng nên luôn tìm thấy lời giải nông nhất. Trên đồ thị vô hạn, BFS vẫn chắc chắn dừng nếu có lời giải ở độ sâu hữu hạn.
  - Khi lời giải nằm gần đỉnh xuất phát, BFS tìm thấy nhanh mà không phải đi lạc vào các nhánh sâu.
- *Nhược điểm:*
  - **Tốn bộ nhớ.** Queue phải chứa toàn bộ biên của tầng hiện tại, tăng theo cấp số mũ *b^d*. Trên đồ thị rất lớn, BFS thường hết bộ nhớ trước khi hết thời gian.
  - Nếu lời giải nằm rất sâu, BFS phải duyệt hết mọi tầng phía trên.

**DFS**
- *Ưu điểm:*
  - **Tiết kiệm bộ nhớ.** Bộ nhớ chỉ tăng tuyến tính theo độ sâu, O(b·m), nên DFS dùng được trên đồ thị rất lớn mà BFS không chạy nổi.
  - Có thể tìm ra lời giải rất nhanh nếu "đoán đúng" nhánh, hoặc khi đồ thị có nhiều lời giải nằm sâu.
- *Nhược điểm:*
  - **Không đầy đủ trên đồ thị vô hạn.** Nếu đi vào một nhánh vô hạn không chứa đích, DFS không bao giờ quay lại, dù đích có thể nằm ngay ở nhánh bên cạnh.
  - **Không tối ưu.** Đường đi tìm được có thể dài hơn rất nhiều so với đường ngắn nhất.
  - Nếu đánh dấu đỉnh đã thăm (graph search), tập `visited` cũng tăng theo số đỉnh đã duyệt. Khi đó lợi thế bộ nhớ của DFS giảm đi trên đồ thị rất lớn.

**Minh họa từ bài lab (`graph.txt`, 1000 đỉnh):** BFS tìm được đường `[0, 1, 296, 999]` chỉ gồm 4 đỉnh. DFS đi theo nhánh có chỉ số nhỏ trước và trả về một đường dài 1000 đỉnh, tức là đi qua gần như toàn bộ đồ thị trước khi tới đích. Điều này cho thấy rõ DFS không tối ưu.

**Kết luận:**
- Nên dùng **BFS** khi cần đường đi ngắn nhất, lời giải nằm nông và đủ bộ nhớ.
- Nên dùng **DFS** khi bộ nhớ hạn chế và đồ thị có độ sâu hữu hạn.
- Với đồ thị vô hạn hoặc rất lớn, giải pháp thường dùng là **Iterative Deepening DFS (IDS)**. IDS chạy DFS với giới hạn độ sâu tăng dần 0, 1, 2, ... Nhờ vậy nó vừa đầy đủ và tối ưu như BFS (khi chi phí các cạnh bằng nhau), vừa chỉ tốn bộ nhớ O(b·d) như DFS. Thời gian vẫn là O(b^d), vì các tầng nông bị duyệt lại nhưng chiếm tỉ lệ nhỏ.
