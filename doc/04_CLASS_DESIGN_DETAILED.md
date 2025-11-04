# 詳細クラス設計書
**Detailed Class Design for Time Series Forecasting System**

---

## 📋 ドキュメント情報

| 項目 | 内容 |
|-----|------|
| **ドキュメントタイトル** | 時系列予測システム 詳細クラス設計書 |
| **バージョン** | v1.0.0 |
| **作成日** | 2025-11-03 |
| **最終更新日** | 2025-11-03 |
| **対象システム** | NeuralForecast Auto Runner + Time Series Forecasting System |

---

## 目次

1. [Layer 1: Configuration層](#layer-1-configuration層)
2. [Layer 2: Data層](#layer-2-data層)
3. [Layer 3: Model Discovery層](#layer-3-model-discovery層)
4. [Layer 4: Hyperparameter層](#layer-4-hyperparameter層)
5. [Layer 5: Execution Plan層](#layer-5-execution-plan層)
6. [Layer 6: Execution層](#layer-6-execution層)
7. [Layer 7: Artifact Management層](#layer-7-artifact-management層)
8. [Layer 8: Logging層](#layer-8-logging層)
9. [Layer 9: Application層](#layer-9-application層)
10. [共通基底クラス・ユーティリティ](#共通基底クラスユーティリティ)

---

## Layer 1: Configuration層

### 1.1 Config (基底クラス)

#### 1.1.1 クラス定義

```python
"""
Configuration基底クラス

すべての設定クラスの抽象基底クラス。
不変性(frozen=True)を保証し、環境変数からの読み込み、検証、
シリアライズ機能を提供する。
"""

from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, TypeVar, Type
from pathlib import Path
import json
import os

T = TypeVar('T', bound='Config')

@dataclass(frozen=True)
class Config(ABC):
    """
    設定基底クラス
    
    Attributes:
        None (抽象クラスのため、派生クラスで定義)
    
    Class Methods:
        from_env: 環境変数から設定を構築
        from_dict: 辞書から設定を構築
        from_json: JSON文字列から設定を構築
        from_json_file: JSONファイルから設定を構築
    
    Instance Methods:
        validate: 設定の妥当性検証
        to_dict: 辞書に変換
        to_json: JSON文字列に変換
        save_to_file: ファイルに保存
    
    Example:
        >>> class MyConfig(Config):
        ...     value: int
        ...     
        ...     @classmethod
        ...     def from_env(cls) -> 'MyConfig':
        ...         return cls(value=int(os.getenv('VALUE', '42')))
        >>> 
        >>> config = MyConfig.from_env()
        >>> config.value
        42
    """
    
    @classmethod
    @abstractmethod
    def from_env(cls: Type[T]) -> T:
        """
        環境変数から設定を構築
        
        Returns:
            T: 設定インスタンス
            
        Raises:
            EnvironmentError: 必須環境変数が存在しない
            ValueError: 環境変数の値が不正
            
        Note:
            派生クラスで必ず実装すること
        """
        pass
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        辞書から設定を構築
        
        Args:
            data: 設定データの辞書
            
        Returns:
            T: 設定インスタンス
            
        Raises:
            TypeError: データ型が不正
            ValueError: データ値が不正
            
        Example:
            >>> config = MyConfig.from_dict({"value": 100})
            >>> config.value
            100
        """
        # Pathオブジェクトの変換
        converted_data = {}
        for key, value in data.items():
            if isinstance(value, str) and key.endswith(('_path', '_dir')):
                converted_data[key] = Path(value)
            else:
                converted_data[key] = value
        
        return cls(**converted_data)
    
    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        """
        JSON文字列から設定を構築
        
        Args:
            json_str: JSON文字列
            
        Returns:
            T: 設定インスタンス
            
        Raises:
            json.JSONDecodeError: JSONパースエラー
            
        Example:
            >>> config = MyConfig.from_json('{"value": 200}')
            >>> config.value
            200
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_json_file(cls: Type[T], file_path: Path) -> T:
        """
        JSONファイルから設定を構築
        
        Args:
            file_path: JSONファイルパス
            
        Returns:
            T: 設定インスタンス
            
        Raises:
            FileNotFoundError: ファイルが存在しない
            json.JSONDecodeError: JSONパースエラー
            
        Example:
            >>> config = MyConfig.from_json_file(Path("config.json"))
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return cls.from_json(f.read())
    
    def validate(self) -> None:
        """
        設定の妥当性検証
        
        Raises:
            ValueError: 設定値が不正
            
        Note:
            派生クラスでオーバーライドして独自の検証を追加可能
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        辞書に変換
        
        Returns:
            Dict[str, Any]: 設定の辞書表現
            
        Example:
            >>> config = MyConfig(value=300)
            >>> config.to_dict()
            {'value': 300}
        """
        result = {}
        for key, value in asdict(self).items():
            if isinstance(value, Path):
                result[key] = str(value)
            else:
                result[key] = value
        return result
    
    def to_json(self, indent: Optional[int] = 2) -> str:
        """
        JSON文字列に変換
        
        Args:
            indent: インデント幅（Noneで改行なし）
            
        Returns:
            str: JSON文字列
            
        Example:
            >>> config = MyConfig(value=400)
            >>> config.to_json()
            '{\\n  "value": 400\\n}'
        """
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def save_to_file(self, file_path: Path, indent: Optional[int] = 2) -> None:
        """
        ファイルに保存
        
        Args:
            file_path: 保存先ファイルパス
            indent: インデント幅
            
        Raises:
            IOError: ファイル書き込みエラー
            
        Example:
            >>> config = MyConfig(value=500)
            >>> config.save_to_file(Path("config.json"))
        """
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json(indent=indent))
```

#### 1.1.2 テストコード

```python
"""Config基底クラスのテスト"""

import pytest
import tempfile
from pathlib import Path
import os

class TestConfig:
    """Config基底クラスのテストスイート"""
    
    def test_from_env(self, monkeypatch):
        """環境変数からの読み込みテスト"""
        monkeypatch.setenv('TEST_VALUE', '42')
        
        @dataclass(frozen=True)
        class TestConfig(Config):
            value: int
            
            @classmethod
            def from_env(cls) -> 'TestConfig':
                return cls(value=int(os.getenv('TEST_VALUE', '0')))
        
        config = TestConfig.from_env()
        assert config.value == 42
    
    def test_from_dict(self):
        """辞書からの読み込みテスト"""
        @dataclass(frozen=True)
        class TestConfig(Config):
            value: int
            name: str
            
            @classmethod
            def from_env(cls) -> 'TestConfig':
                return cls(value=0, name='')
        
        config = TestConfig.from_dict({"value": 100, "name": "test"})
        assert config.value == 100
        assert config.name == "test"
    
    def test_from_json(self):
        """JSON文字列からの読み込みテスト"""
        @dataclass(frozen=True)
        class TestConfig(Config):
            value: int
            
            @classmethod
            def from_env(cls) -> 'TestConfig':
                return cls(value=0)
        
        config = TestConfig.from_json('{"value": 200}')
        assert config.value == 200
    
    def test_from_json_file(self):
        """JSONファイルからの読み込みテスト"""
        @dataclass(frozen=True)
        class TestConfig(Config):
            value: int
            
            @classmethod
            def from_env(cls) -> 'TestConfig':
                return cls(value=0)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"value": 300}')
            temp_path = Path(f.name)
        
        try:
            config = TestConfig.from_json_file(temp_path)
            assert config.value == 300
        finally:
            temp_path.unlink()
    
    def test_to_dict(self):
        """辞書への変換テスト"""
        @dataclass(frozen=True)
        class TestConfig(Config):
            value: int
            path: Path
            
            @classmethod
            def from_env(cls) -> 'TestConfig':
                return cls(value=0, path=Path('.'))
        
        config = TestConfig(value=400, path=Path('/tmp'))
        result = config.to_dict()
        assert result['value'] == 400
        assert result['path'] == '/tmp'
    
    def test_to_json(self):
        """JSON文字列への変換テスト"""
        @dataclass(frozen=True)
        class TestConfig(Config):
            value: int
            
            @classmethod
            def from_env(cls) -> 'TestConfig':
                return cls(value=0)
        
        config = TestConfig(value=500)
        json_str = config.to_json()
        assert '"value": 500' in json_str
    
    def test_save_to_file(self):
        """ファイル保存テスト"""
        @dataclass(frozen=True)
        class TestConfig(Config):
            value: int
            
            @classmethod
            def from_env(cls) -> 'TestConfig':
                return cls(value=0)
        
        config = TestConfig(value=600)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "config.json"
            config.save_to_file(file_path)
            
            assert file_path.exists()
            
            # 読み込んで検証
            loaded = TestConfig.from_json_file(file_path)
            assert loaded.value == 600
    
    def test_immutability(self):
        """不変性のテスト"""
        @dataclass(frozen=True)
        class TestConfig(Config):
            value: int
            
            @classmethod
            def from_env(cls) -> 'TestConfig':
                return cls(value=0)
        
        config = TestConfig(value=700)
        
        with pytest.raises(Exception):  # dataclassのfrozen=Trueで例外
            config.value = 800
```

---

### 1.2 PathConfig

#### 1.2.1 クラス定義

```python
"""
PathConfig: パス関連の設定

ファイルパス、ディレクトリパスの管理を担当。
環境変数から読み込み、自動的にディレクトリを作成する。
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import os

@dataclass(frozen=True)
class PathConfig(Config):
    """
    パス設定
    
    Attributes:
        data_csv: 入力データCSVファイルパス
        output_dir: 出力ディレクトリ
        log_dir: ログディレクトリ
        project_root: プロジェクトルートディレクトリ
        model_dir: モデル保存ディレクトリ
        artifact_dir: アーティファクト保存ディレクトリ
        checkpoint_dir: チェックポイント保存ディレクトリ
        plot_dir: プロット保存ディレクトリ
    
    Environment Variables:
        NF_DATA_CSV: データCSVパス (default: ./data.csv)
        NF_OUTPUT_DIR: 出力ディレクトリ (default: ./nf_auto_runs)
        NF_LOG_DIR: ログディレクトリ (default: ./nf_auto_runs/logs)
        NF_MODEL_DIR: モデルディレクトリ (default: ./nf_auto_runs/models)
        NF_ARTIFACT_DIR: アーティファクトディレクトリ (default: ./nf_auto_runs/artifacts)
        NF_CHECKPOINT_DIR: チェックポイントディレクトリ (default: ./nf_auto_runs/checkpoints)
        NF_PLOT_DIR: プロットディレクトリ (default: ./nf_auto_runs/plots)
    
    Example:
        >>> config = PathConfig.from_env()
        >>> config.data_csv
        PosixPath('./data.csv')
        >>> config.output_dir
        PosixPath('./nf_auto_runs')
    """
    
    data_csv: Path
    output_dir: Path
    log_dir: Path
    project_root: Path
    model_dir: Path
    artifact_dir: Path
    checkpoint_dir: Path
    plot_dir: Path
    
    @classmethod
    def from_env(cls) -> 'PathConfig':
        """
        環境変数から設定を構築
        
        Returns:
            PathConfig: パス設定インスタンス
            
        Example:
            >>> config = PathConfig.from_env()
            >>> isinstance(config.data_csv, Path)
            True
        """
        project_root = Path(__file__).resolve().parent.parent
        output_dir = Path(os.getenv('NF_OUTPUT_DIR', './nf_auto_runs'))
        
        return cls(
            data_csv=Path(os.getenv('NF_DATA_CSV', './data.csv')),
            output_dir=output_dir,
            log_dir=Path(os.getenv('NF_LOG_DIR', str(output_dir / 'logs'))),
            project_root=project_root,
            model_dir=Path(os.getenv('NF_MODEL_DIR', str(output_dir / 'models'))),
            artifact_dir=Path(os.getenv('NF_ARTIFACT_DIR', str(output_dir / 'artifacts'))),
            checkpoint_dir=Path(os.getenv('NF_CHECKPOINT_DIR', str(output_dir / 'checkpoints'))),
            plot_dir=Path(os.getenv('NF_PLOT_DIR', str(output_dir / 'plots'))),
        )
    
    def __post_init__(self):
        """
        初期化後処理: ディレクトリの作成
        
        Note:
            frozen=Trueでもobject.__setattr__で変更可能だが、
            ここではディレクトリ作成のみ行う
        """
        # ディレクトリの作成
        for dir_path in [
            self.output_dir,
            self.log_dir,
            self.model_dir,
            self.artifact_dir,
            self.checkpoint_dir,
            self.plot_dir,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> None:
        """
        設定の妥当性検証
        
        Raises:
            ValueError: パスが不正
        """
        # data_csvの親ディレクトリが存在するか
        if not self.data_csv.parent.exists():
            raise ValueError(f"Data CSV parent directory does not exist: {self.data_csv.parent}")
        
        # すべてのディレクトリが作成可能か（書き込み権限チェック）
        for dir_path in [self.output_dir, self.log_dir, self.model_dir]:
            if dir_path.exists() and not os.access(dir_path, os.W_OK):
                raise ValueError(f"Directory is not writable: {dir_path}")
    
    def get_run_dir(self, run_id: str) -> Path:
        """
        特定のRunのディレクトリパスを取得
        
        Args:
            run_id: Run ID
            
        Returns:
            Path: Runディレクトリパス
            
        Example:
            >>> config = PathConfig.from_env()
            >>> run_dir = config.get_run_dir("abc123")
            >>> run_dir
            PosixPath('./nf_auto_runs/runs/abc123')
        """
        run_dir = self.output_dir / "runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir
    
    def get_model_path(self, run_id: str, model_name: str) -> Path:
        """
        モデルファイルパスを取得
        
        Args:
            run_id: Run ID
            model_name: モデル名
            
        Returns:
            Path: モデルファイルパス
            
        Example:
            >>> config = PathConfig.from_env()
            >>> model_path = config.get_model_path("abc123", "AutoNHITS")
            >>> model_path
            PosixPath('./nf_auto_runs/models/abc123_AutoNHITS.pth')
        """
        return self.model_dir / f"{run_id}_{model_name}.pth"
    
    def get_log_path(self, run_id: str) -> Path:
        """
        ログファイルパスを取得
        
        Args:
            run_id: Run ID
            
        Returns:
            Path: ログファイルパス
            
        Example:
            >>> config = PathConfig.from_env()
            >>> log_path = config.get_log_path("abc123")
            >>> log_path
            PosixPath('./nf_auto_runs/logs/abc123.jsonl')
        """
        return self.log_dir / f"{run_id}.jsonl"
```

#### 1.2.2 テストコード

```python
"""PathConfigのテスト"""

import pytest
import tempfile
from pathlib import Path
import os

class TestPathConfig:
    """PathConfigのテストスイート"""
    
    def test_from_env_default(self, monkeypatch):
        """デフォルト値での環境変数読み込みテスト"""
        # 環境変数をクリア
        for key in ['NF_DATA_CSV', 'NF_OUTPUT_DIR', 'NF_LOG_DIR']:
            monkeypatch.delenv(key, raising=False)
        
        config = PathConfig.from_env()
        
        assert config.data_csv == Path('./data.csv')
        assert config.output_dir == Path('./nf_auto_runs')
        assert config.log_dir == Path('./nf_auto_runs/logs')
    
    def test_from_env_custom(self, monkeypatch):
        """カスタム値での環境変数読み込みテスト"""
        monkeypatch.setenv('NF_DATA_CSV', '/custom/data.csv')
        monkeypatch.setenv('NF_OUTPUT_DIR', '/custom/output')
        
        config = PathConfig.from_env()
        
        assert config.data_csv == Path('/custom/data.csv')
        assert config.output_dir == Path('/custom/output')
    
    def test_directory_creation(self):
        """ディレクトリ自動作成のテスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            
            config = PathConfig(
                data_csv=Path(tmpdir) / "data.csv",
                output_dir=output_dir,
                log_dir=output_dir / "logs",
                project_root=Path(tmpdir),
                model_dir=output_dir / "models",
                artifact_dir=output_dir / "artifacts",
                checkpoint_dir=output_dir / "checkpoints",
                plot_dir=output_dir / "plots",
            )
            
            # ディレクトリが作成されているか
            assert config.output_dir.exists()
            assert config.log_dir.exists()
            assert config.model_dir.exists()
            assert config.artifact_dir.exists()
    
    def test_validate_success(self):
        """検証成功のテスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            config = PathConfig(
                data_csv=tmpdir_path / "data.csv",
                output_dir=tmpdir_path / "output",
                log_dir=tmpdir_path / "output" / "logs",
                project_root=tmpdir_path,
                model_dir=tmpdir_path / "output" / "models",
                artifact_dir=tmpdir_path / "output" / "artifacts",
                checkpoint_dir=tmpdir_path / "output" / "checkpoints",
                plot_dir=tmpdir_path / "output" / "plots",
            )
            
            # 例外が発生しないことを確認
            config.validate()
    
    def test_validate_failure_nonexistent_parent(self):
        """検証失敗のテスト（親ディレクトリが存在しない）"""
        config = PathConfig(
            data_csv=Path('/nonexistent/dir/data.csv'),
            output_dir=Path('/tmp/output'),
            log_dir=Path('/tmp/output/logs'),
            project_root=Path('/tmp'),
            model_dir=Path('/tmp/output/models'),
            artifact_dir=Path('/tmp/output/artifacts'),
            checkpoint_dir=Path('/tmp/output/checkpoints'),
            plot_dir=Path('/tmp/output/plots'),
        )
        
        with pytest.raises(ValueError, match="parent directory does not exist"):
            config.validate()
    
    def test_get_run_dir(self):
        """Runディレクトリ取得のテスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = PathConfig(
                data_csv=Path(tmpdir) / "data.csv",
                output_dir=Path(tmpdir),
                log_dir=Path(tmpdir) / "logs",
                project_root=Path(tmpdir),
                model_dir=Path(tmpdir) / "models",
                artifact_dir=Path(tmpdir) / "artifacts",
                checkpoint_dir=Path(tmpdir) / "checkpoints",
                plot_dir=Path(tmpdir) / "plots",
            )
            
            run_dir = config.get_run_dir("test_run_123")
            
            assert run_dir.exists()
            assert run_dir.name == "test_run_123"
            assert run_dir.parent.name == "runs"
    
    def test_get_model_path(self):
        """モデルパス取得のテスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = PathConfig(
                data_csv=Path(tmpdir) / "data.csv",
                output_dir=Path(tmpdir),
                log_dir=Path(tmpdir) / "logs",
                project_root=Path(tmpdir),
                model_dir=Path(tmpdir) / "models",
                artifact_dir=Path(tmpdir) / "artifacts",
                checkpoint_dir=Path(tmpdir) / "checkpoints",
                plot_dir=Path(tmpdir) / "plots",
            )
            
            model_path = config.get_model_path("run123", "AutoNHITS")
            
            assert model_path.name == "run123_AutoNHITS.pth"
            assert model_path.parent == config.model_dir
    
    def test_get_log_path(self):
        """ログパス取得のテスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = PathConfig(
                data_csv=Path(tmpdir) / "data.csv",
                output_dir=Path(tmpdir),
                log_dir=Path(tmpdir) / "logs",
                project_root=Path(tmpdir),
                model_dir=Path(tmpdir) / "models",
                artifact_dir=Path(tmpdir) / "artifacts",
                checkpoint_dir=Path(tmpdir) / "checkpoints",
                plot_dir=Path(tmpdir) / "plots",
            )
            
            log_path = config.get_log_path("run456")
            
            assert log_path.name == "run456.jsonl"
            assert log_path.parent == config.log_dir
```

---

### 1.3 ExecutionConfig

#### 1.3.1 クラス定義

```python
"""
ExecutionConfig: 実行設定

実行パラメータ（並列度、試行回数、ハイパーパラメータなど）を管理。
"""

from dataclasses import dataclass
from typing import Optional
import os

@dataclass(frozen=True)
class ExecutionConfig(Config):
    """
    実行設定
    
    Attributes:
        random_state: 乱数シード
        trial_num_samples: Optuna試行回数
        trial_max_steps: 最大学習ステップ数
        default_h: デフォルト予測期間
        h_ratio: 予測期間比率（データ長に対する）
        max_workers: 最大並列ワーカー数
        allow_ray_parallel: Ray並列実行を許可
        save_model: モデルを保存するか
        overwrite_model: 既存モデルを上書きするか
        dir_tokens_maxlen: ディレクトリトークン最大長
        max_exog_futr: 未来外生変数の最大数
        max_exog_hist: 過去外生変数の最大数
        max_exog_stat: 静的外生変数の最大数
        early_stopping_patience: Early Stopping patience
        gradient_clip_val: 勾配クリッピング値
        accelerator: 計算バックエンド（cpu, cuda, mps）
        devices: デバイス数
        precision: 精度（32, 16, bf16）
    
    Environment Variables:
        RANDOM_STATE: 乱数シード (default: 42)
        TRIAL_NUM_SAMPLES: 試行回数 (default: 10)
        TRIAL_MAX_STEPS: 最大ステップ (default: 1000)
        DEFAULT_H: 予測期間 (default: 7)
        H_RATIO: 予測期間比率 (default: 0.2)
        MAX_WORKERS: 最大ワーカー数 (default: 4)
        ALLOW_RAY_PARALLEL: Ray並列 (default: false)
        SAVE_MODEL: モデル保存 (default: true)
        OVERWRITE_MODEL: モデル上書き (default: false)
        MAX_EXOG_FUTR: 未来外生変数最大数 (default: 10)
        MAX_EXOG_HIST: 過去外生変数最大数 (default: 10)
        MAX_EXOG_STAT: 静的外生変数最大数 (default: 5)
        EARLY_STOPPING_PATIENCE: Early Stopping (default: 10)
        GRADIENT_CLIP_VAL: 勾配クリップ (default: 1.0)
        ACCELERATOR: バックエンド (default: auto)
        DEVICES: デバイス数 (default: 1)
        PRECISION: 精度 (default: 32)
    
    Example:
        >>> config = ExecutionConfig.from_env()
        >>> config.random_state
        42
        >>> config.max_workers
        4
    """
    
    # 基本設定
    random_state: int
    trial_num_samples: int
    trial_max_steps: int
    default_h: int
    h_ratio: float
    
    # 並列実行設定
    max_workers: int
    allow_ray_parallel: bool
    
    # モデル保存設定
    save_model: bool
    overwrite_model: bool
    dir_tokens_maxlen: int
    
    # 外生変数制限
    max_exog_futr: int
    max_exog_hist: int
    max_exog_stat: int
    
    # 学習設定
    early_stopping_patience: int
    gradient_clip_val: float
    
    # デバイス設定
    accelerator: str
    devices: int
    precision: str
    
    @classmethod
    def from_env(cls) -> 'ExecutionConfig':
        """
        環境変数から設定を構築
        
        Returns:
            ExecutionConfig: 実行設定インスタンス
            
        Example:
            >>> config = ExecutionConfig.from_env()
            >>> config.random_state >= 0
            True
        """
        return cls(
            # 基本設定
            random_state=int(os.getenv('RANDOM_STATE', '42')),
            trial_num_samples=int(os.getenv('TRIAL_NUM_SAMPLES', '10')),
            trial_max_steps=int(os.getenv('TRIAL_MAX_STEPS', '1000')),
            default_h=int(os.getenv('DEFAULT_H', '7')),
            h_ratio=float(os.getenv('H_RATIO', '0.2')),
            
            # 並列実行設定
            max_workers=int(os.getenv('MAX_WORKERS', '4')),
            allow_ray_parallel=os.getenv('ALLOW_RAY_PARALLEL', 'false').lower() == 'true',
            
            # モデル保存設定
            save_model=os.getenv('SAVE_MODEL', 'true').lower() == 'true',
            overwrite_model=os.getenv('OVERWRITE_MODEL', 'false').lower() == 'true',
            dir_tokens_maxlen=int(os.getenv('DIR_TOKENS_MAXLEN', '50')),
            
            # 外生変数制限
            max_exog_futr=int(os.getenv('MAX_EXOG_FUTR', '10')),
            max_exog_hist=int(os.getenv('MAX_EXOG_HIST', '10')),
            max_exog_stat=int(os.getenv('MAX_EXOG_STAT', '5')),
            
            # 学習設定
            early_stopping_patience=int(os.getenv('EARLY_STOPPING_PATIENCE', '10')),
            gradient_clip_val=float(os.getenv('GRADIENT_CLIP_VAL', '1.0')),
            
            # デバイス設定
            accelerator=os.getenv('ACCELERATOR', 'auto'),
            devices=int(os.getenv('DEVICES', '1')),
            precision=os.getenv('PRECISION', '32'),
        )
    
    def validate(self) -> None:
        """
        設定の妥当性検証
        
        Raises:
            ValueError: 設定値が不正
        """
        # 正の整数チェック
        if self.random_state < 0:
            raise ValueError(f"random_state must be non-negative: {self.random_state}")
        
        if self.trial_num_samples < 1:
            raise ValueError(f"trial_num_samples must be >= 1: {self.trial_num_samples}")
        
        if self.trial_max_steps < 1:
            raise ValueError(f"trial_max_steps must be >= 1: {self.trial_max_steps}")
        
        if self.default_h < 1:
            raise ValueError(f"default_h must be >= 1: {self.default_h}")
        
        # 比率チェック
        if not 0 < self.h_ratio <= 1.0:
            raise ValueError(f"h_ratio must be in (0, 1]: {self.h_ratio}")
        
        # 並列数チェック
        if self.max_workers < 1:
            raise ValueError(f"max_workers must be >= 1: {self.max_workers}")
        
        # 外生変数チェック
        if self.max_exog_futr < 0:
            raise ValueError(f"max_exog_futr must be non-negative: {self.max_exog_futr}")
        
        # アクセラレータチェック
        valid_accelerators = ['auto', 'cpu', 'cuda', 'mps', 'tpu']
        if self.accelerator not in valid_accelerators:
            raise ValueError(f"accelerator must be one of {valid_accelerators}: {self.accelerator}")
        
        # 精度チェック
        valid_precisions = ['32', '16', 'bf16']
        if self.precision not in valid_precisions:
            raise ValueError(f"precision must be one of {valid_precisions}: {self.precision}")
    
    def get_effective_h(self, data_length: int) -> int:
        """
        実効的な予測期間を計算
        
        Args:
            data_length: データ長
            
        Returns:
            int: 予測期間（h）
            
        Example:
            >>> config = ExecutionConfig.from_env()
            >>> config.get_effective_h(100)
            20  # h_ratio=0.2の場合
        """
        return max(self.default_h, int(data_length * self.h_ratio))
    
    def should_use_gpu(self) -> bool:
        """
        GPUを使用すべきか判定
        
        Returns:
            bool: GPU使用可否
            
        Example:
            >>> config = ExecutionConfig.from_env()
            >>> config.should_use_gpu()
            True  # accelerator='cuda'の場合
        """
        return self.accelerator in ['cuda', 'auto']
    
    def get_num_workers(self) -> int:
        """
        実際に使用するワーカー数を取得
        
        Returns:
            int: ワーカー数
            
        Note:
            CPUコア数を超えないように制限
            
        Example:
            >>> config = ExecutionConfig.from_env()
            >>> workers = config.get_num_workers()
            >>> workers >= 1
            True
        """
        import os
        cpu_count = os.cpu_count() or 1
        return min(self.max_workers, cpu_count)
```

#### 1.3.2 テストコード

```python
"""ExecutionConfigのテスト"""

import pytest
import os

class TestExecutionConfig:
    """ExecutionConfigのテストスイート"""
    
    def test_from_env_default(self, monkeypatch):
        """デフォルト値での読み込みテスト"""
        # 環境変数をクリア
        for key in ['RANDOM_STATE', 'TRIAL_NUM_SAMPLES', 'MAX_WORKERS']:
            monkeypatch.delenv(key, raising=False)
        
        config = ExecutionConfig.from_env()
        
        assert config.random_state == 42
        assert config.trial_num_samples == 10
        assert config.max_workers == 4
        assert config.save_model is True
        assert config.allow_ray_parallel is False
    
    def test_from_env_custom(self, monkeypatch):
        """カスタム値での読み込みテスト"""
        monkeypatch.setenv('RANDOM_STATE', '123')
        monkeypatch.setenv('TRIAL_NUM_SAMPLES', '20')
        monkeypatch.setenv('MAX_WORKERS', '8')
        monkeypatch.setenv('SAVE_MODEL', 'false')
        
        config = ExecutionConfig.from_env()
        
        assert config.random_state == 123
        assert config.trial_num_samples == 20
        assert config.max_workers == 8
        assert config.save_model is False
    
    def test_validate_success(self):
        """検証成功のテスト"""
        config = ExecutionConfig(
            random_state=42,
            trial_num_samples=10,
            trial_max_steps=1000,
            default_h=7,
            h_ratio=0.2,
            max_workers=4,
            allow_ray_parallel=False,
            save_model=True,
            overwrite_model=False,
            dir_tokens_maxlen=50,
            max_exog_futr=10,
            max_exog_hist=10,
            max_exog_stat=5,
            early_stopping_patience=10,
            gradient_clip_val=1.0,
            accelerator='auto',
            devices=1,
            precision='32',
        )
        
        # 例外が発生しないことを確認
        config.validate()
    
    def test_validate_failure_negative_random_state(self):
        """検証失敗のテスト（負の乱数シード）"""
        config = ExecutionConfig(
            random_state=-1,
            trial_num_samples=10,
            trial_max_steps=1000,
            default_h=7,
            h_ratio=0.2,
            max_workers=4,
            allow_ray_parallel=False,
            save_model=True,
            overwrite_model=False,
            dir_tokens_maxlen=50,
            max_exog_futr=10,
            max_exog_hist=10,
            max_exog_stat=5,
            early_stopping_patience=10,
            gradient_clip_val=1.0,
            accelerator='auto',
            devices=1,
            precision='32',
        )
        
        with pytest.raises(ValueError, match="random_state must be non-negative"):
            config.validate()
    
    def test_validate_failure_invalid_h_ratio(self):
        """検証失敗のテスト（不正なh_ratio）"""
        config = ExecutionConfig(
            random_state=42,
            trial_num_samples=10,
            trial_max_steps=1000,
            default_h=7,
            h_ratio=1.5,  # > 1.0
            max_workers=4,
            allow_ray_parallel=False,
            save_model=True,
            overwrite_model=False,
            dir_tokens_maxlen=50,
            max_exog_futr=10,
            max_exog_hist=10,
            max_exog_stat=5,
            early_stopping_patience=10,
            gradient_clip_val=1.0,
            accelerator='auto',
            devices=1,
            precision='32',
        )
        
        with pytest.raises(ValueError, match="h_ratio must be in"):
            config.validate()
    
    def test_validate_failure_invalid_accelerator(self):
        """検証失敗のテスト（不正なaccelerator）"""
        config = ExecutionConfig(
            random_state=42,
            trial_num_samples=10,
            trial_max_steps=1000,
            default_h=7,
            h_ratio=0.2,
            max_workers=4,
            allow_ray_parallel=False,
            save_model=True,
            overwrite_model=False,
            dir_tokens_maxlen=50,
            max_exog_futr=10,
            max_exog_hist=10,
            max_exog_stat=5,
            early_stopping_patience=10,
            gradient_clip_val=1.0,
            accelerator='invalid',
            devices=1,
            precision='32',
        )
        
        with pytest.raises(ValueError, match="accelerator must be one of"):
            config.validate()
    
    def test_get_effective_h(self):
        """実効予測期間の計算テスト"""
        config = ExecutionConfig.from_env()
        
        # データ長100の場合
        h = config.get_effective_h(100)
        assert h == max(config.default_h, int(100 * config.h_ratio))
        
        # データ長10の場合（default_hより小さい）
        h = config.get_effective_h(10)
        assert h == config.default_h
    
    def test_should_use_gpu(self):
        """GPU使用判定のテスト"""
        # CUDA指定
        config = ExecutionConfig(
            random_state=42,
            trial_num_samples=10,
            trial_max_steps=1000,
            default_h=7,
            h_ratio=0.2,
            max_workers=4,
            allow_ray_parallel=False,
            save_model=True,
            overwrite_model=False,
            dir_tokens_maxlen=50,
            max_exog_futr=10,
            max_exog_hist=10,
            max_exog_stat=5,
            early_stopping_patience=10,
            gradient_clip_val=1.0,
            accelerator='cuda',
            devices=1,
            precision='32',
        )
        assert config.should_use_gpu() is True
        
        # CPU指定
        config2 = ExecutionConfig(
            random_state=42,
            trial_num_samples=10,
            trial_max_steps=1000,
            default_h=7,
            h_ratio=0.2,
            max_workers=4,
            allow_ray_parallel=False,
            save_model=True,
            overwrite_model=False,
            dir_tokens_maxlen=50,
            max_exog_futr=10,
            max_exog_hist=10,
            max_exog_stat=5,
            early_stopping_patience=10,
            gradient_clip_val=1.0,
            accelerator='cpu',
            devices=1,
            precision='32',
        )
        assert config2.should_use_gpu() is False
    
    def test_get_num_workers(self):
        """ワーカー数取得のテスト"""
        config = ExecutionConfig.from_env()
        
        num_workers = config.get_num_workers()
        
        # CPUコア数以下であることを確認
        cpu_count = os.cpu_count() or 1
        assert num_workers <= cpu_count
        assert num_workers >= 1
```

---

### 1.4 ModelSelectionConfig

#### 1.4.1 クラス定義

```python
"""
ModelSelectionConfig: モデル選択設定

どのモデルを有効化するかを管理。
ホワイトリスト/ブラックリストによるフィルタリング機能も提供。
"""

from dataclasses import dataclass, field
from typing import List, Set
import os
import json

@dataclass(frozen=True)
class ModelSelectionConfig(Config):
    """
    モデル選択設定
    
    Attributes:
        enable_auto_nhits: AutoNHITSを有効化
        enable_auto_lstm: AutoLSTMを有効化
        enable_auto_tft: AutoTFTを有効化
        enable_auto_informer: AutoInformerを有効化
        enable_auto_autoformer: AutoAutoformerを有効化
        enable_auto_patchtst: AutoPatchTSTを有効化
        model_whitelist: モデルホワイトリスト（空の場合は全て許可）
        model_blacklist: モデルブラックリスト
    
    Environment Variables:
        ENABLE_AUTO_NHITS: AutoNHITS (default: true)
        ENABLE_AUTO_LSTM: AutoLSTM (default: true)
        ENABLE_AUTO_TFT: AutoTFT (default: false)
        ENABLE_AUTO_INFORMER: AutoInformer (default: false)
        ENABLE_AUTO_AUTOFORMER: AutoAutoformer (default: false)
        ENABLE_AUTO_PATCHTST: AutoPatchTST (default: false)
        MODEL_WHITELIST: ホワイトリスト（JSON配列, default: []）
        MODEL_BLACKLIST: ブラックリスト（JSON配列, default: []）
    
    Example:
        >>> config = ModelSelectionConfig.from_env()
        >>> config.enable_auto_nhits
        True
        >>> enabled = config.get_enabled_models()
        >>> 'AutoNHITS' in enabled
        True
    """
    
    # 各モデルの有効/無効
    enable_auto_nhits: bool
    enable_auto_lstm: bool
    enable_auto_tft: bool
    enable_auto_informer: bool
    enable_auto_autoformer: bool
    enable_auto_patchtst: bool
    
    # ホワイトリスト/ブラックリスト
    model_whitelist: List[str] = field(default_factory=list)
    model_blacklist: List[str] = field(default_factory=list)
    
    @classmethod
    def from_env(cls) -> 'ModelSelectionConfig':
        """
        環境変数から設定を構築
        
        Returns:
            ModelSelectionConfig: モデル選択設定インスタンス
            
        Example:
            >>> config = ModelSelectionConfig.from_env()
            >>> isinstance(config.model_whitelist, list)
            True
        """
        # ホワイトリスト/ブラックリストの読み込み
        whitelist_str = os.getenv('MODEL_WHITELIST', '[]')
        blacklist_str = os.getenv('MODEL_BLACKLIST', '[]')
        
        try:
            whitelist = json.loads(whitelist_str)
        except json.JSONDecodeError:
            whitelist = []
        
        try:
            blacklist = json.loads(blacklist_str)
        except json.JSONDecodeError:
            blacklist = []
        
        return cls(
            enable_auto_nhits=os.getenv('ENABLE_AUTO_NHITS', 'true').lower() == 'true',
            enable_auto_lstm=os.getenv('ENABLE_AUTO_LSTM', 'true').lower() == 'true',
            enable_auto_tft=os.getenv('ENABLE_AUTO_TFT', 'false').lower() == 'true',
            enable_auto_informer=os.getenv('ENABLE_AUTO_INFORMER', 'false').lower() == 'true',
            enable_auto_autoformer=os.getenv('ENABLE_AUTO_AUTOFORMER', 'false').lower() == 'true',
            enable_auto_patchtst=os.getenv('ENABLE_AUTO_PATCHTST', 'false').lower() == 'true',
            model_whitelist=whitelist,
            model_blacklist=blacklist,
        )
    
    def validate(self) -> None:
        """
        設定の妥当性検証
        
        Raises:
            ValueError: 設定値が不正
        """
        # 少なくとも1つのモデルが有効であること
        if not any([
            self.enable_auto_nhits,
            self.enable_auto_lstm,
            self.enable_auto_tft,
            self.enable_auto_informer,
            self.enable_auto_autoformer,
            self.enable_auto_patchtst,
        ]):
            raise ValueError("At least one model must be enabled")
        
        # ホワイトリストとブラックリストの重複チェック
        whitelist_set = set(self.model_whitelist)
        blacklist_set = set(self.model_blacklist)
        overlap = whitelist_set & blacklist_set
        
        if overlap:
            raise ValueError(f"Models appear in both whitelist and blacklist: {overlap}")
    
    def get_enabled_models(self) -> List[str]:
        """
        有効なモデル一覧を取得
        
        Returns:
            List[str]: 有効なモデル名のリスト
            
        Note:
            フラグで有効化されたモデルに対して、
            ホワイトリスト/ブラックリストでフィルタリングを行う
            
        Example:
            >>> config = ModelSelectionConfig.from_env()
            >>> models = config.get_enabled_models()
            >>> isinstance(models, list)
            True
            >>> all(isinstance(m, str) for m in models)
            True
        """
        # フラグで有効化されたモデル
        enabled = []
        
        if self.enable_auto_nhits:
            enabled.append('AutoNHITS')
        if self.enable_auto_lstm:
            enabled.append('AutoLSTM')
        if self.enable_auto_tft:
            enabled.append('AutoTFT')
        if self.enable_auto_informer:
            enabled.append('AutoInformer')
        if self.enable_auto_autoformer:
            enabled.append('AutoAutoformer')
        if self.enable_auto_patchtst:
            enabled.append('AutoPatchTST')
        
        # ホワイトリストが指定されている場合はフィルタ
        if self.model_whitelist:
            enabled = [m for m in enabled if m in self.model_whitelist]
        
        # ブラックリストで除外
        if self.model_blacklist:
            enabled = [m for m in enabled if m not in self.model_blacklist]
        
        return enabled
    
    def is_model_enabled(self, model_name: str) -> bool:
        """
        特定のモデルが有効かチェック
        
        Args:
            model_name: モデル名
            
        Returns:
            bool: 有効な場合True
            
        Example:
            >>> config = ModelSelectionConfig.from_env()
            >>> config.is_model_enabled('AutoNHITS')
            True
        """
        return model_name in self.get_enabled_models()
    
    def get_disabled_models(self) -> List[str]:
        """
        無効なモデル一覧を取得
        
        Returns:
            List[str]: 無効なモデル名のリスト
            
        Example:
            >>> config = ModelSelectionConfig.from_env()
            >>> disabled = config.get_disabled_models()
            >>> isinstance(disabled, list)
            True
        """
        all_models = [
            'AutoNHITS',
            'AutoLSTM',
            'AutoTFT',
            'AutoInformer',
            'AutoAutoformer',
            'AutoPatchTST',
        ]
        
        enabled = set(self.get_enabled_models())
        return [m for m in all_models if m not in enabled]
```

#### 1.4.2 テストコード

```python
"""ModelSelectionConfigのテスト"""

import pytest
import json

class TestModelSelectionConfig:
    """ModelSelectionConfigのテストスイート"""
    
    def test_from_env_default(self, monkeypatch):
        """デフォルト値での読み込みテスト"""
        # 環境変数をクリア
        for key in ['ENABLE_AUTO_NHITS', 'ENABLE_AUTO_LSTM', 'MODEL_WHITELIST']:
            monkeypatch.delenv(key, raising=False)
        
        config = ModelSelectionConfig.from_env()
        
        assert config.enable_auto_nhits is True
        assert config.enable_auto_lstm is True
        assert config.enable_auto_tft is False
        assert config.model_whitelist == []
        assert config.model_blacklist == []
    
    def test_from_env_custom(self, monkeypatch):
        """カスタム値での読み込みテスト"""
        monkeypatch.setenv('ENABLE_AUTO_NHITS', 'false')
        monkeypatch.setenv('ENABLE_AUTO_TFT', 'true')
        monkeypatch.setenv('MODEL_WHITELIST', '["AutoNHITS", "AutoTFT"]')
        monkeypatch.setenv('MODEL_BLACKLIST', '["AutoLSTM"]')
        
        config = ModelSelectionConfig.from_env()
        
        assert config.enable_auto_nhits is False
        assert config.enable_auto_tft is True
        assert config.model_whitelist == ["AutoNHITS", "AutoTFT"]
        assert config.model_blacklist == ["AutoLSTM"]
    
    def test_validate_success(self):
        """検証成功のテスト"""
        config = ModelSelectionConfig(
            enable_auto_nhits=True,
            enable_auto_lstm=False,
            enable_auto_tft=False,
            enable_auto_informer=False,
            enable_auto_autoformer=False,
            enable_auto_patchtst=False,
            model_whitelist=[],
            model_blacklist=[],
        )
        
        # 例外が発生しないことを確認
        config.validate()
    
    def test_validate_failure_no_models_enabled(self):
        """検証失敗のテスト（モデルが1つも有効でない）"""
        config = ModelSelectionConfig(
            enable_auto_nhits=False,
            enable_auto_lstm=False,
            enable_auto_tft=False,
            enable_auto_informer=False,
            enable_auto_autoformer=False,
            enable_auto_patchtst=False,
            model_whitelist=[],
            model_blacklist=[],
        )
        
        with pytest.raises(ValueError, match="At least one model must be enabled"):
            config.validate()
    
    def test_validate_failure_overlap(self):
        """検証失敗のテスト（ホワイトリストとブラックリストの重複）"""
        config = ModelSelectionConfig(
            enable_auto_nhits=True,
            enable_auto_lstm=True,
            enable_auto_tft=False,
            enable_auto_informer=False,
            enable_auto_autoformer=False,
            enable_auto_patchtst=False,
            model_whitelist=['AutoNHITS', 'AutoLSTM'],
            model_blacklist=['AutoLSTM'],  # 重複
        )
        
        with pytest.raises(ValueError, match="appear in both whitelist and blacklist"):
            config.validate()
    
    def test_get_enabled_models_all(self):
        """有効モデル取得のテスト（全て有効）"""
        config = ModelSelectionConfig(
            enable_auto_nhits=True,
            enable_auto_lstm=True,
            enable_auto_tft=True,
            enable_auto_informer=True,
            enable_auto_autoformer=True,
            enable_auto_patchtst=True,
            model_whitelist=[],
            model_blacklist=[],
        )
        
        enabled = config.get_enabled_models()
        
        assert len(enabled) == 6
        assert 'AutoNHITS' in enabled
        assert 'AutoLSTM' in enabled
        assert 'AutoTFT' in enabled
    
    def test_get_enabled_models_with_whitelist(self):
        """有効モデル取得のテスト（ホワイトリスト適用）"""
        config = ModelSelectionConfig(
            enable_auto_nhits=True,
            enable_auto_lstm=True,
            enable_auto_tft=True,
            enable_auto_informer=False,
            enable_auto_autoformer=False,
            enable_auto_patchtst=False,
            model_whitelist=['AutoNHITS', 'AutoTFT'],
            model_blacklist=[],
        )
        
        enabled = config.get_enabled_models()
        
        # ホワイトリストに含まれるもののみ
        assert len(enabled) == 2
        assert 'AutoNHITS' in enabled
        assert 'AutoTFT' in enabled
        assert 'AutoLSTM' not in enabled  # フラグは有効だがホワイトリストにない
    
    def test_get_enabled_models_with_blacklist(self):
        """有効モデル取得のテスト（ブラックリスト適用）"""
        config = ModelSelectionConfig(
            enable_auto_nhits=True,
            enable_auto_lstm=True,
            enable_auto_tft=True,
            enable_auto_informer=False,
            enable_auto_autoformer=False,
            enable_auto_patchtst=False,
            model_whitelist=[],
            model_blacklist=['AutoLSTM'],
        )
        
        enabled = config.get_enabled_models()
        
        # ブラックリストのものは除外
        assert len(enabled) == 2
        assert 'AutoNHITS' in enabled
        assert 'AutoTFT' in enabled
        assert 'AutoLSTM' not in enabled
    
    def test_is_model_enabled(self):
        """モデル有効チェックのテスト"""
        config = ModelSelectionConfig(
            enable_auto_nhits=True,
            enable_auto_lstm=False,
            enable_auto_tft=False,
            enable_auto_informer=False,
            enable_auto_autoformer=False,
            enable_auto_patchtst=False,
            model_whitelist=[],
            model_blacklist=[],
        )
        
        assert config.is_model_enabled('AutoNHITS') is True
        assert config.is_model_enabled('AutoLSTM') is False
        assert config.is_model_enabled('AutoTFT') is False
    
    def test_get_disabled_models(self):
        """無効モデル取得のテスト"""
        config = ModelSelectionConfig(
            enable_auto_nhits=True,
            enable_auto_lstm=True,
            enable_auto_tft=False,
            enable_auto_informer=False,
            enable_auto_autoformer=False,
            enable_auto_patchtst=False,
            model_whitelist=[],
            model_blacklist=[],
        )
        
        disabled = config.get_disabled_models()
        
        assert len(disabled) == 4
        assert 'AutoTFT' in disabled
        assert 'AutoInformer' in disabled
        assert 'AutoAutoformer' in disabled
        assert 'AutoPatchTST' in disabled
        assert 'AutoNHITS' not in disabled
        assert 'AutoLSTM' not in disabled
```

---

### 1.5 ConfigLoader

#### 1.5.1 クラス定義

```python
"""
ConfigLoader: 設定ローダー

複数の設定を一括で読み込み、検証、マージを行う。
"""

from typing import Dict, List, Type, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ConfigLoader:
    """
    設定ローダー
    
    複数の設定クラスを一括で読み込み、統合的に管理する。
    
    Attributes:
        configs: 読み込まれた設定の辞書
    
    Methods:
        load_all: 全設定を環境変数から読み込み
        load_from_file: ファイルから設定を読み込み
        merge_configs: 複数の設定をマージ
        validate_all: 全設定を検証
        get: 特定の設定を取得
        save_all: 全設定をファイルに保存
    
    Example:
        >>> loader = ConfigLoader()
        >>> configs = loader.load_all()
        >>> path_config = loader.get(PathConfig)
        >>> path_config.data_csv
        PosixPath('./data.csv')
    """
    
    def __init__(self):
        """
        ConfigLoaderを初期化
        """
        self.configs: Dict[Type[Config], Config] = {}
    
    def load_all(self) -> Dict[str, Config]:
        """
        全設定を環境変数から読み込み
        
        Returns:
            Dict[str, Config]: 設定名をキー、設定インスタンスを値とする辞書
            
        Raises:
            ValueError: 設定の読み込みまたは検証に失敗
            
        Example:
            >>> loader = ConfigLoader()
            >>> configs = loader.load_all()
            >>> 'path' in configs
            True
            >>> 'execution' in configs
            True
        """
        logger.info("Loading all configurations from environment")
        
        try:
            # 各設定を読み込み
            path_config = PathConfig.from_env()
            execution_config = ExecutionConfig.from_env()
            model_selection_config = ModelSelectionConfig.from_env()
            
            # 検証
            path_config.validate()
            execution_config.validate()
            model_selection_config.validate()
            
            # 保存
            self.configs[PathConfig] = path_config
            self.configs[ExecutionConfig] = execution_config
            self.configs[ModelSelectionConfig] = model_selection_config
            
            # 辞書形式で返す
            result = {
                'path': path_config,
                'execution': execution_config,
                'model_selection': model_selection_config,
            }
            
            logger.info(f"Successfully loaded {len(result)} configurations")
            return result
            
        except Exception as e:
            logger.error(f"Failed to load configurations: {e}")
            raise ValueError(f"Configuration loading failed: {e}") from e
    
    def load_from_file(self, file_path: Path) -> Dict[str, Config]:
        """
        ファイルから設定を読み込み
        
        Args:
            file_path: 設定ファイルパス（JSON）
            
        Returns:
            Dict[str, Config]: 設定の辞書
            
        Raises:
            FileNotFoundError: ファイルが存在しない
            ValueError: 設定の読み込みまたは検証に失敗
            
        Example:
            >>> loader = ConfigLoader()
            >>> configs = loader.load_from_file(Path("config.json"))
        """
        logger.info(f"Loading configurations from file: {file_path}")
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        import json
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        configs = {}
        
        # 各設定を読み込み
        if 'path' in data:
            path_config = PathConfig.from_dict(data['path'])
            path_config.validate()
            configs['path'] = path_config
            self.configs[PathConfig] = path_config
        
        if 'execution' in data:
            execution_config = ExecutionConfig.from_dict(data['execution'])
            execution_config.validate()
            configs['execution'] = execution_config
            self.configs[ExecutionConfig] = execution_config
        
        if 'model_selection' in data:
            model_selection_config = ModelSelectionConfig.from_dict(data['model_selection'])
            model_selection_config.validate()
            configs['model_selection'] = model_selection_config
            self.configs[ModelSelectionConfig] = model_selection_config
        
        logger.info(f"Successfully loaded {len(configs)} configurations from file")
        return configs
    
    def merge_configs(
        self,
        configs: List[Config],
        *,
        strategy: str = 'last'
    ) -> Config:
        """
        複数の設定をマージ
        
        Args:
            configs: マージする設定のリスト（同じ型であること）
            strategy: マージ戦略
                - 'last': 最後の設定を優先（デフォルト）
                - 'first': 最初の設定を優先
                
        Returns:
            Config: マージされた設定
            
        Raises:
            ValueError: 設定の型が異なる
            
        Example:
            >>> loader = ConfigLoader()
            >>> config1 = PathConfig.from_env()
            >>> config2 = PathConfig.from_dict({"data_csv": "/custom/data.csv"})
            >>> merged = loader.merge_configs([config1, config2])
        """
        if not configs:
            raise ValueError("No configs to merge")
        
        # すべて同じ型であることを確認
        config_type = type(configs[0])
        if not all(isinstance(c, config_type) for c in configs):
            raise ValueError("All configs must be of the same type")
        
        if strategy == 'last':
            base_config = configs[-1]
        elif strategy == 'first':
            base_config = configs[0]
        else:
            raise ValueError(f"Unknown merge strategy: {strategy}")
        
        logger.info(f"Merged {len(configs)} configurations using '{strategy}' strategy")
        return base_config
    
    def validate_all(self, configs: Optional[Dict[str, Config]] = None) -> bool:
        """
        全設定を検証
        
        Args:
            configs: 検証する設定の辞書（Noneの場合は内部の設定を検証）
            
        Returns:
            bool: 検証が成功した場合True
            
        Raises:
            ValueError: 検証に失敗
            
        Example:
            >>> loader = ConfigLoader()
            >>> loader.load_all()
            >>> loader.validate_all()
            True
        """
        if configs is None:
            configs = {
                'path': self.configs.get(PathConfig),
                'execution': self.configs.get(ExecutionConfig),
                'model_selection': self.configs.get(ModelSelectionConfig),
            }
        
        errors = []
        
        for name, config in configs.items():
            if config is None:
                errors.append(f"{name}: config is None")
                continue
            
            try:
                config.validate()
            except ValueError as e:
                errors.append(f"{name}: {e}")
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("All configurations validated successfully")
        return True
    
    def get(self, config_type: Type[Config]) -> Config:
        """
        特定の設定を取得
        
        Args:
            config_type: 設定クラスの型
            
        Returns:
            Config: 設定インスタンス
            
        Raises:
            KeyError: 設定が読み込まれていない
            
        Example:
            >>> loader = ConfigLoader()
            >>> loader.load_all()
            >>> path_config = loader.get(PathConfig)
            >>> isinstance(path_config, PathConfig)
            True
        """
        if config_type not in self.configs:
            raise KeyError(f"Configuration not loaded: {config_type.__name__}")
        
        return self.configs[config_type]
    
    def save_all(self, file_path: Path, indent: int = 2) -> None:
        """
        全設定をファイルに保存
        
        Args:
            file_path: 保存先ファイルパス
            indent: インデント幅
            
        Raises:
            ValueError: 設定が読み込まれていない
            IOError: ファイル書き込みエラー
            
        Example:
            >>> loader = ConfigLoader()
            >>> loader.load_all()
            >>> loader.save_all(Path("config.json"))
        """
        if not self.configs:
            raise ValueError("No configurations to save")
        
        data = {}
        
        if PathConfig in self.configs:
            data['path'] = self.configs[PathConfig].to_dict()
        
        if ExecutionConfig in self.configs:
            data['execution'] = self.configs[ExecutionConfig].to_dict()
        
        if ModelSelectionConfig in self.configs:
            data['model_selection'] = self.configs[ModelSelectionConfig].to_dict()
        
        import json
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        
        logger.info(f"Saved {len(data)} configurations to {file_path}")
```

#### 1.5.2 テストコード

```python
"""ConfigLoaderのテスト"""

import pytest
import tempfile
from pathlib import Path
import json

class TestConfigLoader:
    """ConfigLoaderのテストスイート"""
    
    def test_load_all_success(self, monkeypatch):
        """全設定読み込みのテスト（成功）"""
        # 環境変数を設定
        monkeypatch.setenv('NF_DATA_CSV', './test_data.csv')
        monkeypatch.setenv('RANDOM_STATE', '123')
        monkeypatch.setenv('ENABLE_AUTO_NHITS', 'true')
        
        loader = ConfigLoader()
        configs = loader.load_all()
        
        assert 'path' in configs
        assert 'execution' in configs
        assert 'model_selection' in configs
        
        assert isinstance(configs['path'], PathConfig)
        assert isinstance(configs['execution'], ExecutionConfig)
        assert isinstance(configs['model_selection'], ModelSelectionConfig)
    
    def test_load_from_file_success(self):
        """ファイルからの読み込みテスト（成功）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "config.json"
            
            # テスト用の設定ファイルを作成
            config_data = {
                "path": {
                    "data_csv": f"{tmpdir}/data.csv",
                    "output_dir": f"{tmpdir}/output",
                    "log_dir": f"{tmpdir}/output/logs",
                    "project_root": tmpdir,
                    "model_dir": f"{tmpdir}/output/models",
                    "artifact_dir": f"{tmpdir}/output/artifacts",
                    "checkpoint_dir": f"{tmpdir}/output/checkpoints",
                    "plot_dir": f"{tmpdir}/output/plots",
                },
                "execution": {
                    "random_state": 42,
                    "trial_num_samples": 10,
                    "trial_max_steps": 1000,
                    "default_h": 7,
                    "h_ratio": 0.2,
                    "max_workers": 4,
                    "allow_ray_parallel": False,
                    "save_model": True,
                    "overwrite_model": False,
                    "dir_tokens_maxlen": 50,
                    "max_exog_futr": 10,
                    "max_exog_hist": 10,
                    "max_exog_stat": 5,
                    "early_stopping_patience": 10,
                    "gradient_clip_val": 1.0,
                    "accelerator": "auto",
                    "devices": 1,
                    "precision": "32",
                },
                "model_selection": {
                    "enable_auto_nhits": True,
                    "enable_auto_lstm": True,
                    "enable_auto_tft": False,
                    "enable_auto_informer": False,
                    "enable_auto_autoformer": False,
                    "enable_auto_patchtst": False,
                    "model_whitelist": [],
                    "model_blacklist": [],
                }
            }
            
            with open(file_path, 'w') as f:
                json.dump(config_data, f)
            
            # 読み込み
            loader = ConfigLoader()
            configs = loader.load_from_file(file_path)
            
            assert 'path' in configs
            assert 'execution' in configs
            assert 'model_selection' in configs
    
    def test_load_from_file_not_found(self):
        """ファイルからの読み込みテスト（ファイルが存在しない）"""
        loader = ConfigLoader()
        
        with pytest.raises(FileNotFoundError):
            loader.load_from_file(Path("/nonexistent/config.json"))
    
    def test_merge_configs_last_strategy(self):
        """設定マージのテスト（last戦略）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config1 = PathConfig(
                data_csv=Path(tmpdir) / "data1.csv",
                output_dir=Path(tmpdir) / "output1",
                log_dir=Path(tmpdir) / "output1/logs",
                project_root=Path(tmpdir),
                model_dir=Path(tmpdir) / "output1/models",
                artifact_dir=Path(tmpdir) / "output1/artifacts",
                checkpoint_dir=Path(tmpdir) / "output1/checkpoints",
                plot_dir=Path(tmpdir) / "output1/plots",
            )
            
            config2 = PathConfig(
                data_csv=Path(tmpdir) / "data2.csv",
                output_dir=Path(tmpdir) / "output2",
                log_dir=Path(tmpdir) / "output2/logs",
                project_root=Path(tmpdir),
                model_dir=Path(tmpdir) / "output2/models",
                artifact_dir=Path(tmpdir) / "output2/artifacts",
                checkpoint_dir=Path(tmpdir) / "output2/checkpoints",
                plot_dir=Path(tmpdir) / "output2/plots",
            )
            
            loader = ConfigLoader()
            merged = loader.merge_configs([config1, config2], strategy='last')
            
            # 最後の設定が優先される
            assert merged.data_csv == Path(tmpdir) / "data2.csv"
    
    def test_merge_configs_different_types(self):
        """設定マージのテスト（異なる型のエラー）"""
        path_config = PathConfig.from_env()
        execution_config = ExecutionConfig.from_env()
        
        loader = ConfigLoader()
        
        with pytest.raises(ValueError, match="same type"):
            loader.merge_configs([path_config, execution_config])
    
    def test_validate_all_success(self):
        """全設定検証のテスト（成功）"""
        loader = ConfigLoader()
        loader.load_all()
        
        # 例外が発生しないことを確認
        assert loader.validate_all() is True
    
    def test_get_success(self):
        """設定取得のテスト（成功）"""
        loader = ConfigLoader()
        loader.load_all()
        
        path_config = loader.get(PathConfig)
        assert isinstance(path_config, PathConfig)
        
        execution_config = loader.get(ExecutionConfig)
        assert isinstance(execution_config, ExecutionConfig)
    
    def test_get_not_loaded(self):
        """設定取得のテスト（未読み込み）"""
        loader = ConfigLoader()
        
        with pytest.raises(KeyError, match="not loaded"):
            loader.get(PathConfig)
    
    def test_save_all_success(self):
        """全設定保存のテスト（成功）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "config.json"
            
            loader = ConfigLoader()
            loader.load_all()
            loader.save_all(file_path)
            
            assert file_path.exists()
            
            # 読み込んで検証
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            assert 'path' in data
            assert 'execution' in data
            assert 'model_selection' in data
    
    def test_save_all_no_configs(self):
        """全設定保存のテスト（設定なし）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "config.json"
            
            loader = ConfigLoader()
            
            with pytest.raises(ValueError, match="No configurations to save"):
                loader.save_all(file_path)
```

---

## Layer 2: Data層

### 2.1 DataLoader

#### 2.1.1 クラス定義

```python
"""
DataLoader: データ読み込み

CSV/Parquetファイルからデータを読み込み、標準スキーマに変換する。
"""

from pathlib import Path
from typing import Optional, Iterator, Dict, Any, List
import pandas as pd
import chardet
import logging

logger = logging.getLogger(__name__)

class DataLoader:
    """
    データローダー
    
    CSVファイルやParquetファイルから時系列データを読み込み、
    標準スキーマ（unique_id, ds, y, exog_*）に変換する。
    
    Attributes:
        encoding_cache: ファイルパスとエンコーディングのキャッシュ
    
    Methods:
        load_csv: CSVファイルを読み込む
        load_parquet: Parquetファイルを読み込む
        auto_detect_encoding: エンコーディングを自動検出
        infer_schema: データフレームからスキーマを推論
        load: ファイル形式を自動判定して読み込む
    
    Example:
        >>> loader = DataLoader()
        >>> df = loader.load_csv(Path("data.csv"))
        >>> df.columns
        Index(['unique_id', 'ds', 'y'])
    """
    
    def __init__(self):
        """
        DataLoaderを初期化
        """
        self.encoding_cache: Dict[str, str] = {}
    
    def load_csv(
        self,
        file_path: Path,
        *,
        encoding: Optional[str] = None,
        chunksize: Optional[int] = None,
        date_format: Optional[str] = None,
        parse_dates: bool = True,
        infer_datetime_format: bool = True,
        required_columns: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        CSVファイルを読み込む
        
        Args:
            file_path: CSVファイルパス
            encoding: 文字エンコーディング（Noneで自動検出）
            chunksize: チャンク読み込みサイズ（行数）
            date_format: 日時フォーマット（例: '%Y-%m-%d'）
            parse_dates: 日時カラムを自動パース
            infer_datetime_format: 日時フォーマットを推定
            required_columns: 必須カラムリスト（Noneで['unique_id', 'ds', 'y']）
            
        Returns:
            pd.DataFrame: 読み込まれたDataFrame
            
        Raises:
            FileNotFoundError: ファイルが存在しない
            ValueError: スキーマ不正（必須カラム欠如）
            EncodingError: エンコーディング検出失敗
            
        Example:
            >>> loader = DataLoader()
            >>> df = loader.load_csv(Path("data.csv"))
            >>> 'unique_id' in df.columns
            True
            >>> 'ds' in df.columns
            True
            >>> 'y' in df.columns
            True
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"Loading CSV file: {file_path}")
        
        # エンコーディング検出
        if encoding is None:
            encoding = self.auto_detect_encoding(file_path)
            logger.info(f"Detected encoding: {encoding}")
        
        # CSVを読み込み
        try:
            df = pd.read_csv(
                file_path,
                encoding=encoding,
                chunksize=chunksize,
                parse_dates=['ds'] if parse_dates else False,
                date_format=date_format,
                infer_datetime_format=infer_datetime_format,
            )
            
            # chunksize指定時はIteratorが返るので結合
            if isinstance(df, Iterator):
                df = pd.concat(df, ignore_index=True)
            
        except Exception as e:
            logger.error(f"Failed to read CSV: {e}")
            raise
        
        # 必須カラムチェック
        if required_columns is None:
            required_columns = ['unique_id', 'ds', 'y']
        
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}. "
                f"Found columns: {list(df.columns)}"
            )
        
        logger.info(
            f"Successfully loaded CSV: {len(df)} rows, {len(df.columns)} columns"
        )
        
        return df
    
    def load_parquet(
        self,
        file_path: Path,
        *,
        columns: Optional[List[str]] = None,
        filters: Optional[List[tuple]] = None,
    ) -> pd.DataFrame:
        """
        Parquetファイルを読み込む
        
        Args:
            file_path: Parquetファイルパス
            columns: 読み込むカラムリスト（Noneで全カラム）
            filters: フィルタ条件（PyArrow形式）
            
        Returns:
            pd.DataFrame: 読み込まれたDataFrame
            
        Raises:
            FileNotFoundError: ファイルが存在しない
            ValueError: スキーマ不正
            
        Example:
            >>> loader = DataLoader()
            >>> df = loader.load_parquet(Path("data.parquet"))
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"Loading Parquet file: {file_path}")
        
        try:
            df = pd.read_parquet(
                file_path,
                columns=columns,
                filters=filters,
            )
        except Exception as e:
            logger.error(f"Failed to read Parquet: {e}")
            raise
        
        # 必須カラムチェック
        required_columns = ['unique_id', 'ds', 'y']
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}. "
                f"Found columns: {list(df.columns)}"
            )
        
        logger.info(
            f"Successfully loaded Parquet: {len(df)} rows, {len(df.columns)} columns"
        )
        
        return df
    
    def auto_detect_encoding(self, file_path: Path, sample_size: int = 10000) -> str:
        """
        エンコーディングを自動検出
        
        Args:
            file_path: ファイルパス
            sample_size: サンプルサイズ（バイト数）
            
        Returns:
            str: エンコーディング名
            
        Raises:
            IOError: ファイル読み込みエラー
            
        Example:
            >>> loader = DataLoader()
            >>> encoding = loader.auto_detect_encoding(Path("data.csv"))
            >>> encoding in ['utf-8', 'shift_jis', 'euc-jp']
            True
        """
        # キャッシュチェック
        cache_key = str(file_path)
        if cache_key in self.encoding_cache:
            return self.encoding_cache[cache_key]
        
        # ファイルの一部を読み込んで検出
        with open(file_path, 'rb') as f:
            raw_data = f.read(sample_size)
        
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        confidence = result['confidence']
        
        logger.debug(
            f"Encoding detection: {encoding} (confidence: {confidence:.2%})"
        )
        
        # デフォルトフォールバック
        if encoding is None or confidence < 0.7:
            encoding = 'utf-8'
            logger.warning(
                f"Low confidence encoding detection. Using default: {encoding}"
            )
        
        # キャッシュに保存
        self.encoding_cache[cache_key] = encoding
        
        return encoding
    
    def infer_schema(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        データフレームからスキーマを推論
        
        Args:
            df: データフレーム
            
        Returns:
            Dict[str, str]: カラム名と型のマッピング
            
        Example:
            >>> loader = DataLoader()
            >>> df = pd.DataFrame({
            ...     'unique_id': ['a', 'b'],
            ...     'ds': pd.to_datetime(['2025-01-01', '2025-01-02']),
            ...     'y': [1.0, 2.0]
            ... })
            >>> schema = loader.infer_schema(df)
            >>> schema['unique_id']
            'object'
            >>> schema['ds']
            'datetime64[ns]'
            >>> schema['y']
            'float64'
        """
        schema = {}
        
        for col in df.columns:
            dtype = str(df[col].dtype)
            schema[col] = dtype
        
        logger.debug(f"Inferred schema: {schema}")
        
        return schema
    
    def load(
        self,
        file_path: Path,
        **kwargs
    ) -> pd.DataFrame:
        """
        ファイル形式を自動判定して読み込む
        
        Args:
            file_path: ファイルパス
            **kwargs: load_csv/load_parquetに渡す引数
            
        Returns:
            pd.DataFrame: 読み込まれたDataFrame
            
        Raises:
            ValueError: サポートされていないファイル形式
            
        Example:
            >>> loader = DataLoader()
            >>> df = loader.load(Path("data.csv"))
            >>> # または
            >>> df = loader.load(Path("data.parquet"))
        """
        suffix = file_path.suffix.lower()
        
        if suffix == '.csv':
            return self.load_csv(file_path, **kwargs)
        elif suffix in ['.parquet', '.pq']:
            return self.load_parquet(file_path, **kwargs)
        else:
            raise ValueError(
                f"Unsupported file format: {suffix}. "
                "Supported formats: .csv, .parquet, .pq"
            )
```

#### 2.1.2 テストコード

```python
"""DataLoaderのテスト"""

import pytest
import pandas as pd
import tempfile
from pathlib import Path

class TestDataLoader:
    """DataLoaderのテストスイート"""
    
    @pytest.fixture
    def sample_csv(self):
        """サンプルCSVファイルを作成"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("unique_id,ds,y\n")
            f.write("store_1,2025-01-01,100.0\n")
            f.write("store_1,2025-01-02,110.0\n")
            f.write("store_2,2025-01-01,200.0\n")
            f.write("store_2,2025-01-02,210.0\n")
            temp_path = Path(f.name)
        
        yield temp_path
        
        # クリーンアップ
        temp_path.unlink()
    
    @pytest.fixture
    def sample_parquet(self):
        """サンプルParquetファイルを作成"""
        df = pd.DataFrame({
            'unique_id': ['store_1', 'store_1', 'store_2', 'store_2'],
            'ds': pd.to_datetime(['2025-01-01', '2025-01-02', '2025-01-01', '2025-01-02']),
            'y': [100.0, 110.0, 200.0, 210.0]
        })
        
        with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as f:
            temp_path = Path(f.name)
        
        df.to_parquet(temp_path, index=False)
        
        yield temp_path
        
        # クリーンアップ
        temp_path.unlink()
    
    def test_load_csv_success(self, sample_csv):
        """CSV読み込みのテスト（成功）"""
        loader = DataLoader()
        df = loader.load_csv(sample_csv)
        
        assert len(df) == 4
        assert 'unique_id' in df.columns
        assert 'ds' in df.columns
        assert 'y' in df.columns
        
        # unique_idの値をチェック
        assert set(df['unique_id'].unique()) == {'store_1', 'store_2'}
    
    def test_load_csv_not_found(self):
        """CSV読み込みのテスト（ファイルが存在しない）"""
        loader = DataLoader()
        
        with pytest.raises(FileNotFoundError):
            loader.load_csv(Path("/nonexistent/data.csv"))
    
    def test_load_csv_missing_columns(self):
        """CSV読み込みのテスト（必須カラム欠如）"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("id,date,value\n")  # 間違ったカラム名
            f.write("1,2025-01-01,100\n")
            temp_path = Path(f.name)
        
        try:
            loader = DataLoader()
            
            with pytest.raises(ValueError, match="Missing required columns"):
                loader.load_csv(temp_path)
        finally:
            temp_path.unlink()
    
    def test_load_parquet_success(self, sample_parquet):
        """Parquet読み込みのテスト（成功）"""
        loader = DataLoader()
        df = loader.load_parquet(sample_parquet)
        
        assert len(df) == 4
        assert 'unique_id' in df.columns
        assert 'ds' in df.columns
        assert 'y' in df.columns
    
    def test_auto_detect_encoding_utf8(self, sample_csv):
        """エンコーディング検出のテスト（UTF-8）"""
        loader = DataLoader()
        encoding = loader.auto_detect_encoding(sample_csv)
        
        # UTF-8またはASCIIが検出されるはず
        assert encoding.lower() in ['utf-8', 'ascii']
    
    def test_auto_detect_encoding_cache(self, sample_csv):
        """エンコーディング検出のキャッシュテスト"""
        loader = DataLoader()
        
        # 1回目
        encoding1 = loader.auto_detect_encoding(sample_csv)
        
        # 2回目（キャッシュから取得）
        encoding2 = loader.auto_detect_encoding(sample_csv)
        
        assert encoding1 == encoding2
        assert str(sample_csv) in loader.encoding_cache
    
    def test_infer_schema(self):
        """スキーマ推論のテスト"""
        df = pd.DataFrame({
            'unique_id': ['a', 'b'],
            'ds': pd.to_datetime(['2025-01-01', '2025-01-02']),
            'y': [1.0, 2.0],
            'temperature': [15.5, 16.2]
        })
        
        loader = DataLoader()
        schema = loader.infer_schema(df)
        
        assert 'unique_id' in schema
        assert 'ds' in schema
        assert 'y' in schema
        assert 'temperature' in schema
        
        # 型チェック
        assert 'object' in schema['unique_id']
        assert 'datetime' in schema['ds']
        assert 'float' in schema['y']
    
    def test_load_auto_detect_csv(self, sample_csv):
        """自動判定読み込みのテスト（CSV）"""
        loader = DataLoader()
        df = loader.load(sample_csv)
        
        assert len(df) == 4
        assert 'unique_id' in df.columns
    
    def test_load_auto_detect_parquet(self, sample_parquet):
        """自動判定読み込みのテスト（Parquet）"""
        loader = DataLoader()
        df = loader.load(sample_parquet)
        
        assert len(df) == 4
        assert 'unique_id' in df.columns
    
    def test_load_unsupported_format(self):
        """自動判定読み込みのテスト（サポートされていない形式）"""
        loader = DataLoader()
        
        with pytest.raises(ValueError, match="Unsupported file format"):
            loader.load(Path("data.xlsx"))
    
    def test_load_csv_with_chunksize(self, sample_csv):
        """CSV読み込みのテスト（チャンクサイズ指定）"""
        loader = DataLoader()
        df = loader.load_csv(sample_csv, chunksize=2)
        
        # chunksize指定時も結合されて返る
        assert len(df) == 4
        assert isinstance(df, pd.DataFrame)
```

---

**注**: ドキュメントが非常に長くなるため、ここでは Layer 1 (Configuration層) の5つのクラスと Layer 2 (Data層) の DataLoader クラスまでを詳細に記述しました。

残りのクラス（Layer 2～9）についても同様の詳細度で記述可能ですが、トークン制限のため、以下のような構成で続きを作成することを推奨します：

### 続きの構成案

1. **04_CLASS_DESIGN_DETAILED_PART2.md**: Layer 2 残り + Layer 3, 4
2. **04_CLASS_DESIGN_DETAILED_PART3.md**: Layer 5, 6
3. **04_CLASS_DESIGN_DETAILED_PART4.md**: Layer 7, 8, 9 + 共通クラス

各ファイルは以下を含みます：
- 完全なクラス定義（型ヒント、Docstring）
- すべてのメソッドの詳細
- 使用例
- 包括的なテストコード

---

**このファイルの統計**:
- **総行数**: 約3,500行
- **クラス数**: 6クラス（Config, PathConfig, ExecutionConfig, ModelSelectionConfig, ConfigLoader, DataLoader）
- **メソッド数**: 約60個
- **テストケース数**: 約50個

次のパートを作成しますか？
