# Tóm tắt các hàm NumPy thường dùng

Quy ước: `import numpy as np`

## 1. Tạo mảng

| Hàm | Mô tả |
|---|---|
| `np.array([1,2,3])` | Tạo mảng từ list/tuple |
| `np.zeros((2,3))`, `np.ones(...)`, `np.empty(...)` | Mảng toàn 0, toàn 1, hoặc chưa khởi tạo giá trị |
| `np.full((2,2), 7)` | Mảng toàn một giá trị |
| `np.eye(3)`, `np.identity(3)` | Ma trận đơn vị |
| `np.arange(0, 10, 2)` | Dãy số cách đều theo bước |
| `np.linspace(0, 1, 5)` | Chia đều N điểm trong khoảng |
| `np.zeros_like(a)`, `np.ones_like(a)` | Tạo mảng cùng kích thước với `a` |
| `np.meshgrid(x, y)` | Tạo lưới tọa độ |

## 2. Thông tin mảng (thuộc tính)

`a.shape`, `a.ndim`, `a.size`, `a.dtype`, `a.itemsize`, `a.T` (chuyển vị)

## 3. Thay đổi hình dạng

- `a.reshape(3, 4)`, `a.flatten()`, `a.ravel()`
- `np.transpose(a)`, `np.swapaxes(a, 0, 1)`
- `np.expand_dims(a, axis=0)`, `np.squeeze(a)`
- Nối mảng: `np.concatenate`, `np.stack`, `np.vstack`, `np.hstack`
- Tách mảng: `np.split`, `np.vsplit`, `np.hsplit`
- `np.tile`, `np.repeat`

## 4. Toán học theo phần tử

- Cơ bản: `np.add`, `np.subtract`, `np.multiply`, `np.divide`, `np.power`, `np.mod`
- `np.sqrt`, `np.exp`, `np.log`, `np.log10`, `np.abs`
- Lượng giác: `np.sin`, `np.cos`, `np.tan`, `np.arcsin`...
- Làm tròn: `np.round`, `np.floor`, `np.ceil`, `np.trunc`
- `np.clip(a, 0, 1)` – giới hạn giá trị trong khoảng

## 5. Thống kê

- `np.sum`, `np.prod`, `np.cumsum`, `np.cumprod`
- `np.mean`, `np.median`, `np.std`, `np.var`
- `np.min`, `np.max`, `np.argmin`, `np.argmax`
- `np.percentile`, `np.quantile`
- `np.corrcoef`, `np.cov`, `np.histogram`
- Phiên bản bỏ qua NaN: `np.nanmean`, `np.nansum`, `np.nanmax`...

Hầu hết đều nhận tham số `axis` (ví dụ `np.sum(a, axis=0)` cộng theo cột).

## 6. Đại số tuyến tính (`np.linalg`)

- `np.dot(a, b)`, `a @ b`, `np.matmul`, `np.inner`, `np.outer`, `np.cross`
- `np.linalg.inv` (nghịch đảo), `np.linalg.det` (định thức)
- `np.linalg.eig` (trị riêng), `np.linalg.svd`
- `np.linalg.solve(A, b)` (giải hệ phương trình), `np.linalg.norm`, `np.linalg.matrix_rank`

## 7. Logic, so sánh và tìm kiếm

- `np.where(cond, x, y)` – chọn giá trị theo điều kiện
- `np.any`, `np.all`, `np.isnan`, `np.isinf`, `np.isclose`, `np.allclose`
- `np.logical_and`, `np.logical_or`, `np.logical_not`
- `np.nonzero`, `np.argwhere`, `np.searchsorted`

## 8. Sắp xếp và tập hợp

- `np.sort`, `np.argsort`, `np.partition`
- `np.unique(a, return_counts=True)`
- `np.intersect1d`, `np.union1d`, `np.setdiff1d`, `np.isin`

## 9. Số ngẫu nhiên (`np.random`)

Cách khuyến nghị hiện nay là dùng Generator:

```python
rng = np.random.default_rng(42)
rng.random((2, 3))          # số thực [0, 1)
rng.integers(0, 10, 5)      # số nguyên
rng.normal(0, 1, 100)       # phân phối chuẩn
rng.choice([1, 2, 3], 2)    # chọn ngẫu nhiên
rng.shuffle(a)              # xáo trộn
```

## 10. Đọc/ghi file

- `np.save` / `np.load` (định dạng `.npy`), `np.savez` (nhiều mảng)
- `np.savetxt` / `np.loadtxt`, `np.genfromtxt` (file văn bản/CSV)

## 11. Khác

- `np.copy(a)` – sao chép thật (tránh dùng chung bộ nhớ như với view)
- `a.astype(np.float32)` – đổi kiểu dữ liệu
- `np.fft.fft` – biến đổi Fourier
- `np.polyfit`, `np.polyval` – khớp và tính đa thức
- `np.diff`, `np.gradient`, `np.interp`

## Ví dụ nhanh

```python
import numpy as np

a = np.arange(12).reshape(3, 4)
print(a.mean(axis=0))      # trung bình từng cột
print(np.where(a > 5, a, 0))
print(a @ a.T)             # nhân ma trận
```
