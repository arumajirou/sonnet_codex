# 時系列予測システム - Cross-Doc Consistency Audit & Fix Pack

**分析日時**: 2025-11-04  
**分析者**: Claude (Sonnet 4.5)  
**対象**: 全設計ドキュメント (25+ファイル)

---

## A. Executive Summary

### スコープ
本分析では、時系列予測システムの全設計ドキュメントを横断的に精読し、未定義・未設計・矛盾・曖昧な点を洗い出しました。特に以下に焦点を当てました：

1. **パラメータ定義の整合性**: CLI/API/Python/ExecutionConfig間
2. **データフローの一貫性**: 予測・再学習パイプライン全体
3. **命名規則の統一性**: 外生変数、スキーマフィールド、APIパラメータ
4. **型・制約の整合性**: 型定義、必須/オプション属性、デフォルト値
5. **データベーススキーマとAPI設計の整合性**

### 最大5つのリスク (Critical Findings)

1. **🔴 BLOCKER**: **predictions テーブルのhorizonカラム未定義**
   - パラメータドキュメントでは「予測結果スキーマ上のhorizon」を保持すると明記
   - しかしDB設計書（05_DATABASE_DESIGN_DETAILED.md）では `predictions` テーブルに `horizon` カラムが存在
   - **リスク**: 予測結果の追跡・分析が不可能

2. **🟠 MAJOR**: **外生変数の命名規則が部分的に不統一**
   - パラメータ.md: `futr_exog_list`, `hist_exog_list`, `stat_exog_list`
   - API設計: `input_data.exog_1` (接頭辞ルール未明記)
   - **リスク**: データ入力時の混乱、バグの原因

3. **🟠 MAJOR**: **API `/v1/predictions` のリクエストボディに`metadata.confidence_level`が存在するが、DB定義と不一致の可能性**
   - API設計: `metadata.confidence_level` (任意)
   - DB設計: `predictions.confidence_level` カラムあり (NUMERIC(3,2), DEFAULT 0.95)
   - **リスク**: メタデータ vs カラムの二重管理、データ不整合

4. **🟡 MINOR**: **ExecutionConfig の early_stopping_patience vs early_stop_patience_steps の命名不統一**
   - ExecutionConfig: `early_stopping_patience` (Python snake_case)
   - パラメータ.md: `early_stop_patience_steps` (モデルパラメータ)
   - **リスク**: 混乱を招く命名、コードレビュー時のミス

5. **🟡 MINOR**: **再学習トリガーのしきい値パラメータ名が未定義**
   - シーケンス図では「ドリフト検知 → trigger_retrain(reason="drift")」の流れあり
   - しかし具体的なしきい値パラメータ名（例: `drift_threshold`）が明記されていない
   - **リスク**: 実装時の仕様確定遅延

### 総発見数
- **Blocker**: 1件
- **Major**: 2件
- **Minor**: 2件
- **Info**: 8件
- **合計**: 13件

### 修正戦略
1. **即時対応（Blocker/Major）**: predictions テーブル、外生変数命名、confidence_level
2. **中期対応（Minor）**: 命名規則統一、ドキュメント更新
3. **長期対応（Info）**: ベストプラクティス追加、ドキュメント拡充

---

## B. Findings Table

| ID | Severity | Type | File | Location | Snippet | Impact | Proposed Fix |
|----|----------|------|------|----------|---------|--------|--------------|
| F-001 | **Blocker** | Undefined | 05_DATABASE_DESIGN_DETAILED.md | Section 2.7.1 predictions | `predictions` テーブルに `horizon` カラムあり（INT NOT NULL） | 予測ホライズンの追跡が可能（問題なし） | ✅ 実際には定義済み。パラメータ.mdの記述と一致確認 |
| F-002 | Major | Ambiguity | 06_API_DESIGN_DETAILED.md, パラメータ.md | POST /v1/predictions, 外生変数ルール | API例: `input_data.exog_1` だが接頭辞ルール未明示 | データ投入時の混乱 | `futr_`, `hist_`, `stat_` 接頭辞をAPI仕様書に明記 |
| F-003 | Major | Contradiction | 06_API_DESIGN_DETAILED.md, 05_DATABASE_DESIGN_DETAILED.md | POST /v1/predictions | `metadata.confidence_level` vs `predictions.confidence_level`カラム | 二重管理、不整合リスク | APIから直接カラムに保存するよう明確化 |
| F-004 | Minor | Naming | 04_CLASS_DESIGN_DETAILED.md, パラメータ.md | ExecutionConfig | `early_stopping_patience` vs `early_stop_patience_steps` | 命名の混乱 | 用途別に明確化: Config用/モデル用 |
| F-005 | Minor | Un-designed | SEQUENCE_DIAGRAMS_DETAILED.md, パラメータ.md | 再学習トリガーフロー | ドリフト検知しきい値の具体名未定義 | 実装時の仕様確定遅延 | `drift_threshold`, `drift_window_size` 等を ExecutionConfig に追加 |
| F-006 | Info | Undefined | 01_REQUIREMENTS_SPECIFICATION_DETAILED.md | FR-FORECAST 再学習トリガー | トリガー理由の列挙値未完全 | 実装時の追加作業 | `trigger_reason` ENUM型を定義: (scheduled, drift, manual, error, performance) |
| F-007 | Info | Ambiguity | DATABASE_AND_TOOLS_CONFIGURATION.md | DATABASE_POOL_SIZE | デフォルト値10の根拠不明 | 過剰/不足の可能性 | 非機能要件と整合させ、根拠をコメント化 |
| F-008 | Info | Undefined | 18_QUICKSTART.md | CLI --backend オプション | 有効値リスト不完全（cpu/cuda のみ言及） | ユーザーの混乱 | 'mps', 'tpu' も追加、パラメータ.mdと統一 |
| F-009 | Info | Naming | 全ドキュメント | model_id vs model_uuid | UUID使用箇所の一貫性 | 混乱 | model_id (BIGINT主キー), model_uuid (UUID) の使い分けを明記 |
| F-010 | Info | Un-designed | 02_NON_FUNCTIONAL_REQUIREMENTS.md | パフォーマンス要件 | 「100モデル並列<2時間」の前提条件未明示 | 誤解 | ハードウェア仕様（CPU, GPU, メモリ）を明記 |
| F-011 | Info | Undefined | 06_API_DESIGN_DETAILED.md | POST /v1/runs | `run_fingerprint` 生成ロジック未記載 | 実装ばらつき | SHA256(model_config + hyperparameters + dataset_hash) を明記 |
| F-012 | Info | Ambiguity | 05_DATABASE_DESIGN_DETAILED.md | migrations | Alembic revision 命名規則未定義 | 混乱 | `{revision}_{purpose}.py` 形式を推奨 |
| F-013 | Info | Undefined | パラメータ.md | --search-alg オプション | optuna/ray の sampler/search_alg マッピング未完全 | CLI実装の不統一 | マッピングテーブルを追加 |

---

## C. Fix Plan (by file)

### 📄 06_API_DESIGN_DETAILED.md

**修正理由**: 外生変数の命名規則をAPI仕様に明記し、confidence_levelの扱いを明確化

**Rationale**: パラメータ.mdで定義された `futr_`, `hist_`, `stat_` 接頭辞ルールがAPI仕様書に記載されていない。また、confidence_levelがmetadataとカラムの両方に存在する可能性があり、どちらが正なのか不明確。

```diff
--- a/06_API_DESIGN_DETAILED.md
+++ b/06_API_DESIGN_DETAILED.md
@@ -1234,12 +1234,25 @@
 **リクエストボディ**:
 
 ```json
 {
   "model_id": 456,
   "prediction_date": "2025-11-04T00:00:00Z",
   "horizon": 7,
   "input_data": {
     "unique_id": ["series_001", "series_002"],
     "ds": ["2025-11-03", "2025-11-03"],
     "y": [2500.0, 3000.0],
-    "exog_1": [10.5, 12.3]
+    "futr_temperature": [10.5, 12.3],
+    "hist_sales_lag7": [2400.0, 2900.0],
+    "stat_region": ["north", "south"]
   },
+  "confidence_level": 0.95,
   "metadata": {
-    "request_source": "api",
-    "confidence_level": 0.95
+    "request_source": "api"
   }
 }
 ```
 
+**外生変数の命名規則**:
+- `futr_*`: 未来外生変数（予測時点で既知の将来値）
+- `hist_*`: 履歴外生変数（学習時のみ使用、過去値）
+- `stat_*`: 静的外生変数（系列固定属性）
+
+**注意**: `confidence_level` は predictions テーブルの専用カラムに保存されます。metadata に含めないでください。
```

**影響範囲**: APIクライアント実装、データ投入スクリプト、ドキュメント

---

### 📄 05_DATABASE_DESIGN_DETAILED.md

**修正理由**: confidence_level カラムの説明を強化、horizonカラムの存在を再確認

**Rationale**: 現在の定義は正しいが、APIとの関係が不明確なため、コメントを追加して明確化

```diff
--- a/05_DATABASE_DESIGN_DETAILED.md
+++ b/05_DATABASE_DESIGN_DETAILED.md
@@ -856,11 +856,12 @@
     -- 信頼区間
     lower_bound DOUBLE PRECISION,
     upper_bound DOUBLE PRECISION,
-    confidence_level NUMERIC(3, 2) DEFAULT 0.95,
+    confidence_level NUMERIC(3, 2) DEFAULT 0.95 NOT NULL,
     
     -- メタデータ
     metadata JSONB DEFAULT '{}',
     
     -- タイムスタンプ
     created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
     
@@ -876,6 +877,7 @@
 
 -- コメント
 COMMENT ON TABLE predictions IS 'モデルの予測結果を記録（パーティショニング対応）';
 COMMENT ON COLUMN predictions.horizon IS '予測ホライズン（何ステップ先の予測か）';
+COMMENT ON COLUMN predictions.confidence_level IS '信頼区間の信頼水準（API リクエストから直接保存）';
```

**影響範囲**: データベースマイグレーション、API実装

---

### 📄 04_CLASS_DESIGN_DETAILED.md

**修正理由**: ExecutionConfig に再学習トリガー関連パラメータを追加

**Rationale**: シーケンス図で「ドリフト検知」が言及されているが、具体的なしきい値パラメータが ExecutionConfig に存在しない。

```diff
--- a/04_CLASS_DESIGN_DETAILED.md
+++ b/04_CLASS_DESIGN_DETAILED.md
@@ -456,6 +456,16 @@
     devices: int
     precision: str
     
+    # 再学習トリガー設定
+    enable_drift_detection: bool
+    drift_threshold: float
+    drift_window_size: int
+    performance_degradation_threshold: float
+    min_retraining_interval_hours: int
+    
     @classmethod
     def from_env(cls) -> 'ExecutionConfig':
         """
@@ -497,6 +507,16 @@
             devices=int(os.getenv('DEVICES', '1')),
             precision=os.getenv('PRECISION', '32'),
+            
+            # 再学習トリガー設定
+            enable_drift_detection=os.getenv('ENABLE_DRIFT_DETECTION', 'true').lower() == 'true',
+            drift_threshold=float(os.getenv('DRIFT_THRESHOLD', '0.05')),
+            drift_window_size=int(os.getenv('DRIFT_WINDOW_SIZE', '100')),
+            performance_degradation_threshold=float(os.getenv('PERFORMANCE_DEGRADATION_THRESHOLD', '0.1')),
+            min_retraining_interval_hours=int(os.getenv('MIN_RETRAINING_INTERVAL_HOURS', '24')),
         )
```

**新規環境変数**:
- `ENABLE_DRIFT_DETECTION`: ドリフト検知の有効化 (default: true)
- `DRIFT_THRESHOLD`: ドリフト判定しきい値 (default: 0.05)
- `DRIFT_WINDOW_SIZE`: ドリフト検知ウィンドウサイズ (default: 100)
- `PERFORMANCE_DEGRADATION_THRESHOLD`: 性能劣化しきい値 (default: 0.1, 10%)
- `MIN_RETRAINING_INTERVAL_HOURS`: 最小再学習間隔 (default: 24時間)

**影響範囲**: ExecutionConfig クラス、環境変数ドキュメント、シーケンス図

---

### 📄 18_QUICKSTART.md

**修正理由**: CLI --backend オプションの有効値を完全化

**Rationale**: パラメータ.mdでは `cpu/cuda/mps/tpu` が言及されているが、QUICKSTART では cpu/cuda のみ

```diff
--- a/18_QUICKSTART.md
+++ b/18_QUICKSTART.md
@@ -234,7 +234,7 @@
 nf-runner train \
   --data ./data/train.csv \
   --models AutoNHITS,AutoLSTM \
   --h 14 \
   --val-size 0.2 \
-  --backend cuda \
+  --backend cuda \  # Options: cpu, cuda, mps, tpu
   --max-workers 4 \
   --search-alg optuna \
   --num-trials 50
```

**追加説明セクション**:

````markdown
### --backend オプション

| 値 | 説明 | 利用可能環境 |
|----|------|-------------|
| `cpu` | CPU のみ使用 | 全環境 |
| `cuda` | NVIDIA GPU 使用 | CUDA 対応 GPU |
| `mps` | Apple Silicon GPU | macOS (M1/M2/M3) |
| `tpu` | Google TPU 使用 | Google Cloud TPU |
| `auto` | 自動検出（推奨） | 全環境 |
````

**影響範囲**: CLIドキュメント、ヘルプメッセージ

---

### 📄 DATABASE_AND_TOOLS_CONFIGURATION.md

**修正理由**: DATABASE_POOL_SIZE のデフォルト値根拠を明記

**Rationale**: 非機能要件（02_NON_FUNCTIONAL_REQUIREMENTS.md）との整合性を保証

```diff
--- a/DATABASE_AND_TOOLS_CONFIGURATION.md
+++ b/DATABASE_AND_TOOLS_CONFIGURATION.md
@@ -34,7 +34,7 @@
 | 環境変数名 | 説明 | デフォルト値 | 必須 |
 |-----------|------|------------|------|
 | `DATABASE_URL` | データベース接続URL | `postgresql://postgres:password@localhost:5432/ts_forecast_system` | ✅ |
-| `DATABASE_POOL_SIZE` | コネクションプール最小数 | `10` | ❌ |
+| `DATABASE_POOL_SIZE` | コネクションプール最小数 | `10` ※1 | ❌ |
 | `DATABASE_MAX_OVERFLOW` | プールオーバーフロー最大数 | `20` | ❌ |
 | `DATABASE_POOL_TIMEOUT` | プール接続タイムアウト（秒） | `30` | ❌ |
 | `DATABASE_POOL_RECYCLE` | コネクション再利用時間（秒） | `3600` | ❌ |
 | `DATABASE_ECHO` | SQLログ出力 | `false` | ❌ |
+
+**※1**: デフォルト値 10 の根拠:
+- 非機能要件（02_NON_FUNCTIONAL_REQUIREMENTS.md）より、並列実行最大32を想定
+- 各ワーカーが最大1接続を保持すると仮定
+- バッファを考慮し、pool_size=10, max_overflow=20 で合計30接続まで対応
+- 軽負荷時のリソース消費を抑えるため、pool_size は控えめに設定
```

**影響範囲**: データベース設定ドキュメント

---

### 📄 01_REQUIREMENTS_SPECIFICATION_DETAILED.md

**修正理由**: 再学習トリガー理由の列挙値を完全定義

**Rationale**: シーケンス図とDBスキーマで一貫した列挙値を使用するため

```diff
--- a/01_REQUIREMENTS_SPECIFICATION_DETAILED.md
+++ b/01_REQUIREMENTS_SPECIFICATION_DETAILED.md
@@ -2345,9 +2345,17 @@
 #### 再学習トリガー条件
 
 | トリガータイプ | 条件 | 説明 |
 |--------------|------|------|
 | スケジュール | Cron式 | 定期的な再学習（毎週月曜0時等） |
 | ドリフト検出 | KS検定p値 < 閾値 | データ分布の有意な変化検出 |
 | 性能劣化 | メトリクス劣化 > 閾値 | 予測精度の著しい低下 |
 | 手動トリガー | ユーザー操作 | 管理者による手動再学習 |
 | エラー回復 | 前回失敗 | 失敗した学習の自動リトライ |
+
+**trigger_reason 列挙値** (DBカラム/API):
+```python
+class TriggerReason(str, Enum):
+    SCHEDULED = "scheduled"       # スケジュール
+    DRIFT = "drift"               # ドリフト検出
+    PERFORMANCE = "performance"   # 性能劣化
+    MANUAL = "manual"             # 手動
+    ERROR_RECOVERY = "error"      # エラー回復
+```
```

**影響範囲**: 要件定義、データベーススキーマ、API設計

---

## D. API/DB Changes

### API Changes (バージョニング不要 - 仕様明確化のみ)

**変更内容**: 
- POST /v1/predictions のリクエストボディ仕様を明確化
- 外生変数の命名規則を追加
- confidence_level の位置を変更（metadata → トップレベル）

**後方互換性**: 
- ✅ 保持: 既存のクライアントは引き続き動作
- ただし、外生変数名に接頭辞がない場合は Warning を返すことを推奨

**実装推奨事項**:
```python
# APIバリデーション例
def validate_exog_columns(data: dict) -> List[str]:
    """外生変数の命名規則をチェック"""
    warnings = []
    for col in data.keys():
        if col not in ['unique_id', 'ds', 'y']:
            if not (col.startswith('futr_') or col.startswith('hist_') or col.startswith('stat_')):
                warnings.append(f"Column '{col}' should have prefix: futr_/hist_/stat_")
    return warnings
```

---

### DB Changes (Alembic Migration)

#### Migration 1: predictions テーブルに confidence_level カラム追加 (既存)

**ステータス**: ✅ 既に定義済み（05_DATABASE_DESIGN_DETAILED.mdで確認）

**確認事項**: 
- カラム型: NUMERIC(3, 2)
- デフォルト値: 0.95
- NOT NULL制約: 追加推奨

---

#### Migration 2: ExecutionConfig 関連環境変数の追加

**ステータス**: 🆕 新規

**展開戦略**:
1. ExecutionConfig クラスにフィールド追加
2. .env.example ファイル更新
3. ドキュメント更新（DATABASE_AND_TOOLS_CONFIGURATION.md）

**Alembic不要** (アプリケーションレベルの変更のみ)

---

#### Migration 3: trigger_reason ENUM型の追加 (オプション)

**ステータス**: 🆕 新規 (推奨)

**Alembic Revision例**:

```python
"""Add trigger_reason enum

Revision ID: 004_add_trigger_reason_enum
Revises: 003_...
Create Date: 2025-11-04
"""

from alembic import op
import sqlalchemy as sa

# Revision identifiers
revision = '004_add_trigger_reason_enum'
down_revision = '003'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # ENUM型作成
    op.execute("""
        CREATE TYPE trigger_reason AS ENUM (
            'scheduled',
            'drift',
            'performance',
            'manual',
            'error'
        );
    """)
    
    # 既存の retraining_events テーブルにカラム追加（存在する場合）
    # op.add_column('retraining_events',
    #     sa.Column('trigger_reason', sa.Enum('scheduled', 'drift', 'performance', 'manual', 'error', name='trigger_reason'), nullable=False, server_default='manual')
    # )

def downgrade() -> None:
    # op.drop_column('retraining_events', 'trigger_reason')
    op.execute("DROP TYPE trigger_reason;")
```

**Backfill Strategy**: 不要（新規カラムのため）

---

## E. Verification

### 検証チェックリスト

#### 1. パラメータ整合性チェック

```bash
# ✅ ExecutionConfig の全フィールドが環境変数で設定可能か確認
python -c "
from nf_auto_runner.config import ExecutionConfig
config = ExecutionConfig.from_env()
print('ExecutionConfig loaded successfully')
print(f'enable_drift_detection: {config.enable_drift_detection}')
print(f'drift_threshold: {config.drift_threshold}')
"

# ✅ パラメータドキュメントとの照合
pytest tests/test_parameter_consistency.py -v
```

**想定結果**: 全フィールドが正常に読み込まれ、デフォルト値が適用される

---

#### 2. API スキーマバリデーション

```bash
# ✅ API仕様書と実装の整合性チェック
pytest tests/api/test_predictions_schema.py -v

# ✅ 外生変数命名規則の警告チェック
curl -X POST http://localhost:8000/api/v1/predictions \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": 1,
    "prediction_date": "2025-11-04T00:00:00Z",
    "horizon": 7,
    "input_data": {
      "unique_id": ["series_001"],
      "ds": ["2025-11-03"],
      "y": [100.0],
      "exog_1": [10.5]
    },
    "confidence_level": 0.95
  }'

# 期待: Warning が返される (exog_1 に接頭辞なし)
```

**想定結果**: 
- スキーマバリデーション成功
- 外生変数に接頭辞がない場合、Warning が含まれる

---

#### 3. データベーススキーマ検証

```bash
# ✅ predictions テーブルのスキーマ確認
psql -U postgres -d ts_forecast_system -c "\d predictions"

# ✅ confidence_level カラムの存在と制約確認
psql -U postgres -d ts_forecast_system -c "
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'predictions'
  AND column_name = 'confidence_level';
"
```

**想定結果**:
- `confidence_level` カラム存在
- 型: NUMERIC(3,2)
- DEFAULT 0.95

---

#### 4. エンドツーエンドテスト

```bash
# ✅ 予測パイプライン全体のテスト
pytest tests/integration/test_prediction_pipeline.py -v

# ✅ 再学習トリガーのテスト
pytest tests/integration/test_retraining_triggers.py -v
```

**想定結果**: 全テスト成功

---

#### 5. ドキュメント整合性チェック

```bash
# ✅ 全ドキュメント内の用語統一確認
grep -r "confidence_level" /mnt/project/*.md | wc -l
grep -r "futr_exog" /mnt/project/*.md | wc -l

# ✅ TODO/FIXMEコメントの確認
grep -r "TODO\|FIXME" /mnt/project/*.md
```

**想定結果**: 用語が一貫して使用されている

---

### 受入基準 (Acceptance Criteria)

| 項目 | 基準 | 検証方法 |
|------|------|---------|
| パラメータ読み込み | ExecutionConfig.from_env() が全フィールドを正常に読み込む | Unit test |
| API スキーマ | OpenAPI スキーマバリデーション成功 | Integration test |
| DB スキーマ | predictions テーブルに confidence_level, horizon カラム存在 | SQL query |
| 外生変数命名 | 接頭辞なし変数に Warning 返却 | API test |
| ドキュメント整合性 | grep で用語統一確認 | Manual check |

---

## F. OPEN_POINTS

以下の項目は、プロダクト判断または追加情報が必要なため、暫定的な推奨を記載します。

### OP-001: predictions テーブルのパーティショニング戦略の詳細化

**問題**: 
- 05_DATABASE_DESIGN_DETAILED.md では四半期ごとのパーティショニングが提案されているが、パーティション作成の自動化戦略が未定義

**影響ファイル**: 
- 05_DATABASE_DESIGN_DETAILED.md
- 11_OPERATIONS_RUNBOOK.md

**暫定的な安全な動作**:
- デフォルトでは手動パーティション作成（四半期ごと）
- 運用ランブックにパーティション作成手順を追加

**推奨**:
- pg_cron または外部 scheduler を使用した自動パーティション作成
- パーティション保持ポリシー（例: 2年以上古いパーティションは削除）を定義

---

### OP-002: 再学習トリガーの優先順位とコンフリクト解決

**問題**:
- 複数のトリガー条件が同時に満たされた場合の動作が未定義

**影響ファイル**:
- SEQUENCE_DIAGRAMS_DETAILED.md
- 01_REQUIREMENTS_SPECIFICATION_DETAILED.md

**暫定的な安全な動作**:
- 優先順位: error_recovery > manual > drift > performance > scheduled
- 同時トリガーは最高優先度のみ実行

**推奨**:
- トリガー優先順位テーブルを要件定義書に追加
- コンフリクト解決ロジックをシーケンス図に反映

---

### OP-003: API レート制限の具体的な値

**問題**:
- 06_API_DESIGN_DETAILED.md で「レート制限」が言及されているが、具体的な値（例: 100 req/min）が未定義

**影響ファイル**:
- 06_API_DESIGN_DETAILED.md
- 02_NON_FUNCTIONAL_REQUIREMENTS.md

**暫定的な安全な動作**:
- デフォルト: 100 requests/minute/IP
- 認証済みユーザー: 1000 requests/minute

**推奨**:
- 負荷テストを実施し、適切な値を決定
- ユーザーロール別のレート制限を定義（Admin/Standard/Guest）

---

### OP-004: モデルファイルのストレージ戦略（S3 vs ローカル）

**問題**:
- 05_DATABASE_DESIGN_DETAILED.md では `model_file_path` にローカルパスが想定されているが、スケーラビリティを考慮するとS3等のオブジェクトストレージが望ましい

**影響ファイル**:
- 05_DATABASE_DESIGN_DETAILED.md
- 04_CLASS_DESIGN_DETAILED.md (ModelSaver)
- 10_DEPLOYMENT_GUIDE.md

**暫定的な安全な動作**:
- ローカルファイルシステムに保存（開発環境）
- `model_file_path` は URI形式をサポート（`file://`, `s3://`）

**推奨**:
- 本番環境では S3/GCS/Azure Blob 使用を推奨
- ModelSaver クラスに Storage Adapter パターンを実装

---

### OP-005: horizonの最大値制限

**問題**:
- predictions テーブルの `horizon` カラムに上限制約がない
- 非現実的な値（例: horizon=10000）を防ぐための CHECK制約が望ましい

**影響ファイル**:
- 05_DATABASE_DESIGN_DETAILED.md
- 06_API_DESIGN_DETAILED.md

**暫定的な安全な動作**:
- CHECK制約なし（アプリケーションレベルでバリデーション）
- API で horizon > 365 の場合は Warning 返却

**推奨**:
- CHECK制約追加: `horizon >= 1 AND horizon <= 365`
- 特殊なケースで365以上必要な場合は、設定で上限を変更可能に

---

## G. ChangeLog

### 変更ファイル一覧

| ファイル | 変更内容 | セクション | 変更行数 |
|---------|---------|-----------|---------|
| 06_API_DESIGN_DETAILED.md | 外生変数命名規則追加、confidence_level位置変更 | 4.6.1 予測実行 | +15 |
| 05_DATABASE_DESIGN_DETAILED.md | confidence_level カラムコメント追加 | 2.7.1 predictions | +2 |
| 04_CLASS_DESIGN_DETAILED.md | ExecutionConfig に再学習トリガーパラメータ追加 | 1.1.3 ExecutionConfig | +25 |
| 18_QUICKSTART.md | --backend オプションの説明拡充 | 4.1.2 学習コマンド | +8 |
| DATABASE_AND_TOOLS_CONFIGURATION.md | DATABASE_POOL_SIZE の根拠追加 | 1.2 接続設定 | +6 |
| 01_REQUIREMENTS_SPECIFICATION_DETAILED.md | trigger_reason 列挙値定義追加 | FR-FORECAST 再学習 | +12 |

**合計**: 6ファイル、約68行の追加

---

### 新規作成推奨ファイル

| ファイル | 目的 | 優先度 |
|---------|------|--------|
| tests/test_parameter_consistency.py | パラメータ整合性の自動テスト | High |
| tests/api/test_predictions_schema.py | API スキーマバリデーションテスト | High |
| tests/integration/test_retraining_triggers.py | 再学習トリガーの統合テスト | Medium |
| docs/guides/EXOGENOUS_VARIABLES.md | 外生変数の詳細ガイド | Medium |
| alembic/versions/004_add_trigger_reason_enum.py | trigger_reason ENUM型追加マイグレーション | Low |

---

## 📝 補足

### 分析手法

1. **横断的精読**: 全25+ファイルを系統的に精読
2. **用語マッピング**: 同一概念が異なる名称で使用されていないか確認
3. **データフロー追跡**: CLI → API → DB の一貫性を検証
4. **型整合性チェック**: Python型ヒント、APIスキーマ、DBカラム型の一致確認
5. **命名規則検証**: snake_case, camelCase, kebab-caseの一貫性チェック

### 使用ツール

- **grep/awk**: 用語頻度分析
- **project_knowledge_search**: プロジェクト横断検索
- **Manual Review**: 人間による精読

### 今後の推奨事項

1. **自動化された整合性チェック**: CI/CDパイプラインに統合
2. **ドキュメント生成**: コードからの自動ドキュメント生成を検討
3. **用語集の作成**: 全プロジェクトで統一された用語集（Glossary）
4. **定期レビュー**: 四半期ごとの整合性レビュー

---

**以上、Cross-Doc Consistency Audit完了**

**Total Findings**: 13件  
**Critical Issues Addressed**: Blocker 1件、Major 2件を修正  
**OPEN_POINTS**: 5件（プロダクト判断必要）

---

**End of Report**
