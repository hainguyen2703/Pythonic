# Tóm tắt các hàm SciPy thường dùng

SciPy được xây dựng trên NumPy và chia thành nhiều module con. Thường import theo từng module:

```python
import numpy as np
from scipy import stats, optimize, integrate, interpolate, linalg, signal
```

## Tổng quan các module

| Module | Chức năng |
|---|---|
| `scipy.stats` | Thống kê, phân phối xác suất, kiểm định giả thuyết |
| `scipy.optimize` | Tối ưu hóa, tìm nghiệm, khớp đường cong |
| `scipy.integrate` | Tích phân, giải phương trình vi phân |
| `scipy.interpolate` | Nội suy |
| `scipy.linalg` | Đại số tuyến tính (mở rộng hơn `np.linalg`) |
| `scipy.signal` | Xử lý tín hiệu, bộ lọc |
| `scipy.fft` | Biến đổi Fourier |
| `scipy.sparse` | Ma trận thưa |
| `scipy.spatial` | Hình học không gian, khoảng cách, KD-tree |
| `scipy.cluster` | Phân cụm |
| `scipy.ndimage` | Xử lý ảnh N chiều |
| `scipy.special` | Hàm đặc biệt (gamma, beta, Bessel...) |
| `scipy.io` | Đọc/ghi file MATLAB, WAV... |
| `scipy.constants` | Hằng số vật lý và toán học |

## 1. Thống kê (`scipy.stats`)

### Thống kê mô tả
- `stats.describe(x)` – tóm tắt: số lượng, min/max, trung bình, phương sai, độ lệch, độ nhọn
- `stats.mode(x)`, `stats.skew(x)`, `stats.kurtosis(x)`
- `stats.zscore(x)` – chuẩn hóa z-score
- `stats.iqr(x)`, `stats.sem(x)` (sai số chuẩn của trung bình)
- `stats.trim_mean(x, 0.1)` – trung bình cắt bỏ 10% hai đầu

### Phân phối xác suất
Các phân phối thường gặp: `stats.norm`, `stats.t`, `stats.chi2`, `stats.f`, `stats.uniform`, `stats.expon`, `stats.binom`, `stats.poisson`, `stats.beta`, `stats.gamma`.

Các phương thức chung:

| Phương thức | Ý nghĩa |
|---|---|
| `.pdf(x)` / `.pmf(k)` | Hàm mật độ (liên tục) / hàm khối xác suất (rời rạc) |
| `.cdf(x)` | Hàm phân phối tích lũy P(X ≤ x) |
| `.sf(x)` | 1 − cdf, P(X > x) |
| `.ppf(q)` | Hàm phân vị (nghịch đảo cdf) |
| `.rvs(size=n)` | Sinh số ngẫu nhiên |
| `.fit(data)` | Ước lượng tham số từ dữ liệu |
| `.mean()`, `.var()`, `.std()`, `.interval(0.95)` | Đặc trưng của phân phối |

```python
stats.norm.cdf(1.96)               # ≈ 0.975
stats.norm.ppf(0.975)              # ≈ 1.96
stats.norm(loc=10, scale=2).rvs(5) # 5 số từ N(10, 2²)
```

### Kiểm định giả thuyết
| Hàm | Kiểm định |
|---|---|
| `stats.ttest_1samp(x, popmean)` | t-test một mẫu |
| `stats.ttest_ind(a, b)` | t-test hai mẫu độc lập (`equal_var=False` cho Welch) |
| `stats.ttest_rel(a, b)` | t-test mẫu cặp |
| `stats.f_oneway(a, b, c)` | ANOVA một yếu tố |
| `stats.chi2_contingency(table)` | Chi bình phương độc lập |
| `stats.chisquare(obs, exp)` | Chi bình phương phù hợp |
| `stats.shapiro(x)`, `stats.normaltest(x)` | Kiểm định phân phối chuẩn |
| `stats.kstest(x, 'norm')` | Kolmogorov–Smirnov |
| `stats.mannwhitneyu(a, b)` | Mann–Whitney U (phi tham số) |
| `stats.wilcoxon(a, b)` | Wilcoxon (mẫu cặp, phi tham số) |
| `stats.kruskal(a, b, c)` | Kruskal–Wallis |
| `stats.levene(a, b)` | Đồng nhất phương sai |

Kết quả trả về thường có `.statistic` và `.pvalue`.

### Tương quan và hồi quy
- `stats.pearsonr(x, y)`, `stats.spearmanr(x, y)`, `stats.kendalltau(x, y)`
- `stats.linregress(x, y)` – hồi quy tuyến tính đơn: `slope`, `intercept`, `rvalue`, `pvalue`, `stderr`

## 2. Tối ưu hóa (`scipy.optimize`)

- `optimize.minimize(f, x0, method='BFGS')` – cực tiểu hàm nhiều biến (method: `Nelder-Mead`, `BFGS`, `L-BFGS-B`, `SLSQP`...; hỗ trợ `bounds`, `constraints`)
- `optimize.minimize_scalar(f)` – cực tiểu hàm một biến
- `optimize.root(f, x0)` – tìm nghiệm hệ phương trình
- `optimize.root_scalar(f, bracket=[a, b])`, `optimize.brentq(f, a, b)` – nghiệm một biến
- `optimize.fsolve(f, x0)` – giải hệ phi tuyến
- `optimize.curve_fit(model, xdata, ydata)` – khớp đường cong, trả về tham số và ma trận hiệp phương sai
- `optimize.least_squares(residuals, x0)` – bình phương tối thiểu phi tuyến
- `optimize.linprog(c, A_ub, b_ub)` – quy hoạch tuyến tính
- `optimize.differential_evolution(f, bounds)` – tối ưu toàn cục

```python
f = lambda x: (x[0] - 1)**2 + (x[1] - 2)**2
res = optimize.minimize(f, x0=[0, 0])
print(res.x, res.fun)   # [1, 2], 0
```

## 3. Tích phân và phương trình vi phân (`scipy.integrate`)

- `integrate.quad(f, a, b)` – tích phân xác định một biến (trả về giá trị và sai số)
- `integrate.dblquad`, `integrate.tplquad`, `integrate.nquad` – tích phân bội
- `integrate.trapezoid(y, x)`, `integrate.simpson(y, x=x)` – tích phân từ dữ liệu rời rạc
- `integrate.cumulative_trapezoid(y, x)` – tích phân tích lũy
- `integrate.solve_ivp(fun, t_span, y0)` – giải bài toán giá trị ban đầu ODE (khuyến nghị)
- `integrate.odeint(func, y0, t)` – giao diện ODE cũ

```python
val, err = integrate.quad(np.sin, 0, np.pi)   # ≈ 2.0

sol = integrate.solve_ivp(lambda t, y: -0.5 * y, [0, 10], [1.0],
                          t_eval=np.linspace(0, 10, 50))
print(sol.t, sol.y)
```

## 4. Nội suy (`scipy.interpolate`)

- `interpolate.interp1d(x, y, kind='cubic')` – nội suy 1 chiều (API cũ, vẫn dùng được)
- `interpolate.CubicSpline(x, y)` – spline bậc ba
- `interpolate.make_interp_spline(x, y, k=3)` – B-spline
- `interpolate.PchipInterpolator(x, y)` – nội suy đơn điệu
- `interpolate.UnivariateSpline(x, y, s=...)` – spline làm trơn
- `interpolate.griddata(points, values, xi)` – nội suy dữ liệu tán xạ nhiều chiều
- `interpolate.RegularGridInterpolator((x, y), data)` – nội suy trên lưới đều

## 5. Đại số tuyến tính (`scipy.linalg`)

- `linalg.inv`, `linalg.det`, `linalg.norm`, `linalg.pinv` (giả nghịch đảo)
- `linalg.solve(A, b)` – giải hệ Ax = b
- `linalg.lstsq(A, b)` – bình phương tối thiểu
- Phân rã: `linalg.lu`, `linalg.qr`, `linalg.cholesky`, `linalg.svd`, `linalg.schur`
- Trị riêng: `linalg.eig`, `linalg.eigh` (ma trận đối xứng)
- Hàm ma trận: `linalg.expm` (mũ ma trận), `linalg.sqrtm`, `linalg.logm`

## 6. Xử lý tín hiệu (`scipy.signal`)

- Thiết kế bộ lọc: `signal.butter`, `signal.cheby1`, `signal.firwin`
- Áp dụng bộ lọc: `signal.filtfilt(b, a, x)` (không lệch pha), `signal.lfilter`, `signal.sosfilt`
- `signal.convolve`, `signal.correlate`
- `signal.find_peaks(x, height=..., distance=...)` – tìm đỉnh
- `signal.savgol_filter(x, window, polyorder)` – làm trơn Savitzky–Golay
- `signal.medfilt(x)` – lọc trung vị
- `signal.welch(x, fs)`, `signal.periodogram`, `signal.spectrogram` – phân tích phổ
- `signal.resample`, `signal.decimate`, `signal.detrend`

```python
b, a = signal.butter(4, 0.1)       # bộ lọc thông thấp bậc 4
y = signal.filtfilt(b, a, x)
peaks, _ = signal.find_peaks(y, height=0.5)
```

## 7. Biến đổi Fourier (`scipy.fft`)

- `fft.fft`, `fft.ifft`, `fft.rfft`, `fft.irfft`
- `fft.fft2`, `fft.fftn` – nhiều chiều
- `fft.fftfreq(n, d)`, `fft.rfftfreq(n, d)` – trục tần số
- `fft.fftshift` – dời tần số 0 vào giữa
- `fft.dct`, `fft.idct` – biến đổi cosin rời rạc

## 8. Ma trận thưa (`scipy.sparse`)

- Định dạng: `sparse.csr_matrix`, `sparse.csc_matrix`, `sparse.coo_matrix`, `sparse.lil_matrix` (bản mới: `csr_array`...)
- `sparse.eye`, `sparse.diags`, `sparse.random`
- `A.toarray()` – chuyển sang mảng dày
- `sparse.linalg.spsolve(A, b)` – giải hệ thưa
- `sparse.linalg.eigs`, `sparse.linalg.eigsh`, `sparse.linalg.svds`
- `sparse.csgraph.shortest_path`, `sparse.csgraph.connected_components` – thuật toán đồ thị

## 9. Không gian và khoảng cách (`scipy.spatial`)

- `spatial.distance.euclidean(u, v)`, `cosine`, `cityblock`, `hamming`...
- `spatial.distance.pdist(X)` – khoảng cách từng cặp; `squareform` chuyển sang ma trận
- `spatial.distance.cdist(XA, XB)` – khoảng cách giữa hai tập điểm
- `spatial.KDTree(points)` – `.query(x, k)` tìm k láng giềng gần nhất
- `spatial.ConvexHull`, `spatial.Delaunay`, `spatial.Voronoi`
- `spatial.transform.Rotation` – phép quay 3D

## 10. Phân cụm (`scipy.cluster`)

- `cluster.vq.kmeans2(data, k)` – K-means
- `cluster.hierarchy.linkage(X, method='ward')` – phân cụm phân cấp
- `cluster.hierarchy.fcluster(Z, t, criterion='maxclust')` – cắt cây thành cụm
- `cluster.hierarchy.dendrogram(Z)` – vẽ cây phân cấp

## 11. Xử lý ảnh (`scipy.ndimage`)

- `ndimage.gaussian_filter`, `ndimage.median_filter`, `ndimage.uniform_filter`
- `ndimage.sobel`, `ndimage.laplace` – phát hiện cạnh
- `ndimage.rotate`, `ndimage.zoom`, `ndimage.shift`
- `ndimage.label` – gán nhãn vùng liên thông
- `ndimage.binary_erosion`, `binary_dilation`, `binary_opening`, `binary_closing`
- `ndimage.center_of_mass`, `ndimage.distance_transform_edt`

## 12. Hàm đặc biệt (`scipy.special`)

- `special.gamma`, `special.gammaln`, `special.beta`
- `special.factorial(n)`, `special.comb(n, k)`, `special.perm(n, k)`
- `special.erf`, `special.erfc`
- `special.expit` (sigmoid), `special.logit`, `special.softmax`, `special.logsumexp`
- `special.jv` (Bessel), `special.legendre`

## 13. Đọc/ghi file (`scipy.io`)

- `io.loadmat('file.mat')`, `io.savemat('file.mat', {'a': a})` – file MATLAB
- `io.wavfile.read('a.wav')`, `io.wavfile.write('b.wav', rate, data)` – file âm thanh WAV
- `io.mmread`, `io.mmwrite` – Matrix Market

## 14. Hằng số (`scipy.constants`)

- `constants.pi`, `constants.c` (tốc độ ánh sáng), `constants.g` (gia tốc trọng trường)
- `constants.h` (Planck), `constants.k` (Boltzmann), `constants.N_A` (Avogadro)
- `constants.convert_temperature(100, 'Celsius', 'Kelvin')`

## Ví dụ tổng hợp

```python
import numpy as np
from scipy import stats, optimize

rng = np.random.default_rng(0)

# Kiểm định t hai nhóm
a = rng.normal(10, 2, 30)
b = rng.normal(11, 2, 30)
res = stats.ttest_ind(a, b)
print(f"t = {res.statistic:.3f}, p = {res.pvalue:.4f}")

# Khớp đường cong mũ
x = np.linspace(0, 4, 50)
y = 2.5 * np.exp(-1.3 * x) + rng.normal(0, 0.05, x.size)
model = lambda x, a, k: a * np.exp(-k * x)
params, cov = optimize.curve_fit(model, x, y)
print("a, k =", params)
```
