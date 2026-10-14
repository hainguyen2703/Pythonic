# Tóm tắt các hàm Scikit-learn thường dùng

Cài đặt: `pip install scikit-learn` — import với tên `sklearn`.

## Nguyên lý chung (API thống nhất)

Mọi mô hình và bộ biến đổi trong scikit-learn dùng chung một bộ phương thức:

| Phương thức | Ý nghĩa |
|---|---|
| `.fit(X, y)` | Huấn luyện / học tham số từ dữ liệu |
| `.predict(X)` | Dự đoán nhãn hoặc giá trị |
| `.predict_proba(X)` | Dự đoán xác suất từng lớp (phân loại) |
| `.score(X, y)` | Đánh giá nhanh (accuracy cho phân loại, R² cho hồi quy) |
| `.transform(X)` | Biến đổi dữ liệu (tiền xử lý, giảm chiều) |
| `.fit_transform(X)` | Vừa học vừa biến đổi |
| `.get_params()`, `.set_params()` | Xem/đặt siêu tham số |

Quy ước: `X` là ma trận đặc trưng dạng (số mẫu, số đặc trưng), `y` là vector nhãn/mục tiêu.

## 1. Bộ dữ liệu mẫu (`sklearn.datasets`)

- Có sẵn: `load_iris()`, `load_digits()`, `load_wine()`, `load_breast_cancer()`, `load_diabetes()`
- Tải về: `fetch_california_housing()`, `fetch_openml('mnist_784')`, `fetch_20newsgroups()`
- Sinh dữ liệu: `make_classification()`, `make_regression()`, `make_blobs()`, `make_moons()`, `make_circles()`

```python
from sklearn.datasets import load_iris
X, y = load_iris(return_X_y=True)          # hoặc as_frame=True để nhận DataFrame
```

## 2. Chia dữ liệu (`sklearn.model_selection`)

- `train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)`
- `KFold(n_splits=5, shuffle=True)`, `StratifiedKFold`, `GroupKFold`
- `TimeSeriesSplit` – cho chuỗi thời gian
- `LeaveOneOut`, `ShuffleSplit`

## 3. Tiền xử lý (`sklearn.preprocessing`, `sklearn.impute`)

### Chuẩn hóa
| Lớp | Tác dụng |
|---|---|
| `StandardScaler` | Trung bình 0, độ lệch chuẩn 1 |
| `MinMaxScaler` | Đưa về khoảng [0, 1] |
| `RobustScaler` | Dùng trung vị và IQR, ít nhạy với ngoại lai |
| `MaxAbsScaler` | Chia cho giá trị tuyệt đối lớn nhất (hợp với dữ liệu thưa) |
| `Normalizer` | Chuẩn hóa từng mẫu về độ dài 1 |

### Mã hóa biến phân loại
- `OneHotEncoder(handle_unknown='ignore')` – one-hot
- `OrdinalEncoder` – mã hóa thứ tự cho đặc trưng
- `LabelEncoder` – mã hóa nhãn `y`
- `TargetEncoder` – mã hóa theo giá trị mục tiêu

### Biến đổi khác
- `PolynomialFeatures(degree=2)` – tạo đặc trưng đa thức
- `KBinsDiscretizer` – rời rạc hóa thành các khoảng
- `PowerTransformer`, `QuantileTransformer` – làm phân phối gần chuẩn
- `FunctionTransformer(np.log1p)` – áp hàm tùy ý

### Xử lý dữ liệu thiếu
- `SimpleImputer(strategy='mean')` – `mean`, `median`, `most_frequent`, `constant`
- `KNNImputer(n_neighbors=5)`
- `IterativeImputer` (cần `from sklearn.experimental import enable_iterative_imputer`)

> Lưu ý: chỉ `fit` bộ tiền xử lý trên tập train, rồi `transform` tập test, để tránh rò rỉ dữ liệu. Dùng `Pipeline` sẽ tự đảm bảo điều này.

## 4. Mô hình hồi quy

| Lớp | Module |
|---|---|
| `LinearRegression` | `linear_model` |
| `Ridge`, `Lasso`, `ElasticNet` | `linear_model` (có điều chuẩn) |
| `SGDRegressor` | `linear_model` |
| `DecisionTreeRegressor` | `tree` |
| `RandomForestRegressor`, `ExtraTreesRegressor` | `ensemble` |
| `GradientBoostingRegressor`, `HistGradientBoostingRegressor` | `ensemble` |
| `SVR` | `svm` |
| `KNeighborsRegressor` | `neighbors` |
| `MLPRegressor` | `neural_network` |

## 5. Mô hình phân loại

| Lớp | Module |
|---|---|
| `LogisticRegression` | `linear_model` |
| `SGDClassifier`, `RidgeClassifier` | `linear_model` |
| `DecisionTreeClassifier` | `tree` |
| `RandomForestClassifier`, `ExtraTreesClassifier` | `ensemble` |
| `GradientBoostingClassifier`, `HistGradientBoostingClassifier` | `ensemble` |
| `AdaBoostClassifier` | `ensemble` |
| `SVC`, `LinearSVC` | `svm` |
| `KNeighborsClassifier` | `neighbors` |
| `GaussianNB`, `MultinomialNB`, `BernoulliNB` | `naive_bayes` |
| `MLPClassifier` | `neural_network` |

Kết hợp nhiều mô hình: `VotingClassifier`, `StackingClassifier`, `BaggingClassifier` (và các bản `Regressor` tương ứng).

## 6. Phân cụm (`sklearn.cluster`)

- `KMeans(n_clusters=3)`, `MiniBatchKMeans`
- `DBSCAN(eps=0.5, min_samples=5)`, `HDBSCAN`
- `AgglomerativeClustering` – phân cụm phân cấp
- `SpectralClustering`, `MeanShift`, `Birch`
- `GaussianMixture` (module `mixture`) – mô hình hỗn hợp Gauss

Kết quả: `.labels_`, `.cluster_centers_` (KMeans), hoặc `.fit_predict(X)`.

## 7. Giảm chiều (`sklearn.decomposition`, `sklearn.manifold`)

- `PCA(n_components=2)` – thuộc tính `explained_variance_ratio_`
- `TruncatedSVD` – cho ma trận thưa (ví dụ văn bản)
- `NMF`, `FastICA`, `LatentDirichletAllocation`
- `TSNE(n_components=2)`, `Isomap`, `MDS` – chủ yếu để trực quan hóa
- `LinearDiscriminantAnalysis` (module `discriminant_analysis`) – giảm chiều có giám sát

## 8. Chọn đặc trưng (`sklearn.feature_selection`)

- `VarianceThreshold` – bỏ đặc trưng ít biến thiên
- `SelectKBest(f_classif, k=10)` – các hàm điểm: `f_classif`, `chi2`, `mutual_info_classif`, `f_regression`
- `RFE(estimator, n_features_to_select=5)`, `RFECV`
- `SelectFromModel(estimator)` – chọn theo `feature_importances_` hoặc hệ số
- `SequentialFeatureSelector`

## 9. Đánh giá mô hình (`sklearn.metrics`)

### Phân loại
- `accuracy_score`, `precision_score`, `recall_score`, `f1_score`
- `confusion_matrix`, `classification_report`
- `roc_auc_score`, `roc_curve`, `precision_recall_curve`, `average_precision_score`
- `log_loss`, `balanced_accuracy_score`, `matthews_corrcoef`
- Vẽ: `ConfusionMatrixDisplay.from_estimator(...)`, `RocCurveDisplay.from_estimator(...)`

### Hồi quy
- `mean_squared_error`, `root_mean_squared_error`, `mean_absolute_error`
- `r2_score`, `mean_absolute_percentage_error`, `median_absolute_error`

### Phân cụm
- Không có nhãn: `silhouette_score`, `calinski_harabasz_score`, `davies_bouldin_score`
- Có nhãn thật: `adjusted_rand_score`, `normalized_mutual_info_score`

## 10. Kiểm định chéo và tinh chỉnh siêu tham số

- `cross_val_score(model, X, y, cv=5, scoring='accuracy')`
- `cross_validate(...)` – trả về nhiều chỉ số cùng lúc
- `cross_val_predict(...)` – dự đoán ngoài mẫu cho từng điểm
- `GridSearchCV(model, param_grid, cv=5)` – thử mọi tổ hợp
- `RandomizedSearchCV(model, param_distributions, n_iter=50)` – thử ngẫu nhiên
- `HalvingGridSearchCV` (cần `enable_halving_search_cv`)
- `learning_curve`, `validation_curve` – chẩn đoán overfit/underfit

Sau khi tìm: `.best_params_`, `.best_score_`, `.best_estimator_`, `.cv_results_`.

## 11. Pipeline và xử lý theo cột (`sklearn.pipeline`, `sklearn.compose`)

- `Pipeline([('scaler', StandardScaler()), ('clf', LogisticRegression())])`
- `make_pipeline(StandardScaler(), LogisticRegression())` – tự đặt tên bước
- `ColumnTransformer` / `make_column_transformer` – xử lý khác nhau cho cột số và cột phân loại
- `make_column_selector(dtype_include='number')` – chọn cột theo kiểu
- `FeatureUnion` – ghép kết quả nhiều bộ biến đổi
- `TransformedTargetRegressor` – biến đổi cả biến mục tiêu `y`

Đặt siêu tham số trong pipeline theo cú pháp `tênbước__thamsố`, ví dụ `{'clf__C': [0.1, 1, 10]}`.

## 12. Xử lý văn bản (`sklearn.feature_extraction.text`)

- `CountVectorizer` – túi từ (bag of words)
- `TfidfVectorizer(ngram_range=(1, 2), max_features=5000)` – TF-IDF
- `HashingVectorizer` – không lưu từ điển, tiết kiệm bộ nhớ
- `DictVectorizer` (module `feature_extraction`) – từ list dict sang ma trận

## 13. Diễn giải mô hình (`sklearn.inspection`)

- `model.feature_importances_` (mô hình cây), `model.coef_` (mô hình tuyến tính)
- `permutation_importance(model, X, y)` – độ quan trọng theo hoán vị
- `PartialDependenceDisplay.from_estimator(model, X, features)` – biểu đồ phụ thuộc riêng phần
- `DecisionBoundaryDisplay.from_estimator(...)` – vẽ biên quyết định
- `tree.plot_tree(model)`, `tree.export_text(model)` – xem cây quyết định

## 14. Tiện ích khác

- Lưu/tải mô hình: `joblib.dump(model, 'model.joblib')`, `joblib.load('model.joblib')`
- `sklearn.utils.shuffle`, `sklearn.utils.resample`
- `sklearn.utils.class_weight.compute_class_weight` – cân bằng lớp (hoặc dùng `class_weight='balanced'` trong mô hình)
- `sklearn.set_config(transform_output='pandas')` – để transformer trả về DataFrame
- `sklearn.calibration.CalibratedClassifierCV` – hiệu chỉnh xác suất
- `sklearn.dummy.DummyClassifier`, `DummyRegressor` – mô hình cơ sở để so sánh

## Ví dụ tổng hợp

```python
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# df: DataFrame có cột số, cột phân loại và cột nhãn 'target'
X = df.drop(columns='target')
y = df['target']

num_cols = X.select_dtypes('number').columns
cat_cols = X.select_dtypes(exclude='number').columns

preprocess = ColumnTransformer([
    ('num', Pipeline([('impute', SimpleImputer(strategy='median')),
                      ('scale', StandardScaler())]), num_cols),
    ('cat', Pipeline([('impute', SimpleImputer(strategy='most_frequent')),
                      ('onehot', OneHotEncoder(handle_unknown='ignore'))]), cat_cols),
])

pipe = Pipeline([('prep', preprocess),
                 ('clf', RandomForestClassifier(random_state=42))])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42)

grid = GridSearchCV(pipe,
                    {'clf__n_estimators': [100, 300],
                     'clf__max_depth': [None, 10]},
                    cv=5, scoring='f1_macro')
grid.fit(X_train, y_train)

print(grid.best_params_)
print(classification_report(y_test, grid.predict(X_test)))
```
