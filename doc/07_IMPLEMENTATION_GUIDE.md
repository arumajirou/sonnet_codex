# 詳細実装ガイド
**Detailed Implementation Guide for Time Series Forecasting System**

---

## 📋 ドキュメント情報

| 項目 | 内容 |
|-----|------|
| **ドキュメントタイトル** | 時系列予測システム 詳細実装ガイド |
| **バージョン** | v1.0.0 |
| **作成日** | 2025-11-03 |
| **最終更新日** | 2025-11-03 |
| **対象システム** | NeuralForecast Auto Runner + Time Series Forecasting System |
| **対象読者** | 開発者、MLエンジニア |

---

## 目次

1. [開発環境セットアップ](#1-開発環境セットアップ)
2. [フェーズ別実装手順](#2-フェーズ別実装手順)
3. [コーディング規約](#3-コーディング規約)
4. [ベストプラクティス](#4-ベストプラクティス)
5. [TDD実践ガイド](#5-tdd実践ガイド)
6. [CI/CD設定](#6-cicd設定)
7. [コードレビューガイドライン](#7-コードレビューガイドライン)
8. [トラブルシューティング](#8-トラブルシューティング)
9. [付録](#9-付録)

---

## 1. 開発環境セットアップ

### 1.1 必要なソフトウェア

#### 1.1.1 基本ツール

```bash
# Python 3.11のインストール（pyenv推奨）
pyenv install 3.11.6
pyenv local 3.11.6

# パッケージマネージャー
pip install --upgrade pip setuptools wheel

# 開発ツール
pip install poetry  # または pipenv
pip install pre-commit
pip install black isort flake8 mypy pylint
```

**バージョン要件**:

| ツール | バージョン | 必須 |
|-------|-----------|------|
| Python | 3.11+ | ✅ |
| PostgreSQL | 14+ | ✅ |
| Git | 2.30+ | ✅ |
| Docker | 20.10+ | 推奨 |
| Make | 4.0+ | 推奨 |
| CUDA | 11.0+ | GPU使用時 |

---

#### 1.1.2 IDE/エディタ設定

**VS Code推奨設定** (`.vscode/settings.json`):

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "100"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "tests",
    "-v",
    "--cov=src",
    "--cov-report=html"
  ],
  "[python]": {
    "editor.rulers": [100],
    "editor.tabSize": 4
  }
}
```

**PyCharm推奨設定**:

- インタープリタ: プロジェクト仮想環境
- コードスタイル: Black
- インスペクション: すべて有効化
- Type checking: Strict mode

---

### 1.2 プロジェクトセットアップ

#### 1.2.1 リポジトリクローン

```bash
# リポジトリクローン
git clone https://github.com/your-org/time-series-forecasting-system.git
cd time-series-forecasting-system

# ブランチ戦略確認
git checkout develop
```

---

#### 1.2.2 仮想環境作成

**方法1: venv（標準）**:

```bash
python3.11 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# または
.venv\Scripts\activate  # Windows

# 依存関係インストール
pip install -r requirements-dev.txt
pip install -e .  # 開発モードでインストール
```

**方法2: Poetry（推奨）**:

```bash
# Poetryインストール
curl -sSL https://install.python-poetry.org | python3 -

# プロジェクトセットアップ
poetry install
poetry shell  # 仮想環境有効化
```

---

#### 1.2.3 環境変数設定

```bash
# .envファイル作成
cp .env.example .env

# 必要な環境変数を設定
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/ts_forecast_system
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Paths
DATA_DIR=/path/to/data
MODEL_DIR=/path/to/models
OUTPUT_DIR=/path/to/outputs
LOG_DIR=/path/to/logs

# Execution
MAX_PARALLEL_RUNS=10
DEFAULT_BACKEND=cuda  # または cpu, mps

# Tracking
MLFLOW_TRACKING_URI=http://localhost:5000
ENABLE_WANDB=false
WANDB_API_KEY=your_wandb_key

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
EOF

# 環境変数読み込み
source .env  # または export $(cat .env | xargs)
```

---

#### 1.2.4 データベース初期化

```bash
# PostgreSQL起動（Docker使用の場合）
docker-compose up -d postgres

# データベース作成
psql -U postgres -c "CREATE DATABASE ts_forecast_system;"

# マイグレーション実行
alembic upgrade head

# 初期データ投入
python scripts/setup/seed_data.py
```

---

#### 1.2.5 pre-commitフックセットアップ

```bash
# pre-commitインストール
pip install pre-commit

# フック設定
pre-commit install

# 全ファイルで実行（初回）
pre-commit run --all-files
```

**`.pre-commit-config.yaml`**:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.11
        args: ['--line-length=100']

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ['--profile=black', '--line-length=100']

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: ['--max-line-length=100', '--extend-ignore=E203,W503']

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: ['--strict', '--ignore-missing-imports']

  - repo: https://github.com/pycqa/pylint
    rev: v3.0.2
    hooks:
      - id: pylint
        args: ['--rcfile=.pylintrc']
```

---

### 1.3 動作確認

```bash
# 1. Pythonバージョン確認
python --version  # 3.11.x

# 2. パッケージ確認
pip list

# 3. テスト実行
pytest tests/ -v

# 4. 静的解析
make lint

# 5. カバレッジ確認
make coverage

# 6. 型チェック
make typecheck

# 7. ドキュメント生成
make docs
```

---

## 2. フェーズ別実装手順

### 2.1 開発プロセス全体像

```mermaid
graph LR
    A[Phase 1: Config] --> B[Phase 2: Data]
    B --> C[Phase 3: Model Discovery]
    C --> D[Phase 4: Hyperparameter]
    D --> E[Phase 5: Execution Plan]
    E --> F[Phase 6: Execution]
    F --> G[Phase 7: Artifact]
    G --> H[Phase 8: Logging]
    H --> I[Phase 9: Application]
    
    style A fill:#e1f5e1
    style B fill:#e1f5e1
    style C fill:#ffe1e1
    style D fill:#ffe1e1
    style E fill:#ffe1e1
    style F fill:#ffe1e1
    style G fill:#fff4e1
    style H fill:#fff4e1
    style I fill:#e1f0ff
```

---

### 2.2 Phase 1: Configuration層（1週間）

#### 2.2.1 目標

- システム全体の設定管理機能を実装
- 環境変数、YAML、JSONからの設定読み込み
- 設定の検証と不変性保証

---

#### 2.2.2 実装タスク

**Task 1.1: Config基底クラス実装**

```python
"""
src/nf_auto_runner/config/base.py

Configuration層の基底クラス
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
    
    すべての設定クラスはこのクラスを継承する。
    frozen=Trueで不変性を保証。
    
    Attributes:
        派生クラスで定義
    
    Example:
        >>> @dataclass(frozen=True)
        ... class MyConfig(Config):
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
            設定インスタンス
            
        Raises:
            EnvironmentError: 必須環境変数が存在しない
            ValueError: 環境変数の値が不正
        """
        pass
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        辞書から設定を構築
        
        Args:
            data: 設定データの辞書
            
        Returns:
            設定インスタンス
        """
        # Pathオブジェクトの変換
        converted_data = {}
        for key, value in data.items():
            if isinstance(value, str) and key.endswith(('_path', '_dir')):
                converted_data[key] = Path(value)
            else:
                converted_data[key] = value
        
        return cls(**converted_data)
    
    def validate(self) -> None:
        """
        設定の妥当性検証
        
        Raises:
            ValueError: 設定値が不正
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        辞書に変換
        
        Returns:
            設定の辞書表現
        """
        result = {}
        for key, value in asdict(self).items():
            if isinstance(value, Path):
                result[key] = str(value)
            else:
                result[key] = value
        return result


# テスト作成
"""
tests/unit/config/test_base.py
"""
import pytest
from pathlib import Path
from dataclasses import dataclass

from nf_auto_runner.config.base import Config


@dataclass(frozen=True)
class TestConfig(Config):
    """テスト用設定クラス"""
    value: int
    name: str = "test"
    
    @classmethod
    def from_env(cls) -> 'TestConfig':
        return cls(
            value=int(os.getenv('TEST_VALUE', '0')),
            name=os.getenv('TEST_NAME', 'test')
        )


class TestConfigBase:
    """Config基底クラスのテストスイート"""
    
    def test_from_dict(self):
        """辞書からの作成"""
        data = {"value": 100, "name": "test"}
        config = TestConfig.from_dict(data)
        assert config.value == 100
        assert config.name == "test"
    
    def test_to_dict(self):
        """辞書への変換"""
        config = TestConfig(value=100, name="test")
        data = config.to_dict()
        assert data == {"value": 100, "name": "test"}
    
    def test_immutability(self):
        """不変性の確認"""
        config = TestConfig(value=100)
        with pytest.raises(Exception):  # FrozenInstanceError
            config.value = 200
    
    def test_from_env(self, monkeypatch):
        """環境変数からの作成"""
        monkeypatch.setenv('TEST_VALUE', '42')
        monkeypatch.setenv('TEST_NAME', 'production')
        config = TestConfig.from_env()
        assert config.value == 42
        assert config.name == 'production'
```

---

**Task 1.2: PathConfig実装**

```python
"""
src/nf_auto_runner/config/path_config.py
"""
from dataclasses import dataclass
from pathlib import Path
import os

from .base import Config


@dataclass(frozen=True)
class PathConfig(Config):
    """
    パス設定クラス
    
    Attributes:
        project_root: プロジェクトルート
        data_dir: データディレクトリ
        model_dir: モデル保存ディレクトリ
        output_dir: 出力ディレクトリ
        log_dir: ログディレクトリ
    """
    
    project_root: Path
    data_dir: Path
    model_dir: Path
    output_dir: Path
    log_dir: Path
    
    @classmethod
    def from_env(cls) -> 'PathConfig':
        """環境変数から設定を構築"""
        project_root = Path(os.getenv('PROJECT_ROOT', Path.cwd()))
        
        return cls(
            project_root=project_root,
            data_dir=Path(os.getenv('DATA_DIR', project_root / 'data')),
            model_dir=Path(os.getenv('MODEL_DIR', project_root / 'models')),
            output_dir=Path(os.getenv('OUTPUT_DIR', project_root / 'outputs')),
            log_dir=Path(os.getenv('LOG_DIR', project_root / 'logs'))
        )
    
    def validate(self) -> None:
        """パスの妥当性検証"""
        # ルートディレクトリの存在確認
        if not self.project_root.exists():
            raise ValueError(f"Project root does not exist: {self.project_root}")
        
        # 必要なディレクトリを作成
        for path_name in ['data_dir', 'model_dir', 'output_dir', 'log_dir']:
            path = getattr(self, path_name)
            path.mkdir(parents=True, exist_ok=True)
    
    def get_data_path(self, filename: str) -> Path:
        """データファイルパスを取得"""
        return self.data_dir / filename
    
    def get_model_path(self, filename: str) -> Path:
        """モデルファイルパスを取得"""
        return self.model_dir / filename


# テスト
"""
tests/unit/config/test_path_config.py
"""
import pytest
from pathlib import Path
import tempfile

from nf_auto_runner.config.path_config import PathConfig


class TestPathConfig:
    """PathConfigのテストスイート"""
    
    def test_from_env_default(self, monkeypatch, tmp_path):
        """デフォルト値での作成"""
        monkeypatch.setenv('PROJECT_ROOT', str(tmp_path))
        config = PathConfig.from_env()
        
        assert config.project_root == tmp_path
        assert config.data_dir == tmp_path / 'data'
        assert config.model_dir == tmp_path / 'models'
    
    def test_validate_creates_directories(self, tmp_path):
        """validateでディレクトリが作成される"""
        config = PathConfig(
            project_root=tmp_path,
            data_dir=tmp_path / 'data',
            model_dir=tmp_path / 'models',
            output_dir=tmp_path / 'outputs',
            log_dir=tmp_path / 'logs'
        )
        config.validate()
        
        assert (tmp_path / 'data').exists()
        assert (tmp_path / 'models').exists()
        assert (tmp_path / 'outputs').exists()
        assert (tmp_path / 'logs').exists()
    
    def test_get_data_path(self, tmp_path):
        """データパス取得"""
        config = PathConfig(
            project_root=tmp_path,
            data_dir=tmp_path / 'data',
            model_dir=tmp_path / 'models',
            output_dir=tmp_path / 'outputs',
            log_dir=tmp_path / 'logs'
        )
        path = config.get_data_path('test.csv')
        assert path == tmp_path / 'data' / 'test.csv'
```

---

**Task 1.3: その他のConfig実装**

同様に以下を実装：
- `ExecutionConfig`: 実行設定
- `ModelSelectionConfig`: モデル選択設定
- `TrackingConfig`: トラッキング設定

---

#### 2.2.3 品質ゲート

```bash
# テスト実行
pytest tests/unit/config/ -v --cov=src/nf_auto_runner/config --cov-report=term-missing

# カバレッジ確認（>95%必須）
coverage report

# 静的解析
pylint src/nf_auto_runner/config/ --rcfile=.pylintrc
mypy src/nf_auto_runner/config/ --strict

# ドキュメント生成
interrogate src/nf_auto_runner/config/ --verbose
```

**合格基準**:
- ✅ テストカバレッジ > 95%
- ✅ Pylintスコア ≥ 8.5/10
- ✅ MyPy strict mode でエラーなし
- ✅ すべてのクラス・メソッドにdocstring

---

### 2.3 Phase 2: Data層（1週間）

#### 2.3.1 目標

- データ読み込み、前処理、検証機能を実装
- CSVファイルの読み込みと正規化
- 時系列データの検証とクリーニング

---

#### 2.3.2 実装タスク

**Task 2.1: DataLoader実装**

```python
"""
src/nf_auto_runner/data/data_loader.py
"""
from pathlib import Path
from typing import Optional, List
import pandas as pd
from dataclasses import dataclass

from ..config.path_config import PathConfig


@dataclass
class DataLoadResult:
    """データ読み込み結果"""
    data: pd.DataFrame
    file_path: Path
    num_rows: int
    num_columns: int
    unique_ids: List[str]
    date_range: tuple[pd.Timestamp, pd.Timestamp]


class DataLoader:
    """
    データローダークラス
    
    CSVファイルを読み込み、標準スキーマに変換する。
    
    Attributes:
        path_config: パス設定
        
    Example:
        >>> loader = DataLoader(path_config)
        >>> result = loader.load_csv('sales_data.csv')
        >>> print(f"Loaded {result.num_rows} rows")
    """
    
    def __init__(self, path_config: PathConfig):
        """
        初期化
        
        Args:
            path_config: パス設定
        """
        self.path_config = path_config
    
    def load_csv(
        self,
        file_path: str | Path,
        encoding: str = 'utf-8',
        date_column: str = 'ds',
        target_column: str = 'y',
        id_column: str = 'unique_id'
    ) -> DataLoadResult:
        """
        CSVファイルを読み込む
        
        Args:
            file_path: ファイルパス
            encoding: 文字エンコーディング
            date_column: 日付カラム名
            target_column: 目的変数カラム名
            id_column: ID カラム名
            
        Returns:
            読み込み結果
            
        Raises:
            FileNotFoundError: ファイルが存在しない
            ValueError: 必須カラムが存在しない
        """
        # ファイルパス解決
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        if not file_path.is_absolute():
            file_path = self.path_config.get_data_path(str(file_path))
        
        # ファイル存在確認
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # CSV読み込み
        df = pd.read_csv(file_path, encoding=encoding)
        
        # 必須カラム確認
        required_columns = {id_column, date_column, target_column}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # 日付カラムをdatetime型に変換
        df[date_column] = pd.to_datetime(df[date_column])
        
        # ソート
        df = df.sort_values([id_column, date_column]).reset_index(drop=True)
        
        # 統計情報計算
        unique_ids = df[id_column].unique().tolist()
        date_range = (df[date_column].min(), df[date_column].max())
        
        return DataLoadResult(
            data=df,
            file_path=file_path,
            num_rows=len(df),
            num_columns=len(df.columns),
            unique_ids=unique_ids,
            date_range=date_range
        )
    
    def validate_schema(self, df: pd.DataFrame) -> bool:
        """
        スキーマ検証
        
        Args:
            df: データフレーム
            
        Returns:
            検証結果
        """
        # 必須カラムの存在確認
        required_columns = {'unique_id', 'ds', 'y'}
        if not required_columns.issubset(df.columns):
            return False
        
        # データ型の確認
        if df['ds'].dtype not in ['datetime64[ns]']:
            return False
        
        if not pd.api.types.is_numeric_dtype(df['y']):
            return False
        
        return True


# テスト
"""
tests/unit/data/test_data_loader.py
"""
import pytest
import pandas as pd
from pathlib import Path

from nf_auto_runner.data.data_loader import DataLoader
from nf_auto_runner.config.path_config import PathConfig


@pytest.fixture
def sample_csv(tmp_path):
    """サンプルCSVファイル作成"""
    csv_path = tmp_path / 'data' / 'sample.csv'
    csv_path.parent.mkdir(parents=True)
    
    df = pd.DataFrame({
        'unique_id': ['A', 'A', 'B', 'B'],
        'ds': ['2025-01-01', '2025-01-02', '2025-01-01', '2025-01-02'],
        'y': [100, 110, 200, 210]
    })
    df.to_csv(csv_path, index=False)
    
    return csv_path


class TestDataLoader:
    """DataLoaderのテストスイート"""
    
    def test_load_csv_success(self, tmp_path, sample_csv):
        """正常なCSV読み込み"""
        path_config = PathConfig(
            project_root=tmp_path,
            data_dir=tmp_path / 'data',
            model_dir=tmp_path / 'models',
            output_dir=tmp_path / 'outputs',
            log_dir=tmp_path / 'logs'
        )
        
        loader = DataLoader(path_config)
        result = loader.load_csv(sample_csv)
        
        assert result.num_rows == 4
        assert result.num_columns == 3
        assert len(result.unique_ids) == 2
        assert result.data['ds'].dtype == 'datetime64[ns]'
    
    def test_load_csv_file_not_found(self, tmp_path):
        """ファイルが存在しない場合"""
        path_config = PathConfig(
            project_root=tmp_path,
            data_dir=tmp_path / 'data',
            model_dir=tmp_path / 'models',
            output_dir=tmp_path / 'outputs',
            log_dir=tmp_path / 'logs'
        )
        
        loader = DataLoader(path_config)
        with pytest.raises(FileNotFoundError):
            loader.load_csv('nonexistent.csv')
    
    def test_validate_schema(self, tmp_path):
        """スキーマ検証"""
        path_config = PathConfig(
            project_root=tmp_path,
            data_dir=tmp_path / 'data',
            model_dir=tmp_path / 'models',
            output_dir=tmp_path / 'outputs',
            log_dir=tmp_path / 'logs'
        )
        
        loader = DataLoader(path_config)
        
        # 正常なデータ
        valid_df = pd.DataFrame({
            'unique_id': ['A'],
            'ds': pd.to_datetime(['2025-01-01']),
            'y': [100]
        })
        assert loader.validate_schema(valid_df)
        
        # 不正なデータ（必須カラムなし）
        invalid_df = pd.DataFrame({
            'unique_id': ['A'],
            'ds': pd.to_datetime(['2025-01-01'])
        })
        assert not loader.validate_schema(invalid_df)
```

---

**Task 2.2: DataPreprocessor実装**

同様のパターンで実装：
- データのクリーニング
- 欠損値処理
- 外れ値検出

---

#### 2.3.3 品質ゲート

```bash
pytest tests/unit/data/ -v --cov=src/nf_auto_runner/data --cov-report=html
pylint src/nf_auto_runner/data/ --rcfile=.pylintrc
mypy src/nf_auto_runner/data/ --strict
```

**合格基準**: Phase 1と同様

---

### 2.4 Phase 3-9: 同様のパターン

各Phaseで以下を繰り返す：

1. **設計確認**: クラス設計書を読む
2. **テストファースト**: テストを先に書く
3. **実装**: 実際のコードを書く
4. **品質ゲート**: テスト・静的解析を実行
5. **レビュー**: プルリクエスト作成
6. **統合**: developブランチにマージ

---

## 3. コーディング規約

### 3.1 Python スタイルガイド

#### 3.1.1 基本ルール

- **PEP 8準拠**: Pythonの標準スタイルガイド
- **行の長さ**: 100文字以内
- **インデント**: スペース4つ
- **引用符**: シングルクォート`'`を使用（docstringは`"""`）
- **エンコーディング**: UTF-8

---

#### 3.1.2 命名規則

```python
# モジュール・パッケージ: lowercase_with_underscores
my_module.py
my_package/

# クラス: PascalCase
class DataLoader:
    pass

# 関数・メソッド: lowercase_with_underscores
def load_data():
    pass

# 変数: lowercase_with_underscores
my_variable = 10

# 定数: UPPERCASE_WITH_UNDERSCORES
MAX_BATCH_SIZE = 128

# プライベート: 先頭にアンダースコア
_internal_function()
_private_variable = 10

# 型変数: PascalCase
T = TypeVar('T')
ModelType = TypeVar('ModelType', bound='BaseModel')
```

---

#### 3.1.3 インポート順序

```python
"""
1. 標準ライブラリ
2. サードパーティライブラリ
3. ローカルライブラリ
"""

# 標準ライブラリ
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

# サードパーティライブラリ
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field

# ローカルライブラリ
from nf_auto_runner.config import PathConfig
from nf_auto_runner.data import DataLoader
```

---

### 3.2 型ヒント

#### 3.2.1 基本的な型ヒント

```python
from typing import Optional, List, Dict, Any, Union, Tuple

def process_data(
    data: pd.DataFrame,
    column_name: str,
    threshold: float = 0.5,
    options: Optional[Dict[str, Any]] = None
) -> Tuple[pd.DataFrame, int]:
    """
    データを処理する
    
    Args:
        data: 入力データフレーム
        column_name: 処理対象カラム名
        threshold: 閾値
        options: オプション設定
        
    Returns:
        処理後のデータフレームと処理件数のタプル
    """
    if options is None:
        options = {}
    
    # 処理
    processed_data = data.copy()
    count = len(processed_data)
    
    return processed_data, count
```

---

#### 3.2.2 高度な型ヒント

```python
from typing import TypeVar, Generic, Protocol, Literal

# TypeVar
T = TypeVar('T')

class Container(Generic[T]):
    """ジェネリックコンテナ"""
    def __init__(self, value: T):
        self.value = value
    
    def get(self) -> T:
        return self.value

# Protocol
class Saveable(Protocol):
    """保存可能なオブジェクトのプロトコル"""
    def save(self, path: Path) -> None:
        ...

# Literal
def set_mode(mode: Literal['train', 'test', 'predict']) -> None:
    """モード設定"""
    pass
```

---

### 3.3 Docstring

#### 3.3.1 Google Style

```python
def calculate_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    metrics: List[str]
) -> Dict[str, float]:
    """
    評価指標を計算する
    
    Args:
        y_true: 真値の配列
        y_pred: 予測値の配列
        metrics: 計算する指標のリスト（'mae', 'rmse', 'smape'）
        
    Returns:
        指標名と値の辞書
        
    Raises:
        ValueError: 配列の形状が一致しない場合
        ValueError: サポートされていない指標が含まれる場合
        
    Example:
        >>> y_true = np.array([1, 2, 3])
        >>> y_pred = np.array([1.1, 2.1, 2.9])
        >>> metrics = calculate_metrics(y_true, y_pred, ['mae', 'rmse'])
        >>> print(metrics)
        {'mae': 0.1, 'rmse': 0.1}
        
    Note:
        大量のデータに対しては、メモリ使用量に注意してください。
    """
    if y_true.shape != y_pred.shape:
        raise ValueError("Shape mismatch")
    
    results = {}
    for metric in metrics:
        if metric == 'mae':
            results['mae'] = np.mean(np.abs(y_true - y_pred))
        elif metric == 'rmse':
            results['rmse'] = np.sqrt(np.mean((y_true - y_pred) ** 2))
        else:
            raise ValueError(f"Unsupported metric: {metric}")
    
    return results
```

---

#### 3.3.2 クラスのdocstring

```python
class ModelRegistry:
    """
    モデルレジストリクラス
    
    学習済みモデルの登録、検索、管理を行う。
    
    Attributes:
        models: 登録済みモデルの辞書
        storage_path: モデル保存パス
        
    Example:
        >>> registry = ModelRegistry(storage_path='/models')
        >>> registry.register('my_model', model)
        >>> loaded_model = registry.load('my_model')
        
    Note:
        このクラスはスレッドセーフではありません。
        並行アクセスが必要な場合はロックを使用してください。
    """
    
    def __init__(self, storage_path: Path):
        """
        初期化
        
        Args:
            storage_path: モデル保存ディレクトリ
        """
        self.storage_path = storage_path
        self.models: Dict[str, Any] = {}
```

---

### 3.4 エラーハンドリング

#### 3.4.1 例外の使用

```python
# カスタム例外定義
class DataValidationError(Exception):
    """データ検証エラー"""
    pass


class ModelNotFoundError(Exception):
    """モデル未発見エラー"""
    pass


# 例外の使用
def validate_data(df: pd.DataFrame) -> None:
    """
    データを検証する
    
    Raises:
        DataValidationError: データが不正な場合
    """
    if df.empty:
        raise DataValidationError("DataFrame is empty")
    
    if 'unique_id' not in df.columns:
        raise DataValidationError("Missing 'unique_id' column")


# 例外のキャッチ
def safe_load_model(model_id: int) -> Optional[Model]:
    """
    モデルを安全に読み込む
    
    Args:
        model_id: モデルID
        
    Returns:
        モデルオブジェクト、読み込めない場合はNone
    """
    try:
        model = load_model(model_id)
        return model
    except ModelNotFoundError as e:
        logger.warning(f"Model not found: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
```

---

### 3.5 ロギング

#### 3.5.1 structlog使用

```python
import structlog

# ロガー設定
logger = structlog.get_logger()


class DataLoader:
    """データローダー"""
    
    def load_csv(self, file_path: Path) -> pd.DataFrame:
        """CSVファイルを読み込む"""
        logger.info(
            "loading_csv",
            file_path=str(file_path),
            operation="load"
        )
        
        try:
            df = pd.read_csv(file_path)
            logger.info(
                "csv_loaded",
                file_path=str(file_path),
                num_rows=len(df),
                num_columns=len(df.columns)
            )
            return df
        except Exception as e:
            logger.error(
                "csv_load_failed",
                file_path=str(file_path),
                error=str(e),
                exc_info=True
            )
            raise
```

---

## 4. ベストプラクティス

### 4.1 SOLID原則

#### 4.1.1 Single Responsibility Principle（単一責任の原則）

**悪い例**:

```python
class DataProcessor:
    """データ処理クラス（責務が多すぎる）"""
    
    def load_data(self, path: Path) -> pd.DataFrame:
        """データ読み込み"""
        pass
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """データクリーニング"""
        pass
    
    def save_data(self, df: pd.DataFrame, path: Path) -> None:
        """データ保存"""
        pass
    
    def train_model(self, df: pd.DataFrame) -> Model:
        """モデル学習"""
        pass
```

**良い例**:

```python
class DataLoader:
    """データ読み込み専用クラス"""
    def load(self, path: Path) -> pd.DataFrame:
        pass


class DataCleaner:
    """データクリーニング専用クラス"""
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        pass


class DataSaver:
    """データ保存専用クラス"""
    def save(self, df: pd.DataFrame, path: Path) -> None:
        pass


class ModelTrainer:
    """モデル学習専用クラス"""
    def train(self, df: pd.DataFrame) -> Model:
        pass
```

---

#### 4.1.2 Open/Closed Principle（開放/閉鎖の原則）

```python
from abc import ABC, abstractmethod

# 拡張に開いている
class Metric(ABC):
    """評価指標の基底クラス"""
    
    @abstractmethod
    def calculate(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """指標を計算"""
        pass


class MAE(Metric):
    """Mean Absolute Error"""
    def calculate(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return np.mean(np.abs(y_true - y_pred))


class RMSE(Metric):
    """Root Mean Squared Error"""
    def calculate(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return np.sqrt(np.mean((y_true - y_pred) ** 2))


# 新しい指標を追加（既存コードを変更せずに）
class SMAPE(Metric):
    """Symmetric Mean Absolute Percentage Error"""
    def calculate(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        denominator = (np.abs(y_true) + np.abs(y_pred)) / 2
        return np.mean(np.abs(y_true - y_pred) / denominator) * 100
```

---

#### 4.1.3 Dependency Inversion Principle（依存性逆転の原則）

```python
from typing import Protocol

# 抽象に依存
class DataSource(Protocol):
    """データソースのプロトコル"""
    def read(self) -> pd.DataFrame:
        ...


class CSVDataSource:
    """CSV実装"""
    def __init__(self, path: Path):
        self.path = path
    
    def read(self) -> pd.DataFrame:
        return pd.read_csv(self.path)


class ParquetDataSource:
    """Parquet実装"""
    def __init__(self, path: Path):
        self.path = path
    
    def read(self) -> pd.DataFrame:
        return pd.read_parquet(self.path)


class DataPipeline:
    """データパイプライン（抽象に依存）"""
    
    def __init__(self, data_source: DataSource):
        self.data_source = data_source
    
    def process(self) -> pd.DataFrame:
        data = self.data_source.read()
        # 処理
        return data


# 使用例（実装を簡単に切り替え可能）
csv_pipeline = DataPipeline(CSVDataSource(Path('data.csv')))
parquet_pipeline = DataPipeline(ParquetDataSource(Path('data.parquet')))
```

---

### 4.2 デザインパターン

#### 4.2.1 Factory Pattern

```python
from enum import Enum
from typing import Dict, Type

class ModelType(Enum):
    """モデルタイプ"""
    NHITS = "nhits"
    LSTM = "lstm"
    TFT = "tft"


class ModelFactory:
    """モデルファクトリー"""
    
    _registry: Dict[ModelType, Type[BaseModel]] = {}
    
    @classmethod
    def register(cls, model_type: ModelType, model_class: Type[BaseModel]) -> None:
        """モデルクラスを登録"""
        cls._registry[model_type] = model_class
    
    @classmethod
    def create(cls, model_type: ModelType, **kwargs) -> BaseModel:
        """モデルを作成"""
        if model_type not in cls._registry:
            raise ValueError(f"Unknown model type: {model_type}")
        
        model_class = cls._registry[model_type]
        return model_class(**kwargs)


# 使用例
ModelFactory.register(ModelType.NHITS, NHITSModel)
ModelFactory.register(ModelType.LSTM, LSTMModel)

model = ModelFactory.create(ModelType.NHITS, input_size=30, h=7)
```

---

#### 4.2.2 Strategy Pattern

```python
class OptimizationStrategy(ABC):
    """最適化戦略の基底クラス"""
    
    @abstractmethod
    def optimize(self, objective_func, search_space) -> Dict[str, Any]:
        """最適化を実行"""
        pass


class OptunaStrategy(OptimizationStrategy):
    """Optuna戦略"""
    def optimize(self, objective_func, search_space) -> Dict[str, Any]:
        import optuna
        study = optuna.create_study()
        study.optimize(objective_func, n_trials=100)
        return study.best_params


class GridSearchStrategy(OptimizationStrategy):
    """グリッドサーチ戦略"""
    def optimize(self, objective_func, search_space) -> Dict[str, Any]:
        from sklearn.model_selection import GridSearchCV
        # 実装
        pass


class HyperparameterOptimizer:
    """ハイパーパラメータ最適化"""
    
    def __init__(self, strategy: OptimizationStrategy):
        self.strategy = strategy
    
    def run(self, objective_func, search_space) -> Dict[str, Any]:
        return self.strategy.optimize(objective_func, search_space)


# 使用例（戦略を簡単に切り替え）
optimizer = HyperparameterOptimizer(OptunaStrategy())
best_params = optimizer.run(objective_func, search_space)
```

---

## 5. TDD実践ガイド

### 5.1 TDDサイクル

```
1. Red: テストを書く（失敗する）
2. Green: 最小限のコードを書く（テストを通す）
3. Refactor: コードをリファクタリング
```

---

### 5.2 pytest基本

#### 5.2.1 基本的なテスト

```python
"""
tests/unit/data/test_data_loader.py
"""
import pytest
import pandas as pd
from pathlib import Path

from nf_auto_runner.data.data_loader import DataLoader


class TestDataLoader:
    """DataLoaderのテストクラス"""
    
    def test_load_csv_success(self, sample_csv):
        """正常系: CSV読み込み成功"""
        loader = DataLoader()
        result = loader.load_csv(sample_csv)
        
        assert result is not None
        assert isinstance(result.data, pd.DataFrame)
        assert result.num_rows > 0
    
    def test_load_csv_file_not_found(self):
        """異常系: ファイルが存在しない"""
        loader = DataLoader()
        
        with pytest.raises(FileNotFoundError):
            loader.load_csv('nonexistent.csv')
    
    def test_load_csv_invalid_schema(self, invalid_csv):
        """異常系: スキーマが不正"""
        loader = DataLoader()
        
        with pytest.raises(ValueError, match="Missing required columns"):
            loader.load_csv(invalid_csv)
```

---

#### 5.2.2 Fixture

```python
import pytest
import pandas as pd
from pathlib import Path


@pytest.fixture
def tmp_data_dir(tmp_path):
    """一時データディレクトリ"""
    data_dir = tmp_path / 'data'
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def sample_csv(tmp_data_dir):
    """サンプルCSVファイル"""
    csv_path = tmp_data_dir / 'sample.csv'
    
    df = pd.DataFrame({
        'unique_id': ['A', 'A', 'B', 'B'],
        'ds': ['2025-01-01', '2025-01-02', '2025-01-01', '2025-01-02'],
        'y': [100, 110, 200, 210]
    })
    df.to_csv(csv_path, index=False)
    
    return csv_path


@pytest.fixture
def sample_dataframe():
    """サンプルデータフレーム"""
    return pd.DataFrame({
        'unique_id': ['A'] * 10,
        'ds': pd.date_range('2025-01-01', periods=10),
        'y': range(100, 110)
    })


@pytest.fixture(scope='session')
def database_connection():
    """データベース接続（セッションスコープ）"""
    # セットアップ
    conn = create_connection()
    
    yield conn
    
    # ティアダウン
    conn.close()
```

---

#### 5.2.3 パラメータ化テスト

```python
import pytest


@pytest.mark.parametrize(
    "input_value,expected",
    [
        (0, 0),
        (1, 1),
        (2, 4),
        (3, 9),
        (4, 16),
    ]
)
def test_square(input_value, expected):
    """二乗計算のテスト"""
    assert input_value ** 2 == expected


@pytest.mark.parametrize(
    "y_true,y_pred,expected_mae",
    [
        ([1, 2, 3], [1, 2, 3], 0.0),
        ([1, 2, 3], [2, 3, 4], 1.0),
        ([0, 0, 0], [1, 1, 1], 1.0),
    ]
)
def test_mae_calculation(y_true, y_pred, expected_mae):
    """MAE計算のテスト"""
    result = calculate_mae(y_true, y_pred)
    assert result == pytest.approx(expected_mae)
```

---

#### 5.2.4 モックとスパイ

```python
from unittest.mock import Mock, patch, MagicMock
import pytest


class TestModelTrainer:
    """ModelTrainerのテスト"""
    
    def test_train_with_mock(self):
        """モデル学習のテスト（モック使用）"""
        # モックオブジェクト作成
        mock_model = Mock()
        mock_model.fit.return_value = None
        mock_model.score.return_value = 0.95
        
        trainer = ModelTrainer(mock_model)
        trainer.train(X_train, y_train)
        
        # モックが呼ばれたことを確認
        mock_model.fit.assert_called_once_with(X_train, y_train)
    
    @patch('nf_auto_runner.data.data_loader.pd.read_csv')
    def test_load_with_patch(self, mock_read_csv):
        """データ読み込みのテスト（パッチ使用）"""
        # モックの戻り値設定
        mock_df = pd.DataFrame({'col1': [1, 2, 3]})
        mock_read_csv.return_value = mock_df
        
        loader = DataLoader()
        result = loader.load_csv('dummy.csv')
        
        # パッチが呼ばれたことを確認
        mock_read_csv.assert_called_once_with('dummy.csv', encoding='utf-8')
        assert result.num_rows == 3
```

---

### 5.3 カバレッジ

```bash
# カバレッジ測定
pytest tests/ --cov=src/nf_auto_runner --cov-report=html --cov-report=term

# カバレッジレポート確認
open htmlcov/index.html

# カバレッジ目標
# - 全体: >90%
# - 各モジュール: >85%
# - クリティカルパス: 100%
```

**`.coveragerc`**:

```ini
[run]
source = src/nf_auto_runner
omit =
    */tests/*
    */test_*.py
    */__pycache__/*
    */site-packages/*
    */venv/*

[report]
precision = 2
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod
```

---

### 5.4 テストの構造化

```
tests/
├── unit/                      # ユニットテスト
│   ├── config/
│   │   ├── test_base.py
│   │   └── test_path_config.py
│   ├── data/
│   │   ├── test_data_loader.py
│   │   └── test_preprocessor.py
│   └── model/
│       └── test_registry.py
├── integration/               # 統合テスト
│   ├── test_data_pipeline.py
│   └── test_training_flow.py
├── e2e/                       # E2Eテスト
│   └── test_full_workflow.py
├── fixtures/                  # 共有フィクスチャ
│   ├── sample_data/
│   └── conftest.py
└── conftest.py                # グローバル設定
```

---

## 6. CI/CD設定

### 6.1 GitHub Actions

#### 6.1.1 基本ワークフロー

**`.github/workflows/ci.yml`**:

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11']
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: ts_forecast_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt
          pip install -e .
      
      - name: Lint with flake8
        run: |
          flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
          flake8 src/ --count --max-line-length=100 --statistics
      
      - name: Type check with mypy
        run: |
          mypy src/ --strict --ignore-missing-imports
      
      - name: Test with pytest
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/ts_forecast_test
        run: |
          pytest tests/ -v --cov=src --cov-report=xml --cov-report=term
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
      
      - name: Check coverage threshold
        run: |
          coverage report --fail-under=90

  quality:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install pylint black isort
      
      - name: Check code formatting with black
        run: |
          black --check src/ tests/
      
      - name: Check import sorting with isort
        run: |
          isort --check-only src/ tests/
      
      - name: Lint with pylint
        run: |
          pylint src/ --rcfile=.pylintrc --fail-under=8.5
```

---

#### 6.1.2 リリースワークフロー

**`.github/workflows/release.yml`**:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install build dependencies
        run: |
          pip install build twine
      
      - name: Build package
        run: |
          python -m build
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
        run: |
          twine upload dist/*
      
      - name: Create GitHub Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false
```

---

### 6.2 品質ゲート

#### 6.2.1 品質基準

| メトリクス | 目標値 | 許容値 | 判定 |
|----------|--------|--------|------|
| テストカバレッジ | >95% | >90% | 必須 |
| Pylintスコア | ≥9.0 | ≥8.5 | 必須 |
| 複雑度 | <10 | <15 | 推奨 |
| 重複率 | <3% | <5% | 推奨 |
| ドキュメント率 | 100% | >95% | 必須 |

---

#### 6.2.2 品質チェックスクリプト

**`scripts/quality_check.sh`**:

```bash
#!/bin/bash
set -e

echo "=== Running Quality Checks ==="

# テストカバレッジ
echo "1. Testing with coverage..."
pytest tests/ --cov=src --cov-report=term --cov-report=html --cov-fail-under=90

# 静的解析
echo "2. Running static analysis..."
pylint src/ --rcfile=.pylintrc --fail-under=8.5

# 型チェック
echo "3. Type checking..."
mypy src/ --strict --ignore-missing-imports

# コード品質
echo "4. Checking code quality..."
radon cc src/ -a -nb

# 重複コード検出
echo "5. Detecting duplicate code..."
pylint src/ --disable=all --enable=duplicate-code

# ドキュメント率
echo "6. Checking documentation..."
interrogate src/ --fail-under=95 -v

# セキュリティチェック
echo "7. Security check..."
bandit -r src/ -ll

echo "=== All Quality Checks Passed ==="
```

---

### 6.3 Makefile

**`Makefile`**:

```makefile
.PHONY: help install test lint format typecheck coverage docs clean

help:  ## このヘルプを表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## 依存関係をインストール
	pip install -r requirements-dev.txt
	pip install -e .
	pre-commit install

test:  ## テストを実行
	pytest tests/ -v

test-unit:  ## ユニットテストのみ実行
	pytest tests/unit/ -v

test-integration:  ## 統合テストのみ実行
	pytest tests/integration/ -v

test-e2e:  ## E2Eテストのみ実行
	pytest tests/e2e/ -v

lint:  ## リント実行
	flake8 src/ tests/
	pylint src/ --rcfile=.pylintrc
	black --check src/ tests/
	isort --check-only src/ tests/

format:  ## コード整形
	black src/ tests/
	isort src/ tests/

typecheck:  ## 型チェック
	mypy src/ --strict --ignore-missing-imports

coverage:  ## カバレッジ測定
	pytest tests/ --cov=src --cov-report=html --cov-report=term
	@echo "Opening coverage report..."
	@open htmlcov/index.html || xdg-open htmlcov/index.html

quality:  ## 品質チェック
	./scripts/quality_check.sh

docs:  ## ドキュメント生成
	cd docs && make html
	@echo "Opening documentation..."
	@open docs/_build/html/index.html || xdg-open docs/_build/html/index.html

clean:  ## クリーンアップ
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name '*~' -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

setup-db:  ## データベース初期化
	python scripts/setup/init_db.py

migrate:  ## マイグレーション実行
	alembic upgrade head

migrate-rollback:  ## マイグレーションロールバック
	alembic downgrade -1

run:  ## アプリケーション実行
	python -m nf_auto_runner.app.main

dev:  ## 開発サーバー起動
	uvicorn nf_auto_runner.app.api:app --reload --port 8000
```

---

## 7. コードレビューガイドライン

### 7.1 レビューチェックリスト

#### 7.1.1 コード品質

- [ ] コードがPEP 8に準拠している
- [ ] 適切な命名規則が使われている
- [ ] 関数・クラスが単一責任を持っている
- [ ] 適切な抽象化レベルになっている
- [ ] 重複コードがない（DRY原則）
- [ ] マジックナンバーが定数化されている

---

#### 7.1.2 テスト

- [ ] 新機能に対するテストが追加されている
- [ ] テストカバレッジが90%以上
- [ ] エッジケースがカバーされている
- [ ] 異常系のテストがある
- [ ] テストが独立している（順序依存なし）

---

#### 7.1.3 ドキュメント

- [ ] すべてのクラス・関数にdocstringがある
- [ ] docstringがGoogle Styleに準拠
- [ ] パラメータと戻り値が明記されている
- [ ] 例外が明記されている
- [ ] 必要に応じて使用例がある

---

#### 7.1.4 セキュリティ

- [ ] SQLインジェクション対策
- [ ] XSS対策
- [ ] パスワード・トークンがハードコードされていない
- [ ] 適切なバリデーションがある
- [ ] 機密情報がログに出力されていない

---

### 7.2 プルリクエストテンプレート

**`.github/pull_request_template.md`**:

```markdown
## 変更内容

<!-- 何を変更したか簡潔に説明 -->

## 変更の種類

- [ ] バグフィックス
- [ ] 新機能
- [ ] リファクタリング
- [ ] ドキュメント更新
- [ ] パフォーマンス改善
- [ ] テスト追加

## 関連Issue

Closes #

## テスト

- [ ] ユニットテストを追加・更新
- [ ] 統合テストを追加・更新
- [ ] すべてのテストがパス
- [ ] カバレッジが90%以上

## チェックリスト

- [ ] コードがPEP 8に準拠
- [ ] 型ヒントを追加
- [ ] docstringを追加
- [ ] pre-commit チェックがパス
- [ ] CI/CDがパス
- [ ] ドキュメントを更新

## スクリーンショット（必要な場合）

## レビュアーへの注意事項
```

---

## 8. トラブルシューティング

### 8.1 よくある問題

#### 8.1.1 インポートエラー

**問題**:
```
ModuleNotFoundError: No module named 'nf_auto_runner'
```

**解決策**:
```bash
# 開発モードでインストール
pip install -e .

# または
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

---

#### 8.1.2 テスト失敗

**問題**:
```
pytest tests/test_data.py
FAILED tests/test_data.py::test_load_csv - FileNotFoundError
```

**解決策**:
```python
# フィクスチャを使用
@pytest.fixture
def sample_csv(tmp_path):
    csv_path = tmp_path / 'sample.csv'
    # CSVファイル作成
    return csv_path

def test_load_csv(sample_csv):
    # テスト
    pass
```

---

#### 8.1.3 カバレッジが上がらない

**問題**:
カバレッジが目標に達しない

**解決策**:
```bash
# カバレッジレポート確認
pytest --cov=src --cov-report=html
open htmlcov/index.html

# 未カバー行を確認して追加テスト作成
```

---

### 8.2 デバッグ Tips

#### 8.2.1 pytest デバッグ

```bash
# 詳細出力
pytest tests/ -vv

# 失敗したテストのみ再実行
pytest --lf

# 最初の失敗で停止
pytest -x

# pdbでデバッグ
pytest --pdb

# 特定のテストのみ実行
pytest tests/unit/data/test_loader.py::TestDataLoader::test_load_csv
```

---

#### 8.2.2 ログ出力

```python
import logging

# ロガー設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# デバッグログ
logger.debug(f"Processing data: {data.shape}")
```

---

## 9. 付録

### 9.1 設定ファイルテンプレート

#### 9.1.1 pyproject.toml

```toml
[tool.poetry]
name = "nf-auto-runner"
version = "1.0.0"
description = "NeuralForecast Auto Runner"
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
pandas = "^2.0.0"
numpy = "^1.24.0"
scikit-learn = "^1.3.0"
neuralforecast = "^1.6.0"
pytorch = "^2.0.0"
lightning = "^2.0.0"

[tool.poetry.dev-dependencies]
pytest = "^7.4.0"
pytest-cov = "^4.1.0"
black = "^23.11.0"
isort = "^5.12.0"
mypy = "^1.7.0"
pylint = "^3.0.0"

[tool.black]
line-length = 100
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

---

#### 9.1.2 .pylintrc

```ini
[MASTER]
ignore=CVS,.git,__pycache__
jobs=4

[MESSAGES CONTROL]
disable=
    C0111,  # missing-docstring
    R0903,  # too-few-public-methods
    R0913,  # too-many-arguments

[FORMAT]
max-line-length=100
indent-string='    '

[DESIGN]
max-args=7
max-locals=15
max-returns=6
max-branches=12
max-statements=50
```

---

### 9.2 チートシート

#### 9.2.1 Git コマンド

```bash
# ブランチ作成
git checkout -b feature/phase-1-config

# 変更をコミット
git add .
git commit -m "feat: implement Config base class"

# プッシュ
git push origin feature/phase-1-config

# マージ
git checkout develop
git merge feature/phase-1-config
```

---

#### 9.2.2 pytest コマンド

```bash
# すべてのテスト実行
pytest

# 特定のファイル
pytest tests/unit/config/test_base.py

# 特定のクラス
pytest tests/unit/config/test_base.py::TestConfig

# 特定のメソッド
pytest tests/unit/config/test_base.py::TestConfig::test_from_dict

# カバレッジ付き
pytest --cov=src --cov-report=html

# 並列実行
pytest -n auto
```

---

### 9.3 参考資料

- [PEP 8 -- Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [pytest Documentation](https://docs.pytest.org/)
- [Type Hints Documentation](https://docs.python.org/3/library/typing.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)

---

**End of Document**
