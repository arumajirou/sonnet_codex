# データベース・ツール設定値定義書
**Database and Tools Configuration Specification**

---

## 📋 ドキュメント情報

| 項目 | 内容 |
|-----|------|
| **ドキュメントタイトル** | データベース・ツール設定値定義書 |
| **バージョン** | v1.0.0 |
| **作成日** | 2025-11-04 |
| **対象システム** | NeuralForecast Auto Runner + Time Series Forecasting System |

---

## 目次

1. [データベース設定（PostgreSQL）](#1-データベース設定postgresql)
2. [アプリケーション環境変数](#2-アプリケーション環境変数)
3. [MLflow設定](#3-mlflow設定)
4. [Weights & Biases設定](#4-weights--biases設定)
5. [Ray設定](#5-ray設定)
6. [Optuna設定](#6-optuna設定)
7. [その他のツール設定](#7-その他のツール設定)
8. [Docker Compose設定](#8-docker-compose設定)
9. [環境別設定例](#9-環境別設定例)

---

## 1. データベース設定（PostgreSQL）

### 1.1 基本構成

```yaml
Database Configuration:
  Database Name: ts_forecast_system
  Database Engine: PostgreSQL
  Version: 14+ (推奨: 15.x)
  Encoding: UTF8
  Locale: en_US.UTF-8
  Timezone: UTC
  Default Port: 5432
```

### 1.2 接続設定

#### 環境変数

| 環境変数名 | 説明 | デフォルト値 | 必須 |
|-----------|------|------------|------|
| `DATABASE_URL` | データベース接続URL | `postgresql://postgres:password@localhost:5432/ts_forecast_system` | ✅ |
| `DATABASE_POOL_SIZE` | コネクションプール最小数 | `10` | ❌ |
| `DATABASE_MAX_OVERFLOW` | プールオーバーフロー最大数 | `20` | ❌ |
| `DATABASE_POOL_TIMEOUT` | プール接続タイムアウト（秒） | `30` | ❌ |
| `DATABASE_POOL_RECYCLE` | コネクション再利用時間（秒） | `3600` | ❌ |
| `DATABASE_ECHO` | SQLログ出力 | `false` | ❌ |

#### 接続URL形式

```
postgresql://[user[:password]@][host][:port][/database][?options]
```

**例**:
```bash
# ローカル開発
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ts_forecast_system

# 本番環境（SSL有効）
DATABASE_URL=postgresql://user:password@db.example.com:5432/ts_forecast_system?sslmode=require

# Docker環境
DATABASE_URL=postgresql://mlflow:mlflow@postgres:5432/mlflow
```

### 1.3 コネクションプール設定

```python
# SQLAlchemy設定例
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,              # 最小コネクション数
    max_overflow=20,           # 最大オーバーフロー
    pool_timeout=30,           # タイムアウト（秒）
    pool_recycle=3600,         # 再利用時間（秒）
    pool_pre_ping=True,        # 接続確認
    echo=False,                # SQLログ
)
```

### 1.4 スキーマ構成

```sql
-- メインスキーマ
CREATE SCHEMA IF NOT EXISTS public;

-- 監査ログスキーマ
CREATE SCHEMA IF NOT EXISTS audit;

-- ステージングスキーマ
CREATE SCHEMA IF NOT EXISTS staging;

-- アーカイブスキーマ
CREATE SCHEMA IF NOT EXISTS archive;
```

### 1.5 データベースユーザー権限

```sql
-- アプリケーションユーザー作成
CREATE USER app_user WITH PASSWORD 'secure_password';

-- 権限付与
GRANT CONNECT ON DATABASE ts_forecast_system TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- 将来のテーブルに対する権限
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
```

### 1.6 バックアップ設定

```bash
# 環境変数
BACKUP_DIR=/path/to/backups
BACKUP_RETENTION_DAYS=30
DB_NAME=ts_forecast_system
DB_USER=postgres
DB_HOST=localhost
DB_PORT=5432

# バックアップスクリプト
pg_dump -U ${DB_USER} -h ${DB_HOST} -p ${DB_PORT} \
  -Fc -Z9 ${DB_NAME} | gzip > "${BACKUP_DIR}/full_${DB_NAME}_$(date +%Y%m%d).sql.gz"
```

---

## 2. アプリケーション環境変数

### 2.1 NF_プレフィックス環境変数（完全リスト）

#### 2.1.1 パス設定

| 環境変数名 | 説明 | デフォルト値 | 型 |
|-----------|------|------------|-----|
| `NF_DATA_CSV` | 入力データCSVパス | `./data.csv` | Path |
| `NF_OUTPUT_DIR` | 出力ディレクトリ | `./nf_auto_runs` | Path |
| `NF_LOG_DIR` | ログディレクトリ | `./nf_auto_runs/logs` | Path |
| `NF_MODEL_DIR` | モデル保存ディレクトリ | `./nf_auto_runs/models` | Path |
| `NF_ARTIFACT_DIR` | アーティファクトディレクトリ | `./nf_auto_runs/artifacts` | Path |
| `NF_CHECKPOINT_DIR` | チェックポイントディレクトリ | `./nf_auto_runs/checkpoints` | Path |
| `NF_PLOT_DIR` | プロット保存ディレクトリ | `./nf_auto_runs/plots` | Path |

#### 2.1.2 実行制御

| 環境変数名 | 説明 | デフォルト値 | 型 | 範囲 |
|-----------|------|------------|-----|------|
| `NF_RANDOM_STATE` | 乱数シード | `2077` | int | 0-2147483647 |
| `NF_TRIAL_NUM_SAMPLES` | 試行回数 | `1` | int | 1-1000 |
| `NF_TRIAL_MAX_STEPS` | 最大ステップ数 | `50` | int | 1-1000 |
| `NF_DEFAULT_H` | デフォルト予測期間 | `24` | int | 1-1000 |
| `NF_H_RATIO` | 予測期間比率 | `0.1` | float | 0.0-1.0 |
| `NF_MAX_WORKERS` | 最大並列ワーカー数 | `cpu_count//2` | int | 1-128 |
| `NF_ALLOW_RAY_PARALLEL` | Ray並列実行を許可 | `false` | bool | true/false |
| `NF_SAVE_MODEL` | モデル保存を有効化 | `true` | bool | true/false |
| `NF_OVERWRITE_MODEL` | モデル上書きを許可 | `false` | bool | true/false |

#### 2.1.3 データ処理

| 環境変数名 | 説明 | デフォルト値 | 型 |
|-----------|------|------------|-----|
| `NF_MAX_EXOG_F` | 最大Future外生変数数 | `256` | int |
| `NF_MAX_EXOG_H` | 最大Historical外生変数数 | `256` | int |
| `NF_MAX_EXOG_S` | 最大Static外生変数数 | `256` | int |
| `NF_DIR_TOKENS_MAXLEN` | ディレクトリ名最大長 | `200` | int |

#### 2.1.4 モデル・アルゴリズム選択

| 環境変数名 | 説明 | デフォルト値 | 型 |
|-----------|------|------------|-----|
| `NF_MODELS` | 使用モデルリスト（カンマ区切り） | `auto` | str |
| `NF_BACKENDS` | 計算バックエンド（カンマ区切り） | `auto` | str |
| `NF_SEARCH_ALGS` | 探索アルゴリズム（カンマ区切り） | `auto` | str |
| `NF_LOSSES` | 損失関数（カンマ区切り） | `auto` | str |
| `NF_SCALERS` | スケーラー（カンマ区切り） | `auto` | str |
| `NF_EARLY_STOPS` | Early Stopping設定 | `auto` | str |

**使用例**:
```bash
# 特定モデルのみ使用
export NF_MODELS="AutoNHITS,AutoLSTM"

# CUDAバックエンドのみ
export NF_BACKENDS="cuda"

# 複数探索アルゴリズム
export NF_SEARCH_ALGS="grid,random,bayesian"

# 複数損失関数
export NF_LOSSES="mae,mse,rmse"
```

#### 2.1.5 その他

| 環境変数名 | 説明 | デフォルト値 | 型 |
|-----------|------|------------|-----|
| `NF_EXPAND_AXES` | 軸展開設定 | `auto` | str |
| `NF_COMBO_DEPTH` | 組み合わせ深さ | `3` | int |
| `NF_VAL_SIZE` | 検証セットサイズ | `0.2` | float |
| `NF_PATCH_MODEL_INIT` | モデル初期化パッチ | `false` | bool |
| `NF_DB_ENABLE` | データベース記録有効化 | `true` | bool |

### 2.2 標準環境変数

#### 2.2.1 一般設定

| 環境変数名 | 説明 | デフォルト値 | 必須 |
|-----------|------|------------|------|
| `LOG_LEVEL` | ログレベル | `INFO` | ❌ |
| `LOG_FORMAT` | ログフォーマット | `json` | ❌ |
| `PYTHONPATH` | Pythonパス | - | ❌ |
| `TZ` | タイムゾーン | `UTC` | ❌ |

#### 2.2.2 セキュリティ

| 環境変数名 | 説明 | デフォルト値 | 必須 |
|-----------|------|------------|------|
| `SECRET_KEY` | シークレットキー | - | ✅ |
| `JWT_ALGORITHM` | JWT署名アルゴリズム | `HS256` | ❌ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | トークン有効期限（分） | `60` | ❌ |

---

## 3. MLflow設定

### 3.1 環境変数

| 環境変数名 | 説明 | デフォルト値 | 必須 |
|-----------|------|------------|------|
| `MLFLOW_TRACKING_URI` | トラッキングサーバーURI | `file:./mlruns` | ✅ |
| `MLFLOW_EXPERIMENT_NAME` | 実験名 | `ts-autorunner` | ❌ |
| `MLFLOW_S3_ENDPOINT_URL` | S3エンドポイント（MinIO等） | - | ❌ |
| `MLFLOW_TRACKING_USERNAME` | 認証ユーザー名 | - | ❌ |
| `MLFLOW_TRACKING_PASSWORD` | 認証パスワード | - | ❌ |

### 3.2 設定例

#### ローカルファイルストレージ
```bash
export MLFLOW_TRACKING_URI="file:./mlruns"
```

#### リモートトラッキングサーバー
```bash
export MLFLOW_TRACKING_URI="http://mlflow-server:5000"
```

#### PostgreSQLバックエンド
```bash
export MLFLOW_TRACKING_URI="postgresql://mlflow:password@db:5432/mlflowdb"
```

#### S3 Artifact Store（MinIO）
```bash
export MLFLOW_TRACKING_URI="http://mlflow-server:5000"
export MLFLOW_S3_ENDPOINT_URL="http://minio:9000"
export AWS_ACCESS_KEY_ID="minioadmin"
export AWS_SECRET_ACCESS_KEY="minioadmin"
```

### 3.3 MLflowサーバー起動設定

```bash
# 基本起動
mlflow server \
  --backend-store-uri postgresql://mlflow:password@localhost:5432/mlflowdb \
  --default-artifact-root s3://mlflow-artifacts/ \
  --host 0.0.0.0 \
  --port 5000

# 認証有効化
mlflow server \
  --backend-store-uri postgresql://mlflow:password@localhost:5432/mlflowdb \
  --default-artifact-root s3://mlflow-artifacts/ \
  --host 0.0.0.0 \
  --port 5000 \
  --app-name basic-auth
```

### 3.4 Python API設定

```python
import mlflow
import os

# トラッキングURI設定
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns"))

# 実験設定
mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT_NAME", "ts-autorunner"))

# 自動ログ有効化
mlflow.autolog()
```

---

## 4. Weights & Biases設定

### 4.1 環境変数

| 環境変数名 | 説明 | デフォルト値 | 必須 |
|-----------|------|------------|------|
| `WANDB_API_KEY` | W&B APIキー | - | ✅（有効化時） |
| `WANDB_PROJECT` | プロジェクト名 | `ts-forecasting` | ❌ |
| `WANDB_ENTITY` | エンティティ名（ユーザー/チーム） | - | ❌ |
| `WANDB_MODE` | 動作モード | `online` | ❌ |
| `WANDB_DIR` | ログディレクトリ | `./wandb` | ❌ |
| `WANDB_SILENT` | サイレントモード | `false` | ❌ |
| `NF_WANDB_PROJECT` | プロジェクト名（NF用） | - | ❌ |

### 4.2 動作モード

| モード | 説明 | 用途 |
|--------|------|------|
| `online` | オンライン同期 | 通常運用 |
| `offline` | オフライン保存のみ | ネットワーク制限環境 |
| `disabled` | W&B無効化 | CI/テスト環境 |
| `dryrun` | ダミー実行 | デバッグ |

### 4.3 設定例

#### 基本設定
```bash
export WANDB_API_KEY="your_api_key_here"
export WANDB_PROJECT="time-series-forecasting"
export WANDB_ENTITY="your-team"
```

#### オフラインモード
```bash
export WANDB_MODE="offline"
export WANDB_DIR="./wandb_logs"
```

#### CI/テスト環境
```bash
export WANDB_MODE="disabled"
```

### 4.4 Python API設定

```python
import wandb
import os

# 初期化
wandb.init(
    project=os.getenv("WANDB_PROJECT", "ts-forecasting"),
    entity=os.getenv("WANDB_ENTITY"),
    mode=os.getenv("WANDB_MODE", "online"),
    dir=os.getenv("WANDB_DIR", "./wandb"),
)

# ログ
wandb.log({"loss": 0.5, "accuracy": 0.95})

# 終了
wandb.finish()
```

### 4.5 オフラインログの同期

```bash
# オフラインで保存したログを同期
wandb sync ./wandb/offline-run-20231104_120000-abcd1234
```

---

## 5. Ray設定

### 5.1 環境変数

| 環境変数名 | 説明 | デフォルト値 | 必須 |
|-----------|------|------------|------|
| `RAY_ADDRESS` | Rayクラスタアドレス | `auto` | ❌ |
| `RAY_NAMESPACE` | ネームスペース | `default` | ❌ |
| `RAY_DEDUP_LOGS` | 重複ログ削除 | `1` | ❌ |
| `RAY_BACKEND_LOG_LEVEL` | ログレベル | `warning` | ❌ |
| `RAY_NUM_CPUS` | CPU数 | `auto` | ❌ |
| `RAY_NUM_GPUS` | GPU数 | `auto` | ❌ |
| `RAY_OBJECT_STORE_MEMORY` | オブジェクトストアメモリ | `auto` | ❌ |
| `RAY_TMPDIR` | 一時ディレクトリ | `/tmp/ray` | ❌ |

### 5.2 接続設定

#### ローカル起動
```bash
# 自動ローカルクラスタ起動
export RAY_ADDRESS="auto"
```

#### リモートクラスタ接続
```bash
# Headノード接続
export RAY_ADDRESS="ray://ray-head:10001"

# または
export RAY_ADDRESS="ray://192.168.1.100:10001"
```

### 5.3 Ray Cluster起動

#### Head Node
```bash
ray start --head \
  --port=6379 \
  --dashboard-host=0.0.0.0 \
  --dashboard-port=8265 \
  --num-cpus=8 \
  --num-gpus=1 \
  --object-store-memory=10000000000
```

#### Worker Node
```bash
ray start \
  --address=ray-head:6379 \
  --num-cpus=8 \
  --num-gpus=1 \
  --object-store-memory=10000000000
```

### 5.4 Python API設定

```python
import ray
import os

# 初期化
ray.init(
    address=os.getenv("RAY_ADDRESS", "auto"),
    namespace=os.getenv("RAY_NAMESPACE", "default"),
    num_cpus=int(os.getenv("RAY_NUM_CPUS", "0")) or None,
    num_gpus=int(os.getenv("RAY_NUM_GPUS", "0")) or None,
    _temp_dir=os.getenv("RAY_TMPDIR", "/tmp/ray"),
)

# リソース情報確認
print(ray.available_resources())

# シャットダウン
ray.shutdown()
```

### 5.5 Ray Dashboard

| 項目 | 設定値 |
|------|--------|
| URL | `http://localhost:8265` |
| 認証 | デフォルトなし |
| メトリクス | CPU、メモリ、GPU使用率 |

---

## 6. Optuna設定

### 6.1 環境変数

| 環境変数名 | 説明 | デフォルト値 | 必須 |
|-----------|------|------------|------|
| `OPTUNA_STORAGE` | ストレージURL | `sqlite:///optuna.db` | ❌ |
| `OPTUNA_STUDY_NAME` | スタディ名 | - | ❌ |
| `OPTUNA_N_TRIALS` | 試行回数 | `100` | ❌ |
| `OPTUNA_TIMEOUT` | タイムアウト（秒） | - | ❌ |
| `OPTUNA_N_JOBS` | 並列ジョブ数 | `1` | ❌ |

### 6.2 ストレージ設定

#### SQLite（ローカル開発）
```bash
export OPTUNA_STORAGE="sqlite:///optuna_study.db"
```

#### PostgreSQL（本番環境）
```bash
export OPTUNA_STORAGE="postgresql://optuna:password@localhost:5432/optuna_db"
```

#### MySQL
```bash
export OPTUNA_STORAGE="mysql://optuna:password@localhost:3306/optuna_db"
```

### 6.3 Python API設定

```python
import optuna
import os

# ストレージ設定
storage = os.getenv("OPTUNA_STORAGE", "sqlite:///optuna.db")

# スタディ作成
study = optuna.create_study(
    study_name=os.getenv("OPTUNA_STUDY_NAME", "ts-optimization"),
    storage=storage,
    direction="minimize",
    load_if_exists=True,
)

# 最適化実行
study.optimize(
    objective_function,
    n_trials=int(os.getenv("OPTUNA_N_TRIALS", "100")),
    timeout=int(os.getenv("OPTUNA_TIMEOUT", "0")) or None,
    n_jobs=int(os.getenv("OPTUNA_N_JOBS", "1")),
)
```

### 6.4 Optuna Dashboard

```bash
# ダッシュボード起動
optuna-dashboard \
  sqlite:///optuna_study.db \
  --host 0.0.0.0 \
  --port 8080
```

---

## 7. その他のツール設定

### 7.1 TensorBoard

| 環境変数名 | 説明 | デフォルト値 |
|-----------|------|------------|
| `TENSORBOARD_LOG_DIR` | ログディレクトリ | `./logs` |
| `TENSORBOARD_PORT` | ポート番号 | `6006` |

```bash
tensorboard --logdir=${TENSORBOARD_LOG_DIR} --port=${TENSORBOARD_PORT}
```

### 7.2 Hydra

| 環境変数名 | 説明 | デフォルト値 |
|-----------|------|------------|
| `HYDRA_FULL_ERROR` | フルエラー表示 | `1` |

### 7.3 CUDA/GPU

| 環境変数名 | 説明 | デフォルト値 |
|-----------|------|------------|
| `CUDA_VISIBLE_DEVICES` | 使用GPU ID | `0` |
| `CUDA_LAUNCH_BLOCKING` | 同期実行 | `0` |

```bash
# GPU 0, 1のみ使用
export CUDA_VISIBLE_DEVICES="0,1"
```

---

## 8. Docker Compose設定

### 8.1 完全なdocker-compose.yml例

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: ts_postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: ts_forecast_system
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --locale=en_US.UTF-8"
      TZ: UTC
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - ts_network

  # MLflow Tracking Server
  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    container_name: ts_mlflow
    command: >
      mlflow server
      --backend-store-uri postgresql://mlflow:mlflow@postgres:5432/mlflow
      --default-artifact-root /mlflow/artifacts
      --host 0.0.0.0
      --port 5000
    environment:
      MLFLOW_TRACKING_URI: postgresql://mlflow:mlflow@postgres:5432/mlflow
      AWS_ACCESS_KEY_ID: minioadmin
      AWS_SECRET_ACCESS_KEY: minioadmin
      MLFLOW_S3_ENDPOINT_URL: http://minio:9000
    ports:
      - "5000:5000"
    volumes:
      - mlflow_artifacts:/mlflow/artifacts
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - ts_network

  # MinIO (S3-compatible storage)
  minio:
    image: minio/minio:latest
    container_name: ts_minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data
    networks:
      - ts_network

  # Ray Head Node
  ray-head:
    image: rayproject/ray:latest-py311
    container_name: ts_ray_head
    command: >
      ray start --head
      --port=6379
      --dashboard-host=0.0.0.0
      --dashboard-port=8265
      --num-cpus=4
    environment:
      RAY_BACKEND_LOG_LEVEL: warning
    ports:
      - "6379:6379"
      - "8265:8265"
      - "10001:10001"
    volumes:
      - ray_data:/tmp/ray
    networks:
      - ts_network

  # Ray Worker Nodes
  ray-worker:
    image: rayproject/ray:latest-py311
    command: ray start --address=ray-head:6379 --num-cpus=4
    environment:
      RAY_BACKEND_LOG_LEVEL: warning
    depends_on:
      - ray-head
    deploy:
      replicas: 2
    networks:
      - ts_network

  # Application
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ts_app
    environment:
      # Database
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/ts_forecast_system
      
      # Paths
      NF_DATA_CSV: /app/data/input.csv
      NF_OUTPUT_DIR: /app/outputs
      NF_LOG_DIR: /app/logs
      
      # Execution
      NF_RANDOM_STATE: 2077
      NF_TRIAL_NUM_SAMPLES: 10
      NF_MAX_WORKERS: 4
      NF_ALLOW_RAY_PARALLEL: "true"
      
      # Tracking
      MLFLOW_TRACKING_URI: http://mlflow:5000
      WANDB_MODE: disabled
      
      # Ray
      RAY_ADDRESS: ray://ray-head:10001
      
      # Logging
      LOG_LEVEL: INFO
      LOG_FORMAT: json
    volumes:
      - ./data:/app/data
      - ./outputs:/app/outputs
      - ./logs:/app/logs
    depends_on:
      - postgres
      - mlflow
      - ray-head
    networks:
      - ts_network

volumes:
  postgres_data:
  mlflow_artifacts:
  minio_data:
  ray_data:

networks:
  ts_network:
    driver: bridge
```

---

## 9. 環境別設定例

### 9.1 ローカル開発環境

```bash
# .env.local
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ts_forecast_system

# Paths
NF_DATA_CSV=./data/sample.csv
NF_OUTPUT_DIR=./outputs
NF_LOG_DIR=./logs

# Execution
NF_RANDOM_STATE=42
NF_TRIAL_NUM_SAMPLES=1
NF_MAX_WORKERS=2
NF_ALLOW_RAY_PARALLEL=false
NF_SAVE_MODEL=true

# Tracking
MLFLOW_TRACKING_URI=file:./mlruns
WANDB_MODE=disabled

# Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=text
```

### 9.2 ステージング環境

```bash
# .env.staging
# Database
DATABASE_URL=postgresql://app_user:${DB_PASSWORD}@db-staging:5432/ts_forecast_staging

# Paths
NF_DATA_CSV=/data/staging_data.csv
NF_OUTPUT_DIR=/outputs
NF_LOG_DIR=/logs

# Execution
NF_RANDOM_STATE=2077
NF_TRIAL_NUM_SAMPLES=10
NF_MAX_WORKERS=8
NF_ALLOW_RAY_PARALLEL=true
NF_SAVE_MODEL=true

# Tracking
MLFLOW_TRACKING_URI=http://mlflow-staging:5000
WANDB_MODE=online
WANDB_PROJECT=ts-forecasting-staging

# Ray
RAY_ADDRESS=ray://ray-head-staging:10001

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### 9.3 本番環境

```bash
# .env.production
# Database
DATABASE_URL=postgresql://app_user:${DB_PASSWORD}@db-prod:5432/ts_forecast_production
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Paths
NF_DATA_CSV=/data/production_data.csv
NF_OUTPUT_DIR=/outputs
NF_LOG_DIR=/logs

# Execution
NF_RANDOM_STATE=2077
NF_TRIAL_NUM_SAMPLES=50
NF_MAX_WORKERS=16
NF_ALLOW_RAY_PARALLEL=true
NF_SAVE_MODEL=true

# Tracking
MLFLOW_TRACKING_URI=https://mlflow.example.com
MLFLOW_TRACKING_USERNAME=${MLFLOW_USER}
MLFLOW_TRACKING_PASSWORD=${MLFLOW_PASSWORD}
WANDB_MODE=online
WANDB_PROJECT=ts-forecasting-production
WANDB_ENTITY=your-org

# Ray
RAY_ADDRESS=ray://ray-head-prod:10001

# Security
SECRET_KEY=${SECRET_KEY}
JWT_ALGORITHM=HS256

# Logging
LOG_LEVEL=WARNING
LOG_FORMAT=json
```

### 9.4 CI/テスト環境

```bash
# .env.test
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ts_forecast_test

# Paths
NF_DATA_CSV=./tests/fixtures/test_data.csv
NF_OUTPUT_DIR=./tests/outputs
NF_LOG_DIR=./tests/logs

# Execution
NF_RANDOM_STATE=42
NF_TRIAL_NUM_SAMPLES=1
NF_MAX_WORKERS=1
NF_ALLOW_RAY_PARALLEL=false
NF_SAVE_MODEL=false

# Tracking
MLFLOW_TRACKING_URI=file:./tests/mlruns
WANDB_MODE=disabled

# Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=text
```

---

## 10. 設定検証

### 10.1 環境変数チェックスクリプト

```python
#!/usr/bin/env python3
"""環境変数の検証スクリプト"""

import os
import sys
from typing import Dict, List, Tuple

# 必須環境変数
REQUIRED_VARS = [
    "DATABASE_URL",
]

# 推奨環境変数
RECOMMENDED_VARS = [
    "NF_DATA_CSV",
    "NF_OUTPUT_DIR",
    "MLFLOW_TRACKING_URI",
]

# 型チェック
TYPE_CHECKS: Dict[str, type] = {
    "NF_RANDOM_STATE": int,
    "NF_TRIAL_NUM_SAMPLES": int,
    "NF_H_RATIO": float,
    "NF_ALLOW_RAY_PARALLEL": bool,
}

def check_required_vars() -> List[str]:
    """必須環境変数のチェック"""
    missing = []
    for var in REQUIRED_VARS:
        if not os.getenv(var):
            missing.append(var)
    return missing

def check_recommended_vars() -> List[str]:
    """推奨環境変数のチェック"""
    missing = []
    for var in RECOMMENDED_VARS:
        if not os.getenv(var):
            missing.append(var)
    return missing

def validate_types() -> List[Tuple[str, str]]:
    """型検証"""
    errors = []
    for var, expected_type in TYPE_CHECKS.items():
        value = os.getenv(var)
        if value:
            try:
                if expected_type == bool:
                    if value.lower() not in ('true', 'false', '0', '1'):
                        errors.append((var, f"Expected bool, got {value}"))
                elif expected_type == int:
                    int(value)
                elif expected_type == float:
                    float(value)
            except ValueError:
                errors.append((var, f"Expected {expected_type.__name__}, got {value}"))
    return errors

def main():
    """メイン処理"""
    print("=== 環境変数検証 ===\n")
    
    # 必須チェック
    missing_required = check_required_vars()
    if missing_required:
        print("❌ 必須環境変数が不足:")
        for var in missing_required:
            print(f"  - {var}")
        sys.exit(1)
    else:
        print("✅ 必須環境変数: OK")
    
    # 推奨チェック
    missing_recommended = check_recommended_vars()
    if missing_recommended:
        print("\n⚠️  推奨環境変数が不足:")
        for var in missing_recommended:
            print(f"  - {var}")
    else:
        print("✅ 推奨環境変数: OK")
    
    # 型チェック
    type_errors = validate_types()
    if type_errors:
        print("\n❌ 型エラー:")
        for var, error in type_errors:
            print(f"  - {var}: {error}")
        sys.exit(1)
    else:
        print("✅ 型検証: OK")
    
    print("\n✅ すべての検証に合格しました")

if __name__ == "__main__":
    main()
```

### 10.2 データベース接続テスト

```python
#!/usr/bin/env python3
"""データベース接続テスト"""

import os
import sys
from sqlalchemy import create_engine, text

def test_database_connection():
    """データベース接続テスト"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL が設定されていません")
        sys.exit(1)
    
    try:
        print(f"接続テスト: {database_url}")
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ 接続成功: {version}")
            
    except Exception as e:
        print(f"❌ 接続失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_database_connection()
```

---

## 付録A: 環境変数クイックリファレンス

### カテゴリ別環境変数一覧

```bash
# === データベース ===
DATABASE_URL=postgresql://user:pass@host:5432/db
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# === パス（NF_） ===
NF_DATA_CSV=./data.csv
NF_OUTPUT_DIR=./nf_auto_runs
NF_LOG_DIR=./nf_auto_runs/logs
NF_MODEL_DIR=./nf_auto_runs/models

# === 実行制御（NF_） ===
NF_RANDOM_STATE=2077
NF_TRIAL_NUM_SAMPLES=10
NF_MAX_WORKERS=8
NF_ALLOW_RAY_PARALLEL=true

# === MLflow ===
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=my-experiment

# === Weights & Biases ===
WANDB_API_KEY=your_key
WANDB_PROJECT=my-project
WANDB_MODE=online

# === Ray ===
RAY_ADDRESS=ray://localhost:10001
RAY_NUM_CPUS=8
RAY_NUM_GPUS=1

# === Optuna ===
OPTUNA_STORAGE=sqlite:///optuna.db
OPTUNA_N_TRIALS=100

# === ログ ===
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

**Document End**

**総環境変数数**: 60個以上  
**カテゴリ数**: 8カテゴリ  
**詳細度**: 完全（デフォルト値、型、範囲、例まで記載）
