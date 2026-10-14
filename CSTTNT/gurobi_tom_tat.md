# Tóm tắt các hàm Gurobi (gurobipy) thường dùng

Gurobi là bộ giải tối ưu (solver) thương mại cho quy hoạch tuyến tính (LP), quy hoạch nguyên hỗn hợp (MIP), quy hoạch toàn phương (QP/QCP/MIQP) và một số bài toán phi tuyến. Giao diện Python là `gurobipy`.

- Cài đặt: `pip install gurobipy` (kèm giấy phép giới hạn kích thước để thử nghiệm; mô hình lớn cần license, có license học thuật miễn phí)
- Import:

```python
import gurobipy as gp
from gurobipy import GRB
```

## Quy trình chung

1. Tạo mô hình: `m = gp.Model("ten")`
2. Thêm biến: `m.addVar()`, `m.addVars()`, `m.addMVar()`
3. Đặt hàm mục tiêu: `m.setObjective(expr, GRB.MAXIMIZE)`
4. Thêm ràng buộc: `m.addConstr()`, `m.addConstrs()`
5. Giải: `m.optimize()`
6. Kiểm tra trạng thái và đọc kết quả: `m.Status`, `x.X`, `m.ObjVal`

## 1. Môi trường và mô hình

| Hàm | Mô tả |
|---|---|
| `gp.Model("ten")` | Tạo mô hình mới |
| `gp.Env()` | Tạo môi trường riêng (đặt tham số, license) |
| `gp.Model(env=env)` | Tạo mô hình trong môi trường đã chọn |
| `m.update()` | Áp dụng các thay đổi đang chờ (thường tự động khi `optimize`) |
| `m.copy()` | Sao chép mô hình |
| `m.dispose()`, `env.dispose()` | Giải phóng tài nguyên |
| `gp.read("model.lp")` | Đọc mô hình từ file |

Nên dùng `with` để tự giải phóng tài nguyên:

```python
with gp.Env() as env, gp.Model(env=env) as m:
    ...
```

## 2. Biến quyết định

### Thêm biến
- `m.addVar(lb=0, ub=GRB.INFINITY, obj=0, vtype=GRB.CONTINUOUS, name="x")` – một biến
- `m.addVars(I, J, vtype=GRB.BINARY, name="x")` – nhiều biến theo chỉ số, trả về `tupledict`
- `m.addMVar(shape=(m, n), lb=0, name="X")` – biến dạng ma trận (giống NumPy)

### Kiểu biến (`vtype`)
| Hằng số | Kiểu |
|---|---|
| `GRB.CONTINUOUS` | Liên tục (mặc định) |
| `GRB.INTEGER` | Nguyên |
| `GRB.BINARY` | Nhị phân 0/1 |
| `GRB.SEMICONT` | Bán liên tục (0 hoặc trong [lb, ub]) |
| `GRB.SEMIINT` | Bán nguyên |

> Lưu ý: cận dưới mặc định là `lb=0`. Muốn biến nhận giá trị âm phải đặt `lb=-GRB.INFINITY`.

### Ví dụ
```python
x = m.addVar(vtype=GRB.INTEGER, name="x")
y = m.addVars(range(3), range(4), lb=0, name="y")      # y[i, j]
z = m.addMVar(10, vtype=GRB.BINARY, name="z")          # vector 10 biến
```

## 3. Biểu thức

- `gp.LinExpr()` – biểu thức tuyến tính; `gp.QuadExpr()` – biểu thức bậc hai
- `gp.quicksum(...)` – cộng nhanh, hiệu quả hơn `sum()` của Python
- Phương thức của `tupledict`:
  - `y.sum(i, '*')` – tổng theo một chỉ số (`'*'` là ký tự đại diện)
  - `y.prod(coeff)` – tổng có trọng số với dict hệ số
  - `y.select(i, '*')` – lấy danh sách biến phù hợp mẫu
- Với `MVar`: dùng toán tử NumPy như `A @ x`, `x.sum()`, `x @ Q @ x`

```python
expr = gp.quicksum(c[i] * x[i] for i in I)
expr2 = y.prod(cost)           # sum cost[i,j] * y[i,j]
```

## 4. Hàm mục tiêu

- `m.setObjective(expr, GRB.MINIMIZE)` hoặc `GRB.MAXIMIZE`
- `m.ModelSense = GRB.MAXIMIZE` – đổi chiều tối ưu
- Đa mục tiêu: `m.setObjectiveN(expr, index, priority=..., weight=..., name=...)`
- Mục tiêu tuyến tính từng khúc: `m.setPWLObj(var, xpts, ypts)`

## 5. Ràng buộc

### Ràng buộc tuyến tính và bậc hai
- `m.addConstr(expr <= rhs, name="c")` – một ràng buộc (dùng `<=`, `>=`, `==`)
- `m.addConstrs((expr_i <= b[i] for i in I), name="c")` – nhiều ràng buộc từ generator
- `m.addLConstr(lhs, sense, rhs)` – thêm ràng buộc tuyến tính nhanh
- `m.addQConstr(...)` – ràng buộc bậc hai
- Dạng ma trận: `m.addConstr(A @ x <= b)` với `x` là `MVar`
- `m.addRange(expr, lower, upper)` – ràng buộc dạng khoảng

```python
m.addConstrs((y.sum(i, '*') <= cap[i] for i in I), name="capacity")
m.addConstrs((y.sum('*', j) == demand[j] for j in J), name="demand")
```

### Ràng buộc tổng quát (general constraints)
| Hàm | Ý nghĩa |
|---|---|
| `m.addGenConstrMax(r, [x1, x2], constant)` | r = max(x1, x2, constant) |
| `m.addGenConstrMin(r, [x1, x2])` | r = min(...) |
| `m.addGenConstrAbs(r, x)` | r = \|x\| |
| `m.addGenConstrAnd(r, [b1, b2])` / `addGenConstrOr` | Phép logic trên biến nhị phân |
| `m.addGenConstrIndicator(b, 1, expr <= rhs)` | Nếu b = 1 thì ràng buộc phải thỏa |
| `m.addGenConstrPWL(x, y, xpts, ypts)` | y = hàm tuyến tính từng khúc của x |
| `m.addGenConstrExp`, `Log`, `Pow`, `Sin`, `Cos`... | Hàm phi tuyến (xấp xỉ hoặc giải toàn cục tùy phiên bản) |
| `m.addGenConstrNL(y, expr)` | Ràng buộc phi tuyến tổng quát (Gurobi 12 trở lên, dùng `gp.nlfunc`) |

Cú pháp rút gọn: `m.addConstr((b == 1) >> (x + y <= 10))` cho ràng buộc chỉ báo, `m.addConstr(r == gp.max_(x1, x2))`.

### Ràng buộc SOS
- `m.addSOS(GRB.SOS_TYPE1, vars, weights)` – tối đa một biến khác 0
- `GRB.SOS_TYPE2` – tối đa hai biến liên tiếp khác 0

## 6. Giải mô hình

- `m.optimize()` – giải
- `m.optimize(callback)` – giải kèm hàm callback
- `m.reset()` – xóa lời giải hiện có để giải lại từ đầu
- `m.terminate()` – dừng giải (thường gọi trong callback)
- `m.relax()` – tạo bản nới lỏng liên tục của mô hình MIP
- `m.presolve()` – trả về mô hình sau khi tiền xử lý
- `m.tune()` – tự động tìm bộ tham số tốt

## 7. Trạng thái lời giải (`m.Status`)

| Hằng số | Giá trị | Ý nghĩa |
|---|---|---|
| `GRB.OPTIMAL` | 2 | Tìm được lời giải tối ưu |
| `GRB.INFEASIBLE` | 3 | Vô nghiệm |
| `GRB.INF_OR_UNBD` | 4 | Vô nghiệm hoặc không bị chặn |
| `GRB.UNBOUNDED` | 5 | Không bị chặn |
| `GRB.TIME_LIMIT` | 9 | Hết thời gian |
| `GRB.NODE_LIMIT`, `GRB.SOLUTION_LIMIT` | 8, 10 | Đạt giới hạn nút / số lời giải |
| `GRB.INTERRUPTED` | 11 | Bị ngắt |
| `GRB.SUBOPTIMAL` | 13 | Lời giải chưa tối ưu |

Kiểm tra có lời giải khả thi hay chưa: `m.SolCount > 0`.

## 8. Thuộc tính (attributes) để đọc kết quả

### Mô hình
- `m.ObjVal` – giá trị mục tiêu tốt nhất
- `m.ObjBound` – cận tốt nhất (MIP)
- `m.MIPGap` – khoảng cách tối ưu tương đối
- `m.Runtime`, `m.NodeCount`, `m.IterCount`
- `m.NumVars`, `m.NumConstrs`, `m.NumIntVars`, `m.IsMIP`

### Biến
- `x.X` – giá trị lời giải
- `x.VarName`, `x.LB`, `x.UB`, `x.Obj`, `x.VType`
- `x.RC` – chi phí rút gọn (reduced cost, chỉ LP)
- `x.Start` – lời giải khởi tạo cho MIP (warm start)

### Ràng buộc
- `c.Pi` – giá đối ngẫu / giá bóng (shadow price, chỉ LP)
- `c.Slack` – độ dư
- `c.RHS`, `c.Sense`, `c.ConstrName`

### Phân tích độ nhạy (LP)
- `x.SAObjLow`, `x.SAObjUp` – khoảng hệ số mục tiêu giữ nguyên lời giải
- `c.SARHSLow`, `c.SARHSUp` – khoảng vế phải giữ nguyên cơ sở

### Đọc nhiều giá trị cùng lúc
- `m.getAttr("X", vars)` hoặc `m.getAttr(GRB.Attr.X, x)` với `tupledict`
- `x_mvar.X` – trả về mảng NumPy
- `m.getVars()`, `m.getConstrs()`, `m.getVarByName("x")`, `m.getConstrByName("c")`

```python
if m.Status == GRB.OPTIMAL:
    print("Mục tiêu:", m.ObjVal)
    for v in m.getVars():
        if v.X > 1e-6:
            print(v.VarName, v.X)
```

## 9. Tham số (parameters)

Đặt trước khi gọi `optimize()`: `m.Params.TimeLimit = 60` hoặc `m.setParam("TimeLimit", 60)`.

| Tham số | Ý nghĩa |
|---|---|
| `TimeLimit` | Giới hạn thời gian (giây) |
| `MIPGap` | Dừng khi gap tương đối nhỏ hơn giá trị này (mặc định 1e-4) |
| `MIPGapAbs` | Gap tuyệt đối |
| `OutputFlag` | 0 để tắt log |
| `LogFile` | Ghi log ra file |
| `Threads` | Số luồng sử dụng |
| `MIPFocus` | 1: tìm lời giải khả thi; 2: chứng minh tối ưu; 3: cải thiện cận |
| `Method` | Thuật toán LP: -1 tự động, 0 primal simplex, 1 dual simplex, 2 barrier |
| `Presolve` | Mức tiền xử lý (-1 đến 2) |
| `Heuristics` | Tỷ lệ thời gian dành cho heuristic |
| `Cuts` | Mức độ sinh mặt cắt |
| `SolutionLimit` | Dừng sau khi tìm đủ số lời giải |
| `NonConvex` | 2 để cho phép QP/QCP không lồi (mặc định đã bật từ Gurobi 11) |
| `PoolSearchMode`, `PoolSolutions` | Tìm nhiều lời giải |
| `Seed` | Hạt giống ngẫu nhiên |

## 10. Xử lý mô hình vô nghiệm

- `m.computeIIS()` – tìm tập ràng buộc mâu thuẫn tối thiểu (IIS)
- Sau đó `c.IISConstr`, `v.IISLB`, `v.IISUB` cho biết thành phần nào thuộc IIS
- `m.write("model.ilp")` – ghi IIS ra file để xem
- `m.feasRelaxS(...)` / `m.feasRelax(...)` – nới lỏng tối thiểu để mô hình khả thi

```python
if m.Status == GRB.INFEASIBLE:
    m.computeIIS()
    for c in m.getConstrs():
        if c.IISConstr:
            print("Mâu thuẫn:", c.ConstrName)
```

Nếu trạng thái là `INF_OR_UNBD`, đặt `m.Params.DualReductions = 0` rồi giải lại để biết chính xác.

## 11. Nhiều lời giải (solution pool)

- Đặt `PoolSearchMode = 2` và `PoolSolutions = 10` để tìm 10 lời giải tốt nhất
- `m.SolCount` – số lời giải tìm được
- Đặt `m.Params.SolutionNumber = k`, sau đó đọc `x.Xn` và `m.PoolObjVal`

## 12. Đa mục tiêu

```python
m.setObjectiveN(chi_phi, index=0, priority=2, name="ChiPhi")
m.setObjectiveN(thoi_gian, index=1, priority=1, weight=1.0, name="ThoiGian")
m.ModelSense = GRB.MINIMIZE
```

- Ưu tiên cao hơn được tối ưu trước (thứ tự từ điển); cùng ưu tiên thì cộng có trọng số
- `reltol`, `abstol` – độ suy giảm cho phép với mục tiêu ưu tiên cao
- Đọc giá trị: đặt `m.Params.ObjNumber = i`, rồi đọc `m.ObjNVal`

## 13. Callback

Dùng để theo dõi tiến trình hoặc thêm ràng buộc lười (lazy constraints) trong khi giải.

```python
def cb(model, where):
    if where == GRB.Callback.MIPSOL:
        vals = model.cbGetSolution(model._x)
        # nếu vi phạm điều kiện thì thêm ràng buộc
        # model.cbLazy(expr <= rhs)
    elif where == GRB.Callback.MIP:
        gap_info = model.cbGet(GRB.Callback.MIP_OBJBST)

m._x = x
m.Params.LazyConstraints = 1
m.optimize(cb)
```

Các điểm callback (`where`): `MIP`, `MIPSOL`, `MIPNODE`, `SIMPLEX`, `BARRIER`, `PRESOLVE`, `MESSAGE`.
Các hàm trong callback: `cbGet`, `cbGetSolution`, `cbGetNodeRel`, `cbLazy`, `cbCut`, `cbSetSolution`.

## 14. Đọc/ghi file

- `m.write("model.lp")` – định dạng LP, dễ đọc để kiểm tra mô hình
- `m.write("model.mps")` – định dạng MPS chuẩn
- `m.write("solution.sol")` – lời giải
- `m.write("params.prm")`, `m.read("params.prm")` – tham số
- `m.read("start.mst")` – lời giải khởi tạo
- `m.write("model.json")` – lời giải dạng JSON

## 15. Cấu trúc dữ liệu tiện ích

- `gp.multidict({...})` – tách dict thành danh sách khóa và nhiều dict giá trị
- `gp.tuplelist([...])` – danh sách tuple có `.select()` lọc nhanh
- `gp.tupledict` – dict chỉ số tuple, có `.sum()`, `.prod()`, `.select()`

```python
arcs, cost, cap = gp.multidict({
    ('A', 'B'): [4, 10],
    ('A', 'C'): [2, 5],
    ('B', 'C'): [1, 8],
})
```

Thư viện bổ trợ: `gurobipy-pandas` (xây mô hình trực tiếp từ DataFrame), `gurobi-optimods` (các mô hình mẫu có sẵn), `gurobi-machinelearning` (nhúng mô hình học máy vào ràng buộc).

## Ví dụ tổng hợp: bài toán vận tải

```python
import gurobipy as gp
from gurobipy import GRB

kho = {'K1': 100, 'K2': 150}                     # cung
khach = {'C1': 80, 'C2': 70, 'C3': 90}          # cầu
chi_phi = {('K1', 'C1'): 4, ('K1', 'C2'): 6, ('K1', 'C3'): 9,
           ('K2', 'C1'): 5, ('K2', 'C2'): 3, ('K2', 'C3'): 7}

with gp.Model("van_tai") as m:
    x = m.addVars(chi_phi.keys(), lb=0, name="x")

    m.setObjective(x.prod(chi_phi), GRB.MINIMIZE)

    m.addConstrs((x.sum(i, '*') <= kho[i] for i in kho), name="cung")
    m.addConstrs((x.sum('*', j) == khach[j] for j in khach), name="cau")

    m.Params.OutputFlag = 0
    m.optimize()

    if m.Status == GRB.OPTIMAL:
        print("Tổng chi phí:", m.ObjVal)
        for (i, j), v in x.items():
            if v.X > 1e-6:
                print(f"{i} -> {j}: {v.X:g}")
```
