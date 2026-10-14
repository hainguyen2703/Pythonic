# Tóm tắt các hàm Pandas thường dùng

Quy ước: `import pandas as pd`

Hai cấu trúc dữ liệu chính:
- **Series**: mảng 1 chiều có nhãn (index)
- **DataFrame**: bảng 2 chiều gồm nhiều cột (mỗi cột là một Series)

## 1. Tạo dữ liệu

| Hàm | Mô tả |
|---|---|
| `pd.Series([1, 2, 3], index=['a','b','c'])` | Tạo Series |
| `pd.DataFrame({'A': [1,2], 'B': [3,4]})` | Tạo DataFrame từ dict |
| `pd.DataFrame(np_array, columns=[...])` | Tạo từ mảng NumPy |
| `pd.date_range('2026-01-01', periods=7, freq='D')` | Dãy ngày tháng |

## 2. Đọc/ghi file

| Đọc | Ghi | Định dạng |
|---|---|---|
| `pd.read_csv('file.csv')` | `df.to_csv('file.csv', index=False)` | CSV |
| `pd.read_excel('file.xlsx', sheet_name=0)` | `df.to_excel('file.xlsx')` | Excel |
| `pd.read_json('file.json')` | `df.to_json('file.json')` | JSON |
| `pd.read_sql(query, conn)` | `df.to_sql('table', conn)` | Cơ sở dữ liệu SQL |
| `pd.read_parquet('file.parquet')` | `df.to_parquet('file.parquet')` | Parquet |
| `pd.read_html(url)` | `df.to_html()` | Bảng HTML |

Tham số hay dùng của `read_csv`: `sep`, `header`, `usecols`, `dtype`, `parse_dates`, `encoding`, `nrows`.

## 3. Xem nhanh dữ liệu

- `df.head(5)`, `df.tail(5)`, `df.sample(5)`
- `df.shape`, `df.columns`, `df.index`, `df.dtypes`
- `df.info()` – kiểu dữ liệu, số giá trị khác null
- `df.describe()` – thống kê mô tả
- `df['col'].value_counts()`, `df['col'].unique()`, `df['col'].nunique()`

## 4. Chọn và lọc dữ liệu

- Chọn cột: `df['A']`, `df[['A', 'B']]`
- Theo nhãn: `df.loc[hàng, cột]`, ví dụ `df.loc[0:5, ['A', 'B']]`
- Theo vị trí: `df.iloc[0:5, 0:2]`
- Một ô: `df.at[0, 'A']`, `df.iat[0, 0]`
- Lọc theo điều kiện: `df[df['A'] > 10]`, `df[(df['A'] > 10) & (df['B'] == 'x')]`
- `df.query('A > 10 and B == "x"')`
- `df[df['col'].isin(['a', 'b'])]`, `df[df['col'].between(1, 5)]`

## 5. Xử lý dữ liệu thiếu

- `df.isna()` / `df.isnull()`, `df.notna()`
- `df.isna().sum()` – đếm giá trị thiếu theo cột
- `df.dropna()` (tham số `axis`, `how`, `subset`)
- `df.fillna(0)`, `df.fillna(df.mean(numeric_only=True))`
- `df.ffill()`, `df.bfill()` – điền theo giá trị trước/sau
- `df.interpolate()` – nội suy

## 6. Làm sạch và biến đổi

- Đổi tên: `df.rename(columns={'old': 'new'})`
- Xóa: `df.drop(columns=['A'])`, `df.drop(index=[0, 1])`
- Trùng lặp: `df.duplicated()`, `df.drop_duplicates()`
- Đổi kiểu: `df['A'].astype(int)`, `pd.to_numeric`, `pd.to_datetime`
- Thay giá trị: `df.replace({'old': 'new'})`
- Áp dụng hàm: `df['A'].apply(func)`, `df.apply(func, axis=1)`, `df['A'].map(dict_or_func)`
- Thêm cột: `df['C'] = df['A'] + df['B']`, `df.assign(C=lambda d: d.A * 2)`
- Chia nhóm giá trị: `pd.cut(df['tuoi'], bins=[0, 18, 60, 100])`, `pd.qcut`
- Mã hóa one-hot: `pd.get_dummies(df, columns=['col'])`

## 7. Sắp xếp và index

- `df.sort_values('A', ascending=False)`, `df.sort_values(['A', 'B'])`
- `df.sort_index()`
- `df.set_index('col')`, `df.reset_index(drop=True)`
- `df.nlargest(5, 'A')`, `df.nsmallest(5, 'A')`
- `df['A'].rank()`

## 8. Thống kê

- `df.sum()`, `df.mean()`, `df.median()`, `df.min()`, `df.max()`
- `df.std()`, `df.var()`, `df.count()`, `df.mode()`
- `df.cumsum()`, `df.pct_change()`, `df.diff()`
- `df.corr()`, `df.cov()`
- `df['A'].idxmax()`, `df['A'].idxmin()`

Hầu hết nhận tham số `axis` và `numeric_only=True`.

## 9. Nhóm và tổng hợp

```python
df.groupby('loai')['gia'].mean()
df.groupby(['loai', 'nam']).agg({'gia': 'mean', 'so_luong': 'sum'})
df.groupby('loai').agg(gia_tb=('gia', 'mean'), tong_sl=('so_luong', 'sum'))
df.groupby('loai')['gia'].transform('mean')   # giữ nguyên số dòng
```

- Bảng tổng hợp: `pd.pivot_table(df, values='gia', index='loai', columns='nam', aggfunc='mean')`
- Bảng chéo: `pd.crosstab(df['A'], df['B'])`

## 10. Định hình lại bảng

- `df.pivot(index=..., columns=..., values=...)` – dài → rộng
- `df.melt(id_vars=[...], value_vars=[...])` – rộng → dài
- `df.stack()`, `df.unstack()`
- `df.T` – chuyển vị
- `df.explode('col')` – tách list trong ô thành nhiều dòng

## 11. Gộp và nối bảng

- `pd.concat([df1, df2])` – nối theo dòng; `axis=1` nối theo cột
- `pd.merge(df1, df2, on='id', how='left')` – `how`: `inner`, `left`, `right`, `outer`
- `df1.join(df2, on='key')` – nối theo index

## 12. Chuỗi ký tự (`.str`)

- `df['ten'].str.lower()`, `.str.upper()`, `.str.strip()`
- `.str.contains('abc')`, `.str.startswith('a')`
- `.str.replace('a', 'b')`, `.str.split(',')`, `.str.len()`
- `.str.extract(r'(\d+)')` – trích bằng regex

## 13. Ngày giờ (`.dt`)

- `pd.to_datetime(df['ngay'])`
- `df['ngay'].dt.year`, `.dt.month`, `.dt.day`, `.dt.dayofweek`
- `df['ngay'].dt.strftime('%d/%m/%Y')`
- Chuỗi thời gian: `df.resample('M').sum()` (cần index là ngày giờ)
- Cửa sổ trượt: `df['A'].rolling(7).mean()`, `df['A'].expanding().sum()`
- `df['A'].shift(1)` – dịch dữ liệu

## 14. Vẽ biểu đồ nhanh (cần matplotlib)

- `df.plot()`, `df.plot(kind='bar')`, `df['A'].hist()`
- `df.plot.scatter(x='A', y='B')`, `df.boxplot()`

## Ví dụ nhanh

```python
import pandas as pd

df = pd.DataFrame({
    'loai': ['A', 'B', 'A', 'B', 'A'],
    'gia': [10, 20, 15, None, 30],
    'so_luong': [1, 2, 3, 4, 5],
})

df['gia'] = df['gia'].fillna(df['gia'].mean())
df['doanh_thu'] = df['gia'] * df['so_luong']

print(df[df['gia'] > 12])
print(df.groupby('loai')['doanh_thu'].sum())
print(df.sort_values('doanh_thu', ascending=False).head(3))
```
