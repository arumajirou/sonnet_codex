# 詳細データベース設計書
**Detailed Database Design for Time Series Forecasting System**

---

## 📋 ドキュメント情報

| 項目 | 内容 |
|-----|------|
| **ドキュメントタイトル** | 時系列予測システム 詳細データベース設計書 |
| **バージョン** | v1.0.0 |
| **作成日** | 2025-11-03 |
| **最終更新日** | 2025-11-03 |
| **対象システム** | NeuralForecast Auto Runner + Time Series Forecasting System |
| **データベース** | PostgreSQL 14+ |
| **ORM** | SQLAlchemy 2.0+ |

---

## 目次

1. [データベース概要](#1-データベース概要)
2. [テーブル定義](#2-テーブル定義)
3. [ER図](#3-er図)
4. [インデックス設計](#4-インデックス設計)
5. [マイグレーション計画](#5-マイグレーション計画)
6. [パフォーマンスチューニング](#6-パフォーマンスチューニング)
7. [バックアップ戦略](#7-バックアップ戦略)
8. [セキュリティ](#8-セキュリティ)
9. [運用手順](#9-運用手順)
10. [付録](#10-付録)

---

## 1. データベース概要

### 1.1 データベース構成

#### 1.1.1 基本情報

```yaml
Database:
  Name: ts_forecast_system
  Engine: PostgreSQL
  Version: 14+
  Encoding: UTF8
  Locale: en_US.UTF-8
  Timezone: UTC
  
Connection Pool:
  Min: 2
  Max: 20
  Overflow: 10
  Timeout: 30s
  Recycle: 3600s
```

---

#### 1.1.2 スキーマ構成

| スキーマ名 | 用途 | 主要テーブル数 |
|----------|------|--------------|
| **public** | メインデータ | 15 |
| **audit** | 監査ログ | 3 |
| **staging** | 一時データ | 2 |
| **archive** | アーカイブ | 5 |

---

### 1.2 設計原則

#### 1.2.1 正規化レベル

- **第3正規形 (3NF)** を基本とする
- パフォーマンスが必要な部分は**意図的な非正規化**を許容
- 時系列データテーブルは**パーティショニング**を活用

#### 1.2.2 命名規則

```yaml
Tables:
  Format: snake_case
  Singular: false  # 複数形を使用
  Prefix: なし
  
Columns:
  Format: snake_case
  Reserved Words: 回避
  
Primary Keys:
  Format: "{table_name}_id" or "id"
  Type: BIGSERIAL or UUID
  
Foreign Keys:
  Format: "{referenced_table}_id"
  
Indexes:
  Format: "idx_{table}_{columns}"
  
Constraints:
  Format: "ck_{table}_{column}_{condition}"
  
Sequences:
  Format: "{table}_{column}_seq"
```

---

### 1.3 データ型ポリシー

| PostgreSQL型 | 用途 | 備考 |
|-------------|------|------|
| **BIGSERIAL** | 自動増分ID | 主キーで使用 |
| **UUID** | グローバルID | 分散環境用 |
| **TIMESTAMP** | 日時（タイムゾーンなし） | UTCで統一 |
| **TIMESTAMPTZ** | 日時（タイムゾーンあり） | ユーザー入力用 |
| **NUMERIC(p,s)** | 高精度数値 | 金額、評価指標 |
| **DOUBLE PRECISION** | 浮動小数点 | 機械学習パラメータ |
| **TEXT** | 可変長文字列 | 長さ制限なし |
| **VARCHAR(n)** | 制限付き文字列 | 名前、コード |
| **JSONB** | JSON | 柔軟なデータ |
| **BOOLEAN** | 真偽値 | フラグ |
| **BYTEA** | バイナリ | モデルファイル（小） |

---

## 2. テーブル定義

### 2.1 実験管理テーブル

#### 2.1.1 experiments (実験)

**目的**: 実験の基本情報を管理

```sql
CREATE TABLE experiments (
    -- 主キー
    experiment_id BIGSERIAL PRIMARY KEY,
    
    -- 基本情報
    experiment_name VARCHAR(255) NOT NULL,
    experiment_description TEXT,
    experiment_type VARCHAR(50) NOT NULL DEFAULT 'training',
    
    -- ステータス
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    lifecycle_stage VARCHAR(50) NOT NULL DEFAULT 'active',
    
    -- メタデータ
    created_by VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    -- タグ・属性
    tags JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    
    -- 制約
    CONSTRAINT ck_experiments_status CHECK (
        status IN ('active', 'archived', 'deleted')
    ),
    CONSTRAINT ck_experiments_lifecycle CHECK (
        lifecycle_stage IN ('active', 'deleted', 'archived')
    ),
    CONSTRAINT ck_experiments_type CHECK (
        experiment_type IN ('training', 'testing', 'production', 'development')
    )
);

-- インデックス
CREATE INDEX idx_experiments_name ON experiments(experiment_name);
CREATE INDEX idx_experiments_created_at ON experiments(created_at DESC);
CREATE INDEX idx_experiments_status ON experiments(status) WHERE status = 'active';
CREATE INDEX idx_experiments_tags ON experiments USING GIN(tags);

-- コメント
COMMENT ON TABLE experiments IS '実験の基本情報を管理するテーブル';
COMMENT ON COLUMN experiments.experiment_id IS '実験の一意識別子';
COMMENT ON COLUMN experiments.experiment_name IS '実験名（ユーザー指定）';
COMMENT ON COLUMN experiments.lifecycle_stage IS 'MLflowとの互換性のためのステージ';
COMMENT ON COLUMN experiments.tags IS 'カスタムタグ（JSONB形式）';
```

---

#### 2.1.2 runs (実行)

**目的**: 各実験の個別実行を記録

```sql
CREATE TABLE runs (
    -- 主キー
    run_id BIGSERIAL PRIMARY KEY,
    run_uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    
    -- 外部キー
    experiment_id BIGINT NOT NULL REFERENCES experiments(experiment_id) ON DELETE CASCADE,
    parent_run_id BIGINT REFERENCES runs(run_id) ON DELETE SET NULL,
    
    -- 基本情報
    run_name VARCHAR(255) NOT NULL,
    run_description TEXT,
    
    -- Fingerprint（重複検出用）
    run_fingerprint VARCHAR(64) NOT NULL,
    
    -- ステータス
    status VARCHAR(50) NOT NULL DEFAULT 'running',
    lifecycle_stage VARCHAR(50) NOT NULL DEFAULT 'active',
    
    -- 実行情報
    start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    execution_duration_seconds NUMERIC(12, 3),
    
    -- ソースコード情報
    source_type VARCHAR(50),
    source_name TEXT,
    git_commit_hash VARCHAR(40),
    git_branch VARCHAR(255),
    git_repo_url TEXT,
    
    -- ユーザー情報
    user_id VARCHAR(255),
    
    -- メタデータ
    tags JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    
    -- タイムスタンプ
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    -- 制約
    CONSTRAINT ck_runs_status CHECK (
        status IN ('running', 'completed', 'failed', 'killed', 'scheduled')
    ),
    CONSTRAINT ck_runs_lifecycle CHECK (
        lifecycle_stage IN ('active', 'deleted')
    ),
    CONSTRAINT ck_runs_source_type CHECK (
        source_type IN ('notebook', 'script', 'cli', 'api', 'scheduled')
    ),
    CONSTRAINT ck_runs_duration CHECK (
        execution_duration_seconds IS NULL OR execution_duration_seconds >= 0
    )
);

-- インデックス
CREATE INDEX idx_runs_experiment_id ON runs(experiment_id);
CREATE INDEX idx_runs_fingerprint ON runs(run_fingerprint);
CREATE INDEX idx_runs_status ON runs(status);
CREATE INDEX idx_runs_start_time ON runs(start_time DESC);
CREATE INDEX idx_runs_parent_run ON runs(parent_run_id) WHERE parent_run_id IS NOT NULL;
CREATE INDEX idx_runs_tags ON runs USING GIN(tags);
CREATE INDEX idx_runs_composite ON runs(experiment_id, status, start_time DESC);

-- 一意制約（重複実行防止）
CREATE UNIQUE INDEX idx_runs_unique_fingerprint 
    ON runs(experiment_id, run_fingerprint) 
    WHERE deleted_at IS NULL;

-- コメント
COMMENT ON TABLE runs IS '実験の個別実行を記録するテーブル';
COMMENT ON COLUMN runs.run_fingerprint IS '実行条件の一意識別用ハッシュ（SHA-256）';
COMMENT ON COLUMN runs.parent_run_id IS 'ハイパーパラメータチューニングの親Run';
```

---

### 2.2 モデル管理テーブル

#### 2.2.1 models (モデル)

**目的**: 学習済みモデルの情報を管理

```sql
CREATE TABLE models (
    -- 主キー
    model_id BIGSERIAL PRIMARY KEY,
    model_uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    
    -- 外部キー
    run_id BIGINT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
    
    -- モデル基本情報
    model_name VARCHAR(255) NOT NULL,
    model_type VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL DEFAULT '1.0.0',
    
    -- モデルライブラリ情報
    framework VARCHAR(50) NOT NULL,
    framework_version VARCHAR(50),
    
    -- モデル設定
    model_config JSONB NOT NULL,
    hyperparameters JSONB NOT NULL DEFAULT '{}',
    
    -- 学習情報
    training_dataset_id BIGINT REFERENCES datasets(dataset_id),
    training_samples INTEGER,
    training_duration_seconds NUMERIC(12, 3),
    
    -- モデルサイズ
    model_size_bytes BIGINT,
    
    -- ファイルパス
    model_file_path TEXT NOT NULL,
    checkpoint_path TEXT,
    
    -- ステータス
    status VARCHAR(50) NOT NULL DEFAULT 'training',
    
    -- メタデータ
    tags JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    
    -- タイムスタンプ
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- 制約
    CONSTRAINT ck_models_status CHECK (
        status IN ('training', 'trained', 'evaluating', 'evaluated', 'deployed', 'archived', 'failed')
    ),
    CONSTRAINT ck_models_framework CHECK (
        framework IN ('neuralforecast', 'pytorch', 'tensorflow', 'sklearn', 'darts', 'gluonts', 'prophet')
    ),
    CONSTRAINT ck_models_training_samples CHECK (
        training_samples IS NULL OR training_samples > 0
    ),
    CONSTRAINT ck_models_size CHECK (
        model_size_bytes IS NULL OR model_size_bytes > 0
    )
);

-- インデックス
CREATE INDEX idx_models_run_id ON models(run_id);
CREATE INDEX idx_models_name ON models(model_name);
CREATE INDEX idx_models_type ON models(model_type);
CREATE INDEX idx_models_framework ON models(framework);
CREATE INDEX idx_models_status ON models(status);
CREATE INDEX idx_models_created_at ON models(created_at DESC);
CREATE INDEX idx_models_config ON models USING GIN(model_config);
CREATE INDEX idx_models_tags ON models USING GIN(tags);

-- コメント
COMMENT ON TABLE models IS '学習済みモデルの情報を管理するテーブル';
COMMENT ON COLUMN models.model_type IS 'モデルの種類（例: AutoNHITS, AutoLSTM, AutoTFT）';
COMMENT ON COLUMN models.model_config IS 'モデルの詳細設定（JSONB形式）';
COMMENT ON COLUMN models.hyperparameters IS 'ハイパーパラメータ（JSONB形式）';
```

---

#### 2.2.2 model_registry (モデルレジストリ)

**目的**: モデルのバージョン管理とステージ遷移

```sql
CREATE TABLE model_registry (
    -- 主キー
    registry_id BIGSERIAL PRIMARY KEY,
    
    -- 外部キー
    model_id BIGINT NOT NULL REFERENCES models(model_id) ON DELETE CASCADE,
    
    -- レジストリ情報
    registered_model_name VARCHAR(255) NOT NULL,
    model_version INTEGER NOT NULL,
    
    -- ステージ管理
    current_stage VARCHAR(50) NOT NULL DEFAULT 'staging',
    previous_stage VARCHAR(50),
    stage_transition_at TIMESTAMP,
    
    -- 承認情報
    approved_by VARCHAR(255),
    approved_at TIMESTAMP,
    approval_notes TEXT,
    
    -- デプロイ情報
    deployed_at TIMESTAMP,
    deployment_target VARCHAR(100),
    
    -- パフォーマンス追跡
    production_metrics JSONB DEFAULT '{}',
    
    -- メタデータ
    description TEXT,
    tags JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    
    -- タイムスタンプ
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- 制約
    CONSTRAINT ck_registry_stage CHECK (
        current_stage IN ('staging', 'production', 'archived', 'none')
    ),
    CONSTRAINT ck_registry_version CHECK (
        model_version > 0
    ),
    CONSTRAINT uq_registry_name_version UNIQUE (registered_model_name, model_version)
);

-- インデックス
CREATE INDEX idx_registry_model_id ON model_registry(model_id);
CREATE INDEX idx_registry_name ON model_registry(registered_model_name);
CREATE INDEX idx_registry_stage ON model_registry(current_stage);
CREATE INDEX idx_registry_deployed_at ON model_registry(deployed_at DESC) 
    WHERE deployed_at IS NOT NULL;

-- コメント
COMMENT ON TABLE model_registry IS 'モデルのバージョン管理とステージ遷移を管理';
COMMENT ON COLUMN model_registry.current_stage IS 'staging, production, archived, none';
COMMENT ON COLUMN model_registry.production_metrics IS 'プロダクション環境での評価指標';
```

---

### 2.3 データセット管理テーブル

#### 2.3.1 datasets (データセット)

**目的**: 学習・評価に使用するデータセットの情報

```sql
CREATE TABLE datasets (
    -- 主キー
    dataset_id BIGSERIAL PRIMARY KEY,
    dataset_uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    
    -- 基本情報
    dataset_name VARCHAR(255) NOT NULL,
    dataset_description TEXT,
    dataset_type VARCHAR(50) NOT NULL,
    
    -- ファイル情報
    file_path TEXT NOT NULL,
    file_format VARCHAR(50) NOT NULL DEFAULT 'csv',
    file_size_bytes BIGINT,
    file_hash VARCHAR(64),
    
    -- データ統計
    num_rows INTEGER,
    num_columns INTEGER,
    num_time_series INTEGER,
    
    -- 時系列情報
    date_column VARCHAR(100),
    target_column VARCHAR(100),
    frequency VARCHAR(20),
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    
    -- スキーマ情報
    schema_definition JSONB,
    column_types JSONB,
    
    -- データ品質
    missing_values_count INTEGER DEFAULT 0,
    duplicate_rows_count INTEGER DEFAULT 0,
    
    -- バージョン管理
    version VARCHAR(50) DEFAULT '1.0.0',
    parent_dataset_id BIGINT REFERENCES datasets(dataset_id),
    
    -- メタデータ
    tags JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    
    -- タイムスタンプ
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- 制約
    CONSTRAINT ck_datasets_type CHECK (
        dataset_type IN ('raw', 'processed', 'training', 'validation', 'test', 'production')
    ),
    CONSTRAINT ck_datasets_format CHECK (
        file_format IN ('csv', 'parquet', 'json', 'feather')
    ),
    CONSTRAINT ck_datasets_rows CHECK (
        num_rows IS NULL OR num_rows >= 0
    ),
    CONSTRAINT ck_datasets_columns CHECK (
        num_columns IS NULL OR num_columns > 0
    )
);

-- インデックス
CREATE INDEX idx_datasets_name ON datasets(dataset_name);
CREATE INDEX idx_datasets_type ON datasets(dataset_type);
CREATE INDEX idx_datasets_file_hash ON datasets(file_hash);
CREATE INDEX idx_datasets_created_at ON datasets(created_at DESC);
CREATE INDEX idx_datasets_parent ON datasets(parent_dataset_id) 
    WHERE parent_dataset_id IS NOT NULL;

-- コメント
COMMENT ON TABLE datasets IS 'データセットの情報を管理するテーブル';
COMMENT ON COLUMN datasets.file_hash IS 'ファイル内容のSHA-256ハッシュ';
COMMENT ON COLUMN datasets.schema_definition IS 'カラムスキーマの定義（JSONB）';
```

---

#### 2.3.2 dataset_features (特徴量)

**目的**: データセットの特徴量情報を管理

```sql
CREATE TABLE dataset_features (
    -- 主キー
    feature_id BIGSERIAL PRIMARY KEY,
    
    -- 外部キー
    dataset_id BIGINT NOT NULL REFERENCES datasets(dataset_id) ON DELETE CASCADE,
    
    -- 特徴量情報
    feature_name VARCHAR(255) NOT NULL,
    feature_type VARCHAR(50) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    
    -- 統計情報
    min_value DOUBLE PRECISION,
    max_value DOUBLE PRECISION,
    mean_value DOUBLE PRECISION,
    median_value DOUBLE PRECISION,
    std_value DOUBLE PRECISION,
    
    -- カテゴリカル特徴量
    num_unique_values INTEGER,
    unique_values JSONB,
    
    -- 欠損値情報
    missing_count INTEGER DEFAULT 0,
    missing_percentage NUMERIC(5, 2) DEFAULT 0.00,
    
    -- 特徴量の役割
    feature_role VARCHAR(50),
    is_target BOOLEAN DEFAULT FALSE,
    is_exogenous BOOLEAN DEFAULT FALSE,
    exogenous_type VARCHAR(50),
    
    -- メタデータ
    importance_score DOUBLE PRECISION,
    correlation_with_target DOUBLE PRECISION,
    tags JSONB DEFAULT '{}',
    
    -- タイムスタンプ
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- 制約
    CONSTRAINT ck_features_type CHECK (
        feature_type IN ('numeric', 'categorical', 'datetime', 'text', 'boolean')
    ),
    CONSTRAINT ck_features_role CHECK (
        feature_role IN ('target', 'feature', 'id', 'timestamp', 'weight', 'ignore')
    ),
    CONSTRAINT ck_features_exog_type CHECK (
        exogenous_type IS NULL OR 
        exogenous_type IN ('future', 'historic', 'static')
    ),
    CONSTRAINT ck_features_missing_pct CHECK (
        missing_percentage >= 0 AND missing_percentage <= 100
    ),
    CONSTRAINT uq_dataset_feature UNIQUE (dataset_id, feature_name)
);

-- インデックス
CREATE INDEX idx_features_dataset_id ON dataset_features(dataset_id);
CREATE INDEX idx_features_name ON dataset_features(feature_name);
CREATE INDEX idx_features_type ON dataset_features(feature_type);
CREATE INDEX idx_features_role ON dataset_features(feature_role);
CREATE INDEX idx_features_target ON dataset_features(is_target) WHERE is_target = TRUE;

-- コメント
COMMENT ON TABLE dataset_features IS 'データセットの特徴量情報を管理';
COMMENT ON COLUMN dataset_features.exogenous_type IS 'future: 未来値利用可能, historic: 過去値のみ, static: 静的';
```

---

### 2.4 評価指標テーブル

#### 2.4.1 metrics (評価指標)

**目的**: モデルの評価指標を記録

```sql
CREATE TABLE metrics (
    -- 主キー
    metric_id BIGSERIAL PRIMARY KEY,
    
    -- 外部キー
    run_id BIGINT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
    model_id BIGINT REFERENCES models(model_id) ON DELETE CASCADE,
    
    -- 評価指標情報
    metric_name VARCHAR(100) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    metric_step INTEGER DEFAULT 0,
    
    -- 評価コンテキスト
    dataset_type VARCHAR(50) NOT NULL DEFAULT 'validation',
    evaluation_context VARCHAR(100),
    
    -- タイムスタンプ
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- メタデータ
    metadata JSONB DEFAULT '{}',
    
    -- 制約
    CONSTRAINT ck_metrics_dataset_type CHECK (
        dataset_type IN ('train', 'validation', 'test', 'production')
    ),
    CONSTRAINT ck_metrics_step CHECK (
        metric_step >= 0
    )
);

-- インデックス
CREATE INDEX idx_metrics_run_id ON metrics(run_id);
CREATE INDEX idx_metrics_model_id ON metrics(model_id);
CREATE INDEX idx_metrics_name ON metrics(metric_name);
CREATE INDEX idx_metrics_timestamp ON metrics(timestamp DESC);
CREATE INDEX idx_metrics_composite ON metrics(run_id, metric_name, metric_step);

-- パーティショニング準備（オプション）
-- CREATE TABLE metrics_2025_q1 PARTITION OF metrics
--     FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');

-- コメント
COMMENT ON TABLE metrics IS 'モデルの評価指標を記録するテーブル';
COMMENT ON COLUMN metrics.metric_step IS '学習ステップ番号（エポック、イテレーション等）';
COMMENT ON COLUMN metrics.evaluation_context IS '評価コンテキスト（例: backtest_fold_1）';
```

---

#### 2.4.2 metric_summaries (指標サマリー)

**目的**: 評価指標の集計結果を保存（パフォーマンス最適化）

```sql
CREATE TABLE metric_summaries (
    -- 主キー
    summary_id BIGSERIAL PRIMARY KEY,
    
    -- 外部キー
    run_id BIGINT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
    model_id BIGINT REFERENCES models(model_id) ON DELETE CASCADE,
    
    -- 集計情報
    metric_name VARCHAR(100) NOT NULL,
    dataset_type VARCHAR(50) NOT NULL,
    
    -- 統計量
    min_value DOUBLE PRECISION,
    max_value DOUBLE PRECISION,
    mean_value DOUBLE PRECISION,
    median_value DOUBLE PRECISION,
    std_value DOUBLE PRECISION,
    
    -- 四分位数
    q1_value DOUBLE PRECISION,
    q3_value DOUBLE PRECISION,
    
    -- サンプル数
    sample_count INTEGER NOT NULL,
    
    -- タイムスタンプ
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- 制約
    CONSTRAINT uq_summary_run_metric UNIQUE (run_id, metric_name, dataset_type)
);

-- インデックス
CREATE INDEX idx_summary_run_id ON metric_summaries(run_id);
CREATE INDEX idx_summary_model_id ON metric_summaries(model_id);
CREATE INDEX idx_summary_metric ON metric_summaries(metric_name);

-- コメント
COMMENT ON TABLE metric_summaries IS '評価指標の集計結果を保存（高速クエリ用）';
```

---

### 2.5 ハイパーパラメータ管理テーブル

#### 2.5.1 hyperparameters (ハイパーパラメータ)

**目的**: 各実行のハイパーパラメータを記録

```sql
CREATE TABLE hyperparameters (
    -- 主キー
    hyperparameter_id BIGSERIAL PRIMARY KEY,
    
    -- 外部キー
    run_id BIGINT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
    
    -- パラメータ情報
    param_key VARCHAR(255) NOT NULL,
    param_value TEXT NOT NULL,
    param_type VARCHAR(50) NOT NULL DEFAULT 'string',
    
    -- メタデータ
    is_hyperparameter BOOLEAN DEFAULT TRUE,
    param_category VARCHAR(100),
    
    -- タイムスタンプ
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- 制約
    CONSTRAINT ck_params_type CHECK (
        param_type IN ('string', 'integer', 'float', 'boolean', 'json')
    ),
    CONSTRAINT uq_run_param_key UNIQUE (run_id, param_key)
);

-- インデックス
CREATE INDEX idx_params_run_id ON hyperparameters(run_id);
CREATE INDEX idx_params_key ON hyperparameters(param_key);
CREATE INDEX idx_params_category ON hyperparameters(param_category) 
    WHERE param_category IS NOT NULL;

-- コメント
COMMENT ON TABLE hyperparameters IS 'ハイパーパラメータと設定パラメータを記録';
COMMENT ON COLUMN hyperparameters.is_hyperparameter IS 'TRUE: ハイパーパラメータ, FALSE: 設定パラメータ';
```

---

#### 2.5.2 hyperparameter_search_spaces (探索空間)

**目的**: ハイパーパラメータの探索空間を定義

```sql
CREATE TABLE hyperparameter_search_spaces (
    -- 主キー
    search_space_id BIGSERIAL PRIMARY KEY,
    
    -- 探索空間情報
    space_name VARCHAR(255) NOT NULL UNIQUE,
    space_description TEXT,
    
    -- モデル情報
    model_type VARCHAR(100) NOT NULL,
    framework VARCHAR(50) NOT NULL,
    
    -- 探索空間定義
    search_space_definition JSONB NOT NULL,
    
    -- メタデータ
    created_by VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    tags JSONB DEFAULT '{}',
    
    -- タイムスタンプ
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- インデックス
CREATE INDEX idx_search_space_model ON hyperparameter_search_spaces(model_type);
CREATE INDEX idx_search_space_active ON hyperparameter_search_spaces(is_active) 
    WHERE is_active = TRUE;

-- コメント
COMMENT ON TABLE hyperparameter_search_spaces IS 'ハイパーパラメータの探索空間定義';
COMMENT ON COLUMN hyperparameter_search_spaces.search_space_definition IS 'Optuna/Ray Tune形式の探索空間（JSONB）';
```

---

### 2.6 アーティファクト管理テーブル

#### 2.6.1 artifacts (アーティファクト)

**目的**: 実験で生成されるすべての成果物を管理

```sql
CREATE TABLE artifacts (
    -- 主キー
    artifact_id BIGSERIAL PRIMARY KEY,
    artifact_uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    
    -- 外部キー
    run_id BIGINT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
    
    -- アーティファクト情報
    artifact_name VARCHAR(255) NOT NULL,
    artifact_type VARCHAR(100) NOT NULL,
    artifact_path TEXT NOT NULL,
    
    -- ファイル情報
    file_size_bytes BIGINT,
    file_format VARCHAR(50),
    mime_type VARCHAR(100),
    file_hash VARCHAR(64),
    
    -- ストレージ情報
    storage_type VARCHAR(50) NOT NULL DEFAULT 'local',
    storage_path TEXT NOT NULL,
    
    -- メタデータ
    description TEXT,
    tags JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    
    -- アクセス管理
    is_public BOOLEAN DEFAULT FALSE,
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP,
    
    -- タイムスタンプ
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- 制約
    CONSTRAINT ck_artifacts_type CHECK (
        artifact_type IN (
            'model', 'checkpoint', 'prediction', 'plot', 'log', 
            'config', 'report', 'data', 'other'
        )
    ),
    CONSTRAINT ck_artifacts_storage CHECK (
        storage_type IN ('local', 's3', 'gcs', 'azure', 'mlflow', 'wandb')
    ),
    CONSTRAINT ck_artifacts_size CHECK (
        file_size_bytes IS NULL OR file_size_bytes >= 0
    )
);

-- インデックス
CREATE INDEX idx_artifacts_run_id ON artifacts(run_id);
CREATE INDEX idx_artifacts_type ON artifacts(artifact_type);
CREATE INDEX idx_artifacts_name ON artifacts(artifact_name);
CREATE INDEX idx_artifacts_hash ON artifacts(file_hash);
CREATE INDEX idx_artifacts_created_at ON artifacts(created_at DESC);
CREATE INDEX idx_artifacts_tags ON artifacts USING GIN(tags);

-- コメント
COMMENT ON TABLE artifacts IS '実験で生成される成果物を管理';
COMMENT ON COLUMN artifacts.file_hash IS 'ファイル内容のSHA-256ハッシュ';
COMMENT ON COLUMN artifacts.storage_path IS '実際のストレージパス（URI形式）';
```

---

### 2.7 予測結果テーブル

#### 2.7.1 predictions (予測結果)

**目的**: モデルの予測結果を記録

```sql
CREATE TABLE predictions (
    -- 主キー
    prediction_id BIGSERIAL PRIMARY KEY,
    
    -- 外部キー
    run_id BIGINT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
    model_id BIGINT NOT NULL REFERENCES models(model_id) ON DELETE CASCADE,
    
    -- 予測情報
    prediction_date TIMESTAMP NOT NULL,
    unique_id TEXT NOT NULL,
    horizon INTEGER NOT NULL,
    
    -- 予測値
    predicted_value DOUBLE PRECISION NOT NULL,
    actual_value DOUBLE PRECISION,
    
    -- 信頼区間
    lower_bound DOUBLE PRECISION,
    upper_bound DOUBLE PRECISION,
    confidence_level NUMERIC(3, 2) DEFAULT 0.95,
    
    -- メタデータ
    metadata JSONB DEFAULT '{}',
    
    -- タイムスタンプ
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- 制約
    CONSTRAINT ck_predictions_horizon CHECK (horizon > 0),
    CONSTRAINT ck_predictions_confidence CHECK (
        confidence_level > 0 AND confidence_level < 1
    )
) PARTITION BY RANGE (prediction_date);

-- パーティション作成（四半期ごと）
CREATE TABLE predictions_2025_q1 PARTITION OF predictions
    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
CREATE TABLE predictions_2025_q2 PARTITION OF predictions
    FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');
CREATE TABLE predictions_2025_q3 PARTITION OF predictions
    FOR VALUES FROM ('2025-07-01') TO ('2025-10-01');
CREATE TABLE predictions_2025_q4 PARTITION OF predictions
    FOR VALUES FROM ('2025-10-01') TO ('2026-01-01');

-- インデックス（各パーティションに自動作成）
CREATE INDEX idx_predictions_run_id ON predictions(run_id);
CREATE INDEX idx_predictions_model_id ON predictions(model_id);
CREATE INDEX idx_predictions_date ON predictions(prediction_date);
CREATE INDEX idx_predictions_unique_id ON predictions(unique_id);
CREATE INDEX idx_predictions_composite ON predictions(unique_id, prediction_date, horizon);

-- コメント
COMMENT ON TABLE predictions IS 'モデルの予測結果を記録（パーティショニング対応）';
COMMENT ON COLUMN predictions.horizon IS '予測ホライズン（何ステップ先の予測か）';
```

---

### 2.8 ログ・監査テーブル

#### 2.8.1 system_logs (システムログ)

**目的**: システムのログを記録

```sql
CREATE TABLE system_logs (
    -- 主キー
    log_id BIGSERIAL PRIMARY KEY,
    
    -- ログ情報
    log_level VARCHAR(20) NOT NULL,
    log_message TEXT NOT NULL,
    log_source VARCHAR(255),
    
    -- コンテキスト情報
    run_id BIGINT REFERENCES runs(run_id) ON DELETE SET NULL,
    user_id VARCHAR(255),
    
    -- 詳細情報
    stack_trace TEXT,
    exception_type VARCHAR(255),
    extra_data JSONB DEFAULT '{}',
    
    -- タイムスタンプ
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- 制約
    CONSTRAINT ck_logs_level CHECK (
        log_level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    )
) PARTITION BY RANGE (created_at);

-- パーティション作成（月次）
CREATE TABLE system_logs_2025_01 PARTITION OF system_logs
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
CREATE TABLE system_logs_2025_02 PARTITION OF system_logs
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
CREATE TABLE system_logs_2025_03 PARTITION OF system_logs
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');

-- インデックス
CREATE INDEX idx_logs_level ON system_logs(log_level);
CREATE INDEX idx_logs_created_at ON system_logs(created_at DESC);
CREATE INDEX idx_logs_run_id ON system_logs(run_id) WHERE run_id IS NOT NULL;
CREATE INDEX idx_logs_source ON system_logs(log_source);

-- コメント
COMMENT ON TABLE system_logs IS 'システムログを記録（パーティショニング対応）';
```

---

#### 2.8.2 audit_logs (監査ログ)

**目的**: データベース操作の監査ログ

```sql
CREATE TABLE audit.audit_logs (
    -- 主キー
    audit_id BIGSERIAL PRIMARY KEY,
    
    -- 監査情報
    table_name VARCHAR(255) NOT NULL,
    operation_type VARCHAR(20) NOT NULL,
    record_id BIGINT,
    
    -- 変更内容
    old_values JSONB,
    new_values JSONB,
    changed_fields JSONB,
    
    -- ユーザー情報
    user_id VARCHAR(255),
    user_ip VARCHAR(50),
    session_id VARCHAR(255),
    
    -- タイムスタンプ
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- 制約
    CONSTRAINT ck_audit_operation CHECK (
        operation_type IN ('INSERT', 'UPDATE', 'DELETE', 'TRUNCATE')
    )
) PARTITION BY RANGE (created_at);

-- パーティション作成（四半期ごと）
CREATE TABLE audit.audit_logs_2025_q1 PARTITION OF audit.audit_logs
    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');

-- インデックス
CREATE INDEX idx_audit_table ON audit.audit_logs(table_name);
CREATE INDEX idx_audit_operation ON audit.audit_logs(operation_type);
CREATE INDEX idx_audit_user ON audit.audit_logs(user_id);
CREATE INDEX idx_audit_created_at ON audit.audit_logs(created_at DESC);

-- コメント
COMMENT ON TABLE audit.audit_logs IS 'データベース操作の監査ログ';
```

---

### 2.9 ユーザー・権限管理テーブル

#### 2.9.1 users (ユーザー)

**目的**: システムユーザーの情報を管理

```sql
CREATE TABLE users (
    -- 主キー
    user_id BIGSERIAL PRIMARY KEY,
    user_uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    
    -- ユーザー情報
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255),
    
    -- 認証情報（外部認証を想定）
    auth_provider VARCHAR(50) DEFAULT 'local',
    external_id VARCHAR(255),
    
    -- ステータス
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    
    -- 最終ログイン
    last_login_at TIMESTAMP,
    login_count INTEGER DEFAULT 0,
    
    -- メタデータ
    preferences JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    
    -- タイムスタンプ
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- 制約
    CONSTRAINT ck_users_auth_provider CHECK (
        auth_provider IN ('local', 'oauth2', 'ldap', 'saml')
    )
);

-- インデックス
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_users_provider ON users(auth_provider);

-- コメント
COMMENT ON TABLE users IS 'システムユーザーの情報を管理';
COMMENT ON COLUMN users.preferences IS 'ユーザー設定（UI設定、通知設定等）';
```

---

#### 2.9.2 user_experiments (ユーザー実験関連)

**目的**: ユーザーと実験の関連を管理

```sql
CREATE TABLE user_experiments (
    -- 主キー
    user_experiment_id BIGSERIAL PRIMARY KEY,
    
    -- 外部キー
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    experiment_id BIGINT NOT NULL REFERENCES experiments(experiment_id) ON DELETE CASCADE,
    
    -- 権限
    permission_level VARCHAR(50) NOT NULL DEFAULT 'read',
    
    -- タイムスタンプ
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- 制約
    CONSTRAINT ck_user_exp_permission CHECK (
        permission_level IN ('read', 'write', 'admin', 'owner')
    ),
    CONSTRAINT uq_user_experiment UNIQUE (user_id, experiment_id)
);

-- インデックス
CREATE INDEX idx_user_exp_user_id ON user_experiments(user_id);
CREATE INDEX idx_user_exp_experiment_id ON user_experiments(experiment_id);
CREATE INDEX idx_user_exp_permission ON user_experiments(permission_level);

-- コメント
COMMENT ON TABLE user_experiments IS 'ユーザーと実験のアクセス権限を管理';
```

---

### 2.10 設定・メタデータテーブル

#### 2.10.1 system_config (システム設定)

**目的**: システム全体の設定を管理

```sql
CREATE TABLE system_config (
    -- 主キー
    config_id BIGSERIAL PRIMARY KEY,
    
    -- 設定情報
    config_key VARCHAR(255) NOT NULL UNIQUE,
    config_value TEXT NOT NULL,
    config_type VARCHAR(50) NOT NULL DEFAULT 'string',
    
    -- 説明
    description TEXT,
    
    -- 設定カテゴリ
    category VARCHAR(100),
    
    -- 検証
    validation_regex TEXT,
    is_secret BOOLEAN DEFAULT FALSE,
    
    -- タイムスタンプ
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- 制約
    CONSTRAINT ck_config_type CHECK (
        config_type IN ('string', 'integer', 'float', 'boolean', 'json')
    )
);

-- インデックス
CREATE INDEX idx_config_key ON system_config(config_key);
CREATE INDEX idx_config_category ON system_config(category);

-- コメント
COMMENT ON TABLE system_config IS 'システム全体の設定を管理';
COMMENT ON COLUMN system_config.is_secret IS 'TRUE: 機密情報（暗号化推奨）';

-- デフォルト設定の挿入
INSERT INTO system_config (config_key, config_value, config_type, category, description) VALUES
    ('max_parallel_runs', '10', 'integer', 'execution', '最大並列実行数'),
    ('default_retention_days', '90', 'integer', 'storage', 'デフォルトのデータ保持期間（日）'),
    ('enable_mlflow', 'true', 'boolean', 'tracking', 'MLflowトラッキング有効化'),
    ('enable_wandb', 'false', 'boolean', 'tracking', 'W&Bトラッキング有効化'),
    ('log_level', 'INFO', 'string', 'logging', 'ログレベル');
```

---

#### 2.10.2 tags (タグ)

**目的**: システム全体で使用するタグを管理

```sql
CREATE TABLE tags (
    -- 主キー
    tag_id BIGSERIAL PRIMARY KEY,
    
    -- タグ情報
    tag_name VARCHAR(255) NOT NULL UNIQUE,
    tag_category VARCHAR(100),
    tag_description TEXT,
    
    -- 使用統計
    usage_count INTEGER DEFAULT 0,
    
    -- メタデータ
    metadata JSONB DEFAULT '{}',
    
    -- タイムスタンプ
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- インデックス
CREATE INDEX idx_tags_name ON tags(tag_name);
CREATE INDEX idx_tags_category ON tags(tag_category);
CREATE INDEX idx_tags_usage ON tags(usage_count DESC);

-- コメント
COMMENT ON TABLE tags IS 'システム全体で使用するタグを管理';
```

---

## 3. ER図

### 3.1 エンティティ関係図（全体）

```mermaid
erDiagram
    users ||--o{ user_experiments : "has"
    users ||--o{ experiments : "creates"
    
    experiments ||--o{ runs : "contains"
    experiments ||--o{ user_experiments : "shared_with"
    
    runs ||--o{ models : "produces"
    runs ||--o{ metrics : "records"
    runs ||--o{ hyperparameters : "uses"
    runs ||--o{ artifacts : "generates"
    runs ||--o{ predictions : "makes"
    runs ||--o{ system_logs : "logs"
    runs }o--|| runs : "parent_of"
    
    models ||--|| model_registry : "registered_in"
    models ||--o{ metrics : "evaluated_by"
    models ||--o{ predictions : "makes"
    models }o--|| datasets : "trained_on"
    
    datasets ||--o{ dataset_features : "contains"
    datasets }o--|| datasets : "derived_from"
    
    hyperparameter_search_spaces ||--o{ hyperparameters : "defines"
    
    experiments {
        bigint experiment_id PK
        varchar experiment_name
        text experiment_description
        varchar status
        varchar lifecycle_stage
        jsonb tags
        jsonb metadata
        timestamp created_at
        timestamp updated_at
    }
    
    runs {
        bigint run_id PK
        uuid run_uuid UK
        bigint experiment_id FK
        bigint parent_run_id FK
        varchar run_name
        varchar run_fingerprint
        varchar status
        timestamp start_time
        timestamp end_time
        numeric execution_duration_seconds
        jsonb tags
        jsonb metadata
    }
    
    models {
        bigint model_id PK
        uuid model_uuid UK
        bigint run_id FK
        varchar model_name
        varchar model_type
        varchar framework
        jsonb model_config
        jsonb hyperparameters
        text model_file_path
        varchar status
    }
    
    model_registry {
        bigint registry_id PK
        bigint model_id FK
        varchar registered_model_name
        integer model_version
        varchar current_stage
        timestamp deployed_at
        jsonb production_metrics
    }
    
    datasets {
        bigint dataset_id PK
        uuid dataset_uuid UK
        varchar dataset_name
        varchar dataset_type
        text file_path
        varchar file_format
        bigint parent_dataset_id FK
        jsonb schema_definition
    }
    
    dataset_features {
        bigint feature_id PK
        bigint dataset_id FK
        varchar feature_name
        varchar feature_type
        varchar feature_role
        boolean is_target
        boolean is_exogenous
    }
    
    metrics {
        bigint metric_id PK
        bigint run_id FK
        bigint model_id FK
        varchar metric_name
        double metric_value
        integer metric_step
        varchar dataset_type
        timestamp timestamp
    }
    
    hyperparameters {
        bigint hyperparameter_id PK
        bigint run_id FK
        varchar param_key
        text param_value
        varchar param_type
    }
    
    artifacts {
        bigint artifact_id PK
        uuid artifact_uuid UK
        bigint run_id FK
        varchar artifact_name
        varchar artifact_type
        text storage_path
        varchar storage_type
    }
    
    predictions {
        bigint prediction_id PK
        bigint run_id FK
        bigint model_id FK
        timestamp prediction_date
        text unique_id
        integer horizon
        double predicted_value
        double actual_value
    }
    
    users {
        bigint user_id PK
        uuid user_uuid UK
        varchar username UK
        varchar email UK
        boolean is_active
        timestamp last_login_at
    }
```

---

### 3.2 エンティティ関係図（実験・実行・モデル）

```mermaid
erDiagram
    experiments ||--o{ runs : contains
    runs ||--o{ models : produces
    runs ||--o{ metrics : records
    runs ||--o{ hyperparameters : uses
    models ||--|| model_registry : registered_in
    models ||--o{ predictions : makes
    
    experiments {
        bigint experiment_id PK "実験ID"
        varchar experiment_name "実験名"
        varchar status "ステータス"
        timestamp created_at "作成日時"
    }
    
    runs {
        bigint run_id PK "実行ID"
        uuid run_uuid UK "UUID"
        bigint experiment_id FK "実験ID"
        varchar run_fingerprint "フィンガープリント"
        varchar status "ステータス"
        timestamp start_time "開始時刻"
        timestamp end_time "終了時刻"
    }
    
    models {
        bigint model_id PK "モデルID"
        bigint run_id FK "実行ID"
        varchar model_name "モデル名"
        varchar model_type "モデル種別"
        jsonb model_config "モデル設定"
        text model_file_path "ファイルパス"
    }
    
    model_registry {
        bigint registry_id PK "レジストリID"
        bigint model_id FK "モデルID"
        varchar current_stage "現在のステージ"
        integer model_version "バージョン"
    }
```

---

## 4. インデックス設計

### 4.1 インデックス戦略

#### 4.1.1 B-Treeインデックス

**用途**: 範囲検索、ソート、等価比較

```sql
-- 実験検索の最適化
CREATE INDEX idx_experiments_status_created 
    ON experiments(status, created_at DESC) 
    WHERE status = 'active';

-- 実行検索の最適化
CREATE INDEX idx_runs_exp_status_start 
    ON runs(experiment_id, status, start_time DESC);

-- モデル検索の最適化
CREATE INDEX idx_models_type_created 
    ON models(model_type, created_at DESC);

-- 評価指標検索の最適化
CREATE INDEX idx_metrics_run_name_step 
    ON metrics(run_id, metric_name, metric_step);
```

---

#### 4.1.2 GINインデックス

**用途**: JSONB、全文検索、配列

```sql
-- JSONB検索の最適化
CREATE INDEX idx_experiments_tags_gin 
    ON experiments USING GIN(tags);

CREATE INDEX idx_runs_metadata_gin 
    ON runs USING GIN(metadata);

CREATE INDEX idx_models_config_gin 
    ON models USING GIN(model_config);

-- タグ検索の最適化
CREATE INDEX idx_experiments_tags_jsonb_path 
    ON experiments USING GIN(tags jsonb_path_ops);
```

---

#### 4.1.3 部分インデックス

**用途**: 特定条件のデータのみインデックス化

```sql
-- アクティブな実験のみ
CREATE INDEX idx_experiments_active 
    ON experiments(experiment_name) 
    WHERE status = 'active' AND deleted_at IS NULL;

-- 実行中のRunのみ
CREATE INDEX idx_runs_running 
    ON runs(start_time DESC) 
    WHERE status = 'running';

-- Productionステージのモデルのみ
CREATE INDEX idx_registry_production 
    ON model_registry(registered_model_name, model_version) 
    WHERE current_stage = 'production';
```

---

#### 4.1.4 複合インデックス

**用途**: 複数カラムでの検索最適化

```sql
-- 実験内の実行検索
CREATE INDEX idx_runs_composite 
    ON runs(experiment_id, status, start_time DESC);

-- 予測検索
CREATE INDEX idx_predictions_composite 
    ON predictions(unique_id, prediction_date, horizon);

-- メトリクス検索
CREATE INDEX idx_metrics_composite 
    ON metrics(run_id, metric_name, dataset_type, metric_step);
```

---

### 4.2 インデックスメンテナンス

#### 4.2.1 インデックス再構築

```sql
-- インデックスの肥大化確認
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    idx_scan AS index_scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;

-- インデックス再構築（CONCURRENT使用で無停止）
REINDEX INDEX CONCURRENTLY idx_runs_fingerprint;
REINDEX TABLE CONCURRENTLY runs;
```

---

#### 4.2.2 未使用インデックスの検出

```sql
-- 使用されていないインデックスの検出
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
  AND idx_scan = 0
  AND indexrelname NOT LIKE 'pk_%'
ORDER BY pg_relation_size(indexrelid) DESC;
```

---

## 5. マイグレーション計画

### 5.1 マイグレーションツール

#### 5.1.1 Alembic設定

```python
# alembic.ini
[alembic]
script_location = db/migrations
sqlalchemy.url = postgresql://user:pass@localhost/ts_forecast_system

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = INFO
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

---

#### 5.1.2 マイグレーションスクリプトテンプレート

```python
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
```

---

### 5.2 マイグレーションフェーズ

#### Phase 1: 基本テーブル作成

```python
"""Create base tables

Revision ID: 001
Create Date: 2025-11-03
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade() -> None:
    # experiments テーブル
    op.create_table(
        'experiments',
        sa.Column('experiment_id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('experiment_name', sa.String(255), nullable=False),
        sa.Column('experiment_description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('tags', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('experiment_id')
    )
    
    # runs テーブル
    op.create_table(
        'runs',
        sa.Column('run_id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('run_uuid', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('experiment_id', sa.BigInteger(), nullable=False),
        sa.Column('run_name', sa.String(255), nullable=False),
        sa.Column('run_fingerprint', sa.String(64), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='running'),
        sa.Column('start_time', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('end_time', sa.TIMESTAMP(), nullable=True),
        sa.Column('tags', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['experiment_id'], ['experiments.experiment_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('run_id'),
        sa.UniqueConstraint('run_uuid')
    )
    
    # インデックス作成
    op.create_index('idx_experiments_name', 'experiments', ['experiment_name'])
    op.create_index('idx_runs_experiment_id', 'runs', ['experiment_id'])
    op.create_index('idx_runs_fingerprint', 'runs', ['run_fingerprint'])

def downgrade() -> None:
    op.drop_table('runs')
    op.drop_table('experiments')
```

---

#### Phase 2: モデル・データセットテーブル

```python
"""Create model and dataset tables

Revision ID: 002
Revises: 001
Create Date: 2025-11-03
"""

def upgrade() -> None:
    # models テーブル
    op.create_table(
        'models',
        # ... (テーブル定義)
    )
    
    # datasets テーブル
    op.create_table(
        'datasets',
        # ... (テーブル定義)
    )
    
    # dataset_features テーブル
    op.create_table(
        'dataset_features',
        # ... (テーブル定義)
    )

def downgrade() -> None:
    op.drop_table('dataset_features')
    op.drop_table('datasets')
    op.drop_table('models')
```

---

#### Phase 3: 評価・予測テーブル（パーティショニング）

```python
"""Create metrics and predictions tables with partitioning

Revision ID: 003
Revises: 002
Create Date: 2025-11-03
"""

def upgrade() -> None:
    # predictions テーブル（パーティション親）
    op.execute("""
        CREATE TABLE predictions (
            prediction_id BIGSERIAL,
            run_id BIGINT NOT NULL,
            model_id BIGINT NOT NULL,
            prediction_date TIMESTAMP NOT NULL,
            unique_id TEXT NOT NULL,
            horizon INTEGER NOT NULL,
            predicted_value DOUBLE PRECISION NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (prediction_id, prediction_date),
            FOREIGN KEY (run_id) REFERENCES runs(run_id) ON DELETE CASCADE,
            FOREIGN KEY (model_id) REFERENCES models(model_id) ON DELETE CASCADE
        ) PARTITION BY RANGE (prediction_date);
    """)
    
    # 四半期ごとのパーティション作成
    for year in [2025, 2026]:
        for q in range(1, 5):
            start_month = (q - 1) * 3 + 1
            end_month = start_month + 3
            op.execute(f"""
                CREATE TABLE predictions_{year}_q{q} PARTITION OF predictions
                FOR VALUES FROM ('{year}-{start_month:02d}-01') 
                TO ('{year if end_month <= 12 else year+1}-{end_month if end_month <= 12 else 1:02d}-01');
            """)

def downgrade() -> None:
    op.execute("DROP TABLE predictions CASCADE;")
```

---

### 5.3 マイグレーション実行手順

```bash
# 1. 新しいマイグレーションファイルの生成
alembic revision -m "description_of_changes"

# 2. 自動マイグレーション（既存テーブルとの差分検出）
alembic revision --autogenerate -m "auto_generated_changes"

# 3. マイグレーション適用
alembic upgrade head

# 4. 特定バージョンへのマイグレーション
alembic upgrade <revision_id>

# 5. ロールバック
alembic downgrade -1  # 1つ前のバージョンに戻す
alembic downgrade base  # 初期状態に戻す

# 6. 現在のバージョン確認
alembic current

# 7. マイグレーション履歴表示
alembic history --verbose

# 8. マイグレーションスタンプ（手動でバージョン設定）
alembic stamp head
```

---

## 6. パフォーマンスチューニング

### 6.1 クエリ最適化

#### 6.1.1 EXPLAINの活用

```sql
-- クエリプランの確認
EXPLAIN ANALYZE
SELECT 
    e.experiment_name,
    COUNT(r.run_id) AS total_runs,
    AVG(r.execution_duration_seconds) AS avg_duration
FROM experiments e
LEFT JOIN runs r ON e.experiment_id = r.experiment_id
WHERE e.status = 'active'
GROUP BY e.experiment_id, e.experiment_name
ORDER BY total_runs DESC
LIMIT 10;
```

---

#### 6.1.2 スロークエリの検出

```sql
-- pg_stat_statements 有効化
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- スロークエリトップ10
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time,
    stddev_exec_time
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

---

### 6.2 テーブル最適化

#### 6.2.1 VACUUM設定

```sql
-- 自動VACUUM設定の確認
SHOW autovacuum;
SHOW autovacuum_naptime;
SHOW autovacuum_vacuum_threshold;
SHOW autovacuum_analyze_threshold;

-- テーブルごとのVACUUM統計
SELECT
    schemaname,
    relname,
    last_vacuum,
    last_autovacuum,
    vacuum_count,
    autovacuum_count,
    n_dead_tup,
    n_live_tup
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_dead_tup DESC;

-- 手動VACUUM（必要に応じて）
VACUUM ANALYZE experiments;
VACUUM FULL ANALYZE runs;  -- テーブルロック注意
```

---

#### 6.2.2 ANALYZE統計更新

```sql
-- 統計情報の更新
ANALYZE experiments;
ANALYZE runs;
ANALYZE models;

-- 統計情報の確認
SELECT
    schemaname,
    tablename,
    last_analyze,
    last_autoanalyze,
    analyze_count,
    autoanalyze_count
FROM pg_stat_user_tables
WHERE schemaname = 'public';
```

---

### 6.3 接続プール最適化

#### 6.3.1 SQLAlchemy接続プール設定

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'postgresql://user:password@localhost/ts_forecast_system',
    poolclass=QueuePool,
    pool_size=10,              # 通常接続数
    max_overflow=20,           # 最大追加接続数
    pool_timeout=30,           # 接続タイムアウト（秒）
    pool_recycle=3600,         # 接続再利用時間（秒）
    pool_pre_ping=True,        # 接続チェック有効化
    echo=False,                # SQLログ出力
    echo_pool=False,           # プールログ出力
)
```

---

#### 6.3.2 PgBouncer設定

```ini
# /etc/pgbouncer/pgbouncer.ini
[databases]
ts_forecast_system = host=localhost port=5432 dbname=ts_forecast_system

[pgbouncer]
listen_addr = 127.0.0.1
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

# Connection pooling settings
pool_mode = transaction
max_client_conn = 100
default_pool_size = 20
reserve_pool_size = 5
reserve_pool_timeout = 3

# Server lifetime
server_lifetime = 3600
server_idle_timeout = 600

# Logging
log_connections = 1
log_disconnections = 1
log_pooler_errors = 1
```

---

### 6.4 パーティショニング戦略

#### 6.4.1 範囲パーティショニング

```sql
-- predictions テーブルのパーティション管理

-- 新しいパーティション追加（自動化推奨）
CREATE TABLE predictions_2026_q1 PARTITION OF predictions
    FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');

-- 古いパーティションのDETACH（アーカイブ前）
ALTER TABLE predictions DETACH PARTITION predictions_2023_q1;

-- パーティション削除（データ削除）
DROP TABLE predictions_2023_q1;

-- パーティション情報の確認
SELECT
    parent.relname AS parent_table,
    child.relname AS partition_name,
    pg_get_expr(child.relpartbound, child.oid) AS partition_range
FROM pg_inherits
JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
JOIN pg_class child ON pg_inherits.inhrelid = child.oid
WHERE parent.relname = 'predictions'
ORDER BY child.relname;
```

---

#### 6.4.2 自動パーティション作成

```python
"""
自動パーティション作成スクリプト
"""
from datetime import datetime, timedelta
from sqlalchemy import text

def create_future_partitions(engine, table_name: str, months_ahead: int = 6):
    """
    将来のパーティションを自動作成
    
    Args:
        engine: SQLAlchemy engine
        table_name: パーティション対象テーブル
        months_ahead: 何ヶ月先まで作成するか
    """
    current_date = datetime.now()
    
    for i in range(months_ahead):
        # パーティション期間の計算
        start_date = current_date + timedelta(days=30*i)
        end_date = start_date + timedelta(days=30)
        
        partition_name = f"{table_name}_{start_date.year}_{start_date.month:02d}"
        
        sql = f"""
        CREATE TABLE IF NOT EXISTS {partition_name} PARTITION OF {table_name}
        FOR VALUES FROM ('{start_date.strftime('%Y-%m-%d')}') 
        TO ('{end_date.strftime('%Y-%m-%d')}');
        """
        
        with engine.begin() as conn:
            conn.execute(text(sql))
            print(f"Created partition: {partition_name}")

# 使用例
if __name__ == "__main__":
    from sqlalchemy import create_engine
    engine = create_engine('postgresql://user:pass@localhost/ts_forecast_system')
    
    # predictions テーブルの6ヶ月先までパーティション作成
    create_future_partitions(engine, 'predictions', months_ahead=6)
    
    # system_logs テーブルの3ヶ月先までパーティション作成
    create_future_partitions(engine, 'system_logs', months_ahead=3)
```

---

### 6.5 キャッシング戦略

#### 6.5.1 マテリアライズドビュー

```sql
-- 実験サマリービュー
CREATE MATERIALIZED VIEW mv_experiment_summary AS
SELECT
    e.experiment_id,
    e.experiment_name,
    e.status,
    COUNT(r.run_id) AS total_runs,
    COUNT(CASE WHEN r.status = 'completed' THEN 1 END) AS completed_runs,
    COUNT(CASE WHEN r.status = 'failed' THEN 1 END) AS failed_runs,
    AVG(r.execution_duration_seconds) AS avg_duration,
    MAX(r.end_time) AS last_run_time,
    e.created_at
FROM experiments e
LEFT JOIN runs r ON e.experiment_id = r.experiment_id
WHERE e.deleted_at IS NULL
GROUP BY e.experiment_id, e.experiment_name, e.status, e.created_at;

-- インデックス作成
CREATE UNIQUE INDEX idx_mv_exp_summary_id ON mv_experiment_summary(experiment_id);
CREATE INDEX idx_mv_exp_summary_name ON mv_experiment_summary(experiment_name);

-- 定期的なリフレッシュ（cronジョブ推奨）
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_experiment_summary;
```

---

#### 6.5.2 モデルパフォーマンスサマリー

```sql
CREATE MATERIALIZED VIEW mv_model_performance AS
SELECT
    m.model_id,
    m.model_name,
    m.model_type,
    m.framework,
    r.run_id,
    r.experiment_id,
    -- 評価指標の集計
    MAX(CASE WHEN mt.metric_name = 'mae' AND mt.dataset_type = 'validation' 
        THEN mt.metric_value END) AS validation_mae,
    MAX(CASE WHEN mt.metric_name = 'rmse' AND mt.dataset_type = 'validation' 
        THEN mt.metric_value END) AS validation_rmse,
    MAX(CASE WHEN mt.metric_name = 'smape' AND mt.dataset_type = 'validation' 
        THEN mt.metric_value END) AS validation_smape,
    MAX(CASE WHEN mt.metric_name = 'mae' AND mt.dataset_type = 'test' 
        THEN mt.metric_value END) AS test_mae,
    MAX(CASE WHEN mt.metric_name = 'rmse' AND mt.dataset_type = 'test' 
        THEN mt.metric_value END) AS test_rmse,
    MAX(CASE WHEN mt.metric_name = 'smape' AND mt.dataset_type = 'test' 
        THEN mt.metric_value END) AS test_smape,
    m.training_duration_seconds,
    m.model_size_bytes,
    m.created_at
FROM models m
JOIN runs r ON m.run_id = r.run_id
LEFT JOIN metrics mt ON m.model_id = mt.model_id
WHERE m.status = 'evaluated'
GROUP BY m.model_id, m.model_name, m.model_type, m.framework, 
         r.run_id, r.experiment_id, m.training_duration_seconds, 
         m.model_size_bytes, m.created_at;

-- インデックス
CREATE UNIQUE INDEX idx_mv_model_perf_id ON mv_model_performance(model_id);
CREATE INDEX idx_mv_model_perf_type ON mv_model_performance(model_type);
```

---

## 7. バックアップ戦略

### 7.1 バックアップ方針

#### 7.1.1 バックアップ要件

| 項目 | 要件 | 実装 |
|-----|------|------|
| **RPO** (Recovery Point Objective) | 1時間 | 継続的アーカイブ + 定期バックアップ |
| **RTO** (Recovery Time Objective) | 4時間 | ホットスタンバイ + PITR |
| **保持期間** | 30日間（フル）、90日間（アーカイブ） | 自動ローテーション |
| **バックアップ頻度** | 毎日（フル）、1時間（差分） | cronジョブ |
| **バックアップ場所** | ローカル + 外部ストレージ | S3/GCS/Azure Blob |

---

### 7.2 バックアップスクリプト

#### 7.2.1 フルバックアップ

```bash
#!/bin/bash
# full_backup.sh

set -e

# 設定
DB_NAME="ts_forecast_system"
DB_USER="postgres"
BACKUP_DIR="/var/backups/postgresql"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/full_${DB_NAME}_${DATE}.sql.gz"

# バックアップディレクトリ作成
mkdir -p "${BACKUP_DIR}"

# フルバックアップ実行
echo "[$(date)] Starting full backup..."
pg_dump -U "${DB_USER}" -Fc -Z9 "${DB_NAME}" | gzip > "${BACKUP_FILE}"

# バックアップ検証
if [ -f "${BACKUP_FILE}" ]; then
    echo "[$(date)] Backup completed: ${BACKUP_FILE}"
    echo "[$(date)] Backup size: $(du -h ${BACKUP_FILE} | cut -f1)"
else
    echo "[$(date)] ERROR: Backup failed!"
    exit 1
fi

# 古いバックアップの削除
find "${BACKUP_DIR}" -name "full_${DB_NAME}_*.sql.gz" -mtime +${RETENTION_DAYS} -delete
echo "[$(date)] Old backups cleaned up (retention: ${RETENTION_DAYS} days)"

# 外部ストレージへのコピー（オプション）
# aws s3 cp "${BACKUP_FILE}" "s3://my-bucket/backups/"

echo "[$(date)] Backup process completed successfully"
```

---

#### 7.2.2 継続的アーカイブ（WAL）

```bash
#!/bin/bash
# wal_archive.sh

set -e

# 設定
ARCHIVE_DIR="/var/backups/postgresql/wal_archive"
WAL_FILE=$1
WAL_PATH=$2

# アーカイブディレクトリ作成
mkdir -p "${ARCHIVE_DIR}"

# WALファイルをアーカイブ
if [ -f "${WAL_PATH}" ]; then
    gzip -c "${WAL_PATH}" > "${ARCHIVE_DIR}/${WAL_FILE}.gz"
    echo "[$(date)] WAL archived: ${WAL_FILE}"
else
    echo "[$(date)] ERROR: WAL file not found: ${WAL_PATH}"
    exit 1
fi
```

**postgresql.conf設定**:

```ini
# WAL設定
wal_level = replica
archive_mode = on
archive_command = '/path/to/wal_archive.sh %f %p'
archive_timeout = 300  # 5分

# チェックポイント設定
checkpoint_timeout = 5min
max_wal_size = 2GB
min_wal_size = 1GB
```

---

#### 7.2.3 差分バックアップ

```bash
#!/bin/bash
# incremental_backup.sh

set -e

# 設定
DB_NAME="ts_forecast_system"
DB_USER="postgres"
BACKUP_DIR="/var/backups/postgresql/incremental"
BASE_BACKUP_DIR="/var/backups/postgresql/base"
DATE=$(date +%Y%m%d_%H%M%S)

# ベースバックアップの存在確認
if [ ! -d "${BASE_BACKUP_DIR}/base" ]; then
    echo "[$(date)] ERROR: Base backup not found. Run base_backup.sh first."
    exit 1
fi

# 増分バックアップ実行
mkdir -p "${BACKUP_DIR}"
pg_basebackup -U "${DB_USER}" -D "${BACKUP_DIR}/${DATE}" \
    -Fp -Xs -P -R --incremental="${BASE_BACKUP_DIR}/base/backup_manifest"

echo "[$(date)] Incremental backup completed: ${BACKUP_DIR}/${DATE}"
```

---

### 7.3 リストア手順

#### 7.3.1 フルリストア

```bash
#!/bin/bash
# restore_full.sh

set -e

BACKUP_FILE=$1
DB_NAME="ts_forecast_system"
DB_USER="postgres"

if [ -z "${BACKUP_FILE}" ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    exit 1
fi

# データベースを削除して再作成
echo "[$(date)] Dropping database..."
psql -U "${DB_USER}" -c "DROP DATABASE IF EXISTS ${DB_NAME};"
psql -U "${DB_USER}" -c "CREATE DATABASE ${DB_NAME};"

# リストア実行
echo "[$(date)] Restoring from backup..."
gunzip -c "${BACKUP_FILE}" | pg_restore -U "${DB_USER}" -d "${DB_NAME}" -Fc

echo "[$(date)] Restore completed successfully"

# 統計情報の更新
echo "[$(date)] Analyzing database..."
psql -U "${DB_USER}" -d "${DB_NAME}" -c "ANALYZE;"

echo "[$(date)] Database ready for use"
```

---

#### 7.3.2 PITR（Point-In-Time Recovery）

```bash
#!/bin/bash
# restore_pitr.sh

set -e

BACKUP_DIR="/var/backups/postgresql/base"
WAL_ARCHIVE_DIR="/var/backups/postgresql/wal_archive"
TARGET_TIME=$1  # 例: '2025-11-03 14:30:00'
DATA_DIR="/var/lib/postgresql/15/main"

if [ -z "${TARGET_TIME}" ]; then
    echo "Usage: $0 'YYYY-MM-DD HH:MM:SS'"
    exit 1
fi

# PostgreSQLの停止
systemctl stop postgresql

# データディレクトリのバックアップ
mv "${DATA_DIR}" "${DATA_DIR}.old"

# ベースバックアップのリストア
cp -r "${BACKUP_DIR}/base" "${DATA_DIR}"

# recovery.conf作成（PostgreSQL 12+では recovery.signal）
cat > "${DATA_DIR}/postgresql.auto.conf" <<EOF
restore_command = 'gunzip -c ${WAL_ARCHIVE_DIR}/%f.gz > %p'
recovery_target_time = '${TARGET_TIME}'
recovery_target_action = 'promote'
EOF

touch "${DATA_DIR}/recovery.signal"

# PostgreSQLの起動
systemctl start postgresql

echo "[$(date)] PITR recovery initiated. Target time: ${TARGET_TIME}"
echo "[$(date)] Check PostgreSQL logs for recovery progress"
```

---

### 7.4 バックアップ監視

#### 7.4.1 バックアップステータスチェック

```sql
-- バックアップ状態の確認
SELECT
    pg_current_wal_lsn() AS current_wal_lsn,
    pg_walfile_name(pg_current_wal_lsn()) AS current_wal_file,
    pg_last_wal_receive_lsn() AS last_received_lsn,
    pg_last_wal_replay_lsn() AS last_replayed_lsn,
    (pg_current_wal_lsn() - pg_last_wal_replay_lsn())::bigint AS replication_lag_bytes;

-- アーカイブ状態の確認
SELECT
    archived_count,
    last_archived_wal,
    last_archived_time,
    failed_count,
    last_failed_wal,
    last_failed_time
FROM pg_stat_archiver;
```

---

#### 7.4.2 バックアップ検証

```bash
#!/bin/bash
# verify_backup.sh

set -e

BACKUP_FILE=$1
TEMP_DB="ts_forecast_system_verify"
DB_USER="postgres"

if [ -z "${BACKUP_FILE}" ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    exit 1
fi

echo "[$(date)] Starting backup verification..."

# 一時データベース作成
psql -U "${DB_USER}" -c "DROP DATABASE IF EXISTS ${TEMP_DB};"
psql -U "${DB_USER}" -c "CREATE DATABASE ${TEMP_DB};"

# リストア実行
if gunzip -c "${BACKUP_FILE}" | pg_restore -U "${DB_USER}" -d "${TEMP_DB}" -Fc; then
    echo "[$(date)] Backup verification successful: ${BACKUP_FILE}"
    
    # テーブル数確認
    TABLE_COUNT=$(psql -U "${DB_USER}" -d "${TEMP_DB}" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")
    echo "[$(date)] Tables restored: ${TABLE_COUNT}"
    
    # クリーンアップ
    psql -U "${DB_USER}" -c "DROP DATABASE ${TEMP_DB};"
    exit 0
else
    echo "[$(date)] ERROR: Backup verification failed!"
    psql -U "${DB_USER}" -c "DROP DATABASE IF EXISTS ${TEMP_DB};"
    exit 1
fi
```

---

## 8. セキュリティ

### 8.1 アクセス制御

#### 8.1.1 ロール・権限管理

```sql
-- 読み取り専用ロール
CREATE ROLE readonly_user;
GRANT CONNECT ON DATABASE ts_forecast_system TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT SELECT ON TABLES TO readonly_user;

-- データサイエンティストロール
CREATE ROLE data_scientist;
GRANT CONNECT ON DATABASE ts_forecast_system TO data_scientist;
GRANT USAGE ON SCHEMA public TO data_scientist;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO data_scientist;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO data_scientist;

-- 管理者ロール
CREATE ROLE admin_user WITH CREATEDB CREATEROLE;
GRANT ALL PRIVILEGES ON DATABASE ts_forecast_system TO admin_user;

-- ユーザー作成例
CREATE USER alice WITH PASSWORD 'secure_password_here';
GRANT data_scientist TO alice;
```

---

#### 8.1.2 行レベルセキュリティ（RLS）

```sql
-- RLS有効化
ALTER TABLE experiments ENABLE ROW LEVEL SECURITY;

-- ポリシー作成: ユーザーは自分の実験のみ参照可能
CREATE POLICY user_experiments_policy ON experiments
    FOR SELECT
    USING (created_by = current_user OR current_user IN (SELECT user_id FROM users WHERE is_superuser = TRUE));

-- ポリシー作成: ユーザーは自分の実験のみ更新可能
CREATE POLICY user_experiments_update_policy ON experiments
    FOR UPDATE
    USING (created_by = current_user)
    WITH CHECK (created_by = current_user);
```

---

### 8.2 データ暗号化

#### 8.2.1 接続暗号化（SSL/TLS）

**postgresql.conf設定**:

```ini
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'
ssl_ca_file = '/etc/ssl/certs/ca.crt'
ssl_ciphers = 'HIGH:MEDIUM:+3DES:!aNULL'
ssl_prefer_server_ciphers = on
ssl_min_protocol_version = 'TLSv1.2'
```

**pg_hba.conf設定**:

```
# TYPE  DATABASE        USER            ADDRESS                 METHOD
hostssl all             all             0.0.0.0/0               md5
hostssl all             all             ::/0                    md5
```

---

#### 8.2.2 データ暗号化（pgcrypto）

```sql
-- pgcrypto拡張のインストール
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 機密データの暗号化例
CREATE TABLE secure_config (
    config_id SERIAL PRIMARY KEY,
    config_key VARCHAR(255) NOT NULL,
    config_value_encrypted BYTEA NOT NULL,
    encryption_key_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 暗号化関数
CREATE OR REPLACE FUNCTION encrypt_value(
    plain_text TEXT,
    encryption_key TEXT
) RETURNS BYTEA AS $$
BEGIN
    RETURN pgp_sym_encrypt(plain_text, encryption_key);
END;
$$ LANGUAGE plpgsql;

-- 復号化関数
CREATE OR REPLACE FUNCTION decrypt_value(
    encrypted_data BYTEA,
    encryption_key TEXT
) RETURNS TEXT AS $$
BEGIN
    RETURN pgp_sym_decrypt(encrypted_data, encryption_key);
END;
$$ LANGUAGE plpgsql;

-- 使用例
INSERT INTO secure_config (config_key, config_value_encrypted, encryption_key_id)
VALUES ('api_key', encrypt_value('secret_api_key_value', 'encryption_password'), 'key_v1');

-- 復号化して取得
SELECT config_key, decrypt_value(config_value_encrypted, 'encryption_password') AS config_value
FROM secure_config
WHERE config_key = 'api_key';
```

---

### 8.3 監査・ロギング

#### 8.3.1 監査ログ設定

**postgresql.conf設定**:

```ini
# ロギング設定
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB

# 何をログに記録するか
log_connections = on
log_disconnections = on
log_duration = on
log_line_prefix = '%t [%p]: user=%u,db=%d,app=%a,client=%h '
log_statement = 'all'  # または 'ddl', 'mod', 'none'
log_min_duration_statement = 1000  # 1秒以上のクエリをログ

# エラーログ
log_error_verbosity = default
log_min_messages = warning
```

---

#### 8.3.2 監査トリガー

```sql
-- 監査ログトリガー関数
CREATE OR REPLACE FUNCTION audit.log_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit.audit_logs (
            table_name, operation_type, record_id, new_values,
            user_id, user_ip
        ) VALUES (
            TG_TABLE_NAME, 'INSERT', NEW.experiment_id, to_jsonb(NEW),
            current_user, inet_client_addr()
        );
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit.audit_logs (
            table_name, operation_type, record_id,
            old_values, new_values, changed_fields,
            user_id, user_ip
        ) VALUES (
            TG_TABLE_NAME, 'UPDATE', NEW.experiment_id,
            to_jsonb(OLD), to_jsonb(NEW),
            jsonb_object_agg(key, value)
                FILTER (WHERE to_jsonb(OLD) -> key IS DISTINCT FROM to_jsonb(NEW) -> key),
            current_user, inet_client_addr()
        );
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit.audit_logs (
            table_name, operation_type, record_id, old_values,
            user_id, user_ip
        ) VALUES (
            TG_TABLE_NAME, 'DELETE', OLD.experiment_id, to_jsonb(OLD),
            current_user, inet_client_addr()
        );
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- トリガー作成
CREATE TRIGGER experiments_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON experiments
    FOR EACH ROW
    EXECUTE FUNCTION audit.log_changes();

CREATE TRIGGER models_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON models
    FOR EACH ROW
    EXECUTE FUNCTION audit.log_changes();
```

---

## 9. 運用手順

### 9.1 日次運用

#### 9.1.1 ヘルスチェック

```sql
-- データベース接続数確認
SELECT 
    count(*) AS total_connections,
    count(*) FILTER (WHERE state = 'active') AS active_connections,
    count(*) FILTER (WHERE state = 'idle') AS idle_connections
FROM pg_stat_activity
WHERE datname = 'ts_forecast_system';

-- テーブルサイズ確認
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    n_live_tup AS row_count
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;

-- インデックスヘルス確認
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
  AND idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```

---

#### 9.1.2 パフォーマンス監視

```sql
-- 実行中の長時間クエリ
SELECT
    pid,
    now() - query_start AS duration,
    usename,
    state,
    query
FROM pg_stat_activity
WHERE state != 'idle'
  AND now() - query_start > interval '5 minutes'
ORDER BY duration DESC;

-- ロック待ち確認
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks 
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

---

### 9.2 週次運用

#### 9.2.1 統計情報更新

```bash
#!/bin/bash
# weekly_maintenance.sh

set -e

DB_NAME="ts_forecast_system"
DB_USER="postgres"

echo "[$(date)] Starting weekly maintenance..."

# VACUUM ANALYZE
echo "[$(date)] Running VACUUM ANALYZE..."
psql -U "${DB_USER}" -d "${DB_NAME}" -c "VACUUM ANALYZE;"

# インデックス再構築（必要な場合のみ）
echo "[$(date)] Checking for bloated indexes..."
psql -U "${DB_USER}" -d "${DB_NAME}" <<EOF
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND pg_relation_size(indexrelid) > 10485760  -- 10MB以上
ORDER BY pg_relation_size(indexrelid) DESC;
EOF

# マテリアライズドビューの更新
echo "[$(date)] Refreshing materialized views..."
psql -U "${DB_USER}" -d "${DB_NAME}" -c "REFRESH MATERIALIZED VIEW CONCURRENTLY mv_experiment_summary;"
psql -U "${DB_USER}" -d "${DB_NAME}" -c "REFRESH MATERIALIZED VIEW CONCURRENTLY mv_model_performance;"

echo "[$(date)] Weekly maintenance completed"
```

---

### 9.3 月次運用

#### 9.3.1 容量管理

```bash
#!/bin/bash
# monthly_capacity_report.sh

set -e

DB_NAME="ts_forecast_system"
DB_USER="postgres"
REPORT_FILE="/var/log/postgresql/capacity_report_$(date +%Y%m).txt"

echo "Database Capacity Report - $(date)" > "${REPORT_FILE}"
echo "========================================" >> "${REPORT_FILE}"

# データベースサイズ
echo -e "\n## Database Size ##" >> "${REPORT_FILE}"
psql -U "${DB_USER}" -d "${DB_NAME}" -t -c "
SELECT pg_size_pretty(pg_database_size('${DB_NAME}'));
" >> "${REPORT_FILE}"

# テーブルサイズトップ10
echo -e "\n## Top 10 Largest Tables ##" >> "${REPORT_FILE}"
psql -U "${DB_USER}" -d "${DB_NAME}" -t -c "
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
" >> "${REPORT_FILE}"

# 成長率の計算（前月比）
echo -e "\n## Growth Rate ##" >> "${REPORT_FILE}"
# 実装省略（前月のレポートと比較）

cat "${REPORT_FILE}"
```

---

### 9.4 トラブルシューティング

#### 9.4.1 接続エラー

```bash
# 接続数上限確認
psql -U postgres -c "SHOW max_connections;"

# 現在の接続数確認
psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# アイドル接続の強制終了
psql -U postgres -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'ts_forecast_system'
  AND state = 'idle'
  AND state_change < now() - interval '1 hour';
"
```

---

#### 9.4.2 スロークエリ対応

```sql
-- スロークエリの特定
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    rows
FROM pg_stat_statements
WHERE mean_exec_time > 1000  -- 1秒以上
ORDER BY mean_exec_time DESC
LIMIT 10;

-- クエリプラン確認
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT ...;  -- 該当クエリ

-- インデックス追加
CREATE INDEX idx_name ON table_name(column_name);
ANALYZE table_name;
```

---

## 10. 付録

### 10.1 SQLAlchemy モデル例

```python
"""
SQLAlchemy ORM モデル定義
"""
from sqlalchemy import (
    Column, BigInteger, String, Text, Integer, Boolean, 
    TIMESTAMP, Numeric, ForeignKey, CheckConstraint, UniqueConstraint,
    Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class Experiment(Base):
    """実験テーブル"""
    __tablename__ = 'experiments'
    
    experiment_id = Column(BigInteger, primary_key=True, autoincrement=True)
    experiment_name = Column(String(255), nullable=False)
    experiment_description = Column(Text)
    experiment_type = Column(String(50), nullable=False, default='training')
    status = Column(String(50), nullable=False, default='active')
    lifecycle_stage = Column(String(50), nullable=False, default='active')
    created_by = Column(String(255))
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    deleted_at = Column(TIMESTAMP)
    tags = Column(JSONB, nullable=False, server_default='{}')
    metadata = Column('metadata', JSONB, nullable=False, server_default='{}')
    
    # リレーションシップ
    runs = relationship("Run", back_populates="experiment", cascade="all, delete-orphan")
    
    # 制約
    __table_args__ = (
        CheckConstraint(status.in_(['active', 'archived', 'deleted']), name='ck_experiments_status'),
        CheckConstraint(lifecycle_stage.in_(['active', 'deleted', 'archived']), name='ck_experiments_lifecycle'),
        Index('idx_experiments_name', 'experiment_name'),
        Index('idx_experiments_created_at', 'created_at'),
    )


class Run(Base):
    """実行テーブル"""
    __tablename__ = 'runs'
    
    run_id = Column(BigInteger, primary_key=True, autoincrement=True)
    run_uuid = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4)
    experiment_id = Column(BigInteger, ForeignKey('experiments.experiment_id', ondelete='CASCADE'), nullable=False)
    parent_run_id = Column(BigInteger, ForeignKey('runs.run_id', ondelete='SET NULL'))
    run_name = Column(String(255), nullable=False)
    run_description = Column(Text)
    run_fingerprint = Column(String(64), nullable=False)
    status = Column(String(50), nullable=False, default='running')
    lifecycle_stage = Column(String(50), nullable=False, default='active')
    start_time = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    end_time = Column(TIMESTAMP)
    execution_duration_seconds = Column(Numeric(12, 3))
    source_type = Column(String(50))
    source_name = Column(Text)
    git_commit_hash = Column(String(40))
    git_branch = Column(String(255))
    user_id = Column(String(255))
    tags = Column(JSONB, nullable=False, server_default='{}')
    metadata = Column('metadata', JSONB, nullable=False, server_default='{}')
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    deleted_at = Column(TIMESTAMP)
    
    # リレーションシップ
    experiment = relationship("Experiment", back_populates="runs")
    models = relationship("Model", back_populates="run", cascade="all, delete-orphan")
    metrics = relationship("Metric", back_populates="run", cascade="all, delete-orphan")
    hyperparameters = relationship("Hyperparameter", back_populates="run", cascade="all, delete-orphan")
    artifacts = relationship("Artifact", back_populates="run", cascade="all, delete-orphan")
    
    # 制約
    __table_args__ = (
        CheckConstraint(status.in_(['running', 'completed', 'failed', 'killed', 'scheduled']), name='ck_runs_status'),
        UniqueConstraint('experiment_id', 'run_fingerprint', name='uq_run_fingerprint'),
        Index('idx_runs_experiment_id', 'experiment_id'),
        Index('idx_runs_fingerprint', 'run_fingerprint'),
        Index('idx_runs_status', 'status'),
    )


class Model(Base):
    """モデルテーブル"""
    __tablename__ = 'models'
    
    model_id = Column(BigInteger, primary_key=True, autoincrement=True)
    model_uuid = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4)
    run_id = Column(BigInteger, ForeignKey('runs.run_id', ondelete='CASCADE'), nullable=False)
    model_name = Column(String(255), nullable=False)
    model_type = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False, default='1.0.0')
    framework = Column(String(50), nullable=False)
    framework_version = Column(String(50))
    model_config = Column(JSONB, nullable=False)
    hyperparameters = Column(JSONB, nullable=False, server_default='{}')
    training_dataset_id = Column(BigInteger, ForeignKey('datasets.dataset_id'))
    training_samples = Column(Integer)
    training_duration_seconds = Column(Numeric(12, 3))
    model_size_bytes = Column(BigInteger)
    model_file_path = Column(Text, nullable=False)
    checkpoint_path = Column(Text)
    status = Column(String(50), nullable=False, default='training')
    tags = Column(JSONB, nullable=False, server_default='{}')
    metadata = Column('metadata', JSONB, nullable=False, server_default='{}')
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # リレーションシップ
    run = relationship("Run", back_populates="models")
    registry = relationship("ModelRegistry", back_populates="model", uselist=False)
    
    # 制約
    __table_args__ = (
        CheckConstraint(status.in_(['training', 'trained', 'evaluating', 'evaluated', 'deployed', 'archived', 'failed']), 
                       name='ck_models_status'),
        Index('idx_models_run_id', 'run_id'),
        Index('idx_models_type', 'model_type'),
    )
```

---

### 10.2 データベース初期化スクリプト

```python
#!/usr/bin/env python3
"""
データベース初期化スクリプト
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pathlib import Path

def init_database(database_url: str):
    """データベースを初期化"""
    
    # エンジン作成
    engine = create_engine(database_url, echo=True)
    Session = sessionmaker(bind=engine)
    
    # スキーマ作成
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS audit;"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS staging;"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS archive;"))
    
    # 拡張機能インストール
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_stat_statements;"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto;"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"))
    
    # Alembicマイグレーション実行
    import subprocess
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    
    # デフォルトデータ挿入
    with Session() as session:
        # system_config
        from models import SystemConfig
        default_configs = [
            SystemConfig(config_key='max_parallel_runs', config_value='10', config_type='integer'),
            SystemConfig(config_key='default_retention_days', config_value='90', config_type='integer'),
            SystemConfig(config_key='enable_mlflow', config_value='true', config_type='boolean'),
        ]
        session.add_all(default_configs)
        session.commit()
    
    print("Database initialization completed successfully!")

if __name__ == "__main__":
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost/ts_forecast_system')
    init_database(database_url)
```

---

### 10.3 用語集

| 用語 | 説明 |
|-----|------|
| **B-Tree** | 平衡木構造のインデックス。範囲検索に適している |
| **GIN** | Generalized Inverted Index。JSONB、配列、全文検索に使用 |
| **MVCC** | Multi-Version Concurrency Control。PostgreSQLの並行制御方式 |
| **WAL** | Write-Ahead Logging。トランザクションログ |
| **VACUUM** | 不要なタプルの削除とディスク領域の回収 |
| **ANALYZE** | テーブルの統計情報を更新 |
| **REINDEX** | インデックスの再構築 |
| **PITR** | Point-In-Time Recovery。特定時点への復元 |
| **RLS** | Row Level Security。行レベルのアクセス制御 |
| **Partition** | テーブルを複数の物理的なテーブルに分割 |

---

## まとめ

本データベース設計書では、時系列予測システムに必要な以下を定義しました：

### ✅ 主要成果物

1. **15のコアテーブル定義**
   - 実験管理（experiments, runs）
   - モデル管理（models, model_registry）
   - データセット管理（datasets, dataset_features）
   - 評価指標（metrics, metric_summaries）
   - ハイパーパラメータ（hyperparameters, hyperparameter_search_spaces）
   - アーティファクト（artifacts）
   - 予測結果（predictions）
   - ログ・監査（system_logs, audit_logs）
   - ユーザー管理（users, user_experiments）
   - 設定（system_config, tags）

2. **包括的なインデックス設計**
   - B-Treeインデックス（範囲検索・ソート）
   - GINインデックス（JSONB検索）
   - 部分インデックス（特定条件の最適化）
   - 複合インデックス（複数カラム検索）

3. **パーティショニング戦略**
   - 時系列データの四半期パーティション
   - ログデータの月次パーティション
   - 自動パーティション管理

4. **完全なマイグレーション計画**
   - Alembic設定
   - フェーズ別マイグレーション
   - ロールバック手順

5. **パフォーマンスチューニング**
   - クエリ最適化
   - 接続プール設定
   - マテリアライズドビュー

6. **バックアップ・リストア戦略**
   - フルバックアップ（日次）
   - 継続的アーカイブ（WAL）
   - PITR対応

7. **セキュリティ対策**
   - ロール・権限管理
   - 行レベルセキュリティ
   - データ暗号化
   - 監査ログ

8. **運用手順**
   - 日次・週次・月次タスク
   - ヘルスチェック
   - トラブルシューティング

---

**データベース設計の特徴**:

- ✅ **拡張性**: パーティショニングによる大規模データ対応
- ✅ **パフォーマンス**: 適切なインデックス設計
- ✅ **可用性**: 包括的なバックアップ戦略
- ✅ **セキュリティ**: 多層防御によるデータ保護
- ✅ **保守性**: 明確な運用手順とツール

---

**次のステップ**:

1. ✅ 本設計書のレビュー
2. 📝 Alembicマイグレーションファイルの作成
3. 🧪 ローカル環境でのデータベース構築テスト
4. 🔧 SQLAlchemy ORMモデルの実装
5. 📊 パフォーマンステストの実施
6. 🚀 本番環境へのデプロイ準備

---

**End of Document**
