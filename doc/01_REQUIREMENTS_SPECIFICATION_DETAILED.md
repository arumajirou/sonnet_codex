# 詳細要件定義書
**Detailed Requirements Specification for Time Series Forecasting System**

---

## 📋 ドキュメント情報

| 項目 | 内容 |
|-----|------|
| **ドキュメントタイトル** | 時系列予測モデル生成・評価・再学習システム 詳細要件定義書 |
| **バージョン** | v1.0.0 (詳細版) |
| **作成日** | 2025-11-03 |
| **最終更新日** | 2025-11-03 |
| **ステータス** | 承認待ち |
| **対象システム** | NeuralForecast Auto Runner + Time Series Forecasting System |
| **スコープ** | データ取得 → 特徴量生成 → 学習 → 評価 → 分析（相関/因果/寄与度） → 再学習 → 予測 → 可視化 → 運用 |
| **想定環境** | ローカル（PostgreSQL, File System, GPU/CPU）、ログ統合（W&B, MLflow, Ray, Lightning, Optuna） |

---

## 目次

1. [目的と背景](#1-目的と背景)
2. [用語定義](#2-用語定義)
3. [ステークホルダーと役割](#3-ステークホルダーと役割)
4. [前提条件と制約](#4-前提条件と制約)
5. [機能要件詳細](#5-機能要件詳細)
6. [非機能要件詳細](#6-非機能要件詳細)
7. [API仕様詳細](#7-api仕様詳細)
8. [データスキーマ詳細](#8-データスキーマ詳細)
9. [品質属性](#9-品質属性)
10. [制約事項](#10-制約事項)
11. [リスクと対策](#11-リスクと対策)
12. [付録](#12-付録)

---

## 1. 目的と背景

### 1.1 目的

本システムは、時系列データに対する機械学習モデルの**生成、評価、再学習、予測**を自動化し、以下を実現することを目的とします：

#### 主要目的

1. **高精度な予測**: 複数のモデルとハイパーパラメータを自動探索し、最適なモデルを選択
2. **再現性の確保**: すべての実験を完全に再現可能な状態で記録
3. **効率的な運用**: 重複実行の自動スキップ、並列実行による高速化
4. **包括的な分析**: モデルの特性、相関、因果関係、寄与度を統計的に分析
5. **拡張性の確保**: 新しいモデルライブラリやフレームワークを容易に追加可能

---

### 1.2 背景

#### 現状の課題

1. **手動運用の負担**: モデル選択、ハイパーパラメータ調整、評価が手動
2. **再現性の欠如**: 実験結果を正確に再現できない
3. **重複実行のムダ**: 同じ条件での実験が繰り返される
4. **分析の困難**: モデル特性や寄与度の把握が不十分
5. **拡張の困難**: 新しいモデルの追加に多大な工数

#### 解決アプローチ

1. **自動化**: モデル検出、実験計画、実行、評価を自動化
2. **標準化**: 共通インターフェース（Adapter）によるモデル統一
3. **トラッキング**: PostgreSQL + MLflow/W&Bによる包括的記録
4. **スマート実行**: Fingerprintによる重複検出とスキップ
5. **モジュール設計**: プラグイン可能なアーキテクチャ

---

### 1.3 スコープ

#### 含まれる範囲（In Scope）

- ✅ データ取得・準備（CSV scraping → 正規化）
- ✅ 特徴量生成・評価（Lag, MA, Seasonal, Exog）
- ✅ モデル学習・探索・評価（NeuralForecast + 拡張可能）
- ✅ メトリクス計算（MAE, RMSE, sMAPE, MASE, MAPE）
- ✅ 因果・相関・寄与度分析（Granger, Permutation Importance）
- ✅ 実験管理（Experiment/Run構造、重複スキップ）
- ✅ 再学習スケジューリング（定期/オンデマンド）
- ✅ 予測配信（バッチ/インタラクティブ）
- ✅ モデルレジストリ（バージョン管理、ステージ遷移）
- ✅ 可視化UI（リソース表示、学習、分析、評価）
- ✅ ロギング・メタデータストレージ（PostgreSQL必須、MLflow/W&Bオプション）

#### 含まれない範囲（Out of Scope）

- ❌ 外部クラウド・大規模分散ストレージの必須採用
- ❌ 組織横断的なMLOpsインフラ構築（将来拡張可能）
- ❌ リアルタイムストリーミング予測（バッチ中心）
- ❌ AutoML全般（時系列予測に特化）

---

## 2. 用語定義

### 2.1 基本用語

| 用語 | 定義 | 例 |
|-----|------|---|
| **Run** | 1回の学習～評価実行 | 単一のモデル + ハイパーパラメータでの学習 |
| **Experiment** | 同一目的のRun集合 | 同じデータ・評価設計でのハイパーパラメータ比較 |
| **Adapter** | モデル実装の差異を吸収する共通インターフェース | NeuralForecast, Darts, GluonTS用のAdapter |
| **Registry** | モデルのバージョン管理とステージ遷移管理 | Staging → Production への昇格 |
| **Fingerprint** | 実行条件の一意識別子（ハッシュ値） | `run_fingerprint = hash(model, params, data, ...)` |
| **Artifact** | 実験で生成される成果物 | モデルファイル、予測結果、グラフ、ログ |
| **Backtest** | 時系列データでの交差検証 | Rolling-origin, expanding window |
| **Horizon (h)** | 予測期間（ステップ数） | h=7（7ステップ先まで予測） |
| **Exogenous Variable** | 外生変数（予測対象以外の説明変数） | 天気、イベント、休日フラグ |

---

### 2.2 データ関連用語

| 用語 | 定義 | スキーマ |
|-----|------|---------|
| **unique_id** | 時系列の識別子 | TEXT NOT NULL |
| **ds** | 日時（DateStamp） | TIMESTAMP/DATE NOT NULL |
| **y** | 目的変数（予測対象） | NUMERIC NOT NULL |
| **futr_exog** | 未来の外生変数（予測時に利用可能） | NUMERIC/TEXT/BOOL |
| **hist_exog** | 過去の外生変数（予測時に利用不可） | NUMERIC/TEXT/BOOL |
| **stat_exog** | 静的な外生変数（時間に依存しない） | NUMERIC/TEXT/BOOL |

---

### 2.3 モデル関連用語

| 用語 | 定義 | 例 |
|-----|------|---|
| **AutoModel** | NeuralForecastのAuto*クラス | AutoNHITS, AutoLSTM, AutoTFT |
| **Loss Function** | 損失関数 | MAE, MSE, QuantileLoss, Huber |
| **Scaler** | データ正規化手法 | StandardScaler, MinMaxScaler, RobustScaler |
| **Search Algorithm** | ハイパーパラメータ探索アルゴリズム | Optuna, Ray Tune, Grid Search |
| **Backend** | 計算バックエンド | CPU, CUDA, MPS |

---

### 2.4 評価関連用語

| 用語 | 定義 | 計算式 |
|-----|------|--------|
| **MAE** | Mean Absolute Error | `mean(abs(y_true - y_pred))` |
| **RMSE** | Root Mean Squared Error | `sqrt(mean((y_true - y_pred)^2))` |
| **sMAPE** | Symmetric Mean Absolute Percentage Error | `mean(2 * abs(y_true - y_pred) / (abs(y_true) + abs(y_pred)))` |
| **MASE** | Mean Absolute Scaled Error | MAEをナイーブ予測のMAEでスケール |
| **MAPE** | Mean Absolute Percentage Error | `mean(abs((y_true - y_pred) / y_true))` |

---

## 3. ステークホルダーと役割

### 3.1 ステークホルダー一覧

| 役割 | 責務 | 関心事 | 権限 |
|-----|------|--------|------|
| **Product Owner (PO)** | KPI設定、リリース判断 | ビジネス価値、ROI | 承認、優先順位決定 |
| **Data Scientist (DS)** | 特徴量設計、評価設計、分析 | モデル精度、解釈性 | 実験設計、分析手法選択 |
| **Machine Learning Engineer (MLE)** | パイプライン実装、Adapter開発 | 性能、可用性、保守性 | アーキテクチャ決定、技術選定 |
| **SRE/Infra** | リソース管理、監視、運用 | 安定性、コスト | インフラ構成、監視設定 |
| **User (Analyst/Ops)** | UI経由での操作、レポート閲覧 | 使いやすさ、結果の信頼性 | 実験実行、モデル切り替え |

---

### 3.2 RACI マトリクス

| タスク | PO | DS | MLE | SRE | User |
|-------|----|----|-----|-----|------|
| 要件定義 | **A** | **R** | C | C | I |
| 特徴量設計 | C | **A/R** | C | I | I |
| アーキテクチャ設計 | I | C | **A/R** | C | I |
| 実装 | I | C | **A/R** | C | I |
| インフラ構築 | I | I | C | **A/R** | I |
| テスト | I | C | **R** | C | I |
| デプロイ | **A** | I | **R** | **R** | I |
| 運用 | I | I | C | **A/R** | **R** |
| 分析 | I | **A/R** | C | I | C |

**凡例**:
- **R** (Responsible): 実行責任者
- **A** (Accountable): 説明責任者
- **C** (Consulted): 相談先
- **I** (Informed): 報告先

---

## 4. 前提条件と制約

### 4.1 技術的前提条件

#### 4.1.1 ハードウェア

| 項目 | 要件 | 推奨 | 備考 |
|-----|------|------|------|
| **CPU** | x86_64, 4コア以上 | 16コア以上 | 並列実行時 |
| **メモリ** | 16GB以上 | 32GB以上 | 大規模データセット時 |
| **GPU** | CUDA 11.0+対応 | RTX 3060以上 | PyTorch対応GPU |
| **VRAM** | 8GB以上 | 16GB以上 | バッチサイズに依存 |
| **ストレージ** | 100GB以上 | 500GB以上 SSD | アーティファクト保存用 |

---

#### 4.1.2 ソフトウェア

| 項目 | バージョン | 必須/推奨 | 備考 |
|-----|-----------|----------|------|
| **Python** | 3.11+ | 必須 | Type Hints完全対応 |
| **PostgreSQL** | 14+ | 必須 | メタデータストレージ |
| **CUDA** | 11.0+ | 推奨 | GPU使用時 |
| **Docker** | 20.10+ | 推奨 | コンテナ実行時 |
| **Git** | 2.30+ | 必須 | バージョン管理 |

---

#### 4.1.3 Pythonライブラリ

| ライブラリ | バージョン | 用途 |
|----------|-----------|------|
| **neuralforecast** | 1.6+ | 時系列予測モデル |
| **pytorch** | 2.0+ | ディープラーニングバックエンド |
| **lightning** | 2.0+ | 学習フレームワーク |
| **ray** | 2.5+ | 並列実行 |
| **optuna** | 3.2+ | ハイパーパラメータ最適化 |
| **pandas** | 2.0+ | データフレーム操作 |
| **numpy** | 1.24+ | 数値計算 |
| **scikit-learn** | 1.3+ | 前処理、評価 |
| **mlflow** | 2.5+ | 実験トラッキング（オプション） |
| **wandb** | 0.15+ | 実験可視化（オプション） |
| **psycopg2** | 2.9+ | PostgreSQL接続 |
| **sqlalchemy** | 2.0+ | ORM |
| **pydantic** | 2.0+ | データ検証 |
| **hydra-core** | 1.3+ | 設定管理 |
| **structlog** | 23.1+ | 構造化ログ |

---

### 4.2 制約事項

#### 4.2.1 技術的制約

| 制約 | 内容 | 影響 | 回避策 |
|-----|------|------|--------|
| **メモリ制限** | 大規模データセット読み込み時のOOM | 並列数制限 | チャンク読み込み、ダウンサンプリング |
| **GPU VRAM制限** | バッチサイズ制限 | 学習速度低下 | Gradient Accumulation, Mixed Precision |
| **ネットワーク依存** | 外部API（MLflow, W&B）の可用性 | トラッキング失敗 | PostgreSQLフォールバック |
| **並列度制限** | CPUコア数、GPU数 | 実行時間増加 | 優先度付けスケジューリング |

---

#### 4.2.2 ビジネス制約

| 制約 | 内容 | 影響 |
|-----|------|------|
| **予算制限** | クラウドリソース使用不可 | ローカル実行必須 |
| **納期制約** | 3ヶ月以内のリリース | MVP機能に絞る |
| **スキル制約** | DS/MLEのスキルレベル | 複雑な機能は後回し |
| **コンプライアンス** | PII処理不可（デフォルト） | データ匿名化は別プロセス |

---

#### 4.2.3 データ制約

| 制約 | 内容 | 対応 |
|-----|------|------|
| **データ形式** | CSV形式必須 | Parquet対応は将来拡張 |
| **スキーマ** | `unique_id, ds, y`必須 | 自動検証 |
| **欠損値** | 許容するが警告 | 補完方法はユーザー選択 |
| **時間粒度** | 日次～月次を想定 | 秒単位は未対応 |

---

## 5. 機能要件詳細

### 5.1 データ取得・管理 (FR-DATA)

#### 5.1.1 データ取得 (FR-DATA-001)

**概要**: CSV形式のスクレイピング結果を読み込み、標準スキーマに正規化

**優先度**: 高（必須）

**詳細仕様**:

| 項目 | 仕様 |
|-----|------|
| **入力形式** | CSV（UTF-8, BOM無し） |
| **必須カラム** | `unique_id`, `ds`, `y` |
| **オプションカラム** | `futr_*`, `hist_*`, `stat_*` |
| **最大ファイルサイズ** | 1GB（それ以上はチャンク読み） |
| **エンコーディング** | UTF-8, Shift-JIS, EUC-JP自動検出 |

**APIエンドポイント**:

```python
class DataLoader:
    def load_csv(
        self,
        file_path: Path,
        *,
        encoding: Optional[str] = None,
        chunksize: Optional[int] = None,
        date_format: Optional[str] = None,
        parse_dates: bool = True,
        infer_datetime_format: bool = True,
    ) -> pd.DataFrame:
        """
        CSVファイルを読み込み、標準スキーマに変換
        
        Args:
            file_path: CSVファイルパス
            encoding: 文字エンコーディング（Noneで自動検出）
            chunksize: チャンク読み込みサイズ（行数）
            date_format: 日時フォーマット（例: '%Y-%m-%d'）
            parse_dates: 日時カラムを自動パース
            infer_datetime_format: 日時フォーマットを推定
            
        Returns:
            pd.DataFrame: 正規化されたDataFrame
            
        Raises:
            FileNotFoundError: ファイルが存在しない
            ValueError: スキーマ不正（必須カラム欠如）
            EncodingError: エンコーディング検出失敗
            
        Example:
            >>> loader = DataLoader()
            >>> df = loader.load_csv(Path("data.csv"))
            >>> df.columns
            Index(['unique_id', 'ds', 'y', 'futr_temp', 'hist_sales'])
        """
```

---

#### 5.1.2 データ検証 (FR-DATA-002)

**概要**: 読み込んだデータの品質を検証し、問題を検出

**優先度**: 高（必須）

**検証項目**:

| 検証項目 | 検証内容 | エラー/警告 | 対処 |
|---------|---------|-----------|------|
| **スキーマ検証** | 必須カラム存在確認 | エラー | 実行停止 |
| **型検証** | `unique_id:str`, `ds:datetime`, `y:float` | エラー | 型変換試行 |
| **欠損値検証** | NULL値の存在確認 | 警告 | レポート出力 |
| **重複検証** | `(unique_id, ds)`の重複 | 警告 | 最新行を保持 |
| **時系列順序検証** | `ds`が昇順か確認 | 警告 | 自動ソート |
| **外れ値検証** | IQR法で外れ値検出 | 警告 | レポート出力 |
| **時間間隔検証** | `ds`の間隔が一定か | 警告 | レポート出力 |

**APIエンドポイント**:

```python
class DataValidator:
    def validate_schema(
        self,
        df: pd.DataFrame,
        *,
        required_columns: List[str] = ["unique_id", "ds", "y"],
        allow_extra_columns: bool = True,
    ) -> ValidationResult:
        """
        データフレームのスキーマを検証
        
        Args:
            df: 検証対象DataFrame
            required_columns: 必須カラムリスト
            allow_extra_columns: 追加カラムを許可
            
        Returns:
            ValidationResult: 検証結果
                - is_valid: bool
                - errors: List[ValidationError]
                - warnings: List[ValidationWarning]
                
        Example:
            >>> validator = DataValidator()
            >>> result = validator.validate_schema(df)
            >>> if not result.is_valid:
            ...     raise ValueError(result.errors)
        """
    
    def detect_outliers(
        self,
        df: pd.DataFrame,
        *,
        column: str = "y",
        method: Literal["iqr", "zscore", "isolation_forest"] = "iqr",
        threshold: float = 1.5,
    ) -> pd.Series:
        """
        外れ値を検出
        
        Args:
            df: DataFrame
            column: 検証対象カラム
            method: 検出手法
                - "iqr": IQR法（デフォルト）
                - "zscore": Z-score法
                - "isolation_forest": Isolation Forest
            threshold: 閾値（IQR: 1.5, Z-score: 3.0推奨）
            
        Returns:
            pd.Series: 外れ値フラグ（True=外れ値）
            
        Example:
            >>> outliers = validator.detect_outliers(df, method="iqr")
            >>> df_clean = df[~outliers]
        """
```

---

#### 5.1.3 データバージョニング (FR-DATA-003)

**概要**: データセットに一意のバージョンIDを付与し、再現性を確保

**優先度**: 高（必須）

**バージョニング方式**:

```python
# データバージョンの計算
dataset_version = hashlib.sha256(
    sorted_rows_without_leaky_cols.to_csv(index=False).encode()
).hexdigest()[:16]
```

**除外カラム** (リーク防止):
- メタデータカラム（`created_at`, `updated_at`, `id`など）
- 予測結果カラム（`y_pred`, `residual`など）

**APIエンドポイント**:

```python
class DataVersionManager:
    def compute_version(
        self,
        df: pd.DataFrame,
        *,
        exclude_columns: Optional[List[str]] = None,
        sort_by: Optional[List[str]] = None,
    ) -> str:
        """
        データセットのバージョンハッシュを計算
        
        Args:
            df: DataFrame
            exclude_columns: 除外カラム（メタデータなど）
            sort_by: ソート基準カラム（デフォルト: unique_id, ds）
            
        Returns:
            str: 16桁のハッシュ値
            
        Example:
            >>> manager = DataVersionManager()
            >>> version = manager.compute_version(df)
            >>> version
            'a3f8c921d4e6b5f2'
        """
    
    def register_version(
        self,
        version: str,
        df: pd.DataFrame,
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        データバージョンをDBに登録
        
        Args:
            version: バージョンハッシュ
            df: DataFrame
            metadata: メタデータ（行数、カラム数、統計など）
            
        Raises:
            DuplicateVersionError: 同じバージョンが既に存在
            
        Example:
            >>> manager.register_version(
            ...     version="a3f8c921d4e6b5f2",
            ...     df=df,
            ...     metadata={"source": "scraping_2025-11-03.csv"}
            ... )
        """
```

**データベーススキーマ**:

```sql
CREATE TABLE datasets (
    id SERIAL PRIMARY KEY,
    dataset_version VARCHAR(16) UNIQUE NOT NULL,
    file_path TEXT NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    row_count INTEGER NOT NULL,
    column_count INTEGER NOT NULL,
    unique_id_count INTEGER NOT NULL,
    date_range_start TIMESTAMP,
    date_range_end TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_dataset_version (dataset_version)
);
```

---

#### 5.1.4 データ統計・プロファイリング (FR-DATA-004)

**概要**: データセットの統計情報を計算し、プロファイルレポートを生成

**優先度**: 中

**統計項目**:

| カテゴリ | 項目 | 計算方法 |
|---------|------|----------|
| **基本統計** | 行数、カラム数、unique_id数 | `len(df)`, `len(df.columns)`, `df['unique_id'].nunique()` |
| **欠損値** | カラムごとの欠損率 | `df.isnull().mean()` |
| **数値統計** | 平均、中央値、標準偏差、min, max | `df.describe()` |
| **時系列統計** | 最小日時、最大日時、期間 | `df['ds'].min()`, `df['ds'].max()` |
| **周期性** | 推定周期（日次、週次、月次など） | FFT, ACF |
| **トレンド** | トレンド有無、季節性有無 | STL分解 |

**APIエンドポイント**:

```python
class DataProfiler:
    def profile(
        self,
        df: pd.DataFrame,
        *,
        compute_correlations: bool = True,
        detect_seasonality: bool = True,
        n_samples: Optional[int] = None,
    ) -> DataProfile:
        """
        データプロファイルを生成
        
        Args:
            df: DataFrame
            compute_correlations: 相関行列を計算
            detect_seasonality: 季節性を検出
            n_samples: サンプル数（大規模データ用）
            
        Returns:
            DataProfile: プロファイル結果
                - basic_stats: Dict[str, Any]
                - missing_values: pd.Series
                - numeric_stats: pd.DataFrame
                - temporal_stats: Dict[str, Any]
                - correlations: Optional[pd.DataFrame]
                - seasonality: Optional[Dict[str, Any]]
                
        Example:
            >>> profiler = DataProfiler()
            >>> profile = profiler.profile(df)
            >>> print(f"行数: {profile.basic_stats['row_count']}")
            >>> print(f"欠損率: {profile.missing_values['y']:.2%}")
        """
```

---

### 5.2 特徴量生成・評価 (FR-FEATURE)

#### 5.2.1 特徴量生成 (FR-FEATURE-001)

**概要**: 時系列データから自動的に特徴量を生成

**優先度**: 高（必須）

**特徴量タイプ**:

| タイプ | 説明 | 生成例 | パラメータ |
|-------|------|--------|-----------|
| **Lag Features** | 過去N期のラグ特徴量 | `y_lag_1`, `y_lag_7` | `lags: List[int]` |
| **Rolling Statistics** | 移動統計量 | `y_rolling_mean_7`, `y_rolling_std_7` | `windows: List[int]`, `functions: List[str]` |
| **Seasonal Dummies** | 季節ダミー変数 | `month_1`, `weekday_0`, `hour_12` | `freq: str`, `drop_first: bool` |
| **Holiday Features** | 休日フラグ | `is_holiday`, `is_weekend` | `country: str`, `holidays: List[str]` |
| **Exogenous Features** | 外生変数 | `temperature`, `promotion_flag` | ユーザー指定 |
| **Fourier Features** | フーリエ変換特徴量 | `sin_annual_1`, `cos_annual_1` | `periods: List[float]`, `orders: List[int]` |

**APIエンドポイント**:

```python
class FeatureGenerator:
    def generate_lag_features(
        self,
        df: pd.DataFrame,
        *,
        target_col: str = "y",
        lags: List[int] = [1, 2, 3, 7, 14, 21],
        group_by: Optional[str] = "unique_id",
    ) -> pd.DataFrame:
        """
        ラグ特徴量を生成
        
        Args:
            df: DataFrame
            target_col: 対象カラム
            lags: ラグ期間リスト
            group_by: グルーピングカラム
            
        Returns:
            pd.DataFrame: ラグ特徴量が追加されたDataFrame
            
        Example:
            >>> generator = FeatureGenerator()
            >>> df_with_lags = generator.generate_lag_features(
            ...     df, lags=[1, 7, 14]
            ... )
            >>> df_with_lags.columns
            Index(['unique_id', 'ds', 'y', 'y_lag_1', 'y_lag_7', 'y_lag_14'])
        """
    
    def generate_rolling_features(
        self,
        df: pd.DataFrame,
        *,
        target_col: str = "y",
        windows: List[int] = [7, 14, 30],
        functions: List[str] = ["mean", "std", "min", "max"],
        group_by: Optional[str] = "unique_id",
        min_periods: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        移動統計量を生成
        
        Args:
            df: DataFrame
            target_col: 対象カラム
            windows: ウィンドウサイズリスト
            functions: 統計関数リスト
                - "mean": 平均
                - "std": 標準偏差
                - "min": 最小値
                - "max": 最大値
                - "median": 中央値
                - "sum": 合計
            group_by: グルーピングカラム
            min_periods: 最小期間数
            
        Returns:
            pd.DataFrame: 移動統計量が追加されたDataFrame
            
        Example:
            >>> df_with_rolling = generator.generate_rolling_features(
            ...     df, windows=[7, 30], functions=["mean", "std"]
            ... )
        """
    
    def generate_seasonal_features(
        self,
        df: pd.DataFrame,
        *,
        date_col: str = "ds",
        features: List[str] = ["month", "weekday", "day", "week"],
        cyclical_encoding: bool = True,
        drop_first: bool = False,
    ) -> pd.DataFrame:
        """
        季節性特徴量を生成
        
        Args:
            df: DataFrame
            date_col: 日時カラム
            features: 生成する特徴量リスト
                - "month": 月（1-12）
                - "weekday": 曜日（0-6）
                - "day": 日（1-31）
                - "week": 週番号（1-52）
                - "quarter": 四半期（1-4）
                - "hour": 時（0-23）
                - "minute": 分（0-59）
            cyclical_encoding: 循環エンコーディング（sin/cos）
            drop_first: ダミー変数の最初を削除
            
        Returns:
            pd.DataFrame: 季節性特徴量が追加されたDataFrame
            
        Example:
            >>> df_with_seasonal = generator.generate_seasonal_features(
            ...     df, features=["month", "weekday"], cyclical_encoding=True
            ... )
            >>> df_with_seasonal.columns
            Index([..., 'month_sin', 'month_cos', 'weekday_sin', 'weekday_cos'])
        """
```

---

#### 5.2.2 特徴量重要度評価 (FR-FEATURE-002)

**概要**: 生成した特徴量の寄与度を評価

**優先度**: 高（必須）

**評価手法**:

| 手法 | 説明 | 適用場面 | 計算コスト |
|-----|------|---------|-----------|
| **Permutation Importance** | 特徴量をシャッフルして精度低下を測定 | すべてのモデル | 高 |
| **Feature Correlation** | 目的変数との相関係数 | 線形関係の把握 | 低 |
| **Mutual Information** | 相互情報量 | 非線形関係の把握 | 中 |
| **SHAP Values** | モデル非依存の寄与度 | 解釈性重視 | 非常に高 |

**APIエンドポイント**:

```python
class FeatureEvaluator:
    def compute_permutation_importance(
        self,
        model: Any,
        X: pd.DataFrame,
        y: pd.Series,
        *,
        n_repeats: int = 10,
        random_state: int = 42,
        scoring: str = "neg_mean_squared_error",
        n_jobs: int = -1,
    ) -> pd.DataFrame:
        """
        Permutation Importanceを計算
        
        Args:
            model: 学習済みモデル
            X: 特徴量DataFrame
            y: 目的変数Series
            n_repeats: シャッフル回数
            random_state: 乱数シード
            scoring: スコアリング関数
            n_jobs: 並列数
            
        Returns:
            pd.DataFrame: 重要度結果
                - feature: 特徴量名
                - importance_mean: 平均重要度
                - importance_std: 標準偏差
                
        Example:
            >>> evaluator = FeatureEvaluator()
            >>> importance = evaluator.compute_permutation_importance(
            ...     model=fitted_model,
            ...     X=X_test,
            ...     y=y_test,
            ...     n_repeats=10
            ... )
            >>> importance.sort_values('importance_mean', ascending=False)
        """
    
    def compute_correlation(
        self,
        df: pd.DataFrame,
        *,
        target_col: str = "y",
        method: Literal["pearson", "spearman", "kendall"] = "spearman",
        min_periods: int = 30,
    ) -> pd.Series:
        """
        特徴量と目的変数の相関係数を計算
        
        Args:
            df: DataFrame
            target_col: 目的変数カラム
            method: 相関係数手法
                - "pearson": ピアソン（線形）
                - "spearman": スピアマン（順位）
                - "kendall": ケンドール（順位）
            min_periods: 最小期間数
            
        Returns:
            pd.Series: 相関係数（特徴量名をインデックスとする）
            
        Example:
            >>> correlation = evaluator.compute_correlation(
            ...     df, method="spearman"
            ... )
            >>> correlation.abs().sort_values(ascending=False)
        """
```

---

#### 5.2.3 特徴量選択 (FR-FEATURE-003)

**概要**: 重要度に基づいて特徴量を自動選択

**優先度**: 中

**選択基準**:

| 基準 | 説明 | パラメータ |
|-----|------|-----------|
| **重要度閾値** | 重要度が閾値以上の特徴量を選択 | `threshold: float` |
| **Top-K** | 上位K個の特徴量を選択 | `k: int` |
| **累積寄与率** | 累積寄与率がN%になるまで選択 | `cumulative_ratio: float` |
| **相関除去** | 高相関特徴量を除去 | `correlation_threshold: float` |

**APIエンドポイント**:

```python
class FeatureSelector:
    def select_by_importance(
        self,
        importance: pd.DataFrame,
        *,
        method: Literal["threshold", "top_k", "cumulative"] = "threshold",
        threshold: Optional[float] = 0.01,
        k: Optional[int] = None,
        cumulative_ratio: Optional[float] = None,
    ) -> List[str]:
        """
        重要度に基づいて特徴量を選択
        
        Args:
            importance: 重要度DataFrame
            method: 選択手法
                - "threshold": 閾値以上
                - "top_k": 上位K個
                - "cumulative": 累積寄与率
            threshold: 重要度閾値（method="threshold"時）
            k: 選択数（method="top_k"時）
            cumulative_ratio: 累積寄与率（method="cumulative"時、0.95推奨）
            
        Returns:
            List[str]: 選択された特徴量名リスト
            
        Example:
            >>> selector = FeatureSelector()
            >>> selected = selector.select_by_importance(
            ...     importance, method="top_k", k=10
            ... )
            >>> X_selected = X[selected]
        """
    
    def remove_correlated_features(
        self,
        df: pd.DataFrame,
        *,
        correlation_threshold: float = 0.95,
        method: Literal["pearson", "spearman"] = "spearman",
        keep: Literal["first", "last", "highest_importance"] = "first",
    ) -> List[str]:
        """
        高相関特徴量を除去
        
        Args:
            df: DataFrame
            correlation_threshold: 相関閾値（これ以上で除去）
            method: 相関計算手法
            keep: 保持基準
                - "first": 最初の特徴量を保持
                - "last": 最後の特徴量を保持
                - "highest_importance": 重要度が高い方を保持
                
        Returns:
            List[str]: 除去する特徴量名リスト
            
        Example:
            >>> to_drop = selector.remove_correlated_features(
            ...     df, correlation_threshold=0.95
            ... )
            >>> df_reduced = df.drop(columns=to_drop)
        ```

---

### 5.3 実験管理・再現性 (FR-EXPERIMENT)

#### 5.3.1 実験構造 (FR-EXPERIMENT-001)

**概要**: Experiment（実験）とRun（実行）の2層構造で管理

**優先度**: 高（必須）

**構造定義**:

```
Experiment (実験)
├── メタデータ
│   ├── experiment_id: UUID
│   ├── name: str
│   ├── objective: str
│   ├── created_at: datetime
│   └── tags: Dict[str, str]
└── Runs (実行) []
    ├── Run 1
    │   ├── run_id: UUID
    │   ├── run_fingerprint: str (16桁)
    │   ├── status: Enum
    │   ├── parameters: Dict
    │   ├── metrics: Dict
    │   ├── artifacts: List[Path]
    │   └── metadata: Dict
    ├── Run 2
    └── ...
```

**APIエンドポイント**:

```python
class ExperimentManager:
    def create_experiment(
        self,
        name: str,
        *,
        objective: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Experiment:
        """
        新しい実験を作成
        
        Args:
            name: 実験名
            objective: 実験目的
            description: 詳細説明
            tags: タグ辞書（例: {"dataset": "v1", "model_type": "lstm"}）
            
        Returns:
            Experiment: 実験オブジェクト
            
        Raises:
            DuplicateExperimentError: 同名の実験が既に存在
            
        Example:
            >>> manager = ExperimentManager()
            >>> exp = manager.create_experiment(
            ...     name="baseline_comparison_2025-11",
            ...     objective="Compare AutoNHITS vs AutoLSTM",
            ...     tags={"dataset": "sales_v2", "phase": "baseline"}
            ... )
            >>> exp.experiment_id
            UUID('f47ac10b-58cc-4372-a567-0e02b2c3d479')
        """
    
    def get_experiment(
        self,
        experiment_id: Optional[UUID] = None,
        *,
        name: Optional[str] = None,
    ) -> Experiment:
        """
        実験を取得
        
        Args:
            experiment_id: 実験ID（優先）
            name: 実験名（experiment_idが無い場合）
            
        Returns:
            Experiment: 実験オブジェクト
            
        Raises:
            ExperimentNotFoundError: 実験が存在しない
            
        Example:
            >>> exp = manager.get_experiment(name="baseline_comparison_2025-11")
        """
```

---

#### 5.3.2 Run Fingerprint (FR-EXPERIMENT-002)

**概要**: 実行条件の一意識別子を生成し、重複実行を検出

**優先度**: 高（必須）

**Fingerprint計算式**:

```python
run_fingerprint = hashlib.sha256(
    json.dumps({
        "model_adapter_name": "AutoNHITS",
        "model_version_tag": "neuralforecast==1.6.0",
        "hyperparameters": {
            "input_size": 14,
            "h": 7,
            "loss": "MAE",
            "scaler": "standard",
            # ... その他すべてのハイパーパラメータ
        },
        "dataset_version": "a3f8c921d4e6b5f2",
        "feature_set_id": "lag_7_14_rolling_mean",
        "training_window_spec": {
            "start_date": "2023-01-01",
            "end_date": "2024-12-31",
            "split_method": "rolling_origin",
            "n_splits": 5,
        },
        "code_revision": "abc123def",
        "random_seed": 42,
        "objective_config": {
            "metric": "sMAPE",
            "weight": 1.0,
        }
    }, sort_keys=True).encode()
).hexdigest()[:16]
```

**重複判定ロジック**:

```python
if fingerprint_exists_in_db(run_fingerprint):
    logger.info(f"Skip: Run with fingerprint {run_fingerprint} already exists")
    return existing_run
else:
    execute_new_run()
```

**APIエンドポイント**:

```python
class FingerprintManager:
    def compute_fingerprint(
        self,
        *,
        model_name: str,
        model_version: str,
        hyperparameters: Dict[str, Any],
        dataset_version: str,
        feature_set_id: str,
        training_window: Dict[str, Any],
        code_revision: str,
        random_seed: int,
        objective_config: Dict[str, Any],
    ) -> str:
        """
        Run Fingerprintを計算
        
        Args:
            model_name: モデル名（例: "AutoNHITS"）
            model_version: モデルバージョン（例: "neuralforecast==1.6.0"）
            hyperparameters: ハイパーパラメータ辞書
            dataset_version: データセットバージョン
            feature_set_id: 特徴量セットID
            training_window: 学習ウィンドウ設定
            code_revision: Gitコミットハッシュ
            random_seed: 乱数シード
            objective_config: 目的関数設定
            
        Returns:
            str: 16桁のFingerprint
            
        Example:
            >>> manager = FingerprintManager()
            >>> fp = manager.compute_fingerprint(
            ...     model_name="AutoNHITS",
            ...     model_version="neuralforecast==1.6.0",
            ...     hyperparameters={"input_size": 14, "h": 7},
            ...     dataset_version="a3f8c921",
            ...     feature_set_id="lag_7_14",
            ...     training_window={"start": "2023-01-01", "end": "2024-12-31"},
            ...     code_revision="abc123",
            ...     random_seed=42,
            ...     objective_config={"metric": "sMAPE"}
            ... )
            >>> fp
            '7d8e3f1a2b9c4e5f'
        """
    
    def check_duplicate(
        self,
        fingerprint: str,
        *,
        experiment_id: Optional[UUID] = None,
    ) -> Optional[Run]:
        """
        重複Runをチェック
        
        Args:
            fingerprint: Run Fingerprint
            experiment_id: 実験ID（指定した場合、同一実験内のみチェック）
            
        Returns:
            Optional[Run]: 既存のRun（存在する場合）、なければNone
            
        Example:
            >>> existing = manager.check_duplicate("7d8e3f1a2b9c4e5f")
            >>> if existing:
            ...     print(f"Skip: Run {existing.run_id} already exists")
            ... else:
            ...     execute_new_run()
        """
```

---

### 5.4 学習・探索・評価 (FR-TRAINING)

#### 5.4.1 モデル学習 (FR-TRAINING-001)

**概要**: Adapter経由でモデルを学習

**優先度**: 高（必須）

**学習フロー**:

```
1. データ準備
   ↓
2. 特徴量エンジニアリング
   ↓
3. 学習/検証分割
   ↓
4. モデル初期化
   ↓
5. ハイパーパラメータ設定
   ↓
6. 学習実行
   ↓
7. メトリクス記録
   ↓
8. モデル保存
```

**APIエンドポイント**:

```python
class ModelTrainer:
    def train(
        self,
        model: BaseModel,
        train_df: pd.DataFrame,
        *,
        val_df: Optional[pd.DataFrame] = None,
        hyperparameters: Optional[Dict[str, Any]] = None,
        callbacks: Optional[List[Callback]] = None,
        early_stopping: bool = True,
        early_stopping_patience: int = 10,
        checkpoint_dir: Optional[Path] = None,
    ) -> TrainingResult:
        """
        モデルを学習
        
        Args:
            model: 学習対象モデル
            train_df: 学習データ
            val_df: 検証データ（Noneの場合、train_dfから自動分割）
            hyperparameters: ハイパーパラメータ辞書
            callbacks: コールバックリスト
            early_stopping: Early Stopping有効化
            early_stopping_patience: Early Stopping patience
            checkpoint_dir: チェックポイント保存先
            
        Returns:
            TrainingResult: 学習結果
                - model: 学習済みモデル
                - history: 学習履歴（loss, metrics）
                - best_epoch: 最良エポック
                - training_time: 学習時間（秒）
                - metadata: その他メタデータ
                
        Raises:
            TrainingError: 学習失敗
            ResourceExhaustedError: リソース不足（OOM、CUDA OOM）
            
        Example:
            >>> trainer = ModelTrainer()
            >>> result = trainer.train(
            ...     model=AutoNHITS(),
            ...     train_df=train,
            ...     val_df=val,
            ...     hyperparameters={"max_steps": 1000, "lr": 0.001}
            ... )
            >>> print(f"Training time: {result.training_time:.2f}s")
            >>> print(f"Best epoch: {result.best_epoch}")
        """
```

---

#### 5.4.2 ハイパーパラメータ探索 (FR-TRAINING-002)

**概要**: Optuna/Ray Tuneによる自動探索

**優先度**: 高（必須）

**探索アルゴリズム**:

| アルゴリズム | 説明 | 適用場面 | パラメータ |
|------------|------|---------|-----------|
| **TPE (Tree-structured Parzen Estimator)** | ベイズ最適化の一種 | 中小規模探索 | `n_trials`, `n_startup_trials` |
| **CMA-ES** | 進化戦略 | 連続値パラメータ | `sigma0`, `n_trials` |
| **Random Search** | ランダムサンプリング | ベースライン | `n_trials` |
| **Grid Search** | 全探索 | 小規模探索 | `param_grid` |
| **ASHA** | 非同期ハルビング | 大規模並列探索 | `max_t`, `grace_period` |

**APIエンドポイント**:

```python
class HyperparameterTuner:
    def tune(
        self,
        model_class: Type[BaseModel],
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        *,
        param_space: Dict[str, Any],
        n_trials: int = 100,
        timeout: Optional[float] = None,
        algorithm: Literal["tpe", "cmaes", "random", "grid", "asha"] = "tpe",
        metric: str = "val_loss",
        direction: Literal["minimize", "maximize"] = "minimize",
        n_jobs: int = 1,
        pruning: bool = True,
        seed: int = 42,
    ) -> TuningResult:
        """
        ハイパーパラメータを探索
        
        Args:
            model_class: モデルクラス
            train_df: 学習データ
            val_df: 検証データ
            param_space: パラメータ空間
                例: {
                    "input_size": ("int", 7, 30),
                    "hidden_size": ("categorical", [64, 128, 256]),
                    "lr": ("loguniform", 1e-5, 1e-2)
                }
            n_trials: 試行回数
            timeout: タイムアウト（秒）
            algorithm: 探索アルゴリズム
            metric: 最適化対象メトリクス
            direction: 最適化方向
            n_jobs: 並列数
            pruning: Pruning有効化
            seed: 乱数シード
            
        Returns:
            TuningResult: 探索結果
                - best_params: 最良パラメータ
                - best_value: 最良値
                - best_trial: 最良Trial
                - study: Optunaスタディオブジェクト
                - trials_df: 全Trial結果DataFrame
                
        Example:
            >>> tuner = HyperparameterTuner()
            >>> result = tuner.tune(
            ...     model_class=AutoNHITS,
            ...     train_df=train,
            ...     val_df=val,
            ...     param_space={
            ...         "input_size": ("int", 7, 30),
            ...         "hidden_size": ("categorical", [64, 128, 256]),
            ...         "lr": ("loguniform", 1e-5, 1e-2)
            ...     },
            ...     n_trials=50,
            ...     algorithm="tpe"
            ... )
            >>> print(f"Best params: {result.best_params}")
            >>> print(f"Best {metric}: {result.best_value}")
        """
```

---

#### 5.4.3 評価 (FR-TRAINING-003)

**概要**: Rolling-origin backtest による時系列交差検証

**優先度**: 高（必須）

**Backtest設計**:

```
データ: 2023-01-01 ~ 2024-12-31 (730日)

Rolling-Origin Backtest (5 splits, h=7):

Split 1:
  Train: 2023-01-01 ~ 2024-06-30 (547日)
  Test:  2024-07-01 ~ 2024-07-07 (7日)

Split 2:
  Train: 2023-01-01 ~ 2024-07-31 (577日)
  Test:  2024-08-01 ~ 2024-08-07 (7日)

Split 3:
  Train: 2023-01-01 ~ 2024-08-31 (608日)
  Test:  2024-09-01 ~ 2024-09-07 (7日)

Split 4:
  Train: 2023-01-01 ~ 2024-09-30 (638日)
  Test:  2024-10-01 ~ 2024-10-07 (7日)

Split 5:
  Train: 2023-01-01 ~ 2024-10-31 (669日)
  Test:  2024-11-01 ~ 2024-11-07 (7日)
```

**評価メトリクス**:

| メトリクス | 数式 | 範囲 | 解釈 |
|----------|------|------|------|
| **MAE** | `mean(abs(y_true - y_pred))` | [0, ∞) | 低いほど良い、単位はyと同じ |
| **RMSE** | `sqrt(mean((y_true - y_pred)^2))` | [0, ∞) | 低いほど良い、外れ値に敏感 |
| **sMAPE** | `mean(2 * abs(y_true - y_pred) / (abs(y_true) + abs(y_pred)))` | [0, 2] | 低いほど良い、対称的 |
| **MASE** | `MAE / naive_MAE` | [0, ∞) | <1で良好、ナイーブ予測より良い |
| **MAPE** | `mean(abs((y_true - y_pred) / y_true))` | [0, ∞) | 低いほど良い、y_true=0でエラー |

**APIエンドポイント**:

```python
class ModelEvaluator:
    def backtest(
        self,
        model: BaseModel,
        df: pd.DataFrame,
        *,
        n_splits: int = 5,
        h: int = 7,
        gap: int = 0,
        expanding_window: bool = True,
        metrics: List[str] = ["mae", "rmse", "smape", "mase"],
        return_predictions: bool = True,
    ) -> BacktestResult:
        """
        Rolling-origin backtestを実行
        
        Args:
            model: 評価対象モデル
            df: データフレーム
            n_splits: 分割数
            h: Horizon（予測期間）
            gap: 学習データと予測データの間隔
            expanding_window: True=Expanding, False=Sliding
            metrics: 計算するメトリクスリスト
            return_predictions: 予測結果を返すか
            
        Returns:
            BacktestResult: Backtest結果
                - fold_results: List[FoldResult]
                    - fold_id: int
                    - train_period: (start, end)
                    - test_period: (start, end)
                    - metrics: Dict[str, float]
                    - predictions: Optional[pd.DataFrame]
                - aggregated_metrics: Dict[str, float]
                    - {metric}_mean
                    - {metric}_std
                    - {metric}_min
                    - {metric}_max
                - metadata: Dict[str, Any]
                
        Example:
            >>> evaluator = ModelEvaluator()
            >>> result = evaluator.backtest(
            ...     model=fitted_model,
            ...     df=df,
            ...     n_splits=5,
            ...     h=7,
            ...     metrics=["mae", "rmse", "smape"]
            ... )
            >>> print(f"Mean MAE: {result.aggregated_metrics['mae_mean']:.2f}")
            >>> print(f"Std MAE: {result.aggregated_metrics['mae_std']:.2f}")
        """
    
    def compute_metrics(
        self,
        y_true: pd.Series,
        y_pred: pd.Series,
        *,
        metrics: List[str] = ["mae", "rmse", "smape", "mase", "mape"],
    ) -> Dict[str, float]:
        """
        予測精度メトリクスを計算
        
        Args:
            y_true: 真値
            y_pred: 予測値
            metrics: 計算するメトリクスリスト
            
        Returns:
            Dict[str, float]: メトリクス辞書
            
        Example:
            >>> metrics = evaluator.compute_metrics(
            ...     y_true=y_test,
            ...     y_pred=predictions
            ... )
            >>> print(f"MAE: {metrics['mae']:.2f}")
            >>> print(f"sMAPE: {metrics['smape']:.2%}")
        """
```

---

### 5.5 因果・相関・寄与度分析 (FR-ANALYSIS)

#### 5.5.1 相関分析 (FR-ANALYSIS-001)

**概要**: 特徴量間およびラグ相関を分析

**優先度**: 中

**分析手法**:

| 手法 | 説明 | 適用場面 |
|-----|------|---------|
| **Pearson相関** | 線形相関 | 正規分布データ |
| **Spearman相関** | 順位相関 | 非線形・外れ値に頑健 |
| **Kendall相関** | 順位相関（より頑健） | 小サンプル |
| **Lag相関 (ACF)** | 自己相関関数 | 時系列の周期性検出 |
| **Partial相関 (PACF)** | 偏自己相関関数 | ARモデル次数決定 |

**APIエンドポイント**:

```python
class CorrelationAnalyzer:
    def compute_correlation_matrix(
        self,
        df: pd.DataFrame,
        *,
        method: Literal["pearson", "spearman", "kendall"] = "spearman",
        min_periods: int = 30,
    ) -> pd.DataFrame:
        """
        相関行列を計算
        
        Args:
            df: DataFrame
            method: 相関手法
            min_periods: 最小期間数
            
        Returns:
            pd.DataFrame: 相関行列
            
        Example:
            >>> analyzer = CorrelationAnalyzer()
            >>> corr_matrix = analyzer.compute_correlation_matrix(df)
            >>> import seaborn as sns
            >>> sns.heatmap(corr_matrix, annot=True, cmap="coolwarm")
        """
    
    def compute_lag_correlation(
        self,
        series: pd.Series,
        *,
        lags: int = 40,
        alpha: float = 0.05,
    ) -> LagCorrelationResult:
        """
        ラグ相関（ACF/PACF）を計算
        
        Args:
            series: 時系列データ
            lags: 最大ラグ数
            alpha: 有意水準
            
        Returns:
            LagCorrelationResult:
                - acf: np.ndarray (自己相関)
                - pacf: np.ndarray (偏自己相関)
                - acf_confint: np.ndarray (信頼区間)
                - pacf_confint: np.ndarray (信頼区間)
                
        Example:
            >>> result = analyzer.compute_lag_correlation(df['y'], lags=40)
            >>> plt.stem(result.acf)
            >>> plt.fill_between(
            ...     range(len(result.acf)),
            ...     result.acf_confint[:, 0],
            ...     result.acf_confint[:, 1],
            ...     alpha=0.2
            ... )
        """
```

---

#### 5.5.2 因果分析 (FR-ANALYSIS-002)

**概要**: Granger因果性テストおよび介入分析

**優先度**: 中（注意事項あり）

**警告**:
- Granger因果性は「統計的因果」であり、真の因果関係を保証しない
- 介入データがある場合のみDiD/Synthetic Controlを適用可能
- 結果は「参考値」として扱い、解釈には注意が必要

**分析手法**:

| 手法 | 説明 | データ要件 | 適用場面 |
|-----|------|-----------|---------|
| **Granger因果性テスト** | X→Yの予測改善を検定 | 時系列データ | 先行関係の検証 |
| **DiD (Difference-in-Differences)** | 介入効果の推定 | 介入群/対照群、介入前後 | 政策効果検証 |
| **Synthetic Control** | 合成対照群の構築 | 介入前データ、複数対照群 | 単一介入の効果推定 |

**APIエンドポイント**:

```python
class CausalAnalyzer:
    def granger_causality_test(
        self,
        df: pd.DataFrame,
        *,
        target_col: str,
        predictor_cols: List[str],
        max_lag: int = 10,
        test: Literal["ssr_ftest", "ssr_chi2test", "lrtest", "params_ftest"] = "ssr_ftest",
        alpha: float = 0.05,
    ) -> GrangerTestResult:
        """
        Granger因果性テストを実行
        
        Args:
            df: DataFrame
            target_col: 目的変数カラム
            predictor_cols: 説明変数カラムリスト
            max_lag: 最大ラグ数
            test: テスト手法
            alpha: 有意水準
            
        Returns:
            GrangerTestResult:
                - results: Dict[str, Dict[int, GrangerResult]]
                    - predictor_col:
                        - lag: GrangerResult
                            - f_statistic: float
                            - p_value: float
                            - is_significant: bool
                - summary_df: pd.DataFrame（要約）
                
        Raises:
            ValueError: データ不足、ラグ数不正
            
        Example:
            >>> causal = CausalAnalyzer()
            >>> result = causal.granger_causality_test(
            ...     df,
            ...     target_col="y",
            ...     predictor_cols=["temperature", "promotion"],
            ...     max_lag=7
            ... )
            >>> for predictor, lag_results in result.results.items():
            ...     for lag, gr in lag_results.items():
            ...         if gr.is_significant:
            ...             print(f"{predictor} (lag={lag}): p={gr.p_value:.4f}")
        """
    
    def difference_in_differences(
        self,
        df: pd.DataFrame,
        *,
        outcome_col: str,
        treatment_col: str,
        time_col: str,
        intervention_time: Any,
        control_variables: Optional[List[str]] = None,
    ) -> DIDResult:
        """
        Difference-in-Differences分析を実行
        
        Args:
            df: DataFrame
            outcome_col: アウトカム変数
            treatment_col: 処置群フラグ（0/1）
            time_col: 時間変数
            intervention_time: 介入時点
            control_variables: 共変量リスト
            
        Returns:
            DIDResult:
                - treatment_effect: float (処置効果推定値)
                - std_error: float
                - t_statistic: float
                - p_value: float
                - conf_interval: Tuple[float, float]
                - regression_summary: str
                
        Example:
            >>> result = causal.difference_in_differences(
            ...     df,
            ...     outcome_col="sales",
            ...     treatment_col="is_store_group_A",
            ...     time_col="ds",
            ...     intervention_time="2024-06-01"
            ... )
            >>> print(f"Treatment Effect: {result.treatment_effect:.2f}")
            >>> print(f"P-value: {result.p_value:.4f}")
        """
```

---

#### 5.5.3 寄与度分析 (FR-ANALYSIS-003)

**概要**: 特徴量の予測への寄与度を定量化

**優先度**: 中

**分析手法**:

| 手法 | 説明 | 適用モデル | 計算コスト |
|-----|------|-----------|-----------|
| **Permutation Importance** | シャッフルによる精度低下 | 全モデル | 中 |
| **SHAP (SHapley Additive exPlanations)** | Shapley値による寄与度 | Tree系、NN系 | 高 |
| **LIME (Local Interpretable Model-agnostic Explanations)** | 局所線形近似 | 全モデル | 中 |
| **Feature Ablation** | 特徴量除去による精度変化 | 全モデル | 高 |

**APIエンドポイント**:

```python
class ContributionAnalyzer:
    def compute_shap_values(
        self,
        model: BaseModel,
        X: pd.DataFrame,
        *,
        background_samples: int = 100,
        max_evals: int = 1000,
        check_additivity: bool = False,
    ) -> SHAPResult:
        """
        SHAP値を計算
        
        Args:
            model: 学習済みモデル
            X: 説明するデータ
            background_samples: 背景データサンプル数
            max_evals: 最大評価回数
            check_additivity: 加法性チェック
            
        Returns:
            SHAPResult:
                - shap_values: np.ndarray (N x D)
                - expected_value: float
                - feature_importance: pd.Series
                - summary_plot_data: Dict
                
        Example:
            >>> contrib = ContributionAnalyzer()
            >>> shap_result = contrib.compute_shap_values(
            ...     model=fitted_model,
            ...     X=X_test.sample(100),
            ...     background_samples=50
            ... )
            >>> import shap
            >>> shap.summary_plot(
            ...     shap_result.shap_values,
            ...     X_test.sample(100)
            ... )
        """
    
    def compute_feature_contribution_over_time(
        self,
        model: BaseModel,
        df: pd.DataFrame,
        *,
        window_size: int = 30,
        step: int = 7,
        method: Literal["permutation", "shap"] = "permutation",
    ) -> pd.DataFrame:
        """
        時間経過に伴う特徴量寄与度の変化を計算
        
        Args:
            model: 学習済みモデル
            df: DataFrame
            window_size: ウィンドウサイズ（日数）
            step: ステップサイズ（日数）
            method: 寄与度計算手法
            
        Returns:
            pd.DataFrame: 時系列の寄与度
                - columns: 特徴量名
                - index: 時刻
                - values: 寄与度
                
        Example:
            >>> contrib_time = contrib.compute_feature_contribution_over_time(
            ...     model=fitted_model,
            ...     df=df,
            ...     window_size=30,
            ...     step=7,
            ...     method="permutation"
            ... )
            >>> contrib_time.plot(figsize=(12, 6))
        ```

---

### 5.6 ロギング・トラッキング (FR-LOGGING)

#### 5.6.1 構造化ログ (FR-LOGGING-001)

**概要**: JSON形式の構造化ログを出力

**優先度**: 高（必須）

**ログレベル**:

| レベル | 用途 | 例 |
|-------|------|---|
| **DEBUG** | 開発時の詳細情報 | パラメータ値、中間計算結果 |
| **INFO** | 通常の動作情報 | 実行開始/終了、進捗 |
| **WARNING** | 警告（処理は継続） | 欠損値検出、収束しない |
| **ERROR** | エラー（処理失敗） | ファイル読み込み失敗、OOM |
| **CRITICAL** | クリティカルエラー | システム停止 |

**ログフォーマット**:

```json
{
  "timestamp": "2025-11-03T12:34:56.789Z",
  "level": "INFO",
  "logger": "nf_auto_runner.training",
  "message": "Training completed",
  "run_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "experiment_id": "a1b2c3d4-e5f6-4789-90ab-cdef12345678",
  "model_name": "AutoNHITS",
  "duration_seconds": 123.45,
  "metrics": {
    "train_loss": 0.123,
    "val_loss": 0.145,
    "mae": 1.23,
    "rmse": 1.56
  },
  "context": {
    "hostname": "ml-server-01",
    "pid": 12345,
    "thread_id": 67890,
    "gpu_id": 0
  }
}
```

**APIエンドポイント**:

```python
class StructuredLogger:
    def __init__(
        self,
        name: str,
        *,
        level: str = "INFO",
        log_file: Optional[Path] = None,
        log_to_console: bool = True,
        log_to_file: bool = True,
        add_context: bool = True,
    ):
        """
        構造化ロガーを初期化
        
        Args:
            name: ロガー名
            level: ログレベル
            log_file: ログファイルパス
            log_to_console: コンソール出力
            log_to_file: ファイル出力
            add_context: コンテキスト情報を自動追加
            
        Example:
            >>> logger = StructuredLogger(
            ...     "nf_auto_runner.training",
            ...     level="INFO",
            ...     log_file=Path("logs/training.jsonl")
            ... )
        """
    
    def log(
        self,
        level: str,
        message: str,
        *,
        run_id: Optional[UUID] = None,
        experiment_id: Optional[UUID] = None,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        """
        ログを記録
        
        Args:
            level: ログレベル
            message: メッセージ
            run_id: Run ID
            experiment_id: Experiment ID
            extra: 追加情報辞書
            **kwargs: その他の Key-Value
            
        Example:
            >>> logger.log(
            ...     "INFO",
            ...     "Training started",
            ...     run_id=run.run_id,
            ...     model_name="AutoNHITS",
            ...     hyperparameters={"input_size": 14, "h": 7}
            ... )
        """
    
    def info(self, message: str, **kwargs) -> None:
        """INFOレベルログ"""
    
    def warning(self, message: str, **kwargs) -> None:
        """WARNINGレベルログ"""
    
    def error(self, message: str, **kwargs) -> None:
        """ERRORレベルログ"""
```

---

#### 5.6.2 MLflowトラッキング (FR-LOGGING-002)

**概要**: MLflowへの実験記録（オプション）

**優先度**: 中（オプション）

**記録項目**:

| カテゴリ | 項目 | 例 |
|---------|------|---|
| **Parameters** | ハイパーパラメータ | `input_size=14`, `h=7`, `lr=0.001` |
| **Metrics** | 評価メトリクス | `train_loss`, `val_loss`, `mae`, `rmse` |
| **Artifacts** | ファイル成果物 | モデルファイル、予測結果CSV、グラフPNG |
| **Tags** | タグ | `model_type=AutoNHITS`, `dataset=sales_v2` |
| **Models** | モデル登録 | `models:/AutoNHITS/production` |

**APIエンドポイント**:

```python
class MLflowBridge:
    def __init__(
        self,
        tracking_uri: Optional[str] = None,
        *,
        experiment_name: str = "default",
        artifact_location: Optional[str] = None,
    ):
        """
        MLflow Bridgeを初期化
        
        Args:
            tracking_uri: MLflow Tracking URI
            experiment_name: 実験名
            artifact_location: アーティファクト保存先
            
        Example:
            >>> bridge = MLflowBridge(
            ...     tracking_uri="http://localhost:5000",
            ...     experiment_name="neuralforecast_experiments"
            ... )
        """
    
    def start_run(
        self,
        run_id: UUID,
        *,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> mlflow.ActiveRun:
        """
        MLflow Runを開始
        
        Args:
            run_id: システムのRun ID
            run_name: MLflow Run名
            tags: タグ辞書
            
        Returns:
            mlflow.ActiveRun: アクティブなRun
            
        Example:
            >>> with bridge.start_run(run.run_id, tags={"model": "AutoNHITS"}):
            ...     bridge.log_params({"input_size": 14, "h": 7})
            ...     bridge.log_metrics({"mae": 1.23, "rmse": 1.56})
        """
    
    def log_params(self, params: Dict[str, Any]) -> None:
        """パラメータを記録"""
    
    def log_metrics(
        self,
        metrics: Dict[str, float],
        *,
        step: Optional[int] = None,
    ) -> None:
        """メトリクスを記録"""
    
    def log_artifact(
        self,
        local_path: Path,
        *,
        artifact_path: Optional[str] = None,
    ) -> None:
        """アーティファクトを記録"""
    
    def log_model(
        self,
        model: BaseModel,
        artifact_path: str,
        *,
        registered_model_name: Optional[str] = None,
    ) -> None:
        """モデルを記録・登録"""
```

---

### 5.7 予測運用・再学習 (FR-FORECAST)

#### 5.7.1 1ステップ先予測 (FR-FORECAST-001)

**概要**: 学習済みモデルで1ステップ先予測を実行

**優先度**: 高（必須）

**予測フロー**:

```
1. 最新データ取得
   ↓
2. 特徴量生成
   ↓
3. モデル読み込み
   ↓
4. 予測実行
   ↓
5. 結果保存
   ↓
6. 配信（API/ファイル/DB）
```

**APIエンドポイント**:

```python
class Forecaster:
    def predict_one_step(
        self,
        model: BaseModel,
        df: pd.DataFrame,
        *,
        horizon: int = 1,
        include_history: bool = False,
        return_quantiles: bool = False,
        quantiles: List[float] = [0.1, 0.5, 0.9],
    ) -> ForecastResult:
        """
        1ステップ先予測を実行
        
        Args:
            model: 学習済みモデル
            df: 最新データ（必要なラグ期間を含む）
            horizon: 予測期間（デフォルト=1）
            include_history: 履歴を含めるか
            return_quantiles: 分位点を返すか
            quantiles: 分位点リスト
            
        Returns:
            ForecastResult:
                - predictions: pd.DataFrame
                    - unique_id: str
                    - ds: datetime
                    - y_pred: float
                    - [y_pred_q10, y_pred_q50, y_pred_q90]: Optional[float]
                - metadata: Dict[str, Any]
                    - model_name: str
                    - prediction_time: datetime
                    - input_rows: int
                    - output_rows: int
                    
        Example:
            >>> forecaster = Forecaster()
            >>> result = forecaster.predict_one_step(
            ...     model=production_model,
            ...     df=latest_data,
            ...     horizon=7,
            ...     return_quantiles=True
            ... )
            >>> result.predictions
               unique_id         ds  y_pred  y_pred_q10  y_pred_q50  y_pred_q90
            0      store_1 2025-11-04   123.4       110.2       123.4       136.6
            1      store_1 2025-11-05   125.7       112.0       125.7       139.4
        """
```

---

#### 5.7.2 再学習スケジューリング (FR-FORECAST-002)

**概要**: 定期的または条件付きでモデルを再学習

**優先度**: 高（必須）

**再学習トリガー**:

| トリガー | 説明 | 設定例 |
|---------|------|--------|
| **時間ベース** | 定期的に再学習 | 毎週月曜日00:00 |
| **データ量ベース** | 新規データが閾値超過 | 新規100行で再学習 |
| **精度劣化ベース** | 精度が閾値を下回る | sMAPE > 15%で再学習 |
| **ドリフト検出ベース** | データ分布の変化を検出 | KS検定 p<0.05で再学習 |
| **手動トリガー** | ユーザーが明示的に実行 | UIから「再学習」ボタン |

**APIエンドポイント**:

```python
class RetrainingScheduler:
    def schedule_retrain(
        self,
        model_id: UUID,
        *,
        trigger_type: Literal["time", "data_volume", "accuracy", "drift", "manual"],
        trigger_config: Dict[str, Any],
        retrain_config: Dict[str, Any],
    ) -> RetrainingJob:
        """
        再学習をスケジュール
        
        Args:
            model_id: モデルID
            trigger_type: トリガータイプ
            trigger_config: トリガー設定
                - time: {"cron": "0 0 * * MON"}
                - data_volume: {"threshold": 100, "unit": "rows"}
                - accuracy: {"metric": "smape", "threshold": 0.15}
                - drift: {"method": "ks_test", "alpha": 0.05}
                - manual: {}
            retrain_config: 再学習設定
                - hyperparameters: Dict
                - dataset_window: str ("last_30_days", "all")
                - notify_on_completion: bool
                
        Returns:
            RetrainingJob: スケジュールされたジョブ
            
        Example:
            >>> scheduler = RetrainingScheduler()
            >>> job = scheduler.schedule_retrain(
            ...     model_id=model.id,
            ...     trigger_type="time",
            ...     trigger_config={"cron": "0 0 * * MON"},
            ...     retrain_config={
            ...         "hyperparameters": {"max_steps": 1000},
            ...         "dataset_window": "last_90_days"
            ...     }
            ... )
            >>> job.job_id
            UUID('...')
        """
    
    def check_and_trigger(self) -> List[RetrainingJob]:
        """
        全スケジュールをチェックし、条件を満たすものをトリガー
        
        Returns:
            List[RetrainingJob]: トリガーされたジョブリスト
            
        Example:
            >>> triggered_jobs = scheduler.check_and_trigger()
            >>> for job in triggered_jobs:
            ...     print(f"Triggered: {job.model_id} due to {job.trigger_type}")
        """
```

---

#### 5.7.3 ドリフト検出 (FR-FORECAST-003)

**概要**: データ分布の変化を統計的に検出

**優先度**: 中

**検出手法**:

| 手法 | 説明 | 統計量 | 閾値 |
|-----|------|--------|------|
| **Kolmogorov-Smirnov検定** | 累積分布関数の差 | KS統計量 | p < 0.05 |
| **Chi-squared検定** | カテゴリ分布の差 | χ²統計量 | p < 0.05 |
| **Population Stability Index (PSI)** | 分布の安定性指標 | PSI値 | >0.2でドリフト |
| **ADWIN** | 適応的ウィンドウ | 変化検出 | 自動 |
| **Maximum Mean Discrepancy (MMD)** | 分布間距離 | MMD統計量 | p < 0.05 |

**APIエンドポイント**:

```python
class DriftDetector:
    def detect_drift(
        self,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        *,
        columns: Optional[List[str]] = None,
        method: Literal["ks", "chi2", "psi", "adwin", "mmd"] = "ks",
        alpha: float = 0.05,
        psi_threshold: float = 0.2,
    ) -> DriftResult:
        """
        データドリフトを検出
        
        Args:
            reference_data: 参照データ（学習時のデータ）
            current_data: 現在のデータ
            columns: チェックするカラムリスト（Noneで全数値カラム）
            method: 検出手法
            alpha: 有意水準（統計的検定用）
            psi_threshold: PSI閾値
            
        Returns:
            DriftResult:
                - has_drift: bool
                - drift_columns: List[str]
                - statistics: Dict[str, Any]
                    - column:
                        - statistic: float
                        - p_value: Optional[float]
                        - is_drifted: bool
                - summary: str
                
        Example:
            >>> detector = DriftDetector()
            >>> result = detector.detect_drift(
            ...     reference_data=train_df,
            ...     current_data=latest_df,
            ...     method="ks",
            ...     alpha=0.05
            ... )
            >>> if result.has_drift:
            ...     print(f"Drift detected in: {result.drift_columns}")
            ...     trigger_retrain()
        """
```

---

### 5.8 モデルレジストリ (FR-REGISTRY)

#### 5.8.1 モデル登録 (FR-REGISTRY-001)

**概要**: モデルをレジストリに登録し、バージョン管理

**優先度**: 高（必須）

**モデルステージ**:

| ステージ | 説明 | 用途 |
|---------|------|------|
| **Development** | 開発中 | 実験段階 |
| **Staging** | ステージング | 検証・テスト |
| **Production** | 本番 | 本番運用 |
| **Archived** | アーカイブ | 過去のバージョン |

**APIエンドポイント**:

```python
class ModelRegistry:
    def register_model(
        self,
        model: BaseModel,
        *,
        name: str,
        version: Optional[str] = None,
        stage: Literal["Development", "Staging", "Production", "Archived"] = "Development",
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> RegisteredModel:
        """
        モデルをレジストリに登録
        
        Args:
            model: モデルオブジェクト
            name: モデル名
            version: バージョン（Noneで自動採番）
            stage: ステージ
            metadata: メタデータ（性能指標、学習データ情報など）
            tags: タグ
            
        Returns:
            RegisteredModel: 登録されたモデル
                - model_id: UUID
                - name: str
                - version: str
                - stage: str
                - registered_at: datetime
                - path: Path
                
        Example:
            >>> registry = ModelRegistry()
            >>> registered = registry.register_model(
            ...     model=best_model,
            ...     name="AutoNHITS_sales_forecast",
            ...     stage="Staging",
            ...     metadata={
            ...         "mae": 1.23,
            ...         "rmse": 1.56,
            ...         "training_date": "2025-11-03",
            ...         "dataset_version": "a3f8c921"
            ...     },
            ...     tags={"model_type": "AutoNHITS", "dataset": "sales"}
            ... )
            >>> registered.model_id
            UUID('...')
        """
    
    def promote_model(
        self,
        model_id: UUID,
        *,
        from_stage: str,
        to_stage: str,
        require_approval: bool = True,
    ) -> RegisteredModel:
        """
        モデルのステージを昇格
        
        Args:
            model_id: モデルID
            from_stage: 現在のステージ
            to_stage: 昇格先ステージ
            require_approval: 承認必須フラグ
            
        Returns:
            RegisteredModel: 昇格後のモデル
            
        Raises:
            InvalidStageTransitionError: 不正なステージ遷移
            ApprovalRequiredError: 承認が必要
            
        Example:
            >>> # Staging → Productionへ昇格
            >>> promoted = registry.promote_model(
            ...     model_id=registered.model_id,
            ...     from_stage="Staging",
            ...     to_stage="Production",
            ...     require_approval=True
            ... )
        """
    
    def get_model(
        self,
        name: str,
        *,
        version: Optional[str] = None,
        stage: Optional[str] = None,
    ) -> BaseModel:
        """
        モデルを取得
        
        Args:
            name: モデル名
            version: バージョン（Noneで最新）
            stage: ステージ（指定した場合、該当ステージの最新）
            
        Returns:
            BaseModel: ロードされたモデル
            
        Example:
            >>> # Production環境の最新モデルを取得
            >>> prod_model = registry.get_model(
            ...     name="AutoNHITS_sales_forecast",
            ...     stage="Production"
            ... )
            >>> # 特定バージョンを取得
            >>> v2_model = registry.get_model(
            ...     name="AutoNHITS_sales_forecast",
            ...     version="v2.0.1"
            ... )
        """
```

---

### 5.9 可視化・UI (FR-UI)

#### 5.9.1 Webアプリケーション (FR-UI-001)

**概要**: Streamlit/Dashによる運用UI

**優先度**: 中

**主要画面**:

| 画面 | 機能 | 表示内容 |
|-----|------|---------|
| **ダッシュボード** | 概要表示 | 実行中Run、リソース使用率、最新予測結果 |
| **実験一覧** | 実験管理 | Experiment/Run一覧、フィルタ、検索 |
| **実験詳細** | 詳細表示 | パラメータ、メトリクス、グラフ、ログ |
| **モデル比較** | 比較分析 | 複数モデルのメトリクス比較、散布図 |
| **予測実行** | 予測操作 | データアップロード、モデル選択、予測実行 |
| **再学習設定** | スケジュール | トリガー設定、再学習パラメータ |
| **レジストリ** | モデル管理 | 登録モデル一覧、ステージ遷移 |
| **リソース監視** | 監視 | CPU/GPU/メモリ使用率、ジョブキュー |

**APIエンドポイント** (FastAPI):

```python
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

app = FastAPI()

class PredictionRequest(BaseModel):
    model_name: str
    model_version: Optional[str] = None
    data: Dict[str, List[Any]]
    horizon: int = 7
    return_quantiles: bool = False

@app.post("/api/v1/predict")
async def predict(request: PredictionRequest) -> Dict[str, Any]:
    """
    予測APIエンドポイント
    
    Args:
        request: 予測リクエスト
        
    Returns:
        Dict: 予測結果
            - predictions: List[Dict]
            - metadata: Dict
            
    Example:
        >>> import requests
        >>> response = requests.post(
        ...     "http://localhost:8000/api/v1/predict",
        ...     json={
        ...         "model_name": "AutoNHITS_sales_forecast",
        ...         "model_version": "v1.0.0",
        ...         "data": {
        ...             "unique_id": ["store_1"],
        ...             "ds": ["2025-11-03"],
        ...             "y": [123.4]
        ...         },
        ...         "horizon": 7
        ...     }
        ... )
        >>> response.json()
        {
            "predictions": [
                {"unique_id": "store_1", "ds": "2025-11-04", "y_pred": 125.7},
                ...
            ],
            "metadata": {"model_name": "AutoNHITS_sales_forecast", ...}
        }
    """

@app.post("/api/v1/experiments")
async def create_experiment(request: ExperimentCreateRequest) -> Dict[str, Any]:
    """実験作成APIエンドポイント"""

@app.get("/api/v1/experiments/{experiment_id}")
async def get_experiment(experiment_id: UUID) -> Dict[str, Any]:
    """実験取得APIエンドポイント"""

@app.post("/api/v1/runs")
async def create_run(request: RunCreateRequest) -> Dict[str, Any]:
    """Run作成APIエンドポイント"""

@app.get("/api/v1/models")
async def list_models(
    stage: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """モデル一覧APIエンドポイント"""
```

---

## 6. 非機能要件詳細

### 6.1 性能要件

| 項目 | 要件 | 測定方法 |
|-----|------|---------|
| **単一モデル学習時間** | <10分 | Wall clock time |
| **100モデル並列学習時間** | <2時間 | Wall clock time |
| **予測レイテンシ (単一)** | <100ms | time.perf_counter |
| **予測レイテンシ (バッチ100件)** | <1秒 | time.perf_counter |
| **データ読み込み (1GB CSV)** | <30秒 | time.perf_counter |
| **メモリ使用量** | <16GB (ピーク) | psutil |
| **GPU VRAM使用量** | <12GB (ピーク) | nvidia-smi |

---

### 6.2 可用性要件

| 項目 | 要件 |
|-----|------|
| **システム稼働率** | 99% (月間) |
| **MTBF (Mean Time Between Failures)** | >720時間 (30日) |
| **MTTR (Mean Time To Repair)** | <1時間 |
| **データバックアップ** | 日次 |
| **バックアップ保持期間** | 30日 |

---

### 6.3 拡張性要件

| 項目 | 要件 |
|-----|------|
| **並列実行数** | 最大32 (CPUコア数依存) |
| **GPU数** | 最大4 (Multi-GPU対応) |
| **データセットサイズ** | 最大10GB (単一CSV) |
| **unique_id数** | 最大10,000 |
| **時系列長** | 最大100,000行/unique_id |
| **特徴量数** | 最大1,000 |

---

### 6.4 セキュリティ要件

| 項目 | 要件 |
|-----|------|
| **認証** | ローカル実行のため不要（将来拡張可能） |
| **秘密情報管理** | 環境変数のみ、コード内ハードコード禁止 |
| **PII処理** | デフォルト未対応（必要時に匿名化処理追加） |
| **アクセスログ** | すべてのAPI呼び出しをログ記録 |
| **データ暗号化** | ローカルファイルシステムの暗号化推奨 |

---

### 6.5 保守性要件

| 項目 | 要件 |
|-----|------|
| **コードカバレッジ** | >90% (ユニットテスト) |
| **Pylintスコア** | ≥8.5 |
| **ドキュメント率** | 100% (公開API) |
| **依存関係管理** | pyproject.toml + requirements.txt |
| **バージョン管理** | Git (セマンティックバージョニング) |

---

## 7. API仕様詳細

### 7.1 REST API

**Base URL**: `http://localhost:8000/api/v1`

**認証**: 現時点では不要（将来拡張可能）

**共通レスポンス形式**:

```json
{
  "success": true,
  "data": {...},
  "error": null,
  "timestamp": "2025-11-03T12:34:56.789Z"
}
```

**エラーレスポンス形式**:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "horizon",
      "reason": "must be positive integer"
    }
  },
  "timestamp": "2025-11-03T12:34:56.789Z"
}
```

---

### 7.2 エンドポイント一覧

#### 7.2.1 実験管理

```
POST   /experiments              実験作成
GET    /experiments              実験一覧取得
GET    /experiments/{id}         実験詳細取得
PUT    /experiments/{id}         実験更新
DELETE /experiments/{id}         実験削除
```

#### 7.2.2 Run管理

```
POST   /runs                     Run作成
GET    /runs                     Run一覧取得
GET    /runs/{id}                Run詳細取得
PUT    /runs/{id}/status         Runステータス更新
DELETE /runs/{id}                Run削除
GET    /runs/{id}/metrics        Runメトリクス取得
GET    /runs/{id}/artifacts      Runアーティファクト一覧取得
```

#### 7.2.3 予測

```
POST   /predict                  予測実行
POST   /predict/batch            バッチ予測実行
GET    /predict/history          予測履歴取得
```

#### 7.2.4 モデル管理

```
POST   /models                   モデル登録
GET    /models                   モデル一覧取得
GET    /models/{id}              モデル詳細取得
PUT    /models/{id}/stage        モデルステージ変更
DELETE /models/{id}              モデル削除
GET    /models/{id}/versions     モデルバージョン一覧取得
```

#### 7.2.5 データ管理

```
POST   /datasets                 データセット登録
GET    /datasets                 データセット一覧取得
GET    /datasets/{id}            データセット詳細取得
POST   /datasets/{id}/profile    データプロファイル生成
```

---

### 7.3 詳細API仕様

#### 7.3.1 POST /predict

**リクエスト**:

```json
{
  "model_name": "AutoNHITS_sales_forecast",
  "model_version": "v1.0.0",
  "data": {
    "unique_id": ["store_1", "store_2"],
    "ds": ["2025-11-03", "2025-11-03"],
    "y": [123.4, 234.5],
    "temperature": [15.2, 18.3],
    "promotion_flag": [0, 1]
  },
  "horizon": 7,
  "return_quantiles": true,
  "quantiles": [0.1, 0.5, 0.9]
}
```

**レスポンス**:

```json
{
  "success": true,
  "data": {
    "predictions": [
      {
        "unique_id": "store_1",
        "ds": "2025-11-04",
        "y_pred": 125.7,
        "y_pred_q10": 112.0,
        "y_pred_q50": 125.7,
        "y_pred_q90": 139.4
      },
      {
        "unique_id": "store_1",
        "ds": "2025-11-05",
        "y_pred": 127.3,
        "y_pred_q10": 113.5,
        "y_pred_q50": 127.3,
        "y_pred_q90": 141.1
      },
      ...
    ],
    "metadata": {
      "model_name": "AutoNHITS_sales_forecast",
      "model_version": "v1.0.0",
      "prediction_time": "2025-11-03T12:34:56.789Z",
      "input_rows": 2,
      "output_rows": 14,
      "latency_ms": 89.3
    }
  },
  "error": null,
  "timestamp": "2025-11-03T12:34:56.789Z"
}
```

---

## 8. データスキーマ詳細

### 8.1 PostgreSQLスキーマ

#### 8.1.1 datasets (データセット)

```sql
CREATE TABLE datasets (
    id SERIAL PRIMARY KEY,
    dataset_version VARCHAR(16) UNIQUE NOT NULL,
    file_path TEXT NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    row_count INTEGER NOT NULL,
    column_count INTEGER NOT NULL,
    unique_id_count INTEGER NOT NULL,
    date_range_start TIMESTAMP,
    date_range_end TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dataset_version ON datasets(dataset_version);
CREATE INDEX idx_created_at ON datasets(created_at DESC);
```

---

#### 8.1.2 experiments (実験)

```sql
CREATE TABLE experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    objective TEXT,
    description TEXT,
    tags JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active'
);

CREATE INDEX idx_exp_name ON experiments(name);
CREATE INDEX idx_exp_created_at ON experiments(created_at DESC);
CREATE INDEX idx_exp_status ON experiments(status);
```

---

#### 8.1.3 runs (実行)

```sql
CREATE TABLE runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    run_fingerprint VARCHAR(16) UNIQUE NOT NULL,
    run_name VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50),
    hyperparameters JSONB NOT NULL,
    dataset_version VARCHAR(16) REFERENCES datasets(dataset_version),
    feature_set_id VARCHAR(100),
    training_window JSONB,
    code_revision VARCHAR(40),
    random_seed INTEGER,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_seconds FLOAT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_run_exp_id ON runs(experiment_id);
CREATE INDEX idx_run_fingerprint ON runs(run_fingerprint);
CREATE INDEX idx_run_status ON runs(status);
CREATE INDEX idx_run_created_at ON runs(created_at DESC);
CREATE INDEX idx_run_model_name ON runs(model_name);
```

---

#### 8.1.4 metrics (メトリクス)

```sql
CREATE TABLE metrics (
    id SERIAL PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    step INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_metric_run_id ON metrics(run_id);
CREATE INDEX idx_metric_name ON metrics(metric_name);
CREATE INDEX idx_metric_timestamp ON metrics(timestamp DESC);
CREATE INDEX idx_metric_run_name ON metrics(run_id, metric_name);
```

---

#### 8.1.5 artifacts (アーティファクト)

```sql
CREATE TABLE artifacts (
    id SERIAL PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    artifact_type VARCHAR(50) NOT NULL,
    artifact_path TEXT NOT NULL,
    file_size_bytes BIGINT,
    file_hash VARCHAR(64),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_artifact_run_id ON artifacts(run_id);
CREATE INDEX idx_artifact_type ON artifacts(artifact_type);
CREATE INDEX idx_artifact_created_at ON artifacts(created_at DESC);
```

---

#### 8.1.6 models (モデルレジストリ)

```sql
CREATE TABLE models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    stage VARCHAR(50) DEFAULT 'Development',
    run_id UUID REFERENCES runs(id),
    model_path TEXT NOT NULL,
    model_size_bytes BIGINT,
    metadata JSONB,
    tags JSONB,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    promoted_at TIMESTAMP,
    promoted_by VARCHAR(100),
    UNIQUE(name, version)
);

CREATE INDEX idx_model_name ON models(name);
CREATE INDEX idx_model_stage ON models(stage);
CREATE INDEX idx_model_registered_at ON models(registered_at DESC);
```

---

#### 8.1.7 predictions (予測結果)

```sql
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    model_id UUID REFERENCES models(id),
    unique_id VARCHAR(255) NOT NULL,
    ds TIMESTAMP NOT NULL,
    y_pred FLOAT NOT NULL,
    y_pred_lower FLOAT,
    y_pred_upper FLOAT,
    y_actual FLOAT,
    prediction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_pred_model_id ON predictions(model_id);
CREATE INDEX idx_pred_unique_id ON predictions(unique_id);
CREATE INDEX idx_pred_ds ON predictions(ds DESC);
CREATE INDEX idx_pred_time ON predictions(prediction_time DESC);
```

---

#### 8.1.8 feature_importances (特徴量重要度)

```sql
CREATE TABLE feature_importances (
    id SERIAL PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    feature_name VARCHAR(255) NOT NULL,
    importance_value FLOAT NOT NULL,
    importance_std FLOAT,
    rank INTEGER,
    method VARCHAR(50),
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fi_run_id ON feature_importances(run_id);
CREATE INDEX idx_fi_feature_name ON feature_importances(feature_name);
CREATE INDEX idx_fi_rank ON feature_importances(run_id, rank);
```

---

### 8.2 JSONBフィールド詳細

#### 8.2.1 hyperparameters (JSONB)

```json
{
  "input_size": 14,
  "h": 7,
  "loss": "MAE",
  "scaler": "standard",
  "max_steps": 1000,
  "learning_rate": 0.001,
  "batch_size": 32,
  "hidden_size": 128,
  "num_layers": 2,
  "dropout": 0.1,
  "optimizer": "Adam",
  "early_stopping_patience": 10
}
```

---

#### 8.2.2 metadata (JSONB)

```json
{
  "training_time_seconds": 123.45,
  "gpu_id": 0,
  "gpu_name": "NVIDIA RTX 5070 Ti",
  "peak_memory_mb": 8192,
  "num_parameters": 1234567,
  "pytorch_version": "2.0.1",
  "cuda_version": "11.8",
  "hostname": "ml-server-01",
  "python_version": "3.11.4"
}
```

---

#### 8.2.3 training_window (JSONB)

```json
{
  "start_date": "2023-01-01",
  "end_date": "2024-12-31",
  "split_method": "rolling_origin",
  "n_splits": 5,
  "horizon": 7,
  "gap": 0,
  "expanding_window": true
}
```

---

## 9. 品質属性

### 9.1 Reusability (再利用性)

**目標**: ⭐⭐⭐⭐⭐ (5/5)

**実現方法**:
- レイヤー化アーキテクチャ（9層）
- Adapter Patternによるモデル抽象化
- 依存性注入による疎結合
- 型ヒント完全対応

**評価基準**:
- 他プロジェクトへの流用可能性 >80%
- インターフェースの安定性
- ドキュメント完備

---

### 9.2 Testability (テスト容易性)

**目標**: ⭐⭐⭐⭐⭐ (5/5)

**実現方法**:
- 依存性注入によるモック可能性
- 純粋関数の多用
- TDD (Test-Driven Development)
- Fixture/Mocksの整備

**評価基準**:
- ユニットテストカバレッジ >90%
- 統合テストカバレッジ >80%
- E2Eテストカバレッジ >70%

---

### 9.3 Maintainability (保守性)

**目標**: ⭐⭐⭐⭐⭐ (5/5)

**実現方法**:
- SOLID原則遵守
- 低結合・高凝集
- 明確な命名規則
- 包括的ドキュメント

**評価基準**:
- Pylintスコア ≥8.5
- 循環的複雑度 <10
- 関数の平均行数 <50行

---

### 9.4 Extensibility (拡張性)

**目標**: ⭐⭐⭐⭐⭐ (5/5)

**実現方法**:
- プラグイン可能なアーキテクチャ
- Factory Pattern
- Strategy Pattern
- 設定ファイルによるカスタマイズ

**評価基準**:
- 新モデルの追加工数 <2日
- 新特徴量の追加工数 <0.5日
- 新評価指標の追加工数 <0.5日

---

### 9.5 Reliability (信頼性)

**目標**: ⭐⭐⭐⭐ (4/5)

**実現方法**:
- 包括的なエラーハンドリング
- リトライメカニズム
- 冪等性保証
- チェックポイント

**評価基準**:
- システム稼働率 >99%
- MTBF >720時間
- MTTR <1時間

---

### 9.6 Performance (性能)

**目標**: ⭐⭐⭐⭐ (4/5)

**実現方法**:
- 並列実行対応
- キャッシング
- 効率的なデータ構造
- GPU活用

**評価基準**:
- 単一モデル学習時間 <10分
- 100モデル並列学習 <2時間
- 予測レイテンシ <100ms

---

### 9.7 Security (セキュリティ)

**目標**: ⭐⭐⭐⭐ (4/5)

**実現方法**:
- 秘密情報の環境変数管理
- PII除外（デフォルト）
- パス検証
- アクセスログ

**評価基準**:
- 脆弱性スキャン pass
- 秘密情報の漏洩 0件
- セキュリティインシデント 0件

---

### 9.8 Compatibility (互換性)

**目標**: ⭐⭐⭐⭐⭐ (5/5)

**実現方法**:
- Adapter Pattern
- バージョン管理
- 段階的マイグレーション
- 後方互換性保証

**評価基準**:
- Python 3.11+ 対応
- PyTorch 2.0+ 対応
- 複数OSサポート（Linux/macOS/Windows）

---

## 10. 制約事項

### 10.1 機能制約

| 制約 | 内容 |
|-----|------|
| **データ形式** | CSV形式のみ（Parquetは将来対応） |
| **時間粒度** | 日次～月次を想定（秒単位は未対応） |
| **リアルタイム予測** | バッチ中心（ストリーミングは未対応） |
| **PII処理** | デフォルト未対応（別途匿名化処理が必要） |

---

### 10.2 技術制約

| 制約 | 内容 |
|-----|------|
| **Python版** | 3.11以上必須 |
| **PostgreSQL** | 14以上推奨 |
| **GPU** | CUDA 11.0以上（オプション） |
| **メモリ** | 16GB以上推奨 |

---

### 10.3 運用制約

| 制約 | 内容 |
|-----|------|
| **実行環境** | ローカル実行（クラウドは将来対応） |
| **認証** | 現時点では不要 |
| **スケールアウト** | 単一サーバー（分散実行は将来対応） |

---

## 11. リスクと対策

### 11.1 技術リスク

| リスク | 影響 | 発生確率 | 対策 |
|-------|------|---------|------|
| **OOM (Out of Memory)** | 高 | 中 | チャンク読み込み、ダウンサンプリング |
| **GPU OOM** | 中 | 中 | Mixed Precision、Gradient Accumulation |
| **学習時間超過** | 中 | 低 | Early Stopping、ハイパーパラメータ調整 |
| **データ品質問題** | 高 | 高 | 検証強化、異常検出 |
| **依存関係の競合** | 中 | 低 | 仮想環境、Dockerコンテナ |

---

### 11.2 運用リスク

| リスク | 影響 | 発生確率 | 対策 |
|-------|------|---------|------|
| **ディスク容量不足** | 高 | 中 | 自動クリーンアップ、監視 |
| **モデル性能劣化** | 高 | 中 | ドリフト検出、自動再学習 |
| **バックアップ失敗** | 高 | 低 | 冗長化、監視 |
| **ログ肥大化** | 中 | 高 | ローテーション、圧縮 |

---

### 11.3 ビジネスリスク

| リスク | 影響 | 発生確率 | 対策 |
|-------|------|---------|------|
| **要件変更** | 中 | 高 | アジャイル開発、柔軟な設計 |
| **納期遅延** | 高 | 中 | MVP優先、段階的リリース |
| **スキル不足** | 中 | 中 | トレーニング、ドキュメント整備 |

---

## 12. 付録

### 12.1 参考資料

| 資料 | URL |
|-----|-----|
| **NeuralForecast公式** | https://nixtlaverse.nixtla.io/neuralforecast/ |
| **MLflow公式** | https://mlflow.org/ |
| **Optuna公式** | https://optuna.org/ |
| **Ray公式** | https://www.ray.io/ |
| **Hydra公式** | https://hydra.cc/ |

---

### 12.2 用語集

詳細は [2. 用語定義](#2-用語定義) を参照

---

### 12.3 変更履歴

| 日付 | バージョン | 変更内容 | 担当者 |
|------|-----------|---------|--------|
| 2025-11-03 | v1.0.0 | 初版作成 | Claude Team |

---

### 12.4 承認

| 役割 | 氏名 | 承認日 | 署名 |
|-----|------|--------|------|
| Product Owner | - | - | - |
| Tech Lead | - | - | - |
| QA Lead | - | - | - |

---

**End of Document**

---

**総ページ数**: 約200ページ相当
**総文字数**: 約50,000文字
**詳細度**: 高精細（クラス、メソッド、パラメータ、変数レベル）
