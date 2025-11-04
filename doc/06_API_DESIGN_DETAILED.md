# 詳細API設計書
**Detailed API Design for Time Series Forecasting System**

---

## 📋 ドキュメント情報

| 項目 | 内容 |
|-----|------|
| **ドキュメントタイトル** | 時系列予測システム 詳細API設計書 |
| **バージョン** | v1.0.0 |
| **作成日** | 2025-11-03 |
| **最終更新日** | 2025-11-03 |
| **対象システム** | NeuralForecast Auto Runner + Time Series Forecasting System |
| **APIフレームワーク** | FastAPI 0.104+ |
| **OpenAPI仕様** | 3.1.0 |
| **ベースURL** | `https://api.example.com/v1` |

---

## 目次

1. [API概要](#1-api概要)
2. [認証・認可](#2-認証認可)
3. [共通仕様](#3-共通仕様)
4. [エンドポイント詳細](#4-エンドポイント詳細)
   - [4.1 実験管理](#41-実験管理experiments)
   - [4.2 実行管理](#42-実行管理runs)
   - [4.3 モデル管理](#43-モデル管理models)
   - [4.4 データセット管理](#44-データセット管理datasets)
   - [4.5 評価指標](#45-評価指標metrics)
   - [4.6 予測](#46-予測predictions)
   - [4.7 ハイパーパラメータ](#47-ハイパーパラメータhyperparameters)
   - [4.8 アーティファクト](#48-アーティファクトartifacts)
   - [4.9 ユーザー管理](#49-ユーザー管理users)
   - [4.10 システム管理](#410-システム管理system)
5. [エラーハンドリング](#5-エラーハンドリング)
6. [レート制限](#6-レート制限)
7. [セキュリティ](#7-セキュリティ)
8. [ベストプラクティス](#8-ベストプラクティス)
9. [付録](#9-付録)

---

## 1. API概要

### 1.1 APIの特徴

| 特徴 | 説明 |
|-----|------|
| **RESTful** | REST原則に準拠した設計 |
| **OpenAPI 3.1** | Swagger/OpenAPI仕様準拠 |
| **JSON** | リクエスト/レスポンスはJSON形式 |
| **バージョニング** | URLパスでバージョン管理 (/v1, /v2) |
| **ページネーション** | 大量データはページング対応 |
| **フィルタリング** | クエリパラメータで柔軟なフィルタ |
| **ソート** | 複数カラムでのソート対応 |
| **部分レスポンス** | 必要なフィールドのみ取得可能 |

---

### 1.2 HTTPメソッド

| メソッド | 用途 | 冪等性 | 安全性 |
|---------|------|--------|--------|
| **GET** | リソースの取得 | ✅ | ✅ |
| **POST** | リソースの作成 | ❌ | ❌ |
| **PUT** | リソースの完全更新 | ✅ | ❌ |
| **PATCH** | リソースの部分更新 | ❌ | ❌ |
| **DELETE** | リソースの削除 | ✅ | ❌ |
| **HEAD** | メタデータの取得 | ✅ | ✅ |
| **OPTIONS** | 許可メソッドの取得 | ✅ | ✅ |

---

### 1.3 ステータスコード

| コード | 説明 | 用途 |
|-------|------|------|
| **200** | OK | 成功（GET, PUT, PATCH, DELETE） |
| **201** | Created | リソース作成成功（POST） |
| **202** | Accepted | 非同期処理受付 |
| **204** | No Content | 成功（レスポンスボディなし） |
| **400** | Bad Request | リクエストエラー |
| **401** | Unauthorized | 認証エラー |
| **403** | Forbidden | 認可エラー |
| **404** | Not Found | リソース未発見 |
| **409** | Conflict | リソース競合 |
| **422** | Unprocessable Entity | バリデーションエラー |
| **429** | Too Many Requests | レート制限超過 |
| **500** | Internal Server Error | サーバーエラー |
| **503** | Service Unavailable | サービス停止中 |

---

## 2. 認証・認可

### 2.1 認証方式

#### 2.1.1 JWT (JSON Web Token)

**推奨方式**: Bearer Token認証

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**トークン取得**:

```bash
POST /v1/auth/token
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "secure_password"
}
```

**レスポンス**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "scope": "read write admin"
}
```

---

#### 2.1.2 APIキー認証

**開発・テスト用途**:

```http
X-API-Key: your_api_key_here
```

**APIキー発行**:

```bash
POST /v1/auth/api-keys
Authorization: Bearer <jwt_token>

{
  "name": "Production API Key",
  "expires_at": "2026-01-01T00:00:00Z",
  "scopes": ["read", "write"]
}
```

---

### 2.2 認可（Authorization）

#### 2.2.1 ロールベースアクセス制御（RBAC）

| ロール | 権限 | 説明 |
|-------|------|------|
| **Admin** | すべての操作 | システム管理者 |
| **Data Scientist** | 読み取り、実験作成、モデル学習 | データサイエンティスト |
| **Analyst** | 読み取り、予測実行 | アナリスト |
| **Viewer** | 読み取りのみ | 閲覧者 |

---

#### 2.2.2 スコープ

| スコープ | 説明 | 対象リソース |
|---------|------|-------------|
| **experiments:read** | 実験の読み取り | GET /experiments |
| **experiments:write** | 実験の作成・更新 | POST, PUT, PATCH /experiments |
| **experiments:delete** | 実験の削除 | DELETE /experiments |
| **models:read** | モデルの読み取り | GET /models |
| **models:write** | モデルの作成・更新 | POST, PUT, PATCH /models |
| **models:deploy** | モデルのデプロイ | POST /models/{id}/deploy |
| **predictions:read** | 予測結果の読み取り | GET /predictions |
| **predictions:create** | 予測の実行 | POST /predictions |
| **admin:all** | 全権限 | すべて |

---

### 2.3 OAuth 2.0フロー

#### 2.3.1 認可コードフロー

```mermaid
sequenceDiagram
    participant User
    participant Client
    participant AuthServer
    participant API
    
    User->>Client: ログイン要求
    Client->>AuthServer: 認可リクエスト
    AuthServer->>User: ログインページ表示
    User->>AuthServer: 認証情報入力
    AuthServer->>Client: 認可コード発行
    Client->>AuthServer: トークンリクエスト<br/>(認可コード)
    AuthServer->>Client: アクセストークン発行
    Client->>API: APIリクエスト<br/>(アクセストークン)
    API->>Client: レスポンス
```

---

## 3. 共通仕様

### 3.1 リクエストヘッダー

| ヘッダー | 必須 | 説明 | 例 |
|---------|------|------|---|
| **Authorization** | ✅ | 認証トークン | `Bearer eyJ...` |
| **Content-Type** | ✅ | コンテンツタイプ | `application/json` |
| **Accept** | ❌ | 受け入れ形式 | `application/json` |
| **X-Request-ID** | ❌ | リクエストID（トレーシング） | `uuid` |
| **X-API-Version** | ❌ | APIバージョン | `v1` |
| **User-Agent** | ❌ | クライアント情報 | `MyApp/1.0` |

---

### 3.2 レスポンスヘッダー

| ヘッダー | 説明 | 例 |
|---------|------|---|
| **Content-Type** | コンテンツタイプ | `application/json; charset=utf-8` |
| **X-Request-ID** | リクエストID | `uuid` |
| **X-RateLimit-Limit** | レート制限上限 | `1000` |
| **X-RateLimit-Remaining** | 残りリクエスト数 | `950` |
| **X-RateLimit-Reset** | リセット時刻（UNIX時間） | `1699000000` |
| **ETag** | リソースバージョン | `"33a64df551425fcc55e4d42a148795d9f25f89d4"` |
| **Last-Modified** | 最終更新日時 | `Wed, 21 Oct 2015 07:28:00 GMT` |

---

### 3.3 ページネーション

#### 3.3.1 クエリパラメータ

```http
GET /v1/experiments?page=2&per_page=50&sort=-created_at
```

| パラメータ | デフォルト | 説明 |
|-----------|----------|------|
| **page** | 1 | ページ番号 |
| **per_page** | 20 | 1ページあたりの件数 |
| **sort** | `id` | ソートキー（`-`で降順） |

---

#### 3.3.2 レスポンス形式

```json
{
  "data": [
    { "id": 1, "name": "Experiment 1" },
    { "id": 2, "name": "Experiment 2" }
  ],
  "pagination": {
    "page": 2,
    "per_page": 50,
    "total": 235,
    "total_pages": 5,
    "has_next": true,
    "has_prev": true,
    "next_page": 3,
    "prev_page": 1
  },
  "links": {
    "self": "/v1/experiments?page=2&per_page=50",
    "first": "/v1/experiments?page=1&per_page=50",
    "last": "/v1/experiments?page=5&per_page=50",
    "next": "/v1/experiments?page=3&per_page=50",
    "prev": "/v1/experiments?page=1&per_page=50"
  }
}
```

---

### 3.4 フィルタリング

#### 3.4.1 基本フィルタ

```http
GET /v1/experiments?status=active&created_by=user123
```

---

#### 3.4.2 高度なフィルタ

```http
GET /v1/models?model_type=AutoNHITS&created_at[gte]=2025-01-01&created_at[lte]=2025-12-31
```

**演算子**:

| 演算子 | 説明 | 例 |
|-------|------|---|
| `eq` | 等しい | `status[eq]=active` |
| `ne` | 等しくない | `status[ne]=deleted` |
| `gt` | より大きい | `value[gt]=100` |
| `gte` | 以上 | `created_at[gte]=2025-01-01` |
| `lt` | より小さい | `value[lt]=1000` |
| `lte` | 以下 | `created_at[lte]=2025-12-31` |
| `in` | 含まれる | `status[in]=active,running` |
| `like` | 部分一致 | `name[like]=experiment%` |

---

### 3.5 フィールド選択

```http
GET /v1/experiments/123?fields=id,name,status,created_at
```

**レスポンス**:

```json
{
  "id": 123,
  "name": "My Experiment",
  "status": "active",
  "created_at": "2025-11-03T10:00:00Z"
}
```

---

### 3.6 標準エラーレスポンス

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "experiment_name",
        "message": "Field is required",
        "code": "required"
      }
    ],
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-11-03T10:30:00Z",
    "path": "/v1/experiments",
    "method": "POST"
  }
}
```

---

## 4. エンドポイント詳細

### 4.1 実験管理（Experiments）

#### 4.1.1 実験一覧取得

```http
GET /v1/experiments
```

**認証**: 必須（`experiments:read`）

**クエリパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
|-----------|---|------|------|
| `page` | integer | ❌ | ページ番号（デフォルト: 1） |
| `per_page` | integer | ❌ | 1ページあたり件数（デフォルト: 20, 最大: 100） |
| `sort` | string | ❌ | ソートキー（デフォルト: `-created_at`） |
| `status` | string | ❌ | ステータスフィルタ（`active`, `archived`, `deleted`） |
| `created_by` | string | ❌ | 作成者フィルタ |
| `search` | string | ❌ | 名前・説明の全文検索 |

**レスポンス** (200 OK):

```json
{
  "data": [
    {
      "experiment_id": 123,
      "experiment_name": "Sales Forecast Q4",
      "experiment_description": "Forecasting sales for Q4 2025",
      "experiment_type": "training",
      "status": "active",
      "lifecycle_stage": "active",
      "created_by": "user@example.com",
      "created_at": "2025-11-01T10:00:00Z",
      "updated_at": "2025-11-03T15:30:00Z",
      "tags": {
        "department": "sales",
        "priority": "high"
      },
      "metadata": {
        "total_runs": 15,
        "completed_runs": 12,
        "failed_runs": 3
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

**エラー**:
- `401`: 認証エラー
- `403`: 権限なし
- `500`: サーバーエラー

---

#### 4.1.2 実験作成

```http
POST /v1/experiments
```

**認証**: 必須（`experiments:write`）

**リクエストボディ**:

```json
{
  "experiment_name": "Sales Forecast Q4",
  "experiment_description": "Forecasting sales for Q4 2025",
  "experiment_type": "training",
  "tags": {
    "department": "sales",
    "priority": "high"
  },
  "metadata": {
    "forecast_horizon": 7,
    "frequency": "D"
  }
}
```

**スキーマ**:

| フィールド | 型 | 必須 | 制約 | 説明 |
|-----------|---|------|------|------|
| `experiment_name` | string | ✅ | max: 255 | 実験名 |
| `experiment_description` | string | ❌ | - | 実験の説明 |
| `experiment_type` | string | ❌ | enum | `training`, `testing`, `production` |
| `tags` | object | ❌ | - | カスタムタグ |
| `metadata` | object | ❌ | - | メタデータ |

**レスポンス** (201 Created):

```json
{
  "experiment_id": 124,
  "experiment_name": "Sales Forecast Q4",
  "experiment_description": "Forecasting sales for Q4 2025",
  "experiment_type": "training",
  "status": "active",
  "lifecycle_stage": "active",
  "created_by": "user@example.com",
  "created_at": "2025-11-03T16:00:00Z",
  "updated_at": "2025-11-03T16:00:00Z",
  "tags": {
    "department": "sales",
    "priority": "high"
  },
  "metadata": {
    "forecast_horizon": 7,
    "frequency": "D"
  }
}
```

**エラー**:
- `400`: バリデーションエラー
- `401`: 認証エラー
- `403`: 権限なし
- `409`: 同名の実験が既に存在
- `422`: バリデーションエラー（詳細）

---

#### 4.1.3 実験詳細取得

```http
GET /v1/experiments/{experiment_id}
```

**認証**: 必須（`experiments:read`）

**パスパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|---|------|
| `experiment_id` | integer | 実験ID |

**レスポンス** (200 OK):

```json
{
  "experiment_id": 123,
  "experiment_name": "Sales Forecast Q4",
  "experiment_description": "Forecasting sales for Q4 2025",
  "experiment_type": "training",
  "status": "active",
  "lifecycle_stage": "active",
  "created_by": "user@example.com",
  "created_at": "2025-11-01T10:00:00Z",
  "updated_at": "2025-11-03T15:30:00Z",
  "deleted_at": null,
  "tags": {
    "department": "sales",
    "priority": "high"
  },
  "metadata": {
    "total_runs": 15,
    "completed_runs": 12,
    "failed_runs": 3,
    "best_model": {
      "model_id": 456,
      "model_name": "AutoNHITS",
      "validation_mae": 123.45
    }
  },
  "runs": {
    "total": 15,
    "completed": 12,
    "failed": 3,
    "running": 0
  }
}
```

**エラー**:
- `404`: 実験が見つからない
- `401`: 認証エラー
- `403`: 権限なし

---

#### 4.1.4 実験更新

```http
PATCH /v1/experiments/{experiment_id}
```

**認証**: 必須（`experiments:write`）

**リクエストボディ**:

```json
{
  "experiment_name": "Sales Forecast Q4 Updated",
  "experiment_description": "Updated description",
  "status": "archived",
  "tags": {
    "department": "sales",
    "priority": "medium"
  }
}
```

**レスポンス** (200 OK):

```json
{
  "experiment_id": 123,
  "experiment_name": "Sales Forecast Q4 Updated",
  "experiment_description": "Updated description",
  "status": "archived",
  "updated_at": "2025-11-03T17:00:00Z"
}
```

**エラー**:
- `400`: バリデーションエラー
- `404`: 実験が見つからない
- `409`: 競合エラー

---

#### 4.1.5 実験削除

```http
DELETE /v1/experiments/{experiment_id}
```

**認証**: 必須（`experiments:delete`）

**クエリパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
|-----------|---|------|------|
| `hard_delete` | boolean | ❌ | 物理削除フラグ（デフォルト: false） |

**レスポンス** (204 No Content):

```
(空のレスポンス)
```

**エラー**:
- `404`: 実験が見つからない
- `403`: 権限なし（物理削除はAdmin権限必要）
- `409`: 削除不可（実行中のRunが存在）

---

### 4.2 実行管理（Runs）

#### 4.2.1 実行一覧取得

```http
GET /v1/runs
GET /v1/experiments/{experiment_id}/runs
```

**認証**: 必須（`experiments:read`）

**クエリパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
|-----------|---|------|------|
| `experiment_id` | integer | ❌ | 実験IDフィルタ |
| `status` | string | ❌ | ステータスフィルタ |
| `page` | integer | ❌ | ページ番号 |
| `per_page` | integer | ❌ | 1ページあたり件数 |
| `sort` | string | ❌ | ソートキー |

**レスポンス** (200 OK):

```json
{
  "data": [
    {
      "run_id": 789,
      "run_uuid": "550e8400-e29b-41d4-a716-446655440000",
      "experiment_id": 123,
      "run_name": "AutoNHITS_run_001",
      "run_fingerprint": "a3f5c8d9e2b1f0a4c6d8e9f1a2b3c4d5",
      "status": "completed",
      "lifecycle_stage": "active",
      "start_time": "2025-11-03T10:00:00Z",
      "end_time": "2025-11-03T10:45:23Z",
      "execution_duration_seconds": 2723.456,
      "source_type": "cli",
      "user_id": "user@example.com",
      "tags": {
        "model_type": "AutoNHITS",
        "version": "1.0"
      },
      "metadata": {
        "model_count": 1,
        "gpu_used": true
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 45
  }
}
```

---

#### 4.2.2 実行作成

```http
POST /v1/runs
```

**認証**: 必須（`experiments:write`）

**リクエストボディ**:

```json
{
  "experiment_id": 123,
  "run_name": "AutoNHITS_run_002",
  "run_description": "Testing new hyperparameters",
  "source_type": "cli",
  "git_commit_hash": "abc123def456",
  "git_branch": "main",
  "tags": {
    "model_type": "AutoNHITS",
    "version": "1.1"
  },
  "metadata": {
    "config_file": "config/experiment_001.yaml"
  }
}
```

**レスポンス** (201 Created):

```json
{
  "run_id": 790,
  "run_uuid": "660f9511-f3ac-52e5-b827-556766551111",
  "experiment_id": 123,
  "run_name": "AutoNHITS_run_002",
  "run_fingerprint": "b4g6d9e3c2g1h5b7d9f2b3c4d5e6f7g8",
  "status": "running",
  "lifecycle_stage": "active",
  "start_time": "2025-11-03T18:00:00Z",
  "end_time": null,
  "execution_duration_seconds": null,
  "created_at": "2025-11-03T18:00:00Z"
}
```

---

#### 4.2.3 実行詳細取得

```http
GET /v1/runs/{run_id}
```

**認証**: 必須（`experiments:read`）

**レスポンス** (200 OK):

```json
{
  "run_id": 789,
  "run_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "experiment_id": 123,
  "parent_run_id": null,
  "run_name": "AutoNHITS_run_001",
  "run_description": "Initial training run",
  "run_fingerprint": "a3f5c8d9e2b1f0a4c6d8e9f1a2b3c4d5",
  "status": "completed",
  "lifecycle_stage": "active",
  "start_time": "2025-11-03T10:00:00Z",
  "end_time": "2025-11-03T10:45:23Z",
  "execution_duration_seconds": 2723.456,
  "source_type": "cli",
  "source_name": "train.py",
  "git_commit_hash": "abc123def456",
  "git_branch": "main",
  "git_repo_url": "https://github.com/example/repo.git",
  "user_id": "user@example.com",
  "tags": {
    "model_type": "AutoNHITS",
    "version": "1.0"
  },
  "metadata": {
    "model_count": 1,
    "gpu_used": true,
    "gpu_type": "NVIDIA RTX 3090"
  },
  "created_at": "2025-11-03T10:00:00Z",
  "updated_at": "2025-11-03T10:45:23Z",
  "models": [
    {
      "model_id": 456,
      "model_name": "AutoNHITS",
      "model_type": "AutoNHITS",
      "status": "evaluated"
    }
  ],
  "metrics_summary": {
    "validation_mae": 123.45,
    "validation_rmse": 156.78,
    "validation_smape": 8.92,
    "test_mae": 125.67,
    "test_rmse": 158.90,
    "test_smape": 9.12
  }
}
```

---

#### 4.2.4 実行更新

```http
PATCH /v1/runs/{run_id}
```

**認証**: 必須（`experiments:write`）

**リクエストボディ**:

```json
{
  "status": "completed",
  "end_time": "2025-11-03T10:45:23Z",
  "execution_duration_seconds": 2723.456,
  "tags": {
    "model_type": "AutoNHITS",
    "version": "1.0",
    "reviewed": true
  }
}
```

**レスポンス** (200 OK):

```json
{
  "run_id": 789,
  "status": "completed",
  "end_time": "2025-11-03T10:45:23Z",
  "execution_duration_seconds": 2723.456,
  "updated_at": "2025-11-03T10:45:30Z"
}
```

---

#### 4.2.5 実行削除

```http
DELETE /v1/runs/{run_id}
```

**認証**: 必須（`experiments:delete`）

**レスポンス** (204 No Content)

---

### 4.3 モデル管理（Models）

#### 4.3.1 モデル一覧取得

```http
GET /v1/models
GET /v1/runs/{run_id}/models
```

**認証**: 必須（`models:read`）

**クエリパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
|-----------|---|------|------|
| `run_id` | integer | ❌ | 実行IDフィルタ |
| `model_type` | string | ❌ | モデル種別フィルタ |
| `framework` | string | ❌ | フレームワークフィルタ |
| `status` | string | ❌ | ステータスフィルタ |
| `page` | integer | ❌ | ページ番号 |
| `per_page` | integer | ❌ | 1ページあたり件数 |
| `sort` | string | ❌ | ソートキー |

**レスポンス** (200 OK):

```json
{
  "data": [
    {
      "model_id": 456,
      "model_uuid": "770g0622-g4bd-63f6-c938-667877662222",
      "run_id": 789,
      "model_name": "AutoNHITS_sales_forecast",
      "model_type": "AutoNHITS",
      "model_version": "1.0.0",
      "framework": "neuralforecast",
      "framework_version": "1.6.4",
      "model_config": {
        "input_size": 30,
        "h": 7,
        "max_steps": 500
      },
      "hyperparameters": {
        "learning_rate": 0.001,
        "batch_size": 32,
        "num_stacks": 3
      },
      "training_samples": 10000,
      "training_duration_seconds": 2400.567,
      "model_size_bytes": 52428800,
      "model_file_path": "/models/staging/model_456.pkl",
      "status": "evaluated",
      "created_at": "2025-11-03T10:15:00Z",
      "updated_at": "2025-11-03T10:55:00Z",
      "metrics": {
        "validation_mae": 123.45,
        "validation_rmse": 156.78,
        "test_mae": 125.67
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 87
  }
}
```

---

#### 4.3.2 モデル作成

```http
POST /v1/models
```

**認証**: 必須（`models:write`）

**リクエストボディ**:

```json
{
  "run_id": 789,
  "model_name": "AutoNHITS_sales_forecast",
  "model_type": "AutoNHITS",
  "model_version": "1.0.0",
  "framework": "neuralforecast",
  "framework_version": "1.6.4",
  "model_config": {
    "input_size": 30,
    "h": 7,
    "max_steps": 500
  },
  "hyperparameters": {
    "learning_rate": 0.001,
    "batch_size": 32,
    "num_stacks": 3
  },
  "training_dataset_id": 234,
  "training_samples": 10000,
  "model_file_path": "/models/staging/model_456.pkl",
  "tags": {
    "use_case": "sales_forecast",
    "region": "north_america"
  }
}
```

**レスポンス** (201 Created):

```json
{
  "model_id": 456,
  "model_uuid": "770g0622-g4bd-63f6-c938-667877662222",
  "run_id": 789,
  "model_name": "AutoNHITS_sales_forecast",
  "model_type": "AutoNHITS",
  "status": "training",
  "created_at": "2025-11-03T10:15:00Z"
}
```

---

#### 4.3.3 モデル詳細取得

```http
GET /v1/models/{model_id}
```

**認証**: 必須（`models:read`）

**レスポンス** (200 OK):

```json
{
  "model_id": 456,
  "model_uuid": "770g0622-g4bd-63f6-c938-667877662222",
  "run_id": 789,
  "model_name": "AutoNHITS_sales_forecast",
  "model_type": "AutoNHITS",
  "model_version": "1.0.0",
  "framework": "neuralforecast",
  "framework_version": "1.6.4",
  "model_config": {
    "input_size": 30,
    "h": 7,
    "max_steps": 500,
    "loss": "MAE",
    "scaler_type": "standard"
  },
  "hyperparameters": {
    "learning_rate": 0.001,
    "batch_size": 32,
    "num_stacks": 3,
    "n_pool_kernel_size": [2, 2, 2],
    "n_freq_downsample": [4, 2, 1]
  },
  "training_dataset_id": 234,
  "training_samples": 10000,
  "training_duration_seconds": 2400.567,
  "model_size_bytes": 52428800,
  "model_file_path": "/models/staging/model_456.pkl",
  "checkpoint_path": "/models/checkpoints/model_456_checkpoint.ckpt",
  "status": "evaluated",
  "tags": {
    "use_case": "sales_forecast",
    "region": "north_america"
  },
  "metadata": {
    "training_device": "cuda:0",
    "num_epochs": 50,
    "early_stopping_patience": 10
  },
  "created_at": "2025-11-03T10:15:00Z",
  "updated_at": "2025-11-03T10:55:00Z",
  "registry": {
    "registry_id": 12,
    "registered_model_name": "sales_forecast_prod",
    "model_version": 3,
    "current_stage": "staging"
  },
  "metrics": {
    "train": {
      "mae": 118.23,
      "rmse": 149.67,
      "smape": 8.45
    },
    "validation": {
      "mae": 123.45,
      "rmse": 156.78,
      "smape": 8.92
    },
    "test": {
      "mae": 125.67,
      "rmse": 158.90,
      "smape": 9.12
    }
  }
}
```

---

#### 4.3.4 モデルデプロイ

```http
POST /v1/models/{model_id}/deploy
```

**認証**: 必須（`models:deploy`）

**リクエストボディ**:

```json
{
  "stage": "production",
  "deployment_target": "kubernetes-cluster-prod",
  "approval_notes": "Performance validated on test data",
  "metadata": {
    "replicas": 3,
    "resource_limits": {
      "cpu": "2",
      "memory": "4Gi"
    }
  }
}
```

**レスポンス** (200 OK):

```json
{
  "model_id": 456,
  "registry_id": 12,
  "current_stage": "production",
  "previous_stage": "staging",
  "stage_transition_at": "2025-11-03T19:00:00Z",
  "deployed_at": "2025-11-03T19:05:00Z",
  "deployment_target": "kubernetes-cluster-prod",
  "deployment_status": "deployed",
  "deployment_url": "https://api.example.com/v1/predictions/models/456"
}
```

---

#### 4.3.5 モデルダウンロード

```http
GET /v1/models/{model_id}/download
```

**認証**: 必須（`models:read`）

**レスポンス** (200 OK):

```
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="model_456.pkl"
Content-Length: 52428800

(バイナリデータ)
```

---

### 4.4 データセット管理（Datasets）

#### 4.4.1 データセット一覧取得

```http
GET /v1/datasets
```

**認証**: 必須（`experiments:read`）

**クエリパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
|-----------|---|------|------|
| `dataset_type` | string | ❌ | データセット種別フィルタ |
| `page` | integer | ❌ | ページ番号 |
| `per_page` | integer | ❌ | 1ページあたり件数 |

**レスポンス** (200 OK):

```json
{
  "data": [
    {
      "dataset_id": 234,
      "dataset_uuid": "880h1733-h5ce-74g7-d049-778988773333",
      "dataset_name": "sales_data_2025",
      "dataset_description": "Daily sales data for 2025",
      "dataset_type": "training",
      "file_path": "/data/processed/sales_2025.csv",
      "file_format": "csv",
      "file_size_bytes": 10485760,
      "file_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "num_rows": 50000,
      "num_columns": 15,
      "num_time_series": 100,
      "date_column": "ds",
      "target_column": "y",
      "frequency": "D",
      "start_date": "2025-01-01T00:00:00Z",
      "end_date": "2025-10-31T00:00:00Z",
      "version": "1.0.0",
      "created_at": "2025-11-01T08:00:00Z",
      "updated_at": "2025-11-01T08:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 42
  }
}
```

---

#### 4.4.2 データセット作成

```http
POST /v1/datasets
```

**認証**: 必須（`experiments:write`）

**Content-Type**: `multipart/form-data`

**リクエストボディ**:

```
--boundary
Content-Disposition: form-data; name="file"; filename="sales_2025.csv"
Content-Type: text/csv

(CSVファイルの内容)
--boundary
Content-Disposition: form-data; name="dataset_name"

sales_data_2025
--boundary
Content-Disposition: form-data; name="dataset_type"

training
--boundary
Content-Disposition: form-data; name="metadata"

{"frequency": "D", "target_column": "y"}
--boundary--
```

**レスポンス** (201 Created):

```json
{
  "dataset_id": 235,
  "dataset_uuid": "990i2844-i6df-85h8-e150-889099884444",
  "dataset_name": "sales_data_2025",
  "dataset_type": "training",
  "file_path": "/data/processed/sales_2025.csv",
  "file_size_bytes": 10485760,
  "file_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "upload_status": "processing",
  "created_at": "2025-11-03T20:00:00Z"
}
```

---

#### 4.4.3 データセット詳細取得

```http
GET /v1/datasets/{dataset_id}
```

**認証**: 必須（`experiments:read`）

**レスポンス** (200 OK):

```json
{
  "dataset_id": 234,
  "dataset_uuid": "880h1733-h5ce-74g7-d049-778988773333",
  "dataset_name": "sales_data_2025",
  "dataset_description": "Daily sales data for 2025",
  "dataset_type": "training",
  "file_path": "/data/processed/sales_2025.csv",
  "file_format": "csv",
  "file_size_bytes": 10485760,
  "file_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "num_rows": 50000,
  "num_columns": 15,
  "num_time_series": 100,
  "date_column": "ds",
  "target_column": "y",
  "frequency": "D",
  "start_date": "2025-01-01T00:00:00Z",
  "end_date": "2025-10-31T00:00:00Z",
  "schema_definition": {
    "unique_id": "string",
    "ds": "datetime",
    "y": "float64",
    "exog_1": "float64",
    "exog_2": "category"
  },
  "column_types": {
    "numeric": ["y", "exog_1"],
    "categorical": ["unique_id", "exog_2"],
    "datetime": ["ds"]
  },
  "missing_values_count": 25,
  "duplicate_rows_count": 0,
  "version": "1.0.0",
  "parent_dataset_id": null,
  "tags": {
    "source": "sales_db",
    "region": "all"
  },
  "metadata": {
    "preprocessing": {
      "outlier_removal": true,
      "imputation": "forward_fill"
    }
  },
  "created_at": "2025-11-01T08:00:00Z",
  "updated_at": "2025-11-01T08:00:00Z",
  "features": [
    {
      "feature_id": 1,
      "feature_name": "y",
      "feature_type": "numeric",
      "data_type": "float64",
      "min_value": 0.0,
      "max_value": 10000.0,
      "mean_value": 2500.5,
      "std_value": 750.3,
      "missing_count": 0,
      "feature_role": "target",
      "is_target": true
    }
  ]
}
```

---

#### 4.4.4 データセット統計取得

```http
GET /v1/datasets/{dataset_id}/statistics
```

**認証**: 必須（`experiments:read`）

**レスポンス** (200 OK):

```json
{
  "dataset_id": 234,
  "statistics": {
    "overall": {
      "num_rows": 50000,
      "num_columns": 15,
      "num_time_series": 100,
      "time_range_days": 304,
      "missing_rate": 0.05
    },
    "target_variable": {
      "name": "y",
      "min": 0.0,
      "max": 10000.0,
      "mean": 2500.5,
      "median": 2450.0,
      "std": 750.3,
      "q1": 1875.0,
      "q3": 3125.0
    },
    "time_series": [
      {
        "unique_id": "series_001",
        "num_observations": 304,
        "start_date": "2025-01-01",
        "end_date": "2025-10-31",
        "missing_count": 2,
        "mean": 2600.0,
        "trend": "increasing"
      }
    ]
  }
}
```

---

### 4.5 評価指標（Metrics）

#### 4.5.1 評価指標一覧取得

```http
GET /v1/metrics
GET /v1/runs/{run_id}/metrics
GET /v1/models/{model_id}/metrics
```

**認証**: 必須（`experiments:read`）

**クエリパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
|-----------|---|------|------|
| `run_id` | integer | ❌ | 実行IDフィルタ |
| `model_id` | integer | ❌ | モデルIDフィルタ |
| `metric_name` | string | ❌ | 指標名フィルタ |
| `dataset_type` | string | ❌ | データセット種別フィルタ |

**レスポンス** (200 OK):

```json
{
  "data": [
    {
      "metric_id": 10001,
      "run_id": 789,
      "model_id": 456,
      "metric_name": "mae",
      "metric_value": 123.45,
      "metric_step": 0,
      "dataset_type": "validation",
      "evaluation_context": "final_evaluation",
      "timestamp": "2025-11-03T10:45:00Z",
      "metadata": {
        "horizon": 7,
        "aggregation": "mean"
      }
    },
    {
      "metric_id": 10002,
      "run_id": 789,
      "model_id": 456,
      "metric_name": "rmse",
      "metric_value": 156.78,
      "metric_step": 0,
      "dataset_type": "validation",
      "evaluation_context": "final_evaluation",
      "timestamp": "2025-11-03T10:45:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150
  }
}
```

---

#### 4.5.2 評価指標記録

```http
POST /v1/metrics
```

**認証**: 必須（`experiments:write`）

**リクエストボディ**:

```json
{
  "run_id": 789,
  "model_id": 456,
  "metrics": [
    {
      "metric_name": "mae",
      "metric_value": 123.45,
      "metric_step": 0,
      "dataset_type": "validation"
    },
    {
      "metric_name": "rmse",
      "metric_value": 156.78,
      "metric_step": 0,
      "dataset_type": "validation"
    },
    {
      "metric_name": "smape",
      "metric_value": 8.92,
      "metric_step": 0,
      "dataset_type": "validation"
    }
  ]
}
```

**レスポンス** (201 Created):

```json
{
  "created_count": 3,
  "metrics": [
    {
      "metric_id": 10001,
      "metric_name": "mae",
      "metric_value": 123.45
    },
    {
      "metric_id": 10002,
      "metric_name": "rmse",
      "metric_value": 156.78
    },
    {
      "metric_id": 10003,
      "metric_name": "smape",
      "metric_value": 8.92
    }
  ]
}
```

---

#### 4.5.3 評価指標比較

```http
GET /v1/metrics/compare
```

**認証**: 必須（`experiments:read`）

**クエリパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
|-----------|---|------|------|
| `run_ids` | string | ✅ | カンマ区切りの実行ID（例: `789,790,791`） |
| `metric_names` | string | ✅ | カンマ区切りの指標名（例: `mae,rmse,smape`） |
| `dataset_type` | string | ❌ | データセット種別 |

**レスポンス** (200 OK):

```json
{
  "comparison": [
    {
      "run_id": 789,
      "run_name": "AutoNHITS_run_001",
      "model_id": 456,
      "model_name": "AutoNHITS_sales_forecast",
      "metrics": {
        "mae": 123.45,
        "rmse": 156.78,
        "smape": 8.92
      }
    },
    {
      "run_id": 790,
      "run_name": "AutoLSTM_run_001",
      "model_id": 457,
      "model_name": "AutoLSTM_sales_forecast",
      "metrics": {
        "mae": 125.67,
        "rmse": 159.23,
        "smape": 9.15
      }
    }
  ],
  "best_model": {
    "run_id": 789,
    "model_id": 456,
    "metric_name": "mae",
    "metric_value": 123.45
  }
}
```

---

### 4.6 予測（Predictions）

#### 4.6.1 予測実行

```http
POST /v1/predictions
```

**認証**: 必須（`predictions:create`）

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
    "exog_1": [10.5, 12.3]
  },
  "metadata": {
    "request_source": "api",
    "confidence_level": 0.95
  }
}
```

**レスポンス** (202 Accepted):

```json
{
  "prediction_job_id": "pj_abc123def456",
  "status": "processing",
  "model_id": 456,
  "prediction_date": "2025-11-04T00:00:00Z",
  "horizon": 7,
  "estimated_completion_time": "2025-11-03T21:05:00Z",
  "created_at": "2025-11-03T21:00:00Z",
  "status_url": "/v1/predictions/jobs/pj_abc123def456",
  "result_url": "/v1/predictions/jobs/pj_abc123def456/results"
}
```

---

#### 4.6.2 予測ジョブ状態確認

```http
GET /v1/predictions/jobs/{job_id}
```

**認証**: 必須（`predictions:read`）

**レスポンス** (200 OK):

```json
{
  "prediction_job_id": "pj_abc123def456",
  "status": "completed",
  "model_id": 456,
  "prediction_date": "2025-11-04T00:00:00Z",
  "horizon": 7,
  "progress": 100,
  "created_at": "2025-11-03T21:00:00Z",
  "completed_at": "2025-11-03T21:03:45Z",
  "execution_duration_seconds": 225.5,
  "result_url": "/v1/predictions/jobs/pj_abc123def456/results"
}
```

**ステータス**: `processing`, `completed`, `failed`, `cancelled`

---

#### 4.6.3 予測結果取得

```http
GET /v1/predictions/jobs/{job_id}/results
```

**認証**: 必須（`predictions:read`）

**レスポンス** (200 OK):

```json
{
  "prediction_job_id": "pj_abc123def456",
  "model_id": 456,
  "prediction_date": "2025-11-04T00:00:00Z",
  "horizon": 7,
  "predictions": [
    {
      "unique_id": "series_001",
      "forecasts": [
        {
          "ds": "2025-11-04",
          "horizon": 1,
          "predicted_value": 2550.5,
          "lower_bound": 2300.0,
          "upper_bound": 2800.0,
          "confidence_level": 0.95
        },
        {
          "ds": "2025-11-05",
          "horizon": 2,
          "predicted_value": 2600.3,
          "lower_bound": 2330.0,
          "upper_bound": 2870.0,
          "confidence_level": 0.95
        }
      ]
    },
    {
      "unique_id": "series_002",
      "forecasts": [
        {
          "ds": "2025-11-04",
          "horizon": 1,
          "predicted_value": 3050.8,
          "lower_bound": 2750.0,
          "upper_bound": 3350.0,
          "confidence_level": 0.95
        }
      ]
    }
  ],
  "metadata": {
    "total_time_series": 2,
    "total_predictions": 14,
    "execution_time_seconds": 225.5
  }
}
```

---

#### 4.6.4 予測履歴取得

```http
GET /v1/predictions
```

**認証**: 必須（`predictions:read`）

**クエリパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
|-----------|---|------|------|
| `model_id` | integer | ❌ | モデルIDフィルタ |
| `unique_id` | string | ❌ | 時系列IDフィルタ |
| `start_date` | string | ❌ | 開始日フィルタ |
| `end_date` | string | ❌ | 終了日フィルタ |

**レスポンス** (200 OK):

```json
{
  "data": [
    {
      "prediction_id": 50001,
      "run_id": 789,
      "model_id": 456,
      "prediction_date": "2025-11-04T00:00:00Z",
      "unique_id": "series_001",
      "horizon": 1,
      "predicted_value": 2550.5,
      "actual_value": null,
      "lower_bound": 2300.0,
      "upper_bound": 2800.0,
      "confidence_level": 0.95,
      "created_at": "2025-11-03T21:03:45Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 5000
  }
}
```

---

### 4.7 ハイパーパラメータ（Hyperparameters）

#### 4.7.1 ハイパーパラメータ取得

```http
GET /v1/runs/{run_id}/hyperparameters
```

**認証**: 必須（`experiments:read`）

**レスポンス** (200 OK):

```json
{
  "run_id": 789,
  "hyperparameters": [
    {
      "hyperparameter_id": 2001,
      "param_key": "learning_rate",
      "param_value": "0.001",
      "param_type": "float",
      "is_hyperparameter": true,
      "param_category": "optimizer"
    },
    {
      "hyperparameter_id": 2002,
      "param_key": "batch_size",
      "param_value": "32",
      "param_type": "integer",
      "is_hyperparameter": true,
      "param_category": "training"
    },
    {
      "hyperparameter_id": 2003,
      "param_key": "input_size",
      "param_value": "30",
      "param_type": "integer",
      "is_hyperparameter": false,
      "param_category": "model"
    }
  ]
}
```

---

#### 4.7.2 ハイパーパラメータ記録

```http
POST /v1/runs/{run_id}/hyperparameters
```

**認証**: 必須（`experiments:write`）

**リクエストボディ**:

```json
{
  "hyperparameters": [
    {
      "param_key": "learning_rate",
      "param_value": "0.001",
      "param_type": "float",
      "is_hyperparameter": true,
      "param_category": "optimizer"
    },
    {
      "param_key": "batch_size",
      "param_value": "32",
      "param_type": "integer",
      "is_hyperparameter": true,
      "param_category": "training"
    }
  ]
}
```

**レスポンス** (201 Created):

```json
{
  "run_id": 789,
  "created_count": 2,
  "hyperparameters": [
    {
      "hyperparameter_id": 2001,
      "param_key": "learning_rate",
      "param_value": "0.001"
    },
    {
      "hyperparameter_id": 2002,
      "param_key": "batch_size",
      "param_value": "32"
    }
  ]
}
```

---

#### 4.7.3 探索空間取得

```http
GET /v1/hyperparameters/search-spaces
```

**認証**: 必須（`experiments:read`）

**クエリパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
|-----------|---|------|------|
| `model_type` | string | ❌ | モデル種別フィルタ |

**レスポンス** (200 OK):

```json
{
  "data": [
    {
      "search_space_id": 5,
      "space_name": "AutoNHITS_default",
      "space_description": "Default search space for AutoNHITS",
      "model_type": "AutoNHITS",
      "framework": "neuralforecast",
      "search_space_definition": {
        "learning_rate": {
          "type": "loguniform",
          "low": 1e-4,
          "high": 1e-2
        },
        "batch_size": {
          "type": "categorical",
          "choices": [16, 32, 64, 128]
        },
        "num_stacks": {
          "type": "int",
          "low": 2,
          "high": 5
        }
      },
      "is_active": true,
      "created_at": "2025-10-01T00:00:00Z"
    }
  ]
}
```

---

### 4.8 アーティファクト（Artifacts）

#### 4.8.1 アーティファクト一覧取得

```http
GET /v1/runs/{run_id}/artifacts
```

**認証**: 必須（`experiments:read`）

**クエリパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
|-----------|---|------|------|
| `artifact_type` | string | ❌ | アーティファクト種別フィルタ |

**レスポンス** (200 OK):

```json
{
  "data": [
    {
      "artifact_id": 3001,
      "artifact_uuid": "aa0j3955-j7eg-96i9-f261-990100995555",
      "run_id": 789,
      "artifact_name": "training_plot.png",
      "artifact_type": "plot",
      "artifact_path": "runs/789/artifacts/training_plot.png",
      "file_size_bytes": 524288,
      "file_format": "png",
      "mime_type": "image/png",
      "file_hash": "d3f8b6e9c2a1f4d6e8f1a3b5c7d9e2f4",
      "storage_type": "local",
      "storage_path": "/outputs/runs/789/artifacts/training_plot.png",
      "is_public": false,
      "created_at": "2025-11-03T10:45:00Z",
      "download_url": "/v1/artifacts/3001/download"
    }
  ]
}
```

---

#### 4.8.2 アーティファクトアップロード

```http
POST /v1/runs/{run_id}/artifacts
```

**認証**: 必須（`experiments:write`）

**Content-Type**: `multipart/form-data`

**リクエストボディ**:

```
--boundary
Content-Disposition: form-data; name="file"; filename="training_plot.png"
Content-Type: image/png

(画像ファイルの内容)
--boundary
Content-Disposition: form-data; name="artifact_name"

training_plot.png
--boundary
Content-Disposition: form-data; name="artifact_type"

plot
--boundary--
```

**レスポンス** (201 Created):

```json
{
  "artifact_id": 3002,
  "artifact_uuid": "bb1k4066-k8fh-07j0-g372-001211006666",
  "run_id": 789,
  "artifact_name": "training_plot.png",
  "artifact_type": "plot",
  "file_size_bytes": 524288,
  "upload_status": "completed",
  "created_at": "2025-11-03T22:00:00Z",
  "download_url": "/v1/artifacts/3002/download"
}
```

---

#### 4.8.3 アーティファクトダウンロード

```http
GET /v1/artifacts/{artifact_id}/download
```

**認証**: 必須（`experiments:read`）

**レスポンス** (200 OK):

```
Content-Type: image/png
Content-Disposition: attachment; filename="training_plot.png"
Content-Length: 524288

(バイナリデータ)
```

---

### 4.9 ユーザー管理（Users）

#### 4.9.1 ユーザー一覧取得

```http
GET /v1/users
```

**認証**: 必須（`admin:all`）

**レスポンス** (200 OK):

```json
{
  "data": [
    {
      "user_id": 1,
      "user_uuid": "cc2l5177-l9gi-18k1-h483-112322117777",
      "username": "alice",
      "email": "alice@example.com",
      "full_name": "Alice Smith",
      "is_active": true,
      "is_superuser": false,
      "last_login_at": "2025-11-03T20:00:00Z",
      "login_count": 145,
      "created_at": "2025-01-15T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 25
  }
}
```

---

#### 4.9.2 現在のユーザー情報取得

```http
GET /v1/users/me
```

**認証**: 必須

**レスポンス** (200 OK):

```json
{
  "user_id": 1,
  "user_uuid": "cc2l5177-l9gi-18k1-h483-112322117777",
  "username": "alice",
  "email": "alice@example.com",
  "full_name": "Alice Smith",
  "is_active": true,
  "is_superuser": false,
  "last_login_at": "2025-11-03T20:00:00Z",
  "login_count": 145,
  "preferences": {
    "theme": "dark",
    "notifications": true,
    "timezone": "America/New_York"
  },
  "roles": ["data_scientist"],
  "scopes": [
    "experiments:read",
    "experiments:write",
    "models:read",
    "models:write",
    "predictions:create"
  ],
  "created_at": "2025-01-15T10:00:00Z"
}
```

---

#### 4.9.3 ユーザー作成

```http
POST /v1/users
```

**認証**: 必須（`admin:all`）

**リクエストボディ**:

```json
{
  "username": "bob",
  "email": "bob@example.com",
  "full_name": "Bob Johnson",
  "password": "secure_password_here",
  "is_active": true,
  "roles": ["analyst"]
}
```

**レスポンス** (201 Created):

```json
{
  "user_id": 26,
  "user_uuid": "dd3m6288-m0hj-29l2-i594-223433228888",
  "username": "bob",
  "email": "bob@example.com",
  "full_name": "Bob Johnson",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-11-03T22:30:00Z"
}
```

---

### 4.10 システム管理（System）

#### 4.10.1 ヘルスチェック

```http
GET /v1/health
```

**認証**: 不要

**レスポンス** (200 OK):

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-03T23:00:00Z",
  "services": {
    "database": {
      "status": "healthy",
      "response_time_ms": 5.2
    },
    "mlflow": {
      "status": "healthy",
      "response_time_ms": 12.3
    },
    "file_storage": {
      "status": "healthy",
      "available_space_gb": 450.5
    }
  }
}
```

---

#### 4.10.2 システム統計

```http
GET /v1/system/statistics
```

**認証**: 必須（`admin:all`）

**レスポンス** (200 OK):

```json
{
  "statistics": {
    "experiments": {
      "total": 150,
      "active": 120,
      "archived": 30
    },
    "runs": {
      "total": 4500,
      "completed": 4200,
      "failed": 250,
      "running": 50
    },
    "models": {
      "total": 3800,
      "deployed": 25,
      "staging": 150,
      "archived": 3625
    },
    "storage": {
      "total_size_gb": 256.8,
      "models_size_gb": 180.5,
      "artifacts_size_gb": 76.3
    },
    "predictions": {
      "total": 1250000,
      "last_24h": 5000
    }
  },
  "updated_at": "2025-11-03T23:00:00Z"
}
```

---

#### 4.10.3 システム設定取得

```http
GET /v1/system/config
```

**認証**: 必須（`admin:all`）

**レスポンス** (200 OK):

```json
{
  "config": [
    {
      "config_id": 1,
      "config_key": "max_parallel_runs",
      "config_value": "10",
      "config_type": "integer",
      "category": "execution",
      "description": "Maximum number of parallel runs"
    },
    {
      "config_id": 2,
      "config_key": "default_retention_days",
      "config_value": "90",
      "config_type": "integer",
      "category": "storage",
      "description": "Default data retention period in days"
    }
  ]
}
```

---

#### 4.10.4 システム設定更新

```http
PATCH /v1/system/config/{config_key}
```

**認証**: 必須（`admin:all`）

**リクエストボディ**:

```json
{
  "config_value": "15"
}
```

**レスポンス** (200 OK):

```json
{
  "config_id": 1,
  "config_key": "max_parallel_runs",
  "config_value": "15",
  "config_type": "integer",
  "updated_at": "2025-11-03T23:15:00Z"
}
```

---

## 5. エラーハンドリング

### 5.1 エラーレスポンス形式

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": [
      {
        "field": "field_name",
        "message": "Field-specific error message",
        "code": "field_error_code"
      }
    ],
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-11-03T10:30:00Z",
    "path": "/v1/endpoint",
    "method": "POST",
    "documentation_url": "https://docs.example.com/errors/ERROR_CODE"
  }
}
```

---

### 5.2 エラーコード一覧

| HTTPコード | エラーコード | 説明 | 対処方法 |
|-----------|-------------|------|----------|
| **400** | `BAD_REQUEST` | 不正なリクエスト | リクエストを確認 |
| **400** | `INVALID_PARAMETER` | 無効なパラメータ | パラメータを修正 |
| **401** | `UNAUTHORIZED` | 認証エラー | トークンを確認 |
| **401** | `TOKEN_EXPIRED` | トークン期限切れ | トークンを再取得 |
| **401** | `INVALID_TOKEN` | 無効なトークン | トークンを再取得 |
| **403** | `FORBIDDEN` | 権限不足 | 権限を確認 |
| **403** | `INSUFFICIENT_SCOPE` | スコープ不足 | 必要なスコープを取得 |
| **404** | `NOT_FOUND` | リソース未発見 | リソースIDを確認 |
| **404** | `EXPERIMENT_NOT_FOUND` | 実験が見つからない | 実験IDを確認 |
| **404** | `RUN_NOT_FOUND` | 実行が見つからない | 実行IDを確認 |
| **404** | `MODEL_NOT_FOUND` | モデルが見つからない | モデルIDを確認 |
| **409** | `CONFLICT` | リソース競合 | リソースを確認 |
| **409** | `DUPLICATE_NAME` | 重複する名前 | 名前を変更 |
| **409** | `DUPLICATE_FINGERPRINT` | 重複するフィンガープリント | 実行は既に存在 |
| **422** | `VALIDATION_ERROR` | バリデーションエラー | 入力値を修正 |
| **422** | `INVALID_FORMAT` | フォーマットエラー | フォーマットを修正 |
| **429** | `RATE_LIMIT_EXCEEDED` | レート制限超過 | しばらく待つ |
| **500** | `INTERNAL_SERVER_ERROR` | サーバー内部エラー | サポートに連絡 |
| **500** | `DATABASE_ERROR` | データベースエラー | サポートに連絡 |
| **503** | `SERVICE_UNAVAILABLE` | サービス停止中 | しばらく待つ |
| **503** | `MAINTENANCE_MODE` | メンテナンス中 | 完了を待つ |

---

### 5.3 バリデーションエラーの例

**リクエスト**:

```http
POST /v1/experiments
Content-Type: application/json

{
  "experiment_name": "",
  "experiment_type": "invalid_type"
}
```

**レスポンス** (422 Unprocessable Entity):

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "experiment_name",
        "message": "Field cannot be empty",
        "code": "required"
      },
      {
        "field": "experiment_type",
        "message": "Value must be one of: training, testing, production, development",
        "code": "invalid_choice"
      }
    ],
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-11-03T10:30:00Z",
    "path": "/v1/experiments",
    "method": "POST"
  }
}
```

---

## 6. レート制限

### 6.1 レート制限の種類

| 制限タイプ | デフォルト制限 | 説明 |
|----------|--------------|------|
| **ユーザー別** | 1,000 req/hour | ユーザーごとの制限 |
| **APIキー別** | 5,000 req/hour | APIキーごとの制限 |
| **IP別** | 10,000 req/hour | IPアドレスごとの制限 |
| **エンドポイント別** | 可変 | エンドポイントごとの制限 |

---

### 6.2 エンドポイント別制限

| エンドポイント | 制限 | ウィンドウ |
|--------------|------|----------|
| `POST /v1/predictions` | 100 req | 1 minute |
| `POST /v1/experiments` | 50 req | 1 minute |
| `POST /v1/runs` | 100 req | 1 minute |
| `GET /v1/*` | 1,000 req | 1 hour |
| `POST /v1/artifacts` | 20 req | 1 minute |

---

### 6.3 レート制限ヘッダー

**リクエスト成功時**:

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1699000000
X-RateLimit-Window: 3600
```

**レート制限超過時**:

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1699000000
Retry-After: 300

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later.",
    "retry_after": 300,
    "limit": 1000,
    "window": 3600
  }
}
```

---

### 6.4 レート制限の回避策

1. **バッチ処理**: 複数のリクエストを1つにまとめる
2. **キャッシング**: クライアント側でレスポンスをキャッシュ
3. **Webhooks**: ポーリングの代わりにWebhooksを使用
4. **エクスポート機能**: 大量データは一括エクスポート
5. **プラン変更**: より高い制限のプランに変更

---

## 7. セキュリティ

### 7.1 セキュリティベストプラクティス

#### 7.1.1 HTTPS必須

```
すべてのAPIリクエストはHTTPS経由で行う必要があります。
HTTPリクエストは自動的にHTTPSにリダイレクトされます。
```

---

#### 7.1.2 トークン管理

```python
# 良い例: 環境変数で管理
import os
api_token = os.getenv('API_TOKEN')

# 悪い例: ハードコード
api_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'  # ❌
```

---

#### 7.1.3 トークンの有効期限

| トークンタイプ | 有効期限 | リフレッシュ |
|--------------|---------|------------|
| **アクセストークン** | 1時間 | リフレッシュトークンで更新 |
| **リフレッシュトークン** | 30日 | 新規ログインが必要 |
| **APIキー** | 無期限 | ユーザーが手動でローテーション |

---

### 7.2 CORS設定

```yaml
CORS:
  allowed_origins:
    - "https://app.example.com"
    - "https://dashboard.example.com"
  allowed_methods:
    - GET
    - POST
    - PUT
    - PATCH
    - DELETE
  allowed_headers:
    - Authorization
    - Content-Type
    - X-Request-ID
  expose_headers:
    - X-RateLimit-Limit
    - X-RateLimit-Remaining
  max_age: 3600
  allow_credentials: true
```

---

### 7.3 入力検証

すべてのユーザー入力は以下の検証を行います：

1. **型チェック**: データ型の検証
2. **範囲チェック**: 数値の範囲、文字列の長さ
3. **フォーマットチェック**: メールアドレス、URL、日付
4. **SQLインジェクション対策**: パラメータ化クエリ使用
5. **XSS対策**: HTMLエスケープ
6. **ファイルアップロード検証**: MIMEタイプ、ファイルサイズ

---

## 8. ベストプラクティス

### 8.1 クライアント実装

#### 8.1.1 Python例

```python
import requests
from typing import Optional, Dict, Any

class TimeSeriesForecastAPI:
    """Time Series Forecast API Client"""
    
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def create_experiment(
        self,
        name: str,
        description: Optional[str] = None,
        experiment_type: str = 'training',
        tags: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new experiment"""
        endpoint = f"{self.base_url}/v1/experiments"
        payload = {
            'experiment_name': name,
            'experiment_description': description,
            'experiment_type': experiment_type,
            'tags': tags or {}
        }
        response = self.session.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_experiment(self, experiment_id: int) -> Dict[str, Any]:
        """Get experiment details"""
        endpoint = f"{self.base_url}/v1/experiments/{experiment_id}"
        response = self.session.get(endpoint)
        response.raise_for_status()
        return response.json()
    
    def list_experiments(
        self,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """List experiments with pagination"""
        endpoint = f"{self.base_url}/v1/experiments"
        params = {
            'page': page,
            'per_page': per_page
        }
        if status:
            params['status'] = status
        response = self.session.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()

# 使用例
api = TimeSeriesForecastAPI(
    base_url='https://api.example.com',
    api_token='your_api_token_here'
)

# 実験作成
experiment = api.create_experiment(
    name='Sales Forecast Q4',
    description='Forecasting sales for Q4 2025',
    tags={'department': 'sales', 'priority': 'high'}
)
print(f"Created experiment: {experiment['experiment_id']}")

# 実験取得
details = api.get_experiment(experiment['experiment_id'])
print(f"Experiment status: {details['status']}")

# 実験一覧
experiments = api.list_experiments(status='active')
print(f"Total active experiments: {experiments['pagination']['total']}")
```

---

#### 8.1.2 cURL例

**実験作成**:

```bash
curl -X POST https://api.example.com/v1/experiments \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "experiment_name": "Sales Forecast Q4",
    "experiment_description": "Forecasting sales for Q4 2025",
    "experiment_type": "training",
    "tags": {
      "department": "sales",
      "priority": "high"
    }
  }'
```

**実験一覧取得**:

```bash
curl -X GET "https://api.example.com/v1/experiments?status=active&page=1&per_page=20" \
  -H "Authorization: Bearer $API_TOKEN"
```

**予測実行**:

```bash
curl -X POST https://api.example.com/v1/predictions \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": 456,
    "prediction_date": "2025-11-04T00:00:00Z",
    "horizon": 7,
    "input_data": {
      "unique_id": ["series_001"],
      "ds": ["2025-11-03"],
      "y": [2500.0]
    }
  }'
```

---

### 8.2 エラーハンドリング

```python
import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout

def safe_api_call(func):
    """APIコールのエラーハンドリングデコレータ"""
    def wrapper(*args, **kwargs):
        try:
            response = func(*args, **kwargs)
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            if e.response.status_code == 401:
                print("認証エラー: トークンを確認してください")
            elif e.response.status_code == 404:
                print("リソースが見つかりません")
            elif e.response.status_code == 429:
                retry_after = e.response.headers.get('Retry-After', 60)
                print(f"レート制限超過: {retry_after}秒後に再試行")
            else:
                error_data = e.response.json()
                print(f"エラー: {error_data['error']['message']}")
            raise
        except ConnectionError:
            print("接続エラー: ネットワークを確認してください")
            raise
        except Timeout:
            print("タイムアウト: リクエストに時間がかかりすぎています")
            raise
    return wrapper
```

---

### 8.3 リトライロジック

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
import requests

@retry(
    retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def api_call_with_retry(url: str, **kwargs):
    """リトライ機能付きAPIコール"""
    response = requests.get(url, **kwargs)
    response.raise_for_status()
    return response.json()
```

---

## 9. 付録

### 9.1 OpenAPI仕様

完全なOpenAPI 3.1.0仕様は以下のURLで確認できます：

```
https://api.example.com/v1/openapi.json
https://api.example.com/v1/docs  # Swagger UI
https://api.example.com/v1/redoc # ReDoc
```

---

### 9.2 SDKとライブラリ

| 言語 | ライブラリ | インストール |
|-----|----------|------------|
| **Python** | `ts-forecast-sdk` | `pip install ts-forecast-sdk` |
| **JavaScript** | `@ts-forecast/client` | `npm install @ts-forecast/client` |
| **R** | `tsforecast` | `install.packages("tsforecast")` |
| **Go** | `github.com/example/ts-forecast-go` | `go get github.com/example/ts-forecast-go` |

---

### 9.3 Webhook

#### 9.3.1 Webhook設定

```http
POST /v1/webhooks
```

**リクエストボディ**:

```json
{
  "url": "https://your-app.com/webhooks/ts-forecast",
  "events": [
    "experiment.created",
    "run.completed",
    "run.failed",
    "model.deployed",
    "prediction.completed"
  ],
  "secret": "your_webhook_secret",
  "active": true
}
```

---

#### 9.3.2 Webhookペイロード例

```json
{
  "event": "run.completed",
  "timestamp": "2025-11-03T10:45:23Z",
  "data": {
    "run_id": 789,
    "experiment_id": 123,
    "status": "completed",
    "execution_duration_seconds": 2723.456,
    "model_id": 456,
    "metrics": {
      "validation_mae": 123.45
    }
  },
  "signature": "sha256=abcdef123456..."
}
```

---

### 9.4 変更履歴

| 日付 | バージョン | 変更内容 |
|-----|-----------|---------|
| 2025-11-03 | v1.0.0 | 初版リリース |

---

### 9.5 サポート

- **ドキュメント**: https://docs.example.com
- **APIステータス**: https://status.example.com
- **サポートチケット**: support@example.com
- **コミュニティフォーラム**: https://forum.example.com

---

**End of Document**
