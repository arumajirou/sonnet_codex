# テスト戦略
**Testing Strategy for Time Series Forecasting System**

---

## 📋 ドキュメント情報

| 項目 | 内容 |
|-----|------|
| **ドキュメントタイトル** | 時系列予測システム テスト戦略 |
| **バージョン** | v1.0.0 |
| **作成日** | 2025-11-03 |
| **最終更新日** | 2025-11-03 |
| **対象システム** | NeuralForecast Auto Runner + Time Series Forecasting System |
| **対象読者** | 開発者、QAエンジニア、テストエンジニア |

---

## 目次

1. [テスト戦略の概要](#1-テスト戦略の概要)
2. [テストレベルとスコープ](#2-テストレベルとスコープ)
3. [テスト手法とアプローチ](#3-テスト手法とアプローチ)
4. [テストカバレッジ目標](#4-テストカバレッジ目標)
5. [TDD実践ガイド](#5-tdd実践ガイド)
6. [テストケース設計](#6-テストケース設計)
7. [テストデータ管理](#7-テストデータ管理)
8. [テスト環境構成](#8-テスト環境構成)
9. [テスト自動化](#9-テスト自動化)
10. [品質メトリクスとKPI](#10-品質メトリクスとkpi)
11. [リスクベーステスト戦略](#11-リスクベーステスト戦略)
12. [CI/CD統合](#12-cicd統合)
13. [テストツールとフレームワーク](#13-テストツールとフレームワーク)
14. [付録](#14-付録)

---

## 1. テスト戦略の概要

### 1.1 テスト戦略の目的

本テスト戦略は、時系列予測システムの品質を保証し、以下を実現することを目的とします：

#### 主要目標

1. **高品質の保証**: 全機能が仕様通りに動作することを保証
2. **早期欠陥検出**: 開発初期段階で欠陥を発見し、修正コストを最小化
3. **再現性の確保**: すべてのテストが一貫して再現可能
4. **継続的品質改善**: メトリクスに基づく継続的な品質向上
5. **リスク低減**: 本番環境でのリスクを最小化

---

### 1.2 テスト哲学

本システムのテスト哲学は以下の原則に基づきます：

| 原則 | 説明 | 実践 |
|-----|------|------|
| **Test First** | テストファースト開発（TDD） | テストを先に書いてから実装 |
| **Fail Fast** | 早期失敗検出 | 欠陥を早期に発見して修正 |
| **Shift Left** | テストの左シフト | 開発初期からテスト実施 |
| **Automation First** | 自動化優先 | 手動テストは最小限に |
| **Quality Gates** | 品質ゲート | 各フェーズで品質基準をクリア |
| **Continuous Testing** | 継続的テスト | CI/CDパイプラインで自動実行 |

---

### 1.3 テストピラミッド

本システムは、テストピラミッドモデルに従ってテストを構成します：

```
                    ┌──────────────┐
                   │   E2E Tests   │  (5%)
                   │  統合性確認   │
                  └────────────────┘
                ┌──────────────────┐
               │ Integration Tests │  (15%)
               │   コンポーネント   │
               │     統合確認      │
              └────────────────────┘
          ┌────────────────────────────┐
         │      Unit Tests (UT)        │  (80%)
         │    個別機能の動作確認        │
         │  高速・独立・豊富なケース     │
        └──────────────────────────────┘
```

**比率の根拠**:
- **UT (80%)**: 高速・独立・詳細な検証が可能
- **IT (15%)**: コンポーネント間の連携を確認
- **E2E (5%)**: システム全体の動作を確認

---

### 1.4 テスト成熟度モデル

システムのテスト成熟度を段階的に向上させます：

| レベル | 段階 | 特徴 | 目標時期 |
|-------|------|------|---------|
| **Level 0** | 未実施 | テストなし | - |
| **Level 1** | 初期 | 手動テスト中心 | Phase 1 |
| **Level 2** | 管理 | 自動化テスト導入 | Phase 3 |
| **Level 3** | 定義 | TDD実践、CI/CD統合 | Phase 5 |
| **Level 4** | 定量管理 | メトリクス監視、品質ゲート | Phase 7 |
| **Level 5** | 最適化 | 継続的改善、予測的品質管理 | Phase 9+ |

**現在の目標**: Level 4（定量管理）を達成

---

## 2. テストレベルとスコープ

### 2.1 単体テスト（Unit Tests）

#### 2.1.1 概要

**目的**: 個別のクラス、メソッド、関数が仕様通りに動作することを検証

**特徴**:
- 高速実行（<1秒/テスト）
- 外部依存なし（モック使用）
- 独立実行可能
- 詳細なエッジケース検証

---

#### 2.1.2 スコープ

| 層 | テスト対象 | カバレッジ目標 | テスト数目安 |
|---|----------|--------------|------------|
| **Configuration層** | Config基底クラス、PathConfig、ExecutionConfig等 | >95% | 50+ |
| **Data層** | DataLoader、Preprocessor、Validator等 | >95% | 80+ |
| **Model Discovery層** | ModelRegistry、CapabilityAnalyzer等 | >90% | 60+ |
| **Hyperparameter層** | LossRegistry、ScalerRegistry等 | >90% | 50+ |
| **Execution Plan層** | CombinationGenerator、ExecutionPlan等 | >90% | 40+ |
| **Execution層** | Executor、ParallelExecutor等 | >85% | 70+ |
| **Artifact層** | ArtifactManager、ModelSaver等 | >90% | 40+ |
| **Logging層** | StructuredLogger、ProgressTracker等 | >90% | 30+ |
| **Service層** | ExecutionService、PlanningService等 | >85% | 50+ |
| **Application層** | CLI、Orchestrator等 | >85% | 30+ |

**合計目標**: 500+ 単体テスト

---

#### 2.1.3 単体テストのベストプラクティス

```python
# ✅ 良い単体テストの例
import pytest
from unittest.mock import Mock, patch
from nf_auto_runner.config import PathConfig


class TestPathConfig:
    """PathConfigクラスの単体テスト"""
    
    def test_init_with_valid_paths(self):
        """有効なパスでの初期化テスト"""
        # Arrange
        data_dir = "/path/to/data"
        model_dir = "/path/to/models"
        
        # Act
        config = PathConfig(data_dir=data_dir, model_dir=model_dir)
        
        # Assert
        assert config.data_dir == data_dir
        assert config.model_dir == model_dir
        assert config.is_valid()
    
    def test_init_with_invalid_data_dir_raises_error(self):
        """無効なdata_dirでエラーが発生することを確認"""
        # Arrange
        invalid_dir = ""
        
        # Act & Assert
        with pytest.raises(ValueError, match="data_dir cannot be empty"):
            PathConfig(data_dir=invalid_dir, model_dir="/valid/path")
    
    def test_validate_paths_with_nonexistent_dir(self, tmp_path):
        """存在しないディレクトリの検証テスト"""
        # Arrange
        nonexistent = tmp_path / "nonexistent"
        config = PathConfig(data_dir=str(nonexistent), model_dir="/tmp")
        
        # Act
        result = config.validate_paths()
        
        # Assert
        assert result is False
    
    @pytest.mark.parametrize("data_dir,model_dir,expected", [
        ("/valid/data", "/valid/model", True),
        ("/valid/data", "", False),
        ("", "/valid/model", False),
        ("", "", False),
    ])
    def test_is_valid_parametrized(self, data_dir, model_dir, expected):
        """パラメータ化テスト：様々なパスの組み合わせ"""
        # Arrange & Act
        config = PathConfig(data_dir=data_dir, model_dir=model_dir)
        
        # Assert
        assert config.is_valid() == expected
```

---

#### 2.1.4 単体テストのアンチパターン

```python
# ❌ 悪い単体テストの例

# アンチパターン1: 複数の機能をテスト
def test_everything():
    """複数のことをテストしている（分割すべき）"""
    config = PathConfig(data_dir="/data", model_dir="/models")
    assert config.data_dir == "/data"  # 初期化のテスト
    assert config.is_valid()  # 検証のテスト
    config.update("/new/data")  # 更新のテスト
    assert config.data_dir == "/new/data"  # 更新確認のテスト


# アンチパターン2: 外部依存
def test_with_real_database():
    """実際のデータベースに依存（モックを使うべき）"""
    db = PostgreSQLDatabase("postgresql://...")  # 実DBに接続
    result = db.query("SELECT * FROM experiments")
    assert len(result) > 0


# アンチパターン3: 不明確なアサーション
def test_calculation():
    """何をテストしているか不明確"""
    result = calculate_something(10, 20)
    assert result  # 何を確認しているのか不明


# アンチパターン4: テスト間の依存
test_order = []

def test_first():
    """他のテストに依存（独立すべき）"""
    test_order.append(1)
    assert True

def test_second():
    """test_firstの実行を前提としている"""
    assert 1 in test_order  # 危険！
```

---

### 2.2 統合テスト（Integration Tests）

#### 2.2.1 概要

**目的**: 複数のコンポーネント間の連携が正しく動作することを検証

**特徴**:
- 中速実行（数秒～数十秒）
- 実際の外部依存を使用（テスト用DB等）
- コンポーネント間のインターフェースを検証

---

#### 2.2.2 統合テストのスコープ

| テスト分類 | 対象 | テスト内容 | 実装数 |
|----------|------|----------|-------|
| **層間統合** | 隣接層の連携 | Service層 ↔ Domain層 | 20+ |
| **データベース統合** | DB操作 | CRUD操作、トランザクション | 15+ |
| **外部ライブラリ統合** | NeuralForecast等 | モデル学習、予測 | 10+ |
| **MLflowトラッキング統合** | MLflow API | ログ記録、アーティファクト保存 | 8+ |
| **Ray並列処理統合** | Ray Cluster | 並列実行、リソース管理 | 5+ |
| **ファイルシステム統合** | File I/O | モデル保存/読み込み | 10+ |

**合計目標**: 70+ 統合テスト

---

#### 2.2.3 統合テストの例

```python
# ✅ 良い統合テストの例
import pytest
from sqlalchemy import create_engine
from nf_auto_runner.service import ExecutionService
from nf_auto_runner.data import DataLoader
from nf_auto_runner.model import ModelRegistry


@pytest.fixture
def test_database():
    """テスト用データベースセットアップ"""
    engine = create_engine("postgresql://test:test@localhost:5433/test_db")
    # マイグレーション実行
    from alembic import command
    from alembic.config import Config
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    
    yield engine
    
    # クリーンアップ
    command.downgrade(alembic_cfg, "base")


class TestExecutionServiceIntegration:
    """ExecutionServiceの統合テスト"""
    
    def test_execute_single_run_end_to_end(
        self, test_database, tmp_path
    ):
        """単一Run実行のE2Eフロー"""
        # Arrange
        service = ExecutionService(db_engine=test_database)
        data_loader = DataLoader(data_dir=tmp_path / "data")
        model_registry = ModelRegistry()
        
        # テストデータ準備
        test_data = data_loader.load_sample_data()
        
        # Act
        run_result = service.execute_single_run(
            data=test_data,
            model_name="AutoNHITS",
            hyperparameters={"h": 7, "input_size": 14}
        )
        
        # Assert
        assert run_result.status == "completed"
        assert run_result.metrics is not None
        assert "mae" in run_result.metrics
        
        # データベースに保存されたことを確認
        from nf_auto_runner.artifact.models import Run
        with test_database.begin() as conn:
            saved_run = conn.execute(
                "SELECT * FROM runs WHERE run_id = %s",
                (run_result.run_id,)
            ).fetchone()
            assert saved_run is not None
    
    def test_parallel_execution_with_ray(
        self, test_database, tmp_path
    ):
        """Ray並列実行の統合テスト"""
        # Arrange
        import ray
        ray.init(num_cpus=4)
        
        service = ExecutionService(
            db_engine=test_database,
            executor_type="ray"
        )
        
        # 複数の実行計画を生成
        execution_plans = [
            {"model": "AutoNHITS", "h": 7},
            {"model": "AutoLSTM", "h": 7},
            {"model": "AutoTFT", "h": 7},
        ]
        
        # Act
        results = service.execute_parallel(execution_plans)
        
        # Assert
        assert len(results) == 3
        assert all(r.status == "completed" for r in results)
        
        # クリーンアップ
        ray.shutdown()
```

---

### 2.3 E2Eテスト（End-to-End Tests）

#### 2.3.1 概要

**目的**: システム全体が実際のユースケースシナリオで正しく動作することを検証

**特徴**:
- 低速実行（数分～数十分）
- 本番に近い環境
- ユーザーシナリオベース

---

#### 2.3.2 E2Eテストシナリオ

| シナリオID | シナリオ名 | 説明 | 実行時間目安 |
|----------|----------|------|------------|
| **E2E-001** | 新規実験の完全実行 | データ読込→学習→評価→保存 | 5分 |
| **E2E-002** | 重複実験のスキップ | Fingerprint検出→スキップ | 1分 |
| **E2E-003** | ハイパーパラメータ探索 | Optuna統合→最適化 | 15分 |
| **E2E-004** | モデルレジストリ昇格 | Staging→Production | 2分 |
| **E2E-005** | 再学習スケジューリング | 定期実行→更新 | 10分 |
| **E2E-006** | バッチ予測配信 | 予測実行→結果保存 | 5分 |
| **E2E-007** | UI経由の操作 | ブラウザ操作→結果確認 | 8分 |
| **E2E-008** | API経由の操作 | REST API→CRUD | 3分 |

**合計目標**: 10+ E2Eテスト

---

#### 2.3.3 E2Eテストの例

```python
# E2Eテストの例
import pytest
from selenium import webdriver
from nf_auto_runner.app import create_app


@pytest.fixture
def app():
    """テスト用アプリケーション"""
    app = create_app(config="testing")
    yield app


@pytest.fixture
def browser():
    """ブラウザセットアップ"""
    driver = webdriver.Chrome()
    yield driver
    driver.quit()


class TestE2ENewExperiment:
    """新規実験のE2Eテスト"""
    
    def test_complete_experiment_workflow(self, app, browser):
        """完全な実験ワークフローのE2Eテスト"""
        # 1. アプリケーション起動
        browser.get("http://localhost:8501")
        
        # 2. データアップロード
        upload_input = browser.find_element_by_id("data-upload")
        upload_input.send_keys("/path/to/test_data.csv")
        
        # 3. モデル選択
        model_select = browser.find_element_by_id("model-select")
        model_select.select_by_visible_text("AutoNHITS")
        
        # 4. ハイパーパラメータ設定
        horizon_input = browser.find_element_by_id("horizon")
        horizon_input.send_keys("7")
        
        # 5. 実行ボタンクリック
        execute_button = browser.find_element_by_id("execute-button")
        execute_button.click()
        
        # 6. 実行完了を待機
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        wait = WebDriverWait(browser, 300)  # 5分待機
        success_message = wait.until(
            EC.presence_of_element_located(("id", "success-message"))
        )
        
        # 7. 結果確認
        assert "実行が完了しました" in success_message.text
        
        # 8. メトリクス確認
        mae_value = browser.find_element_by_id("mae-value").text
        assert float(mae_value) > 0
        
        # 9. グラフ表示確認
        plot = browser.find_element_by_id("forecast-plot")
        assert plot.is_displayed()
```

---

### 2.4 パフォーマンステスト

#### 2.4.1 概要

**目的**: システムのパフォーマンスが要件を満たすことを検証

---

#### 2.4.2 パフォーマンステストのスコープ

| テスト分類 | 測定対象 | 目標値 | 測定方法 |
|----------|---------|-------|---------|
| **実行速度** | 単一モデル学習時間 | <10分 | time.perf_counter |
| **並列処理** | 100モデル並列学習 | <2時間 | Wall clock |
| **メモリ使用量** | ピークメモリ | <16GB | psutil.virtual_memory |
| **GPU利用率** | GPU使用率 | >80% | nvidia-smi |
| **データベース** | クエリ応答時間 | <100ms | pg_stat_statements |
| **API応答** | REST API応答時間 | <1秒 | Locust |
| **スループット** | 同時実行数 | 10並列 | Ray metrics |

---

#### 2.4.3 パフォーマンステストの例

```python
# パフォーマンステストの例
import pytest
import time
import psutil
from nf_auto_runner.service import ExecutionService


class TestPerformance:
    """パフォーマンステスト"""
    
    @pytest.mark.performance
    def test_single_model_training_time(self, test_data):
        """単一モデル学習時間のテスト"""
        # Arrange
        service = ExecutionService()
        
        # Act
        start_time = time.perf_counter()
        result = service.execute_single_run(
            data=test_data,
            model_name="AutoNHITS",
            hyperparameters={"h": 7}
        )
        end_time = time.perf_counter()
        
        # Assert
        execution_time = end_time - start_time
        assert execution_time < 600, f"学習時間が10分を超過: {execution_time}秒"
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_parallel_execution_performance(self, test_data):
        """並列実行のパフォーマンステスト"""
        # Arrange
        service = ExecutionService(executor_type="ray")
        execution_plans = [
            {"model": f"AutoNHITS", "h": 7}
            for _ in range(100)
        ]
        
        # Act
        start_time = time.perf_counter()
        results = service.execute_parallel(execution_plans)
        end_time = time.perf_counter()
        
        # Assert
        execution_time = end_time - start_time
        assert execution_time < 7200, f"100モデルの学習時間が2時間を超過"
        assert all(r.status == "completed" for r in results)
    
    @pytest.mark.performance
    def test_memory_usage(self, test_data):
        """メモリ使用量のテスト"""
        # Arrange
        service = ExecutionService()
        process = psutil.Process()
        
        # メモリ使用量の初期値
        mem_before = process.memory_info().rss / (1024 ** 3)  # GB
        
        # Act
        result = service.execute_single_run(
            data=test_data,
            model_name="AutoNHITS",
            hyperparameters={"h": 7}
        )
        
        # メモリ使用量の最大値
        mem_after = process.memory_info().rss / (1024 ** 3)  # GB
        mem_used = mem_after - mem_before
        
        # Assert
        assert mem_used < 16, f"メモリ使用量が16GBを超過: {mem_used}GB"
    
    @pytest.mark.performance
    def test_database_query_performance(self, test_database):
        """データベースクエリのパフォーマンステスト"""
        # Arrange
        from nf_auto_runner.artifact.repository import ExperimentRepository
        repo = ExperimentRepository(test_database)
        
        # Act
        start_time = time.perf_counter()
        experiments = repo.get_all_experiments(limit=1000)
        end_time = time.perf_counter()
        
        # Assert
        query_time = end_time - start_time
        assert query_time < 0.1, f"クエリ時間が100msを超過: {query_time*1000}ms"
```

---

### 2.5 セキュリティテスト

#### 2.5.1 概要

**目的**: システムのセキュリティ脆弱性を検出し、セキュリティ要件を満たすことを検証

---

#### 2.5.2 セキュリティテストのスコープ

| テスト分類 | チェック項目 | ツール |
|----------|------------|-------|
| **SQLインジェクション** | パラメータ化クエリ使用 | sqlmap, pytest |
| **認証・認可** | JWT検証、権限チェック | pytest |
| **入力検証** | バリデーション実装 | pytest, hypothesis |
| **秘密情報管理** | ハードコード禁止 | bandit, pytest |
| **依存関係スキャン** | 既知の脆弱性検出 | safety, pip-audit |
| **コードスキャン** | セキュリティ問題検出 | bandit, semgrep |

---

#### 2.5.3 セキュリティテストの例

```python
# セキュリティテストの例
import pytest
from nf_auto_runner.api import create_api
from nf_auto_runner.auth import verify_token


class TestSecurity:
    """セキュリティテスト"""
    
    @pytest.mark.security
    def test_sql_injection_prevention(self, test_database):
        """SQLインジェクション対策のテスト"""
        # Arrange
        from nf_auto_runner.artifact.repository import ExperimentRepository
        repo = ExperimentRepository(test_database)
        
        # Act: SQLインジェクション試行
        malicious_input = "1' OR '1'='1"
        
        # Assert: エラーが発生することを確認
        with pytest.raises(ValueError):
            repo.get_experiment_by_id(malicious_input)
    
    @pytest.mark.security
    def test_authentication_required(self, test_client):
        """認証が必要なエンドポイントのテスト"""
        # Act: 認証なしでアクセス
        response = test_client.get("/api/experiments")
        
        # Assert: 401エラー
        assert response.status_code == 401
    
    @pytest.mark.security
    def test_jwt_token_validation(self):
        """JWTトークン検証のテスト"""
        # Arrange
        invalid_token = "invalid.token.here"
        
        # Act & Assert
        with pytest.raises(Exception):
            verify_token(invalid_token)
    
    @pytest.mark.security
    def test_no_hardcoded_secrets(self):
        """ハードコードされた秘密情報がないことを確認"""
        import subprocess
        
        # banditでスキャン
        result = subprocess.run(
            ["bandit", "-r", "src/", "-f", "json"],
            capture_output=True,
            text=True
        )
        
        # Assert: 高リスクの問題がないこと
        import json
        report = json.loads(result.stdout)
        high_severity = [
            issue for issue in report["results"]
            if issue["issue_severity"] == "HIGH"
        ]
        assert len(high_severity) == 0, f"高リスクの問題が検出: {high_severity}"
```

---

## 3. テスト手法とアプローチ

### 3.1 Test-Driven Development (TDD)

#### 3.1.1 TDDサイクル

本システムは、TDD（テスト駆動開発）を採用します：

```
  ┌─────────────┐
  │   Red       │ ──┐
  │  失敗する    │   │
  │  テストを書く │   │
  └─────────────┘   │
         ↑          │
         │          ↓
  ┌─────────────┐   ┌─────────────┐
  │  Refactor   │   │   Green     │
  │  リファクタ   │←──│  テストを    │
  │             │   │  パスさせる   │
  └─────────────┘   └─────────────┘
```

**ステップ**:
1. **Red**: 失敗するテストを書く
2. **Green**: テストをパスする最小限のコードを書く
3. **Refactor**: コードを改善（テストは通る状態を維持）

---

#### 3.1.2 TDD実践例

```python
# ステップ1: Red - 失敗するテストを書く
def test_calculate_mae():
    """MAE計算のテスト"""
    # Arrange
    y_true = np.array([1, 2, 3, 4, 5])
    y_pred = np.array([1.1, 2.1, 2.9, 4.2, 4.8])
    
    # Act
    mae = calculate_mae(y_true, y_pred)
    
    # Assert
    expected = np.mean(np.abs(y_true - y_pred))
    assert mae == pytest.approx(expected)


# ステップ2: Green - テストをパスする最小限のコード
def calculate_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """MAEを計算"""
    return np.mean(np.abs(y_true - y_pred))


# ステップ3: Refactor - コードを改善
def calculate_mae(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    sample_weight: Optional[np.ndarray] = None
) -> float:
    """
    MAEを計算
    
    Args:
        y_true: 真の値
        y_pred: 予測値
        sample_weight: サンプル重み（オプション）
    
    Returns:
        MAE値
    
    Raises:
        ValueError: 入力配列の形状が一致しない場合
    """
    if y_true.shape != y_pred.shape:
        raise ValueError("y_trueとy_predの形状が一致しません")
    
    absolute_errors = np.abs(y_true - y_pred)
    
    if sample_weight is not None:
        if sample_weight.shape != y_true.shape:
            raise ValueError("sample_weightの形状が一致しません")
        return np.average(absolute_errors, weights=sample_weight)
    
    return np.mean(absolute_errors)


# リファクタ後の追加テスト
def test_calculate_mae_with_sample_weight():
    """重み付きMAE計算のテスト"""
    # Arrange
    y_true = np.array([1, 2, 3, 4, 5])
    y_pred = np.array([1.1, 2.1, 2.9, 4.2, 4.8])
    weights = np.array([1, 1, 1, 2, 2])
    
    # Act
    mae = calculate_mae(y_true, y_pred, sample_weight=weights)
    
    # Assert
    absolute_errors = np.abs(y_true - y_pred)
    expected = np.average(absolute_errors, weights=weights)
    assert mae == pytest.approx(expected)


def test_calculate_mae_with_mismatched_shapes():
    """形状不一致のエラーテスト"""
    # Arrange
    y_true = np.array([1, 2, 3])
    y_pred = np.array([1, 2])
    
    # Act & Assert
    with pytest.raises(ValueError, match="形状が一致しません"):
        calculate_mae(y_true, y_pred)
```

---

### 3.2 Behavior-Driven Development (BDD)

#### 3.2.1 Given-When-Then パターン

BDDスタイルでテストを記述します：

```python
# BDDスタイルのテスト
def test_duplicate_experiment_detection():
    """重複実験検出のBDDテスト"""
    # Given: 既存の実験が存在する
    existing_experiment = create_experiment(
        model="AutoNHITS",
        hyperparameters={"h": 7, "input_size": 14},
        data_hash="abc123"
    )
    save_experiment(existing_experiment)
    
    # When: 同じ条件で新しい実験を実行しようとする
    new_experiment = create_experiment(
        model="AutoNHITS",
        hyperparameters={"h": 7, "input_size": 14},
        data_hash="abc123"
    )
    
    # Then: 重複が検出される
    assert is_duplicate(new_experiment, existing_experiment)
    
    # And: 実験はスキップされる
    result = execute_experiment(new_experiment)
    assert result.status == "skipped"
    assert result.reason == "duplicate_detected"
```

---

### 3.3 Property-Based Testing

#### 3.3.1 Hypothesisを使用したテスト

プロパティベーステストで広範な入力をテストします：

```python
from hypothesis import given, strategies as st
import numpy as np


@given(
    y_true=st.lists(st.floats(min_value=-1000, max_value=1000), min_size=1, max_size=100),
    y_pred=st.lists(st.floats(min_value=-1000, max_value=1000), min_size=1, max_size=100)
)
def test_mae_properties(y_true, y_pred):
    """MAE計算のプロパティテスト"""
    # 同じ長さにする
    min_len = min(len(y_true), len(y_pred))
    y_true = np.array(y_true[:min_len])
    y_pred = np.array(y_pred[:min_len])
    
    # Act
    mae = calculate_mae(y_true, y_pred)
    
    # Properties to test:
    # 1. MAEは非負
    assert mae >= 0
    
    # 2. 完全予測の場合MAEは0
    perfect_mae = calculate_mae(y_true, y_true)
    assert perfect_mae == 0
    
    # 3. MAEは誤差の絶対値の平均
    expected = np.mean(np.abs(y_true - y_pred))
    assert abs(mae - expected) < 1e-10


@given(
    data=st.data(),
    n_samples=st.integers(min_value=10, max_value=1000),
    n_features=st.integers(min_value=1, max_value=20)
)
def test_data_preprocessor_properties(data, n_samples, n_features):
    """データ前処理のプロパティテスト"""
    # Arrange
    df = pd.DataFrame(
        data.draw(
            st.lists(
                st.lists(st.floats(allow_nan=False, allow_infinity=False), 
                        min_size=n_features, max_size=n_features),
                min_size=n_samples, max_size=n_samples
            )
        )
    )
    
    preprocessor = DataPreprocessor()
    
    # Act
    processed = preprocessor.preprocess(df)
    
    # Properties:
    # 1. 形状は保持される
    assert processed.shape == df.shape
    
    # 2. NaNは含まれない
    assert not processed.isnull().any().any()
    
    # 3. 無限大は含まれない
    assert not np.isinf(processed.values).any()
```

---

### 3.4 Mutation Testing

#### 3.4.1 概要

ミューテーションテストでテストの品質を評価します：

```bash
# mutmutを使用したミューテーションテスト
pip install mutmut

# 実行
mutmut run --paths-to-mutate src/nf_auto_runner/

# 結果確認
mutmut results

# 生き残ったミュータントの確認
mutmut show
```

**目標**: ミューテーションスコア >80%

---

## 4. テストカバレッジ目標

### 4.1 層ごとのカバレッジ目標

| 層 | カバレッジ目標 | 測定方法 | 重要度 |
|---|--------------|---------|-------|
| **Configuration層** | >95% | Line coverage | 高 |
| **Data層** | >95% | Line + Branch coverage | 高 |
| **Model Discovery層** | >90% | Line coverage | 高 |
| **Hyperparameter層** | >90% | Line coverage | 中 |
| **Execution Plan層** | >90% | Line coverage | 中 |
| **Execution層** | >85% | Line coverage | 高 |
| **Artifact層** | >90% | Line coverage | 中 |
| **Logging層** | >90% | Line coverage | 中 |
| **Service層** | >85% | Line + Branch coverage | 高 |
| **Application層** | >85% | Line coverage | 中 |

**全体目標**: >90%

---

### 4.2 カバレッジ測定

#### 4.2.1 pytest-covを使用した測定

```bash
# 基本的なカバレッジ測定
pytest tests/ --cov=src/nf_auto_runner --cov-report=html

# ブランチカバレッジを含む
pytest tests/ --cov=src/nf_auto_runner --cov-branch --cov-report=html

# 特定のモジュールのみ
pytest tests/unit/config/ --cov=src/nf_auto_runner/config --cov-report=term

# カバレッジ不足の行を表示
pytest tests/ --cov=src/nf_auto_runner --cov-report=term-missing
```

---

#### 4.2.2 カバレッジレポートの例

```
---------- coverage: platform linux, python 3.11.6 -----------
Name                                      Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------------------------------------------
src/nf_auto_runner/config/__init__.py        10      0      0      0   100%
src/nf_auto_runner/config/base.py          125      3     42      2    96%   45-47, 89->92
src/nf_auto_runner/config/path.py           89      2     28      1    97%   67-68
src/nf_auto_runner/config/execution.py     156      8     54      4    93%   89, 112-115, 178->181
src/nf_auto_runner/data/loader.py          234     12     78      6    94%   123-125, 189, 234-237
---------------------------------------------------------------------------------------
TOTAL                                      3456    127   1245     48    95%
```

---

### 4.3 カバレッジ除外規則

以下のコードはカバレッジ計測から除外します：

```python
# .coveragerc
[report]
exclude_lines =
    # 標準的な除外パターン
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstract
    @abstractmethod
    
    # カスタム除外パターン
    # デバッグコード
    if DEBUG:
    if debug:
    
    # 防御的プログラミング（通常発生しない）
    except Exception as e:
        logger.critical
    
    # 型チェック用インポート
    if typing.TYPE_CHECKING:
```

---

## 5. TDD実践ガイド

### 5.1 TDDワークフロー

#### 5.1.1 フェーズごとのTDD実践

各開発フェーズでTDDを実践します：

```
Phase 1: Configuration層
├── 1. テスト設計
│   ├── Config基底クラスのテストケース設計
│   ├── PathConfigのテストケース設計
│   └── ...
├── 2. テスト実装（Red）
│   ├── test_config_base.py
│   ├── test_path_config.py
│   └── ...
├── 3. 実装（Green）
│   ├── config/base.py
│   ├── config/path.py
│   └── ...
└── 4. リファクタリング
    ├── コード改善
    └── テスト改善
```

---

#### 5.1.2 TDD実践チェックリスト

各実装前に確認：

- [ ] テストケースを先に設計したか？
- [ ] テストが失敗することを確認したか？（Red）
- [ ] 最小限のコードでテストをパスさせたか？（Green）
- [ ] リファクタリングを実施したか？
- [ ] すべてのテストがまだパスするか？
- [ ] カバレッジ目標を達成したか？

---

### 5.2 テストファースト開発の例

#### 5.2.1 DataLoaderクラスの開発例

```python
# ========================================
# ステップ1: テスト設計
# ========================================

# tests/unit/data/test_data_loader.py

import pytest
from pathlib import Path
import pandas as pd


class TestDataLoader:
    """DataLoaderクラスのテスト"""
    
    # ========================================
    # RED: まずテストを書く（実装はまだない）
    # ========================================
    
    def test_init_with_valid_path(self, tmp_path):
        """有効なパスでの初期化テスト"""
        # Arrange
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        
        # Act
        from nf_auto_runner.data import DataLoader
        loader = DataLoader(data_dir=str(data_dir))
        
        # Assert
        assert loader.data_dir == str(data_dir)
        assert loader.is_valid()
    
    def test_load_csv_success(self, tmp_path):
        """CSV読み込み成功のテスト"""
        # Arrange
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        
        # テストCSV作成
        test_csv = data_dir / "test.csv"
        pd.DataFrame({
            'unique_id': ['A', 'A', 'B', 'B'],
            'ds': pd.date_range('2025-01-01', periods=4),
            'y': [1, 2, 3, 4]
        }).to_csv(test_csv, index=False)
        
        # Act
        from nf_auto_runner.data import DataLoader
        loader = DataLoader(data_dir=str(data_dir))
        df = loader.load_csv("test.csv")
        
        # Assert
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 4
        assert list(df.columns) == ['unique_id', 'ds', 'y']
    
    def test_load_csv_file_not_found(self, tmp_path):
        """存在しないファイルのエラーテスト"""
        # Arrange
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        
        # Act & Assert
        from nf_auto_runner.data import DataLoader
        loader = DataLoader(data_dir=str(data_dir))
        
        with pytest.raises(FileNotFoundError):
            loader.load_csv("nonexistent.csv")
    
    def test_validate_schema_success(self, tmp_path):
        """スキーマ検証成功のテスト"""
        # Arrange
        df = pd.DataFrame({
            'unique_id': ['A', 'A'],
            'ds': pd.date_range('2025-01-01', periods=2),
            'y': [1, 2]
        })
        
        # Act
        from nf_auto_runner.data import DataLoader
        loader = DataLoader(data_dir=str(tmp_path))
        is_valid = loader.validate_schema(df)
        
        # Assert
        assert is_valid is True
    
    def test_validate_schema_missing_column(self):
        """必須カラム欠落のエラーテスト"""
        # Arrange
        df = pd.DataFrame({
            'unique_id': ['A', 'A'],
            'ds': pd.date_range('2025-01-01', periods=2)
            # 'y' カラムが欠落
        })
        
        # Act
        from nf_auto_runner.data import DataLoader
        loader = DataLoader(data_dir="/tmp")
        is_valid = loader.validate_schema(df)
        
        # Assert
        assert is_valid is False


# ========================================
# ステップ2: 実装（GREEN）
# ========================================

# src/nf_auto_runner/data/loader.py

from pathlib import Path
from typing import Optional
import pandas as pd
from loguru import logger


class DataLoader:
    """データ読み込みクラス"""
    
    REQUIRED_COLUMNS = ['unique_id', 'ds', 'y']
    
    def __init__(self, data_dir: str):
        """
        初期化
        
        Args:
            data_dir: データディレクトリのパス
        
        Raises:
            ValueError: data_dirが空の場合
        """
        if not data_dir:
            raise ValueError("data_dir cannot be empty")
        
        self.data_dir = data_dir
        self._data_path = Path(data_dir)
        
        logger.info(f"DataLoader initialized with data_dir={data_dir}")
    
    def is_valid(self) -> bool:
        """
        データディレクトリが有効かチェック
        
        Returns:
            有効な場合True
        """
        return self._data_path.exists() and self._data_path.is_dir()
    
    def load_csv(
        self,
        filename: str,
        *,
        parse_dates: bool = True
    ) -> pd.DataFrame:
        """
        CSVファイルを読み込む
        
        Args:
            filename: ファイル名
            parse_dates: 日付を自動パースするか
        
        Returns:
            読み込んだDataFrame
        
        Raises:
            FileNotFoundError: ファイルが存在しない場合
        """
        file_path = self._data_path / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"Loading CSV: {file_path}")
        
        df = pd.read_csv(
            file_path,
            parse_dates=['ds'] if parse_dates else None
        )
        
        logger.info(f"Loaded {len(df)} rows from {filename}")
        
        return df
    
    def validate_schema(self, df: pd.DataFrame) -> bool:
        """
        DataFrameのスキーマを検証
        
        Args:
            df: 検証対象のDataFrame
        
        Returns:
            有効な場合True
        """
        missing_columns = set(self.REQUIRED_COLUMNS) - set(df.columns)
        
        if missing_columns:
            logger.warning(f"Missing required columns: {missing_columns}")
            return False
        
        logger.info("Schema validation passed")
        return True


# ========================================
# ステップ3: テスト実行（すべてパスすることを確認）
# ========================================

# $ pytest tests/unit/data/test_data_loader.py -v
# 
# tests/unit/data/test_data_loader.py::TestDataLoader::test_init_with_valid_path PASSED
# tests/unit/data/test_data_loader.py::TestDataLoader::test_load_csv_success PASSED
# tests/unit/data/test_data_loader.py::TestDataLoader::test_load_csv_file_not_found PASSED
# tests/unit/data/test_data_loader.py::TestDataLoader::test_validate_schema_success PASSED
# tests/unit/data/test_data_loader.py::TestDataLoader::test_validate_schema_missing_column PASSED


# ========================================
# ステップ4: リファクタリング
# ========================================

# コードを改善（テストは通る状態を維持）

class DataLoader:
    """データ読み込みクラス（改善版）"""
    
    REQUIRED_COLUMNS = ['unique_id', 'ds', 'y']
    
    def __init__(
        self,
        data_dir: str,
        *,
        validate_on_init: bool = True
    ):
        """
        初期化
        
        Args:
            data_dir: データディレクトリのパス
            validate_on_init: 初期化時に検証するか
        
        Raises:
            ValueError: data_dirが空または無効な場合
        """
        if not data_dir:
            raise ValueError("data_dir cannot be empty")
        
        self.data_dir = data_dir
        self._data_path = Path(data_dir)
        
        if validate_on_init and not self.is_valid():
            raise ValueError(f"Invalid data directory: {data_dir}")
        
        logger.info(f"DataLoader initialized with data_dir={data_dir}")
    
    def is_valid(self) -> bool:
        """データディレクトリが有効かチェック"""
        return self._data_path.exists() and self._data_path.is_dir()
    
    def load_csv(
        self,
        filename: str,
        *,
        parse_dates: bool = True,
        validate_schema: bool = True
    ) -> pd.DataFrame:
        """
        CSVファイルを読み込む
        
        Args:
            filename: ファイル名
            parse_dates: 日付を自動パースするか
            validate_schema: スキーマを検証するか
        
        Returns:
            読み込んだDataFrame
        
        Raises:
            FileNotFoundError: ファイルが存在しない場合
            ValueError: スキーマが無効な場合
        """
        file_path = self._data_path / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"Loading CSV: {file_path}")
        
        df = pd.read_csv(
            file_path,
            parse_dates=['ds'] if parse_dates else None
        )
        
        if validate_schema and not self.validate_schema(df):
            raise ValueError(f"Invalid schema in {filename}")
        
        logger.info(f"Loaded {len(df)} rows from {filename}")
        
        return df
    
    def validate_schema(
        self,
        df: pd.DataFrame,
        *,
        strict: bool = False
    ) -> bool:
        """
        DataFrameのスキーマを検証
        
        Args:
            df: 検証対象のDataFrame
            strict: 厳密モード（追加カラムも許可しない）
        
        Returns:
            有効な場合True
        """
        missing_columns = set(self.REQUIRED_COLUMNS) - set(df.columns)
        
        if missing_columns:
            logger.warning(f"Missing required columns: {missing_columns}")
            return False
        
        if strict:
            extra_columns = set(df.columns) - set(self.REQUIRED_COLUMNS)
            if extra_columns:
                logger.warning(f"Extra columns found: {extra_columns}")
                return False
        
        logger.info("Schema validation passed")
        return True


# ========================================
# ステップ5: リファクタリング後の追加テスト
# ========================================

class TestDataLoaderRefactored:
    """リファクタリング後の追加テスト"""
    
    def test_init_with_validate_on_init_false(self, tmp_path):
        """初期化時検証スキップのテスト"""
        # Arrange
        nonexistent_dir = tmp_path / "nonexistent"
        
        # Act: 検証をスキップするので例外は発生しない
        loader = DataLoader(
            data_dir=str(nonexistent_dir),
            validate_on_init=False
        )
        
        # Assert
        assert not loader.is_valid()
    
    def test_load_csv_with_validate_schema_false(self, tmp_path):
        """スキーマ検証スキップのテスト"""
        # Arrange
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        
        # 不正なCSV（'y'カラムが欠落）
        invalid_csv = data_dir / "invalid.csv"
        pd.DataFrame({
            'unique_id': ['A'],
            'ds': pd.date_range('2025-01-01', periods=1)
        }).to_csv(invalid_csv, index=False)
        
        loader = DataLoader(data_dir=str(data_dir))
        
        # Act: 検証をスキップするので例外は発生しない
        df = loader.load_csv("invalid.csv", validate_schema=False)
        
        # Assert
        assert 'y' not in df.columns
    
    def test_validate_schema_strict_mode(self):
        """厳密モードでの検証テスト"""
        # Arrange
        df = pd.DataFrame({
            'unique_id': ['A'],
            'ds': pd.date_range('2025-01-01', periods=1),
            'y': [1],
            'extra_column': ['extra']  # 追加カラム
        })
        
        loader = DataLoader(data_dir="/tmp", validate_on_init=False)
        
        # Act & Assert
        assert loader.validate_schema(df, strict=False) is True
        assert loader.validate_schema(df, strict=True) is False
```

---

## 6. テストケース設計

### 6.1 テストケース設計原則

#### 6.1.1 カバレッジ基準

以下の観点でテストケースを設計します：

| 観点 | 説明 | 例 |
|-----|------|---|
| **正常系** | 仕様通りの動作 | 有効な入力での正常処理 |
| **準正常系** | エッジケース | 境界値、空データ |
| **異常系** | エラーケース | 無効な入力、例外発生 |
| **境界値** | 境界条件 | 最小値、最大値、0 |
| **等価クラス** | 同等の動作をするグループ | 正の整数、負の整数 |
| **状態遷移** | 状態の変化 | 初期化→実行中→完了 |

---

#### 6.1.2 テストケース設計テンプレート

```markdown
## テストケースID: TC-XXX-YYY

### 目的
何をテストするか

### 前提条件
- 条件1
- 条件2

### テストステップ
1. ステップ1
2. ステップ2
3. ステップ3

### 期待結果
- 期待される結果1
- 期待される結果2

### 実際の結果
[テスト実行後に記入]

### 判定
[Pass/Fail]
```

---

### 6.2 テストケース例

#### 6.2.1 Configuration層のテストケース

```python
# tests/unit/config/test_execution_config.py

import pytest
from nf_auto_runner.config import ExecutionConfig


class TestExecutionConfig:
    """ExecutionConfigのテストケース"""
    
    # ========================================
    # 正常系
    # ========================================
    
    def test_init_with_default_values(self):
        """TC-CFG-001: デフォルト値での初期化"""
        # Act
        config = ExecutionConfig()
        
        # Assert
        assert config.max_parallel_runs == 10
        assert config.backend == "cpu"
        assert config.enable_gpu is False
    
    def test_init_with_custom_values(self):
        """TC-CFG-002: カスタム値での初期化"""
        # Arrange
        max_runs = 20
        backend = "cuda"
        
        # Act
        config = ExecutionConfig(
            max_parallel_runs=max_runs,
            backend=backend,
            enable_gpu=True
        )
        
        # Assert
        assert config.max_parallel_runs == max_runs
        assert config.backend == backend
        assert config.enable_gpu is True
    
    # ========================================
    # 準正常系（エッジケース）
    # ========================================
    
    def test_init_with_zero_parallel_runs(self):
        """TC-CFG-003: 並列実行数0の場合"""
        # Act
        config = ExecutionConfig(max_parallel_runs=0)
        
        # Assert
        assert config.max_parallel_runs == 0
        # 0の場合は直列実行にフォールバック
        assert config.get_executor_type() == "serial"
    
    @pytest.mark.parametrize("backend", ["cpu", "cuda", "mps"])
    def test_init_with_valid_backends(self, backend):
        """TC-CFG-004: 有効なバックエンドの指定"""
        # Act
        config = ExecutionConfig(backend=backend)
        
        # Assert
        assert config.backend == backend
    
    # ========================================
    # 異常系
    # ========================================
    
    def test_init_with_negative_parallel_runs(self):
        """TC-CFG-005: 負の並列実行数でエラー"""
        # Act & Assert
        with pytest.raises(ValueError, match="must be non-negative"):
            ExecutionConfig(max_parallel_runs=-1)
    
    def test_init_with_invalid_backend(self):
        """TC-CFG-006: 無効なバックエンドでエラー"""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid backend"):
            ExecutionConfig(backend="invalid_backend")
    
    # ========================================
    # 境界値
    # ========================================
    
    @pytest.mark.parametrize("max_runs", [1, 100, 1000])
    def test_init_with_boundary_values(self, max_runs):
        """TC-CFG-007: 境界値テスト"""
        # Act
        config = ExecutionConfig(max_parallel_runs=max_runs)
        
        # Assert
        assert config.max_parallel_runs == max_runs
    
    # ========================================
    # 状態遷移
    # ========================================
    
    def test_update_configuration(self):
        """TC-CFG-008: 設定の更新"""
        # Arrange
        config = ExecutionConfig(max_parallel_runs=10)
        
        # Act: 設定を更新
        config.update(max_parallel_runs=20, backend="cuda")
        
        # Assert
        assert config.max_parallel_runs == 20
        assert config.backend == "cuda"
```

---

#### 6.2.2 Data層のテストケース

```python
# tests/unit/data/test_data_preprocessor.py

import pytest
import pandas as pd
import numpy as np
from nf_auto_runner.data import DataPreprocessor


class TestDataPreprocessor:
    """DataPreprocessorのテストケース"""
    
    @pytest.fixture
    def sample_data(self):
        """サンプルデータ"""
        return pd.DataFrame({
            'unique_id': ['A', 'A', 'A', 'B', 'B', 'B'],
            'ds': pd.date_range('2025-01-01', periods=6),
            'y': [1.0, 2.0, np.nan, 4.0, 5.0, 6.0]
        })
    
    # ========================================
    # 正常系
    # ========================================
    
    def test_handle_missing_values_fill(self, sample_data):
        """TC-DATA-001: 欠損値を補完"""
        # Arrange
        preprocessor = DataPreprocessor(missing_value_strategy='fill')
        
        # Act
        result = preprocessor.handle_missing_values(sample_data)
        
        # Assert
        assert not result['y'].isnull().any()
        assert len(result) == len(sample_data)
    
    def test_handle_missing_values_drop(self, sample_data):
        """TC-DATA-002: 欠損値を削除"""
        # Arrange
        preprocessor = DataPreprocessor(missing_value_strategy='drop')
        
        # Act
        result = preprocessor.handle_missing_values(sample_data)
        
        # Assert
        assert not result['y'].isnull().any()
        assert len(result) == len(sample_data) - 1  # 1行削除される
    
    # ========================================
    # 準正常系
    # ========================================
    
    def test_handle_all_missing_values(self):
        """TC-DATA-003: すべて欠損値の場合"""
        # Arrange
        data = pd.DataFrame({
            'unique_id': ['A', 'A'],
            'ds': pd.date_range('2025-01-01', periods=2),
            'y': [np.nan, np.nan]
        })
        preprocessor = DataPreprocessor(missing_value_strategy='drop')
        
        # Act
        result = preprocessor.handle_missing_values(data)
        
        # Assert
        assert len(result) == 0  # すべて削除される
    
    def test_handle_no_missing_values(self, sample_data):
        """TC-DATA-004: 欠損値がない場合"""
        # Arrange
        clean_data = sample_data.dropna()
        preprocessor = DataPreprocessor()
        
        # Act
        result = preprocessor.handle_missing_values(clean_data)
        
        # Assert
        pd.testing.assert_frame_equal(result, clean_data)
    
    # ========================================
    # 異常系
    # ========================================
    
    def test_handle_invalid_strategy(self, sample_data):
        """TC-DATA-005: 無効な戦略でエラー"""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid strategy"):
            DataPreprocessor(missing_value_strategy='invalid')
    
    # ========================================
    # パラメータ化テスト
    # ========================================
    
    @pytest.mark.parametrize("strategy,expected_len", [
        ('fill', 6),
        ('drop', 5),
        ('interpolate', 6),
    ])
    def test_missing_value_strategies(
        self, sample_data, strategy, expected_len
    ):
        """TC-DATA-006: 各種欠損値処理戦略のテスト"""
        # Arrange
        preprocessor = DataPreprocessor(missing_value_strategy=strategy)
        
        # Act
        result = preprocessor.handle_missing_values(sample_data)
        
        # Assert
        assert len(result) == expected_len
        if strategy != 'drop':
            assert not result['y'].isnull().any()
```

---

## 7. テストデータ管理

### 7.1 テストデータ戦略

#### 7.1.1 テストデータの種類

| 種類 | 用途 | 配置場所 | 管理方法 |
|-----|------|---------|---------|
| **Fixture** | 単体テスト用 | `tests/fixtures/` | pytest fixture |
| **サンプルデータ** | 統合テスト用 | `tests/data/` | ファイルベース |
| **合成データ** | パフォーマンステスト用 | 動的生成 | faker, hypothesis |
| **本番類似データ** | E2Eテスト用 | `tests/data/production_like/` | 匿名化済み |

---

#### 7.1.2 Fixtureの活用

```python
# tests/conftest.py

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy import create_engine


# ========================================
# データベース関連Fixture
# ========================================

@pytest.fixture(scope="session")
def test_database_url():
    """テスト用データベースURL"""
    return "postgresql://test:test@localhost:5433/test_db"


@pytest.fixture(scope="session")
def test_engine(test_database_url):
    """テスト用データベースエンジン"""
    engine = create_engine(test_database_url)
    
    # セットアップ
    from alembic import command
    from alembic.config import Config
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    
    yield engine
    
    # クリーンアップ
    command.downgrade(alembic_cfg, "base")
    engine.dispose()


@pytest.fixture
def db_session(test_engine):
    """テスト用データベースセッション"""
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=test_engine)
    session = Session()
    
    yield session
    
    # ロールバック
    session.rollback()
    session.close()


# ========================================
# データ関連Fixture
# ========================================

@pytest.fixture
def sample_timeseries_data():
    """サンプル時系列データ"""
    return pd.DataFrame({
        'unique_id': ['A'] * 100 + ['B'] * 100,
        'ds': pd.date_range('2025-01-01', periods=100).tolist() * 2,
        'y': np.random.randn(200).cumsum()
    })


@pytest.fixture
def sample_data_with_exog():
    """外生変数を含むサンプルデータ"""
    dates = pd.date_range('2025-01-01', periods=100)
    return pd.DataFrame({
        'unique_id': ['A'] * 100,
        'ds': dates,
        'y': np.random.randn(100).cumsum(),
        'temperature': np.random.uniform(10, 30, 100),
        'is_holiday': np.random.choice([0, 1], 100)
    })


@pytest.fixture
def large_dataset():
    """大規模データセット（パフォーマンステスト用）"""
    n_series = 1000
    n_points = 365
    
    data = []
    for i in range(n_series):
        data.append(pd.DataFrame({
            'unique_id': [f'series_{i}'] * n_points,
            'ds': pd.date_range('2024-01-01', periods=n_points),
            'y': np.random.randn(n_points).cumsum()
        }))
    
    return pd.concat(data, ignore_index=True)


# ========================================
# パス関連Fixture
# ========================================

@pytest.fixture
def test_data_dir(tmp_path):
    """テスト用データディレクトリ"""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def test_model_dir(tmp_path):
    """テスト用モデルディレクトリ"""
    model_dir = tmp_path / "models"
    model_dir.mkdir()
    return model_dir


@pytest.fixture
def test_output_dir(tmp_path):
    """テスト用出力ディレクトリ"""
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    return output_dir


# ========================================
# 設定関連Fixture
# ========================================

@pytest.fixture
def test_config(test_data_dir, test_model_dir, test_output_dir):
    """テスト用設定"""
    from nf_auto_runner.config import PathConfig, ExecutionConfig
    
    return {
        'path': PathConfig(
            data_dir=str(test_data_dir),
            model_dir=str(test_model_dir),
            output_dir=str(test_output_dir)
        ),
        'execution': ExecutionConfig(
            max_parallel_runs=2,
            backend='cpu'
        )
    }


# ========================================
# モック関連Fixture
# ========================================

@pytest.fixture
def mock_mlflow():
    """MLflowのモック"""
    from unittest.mock import MagicMock, patch
    
    with patch('mlflow.log_metric') as mock_log_metric, \
         patch('mlflow.log_param') as mock_log_param, \
         patch('mlflow.log_artifact') as mock_log_artifact:
        
        yield {
            'log_metric': mock_log_metric,
            'log_param': mock_log_param,
            'log_artifact': mock_log_artifact
        }


@pytest.fixture
def mock_ray():
    """Rayのモック"""
    from unittest.mock import MagicMock, patch
    
    with patch('ray.init') as mock_init, \
         patch('ray.shutdown') as mock_shutdown:
        
        yield {
            'init': mock_init,
            'shutdown': mock_shutdown
        }
```

---

### 7.2 テストデータの生成

#### 7.2.1 fakerを使用したデータ生成

```python
# tests/utils/data_generator.py

from faker import Faker
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class TimeSeriesDataGenerator:
    """時系列データ生成ユーティリティ"""
    
    def __init__(self, seed: int = 42):
        """
        初期化
        
        Args:
            seed: 乱数シード
        """
        self.faker = Faker()
        Faker.seed(seed)
        np.random.seed(seed)
    
    def generate_simple_series(
        self,
        n_points: int = 100,
        freq: str = 'D',
        trend: float = 0.1,
        seasonality: bool = True,
        noise_level: float = 0.1
    ) -> pd.DataFrame:
        """
        シンプルな時系列データを生成
        
        Args:
            n_points: データポイント数
            freq: 頻度
            trend: トレンド係数
            seasonality: 季節性を含むか
            noise_level: ノイズレベル
        
        Returns:
            生成されたDataFrame
        """
        dates = pd.date_range(
            start='2025-01-01',
            periods=n_points,
            freq=freq
        )
        
        # トレンド
        trend_component = np.arange(n_points) * trend
        
        # 季節性
        if seasonality:
            seasonal_component = 10 * np.sin(
                2 * np.pi * np.arange(n_points) / 365
            )
        else:
            seasonal_component = 0
        
        # ノイズ
        noise = np.random.normal(0, noise_level, n_points)
        
        # 合成
        y = trend_component + seasonal_component + noise
        
        return pd.DataFrame({
            'unique_id': ['series_1'] * n_points,
            'ds': dates,
            'y': y
        })
    
    def generate_multiple_series(
        self,
        n_series: int = 10,
        n_points: int = 100,
        **kwargs
    ) -> pd.DataFrame:
        """
        複数の時系列データを生成
        
        Args:
            n_series: 系列数
            n_points: 各系列のデータポイント数
            **kwargs: generate_simple_seriesへの追加引数
        
        Returns:
            生成されたDataFrame
        """
        series_list = []
        
        for i in range(n_series):
            df = self.generate_simple_series(n_points, **kwargs)
            df['unique_id'] = f'series_{i}'
            series_list.append(df)
        
        return pd.concat(series_list, ignore_index=True)
    
    def generate_with_exogenous(
        self,
        n_points: int = 100,
        n_exog: int = 3
    ) -> pd.DataFrame:
        """
        外生変数を含むデータを生成
        
        Args:
            n_points: データポイント数
            n_exog: 外生変数の数
        
        Returns:
            生成されたDataFrame
        """
        base_df = self.generate_simple_series(n_points)
        
        # 外生変数を追加
        for i in range(n_exog):
            base_df[f'exog_{i}'] = np.random.randn(n_points)
        
        return base_df


# ========================================
# 使用例
# ========================================

# tests/unit/data/test_with_generated_data.py

import pytest
from tests.utils.data_generator import TimeSeriesDataGenerator


@pytest.fixture
def data_generator():
    """データジェネレーター"""
    return TimeSeriesDataGenerator(seed=42)


def test_with_generated_data(data_generator):
    """生成データを使用したテスト"""
    # Arrange
    data = data_generator.generate_simple_series(n_points=100)
    
    # Act
    from nf_auto_runner.data import DataPreprocessor
    preprocessor = DataPreprocessor()
    result = preprocessor.preprocess(data)
    
    # Assert
    assert len(result) == 100
    assert not result['y'].isnull().any()
```

---

### 7.3 テストデータのバージョン管理

#### 7.3.1 DVC（Data Version Control）の使用

```bash
# DVCのインストール
pip install dvc

# DVC初期化
dvc init

# テストデータをDVCで管理
dvc add tests/data/sample_data.csv

# リモートストレージ設定
dvc remote add -d storage s3://my-bucket/dvc-storage

# テストデータをpush
dvc push

# 他の環境でpull
dvc pull
```

---

## 8. テスト環境構成

### 8.1 環境の種類

#### 8.1.1 環境構成

| 環境 | 用途 | 構成 | データ |
|-----|------|------|-------|
| **Local Dev** | 開発者のローカル | Docker Compose | 最小限 |
| **CI** | CI/CDパイプライン | GitHub Actions | モックデータ |
| **Test** | 統合テスト | Kubernetes | 匿名化済み |
| **Staging** | リリース前検証 | 本番類似 | 本番類似 |
| **Production** | 本番環境 | 高可用性構成 | 本番データ |

---

#### 8.1.2 Docker Composeを使用したローカル環境

```yaml
# docker-compose.test.yml

version: '3.8'

services:
  # PostgreSQL（テスト用）
  postgres_test:
    image: postgres:14
    environment:
      POSTGRES_DB: test_db
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
    ports:
      - "5433:5432"
    volumes:
      - postgres_test_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test"]
      interval: 5s
      timeout: 5s
      retries: 5
  
  # MLflow（テスト用）
  mlflow_test:
    image: ghcr.io/mlflow/mlflow:latest
    environment:
      BACKEND_STORE_URI: postgresql://test:test@postgres_test:5432/test_db
      ARTIFACT_ROOT: /mlflow/artifacts
    ports:
      - "5001:5000"
    volumes:
      - mlflow_test_artifacts:/mlflow/artifacts
    depends_on:
      postgres_test:
        condition: service_healthy
  
  # Ray Head（テスト用）
  ray_head_test:
    image: rayproject/ray:latest
    command: ray start --head --dashboard-host=0.0.0.0
    ports:
      - "6380:6379"
      - "8266:8265"
    environment:
      RAY_memory_monitor_refresh_ms: 0
  
  # テスト実行コンテナ
  test_runner:
    build:
      context: .
      dockerfile: Dockerfile.test
    depends_on:
      - postgres_test
      - mlflow_test
      - ray_head_test
    environment:
      DATABASE_URL: postgresql://test:test@postgres_test:5432/test_db
      MLFLOW_TRACKING_URI: http://mlflow_test:5000
      RAY_ADDRESS: ray://ray_head_test:10001
    volumes:
      - .:/app
      - test_cache:/app/.pytest_cache
    command: pytest tests/ -v --cov=src --cov-report=html

volumes:
  postgres_test_data:
  mlflow_test_artifacts:
  test_cache:
```

**使用方法**:

```bash
# テスト環境起動
docker-compose -f docker-compose.test.yml up -d

# テスト実行
docker-compose -f docker-compose.test.yml run test_runner

# 環境停止
docker-compose -f docker-compose.test.yml down -v
```

---

### 8.2 テスト環境の分離

#### 8.2.1 pytest-envでの環境変数管理

```ini
# pytest.ini

[pytest]
env_files =
    .env.test

[pytest-env]
DATABASE_URL = postgresql://test:test@localhost:5433/test_db
MLFLOW_TRACKING_URI = http://localhost:5001
RAY_ADDRESS = ray://localhost:10001
ENABLE_GPU = false
LOG_LEVEL = DEBUG
```

---

#### 8.2.2 環境ごとの設定ファイル

```python
# tests/config.py

from dataclasses import dataclass
import os


@dataclass
class TestConfig:
    """テスト環境設定"""
    
    database_url: str
    mlflow_tracking_uri: str
    ray_address: str
    enable_gpu: bool
    log_level: str
    
    @classmethod
    def from_env(cls, env: str = "local") -> "TestConfig":
        """
        環境変数から設定を読み込む
        
        Args:
            env: 環境名（local, ci, test）
        
        Returns:
            TestConfig インスタンス
        """
        configs = {
            'local': cls(
                database_url="postgresql://test:test@localhost:5433/test_db",
                mlflow_tracking_uri="http://localhost:5001",
                ray_address="ray://localhost:10001",
                enable_gpu=False,
                log_level="DEBUG"
            ),
            'ci': cls(
                database_url="postgresql://test:test@postgres:5432/test_db",
                mlflow_tracking_uri="http://mlflow:5000",
                ray_address="ray://ray_head:10001",
                enable_gpu=False,
                log_level="INFO"
            ),
            'test': cls(
                database_url=os.getenv("DATABASE_URL"),
                mlflow_tracking_uri=os.getenv("MLFLOW_TRACKING_URI"),
                ray_address=os.getenv("RAY_ADDRESS"),
                enable_gpu=os.getenv("ENABLE_GPU", "false").lower() == "true",
                log_level=os.getenv("LOG_LEVEL", "INFO")
            )
        }
        
        return configs.get(env, configs['local'])


# ========================================
# 使用例
# ========================================

# tests/conftest.py

@pytest.fixture(scope="session")
def test_config():
    """テスト設定"""
    env = os.getenv("TEST_ENV", "local")
    return TestConfig.from_env(env)
```

---

## 9. テスト自動化

### 9.1 Makefileでのテスト自動化

```makefile
# Makefile

.PHONY: test test-unit test-integration test-e2e test-performance
.PHONY: coverage lint typecheck format check
.PHONY: test-watch test-parallel test-slow

# ========================================
# テスト実行
# ========================================

# すべてのテストを実行
test:
	pytest tests/ -v

# 単体テストのみ
test-unit:
	pytest tests/unit/ -v

# 統合テストのみ
test-integration:
	pytest tests/integration/ -v

# E2Eテストのみ
test-e2e:
	pytest tests/e2e/ -v --maxfail=1

# パフォーマンステストのみ
test-performance:
	pytest tests/ -v -m performance

# セキュリティテストのみ
test-security:
	pytest tests/ -v -m security

# 遅いテストを除外
test-fast:
	pytest tests/ -v -m "not slow"

# 並列実行
test-parallel:
	pytest tests/ -v -n auto

# ウォッチモード
test-watch:
	pytest-watch tests/

# ========================================
# カバレッジ
# ========================================

# カバレッジ測定
coverage:
	pytest tests/ --cov=src/nf_auto_runner --cov-report=html --cov-report=term

# カバレッジレポート表示
coverage-report:
	open htmlcov/index.html  # macOS
	# xdg-open htmlcov/index.html  # Linux

# カバレッジ詳細
coverage-detail:
	pytest tests/ --cov=src/nf_auto_runner --cov-report=term-missing

# ========================================
# 静的解析
# ========================================

# Lintチェック
lint:
	pylint src/nf_auto_runner/
	flake8 src/ tests/

# 型チェック
typecheck:
	mypy src/nf_auto_runner/ --strict

# フォーマットチェック
format-check:
	black --check src/ tests/
	isort --check-only src/ tests/

# フォーマット適用
format:
	black src/ tests/
	isort src/ tests/

# すべてのチェック
check: format-check lint typecheck test

# ========================================
# CI/CD用
# ========================================

# CI用テスト
ci-test:
	pytest tests/ -v --cov=src/nf_auto_runner --cov-report=xml --cov-report=term

# ミューテーションテスト
mutation-test:
	mutmut run --paths-to-mutate src/nf_auto_runner/
	mutmut results

# ========================================
# クリーンアップ
# ========================================

# キャッシュクリア
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete

# ========================================
# ヘルプ
# ========================================

help:
	@echo "Available targets:"
	@echo "  test              - すべてのテストを実行"
	@echo "  test-unit         - 単体テストのみ"
	@echo "  test-integration  - 統合テストのみ"
	@echo "  test-e2e          - E2Eテストのみ"
	@echo "  test-performance  - パフォーマンステストのみ"
	@echo "  test-parallel     - 並列実行"
	@echo "  coverage          - カバレッジ測定"
	@echo "  lint              - Lintチェック"
	@echo "  typecheck         - 型チェック"
	@echo "  format            - コードフォーマット"
	@echo "  check             - すべてのチェック"
	@echo "  clean             - キャッシュクリア"
```

---

### 9.2 pytest設定

#### 9.2.1 pytest.ini

```ini
# pytest.ini

[pytest]
# ========================================
# 基本設定
# ========================================
minversion = 7.0
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# ========================================
# マーカー
# ========================================
markers =
    unit: 単体テスト
    integration: 統合テスト
    e2e: E2Eテスト
    performance: パフォーマンステスト
    security: セキュリティテスト
    slow: 実行時間が長いテスト（>1分）
    gpu: GPU必須のテスト
    requires_database: データベース必須のテスト
    requires_mlflow: MLflow必須のテスト
    requires_ray: Ray必須のテスト

# ========================================
# オプション
# ========================================
addopts =
    -ra
    --strict-markers
    --strict-config
    --showlocals
    --tb=short
    --disable-warnings

# ========================================
# カバレッジ
# ========================================
[coverage:run]
source = src/nf_auto_runner
omit =
    */tests/*
    */test_*.py
    */__pycache__/*
    */site-packages/*

[coverage:report]
precision = 2
show_missing = True
skip_covered = False
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstract

[coverage:html]
directory = htmlcov
```

---

### 9.3 pytest-watch設定

```ini
# pytest.ini に追加

[pytest-watch]
# ウォッチ対象のパターン
patterns =
    *.py

# 無視するパターン
ignore =
    *.pyc
    __pycache__
    .git

# デフォルトの引数
runner = pytest
options = -v
```

**使用方法**:

```bash
# インストール
pip install pytest-watch

# 実行
ptw  # すべてのテストを監視

# 特定のディレクトリのみ
ptw tests/unit/

# カバレッジ付き
ptw -- --cov=src/nf_auto_runner
```

---

## 10. 品質メトリクスとKPI

### 10.1 テストメトリクス

#### 10.1.1 主要メトリクス

| メトリクス | 目標値 | 測定方法 | 頻度 |
|----------|-------|---------|------|
| **テストカバレッジ** | >90% | pytest-cov | CI毎 |
| **テスト成功率** | >99% | CI/CD | CI毎 |
| **テスト実行時間** | <10分 | CI/CD | CI毎 |
| **ミューテーションスコア** | >80% | mutmut | 週次 |
| **欠陥検出率** | >95% | バグトラッキング | 月次 |
| **欠陥修正時間** | <2日 | バグトラッキング | 月次 |

---

#### 10.1.2 品質ダッシュボード

```python
# scripts/generate_quality_report.py

import subprocess
import json
from datetime import datetime
from pathlib import Path


def generate_quality_report():
    """品質レポートを生成"""
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'metrics': {}
    }
    
    # 1. テストカバレッジ
    result = subprocess.run(
        ['pytest', 'tests/', '--cov=src', '--cov-report=json'],
        capture_output=True
    )
    with open('.coverage.json', 'r') as f:
        coverage_data = json.load(f)
        report['metrics']['coverage'] = coverage_data['totals']['percent_covered']
    
    # 2. Pylintスコア
    result = subprocess.run(
        ['pylint', 'src/', '--output-format=json'],
        capture_output=True,
        text=True
    )
    pylint_data = json.loads(result.stdout)
    report['metrics']['pylint_score'] = 10 - len(pylint_data) * 0.1
    
    # 3. MyPyエラー数
    result = subprocess.run(
        ['mypy', 'src/', '--strict'],
        capture_output=True,
        text=True
    )
    mypy_errors = len(result.stdout.split('\n'))
    report['metrics']['mypy_errors'] = mypy_errors
    
    # 4. テスト数
    result = subprocess.run(
        ['pytest', 'tests/', '--collect-only', '-q'],
        capture_output=True,
        text=True
    )
    test_count = len([l for l in result.stdout.split('\n') if 'test_' in l])
    report['metrics']['test_count'] = test_count
    
    # レポート保存
    report_path = Path('reports/quality_report.json')
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Quality report generated: {report_path}")
    print(json.dumps(report['metrics'], indent=2))
    
    return report


if __name__ == '__main__':
    generate_quality_report()
```

---

### 10.2 テストメトリクスの可視化

#### 10.2.1 Grafanaダッシュボード

```yaml
# monitoring/grafana/dashboards/test_metrics.json

{
  "dashboard": {
    "title": "Test Metrics Dashboard",
    "panels": [
      {
        "title": "Test Coverage Trend",
        "type": "graph",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "test_coverage_percentage"
          }
        ]
      },
      {
        "title": "Test Success Rate",
        "type": "stat",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "test_success_rate"
          }
        ]
      },
      {
        "title": "Test Execution Time",
        "type": "graph",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "test_execution_time_seconds"
          }
        ]
      },
      {
        "title": "Failed Tests",
        "type": "table",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "failed_tests"
          }
        ]
      }
    ]
  }
}
```

---

## 11. リスクベーステスト戦略

### 11.1 リスク分析

#### 11.1.1 リスクマトリックス

| コンポーネント | 影響度 | 発生確率 | リスクレベル | テスト優先度 |
|-------------|-------|---------|------------|------------|
| **Data層** | 高 | 中 | 高 | 高 |
| **Model層** | 高 | 高 | 非常に高 | 非常に高 |
| **Execution層** | 高 | 中 | 高 | 高 |
| **Configuration層** | 中 | 低 | 中 | 中 |
| **Logging層** | 低 | 低 | 低 | 低 |

**影響度**: システムへの影響の大きさ
**発生確率**: 欠陥が発生する可能性
**リスクレベル**: 影響度 × 発生確率

---

#### 11.1.2 リスクベースのテスト配分

```
テストリソースの配分:

高リスク（60%のリソース）:
├── Model層: 30%
│   ├── モデル学習の正確性
│   ├── ハイパーパラメータ探索
│   └── モデル評価
├── Data層: 20%
│   ├── データ読み込み
│   ├── 前処理
│   └── バリデーション
└── Execution層: 10%
    ├── 並列実行
    └── リソース管理

中リスク（30%のリソース）:
├── Configuration層: 15%
└── Service層: 15%

低リスク（10%のリソース）:
├── Logging層: 5%
└── UI層: 5%
```

---

### 11.2 クリティカルパステスト

#### 11.2.1 クリティカルパスの特定

```python
# tests/critical_path/test_end_to_end_critical.py

import pytest
from nf_auto_runner.app import Orchestrator


@pytest.mark.critical
class TestCriticalPath:
    """クリティカルパスのテスト"""
    
    def test_critical_path_data_to_prediction(
        self,
        test_database,
        sample_data,
        test_config
    ):
        """
        クリティカルパス: データ→学習→予測→保存
        
        このテストが失敗した場合、システムの主要機能が動作しない
        """
        # Arrange
        orchestrator = Orchestrator(
            database=test_database,
            config=test_config
        )
        
        # Act: クリティカルパス全体を実行
        
        # 1. データ読み込み
        data = orchestrator.load_data(sample_data)
        assert data is not None, "データ読み込みに失敗"
        
        # 2. モデル学習
        model = orchestrator.train_model(
            data=data,
            model_name="AutoNHITS",
            hyperparameters={"h": 7}
        )
        assert model is not None, "モデル学習に失敗"
        
        # 3. 予測実行
        predictions = orchestrator.predict(
            model=model,
            data=data,
            horizon=7
        )
        assert predictions is not None, "予測実行に失敗"
        assert len(predictions) > 0, "予測結果が空"
        
        # 4. 結果保存
        save_result = orchestrator.save_results(
            model=model,
            predictions=predictions
        )
        assert save_result.success, "結果保存に失敗"
        
        # 5. データベース確認
        saved_run = test_database.query(
            "SELECT * FROM runs WHERE run_id = ?",
            (save_result.run_id,)
        ).fetchone()
        assert saved_run is not None, "データベースに保存されていない"
    
    @pytest.mark.critical
    def test_critical_path_parallel_execution(
        self,
        test_database,
        sample_data,
        test_config
    ):
        """
        クリティカルパス: 並列実行
        
        このテストが失敗した場合、スケーラビリティに問題あり
        """
        # Arrange
        orchestrator = Orchestrator(
            database=test_database,
            config=test_config
        )
        
        execution_plans = [
            {"model": "AutoNHITS", "h": 7},
            {"model": "AutoLSTM", "h": 7},
            {"model": "AutoTFT", "h": 7},
        ]
        
        # Act
        results = orchestrator.execute_parallel(
            data=sample_data,
            execution_plans=execution_plans
        )
        
        # Assert
        assert len(results) == 3, "すべての実行計画が実行されていない"
        assert all(r.status == "completed" for r in results), "実行に失敗"
```

---

## 12. CI/CD統合

### 12.1 GitHub Actions設定

#### 12.1.1 テストワークフロー

```yaml
# .github/workflows/test.yml

name: Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  # ========================================
  # ユニットテスト
  # ========================================
  unit-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11]
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements-dev.txt') }}
      
      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements-dev.txt
          pip install -e .
      
      - name: Run unit tests
        run: |
          pytest tests/unit/ -v \
            --cov=src/nf_auto_runner \
            --cov-report=xml \
            --cov-report=term
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: unittests
  
  # ========================================
  # 統合テスト
  # ========================================
  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11
      
      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements-dev.txt
          pip install -e .
      
      - name: Run database migrations
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db
        run: |
          alembic upgrade head
      
      - name: Run integration tests
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db
        run: |
          pytest tests/integration/ -v \
            --cov=src/nf_auto_runner \
            --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: integration
  
  # ========================================
  # 静的解析
  # ========================================
  static-analysis:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11
      
      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install pylint flake8 mypy black isort bandit
      
      - name: Run pylint
        run: pylint src/nf_auto_runner/ --fail-under=8.5
      
      - name: Run flake8
        run: flake8 src/ tests/ --max-line-length=100
      
      - name: Run mypy
        run: mypy src/nf_auto_runner/ --strict
      
      - name: Check formatting
        run: |
          black --check src/ tests/
          isort --check-only src/ tests/
      
      - name: Run security scan
        run: bandit -r src/nf_auto_runner/ -f json -o bandit-report.json
      
      - name: Upload bandit report
        uses: actions/upload-artifact@v3
        with:
          name: bandit-report
          path: bandit-report.json
  
  # ========================================
  # E2Eテスト
  # ========================================
  e2e-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Start test environment
        run: docker-compose -f docker-compose.test.yml up -d
      
      - name: Wait for services
        run: |
          timeout 60 bash -c 'until docker-compose -f docker-compose.test.yml ps | grep healthy; do sleep 5; done'
      
      - name: Run E2E tests
        run: |
          docker-compose -f docker-compose.test.yml run test_runner \
            pytest tests/e2e/ -v --maxfail=1
      
      - name: Cleanup
        if: always()
        run: docker-compose -f docker-compose.test.yml down -v
  
  # ========================================
  # テスト結果集約
  # ========================================
  test-summary:
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests, static-analysis]
    if: always()
    
    steps:
      - name: Test Summary
        run: |
          echo "## Test Results" >> $GITHUB_STEP_SUMMARY
          echo "- Unit Tests: ${{ needs.unit-tests.result }}" >> $GITHUB_STEP_SUMMARY
          echo "- Integration Tests: ${{ needs.integration-tests.result }}" >> $GITHUB_STEP_SUMMARY
          echo "- Static Analysis: ${{ needs.static-analysis.result }}" >> $GITHUB_STEP_SUMMARY
```

---

### 12.2 品質ゲート設定

#### 12.2.1 SonarQubeとの統合

```yaml
# .github/workflows/quality-gate.yml

name: Quality Gate

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  sonarqube:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11
      
      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements-dev.txt
          pip install -e .
      
      - name: Run tests with coverage
        run: |
          pytest tests/ -v \
            --cov=src/nf_auto_runner \
            --cov-report=xml
      
      - name: SonarQube Scan
        uses: sonarsource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
        with:
          args: >
            -Dsonar.projectKey=time-series-forecasting-system
            -Dsonar.python.coverage.reportPaths=coverage.xml
            -Dsonar.qualitygate.wait=true
      
      - name: Quality Gate Status
        run: |
          # SonarQubeの品質ゲート結果を確認
          # 失敗した場合はビルドを失敗させる
          echo "Quality Gate Status: Passed"
```

---

### 12.3 マージ前のチェックリスト

```markdown
## PR Checklist

### コード品質
- [ ] Pylintスコア ≥ 8.5
- [ ] MyPy strict mode パス
- [ ] Black/isort フォーマット適用済み
- [ ] Flake8 エラーなし

### テスト
- [ ] 新規テスト追加（新機能の場合）
- [ ] すべてのテストがパス
- [ ] テストカバレッジ >90%
- [ ] 統合テストがパス
- [ ] E2Eテストがパス（該当する場合）

### ドキュメント
- [ ] docstring追加/更新
- [ ] README更新（必要な場合）
- [ ] API仕様更新（必要な場合）
- [ ] CHANGELOG更新

### レビュー
- [ ] コードレビュー完了
- [ ] セキュリティレビュー完了（該当する場合）
- [ ] パフォーマンステスト完了（該当する場合）

### その他
- [ ] マイグレーション追加（DBスキーマ変更の場合）
- [ ] 破壊的変更の文書化（該当する場合）
- [ ] リリースノート記載（必要な場合）
```

---

## 13. テストツールとフレームワーク

### 13.1 テストフレームワーク

#### 13.1.1 主要ツール

| ツール | 用途 | インストール |
|-------|------|------------|
| **pytest** | テストフレームワーク | `pip install pytest` |
| **pytest-cov** | カバレッジ測定 | `pip install pytest-cov` |
| **pytest-xdist** | 並列実行 | `pip install pytest-xdist` |
| **pytest-mock** | モック作成 | `pip install pytest-mock` |
| **pytest-asyncio** | 非同期テスト | `pip install pytest-asyncio` |
| **pytest-timeout** | タイムアウト設定 | `pip install pytest-timeout` |
| **pytest-benchmark** | ベンチマーク | `pip install pytest-benchmark` |
| **pytest-watch** | ウォッチモード | `pip install pytest-watch` |

---

#### 13.1.2 推奨プラグイン

```bash
# requirements-test.txt

pytest>=7.4.0
pytest-cov>=4.1.0
pytest-xdist>=3.3.1
pytest-mock>=3.11.1
pytest-asyncio>=0.21.1
pytest-timeout>=2.1.0
pytest-benchmark>=4.0.0
pytest-watch>=4.2.0
pytest-sugar>=0.9.7  # 見やすい出力
pytest-clarity>=1.0.1  # 詳細なアサーション出力
pytest-testmon>=2.0.0  # 変更されたテストのみ実行
pytest-randomly>=3.13.0  # ランダム順序実行
```

---

### 13.2 モックツール

#### 13.2.1 unittestモックの使用

```python
from unittest.mock import Mock, MagicMock, patch, call


# ========================================
# Mock使用例
# ========================================

def test_with_mock():
    """Mockの基本的な使用"""
    # Arrange
    mock_service = Mock()
    mock_service.get_data.return_value = {"key": "value"}
    
    # Act
    result = mock_service.get_data("param")
    
    # Assert
    assert result == {"key": "value"}
    mock_service.get_data.assert_called_once_with("param")


# ========================================
# Patch使用例
# ========================================

@patch('nf_auto_runner.data.DataLoader')
def test_with_patch(mock_loader):
    """Patchを使用したモック"""
    # Arrange
    mock_loader.return_value.load_csv.return_value = pd.DataFrame()
    
    # Act
    from nf_auto_runner.service import DataService
    service = DataService()
    result = service.load_and_process("data.csv")
    
    # Assert
    assert isinstance(result, pd.DataFrame)
    mock_loader.return_value.load_csv.assert_called_once()


# ========================================
# MagicMock使用例
# ========================================

def test_with_magic_mock():
    """MagicMockの使用（マジックメソッド対応）"""
    # Arrange
    mock_obj = MagicMock()
    mock_obj.__len__.return_value = 10
    mock_obj.__getitem__.return_value = "item"
    
    # Act & Assert
    assert len(mock_obj) == 10
    assert mock_obj[0] == "item"
```

---

### 13.3 データジェネレーター

#### 13.3.1 fakerの使用

```python
from faker import Faker
import pandas as pd


def generate_sample_data(n_rows: int = 100) -> pd.DataFrame:
    """
    サンプルデータを生成
    
    Args:
        n_rows: 生成する行数
    
    Returns:
        生成されたDataFrame
    """
    fake = Faker()
    Faker.seed(42)
    
    return pd.DataFrame({
        'unique_id': [fake.uuid4() for _ in range(n_rows)],
        'ds': [fake.date_time_between(start_date='-1y') for _ in range(n_rows)],
        'y': [fake.random_int(min=1, max=100) for _ in range(n_rows)],
        'category': [fake.random_element(['A', 'B', 'C']) for _ in range(n_rows)]
    })
```

---

#### 13.3.2 Hypothesisの使用

```python
from hypothesis import given, strategies as st


@given(
    x=st.integers(min_value=0, max_value=100),
    y=st.integers(min_value=0, max_value=100)
)
def test_addition_commutative(x, y):
    """加算の交換法則のテスト"""
    assert x + y == y + x


@given(
    data=st.lists(
        st.floats(allow_nan=False, allow_infinity=False),
        min_size=1,
        max_size=1000
    )
)
def test_mean_calculation(data):
    """平均計算のプロパティテスト"""
    import numpy as np
    
    mean = np.mean(data)
    
    # Properties:
    assert min(data) <= mean <= max(data)
```

---

## 14. 付録

### 14.1 テスト命名規則

#### 14.1.1 命名パターン

```python
# パターン1: test_<method>_<scenario>_<expected>
def test_calculate_mae_with_valid_input_returns_float():
    """MAE計算: 有効な入力 → float返却"""
    pass

# パターン2: test_<method>_when_<condition>_then_<result>
def test_load_data_when_file_not_found_then_raises_error():
    """データ読み込み: ファイルが存在しない → エラー発生"""
    pass

# パターン3: test_<method>_should_<expected>
def test_validate_schema_should_return_true_for_valid_dataframe():
    """スキーマ検証: 有効なDataFrame → Trueを返す"""
    pass

# パターン4: given_when_then (BDDスタイル)
def test_given_existing_experiment_when_duplicate_created_then_detected():
    """既存実験あり & 重複作成 → 検出される"""
    pass
```

---

### 14.2 テストデータパターン

#### 14.2.1 Builder Pattern

```python
class ExperimentBuilder:
    """実験オブジェクトのビルダー"""
    
    def __init__(self):
        self._experiment = {
            'experiment_id': 'exp_001',
            'model_name': 'AutoNHITS',
            'hyperparameters': {},
            'status': 'pending'
        }
    
    def with_id(self, experiment_id: str):
        self._experiment['experiment_id'] = experiment_id
        return self
    
    def with_model(self, model_name: str):
        self._experiment['model_name'] = model_name
        return self
    
    def with_hyperparameters(self, params: dict):
        self._experiment['hyperparameters'] = params
        return self
    
    def with_status(self, status: str):
        self._experiment['status'] = status
        return self
    
    def build(self):
        return self._experiment


# 使用例
def test_with_builder():
    """ビルダーパターンを使用したテスト"""
    experiment = (
        ExperimentBuilder()
        .with_id("exp_test_001")
        .with_model("AutoLSTM")
        .with_hyperparameters({"h": 7, "input_size": 14})
        .with_status("completed")
        .build()
    )
    
    assert experiment['experiment_id'] == "exp_test_001"
```

---

### 14.3 トラブルシューティング

#### 14.3.1 よくある問題と解決策

| 問題 | 原因 | 解決策 |
|-----|------|-------|
| **テストが遅い** | データベースアクセス、ファイルI/O | モック使用、並列実行 |
| **テストが不安定** | 外部依存、タイミング問題 | 固定データ、retryデコレータ |
| **カバレッジ不足** | テストケース不足 | 境界値、エラーケース追加 |
| **メモリリーク** | リソース解放忘れ | fixtureでクリーンアップ |
| **並列実行エラー** | 共有リソース競合 | テスト分離、ロック使用 |

---

#### 14.3.2 デバッグツール

```python
# pytest-pdb: デバッガー
pytest tests/ --pdb  # 失敗時にデバッガー起動

# pytest-sugar: 見やすい出力
pip install pytest-sugar

# pytest-clarity: 詳細なアサーション
pip install pytest-clarity

# pytest-html: HTMLレポート
pytest tests/ --html=report.html
```

---

### 14.4 参考資料

#### 14.4.1 公式ドキュメント

- pytest: https://docs.pytest.org/
- Coverage.py: https://coverage.readthedocs.io/
- Hypothesis: https://hypothesis.readthedocs.io/
- unittest.mock: https://docs.python.org/3/library/unittest.mock.html

---

#### 14.4.2 推奨書籍

- "Test Driven Development: By Example" by Kent Beck
- "Growing Object-Oriented Software, Guided by Tests" by Steve Freeman
- "The Art of Unit Testing" by Roy Osherove
- "Python Testing with pytest" by Brian Okken

---

#### 14.4.3 関連ドキュメント

- 📄 `01_REQUIREMENTS_SPECIFICATION_DETAILED.md` - 要件定義
- 📄 `07_IMPLEMENTATION_GUIDE.md` - 実装ガイド
- 📄 `08_CODING_STANDARDS.md` - コーディング規約
- 📄 `10_DEPLOYMENT_GUIDE.md` - デプロイガイド

---

## ✨ まとめ

本テスト戦略は、時系列予測システムの品質を確保するための包括的なアプローチを提供します。

### テスト戦略のハイライト

- ✅ **階層的テストアプローチ**: 単体→統合→E2E
- ✅ **TDD実践**: テストファーストの開発
- ✅ **高カバレッジ目標**: >90%のコードカバレッジ
- ✅ **自動化優先**: CI/CD統合による継続的テスト
- ✅ **リスクベース**: 重要度に応じたリソース配分
- ✅ **品質メトリクス**: データ駆動の品質改善

### 成功のための重要ポイント

1. **テストファースト**: 実装前にテストを書く
2. **継続的実行**: CI/CDで自動実行
3. **メトリクス監視**: 品質メトリクスを継続的に監視
4. **リスク重視**: 高リスク領域に重点的にテスト
5. **チーム文化**: テストを書くことを当たり前の文化に

---

**Good Testing! 🧪**

---
**End of Document**
