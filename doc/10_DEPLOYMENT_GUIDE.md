# 📦 10_DEPLOYMENT_GUIDE.md - デプロイガイド

**Time Series Forecasting System - Deployment Guide**

---

## 📋 目次

1. [概要](#1-概要)
2. [システム要件](#2-システム要件)
3. [前提条件](#3-前提条件)
4. [ローカル環境デプロイ](#4-ローカル環境デプロイ)
5. [Docker環境デプロイ](#5-docker環境デプロイ)
6. [本番環境デプロイ](#6-本番環境デプロイ準備中)
7. [環境変数設定](#7-環境変数設定)
8. [データベース設定](#8-データベース設定)
9. [オプションサービス設定](#9-オプションサービス設定)
10. [セキュリティ設定](#10-セキュリティ設定)
11. [監視・ロギング設定](#11-監視ロギング設定)
12. [バックアップ・復旧手順](#12-バックアップ復旧手順)
13. [トラブルシューティング](#13-トラブルシューティング)
14. [付録](#14-付録)

---

## 1. 概要

### 1.1 ドキュメントの目的

本ドキュメントは、時系列予測システムの各環境へのデプロイ手順を提供します。

### 1.2 対象読者

- **開発者**: ローカル環境でのセットアップ
- **DevOpsエンジニア**: Docker/Kubernetesデプロイ
- **運用担当者**: 本番環境の管理・保守

### 1.3 デプロイ環境

| 環境 | 用途 | インフラ | 可用性 |
|-----|------|---------|--------|
| **Local** | 開発・デバッグ | ローカルマシン | N/A |
| **Docker** | 統合テスト・ステージング | Docker Compose | 単一ホスト |
| **Production** | 本番運用 | Kubernetes/VM | 高可用性 |

---

## 2. システム要件

### 2.1 ハードウェア要件

#### 最小構成

| コンポーネント | 最小要件 | 推奨要件 |
|--------------|---------|---------|
| **CPU** | 4コア | 8コア以上 |
| **メモリ** | 8GB | 16GB以上 |
| **ディスク** | 50GB | 100GB以上（SSD） |
| **GPU** | なし | NVIDIA GPU（CUDA対応） |
| **ネットワーク** | 10Mbps | 100Mbps以上 |

#### 推奨構成（本番環境）

| コンポーネント | 推奨要件 |
|--------------|---------|
| **CPU** | 16コア以上 |
| **メモリ** | 32GB以上 |
| **ディスク** | 500GB以上（NVMe SSD） |
| **GPU** | NVIDIA A100/V100 |
| **ネットワーク** | 1Gbps以上 |

---

### 2.2 ソフトウェア要件

#### 必須ソフトウェア

| ソフトウェア | バージョン | 用途 |
|------------|-----------|------|
| **Python** | 3.11.x | アプリケーション実行 |
| **PostgreSQL** | 14.x以上 | データベース |
| **pip** | 最新版 | パッケージ管理 |

#### オプションソフトウェア

| ソフトウェア | バージョン | 用途 |
|------------|-----------|------|
| **Docker** | 24.x以上 | コンテナ化 |
| **Docker Compose** | 2.x以上 | マルチコンテナ管理 |
| **MLflow** | 2.x以上 | 実験管理 |
| **Ray** | 2.x以上 | 分散実行 |
| **CUDA** | 11.8以上 | GPU計算 |

---

### 2.3 OS互換性

| OS | サポートレベル | 備考 |
|----|--------------|------|
| **Ubuntu** 20.04+ | 完全サポート | 推奨 |
| **macOS** 12+ | 完全サポート | Apple Silicon対応 |
| **Windows** 10+ | ベストエフォート | WSL2推奨 |
| **CentOS/RHEL** 8+ | ベストエフォート | - |

---

## 3. 前提条件

### 3.1 必要な知識

- **基本的なコマンドライン操作**
- **Python仮想環境の理解**
- **Docker/Docker Composeの基礎知識**（Docker環境の場合）
- **PostgreSQLの基本操作**

### 3.2 事前準備

#### 3.2.1 アクセス権限

```bash
# 必要な権限を確認
id  # ユーザーIDとグループを確認
groups  # 所属グループを確認

# Dockerグループへの追加（Docker使用の場合）
sudo usermod -aG docker $USER
newgrp docker  # グループを即座に反映
```

#### 3.2.2 ネットワーク設定

```bash
# ファイアウォール設定（必要に応じて）
sudo ufw allow 5432/tcp  # PostgreSQL
sudo ufw allow 8000/tcp  # FastAPI
sudo ufw allow 5000/tcp  # MLflow
sudo ufw allow 8265/tcp  # Ray Dashboard

# SELinux設定（CentOS/RHELの場合）
sudo setenforce 0  # 一時的に無効化
# または
sudo vi /etc/selinux/config
# SELINUX=permissive に変更
```

#### 3.2.3 必要なポート

| ポート | サービス | 用途 |
|-------|---------|------|
| 5432 | PostgreSQL | データベース |
| 8000 | FastAPI | Web API |
| 5000 | MLflow | 実験トラッキング |
| 8265 | Ray | 分散実行ダッシュボード |
| 9090 | Prometheus | メトリクス収集 |
| 3000 | Grafana | 監視ダッシュボード |

---

## 4. ローカル環境デプロイ

### 4.1 セットアップフロー

```mermaid
graph TB
    A[開始] --> B[Python 3.11インストール]
    B --> C[リポジトリクローン]
    C --> D[仮想環境作成]
    D --> E[依存関係インストール]
    E --> F[PostgreSQLセットアップ]
    F --> G[環境変数設定]
    G --> H[データベース初期化]
    H --> I[動作確認]
    I --> J[完了]
```

---

### 4.2 Python環境セットアップ

#### 4.2.1 Python 3.11のインストール

**Ubuntu/Debian**:

```bash
# リポジトリ追加
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# Python 3.11インストール
sudo apt install python3.11 python3.11-venv python3.11-dev

# 確認
python3.11 --version
```

**macOS**:

```bash
# Homebrew経由でインストール
brew install python@3.11

# 確認
python3.11 --version
```

**Windows**:

```powershell
# Python公式サイトからインストーラーをダウンロード
# https://www.python.org/downloads/

# または Chocolatey使用
choco install python311

# 確認
python --version
```

---

#### 4.2.2 リポジトリのクローン

```bash
# HTTPSでクローン
git clone https://github.com/your-org/time-series-forecasting-system.git
cd time-series-forecasting-system

# またはSSHでクローン
git clone git@github.com:your-org/time-series-forecasting-system.git
cd time-series-forecasting-system

# ブランチ確認
git branch -a
git checkout main  # または develop
```

---

#### 4.2.3 仮想環境の作成

**方法1: venv（標準）**:

```bash
# 仮想環境作成
python3.11 -m venv .venv

# 有効化
source .venv/bin/activate  # Linux/macOS
# または
.venv\Scripts\activate  # Windows

# 仮想環境が有効になったことを確認
which python  # 仮想環境のPythonパスが表示される
python --version  # Python 3.11.x
```

**方法2: Poetry（推奨）**:

```bash
# Poetryインストール
curl -sSL https://install.python-poetry.org | python3 -

# Poetryをパスに追加
export PATH="$HOME/.local/bin:$PATH"

# プロジェクトセットアップ
poetry install

# 仮想環境有効化
poetry shell

# または、仮想環境内でコマンド実行
poetry run python --version
```

---

#### 4.2.4 依存関係のインストール

```bash
# pipのアップグレード
pip install --upgrade pip setuptools wheel

# 基本パッケージインストール
pip install -r requirements.txt

# 開発用パッケージインストール（オプション）
pip install -r requirements-dev.txt

# 開発モードでパッケージインストール
pip install -e .

# インストール確認
pip list
pip check  # 依存関係の整合性確認
```

**requirements.txt（主要依存関係）**:

```txt
# Core
neuralforecast>=1.6.0,<2.0.0
pandas>=2.0.0,<3.0.0
numpy>=1.24.0,<2.0.0
torch>=2.0.0,<3.0.0

# Database
sqlalchemy>=2.0.0,<3.0.0
psycopg2-binary>=2.9.0
alembic>=1.12.0

# API
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.0.0

# Tracking (Optional)
mlflow>=2.8.0
wandb>=0.16.0

# Distributed Computing (Optional)
ray[default]>=2.8.0

# Hyperparameter Optimization
optuna>=3.4.0

# Utilities
python-dotenv>=1.0.0
typer>=0.9.0
rich>=13.6.0
```

---

### 4.3 PostgreSQLセットアップ

#### 4.3.1 PostgreSQLインストール

**Ubuntu/Debian**:

```bash
# PostgreSQL 14インストール
sudo apt install postgresql-14 postgresql-contrib-14

# サービス開始
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 状態確認
sudo systemctl status postgresql
```

**macOS**:

```bash
# Homebrewでインストール
brew install postgresql@14

# サービス開始
brew services start postgresql@14

# 確認
psql --version
```

**Docker（推奨）**:

```bash
# PostgreSQLコンテナ起動
docker run -d \
  --name ts-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_DB=ts_forecast_system \
  -p 5432:5432 \
  -v postgres-data:/var/lib/postgresql/data \
  postgres:14

# 確認
docker ps | grep ts-postgres
```

---

#### 4.3.2 データベース作成

```bash
# PostgreSQLに接続
sudo -u postgres psql

# データベース作成
CREATE DATABASE ts_forecast_system;

# ユーザー作成
CREATE USER ts_user WITH ENCRYPTED PASSWORD 'yourpassword';

# 権限付与
GRANT ALL PRIVILEGES ON DATABASE ts_forecast_system TO ts_user;

# 確認
\l  # データベース一覧
\du  # ユーザー一覧
\q  # 終了
```

---

#### 4.3.3 接続確認

```bash
# データベース接続テスト
psql -h localhost -U ts_user -d ts_forecast_system -W

# SQL実行テスト
SELECT version();
SELECT current_database();

# 終了
\q
```

---

### 4.4 環境変数設定

#### 4.4.1 .envファイル作成

```bash
# サンプルファイルからコピー
cp .env.example .env

# エディタで編集
vi .env  # または nano, code など
```

**最小構成の.env**:

```bash
# ========================================
# Database Configuration
# ========================================
DATABASE_URL=postgresql://ts_user:yourpassword@localhost:5432/ts_forecast_system
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30
DATABASE_ECHO=false

# ========================================
# Path Configuration
# ========================================
DATA_DIR=./data
MODEL_DIR=./models
OUTPUT_DIR=./outputs
LOG_DIR=./logs

# ========================================
# Execution Configuration
# ========================================
MAX_PARALLEL_RUNS=4
DEFAULT_BACKEND=cuda  # cuda, cpu, mps
ENABLE_GPU=true
GPU_MEMORY_LIMIT=0.8

# ========================================
# Logging Configuration
# ========================================
LOG_LEVEL=INFO
LOG_FORMAT=json
ENABLE_FILE_LOGGING=true

# ========================================
# Optional Services
# ========================================
ENABLE_MLFLOW=false
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=time_series_forecasting

ENABLE_WANDB=false
WANDB_API_KEY=your_wandb_key
WANDB_PROJECT=time-series-forecasting

ENABLE_RAY=false
RAY_ADDRESS=auto
RAY_NAMESPACE=ts_forecast
```

---

#### 4.4.2 環境変数の読み込み

```bash
# .envファイルから読み込み
source .env

# または
export $(cat .env | grep -v '^#' | xargs)

# 確認
echo $DATABASE_URL
echo $DATA_DIR
```

---

### 4.5 ディレクトリ構造作成

```bash
# 必要なディレクトリを作成
mkdir -p data/{raw,processed,external,interim}
mkdir -p models/{staging,production}
mkdir -p outputs/{runs,predictions,plots,reports}
mkdir -p logs/{app,training,inference}

# 権限設定
chmod -R 755 data models outputs logs

# 確認
tree -L 2 -d
```

**期待される構造**:

```
.
├── data/
│   ├── raw/
│   ├── processed/
│   ├── external/
│   └── interim/
├── models/
│   ├── staging/
│   └── production/
├── outputs/
│   ├── runs/
│   ├── predictions/
│   ├── plots/
│   └── reports/
└── logs/
    ├── app/
    ├── training/
    └── inference/
```

---

### 4.6 データベース初期化

#### 4.6.1 Alembicマイグレーション

```bash
# マイグレーション履歴確認
alembic history

# 最新バージョンへマイグレーション
alembic upgrade head

# マイグレーション確認
alembic current

# データベーススキーマ確認
psql -h localhost -U ts_user -d ts_forecast_system -c "\dt"
```

---

#### 4.6.2 初期データ投入（オプション）

```bash
# シードデータスクリプト実行
python scripts/setup/seed_data.py

# 確認
psql -h localhost -U ts_user -d ts_forecast_system << EOF
SELECT COUNT(*) FROM experiments;
SELECT COUNT(*) FROM models;
EOF
```

---

### 4.7 動作確認

#### 4.7.1 ヘルスチェック

```bash
# データベース接続確認
python -c "
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    result = conn.execute('SELECT 1')
    print('Database connection: OK')
"
```

---

#### 4.7.2 テスト実行

```bash
# ユニットテスト
pytest tests/unit/ -v

# 統合テスト
pytest tests/integration/ -v

# カバレッジ付き
pytest tests/ -v --cov=src/nf_auto_runner --cov-report=html

# カバレッジレポート確認
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

---

#### 4.7.3 サンプル実行

```bash
# CLIヘルプ表示
python -m nf_auto_runner.app.main --help

# サンプルデータで実行
python -m nf_auto_runner.app.main \
  --data-path ./data/sample/sample_data.csv \
  --models NHITS,PatchTST \
  --horizons 24,48 \
  --backend cpu \
  --output-dir ./outputs/test_run

# 実行結果確認
ls -lh ./outputs/test_run/
```

---

## 5. Docker環境デプロイ

### 5.1 Dockerセットアップフロー

```mermaid
graph TB
    A[開始] --> B[Docker/Docker Composeインストール]
    B --> C[.envファイル作成]
    C --> D[docker-compose.ymlレビュー]
    D --> E[イメージビルド]
    E --> F[コンテナ起動]
    F --> G[ヘルスチェック]
    G --> H[動作確認]
    H --> I[完了]
```

---

### 5.2 Docker環境準備

#### 5.2.1 Dockerインストール

**Ubuntu/Debian**:

```bash
# 古いバージョン削除
sudo apt remove docker docker-engine docker.io containerd runc

# リポジトリ追加
sudo apt update
sudo apt install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Dockerインストール
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin

# Dockerグループに追加
sudo usermod -aG docker $USER
newgrp docker

# 確認
docker --version
docker compose version
```

**macOS**:

```bash
# Docker Desktopインストール
brew install --cask docker

# Docker起動
open -a Docker

# 確認
docker --version
docker compose version
```

---

### 5.3 Docker Compose設定

#### 5.3.1 docker-compose.yml

```yaml
version: '3.8'

services:
  # ========================================
  # PostgreSQL Database
  # ========================================
  postgres:
    image: postgres:14-alpine
    container_name: ts-postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?error}
      POSTGRES_DB: ${POSTGRES_DB:-ts_forecast_system}
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./scripts/db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - ts-network
    restart: unless-stopped

  # ========================================
  # Application
  # ========================================
  app:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        PYTHON_VERSION: "3.11"
    container_name: ts-app
    env_file:
      - .env
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-ts_forecast_system}
      MLFLOW_TRACKING_URI: ${ENABLE_MLFLOW:-false}
      RAY_ADDRESS: ${ENABLE_RAY:-false}
    volumes:
      - ./data:/app/data:rw
      - ./models:/app/models:rw
      - ./outputs:/app/outputs:rw
      - ./logs:/app/logs:rw
      - ./src:/app/src:ro
      - ./conf:/app/conf:ro
    ports:
      - "${APP_PORT:-8000}:8000"
    depends_on:
      postgres:
        condition: service_healthy
      mlflow:
        condition: service_started
        required: false
      ray-head:
        condition: service_started
        required: false
    networks:
      - ts-network
    restart: unless-stopped
    command: uvicorn nf_auto_runner.app.api:app --host 0.0.0.0 --port 8000

  # ========================================
  # MLflow Server (Optional)
  # ========================================
  mlflow:
    image: ghcr.io/mlflow/mlflow:v2.8.1
    container_name: ts-mlflow
    environment:
      BACKEND_STORE_URI: postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-ts_forecast_system}
      ARTIFACT_ROOT: /mlflow/artifacts
      MLFLOW_S3_ENDPOINT_URL: ${MLFLOW_S3_ENDPOINT_URL:-}
      AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID:-}
      AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY:-}
    volumes:
      - mlflow-artifacts:/mlflow/artifacts
    ports:
      - "${MLFLOW_PORT:-5000}:5000"
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - ts-network
    restart: unless-stopped
    command: >
      mlflow server
      --backend-store-uri ${BACKEND_STORE_URI}
      --default-artifact-root ${ARTIFACT_ROOT}
      --host 0.0.0.0
      --port 5000
    profiles:
      - mlflow

  # ========================================
  # Ray Head (Optional)
  # ========================================
  ray-head:
    image: rayproject/ray:2.8.1-py311
    container_name: ts-ray-head
    environment:
      RAY_memory_monitor_refresh_ms: 0
    volumes:
      - ./data:/data:ro
      - ./models:/models:rw
      - ray-data:/tmp/ray
    ports:
      - "${RAY_DASHBOARD_PORT:-8265}:8265"
      - "6379:6379"
      - "10001:10001"
    networks:
      - ts-network
    restart: unless-stopped
    command: >
      ray start
      --head
      --dashboard-host=0.0.0.0
      --dashboard-port=8265
      --port=6379
      --block
    shm_size: '2gb'
    profiles:
      - ray

  # ========================================
  # Ray Worker (Optional)
  # ========================================
  ray-worker:
    image: rayproject/ray:2.8.1-py311
    environment:
      RAY_memory_monitor_refresh_ms: 0
    volumes:
      - ./data:/data:ro
      - ./models:/models:rw
      - ray-data:/tmp/ray
    depends_on:
      - ray-head
    networks:
      - ts-network
    restart: unless-stopped
    command: >
      ray start
      --address=ray-head:6379
      --block
    deploy:
      replicas: ${RAY_WORKER_REPLICAS:-2}
    shm_size: '2gb'
    profiles:
      - ray

  # ========================================
  # Prometheus (Optional)
  # ========================================
  prometheus:
    image: prom/prometheus:v2.47.0
    container_name: ts-prometheus
    volumes:
      - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    ports:
      - "${PROMETHEUS_PORT:-9090}:9090"
    networks:
      - ts-network
    restart: unless-stopped
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
    profiles:
      - monitoring

  # ========================================
  # Grafana (Optional)
  # ========================================
  grafana:
    image: grafana/grafana:10.1.5
    container_name: ts-grafana
    environment:
      GF_SECURITY_ADMIN_USER: ${GRAFANA_USER:-admin}
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD:?error}
      GF_INSTALL_PLUGINS: grafana-piechart-panel
    volumes:
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources:ro
      - grafana-data:/var/lib/grafana
    ports:
      - "${GRAFANA_PORT:-3000}:3000"
    depends_on:
      - prometheus
    networks:
      - ts-network
    restart: unless-stopped
    profiles:
      - monitoring

# ========================================
# Networks
# ========================================
networks:
  ts-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.25.0.0/16

# ========================================
# Volumes
# ========================================
volumes:
  postgres-data:
    driver: local
  mlflow-artifacts:
    driver: local
  ray-data:
    driver: local
  prometheus-data:
    driver: local
  grafana-data:
    driver: local
```

---

#### 5.3.2 Dockerfile

```dockerfile
# ========================================
# Multi-stage Build
# ========================================

# ----------------------------------------
# Stage 1: Builder
# ----------------------------------------
FROM python:3.11-slim as builder

# 引数
ARG PYTHON_VERSION=3.11

# 作業ディレクトリ
WORKDIR /build

# システム依存関係
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係
COPY requirements.txt .
RUN pip install --user --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --user --no-cache-dir -r requirements.txt

# アプリケーションコード
COPY src /build/src
COPY setup.py pyproject.toml README.md /build/
RUN pip install --user --no-cache-dir -e .

# ----------------------------------------
# Stage 2: Runtime
# ----------------------------------------
FROM python:3.11-slim

# ラベル
LABEL maintainer="your-team@example.com"
LABEL version="1.0.0"
LABEL description="Time Series Forecasting System"

# 環境変数
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH=/home/appuser/.local/bin:$PATH

# 非rootユーザー作成
RUN groupadd -g 1000 appuser && \
    useradd -r -u 1000 -g appuser -m -d /home/appuser -s /bin/bash appuser

# ランタイム依存関係
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Builderステージからコピー
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# 作業ディレクトリ
WORKDIR /app

# アプリケーションファイル
COPY --chown=appuser:appuser src /app/src
COPY --chown=appuser:appuser conf /app/conf
COPY --chown=appuser:appuser scripts /app/scripts

# ディレクトリ作成
RUN mkdir -p /app/data /app/models /app/outputs /app/logs && \
    chown -R appuser:appuser /app

# ユーザー切り替え
USER appuser

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# エントリーポイント
EXPOSE 8000
CMD ["uvicorn", "nf_auto_runner.app.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### 5.4 Docker環境起動

#### 5.4.1 基本構成で起動

```bash
# .envファイル確認
cat .env

# イメージビルド
docker compose build

# コンテナ起動（デタッチモード）
docker compose up -d

# ログ確認
docker compose logs -f

# 起動確認
docker compose ps
```

---

#### 5.4.2 全サービス起動

```bash
# 全プロファイル有効化
docker compose --profile mlflow --profile ray --profile monitoring up -d

# または
COMPOSE_PROFILES=mlflow,ray,monitoring docker compose up -d

# 確認
docker compose ps
```

---

#### 5.4.3 個別サービス起動

```bash
# PostgreSQLのみ
docker compose up -d postgres

# アプリケーション + PostgreSQL
docker compose up -d app

# MLflow追加
docker compose --profile mlflow up -d

# Ray追加
docker compose --profile ray up -d
```

---

### 5.5 ヘルスチェック

#### 5.5.1 サービス状態確認

```bash
# 全コンテナの状態
docker compose ps

# 特定コンテナの詳細
docker inspect ts-app

# ヘルスチェック状態
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Health}}"
```

---

#### 5.5.2 接続確認

```bash
# PostgreSQL接続
docker compose exec postgres psql -U postgres -d ts_forecast_system -c "SELECT 1;"

# アプリケーションAPI
curl http://localhost:8000/health

# MLflow UI
curl http://localhost:5000/health

# Ray Dashboard
curl http://localhost:8265/api/cluster_status
```

---

#### 5.5.3 ログ確認

```bash
# 全サービスのログ
docker compose logs -f

# 特定サービスのログ
docker compose logs -f app
docker compose logs -f postgres

# タイムスタンプ付き
docker compose logs -f --timestamps app

# 最新100行
docker compose logs --tail=100 app
```

---

### 5.6 トラブルシューティング

#### 5.6.1 コンテナ再起動

```bash
# 全コンテナ再起動
docker compose restart

# 特定コンテナ再起動
docker compose restart app

# 強制再作成
docker compose up -d --force-recreate app
```

---

#### 5.6.2 クリーンアップ

```bash
# コンテナ停止
docker compose down

# コンテナ + ボリューム削除
docker compose down -v

# コンテナ + イメージ削除
docker compose down --rmi all

# 完全クリーンアップ
docker compose down -v --rmi all --remove-orphans
```

---

## 6. 本番環境デプロイ（準備中）

### 6.1 本番環境アーキテクチャ

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[NGINX Load Balancer<br/>HAProxy]
    end
    
    subgraph "Application Tier"
        APP1[App Instance 1<br/>Kubernetes Pod]
        APP2[App Instance 2<br/>Kubernetes Pod]
        APP3[App Instance 3<br/>Kubernetes Pod]
    end
    
    subgraph "Database Tier"
        DB_MASTER[(PostgreSQL Master)]
        DB_REPLICA1[(PostgreSQL Replica 1)]
        DB_REPLICA2[(PostgreSQL Replica 2)]
    end
    
    subgraph "Compute Tier"
        RAY_HEAD[Ray Head Node]
        RAY_WORKER1[Ray Worker 1]
        RAY_WORKER2[Ray Worker N]
    end
    
    subgraph "Storage Tier"
        S3[S3/MinIO<br/>Object Storage]
    end
    
    subgraph "Monitoring Tier"
        PROM[Prometheus]
        GRAF[Grafana]
        ALERT[Alertmanager]
    end
    
    LB --> APP1
    LB --> APP2
    LB --> APP3
    
    APP1 --> DB_MASTER
    APP2 --> DB_MASTER
    APP3 --> DB_MASTER
    
    DB_MASTER --> DB_REPLICA1
    DB_MASTER --> DB_REPLICA2
    
    APP1 --> RAY_HEAD
    APP2 --> RAY_HEAD
    APP3 --> RAY_HEAD
    
    RAY_HEAD --> RAY_WORKER1
    RAY_HEAD --> RAY_WORKER2
    
    APP1 --> S3
    APP2 --> S3
    APP3 --> S3
    
    PROM --> APP1
    PROM --> APP2
    PROM --> APP3
    PROM --> ALERT
    GRAF --> PROM
```

---

### 6.2 Kubernetesデプロイ（計画中）

#### 6.2.1 Helmチャート構成

```yaml
# values.yaml（抜粋）

replicaCount: 3

image:
  repository: your-registry/ts-forecasting
  tag: "1.0.0"
  pullPolicy: IfNotPresent

resources:
  limits:
    cpu: 4000m
    memory: 8Gi
    nvidia.com/gpu: 1
  requests:
    cpu: 2000m
    memory: 4Gi
    nvidia.com/gpu: 1

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

postgresql:
  enabled: true
  auth:
    username: ts_user
    database: ts_forecast_system
  primary:
    persistence:
      size: 100Gi
  readReplicas:
    replicaCount: 2

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: ts-forecast.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: ts-forecast-tls
      hosts:
        - ts-forecast.example.com
```

---

#### 6.2.2 デプロイコマンド

```bash
# Helmリポジトリ追加
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# 名前空間作成
kubectl create namespace ts-forecast

# Helmチャートデプロイ
helm install ts-forecast ./helm/ts-forecast \
  --namespace ts-forecast \
  --values values.yaml \
  --wait

# デプロイ確認
kubectl get pods -n ts-forecast
kubectl get services -n ts-forecast
kubectl get ingress -n ts-forecast

# ログ確認
kubectl logs -n ts-forecast -l app=ts-forecast --tail=100 -f
```

---

### 6.3 クラウドプロバイダー対応

#### 6.3.1 AWS

```bash
# EKSクラスター作成
eksctl create cluster \
  --name ts-forecast-cluster \
  --region us-west-2 \
  --nodegroup-name standard-workers \
  --node-type m5.2xlarge \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 10 \
  --managed

# RDS PostgreSQL作成
aws rds create-db-instance \
  --db-instance-identifier ts-forecast-db \
  --db-instance-class db.r5.xlarge \
  --engine postgres \
  --engine-version 14.9 \
  --master-username admin \
  --master-user-password <password> \
  --allocated-storage 100 \
  --storage-type gp3 \
  --multi-az

# S3バケット作成
aws s3 mb s3://ts-forecast-artifacts
aws s3api put-bucket-versioning \
  --bucket ts-forecast-artifacts \
  --versioning-configuration Status=Enabled
```

---

#### 6.3.2 GCP

```bash
# GKEクラスター作成
gcloud container clusters create ts-forecast-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-4 \
  --enable-autoscaling \
  --min-nodes 2 \
  --max-nodes 10

# Cloud SQL PostgreSQL作成
gcloud sql instances create ts-forecast-db \
  --database-version=POSTGRES_14 \
  --tier=db-n1-standard-4 \
  --region=us-central1 \
  --enable-bin-log \
  --backup

# Cloud Storage作成
gsutil mb -l us-central1 gs://ts-forecast-artifacts
gsutil versioning set on gs://ts-forecast-artifacts
```

---

#### 6.3.3 Azure

```bash
# AKSクラスター作成
az aks create \
  --resource-group ts-forecast-rg \
  --name ts-forecast-cluster \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --enable-cluster-autoscaler \
  --min-count 2 \
  --max-count 10 \
  --generate-ssh-keys

# Azure Database for PostgreSQL作成
az postgres flexible-server create \
  --resource-group ts-forecast-rg \
  --name ts-forecast-db \
  --location eastus \
  --admin-user admin \
  --admin-password <password> \
  --sku-name Standard_D4s_v3 \
  --version 14 \
  --storage-size 128

# Blob Storage作成
az storage account create \
  --name tsforecaststorage \
  --resource-group ts-forecast-rg \
  --location eastus \
  --sku Standard_LRS \
  --enable-versioning
```

---

## 7. 環境変数設定

### 7.1 環境変数一覧

#### 7.1.1 必須環境変数

| 変数名 | 説明 | デフォルト値 | 例 |
|-------|------|------------|-----|
| `DATABASE_URL` | データベース接続URL | なし | `postgresql://user:pass@localhost:5432/db` |
| `DATA_DIR` | データディレクトリ | `./data` | `/app/data` |
| `MODEL_DIR` | モデル保存ディレクトリ | `./models` | `/app/models` |
| `OUTPUT_DIR` | 出力ディレクトリ | `./outputs` | `/app/outputs` |
| `LOG_DIR` | ログディレクトリ | `./logs` | `/app/logs` |

---

#### 7.1.2 オプション環境変数

| 変数名 | 説明 | デフォルト値 | 例 |
|-------|------|------------|-----|
| `MAX_PARALLEL_RUNS` | 最大並列実行数 | `4` | `10` |
| `DEFAULT_BACKEND` | 計算バックエンド | `cpu` | `cuda` |
| `ENABLE_GPU` | GPU使用有効化 | `false` | `true` |
| `GPU_MEMORY_LIMIT` | GPU メモリ制限 | `0.8` | `0.9` |
| `LOG_LEVEL` | ログレベル | `INFO` | `DEBUG` |
| `LOG_FORMAT` | ログフォーマット | `json` | `text` |
| `ENABLE_MLFLOW` | MLflow有効化 | `false` | `true` |
| `MLFLOW_TRACKING_URI` | MLflow URI | なし | `http://localhost:5000` |
| `ENABLE_WANDB` | W&B有効化 | `false` | `true` |
| `WANDB_API_KEY` | W&B APIキー | なし | `your_key` |
| `ENABLE_RAY` | Ray有効化 | `false` | `true` |
| `RAY_ADDRESS` | Ray クラスター | `auto` | `ray://localhost:10001` |

---

### 7.2 環境別設定

#### 7.2.1 開発環境

```bash
# .env.development

# Database
DATABASE_URL=postgresql://dev_user:dev_pass@localhost:5432/ts_forecast_dev
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10

# Paths
DATA_DIR=./data
MODEL_DIR=./models
OUTPUT_DIR=./outputs
LOG_DIR=./logs

# Execution
MAX_PARALLEL_RUNS=2
DEFAULT_BACKEND=cpu
ENABLE_GPU=false

# Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=text
ENABLE_FILE_LOGGING=true

# Optional Services
ENABLE_MLFLOW=false
ENABLE_WANDB=false
ENABLE_RAY=false
```

---

#### 7.2.2 ステージング環境

```bash
# .env.staging

# Database
DATABASE_URL=postgresql://staging_user:staging_pass@staging-db:5432/ts_forecast_staging
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Paths
DATA_DIR=/data
MODEL_DIR=/models
OUTPUT_DIR=/outputs
LOG_DIR=/logs

# Execution
MAX_PARALLEL_RUNS=8
DEFAULT_BACKEND=cuda
ENABLE_GPU=true
GPU_MEMORY_LIMIT=0.8

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
ENABLE_FILE_LOGGING=true

# Optional Services
ENABLE_MLFLOW=true
MLFLOW_TRACKING_URI=http://mlflow:5000
ENABLE_WANDB=false
ENABLE_RAY=true
RAY_ADDRESS=ray://ray-head:10001
```

---

#### 7.2.3 本番環境

```bash
# .env.production

# Database (環境変数やSecretから取得)
DATABASE_URL=${DB_CONNECTION_STRING}
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40
DATABASE_POOL_TIMEOUT=30

# Paths
DATA_DIR=/mnt/data
MODEL_DIR=/mnt/models
OUTPUT_DIR=/mnt/outputs
LOG_DIR=/mnt/logs

# Execution
MAX_PARALLEL_RUNS=10
DEFAULT_BACKEND=cuda
ENABLE_GPU=true
GPU_MEMORY_LIMIT=0.9

# Logging
LOG_LEVEL=WARNING
LOG_FORMAT=json
ENABLE_FILE_LOGGING=true

# Optional Services
ENABLE_MLFLOW=true
MLFLOW_TRACKING_URI=${MLFLOW_URI}
MLFLOW_S3_ENDPOINT_URL=${S3_ENDPOINT}
AWS_ACCESS_KEY_ID=${AWS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_KEY}

ENABLE_WANDB=true
WANDB_API_KEY=${WANDB_KEY}
WANDB_PROJECT=ts-forecast-prod

ENABLE_RAY=true
RAY_ADDRESS=ray://${RAY_HEAD_HOST}:10001
RAY_NAMESPACE=production
```

---

### 7.3 環境変数管理ツール

#### 7.3.1 direnv

```bash
# direnvインストール
brew install direnv  # macOS
# または
sudo apt install direnv  # Ubuntu

# シェル設定追加
echo 'eval "$(direnv hook bash)"' >> ~/.bashrc
source ~/.bashrc

# .envrcファイル作成
cat > .envrc << 'EOF'
# 開発環境用
export DATABASE_URL=postgresql://dev_user:dev_pass@localhost:5432/ts_forecast_dev
export DATA_DIR=./data
export LOG_LEVEL=DEBUG
EOF

# 許可
direnv allow .
```

---

#### 7.3.2 AWS Systems Manager Parameter Store

```bash
# パラメータ登録
aws ssm put-parameter \
  --name /ts-forecast/prod/database-url \
  --value "postgresql://user:pass@host:5432/db" \
  --type SecureString \
  --tier Advanced

# パラメータ取得
aws ssm get-parameter \
  --name /ts-forecast/prod/database-url \
  --with-decryption \
  --query 'Parameter.Value' \
  --output text
```

---

#### 7.3.3 Kubernetes Secrets

```bash
# Secret作成
kubectl create secret generic ts-forecast-secrets \
  --from-literal=database-url='postgresql://user:pass@host:5432/db' \
  --from-literal=mlflow-uri='http://mlflow:5000' \
  --from-literal=wandb-api-key='your_key' \
  --namespace ts-forecast

# Secret確認
kubectl get secrets -n ts-forecast
kubectl describe secret ts-forecast-secrets -n ts-forecast

# アプリケーションでの使用（deployment.yaml）
# envFrom:
#   - secretRef:
#       name: ts-forecast-secrets
```

---

## 8. データベース設定

### 8.1 PostgreSQL設定最適化

#### 8.1.1 postgresql.conf

```ini
# ========================================
# Connection Settings
# ========================================
max_connections = 200
superuser_reserved_connections = 3

# ========================================
# Memory Settings
# ========================================
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
work_mem = 64MB

# ========================================
# WAL Settings
# ========================================
wal_buffers = 16MB
min_wal_size = 2GB
max_wal_size = 8GB
checkpoint_completion_target = 0.9

# ========================================
# Query Tuning
# ========================================
random_page_cost = 1.1
effective_io_concurrency = 200
default_statistics_target = 100

# ========================================
# Logging
# ========================================
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_min_duration_statement = 1000
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '

# ========================================
# Autovacuum
# ========================================
autovacuum = on
autovacuum_max_workers = 3
autovacuum_naptime = 10s
```

---

#### 8.1.2 pg_hba.conf

```ini
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Local connections
local   all             all                                     peer

# IPv4 local connections
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             172.25.0.0/16           scram-sha-256

# IPv6 local connections
host    all             all             ::1/128                 scram-sha-256

# Allow replication connections
host    replication     replicator      172.25.0.0/16           scram-sha-256
```

---

### 8.2 データベーススキーマ

#### 8.2.1 初期化SQLスクリプト

```sql
-- scripts/db/init.sql

-- ========================================
-- Extensions
-- ========================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ========================================
-- Schemas
-- ========================================
CREATE SCHEMA IF NOT EXISTS ts_forecast;
SET search_path TO ts_forecast, public;

-- ========================================
-- Tables
-- ========================================

-- Experiments
CREATE TABLE IF NOT EXISTS experiments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Runs
CREATE TABLE IF NOT EXISTS runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    experiment_id UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    run_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('running', 'completed', 'failed', 'cancelled')),
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    parameters JSONB,
    metrics JSONB,
    artifacts JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(experiment_id, run_name)
);

-- Models
CREATE TABLE IF NOT EXISTS models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    model_name VARCHAR(255) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    model_path TEXT NOT NULL,
    model_size_bytes BIGINT,
    hyperparameters JSONB,
    training_metrics JSONB,
    validation_metrics JSONB,
    test_metrics JSONB,
    is_production BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Predictions
CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    prediction_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    input_data JSONB NOT NULL,
    predictions JSONB NOT NULL,
    prediction_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- Indexes
-- ========================================

-- Experiments
CREATE INDEX idx_experiments_name ON experiments(name);
CREATE INDEX idx_experiments_created_at ON experiments(created_at);

-- Runs
CREATE INDEX idx_runs_experiment_id ON runs(experiment_id);
CREATE INDEX idx_runs_status ON runs(status);
CREATE INDEX idx_runs_start_time ON runs(start_time);
CREATE INDEX idx_runs_parameters ON runs USING GIN (parameters);
CREATE INDEX idx_runs_metrics ON runs USING GIN (metrics);

-- Models
CREATE INDEX idx_models_run_id ON models(run_id);
CREATE INDEX idx_models_name_version ON models(model_name, model_version);
CREATE INDEX idx_models_is_production ON models(is_production) WHERE is_production = TRUE;
CREATE INDEX idx_models_created_at ON models(created_at);

-- Predictions
CREATE INDEX idx_predictions_model_id ON predictions(model_id);
CREATE INDEX idx_predictions_time ON predictions(prediction_time);
CREATE INDEX idx_predictions_input ON predictions USING GIN (input_data);

-- ========================================
-- Functions
-- ========================================

-- Updated_at自動更新トリガー関数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers
CREATE TRIGGER update_experiments_updated_at
    BEFORE UPDATE ON experiments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_runs_updated_at
    BEFORE UPDATE ON runs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_models_updated_at
    BEFORE UPDATE ON models
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- Views
-- ========================================

-- 最新の実験概要
CREATE OR REPLACE VIEW v_latest_experiments AS
SELECT
    e.id,
    e.name,
    e.description,
    COUNT(r.id) as total_runs,
    SUM(CASE WHEN r.status = 'completed' THEN 1 ELSE 0 END) as completed_runs,
    SUM(CASE WHEN r.status = 'failed' THEN 1 ELSE 0 END) as failed_runs,
    SUM(CASE WHEN r.status = 'running' THEN 1 ELSE 0 END) as running_runs,
    MAX(r.start_time) as last_run_time,
    e.created_at,
    e.updated_at
FROM experiments e
LEFT JOIN runs r ON e.id = r.experiment_id
GROUP BY e.id, e.name, e.description, e.created_at, e.updated_at
ORDER BY e.updated_at DESC;

-- 本番モデル一覧
CREATE OR REPLACE VIEW v_production_models AS
SELECT
    m.id,
    m.model_name,
    m.model_version,
    m.model_path,
    m.training_metrics,
    m.validation_metrics,
    m.test_metrics,
    r.run_name,
    e.name as experiment_name,
    m.created_at,
    m.updated_at
FROM models m
JOIN runs r ON m.run_id = r.id
JOIN experiments e ON r.experiment_id = e.id
WHERE m.is_production = TRUE
ORDER BY m.created_at DESC;

-- ========================================
-- Grants
-- ========================================

-- アプリケーションユーザーに権限付与
GRANT USAGE ON SCHEMA ts_forecast TO ts_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ts_forecast TO ts_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA ts_forecast TO ts_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA ts_forecast TO ts_user;

-- ========================================
-- Comments
-- ========================================

COMMENT ON SCHEMA ts_forecast IS 'Time Series Forecasting System schema';
COMMENT ON TABLE experiments IS '実験管理テーブル';
COMMENT ON TABLE runs IS '実行管理テーブル';
COMMENT ON TABLE models IS 'モデル管理テーブル';
COMMENT ON TABLE predictions IS '予測結果テーブル';
```

---

### 8.3 マイグレーション管理

#### 8.3.1 Alembic設定

```python
# alembic/env.py

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import your models' MetaData object
from nf_auto_runner.db import Base
target_metadata = Base.metadata

# Override sqlalchemy.url with environment variable
config.set_main_option('sqlalchemy.url', os.getenv('DATABASE_URL'))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

#### 8.3.2 マイグレーション実行

```bash
# マイグレーション履歴確認
alembic history --verbose

# 現在のバージョン確認
alembic current

# 新しいマイグレーション作成
alembic revision --autogenerate -m "Add new table for feature X"

# マイグレーション適用
alembic upgrade head

# 特定バージョンへマイグレーション
alembic upgrade abc123

# ロールバック（1つ前）
alembic downgrade -1

# 特定バージョンへロールバック
alembic downgrade abc123

# 完全ロールバック
alembic downgrade base
```

---

### 8.4 バックアップ戦略

#### 8.4.1 論理バックアップ

```bash
# pg_dumpでフルバックアップ
pg_dump -h localhost -U postgres -d ts_forecast_system \
  -F c -b -v -f backup_$(date +%Y%m%d_%H%M%S).dump

# スキーマのみバックアップ
pg_dump -h localhost -U postgres -d ts_forecast_system \
  -s -F p -f schema_$(date +%Y%m%d).sql

# 特定テーブルのみバックアップ
pg_dump -h localhost -U postgres -d ts_forecast_system \
  -t ts_forecast.models -t ts_forecast.predictions \
  -F c -f models_backup_$(date +%Y%m%d).dump
```

---

#### 8.4.2 物理バックアップ（pg_basebackup）

```bash
# ベースバックアップ
pg_basebackup -h localhost -U postgres \
  -D /backup/base_$(date +%Y%m%d) \
  -Ft -z -P

# 継続的アーカイビング設定
# postgresql.conf に追加:
# wal_level = replica
# archive_mode = on
# archive_command = 'cp %p /backup/wal/%f'
```

---

#### 8.4.3 自動バックアップスクリプト

```bash
#!/bin/bash
# scripts/backup/backup_db.sh

set -e

# 設定
BACKUP_DIR="/backup/postgres"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/ts_forecast_${TIMESTAMP}.dump"

# ディレクトリ作成
mkdir -p "${BACKUP_DIR}"

# バックアップ実行
echo "Starting backup at $(date)"
pg_dump -h localhost -U postgres -d ts_forecast_system \
  -F c -b -v -f "${BACKUP_FILE}"

# 圧縮
gzip "${BACKUP_FILE}"
echo "Backup completed: ${BACKUP_FILE}.gz"

# 古いバックアップ削除
find "${BACKUP_DIR}" -name "ts_forecast_*.dump.gz" \
  -mtime +${RETENTION_DAYS} -delete
echo "Old backups cleaned up"

# S3にアップロード（オプション）
if [ -n "${AWS_S3_BUCKET}" ]; then
    aws s3 cp "${BACKUP_FILE}.gz" \
      "s3://${AWS_S3_BUCKET}/backups/postgres/"
    echo "Backup uploaded to S3"
fi

echo "Backup process finished at $(date)"
```

---

#### 8.4.4 cronジョブ設定

```bash
# crontab -e

# 毎日午前2時にバックアップ
0 2 * * * /path/to/scripts/backup/backup_db.sh >> /var/log/backup.log 2>&1

# 毎週日曜日午前3時にVACUUM
0 3 * * 0 psql -h localhost -U postgres -d ts_forecast_system -c "VACUUM ANALYZE;" >> /var/log/vacuum.log 2>&1
```

---

## 9. オプションサービス設定

### 9.1 MLflowセットアップ

#### 9.1.1 MLflowサーバー起動

```bash
# ローカル起動（SQLiteバックエンド）
mlflow server \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlruns \
  --host 0.0.0.0 \
  --port 5000

# PostgreSQLバックエンド
mlflow server \
  --backend-store-uri postgresql://user:pass@localhost:5432/mlflow \
  --default-artifact-root s3://mlflow-artifacts \
  --host 0.0.0.0 \
  --port 5000
```

---

#### 9.1.2 MLflow設定ファイル

```yaml
# conf/mlflow.yml

tracking:
  uri: ${MLFLOW_TRACKING_URI}
  experiment_name: ${MLFLOW_EXPERIMENT_NAME}
  run_name_prefix: "run"
  tags:
    project: "time-series-forecasting"
    version: "1.0.0"

artifacts:
  location: ${MLFLOW_ARTIFACT_ROOT}
  storage_type: "s3"  # s3, azure, gcs, local
  
logging:
  log_models: true
  log_params: true
  log_metrics: true
  log_artifacts: true
  log_system_metrics: true
  
autolog:
  disable: false
  log_input_examples: true
  log_model_signatures: true
  exclusive: false
```

---

### 9.2 Rayセットアップ

#### 9.2.1 Rayクラスター起動

```bash
# Rayヘッドノード起動
ray start --head \
  --dashboard-host=0.0.0.0 \
  --dashboard-port=8265 \
  --port=6379 \
  --num-cpus=8 \
  --num-gpus=1

# Rayワーカーノード起動
ray start \
  --address='ray-head-ip:6379' \
  --num-cpus=8 \
  --num-gpus=1

# クラスター状態確認
ray status
```

---

#### 9.2.2 Ray設定ファイル

```yaml
# conf/ray.yml

cluster:
  address: ${RAY_ADDRESS}
  namespace: ${RAY_NAMESPACE}
  runtime_env:
    pip:
      - neuralforecast
      - torch
      - pandas
    env_vars:
      OMP_NUM_THREADS: "1"

resources:
  num_cpus: 1
  num_gpus: 0
  memory: 4294967296  # 4GB
  
scheduling:
  placement_strategy: "SPREAD"
  max_pending_placement_groups: 100
  
autoscaling:
  enabled: true
  min_workers: 2
  max_workers: 10
  idle_timeout_minutes: 5
```

---

### 9.3 Weights & Biases (W&B)セットアップ

#### 9.3.1 W&Bログイン

```bash
# W&B APIキー設定
export WANDB_API_KEY=your_api_key

# またはログインコマンド
wandb login

# プロジェクト初期化
wandb init \
  --project time-series-forecasting \
  --entity your-team \
  --name experiment-1
```

---

#### 9.3.2 W&B設定ファイル

```yaml
# conf/wandb.yml

project: ${WANDB_PROJECT}
entity: ${WANDB_ENTITY}
name: ${WANDB_RUN_NAME}

config:
  log_frequency: 1
  save_code: true
  log_model: true
  log_dataset: false

tags:
  - time-series
  - forecasting
  - production

notes: "Time series forecasting experiment"

mode: "online"  # online, offline, disabled
```

---

## 10. セキュリティ設定

### 10.1 秘密情報管理

#### 10.1.1 環境変数による管理

```bash
# .env（絶対にGitにコミットしない）
DATABASE_PASSWORD=strong_password_here
MLFLOW_TRACKING_TOKEN=secret_token
WANDB_API_KEY=secret_api_key
AWS_SECRET_ACCESS_KEY=aws_secret
```

**.gitignore**:

```
# 環境変数
.env
.env.*
!.env.example

# 秘密鍵
*.pem
*.key
secrets/
```

---

#### 10.1.2 AWS Secrets Managerの使用

```python
# scripts/utils/get_secret.py

import boto3
from botocore.exceptions import ClientError
import json


def get_secret(secret_name: str, region_name: str = "us-west-2") -> dict:
    """
    AWS Secrets Managerから秘密情報を取得
    """
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e

    if 'SecretString' in response:
        secret = response['SecretString']
        return json.loads(secret)
    else:
        raise ValueError("Secret not found")


# 使用例
if __name__ == "__main__":
    secrets = get_secret("ts-forecast/prod/db-credentials")
    DATABASE_URL = f"postgresql://{secrets['username']}:{secrets['password']}@" \
                   f"{secrets['host']}:{secrets['port']}/{secrets['database']}"
    print(DATABASE_URL)
```

---

### 10.2 ネットワークセキュリティ

#### 10.2.1 ファイアウォール設定

```bash
# UFW（Ubuntu）
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 8000/tcp  # API
sudo ufw allow 5432/tcp from 172.25.0.0/16  # PostgreSQL (Docker network only)
sudo ufw enable

# iptables
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 5432 -s 172.25.0.0/16 -j ACCEPT
sudo iptables -A INPUT -j DROP
```

---

#### 10.2.2 SSL/TLS証明書設定

```bash
# Let's Encrypt証明書取得
sudo apt install certbot
sudo certbot certonly --standalone -d ts-forecast.example.com

# 証明書の場所
# /etc/letsencrypt/live/ts-forecast.example.com/fullchain.pem
# /etc/letsencrypt/live/ts-forecast.example.com/privkey.pem

# 自動更新設定
sudo crontab -e
# 0 3 * * * certbot renew --quiet --post-hook "systemctl reload nginx"
```

**NGINX SSL設定**:

```nginx
server {
    listen 443 ssl http2;
    server_name ts-forecast.example.com;

    ssl_certificate /etc/letsencrypt/live/ts-forecast.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ts-forecast.example.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

### 10.3 認証・認可

#### 10.3.1 JWT認証設定

```python
# src/nf_auto_runner/app/auth.py

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os

# 設定
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """パスワード検証"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """パスワードハッシュ化"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """JWTトークン作成"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """現在のユーザー取得"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # ユーザー情報取得（DB from）
    # ...
    
    return {"username": username}
```

---

## 11. 監視・ロギング設定

### 11.1 Prometheus設定

#### 11.1.1 prometheus.yml

```yaml
# monitoring/prometheus/prometheus.yml

global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'ts-forecast'
    environment: 'production'

scrape_configs:
  # Application
  - job_name: 'ts-forecast-app'
    static_configs:
      - targets: ['app:8000']
    metrics_path: '/metrics'
    
  # PostgreSQL
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
    
  # Ray
  - job_name: 'ray'
    static_configs:
      - targets: ['ray-head:8265']
    metrics_path: '/metrics'
    
  # Node Exporter
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - '/etc/prometheus/rules/*.yml'
```

---

#### 11.1.2 アラートルール

```yaml
# monitoring/prometheus/rules/alerts.yml

groups:
  - name: application_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} req/s"
      
      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes / 1e9 > 8
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value }}GB"
      
      - alert: DatabaseConnectionPoolExhausted
        expr: db_connection_pool_active / db_connection_pool_size > 0.9
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Database connection pool almost exhausted"
```

---

### 11.2 Grafanaダッシュボード

#### 11.2.1 データソース設定

```yaml
# monitoring/grafana/datasources/prometheus.yml

apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
    jsonData:
      timeInterval: "15s"
      queryTimeout: "60s"
```

---

#### 11.2.2 ダッシュボード定義

```json
{
  "dashboard": {
    "title": "Time Series Forecasting - System Overview",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{path}}"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx errors"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Active Runs",
        "targets": [
          {
            "expr": "ts_forecast_active_runs",
            "legendFormat": "Active"
          }
        ],
        "type": "stat"
      },
      {
        "title": "Memory Usage",
        "targets": [
          {
            "expr": "process_resident_memory_bytes / 1e9",
            "legendFormat": "RSS (GB)"
          }
        ],
        "type": "graph"
      }
    ]
  }
}
```

---

### 11.3 ログ管理

#### 11.3.1 ログ設定

```python
# src/nf_auto_runner/utils/logging_config.py

import logging
import logging.config
from pythonjsonlogger import jsonlogger
import os


def setup_logging():
    """ログ設定のセットアップ"""
    
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_format = os.getenv("LOG_FORMAT", "json")
    log_dir = os.getenv("LOG_DIR", "./logs")
    
    os.makedirs(f"{log_dir}/app", exist_ok=True)
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": jsonlogger.JsonFormatter,
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
            },
            "text": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": log_format,
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": log_format,
                "filename": f"{log_dir}/app/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 10
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": log_format,
                "filename": f"{log_dir}/app/error.log",
                "maxBytes": 10485760,
                "backupCount": 10,
                "level": "ERROR"
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["console", "file", "error_file"]
        },
        "loggers": {
            "uvicorn": {"level": "INFO"},
            "sqlalchemy.engine": {"level": "WARNING"},
            "alembic": {"level": "INFO"}
        }
    }
    
    logging.config.dictConfig(config)
    logger = logging.getLogger(__name__)
    logger.info("Logging configured", extra={"log_level": log_level, "log_format": log_format})
```

---

#### 11.3.2 ログローテーション

```bash
# /etc/logrotate.d/ts-forecast

/app/logs/**/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 appuser appuser
    sharedscripts
    postrotate
        # シグナル送信でログファイル再オープン
        /usr/bin/killall -SIGUSR1 python3 || true
    endscript
}
```

---

## 12. バックアップ・復旧手順

### 12.1 バックアップ戦略

#### 12.1.1 バックアップスケジュール

| 対象 | 頻度 | 保持期間 | 方法 |
|-----|------|---------|------|
| **データベース** | 毎日 | 30日 | pg_dump + S3 |
| **モデルファイル** | 毎週 | 90日 | rsync + S3 |
| **設定ファイル** | 変更時 | 永続 | Git |
| **ログ** | 毎週 | 90日 | tar.gz + S3 |

---

#### 12.1.2 バックアップスクリプト

```bash
#!/bin/bash
# scripts/backup/full_backup.sh

set -euo pipefail

# 設定
BACKUP_ROOT="/backup"
S3_BUCKET="s3://ts-forecast-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# ログ設定
LOG_FILE="/var/log/backup_${TIMESTAMP}.log"
exec 1> >(tee -a "${LOG_FILE}")
exec 2>&1

echo "========================================="
echo "Starting backup at $(date)"
echo "========================================="

# データベースバックアップ
echo "Backing up database..."
DB_BACKUP="${BACKUP_ROOT}/db/ts_forecast_${TIMESTAMP}.dump"
mkdir -p "${BACKUP_ROOT}/db"
pg_dump -h localhost -U postgres -d ts_forecast_system \
    -F c -b -v -f "${DB_BACKUP}"
gzip "${DB_BACKUP}"
echo "Database backup completed: ${DB_BACKUP}.gz"

# モデルファイルバックアップ
echo "Backing up models..."
MODEL_BACKUP="${BACKUP_ROOT}/models/models_${TIMESTAMP}.tar.gz"
mkdir -p "${BACKUP_ROOT}/models"
tar -czf "${MODEL_BACKUP}" -C /app models/
echo "Models backup completed: ${MODEL_BACKUP}"

# ログバックアップ
echo "Backing up logs..."
LOG_BACKUP="${BACKUP_ROOT}/logs/logs_${TIMESTAMP}.tar.gz"
mkdir -p "${BACKUP_ROOT}/logs"
tar -czf "${LOG_BACKUP}" -C /app logs/
echo "Logs backup completed: ${LOG_BACKUP}"

# S3へアップロード
if [ -n "${S3_BUCKET}" ]; then
    echo "Uploading to S3..."
    aws s3 sync "${BACKUP_ROOT}" "${S3_BUCKET}/${TIMESTAMP}/" \
        --storage-class STANDARD_IA
    echo "S3 upload completed"
fi

# 古いバックアップ削除（30日以上前）
echo "Cleaning up old backups..."
find "${BACKUP_ROOT}" -type f -mtime +30 -delete
echo "Cleanup completed"

echo "========================================="
echo "Backup completed successfully at $(date)"
echo "========================================="
```

---

### 12.2 復旧手順

#### 12.2.1 データベース復旧

```bash
#!/bin/bash
# scripts/restore/restore_db.sh

set -euo pipefail

# 引数チェック
if [ $# -ne 1 ]; then
    echo "Usage: $0 <backup_file.dump.gz>"
    exit 1
fi

BACKUP_FILE="$1"

echo "Starting database restore from ${BACKUP_FILE}"

# バックアップファイル存在確認
if [ ! -f "${BACKUP_FILE}" ]; then
    echo "Error: Backup file not found"
    exit 1
fi

# 解凍
TEMP_DIR=$(mktemp -d)
gunzip -c "${BACKUP_FILE}" > "${TEMP_DIR}/backup.dump"

# 現在のDBのバックアップ
echo "Creating safety backup of current database..."
pg_dump -h localhost -U postgres -d ts_forecast_system \
    -F c -b -f "${TEMP_DIR}/safety_backup.dump"

# データベース削除・再作成
echo "Dropping and recreating database..."
psql -h localhost -U postgres << EOF
DROP DATABASE IF EXISTS ts_forecast_system;
CREATE DATABASE ts_forecast_system;
GRANT ALL PRIVILEGES ON DATABASE ts_forecast_system TO ts_user;
EOF

# リストア
echo "Restoring database..."
pg_restore -h localhost -U postgres -d ts_forecast_system \
    -v "${TEMP_DIR}/backup.dump"

# 確認
echo "Verifying restore..."
psql -h localhost -U postgres -d ts_forecast_system -c "
    SELECT COUNT(*) FROM experiments;
    SELECT COUNT(*) FROM runs;
    SELECT COUNT(*) FROM models;
"

# クリーンアップ
rm -rf "${TEMP_DIR}"

echo "Database restore completed successfully"
```

---

#### 12.2.2 モデルファイル復旧

```bash
#!/bin/bash
# scripts/restore/restore_models.sh

set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: $0 <models_backup.tar.gz>"
    exit 1
fi

BACKUP_FILE="$1"
RESTORE_DIR="/app/models"

echo "Starting models restore from ${BACKUP_FILE}"

# 現在のモデルをバックアップ
if [ -d "${RESTORE_DIR}" ]; then
    echo "Backing up current models..."
    mv "${RESTORE_DIR}" "${RESTORE_DIR}.old_$(date +%Y%m%d_%H%M%S)"
fi

# リストア
echo "Restoring models..."
mkdir -p "${RESTORE_DIR}"
tar -xzf "${BACKUP_FILE}" -C "${RESTORE_DIR}" --strip-components=1

# 権限設定
chown -R appuser:appuser "${RESTORE_DIR}"
chmod -R 755 "${RESTORE_DIR}"

# 確認
echo "Verifying restore..."
ls -lh "${RESTORE_DIR}"

echo "Models restore completed successfully"
```

---

#### 12.2.3 災害復旧（DR）手順

**完全な復旧手順**:

```bash
#!/bin/bash
# scripts/restore/disaster_recovery.sh

set -euo pipefail

echo "========================================="
echo "Starting Disaster Recovery Process"
echo "========================================="

# S3から最新バックアップをダウンロード
echo "Downloading latest backups from S3..."
BACKUP_DIR="/tmp/dr_restore"
mkdir -p "${BACKUP_DIR}"

aws s3 sync "s3://ts-forecast-backups/" "${BACKUP_DIR}/" \
    --exclude "*" \
    --include "*/ts_forecast_*.dump.gz" \
    --include "*/models_*.tar.gz"

# 最新のバックアップファイルを特定
LATEST_DB=$(find "${BACKUP_DIR}" -name "ts_forecast_*.dump.gz" | sort -r | head -n1)
LATEST_MODELS=$(find "${BACKUP_DIR}" -name "models_*.tar.gz" | sort -r | head -n1)

echo "Latest DB backup: ${LATEST_DB}"
echo "Latest Models backup: ${LATEST_MODELS}"

# データベース復旧
echo "Restoring database..."
./scripts/restore/restore_db.sh "${LATEST_DB}"

# モデル復旧
echo "Restoring models..."
./scripts/restore/restore_models.sh "${LATEST_MODELS}"

# サービス再起動
echo "Restarting services..."
docker compose restart app

# ヘルスチェック
echo "Performing health checks..."
sleep 10
curl -f http://localhost:8000/health || exit 1

echo "========================================="
echo "Disaster Recovery Completed Successfully"
echo "========================================="
```

---

## 13. トラブルシューティング

### 13.1 よくある問題と解決策

#### 13.1.1 データベース接続エラー

**問題**:
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

**解決策**:

```bash
# 1. PostgreSQLサービス確認
sudo systemctl status postgresql
docker ps | grep postgres

# 2. 接続テスト
psql -h localhost -U postgres -d ts_forecast_system

# 3. pg_hba.confを確認
sudo cat /etc/postgresql/14/main/pg_hba.conf

# 4. ファイアウォール確認
sudo ufw status
sudo netstat -tulpn | grep 5432

# 5. 環境変数確認
echo $DATABASE_URL
```

---

#### 13.1.2 メモリ不足エラー

**問題**:
```
RuntimeError: CUDA out of memory
```

**解決策**:

```bash
# 1. GPU メモリ使用状況確認
nvidia-smi

# 2. 環境変数で制限
export GPU_MEMORY_LIMIT=0.7

# 3. バッチサイズ削減
# conf/config.yaml
batch_size: 32  # 64から削減

# 4. モデル並列実行数削減
export MAX_PARALLEL_RUNS=2

# 5. システムメモリ確認
free -h
```

---

#### 13.1.3 パッケージ依存関係エラー

**問題**:
```
ModuleNotFoundError: No module named 'neuralforecast'
```

**解決策**:

```bash
# 1. 仮想環境の確認
which python
python --version

# 2. パッケージ再インストール
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# 3. パッケージ確認
pip list | grep neuralforecast
pip check

# 4. 環境のクリーン
pip cache purge
rm -rf ~/.cache/pip

# 5. 仮想環境再作成
deactivate
rm -rf .venv
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

#### 13.1.4 Docker コンテナ起動失敗

**問題**:
```
Error response from daemon: driver failed programming external connectivity
```

**解決策**:

```bash
# 1. ポート使用状況確認
sudo lsof -i :5432
sudo lsof -i :8000

# 2. 既存コンテナ停止
docker compose down

# 3. ポート解放
sudo kill -9 <PID>

# 4. Dockerネットワーク再作成
docker network prune
docker network create ts-network

# 5. コンテナ再起動
docker compose up -d --force-recreate
```

---

### 13.2 ログ確認方法

#### 13.2.1 アプリケーションログ

```bash
# ローカル環境
tail -f logs/app/app.log

# Docker環境
docker compose logs -f app

# 特定期間のログ
docker compose logs --since 1h app

# エラーログのみ
grep ERROR logs/app/app.log
docker compose logs app 2>&1 | grep ERROR
```

---

#### 13.2.2 データベースログ

```bash
# PostgreSQLログ確認
sudo tail -f /var/log/postgresql/postgresql-14-main.log

# Docker環境
docker compose logs -f postgres

# スロークエリ確認
sudo grep "duration:" /var/log/postgresql/postgresql-14-main.log | \
    grep -E "duration: [0-9]{4,}" | \
    sort -t: -k2 -n
```

---

#### 13.2.3 システムログ

```bash
# systemdログ
sudo journalctl -u ts-forecast -f

# Dockerログ
docker logs ts-app -f --tail=100

# カーネルログ
dmesg | tail -100
```

---

### 13.3 パフォーマンス診断

#### 13.3.1 プロファイリング

```python
# scripts/utils/profile_app.py

import cProfile
import pstats
import io
from pstats import SortKey


def profile_function(func, *args, **kwargs):
    """関数のプロファイリング"""
    pr = cProfile.Profile()
    pr.enable()
    
    result = func(*args, **kwargs)
    
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats(SortKey.CUMULATIVE)
    ps.print_stats()
    
    print(s.getvalue())
    return result


# 使用例
if __name__ == "__main__":
    from nf_auto_runner.app.main import run_experiment
    profile_function(run_experiment, config_path="conf/config.yaml")
```

---

#### 13.3.2 メモリプロファイリング

```python
# scripts/utils/memory_profile.py

from memory_profiler import profile
import tracemalloc


@profile
def memory_intensive_function():
    """メモリ使用量の測定"""
    # 処理
    pass


def trace_memory():
    """メモリ使用量トレース"""
    tracemalloc.start()
    
    # 処理
    memory_intensive_function()
    
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    
    print("[ Top 10 Memory Consumers ]")
    for stat in top_stats[:10]:
        print(stat)
    
    tracemalloc.stop()


if __name__ == "__main__":
    trace_memory()
```

---

## 14. 付録

### 14.1 チェックリスト

#### 14.1.1 デプロイ前チェックリスト

```markdown
## ローカル環境

- [ ] Python 3.11インストール済み
- [ ] 仮想環境作成済み
- [ ] 依存関係インストール済み
- [ ] PostgreSQL起動確認
- [ ] データベース作成完了
- [ ] 環境変数設定完了
- [ ] マイグレーション適用済み
- [ ] テスト実行成功
- [ ] サンプルデータで動作確認

## Docker環境

- [ ] Docker/Docker Composeインストール済み
- [ ] .envファイル作成済み
- [ ] docker-compose.ymlレビュー完了
- [ ] イメージビルド成功
- [ ] コンテナ起動成功
- [ ] ヘルスチェック通過
- [ ] API動作確認
- [ ] データベース接続確認

## 本番環境

- [ ] インフラプロビジョニング完了
- [ ] SSL/TLS証明書設定済み
- [ ] ファイアウォール設定完了
- [ ] 監視・アラート設定完了
- [ ] バックアップ設定完了
- [ ] ドキュメント更新済み
- [ ] ロールバック手順確認済み
- [ ] 負荷テスト実施済み
```

---

#### 14.1.2 セキュリティチェックリスト

```markdown
## 認証・認可

- [ ] 秘密情報は環境変数で管理
- [ ] .envファイルは.gitignore追加済み
- [ ] JWT秘密鍵は強力な値に設定
- [ ] APIエンドポイントに認証実装
- [ ] 権限チェック実装

## ネットワーク

- [ ] 不要なポートは閉じる
- [ ] SSL/TLS証明書設定
- [ ] ファイアウォール有効化
- [ ] VPN/Bastionホスト経由でアクセス

## データ

- [ ] データベースパスワードは強力
- [ ] PII データの匿名化実装
- [ ] バックアップは暗号化
- [ ] アクセスログ記録

## コード

- [ ] 依存関係の脆弱性スキャン実施
- [ ] セキュリティパッチ適用済み
- [ ] Secretsのハードコードなし
- [ ] SQL インジェクション対策済み
```

---

### 14.2 コマンドリファレンス

#### 14.2.1 よく使うコマンド

```bash
# ========================================
# アプリケーション
# ========================================

# 学習実行
python -m nf_auto_runner.app.main \
  --data-path data/sample.csv \
  --models NHITS,PatchTST \
  --horizons 24

# API起動
uvicorn nf_auto_runner.app.api:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload

# ========================================
# データベース
# ========================================

# マイグレーション
alembic upgrade head
alembic downgrade -1
alembic revision --autogenerate -m "message"

# バックアップ
pg_dump -h localhost -U postgres -d ts_forecast_system \
  -F c -b -f backup.dump

# リストア
pg_restore -h localhost -U postgres -d ts_forecast_system \
  -v backup.dump

# ========================================
# Docker
# ========================================

# 起動
docker compose up -d
docker compose --profile mlflow --profile ray up -d

# 停止
docker compose down
docker compose down -v  # ボリューム削除

# ログ
docker compose logs -f app
docker compose logs --tail=100 postgres

# 再起動
docker compose restart app

# ========================================
# テスト
# ========================================

# 全テスト
pytest tests/ -v

# カバレッジ
pytest tests/ --cov=src --cov-report=html

# 特定テスト
pytest tests/unit/test_config.py::test_config_load -v

# ========================================
# コード品質
# ========================================

# Lint
pylint src/nf_auto_runner/
flake8 src/ tests/
mypy src/nf_auto_runner/ --strict

# Format
black src/ tests/
isort src/ tests/

# セキュリティスキャン
bandit -r src/nf_auto_runner/
```

---

### 14.3 トラブルシューティングフローチャート

```mermaid
graph TD
    A[問題発生] --> B{エラーの種類は?}
    
    B -->|接続エラー| C[データベース起動確認]
    C --> D[環境変数確認]
    D --> E[ファイアウォール確認]
    
    B -->|メモリエラー| F[GPU/CPUメモリ確認]
    F --> G[バッチサイズ調整]
    G --> H[並列数削減]
    
    B -->|パッケージエラー| I[仮想環境確認]
    I --> J[依存関係再インストール]
    J --> K[Python バージョン確認]
    
    B -->|Dockerエラー| L[コンテナ状態確認]
    L --> M[ログ確認]
    M --> N[ポート競合確認]
    
    E --> O{解決した?}
    H --> O
    K --> O
    N --> O
    
    O -->|Yes| P[完了]
    O -->|No| Q[サポートに連絡]
```

---

### 14.4 参考資料

#### 14.4.1 公式ドキュメント

- **NeuralForecast**: https://nixtla.github.io/neuralforecast/
- **FastAPI**: https://fastapi.tiangolo.com/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Docker**: https://docs.docker.com/
- **MLflow**: https://mlflow.org/docs/latest/index.html
- **Ray**: https://docs.ray.io/
- **Prometheus**: https://prometheus.io/docs/
- **Grafana**: https://grafana.com/docs/

---

#### 14.4.2 関連ドキュメント

| ドキュメント | 説明 |
|------------|------|
| `00_INTEGRATED_DESIGN_OVERVIEW.md` | 統合設計概要 |
| `01_REQUIREMENTS_SPECIFICATION_DETAILED.md` | 詳細要件定義 |
| `02_NON_FUNCTIONAL_REQUIREMENTS.md` | 非機能要件 |
| `03_ARCHITECTURE_DESIGN_DETAILED.md` | アーキテクチャ設計 |
| `07_IMPLEMENTATION_GUIDE.md` | 実装ガイド |
| `08_CODING_STANDARDS.md` | コーディング規約 |
| `09_TESTING_STRATEGY.md` | テスト戦略 |
| `11_OPERATIONS_RUNBOOK.md` | 運用手順書 |
| `12_MONITORING_GUIDE.md` | 監視ガイド |

---

## ✨ まとめ

本デプロイガイドは、時系列予測システムの各環境へのデプロイ手順を包括的に提供しています。

### デプロイのポイント

- ✅ **段階的デプロイ**: ローカル → Docker → 本番
- ✅ **環境分離**: 開発、ステージング、本番環境の明確な分離
- ✅ **自動化**: Docker Compose、Kubernetes による自動デプロイ
- ✅ **監視**: Prometheus/Grafana による包括的な監視
- ✅ **バックアップ**: 定期バックアップと復旧手順の整備
- ✅ **セキュリティ**: 秘密情報管理、認証、暗号化の実装

### 次のステップ

1. ✅ **本デプロイガイドを読了**
2. 🔧 環境に応じたセクションを実行
   - ローカル開発: セクション4
   - Docker環境: セクション5
   - 本番環境: セクション6（準備中）
3. 🔐 セキュリティ設定の実施
4. 📊 監視・ロギングの設定
5. 💾 バックアップ戦略の実装
6. 📝 運用ドキュメントの確認

---

**Happy Deploying! 🚀**

---
**End of Document**
