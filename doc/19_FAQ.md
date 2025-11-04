# FAQ（よくある質問）
**Frequently Asked Questions for Time Series Forecasting System**

---

## 📋 ドキュメント情報

| 項目 | 内容 |
|-----|------|
| **ドキュメントタイトル** | 時系列予測システム FAQ |
| **バージョン** | v1.0.0 |
| **作成日** | 2025-11-03 |
| **最終更新日** | 2025-11-03 |
| **対象読者** | 全ユーザー |

---

## 目次

1. [一般的な質問](#1-一般的な質問)
2. [インストールと環境設定](#2-インストールと環境設定)
3. [データ準備](#3-データ準備)
4. [モデル学習](#4-モデル学習)
5. [予測と評価](#5-予測と評価)
6. [パフォーマンス](#6-パフォーマンス)
7. [トラブルシューティング](#7-トラブルシューティング)
8. [ベストプラクティス](#8-ベストプラクティス)
9. [Tips & Tricks](#9-tips--tricks)

---

## 1. 一般的な質問

### Q1.1: このシステムは何ができますか？

**A**: 時系列予測システムは以下の機能を提供します：

- ✅ **自動モデル選択**: AutoNHITS、AutoLSTM、AutoGRUなど複数のモデル
- ✅ **ハイパーパラメータ探索**: OptunaまたはRayによる自動最適化
- ✅ **並列実行**: 複数モデルの同時学習
- ✅ **実験管理**: PostgreSQL + MLflow/W&Bによるトラッキング
- ✅ **バッチ予測**: 大規模データの効率的な予測
- ✅ **モデルレジストリ**: バージョン管理と本番デプロイ

---

### Q1.2: どのような時系列データに対応していますか?

**A**: 以下の形式をサポートしています：

| 頻度 | コード | 例 |
|------|--------|-----|
| **秒** | S | センサーデータ |
| **分** | T, min | トラフィックデータ |
| **時間** | H | 電力消費量 |
| **日** | D | 売上データ |
| **週** | W | 在庫データ |
| **月** | M, MS | 財務データ |
| **四半期** | Q, QS | 業績データ |
| **年** | Y, YS | 経済指標 |

**データ形式**:
```csv
unique_id,ds,y
series_1,2025-01-01,100.0
series_1,2025-01-02,102.5
```

---

### Q1.3: どのくらいのデータ量が必要ですか？

**A**: モデルと予測期間によって異なります：

| モデル | 最小データ点数 | 推奨データ点数 | 予測期間の目安 |
|--------|--------------|--------------|---------------|
| **AutoNHITS** | 2 × h | 10 × h | h ≤ データ点数 / 2 |
| **AutoLSTM** | 3 × h | 20 × h | h ≤ データ点数 / 3 |
| **AutoGRU** | 3 × h | 20 × h | h ≤ データ点数 / 3 |
| **AutoTCN** | 2 × h | 15 × h | h ≤ データ点数 / 2 |

**例**:
- 日次データで7日先を予測 (h=7): 最低14点、推奨70点以上
- 月次データで12ヶ月先を予測 (h=12): 最低24点、推奨120点以上

---

### Q1.4: GPU は必要ですか？

**A**: 必須ではありませんが、推奨します：

| 使用環境 | GPU | 学習時間（例）* | 推奨 |
|---------|-----|---------------|------|
| **開発・テスト** | 不要 | 5-10分 | CPU可 |
| **小規模運用** (< 100系列) | 不要 | 10-30分 | CPU可 |
| **中規模運用** (100-1000系列) | 推奨 | 30分-2時間 | GPU推奨 |
| **大規模運用** (> 1000系列) | 必須 | 2時間以上 | GPU必須 |

*単一モデル、100系列、365データ点の場合

**GPUの設定**:
```bash
# GPUを使用
nf-runner train --data data.csv --backend cuda

# CPUを使用
nf-runner train --data data.csv --backend cpu
```

---

### Q1.5: クラウド環境でも動作しますか？

**A**: はい、主要なクラウドプラットフォームで動作します：

| プラットフォーム | サポート | 推奨構成 |
|----------------|---------|---------|
| **AWS** | ✅ | EC2 (g4dn.xlarge) + RDS PostgreSQL |
| **Google Cloud** | ✅ | Compute Engine (n1-standard-4 + GPU) + Cloud SQL |
| **Azure** | ✅ | VM (NC6) + Azure Database for PostgreSQL |
| **オンプレミス** | ✅ | Ubuntu 20.04+, PostgreSQL 14+ |

---

## 2. インストールと環境設定

### Q2.1: インストールが失敗します

**A**: よくある原因と解決策：

#### 原因1: Pythonバージョンが古い
```bash
# バージョン確認
python --version  # 3.11以上が必要

# pyenvでアップグレード
pyenv install 3.11.6
pyenv local 3.11.6
```

#### 原因2: 依存関係の競合
```bash
# 仮想環境を作り直す
rm -rf .venv
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install nf-auto-runner
```

#### 原因3: PyTorchのインストールエラー
```bash
# CPU版を明示的にインストール
pip install torch --index-url https://download.pytorch.org/whl/cpu

# GPU版（CUDA 11.8）
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

---

### Q2.2: データベース接続ができません

**A**: 接続確認の手順：

```bash
# 1. PostgreSQLが起動しているか確認
sudo systemctl status postgresql

# 2. 接続テスト
psql -U postgres -h localhost -c "SELECT version();"

# 3. データベースが存在するか確認
psql -U postgres -l | grep ts_forecast

# 4. 環境変数を確認
echo $DATABASE_URL
# 期待値: postgresql://user:password@host:5432/dbname

# 5. 接続文字列のテスト
python -c "
from sqlalchemy import create_engine
engine = create_engine('$DATABASE_URL')
with engine.connect() as conn:
    print('✓ Connection successful')
"
```

**よくあるエラー**:
- `FATAL: role "postgres" does not exist` → ユーザーを作成
- `FATAL: database "ts_forecast" does not exist` → データベースを作成
- `FATAL: password authentication failed` → パスワードを確認

---

### Q2.3: どの環境変数が必須ですか？

**A**: 最小限の必須環境変数：

```bash
# 必須（データベース接続）
DATABASE_URL=postgresql://postgres:password@localhost:5432/ts_forecast

# 推奨（パス設定）
DATA_DIR=/path/to/data
MODEL_DIR=/path/to/models
OUTPUT_DIR=/path/to/outputs
LOG_DIR=/path/to/logs

# オプション（実行制御）
MAX_WORKERS=4
DEFAULT_BACKEND=cpu  # または cuda
```

**完全な例**（`.env`ファイル）:
```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/ts_forecast

# Paths
DATA_DIR=./data
MODEL_DIR=./models
OUTPUT_DIR=./outputs
LOG_DIR=./logs

# Execution
MAX_WORKERS=4
DEFAULT_BACKEND=cpu
DEFAULT_H=7
H_RATIO=0.8

# Tracking (オプション)
MLFLOW_TRACKING_URI=http://localhost:5000
ENABLE_WANDB=false

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

### Q2.4: Docker で実行できますか？

**A**: はい、Dockerをサポートしています：

```bash
# 1. イメージをビルド
docker build -t nf-auto-runner:latest .

# 2. Docker Composeで起動
docker-compose up -d

# 3. 学習実行
docker exec nf-runner nf-runner train \
  --data /data/sample.csv \
  --models AutoNHITS

# 4. ログ確認
docker logs nf-runner -f
```

**docker-compose.yml の例**:
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: ts_forecast
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  app:
    build: .
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/ts_forecast
    volumes:
      - ./data:/data
      - ./models:/models
      - ./outputs:/outputs
    command: python -m nf_auto_runner.app.main

volumes:
  postgres_data:
```

---

## 3. データ準備

### Q3.1: CSVファイルの必須列は何ですか？

**A**: 最小限の3列が必要です：

```csv
unique_id,ds,y
series_1,2025-01-01,100.0
series_1,2025-01-02,102.5
series_2,2025-01-01,200.0
series_2,2025-01-02,205.0
```

**列の説明**:
- `unique_id`: 時系列の識別子（文字列）
- `ds`: 日時（ISO 8601形式、例: `2025-01-01` または `2025-01-01 10:30:00`）
- `y`: 目的変数（数値）

**オプションの列**:
- `futr_*`: 将来の特徴量（予測時に必要）
- `hist_*`: 過去の説明変数（学習時のみ）
- `stat_*`: 静的特徴量（系列レベルの定数）

---

### Q3.2: 日時のフォーマットは？

**A**: 複数のフォーマットをサポートしています：

| フォーマット | 例 | 用途 |
|------------|-----|------|
| **ISO 8601** | `2025-01-01` | 日次データ |
| **ISO 8601 + 時刻** | `2025-01-01 10:30:00` | 時間データ |
| **UNIX timestamp** | `1704067200` | システム間連携 |
| **カスタム** | `01/01/2025` | 設定で指定 |

**推奨**: ISO 8601形式（`YYYY-MM-DD`）

**カスタムフォーマットの指定**:
```yaml
# conf/data.yaml
data:
  date_format: "%d/%m/%Y"  # 01/01/2025
```

---

### Q3.3: 欠損値はどう扱えばいいですか？

**A**: 欠損値の処理方法：

#### 方法1: 前処理で補完（推奨）
```python
import pandas as pd

# 前方埋め
df['y'] = df.groupby('unique_id')['y'].fillna(method='ffill')

# 線形補間
df['y'] = df.groupby('unique_id')['y'].interpolate()

# 平均値補完
df['y'] = df.groupby('unique_id')['y'].fillna(
    df.groupby('unique_id')['y'].transform('mean')
)
```

#### 方法2: システムの自動処理
```bash
# 欠損値処理を有効化
nf-runner train \
  --data data.csv \
  --handle-missing forward_fill  # または linear, mean, drop
```

#### 方法3: 検証で警告
```bash
# データ検証
nf-runner data validate --data data.csv

# 出力例：
# ⚠ Warning: 25 missing values detected in 'y' column
# Suggestion: Use forward fill or interpolation
```

---

### Q3.4: 複数の時系列を1つのファイルに入れられますか？

**A**: はい、`unique_id`で区別します：

```csv
unique_id,ds,y
tokyo,2025-01-01,100
tokyo,2025-01-02,105
tokyo,2025-01-03,110
osaka,2025-01-01,200
osaka,2025-01-02,210
osaka,2025-01-03,220
kyoto,2025-01-01,150
kyoto,2025-01-02,155
kyoto,2025-01-03,160
```

**利点**:
- 1回の実行で複数系列を学習
- 系列間で共通のモデルアーキテクチャ
- メモリ効率が良い

**注意点**:
- すべての系列は同じ頻度（日次、時間など）である必要がある
- 系列ごとに異なる長さは可能

---

### Q3.5: 外生変数はどう追加しますか？

**A**: 列名の接頭辞で種類を指定：

```csv
unique_id,ds,y,futr_temperature,hist_demand_lag,stat_region
series_1,2025-01-01,100,25.0,95,tokyo
series_1,2025-01-02,105,26.0,100,tokyo
```

**接頭辞の意味**:
- `futr_*`: **将来の特徴量**
  - 予測時点でも値が分かる（例: 気温予報、カレンダー情報）
  - 予測時に必須
  
- `hist_*`: **過去の説明変数**
  - 学習時のみ使用（例: 過去の需要、遅れ変数）
  - 予測時は不要
  
- `stat_*`: **静的特徴量**
  - 時系列全体で一定（例: 地域、カテゴリ）
  - 学習・予測の両方で使用

**使用例**:
```bash
nf-runner train \
  --data data_with_exog.csv \
  --exog-future temperature,holiday \
  --exog-historical demand_lag_1,demand_lag_2 \
  --exog-static region,category
```

---

## 4. モデル学習

### Q4.1: どのモデルを選べばいいですか？

**A**: データと用途に応じて選択：

| モデル | 特徴 | 適した用途 | 学習時間 |
|--------|------|-----------|---------|
| **AutoNHITS** | 高精度、効率的 | 一般的な時系列全般 | 中 |
| **AutoLSTM** | 長期依存関係 | 長期予測、複雑なパターン | 長 |
| **AutoGRU** | LSTMより高速 | 中期予測 | 中 |
| **AutoTCN** | 並列化可能 | 大規模データ、リアルタイム | 短 |
| **AutoPatchTST** | Transformer | 長期予測、複雑なパターン | 長 |

**推奨アプローチ**:
1. まず**AutoNHITS**で試す（バランスが良い）
2. 精度が不十分なら**AutoPatchTST**または**AutoLSTM**
3. 速度が必要なら**AutoTCN**

```bash
# 複数モデルで比較
nf-runner train \
  --data data.csv \
  --models AutoNHITS,AutoLSTM,AutoGRU,AutoTCN \
  --h 7

# 最良モデルを確認
nf-runner results best --metric mae
```

---

### Q4.2: 学習時間を短縮するには？

**A**: 以下の方法で高速化できます：

#### 方法1: 並列実行
```bash
nf-runner train \
  --data data.csv \
  --models AutoNHITS,AutoLSTM,AutoGRU \
  --max-workers 4  # CPUコア数に応じて調整
```

#### 方法2: max_stepsを減らす
```bash
nf-runner train \
  --data data.csv \
  --models AutoNHITS \
  --max-steps 500  # デフォルト: 1000
```

#### 方法3: データをサンプリング
```python
# 大規模データの場合、一部で実験
df_sample = df.sample(frac=0.1, random_state=42)
```

#### 方法4: GPUを使用
```bash
nf-runner train \
  --data data.csv \
  --models AutoNHITS \
  --backend cuda  # GPUがある場合
```

#### 方法5: Rayで分散実行
```bash
# Ray クラスタ起動
ray start --head

# Ray 並列実行
nf-runner train \
  --data data.csv \
  --models AutoNHITS,AutoLSTM \
  --backend ray \
  --max-workers 10
```

**効果の目安**（100モデル学習の場合）:
- CPUシリアル: 約10時間
- CPU並列（4コア）: 約3時間
- GPU並列: 約1時間
- Ray分散（10ノード）: 約30分

---

### Q4.3: ハイパーパラメータ探索はどうすればいいですか？

**A**: Optunaを使った自動探索を推奨：

```bash
# 基本的な探索
nf-runner train \
  --data data.csv \
  --models AutoNHITS \
  --search-alg optuna \
  --num-trials 50

# タイムアウトを設定
nf-runner train \
  --data data.csv \
  --models AutoNHITS \
  --search-alg optuna \
  --num-trials 100 \
  --timeout 3600  # 1時間
```

**探索空間のカスタマイズ**:
```yaml
# conf/hyperparameter.yaml
model:
  AutoNHITS:
    input_size: [7, 14, 21, 28]
    n_pool_kernel_size:
      - [2, 2, 2]
      - [4, 4, 4]
      - [8, 8, 8]
    max_steps: [500, 1000, 1500]
```

**探索結果の分析**:
```python
from nf_auto_runner import HyperparameterAnalyzer

analyzer = HyperparameterAnalyzer()
study = analyzer.load_study(study_name='optuna_study_001')

# 最適パラメータ
print(study.best_params)

# 重要度プロット
analyzer.plot_param_importances(
    save_path='./outputs/param_importance.png'
)
```

---

### Q4.4: 検証データのサイズはどうすればいいですか？

**A**: データ量と予測期間に応じて調整：

| データ点数 | 予測期間 (h) | 推奨検証サイズ |
|-----------|-------------|--------------|
| < 100 | 任意 | 0.2 (20%) |
| 100-500 | h < 50 | 0.2 (20%) |
| 100-500 | h ≥ 50 | 0.3 (30%) |
| > 500 | h < 50 | 0.15 (15%) |
| > 500 | h ≥ 50 | 0.2 (20%) |

**val_sizeの指定方法**:
```bash
# 比率で指定（推奨）
nf-runner train --data data.csv --val-size 0.2  # 20%

# 絶対数で指定
nf-runner train --data data.csv --val-size 50  # 50データ点

# hの倍数で指定
nf-runner train --data data.csv --val-size 24/h  # 24 × h

# 自動設定
nf-runner train --data data.csv --val-size auto  # システムが決定
```

---

### Q4.5: 学習が失敗する場合の対処法は？

**A**: エラーメッセージに応じて対処：

#### エラー1: `ValueError: input_size must be less than or equal to data length`
**原因**: データが短すぎる
**解決**:
```bash
# input_size を小さくする
nf-runner train --data data.csv --input-size 7  # デフォルト: 自動

# または h を小さくする
nf-runner train --data data.csv --h 3
```

#### エラー2: `RuntimeError: CUDA out of memory`
**原因**: GPU メモリ不足
**解決**:
```bash
# バッチサイズを小さく
nf-runner train --data data.csv --batch-size 32

# CPUに切り替え
nf-runner train --data data.csv --backend cpu
```

#### エラー3: `KeyError: 'unique_id'`
**原因**: 列名が不正
**解決**:
```python
# 列名を確認
df = pd.read_csv('data.csv')
print(df.columns)

# 列名を修正
df = df.rename(columns={'id': 'unique_id', 'date': 'ds', 'value': 'y'})
df.to_csv('data_fixed.csv', index=False)
```

---

## 5. 予測と評価

### Q5.1: 予測の実行方法は？

**A**: 3つの方法があります：

#### 方法1: モデルIDで予測
```bash
nf-runner predict \
  --model-id 123 \
  --data new_data.csv \
  --h 7
```

#### 方法2: モデルファイルで予測
```bash
nf-runner predict \
  --model ./outputs/models/AutoNHITS_20251103_120000.pkl \
  --data new_data.csv \
  --h 14
```

#### 方法3: Python APIで予測
```python
from nf_auto_runner import NeuralForecastRunner

# モデル読み込み
runner = NeuralForecastRunner.load_model(
    model_path='./outputs/models/AutoNHITS_*.pkl'
)

# 予測実行
forecasts = runner.predict(data, h=7)

# 結果保存
forecasts.to_csv('./outputs/predictions/forecast.csv', index=False)
```

---

### Q5.2: 予測精度はどう評価すればいいですか？

**A**: 複数のメトリクスで評価：

| メトリクス | 説明 | 推奨用途 | 計算式 |
|-----------|------|---------|--------|
| **MAE** | 平均絶対誤差 | 一般的 | `mean(\|y - ŷ\|)` |
| **RMSE** | 二乗平均平方根誤差 | 外れ値に敏感 | `sqrt(mean((y - ŷ)²))` |
| **MAPE** | 平均絶対パーセント誤差 | 相対誤差 | `mean(\|y - ŷ\| / \|y\|) × 100` |
| **sMAPE** | 対称MAPE | 相対誤差（改良版） | `mean(2 × \|y - ŷ\| / (\|y\| + \|ŷ\|)) × 100` |

**評価の実行**:
```bash
# すべてのメトリクスで評価
nf-runner evaluate \
  --run-id 456 \
  --data test_data.csv

# 特定のメトリクスのみ
nf-runner evaluate \
  --run-id 456 \
  --metrics mae,rmse,mape
```

**結果の解釈**:
- MAE < 10%: 優秀
- MAE 10-20%: 良好
- MAE 20-30%: 許容範囲
- MAE > 30%: 改善が必要

---

### Q5.3: 信頼区間はどう解釈すればいいですか？

**A**: 予測の不確実性を表します：

```csv
unique_id,ds,y_pred,y_pred_lower,y_pred_upper
series_1,2025-11-04,105.2,100.0,110.4
```

**解釈**:
- `y_pred`: 点予測（最も可能性が高い値）
- `y_pred_lower`: 信頼区間の下限（95%信頼区間）
- `y_pred_upper`: 信頼区間の上限（95%信頼区間）

**意味**:
- 95%の確率で実際の値が`[y_pred_lower, y_pred_upper]`の範囲内に入る
- 区間が狭い = 予測の確信度が高い
- 区間が広い = 予測の不確実性が高い

**可視化**:
```python
import matplotlib.pyplot as plt

plt.plot(forecasts['ds'], forecasts['y_pred'], label='Prediction')
plt.fill_between(
    forecasts['ds'],
    forecasts['y_pred_lower'],
    forecasts['y_pred_upper'],
    alpha=0.3,
    label='95% CI'
)
plt.legend()
plt.show()
```

---

### Q5.4: 過去のデータで予測精度を確認するには？

**A**: バックテストを実行：

```bash
# バックテスト（交差検証）
nf-runner backtest \
  --data data.csv \
  --models AutoNHITS \
  --h 7 \
  --n-folds 5  # 5分割交差検証
```

**手動でのバックテスト**:
```python
from sklearn.model_selection import TimeSeriesSplit

# データ分割
tscv = TimeSeriesSplit(n_splits=5)

results = []
for train_idx, test_idx in tscv.split(df):
    train = df.iloc[train_idx]
    test = df.iloc[test_idx]
    
    # 学習
    runner.fit(train)
    
    # 予測
    forecasts = runner.predict(train, h=len(test))
    
    # 評価
    mae = calculate_mae(test['y'], forecasts['y_pred'])
    results.append(mae)

print(f"Average MAE: {np.mean(results):.2f}")
```

---

## 6. パフォーマンス

### Q6.1: メモリ使用量を削減するには？

**A**: 以下の方法で削減できます：

#### 方法1: バッチサイズを小さく
```bash
nf-runner train \
  --data data.csv \
  --batch-size 32  # デフォルト: 128
```

#### 方法2: データ型を最適化
```python
# カテゴリ型を使用
df['unique_id'] = df['unique_id'].astype('category')

# float32を使用（float64の半分のメモリ）
df['y'] = df['y'].astype('float32')
```

#### 方法3: チャンク処理
```python
# 大規模データをチャンクで処理
for chunk in pd.read_csv('large.csv', chunksize=10000):
    process_chunk(chunk)
```

#### 方法4: 不要なデータを削除
```python
# 学習後にモデルから不要な情報を削除
runner.cleanup_model()

# Pythonのガベージコレクション
import gc
gc.collect()
```

---

### Q6.2: CPU使用率を上げるには？

**A**: 並列処理を活用：

```bash
# 並列実行数を増やす
nf-runner train \
  --data data.csv \
  --models AutoNHITS,AutoLSTM,AutoGRU,AutoTCN \
  --max-workers 8  # CPUコア数まで

# Ray で分散実行
ray start --head
nf-runner train \
  --data data.csv \
  --models AutoNHITS,AutoLSTM \
  --backend ray \
  --max-workers 16
```

---

### Q6.3: GPU使用率が低い場合の対処法は？

**A**: 以下を確認・調整：

#### 確認1: GPUが正しく認識されているか
```bash
# CUDA デバイス確認
python -c "import torch; print(torch.cuda.is_available())"

# GPU情報
nvidia-smi
```

#### 確認2: バックエンドがcudaになっているか
```bash
nf-runner train \
  --data data.csv \
  --backend cuda  # cpuではなくcuda
```

#### 調整1: バッチサイズを大きく
```bash
nf-runner train \
  --data data.csv \
  --batch-size 256  # デフォルト: 128
```

#### 調整2: num_workersを調整
```yaml
# conf/execution.yaml
execution:
  num_workers: 4  # データローダーのワーカー数
```

---

## 7. トラブルシューティング

### Q7.1: "loss is NaN" エラーが出ます

**A**: 学習の不安定性が原因です：

#### 解決策1: 学習率を下げる
```bash
nf-runner train \
  --data data.csv \
  --learning-rate 0.0001  # デフォルト: 0.001
```

#### 解決策2: データを正規化
```python
# 標準化
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
df['y_scaled'] = scaler.fit_transform(df[['y']])
```

#### 解決策3: グラデーションクリッピング
```yaml
# conf/model.yaml
model:
  gradient_clip_val: 1.0
```

---

### Q7.2: "Connection refused" エラーが出ます

**A**: データベースまたはサービスに接続できません：

#### PostgreSQLの場合
```bash
# PostgreSQL起動確認
sudo systemctl status postgresql

# 起動していない場合
sudo systemctl start postgresql

# 接続テスト
psql -U postgres -h localhost -c "SELECT 1;"
```

#### MLflowの場合
```bash
# MLflow サーバー起動
mlflow ui --port 5000

# バックグラウンドで起動
nohup mlflow ui --port 5000 &
```

#### Rayの場合
```bash
# Ray クラスタ起動
ray start --head

# 既存のクラスタに接続
ray start --address='ray://localhost:10001'
```

---

### Q7.3: 予測結果が不自然です

**A**: データやモデルの問題を確認：

#### 確認1: データに異常値がないか
```python
# 統計情報確認
print(df['y'].describe())

# 外れ値検出
Q1 = df['y'].quantile(0.25)
Q3 = df['y'].quantile(0.75)
IQR = Q3 - Q1
outliers = df[(df['y'] < Q1 - 1.5*IQR) | (df['y'] > Q3 + 1.5*IQR)]
print(f"Outliers: {len(outliers)}")
```

#### 確認2: 頻度が正しいか
```python
# 頻度推定
from pandas.tseries.frequencies import infer_freq
freq = infer_freq(df['ds'])
print(f"Inferred frequency: {freq}")
```

#### 確認3: モデルの過学習
```bash
# 検証データサイズを増やす
nf-runner train \
  --data data.csv \
  --val-size 0.3  # 30%

# Early stoppingを有効化
nf-runner train \
  --data data.csv \
  --early-stopping-patience 10
```

---

### Q7.4: ログが表示されません

**A**: ログレベルを調整：

```bash
# ログレベルを DEBUG に
nf-runner train \
  --data data.csv \
  --log-level DEBUG

# または環境変数で設定
export LOG_LEVEL=DEBUG
nf-runner train --data data.csv
```

**ログファイルの確認**:
```bash
# アプリケーションログ
tail -f ./logs/app.log

# 実行ログ
cat ./logs/run_<run_id>.log

# エラーログ
grep ERROR ./logs/*.log
```

---

## 8. ベストプラクティス

### Q8.1: 開発から本番への移行手順は？

**A**: 段階的に移行します：

#### ステップ1: 開発環境でプロトタイプ
```bash
# 小規模データでテスト
nf-runner train \
  --data sample_data.csv \
  --models AutoNHITS \
  --max-steps 500
```

#### ステップ2: ステージング環境で検証
```bash
# 本番相当のデータで検証
nf-runner train \
  --data full_data.csv \
  --models AutoNHITS,AutoLSTM \
  --val-size 0.2 \
  --save-model true
```

#### ステップ3: モデルの評価
```bash
# バックテスト
nf-runner backtest \
  --data historical_data.csv \
  --models AutoNHITS \
  --h 7 \
  --n-folds 5

# 評価
nf-runner evaluate \
  --run-id <run_id> \
  --data test_data.csv
```

#### ステップ4: 本番環境へデプロイ
```bash
# モデルを本番環境に昇格
nf-runner registry promote \
  --model-id <model_id> \
  --stage production

# 本番予測
nf-runner predict \
  --model-id <model_id> \
  --data latest_data.csv
```

---

### Q8.2: 再学習の頻度はどうすればいいですか？

**A**: データの性質に応じて決定：

| データ特性 | 推奨再学習頻度 | 理由 |
|----------|--------------|------|
| **安定的** (季節性のみ) | 月次〜四半期 | パターンの変化が遅い |
| **変動的** (トレンド変化) | 週次〜月次 | 定期的な更新が必要 |
| **不安定** (急変あり) | 日次〜週次 | 頻繁な更新が必要 |
| **イベント駆動** | イベント発生時 | 重要な変化に応じて |

**自動再学習の設定**:
```python
# ドリフト検出による自動再学習
from nf_auto_runner import DriftDetector

detector = DriftDetector()
has_drift = detector.detect(new_data)

if has_drift:
    print("Drift detected. Retraining model...")
    runner.fit(new_data)
```

---

### Q8.3: モデルのバージョン管理はどうすればいいですか？

**A**: MLflowを活用：

```bash
# MLflow有効化
export MLFLOW_TRACKING_URI=http://localhost:5000
nf-runner train \
  --data data.csv \
  --models AutoNHITS \
  --enable-mlflow

# MLflow UI で確認
mlflow ui --port 5000
```

**バージョニングの戦略**:
1. **実験単位**: 各実験にユニークなID
2. **モデル単位**: 各モデルにバージョン番号
3. **ステージ管理**: Staging → Production

```bash
# モデル登録
nf-runner registry register \
  --model-path ./models/AutoNHITS_*.pkl \
  --name AutoNHITS_v1

# ステージ変更
nf-runner registry promote \
  --model-name AutoNHITS_v1 \
  --stage production
```

---

### Q8.4: データの品質をどう保証すればいいですか？

**A**: 自動検証を導入：

```bash
# データ検証
nf-runner data validate \
  --data data.csv \
  --strict  # 厳格モード

# 検証項目:
# ✓ 必須列の存在
# ✓ データ型の正しさ
# ✓ 欠損値の有無
# ✓ 重複の有無
# ✓ 日時の連続性
# ✓ 外れ値の検出
```

**CI/CDパイプラインに組み込む**:
```yaml
# .github/workflows/data-validation.yml
name: Data Validation

on: [push]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Validate Data
        run: |
          nf-runner data validate --data data/latest.csv
```

---

## 9. Tips & Tricks

### Q9.1: 高速に実験を回すコツは？

**A**: 以下のテクニックを活用：

#### Tip 1: データをサンプリング
```python
# 開発時は小規模データで実験
df_dev = df.sample(frac=0.1, random_state=42)
```

#### Tip 2: max_stepsを削減
```bash
# 開発時は少ないステップで
nf-runner train --data data.csv --max-steps 100  # デフォルト: 1000
```

#### Tip 3: dry-runで確認
```bash
# 実行前に計画を確認
nf-runner train --data data.csv --dry-run
```

#### Tip 4: 設定ファイルを活用
```yaml
# conf/dev.yaml (開発用)
data:
  sample_frac: 0.1

execution:
  max_steps: 100
  max_workers: 2

# conf/prod.yaml (本番用)
data:
  sample_frac: 1.0

execution:
  max_steps: 1000
  max_workers: 8
```

---

### Q9.2: デバッグのコツは？

**A**: 段階的にデバッグ：

#### Tip 1: ログレベルを上げる
```bash
nf-runner train --data data.csv --log-level DEBUG
```

#### Tip 2: 最小限のデータでテスト
```python
# 1系列、少数データ点で確認
df_minimal = df[df['unique_id'] == 'series_1'].head(50)
```

#### Tip 3: Python デバッガーを使用
```python
import pdb

# デバッグポイント
pdb.set_trace()

# またはIPython
from IPython import embed
embed()
```

#### Tip 4: テストを書く
```python
# tests/test_data_loader.py
def test_load_csv_success():
    loader = DataLoader()
    result = loader.load_csv('sample.csv')
    assert result is not None
```

---

### Q9.3: 結果を見やすくするコツは？

**A**: 可視化ツールを活用：

#### Tip 1: MLflow UI
```bash
mlflow ui --port 5000
# http://localhost:5000 でアクセス
```

#### Tip 2: カスタムダッシュボード
```python
import matplotlib.pyplot as plt
import seaborn as sns

# モデル比較プロット
results = analyzer.load_experiment(experiment_id=123)
results_df = pd.DataFrame(results)

sns.barplot(data=results_df, x='model', y='mae')
plt.title('Model Comparison (MAE)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('./outputs/model_comparison.png')
```

#### Tip 3: Jupyter Notebook
```python
# notebooks/analysis.ipynb
from nf_auto_runner import NeuralForecastRunner

runner = NeuralForecastRunner.load_model(model_path='...')
forecasts = runner.predict(data, h=7)

# インタラクティブにプロット
import plotly.express as px
fig = px.line(forecasts, x='ds', y='y_pred')
fig.show()
```

---

### Q9.4: 効率的な設定管理のコツは？

**A**: Hydraを活用：

#### Tip 1: 設定を階層化
```
conf/
├── config.yaml           # メイン設定
├── data/
│   ├── small.yaml       # 小規模データ
│   ├── medium.yaml      # 中規模データ
│   └── large.yaml       # 大規模データ
├── model/
│   ├── fast.yaml        # 高速モデル
│   └── accurate.yaml    # 高精度モデル
└── experiment/
    ├── dev.yaml         # 開発用
    ├── staging.yaml     # ステージング用
    └── prod.yaml        # 本番用
```

#### Tip 2: コマンドラインで上書き
```bash
# 設定を動的に上書き
nf-runner train \
  --config-name config \
  data=large \
  model=accurate \
  execution.max_workers=8
```

#### Tip 3: 実験グループを作成
```yaml
# conf/config.yaml
defaults:
  - data: small
  - model: fast
  - experiment: dev

# グループ指定で一括変更
# nf-runner train --config-name config experiment=prod
```

---

### Q9.5: エラー回復のコツは？

**A**: 冪等性と中間保存を活用：

#### Tip 1: チェックポイントを保存
```yaml
# conf/execution.yaml
execution:
  save_checkpoint: true
  checkpoint_interval: 100  # 100ステップごと
```

#### Tip 2: 失敗時の再開
```bash
# 失敗したrunを再開
nf-runner train --resume-from <run_id>
```

#### Tip 3: 段階的な実行
```bash
# Phase 1: データ準備
nf-runner data prepare --data raw_data.csv --output prepared_data.csv

# Phase 2: 学習
nf-runner train --data prepared_data.csv
```

---

## ✨ まとめ

このFAQは時系列予測システムのよくある質問を網羅しています。

### 主要トピック

1. **一般的な質問**: システムの概要と対応範囲
2. **インストール**: 環境設定とトラブルシューティング
3. **データ準備**: 形式、欠損値、外生変数
4. **モデル学習**: 選択、最適化、高速化
5. **予測と評価**: 実行方法、精度評価、バックテスト
6. **パフォーマンス**: メモリ、CPU、GPU の最適化
7. **トラブルシューティング**: よくあるエラーと解決策
8. **ベストプラクティス**: 本番運用の推奨事項
9. **Tips & Tricks**: 効率的な開発手法

---

**更に質問がある場合は**:
- 📖 [クイックスタートガイド](./18_QUICKSTART.md)
- 📖 [詳細ドキュメント](./01_REQUIREMENTS_SPECIFICATION_DETAILED.md)
- 💬 [GitHub Discussions](https://github.com/your-org/nf-auto-runner/discussions)
- 💬 [Slack: #nf-auto-runner]()

---
**End of Document**
