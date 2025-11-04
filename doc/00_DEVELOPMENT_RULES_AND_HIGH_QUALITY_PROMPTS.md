# 開発ルール＆高品質プロンプト大全
**Comprehensive Development Rules & High-Quality Prompt Guidebook**

---

## 📋 ドキュメント情報

| 項目 | 内容 |
|-----|------|
| **ドキュメントタイトル** | 時系列予測システム 開発ルール＆高品質プロンプト大全 |
| **バージョン** | v1.0.0 |
| **作成日** | 2025-11-04 |
| **最終更新日** | 2025-11-04 |
| **対象システム** | NeuralForecast Auto Runner + Time Series Forecasting System |
| **適用範囲** | 全開発フェーズ、全Roleに適用 |
| **準拠** | プロジェクト統合設計書、コーディング規約、テスト戦略 |

---

## 📚 目次

### 第1部: 開発の基本原則
1. [厳格な開発ルール](#1-厳格な開発ルール)
2. [品質保証の原則](#2-品質保証の原則)
3. [開発プロセスとPDCA](#3-開発プロセスとpdca)

### 第2部: Role別プロンプトテンプレート
4. [リードエンジニアRole](#4-リードエンジニアrole)
5. [インシデント対応Role](#5-インシデント対応role)
6. [仕様分析Role](#6-仕様分析role)
7. [環境チェックRole](#7-環境チェックrole)
8. [コード生成Role](#8-コード生成role)
9. [デバッグ&トラブルシュートRole](#9-デバッグトラブルシュートrole)
10. [テスト設計Role](#10-テスト設計role)
11. [品質評価Role](#11-品質評価role)

### 第3部: 実践ガイド
12. [開発ワークフロー](#12-開発ワークフロー)
13. [品質チェックリスト](#13-品質チェックリスト)
14. [ベストプラクティス集](#14-ベストプラクティス集)

### 第4部: 付録
15. [用語集](#15-用語集)
16. [参考資料](#16-参考資料)
17. [FAQ](#17-faq)

---

# 第1部: 開発の基本原則

## 1. 厳格な開発ルール

本プロジェクトでは、以下の**8つの厳格なルール**を必ず遵守します。

---

### 1.1 真偽の検証ルール

#### 原則
すべての主張、実装、設計決定は、**一次情報（公式ドキュメント/標準仕様/実測データ）**で裏付けること。

#### 実践方法

```markdown
## ✅ 良い例

### 主張
NeuralForecastの`AutoNHITS`は、時系列のトレンドと季節性を自動検出できる。

### 根拠
- **出典**: NeuralForecast公式ドキュメント v1.7.2
- **URL**: https://nixtlaverse.nixtla.io/neuralforecast/models.nhits.html
- **該当箇所**: Section 3.2 "Architecture - Multi-rate Encoder"
- **引用**: "AutoNHITS automatically detects seasonality and trend patterns using hierarchical interpolation."
- **実測**: テストデータ（Air Passengers）で季節成分検出率98.3%を確認

### 検証手順
```python
# 実測コード
from neuralforecast.models import AutoNHITS
model = AutoNHITS(h=12)
model.fit(train_data)
predictions = model.predict()
# 季節成分の検出を確認
```
```

```markdown
## ❌ 悪い例

### 主張
NeuralForecastは優れている。

### 問題点
- 根拠が不明（どの観点で優れているのか？）
- 一次情報の引用なし
- 実測データなし
- 主観的な断定
```

#### チェックリスト

- [ ] **一次情報の明記**: 公式ドキュメント、標準仕様、論文を引用
- [ ] **バージョン明記**: ライブラリ/ツールのバージョンを記載
- [ ] **日付明記**: 情報の取得日時を記載
- [ ] **実測**: 可能な限り実測データで検証
- [ ] **再現手順**: 他者が検証できる手順を提示
- [ ] **反証可能性**: 主張を反証できる形で記述

---

### 1.2 再現性の確保ルール

#### 原則
すべての実験、実装、デプロイは、**完全に再現可能**でなければならない。

#### 実践方法

**必須記録項目**:

```python
# config/reproducibility.py
from dataclasses import dataclass
from typing import Dict, Optional
import hashlib
import json

@dataclass
class ReproducibilityConfig:
    """再現性確保のための設定"""
    
    # 1. 環境
    python_version: str  # "3.11.5"
    os: str              # "Ubuntu 22.04.3 LTS"
    cuda_version: Optional[str] = None  # "12.1"
    
    # 2. 依存関係（完全なバージョン固定）
    dependencies: Dict[str, str] = None  # {"neuralforecast": "1.7.2", ...}
    
    # 3. 乱数シード
    random_seed: int = 42
    numpy_seed: int = 42
    torch_seed: int = 42
    
    # 4. データ
    data_hash: str = ""  # SHA256ハッシュ
    data_source: str = ""
    data_version: str = ""
    
    # 5. 実行コマンド
    command: str = ""
    working_directory: str = ""
    
    # 6. ハイパーパラメータ
    hyperparameters: Dict = None
    
    # 7. 実行時刻
    execution_timestamp: str = ""
    
    def to_fingerprint(self) -> str:
        """設定から一意のフィンガープリントを生成"""
        config_dict = {
            "python": self.python_version,
            "os": self.os,
            "cuda": self.cuda_version,
            "deps": self.dependencies,
            "seeds": {
                "random": self.random_seed,
                "numpy": self.numpy_seed,
                "torch": self.torch_seed
            },
            "data_hash": self.data_hash,
            "hyperparams": self.hyperparameters
        }
        config_json = json.dumps(config_dict, sort_keys=True)
        return hashlib.sha256(config_json.encode()).hexdigest()
```

**記録例**:

```yaml
# experiment_run_20251104_120530.yaml
run_id: "exp_001_run_042"
fingerprint: "a3f5c9d8e2b1..."

environment:
  python_version: "3.11.5"
  os: "Ubuntu 22.04.3 LTS"
  cuda_version: "12.1"
  hostname: "ml-workstation-01"

dependencies:
  neuralforecast: "1.7.2"
  torch: "2.1.0"
  pandas: "2.1.3"
  numpy: "1.26.2"

seeds:
  random: 42
  numpy: 42
  torch: 42
  torch_cuda: 42

data:
  source: "s3://myproject/data/train.csv"
  hash_sha256: "e3b0c44298fc1c149afb..."
  version: "v2.1.3"
  n_rows: 100000
  n_cols: 15

command: |
  python src/main.py \
    --config configs/experiment_001.yaml \
    --data data/train.csv \
    --output outputs/

hyperparameters:
  model: "AutoNHITS"
  h: 24
  input_size: 168
  learning_rate: 0.001
  batch_size: 32
  max_epochs: 100

execution:
  start_time: "2025-11-04T12:05:30.123456Z"
  end_time: "2025-11-04T13:42:15.987654Z"
  duration_seconds: 5805.864198
  
artifacts:
  - "outputs/model_checkpoint.pt"
  - "outputs/predictions.csv"
  - "mlflow_run://experiments/1/runs/abc123"
```

#### 再現手順テンプレート

```bash
#!/bin/bash
# reproduce_run_042.sh
# このスクリプトで実験を完全再現できる

set -e  # エラーで停止

# 1. 環境確認
echo "=== Environment Check ==="
python --version  # Python 3.11.5 期待
nvidia-smi  # CUDA 12.1 期待

# 2. 依存関係インストール
pip install -r requirements_frozen.txt

# 3. データ検証
echo "=== Data Validation ==="
EXPECTED_HASH="e3b0c44298fc1c149afb..."
ACTUAL_HASH=$(sha256sum data/train.csv | awk '{print $1}')
if [ "$ACTUAL_HASH" != "$EXPECTED_HASH" ]; then
    echo "ERROR: Data hash mismatch!"
    exit 1
fi

# 4. 実行
python src/main.py \
    --config configs/experiment_001.yaml \
    --data data/train.csv \
    --output outputs/ \
    --seed 42

# 5. 結果検証
python scripts/verify_outputs.py \
    --expected outputs/expected_results.json \
    --actual outputs/predictions.csv
```

#### チェックリスト

- [ ] **環境記録**: Python、OS、CUDA、ホスト名
- [ ] **依存関係固定**: `requirements.txt`にバージョン完全指定
- [ ] **シード固定**: 全乱数生成器でシード設定
- [ ] **データハッシュ**: SHA256で入力データを検証
- [ ] **コマンド記録**: 実行したコマンド完全記録
- [ ] **ハイパーパラメータ**: すべてのパラメータをYAML/JSONで保存
- [ ] **成果物保存**: モデル、予測、ログをバージョン管理
- [ ] **再現スクリプト**: 1コマンドで再現できるスクリプト作成

---

### 1.3 可観測性の確保ルール

#### 原則
システムの内部状態、パフォーマンス、エラーを**常に可視化・追跡可能**にする。

#### 三本柱

1. **ログ (Logging)**
2. **メトリクス (Metrics)**
3. **トレース (Tracing)**

#### 実装例

```python
# logging/structured_logger.py
import logging
import json
import time
from typing import Any, Dict, Optional
from contextlib import contextmanager

class StructuredLogger:
    """構造化ログ出力"""
    
    def __init__(self, name: str, run_id: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.run_id = run_id or "unknown"
        
    def _build_log_entry(
        self,
        level: str,
        message: str,
        **kwargs
    ) -> Dict[str, Any]:
        """ログエントリを構築"""
        entry = {
            "timestamp": time.time(),
            "level": level,
            "run_id": self.run_id,
            "message": message
        }
        entry.update(kwargs)
        return entry
    
    def info(self, message: str, **kwargs):
        """INFO ログ"""
        entry = self._build_log_entry("INFO", message, **kwargs)
        self.logger.info(json.dumps(entry))
    
    def error(self, message: str, **kwargs):
        """ERROR ログ"""
        entry = self._build_log_entry("ERROR", message, **kwargs)
        self.logger.error(json.dumps(entry))
    
    @contextmanager
    def log_execution_time(self, operation: str, **metadata):
        """実行時間を記録"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.info(
                f"Operation completed: {operation}",
                operation=operation,
                duration_seconds=duration,
                **metadata
            )


# 使用例
logger = StructuredLogger("model_training", run_id="exp_001_run_042")

with logger.log_execution_time("data_loading", dataset="train.csv"):
    data = load_data("train.csv")

logger.info(
    "Training started",
    model="AutoNHITS",
    n_samples=len(data),
    n_features=data.shape[1]
)
```

```python
# monitoring/metrics_tracker.py
from typing import Dict, List
import time

class MetricsTracker:
    """メトリクス追跡"""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.start_times: Dict[str, float] = {}
    
    def record(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """メトリクスを記録"""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        entry = {
            "timestamp": time.time(),
            "value": value,
            "tags": tags or {}
        }
        self.metrics[metric_name].append(entry)
        
        # MLflowにも記録
        if mlflow.active_run():
            mlflow.log_metric(metric_name, value)
    
    def start_timer(self, operation: str):
        """タイマー開始"""
        self.start_times[operation] = time.time()
    
    def stop_timer(self, operation: str) -> float:
        """タイマー停止、経過時間を返す"""
        if operation not in self.start_times:
            raise ValueError(f"Timer not started for {operation}")
        
        duration = time.time() - self.start_times[operation]
        self.record(f"duration_{operation}", duration)
        del self.start_times[operation]
        return duration
    
    def get_statistics(self, metric_name: str) -> Dict[str, float]:
        """メトリクスの統計を取得"""
        values = [entry["value"] for entry in self.metrics.get(metric_name, [])]
        if not values:
            return {}
        
        return {
            "count": len(values),
            "mean": np.mean(values),
            "std": np.std(values),
            "min": np.min(values),
            "max": np.max(values),
            "p50": np.percentile(values, 50),
            "p95": np.percentile(values, 95),
            "p99": np.percentile(values, 99)
        }


# 使用例
tracker = MetricsTracker()

tracker.start_timer("model_training")
model.fit(X_train, y_train)
training_duration = tracker.stop_timer("model_training")

tracker.record("training_loss", 0.123, tags={"epoch": "10", "model": "AutoNHITS"})
tracker.record("validation_mae", 42.5, tags={"epoch": "10", "split": "val"})
```

#### 保存先の指定

| 種類 | 保存先 | 形式 | 保持期間 |
|-----|--------|------|----------|
| **ログ** | `logs/structured/{date}.json` | JSON Lines | 90日 |
| **メトリクス** | MLflow/PostgreSQL | Time Series | 1年 |
| **モデル** | `artifacts/models/{run_id}/` | pickle/torch | 永続 |
| **予測結果** | PostgreSQL `predictions` | Table | 1年 |
| **ダッシュボード** | Grafana | - | リアルタイム |

#### チェックリスト

- [ ] **構造化ログ**: JSON形式で出力
- [ ] **run_id**: すべてのログにrun_id含める
- [ ] **タイムスタンプ**: ISO 8601形式
- [ ] **メトリクス記録**: 主要経路で duration, throughput 記録
- [ ] **MLflow統合**: メトリクス自動送信
- [ ] **Grafana統合**: リアルタイム監視
- [ ] **エラー追跡**: スタックトレース完全記録
- [ ] **パフォーマンス**: p50, p95, p99 記録

---

### 1.4 合理性の追求ルール

#### 原則
すべての判断・実装は、**論理的根拠**に基づく。感情的・主観的な決定を避ける。

#### 意思決定フレームワーク

```markdown
## 決定事項テンプレート

### 1. 現状分析
- **問題**: 何が課題か？
- **影響範囲**: どこに影響するか？
- **緊急度**: どれだけ急ぐ必要があるか？

### 2. 仮説
- **仮説1**: オプションA（例: PostgreSQL必須化）
- **仮説2**: オプションB（例: SQLite + MLflow）
- **仮説3**: オプションC（例: MLflow必須化）

### 3. 評価軸
- **性能**: 応答速度、スループット
- **信頼性**: 可用性、耐障害性
- **コスト**: 初期コスト、運用コスト
- **開発効率**: 実装工数、保守工数

### 4. 各オプションの評価

#### オプションA: PostgreSQL必須化
- **性能**: ⭐⭐⭐⭐⭐ (並列アクセス高速)
- **信頼性**: ⭐⭐⭐⭐⭐ (ACID保証)
- **コスト**: ⭐⭐⭐ (初期セットアップ必要)
- **開発効率**: ⭐⭐⭐⭐ (SQLAlchemy使用)

#### オプションB: SQLite + MLflow
- **性能**: ⭐⭐⭐ (並列アクセス弱い)
- **信頼性**: ⭐⭐⭐ (ファイルロック問題)
- **コスト**: ⭐⭐⭐⭐⭐ (追加セットアップ不要)
- **開発効率**: ⭐⭐⭐ (ネットワーク依存)

#### オプションC: MLflow必須化
- **性能**: ⭐⭐⭐⭐ (専用DB使用)
- **信頼性**: ⭐⭐ (ネットワーク障害リスク)
- **コスト**: ⭐⭐ (MLflowサーバー必要)
- **開発効率**: ⭐⭐⭐ (ネットワーク依存)

### 5. 結論
**選択**: オプションA (PostgreSQL必須化)

**理由**:
1. 並列実行時の性能が最も高い（実測: 3倍高速）
2. ACID保証により信頼性が最も高い
3. ローカル完結でネットワーク依存なし
4. SQLAlchemyで開発効率良好

**トレードオフ**:
- 初期セットアップが必要（1時間程度）
- PostgreSQLの知識が必要

### 6. 検証計画
- [ ] **実測**: 100並列実行でベンチマーク
- [ ] **障害テスト**: ネットワーク切断時の動作確認
- [ ] **コスト測定**: セットアップ時間、運用工数を測定

### 7. ロールバック計画
もし選択が誤りだった場合:
1. SQLite実装は維持（フォールバック可能）
2. データマイグレーションスクリプト準備
3. 1週間以内に切り戻し可能
```

#### チェックリスト

- [ ] **仮説→検証→結果→解釈**: この順序で思考
- [ ] **複数オプション**: 最低3つのオプション検討
- [ ] **定量評価**: 可能な限り数値で評価
- [ ] **トレードオフ明記**: メリット/デメリット両方記述
- [ ] **検証計画**: 決定の妥当性を検証する方法を明記
- [ ] **ロールバック計画**: 失敗時の対策を事前準備
- [ ] **感情排除**: "好き/嫌い"ではなく根拠で決定

---

### 1.5 安全性の確保ルール

#### 原則
**Secrets、PII、危険な操作**を適切に管理し、システムとデータを保護する。

#### 実装例

```python
# security/secrets_manager.py
import os
from typing import Optional
from cryptography.fernet import Fernet

class SecretsManager:
    """秘密情報管理"""
    
    def __init__(self):
        # 環境変数からのみ読み込み
        self.encryption_key = os.getenv("ENCRYPTION_KEY")
        if not self.encryption_key:
            raise ValueError("ENCRYPTION_KEY not set in environment")
        
        self.cipher = Fernet(self.encryption_key.encode())
    
    def get_secret(self, key: str) -> Optional[str]:
        """秘密情報を取得"""
        # ✅ 環境変数から取得
        value = os.getenv(key)
        
        # ❌ ファイルからは読まない（漏洩リスク）
        # ❌ コードにハードコードしない
        
        return value
    
    def encrypt(self, plaintext: str) -> bytes:
        """暗号化"""
        return self.cipher.encrypt(plaintext.encode())
    
    def decrypt(self, ciphertext: bytes) -> str:
        """復号化"""
        return self.cipher.decrypt(ciphertext).decode()


# ❌ 悪い例: ハードコード
DB_PASSWORD = "my_secret_password"  # 絶対にダメ！

# ✅ 良い例: 環境変数
DB_PASSWORD = os.getenv("DB_PASSWORD")
if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD not set")
```

```python
# security/pii_filter.py
import re
from typing import Any, Dict

class PIIFilter:
    """個人情報フィルター"""
    
    # 検出パターン
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_PATTERN = re.compile(r'\b\d{3}-\d{4}-\d{4}\b')
    CREDIT_CARD_PATTERN = re.compile(r'\b\d{4}-\d{4}-\d{4}-\d{4}\b')
    
    @classmethod
    def mask(cls, text: str) -> str:
        """PIIをマスク"""
        text = cls.EMAIL_PATTERN.sub('[EMAIL_MASKED]', text)
        text = cls.PHONE_PATTERN.sub('[PHONE_MASKED]', text)
        text = cls.CREDIT_CARD_PATTERN.sub('[CARD_MASKED]', text)
        return text
    
    @classmethod
    def filter_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """辞書からPIIを除外"""
        filtered = {}
        for key, value in data.items():
            if key.lower() in ['email', 'phone', 'ssn', 'credit_card']:
                filtered[key] = '[REDACTED]'
            elif isinstance(value, str):
                filtered[key] = cls.mask(value)
            else:
                filtered[key] = value
        return filtered


# 使用例
logger = StructuredLogger("app")

# ❌ 悪い例: PIIをそのままログ
logger.info("User registered", email="user@example.com")  # 危険！

# ✅ 良い例: PIIをフィルタ
user_data = {"email": "user@example.com", "name": "John Doe"}
filtered_data = PIIFilter.filter_dict(user_data)
logger.info("User registered", **filtered_data)  # email=[REDACTED]
```

```python
# security/safe_operations.py
import os
from pathlib import Path
from typing import Optional

class SafeFileOperations:
    """安全なファイル操作"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir).resolve()
    
    def validate_path(self, file_path: str) -> Path:
        """パストラバーサル攻撃を防ぐ"""
        requested_path = (self.base_dir / file_path).resolve()
        
        # ベースディレクトリ外へのアクセスを拒否
        if not str(requested_path).startswith(str(self.base_dir)):
            raise ValueError(f"Access denied: {file_path} is outside base directory")
        
        return requested_path
    
    def safe_delete(self, file_path: str, dry_run: bool = False) -> bool:
        """安全な削除（確認付き）"""
        validated_path = self.validate_path(file_path)
        
        if not validated_path.exists():
            return False
        
        if dry_run:
            print(f"[DRY-RUN] Would delete: {validated_path}")
            return True
        
        # 確認なしの削除は危険
        print(f"WARNING: About to delete: {validated_path}")
        confirmation = input("Type 'yes' to confirm: ")
        
        if confirmation.lower() == 'yes':
            os.remove(validated_path)
            return True
        else:
            print("Deletion cancelled")
            return False


# 使用例
safe_ops = SafeFileOperations("/data/experiments")

# ✅ 良い例: パス検証
try:
    safe_path = safe_ops.validate_path("exp_001/model.pt")
except ValueError as e:
    logger.error(f"Invalid path: {e}")

# ✅ 良い例: dry-run
safe_ops.safe_delete("exp_001/model.pt", dry_run=True)  # 実際には削除しない

# ✅ 良い例: 確認付き削除
safe_ops.safe_delete("exp_001/model.pt", dry_run=False)  # 確認を求める
```

#### チェックリスト

- [ ] **Secrets**: 環境変数でのみ管理（`.env`ファイル使用）
- [ ] **PII除外**: ログ、メトリクスから個人情報を除外
- [ ] **パス検証**: パストラバーサル攻撃を防ぐ
- [ ] **確認ガード**: 危険な操作には確認を求める
- [ ] **dry-run**: 破壊的操作にはdry-runモード実装
- [ ] **backup**: 削除前にバックアップ
- [ ] **roll-back**: 失敗時のロールバック手順準備
- [ ] **監査ログ**: すべての重要操作を記録

---

### 1.6 ミスコミュニケーション防止ルール

#### 原則
**要件、制約、受入基準、デリバラブル**を最初に明確化し、認識のズレを防ぐ。

#### コミュニケーションテンプレート

```markdown
## タスク定義テンプレート

### 1. 要件 (Requirements)
**何を作るのか？**

- 機能: ユーザーがデータをアップロードし、時系列予測を実行できる
- 入力: CSV形式、列 `date`, `unique_id`, `y`
- 出力: 予測結果CSV、メトリクスJSON

### 2. 制約 (Constraints)
**何ができないのか？制限は？**

- 時間: 2週間以内に完成
- リソース: 単一GPU（NVIDIA RTX 4090）
- 互換性: Python 3.11以上、NeuralForecast 1.7.x
- セキュリティ: ユーザーデータは外部送信しない

### 3. 受入基準 (Acceptance Criteria)
**どうなったら完成か？**

- [ ] ユーザーがWebUIからCSVをアップロードできる
- [ ] アップロード後、自動的に予測が開始される
- [ ] 予測完了後、結果CSVをダウンロードできる
- [ ] メトリクス（MAE, RMSE）が画面表示される
- [ ] テストカバレッジ >90%
- [ ] Pylintスコア ≥8.5
- [ ] ドキュメント完備（README、API docstring）

### 4. デリバラブル (Deliverables)
**何を納品するのか？**

- [ ] Webアプリケーション（Streamlit）
  - `src/ui/app.py`
- [ ] バックエンドAPI（FastAPI）
  - `src/api/endpoints.py`
- [ ] テストコード
  - `tests/unit/test_api.py`
  - `tests/integration/test_ui.py`
- [ ] ドキュメント
  - `docs/USER_GUIDE.md`
  - `docs/API_REFERENCE.md`
- [ ] デプロイスクリプト
  - `scripts/deploy.sh`

### 5. 依存関係 (Dependencies)
**このタスクは何に依存しているか？**

- データパイプライン実装完了 (Task #42)
- モデルレジストリ実装完了 (Task #57)
- PostgreSQLセットアップ完了 (Task #12)

### 6. 担当 (Ownership)
**誰が何をするのか？**

| Role | 担当者 | 責任 |
|------|--------|------|
| **R (Responsible)** | Alice | 実装・テスト作成 |
| **A (Accountable)** | Bob | レビュー・承認 |
| **C (Consulted)** | Charlie | アーキテクチャ相談 |
| **I (Informed)** | Team | 進捗報告 |

### 7. スケジュール (Schedule)
**いつまでに何をするか？**

| 日付 | マイルストーン |
|------|--------------|
| 2025-11-05 | 要件確認・設計書レビュー |
| 2025-11-08 | バックエンドAPI実装完了 |
| 2025-11-12 | WebUI実装完了 |
| 2025-11-15 | テスト完了、ドキュメント作成 |
| 2025-11-18 | 最終レビュー、デプロイ |

### 8. リスク (Risks)
**何が問題になり得るか？**

| リスク | 影響度 | 対策 |
|--------|--------|------|
| NeuralForecastのバグ | High | 代替ライブラリ(Prophet)準備 |
| GPUメモリ不足 | Medium | バッチサイズ削減 |
| CSVパースエラー | Low | エラーハンドリング実装 |
```

#### チェックリスト

- [ ] **要件明確化**: 何を作るか明文化
- [ ] **制約明記**: 何ができないか、制限を記載
- [ ] **受入基準**: チェックリスト形式で定義
- [ ] **デリバラブル**: 納品物を具体的にリスト
- [ ] **RACI明記**: 責任分担を明確化
- [ ] **スケジュール**: マイルストーンを日付で定義
- [ ] **リスク管理**: 潜在的問題と対策を事前検討

---

### 1.7 エラー処理ルール

#### 原則
エラーは**切り分け→再現→最小化→仮説→検証→恒久対策**の順で対処する。

#### エラー対応フレームワーク

```markdown
## エラー対応テンプレート

### 1. 事実の記録 (Facts)
**何が起きたか？**

- **症状**: モデル学習時に `CUDA out of memory` エラー
- **エラーメッセージ**:
  ```
  RuntimeError: CUDA out of memory. Tried to allocate 2.00 GiB 
  (GPU 0; 23.70 GiB total capacity; 20.50 GiB already allocated; 
  1.50 GiB free; 21.00 GiB reserved in total by PyTorch)
  ```
- **発生時刻**: 2025-11-04 14:32:15
- **影響範囲**: AutoNHITS モデル学習のみ（他モデルは正常）
- **発生頻度**: 100% (10回中10回再現)

### 2. 環境情報 (Environment)
- Python: 3.11.5
- PyTorch: 2.1.0+cu121
- GPU: NVIDIA RTX 4090 (24GB)
- データサイズ: 100,000行 × 15列
- バッチサイズ: 32
- `input_size`: 168
- `h`: 24

### 3. 直近の変更 (Recent Changes)
- 昨日: データセットを10万行→20万行に変更
- 今朝: `input_size`を84→168に変更
- コードの変更: なし

### 4. 切り分け (Isolation)
**どこで問題が起きているか？**

#### テスト1: データサイズを半分に
```bash
# 10万行で実行
python src/train.py --data data/train_small.csv
# 結果: 成功 ✅
```

#### テスト2: `input_size`を元に戻す
```bash
# input_size=84で実行
python src/train.py --input-size 84
# 結果: 成功 ✅
```

#### テスト3: バッチサイズを半分に
```bash
# batch_size=16で実行
python src/train.py --batch-size 16
# 結果: 失敗 ❌ (同じエラー)
```

**結論**: `input_size`を大きくしたことが原因

### 5. 再現の最小化 (Minimal Reproduction)
**最小限のコードで再現**

```python
# minimal_repro.py
import torch
from neuralforecast.models import AutoNHITS

# 最小限の設定
model = AutoNHITS(
    h=24,
    input_size=168,  # これが大きいと失敗
    max_steps=10
)

# ダミーデータ
X = torch.randn(32, 168, 1).cuda()  # batch_size=32, input_size=168
y = torch.randn(32, 24, 1).cuda()

# 学習
try:
    model.fit(X, y)
    print("✅ Success")
except RuntimeError as e:
    print(f"❌ Error: {e}")
```

### 6. 仮説 (Hypothesis)
**なぜ起きたか？**

| 仮説 | 確率 | 検証方法 |
|-----|------|---------|
| H1: `input_size`が大きすぎる | 90% | `input_size`を段階的に増やす |
| H2: モデルアーキテクチャが深すぎる | 5% | レイヤー数を減らす |
| H3: PyTorchのバグ | 5% | バージョンをダウングレード |

### 7. 検証 (Validation)
**仮説H1の検証**

```python
# test_input_size.py
import torch
from neuralforecast.models import AutoNHITS

def test_memory(input_size: int) -> bool:
    """指定のinput_sizeでメモリが足りるか確認"""
    try:
        model = AutoNHITS(h=24, input_size=input_size, max_steps=10)
        X = torch.randn(32, input_size, 1).cuda()
        y = torch.randn(32, 24, 1).cuda()
        model.fit(X, y)
        return True
    except RuntimeError:
        return False

# 二分探索で限界を見つける
for size in [84, 96, 112, 128, 144, 168]:
    result = test_memory(size)
    print(f"input_size={size}: {'✅' if result else '❌'}")
```

**結果**:
```
input_size=84: ✅
input_size=96: ✅
input_size=112: ✅
input_size=128: ✅
input_size=144: ❌
input_size=168: ❌
```

**結論**: `input_size > 128` でメモリ不足

### 8. 原因確定 (Root Cause)
`input_size`を168に設定したことで、モデルの中間層のメモリ使用量が増加し、24GBのGPUメモリを超過した。

**計算**:
- バッチサイズ: 32
- `input_size`: 168
- 中間層の次元: 512
- メモリ使用量: 32 × 168 × 512 × 4 bytes ≈ 11 MB (per layer)
- レイヤー数: 10
- 合計: 約110 MB (中間層のみ)
- その他（勾配、オプティマイザ状態）: 約2 GB
- **合計**: 約2.2 GB → これが複数バッチ分蓄積して24GBを超過

### 9. 対策 (Solution)

#### 暫定対策 (Temporary Fix)
```python
# すぐにできる対策
# input_sizeを128に制限
config.input_size = min(config.input_size, 128)
```

#### 恒久対策 (Permanent Fix)
```python
# 1. Gradient Accumulation
model = AutoNHITS(
    h=24,
    input_size=168,
    batch_size=16,  # バッチサイズを半分に
    accumulate_grad_batches=2  # 勾配を2回分蓄積
)

# 2. Mixed Precision Training
model = AutoNHITS(
    h=24,
    input_size=168,
    precision=16  # FP16で学習
)

# 3. メモリ効率化
torch.cuda.empty_cache()  # 不要なメモリ解放
model = AutoNHITS(
    h=24,
    input_size=168,
    gradient_checkpointing=True  # メモリ節約
)
```

### 10. 検証 (Verification)
```python
# 恒久対策の動作確認
model = AutoNHITS(
    h=24,
    input_size=168,
    batch_size=16,
    accumulate_grad_batches=2,
    precision=16
)

X = torch.randn(10000, 168, 1)  # 大きなデータ
y = torch.randn(10000, 24, 1)

try:
    model.fit(X, y)
    print("✅ Fixed!")
except RuntimeError as e:
    print(f"❌ Still failing: {e}")
```

### 11. 予防策 (Prevention)
- [ ] メモリ使用量の監視ダッシュボード追加
- [ ] `input_size`の上限を設定ファイルで管理
- [ ] GPU メモリチェックを学習前に実行
- [ ] ドキュメントに推奨設定を記載
- [ ] 回帰テストに大規模データのケース追加

### 12. ドキュメント更新
```markdown
# docs/TROUBLESHOOTING.md

## メモリ不足エラー

### 症状
`RuntimeError: CUDA out of memory`

### 原因
`input_size`が大きすぎる、またはバッチサイズが大きすぎる

### 解決策
1. `input_size`を128以下に制限
2. バッチサイズを16に削減
3. Mixed Precision Trainingを有効化 (`precision=16`)
4. Gradient Accumulation を使用
```
```

#### チェックリスト

- [ ] **事実記録**: エラーメッセージ、発生時刻、影響範囲
- [ ] **環境情報**: バージョン、設定、リソース
- [ ] **直近変更**: 何を変えたか明記
- [ ] **切り分け**: どこで問題が起きているか特定
- [ ] **最小再現**: 最小限のコードで再現
- [ ] **仮説列挙**: 複数の原因候補を考える
- [ ] **検証**: 仮説を実験で確認
- [ ] **原因確定**: 根本原因を特定
- [ ] **暫定対策**: すぐにできる対策
- [ ] **恒久対策**: 根本的な解決
- [ ] **予防策**: 再発防止
- [ ] **ドキュメント**: 他者が参照できるよう記録

---

### 1.8 出力契約ルール

#### 原則
**JSON/YAMLなどの固定スキーマ**を守り、曖昧な表現を避ける。数値には単位と信頼区間を付ける。

#### 出力スキーマ定義

```python
# schemas/output_schema.py
from dataclasses import dataclass
from typing import Dict, List, Optional
import json

@dataclass
class MetricValue:
    """メトリクス値（単位と信頼区間付き）"""
    value: float
    unit: str  # "seconds", "MB", "percent", etc.
    confidence_interval_lower: Optional[float] = None
    confidence_interval_upper: Optional[float] = None
    
    def __str__(self) -> str:
        if self.confidence_interval_lower and self.confidence_interval_upper:
            return (
                f"{self.value:.3f} {self.unit} "
                f"(95% CI: [{self.confidence_interval_lower:.3f}, "
                f"{self.confidence_interval_upper:.3f}])"
            )
        return f"{self.value:.3f} {self.unit}"


@dataclass
class ExperimentResult:
    """実験結果の標準出力形式"""
    
    # 必須フィールド
    run_id: str
    experiment_name: str
    status: str  # "success", "failed", "running"
    
    # メトリクス（単位付き）
    metrics: Dict[str, MetricValue]
    
    # アーティファクト（パス）
    artifacts: List[str]
    
    # リスク
    risks: List[str]
    
    # 次のアクション
    next_actions: List[str]
    
    # オーナー
    owners: Dict[str, str]  # {"R": "Alice", "A": "Bob"}
    
    def to_json(self) -> str:
        """JSON形式で出力"""
        data = {
            "run_id": self.run_id,
            "experiment_name": self.experiment_name,
            "status": self.status,
            "metrics": {
                name: {
                    "value": metric.value,
                    "unit": metric.unit,
                    "ci_lower": metric.confidence_interval_lower,
                    "ci_upper": metric.confidence_interval_upper
                }
                for name, metric in self.metrics.items()
            },
            "artifacts": self.artifacts,
            "risks": self.risks,
            "next_actions": self.next_actions,
            "owners": self.owners
        }
        return json.dumps(data, indent=2)


# 使用例
result = ExperimentResult(
    run_id="exp_001_run_042",
    experiment_name="AutoNHITS Hyperparameter Search",
    status="success",
    metrics={
        "mae": MetricValue(
            value=12.5,
            unit="units",
            confidence_interval_lower=11.2,
            confidence_interval_upper=13.8
        ),
        "training_time": MetricValue(
            value=3600.0,
            unit="seconds"
        ),
        "memory_peak": MetricValue(
            value=18.5,
            unit="GB"
        )
    },
    artifacts=[
        "mlflow://experiments/1/runs/abc123",
        "s3://bucket/models/exp_001_run_042/model.pt",
        "outputs/predictions.csv"
    ],
    risks=[
        "過学習の兆候（validation lossが増加）",
        "GPU メモリ使用率 90% 超（将来的なスケーラビリティ懸念）"
    ],
    next_actions=[
        "早期停止（Early Stopping）の実装",
        "Gradient Accumulation によるメモリ最適化",
        "回帰テストにこの設定を追加"
    ],
    owners={
        "R": "Alice",  # Responsible
        "A": "Bob",    # Accountable
        "C": "Charlie" # Consulted
    }
)

# JSON出力
print(result.to_json())
```

**出力例**:

```json
{
  "run_id": "exp_001_run_042",
  "experiment_name": "AutoNHITS Hyperparameter Search",
  "status": "success",
  "metrics": {
    "mae": {
      "value": 12.5,
      "unit": "units",
      "ci_lower": 11.2,
      "ci_upper": 13.8
    },
    "training_time": {
      "value": 3600.0,
      "unit": "seconds",
      "ci_lower": null,
      "ci_upper": null
    },
    "memory_peak": {
      "value": 18.5,
      "unit": "GB",
      "ci_lower": null,
      "ci_upper": null
    }
  },
  "artifacts": [
    "mlflow://experiments/1/runs/abc123",
    "s3://bucket/models/exp_001_run_042/model.pt",
    "outputs/predictions.csv"
  ],
  "risks": [
    "過学習の兆候（validation lossが増加）",
    "GPU メモリ使用率 90% 超（将来的なスケーラビリティ懸念）"
  ],
  "next_actions": [
    "早期停止（Early Stopping）の実装",
    "Gradient Accumulation によるメモリ最適化",
    "回帰テストにこの設定を追加"
  ],
  "owners": {
    "R": "Alice",
    "A": "Bob",
    "C": "Charlie"
  }
}
```

#### チェックリスト

- [ ] **スキーマ定義**: JSON/YAMLスキーマを明確に定義
- [ ] **単位明記**: すべての数値に単位を付ける
- [ ] **信頼区間**: 統計値には95%信頼区間を付ける
- [ ] **曖昧語排除**: "良い"、"速い"などの主観的表現を避ける
- [ ] **具体的表現**: "約50%高速" → "実測1.53倍高速（3600秒→2350秒）"
- [ ] **バージョン管理**: スキーマにバージョン番号を付ける

---

## 2. 品質保証の原則

### 2.1 品質保証の8つの柱

本プロジェクトは、以下の8つの品質属性を最優先します：

| 品質属性 | 目標評価 | 実現方法 | 測定方法 |
|---------|---------|---------|---------|
| **1. Reusability** | ⭐⭐⭐⭐⭐ | レイヤー化、Adapter Pattern | コード重複率 <3% |
| **2. Testability** | ⭐⭐⭐⭐⭐ | DI、純粋関数、モック | カバレッジ >90% |
| **3. Maintainability** | ⭐⭐⭐⭐⭐ | SOLID原則、ドキュメント | Pylint ≥8.5 |
| **4. Extensibility** | ⭐⭐⭐⭐⭐ | プラグイン設計、Factory | 新機能追加工数 |
| **5. Reliability** | ⭐⭐⭐⭐ | エラーハンドリング、リトライ | MTBF >720h |
| **6. Performance** | ⭐⭐⭐⭐ | 並列化、キャッシング | 単一モデル <10分 |
| **7. Security** | ⭐⭐⭐⭐ | 環境変数管理、PII除外 | Bandit スキャン |
| **8. Compatibility** | ⭐⭐⭐⭐⭐ | Adapter、バージョン管理 | 互換性テスト |

---

### 2.2 品質ゲート (Quality Gates)

各フェーズで以下の品質ゲートをクリアする必要があります：

#### Phase 1-9 共通ゲート

| 項目 | 基準 | ツール |
|-----|------|--------|
| **テストカバレッジ** | >90% | pytest-cov |
| **静的解析** | Pylint ≥8.5 | pylint |
| **型チェック** | MyPy strict pass | mypy |
| **フォーマット** | Black準拠 | black |
| **循環的複雑度** | <10 | radon |
| **重複コード** | <3% | pylint |
| **ドキュメント** | 100% | interrogate |
| **セキュリティ** | 高リスク問題0件 | bandit |

#### フェーズ別追加ゲート

| Phase | 追加基準 |
|-------|---------|
| Phase 2 | データ検証テスト100%パス |
| Phase 4 | 並列実行テスト成功 |
| Phase 6 | MLflow/W&B統合テスト成功 |
| Phase 8 | パフォーマンステスト基準達成 |
| Phase 9 | セキュリティレビュー完了 |

---

### 2.3 品質測定の自動化

```python
# scripts/quality_check.py
import subprocess
import json
from typing import Dict, Any

class QualityChecker:
    """品質チェック自動化"""
    
    def __init__(self, source_dir: str = "nf_auto_runner"):
        self.source_dir = source_dir
        self.results: Dict[str, Any] = {}
    
    def check_coverage(self) -> float:
        """テストカバレッジチェック"""
        result = subprocess.run(
            ["pytest", "--cov=" + self.source_dir, "--cov-report=json"],
            capture_output=True,
            text=True
        )
        
        with open("coverage.json") as f:
            data = json.load(f)
        
        coverage = data["totals"]["percent_covered"]
        self.results["coverage"] = coverage
        return coverage
    
    def check_pylint(self) -> float:
        """Pylintスコアチェック"""
        result = subprocess.run(
            ["pylint", self.source_dir, "--output-format=json"],
            capture_output=True,
            text=True
        )
        
        data = json.loads(result.stdout)
        score = 10.0 - (len(data) * 0.1)  # 簡易計算
        self.results["pylint"] = score
        return score
    
    def check_mypy(self) -> bool:
        """MyPy型チェック"""
        result = subprocess.run(
            ["mypy", self.source_dir, "--strict"],
            capture_output=True,
            text=True
        )
        
        passed = result.returncode == 0
        self.results["mypy"] = "pass" if passed else "fail"
        return passed
    
    def check_complexity(self) -> float:
        """循環的複雑度チェック"""
        result = subprocess.run(
            ["radon", "cc", self.source_dir, "-a", "-j"],
            capture_output=True,
            text=True
        )
        
        data = json.loads(result.stdout)
        avg_complexity = sum(
            item["complexity"] for item in data.values()
        ) / len(data)
        
        self.results["complexity"] = avg_complexity
        return avg_complexity
    
    def check_all(self) -> Dict[str, Any]:
        """すべてのチェックを実行"""
        coverage = self.check_coverage()
        pylint_score = self.check_pylint()
        mypy_passed = self.check_mypy()
        complexity = self.check_complexity()
        
        # 品質ゲート判定
        passed = (
            coverage > 90.0 and
            pylint_score >= 8.5 and
            mypy_passed and
            complexity < 10.0
        )
        
        self.results["overall"] = "PASS" if passed else "FAIL"
        
        return self.results
    
    def print_report(self):
        """レポート出力"""
        print("=" * 60)
        print("Quality Check Report")
        print("=" * 60)
        print(f"Coverage:    {self.results['coverage']:.1f}% {'✅' if self.results['coverage'] > 90 else '❌'}")
        print(f"Pylint:      {self.results['pylint']:.1f}/10 {'✅' if self.results['pylint'] >= 8.5 else '❌'}")
        print(f"MyPy:        {self.results['mypy']} {'✅' if self.results['mypy'] == 'pass' else '❌'}")
        print(f"Complexity:  {self.results['complexity']:.1f} {'✅' if self.results['complexity'] < 10 else '❌'}")
        print("=" * 60)
        print(f"Overall:     {self.results['overall']} {'✅' if self.results['overall'] == 'PASS' else '❌'}")
        print("=" * 60)


# 使用例
if __name__ == "__main__":
    checker = QualityChecker()
    results = checker.check_all()
    checker.print_report()
    
    # 品質ゲート失敗時はCI失敗
    if results["overall"] != "PASS":
        exit(1)
```

---

## 3. 開発プロセスとPDCA

### 3.1 PDCAサイクル

すべての開発タスクは、以下のPDCAサイクルに従います：

```
┌─────────────────────────────────────────────────────────┐
│  P (Plan): 目的・KPI・制約・受入基準 → 実験設計        │
│  - 何を達成するのか明確化                                │
│  - 仮説を立てる                                          │
│  - 検証方法を設計                                        │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ↓
┌─────────────────────────────────────────────────────────┐
│  D (Do): 手順（再現可能）、実行ログ、アーティファクト │
│  - 実装・実験を実行                                      │
│  - すべてのステップを記録                                │
│  - アーティファクトを保存                                │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ↓
┌─────────────────────────────────────────────────────────┐
│  C (Check): 結果（指標・統計・費用・CO₂）、差分解釈    │
│  - メトリクスを測定                                      │
│  - 仮説と結果を比較                                      │
│  - 差分を解釈                                            │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ↓
┌─────────────────────────────────────────────────────────┐
│  A (Act): 恒久対策・ADR要否・次の反復                   │
│  - 問題があれば恒久対策                                  │
│  - 重要な決定はADR記録                                   │
│  - 次のサイクルへ                                        │
└─────────────────────────────────────────────────────────┘
```

---

### 3.2 PDCA実践例

```markdown
## PDCA実践: AutoNHITS vs Prophet 性能比較

### P (Plan): 計画

#### 目的
AutoNHITS と Prophet の予測精度を比較し、どちらを採用すべきか決定する

#### KPI
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- 学習時間
- 予測時間

#### 制約
- 予算: 3日以内に完了
- リソース: 単一GPU（RTX 4090）
- データ: Air Passengers データセット（144ヶ月）

#### 受入基準
- [ ] 両モデルで同じデータセット使用
- [ ] 同じ評価指標で比較
- [ ] 統計的有意差を検証（t検定）
- [ ] 5回の独立実行で平均・標準偏差を計算

#### 実験設計
- **対照群**: Prophet（ベースライン）
- **実験群**: AutoNHITS
- **測定指標**: MAE, RMSE, 学習時間, 予測時間
- **交差検証**: Time Series Split (5 folds)

---

### D (Do): 実行

#### 実行手順

```bash
# 1. 環境準備
pip install neuralforecast==1.7.2 prophet==1.1.5

# 2. データ準備
python scripts/prepare_data.py --dataset air_passengers --output data/

# 3. Prophet実行
python src/run_experiment.py \
    --model prophet \
    --data data/air_passengers.csv \
    --output outputs/prophet/ \
    --n-runs 5

# 4. AutoNHITS実行
python src/run_experiment.py \
    --model auto_nhits \
    --data data/air_passengers.csv \
    --output outputs/auto_nhits/ \
    --n-runs 5
```

#### 実行ログ

```json
{
  "experiment_id": "exp_model_comparison_001",
  "timestamp": "2025-11-04T10:00:00Z",
  "models": ["prophet", "auto_nhits"],
  "data": {
    "source": "data/air_passengers.csv",
    "hash": "a3f5c9d8...",
    "n_samples": 144
  },
  "runs": [
    {
      "run_id": "prophet_run_001",
      "model": "prophet",
      "mae": 24.5,
      "rmse": 32.1,
      "train_time_sec": 12.3,
      "predict_time_sec": 0.8
    },
    // ... 省略 ...
  ]
}
```

#### アーティファクト
- `outputs/prophet/model_{1-5}.pkl`
- `outputs/auto_nhits/model_{1-5}.pt`
- `outputs/metrics.csv`
- `mlflow://experiments/model_comparison_001`

---

### C (Check): 確認

#### 結果

| モデル | MAE | RMSE | 学習時間 (秒) | 予測時間 (秒) |
|--------|-----|------|--------------|--------------|
| **Prophet** | 24.5±2.1 | 32.1±2.8 | 12.3±1.5 | 0.8±0.1 |
| **AutoNHITS** | 18.7±1.6 | 25.4±2.1 | 45.2±3.7 | 0.3±0.05 |

**差分**:
- MAE: 23.7% 改善 (24.5 → 18.7)
- RMSE: 20.9% 改善 (32.1 → 25.4)
- 学習時間: 3.7倍遅い (12.3 → 45.2)
- 予測時間: 2.7倍速い (0.8 → 0.3)

#### 統計的有意性

```python
from scipy import stats

prophet_mae = [24.5, 23.8, 25.2, 24.1, 24.9]
autohits_mae = [18.7, 19.2, 18.1, 19.0, 18.5]

t_stat, p_value = stats.ttest_ind(prophet_mae, autohits_mae)
print(f"t統計量: {t_stat:.3f}, p値: {p_value:.4f}")
# 結果: t統計量: 8.542, p値: 0.0003 → 有意差あり (p < 0.05)
```

#### 解釈
- AutoNHITS は Prophet より **有意に精度が高い** (p < 0.05)
- 学習時間は3.7倍だが、**許容範囲内** (45秒 vs 12秒)
- 予測時間は2.7倍速く、**本番運用で有利**

---

### A (Act): 改善

#### 恒久対策
- **決定**: AutoNHITS を採用
- **理由**: 精度が有意に高く、予測時間も速い

#### ADR (Architecture Decision Record)

```markdown
# ADR-004: AutoNHITSの採用

## ステータス
承認済み

## コンテキスト
時系列予測モデルの選定が必要

## 決定
AutoNHITS を採用

## 根拠
- MAE: 23.7% 改善
- RMSE: 20.9% 改善
- 統計的に有意 (p < 0.05)
- 予測時間は2.7倍速い

## 代替案
- Prophet: 精度でAutoNHITSに劣る
- ARIMA: 非線形パターンに弱い

## 影響
- 学習時間が3.7倍（許容範囲内）
- GPU必須
```

#### 次の反復
- [ ] AutoNHITSのハイパーパラメータ最適化
- [ ] 他のデータセットでも検証
- [ ] 本番環境でA/Bテスト
```

---

### 3.3 トラブルシュート時のPDCA

```markdown
## トラブルシュート: CUDA out of memory

### P (Plan): 計画

#### 問題
`CUDA out of memory` エラーが発生

#### 仮説
1. `input_size`が大きすぎる (確率 90%)
2. バッチサイズが大きすぎる (確率 5%)
3. PyTorchのバグ (確率 5%)

#### 検証計画
1. `input_size`を段階的に減らす
2. バッチサイズを半分にする
3. PyTorchをダウングレード

---

### D (Do): 実行

```bash
# 検証1: input_sizeを128に
python src/train.py --input-size 128
# 結果: 成功 ✅

# 検証2: input_sizeを168、batch_size=16に
python src/train.py --input-size 168 --batch-size 16
# 結果: 失敗 ❌

# 検証3: Mixed Precision
python src/train.py --input-size 168 --precision 16
# 結果: 成功 ✅
```

---

### C (Check): 確認

#### 結果
- `input_size=128`: 成功
- `input_size=168 + batch_size=16`: 失敗
- `input_size=168 + precision=16`: 成功

#### 解釈
`input_size`が原因。Mixed Precision (FP16) でメモリ使用量を半減できた。

---

### A (Act): 改善

#### 恒久対策
```python
# config/model.py
@dataclass
class ModelConfig:
    input_size: int = 128  # デフォルトを128に変更
    precision: int = 16    # FP16を有効化
```

#### ドキュメント更新
```markdown
# docs/TROUBLESHOOTING.md

## CUDA out of memory

### 解決策
1. `input_size`を128以下に制限
2. Mixed Precision (`precision=16`) を有効化
3. Gradient Accumulation を使用
```

#### 回帰テスト追加
```python
# tests/test_memory.py
def test_large_input_size_with_fp16():
    """大きなinput_sizeでもFP16なら動作する"""
    model = AutoNHITS(input_size=168, precision=16)
    # テストコード...
```
```

---

# 第2部: Role別プロンプトテンプレート

## 4. リードエンジニアRole

### 4.1 Role定義

```markdown
## [Role]
あなたは本案件のリードエンジニア。資料（複数可）を読み込み、最適解へ到達するためのPDCAを設計・実行する。
```

### 4.2 Input形式

```markdown
## [Input]
- **資料**: <URL/本文/添付要約>
- **目的/KPI**: <定量指標と閾値>
- **制約**: <時間/資源/互換性/セキュリティ>
- **成果物**: <期待するファイル/スキーマ/ダッシュ/コード>
```

### 4.3 Task定義

```markdown
## [Task]
1) 目標/制約/受入基準の再掲
2) 既知ギャップと検証プラン
3) 実行計画（小さなバッチ、計測、ロールバック）
4) 実装/結果の要約
5) KPI評価と解釈
6) 次の一手（改善/追加検証/ADR要否）
```

### 4.4 Output形式 (JSON)

```json
{
  "goals": [
    "AutoNHITSとProphetの性能比較",
    "どちらを採用すべきか決定"
  ],
  "acceptance_criteria": [
    "両モデルで同じデータセット使用",
    "統計的有意差を検証（p < 0.05）",
    "5回の独立実行で平均・標準偏差を計算"
  ],
  "plan": [
    "Step 1: データ準備（Air Passengers）",
    "Step 2: Prophet実行（5回）",
    "Step 3: AutoNHITS実行（5回）",
    "Step 4: 統計的検定（t検定）",
    "Step 5: 結果解釈"
  ],
  "actions": [
    "Prophet学習完了（5回、平均MAE=24.5±2.1）",
    "AutoNHITS学習完了（5回、平均MAE=18.7±1.6）",
    "t検定実施（t=8.542, p=0.0003）"
  ],
  "findings": {
    "metrics": {
      "mae_improvement": "23.7%",
      "rmse_improvement": "20.9%",
      "training_time_ratio": "3.7x slower",
      "prediction_time_ratio": "2.7x faster",
      "statistical_significance": "p=0.0003 (有意)"
    },
    "artifacts": [
      "outputs/prophet/model_{1-5}.pkl",
      "outputs/auto_nhits/model_{1-5}.pt",
      "mlflow://experiments/model_comparison_001"
    ]
  },
  "risks": [
    "AutoNHITSは学習時間が3.7倍（45秒 vs 12秒）",
    "GPU必須（本番環境でGPU調達が必要）"
  ],
  "next": [
    "AutoNHITSのハイパーパラメータ最適化",
    "他のデータセットでも検証",
    "ADR-004記録（AutoNHITS採用決定）"
  ]
}
```

### 4.5 使用例

```markdown
## 入力

[Role]
あなたは本案件のリードエンジニア。

[Input]
- **資料**: Time_Series_Forecasting_System_Requirements_Specification__First_Edition_.md
- **目的/KPI**: AutoNHITS vs Prophet の性能比較、MAE 20%改善
- **制約**: 3日以内、単一GPU（RTX 4090）
- **成果物**: 比較レポート（JSON形式）、ADR

[Task]
上記Inputに基づき、実験を設計・実行し、結果をJSON形式で出力してください。

---

## 出力（Claude）

```json
{
  "goals": [...],
  "acceptance_criteria": [...],
  "plan": [...],
  "actions": [...],
  "findings": {...},
  "risks": [...],
  "next": [...]
}
```
```

---

## 5. インシデント対応Role

### 5.1 Role定義

```markdown
## [Role]
あなたはインシデント指揮担当。障害を冷静にトリアージし、T+15分初動/T+60分暫定復旧を目標に導く。
```

### 5.2 Input形式

```markdown
## [Input]
- **症状/指標**: <p95, error_rate, coverage 乖離 等>
- **直近変更**: <デプロイ/設定/DDL/外部依存>
- **影響範囲**: <API/バッチ/スライス/顧客>
- **ログ/Run**: <リンクまたは抜粋>
```

### 5.3 Task定義

```markdown
## [Task]
1) Severity 評価（P1〜P4）
2) 暫定緩和（A/B比率/ベースライン/遮断/スロットリング）
3) 切り分け決定木（データ/モデル/インフラ）
4) 再現最小化→仮説→検証（エビデンス添付）
5) 暫定復旧案 / 恒久対策案
```

### 5.4 Output形式 (Markdown)

```markdown
### 初動
- **Severity**: P1 (Critical)
- **緩和**: モデルv2.0を即座にロールバック→v1.9に切り替え

### 切り分け/検証
- **仮説**: v2.0のinput_size増加がメモリ不足を引き起こした
- **検証結果**: `input_size=168`で`CUDA out of memory`エラー再現（100%）

### 暫定復旧 / 恒久対策
- **暫定**: v1.9へロールバック完了（T+10分）
- **恒久**: Mixed Precision (FP16) 実装、input_size上限を128に設定
```

### 5.5 使用例

```markdown
## 入力

[Role]
あなたはインシデント指揮担当。

[Input]
- **症状/指標**: 本番環境でモデル学習が100%失敗、`CUDA out of memory`エラー
- **直近変更**: 昨日、モデルv2.0デプロイ（input_sizeを84→168に変更）
- **影響範囲**: 全ユーザーのモデル学習が停止
- **ログ/Run**: `mlflow://experiments/prod/runs/xyz789`

[Task]
上記Inputに基づき、初動対応から恒久対策まで指示してください。

---

## 出力（Claude）

### 初動
- **Severity**: P1 (Critical) - 全ユーザー影響
- **緩和**: 即座にv1.9へロールバック

(以下、詳細...)
```

---

## 6. 仕様分析Role

### 6.1 Role定義

```markdown
## System
一次情報を優先し、用語/数式/閾値/前提を抽出。曖昧語を定義し、齟齬点を列挙。
```

### 6.2 Input形式

```markdown
## User
- **入力資料**: <本文/URL/添付要約>
- **期待**: 用語定義 / 仕様抜粋 / 未確定事項 / アクション
```

### 6.3 Output形式 (Markdown)

```markdown
### 用語/定義
- **AutoNHITS**: NeuralForecastのモデル、階層的補間で季節性・トレンドを自動検出
- **input_size**: 入力時系列の長さ（デフォルト84、推奨≤128）

### 仕様の核（数式/閾値/契約）
- MAE (Mean Absolute Error): `Σ|y_true - y_pred| / n`
- 閾値: MAE < 20 units, RMSE < 30 units

### 矛盾・未確定
- ドキュメントにinput_sizeの上限が明記されていない
- メモリ使用量の計算式が不明

### アクション（担当/RACI/期限）
- [ ] **担当**: Alice (R), Bob (A)
- [ ] **期限**: 2025-11-10
- [ ] **内容**: input_size上限を実測し、ドキュメント更新
```

### 6.4 使用例

```markdown
## 入力

System: 一次情報を優先し、用語/数式/閾値/前提を抽出。

User:
- **入力資料**: https://nixtlaverse.nixtla.io/neuralforecast/models.nhits.html
- **期待**: AutoNHITSの仕様を抽出、未確定事項を列挙

---

## 出力（Claude）

### 用語/定義
- **AutoNHITS**: ...

(以下、詳細...)
```

---

## 7. 環境チェックRole

### 7.1 Role定義

```markdown
## System
実行環境/依存/Secrets/接続先/権限/バージョンを点検し、リスクを列挙。
```

### 7.2 Input形式

```markdown
## User
対象タスク/ノード情報/必要リソース
```

### 7.3 Output形式 (JSON)

```json
{
  "os": "Ubuntu 22.04.3 LTS",
  "python": "3.11.5",
  "cuda": "12.1",
  "deps": {
    "neuralforecast": "1.7.2",
    "torch": "2.1.0",
    "pandas": "2.1.3"
  },
  "endpoints": [
    "postgresql://localhost:5432/mldb",
    "mlflow://localhost:5000"
  ],
  "risks": [
    "CUDA version mismatch（期待: 12.1, 実際: 11.8）",
    "PostgreSQL未起動"
  ],
  "checks": [
    "python --version",
    "nvidia-smi",
    "psql -U postgres -c 'SELECT version();'"
  ]
}
```

### 7.4 使用例

```markdown
## 入力

System: 実行環境を点検し、リスクを列挙。

User: AutoNHITS学習タスクの実行環境をチェックしてください。

---

## 出力（Claude）

```json
{
  "os": "Ubuntu 22.04.3 LTS",
  ...
}
```
```

---

## 8. コード生成Role

### 8.1 Role定義

```markdown
## System
最小API/型/Docstring/例外/ログ/計測/MLflow記録を必ず含む。
```

### 8.2 Input形式

```markdown
## User
要件/入出力/制約/対象モジュール
```

### 8.3 Output形式

- **コード**: 完全な実装
- **単体テスト**: pytest形式
- **使用例**: 実行可能なコード
- **MLflowロギング**: メトリクス記録

### 8.4 使用例

```markdown
## 入力

System: 最小API/型/Docstring/例外/ログ/計測/MLflow記録を必ず含む。

User:
- **要件**: データ検証クラス（DataValidator）を実装
- **入出力**: pd.DataFrame → ValidationResult
- **制約**: スキーマ検証、欠損値チェック、外れ値検出
- **対象モジュール**: `nf_auto_runner/data/validator.py`

---

## 出力（Claude）

```python
# nf_auto_runner/data/validator.py
from dataclasses import dataclass
from typing import List, Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """検証結果"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]

class DataValidator:
    """データ検証"""
    
    def __init__(self, required_columns: List[str]):
        self.required_columns = required_columns
    
    def validate(self, df: pd.DataFrame) -> ValidationResult:
        """
        データを検証する
        
        Args:
            df: 検証対象のDataFrame
        
        Returns:
            ValidationResult: 検証結果
        
        Raises:
            ValueError: dfがNoneの場合
        """
        if df is None:
            raise ValueError("df must not be None")
        
        errors = []
        warnings = []
        
        # スキーマ検証
        missing_cols = set(self.required_columns) - set(df.columns)
        if missing_cols:
            errors.append(f"Missing columns: {missing_cols}")
        
        # 欠損値チェック
        null_counts = df.isnull().sum()
        if null_counts.any():
            warnings.append(f"Null values found: {null_counts[null_counts > 0].to_dict()}")
        
        is_valid = len(errors) == 0
        
        logger.info(
            f"Validation completed",
            is_valid=is_valid,
            n_errors=len(errors),
            n_warnings=len(warnings)
        )
        
        return ValidationResult(is_valid, errors, warnings)


# tests/unit/data/test_validator.py
import pytest
import pandas as pd
from nf_auto_runner.data.validator import DataValidator, ValidationResult

def test_valid_data():
    """正常なデータの検証"""
    validator = DataValidator(required_columns=["date", "y"])
    df = pd.DataFrame({"date": ["2023-01-01"], "y": [100]})
    
    result = validator.validate(df)
    
    assert result.is_valid is True
    assert len(result.errors) == 0

def test_missing_column():
    """列欠損の検出"""
    validator = DataValidator(required_columns=["date", "y"])
    df = pd.DataFrame({"date": ["2023-01-01"]})  # "y"がない
    
    result = validator.validate(df)
    
    assert result.is_valid is False
    assert "Missing columns" in result.errors[0]

def test_null_values():
    """欠損値の検出"""
    validator = DataValidator(required_columns=["date", "y"])
    df = pd.DataFrame({"date": ["2023-01-01"], "y": [None]})
    
    result = validator.validate(df)
    
    assert result.is_valid is True  # 警告だけで通過
    assert len(result.warnings) > 0


# 使用例
if __name__ == "__main__":
    import mlflow
    
    mlflow.start_run()
    
    validator = DataValidator(required_columns=["date", "y"])
    df = pd.read_csv("data/train.csv")
    
    result = validator.validate(df)
    
    # MLflow記録
    mlflow.log_metric("is_valid", 1 if result.is_valid else 0)
    mlflow.log_metric("n_errors", len(result.errors))
    mlflow.log_metric("n_warnings", len(result.warnings))
    
    print(result)
    
    mlflow.end_run()
```
```

---

## 9. デバッグ&トラブルシュートRole

### 9.1 Role定義

```markdown
## System
再現→最小化→原因候補→検証計画→結果→恒久対策を1サイクルで。
```

### 9.2 Input形式

```markdown
## User
エラーメッセージ/ログ/環境差分/直近変更
```

### 9.3 Output形式 (Markdown)

```markdown
### 再現手順
```bash
python src/train.py --input-size 168
# エラー: RuntimeError: CUDA out of memory
```

### 最小再現
```python
import torch
X = torch.randn(32, 168, 1).cuda()
# エラー発生
```

### 原因候補（優先度順）
1. `input_size`が大きすぎる (確率 90%)
2. バッチサイズが大きすぎる (確率 5%)
3. PyTorchのバグ (確率 5%)

### 検証（コマンド/期待/結果）
```bash
# 検証1
python src/train.py --input-size 128
# 期待: 成功
# 結果: 成功 ✅
```

### 恒久対策
```python
# config/model.py
input_size: int = 128  # デフォルトを128に制限
precision: int = 16    # Mixed Precision有効化
```
```

---

## 10. テスト設計Role

### 10.1 Role定義

```markdown
## System
重要経路に対する Smoke/Contract Test を提示（入出力スキーマ固定）。
```

### 10.2 Input形式

```markdown
## User
対象機能/API 名/スキーマ
```

### 10.3 Output形式 (YAML)

```yaml
tests:
  - name: "学習パイプライン Smoke Test"
    preconditions:
      - "PostgreSQL起動"
      - "学習データ存在"
    steps:
      - "データ読み込み"
      - "モデル初期化"
      - "学習実行"
      - "メトリクス記録"
    expected:
      - "学習完了（エラーなし）"
      - "MAE < 50"
      - "MLflowにrun記録"
  
  - name: "予測API Contract Test"
    preconditions:
      - "モデルv1.9ロード"
    steps:
      - "POST /api/predict"
      - "Body: {\"data\": [[1,2,3]]}"
    expected:
      - "Status: 200"
      - "Body: {\"predictions\": [...]}"
      - "Schema: predictions is array of numbers"
```

---

## 11. 品質評価Role

### 11.1 Role定義

```markdown
## System
TEST_PLAN の合格基準に照らして合否を判定、ギャップの補完テストを提案。
```

### 11.2 Input形式

```markdown
## User
実測メトリクス/ログ/レポートリンク
```

### 11.3 Output形式 (Markdown)

```markdown
### 合否判定

| 項目 | 基準 | 実測 | 合否 |
|-----|------|------|------|
| カバレッジ | >90% | 92.3% | ✅ PASS |
| Pylint | ≥8.5 | 8.7 | ✅ PASS |
| MyPy | strict pass | 0 errors | ✅ PASS |
| 循環的複雑度 | <10 | 8.2 | ✅ PASS |

**Overall**: ✅ PASS

### 不足テスト

| 領域 | 現状カバレッジ | 不足ケース |
|-----|--------------|-----------|
| エラーハンドリング | 85% | ネットワークエラー時の挙動 |
| 並列実行 | 0% | 競合条件のテスト |

### 次アクション
- [ ] ネットワークエラーテスト追加
- [ ] 並列実行の統合テスト作成
```

---

# 第3部: 実践ガイド

## 12. 開発ワークフロー

### 12.1 日次ワークフロー

```markdown
## 朝（9:00-9:30）

### 1. 環境確認
```bash
# Git最新化
git pull origin main

# 環境確認
python scripts/check_environment.py

# 品質ゲート確認
pytest tests/ --cov=nf_auto_runner --cov-report=term-missing
pylint nf_auto_runner/
mypy nf_auto_runner/ --strict
```

### 2. 今日のタスク確認
```bash
# Issueを確認
gh issue list --assignee @me

# 今日のチェックリスト
cat checklists/phase_X_checklist.md
```

---

## 日中（9:30-18:00）

### 3. TDDサイクル
```bash
# Red: テストを書く
vim tests/unit/test_new_feature.py

# テスト実行（失敗確認）
pytest tests/unit/test_new_feature.py -v

# Green: 実装
vim nf_auto_runner/new_feature.py

# テスト実行（成功確認）
pytest tests/unit/test_new_feature.py -v

# Refactor: リファクタリング
black nf_auto_runner/new_feature.py
pylint nf_auto_runner/new_feature.py
```

### 4. コミット
```bash
# ステージング
git add tests/unit/test_new_feature.py
git add nf_auto_runner/new_feature.py

# コミット（Conventional Commits）
git commit -m "feat: add new feature for XYZ

- Implement NewFeature class
- Add unit tests (coverage: 95%)
- Update documentation

Closes #123"

# プッシュ
git push origin feature/new-feature
```

### 5. レビュー
```bash
# Pull Request作成
gh pr create --title "feat: add new feature for XYZ" \
             --body "## Changes\n- ..." \
             --base main \
             --head feature/new-feature
```

---

## 夕方（18:00-18:30）

### 6. 品質チェック
```bash
# 全テスト実行
pytest tests/ --cov=nf_auto_runner --cov-report=html

# レポート確認
open htmlcov/index.html

# 品質ゲート確認
python scripts/quality_check.py
```

### 7. 進捗更新
```markdown
# 進捗ログ更新
echo "## 2025-11-04" >> progress.md
echo "- [x] 新機能XYZ実装完了" >> progress.md
echo "- [x] テストカバレッジ 95%" >> progress.md
echo "- [ ] ドキュメント作成（明日）" >> progress.md
```

### 8. MLflow記録
```python
import mlflow

mlflow.start_run(run_name="daily_dev_2025-11-04")

mlflow.log_metric("tests_passed", 142)
mlflow.log_metric("coverage_percent", 95.3)
mlflow.log_metric("pylint_score", 8.7)
mlflow.log_metric("lines_of_code_added", 237)

mlflow.log_artifact("progress.md")

mlflow.end_run()
```
```

---

### 12.2 週次ワークフロー

```markdown
## 金曜（17:00-18:00）

### 1. 週次レビュー
```bash
# 今週のコミット確認
git log --since="1 week ago" --oneline

# 今週のPR確認
gh pr list --state merged --search "merged:>=2025-10-28"
```

### 2. 品質メトリクス集計
```bash
# 週次レポート生成
python scripts/weekly_report.py > reports/week_44.md
```

### 3. 次週計画
```markdown
# next_week.md
## 次週の目標（11/5 - 11/9）

### Phase 4完了
- [ ] 並列実行エンジン実装
- [ ] Ray統合
- [ ] パフォーマンステスト

### 品質目標
- [ ] カバレッジ >92%
- [ ] Pylintスコア ≥8.7
```

### 4. バックアップ
```bash
# 作業ブランチをリモートに
git push origin --all

# DBバックアップ
pg_dump mldb > backups/mldb_2025-11-01.sql
```
```

---

## 13. 品質チェックリスト

### 13.1 コード品質チェックリスト

#### 実装前
- [ ] 要件を再確認（何を作るのか明確か？）
- [ ] 設計書を確認（どう作るのか明確か？）
- [ ] テストケースを先に書く（TDD）
- [ ] 依存関係を確認（必要なライブラリは揃っているか？）

#### 実装中
- [ ] 型ヒントを付ける（すべての関数に）
- [ ] Docstringを書く（Args/Returns/Raises）
- [ ] ログを追加（主要経路に構造化ログ）
- [ ] エラーハンドリング（適切な例外を定義）
- [ ] 命名規則に従う（PEP 8準拠）

#### 実装後
- [ ] 単体テスト実行（pytest）
- [ ] カバレッジ確認（>90%）
- [ ] 静的解析（Pylint ≥8.5）
- [ ] 型チェック（MyPy strict pass）
- [ ] フォーマット（Black適用）
- [ ] 複雑度チェック（<10）
- [ ] ドキュメント更新（README、API reference）

---

### 13.2 テスト品質チェックリスト

#### 単体テスト
- [ ] 正常系テスト（Happy Path）
- [ ] 境界値テスト（Edge Cases）
- [ ] 異常系テスト（Error Cases）
- [ ] NULL/空テスト
- [ ] 型エラーテスト
- [ ] カバレッジ >90%

#### 統合テスト
- [ ] コンポーネント間の連携テスト
- [ ] データベース統合テスト
- [ ] 外部API統合テスト（モック使用）

#### E2Eテスト
- [ ] 主要ユースケースの動作確認
- [ ] パフォーマンステスト
- [ ] ロードテスト（並列実行）

---

### 13.3 セキュリティチェックリスト

- [ ] Secrets管理（環境変数のみ）
- [ ] PII除外（ログ、メトリクス）
- [ ] SQLインジェクション対策（パラメータ化クエリ）
- [ ] パストラバーサル対策（パス検証）
- [ ] 認証・認可（必要に応じて）
- [ ] Banditスキャン（高リスク問題0件）

---

### 13.4 パフォーマンスチェックリスト

- [ ] 単一モデル学習 <10分
- [ ] 100モデル並列 <2時間
- [ ] 予測レイテンシ <100ms
- [ ] メモリ使用 <16GB
- [ ] プロファイリング（cProfile）

---

## 14. ベストプラクティス集

### 14.1 命名規則

```python
# ✅ 良い例

# クラス: PascalCase
class DataValidator:
    pass

# 関数/メソッド: snake_case
def calculate_metrics():
    pass

# 変数: snake_case
input_size = 128

# 定数: UPPER_SNAKE_CASE
MAX_INPUT_SIZE = 168

# プライベート: 先頭にアンダースコア
def _internal_helper():
    pass

# 型変数: PascalCase
T = TypeVar('T')


# ❌ 悪い例

# クラス: snake_case（NG）
class data_validator:
    pass

# 関数: camelCase（NG）
def calculateMetrics():
    pass

# 定数: snake_case（NG）
max_input_size = 168
```

---

### 14.2 Docstring規約

```python
# ✅ 良い例

def calculate_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    metrics: List[str]
) -> Dict[str, float]:
    """
    評価指標を計算する
    
    Args:
        y_true (np.ndarray): 真の値、shape (n_samples,)
        y_pred (np.ndarray): 予測値、shape (n_samples,)
        metrics (List[str]): 計算する指標名のリスト
            例: ['mae', 'rmse', 'mape']
    
    Returns:
        Dict[str, float]: 指標名をキー、値をバリューとする辞書
            例: {'mae': 12.5, 'rmse': 18.3}
    
    Raises:
        ValueError: y_trueとy_predの長さが異なる場合
        ValueError: 未知の指標名が含まれる場合
    
    Examples:
        >>> y_true = np.array([1, 2, 3])
        >>> y_pred = np.array([1.1, 2.2, 2.9])
        >>> calculate_metrics(y_true, y_pred, ['mae'])
        {'mae': 0.1333}
    """
    pass


# ❌ 悪い例

def calculate_metrics(y_true, y_pred, metrics):
    """
    メトリクスを計算
    """
    # Docstringが不十分（Args/Returns/Raises/Examplesがない）
    pass
```

---

### 14.3 エラーハンドリング

```python
# ✅ 良い例

# カスタム例外定義
class DataValidationError(Exception):
    """データ検証エラー"""
    pass

class ModelNotFoundError(Exception):
    """モデルが見つからない"""
    pass


def load_model(model_id: str) -> Model:
    """
    モデルをロードする
    
    Raises:
        ModelNotFoundError: モデルが存在しない場合
    """
    if not model_exists(model_id):
        raise ModelNotFoundError(f"Model {model_id} not found")
    
    return Model.load(model_id)


# 使用側
try:
    model = load_model("model_123")
except ModelNotFoundError as e:
    logger.error(f"Failed to load model: {e}")
    # 適切な対処（フォールバック、再試行など）


# ❌ 悪い例

def load_model(model_id):
    if not model_exists(model_id):
        print("Model not found")  # NG: printではなくlogger使用
        return None  # NG: 例外を投げるべき
    
    return Model.load(model_id)
```

---

### 14.4 ロギング

```python
# ✅ 良い例

import logging
import json

logger = logging.getLogger(__name__)

def train_model(model_config: ModelConfig, data: pd.DataFrame):
    """モデルを学習する"""
    
    # 構造化ログ（JSON形式）
    logger.info(
        json.dumps({
            "event": "training_started",
            "model": model_config.model_name,
            "n_samples": len(data),
            "n_features": data.shape[1],
            "timestamp": time.time()
        })
    )
    
    try:
        # 学習処理
        model = Model(model_config)
        model.fit(data)
        
        logger.info(
            json.dumps({
                "event": "training_completed",
                "model": model_config.model_name,
                "duration_sec": 123.45,
                "final_loss": 0.123
            })
        )
    
    except Exception as e:
        logger.error(
            json.dumps({
                "event": "training_failed",
                "model": model_config.model_name,
                "error": str(e),
                "traceback": traceback.format_exc()
            })
        )
        raise


# ❌ 悪い例

def train_model(model_config, data):
    print("Training started")  # NG: printではなくlogger
    
    model = Model(model_config)
    model.fit(data)
    
    print("Training done")  # NG: 構造化されていない
```

---

### 14.5 依存性注入 (DI)

```python
# ✅ 良い例

class ModelTrainer:
    """モデル学習クラス（DI使用）"""
    
    def __init__(
        self,
        model_registry: ModelRegistry,  # 依存を外部から注入
        logger: StructuredLogger,
        metrics_tracker: MetricsTracker
    ):
        self.model_registry = model_registry
        self.logger = logger
        self.metrics_tracker = metrics_tracker
    
    def train(self, model_config: ModelConfig, data: pd.DataFrame):
        """学習実行"""
        model = self.model_registry.get_model(model_config.model_name)
        
        self.logger.info("Training started")
        model.fit(data)
        
        metrics = self.metrics_tracker.get_metrics()
        return model, metrics


# テスト時はモックを注入
def test_train():
    mock_registry = MockModelRegistry()
    mock_logger = MockLogger()
    mock_tracker = MockMetricsTracker()
    
    trainer = ModelTrainer(mock_registry, mock_logger, mock_tracker)
    # テスト...


# ❌ 悪い例

class ModelTrainer:
    """モデル学習クラス（DI不使用）"""
    
    def __init__(self):
        self.model_registry = ModelRegistry()  # NG: 内部でインスタンス化
        self.logger = StructuredLogger()
        self.metrics_tracker = MetricsTracker()
    
    # テストしにくい（モックに置き換えられない）
```

---

### 14.6 設定管理

```python
# ✅ 良い例

# config/config.py
from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class DatabaseConfig:
    """データベース設定"""
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    database: str = os.getenv("DB_NAME", "mldb")
    user: str = os.getenv("DB_USER", "postgres")
    password: str = os.getenv("DB_PASSWORD", "")  # 環境変数から
    
    def to_connection_string(self) -> str:
        """接続文字列を生成"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class ModelConfig:
    """モデル設定"""
    model_name: str = "AutoNHITS"
    input_size: int = 128
    h: int = 24
    precision: int = 16
    max_epochs: int = 100


# 使用例
db_config = DatabaseConfig()
conn_str = db_config.to_connection_string()


# ❌ 悪い例

# ハードコード（NG）
DB_HOST = "localhost"
DB_PASSWORD = "my_secret_password"  # 絶対ダメ！

# マジックナンバー（NG）
model = Model(input_size=128)  # 128の意味が不明
```

---

# 第4部: 付録

## 15. 用語集

| 用語 | 定義 |
|-----|------|
| **ADR** | Architecture Decision Record、設計判断の記録 |
| **CI/CD** | Continuous Integration / Continuous Deployment |
| **CUDA** | Compute Unified Device Architecture (NVIDIA GPU) |
| **DI** | Dependency Injection、依存性注入 |
| **E2E** | End-to-End、エンドツーエンド |
| **KPI** | Key Performance Indicator、主要業績評価指標 |
| **MAE** | Mean Absolute Error、平均絶対誤差 |
| **MLflow** | 機械学習実験管理プラットフォーム |
| **MTBF** | Mean Time Between Failures、平均故障間隔 |
| **MTTR** | Mean Time To Repair、平均修復時間 |
| **OOP** | Object-Oriented Programming、オブジェクト指向プログラミング |
| **PDCA** | Plan-Do-Check-Act、計画-実行-確認-改善 |
| **PII** | Personally Identifiable Information、個人識別情報 |
| **RACI** | Responsible-Accountable-Consulted-Informed |
| **RMSE** | Root Mean Squared Error、二乗平均平方根誤差 |
| **SOLID** | 5つのOOP設計原則（SRP, OCP, LSP, ISP, DIP） |
| **TDD** | Test-Driven Development、テスト駆動開発 |

---

## 16. 参考資料

### 16.1 公式ドキュメント

- **NeuralForecast**: https://nixtlaverse.nixtla.io/neuralforecast/
- **MLflow**: https://mlflow.org/docs/latest/index.html
- **PostgreSQL**: https://www.postgresql.org/docs/
- **pytest**: https://docs.pytest.org/
- **MyPy**: https://mypy.readthedocs.io/

### 16.2 設計原則

- **Clean Architecture**: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
- **SOLID Principles**: https://en.wikipedia.org/wiki/SOLID
- **Design Patterns**: https://refactoring.guru/design-patterns

### 16.3 書籍

- "Clean Code" by Robert C. Martin
- "Test Driven Development: By Example" by Kent Beck
- "Refactoring" by Martin Fowler

---

## 17. FAQ

### Q1: カバレッジが90%に達しない場合は？

**A**: まず、カバレッジが低い理由を分析します：

1. **エラーハンドリング不足**: 例外処理のブランチがテストされていない
2. **境界値テスト不足**: Edge Casesのテストがない
3. **統合テスト不足**: コンポーネント間の連携テストがない

対策：
- エラーケースのテストを追加
- `pytest-cov --cov-report=html` でカバーされていない行を確認
- 境界値テストを追加

---

### Q2: Pylintスコアが8.5に達しない場合は？

**A**: Pylintの警告を確認し、修正します：

```bash
# 警告を確認
pylint nf_auto_runner/ --output-format=colorized

# よくある警告と対策
# - C0103 (invalid-name): 変数名をsnake_caseに変更
# - R0913 (too-many-arguments): 引数を減らす、dataclassを使う
# - R0914 (too-many-locals): 関数を分割
# - C0114 (missing-module-docstring): モジュールDocstringを追加
```

---

### Q3: MyPy strictで型エラーが出る場合は？

**A**: 型ヒントを追加します：

```python
# ❌ 型エラー
def calculate(x):
    return x * 2

# ✅ 型ヒント追加
def calculate(x: float) -> float:
    return x * 2
```

---

### Q4: パフォーマンステストが基準に達しない場合は？

**A**: プロファイリングで遅い箇所を特定します：

```bash
# cProfileでプロファイリング
python -m cProfile -o output.prof src/train.py

# 結果を可視化
snakeviz output.prof
```

対策：
- 並列化（Dask, Ray）
- キャッシング
- GPU活用
- アルゴリズム最適化

---

### Q5: メモリ不足エラーが頻発する場合は？

**A**: メモリ使用量を削減します：

```python
# 対策1: バッチサイズを減らす
batch_size = 16  # 32 → 16

# 対策2: Mixed Precision (FP16)
precision = 16

# 対策3: Gradient Accumulation
accumulate_grad_batches = 2

# 対策4: メモリ解放
import torch
torch.cuda.empty_cache()
```

---

**End of Document**

---

**総ページ数**: 約300ページ相当  
**総文字数**: 約75,000文字  
**適用範囲**: 全開発フェーズ、全Role  
**最終更新**: 2025-11-04
