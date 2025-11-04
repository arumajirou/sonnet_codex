# Phase 1 開始: Configuration Layer 実装

## Role
あなたは時系列予測システムのシニアMLエンジニアです。TDD（テスト駆動開発）で実装を進めます。

---

## プロジェクト概要

- **プロジェクト**: NeuralForecast Auto Runner（時系列予測の自動学習システム）
- **アーキテクチャ**: 9層レイヤードアーキテクチャ
- **技術スタック**: Python 3.11, NeuralForecast, PyTorch, PostgreSQL, MLflow

---

## 参照資料（必ず確認）

| 優先度 | ファイル | 内容 |
|-------|---------|------|
| 🔴 | `AGENTS.md` | リポジトリガイドライン |
| 🔴 | `doc/00_DEVELOPMENT_RULES_AND_HIGH_QUALITY_PROMPTS.md` | 開発ルール |
| 🔴 | `doc/04_CLASS_DESIGN_DETAILED.md` | クラス設計（Layer 1: Configuration） |
| 🟠 | `doc/08_CODING_STANDARDS.md` | コーディング規約 |

---

## Phase 1 の実装対象

### Layer 1: Configuration Layer

実装する主要クラス：

1. **Config (base class)** - 設定のベースクラス
2. **PathConfig** - パス設定
3. **ExecutionConfig** - 実行設定
4. **ModelSelectionConfig** - モデル選択設定

---

## 開発フロー（TDD）

### Step 1: テストを書く（Red）
```bash
# tests/unit/config/test_path_config.py を作成
```

### Step 2: テスト実行（失敗確認）
```bash
pytest tests/unit/config/test_path_config.py -v
# 期待: FAILED
```

### Step 3: 実装（Green）
```bash
# src/nf_auto_runner/config/path.py を作成
```

### Step 4: テスト再実行（成功確認）
```bash
pytest tests/unit/config/test_path_config.py -v
# 期待: PASSED
```

### Step 5: 品質チェック
```bash
make lint
make typecheck
pytest tests/unit/config/ --cov=src/nf_auto_runner/config --cov-report=term
```

---

## コーディング規約（厳守）

- **型ヒント必須**: すべての関数・メソッドに型ヒント
- **Docstring必須**: Google Style（Args/Returns/Raises）
- **行長**: 100文字以内
- **インデント**: 4スペース
- **命名**: snake_case (関数), CamelCase (クラス), UPPER_SNAKE_CASE (定数)

---

## 品質ゲート（Phase 1 完了基準）

- [ ] カバレッジ >90%
- [ ] Pylint ≥8.5
- [ ] MyPy strict pass (0 errors)
- [ ] すべての関数にDocstring
- [ ] すべてのテストパス

---

## 最初のタスク: Config ベースクラス

### 実装内容

```python
# src/nf_auto_runner/config/base.py

from dataclasses import dataclass
from typing import Dict, Any
import yaml

@dataclass
class Config:
    """設定のベースクラス
    
    すべての設定クラスはこのクラスを継承する。
    YAMLファイルからの読み込み・保存機能を提供。
    
    Attributes:
        name: 設定名
    """
    name: str
    
    @classmethod
    def from_yaml(cls, filepath: str) -> 'Config':
        """YAMLファイルから設定を読み込む
        
        Args:
            filepath: YAMLファイルのパス
        
        Returns:
            Config: 読み込んだ設定オブジェクト
        
        Raises:
            FileNotFoundError: ファイルが存在しない場合
            ValueError: YAMLの形式が不正な場合
        """
        pass
    
    def to_yaml(self, filepath: str) -> None:
        """設定をYAMLファイルに保存
        
        Args:
            filepath: 保存先のファイルパス
        
        Raises:
            IOError: ファイル書き込みに失敗した場合
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """設定を辞書に変換
        
        Returns:
            Dict[str, Any]: 設定の辞書表現
        """
        pass
```

### テスト内容

```python
# tests/unit/config/test_base.py

import pytest
from pathlib import Path
from nf_auto_runner.config.base import Config

class TestConfig:
    """Config ベースクラスのテスト"""
    
    @pytest.fixture
    def config(self):
        """設定フィクスチャ"""
        return Config(name="test_config")
    
    def test_init(self, config):
        """初期化テスト"""
        assert config.name == "test_config"
    
    def test_from_yaml_valid(self, tmp_path):
        """YAML読み込み（正常系）"""
        # YAMLファイル作成
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text("name: test_config\n")
        
        # 読み込み
        config = Config.from_yaml(str(yaml_file))
        
        assert config.name == "test_config"
    
    def test_from_yaml_file_not_found(self):
        """YAML読み込み（ファイルなし）"""
        with pytest.raises(FileNotFoundError):
            Config.from_yaml("/nonexistent/path.yaml")
    
    def test_from_yaml_invalid_format(self, tmp_path):
        """YAML読み込み（不正な形式）"""
        yaml_file = tmp_path / "invalid.yaml"
        yaml_file.write_text("invalid: yaml: format")
        
        with pytest.raises(ValueError):
            Config.from_yaml(str(yaml_file))
    
    def test_to_yaml(self, config, tmp_path):
        """YAML保存"""
        yaml_file = tmp_path / "output.yaml"
        config.to_yaml(str(yaml_file))
        
        # ファイルが作成されたことを確認
        assert yaml_file.exists()
        
        # 内容を確認
        content = yaml_file.read_text()
        assert "name: test_config" in content
    
    def test_to_dict(self, config):
        """辞書変換"""
        result = config.to_dict()
        
        assert isinstance(result, dict)
        assert result["name"] == "test_config"
```

---

## 実行手順

### 1. 環境準備
```bash
cd /mnt/e/env/ts/sonnet_codex
poetry install
poetry shell
```

### 2. ディレクトリ作成
```bash
mkdir -p src/nf_auto_runner/config
mkdir -p tests/unit/config
touch src/nf_auto_runner/config/__init__.py
touch tests/unit/config/__init__.py
```

### 3. テストファイル作成
```bash
# tests/unit/config/test_base.py を作成
# 上記のテストコードを記述
```

### 4. テスト実行（Red）
```bash
pytest tests/unit/config/test_base.py -v
# 期待: ImportError または FAILED
```

### 5. 実装
```bash
# src/nf_auto_runner/config/base.py を作成
# 上記の実装コードを記述
```

### 6. テスト実行（Green）
```bash
pytest tests/unit/config/test_base.py -v
# 期待: PASSED
```

### 7. 品質チェック
```bash
# 型チェック
mypy src/nf_auto_runner/config/base.py --strict

# Linting
pylint src/nf_auto_runner/config/base.py

# フォーマット
black src/nf_auto_runner/config/base.py

# カバレッジ
pytest tests/unit/config/ --cov=src/nf_auto_runner/config --cov-report=term
```

### 8. コミット
```bash
git add tests/unit/config/test_base.py
git add src/nf_auto_runner/config/base.py

git commit -m "feat: implement Config base class

- Add Config base class with YAML I/O
- Add unit tests (coverage: 95%)
- Pass all quality gates

Refs: doc/04_CLASS_DESIGN_DETAILED.md Section 1.1"
```

---

## あなたへの依頼

### タスク
1. 上記の `Config` ベースクラスを実装してください
2. TDD に従い、テストを先に書いてから実装してください
3. 品質チェックをすべてパスしてください

### 確認事項
- [ ] テストを先に書きましたか？
- [ ] テストが失敗することを確認しましたか？
- [ ] 実装後、テストがパスしましたか？
- [ ] 型ヒントをすべて追加しましたか？
- [ ] Docstring を追加しましたか（Google Style）？
- [ ] `make lint` がパスしますか？
- [ ] `make typecheck` がパスしますか？
- [ ] カバレッジが90%を超えていますか？

### 出力形式

実装完了後、以下のJSON形式でレポートしてください：

```json
{
  "task": "Config base class implementation",
  "status": "completed",
  "files_created": [
    "src/nf_auto_runner/config/base.py",
    "tests/unit/config/test_base.py"
  ],
  "quality_metrics": {
    "coverage_percent": 95.0,
    "pylint_score": 9.0,
    "mypy_errors": 0
  },
  "tests_passed": 6,
  "tests_failed": 0,
  "next_steps": [
    "Implement PathConfig class"
  ]
}
```

---

## 開始してください！

**準備ができたら、Config ベースクラスの実装を開始してください。**

TDD に従い、テストから書き始めてください。不明点があれば質問してください。
