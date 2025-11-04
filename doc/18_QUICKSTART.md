# クイックスタートガイド
**Quick Start Guide for Time Series Forecasting System**

---

## 📋 ドキュメント情報

| 項目 | 内容 |
|-----|------|
| **ドキュメントタイトル** | 時系列予測システム クイックスタートガイド |
| **バージョン** | v1.0.0 |
| **作成日** | 2025-11-03 |
| **対象読者** | 初心者、データサイエンティスト、MLエンジニア |
| **所要時間** | 約30分 |

---

## 目次

1. [5分で始める](#1-5分で始める)
2. [最小構成での動作確認](#2-最小構成での動作確認)
3. [サンプルデータ](#3-サンプルデータ)
4. [基本的な使い方](#4-基本的な使い方)
5. [チュートリアル](#5-チュートリアル)
6. [次のステップ](#6-次のステップ)
7. [トラブルシューティング](#7-トラブルシューティング)

---

## 1. 5分で始める

### 1.1 前提条件

- **Python**: 3.11以上
- **OS**: Linux/macOS/Windows
- **メモリ**: 最低4GB（推奨8GB以上）
- **ディスク**: 最低5GB

---

### 1.2 インストール

#### 方法1: pipでインストール（推奨）

```bash
# 仮想環境作成
python3.11 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# パッケージインストール
pip install --upgrade pip
pip install nf-auto-runner

# インストール確認
nf-runner --version
```

---

#### 方法2: ソースからインストール

```bash
# リポジトリクローン
git clone https://github.com/your-org/nf-auto-runner.git
cd nf-auto-runner

# 仮想環境作成
python3.11 -m venv .venv
source .venv/bin/activate

# 開発モードでインストール
pip install -e .

# 依存関係インストール
pip install -r requirements.txt
```

---

### 1.3 最小限の環境変数設定

```bash
# .envファイル作成
cat > .env << 'EOF'
# 必須設定
DATABASE_URL=postgresql://postgres:password@localhost:5432/ts_forecast

# データパス（サンプルデータ用）
DATA_DIR=./data
MODEL_DIR=./models
OUTPUT_DIR=./outputs
LOG_DIR=./logs
EOF

# 環境変数読み込み
source .env  # または export $(cat .env | xargs)
```

---

### 1.4 データベース初期化

```bash
# PostgreSQL起動（Dockerを使用）
docker-compose up -d postgres

# または、ローカルPostgreSQLの場合
sudo systemctl start postgresql

# データベース作成
createdb ts_forecast

# マイグレーション実行
nf-runner db init
nf-runner db migrate
```

---

### 1.5 動作確認

```bash
# ヘルプ表示
nf-runner --help

# バージョン確認
nf-runner --version

# 利用可能なモデル一覧
nf-runner models list

# 設定確認
nf-runner config show
```

**期待される出力**:
```
NF Auto Runner v1.0.0
Available models: AutoNHITS, AutoLSTM, AutoGRU, AutoTCN, ...
Configuration loaded successfully ✓
```

---

## 2. 最小構成での動作確認

### 2.1 サンプルデータの準備

```bash
# サンプルデータ生成スクリプトを実行
nf-runner data generate \
  --output ./data/sample.csv \
  --n-series 10 \
  --n-points 365 \
  --freq D

# データ確認
head -20 ./data/sample.csv
```

**生成されるデータ形式**:
```csv
unique_id,ds,y
series_0,2025-01-01,100.5
series_0,2025-01-02,102.3
series_0,2025-01-03,101.8
...
```

---

### 2.2 最小限の学習実行

```bash
# 単一モデルで学習（約3分）
nf-runner train \
  --data ./data/sample.csv \
  --models AutoNHITS \
  --h 7 \
  --val-size 0.2

# または、設定ファイルを使用
nf-runner train --config ./conf/quickstart.yaml
```

**quickstart.yaml** の例:
```yaml
# conf/quickstart.yaml
data:
  data_path: ./data/sample.csv
  unique_id_column: unique_id
  time_column: ds
  target_column: y

execution:
  h: 7
  val_size: 0.2
  max_workers: 2

model_selection:
  models:
    - AutoNHITS
  backend: cpu
```

---

### 2.3 出力確認

```bash
# 学習結果の確認
ls -lh ./outputs/

# ディレクトリ構造
./outputs/
├── models/              # 保存されたモデル
│   └── AutoNHITS_*.pkl
├── predictions/         # 予測結果
│   └── predictions_*.csv
├── metrics/            # 評価メトリクス
│   └── metrics_*.json
└── logs/               # ログファイル
    └── run_*.log
```

---

### 2.4 予測実行

```bash
# 保存したモデルで予測
nf-runner predict \
  --model ./outputs/models/AutoNHITS_*.pkl \
  --data ./data/sample.csv \
  --h 7 \
  --output ./outputs/predictions/

# 予測結果確認
head ./outputs/predictions/predictions_*.csv
```

**予測結果の形式**:
```csv
unique_id,ds,y_pred,y_pred_lower,y_pred_upper
series_0,2025-11-04,105.2,100.0,110.4
series_0,2025-11-05,106.1,100.8,111.4
...
```

---

## 3. サンプルデータ

### 3.1 内蔵サンプルデータ

システムには複数のサンプルデータセットが用意されています：

```bash
# 利用可能なサンプルデータ一覧
nf-runner data list-samples

# サンプルデータをダウンロード
nf-runner data download \
  --sample air-passengers \
  --output ./data/air_passengers.csv
```

**利用可能なサンプル**:

| データセット | 説明 | 系列数 | データ点数 | 頻度 |
|------------|------|--------|-----------|-----|
| `air-passengers` | 航空旅客数 | 1 | 144 | M（月次） |
| `electricity` | 電力消費量 | 370 | 26,304 | H（時間） |
| `tourism` | 観光客数 | 366 | 2,928 | M（月次） |
| `m4-hourly` | M4コンペ（時間） | 414 | 700-960 | H（時間） |
| `m4-daily` | M4コンペ（日次） | 4,227 | 93-9,919 | D（日次） |

---

### 3.2 カスタムデータの準備

#### 3.2.1 必須フォーマット

**最小限の列**:
```csv
unique_id,ds,y
series_1,2025-01-01,100.0
series_1,2025-01-02,102.5
series_2,2025-01-01,200.0
series_2,2025-01-02,205.0
```

**列の説明**:
- `unique_id`: 時系列の識別子（文字列）
- `ds`: 日時（ISO 8601形式またはYYYY-MM-DD）
- `y`: 目的変数（数値）

---

#### 3.2.2 外生変数を含むデータ

```csv
unique_id,ds,y,futr_exog_1,hist_exog_1,stat_exog_1
series_1,2025-01-01,100.0,25.0,10.5,A
series_1,2025-01-02,102.5,26.0,11.0,A
```

**外生変数の命名規則**:
- `futr_*`: 将来の特徴量（予測時に必要）
- `hist_*`: 過去の説明変数（学習時のみ）
- `stat_*`: 静的特徴量（系列レベルの定数）

---

#### 3.2.3 データ検証

```bash
# データの妥当性チェック
nf-runner data validate --data ./data/your_data.csv

# データ統計情報表示
nf-runner data stats --data ./data/your_data.csv
```

**出力例**:
```
✓ Data validation passed
- Total rows: 3,650
- Unique series: 10
- Date range: 2025-01-01 to 2025-12-31
- Missing values: 0
- Frequency: D (Daily)
- Target column: y (mean=250.5, std=50.2)
```

---

## 4. 基本的な使い方

### 4.1 コマンドライン（CLI）

#### 4.1.1 基本的な学習コマンド

```bash
# シンプルな学習
nf-runner train \
  --data ./data/sample.csv \
  --models AutoNHITS \
  --h 7

# 複数モデルで学習
nf-runner train \
  --data ./data/sample.csv \
  --models AutoNHITS,AutoLSTM,AutoGRU \
  --h 7 \
  --val-size 0.2 \
  --max-workers 4

# ハイパーパラメータ探索
nf-runner train \
  --data ./data/sample.csv \
  --models AutoNHITS \
  --search-alg optuna \
  --num-trials 20 \
  --h 7
```

---

#### 4.1.2 予測コマンド

```bash
# モデルIDで予測
nf-runner predict \
  --model-id 123 \
  --data ./data/new_data.csv \
  --h 14

# モデルファイルで予測
nf-runner predict \
  --model ./outputs/models/AutoNHITS_*.pkl \
  --data ./data/new_data.csv \
  --h 14 \
  --output ./outputs/predictions/
```

---

#### 4.1.3 評価コマンド

```bash
# 学習したモデルを評価
nf-runner evaluate \
  --run-id 456 \
  --data ./data/test_data.csv

# カスタムメトリクスで評価
nf-runner evaluate \
  --run-id 456 \
  --metrics mae,rmse,mape,smape
```

---

### 4.2 Python API

#### 4.2.1 基本的な使い方

```python
from nf_auto_runner import NeuralForecastRunner
import pandas as pd

# データ読み込み
data = pd.read_csv('./data/sample.csv')

# ランナー初期化
runner = NeuralForecastRunner(
    models=['AutoNHITS', 'AutoLSTM'],
    h=7,
    val_size=0.2
)

# 学習実行
results = runner.fit(data)

# 予測実行
forecasts = runner.predict(data, h=14)

# 評価
metrics = runner.evaluate(data)
print(metrics)
```

---

#### 4.2.2 設定ファイルを使用

```python
from nf_auto_runner import NeuralForecastRunner
from hydra import initialize, compose

# Hydra設定読み込み
with initialize(config_path="./conf"):
    cfg = compose(config_name="config")

# ランナー初期化（設定から）
runner = NeuralForecastRunner.from_config(cfg)

# 学習実行
results = runner.fit_from_config()
```

---

#### 4.2.3 カスタムモデル追加

```python
from neuralforecast.models import NHITS
from nf_auto_runner import ModelRegistry

# カスタムモデル登録
registry = ModelRegistry()
registry.register_model(
    name='CustomNHITS',
    model_class=NHITS,
    default_params={
        'input_size': 7,
        'h': 7,
        'max_steps': 1000
    }
)

# 使用
runner = NeuralForecastRunner(
    models=['CustomNHITS'],
    h=7
)
```

---

### 4.3 設定ファイル（YAML）

#### 4.3.1 基本設定

```yaml
# conf/config.yaml
defaults:
  - data: default
  - model: default
  - execution: default

# データ設定
data:
  data_path: ./data/sample.csv
  unique_id_column: unique_id
  time_column: ds
  target_column: y
  freq: D

# モデル設定
model:
  models:
    - AutoNHITS
    - AutoLSTM
  backend: cpu
  search_alg: optuna

# 実行設定
execution:
  h: 7
  val_size: 0.2
  max_workers: 4
  save_model: true
```

---

#### 4.3.2 高度な設定

```yaml
# conf/config_advanced.yaml
data:
  data_path: ./data/electricity.csv
  freq: H
  exogenous:
    future:
      - temperature
      - holiday
    historical:
      - demand_lag_1
      - demand_lag_2
    static:
      - region
      - type

model:
  models:
    - AutoNHITS
    - AutoLSTM
    - AutoTCN
  hyperparameters:
    AutoNHITS:
      input_size: [7, 14, 21]
      n_pool_kernel_size: [[2, 2, 2], [4, 4, 4]]
    AutoLSTM:
      input_size: [7, 14]
      hidden_size: [64, 128, 256]
  
  search_alg: optuna
  num_trials: 50
  timeout_per_trial: 600

execution:
  h: 24
  val_size: 0.2
  max_workers: 8
  backend: ray
  allow_ray_parallel: true
  
  # リソース制限
  max_memory_gb: 32
  max_gpu_memory_gb: 16

logging:
  level: INFO
  enable_mlflow: true
  enable_wandb: false
  log_dir: ./logs
```

---

## 5. チュートリアル

### チュートリアル1: 航空旅客数予測（シンプル）

#### 目的
単一の時系列データで基本的な予測を学ぶ

#### ステップ1: データ準備
```bash
# サンプルデータダウンロード
nf-runner data download \
  --sample air-passengers \
  --output ./data/air_passengers.csv

# データ確認
head ./data/air_passengers.csv
```

#### ステップ2: 学習
```bash
# 単一モデルで学習
nf-runner train \
  --data ./data/air_passengers.csv \
  --models AutoNHITS \
  --h 12 \
  --val-size 0.2
```

#### ステップ3: 可視化
```python
import pandas as pd
import matplotlib.pyplot as plt

# データ読み込み
data = pd.read_csv('./data/air_passengers.csv')
predictions = pd.read_csv('./outputs/predictions/predictions_*.csv')

# プロット
plt.figure(figsize=(12, 6))
plt.plot(data['ds'], data['y'], label='Actual', color='blue')
plt.plot(predictions['ds'], predictions['y_pred'], 
         label='Predicted', color='red', linestyle='--')
plt.fill_between(predictions['ds'], 
                 predictions['y_pred_lower'],
                 predictions['y_pred_upper'],
                 alpha=0.2, color='red')
plt.xlabel('Date')
plt.ylabel('Passengers')
plt.title('Air Passengers Forecast')
plt.legend()
plt.savefig('./outputs/forecast_plot.png')
plt.show()
```

---

### チュートリアル2: 複数モデルの比較

#### 目的
複数のモデルを学習し、最適なモデルを選択する

#### ステップ1: 複数モデルで学習
```bash
nf-runner train \
  --data ./data/sample.csv \
  --models AutoNHITS,AutoLSTM,AutoGRU,AutoTCN \
  --h 7 \
  --val-size 0.2 \
  --max-workers 4
```

#### ステップ2: 結果比較
```bash
# 全実行の結果を表示
nf-runner results list --experiment-id <your_experiment_id>

# 最良モデルを表示
nf-runner results best --metric mae
```

#### ステップ3: 詳細分析
```python
from nf_auto_runner import ResultsAnalyzer

# 分析器初期化
analyzer = ResultsAnalyzer()

# 実験結果読み込み
results = analyzer.load_experiment(experiment_id=123)

# モデル比較表作成
comparison = analyzer.compare_models(
    metrics=['mae', 'rmse', 'mape'],
    sort_by='mae'
)
print(comparison)

# 可視化
analyzer.plot_model_comparison(
    save_path='./outputs/model_comparison.png'
)
```

---

### チュートリアル3: ハイパーパラメータ探索

#### 目的
Optunaを使ったハイパーパラメータ最適化

#### ステップ1: 探索実行
```bash
nf-runner train \
  --data ./data/sample.csv \
  --models AutoNHITS \
  --search-alg optuna \
  --num-trials 50 \
  --timeout 3600 \
  --h 7
```

#### ステップ2: 探索結果確認
```python
from nf_auto_runner import HyperparameterAnalyzer

# 分析器初期化
analyzer = HyperparameterAnalyzer()

# 探索結果読み込み
study = analyzer.load_study(study_name='<study_name>')

# 最適パラメータ表示
print("Best parameters:", study.best_params)
print("Best value:", study.best_value)

# 重要度分析
importance = analyzer.plot_param_importances(
    save_path='./outputs/param_importance.png'
)

# 最適化履歴プロット
analyzer.plot_optimization_history(
    save_path='./outputs/optimization_history.png'
)
```

---

### チュートリアル4: 外生変数を使った予測

#### 目的
外生変数（未来の特徴量）を使った予測

#### ステップ1: データ準備
```python
import pandas as pd
import numpy as np

# 基本データ
data = pd.DataFrame({
    'unique_id': ['series_1'] * 100,
    'ds': pd.date_range('2025-01-01', periods=100),
    'y': np.random.randn(100).cumsum() + 100
})

# 外生変数追加
data['futr_temperature'] = np.random.uniform(15, 30, 100)
data['futr_is_holiday'] = np.random.choice([0, 1], 100, p=[0.9, 0.1])

# 保存
data.to_csv('./data/data_with_exog.csv', index=False)
```

#### ステップ2: 学習
```bash
nf-runner train \
  --data ./data/data_with_exog.csv \
  --models AutoNHITS \
  --h 7 \
  --exog-future temperature,is_holiday
```

#### ステップ3: 予測（外生変数を指定）
```python
from nf_auto_runner import NeuralForecastRunner

# ランナー初期化
runner = NeuralForecastRunner.load_model(
    model_path='./outputs/models/AutoNHITS_*.pkl'
)

# 未来の外生変数を準備
future_exog = pd.DataFrame({
    'unique_id': ['series_1'] * 7,
    'ds': pd.date_range('2025-04-11', periods=7),
    'futr_temperature': [20, 21, 22, 23, 22, 21, 20],
    'futr_is_holiday': [0, 0, 0, 0, 0, 1, 1]
})

# 予測実行
forecasts = runner.predict(
    data=data,
    future_exog=future_exog,
    h=7
)
```

---

### チュートリアル5: バッチ予測と自動再学習

#### 目的
定期的なバッチ予測と自動再学習の設定

#### ステップ1: 予測スクリプト作成
```python
# scripts/batch_predict.py
from nf_auto_runner import NeuralForecastRunner, DriftDetector
import pandas as pd
from datetime import datetime

def batch_predict():
    # データ読み込み
    data = pd.read_csv('./data/latest_data.csv')
    
    # モデル読み込み
    runner = NeuralForecastRunner.load_latest_model(
        experiment_id=123
    )
    
    # ドリフト検出
    detector = DriftDetector()
    has_drift = detector.detect(data)
    
    if has_drift:
        print("Drift detected. Retraining model...")
        runner.fit(data)
    
    # 予測実行
    forecasts = runner.predict(data, h=7)
    
    # 結果保存
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    forecasts.to_csv(
        f'./outputs/predictions/forecast_{timestamp}.csv',
        index=False
    )
    
    print(f"Forecast completed: {len(forecasts)} rows generated")

if __name__ == '__main__':
    batch_predict()
```

#### ステップ2: cronジョブ設定
```bash
# crontabに追加（毎日午前2時に実行）
crontab -e

# 以下を追加
0 2 * * * cd /path/to/project && source .venv/bin/activate && python scripts/batch_predict.py >> logs/batch.log 2>&1
```

---

## 6. 次のステップ

### 6.1 詳細ドキュメント

クイックスタートを完了したら、以下のドキュメントを参照してください：

| ドキュメント | 内容 | 推奨度 |
|------------|------|--------|
| **01_REQUIREMENTS_SPECIFICATION_DETAILED.md** | 詳細な機能仕様 | ⭐⭐⭐ |
| **07_IMPLEMENTATION_GUIDE.md** | 実装ガイド | ⭐⭐⭐ |
| **08_CODING_STANDARDS.md** | コーディング規約 | ⭐⭐ |
| **09_TESTING_STRATEGY.md** | テスト戦略 | ⭐⭐ |
| **API_REFERENCE.md** | API リファレンス | ⭐⭐⭐ |

---

### 6.2 高度な機能

#### 6.2.1 MLflow統合
```bash
# MLflow UI起動
mlflow ui --port 5000

# MLflowトラッキング有効化
export MLFLOW_TRACKING_URI=http://localhost:5000
nf-runner train \
  --data ./data/sample.csv \
  --models AutoNHITS \
  --enable-mlflow
```

#### 6.2.2 Ray並列実行
```bash
# Ray クラスタ起動
ray start --head

# Ray並列実行
nf-runner train \
  --data ./data/sample.csv \
  --models AutoNHITS,AutoLSTM,AutoGRU \
  --backend ray \
  --max-workers 10
```

#### 6.2.3 Dockerデプロイ
```bash
# Dockerイメージビルド
docker build -t nf-auto-runner:latest .

# コンテナ起動
docker-compose up -d

# 学習実行（コンテナ内）
docker exec nf-runner nf-runner train \
  --data /data/sample.csv \
  --models AutoNHITS
```

---

### 6.3 コミュニティリソース

- **GitHub**: https://github.com/your-org/nf-auto-runner
- **ドキュメント**: https://docs.nf-auto-runner.io
- **Discussions**: https://github.com/your-org/nf-auto-runner/discussions
- **Slack**: #nf-auto-runner
- **Stack Overflow**: タグ `nf-auto-runner`

---

## 7. トラブルシューティング

### 7.1 よくある問題

#### 問題1: インストールエラー

**症状**:
```
ERROR: Could not find a version that satisfies the requirement neuralforecast
```

**解決策**:
```bash
# Pythonバージョン確認
python --version  # 3.11以上であること

# pipアップグレード
pip install --upgrade pip setuptools wheel

# 依存関係を個別インストール
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install neuralforecast
```

---

#### 問題2: データベース接続エラー

**症状**:
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**解決策**:
```bash
# PostgreSQLが起動しているか確認
sudo systemctl status postgresql

# 起動していない場合
sudo systemctl start postgresql

# 接続テスト
psql -U postgres -h localhost -c "SELECT 1;"

# .envファイルの接続文字列を確認
cat .env | grep DATABASE_URL
```

---

#### 問題3: メモリ不足

**症状**:
```
RuntimeError: CUDA out of memory
```

**解決策**:
```bash
# CPUバックエンドに切り替え
nf-runner train \
  --data ./data/sample.csv \
  --models AutoNHITS \
  --backend cpu

# バッチサイズを小さく
nf-runner train \
  --data ./data/sample.csv \
  --models AutoNHITS \
  --batch-size 32  # デフォルト: 128

# 並列実行数を減らす
nf-runner train \
  --data ./data/sample.csv \
  --models AutoNHITS,AutoLSTM \
  --max-workers 2  # デフォルト: CPU数
```

---

#### 問題4: 学習が遅い

**症状**:
学習に予想以上の時間がかかる

**解決策**:
```bash
# GPUが使用されているか確認
nvidia-smi

# GPUバックエンドを明示的に指定
nf-runner train \
  --data ./data/sample.csv \
  --models AutoNHITS \
  --backend cuda

# max_stepsを減らす（デバッグ時）
nf-runner train \
  --data ./data/sample.csv \
  --models AutoNHITS \
  --max-steps 500  # デフォルト: 1000

# 並列実行を有効化
nf-runner train \
  --data ./data/sample.csv \
  --models AutoNHITS,AutoLSTM,AutoGRU \
  --max-workers 4
```

---

#### 問題5: 予測精度が低い

**症状**:
MAEやRMSEが高い

**解決策**:

1. **データ品質を確認**:
```bash
# データ統計情報
nf-runner data stats --data ./data/your_data.csv

# 欠損値チェック
nf-runner data validate --data ./data/your_data.csv
```

2. **適切なモデルを選択**:
```bash
# 複数モデルで比較
nf-runner train \
  --data ./data/your_data.csv \
  --models AutoNHITS,AutoLSTM,AutoTCN,AutoPatchTST \
  --h 7
```

3. **ハイパーパラメータ探索**:
```bash
nf-runner train \
  --data ./data/your_data.csv \
  --models AutoNHITS \
  --search-alg optuna \
  --num-trials 50
```

4. **検証データサイズを調整**:
```bash
nf-runner train \
  --data ./data/your_data.csv \
  --models AutoNHITS \
  --val-size 0.3  # 30%を検証用に
```

---

### 7.2 ログ確認

#### システムログ
```bash
# アプリケーションログ
tail -f ./logs/app.log

# エラーログ
tail -f ./logs/error.log

# 実行ログ（特定のRun）
cat ./logs/run_<run_id>.log
```

#### デバッグモード
```bash
# 詳細ログ出力
nf-runner train \
  --data ./data/sample.csv \
  --models AutoNHITS \
  --log-level DEBUG

# または環境変数で設定
export LOG_LEVEL=DEBUG
nf-runner train --data ./data/sample.csv --models AutoNHITS
```

---

### 7.3 サポート情報

#### システム情報の収集
```bash
# システム情報出力
nf-runner system info > system_info.txt

# 設定情報出力
nf-runner config show --verbose > config_info.txt

# 依存関係出力
pip freeze > requirements_installed.txt
```

#### バグレポート
GitHubでIssueを作成する際に以下を含めてください：

1. **システム情報** (`nf-runner system info`)
2. **エラーメッセージ** (完全なトレースバック)
3. **再現手順** (最小限のコード例)
4. **期待される動作** vs **実際の動作**
5. **環境情報** (OS、Pythonバージョン、依存関係)

---

## ✨ まとめ

おめでとうございます！クイックスタートガイドを完了しました 🎉

### 学んだこと

- ✅ システムのインストールと初期設定
- ✅ サンプルデータでの学習と予測
- ✅ コマンドラインとPython APIの基本的な使い方
- ✅ 実践的なチュートリアル（5種類）
- ✅ トラブルシューティング

### 次のアクション

1. **実データで試す**: 自分のデータセットで学習と予測を実行
2. **詳細ドキュメント**: より高度な機能を学ぶ
3. **コミュニティ**: DiscussionsやSlackで質問・共有
4. **貢献**: GitHubでIssueやPull Requestを作成

---

**Happy Forecasting! 📈**

---

**関連ドキュメント**:
- 📄 [01_REQUIREMENTS_SPECIFICATION_DETAILED.md](./01_REQUIREMENTS_SPECIFICATION_DETAILED.md) - 詳細な機能仕様
- 📄 [07_IMPLEMENTATION_GUIDE.md](./07_IMPLEMENTATION_GUIDE.md) - 実装ガイド
- 📄 [API_REFERENCE.md](./API_REFERENCE.md) - API リファレンス
- 📄 [FAQ.md](./FAQ.md) - よくある質問

---
**End of Document**
