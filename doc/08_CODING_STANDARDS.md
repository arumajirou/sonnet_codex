# コーディング規約
**Coding Standards for Time Series Forecasting System**

---

## 📋 ドキュメント情報

| 項目 | 内容 |
|-----|------|
| **ドキュメントタイトル** | 時系列予測システム コーディング規約 |
| **バージョン** | v1.0.0 |
| **作成日** | 2025-11-03 |
| **最終更新日** | 2025-11-03 |
| **対象システム** | NeuralForecast Auto Runner + Time Series Forecasting System |
| **準拠規格** | PEP 8, PEP 257, PEP 484, Google Python Style Guide |

---

## 目次

1. [基本原則](#1-基本原則)
2. [Pythonスタイルガイド](#2-pythonスタイルガイド)
3. [命名規則](#3-命名規則)
4. [コード構造](#4-コード構造)
5. [ドキュメンテーション](#5-ドキュメンテーション)
6. [型ヒント](#6-型ヒント)
7. [エラーハンドリング](#7-エラーハンドリング)
8. [テストコード規約](#8-テストコード規約)
9. [パフォーマンス](#9-パフォーマンス)
10. [セキュリティ](#10-セキュリティ)
11. [データベース規約](#11-データベース規約)
12. [API設計規約](#12-api設計規約)
13. [付録](#13-付録)

---

## 1. 基本原則

### 1.1 コーディングの哲学

#### 1.1.1 Zen of Python

```python
import this

# The Zen of Python, by Tim Peters
# 
# Beautiful is better than ugly.
# Explicit is better than implicit.
# Simple is better than complex.
# Complex is better than complicated.
# Flat is better than nested.
# Sparse is better than dense.
# Readability counts.
# ...
```

---

#### 1.1.2 核心原則

| 原則 | 説明 | 例 |
|-----|------|---|
| **読みやすさ重視** | コードは書く時間より読む時間の方が長い | 明確な変数名、適切なコメント |
| **明示的であれ** | 暗黙的な動作を避ける | 明示的な引数、明確な戻り値 |
| **DRY原則** | Don't Repeat Yourself | 共通処理を関数化 |
| **KISS原則** | Keep It Simple, Stupid | 複雑さを避ける |
| **YAGNI原則** | You Aren't Gonna Need It | 必要になるまで実装しない |
| **関心の分離** | 責務を明確に分ける | 層ごとに責務を分離 |

---

### 1.2 品質基準

| 項目 | 目標値 | 測定方法 |
|-----|--------|---------|
| **テストカバレッジ** | >90% | pytest-cov |
| **Pylintスコア** | ≥8.5/10 | pylint |
| **型チェック** | エラー0件 | mypy --strict |
| **循環的複雑度** | <10 | radon cc |
| **重複コード** | <3% | pylint duplicate-code |
| **ドキュメント率** | 100% | interrogate |
| **行数/関数** | <50行 | 目視確認 |
| **引数/関数** | ≤7個 | 目視確認 |

---

## 2. Pythonスタイルガイド

### 2.1 コードレイアウト

#### 2.1.1 インデント

```python
# ✅ 良い例: 4スペース
def calculate_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    metrics: List[str]
) -> Dict[str, float]:
    """評価指標を計算"""
    results = {}
    for metric in metrics:
        if metric == 'mae':
            results['mae'] = np.mean(np.abs(y_true - y_pred))
    return results


# ❌ 悪い例: タブ使用
def calculate_metrics():
	pass  # タブは使わない


# ❌ 悪い例: 2スペース
def calculate_metrics():
  pass  # 2スペースは使わない
```

---

#### 2.1.2 行の長さ

```python
# ✅ 良い例: 100文字以内
def process_data(
    input_data: pd.DataFrame,
    config: ProcessingConfig
) -> pd.DataFrame:
    """データを処理する"""
    pass


# ✅ 良い例: 長い文字列の分割
message = (
    "This is a very long message that needs to be split "
    "across multiple lines to maintain readability and "
    "adhere to the line length limit."
)


# ❌ 悪い例: 100文字超過
def process_data_with_very_long_function_name_that_exceeds_limit(input_data, config, options, metadata):
    pass
```

---

#### 2.1.3 空行

```python
# ✅ 良い例: 適切な空行
"""モジュールdocstring"""

import os
import sys
from typing import List

import pandas as pd
import numpy as np

from nf_auto_runner.config import Config


class DataLoader:
    """クラス定義の前に2行空ける"""
    
    def __init__(self):
        """メソッド間は1行空ける"""
        pass
    
    def load_data(self):
        """メソッド定義"""
        pass


class DataProcessor:
    """トップレベルクラス間は2行空ける"""
    pass


def standalone_function():
    """トップレベル関数の前も2行空ける"""
    pass


# ❌ 悪い例: 空行が不適切
import os
import pandas as pd
class DataLoader:
    def __init__(self):
        pass
    def load_data(self):
        pass
```

---

#### 2.1.4 引用符

```python
# ✅ 良い例: シングルクォート
name = 'data_loader'
message = 'Processing data'

# docstringはトリプルダブルクォート
def process():
    """データを処理する"""
    pass

# 文字列内にシングルクォートがある場合はダブルクォート
text = "It's a beautiful day"


# ❌ 悪い例: 一貫性がない
name = "data_loader"  # ダブルクォート不要
message = 'Processing data'
text = 'It\'s a beautiful day'  # エスケープ不要
```

---

### 2.2 インポート

#### 2.2.1 インポート順序

```python
"""
1. 標準ライブラリ
2. サードパーティライブラリ
3. ローカルアプリケーション
各グループ間は1行空ける
"""

# ✅ 良い例
# 標準ライブラリ
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# サードパーティライブラリ
import numpy as np
import pandas as pd
from pydantic import BaseModel
from sqlalchemy import Column, Integer

# ローカルアプリケーション
from nf_auto_runner.config import PathConfig
from nf_auto_runner.data import DataLoader
from nf_auto_runner.model import ModelRegistry


# ❌ 悪い例: 順序がバラバラ
import pandas as pd
import os
from nf_auto_runner.config import PathConfig
import numpy as np
from typing import List
```

---

#### 2.2.2 インポート形式

```python
# ✅ 良い例: 明示的インポート
from typing import List, Dict, Optional
from pathlib import Path
import numpy as np
import pandas as pd


# ❌ 悪い例: ワイルドカードインポート
from typing import *  # 何がインポートされたか不明
from nf_auto_runner.data import *  # 名前空間汚染


# ✅ 良い例: 相対インポート（パッケージ内）
from .config import Config  # 同じパッケージ
from ..data import DataLoader  # 親パッケージ
from ...utils import helper  # 祖父パッケージ


# ⚠️ 注意: 深すぎる相対インポート
from ....utils import helper  # 避けるべき
```

---

#### 2.2.3 循環インポート回避

```python
# ❌ 悪い例: 循環インポート
# module_a.py
from module_b import ClassB

class ClassA:
    def method(self):
        return ClassB()

# module_b.py
from module_a import ClassA  # 循環！

class ClassB:
    def method(self):
        return ClassA()


# ✅ 良い例: 型ヒント用の遅延インポート
# module_a.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from module_b import ClassB

class ClassA:
    def method(self) -> 'ClassB':  # 文字列による前方参照
        from module_b import ClassB  # 実行時インポート
        return ClassB()
```

---

### 2.3 式と文

#### 2.3.1 比較

```python
# ✅ 良い例: 明示的な比較
if value is None:
    pass

if len(items) == 0:
    pass

if result is True:  # ブール値の場合
    pass


# ❌ 悪い例: 暗黙的な比較
if not value:  # None以外もFalseになる
    pass

if not items:  # 空リストだけでなくNoneもFalse
    pass


# ✅ 良い例: 型チェック
if isinstance(value, int):
    pass


# ❌ 悪い例: 型チェック
if type(value) == int:  # isinstanceを使うべき
    pass
```

---

#### 2.3.2 条件式

```python
# ✅ 良い例: 三項演算子
result = 'positive' if value > 0 else 'negative'


# ⚠️ 複雑な条件式は避ける
result = (
    'very_positive' if value > 100 
    else 'positive' if value > 0 
    else 'negative' if value < 0 
    else 'zero'
)
# → if-elif-else文を使うべき


# ✅ 良い例: if-elif-else
if value > 100:
    result = 'very_positive'
elif value > 0:
    result = 'positive'
elif value < 0:
    result = 'negative'
else:
    result = 'zero'
```

---

#### 2.3.3 ループ

```python
# ✅ 良い例: enumerate使用
for index, item in enumerate(items):
    print(f"{index}: {item}")


# ❌ 悪い例: 手動インデックス
index = 0
for item in items:
    print(f"{index}: {item}")
    index += 1


# ✅ 良い例: zip使用
for name, age in zip(names, ages):
    print(f"{name} is {age} years old")


# ❌ 悪い例: インデックスアクセス
for i in range(len(names)):
    print(f"{names[i]} is {ages[i]} years old")


# ✅ 良い例: リスト内包表記
squares = [x**2 for x in range(10)]
evens = [x for x in range(10) if x % 2 == 0]


# ⚠️ 複雑な内包表記は避ける
result = [
    process(item)
    for sublist in nested_list
    for item in sublist
    if condition(item)
]
# → 通常のループの方が読みやすい
```

---

## 3. 命名規則

### 3.1 一般的な命名規則

| 対象 | 規則 | 例 |
|-----|------|---|
| **モジュール** | `lowercase_with_underscores` | `data_loader.py` |
| **パッケージ** | `lowercase` | `config`, `data` |
| **クラス** | `PascalCase` | `DataLoader`, `ModelRegistry` |
| **関数/メソッド** | `lowercase_with_underscores` | `load_data()`, `calculate_metrics()` |
| **変数** | `lowercase_with_underscores` | `input_data`, `num_samples` |
| **定数** | `UPPERCASE_WITH_UNDERSCORES` | `MAX_RETRIES`, `DEFAULT_BATCH_SIZE` |
| **型変数** | `PascalCase` | `T`, `ModelType`, `ConfigType` |
| **プライベート** | `_leading_underscore` | `_internal_method()`, `_cache` |

---

### 3.2 詳細な命名ガイドライン

#### 3.2.1 クラス名

```python
# ✅ 良い例: 名詞、明確な意味
class DataLoader:
    """データを読み込むクラス"""
    pass


class ModelRegistry:
    """モデルを登録・管理するクラス"""
    pass


class MetricCalculator:
    """評価指標を計算するクラス"""
    pass


# ❌ 悪い例: 動詞、不明確
class Load:  # 何をLoadするのか不明
    pass


class Manager:  # 何をManageするのか不明
    pass


class Data:  # 抽象的すぎる
    pass
```

---

#### 3.2.2 関数/メソッド名

```python
# ✅ 良い例: 動詞で始まる、明確な動作
def load_csv_file(file_path: Path) -> pd.DataFrame:
    """CSVファイルを読み込む"""
    pass


def calculate_mean_absolute_error(y_true, y_pred) -> float:
    """MAEを計算する"""
    pass


def validate_data_schema(df: pd.DataFrame) -> bool:
    """データスキーマを検証する"""
    pass


# ブール値を返す場合は is_, has_, can_ などを使用
def is_valid_schema(df: pd.DataFrame) -> bool:
    """スキーマが有効かチェック"""
    pass


def has_missing_values(df: pd.DataFrame) -> bool:
    """欠損値があるかチェック"""
    pass


# ❌ 悪い例: 不明確、名詞のみ
def data(file_path):  # 何をするのか不明
    pass


def process(df):  # 何を処理するのか不明
    pass


def get_data():  # どのデータを取得するのか不明
    pass
```

---

#### 3.2.3 変数名

```python
# ✅ 良い例: 明確で意味のある名前
input_data = pd.read_csv('data.csv')
num_samples = len(input_data)
training_start_time = datetime.now()
model_file_path = Path('/models/model.pkl')


# リスト/配列は複数形
user_ids = ['user1', 'user2', 'user3']
metric_values = [0.1, 0.2, 0.3]


# ブール値は is_, has_, can_ などを使用
is_valid = True
has_errors = False
can_proceed = True


# ❌ 悪い例: 不明確、短すぎる
d = pd.read_csv('data.csv')  # dは何の略？
n = len(d)  # nは何を表す？
t = datetime.now()  # tは何の時刻？


# ❌ 悪い例: ハンガリアン記法（型を名前に含める）
str_name = 'John'  # 型ヒントで十分
int_count = 10
list_items = [1, 2, 3]
```

---

#### 3.2.4 定数

```python
# ✅ 良い例: 大文字とアンダースコア
MAX_RETRIES = 3
DEFAULT_BATCH_SIZE = 32
API_BASE_URL = 'https://api.example.com'
TIMEOUT_SECONDS = 30


# 関連する定数はクラスにまとめる
class ModelConfig:
    """モデル設定の定数"""
    DEFAULT_INPUT_SIZE = 30
    DEFAULT_HORIZON = 7
    MAX_EPOCHS = 100
    LEARNING_RATE = 0.001


# ❌ 悪い例: マジックナンバー
def train_model(data):
    for epoch in range(100):  # 100の意味が不明
        batch_size = 32  # 32の意味が不明
        # ...


# ✅ 良い例: 定数使用
MAX_EPOCHS = 100
DEFAULT_BATCH_SIZE = 32

def train_model(data):
    for epoch in range(MAX_EPOCHS):
        batch_size = DEFAULT_BATCH_SIZE
        # ...
```

---

#### 3.2.5 プライベートメンバー

```python
class DataProcessor:
    """データ処理クラス"""
    
    def __init__(self):
        # ✅ パブリック属性
        self.data = None
        self.config = None
        
        # ✅ プライベート属性（外部からアクセスしない）
        self._cache = {}
        self._internal_state = None
        
        # ✅ 名前マングリング（継承時の衝突回避）
        self.__private_data = None
    
    def process(self):
        """パブリックメソッド"""
        self._validate()  # プライベートメソッド呼び出し
    
    def _validate(self):
        """プライベートメソッド（内部使用のみ）"""
        pass
    
    def __internal_process(self):
        """名前マングリング（クラス名がプレフィックスされる）"""
        pass
```

---

### 3.3 ドメイン固有の命名

#### 3.3.1 時系列データ

```python
# ✅ 良い例: ドメイン用語を使用
unique_id = 'series_001'  # 時系列の識別子
ds = pd.to_datetime('2025-01-01')  # DateStamp
y = 100.0  # 目的変数
forecast_horizon = 7  # 予測期間
historical_data = df[df['ds'] < cutoff_date]
future_data = df[df['ds'] >= cutoff_date]


# 外生変数の命名
futr_exog_temperature = 25.0  # 未来の外生変数
hist_exog_sales = 1000.0  # 過去の外生変数
stat_exog_category = 'A'  # 静的な外生変数
```

---

#### 3.3.2 モデル関連

```python
# ✅ 良い例: モデル用語を使用
model_type = 'AutoNHITS'
input_size = 30  # 入力ウィンドウサイズ
output_size = 7  # 出力サイズ（ホライズン）
learning_rate = 0.001
batch_size = 32
num_epochs = 100


# 評価指標
mae_score = 123.45  # Mean Absolute Error
rmse_score = 156.78  # Root Mean Squared Error
smape_score = 8.92  # Symmetric Mean Absolute Percentage Error


# データセット分割
train_data = df[:train_size]
validation_data = df[train_size:train_size+val_size]
test_data = df[train_size+val_size:]
```

---

## 4. コード構造

### 4.1 関数設計

#### 4.1.1 関数の長さ

```python
# ✅ 良い例: 短い関数（<50行）
def calculate_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    MAEを計算する
    
    Args:
        y_true: 真値
        y_pred: 予測値
        
    Returns:
        MAE値
    """
    return np.mean(np.abs(y_true - y_pred))


# ❌ 悪い例: 長すぎる関数（>50行）
def process_and_train_model(data_path, config):
    """100行以上の長い関数"""
    # データ読み込み（10行）
    # データクリーニング（20行）
    # 特徴量生成（15行）
    # モデル学習（30行）
    # 評価（15行）
    # 保存（10行）
    pass


# ✅ 良い例: 小さな関数に分割
def load_data(data_path: Path) -> pd.DataFrame:
    """データを読み込む"""
    pass

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """データをクリーニング"""
    pass

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """特徴量を生成"""
    pass

def train_model(df: pd.DataFrame, config: Config) -> Model:
    """モデルを学習"""
    pass
```

---

#### 4.1.2 関数の引数

```python
# ✅ 良い例: 引数は7個以内
def train_model(
    data: pd.DataFrame,
    model_type: str,
    input_size: int,
    horizon: int,
    learning_rate: float
) -> Model:
    """引数は適切な数"""
    pass


# ❌ 悪い例: 引数が多すぎる
def train_model(
    data, model_type, input_size, horizon, learning_rate,
    batch_size, num_epochs, optimizer, loss_fn, device,
    early_stopping, patience, checkpoint_path
):
    """引数が多すぎる"""
    pass


# ✅ 良い例: 設定オブジェクトでまとめる
@dataclass
class TrainingConfig:
    """学習設定"""
    model_type: str
    input_size: int
    horizon: int
    learning_rate: float
    batch_size: int
    num_epochs: int

def train_model(data: pd.DataFrame, config: TrainingConfig) -> Model:
    """設定をまとめて引数を減らす"""
    pass
```

---

#### 4.1.3 戻り値

```python
# ✅ 良い例: 明確な戻り値
def load_data(file_path: Path) -> pd.DataFrame:
    """DataFrameを返す"""
    return pd.read_csv(file_path)


# ✅ 良い例: 複数の戻り値は名前付きタプル
from typing import NamedTuple

class LoadResult(NamedTuple):
    """データ読み込み結果"""
    data: pd.DataFrame
    num_rows: int
    num_columns: int

def load_data(file_path: Path) -> LoadResult:
    """構造化された結果を返す"""
    df = pd.read_csv(file_path)
    return LoadResult(
        data=df,
        num_rows=len(df),
        num_columns=len(df.columns)
    )


# ❌ 悪い例: タプルで返す（何が何だか分からない）
def load_data(file_path: Path) -> Tuple[pd.DataFrame, int, int]:
    """タプルで返す（意味が不明確）"""
    df = pd.read_csv(file_path)
    return df, len(df), len(df.columns)
```

---

### 4.2 クラス設計

#### 4.2.1 クラスの責務

```python
# ✅ 良い例: 単一責任
class DataLoader:
    """データの読み込みのみを担当"""
    
    def load_csv(self, path: Path) -> pd.DataFrame:
        """CSV読み込み"""
        pass
    
    def load_parquet(self, path: Path) -> pd.DataFrame:
        """Parquet読み込み"""
        pass


class DataValidator:
    """データの検証のみを担当"""
    
    def validate_schema(self, df: pd.DataFrame) -> bool:
        """スキーマ検証"""
        pass
    
    def validate_values(self, df: pd.DataFrame) -> bool:
        """値の検証"""
        pass


# ❌ 悪い例: 責務が多すぎる
class DataManager:
    """データの読み込み、検証、変換、保存を全部やる"""
    
    def load(self, path):
        pass
    
    def validate(self, df):
        pass
    
    def transform(self, df):
        pass
    
    def save(self, df, path):
        pass
    
    def train_model(self, df):  # モデル学習まで！
        pass
```

---

#### 4.2.2 継承 vs コンポジション

```python
# ✅ 良い例: コンポジション優先
class DataPipeline:
    """データパイプライン（コンポジション）"""
    
    def __init__(
        self,
        loader: DataLoader,
        validator: DataValidator,
        transformer: DataTransformer
    ):
        self.loader = loader
        self.validator = validator
        self.transformer = transformer
    
    def process(self, path: Path) -> pd.DataFrame:
        """パイプライン実行"""
        data = self.loader.load_csv(path)
        if not self.validator.validate_schema(data):
            raise ValueError("Invalid schema")
        return self.transformer.transform(data)


# ⚠️ 継承は "is-a" 関係のみ
class AutoModel(BaseModel):
    """AutoModelはBaseModelの一種"""
    pass


# ❌ 悪い例: 不適切な継承
class DataPipeline(DataLoader, DataValidator, DataTransformer):
    """多重継承は複雑になりやすい"""
    pass
```

---

#### 4.2.3 プロパティとメソッド

```python
class Model:
    """モデルクラス"""
    
    def __init__(self, model_id: int):
        self._model_id = model_id
        self._trained = False
        self._metrics = {}
    
    # ✅ プロパティ: 計算不要な属性アクセス
    @property
    def model_id(self) -> int:
        """モデルID（読み取り専用）"""
        return self._model_id
    
    @property
    def is_trained(self) -> bool:
        """学習済みフラグ"""
        return self._trained
    
    @property
    def metrics(self) -> Dict[str, float]:
        """評価指標（読み取り専用）"""
        return self._metrics.copy()
    
    # ✅ メソッド: 計算が必要な操作
    def calculate_score(self) -> float:
        """スコアを計算（計算コストあり）"""
        # 重い計算
        return sum(self._metrics.values()) / len(self._metrics)
    
    def train(self, data: pd.DataFrame) -> None:
        """学習実行（状態を変更）"""
        # 学習処理
        self._trained = True


# ❌ 悪い例: プロパティで重い計算
class Model:
    @property
    def score(self) -> float:
        """プロパティで重い計算はNG"""
        # 1秒かかる計算
        return expensive_calculation()
    
    # メソッドにすべき
    def calculate_score(self) -> float:
        """メソッドにする"""
        return expensive_calculation()
```

---

### 4.3 モジュール構成

#### 4.3.1 ファイル構成

```python
"""
src/nf_auto_runner/data/data_loader.py

モジュールの構成順序:
1. モジュールdocstring
2. インポート
3. 定数
4. 例外クラス
5. クラス定義
6. 関数定義
7. if __name__ == '__main__'
"""

# 1. モジュールdocstring
"""
データローダーモジュール

CSVファイルの読み込みと正規化を提供する。
"""

# 2. インポート
from pathlib import Path
from typing import Optional
import pandas as pd

# 3. 定数
DEFAULT_ENCODING = 'utf-8'
REQUIRED_COLUMNS = {'unique_id', 'ds', 'y'}

# 4. 例外クラス
class DataLoadError(Exception):
    """データ読み込みエラー"""
    pass

# 5. クラス定義
class DataLoader:
    """データローダークラス"""
    pass

# 6. 関数定義
def validate_schema(df: pd.DataFrame) -> bool:
    """スキーマ検証"""
    pass

# 7. エントリーポイント
if __name__ == '__main__':
    # テストコードなど
    pass
```

---

## 5. ドキュメンテーション

### 5.1 Docstring

#### 5.1.1 Google Style Docstring

```python
def calculate_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    metrics: List[str],
    sample_weight: Optional[np.ndarray] = None
) -> Dict[str, float]:
    """
    評価指標を計算する
    
    真値と予測値から複数の評価指標を計算する。
    サポートされる指標: mae, rmse, smape, mase, mape
    
    Args:
        y_true: 真値の配列。shape=(n_samples,)
        y_pred: 予測値の配列。shape=(n_samples,)
        metrics: 計算する指標のリスト。例: ['mae', 'rmse']
        sample_weight: サンプルの重み。Noneの場合は等重み。
            shape=(n_samples,)
    
    Returns:
        指標名と値の辞書。
        例: {'mae': 0.1, 'rmse': 0.15}
    
    Raises:
        ValueError: 配列の形状が一致しない場合
        ValueError: サポートされていない指標が指定された場合
        
    Example:
        >>> y_true = np.array([1.0, 2.0, 3.0])
        >>> y_pred = np.array([1.1, 2.1, 2.9])
        >>> metrics = calculate_metrics(y_true, y_pred, ['mae', 'rmse'])
        >>> print(metrics)
        {'mae': 0.1, 'rmse': 0.1}
        
    Note:
        大量のデータに対してはメモリ使用量に注意してください。
        10M以上のサンプルの場合、チャンク処理を検討してください。
        
    See Also:
        sklearn.metrics: scikit-learnの評価指標
        
    References:
        [1] Hyndman, R. J., & Koehler, A. B. (2006). Another look at
            measures of forecast accuracy. International journal of
            forecasting, 22(4), 679-688.
    """
    if y_true.shape != y_pred.shape:
        raise ValueError(
            f"Shape mismatch: y_true {y_true.shape} vs y_pred {y_pred.shape}"
        )
    
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

#### 5.1.2 クラスのdocstring

```python
class DataLoader:
    """
    データローダークラス
    
    CSVファイルを読み込み、時系列データの標準スキーマに変換する。
    
    このクラスは以下の機能を提供します:
    - CSVファイルの読み込み
    - スキーマの検証
    - 日付カラムの型変換
    - データのソート
    
    Attributes:
        path_config: パス設定オブジェクト
        encoding: デフォルトの文字エンコーディング
        cache: 読み込んだデータのキャッシュ
        
    Example:
        >>> path_config = PathConfig.from_env()
        >>> loader = DataLoader(path_config)
        >>> result = loader.load_csv('sales_data.csv')
        >>> print(f"Loaded {result.num_rows} rows")
        Loaded 10000 rows
        
    Note:
        大きなファイル（>1GB）を読み込む場合は、
        load_csv_chunked() メソッドを使用してください。
        
    Warnings:
        このクラスはスレッドセーフではありません。
        並行アクセスが必要な場合は、インスタンスを分けてください。
    """
    
    def __init__(
        self,
        path_config: PathConfig,
        encoding: str = 'utf-8'
    ):
        """
        初期化
        
        Args:
            path_config: パス設定オブジェクト
            encoding: デフォルトの文字エンコーディング
        """
        self.path_config = path_config
        self.encoding = encoding
        self.cache = {}
```

---

#### 5.1.3 モジュールのdocstring

```python
"""
データローダーモジュール

このモジュールは時系列データの読み込みと正規化機能を提供します。

Classes:
    DataLoader: データ読み込みクラス
    DataLoadResult: 読み込み結果を保持するデータクラス
    
Functions:
    validate_schema: スキーマ検証関数
    infer_frequency: 周期性推定関数
    
Exceptions:
    DataLoadError: データ読み込みエラー
    SchemaValidationError: スキーマ検証エラー

Example:
    >>> from nf_auto_runner.data import DataLoader
    >>> loader = DataLoader(path_config)
    >>> result = loader.load_csv('data.csv')

Author:
    Data Team <data-team@example.com>

Version:
    1.0.0

License:
    MIT License

See Also:
    - pandas.read_csv: CSV読み込みの詳細
    - data_preprocessor: データ前処理モジュール
"""

from pathlib import Path
from typing import List, Optional
import pandas as pd
```

---

### 5.2 コメント

#### 5.2.1 インラインコメント

```python
# ✅ 良い例: 複雑なロジックの説明
def calculate_smape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """sMAPEを計算"""
    # 分母がゼロになるのを防ぐため、小さな値を追加
    epsilon = 1e-10
    denominator = (np.abs(y_true) + np.abs(y_pred)) / 2 + epsilon
    
    # sMAPEの計算: 2 * |y_true - y_pred| / (|y_true| + |y_pred|)
    return np.mean(2 * np.abs(y_true - y_pred) / denominator) * 100


# ❌ 悪い例: 自明なコメント
def add(a: int, b: int) -> int:
    """加算"""
    # aとbを足す
    return a + b  # 結果を返す


# ✅ 良い例: TODOコメント
def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """データ処理"""
    # TODO(username): 外れ値検出アルゴリズムを改善 (Issue #123)
    # FIXME(username): メモリリークの可能性 (Bug #456)
    # HACK(username): 一時的な回避策。将来的に修正が必要
    # NOTE(username): この処理は時間がかかる（約10秒）
    pass
```

---

#### 5.2.2 ブロックコメント

```python
# ✅ 良い例: アルゴリズムの説明
def detect_outliers(data: np.ndarray, threshold: float = 3.0) -> np.ndarray:
    """
    外れ値を検出する
    
    修正Z-scoreを使用した外れ値検出アルゴリズム:
    1. 中央値を計算
    2. MAD (Median Absolute Deviation) を計算
    3. 修正Z-score = 0.6745 * (x - median) / MAD
    4. |修正Z-score| > threshold なら外れ値
    
    この手法は通常のZ-scoreよりもロバストである。
    """
    median = np.median(data)
    mad = np.median(np.abs(data - median))
    
    # MADがゼロの場合の処理
    if mad == 0:
        return np.zeros(len(data), dtype=bool)
    
    # 修正Z-scoreの計算
    modified_z_scores = 0.6745 * (data - median) / mad
    
    # 閾値を超えるものを外れ値とする
    return np.abs(modified_z_scores) > threshold
```

---

### 5.3 README とドキュメント

#### 5.3.1 README.md 構成

```markdown
# Project Name

Short description of the project

## Features

- Feature 1
- Feature 2

## Installation

```bash
pip install package-name
```

## Quick Start

```python
from package import Class
obj = Class()
obj.method()
```

## Documentation

Full documentation: https://docs.example.com

## Contributing

See CONTRIBUTING.md

## License

MIT License
```

---

## 6. 型ヒント

### 6.1 基本的な型ヒント

```python
from typing import List, Dict, Set, Tuple, Optional, Union, Any

# ✅ 基本型
def process_number(value: int) -> float:
    """整数を受け取り浮動小数点を返す"""
    return float(value)


# ✅ コレクション型
def process_list(items: List[str]) -> Dict[str, int]:
    """文字列リストを受け取り辞書を返す"""
    return {item: len(item) for item in items}


# ✅ Optional (None許容)
def find_user(user_id: int) -> Optional[User]:
    """ユーザーを検索（見つからない場合None）"""
    pass


# ✅ Union (複数型許容)
def process_input(value: Union[int, str]) -> str:
    """整数または文字列を受け取る"""
    return str(value)


# ✅ Any (型制約なし、なるべく避ける)
def process_any(value: Any) -> Any:
    """任意の型（最終手段）"""
    pass
```

---

### 6.2 高度な型ヒント

#### 6.2.1 TypeVar とジェネリクス

```python
from typing import TypeVar, Generic, List

T = TypeVar('T')

class Container(Generic[T]):
    """ジェネリックコンテナ"""
    
    def __init__(self) -> None:
        self.items: List[T] = []
    
    def add(self, item: T) -> None:
        """アイテムを追加"""
        self.items.append(item)
    
    def get(self, index: int) -> T:
        """アイテムを取得"""
        return self.items[index]


# 使用例
int_container: Container[int] = Container()
int_container.add(10)
value: int = int_container.get(0)

str_container: Container[str] = Container()
str_container.add("hello")
```

---

#### 6.2.2 Protocol (構造的部分型)

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Saveable(Protocol):
    """保存可能なオブジェクトのプロトコル"""
    
    def save(self, path: Path) -> None:
        """保存メソッド"""
        ...


class Model:
    """モデルクラス（Saveableプロトコルを実装）"""
    
    def save(self, path: Path) -> None:
        """モデルを保存"""
        pass


def save_object(obj: Saveable, path: Path) -> None:
    """Saveableなオブジェクトを保存"""
    obj.save(path)


# 使用例
model = Model()
save_object(model, Path('model.pkl'))  # OK
```

---

#### 6.2.3 Literal

```python
from typing import Literal

def set_log_level(
    level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR']
) -> None:
    """ログレベルを設定"""
    pass


# 使用例
set_log_level('INFO')  # OK
set_log_level('TRACE')  # 型エラー
```

---

#### 6.2.4 型エイリアス

```python
from typing import List, Dict, Union
from pathlib import Path

# ✅ 複雑な型をエイリアスで簡潔に
UserId = int
UserName = str
UserData = Dict[str, Union[str, int, float]]
PathLike = Union[str, Path]

def get_user(user_id: UserId) -> UserData:
    """ユーザー情報を取得"""
    pass

def load_file(path: PathLike) -> str:
    """ファイルを読み込む"""
    if isinstance(path, str):
        path = Path(path)
    return path.read_text()
```

---

### 6.3 型チェック設定

#### 6.3.1 mypy.ini

```ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_any_unimported = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
check_untyped_defs = True
strict_equality = True

[mypy-tests.*]
disallow_untyped_defs = False

[mypy-pandas]
ignore_missing_imports = True

[mypy-numpy]
ignore_missing_imports = True
```

---

## 7. エラーハンドリング

### 7.1 例外の使用

#### 7.1.1 カスタム例外

```python
# ✅ 良い例: カスタム例外定義
class DataError(Exception):
    """データ関連のエラー基底クラス"""
    pass


class DataValidationError(DataError):
    """データ検証エラー"""
    
    def __init__(self, message: str, errors: List[str]):
        super().__init__(message)
        self.errors = errors


class DataLoadError(DataError):
    """データ読み込みエラー"""
    pass


class ModelError(Exception):
    """モデル関連のエラー基底クラス"""
    pass


class ModelNotFoundError(ModelError):
    """モデル未発見エラー"""
    pass


class ModelTrainingError(ModelError):
    """モデル学習エラー"""
    pass
```

---

#### 7.1.2 例外の送出

```python
# ✅ 良い例: 適切な例外送出
def validate_data(df: pd.DataFrame) -> None:
    """
    データを検証する
    
    Raises:
        DataValidationError: データが不正な場合
    """
    errors = []
    
    if df.empty:
        errors.append("DataFrame is empty")
    
    if 'unique_id' not in df.columns:
        errors.append("Missing 'unique_id' column")
    
    if 'ds' not in df.columns:
        errors.append("Missing 'ds' column")
    
    if errors:
        raise DataValidationError(
            "Data validation failed",
            errors=errors
        )


# ✅ 良い例: 詳細なエラーメッセージ
def load_model(model_id: int) -> Model:
    """
    モデルを読み込む
    
    Raises:
        ModelNotFoundError: モデルが見つからない場合
    """
    if not model_exists(model_id):
        raise ModelNotFoundError(
            f"Model not found: id={model_id}. "
            f"Available models: {list_available_models()}"
        )
    
    return load_model_from_storage(model_id)
```

---

#### 7.1.3 例外のキャッチ

```python
# ✅ 良い例: 具体的な例外をキャッチ
def safe_load_model(model_id: int) -> Optional[Model]:
    """
    モデルを安全に読み込む
    
    Returns:
        モデルオブジェクト、失敗時はNone
    """
    try:
        return load_model(model_id)
    except ModelNotFoundError as e:
        logger.warning(f"Model not found: {e}")
        return None
    except ModelError as e:
        logger.error(f"Model error: {e}")
        raise  # 再送出


# ❌ 悪い例: すべての例外をキャッチ
def bad_load_model(model_id: int) -> Optional[Model]:
    """すべての例外をキャッチ（良くない）"""
    try:
        return load_model(model_id)
    except Exception:  # 広すぎる
        return None


# ✅ 良い例: 複数の例外を個別に処理
def process_file(file_path: Path) -> pd.DataFrame:
    """ファイルを処理"""
    try:
        df = pd.read_csv(file_path)
        validate_schema(df)
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except pd.errors.ParserError as e:
        logger.error(f"CSV parse error: {e}")
        raise DataLoadError(f"Invalid CSV format: {file_path}") from e
    except DataValidationError as e:
        logger.error(f"Validation error: {e.errors}")
        raise
```

---

### 7.2 コンテキストマネージャー

```python
from contextlib import contextmanager
from typing import Generator

# ✅ 良い例: リソース管理
@contextmanager
def open_database() -> Generator[Connection, None, None]:
    """データベース接続のコンテキストマネージャー"""
    conn = create_connection()
    try:
        yield conn
    finally:
        conn.close()


# 使用例
with open_database() as conn:
    result = conn.execute("SELECT * FROM users")


# ✅ 良い例: エラー処理付き
@contextmanager
def temporary_directory() -> Generator[Path, None, None]:
    """一時ディレクトリのコンテキストマネージャー"""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        yield temp_dir
    except Exception as e:
        logger.error(f"Error in temporary directory: {e}")
        raise
    finally:
        shutil.rmtree(temp_dir)


# 使用例
with temporary_directory() as temp_dir:
    # 一時ディレクトリを使用
    pass
# 自動的にクリーンアップされる
```

---

## 8. テストコード規約

### 8.1 テストの構造

```python
"""
tests/unit/data/test_data_loader.py

テストファイルの構成:
1. インポート
2. フィクスチャ
3. テストクラス
   - 正常系テスト
   - 異常系テスト
   - エッジケーステスト
"""

import pytest
import pandas as pd
from pathlib import Path

from nf_auto_runner.data.data_loader import DataLoader


# フィクスチャ
@pytest.fixture
def sample_csv(tmp_path):
    """サンプルCSVファイル"""
    csv_path = tmp_path / 'sample.csv'
    df = pd.DataFrame({
        'unique_id': ['A', 'A'],
        'ds': ['2025-01-01', '2025-01-02'],
        'y': [100, 110]
    })
    df.to_csv(csv_path, index=False)
    return csv_path


class TestDataLoader:
    """DataLoaderのテストクラス"""
    
    # 正常系テスト
    def test_load_csv_success(self, sample_csv):
        """正常系: CSV読み込み成功"""
        loader = DataLoader()
        result = loader.load_csv(sample_csv)
        
        assert result is not None
        assert isinstance(result.data, pd.DataFrame)
        assert result.num_rows == 2
        assert len(result.unique_ids) == 1
    
    # 異常系テスト
    def test_load_csv_file_not_found(self):
        """異常系: ファイルが存在しない"""
        loader = DataLoader()
        
        with pytest.raises(FileNotFoundError):
            loader.load_csv('nonexistent.csv')
    
    def test_load_csv_invalid_schema(self, tmp_path):
        """異常系: スキーマが不正"""
        # 必須カラムが欠けているCSVを作成
        invalid_csv = tmp_path / 'invalid.csv'
        df = pd.DataFrame({'col1': [1, 2]})
        df.to_csv(invalid_csv, index=False)
        
        loader = DataLoader()
        with pytest.raises(ValueError, match="Missing required columns"):
            loader.load_csv(invalid_csv)
    
    # エッジケーステスト
    def test_load_csv_empty_file(self, tmp_path):
        """エッジケース: 空ファイル"""
        empty_csv = tmp_path / 'empty.csv'
        empty_csv.write_text('unique_id,ds,y\n')
        
        loader = DataLoader()
        result = loader.load_csv(empty_csv)
        
        assert result.num_rows == 0
    
    def test_load_csv_large_file(self, tmp_path):
        """エッジケース: 大きなファイル"""
        large_csv = tmp_path / 'large.csv'
        df = pd.DataFrame({
            'unique_id': ['A'] * 10000,
            'ds': pd.date_range('2020-01-01', periods=10000),
            'y': range(10000)
        })
        df.to_csv(large_csv, index=False)
        
        loader = DataLoader()
        result = loader.load_csv(large_csv)
        
        assert result.num_rows == 10000
```

---

### 8.2 テスト命名

```python
# ✅ 良い例: 明確なテスト名
def test_calculate_mae_with_valid_inputs():
    """正常系: 有効な入力でMAE計算"""
    pass

def test_calculate_mae_raises_error_on_shape_mismatch():
    """異常系: 形状不一致でエラー"""
    pass

def test_calculate_mae_with_zero_values():
    """エッジケース: ゼロ値"""
    pass


# ❌ 悪い例: 不明確なテスト名
def test_mae():
    """何をテストするのか不明"""
    pass

def test_1():
    """テスト番号だけでは意味不明"""
    pass
```

---

### 8.3 アサーション

```python
# ✅ 良い例: 明確なアサーション
def test_data_loading():
    """データ読み込みテスト"""
    result = load_data('test.csv')
    
    # 存在確認
    assert result is not None, "Result should not be None"
    
    # 型確認
    assert isinstance(result, pd.DataFrame), "Result should be DataFrame"
    
    # 値確認
    assert len(result) == 100, f"Expected 100 rows, got {len(result)}"
    assert 'unique_id' in result.columns, "Missing 'unique_id' column"
    
    # 近似比較
    assert result['y'].mean() == pytest.approx(50.0, rel=0.1), \
        "Mean should be approximately 50.0"


# ❌ 悪い例: メッセージなし
def test_data_loading():
    """データ読み込みテスト"""
    result = load_data('test.csv')
    assert result is not None  # なぜ失敗したか分からない
    assert len(result) == 100  # 期待値が不明確
```

---

## 9. パフォーマンス

### 9.1 効率的なコード

#### 9.1.1 リスト内包表記

```python
# ✅ 良い例: リスト内包表記（高速）
squares = [x**2 for x in range(1000)]

# ❌ 悪い例: ループ（遅い）
squares = []
for x in range(1000):
    squares.append(x**2)


# ✅ 良い例: ジェネレータ式（メモリ効率的）
sum_of_squares = sum(x**2 for x in range(1000000))

# ❌ 悪い例: リスト作成（メモリ浪費）
sum_of_squares = sum([x**2 for x in range(1000000)])
```

---

#### 9.1.2 文字列連結

```python
# ✅ 良い例: join使用（高速）
items = ['apple', 'banana', 'cherry']
result = ', '.join(items)

# ❌ 悪い例: ループで連結（遅い）
result = ''
for item in items:
    result += item + ', '
result = result.rstrip(', ')


# ✅ 良い例: f-string（読みやすく高速）
name = 'Alice'
age = 30
message = f"{name} is {age} years old"

# ❌ 悪い例: %演算子（古い）
message = "%s is %d years old" % (name, age)
```

---

#### 9.1.3 NumPy/Pandas最適化

```python
import numpy as np
import pandas as pd

# ✅ 良い例: ベクトル演算（高速）
arr = np.arange(1000000)
result = arr ** 2

# ❌ 悪い例: ループ（遅い）
result = np.array([x**2 for x in arr])


# ✅ 良い例: Pandas組み込み関数
df['new_col'] = df['col1'] + df['col2']

# ❌ 悪い例: apply（遅い）
df['new_col'] = df.apply(lambda row: row['col1'] + row['col2'], axis=1)


# ✅ 良い例: 条件フィルタリング
filtered = df[df['value'] > 100]

# ❌ 悪い例: iterrows（遅い）
filtered = pd.DataFrame([row for idx, row in df.iterrows() if row['value'] > 100])
```

---

### 9.2 メモリ管理

```python
# ✅ 良い例: ジェネレータ使用
def read_large_file(file_path: Path) -> Generator[str, None, None]:
    """大きなファイルを行ごとに読む"""
    with open(file_path) as f:
        for line in f:
            yield line.strip()


# ❌ 悪い例: 全体を読み込み
def read_large_file(file_path: Path) -> List[str]:
    """メモリを大量消費"""
    with open(file_path) as f:
        return [line.strip() for line in f]


# ✅ 良い例: チャンク読み込み
def process_large_csv(file_path: Path) -> None:
    """大きなCSVをチャンクで処理"""
    chunk_size = 10000
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        process_chunk(chunk)


# ✅ 良い例: 不要なオブジェクトの削除
def process_data():
    """処理後に不要なデータを削除"""
    large_data = load_large_data()
    result = process(large_data)
    del large_data  # 明示的に削除
    import gc
    gc.collect()  # ガベージコレクション実行
    return result
```

---

## 10. セキュリティ

### 10.1 入力検証

```python
# ✅ 良い例: 入力検証
def get_user(user_id: int) -> User:
    """ユーザーを取得"""
    # 入力検証
    if not isinstance(user_id, int):
        raise TypeError("user_id must be integer")
    if user_id < 0:
        raise ValueError("user_id must be non-negative")
    
    # SQLインジェクション対策: パラメータ化クエリ
    query = "SELECT * FROM users WHERE id = ?"
    return db.execute(query, (user_id,))


# ❌ 悪い例: SQLインジェクションの危険性
def get_user(user_id: str) -> User:
    """危険: SQLインジェクション可能"""
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)


# ✅ 良い例: パスの検証
def read_file(file_path: str) -> str:
    """ファイルを読み込む"""
    # パストラバーサル対策
    base_dir = Path('/safe/directory')
    full_path = (base_dir / file_path).resolve()
    
    # ベースディレクトリ外へのアクセスを防ぐ
    if not str(full_path).startswith(str(base_dir)):
        raise ValueError("Invalid file path")
    
    return full_path.read_text()
```

---

### 10.2 機密情報の扱い

```python
import os
from pathlib import Path

# ✅ 良い例: 環境変数で管理
API_KEY = os.getenv('API_KEY')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')


# ❌ 悪い例: ハードコード
API_KEY = 'sk_test_abc123'  # 絶対にやってはいけない
DATABASE_PASSWORD = 'password123'  # 絶対にやってはいけない


# ✅ 良い例: ログに機密情報を出力しない
def process_payment(card_number: str, amount: float):
    """支払い処理"""
    logger.info(f"Processing payment: amount={amount}")  # カード番号は出力しない
    # 処理
    masked_card = f"****-****-****-{card_number[-4:]}"
    logger.info(f"Payment completed: card={masked_card}")


# ❌ 悪い例: ログに機密情報
def process_payment(card_number: str, amount: float):
    """危険: カード番号がログに残る"""
    logger.info(f"Processing payment: card={card_number}, amount={amount}")
```

---

## 11. データベース規約

### 11.1 SQLAlchemy

```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# ✅ 良い例: モデル定義
class User(Base):
    """ユーザーモデル"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False)
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"


# ✅ 良い例: クエリ
def get_active_users(session) -> List[User]:
    """アクティブユーザーを取得"""
    return session.query(User).filter(
        User.is_active == True
    ).all()


# ✅ 良い例: トランザクション
def create_user(session, username: str, email: str) -> User:
    """ユーザーを作成"""
    try:
        user = User(username=username, email=email)
        session.add(user)
        session.commit()
        return user
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create user: {e}")
        raise
```

---

## 12. API設計規約

### 12.1 FastAPI

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List

app = FastAPI()

# ✅ 良い例: Pydanticモデル
class UserCreate(BaseModel):
    """ユーザー作成リクエスト"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    age: int = Field(..., ge=0, le=150)


class UserResponse(BaseModel):
    """ユーザーレスポンス"""
    id: int
    username: str
    email: str
    
    class Config:
        from_attributes = True


# ✅ 良い例: エンドポイント定義
@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate) -> UserResponse:
    """
    ユーザーを作成
    
    - **username**: ユーザー名（3-50文字）
    - **email**: メールアドレス
    - **age**: 年齢（0-150）
    """
    # ビジネスロジック
    created_user = user_service.create(user)
    return UserResponse.from_orm(created_user)


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int) -> UserResponse:
    """ユーザーを取得"""
    user = user_service.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(user)
```

---

## 13. 付録

### 13.1 チェックリスト

#### コードレビューチェックリスト

- [ ] PEP 8準拠
- [ ] 型ヒント完備
- [ ] Docstring完備
- [ ] テスト追加
- [ ] エラーハンドリング適切
- [ ] セキュリティ考慮
- [ ] パフォーマンス考慮
- [ ] ログ適切
- [ ] マジックナンバー定数化
- [ ] 重複コードなし

---

### 13.2 ツール設定まとめ

**`.pre-commit-config.yaml`**:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        args: ['--line-length=100']
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ['--profile=black']
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: ['--max-line-length=100']
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        args: ['--strict']
```

---

### 13.3 参考資料

- [PEP 8 -- Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [PEP 257 -- Docstring Conventions](https://peps.python.org/pep-0257/)
- [PEP 484 -- Type Hints](https://peps.python.org/pep-0484/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [The Hitchhiker's Guide to Python](https://docs.python-guide.org/)

---

**End of Document**
