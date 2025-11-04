# システム機能の分析

**User:** Anonymous (tajimaharu98@gmail.com)  
**Created:** 11/4/2025 9:12:52  
**Updated:** 11/4/2025 12:19:46  
**Exported:** 11/4/2025 12:23:06  
**Link:** [https://chatgpt.com/g/g-p-6909441263f08191999c3ae3253571dc/c/69094500-60b8-8324-b66e-1aef29c431ad](https://chatgpt.com/g/g-p-6909441263f08191999c3ae3253571dc/c/69094500-60b8-8324-b66e-1aef29c431ad)  

## Prompt:
あなたは優秀なリードエンジニアです
アップロードした資料をすべて網羅的かつ全体的かつ、総合的かつ、俯瞰的かつミクロかつマクロの視点で詳細かつ具体的かつ丁寧に分析、解析、精読、熟読、考察、推測して論理的に完全かつ完璧に理解してシステム全体についてどのような機能があるかをわかりやすく教えてください。

思考時間: 24s

## Response:
システム全体の“地図”と“虫眼鏡”：何ができる・どう動く
============================

まず結論：このシステムは\*\*「時系列予測の実験〜本番運用」までを一気通貫で自動化・可視化する統合基盤**です。データ取り込み→特徴量→学習・探索→評価→分析→モデル登録→予測配信→監視・運用、という流れを**9層のクリーンアーキテクチャ**と**堅牢なDB/API/Runbook\*\*で支えます。現バージョンはローカル／単一ユーザー運用を主想定（将来拡張で認証等を追加）です。01\_REQUIREMENTS\_SPECIFICATION\_D…

* * *

1) できること（機能カテゴリの俯瞰）
-------------------

*   **データ〜特徴量**：CSV等からの正規化・検証、ラグ・移動平均・季節等の特徴量生成、外生変数対応（futr/hist/stat\_exog）。01\_REQUIREMENTS\_SPECIFICATION\_D…
*   **自動モデル探索**：NeuralForecast系のAuto\*（AutoNHITS/LSTM/GRU/TCN…）を共通Adapterで横断、Optuna/Rayでハイパラ最適化、並列実行・重複スキップ（Fingerprint）。01\_REQUIREMENTS\_SPECIFICATION\_D…
*   **評価と分析**：MAE/RMSE/sMAPE/MASE/MAPEの指標、ロールング型バックテスト、相関・因果（Granger）・寄与度（Permutation Importance）。01\_REQUIREMENTS\_SPECIFICATION\_D…
*   **実験・アーティファクト管理**：Experiment/Run/Model/Artifact/MetricをPostgreSQLで一元管理、MLflow/W&Bは任意で併用。05\_DATABASE\_DESIGN\_DETAILED
*   **モデルレジストリ**：Staging/Productionなどの**ステージ遷移**とバージョン付与、デプロイ履歴・本番メトリクスの追跡。05\_DATABASE\_DESIGN\_DETAILED
*   **予測提供**：バッチ中心の予測API/CLI、horizon指定・量子化（分位点）出力オプション。01\_REQUIREMENTS\_SPECIFICATION\_D…
*   **監視と運用**：Prometheus/Grafana/Alertmanager、構造化ログ、Jaeger等の可観測性セット、日次・週次Runbook完備。12\_MONITORING\_GUIDE 11\_OPERATIONS\_RUNBOOK
*   **パフォーマンス最適化**：Mixed Precision、バッチ/並列チューニング、キャッシュ戦略、ボトルネック診断。16\_PERFORMANCE\_TUNING
*   **バックアップ/復旧**：DBは日次フル+増分、モデル・実験結果の保持期間と復旧SLA定義。02\_NON\_FUNCTIONAL\_REQUIREMENTS

* * *

2) 9層アーキテクチャ（骨格の理解）
-------------------

**Configuration / Data / Model Discovery / Hyperparameter / Execution Plan / Execution / Artifact / Logging / Application**の9層で責務分離。CLI/REST API/スケジューラ→実行エンジン→Trainer/ Predictor→DB/Storage、という流れを標準化します。詳細クラスはConfiguration基底・PathConfigなどで不変性/検証/シリアライズを提供。00\_INTEGRATED\_DESIGN\_OVERVIEW 04\_CLASS\_DESIGN\_DETAILED

* * *

3) “予測が出るまで”のライフサイクル（ミクロ視点）
---------------------------

1.  **データ登録**：datasetsにメタ情報（期間・頻度・schema・品質統計等）を保存。05\_DATABASE\_DESIGN\_DETAILED
2.  **実験セットアップ**：experiments作成→複数**runs**がぶら下がる。Fingerprintで条件の完全一致はスキップ。05\_DATABASE\_DESIGN\_DETAILED
3.  **学習と評価**：各runが**models**と**metrics**を生成し、学習時間/サイズ/設定も保存。05\_DATABASE\_DESIGN\_DETAILED
4.  **レジストリ登録**：性能が良いモデルを**model\_registry**へ登録し、staging→productionへ遷移。デプロイ先/本番KPIも記録。05\_DATABASE\_DESIGN\_DETAILED
5.  **予測**：/predictにデータ＋horizonをPOST→predictionsへ永続化（四半期パーティションで高速）。01\_REQUIREMENTS\_SPECIFICATION\_D… 05\_DATABASE\_DESIGN\_DETAILED

* * *

4) APIの顔つき（使い方の入口）
------------------

*   代表例：`POST /api/v1/predict`（model\_name, horizon, data, return\_quantiles）— 予測とメタデータを返す。**現状はローカル想定で認証不要**（将来JWT/OAuth2対応設計は用意）。01\_REQUIREMENTS\_SPECIFICATION\_D… 06\_API\_DESIGN\_DETAILED
*   実験/Run/モデル/データセット/指標/アーティファクト用のCRUDが揃い、ページングや高度フィルタが標準。06\_API\_DESIGN\_DETAILED

* * *

5) データベース（裏方の全容）
----------------

**15のコアテーブル**で実験〜予測の全履歴とメタデータを保持。JSONB＋GINや部分/複合Indexで柔軟かつ高速。predictionsは**日付レンジのパーティショニング**で大規模にも耐える構成です。05\_DATABASE\_DESIGN\_DETAILED 05\_DATABASE\_DESIGN\_DETAILED 05\_DATABASE\_DESIGN\_DETAILED

* * *

6) 非機能要件（走りの良さと安全性）
-------------------

*   **性能**：単一モデル学習<10分、100モデル並列<2時間、予測レイテンシ<100ms等を目標に計測・ゲート化。16\_PERFORMANCE\_TUNING 13\_PROJECT\_SCHEDULE
*   **スケーラビリティ/拡張**：最大並列32、最大GPU4、シリーズ1万・時系列長10万までの規模要件を明示。01\_REQUIREMENTS\_SPECIFICATION\_D…
*   **可用性**：SLO（稼働率/MTTR等）、エラー時リトライ、HealthチェックをRunbookに標準化。11\_OPERATIONS\_RUNBOOK
*   **セキュリティ**：現状ローカルは認証不要、APIは将来JWT/OAuth2を段階導入。秘密情報は環境変数で管理。01\_REQUIREMENTS\_SPECIFICATION\_D… 02\_NON\_FUNCTIONAL\_REQUIREMENTS
*   **バックアップ/復旧**：DB日次、モデル/ログ/実験の保持方針＋復旧演習（DB<30分、全体<2時間）。02\_NON\_FUNCTIONAL\_REQUIREMENTS
*   **リリース前チェックリスト**で性能・監視・セキュリティ・ドキュメントを網羅検証。02\_NON\_FUNCTIONAL\_REQUIREMENTS

* * *

7) 運用・監視・デプロイ（現場が回る仕掛け）
-----------------------

*   **監視**：Metrics/Logs/Tracesの“三本柱”。Prometheus（Exporter群＋アプリメトリクス）、Loki、JaegerをGrafanaで統合。警報はAlertmanager→メール/Slack等。12\_MONITORING\_GUIDE
*   **Runbook**：日次ヘルスチェック、週次DBメンテ、障害時の標準SQL/シェル、スケール手順まで脚本化。11\_OPERATIONS\_RUNBOOK
*   **デプロイ**：ローカル/Docker/将来本番の順で手順を段階化。必要ポート、環境変数、DB初期化、セキュリティ/監視設定も明文化。10\_DEPLOYMENT\_GUIDE
*   **トラブルシュート**：ログの読み方、pdb、GPU/メモリ/IOの観測コマンド集、FAQ。15\_TROUBLESHOOTING\_GUIDE

* * *

8) 品質保証（テストの設計思想）
-----------------

**テストピラミッド**でUT 80% / IT 15% / E2E 5%を目安に、カバレッジ>90%と品質ゲートで継続的テストをCI/CDに組み込み。TDD/静的解析/リスクベースの観点もガイド化。09\_TESTING\_STRATEGY

* * *

9) スコープと現時点の制約（現実に根ざす注意点）
-------------------------

*   **スコープ内**：9層アーキテクチャ、実験〜予測〜監視までの土台は実装対象。
*   **スコープ外/将来**：本番クラウド運用、厳密な認証/認可、マルチテナントは将来拡張。スケジュールも段階導入で定義済み。13\_PROJECT\_SCHEDULE

* * *

10) 「どう使い始める？」短い道案内
-------------------

1.  **データ登録**→**実験作成/実行**（並列探索）→**最良モデルをレジストリ昇格**→**/predictで配信**。
2.  **監視ダッシュボード**と**Runbook**で運用をルーチン化、**バックアップ/復旧**で安全網を用意。06\_API\_DESIGN\_DETAILED 11\_OPERATIONS\_RUNBOOK 02\_NON\_FUNCTIONAL\_REQUIREMENTS

* * *

### ひとことで要約

**「予測精度を上げる実験サイクル」と**「それを壊れず運ぶ運用サイクル」を、**DB・API・レジストリ・監視**まで含めて\*\*一枚岩にした“時系列MLOps”\*\*です。次の一歩は、**既存データで実験を1本走らせて、レジストリに載せ、/predictで返す**までを通しで体験すること。そこから最適化（性能/コスト/運用負荷）を回していくのがこのシステムの想定する幸福ループです。01\_REQUIREMENTS\_SPECIFICATION\_D…

## Prompt:
5) データベース（裏方の全容）についてDB,テーブル、ERなどどのような情報がどのように登録されるかについて具体的に教えてください。

思考時間: 46s

## Response:
データベース全体像（裏方のフルマップ）
===================

この時系列予測システムは **PostgreSQL** を採用し、既定のDB名は `ts_forecast_system`。用途別に **public / audit / staging / archive** の4スキーマで構成します。接続は `DATABASE_URL`（例: `postgresql://…/ts_forecast_system`）、運用はSQLAlchemyのQueuePoolでプール・タイムアウト・リサイクルを制御します。権限はアプリ用ユーザー `app_user` に付与し、将来作成テーブルへのデフォルト権限も設定します。DATABASE\_AND\_TOOLS\_CONFIGURATION

* * *

ER関係（何がどう繋がるか）
--------------

中核は **Experiment（実験）→ Run（実行）→ Model（学習成果）** の系譜で、付帯する **Dataset / Metrics / Artifacts / Predictions** などが周辺にぶら下がる構造です。ER図の主な関連は次の通りです（要点のみ）：

*   `experiments 1—N runs`
*   `runs 1—N models / metrics / artifacts / predictions`
*   `models 1—1 model_registry`（登録・段階管理）
*   `datasets 1—N runs`（「このデータでこのRunを回した」）、`datasets 1—N data_slices / quality_reports`
*   解析系（相関、Granger、特徴重要度など）は `runs` と 1—N。  
    この全体像はER図ドキュメントに整理されています。ER\_AND\_CLASS\_DIAGRAMS

* * *

主要テーブルと「どの情報がどう登録されるか」
----------------------

以下、**用途 / 主キー / 代表カラム / いつ・どう登録されるか** の順で要点をまとめます。

### 1) experiments（実験の器）

*   **用途**: 実験の単位（プロジェクト/テーマ）
*   **PK**: `experiment_id`
*   **代表**: `experiment_name, experiment_description, experiment_type, status, lifecycle_stage, tags(jsonb), metadata(jsonb), created_at`
*   **登録タイミング**: 新規プロジェクト開始時やAPI/CLIから実験を作成した瞬間に1行。名前や説明、タグで分類し、後続のRunを格納する入れ物になります。05\_DATABASE\_DESIGN\_DETAILED

### 2) runs（個別実行の履歴）

*   **用途**: 各学習/評価/予測ジョブの1回分の実行ログ
*   **PK**: `run_id`（`run_uuid`は一意制約）
*   **代表**: `experiment_id(FK), run_name, run_fingerprint(重複防止用ハッシュ), status(running/completed/failed…), start_time, end_time, execution_duration_seconds, tags, metadata`
*   **登録タイミング**: 学習や評価を**開始した瞬間に1行INSERT**。開始時は `status='running'`、終了時に `status` と `end_time/実行秒` を更新します。`run_fingerprint` で同条件の二重実行を防止するユニーク制約・インデックス設計が入っています。05\_DATABASE\_DESIGN\_DETAILED

### 3) datasets / dataset\_features（データ資産のカタログ）

*   **用途**: 学習・予測に使うファイルやスキーマのメタ情報
*   **PK**: `dataset_id`
*   **代表**: `dataset_name, dataset_type, file_path, file_format, schema_definition(jsonb), column_types(jsonb), num_rows/num_time_series, start_date/end_date, tags, metadata`／付随の `dataset_features(feature_name, feature_type, feature_role, is_target/is_exogenous)`
*   **登録タイミング**: データ投入時に1行。CSV/Parquet等の場所や`unique_id, ds, y`標準化後の列情報、外生変数（`futr_* / hist_* / stat_*`）の識別結果などをメタとして残します。以後、Run側から「どのデータで回したか」を参照できます。05\_DATABASE\_DESIGN\_DETAILED

### 4) models（学習済みモデルの実体）

*   **用途**: Runで生成された学習済みモデルの記録
*   **PK**: `model_id`（`model_uuid`一意）
*   **代表**: `run_id(FK), model_name, model_type, framework/versions, model_config(jsonb), hyperparameters(jsonb), training_duration_seconds, model_size_bytes, model_file_path, checkpoint_path, status`
*   **登録タイミング**: 学習完了時に1行。モデルファイルの保存先やサイズ、ハイパーパラメータ、学習時間などを格納します。05\_DATABASE\_DESIGN\_DETAILED

### 5) model\_registry（登録・段階管理）

*   **用途**: モデルの\*\*登録名・バージョン・ステージ（Staging/Production/Archived）\*\*を一元管理
*   **PK**: `registry_id`
*   **代表**: `model_id(FK), registered_model_name, model_version, current_stage, deployed_at, production_metrics(jsonb), tags, metadata`
*   **登録タイミング**: モデルをレジストリに載せると1行。状態遷移（Training→Registered→Staging→Production→Archived）は図でも明示されています。05\_DATABASE\_DESIGN\_DETAILED ER\_AND\_CLASS\_DIAGRAMS

### 6) metrics（指標ログ）

*   **用途**: 学習・評価中に記録する指標（例：loss/MAE/MAPE）
*   **PK**: `metric_id`
*   **代表**: `run_id(FK), model_id(FK), metric_name, metric_value, step/epoch, dataset_type(train/valid/test), timestamp`
*   **登録タイミング**: 学習ループ中に**逐次INSERT**。後の可視化・比較用。大量書き込み前提でインデックスを計画。05\_DATABASE\_DESIGN\_DETAILED

### 7) artifacts（成果物）

*   **用途**: 画像・レポート・プロット・大きなCSVなどファイル成果物のメタ
*   **PK**: `artifact_id`（`artifact_uuid`一意）
*   **代表**: `run_id(FK), artifact_name, artifact_type, artifact_path, artifact_size_bytes, artifact_hash, mime_type, artifact_metadata(jsonb), created_at`
*   **登録タイミング**: 保存したタイミングで1行。モデル以外のすべての「ファイルの証跡」をDBで追跡します。05\_DATABASE\_DESIGN\_DETAILED

### 8) predictions（予測結果）

*   **用途**: 予測の記録。設計上、**2形態をサポート**
    1.  **行明細型**：`unique_id, prediction_date(=ds), horizon, predicted_value` を**パーティショニング**で高スループット保存（親テーブル＋日付パーティション）。**大量配信・検索に強い**。
    2.  **ファイル指向型**：明細はファイルに出力し、DB側は `predictions_file_path/size/hash` 等の**メタだけ**保存。**超大容量**向け。
*   **登録タイミング**: 予測実行後に1)は一括INSERT（COPY等）、2)はファイル配置後にメタINSERT。両案を文書で定義しています。05\_DATABASE\_DESIGN\_DETAILED ER\_AND\_CLASS\_DIAGRAMS

### 9) hyperparameters（探索ログ）

*   **用途**: そのRunで最終的に採用／評価したハイパーパラメータの記録
*   **代表**: `run_id, param_key, param_value, param_type`（Optuna/Rayからの反映も想定）
*   **登録タイミング**: 探索過程または確定時にINSERT。05\_DATABASE\_DESIGN\_DETAILED

> ほか、`feature_importances / correlations / granger_tests / data_slices / quality_reports / resource_stats / run_logs` などの解析・運用系テーブルも `runs` や `datasets` にひもづく形で定義されています。ER\_AND\_CLASS\_DIAGRAMS

* * *

登録フロー（時系列）
----------

### ① データ → Dataset登録

データ投入時に**ファイル位置・行数・期間・列型**などのメタを `datasets` に保存。外生変数は接頭辞（`futr_* / hist_* / stat_*`）で分類され、スキーマ定義/特徴テーブルにも反映されます。19\_FAQ

### ② 実験作成 → Experiment

新規テーマ開始時に `experiments` へ1行。タグ/メタで分割管理。05\_DATABASE\_DESIGN\_DETAILED

### ③ 学習/評価開始 → Run

ジョブ開始で `runs` へINSERT（`status='running'`）。以降、**学習ループ中は `metrics` を逐次挿入**、成果物は `artifacts` に追記。終了時にRun行を更新します（終了時刻・実行秒・最終ステータス）。05\_DATABASE\_DESIGN\_DETAILED

### ④ モデル完成 → Models / Model Registry

学習完了で `models` にモデルの**保存先・サイズ・ハイパラ**を記録。運用へ進める場合は `model_registry` に登録名・バージョン・段階（Staging/Production）を付与します。05\_DATABASE\_DESIGN\_DETAILED ER\_AND\_CLASS\_DIAGRAMS

### ⑤ 予測実行 → Predictions

要求に応じて **行明細型 or ファイル指向型**で `predictions` を登録。行明細型は日付パーティションを切って高スループットに耐える設計です。05\_DATABASE\_DESIGN\_DETAILED

* * *

インデックス・制約・パフォーマンス小ネタ
--------------------

*   **重複防止**: `runs(experiment_id, run_fingerprint)` にユニーク制約（同条件の二重走行を抑止）。05\_DATABASE\_DESIGN\_DETAILED
*   **検索系**: `experiments(experiment_name)`, `runs(experiment_id, status, start_time desc)` など多用カラムにインデックス、タグJSONBは **GIN**。05\_DATABASE\_DESIGN\_DETAILED
*   **大量書き込み**: `predictions` は**パーティショニング**前提でINSERT/検索をスケール。05\_DATABASE\_DESIGN\_DETAILED

* * *

スキーマの運用と初期化
-----------

*   **マイグレーション**: Alembicで `experiments/runs → models/datasets → metrics/predictions(Partition)` と段階的に作成。05\_DATABASE\_DESIGN\_DETAILED
*   **初期化**: `alembic upgrade head` で最新に。環境変数は `.env` にまとめ、接続テスト（`SELECT version()`）やPool設定も手順化済み。10\_DEPLOYMENT\_GUIDE

* * *

こんな感じが「裏方の全容」です。次は**特定フローの実データ例**（例：_「予測APIを叩いた1件が、runs/metrics/predictionsにどう落ちるか」_）まで紐づけて図解できます。必要ならそのケースで掘り下げます。

## Prompt:
処理過程のリソース状況の情報もテーブルを作成して保存する要件でしたが、資料には記載ありませんか？

## Response:
思考時間: 1m 13s

あります。資料では ER 図に **`resource_stats` テーブル**として明示されており、各 `run`（実行）にひもづく形で CPU/メモリ/GPU/ディスク I/O を時系列で保存する前提です。主なカラムは下記の通りです（`run_id` 外部キー、`recorded_at` 計測時刻、使用率やバイト数など）。ER\_AND\_CLASS\_DIAGRAMS

*   `stat_id`（PK）, `run_id`（FK to runs）, `recorded_at`
*   `cpu_percent`, `memory_used_bytes`, `memory_total_bytes`
*   `gpu_utilization`, `gpu_memory_used_bytes`, `gpu_memory_total_bytes`
*   `disk_io_read_mb`, `disk_io_write_mb`, `resource_metadata`（JSONB） ER\_AND\_CLASS\_DIAGRAMS

ER 図上の関連も `runs ||--o{ resource_stats : "monitors"` と定義されており、**1 Run に複数のリソース計測レコード**が紐づく設計です。ER\_AND\_CLASS\_DIAGRAMS

一方で、**DB 詳細設計（DDL 集）には `resource_stats` の CREATE 文は掲載されていません**（同章にはログ・監査テーブルやパーティショニング方針、`system_logs` の月次パーティション作成例などはありますが、`resource_stats` の DDL は未収載）。運用整理パートではログ系（`system_logs`, `audit_logs`）の存在とパーティション戦略が示されます。

また、**監視系は Prometheus/Grafana を併用**し、CPU・メモリ・ディスク I/O・ネットワーク・GPU の Gauge/Counter をサンプリングするコードが提示されています。これはストリーミング監視の土台で、`resource_stats` に保存するスナップショットとは補完関係です（Prometheus で常時監視、DB に Run 文脈で永続化）。12\_MONITORING\_GUIDE

* * *

### ドキュメントに沿った結論

*   **要件としては存在**：`resource_stats` を DB に持ち、処理過程のリソース状況を保存する。
*   **実装詳細（DDL）は不足**：DDL は ER 文書に相当する仕様のみで、DB 詳細設計には未掲載。05\_DATABASE\_DESIGN\_DETAILED
*   **監視の取得経路は提示済み**：Prometheus 収集→ダッシュボード／アラート、必要に応じて Run 単位で DB 永続化。12\_MONITORING\_GUIDE

* * *

### すぐ埋められる実装ギャップ（提案）

ドキュメントの ER 仕様に忠実な最小 DDL 例（提案）：

```sql
CREATE TABLE resource_stats (
  stat_id BIGSERIAL PRIMARY KEY,
  run_id BIGINT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
  recorded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  cpu_percent DOUBLE PRECISION,
  memory_used_bytes BIGINT,
  memory_total_bytes BIGINT,
  gpu_utilization DOUBLE PRECISION,
  gpu_memory_used_bytes BIGINT,
  gpu_memory_total_bytes BIGINT,
  disk_io_read_mb DOUBLE PRECISION,
  disk_io_write_mb DOUBLE PRECISION,
  resource_metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX idx_resource_stats_run_time ON resource_stats(run_id, recorded_at DESC);
```

運用は Prometheus 収集間隔（例: 15–60 秒）に合わせ、**Run 開始〜終了の間だけ**サンプルを `resource_stats` に挿入するのが実務的です。Prometheus のメトリクス名（CPU/メモリ/GPU/ディスク I/O）は上のカラムに素直にマッピングできます。12\_MONITORING\_GUIDE

必要なら、`system_logs` と同様に **月次パーティション**（`PARTITION BY RANGE (recorded_at)`）を切ると肥大化に強くなります。05\_DATABASE\_DESIGN\_DETAILED

* * *

さらに詰めたい観点：サンプリング間隔・保存期間、ピークのみ保存か全件保存か、GPU 非搭載時の欠損扱い、Prometheus→DB ブリッジ（Exporter 直書きかアプリ側書き込みか）。ここを決めると運用の手触りがぐっと良くなります。

## Prompt:
UI,UX関連の設計や運用方法を教えてください

## Response:
思考時間: 42s

UI/UX の設計と運用（要点だけ速射）
====================

どんな UI があるか（面の整理）
-----------------

*   **Web UI（運用ダッシュボード）**：Streamlit/Dash 前提。ダッシュボード／実験一覧・詳細／モデル比較／予測実行／再学習設定／レジストリ／リソース監視の画面を持つ情報設計です。Web UI は FastAPI を叩いてデータを取得します。
*   **API ドキュメント UI**：Swagger UI / ReDoc を公開（OpenAPI 3.1）。開発者向けの“使う UI”。06\_API\_DESIGN\_DETAILED
*   **CLI UI**：進捗バー（tqdm/rich）、実行サマリ、エラー表示のふるまいがシーケンス図と非機能要件で規定済み。
*   **運用系 UI**：Grafana（メトリクス/ログ/トレースを集約）、Alertmanager（通知 UI）、MLflow UI・Ray Dashboard も併用可能。Compose で起動ポートや依存関係を定義済み。

* * *

UX 要件（体感品質の約束）
--------------

*   **画面遷移 < 1 秒、グラフ描画 < 2 秒、エラーは人間語で**。CLI はタブ補完・進捗表示が標準。02\_NON\_FUNCTIONAL\_REQUIREMENTS
*   **SLO/可用性の期待値**は運用手順書に明記（例：月間稼働率、API 成功率、予測 p95 レイテンシ等）。11\_OPERATIONS\_RUNBOOK

* * *

情報設計と主要フロー（Web UI）
------------------

*   **情報アーキテクチャ**：  
    ダッシュボード（全体状況）→ 実験一覧 → 実験詳細（パラメータ・メトリクス・ログ・グラフ）／モデル比較 → 予測実行（データ投入→モデル選択→実行）→ レジストリ（Staging→Production）→ 再学習設定（スケジュール/トリガ）。01\_REQUIREMENTS\_SPECIFICATION\_D…
*   **API 連携**：Web UI は FastAPI のエンドポイントを叩く。OpenAPI/Swagger UI で I/F が見える化。将来の OAuth2（スコープ定義と認可コードフロー）も設計に含まれます。
*   **CLI 連携の体験**：シーケンス図どおり、進捗バー更新→タスク/エポックごとのメトリクス→完了サマリ（成功/失敗/合計時間）。Web UI と同じ“語彙”で結果が解釈できるよう統一。SEQUENCE\_DIAGRAMS\_DETAILED

* * *

運用 UI/UX（見る・守るの設計）
------------------

*   **Grafana ダッシュボード**：System Overview（QPS/5xx/Error Rate/Active Runs/メモリ等）を JSON で定義。パネルとクエリの雛形まで載っています。10\_DEPLOYMENT\_GUIDE
*   **監視スタック**：Prometheus（メトリクス）、Loki+Promtail（ログ）、Jaeger（トレース）→ Grafana で統一表示。データソース/保持期間/ジョブ設定が具体化済み。
*   **アラート UX**：メール/Slack テンプレートに「関連ダッシュボードへのリンク」「推奨アクション」を埋め込み、通知から 1 クリックで可視化に飛べる導線。12\_MONITORING\_GUIDE
*   **ヘルスチェックと運用確認**：`/health` や各 UI のスタタスを curl で確認する運用コマンドを提供（Postgres、API、MLflow、Ray）。10\_DEPLOYMENT\_GUIDE
*   **オンコール運用の UX**：チェックリスト・初動スクリプト・インシデントテンプレートが整備され、通知→ダッシュボード→Runbook の遷移が定型化。

* * *

ユーザー管理とパーソナライズ
--------------

*   **ユーザー/権限**：`users` と `user_experiments` でアクセス権（read/write/admin/owner）を管理。`users.preferences` に UI/通知設定などを保存できる前提。UI 側はここを読み書きして体験を個別最適化。05\_DATABASE\_DESIGN\_DETAILED

* * *

品質保証（UI のテスト運用）
---------------

*   **E2E（ブラウザ）**：Selenium による Web UI の自動テスト例あり（モデル選択→実行→成功メッセージ→メトリクス/グラフ表示まで検証）。09\_TESTING\_STRATEGY
*   **性能検証**：API 応答 < 1s を含むパフォーマンス項目を試験観点として明文化。09\_TESTING\_STRATEGY

* * *

デプロイ/構成のポイント（UI を壊さない）
----------------------

*   **Compose 構成**：Grafana/Prometheus/Alertmanager を `profiles: [monitoring]` で起動、ポートは 3000/9090/9093 など標準化。ダッシュボード/データソースは自動プロビジョニング。10\_DEPLOYMENT\_GUIDE
*   **ログ体験の安定化**：構造化ログとログローテーションを既定化（UI 側エラーの追跡を安定させるため）。10\_DEPLOYMENT\_GUIDE

* * *

ここまでで見えている“運用としての UX ループ”
-------------------------

1.  **異常検知**（アラート）→ 2) **可視化**（該当ダッシュボードへジャンプ）→ 3) **対処**（Runbook/スクリプトで初動）→ 4) **事後**（Postmortemでナレッジ化）と、一連の体験がテンプレ化されています。

* * *

### 補足：この先やると UX がさらに締まる

*   Web UI のログイン〜権限連携を OAuth2 スコープ設計に揃える（設計は済、実装面は運用環境に合わせて仕上げ）。06\_API\_DESIGN\_DETAILED
*   `users.preferences` を UI から設定・保存（ダークモード、既定期間、メトリクス既定表示など）に活用。05\_DATABASE\_DESIGN\_DETAILED

必要なら、「各画面のワイヤーフレーム案」か「Grafana の最小ダッシュボード JSON（System/Model/DB の3枚セット）」まで即時に落とし込みます。

## Prompt:
システム運用やユーザー操作マニュアルを具体的なケースを例として示しながら時系列順、イベント順にわかりやすく教えてください。

## Response:
思考時間: 39s

システム運用 & ユーザー操作マニュアル（ケース別・時系列）
==============================

「実際にどう動かすか」「運用でどこを見るか」を、**具体的なケース**で時系列にまとめました。各ケースは、コマンド／API／UIで“何をする→どこを確認→次に何をする”の順で進みます。引用は該当ドキュメントの根拠です。

* * *

0) 事前の“地図”：役割と要件の把握
-------------------

*   役割と責任（PO/DS/MLE/SRE/Ops）と、目的（高精度・再現性・効率・分析・拡張性）を頭に入れておくと全体の導線がスムーズ。
*   ハード/ソフト要件（CPU/メモリ/GPU/OS、Python3.11+/PostgreSQL14+ 等）を満たす。
*   非機能要件（SLO、エラーハンドリング、リトライ、監視・バックアップ・文書）を“出荷基準”として意識。02\_NON\_FUNCTIONAL\_REQUIREMENTS

* * *

ケースA：初回導入 → 動作確認（ローカル or Docker）
--------------------------------

### A-1. 取得とセットアップ（ローカル／Docker共通の前提）

1.  リポジトリを取得、仮想環境を用意し依存を入れる。10\_DEPLOYMENT\_GUIDE
2.  必要ポート（DB 5432 / API 8000 / MLflow 5000 / Ray 8265 / Prometheus 9090 / Grafana 3000）を開ける。10\_DEPLOYMENT\_GUIDE
3.  `.env` を作り、`DATABASE_URL` 等を設定。07\_IMPLEMENTATION\_GUIDE

### A-2. 最短導線（Quick Start）

1.  `nf-auto-runner` を入れて `nf-runner --version`。
2.  `.env` に最低限のパスと DB 接続を書く。
3.  サンプルデータで学習→予測まで 5〜30 分で通す。18\_QUICKSTART

### A-3. DB 初期化と種データ

*   Postgres を起動 → DB 作成 → Alembic マイグレーション → 初期データ投入。07\_IMPLEMENTATION\_GUIDE

### A-4. 正常性の確認（観測も同時に）

*   Grafana / Prometheus / Alertmanager を立ち上げ、ダッシュボード・アラートルールが読める状態に。10\_DEPLOYMENT\_GUIDE
*   “日次監視チェックリスト”を使い、CPU/メモリ/ディスク、DB接続数、バックアップ結果を目視確認。12\_MONITORING\_GUIDE

* * *

ケースB：データ投入 → 実験 → 学習 → モデル登録 → 予測（基本フロー）
----------------------------------------

> “作る→走らせる→評価→登録→使う”の王道フロー

### B-1. 実験の作成（API）

*   `POST /v1/experiments` で作成。OAuth2 スコープや共通ヘッダ、ページネーション・エラー形式は API 仕様に準拠。

### B-2. Run の作成と学習（CLI or API）

*   CLI 最短例：  
    `nf-runner train --data ./data/data_with_exog.csv --models AutoNHITS --h 7`。学習の E2E テスト観点はテスト戦略に準拠。
*   API で `POST /v1/runs` → `GET /v1/runs/{id}` で進捗/結果を取得。06\_API\_DESIGN\_DETAILED
*   実行の内部シーケンス（設定→読込→前処理→計画→実行→評価→保存）は設計図に明示。C4\_ARCHITECTURE\_DIAGRAMS

### B-3. モデル登録・昇格（レジストリ）

*   学習結果はメタ/メトリクスとともに保存され、登録 API で “staging→production” にデプロイ可。レスポンス例やデプロイ要求は API 仕様に記載。06\_API\_DESIGN\_DETAILED

### B-4. 予測を実行（API / ランナー）

*   `POST /predict`（単発）と `/predict/batch`（バッチ）の I/F とサンプルが要件書にある。01\_REQUIREMENTS\_SPECIFICATION\_D…
*   Python ランナーで既存モデルを読み予測するコード例（外生変数含む）はクイックスタートに掲載。18\_QUICKSTART

### B-5. 失敗時の基本トリアージ

*   標準エラーコード表とバリデーション例で、`422`/`401`/`429`/`500` など“まず何を見るか”が明確。

* * *

ケースC：定期バッチ予測＆自動再学習（運用化）
-----------------------

1.  **スクリプト化**：`scripts/batch_predict.py`（ドリフト検知→必要なら再学習→予測→成果物保存）。18\_QUICKSTART
2.  **スケジュール**：`cron` で午前2時に実行し、`logs/batch.log` へ。18\_QUICKSTART
3.  **監視**：実行数/成功率/予測レイテンシ/エラー率をダッシュボードでトレンド管理。アラートは Prometheus ルールに沿う。10\_DEPLOYMENT\_GUIDE

* * *

ケースD：日々の運用監視 → アラート対応 → 収束
--------------------------

### D-1. 日次・週次・月次の“見るところ”

*   チェックリスト（稼働・アラート・ログ・リソース・DB・バックアップ・KPI）を習慣化。週次はトレンド分析。12\_MONITORING\_GUIDE
*   監視の“3本柱”（メトリクス・ログ・トレース）と、可観測性→信頼性→予防の視点。12\_MONITORING\_GUIDE

### D-2. アラートが鳴ったら（初動テンプレ）

*   5分以内にACK、初期診断、ログ確認、P0/P1はインシデント起票。スクリプト雛形あり。11\_OPERATIONS\_RUNBOOK
*   エスカレーション基準・連絡先・フロー図は Runbook に定義済み。11\_OPERATIONS\_RUNBOOK
*   代表的インシデントのタイムライン記載例（原因：DB接続枯渇→再起動）も参照。11\_OPERATIONS\_RUNBOOK

### D-3. 観測スタック（起動と配線）

*   Prometheus/Grafana/Alertmanager のデータソース、ダッシュボード雛形、代表アラート（エラー率・メモリ・接続プール枯渇）。10\_DEPLOYMENT\_GUIDE
*   エクスポーター側の実装（psutil 系コレクタの起動例）と可視化/保持。

* * *

ケースE：バックアップ & 復旧演習（DR含む）
------------------------

### E-1. 戦略と指標（RPO/RTO）

*   ポリシー（RPO=1h、RTO=4h、保持・暗号化・保存先）。改善策も表で明確。
*   RPO/RTO の計算ガイドと改善例。17\_BACKUP\_RECOVERY

### E-2. バックアップの実装対象とスクリプト

*   DB/モデル/設定/ログ/実験成果物が対象。スクリプト例（DB/WAL、モデル、設定の暗号化バックアップ）を参照。

### E-3. 復旧シナリオと手順

*   フル→PITR（時点復旧）などのシナリオに沿って段取り。ランサムウェア時の隔離→クリーン復旧→スキャン→パッチの実行例付き。

### E-4. “バックアップは戻してナンボ”

*   **定期リストアテスト**の手順（チェックサム→pg\_restore→検証ログ）。17\_BACKUP\_RECOVERY

* * *

ケースF：性能・スケール運用（詰まりを避ける実践）
-------------------------

*   スケール目標（実験数/Run数/並列度/GPU 数、負荷シナリオ）を定義し、負荷テストで裏取り。02\_NON\_FUNCTIONAL\_REQUIREMENTS
*   ハード/並列・GPU・データサイズの上限や推奨構成は要件で明示。
*   パフォーマンス/安定性の SLO とゴールデンシグナル（Latency/Traffic/Errors/Saturation）で“何が悪いか”を早く掴む。

* * *

ケースG：トラブルシューティング（症状別 → 原因 → 対処）
-------------------------------

### G-1. 代表的なエラー早見表

*   データ不備（列欠損/型/欠損値）、モデル未検出、学習失敗、メモリ不足、ディスク不足、並列実行エラーなどの対処が一覧化。15\_TROUBLESHOOTING\_GUIDE
*   ログの場所・リアルタイム追跡・DEBUG 有効化・pdb の使い方。15\_TROUBLESHOOTING\_GUIDE
*   GPU/IO/ネットワークの観測コマンドチートシート。15\_TROUBLESHOOTING\_GUIDE

### G-2. API 側の切り分け

*   標準エラーコード表とレート制限時のレスポンス、回避策（バッチ/キャッシュ/Webhook 等）。

* * *

ケースH：UI/CLI/API を横断した“使い勝手”統一
-----------------------------

*   Web/CLI で同じ語彙（Experiment/Run/Model/Stage/Registry）と同じ観測項目（進捗・メトリクス・ログ）を見せる方針。E2E テストでは UI 手順（データアップ→モデル選択→実行→グラフ確認）をそのまま自動化。09\_TESTING\_STRATEGY
*   アーキテクチャ全体（App/API/DB/モデル保存/MLflow/Ray/監視）の配置と接続の“地図”で迷子にならない。

* * *

付録：即使える“運用の決めごと”ミニ集
-------------------

*   **オンコール**：ACK ≤5分、初動 ≤15分、進捗更新 30分毎、P0/P1は即エスカレーション。チェックリストと Slack テンプレあり。11\_OPERATIONS\_RUNBOOK
*   **日次点検**：ダッシュボード、アラート、ログ、DB、バックアップ、KPI。12\_MONITORING\_GUIDE
*   **アラート雛形**：5xx エラー率、メモリ閾値、接続プール枯渇。10\_DEPLOYMENT\_GUIDE
*   **出荷チェック**：パフォーマンス/SLA/セキュリティ/監視/運用ドキュメントの“完了条件”。02\_NON\_FUNCTIONAL\_REQUIREMENTS

* * *

### つぎの一歩

この通りに回せば、**学習・予測の定常運転**と**監視→初動→復旧**の運用ループが回ります。必要なら、あなたの環境に合わせた**ダッシュボード JSON**や**cron/backup/restore スクリプト**の雛形を、すぐにあなた用にチューニングしてお渡しします。

## Prompt:
分析関連の処理を具体的に教えてください。

## Response:
思考時間: 37s

分析まわり、どこからどこまで何をする？
===================

要するにこのシステムの「分析」は、**データを理解→時系列のクセを掴む→モデルを評価→なぜ当たる/外れるかを説明→運用しながら劣化を検知**までを一気通貫で回す設計です。ドキュメントに書かれている“できる分析”を、実行順で具体化します。

* * *

1) データ理解（前処理・品質）
----------------

*   **スキーマ/品質チェック**：必須列（`unique_id, ds, y`）、型、欠損、日付連続性、外れ値（IQR/Z-score）を機械的に検証。CLI で `nf-runner data validate / data stats` を用意。
*   **外生変数の扱い**：`futr_* / hist_* / stat_*` の命名規則で役割を自動判別。統計量や期間の整合も併せて点検します。18\_QUICKSTART

* * *

2) 時系列そのものの探索（EDA）
------------------

*   **ラグ相関**：ACF/PACF（自己相関/偏自己相関）と信頼区間を出し、季節性や差分の要否を判断します。戻り値には値と信頼区間が含まれる想定。01\_REQUIREMENTS\_SPECIFICATION\_D…

* * *

3) 因果・介入の分析（“関係がありそう”の内訳）
-------------------------

*   **Granger因果性**：先行系列がターゲット予測に統計的に寄与するかを検定（複数テスト方式、ラグ上限や有意水準を指定）。注意：真の因果を保証するものではありません。01\_REQUIREMENTS\_SPECIFICATION\_D…
*   **介入効果推定**：**DiD（Difference-in-Differences）**や**Synthetic Control**の利用前提とAPIが定義されています。DiD は処置群/対照群・前後比較で処置効果と信頼区間などを返す設計。

* * *

4) 評価（Backtest と指標）
-------------------

*   **Rolling-origin backtest**：時系列交差検証を n 分割・horizon・gap 指定で実行。fold ごとの指標と集計（mean/std/min/max）、必要なら各 fold の予測も返します。01\_REQUIREMENTS\_SPECIFICATION\_D…
*   **評価指標**：MAE/RMSE/sMAPE/MASE/MAPE を標準化。定義・解釈・範囲が表で明記。

* * *

5) モデル解釈・寄与度
------------

*   **Permutation Importance**、**SHAP**、**LIME**、**Feature Ablation**の4本柱で「どの特徴が効いたか」を定量化。SHAP は背景データや評価回数をパラメタに持つ API 例まで定義済み。01\_REQUIREMENTS\_SPECIFICATION\_D…

* * *

6) ハイパーパラメータの分析
---------------

*   **探索そのもの**は Optuna/TPE ほかで最適化ループを実行。結果は「最良パラメータ」「履歴」「重要度」を可視化するアナライザで確認（Param Importances / Optimization History）。

* * *

7) 予測の不確実性
----------

*   量的（分位点）予測に対応。推論パイプラインで\*\*確率予測（quantiles）\*\*を分岐実行→信頼区間を付与して出力します。SEQUENCE\_DIAGRAMS\_DETAILED

* * *

8) 結果の比較・レポート化
--------------

*   **実験横断の比較**：`ResultsAnalyzer` が実験の読み込み→モデル比較表→可視化（画像保存）までを提供。ダッシュボードと同じ語彙で比較可能。18\_QUICKSTART

* * *

9) 運用中の“分析”＝劣化検知と再学習判断
----------------------

*   **ドリフト検知→再学習トリガ**：新着データの分布比較や統計量監視→ドリフト検出→再学習イベントの記録・起動というフローをシーケンス図で定義。C4\_ARCHITECTURE\_DIAGRAMS
*   **ゴールデンシグナル**：学習時間・予測レイテンシ・成功率などを継続観測し、性能劣化の分析・アラートに繋げます。12\_MONITORING\_GUIDE

* * *

「手を動かす」最短ルート（抜粋）
----------------

1.  **データ健診**
    ```bash
    nf-runner data validate --data ./data/your.csv
    nf-runner data stats --data ./data/your.csv
    ```
    → 欠損/連続性/外れ値・期間を確認。18\_QUICKSTART
2.  **季節性の当たりをつける**（ACF/PACF）  
    `compute_lag_correlation(series, lags=40)` を実行し、ピークと信頼区間で季節性/差分要否を判断。01\_REQUIREMENTS\_SPECIFICATION\_D…
3.  **学習→Backtest→比較**  
    Backtest を `n_splits=5, h=7` で回し、`aggregated_metrics` と fold ごとの分布を見る。01\_REQUIREMENTS\_SPECIFICATION\_D…  
    併せて `ResultsAnalyzer.compare_models()` でモデル横断の表とプロットを出力。18\_QUICKSTART
4.  **“なぜ当たる/外れる？”の説明**  
    重要度（Permutation/SHAP）を出して、特徴寄与のトップ/ボトムを把握。01\_REQUIREMENTS\_SPECIFICATION\_D…
5.  **運用監視→劣化検知→再学習**  
    分布変化や精度低下のアラートを確認し、再学習トリガのイベントが正しく記録・発火するかを見る。

* * *

まとめ（現場での勘どころ）
-------------

*   **順番が命**：データ健診→クセ掴み→評価→解釈→運用。各段に“標準の器”が用意されているので、迷わず積み上がります（CLI/Analyzer/APIが対応）。
*   **注意書きは守る**：Grangerや介入分析は“統計的因果”。ビジネス意思決定では補助線として扱うのが前提です。01\_REQUIREMENTS\_SPECIFICATION\_D…

必要なら、あなたのデータ構造（列名・頻度・外生の種類）に合わせて**具体的なコマンド列**と**可視化テンプレ**（ACF/PACF・モデル比較・SHAP）をそのまま渡せる形に整えます。

## Prompt:
可視化関連の処理について具体的に教えてください。

## Response:
思考時間: 29s

可視化まわりの“設計と手順”、ぜんぶ乗せ
====================

可視化は「どのタイミングで」「何を出し」「どこに残し」「どう見返すか」まで設計されています。要点を実務順でまとめます。

* * *

1) いつ生成されるか（パイプラインの位置づけ）
------------------------

学習・評価フローの中で、\*\*Evaluator（評価）→MetricCalc（指標計算）→Plots（可視化出力）\*\*の順に生成され、成果物はアーティファクトとして保存されます。03\_ARCHITECTURE\_DESIGN\_DETAILED

* * *

2) どこに保存するか（アーティファクト管理）
-----------------------

生成した図は**artifacts**テーブルに`artifact_type='plot'`として登録。保存先はローカル/S3等のURI、ファイルサイズ、ハッシュ、作成時刻、タグを併せて管理します（検索用インデックスも用意）。05\_DATABASE\_DESIGN\_DETAILED  
実ファイルは標準で`outputs/`配下に置くチュートリアル・テスト構成が示されており、そのまま運用に流用できます。

* * *

3) “何を描くか”の標準メニュー（用途別）
----------------------

### A. 予測ライン＋不確実性帯（本番で一番見るやつ）

*   **目的**：実績 vs 予測、予測の上下限（信頼区間/分位）を一枚で把握。
*   **データ**：`predictions`テーブルの`predicted_value / lower_bound / upper_bound`（信頼区間95%など）。レンジパーティション済みで大量でも扱えます。05\_DATABASE\_DESIGN\_DETAILED
*   **実装例**（抜粋）：QuickStartの`fill_between`でバンドを描画→PNG永続化。18\_QUICKSTART
*   **UI**：Web UIのE2Eでは`id="forecast-plot"`の存在を自動テストで確認。09\_TESTING\_STRATEGY

### B. バックテスト可視化（foldごとの分布と集計）

*   **目的**：Rolling-originバックテストの各foldの誤差分布、平均・分散を比較。
*   **根拠**：時系列交差検証（n分割、horizon指定）の設計とメトリクス算出API。01\_REQUIREMENTS\_SPECIFICATION\_D…
*   **表現**：foldごとのMAE/RMSE/sMAPEの棒・箱ひげ、horizon別エラー曲線、最終集計テーブル。

### C. モデル比較（横断ビュー）

*   **目的**：複数モデルの精度（MAE/RMSE/MAPE）をランキング・棒グラフで比較。
*   **実装**：`ResultsAnalyzer.compare_models()` → `plot_model_comparison(save_path=...)`で画像出力。18\_QUICKSTART

### D. ハイパラ探索の分析図

*   **目的**：どのパラメータが効いたか、探索の収束状況。
*   **実装**：`HyperparameterAnalyzer.plot_param_importances()`などで重要度・履歴を保存。18\_QUICKSTART

### E. 相関・ラグ相関（EDA）

*   **目的**：特徴量の関係性・季節性・AR次数のあたりをつける。
*   **API**：相関行列、**ACF/PACF**を返す関数群を定義（信頼区間も返却）。可視化はヒートマップやステムプロットで。01\_REQUIREMENTS\_SPECIFICATION\_D…

### F. 因果・介入の結果サマリ

*   **目的**：Granger因果の有意ラグ、DiDの推定効果と信頼区間を図表化。
*   **API**：Granger/DiDの結果オブジェクト（要約DataFrame/統計量）を返すので、そのまま表・注釈入り図へ。

### G. 運用ダッシュボード（監視の可視化）

*   **目的**：学習時間、予測レイテンシ、失敗率、QPS、DB、GPU/CPUなどの**時系列モニタ**。
*   **構成**：Prometheus/Loki/Jaeger → Grafanaの標準ダッシュボード（System Overview、App、Model、DB、KPI）を設計済み。

* * *

4) “どう描くか”の作法（最短レシピ）
--------------------

### 4.1 予測＋信頼区間プロット（最小例）

*   **やること**：実績`y`と予測`y_pred`、`y_pred_lower/upper`で帯を挟む。
*   **チュートリアル**にそのまま使えるコード（Matplotlib, `plt.fill_between(...)`）が掲載。保存先は`./outputs/forecast_plot.png`。18\_QUICKSTART

### 4.2 モデル比較のPNG出力

```python
from nf_auto_runner import ResultsAnalyzer
analyzer = ResultsAnalyzer()
analyzer.load_experiment(experiment_id=123)
analyzer.plot_model_comparison(save_path='./outputs/model_comparison.png')
```

↑ 公式チュートリアルどおり。18\_QUICKSTART

### 4.3 ACF/PACFの可視化

*   **API**はACF/PACFと信頼区間を返すので、ステム＋`fill_between`で信頼帯を描くのが推奨例。01\_REQUIREMENTS\_SPECIFICATION\_D…

* * *

5) 命名・格納とトレーサビリティ
-----------------

*   **アーティファクト登録**：生成後に`artifacts`へINSERT（`artifact_type='plot'`, `storage_path`, `file_hash`, `tags`）。クエリ性を高めるため、**run\_id/種類/作成日時**にインデックスあり。05\_DATABASE\_DESIGN\_DETAILED
*   **出力先**：`outputs/`配下が標準（テスト/チュートリアル整備済み）。CI/検証やローカル確認と相性が良い。
*   **UI表示**：Web UIで`forecast-plot`が描画されることをE2Eが検証（“表示されているか”まで自動確認）。09\_TESTING\_STRATEGY

* * *

6) モニタリング可視化（運用UIの作り）
---------------------

*   **配線**：App/DB/ノードのメトリクス→Prometheus、ログ→Loki、トレース→Jaeger。Grafanaで統合表示。12\_MONITORING\_GUIDE
*   **ダッシュボード例**：System Overview / Application Metrics / Model Performance / Database Monitoring / Business KPIs をテンプレ化。12\_MONITORING\_GUIDE

* * *

7) 実務フローの型（可視化を“作る→残す→見返す”）
---------------------------

1.  **学習/評価を実行** → Evaluatorがメトリクスとプロットを生成。03\_ARCHITECTURE\_DESIGN\_DETAILED
2.  **ファイル保存 & DB登録** → `outputs/...png`に保存し、`artifacts`へメタ登録。
3.  **UI/ダッシュボードで参照** → 予測図はWeb UI、運用指標はGrafana。E2Eで可視化要素の存在保証。

* * *

8) ここまでの“実装の勘どころ”
-----------------

*   **信頼区間の帯**は`predictions.lower_bound/upper_bound`を必ず使う（分位でもOK）。05\_DATABASE\_DESIGN\_DETAILED
*   **比較は表＋図の二段重ね**：`compare_models()`の表で当たりを付け、PNGをレポート添付。18\_QUICKSTART
*   **EDA→モデル→運用の連結**：ACF/PACFで季節を掴み、学習評価で確からしさを確認、Grafanaで劣化を常時可視化。

* * *

必要なら、**あなたの実験ID/出力ディレクトリ構成**にあわせて、

*   予測＋信頼帯、
*   モデル比較、
*   ACF/PACF、  
    を一気に吐き出す最小スクリプトと**artifacts登録用SQL**まで整えて渡します。

## Prompt:
自動化されている処理と手動化の処理をそれぞれわかりやすく教えてください。

## Response:
思考時間: 28s

何が自動で、何が手動か——一目でわかる運用区分
=======================

下はこのシステムの処理を\*\*「自動／半自動／手動」\*\*に分け、**起点（誰・何が始めるか）**と**根拠**を添えた早見表です。実務で迷いがちな境界も明確にしてあります。

* * *

自動（放っておいて流れる）
-------------

*   **学習パイプライン内の標準処理**  
    モデル検出→組合せ生成→重複チェック（Fingerprint）→学習→バックテスト→メトリクス保存→アーティファクト保存 までを**オーケストレータが自動実行**。同条件のRunは**自動スキップ**。起点＝CLI/API/スケジューラ。
*   **予測APIの後処理**  
    `/predict` で受けた入力は前処理→予測→後処理→**DBへ予測結果を自動保存**して応答。起点＝API。03\_ARCHITECTURE\_DESIGN\_DETAILED
*   **並列実行中のリソース監視**  
    並列エグゼキュータが**ResourceMonitorを自動起動/停止**し、CPU・GPU・メモリを継続監視。起点＝並列実行の開始。03\_ARCHITECTURE\_DESIGN\_DETAILED
*   **再学習の定期・条件トリガ**  
    スケジューラが「時間／データ量／精度閾値／ドリフト」をチェックし、**条件を満たせば自動で再学習を起動**（ジョブ更新・通知含む）。起点＝スケジューラ。
*   **監視・アラート**  
    Prometheusがメトリクス収集、Alertmanagerが**高エラー率やDB接続枯渇を自動通知**。Grafanaはデータソース/ダッシュボードをプロビジョニング。起点＝監視スタック常駐。10\_DEPLOYMENT\_GUIDE
*   **バックアップの定期実行**  
    フル/増分（WALアーカイブ）/設定・モデルのバックアップを**スクリプト化し定期実行**、整合性検証やメタ記録・通知まで自動。起点＝cron等のスケジューラ。
*   **ログとトレースの出力**  
    構造化ログ、MLflow連携、分散トレーシング出力は**処理内で自動フック**。起点＝アプリ起動/Run開始。03\_ARCHITECTURE\_DESIGN\_DETAILED
*   **Runの“自動”起動区分**  
    DB設計上 `runs.source_type` に `scheduled` があり、**スケジュール起動が1stクラス**。05\_DATABASE\_DESIGN\_DETAILED

* * *

半自動（機械が回すが“人間のうなずき”を入れる）
------------------------

*   **モデル昇格（Staging→Production）**  
    自動再学習後のモデルは**レジストリ登録まで自動化**できるが、本番昇格は `require_approval=True` で**承認必須**にできる設計。起点＝自動登録＋人手承認。01\_REQUIREMENTS\_SPECIFICATION\_D…
*   **PITR（時点復旧）・DR切替**  
    復旧スクリプトは自動で進むが、**実行確認やDNS切替は手動**ステップとして明示。起点＝スクリプト＋人手。
*   **アラート対応の初動**  
    通知は自動、**一次トリアージ/エスカレーションはRunbookに沿って人が実施**。起点＝Alert→人。11\_OPERATIONS\_RUNBOOK

* * *

手動（人が始め、人が決める）
--------------

*   **実験作成・初回データ投入・方針決定**  
    新規Experimentの作成やデータ健診の開始は**人の明示操作**（CLI/API/UI）。起点＝人。09\_TESTING\_STRATEGY
*   **緊急対応・運用判断**  
    リソース増強、閾値変更、計画停止、手動再学習（ボタン/CLI）は**運用判断で実行**。起点＝人。11\_OPERATIONS\_RUNBOOK
*   **モデル比較レビューとドキュメンテーション**  
    可視化や比較結果は自動生成されるが、**採用モデルの意思決定はレビュー会で手動**。起点＝人（プロセス）。03\_ARCHITECTURE\_DESIGN\_DETAILED

* * *

迷いどころの“切替スイッチ”まとめ
-----------------

*   **重複防止の自動化ON**：Fingerprintはデフォルト有効（同一条件Runを自動スキップ）。**オフにしない限り**二重実行は起きない。01\_REQUIREMENTS\_SPECIFICATION\_D…
*   **再学習の自動→半自動**：スケジュール/条件は要件の`RetrainingScheduler`に沿って設定、**昇格のみ承認必須**にするのが安全策。
*   **監視の自動→閾値調整は手動**：Alertルールは用意済み。現場のSLOに合わせて**YAMLを更新**して再読み込み。10\_DEPLOYMENT\_GUIDE
*   **バックアップは“回りっぱなし”＋定期検証を人間が確認**：自動整合性テストログを**人が目視**してRPO/RTOを評価。

* * *

「誰が・いつ・どこで」小さな実務ガイド
-------------------

*   **自動の着火点**
    *   API呼び出し→予測保存まで自動。03\_ARCHITECTURE\_DESIGN\_DETAILED
    *   スケジューラ→再学習判定・起動まで自動。C4\_ARCHITECTURE\_DIAGRAMS
    *   監視常駐→アラート自動送信。10\_DEPLOYMENT\_GUIDE
*   **人の介入点**
    *   モデル昇格の承認。01\_REQUIREMENTS\_SPECIFICATION\_D…
    *   復旧スクリプトの実行確認とDNS切替。
    *   運用SLOやAlert閾値の見直し。11\_OPERATIONS\_RUNBOOK

* * *

必要なら、あなたの現場フローに合わせて\*\*「半自動→全自動」\*\*へ寄せる具体的な設定（再学習cron、昇格承認の切り替え、バックアップジョブのcrontab、アラートYAML）をその場で書き下します。

## Prompt:
引数、パラメータの設定値の意味やそれぞれどのような値をどこで設定できるかやそれぞれ値の増減やカテゴリの違いでの影響をわかりやすく教えてください。

## Response:
思考時間: 42s

パラメータ“地図”——何をどこで設定し、増減すると何が起きる？
===============================

下はこの時系列予測システムの**主要パラメータと設定場所**を、影響（値を上げ下げ/カテゴリ変更でどう変わるか）までセットでまとめた実務ガイドです。CLI/API/YAML/環境変数の4レイヤで覚えると迷いません。

* * *

1) データ関連（前提がズレると全部ズレる）
----------------------

**必須列**：`unique_id, ds, y`（識別子・日時・目的変数）。**外生変数**は接頭辞で役割を宣言：

*   `futr_*`（未来に既知の特徴量：例 天気予報）
*   `hist_*`（過去の説明変数）
*   `stat_*`（系列ごとの静的属性）  
    設定場所＝**入力CSV/Parquet**。CLI補助は `nf-runner data validate / data stats`。18\_QUICKSTART

**影響の勘どころ**

*   `futr_*` を予測時に未提供にすると、その特徴は**使えない**（モデルが外生に依存するほど精度が落ちる）。`hist_*` は学習時だけ見える。18\_QUICKSTART
*   系列の**頻度**は自動推定されるが、学習時の最短長さにより安全な `h`（予測長）を内部で下限調整するロジックがある（`safe_h` 計算）。**短い系列で大きな `h`** を要求すると、内部で縮められる。SEQUENCE\_DIAGRAMS\_DETAILED

* * *

2) 学習ジョブ（CLIの主役たち）
------------------

### 2.1 代表的なフラグ

*   `--models AutoNHITS,AutoLSTM,...`  
    モデルの**能力**（外生/カテゴリ/分位予測の可否、必要学習長、対応バックエンド）で互換性確認される。CUDA/MPS などの**利用可能バックエンド**は自動検出。C4\_ARCHITECTURE\_DIAGRAMS
*   `--h 7`（予測ホライズン）  
    大きいほど将来を長く予測。**計算時間・メモリ・学習データ要求**が増える。短すぎると運用上の意思決定視野が狭くなる。内部の `safe_h` で現実的な上限に抑えられるケースあり。SEQUENCE\_DIAGRAMS\_DETAILED
*   `--val-size 0.2 | 50 | auto | 24/h`  
    検証サイズ。**大きいほど**汎化性能評価は安定するが学習データは減る。`auto` や `24/h` の指定パターンもサポート。19\_FAQ
*   `--max-workers 4`（並列度）  
    スループット↑、ただし**メモリ/GPU圧迫**。大きくしすぎるとスワップやOOMで逆効果。18\_QUICKSTART
*   `--search-alg optuna --num-trials 50 --timeout 3600`（探索）  
    探索アルゴリズム（TPE/CMA-ES/ASHA など）、試行回数、制限時間。**試行を増やすほど**良いパラメータに近づくが、**時間と費用**が増える。早期終了（pruning）で短縮も可。
*   `--early-stopping-patience 10`  
    改善が止まったら止める。**大きいほど**粘って精度↑の余地、ただし**時間↑**。19\_FAQ
*   `--log-level DEBUG`（または `LOG_LEVEL` 環境変数）  
    ログ詳細度。DEBUGは**診断に有用**だがI/O量が増える。19\_FAQ

**どこで設定？**  
CLI（`nf-runner train/backtest/evaluate`）と、Hydra/YAMLでの上書きも可（例：`execution.max_workers=8`）。19\_FAQ

* * *

3) 予測API（本番の入り口）
----------------

### 3.1 リクエストの主な項目

```json
{
  "model_name": "AutoNHITS_sales_forecast",
  "model_version": "v1.0.0",
  "data": {...},
  "horizon": 7,
  "return_quantiles": true,
  "quantiles": [0.1, 0.5, 0.9]
}
```

**どこで設定？** `POST /api/v1/predict` のJSON。バッチは `/predict/batch`。

**影響の勘どころ**

*   `horizon` を大きくすると**応答時間・結果サイズ**が線形に増える。
*   `return_quantiles=true` + `quantiles` 追加で**確率予測**を返す。分位の本数を増やすほど**計算/応答サイズ↑**。モデル側が分位に対応している必要あり（Capability）。C4\_ARCHITECTURE\_DIAGRAMS

* * *

4) ハイパーパラメータ（モデルの“性格”を決める）
--------------------------

### 4.1 どうやって指定する？

*   **プログラム/API**：`HyperparameterTuner.tune(..., param_space=...)` に**型×分布**で定義  
    例）`("int", 7, 30)`, `("categorical", [64,128,256])`, `("loguniform", 1e-5, 1e-2)`。01\_REQUIREMENTS\_SPECIFICATION\_D…
*   **YAML**：`conf/hyperparameter.yaml` にモデル別の空間を列挙（CLIの `--search-alg/--num-trials` と併用）。19\_FAQ

### 4.2 代表例と“増減の効き方”

*   `input_size`：過去の参照窓。**大きいほど**長期パターンを掴みやすいが**メモリ/時間↑**、過学習リスクも。01\_REQUIREMENTS\_SPECIFICATION\_D…
*   `hidden_size`（カテゴリ）：表現力。**大きいほど**表現力↑だが**計算↑**。データが小さいと過学習寄り。01\_REQUIREMENTS\_SPECIFICATION\_D…
*   `lr`（学習率、loguniform）：**高すぎ**ると発散、**低すぎ**ると収束遅い。log空間で探索が定石。01\_REQUIREMENTS\_SPECIFICATION\_D…
*   `n_trials` / `timeout`：探索の**幅と深さ**。`n_trials` を増やすほど最適付近に近づくが、**費用↑**。`timeout` で打ち切り。01\_REQUIREMENTS\_SPECIFICATION\_D…
*   `algorithm`：
    *   **tpe**（バランス型）、**cmaes**（連続値に強い）、**random/grid**（ベースライン）、**asha**（早期打ち切りで**速い**）。**連続×多次元**はベイズ系が効きやすい。

* * *

5) 評価・分割（Backtest/検証）
---------------------

*   **Rolling-origin backtest**：`n_splits（fold数）` と `h` の組を設計。fold を増やすと**頑健性↑**だが**時間↑**。01\_REQUIREMENTS\_SPECIFICATION\_D…
*   **メトリクス**（MAE/RMSE/sMAPE/MASE/MAPE）：外れ値に敏感か、ゼロ割が起きるか、**選び方**で見える世界が変わる。01\_REQUIREMENTS\_SPECIFICATION\_D…

**どこで設定？**  
CLIの `nf-runner backtest --h 7 --n-folds 5` 等、または評価API。19\_FAQ

* * *

6) 実行計画・組合せ（爆発を防ぐスイッチ）
----------------------

*   **展開軸**：`model / backend / search_alg / loss` をどこまで**掛け合わせるか**は設定（Hydra/Config）。`combo_depth` で広げすぎを抑制。広げるほど**カバレッジ↑、計算爆発↑**。03\_ARCHITECTURE\_DESIGN\_DETAILED
*   **重複防止**：Run Fingerprint（モデル/データ/ハイパラ/コード等でハッシュ）で**同条件を自動スキップ**。スキップ閾値を緩めると**再現性↓**。01\_REQUIREMENTS\_SPECIFICATION\_D…

* * *

7) レジストリ/運用パラメータ
----------------

*   **Stage**：`staging / production / archived`。昇格先の**ステージ**で“どのモデルをAPI/バッチが拾うか”が決まる。CLI 例：`registry promote --stage production`。**誤昇格**は即時影響。19\_FAQ
*   **レート制限**：エンドポイント/ユーザー別の**リミット**。429が出る場合は**バッチ化/待機**などの運用パラメータ調整が必要。06\_API\_DESIGN\_DETAILED

* * *

8) 可観測性・インフラのパラメータ
------------------

*   **トレーシング**：`JAEGER_HOST/PORT` 等の環境変数で出力先を指定。\*\*サンプリング↑\*\*で可視性↑、オーバーヘッドも↑。12\_MONITORING\_GUIDE
*   **Ray クラスタ**：`conf/ray.yml` の `num_cpus/num_gpus/memory/autoscaling`。並列を上げると**待ち行列は減る**が、**ノード増・コスト↑**。10\_DEPLOYMENT\_GUIDE
*   **MLflow**：`conf/mlflow.yml` の `uri/artifacts/log_models` など。ロギング量↑は**ストレージ/ネットワーク↑**。10\_DEPLOYMENT\_GUIDE
*   **Prometheusアラート**：閾値をYAMLで設定（例：エラー率・メモリ・DBプール）。**厳しすぎ**るとノイジー、**緩すぎ**ると見逃し。10\_DEPLOYMENT\_GUIDE

* * *

9) データベース運用（スループットの裏側）
----------------------

*   **予測テーブルのパーティション**：スクリプトの `months_ahead` で**先回り作成**。短すぎると**月初に失敗**、長すぎると**パーティション過多**。05\_DATABASE\_DESIGN\_DETAILED
*   **監査/運用SQL**：接続数・サイズ・ロックの閾値（運用チームのダッシュボード指標と連動）。05\_DATABASE\_DESIGN\_DETAILED

* * *

10) すぐ使える“値の上げ下げ”チートシート
-----------------------

*   **精度が不安** → `val-size` を**増やす** / `n_splits` を**増やす** / `n_trials` を**増やす**（時間↑）。
*   **遅い** → `max-workers` を**適度に増** / `algorithm=asha` で**早期打切り** / `input_size` を**抑える**。
*   **先の期間も見たい** → `h` を**増やす**（ただし**safe\_h**に注意＋学習窓を**伸ばす**）。SEQUENCE\_DIAGRAMS\_DETAILED
*   **分布が揺らぐ** → 予測APIで `return_quantiles=true` と適切な `quantiles` を設定（レスポンス/計算↑）。01\_REQUIREMENTS\_SPECIFICATION\_D…
*   **GPUが詰まる** → Rayの `num_gpus`/`autoscaling` とモデルの**バックエンド選択**を見直す。

* * *

### まとめ

*   **設定レイヤ**：データ（CSV）→ 学習（CLI/Hydra）→ 推論（API JSON）→ 運用（YAML/環境変数）。
*   **増やすと効く/重くなる**のバランス感覚を持つと、探索・評価・運用の各段が素直に安定します。  
    次は、あなたの実データ頻度と制約（CPU/GPU/締め切り）に合わせて\*\*推奨プリセット（YAML + CLI + API例）\*\*を作ります。

## Prompt:
<style type="text/css">
#T_a496e th {
  position: sticky;
  top: 0;
  background: #111827;
  color: white;
  z-index: 2;
  text-align: left;
}
#T_a496e tbody tr:nth-child(even) {
  background: #f8fafc;
}
#T_a496e td {
  border: 1px solid #e5e7eb;
  padding: 6px 8px;
  font-size: 12px;
}
#T_a496e  th {
  border: 1px solid #e5e7eb;
  padding: 6px 8px;
  font-size: 12px;
}
#T_a496e_row0_col0, #T_a496e_row0_col1, #T_a496e_row0_col2, #T_a496e_row0_col3, #T_a496e_row0_col7, #T_a496e_row0_col8, #T_a496e_row0_col9, #T_a496e_row0_col10, #T_a496e_row0_col11, #T_a496e_row0_col12, #T_a496e_row0_col13, #T_a496e_row0_col14, #T_a496e_row0_col15, #T_a496e_row0_col16, #T_a496e_row0_col17, #T_a496e_row0_col18, #T_a496e_row0_col20, #T_a496e_row0_col21, #T_a496e_row0_col23, #T_a496e_row0_col24, #T_a496e_row0_col25, #T_a496e_row0_col29, #T_a496e_row0_col30, #T_a496e_row0_col31, #T_a496e_row0_col32, #T_a496e_row0_col33, #T_a496e_row1_col0, #T_a496e_row1_col1, #T_a496e_row1_col2, #T_a496e_row1_col3, #T_a496e_row1_col7, #T_a496e_row1_col8, #T_a496e_row1_col9, #T_a496e_row1_col10, #T_a496e_row1_col11, #T_a496e_row1_col12, #T_a496e_row1_col13, #T_a496e_row1_col14, #T_a496e_row1_col15, #T_a496e_row1_col16, #T_a496e_row1_col17, #T_a496e_row1_col18, #T_a496e_row1_col20, #T_a496e_row1_col21, #T_a496e_row1_col23, #T_a496e_row1_col24, #T_a496e_row1_col25, #T_a496e_row1_col29, #T_a496e_row1_col30, #T_a496e_row1_col31, #T_a496e_row1_col32, #T_a496e_row1_col33, #T_a496e_row2_col0, #T_a496e_row2_col1, #T_a496e_row2_col2, #T_a496e_row2_col3, #T_a496e_row2_col7, #T_a496e_row2_col8, #T_a496e_row2_col9, #T_a496e_row2_col10, #T_a496e_row2_col11, #T_a496e_row2_col12, #T_a496e_row2_col13, #T_a496e_row2_col14, #T_a496e_row2_col15, #T_a496e_row2_col16, #T_a496e_row2_col17, #T_a496e_row2_col18, #T_a496e_row2_col20, #T_a496e_row2_col21, #T_a496e_row2_col23, #T_a496e_row2_col24, #T_a496e_row2_col25, #T_a496e_row2_col29, #T_a496e_row2_col30, #T_a496e_row2_col31, #T_a496e_row2_col32, #T_a496e_row2_col33, #T_a496e_row3_col0, #T_a496e_row3_col1, #T_a496e_row3_col2, #T_a496e_row3_col3, #T_a496e_row3_col7, #T_a496e_row3_col8, #T_a496e_row3_col9, #T_a496e_row3_col10, #T_a496e_row3_col11, #T_a496e_row3_col12, #T_a496e_row3_col13, #T_a496e_row3_col14, #T_a496e_row3_col15, #T_a496e_row3_col16, #T_a496e_row3_col17, #T_a496e_row3_col18, #T_a496e_row3_col20, #T_a496e_row3_col21, #T_a496e_row3_col23, #T_a496e_row3_col24, #T_a496e_row3_col25, #T_a496e_row3_col29, #T_a496e_row3_col30, #T_a496e_row3_col31, #T_a496e_row3_col32, #T_a496e_row3_col33, #T_a496e_row4_col0, #T_a496e_row4_col1, #T_a496e_row4_col2, #T_a496e_row4_col3, #T_a496e_row4_col7, #T_a496e_row4_col8, #T_a496e_row4_col9, #T_a496e_row4_col10, #T_a496e_row4_col11, #T_a496e_row4_col12, #T_a496e_row4_col13, #T_a496e_row4_col14, #T_a496e_row4_col15, #T_a496e_row4_col16, #T_a496e_row4_col17, #T_a496e_row4_col18, #T_a496e_row4_col20, #T_a496e_row4_col21, #T_a496e_row4_col23, #T_a496e_row4_col24, #T_a496e_row4_col25, #T_a496e_row4_col29, #T_a496e_row4_col30, #T_a496e_row4_col31, #T_a496e_row4_col32, #T_a496e_row4_col33, #T_a496e_row5_col0, #T_a496e_row5_col1, #T_a496e_row5_col2, #T_a496e_row5_col3, #T_a496e_row5_col7, #T_a496e_row5_col8, #T_a496e_row5_col9, #T_a496e_row5_col10, #T_a496e_row5_col11, #T_a496e_row5_col12, #T_a496e_row5_col13, #T_a496e_row5_col14, #T_a496e_row5_col15, #T_a496e_row5_col16, #T_a496e_row5_col17, #T_a496e_row5_col18, #T_a496e_row5_col20, #T_a496e_row5_col21, #T_a496e_row5_col23, #T_a496e_row5_col24, #T_a496e_row5_col25, #T_a496e_row5_col29, #T_a496e_row5_col30, #T_a496e_row5_col31, #T_a496e_row5_col32, #T_a496e_row5_col33, #T_a496e_row6_col0, #T_a496e_row6_col1, #T_a496e_row6_col2, #T_a496e_row6_col3, #T_a496e_row6_col7, #T_a496e_row6_col8, #T_a496e_row6_col9, #T_a496e_row6_col10, #T_a496e_row6_col11, #T_a496e_row6_col12, #T_a496e_row6_col13, #T_a496e_row6_col14, #T_a496e_row6_col15, #T_a496e_row6_col16, #T_a496e_row6_col17, #T_a496e_row6_col18, #T_a496e_row6_col20, #T_a496e_row6_col21, #T_a496e_row6_col23, #T_a496e_row6_col24, #T_a496e_row6_col25, #T_a496e_row6_col29, #T_a496e_row6_col30, #T_a496e_row6_col31, #T_a496e_row6_col32, #T_a496e_row6_col33, #T_a496e_row7_col0, #T_a496e_row7_col1, #T_a496e_row7_col2, #T_a496e_row7_col3, #T_a496e_row7_col7, #T_a496e_row7_col8, #T_a496e_row7_col9, #T_a496e_row7_col10, #T_a496e_row7_col11, #T_a496e_row7_col12, #T_a496e_row7_col13, #T_a496e_row7_col14, #T_a496e_row7_col15, #T_a496e_row7_col16, #T_a496e_row7_col17, #T_a496e_row7_col18, #T_a496e_row7_col20, #T_a496e_row7_col21, #T_a496e_row7_col23, #T_a496e_row7_col24, #T_a496e_row7_col25, #T_a496e_row7_col29, #T_a496e_row7_col30, #T_a496e_row7_col31, #T_a496e_row7_col32, #T_a496e_row7_col33, #T_a496e_row8_col0, #T_a496e_row8_col1, #T_a496e_row8_col2, #T_a496e_row8_col3, #T_a496e_row8_col7, #T_a496e_row8_col8, #T_a496e_row8_col9, #T_a496e_row8_col10, #T_a496e_row8_col11, #T_a496e_row8_col12, #T_a496e_row8_col13, #T_a496e_row8_col14, #T_a496e_row8_col15, #T_a496e_row8_col16, #T_a496e_row8_col17, #T_a496e_row8_col18, #T_a496e_row8_col20, #T_a496e_row8_col21, #T_a496e_row8_col23, #T_a496e_row8_col24, #T_a496e_row8_col25, #T_a496e_row8_col29, #T_a496e_row8_col30, #T_a496e_row8_col31, #T_a496e_row8_col32, #T_a496e_row8_col33, #T_a496e_row9_col0, #T_a496e_row9_col1, #T_a496e_row9_col2, #T_a496e_row9_col3, #T_a496e_row9_col7, #T_a496e_row9_col8, #T_a496e_row9_col9, #T_a496e_row9_col10, #T_a496e_row9_col11, #T_a496e_row9_col12, #T_a496e_row9_col13, #T_a496e_row9_col14, #T_a496e_row9_col15, #T_a496e_row9_col16, #T_a496e_row9_col17, #T_a496e_row9_col18, #T_a496e_row9_col20, #T_a496e_row9_col21, #T_a496e_row9_col23, #T_a496e_row9_col24, #T_a496e_row9_col25, #T_a496e_row9_col29, #T_a496e_row9_col30, #T_a496e_row9_col31, #T_a496e_row9_col32, #T_a496e_row9_col33, #T_a496e_row10_col0, #T_a496e_row10_col1, #T_a496e_row10_col2, #T_a496e_row10_col3, #T_a496e_row10_col7, #T_a496e_row10_col8, #T_a496e_row10_col9, #T_a496e_row10_col10, #T_a496e_row10_col11, #T_a496e_row10_col12, #T_a496e_row10_col13, #T_a496e_row10_col14, #T_a496e_row10_col15, #T_a496e_row10_col16, #T_a496e_row10_col17, #T_a496e_row10_col18, #T_a496e_row10_col20, #T_a496e_row10_col21, #T_a496e_row10_col23, #T_a496e_row10_col24, #T_a496e_row10_col25, #T_a496e_row10_col29, #T_a496e_row10_col30, #T_a496e_row10_col31, #T_a496e_row10_col32, #T_a496e_row10_col33, #T_a496e_row11_col0, #T_a496e_row11_col1, #T_a496e_row11_col2, #T_a496e_row11_col3, #T_a496e_row11_col7, #T_a496e_row11_col8, #T_a496e_row11_col9, #T_a496e_row11_col10, #T_a496e_row11_col11, #T_a496e_row11_col12, #T_a496e_row11_col13, #T_a496e_row11_col14, #T_a496e_row11_col15, #T_a496e_row11_col16, #T_a496e_row11_col17, #T_a496e_row11_col18, #T_a496e_row11_col20, #T_a496e_row11_col21, #T_a496e_row11_col23, #T_a496e_row11_col24, #T_a496e_row11_col25, #T_a496e_row11_col29, #T_a496e_row11_col30, #T_a496e_row11_col31, #T_a496e_row11_col32, #T_a496e_row11_col33, #T_a496e_row12_col0, #T_a496e_row12_col1, #T_a496e_row12_col2, #T_a496e_row12_col3, #T_a496e_row12_col7, #T_a496e_row12_col8, #T_a496e_row12_col9, #T_a496e_row12_col10, #T_a496e_row12_col11, #T_a496e_row12_col12, #T_a496e_row12_col13, #T_a496e_row12_col14, #T_a496e_row12_col15, #T_a496e_row12_col16, #T_a496e_row12_col17, #T_a496e_row12_col18, #T_a496e_row12_col20, #T_a496e_row12_col21, #T_a496e_row12_col23, #T_a496e_row12_col24, #T_a496e_row12_col25, #T_a496e_row12_col29, #T_a496e_row12_col30, #T_a496e_row12_col31, #T_a496e_row12_col32, #T_a496e_row12_col33, #T_a496e_row13_col0, #T_a496e_row13_col1, #T_a496e_row13_col2, #T_a496e_row13_col3, #T_a496e_row13_col7, #T_a496e_row13_col8, #T_a496e_row13_col9, #T_a496e_row13_col10, #T_a496e_row13_col11, #T_a496e_row13_col12, #T_a496e_row13_col13, #T_a496e_row13_col14, #T_a496e_row13_col15, #T_a496e_row13_col16, #T_a496e_row13_col17, #T_a496e_row13_col18, #T_a496e_row13_col20, #T_a496e_row13_col21, #T_a496e_row13_col23, #T_a496e_row13_col24, #T_a496e_row13_col25, #T_a496e_row13_col29, #T_a496e_row13_col30, #T_a496e_row13_col31, #T_a496e_row13_col32, #T_a496e_row13_col33, #T_a496e_row14_col0, #T_a496e_row14_col1, #T_a496e_row14_col2, #T_a496e_row14_col3, #T_a496e_row14_col7, #T_a496e_row14_col8, #T_a496e_row14_col9, #T_a496e_row14_col10, #T_a496e_row14_col11, #T_a496e_row14_col12, #T_a496e_row14_col13, #T_a496e_row14_col14, #T_a496e_row14_col15, #T_a496e_row14_col16, #T_a496e_row14_col17, #T_a496e_row14_col18, #T_a496e_row14_col20, #T_a496e_row14_col21, #T_a496e_row14_col23, #T_a496e_row14_col24, #T_a496e_row14_col25, #T_a496e_row14_col29, #T_a496e_row14_col30, #T_a496e_row14_col31, #T_a496e_row14_col32, #T_a496e_row14_col33, #T_a496e_row15_col0, #T_a496e_row15_col1, #T_a496e_row15_col2, #T_a496e_row15_col3, #T_a496e_row15_col7, #T_a496e_row15_col8, #T_a496e_row15_col9, #T_a496e_row15_col10, #T_a496e_row15_col11, #T_a496e_row15_col12, #T_a496e_row15_col13, #T_a496e_row15_col14, #T_a496e_row15_col15, #T_a496e_row15_col16, #T_a496e_row15_col17, #T_a496e_row15_col18, #T_a496e_row15_col20, #T_a496e_row15_col21, #T_a496e_row15_col23, #T_a496e_row15_col24, #T_a496e_row15_col25, #T_a496e_row15_col29, #T_a496e_row15_col30, #T_a496e_row15_col31, #T_a496e_row15_col32, #T_a496e_row15_col33, #T_a496e_row16_col0, #T_a496e_row16_col1, #T_a496e_row16_col2, #T_a496e_row16_col3, #T_a496e_row16_col7, #T_a496e_row16_col8, #T_a496e_row16_col9, #T_a496e_row16_col10, #T_a496e_row16_col11, #T_a496e_row16_col12, #T_a496e_row16_col13, #T_a496e_row16_col14, #T_a496e_row16_col15, #T_a496e_row16_col16, #T_a496e_row16_col17, #T_a496e_row16_col18, #T_a496e_row16_col20, #T_a496e_row16_col21, #T_a496e_row16_col23, #T_a496e_row16_col24, #T_a496e_row16_col25, #T_a496e_row16_col29, #T_a496e_row16_col30, #T_a496e_row16_col31, #T_a496e_row16_col32, #T_a496e_row16_col33, #T_a496e_row17_col0, #T_a496e_row17_col1, #T_a496e_row17_col2, #T_a496e_row17_col3, #T_a496e_row17_col7, #T_a496e_row17_col8, #T_a496e_row17_col9, #T_a496e_row17_col10, #T_a496e_row17_col11, #T_a496e_row17_col12, #T_a496e_row17_col13, #T_a496e_row17_col14, #T_a496e_row17_col15, #T_a496e_row17_col16, #T_a496e_row17_col17, #T_a496e_row17_col18, #T_a496e_row17_col20, #T_a496e_row17_col21, #T_a496e_row17_col23, #T_a496e_row17_col24, #T_a496e_row17_col25, #T_a496e_row17_col29, #T_a496e_row17_col30, #T_a496e_row17_col31, #T_a496e_row17_col32, #T_a496e_row17_col33, #T_a496e_row18_col0, #T_a496e_row18_col1, #T_a496e_row18_col2, #T_a496e_row18_col3, #T_a496e_row18_col7, #T_a496e_row18_col8, #T_a496e_row18_col9, #T_a496e_row18_col10, #T_a496e_row18_col11, #T_a496e_row18_col12, #T_a496e_row18_col13, #T_a496e_row18_col14, #T_a496e_row18_col15, #T_a496e_row18_col16, #T_a496e_row18_col17, #T_a496e_row18_col18, #T_a496e_row18_col20, #T_a496e_row18_col21, #T_a496e_row18_col23, #T_a496e_row18_col24, #T_a496e_row18_col25, #T_a496e_row18_col29, #T_a496e_row18_col30, #T_a496e_row18_col31, #T_a496e_row18_col32, #T_a496e_row18_col33, #T_a496e_row19_col0, #T_a496e_row19_col1, #T_a496e_row19_col2, #T_a496e_row19_col3, #T_a496e_row19_col7, #T_a496e_row19_col8, #T_a496e_row19_col9, #T_a496e_row19_col10, #T_a496e_row19_col11, #T_a496e_row19_col12, #T_a496e_row19_col13, #T_a496e_row19_col14, #T_a496e_row19_col15, #T_a496e_row19_col16, #T_a496e_row19_col17, #T_a496e_row19_col18, #T_a496e_row19_col20, #T_a496e_row19_col21, #T_a496e_row19_col23, #T_a496e_row19_col24, #T_a496e_row19_col25, #T_a496e_row19_col29, #T_a496e_row19_col30, #T_a496e_row19_col31, #T_a496e_row19_col32, #T_a496e_row19_col33, #T_a496e_row20_col0, #T_a496e_row20_col1, #T_a496e_row20_col2, #T_a496e_row20_col3, #T_a496e_row20_col7, #T_a496e_row20_col8, #T_a496e_row20_col9, #T_a496e_row20_col10, #T_a496e_row20_col11, #T_a496e_row20_col12, #T_a496e_row20_col13, #T_a496e_row20_col14, #T_a496e_row20_col15, #T_a496e_row20_col16, #T_a496e_row20_col17, #T_a496e_row20_col18, #T_a496e_row20_col20, #T_a496e_row20_col21, #T_a496e_row20_col23, #T_a496e_row20_col24, #T_a496e_row20_col25, #T_a496e_row20_col29, #T_a496e_row20_col30, #T_a496e_row20_col31, #T_a496e_row20_col32, #T_a496e_row20_col33, #T_a496e_row21_col0, #T_a496e_row21_col1, #T_a496e_row21_col2, #T_a496e_row21_col3, #T_a496e_row21_col7, #T_a496e_row21_col8, #T_a496e_row21_col9, #T_a496e_row21_col10, #T_a496e_row21_col11, #T_a496e_row21_col12, #T_a496e_row21_col13, #T_a496e_row21_col14, #T_a496e_row21_col15, #T_a496e_row21_col16, #T_a496e_row21_col17, #T_a496e_row21_col18, #T_a496e_row21_col20, #T_a496e_row21_col21, #T_a496e_row21_col23, #T_a496e_row21_col24, #T_a496e_row21_col25, #T_a496e_row21_col29, #T_a496e_row21_col30, #T_a496e_row21_col31, #T_a496e_row21_col32, #T_a496e_row21_col33, #T_a496e_row22_col0, #T_a496e_row22_col1, #T_a496e_row22_col2, #T_a496e_row22_col3, #T_a496e_row22_col7, #T_a496e_row22_col8, #T_a496e_row22_col9, #T_a496e_row22_col10, #T_a496e_row22_col11, #T_a496e_row22_col12, #T_a496e_row22_col13, #T_a496e_row22_col14, #T_a496e_row22_col15, #T_a496e_row22_col16, #T_a496e_row22_col17, #T_a496e_row22_col18, #T_a496e_row22_col20, #T_a496e_row22_col21, #T_a496e_row22_col23, #T_a496e_row22_col24, #T_a496e_row22_col25, #T_a496e_row22_col29, #T_a496e_row22_col30, #T_a496e_row22_col31, #T_a496e_row22_col32, #T_a496e_row22_col33, #T_a496e_row23_col0, #T_a496e_row23_col1, #T_a496e_row23_col2, #T_a496e_row23_col3, #T_a496e_row23_col7, #T_a496e_row23_col8, #T_a496e_row23_col9, #T_a496e_row23_col10, #T_a496e_row23_col11, #T_a496e_row23_col12, #T_a496e_row23_col13, #T_a496e_row23_col14, #T_a496e_row23_col15, #T_a496e_row23_col16, #T_a496e_row23_col17, #T_a496e_row23_col18, #T_a496e_row23_col20, #T_a496e_row23_col21, #T_a496e_row23_col23, #T_a496e_row23_col24, #T_a496e_row23_col25, #T_a496e_row23_col29, #T_a496e_row23_col30, #T_a496e_row23_col31, #T_a496e_row23_col32, #T_a496e_row23_col33, #T_a496e_row24_col0, #T_a496e_row24_col1, #T_a496e_row24_col2, #T_a496e_row24_col3, #T_a496e_row24_col7, #T_a496e_row24_col8, #T_a496e_row24_col9, #T_a496e_row24_col10, #T_a496e_row24_col11, #T_a496e_row24_col12, #T_a496e_row24_col13, #T_a496e_row24_col14, #T_a496e_row24_col15, #T_a496e_row24_col16, #T_a496e_row24_col17, #T_a496e_row24_col18, #T_a496e_row24_col20, #T_a496e_row24_col21, #T_a496e_row24_col23, #T_a496e_row24_col24, #T_a496e_row24_col25, #T_a496e_row24_col29, #T_a496e_row24_col30, #T_a496e_row24_col31, #T_a496e_row24_col32, #T_a496e_row24_col33, #T_a496e_row25_col0, #T_a496e_row25_col1, #T_a496e_row25_col2, #T_a496e_row25_col3, #T_a496e_row25_col7, #T_a496e_row25_col8, #T_a496e_row25_col9, #T_a496e_row25_col10, #T_a496e_row25_col11, #T_a496e_row25_col12, #T_a496e_row25_col13, #T_a496e_row25_col14, #T_a496e_row25_col15, #T_a496e_row25_col16, #T_a496e_row25_col17, #T_a496e_row25_col18, #T_a496e_row25_col20, #T_a496e_row25_col21, #T_a496e_row25_col23, #T_a496e_row25_col24, #T_a496e_row25_col25, #T_a496e_row25_col29, #T_a496e_row25_col30, #T_a496e_row25_col31, #T_a496e_row25_col32, #T_a496e_row25_col33, #T_a496e_row26_col0, #T_a496e_row26_col1, #T_a496e_row26_col2, #T_a496e_row26_col3, #T_a496e_row26_col7, #T_a496e_row26_col8, #T_a496e_row26_col9, #T_a496e_row26_col10, #T_a496e_row26_col11, #T_a496e_row26_col12, #T_a496e_row26_col13, #T_a496e_row26_col14, #T_a496e_row26_col15, #T_a496e_row26_col16, #T_a496e_row26_col17, #T_a496e_row26_col18, #T_a496e_row26_col20, #T_a496e_row26_col21, #T_a496e_row26_col23, #T_a496e_row26_col24, #T_a496e_row26_col25, #T_a496e_row26_col29, #T_a496e_row26_col30, #T_a496e_row26_col31, #T_a496e_row26_col32, #T_a496e_row26_col33, #T_a496e_row27_col0, #T_a496e_row27_col1, #T_a496e_row27_col2, #T_a496e_row27_col3, #T_a496e_row27_col7, #T_a496e_row27_col8, #T_a496e_row27_col9, #T_a496e_row27_col10, #T_a496e_row27_col11, #T_a496e_row27_col12, #T_a496e_row27_col13, #T_a496e_row27_col14, #T_a496e_row27_col15, #T_a496e_row27_col16, #T_a496e_row27_col17, #T_a496e_row27_col18, #T_a496e_row27_col20, #T_a496e_row27_col21, #T_a496e_row27_col23, #T_a496e_row27_col24, #T_a496e_row27_col25, #T_a496e_row27_col29, #T_a496e_row27_col30, #T_a496e_row27_col31, #T_a496e_row27_col32, #T_a496e_row27_col33, #T_a496e_row28_col0, #T_a496e_row28_col1, #T_a496e_row28_col2, #T_a496e_row28_col3, #T_a496e_row28_col7, #T_a496e_row28_col8, #T_a496e_row28_col9, #T_a496e_row28_col10, #T_a496e_row28_col11, #T_a496e_row28_col12, #T_a496e_row28_col13, #T_a496e_row28_col14, #T_a496e_row28_col15, #T_a496e_row28_col16, #T_a496e_row28_col17, #T_a496e_row28_col18, #T_a496e_row28_col20, #T_a496e_row28_col21, #T_a496e_row28_col23, #T_a496e_row28_col24, #T_a496e_row28_col25, #T_a496e_row28_col29, #T_a496e_row28_col30, #T_a496e_row28_col31, #T_a496e_row28_col32, #T_a496e_row28_col33, #T_a496e_row29_col0, #T_a496e_row29_col1, #T_a496e_row29_col2, #T_a496e_row29_col3, #T_a496e_row29_col7, #T_a496e_row29_col8, #T_a496e_row29_col9, #T_a496e_row29_col10, #T_a496e_row29_col11, #T_a496e_row29_col12, #T_a496e_row29_col13, #T_a496e_row29_col14, #T_a496e_row29_col15, #T_a496e_row29_col16, #T_a496e_row29_col17, #T_a496e_row29_col18, #T_a496e_row29_col20, #T_a496e_row29_col21, #T_a496e_row29_col23, #T_a496e_row29_col24, #T_a496e_row29_col25, #T_a496e_row29_col29, #T_a496e_row29_col30, #T_a496e_row29_col31, #T_a496e_row29_col32, #T_a496e_row29_col33, #T_a496e_row30_col0, #T_a496e_row30_col1, #T_a496e_row30_col2, #T_a496e_row30_col3, #T_a496e_row30_col7, #T_a496e_row30_col8, #T_a496e_row30_col9, #T_a496e_row30_col10, #T_a496e_row30_col11, #T_a496e_row30_col12, #T_a496e_row30_col13, #T_a496e_row30_col14, #T_a496e_row30_col15, #T_a496e_row30_col16, #T_a496e_row30_col17, #T_a496e_row30_col18, #T_a496e_row30_col20, #T_a496e_row30_col21, #T_a496e_row30_col23, #T_a496e_row30_col24, #T_a496e_row30_col25, #T_a496e_row30_col29, #T_a496e_row30_col30, #T_a496e_row30_col31, #T_a496e_row30_col32, #T_a496e_row30_col33, #T_a496e_row31_col0, #T_a496e_row31_col1, #T_a496e_row31_col2, #T_a496e_row31_col3, #T_a496e_row31_col7, #T_a496e_row31_col8, #T_a496e_row31_col9, #T_a496e_row31_col10, #T_a496e_row31_col11, #T_a496e_row31_col12, #T_a496e_row31_col13, #T_a496e_row31_col14, #T_a496e_row31_col15, #T_a496e_row31_col16, #T_a496e_row31_col17, #T_a496e_row31_col18, #T_a496e_row31_col20, #T_a496e_row31_col21, #T_a496e_row31_col23, #T_a496e_row31_col24, #T_a496e_row31_col25, #T_a496e_row31_col29, #T_a496e_row31_col30, #T_a496e_row31_col31, #T_a496e_row31_col32, #T_a496e_row31_col33, #T_a496e_row32_col0, #T_a496e_row32_col1, #T_a496e_row32_col2, #T_a496e_row32_col3, #T_a496e_row32_col7, #T_a496e_row32_col8, #T_a496e_row32_col9, #T_a496e_row32_col10, #T_a496e_row32_col11, #T_a496e_row32_col12, #T_a496e_row32_col13, #T_a496e_row32_col14, #T_a496e_row32_col15, #T_a496e_row32_col16, #T_a496e_row32_col17, #T_a496e_row32_col18, #T_a496e_row32_col20, #T_a496e_row32_col21, #T_a496e_row32_col23, #T_a496e_row32_col24, #T_a496e_row32_col25, #T_a496e_row32_col29, #T_a496e_row32_col30, #T_a496e_row32_col31, #T_a496e_row32_col32, #T_a496e_row32_col33, #T_a496e_row33_col0, #T_a496e_row33_col1, #T_a496e_row33_col2, #T_a496e_row33_col3, #T_a496e_row33_col7, #T_a496e_row33_col8, #T_a496e_row33_col9, #T_a496e_row33_col10, #T_a496e_row33_col11, #T_a496e_row33_col12, #T_a496e_row33_col13, #T_a496e_row33_col14, #T_a496e_row33_col15, #T_a496e_row33_col16, #T_a496e_row33_col17, #T_a496e_row33_col18, #T_a496e_row33_col20, #T_a496e_row33_col21, #T_a496e_row33_col23, #T_a496e_row33_col24, #T_a496e_row33_col25, #T_a496e_row33_col29, #T_a496e_row33_col30, #T_a496e_row33_col31, #T_a496e_row33_col32, #T_a496e_row33_col33, #T_a496e_row34_col0, #T_a496e_row34_col1, #T_a496e_row34_col2, #T_a496e_row34_col3, #T_a496e_row34_col7, #T_a496e_row34_col8, #T_a496e_row34_col9, #T_a496e_row34_col10, #T_a496e_row34_col11, #T_a496e_row34_col12, #T_a496e_row34_col13, #T_a496e_row34_col14, #T_a496e_row34_col15, #T_a496e_row34_col16, #T_a496e_row34_col17, #T_a496e_row34_col18, #T_a496e_row34_col20, #T_a496e_row34_col21, #T_a496e_row34_col23, #T_a496e_row34_col24, #T_a496e_row34_col25, #T_a496e_row34_col29, #T_a496e_row34_col30, #T_a496e_row34_col31, #T_a496e_row34_col32, #T_a496e_row34_col33, #T_a496e_row35_col0, #T_a496e_row35_col1, #T_a496e_row35_col2, #T_a496e_row35_col3, #T_a496e_row35_col7, #T_a496e_row35_col8, #T_a496e_row35_col9, #T_a496e_row35_col10, #T_a496e_row35_col11, #T_a496e_row35_col12, #T_a496e_row35_col13, #T_a496e_row35_col14, #T_a496e_row35_col15, #T_a496e_row35_col16, #T_a496e_row35_col17, #T_a496e_row35_col18, #T_a496e_row35_col20, #T_a496e_row35_col21, #T_a496e_row35_col23, #T_a496e_row35_col24, #T_a496e_row35_col25, #T_a496e_row35_col29, #T_a496e_row35_col30, #T_a496e_row35_col31, #T_a496e_row35_col32, #T_a496e_row35_col33, #T_a496e_row36_col0, #T_a496e_row36_col1, #T_a496e_row36_col2, #T_a496e_row36_col3, #T_a496e_row36_col7, #T_a496e_row36_col8, #T_a496e_row36_col9, #T_a496e_row36_col10, #T_a496e_row36_col11, #T_a496e_row36_col12, #T_a496e_row36_col13, #T_a496e_row36_col14, #T_a496e_row36_col15, #T_a496e_row36_col16, #T_a496e_row36_col17, #T_a496e_row36_col18, #T_a496e_row36_col20, #T_a496e_row36_col21, #T_a496e_row36_col23, #T_a496e_row36_col24, #T_a496e_row36_col25, #T_a496e_row36_col29, #T_a496e_row36_col30, #T_a496e_row36_col31, #T_a496e_row36_col32, #T_a496e_row36_col33, #T_a496e_row37_col0, #T_a496e_row37_col1, #T_a496e_row37_col2, #T_a496e_row37_col3, #T_a496e_row37_col7, #T_a496e_row37_col8, #T_a496e_row37_col9, #T_a496e_row37_col10, #T_a496e_row37_col11, #T_a496e_row37_col12, #T_a496e_row37_col13, #T_a496e_row37_col14, #T_a496e_row37_col15, #T_a496e_row37_col16, #T_a496e_row37_col17, #T_a496e_row37_col18, #T_a496e_row37_col20, #T_a496e_row37_col21, #T_a496e_row37_col23, #T_a496e_row37_col24, #T_a496e_row37_col25, #T_a496e_row37_col29, #T_a496e_row37_col30, #T_a496e_row37_col31, #T_a496e_row37_col32, #T_a496e_row37_col33, #T_a496e_row38_col0, #T_a496e_row38_col1, #T_a496e_row38_col2, #T_a496e_row38_col3, #T_a496e_row38_col7, #T_a496e_row38_col8, #T_a496e_row38_col9, #T_a496e_row38_col10, #T_a496e_row38_col11, #T_a496e_row38_col12, #T_a496e_row38_col13, #T_a496e_row38_col14, #T_a496e_row38_col15, #T_a496e_row38_col16, #T_a496e_row38_col17, #T_a496e_row38_col18, #T_a496e_row38_col20, #T_a496e_row38_col21, #T_a496e_row38_col23, #T_a496e_row38_col24, #T_a496e_row38_col25, #T_a496e_row38_col29, #T_a496e_row38_col30, #T_a496e_row38_col31, #T_a496e_row38_col32, #T_a496e_row38_col33, #T_a496e_row39_col0, #T_a496e_row39_col1, #T_a496e_row39_col2, #T_a496e_row39_col3, #T_a496e_row39_col7, #T_a496e_row39_col8, #T_a496e_row39_col9, #T_a496e_row39_col10, #T_a496e_row39_col11, #T_a496e_row39_col12, #T_a496e_row39_col13, #T_a496e_row39_col14, #T_a496e_row39_col15, #T_a496e_row39_col16, #T_a496e_row39_col17, #T_a496e_row39_col18, #T_a496e_row39_col20, #T_a496e_row39_col21, #T_a496e_row39_col23, #T_a496e_row39_col24, #T_a496e_row39_col25, #T_a496e_row39_col29, #T_a496e_row39_col30, #T_a496e_row39_col31, #T_a496e_row39_col32, #T_a496e_row39_col33, #T_a496e_row40_col0, #T_a496e_row40_col1, #T_a496e_row40_col2, #T_a496e_row40_col3, #T_a496e_row40_col7, #T_a496e_row40_col8, #T_a496e_row40_col9, #T_a496e_row40_col10, #T_a496e_row40_col11, #T_a496e_row40_col12, #T_a496e_row40_col13, #T_a496e_row40_col14, #T_a496e_row40_col15, #T_a496e_row40_col16, #T_a496e_row40_col17, #T_a496e_row40_col18, #T_a496e_row40_col20, #T_a496e_row40_col21, #T_a496e_row40_col23, #T_a496e_row40_col24, #T_a496e_row40_col25, #T_a496e_row40_col29, #T_a496e_row40_col30, #T_a496e_row40_col31, #T_a496e_row40_col32, #T_a496e_row40_col33, #T_a496e_row41_col0, #T_a496e_row41_col1, #T_a496e_row41_col2, #T_a496e_row41_col3, #T_a496e_row41_col7, #T_a496e_row41_col8, #T_a496e_row41_col9, #T_a496e_row41_col10, #T_a496e_row41_col11, #T_a496e_row41_col12, #T_a496e_row41_col13, #T_a496e_row41_col14, #T_a496e_row41_col15, #T_a496e_row41_col16, #T_a496e_row41_col17, #T_a496e_row41_col18, #T_a496e_row41_col20, #T_a496e_row41_col21, #T_a496e_row41_col23, #T_a496e_row41_col24, #T_a496e_row41_col25, #T_a496e_row41_col29, #T_a496e_row41_col30, #T_a496e_row41_col31, #T_a496e_row41_col32, #T_a496e_row41_col33, #T_a496e_row42_col0, #T_a496e_row42_col1, #T_a496e_row42_col2, #T_a496e_row42_col3, #T_a496e_row42_col7, #T_a496e_row42_col8, #T_a496e_row42_col9, #T_a496e_row42_col10, #T_a496e_row42_col11, #T_a496e_row42_col12, #T_a496e_row42_col13, #T_a496e_row42_col14, #T_a496e_row42_col15, #T_a496e_row42_col16, #T_a496e_row42_col17, #T_a496e_row42_col18, #T_a496e_row42_col20, #T_a496e_row42_col21, #T_a496e_row42_col23, #T_a496e_row42_col24, #T_a496e_row42_col25, #T_a496e_row42_col29, #T_a496e_row42_col30, #T_a496e_row42_col31, #T_a496e_row42_col32, #T_a496e_row42_col33, #T_a496e_row43_col0, #T_a496e_row43_col1, #T_a496e_row43_col2, #T_a496e_row43_col3, #T_a496e_row43_col7, #T_a496e_row43_col8, #T_a496e_row43_col9, #T_a496e_row43_col10, #T_a496e_row43_col11, #T_a496e_row43_col12, #T_a496e_row43_col13, #T_a496e_row43_col14, #T_a496e_row43_col15, #T_a496e_row43_col16, #T_a496e_row43_col17, #T_a496e_row43_col18, #T_a496e_row43_col20, #T_a496e_row43_col21, #T_a496e_row43_col23, #T_a496e_row43_col24, #T_a496e_row43_col25, #T_a496e_row43_col29, #T_a496e_row43_col30, #T_a496e_row43_col31, #T_a496e_row43_col32, #T_a496e_row43_col33, #T_a496e_row44_col0, #T_a496e_row44_col1, #T_a496e_row44_col2, #T_a496e_row44_col3, #T_a496e_row44_col7, #T_a496e_row44_col8, #T_a496e_row44_col9, #T_a496e_row44_col10, #T_a496e_row44_col11, #T_a496e_row44_col12, #T_a496e_row44_col13, #T_a496e_row44_col14, #T_a496e_row44_col15, #T_a496e_row44_col16, #T_a496e_row44_col17, #T_a496e_row44_col18, #T_a496e_row44_col20, #T_a496e_row44_col21, #T_a496e_row44_col23, #T_a496e_row44_col24, #T_a496e_row44_col25, #T_a496e_row44_col29, #T_a496e_row44_col30, #T_a496e_row44_col31, #T_a496e_row44_col32, #T_a496e_row44_col33, #T_a496e_row45_col0, #T_a496e_row45_col1, #T_a496e_row45_col2, #T_a496e_row45_col3, #T_a496e_row45_col7, #T_a496e_row45_col8, #T_a496e_row45_col9, #T_a496e_row45_col10, #T_a496e_row45_col11, #T_a496e_row45_col12, #T_a496e_row45_col13, #T_a496e_row45_col14, #T_a496e_row45_col15, #T_a496e_row45_col16, #T_a496e_row45_col17, #T_a496e_row45_col18, #T_a496e_row45_col20, #T_a496e_row45_col21, #T_a496e_row45_col23, #T_a496e_row45_col24, #T_a496e_row45_col25, #T_a496e_row45_col29, #T_a496e_row45_col30, #T_a496e_row45_col31, #T_a496e_row45_col32, #T_a496e_row45_col33, #T_a496e_row46_col0, #T_a496e_row46_col1, #T_a496e_row46_col2, #T_a496e_row46_col3, #T_a496e_row46_col7, #T_a496e_row46_col8, #T_a496e_row46_col9, #T_a496e_row46_col10, #T_a496e_row46_col11, #T_a496e_row46_col12, #T_a496e_row46_col13, #T_a496e_row46_col14, #T_a496e_row46_col15, #T_a496e_row46_col16, #T_a496e_row46_col17, #T_a496e_row46_col18, #T_a496e_row46_col20, #T_a496e_row46_col21, #T_a496e_row46_col23, #T_a496e_row46_col24, #T_a496e_row46_col25, #T_a496e_row46_col29, #T_a496e_row46_col30, #T_a496e_row46_col31, #T_a496e_row46_col32, #T_a496e_row46_col33, #T_a496e_row47_col0, #T_a496e_row47_col1, #T_a496e_row47_col2, #T_a496e_row47_col3, #T_a496e_row47_col7, #T_a496e_row47_col8, #T_a496e_row47_col9, #T_a496e_row47_col10, #T_a496e_row47_col11, #T_a496e_row47_col12, #T_a496e_row47_col13, #T_a496e_row47_col14, #T_a496e_row47_col15, #T_a496e_row47_col16, #T_a496e_row47_col17, #T_a496e_row47_col18, #T_a496e_row47_col20, #T_a496e_row47_col21, #T_a496e_row47_col23, #T_a496e_row47_col24, #T_a496e_row47_col25, #T_a496e_row47_col29, #T_a496e_row47_col30, #T_a496e_row47_col31, #T_a496e_row47_col32, #T_a496e_row47_col33, #T_a496e_row48_col0, #T_a496e_row48_col1, #T_a496e_row48_col2, #T_a496e_row48_col3, #T_a496e_row48_col7, #T_a496e_row48_col8, #T_a496e_row48_col9, #T_a496e_row48_col10, #T_a496e_row48_col11, #T_a496e_row48_col12, #T_a496e_row48_col13, #T_a496e_row48_col14, #T_a496e_row48_col15, #T_a496e_row48_col16, #T_a496e_row48_col17, #T_a496e_row48_col18, #T_a496e_row48_col20, #T_a496e_row48_col21, #T_a496e_row48_col23, #T_a496e_row48_col24, #T_a496e_row48_col25, #T_a496e_row48_col29, #T_a496e_row48_col30, #T_a496e_row48_col31, #T_a496e_row48_col32, #T_a496e_row48_col33, #T_a496e_row49_col0, #T_a496e_row49_col1, #T_a496e_row49_col2, #T_a496e_row49_col3, #T_a496e_row49_col7, #T_a496e_row49_col8, #T_a496e_row49_col9, #T_a496e_row49_col10, #T_a496e_row49_col11, #T_a496e_row49_col12, #T_a496e_row49_col13, #T_a496e_row49_col14, #T_a496e_row49_col15, #T_a496e_row49_col16, #T_a496e_row49_col17, #T_a496e_row49_col18, #T_a496e_row49_col20, #T_a496e_row49_col21, #T_a496e_row49_col23, #T_a496e_row49_col24, #T_a496e_row49_col25, #T_a496e_row49_col29, #T_a496e_row49_col30, #T_a496e_row49_col31, #T_a496e_row49_col32, #T_a496e_row49_col33, #T_a496e_row50_col0, #T_a496e_row50_col1, #T_a496e_row50_col2, #T_a496e_row50_col3, #T_a496e_row50_col7, #T_a496e_row50_col8, #T_a496e_row50_col9, #T_a496e_row50_col10, #T_a496e_row50_col11, #T_a496e_row50_col12, #T_a496e_row50_col13, #T_a496e_row50_col14, #T_a496e_row50_col15, #T_a496e_row50_col16, #T_a496e_row50_col17, #T_a496e_row50_col18, #T_a496e_row50_col20, #T_a496e_row50_col21, #T_a496e_row50_col23, #T_a496e_row50_col24, #T_a496e_row50_col25, #T_a496e_row50_col29, #T_a496e_row50_col30, #T_a496e_row50_col31, #T_a496e_row50_col32, #T_a496e_row50_col33, #T_a496e_row51_col0, #T_a496e_row51_col1, #T_a496e_row51_col2, #T_a496e_row51_col3, #T_a496e_row51_col7, #T_a496e_row51_col8, #T_a496e_row51_col9, #T_a496e_row51_col10, #T_a496e_row51_col11, #T_a496e_row51_col12, #T_a496e_row51_col13, #T_a496e_row51_col14, #T_a496e_row51_col15, #T_a496e_row51_col16, #T_a496e_row51_col17, #T_a496e_row51_col18, #T_a496e_row51_col20, #T_a496e_row51_col21, #T_a496e_row51_col23, #T_a496e_row51_col24, #T_a496e_row51_col25, #T_a496e_row51_col29, #T_a496e_row51_col30, #T_a496e_row51_col31, #T_a496e_row51_col32, #T_a496e_row51_col33, #T_a496e_row52_col0, #T_a496e_row52_col1, #T_a496e_row52_col2, #T_a496e_row52_col3, #T_a496e_row52_col7, #T_a496e_row52_col8, #T_a496e_row52_col9, #T_a496e_row52_col10, #T_a496e_row52_col11, #T_a496e_row52_col12, #T_a496e_row52_col13, #T_a496e_row52_col14, #T_a496e_row52_col15, #T_a496e_row52_col16, #T_a496e_row52_col17, #T_a496e_row52_col18, #T_a496e_row52_col20, #T_a496e_row52_col21, #T_a496e_row52_col23, #T_a496e_row52_col24, #T_a496e_row52_col25, #T_a496e_row52_col29, #T_a496e_row52_col30, #T_a496e_row52_col31, #T_a496e_row52_col32, #T_a496e_row52_col33, #T_a496e_row53_col0, #T_a496e_row53_col1, #T_a496e_row53_col2, #T_a496e_row53_col3, #T_a496e_row53_col7, #T_a496e_row53_col8, #T_a496e_row53_col9, #T_a496e_row53_col10, #T_a496e_row53_col11, #T_a496e_row53_col12, #T_a496e_row53_col13, #T_a496e_row53_col14, #T_a496e_row53_col15, #T_a496e_row53_col16, #T_a496e_row53_col17, #T_a496e_row53_col18, #T_a496e_row53_col20, #T_a496e_row53_col21, #T_a496e_row53_col23, #T_a496e_row53_col24, #T_a496e_row53_col25, #T_a496e_row53_col29, #T_a496e_row53_col30, #T_a496e_row53_col31, #T_a496e_row53_col32, #T_a496e_row53_col33, #T_a496e_row54_col0, #T_a496e_row54_col1, #T_a496e_row54_col2, #T_a496e_row54_col3, #T_a496e_row54_col7, #T_a496e_row54_col8, #T_a496e_row54_col9, #T_a496e_row54_col10, #T_a496e_row54_col11, #T_a496e_row54_col12, #T_a496e_row54_col13, #T_a496e_row54_col14, #T_a496e_row54_col15, #T_a496e_row54_col16, #T_a496e_row54_col17, #T_a496e_row54_col18, #T_a496e_row54_col20, #T_a496e_row54_col21, #T_a496e_row54_col23, #T_a496e_row54_col24, #T_a496e_row54_col25, #T_a496e_row54_col29, #T_a496e_row54_col30, #T_a496e_row54_col31, #T_a496e_row54_col32, #T_a496e_row54_col33, #T_a496e_row55_col0, #T_a496e_row55_col1, #T_a496e_row55_col2, #T_a496e_row55_col3, #T_a496e_row55_col7, #T_a496e_row55_col8, #T_a496e_row55_col9, #T_a496e_row55_col10, #T_a496e_row55_col11, #T_a496e_row55_col12, #T_a496e_row55_col13, #T_a496e_row55_col14, #T_a496e_row55_col15, #T_a496e_row55_col16, #T_a496e_row55_col17, #T_a496e_row55_col18, #T_a496e_row55_col20, #T_a496e_row55_col21, #T_a496e_row55_col23, #T_a496e_row55_col24, #T_a496e_row55_col25, #T_a496e_row55_col29, #T_a496e_row55_col30, #T_a496e_row55_col31, #T_a496e_row55_col32, #T_a496e_row55_col33, #T_a496e_row56_col0, #T_a496e_row56_col1, #T_a496e_row56_col2, #T_a496e_row56_col3, #T_a496e_row56_col7, #T_a496e_row56_col8, #T_a496e_row56_col9, #T_a496e_row56_col10, #T_a496e_row56_col11, #T_a496e_row56_col12, #T_a496e_row56_col13, #T_a496e_row56_col14, #T_a496e_row56_col15, #T_a496e_row56_col16, #T_a496e_row56_col17, #T_a496e_row56_col18, #T_a496e_row56_col20, #T_a496e_row56_col21, #T_a496e_row56_col23, #T_a496e_row56_col24, #T_a496e_row56_col25, #T_a496e_row56_col29, #T_a496e_row56_col30, #T_a496e_row56_col31, #T_a496e_row56_col32, #T_a496e_row56_col33, #T_a496e_row57_col0, #T_a496e_row57_col1, #T_a496e_row57_col2, #T_a496e_row57_col3, #T_a496e_row57_col7, #T_a496e_row57_col8, #T_a496e_row57_col9, #T_a496e_row57_col10, #T_a496e_row57_col11, #T_a496e_row57_col12, #T_a496e_row57_col13, #T_a496e_row57_col14, #T_a496e_row57_col15, #T_a496e_row57_col16, #T_a496e_row57_col17, #T_a496e_row57_col18, #T_a496e_row57_col20, #T_a496e_row57_col21, #T_a496e_row57_col23, #T_a496e_row57_col24, #T_a496e_row57_col25, #T_a496e_row57_col29, #T_a496e_row57_col30, #T_a496e_row57_col31, #T_a496e_row57_col32, #T_a496e_row57_col33, #T_a496e_row58_col0, #T_a496e_row58_col1, #T_a496e_row58_col2, #T_a496e_row58_col3, #T_a496e_row58_col7, #T_a496e_row58_col8, #T_a496e_row58_col9, #T_a496e_row58_col10, #T_a496e_row58_col11, #T_a496e_row58_col12, #T_a496e_row58_col13, #T_a496e_row58_col14, #T_a496e_row58_col15, #T_a496e_row58_col16, #T_a496e_row58_col17, #T_a496e_row58_col18, #T_a496e_row58_col20, #T_a496e_row58_col21, #T_a496e_row58_col23, #T_a496e_row58_col24, #T_a496e_row58_col25, #T_a496e_row58_col29, #T_a496e_row58_col30, #T_a496e_row58_col31, #T_a496e_row58_col32, #T_a496e_row58_col33, #T_a496e_row59_col0, #T_a496e_row59_col1, #T_a496e_row59_col2, #T_a496e_row59_col3, #T_a496e_row59_col7, #T_a496e_row59_col8, #T_a496e_row59_col9, #T_a496e_row59_col10, #T_a496e_row59_col11, #T_a496e_row59_col12, #T_a496e_row59_col13, #T_a496e_row59_col14, #T_a496e_row59_col15, #T_a496e_row59_col16, #T_a496e_row59_col17, #T_a496e_row59_col18, #T_a496e_row59_col20, #T_a496e_row59_col21, #T_a496e_row59_col23, #T_a496e_row59_col24, #T_a496e_row59_col25, #T_a496e_row59_col29, #T_a496e_row59_col30, #T_a496e_row59_col31, #T_a496e_row59_col32, #T_a496e_row59_col33, #T_a496e_row60_col0, #T_a496e_row60_col1, #T_a496e_row60_col2, #T_a496e_row60_col3, #T_a496e_row60_col7, #T_a496e_row60_col8, #T_a496e_row60_col9, #T_a496e_row60_col10, #T_a496e_row60_col11, #T_a496e_row60_col12, #T_a496e_row60_col13, #T_a496e_row60_col14, #T_a496e_row60_col15, #T_a496e_row60_col16, #T_a496e_row60_col17, #T_a496e_row60_col18, #T_a496e_row60_col20, #T_a496e_row60_col21, #T_a496e_row60_col23, #T_a496e_row60_col24, #T_a496e_row60_col25, #T_a496e_row60_col29, #T_a496e_row60_col30, #T_a496e_row60_col31, #T_a496e_row60_col32, #T_a496e_row60_col33, #T_a496e_row61_col0, #T_a496e_row61_col1, #T_a496e_row61_col2, #T_a496e_row61_col3, #T_a496e_row61_col7, #T_a496e_row61_col8, #T_a496e_row61_col9, #T_a496e_row61_col10, #T_a496e_row61_col11, #T_a496e_row61_col12, #T_a496e_row61_col13, #T_a496e_row61_col14, #T_a496e_row61_col15, #T_a496e_row61_col16, #T_a496e_row61_col17, #T_a496e_row61_col18, #T_a496e_row61_col20, #T_a496e_row61_col21, #T_a496e_row61_col23, #T_a496e_row61_col24, #T_a496e_row61_col25, #T_a496e_row61_col29, #T_a496e_row61_col30, #T_a496e_row61_col31, #T_a496e_row61_col32, #T_a496e_row61_col33, #T_a496e_row62_col0, #T_a496e_row62_col1, #T_a496e_row62_col2, #T_a496e_row62_col3, #T_a496e_row62_col7, #T_a496e_row62_col8, #T_a496e_row62_col9, #T_a496e_row62_col10, #T_a496e_row62_col11, #T_a496e_row62_col12, #T_a496e_row62_col13, #T_a496e_row62_col14, #T_a496e_row62_col15, #T_a496e_row62_col16, #T_a496e_row62_col17, #T_a496e_row62_col18, #T_a496e_row62_col20, #T_a496e_row62_col21, #T_a496e_row62_col23, #T_a496e_row62_col24, #T_a496e_row62_col25, #T_a496e_row62_col29, #T_a496e_row62_col30, #T_a496e_row62_col31, #T_a496e_row62_col32, #T_a496e_row62_col33, #T_a496e_row63_col0, #T_a496e_row63_col1, #T_a496e_row63_col2, #T_a496e_row63_col3, #T_a496e_row63_col7, #T_a496e_row63_col8, #T_a496e_row63_col9, #T_a496e_row63_col10, #T_a496e_row63_col11, #T_a496e_row63_col12, #T_a496e_row63_col13, #T_a496e_row63_col14, #T_a496e_row63_col15, #T_a496e_row63_col16, #T_a496e_row63_col17, #T_a496e_row63_col18, #T_a496e_row63_col20, #T_a496e_row63_col21, #T_a496e_row63_col23, #T_a496e_row63_col24, #T_a496e_row63_col25, #T_a496e_row63_col29, #T_a496e_row63_col30, #T_a496e_row63_col31, #T_a496e_row63_col32, #T_a496e_row63_col33, #T_a496e_row64_col0, #T_a496e_row64_col1, #T_a496e_row64_col2, #T_a496e_row64_col3, #T_a496e_row64_col7, #T_a496e_row64_col8, #T_a496e_row64_col9, #T_a496e_row64_col10, #T_a496e_row64_col11, #T_a496e_row64_col12, #T_a496e_row64_col13, #T_a496e_row64_col14, #T_a496e_row64_col15, #T_a496e_row64_col16, #T_a496e_row64_col17, #T_a496e_row64_col18, #T_a496e_row64_col20, #T_a496e_row64_col21, #T_a496e_row64_col23, #T_a496e_row64_col24, #T_a496e_row64_col25, #T_a496e_row64_col29, #T_a496e_row64_col30, #T_a496e_row64_col31, #T_a496e_row64_col32, #T_a496e_row64_col33, #T_a496e_row65_col0, #T_a496e_row65_col1, #T_a496e_row65_col2, #T_a496e_row65_col3, #T_a496e_row65_col7, #T_a496e_row65_col8, #T_a496e_row65_col9, #T_a496e_row65_col10, #T_a496e_row65_col11, #T_a496e_row65_col12, #T_a496e_row65_col13, #T_a496e_row65_col14, #T_a496e_row65_col15, #T_a496e_row65_col16, #T_a496e_row65_col17, #T_a496e_row65_col18, #T_a496e_row65_col20, #T_a496e_row65_col21, #T_a496e_row65_col23, #T_a496e_row65_col24, #T_a496e_row65_col25, #T_a496e_row65_col29, #T_a496e_row65_col30, #T_a496e_row65_col31, #T_a496e_row65_col32, #T_a496e_row65_col33, #T_a496e_row66_col0, #T_a496e_row66_col1, #T_a496e_row66_col2, #T_a496e_row66_col3, #T_a496e_row66_col7, #T_a496e_row66_col8, #T_a496e_row66_col9, #T_a496e_row66_col10, #T_a496e_row66_col11, #T_a496e_row66_col12, #T_a496e_row66_col13, #T_a496e_row66_col14, #T_a496e_row66_col15, #T_a496e_row66_col16, #T_a496e_row66_col17, #T_a496e_row66_col18, #T_a496e_row66_col20, #T_a496e_row66_col21, #T_a496e_row66_col23, #T_a496e_row66_col24, #T_a496e_row66_col25, #T_a496e_row66_col29, #T_a496e_row66_col30, #T_a496e_row66_col31, #T_a496e_row66_col32, #T_a496e_row66_col33, #T_a496e_row67_col0, #T_a496e_row67_col1, #T_a496e_row67_col2, #T_a496e_row67_col3, #T_a496e_row67_col7, #T_a496e_row67_col8, #T_a496e_row67_col9, #T_a496e_row67_col10, #T_a496e_row67_col11, #T_a496e_row67_col12, #T_a496e_row67_col13, #T_a496e_row67_col14, #T_a496e_row67_col15, #T_a496e_row67_col16, #T_a496e_row67_col17, #T_a496e_row67_col18, #T_a496e_row67_col20, #T_a496e_row67_col21, #T_a496e_row67_col23, #T_a496e_row67_col24, #T_a496e_row67_col25, #T_a496e_row67_col29, #T_a496e_row67_col30, #T_a496e_row67_col31, #T_a496e_row67_col32, #T_a496e_row67_col33 {
  white-space: pre-wrap;
}
#T_a496e_row0_col4, #T_a496e_row0_col5, #T_a496e_row0_col19, #T_a496e_row0_col22, #T_a496e_row0_col26, #T_a496e_row0_col27, #T_a496e_row0_col28, #T_a496e_row1_col4, #T_a496e_row1_col19, #T_a496e_row1_col22, #T_a496e_row1_col26, #T_a496e_row1_col27, #T_a496e_row1_col28, #T_a496e_row2_col4, #T_a496e_row2_col5, #T_a496e_row2_col19, #T_a496e_row2_col22, #T_a496e_row2_col26, #T_a496e_row2_col27, #T_a496e_row2_col28, #T_a496e_row3_col4, #T_a496e_row3_col19, #T_a496e_row3_col22, #T_a496e_row3_col26, #T_a496e_row3_col27, #T_a496e_row3_col28, #T_a496e_row4_col4, #T_a496e_row4_col5, #T_a496e_row4_col19, #T_a496e_row4_col26, #T_a496e_row4_col27, #T_a496e_row4_col28, #T_a496e_row5_col4, #T_a496e_row5_col19, #T_a496e_row5_col26, #T_a496e_row5_col27, #T_a496e_row5_col28, #T_a496e_row6_col4, #T_a496e_row6_col5, #T_a496e_row6_col19, #T_a496e_row6_col22, #T_a496e_row6_col26, #T_a496e_row6_col27, #T_a496e_row6_col28, #T_a496e_row7_col4, #T_a496e_row7_col19, #T_a496e_row7_col22, #T_a496e_row7_col26, #T_a496e_row7_col27, #T_a496e_row7_col28, #T_a496e_row8_col4, #T_a496e_row8_col5, #T_a496e_row8_col19, #T_a496e_row8_col22, #T_a496e_row8_col26, #T_a496e_row8_col27, #T_a496e_row8_col28, #T_a496e_row9_col4, #T_a496e_row9_col19, #T_a496e_row9_col22, #T_a496e_row9_col26, #T_a496e_row9_col27, #T_a496e_row9_col28, #T_a496e_row10_col4, #T_a496e_row10_col5, #T_a496e_row10_col19, #T_a496e_row10_col26, #T_a496e_row10_col27, #T_a496e_row10_col28, #T_a496e_row11_col4, #T_a496e_row11_col19, #T_a496e_row11_col26, #T_a496e_row11_col27, #T_a496e_row11_col28, #T_a496e_row12_col4, #T_a496e_row12_col5, #T_a496e_row12_col19, #T_a496e_row12_col22, #T_a496e_row12_col26, #T_a496e_row12_col27, #T_a496e_row12_col28, #T_a496e_row13_col4, #T_a496e_row13_col19, #T_a496e_row13_col22, #T_a496e_row13_col26, #T_a496e_row13_col27, #T_a496e_row13_col28, #T_a496e_row14_col4, #T_a496e_row14_col5, #T_a496e_row14_col19, #T_a496e_row14_col22, #T_a496e_row14_col26, #T_a496e_row14_col27, #T_a496e_row14_col28, #T_a496e_row15_col4, #T_a496e_row15_col19, #T_a496e_row15_col22, #T_a496e_row15_col26, #T_a496e_row15_col27, #T_a496e_row15_col28, #T_a496e_row16_col4, #T_a496e_row16_col5, #T_a496e_row17_col4, #T_a496e_row18_col4, #T_a496e_row18_col5, #T_a496e_row18_col19, #T_a496e_row18_col22, #T_a496e_row18_col26, #T_a496e_row18_col27, #T_a496e_row18_col28, #T_a496e_row19_col4, #T_a496e_row19_col19, #T_a496e_row19_col22, #T_a496e_row19_col26, #T_a496e_row19_col27, #T_a496e_row19_col28, #T_a496e_row20_col4, #T_a496e_row20_col5, #T_a496e_row20_col19, #T_a496e_row20_col26, #T_a496e_row20_col27, #T_a496e_row20_col28, #T_a496e_row21_col4, #T_a496e_row21_col19, #T_a496e_row21_col26, #T_a496e_row21_col27, #T_a496e_row21_col28, #T_a496e_row22_col4, #T_a496e_row22_col5, #T_a496e_row22_col19, #T_a496e_row22_col22, #T_a496e_row22_col26, #T_a496e_row22_col27, #T_a496e_row22_col28, #T_a496e_row23_col4, #T_a496e_row23_col19, #T_a496e_row23_col22, #T_a496e_row23_col26, #T_a496e_row23_col27, #T_a496e_row23_col28, #T_a496e_row24_col4, #T_a496e_row24_col5, #T_a496e_row24_col19, #T_a496e_row24_col26, #T_a496e_row24_col27, #T_a496e_row24_col28, #T_a496e_row25_col4, #T_a496e_row25_col19, #T_a496e_row25_col26, #T_a496e_row25_col27, #T_a496e_row25_col28, #T_a496e_row26_col4, #T_a496e_row26_col5, #T_a496e_row26_col19, #T_a496e_row26_col26, #T_a496e_row26_col27, #T_a496e_row26_col28, #T_a496e_row27_col4, #T_a496e_row27_col19, #T_a496e_row27_col26, #T_a496e_row27_col27, #T_a496e_row27_col28, #T_a496e_row28_col4, #T_a496e_row28_col5, #T_a496e_row28_col19, #T_a496e_row28_col22, #T_a496e_row29_col4, #T_a496e_row29_col19, #T_a496e_row29_col22, #T_a496e_row30_col4, #T_a496e_row30_col5, #T_a496e_row30_col19, #T_a496e_row30_col22, #T_a496e_row30_col26, #T_a496e_row30_col27, #T_a496e_row30_col28, #T_a496e_row31_col4, #T_a496e_row31_col19, #T_a496e_row31_col22, #T_a496e_row31_col26, #T_a496e_row31_col27, #T_a496e_row31_col28, #T_a496e_row32_col4, #T_a496e_row32_col5, #T_a496e_row32_col19, #T_a496e_row32_col22, #T_a496e_row32_col26, #T_a496e_row32_col27, #T_a496e_row32_col28, #T_a496e_row33_col4, #T_a496e_row33_col19, #T_a496e_row33_col22, #T_a496e_row33_col26, #T_a496e_row33_col27, #T_a496e_row33_col28, #T_a496e_row34_col4, #T_a496e_row34_col5, #T_a496e_row34_col19, #T_a496e_row34_col26, #T_a496e_row34_col27, #T_a496e_row34_col28, #T_a496e_row35_col4, #T_a496e_row35_col19, #T_a496e_row35_col26, #T_a496e_row35_col27, #T_a496e_row35_col28, #T_a496e_row36_col4, #T_a496e_row36_col5, #T_a496e_row36_col19, #T_a496e_row36_col22, #T_a496e_row36_col26, #T_a496e_row36_col27, #T_a496e_row36_col28, #T_a496e_row37_col4, #T_a496e_row37_col19, #T_a496e_row37_col22, #T_a496e_row37_col26, #T_a496e_row37_col27, #T_a496e_row37_col28, #T_a496e_row38_col4, #T_a496e_row38_col5, #T_a496e_row38_col19, #T_a496e_row38_col22, #T_a496e_row38_col26, #T_a496e_row38_col27, #T_a496e_row38_col28, #T_a496e_row39_col4, #T_a496e_row39_col19, #T_a496e_row39_col22, #T_a496e_row39_col26, #T_a496e_row39_col27, #T_a496e_row39_col28, #T_a496e_row40_col4, #T_a496e_row40_col5, #T_a496e_row40_col19, #T_a496e_row40_col22, #T_a496e_row40_col26, #T_a496e_row40_col27, #T_a496e_row40_col28, #T_a496e_row41_col4, #T_a496e_row41_col19, #T_a496e_row41_col22, #T_a496e_row41_col26, #T_a496e_row41_col27, #T_a496e_row41_col28, #T_a496e_row42_col4, #T_a496e_row42_col5, #T_a496e_row42_col19, #T_a496e_row42_col22, #T_a496e_row42_col26, #T_a496e_row42_col27, #T_a496e_row42_col28, #T_a496e_row43_col4, #T_a496e_row43_col19, #T_a496e_row43_col22, #T_a496e_row43_col26, #T_a496e_row43_col27, #T_a496e_row43_col28, #T_a496e_row44_col4, #T_a496e_row44_col5, #T_a496e_row44_col19, #T_a496e_row44_col22, #T_a496e_row44_col26, #T_a496e_row44_col27, #T_a496e_row44_col28, #T_a496e_row45_col4, #T_a496e_row45_col19, #T_a496e_row45_col22, #T_a496e_row45_col26, #T_a496e_row45_col27, #T_a496e_row45_col28, #T_a496e_row46_col4, #T_a496e_row46_col5, #T_a496e_row46_col19, #T_a496e_row46_col26, #T_a496e_row46_col27, #T_a496e_row46_col28, #T_a496e_row47_col4, #T_a496e_row47_col19, #T_a496e_row47_col26, #T_a496e_row47_col27, #T_a496e_row47_col28, #T_a496e_row48_col4, #T_a496e_row48_col5, #T_a496e_row48_col19, #T_a496e_row48_col22, #T_a496e_row48_col26, #T_a496e_row48_col27, #T_a496e_row48_col28, #T_a496e_row49_col4, #T_a496e_row49_col19, #T_a496e_row49_col22, #T_a496e_row49_col26, #T_a496e_row49_col27, #T_a496e_row49_col28, #T_a496e_row50_col4, #T_a496e_row50_col5, #T_a496e_row50_col19, #T_a496e_row50_col22, #T_a496e_row50_col26, #T_a496e_row50_col27, #T_a496e_row50_col28, #T_a496e_row51_col4, #T_a496e_row51_col19, #T_a496e_row51_col22, #T_a496e_row51_col26, #T_a496e_row51_col27, #T_a496e_row51_col28, #T_a496e_row52_col4, #T_a496e_row52_col5, #T_a496e_row52_col19, #T_a496e_row52_col22, #T_a496e_row52_col26, #T_a496e_row52_col27, #T_a496e_row52_col28, #T_a496e_row53_col4, #T_a496e_row53_col19, #T_a496e_row53_col22, #T_a496e_row53_col26, #T_a496e_row53_col27, #T_a496e_row53_col28, #T_a496e_row54_col4, #T_a496e_row54_col5, #T_a496e_row54_col19, #T_a496e_row54_col22, #T_a496e_row54_col26, #T_a496e_row54_col27, #T_a496e_row54_col28, #T_a496e_row55_col4, #T_a496e_row55_col19, #T_a496e_row55_col22, #T_a496e_row55_col26, #T_a496e_row55_col27, #T_a496e_row55_col28, #T_a496e_row56_col4, #T_a496e_row56_col5, #T_a496e_row56_col19, #T_a496e_row56_col22, #T_a496e_row56_col26, #T_a496e_row56_col27, #T_a496e_row56_col28, #T_a496e_row57_col4, #T_a496e_row57_col19, #T_a496e_row57_col22, #T_a496e_row57_col26, #T_a496e_row57_col27, #T_a496e_row57_col28, #T_a496e_row58_col4, #T_a496e_row58_col5, #T_a496e_row58_col19, #T_a496e_row58_col22, #T_a496e_row58_col26, #T_a496e_row58_col27, #T_a496e_row58_col28, #T_a496e_row59_col4, #T_a496e_row59_col19, #T_a496e_row59_col22, #T_a496e_row59_col26, #T_a496e_row59_col27, #T_a496e_row59_col28, #T_a496e_row60_col4, #T_a496e_row60_col5, #T_a496e_row60_col19, #T_a496e_row60_col22, #T_a496e_row60_col26, #T_a496e_row60_col27, #T_a496e_row60_col28, #T_a496e_row61_col4, #T_a496e_row61_col19, #T_a496e_row61_col22, #T_a496e_row61_col26, #T_a496e_row61_col27, #T_a496e_row61_col28, #T_a496e_row62_col4, #T_a496e_row62_col5, #T_a496e_row62_col19, #T_a496e_row62_col22, #T_a496e_row62_col26, #T_a496e_row62_col27, #T_a496e_row62_col28, #T_a496e_row63_col4, #T_a496e_row63_col19, #T_a496e_row63_col22, #T_a496e_row63_col26, #T_a496e_row63_col27, #T_a496e_row63_col28, #T_a496e_row64_col4, #T_a496e_row64_col5, #T_a496e_row64_col19, #T_a496e_row64_col22, #T_a496e_row64_col26, #T_a496e_row64_col27, #T_a496e_row64_col28, #T_a496e_row65_col4, #T_a496e_row65_col19, #T_a496e_row65_col22, #T_a496e_row65_col26, #T_a496e_row65_col27, #T_a496e_row65_col28, #T_a496e_row66_col4, #T_a496e_row66_col5, #T_a496e_row66_col19, #T_a496e_row66_col22, #T_a496e_row66_col26, #T_a496e_row66_col27, #T_a496e_row66_col28, #T_a496e_row67_col4, #T_a496e_row67_col19, #T_a496e_row67_col22, #T_a496e_row67_col26, #T_a496e_row67_col27, #T_a496e_row67_col28 {
  background-color: #E8F5E9;
  color: #0b8457;
  font-weight: 600;
  white-space: pre-wrap;
}
#T_a496e_row0_col6, #T_a496e_row2_col6, #T_a496e_row4_col6, #T_a496e_row6_col6, #T_a496e_row8_col6, #T_a496e_row10_col6, #T_a496e_row12_col6, #T_a496e_row14_col6, #T_a496e_row16_col6, #T_a496e_row18_col6, #T_a496e_row20_col6, #T_a496e_row22_col6, #T_a496e_row24_col6, #T_a496e_row26_col6, #T_a496e_row28_col6, #T_a496e_row30_col6, #T_a496e_row32_col6, #T_a496e_row34_col6, #T_a496e_row36_col6, #T_a496e_row38_col6, #T_a496e_row40_col6, #T_a496e_row42_col6, #T_a496e_row44_col6, #T_a496e_row46_col6, #T_a496e_row48_col6, #T_a496e_row50_col6, #T_a496e_row52_col6, #T_a496e_row54_col6, #T_a496e_row56_col6, #T_a496e_row58_col6, #T_a496e_row60_col6, #T_a496e_row62_col6, #T_a496e_row64_col6, #T_a496e_row66_col6 {
  background-color: #C8E6C9;
  color: #1B5E20;
  font-weight: 600;
  white-space: pre-wrap;
}
#T_a496e_row1_col5, #T_a496e_row3_col5, #T_a496e_row4_col22, #T_a496e_row5_col5, #T_a496e_row5_col22, #T_a496e_row7_col5, #T_a496e_row9_col5, #T_a496e_row10_col22, #T_a496e_row11_col5, #T_a496e_row11_col22, #T_a496e_row13_col5, #T_a496e_row15_col5, #T_a496e_row16_col19, #T_a496e_row16_col22, #T_a496e_row16_col26, #T_a496e_row16_col27, #T_a496e_row16_col28, #T_a496e_row17_col5, #T_a496e_row17_col19, #T_a496e_row17_col22, #T_a496e_row17_col26, #T_a496e_row17_col27, #T_a496e_row17_col28, #T_a496e_row19_col5, #T_a496e_row20_col22, #T_a496e_row21_col5, #T_a496e_row21_col22, #T_a496e_row23_col5, #T_a496e_row24_col22, #T_a496e_row25_col5, #T_a496e_row25_col22, #T_a496e_row26_col22, #T_a496e_row27_col5, #T_a496e_row27_col22, #T_a496e_row28_col26, #T_a496e_row28_col27, #T_a496e_row28_col28, #T_a496e_row29_col5, #T_a496e_row29_col26, #T_a496e_row29_col27, #T_a496e_row29_col28, #T_a496e_row31_col5, #T_a496e_row33_col5, #T_a496e_row34_col22, #T_a496e_row35_col5, #T_a496e_row35_col22, #T_a496e_row37_col5, #T_a496e_row39_col5, #T_a496e_row41_col5, #T_a496e_row43_col5, #T_a496e_row45_col5, #T_a496e_row46_col22, #T_a496e_row47_col5, #T_a496e_row47_col22, #T_a496e_row49_col5, #T_a496e_row51_col5, #T_a496e_row53_col5, #T_a496e_row55_col5, #T_a496e_row57_col5, #T_a496e_row59_col5, #T_a496e_row61_col5, #T_a496e_row63_col5, #T_a496e_row65_col5, #T_a496e_row67_col5 {
  background-color: #FDECEA;
  color: #b23b3b;
  font-weight: 600;
  white-space: pre-wrap;
}
#T_a496e_row1_col6, #T_a496e_row3_col6, #T_a496e_row5_col6, #T_a496e_row7_col6, #T_a496e_row9_col6, #T_a496e_row11_col6, #T_a496e_row13_col6, #T_a496e_row15_col6, #T_a496e_row17_col6, #T_a496e_row19_col6, #T_a496e_row21_col6, #T_a496e_row23_col6, #T_a496e_row25_col6, #T_a496e_row27_col6, #T_a496e_row29_col6, #T_a496e_row31_col6, #T_a496e_row33_col6, #T_a496e_row35_col6, #T_a496e_row37_col6, #T_a496e_row39_col6, #T_a496e_row41_col6, #T_a496e_row43_col6, #T_a496e_row45_col6, #T_a496e_row47_col6, #T_a496e_row49_col6, #T_a496e_row51_col6, #T_a496e_row53_col6, #T_a496e_row55_col6, #T_a496e_row57_col6, #T_a496e_row59_col6, #T_a496e_row61_col6, #T_a496e_row63_col6, #T_a496e_row65_col6, #T_a496e_row67_col6 {
  background-color: #FFF9C4;
  color: #F57F17;
  font-weight: 600;
  white-space: pre-wrap;
}
</style>
<table id="T_a496e">
  <thead>
    <tr>
      <th class="blank level0" >&nbsp;</th>
      <th id="T_a496e_level0_col0" class="col_heading level0 col0" >AutoModel</th>
      <th id="T_a496e_level0_col1" class="col_heading level0 col1" >BaseModel</th>
      <th id="T_a496e_level0_col2" class="col_heading level0 col2" >backend</th>
      <th id="T_a496e_level0_col3" class="col_heading level0 col3" >backend_choices</th>
      <th id="T_a496e_level0_col4" class="col_heading level0 col4" >pruner_available</th>
      <th id="T_a496e_level0_col5" class="col_heading level0 col5" >pruner_default_enabled</th>
      <th id="T_a496e_level0_col6" class="col_heading level0 col6" >pruner_status</th>
      <th id="T_a496e_level0_col7" class="col_heading level0 col7" >pruner_note</th>
      <th id="T_a496e_level0_col8" class="col_heading level0 col8" >search_alg</th>
      <th id="T_a496e_level0_col9" class="col_heading level0 col9" >search_alg_choices</th>
      <th id="T_a496e_level0_col10" class="col_heading level0 col10" >loss_default</th>
      <th id="T_a496e_level0_col11" class="col_heading level0 col11" >loss_choices</th>
      <th id="T_a496e_level0_col12" class="col_heading level0 col12" >valid_loss_default</th>
      <th id="T_a496e_level0_col13" class="col_heading level0 col13" >valid_loss_choices</th>
      <th id="T_a496e_level0_col14" class="col_heading level0 col14" >callbacks_state</th>
      <th id="T_a496e_level0_col15" class="col_heading level0 col15" >callbacks_choices</th>
      <th id="T_a496e_level0_col16" class="col_heading level0 col16" >scaler_param</th>
      <th id="T_a496e_level0_col17" class="col_heading level0 col17" >scaler_default</th>
      <th id="T_a496e_level0_col18" class="col_heading level0 col18" >scaler_choices</th>
      <th id="T_a496e_level0_col19" class="col_heading level0 col19" >early_stop_supported</th>
      <th id="T_a496e_level0_col20" class="col_heading level0 col20" >early_stop_default</th>
      <th id="T_a496e_level0_col21" class="col_heading level0 col21" >early_stop_choices</th>
      <th id="T_a496e_level0_col22" class="col_heading level0 col22" >dropout_supported</th>
      <th id="T_a496e_level0_col23" class="col_heading level0 col23" >dropout_params</th>
      <th id="T_a496e_level0_col24" class="col_heading level0 col24" >dropout_defaults</th>
      <th id="T_a496e_level0_col25" class="col_heading level0 col25" >dropout_choices</th>
      <th id="T_a496e_level0_col26" class="col_heading level0 col26" >exog_F</th>
      <th id="T_a496e_level0_col27" class="col_heading level0 col27" >exog_H</th>
      <th id="T_a496e_level0_col28" class="col_heading level0 col28" >exog_S</th>
      <th id="T_a496e_level0_col29" class="col_heading level0 col29" >exog_choices</th>
      <th id="T_a496e_level0_col30" class="col_heading level0 col30" >h_supported</th>
      <th id="T_a496e_level0_col31" class="col_heading level0 col31" >h</th>
      <th id="T_a496e_level0_col32" class="col_heading level0 col32" >h_min</th>
      <th id="T_a496e_level0_col33" class="col_heading level0 col33" >h_source</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th id="T_a496e_level0_row0" class="row_heading level0 row0" >0</th>
      <td id="T_a496e_row0_col0" class="data row0 col0" >AutoAutoformer</td>
      <td id="T_a496e_row0_col1" class="data row0 col1" >Autoformer</td>
      <td id="T_a496e_row0_col2" class="data row0 col2" >optuna</td>
      <td id="T_a496e_row0_col3" class="data row0 col3" >['ray', 'optuna']</td>
      <td id="T_a496e_row0_col4" class="data row0 col4" >True</td>
      <td id="T_a496e_row0_col5" class="data row0 col5" >True</td>
      <td id="T_a496e_row0_col6" class="data row0 col6" >Available (Enabled by Default)</td>
      <td id="T_a496e_row0_col7" class="data row0 col7" >Works with MedianPruner, HyperbandPruner, etc.</td>
      <td id="T_a496e_row0_col8" class="data row0 col8" >TPESampler</td>
      <td id="T_a496e_row0_col9" class="data row0 col9" >['TPESampler', 'RandomSampler', 'GridSampler', 'CmaEsSampler', 'NSGAIISampler', 'MOTPESampler', 'QMCSampler', 'BoTorchSampler']</td>
      <td id="T_a496e_row0_col10" class="data row0 col10" >MAE()</td>
      <td id="T_a496e_row0_col11" class="data row0 col11" >['Accuracy', 'AffineTransform', 'BaseISQF', 'BasePointLoss', 'Bernoulli', 'Beta', 'Categorical', 'Distribution', 'DistributionLoss', 'GMM', 'Gamma', 'HuberIQLoss', 'HuberLoss', 'HuberMQLoss', 'HuberQLoss', 'IQLoss', 'ISQF', 'MAE', 'MAPE', 'MASE', 'MQLoss', 'MSE', 'MixtureSameFamily', 'NBMM', 'NegativeBinomial', 'Normal', 'PMM', 'Poisson', 'QuantileLayer', 'QuantileLoss', 'RMSE', 'SMAPE', 'StudentT', 'TransformedDistribution', 'TukeyLoss', 'Tweedie']</td>
      <td id="T_a496e_row0_col12" class="data row0 col12" >None</td>
      <td id="T_a496e_row0_col13" class="data row0 col13" >['Accuracy', 'AffineTransform', 'BaseISQF', 'BasePointLoss', 'Bernoulli', 'Beta', 'Categorical', 'Distribution', 'DistributionLoss', 'GMM', 'Gamma', 'HuberIQLoss', 'HuberLoss', 'HuberMQLoss', 'HuberQLoss', 'IQLoss', 'ISQF', 'MAE', 'MAPE', 'MASE', 'MQLoss', 'MSE', 'MixtureSameFamily', 'NBMM', 'NegativeBinomial', 'Normal', 'PMM', 'Poisson', 'QuantileLayer', 'QuantileLoss', 'RMSE', 'SMAPE', 'StudentT', 'TransformedDistribution', 'TukeyLoss', 'Tweedie']</td>
      <td id="T_a496e_row0_col14" class="data row0 col14" >None</td>
      <td id="T_a496e_row0_col15" class="data row0 col15" >Any callable(study, trial)</td>
      <td id="T_a496e_row0_col16" class="data row0 col16" >scaler_type</td>
      <td id="T_a496e_row0_col17" class="data row0 col17" >identity</td>
      <td id="T_a496e_row0_col18" class="data row0 col18" >['identity', 'standard', 'robust', 'minmax']</td>
      <td id="T_a496e_row0_col19" class="data row0 col19" >True</td>
      <td id="T_a496e_row0_col20" class="data row0 col20" >-1.000000</td>
      <td id="T_a496e_row0_col21" class="data row0 col21" >{'early_stop_patience_steps': 'int>=1 or -1(disable)'}</td>
      <td id="T_a496e_row0_col22" class="data row0 col22" >True</td>
      <td id="T_a496e_row0_col23" class="data row0 col23" >dropout</td>
      <td id="T_a496e_row0_col24" class="data row0 col24" >dropout=0.05</td>
      <td id="T_a496e_row0_col25" class="data row0 col25" >{'dropout': 'float in [0.0, 1.0]'}</td>
      <td id="T_a496e_row0_col26" class="data row0 col26" >True</td>
      <td id="T_a496e_row0_col27" class="data row0 col27" >True</td>
      <td id="T_a496e_row0_col28" class="data row0 col28" >True</td>
      <td id="T_a496e_row0_col29" class="data row0 col29" >{'futr_exog_list': 'list[str]', 'hist_exog_list': 'list[str]', 'stat_exog_list': 'list[str]'}</td>
      <td id="T_a496e_row0_col30" class="data row0 col30" >None</td>
      <td id="T_a496e_row0_col31" class="data row0 col31" >None</td>
      <td id="T_a496e_row0_col32" class="data row0 col32" >None</td>
      <td id="T_a496e_row0_col33" class="data row0 col33" >None</td>
    </tr>
    <tr>
      <th id="T_a496e_level0_row1" class="row_heading level0 row1" >1</th>
      <td id="T_a496e_row1_col0" class="data row1 col0" >AutoAutoformer</td>
      <td id="T_a496e_row1_col1" class="data row1 col1" >Autoformer</td>
      <td id="T_a496e_row1_col2" class="data row1 col2" >ray</td>
      <td id="T_a496e_row1_col3" class="data row1 col3" >['ray', 'optuna']</td>
      <td id="T_a496e_row1_col4" class="data row1 col4" >True</td>
      <td id="T_a496e_row1_col5" class="data row1 col5" >False</td>
      <td id="T_a496e_row1_col6" class="data row1 col6" >Available (Manual Configuration Required)</td>
      <td id="T_a496e_row1_col7" class="data row1 col7" >Requires explicit scheduler like ASHAScheduler</td>
      <td id="T_a496e_row1_col8" class="data row1 col8" >BasicVariantGenerator</td>
      <td id="T_a496e_row1_col9" class="data row1 col9" >['BasicVariantGenerator', 'OptunaSearch', 'HyperOptSearch', 'BayesOptSearch', 'NevergradSearch', 'SkoptSearch', 'AxSearch', 'DragonflySearch', 'HEBO', 'BlendSearch']</td>
      <td id="T_a496e_row1_col10" class="data row1 col10" >MAE()</td>
      <td id="T_a496e_row1_col11" class="data row1 col11" >['Accuracy', 'AffineTransform', 'BaseISQF', 'BasePointLoss', 'Bernoulli', 'Beta', 'Categorical', 'Distribution', 'DistributionLoss', 'GMM', 'Gamma', 'HuberIQLoss', 'HuberLoss', 'HuberMQLoss', 'HuberQLoss', 'IQLoss', 'ISQF', 'MAE', 'MAPE', 'MASE', 'MQLoss', 'MSE', 'MixtureSameFamily', 'NBMM', 'NegativeBinomial', 'Normal', 'PMM', 'Poisson', 'QuantileLayer', 'QuantileLoss', 'RMSE', 'SMAPE', 'StudentT', 'TransformedDistribution', 'TukeyLoss', 'Tweedie']</td>
      <td id="T_a496e_row1_col12" class="data row1 col12" >None</td>
      <td id="T_a496e_row1_col13" class="data row1 col13" >['Accuracy', 'AffineTransform', 'BaseISQF', 'BasePointLoss', 'Bernoulli', 'Beta', 'Categorical', 'Distribution', 'DistributionLoss', 'GMM', 'Gamma', 'HuberIQLoss', 'HuberLoss', 'HuberMQLoss', 'HuberQLoss', 'IQLoss', 'ISQF', 'MAE', 'MAPE', 'MASE', 'MQLoss', 'MSE', 'MixtureSameFamily', 'NBMM', 'NegativeBinomial', 'Normal', 'PMM', 'Poisson', 'QuantileLayer', 'QuantileLoss', 'RMSE', 'SMAPE', 'StudentT', 'TransformedDistribution', 'TukeyLoss', 'Tweedie']</td>
      <td id="T_a496e_row1_col14" class="data row1 col14" >None</td>
      <td id="T_a496e_row1_col15" class="data row1 col15" >Any ray.tune.Callback</td>
      <td id="T_a496e_row1_col16" class="data row1 col16" >scaler_type</td>
      <td id="T_a496e_row1_col17" class="data row1 col17" >identity</td>
      <td id="T_a496e_row1_col18" class="data row1 col18" >['identity', 'standard', 'robust', 'minmax']</td>
      <td id="T_a496e_row1_col19" class="data row1 col19" >True</td>
      <td id="T_a496e_row1_col20" class="data row1 col20" >-1.000000</td>
      <td id="T_a496e_row1_col21" class="data row1 col21" >{'early_stop_patience_steps': 'int>=1 or -1(disable)'}</td>
      <td id="T_a496e_row1_col22" class="data row1 col22" >True</td>
      <td id="T_a496e_row1_col23" class="data row1 col23" >dropout</td>
      <td id="T_a496e_row1_col24" class="data row1 col24" >dropout=0.05</td>
      <td id="T_a496e_row1_col25" class="data row1 col25" >{'dropout': 'float in [0.0, 1.0]'}</td>
      <td id="T_a496e_row1_col26" class="data row1 col26" >True</td>
      <td id="T_a496e_row1_col27" class="data row1 col27" >True</td>
      <td id="T_a496e_row1_col28" class="data row1 col28" >True</td>
      <td id="T_a496e_row1_col29" class="data row1 col29" >{'futr_exog_list': 'list[str]', 'hist_exog_list': 'list[str]', 'stat_exog_list': 'list[str]'}</td>
      <td id="T_a496e_row1_col30" class="data row1 col30" >None</td>
      <td id="T_a496e_row1_col31" class="data row1 col31" >None</td>
      <td id="T_a496e_row1_col32" class="data row1 col32" >None</td>
      <td id="T_a496e_row1_col33" class="data row1 col33" >None</td>
    </tr>
    <tr>
      <th id="T_a496e_level0_row2" class="row_heading level0 row2" >2</th>
      <td id="T_a496e_row2_col0" class="data row2 col0" >AutoBiTCN</td>
      <td id="T_a496e_row2_col1" class="data row2 col1" >BiTCN</td>
      <td id="T_a496e_row2_col2" class="data row2 col2" >optuna</td>
      <td id="T_a496e_row2_col3" class="data row2 col3" >['ray', 'optuna']</td>
      <td id="T_a496e_row2_col4" class="data row2 col4" >True</td>
      <td id="T_a496e_row2_col5" class="data row2 col5" >True</td>
      <td id="T_a496e_row2_col6" class="data row2 col6" >Available (Enabled by Default)</td>
      <td id="T_a496e_row2_col7" class="data row2 col7" >Works with MedianPruner, HyperbandPruner, etc.</td>
      <td id="T_a496e_row2_col8" class="data row2 col8" >TPESampler</td>
      <td id="T_a496e_row2_col9" class="data row2 col9" >['TPESampler', 'RandomSampler', 'GridSampler', 'CmaEsSampler', 'NSGAIISampler', 'MOTPESampler', 'QMCSampler', 'BoTorchSampler']</td>
      <td id="T_a496e_row2_col10" class="data row2 col10" >MAE()</td>
      <td id="T_a496e_row2_col11" class="data row2 col11" >['Accuracy', 'AffineTransform', 'BaseISQF', 'BasePointLoss', 'Bernoulli', 'Beta', 'Categorical', 'Distribution', 'DistributionLoss', 'GMM', 'Gamma', 'HuberIQLoss', 'HuberLoss', 'HuberMQLoss', 'HuberQLoss', 'IQLoss', 'ISQF', 'MAE', 'MAPE', 'MASE', 'MQLoss', 'MSE', 'MixtureSameFamily', 'NBMM', 'NegativeBinomial', 'Normal', 'PMM', 'Poisson', 'QuantileLayer', 'QuantileLoss', 'RMSE', 'SMAPE', 'StudentT', 'TransformedDistribution', 'TukeyLoss', 'Tweedie']</td>
      <td id="T_a496e_row2_col12" class="data row2 col12" >None</td>
      <td id="T_a496e_row2_col13" class="data row2 col13" >['Accuracy', 'AffineTransform', 'BaseISQF', 'BasePointLoss', 'Bernoulli', 'Beta', 'Categorical', 'Distribution', 'DistributionLoss', 'GMM', 'Gamma', 'HuberIQLoss', 'HuberLoss', 'HuberMQLoss', 'HuberQLoss', 'IQLoss', 'ISQF', 'MAE', 'MAPE', 'MASE', 'MQLoss', 'MSE', 'MixtureSameFamily', 'NBMM', 'NegativeBinomial', 'Normal', 'PMM', 'Poisson', 'QuantileLayer', 'QuantileLoss', 'RMSE', 'SMAPE', 'StudentT', 'TransformedDistribution', 'TukeyLoss', 'Tweedie']</td>
      <td id="T_a496e_row2_col14" class="data row2 col14" >None</td>
      <td id="T_a496e_row2_col15" class="data row2 col15" >Any callable(study, trial)</td>
      <td id="T_a496e_row2_col16" class="data row2 col16" >scaler_type</td>
      <td id="T_a496e_row2_col17" class="data row2 col17" >identity</td>
      <td id="T_a496e_row2_col18" class="data row2 col18" >['identity', 'standard', 'robust', 'minmax']</td>
      <td id="T_a496e_row2_col19" class="data row2 col19" >True</td>
      <td id="T_a496e_row2_col20" class="data row2 col20" >-1.000000</td>
      <td id="T_a496e_row2_col21" class="data row2 col21" >{'early_stop_patience_steps': 'int>=1 or -1(disable)'}</td>
      <td id="T_a496e_row2_col22" class="data row2 col22" >True</td>
      <td id="T_a496e_row2_col23" class="data row2 col23" >dropout</td>
      <td id="T_a496e_row2_col24" class="data row2 col24" >dropout=0.5</td>
      <td id="T_a496e_row2_col25" class="data row2 col25" >{'dropout': 'float in [0.0, 1.0]'}</td>
      <td id="T_a496e_row2_col26" class="data row2 col26" >True</td>
      <td id="T_a496e_row2_col27" class="data row2 col27" >True</td>
      <td id="T_a496e_row2_col28" class="data row2 col28" >True</td>
      <td id="T_a496e_row2_col29" class="data row2 col29" >{'futr_exog_list': 'list[str]', 'hist_exog_list': 'list[str]', 'stat_exog_list': 'list[str]'}</td>
      <td id="T_a496e_row2_col30" class="data row2 col30" >None</td>
      <td id="T_a496e_row2_col31" class="data row2 col31" >None</td>
      <td id="T_a496e_row2_col32" class="data row2 col32" >None</td>
      <td id="T_a496e_row2_col33" class="data row2 col33" >None</td>
    </tr>
    <tr>
      <th id="T_a496e_level0_row3" class="row_heading level0 row3" >3</th>
      <td id="T_a496e_row3_col0" class="data row3 col0" >AutoBiTCN</td>
      <td id="T_a496e_row3_col1" class="data row3 col1" >BiTCN</td>
      <td id="T_a496e_row3_col2" class="data row3 col2" >ray</td>
      <td id="T_a496e_row3_col3" class="data row3 col3" >['ray', 'optuna']</td>
      <td id="T_a496e_row3_col4" class="data row3 col4" >True</td>
      <td id="T_a496e_row3_col5" class="data row3 col5" >False</td>
      <td id="T_a496e_row3_col6" class="data row3 col6" >Available (Manual Configuration Required)</td>
      <td id="T_a496e_row3_col7" class="data row3 col7" >Requires explicit scheduler like ASHAScheduler</td>
      <td id="T_a496e_row3_col8" class="data row3 col8" >BasicVariantGenerator</td>
      <td id="T_a496e_row3_col9" class="data row3 col9" >['BasicVariantGenerator', 'OptunaSearch', 'HyperOptSearch', 'BayesOptSearch', 'NevergradSearch', 'SkoptSearch', 'AxSearch', 'DragonflySearch', 'HEBO', 'BlendSearch']</td>
      <td id="T_a496e_row3_col10" class="data row3 col10" >MAE()</td>
      <td id="T_a496e_row3_col11" class="data row3 col11" >['Accuracy', 'AffineTransform', 'BaseISQF', 'BasePointLoss', 'Bernoulli', 'Beta', 'Categorical', 'Distribution', 'DistributionLoss', 'GMM', 'Gamma', 'HuberIQLoss', 'HuberLoss', 'HuberMQLoss', 'HuberQLoss', 'IQLoss', 'ISQF', 'MAE', 'MAPE', 'MASE', 'MQLoss', 'MSE', 'MixtureSameFamily', 'NBMM', 'NegativeBinomial', 'Normal', 'PMM', 'Poisson', 'QuantileLayer', 'QuantileLoss', 'RMSE', 'SMAPE', 'StudentT', 'TransformedDistribution', 'TukeyLoss', 'Tweedie']</td>
      <td id="T_a496e_row3_col12" class="data row3 col12" >None</td>
      <td id="T_a496e_row3_col13" class="data row3 col13" >['Accuracy', 'AffineTransform', 'BaseISQF', 'BasePointLoss', 'Bernoulli', 'Beta', 'Categorical', 'Distribution', 'DistributionLoss', 'GMM', 'Gamma', 'HuberIQLoss', 'HuberLoss', 'HuberMQLoss', 'HuberQLoss', 'IQLoss', 'ISQF', 'MAE', 'MAPE', 'MASE', 'MQLoss', 'MSE', 'MixtureSameFamily', 'NBMM', 'NegativeBinomial', 'Normal', 'PMM', 'Poisson', 'QuantileLayer', 'QuantileLoss', 'RMSE', 'SMAPE', 'StudentT', 'TransformedDistribution', 'TukeyLoss', 'Tweedie']</td>
      <td id="T_a496e_row3_col14" class="data row3 col14" >None</td>
      <td id="T_a496e_row3_col15" class="data row3 col15" >Any ray.tune.Callback</td>
      <td id="T_a496e_row3_col16" class="data row3 col16" >scaler_type</td>
      <td id="T_a496e_row3_col17" class="data row3 col17" >identity</td>
      <td id="T_a496e_row3_col18" class="data row3 col18" >['identity', 'standard', 'robust', 'minmax']</td>
      <td id="T_a496e_row3_col19" class="data row3 col19" >True</td>
      <td id="T_a496e_row3_col20" class="data row3 col20" >-1.000000</td>
      <td id="T_a496e_row3_col21" class="data row3 col21" >{'early_stop_patience_steps': 'int>=1 or -1(disable)'}</td>
      <td id="T_a496e_row3_col22" class="data row3 col22" >True</td>
      <td id="T_a496e_row3_col23" class="data row3 col23" >dropout</td>
      <td id="T_a496e_row3_col24" class="data row3 col24" >dropout=0.5</td>
      <td id="T_a496e_row3_col25" class="data row3 col25" >{'dropout': 'float in [0.0, 1.0]'}</td>
      <td id="T_a496e_row3_col26" class="data row3 col26" >True</td>
      <td id="T_a496e_row3_col27" class="data row3 col27" >True</td>
      <td id="T_a496e_row3_col28" class="data row3 col28" >True</td>
      <td id="T_a496e_row3_col29" class="data row3 col29" >{'futr_exog_list': 'list[str]', 'hist_exog_list': 'list[str]', 'stat_exog_list': 'list[str]'}</td>
      <td id="T_a496e_row3_col30" class="data row3 col30" >None</td>
      <td id="T_a496e_row3_col31" class="data row3 col31" >None</td>
      <td id="T_a496e_row3_col32" class="data row3 col32" >None</td>
      <td id="T_a496e_row3_col33" class="data row3 col33" >None</td>
    </tr>
    <tr>
      <th id="T_a496e_level0_row4" class="row_heading level0 row4" >4</th>
      <td id="T_a496e_row4_col0" class="data row4 col0" >AutoDLinear</td>
      <td id="T_a496e_row4_col1" class="data row4 col1" >DLinear</td>
      <td id="T_a496e_row4_col2" class="data row4 col2" >optuna</td>
      <td id="T_a496e_row4_col3" class="data row4 col3" >['ray', 'optuna']</td>
      <td id="T_a496e_row4_col4" class="data row4 col4" >True</td>
      <td id="T_a496e_row4_col5" class="data row4 col5" >True</td>
      <td id="T_a496e_row4_col6" class="data row4 col6" >Available (Enabled by Default)</td>
      <td id="T_a496e_row4_col7" class="data row4 col7" >Works with MedianPruner, HyperbandPruner, etc.</td>
      <td id="T_a496e_row4_col8" class="data row4 col8" >TPESampler</td>
      <td id="T_a496e_row4_col9" class="data row4 col9" >['TPESampler', 'RandomSampler', 'GridSampler', 'CmaEsSampler', 'NSGAIISampler', 'MOTPESampler', 'QMCSampler', 'BoTorchSampler']</td>
      <td id="T_a496e_row4_col10" class="data row4 col10" >MAE()</td>
      <td id="T_a496e_row4_col11" class="data row4 col11" >['Accuracy', 'AffineTransform', 'BaseISQF', 'BasePointLoss', 'Bernoulli', 'Beta', 'Categorical', 'Distribution', 'DistributionLoss', 'GMM', 'Gamma', 'HuberIQLoss', 'HuberLoss', 'HuberMQLoss', 'HuberQLoss', 'IQLoss', 'ISQF', 'MAE', 'MAPE', 'MASE', 'MQLoss', 'MSE', 'MixtureSameFamily', 'NBMM', 'NegativeBinomial', 'Normal', 'PMM', 'Poisson', 'QuantileLayer', 'QuantileLoss', 'RMSE', 'SMAPE', 'StudentT', 'TransformedDistribution', 'TukeyLoss', 'Tweedie']</td>
      <td id="T_a496e_row4_col12" class="data row4 col12" >None</td>
      <td id="T_a496e_row4_col13" class="data row4 col13" >['Accuracy', 'AffineTransform', 'BaseISQF', 'BasePointLoss', 'Bernoulli', 'Beta', 'Categorical', 'Distribution', 'DistributionLoss', 'GMM', 'Gamma', 'HuberIQLoss', 'HuberLoss', 'HuberMQLoss', 'HuberQLoss', 'IQLoss', 'ISQF', 'MAE', 'MAPE', 'MASE', 'MQLoss', 'MSE', 'MixtureSameFamily', 'NBMM', 'NegativeBinomial', 'Normal', 'PMM', 'Poisson', 'QuantileLayer', 'QuantileLoss', 'RMSE', 'SMAPE', 'StudentT', 'TransformedDistribution', 'TukeyLoss', 'Tweedie']</td>
      <td id="T_a496e_row4_col14" class="data row4 col14" >None</td>
      <td id="T_a496e_row4_col15" class="data row4 col15" >Any callable(study, trial)</td>
      <td id="T_a496e_row4_col16" class="data row4 col16" >scaler_type</td>
      <td id="T_a496e_row4_col17" class="data row4 col17" >identity</td>
      <td id="T_a496e_row4_col18" class="data row4 col18" >['identity', 'standard', 'robust', 'minmax']</td>
      <td id="T_a496e_row4_col19" class="data row4 col19" >True</td>
      <td id="T_a496e_row4_col20" class="data row4 col20" >-1.000000</td>
      <td id="T_a496e_row4_col21" class="data row4 col21" >{'early_stop_patience_steps': 'int>=1 or -1(disable)'}</td>
      <td id="T_a496e_row4_col22" class="data row4 col22" >False</td>
      <td id="T_a496e_row4_col23" class="data row4 col23" >None</td>
      <td id="T_a496e_row4_col24" class="data row4 col24" >None</td>
      <td id="T_a496e_row4_col25" class="data row4 col25" >None</td>
      <td id="T_a496e_row4_col26" class="data row4 col26" >True</td>
      <td id="T_a496e_row4_col27" class="data row4 col27" >True</td>
      <td id="T_a496e_row4_col28" class="data row4 col28" >True</td>
      <td id="T_a496e_row4_col29" class="data row4 col29" >{'futr_exog_list': 'list[str]', 'hist_exog_list': 'list[str]', 'stat_exog_list': 'list[str]'}</td>
      <td id="T_a496e_row4_col30" class="data row4 col30" >None</td>
      <td id="T_a496e_row4_col31" class="data row4 col31" >None</td>
      <td id="T_a496e_row4_col32" class="data row4 col32" >None</td>
      <td id="T_a496e_row4_col33" class="data row4 col33" >None</td>
    </tr>
    <tr>
      <th id="T_a496e_level0_row5" class="row_heading level0 row5" >5</th>
      <td id="T_a496e_row5_col0" class="data row5 col0" >AutoDLinear</td>
      <td id="T_a496e_row5_col1" class="data row5 col1" >DLinear</td>
      <td id="T_a496e_row5_col2" class="data row5 col2" >ray</td>
      <td id="T_a496e_row5_col3" class="data row5 col3" >['ray', 'optuna']</td>
      <td id="T_a496e_row5_col4" class="data row5 col4" >True</td>
      <td id="T_a496e_row5_col5" class="data row5 col5" >False</td>
      <td id="T_a496e_row5_col6" class="data row5 col6" >Available (Manual Configuration Required)</td>
      <td id="T_a496e_row5_col7" class="data row5 col7" >Requires explicit scheduler like ASHAScheduler</td>
      <td id="T_a496e_row5_col8" class="data row5 col8" >BasicVariantGenerator</td>
      <td id="T_a496e_row5_col9" class="data row5 col9" >['BasicVariantGenerator', 'OptunaSearch', 'HyperOptSearch', 'BayesOptSearch', 'NevergradSearch', 'SkoptSearch', 'AxSearch', 'DragonflySearch', 'HEBO', 'BlendSearch']</td>
      <td id="T_a496e_row5_col10" class="data row5 col10" >MAE()</td>
      <td id="T_a496e_row5_col11" class="data row5 col11" >['Accuracy', 'AffineTransform', 'BaseISQF', 'BasePointLoss', 'Bernoulli', 'Beta', 'Categorical', 'Distribution', 'DistributionLoss', 'GMM', 'Gamma', 'HuberIQLoss', 'HuberLoss', 'HuberMQLoss', 'HuberQLoss', 'IQLoss', 'ISQF', 'MAE', 'MAPE', 'MASE', 'MQLoss', 'MSE', 'MixtureSameFamily', 'NBMM', 'NegativeBinomial', 'Normal', 'PMM', 'Poisson', 'QuantileLayer', 'QuantileLoss', 'RMSE', 'SMAPE', 'StudentT', 'TransformedDistribution', 'TukeyLoss', 'Tweedie']</td>
      <td id="T_a496e_row5_col12" class="data row5 col12" >None</td>
      <td id="T_a496e_row5_col13" class="data row5 col13" >['Accuracy', 'AffineTransform', 'BaseISQF', 'BasePointLoss', 'Bernoulli', 'Beta', 'Categorical', 'Distribution', 'DistributionLoss', 'GMM', 'Gamma', 'HuberIQLoss', 'HuberLoss', 'HuberMQLoss', 'HuberQLoss', 'IQLoss', 'ISQF', 'MAE', 'MAPE', 'MASE', 'MQLoss', 'MSE', 'MixtureSameFamily', 'NBMM', 'NegativeBinomial', 'Normal', 'PMM', 'Poisson', 'QuantileLayer', 'QuantileLoss', 'RMSE', 'SMAPE', 'StudentT', 'TransformedDistribution', 'TukeyLoss', 'Tweedie']</td>
      <td id="T_a496e_row5_col14" class="data row5 col14" >None</td>
      <td id="T_a496e_row5_col15" class="data row5 col15" >Any ray.tune.Callback</td>
      <td id="T_a496e_row5_col16" class="data row5 col16" >scaler_type</td>
      <td id="T_a496e_row5_col17" class="data row5 col17" >identity</td>
      <td id="T_a496e_row5_col18" class="data row5 col18" >['identity', 'standard', 'robust', 'minmax']</td>
      <td id="T_a496e_row5_col19" class="data row5 col19" >True</td>
      <td id="T_a496e_row5_col20" class="data row5 col20" >-1.000000</td>
      <td id="T_a496e_row5_col21" class="data row5 col21" >{'early_stop_patience_steps': 'int>=1 or -1(disable)'}</td>
      <td id="T_a496e_row5_col22" class="data row5 col22" >False</td>
      <td id="T_a496e_row5_col23" class="data row5 col23" >None</td>
      <td id="T_a496e_row5_col24" class="data row5 col24" >None</td>
      <td id="T_a496e_row5_col25" class="data row5 col25" >None</td>
      <td id="T_a496e_row5_col26" class="data row5 col26" >True</td>
      <td id="T_a496e_row5_col27" class="data row5 col27" >True</td>
      <td id="T_a496e_row5_col28" class="data row5 col28" >True</td>
      <td id="T_a496e_row5_col29" class="data row5 col29" >{'futr_exog_list': 'list[str]', 'hist_exog_list': 'list[str]', 'stat_exog_list': 'list[str]'}</td>
      <td id="T_a496e_row5_col30" class="data row5 col30" >None</td>
      <td id="T_a496e_row5_col31" class="data row5 col31" >None</td>
      <td id="T_a496e_row5_col32" class="data row5 col32" >None</td>
      <td id="T_a496e_row5_col33" class="data row5 col33" >None</td>
    </tr>
    <tr>
      <th id="T_a496e_level0_row6" class="row_heading level0 row6" >6</th>
      <td id="T_a496e_row6_col0" class="data row6 col0" >AutoDeepAR</td>
      <td id="T_a496e_row6_col1" class="data row6 col1" >DeepAR</td>
      <td id="T_a496e_row6_col2" class="data row6 col2" >optuna</td>
      <td id="T_a496e_row6_col3" class="data row6 col3" >['ray', 'optuna']</td>
      <td id="T_a496e_row6_col4" class="data row6 col4" >True</td>
      <td id="T_a496e_row6_col5" class="data row6 col5" >True</td>
      <td id="T_a496e_row6_col6" class="data row6 col6" >Available (Enabled by Default)</td>
      <td id="T_a496e_row6_col7" class="data row6 col7" >Works with MedianPruner, HyperbandPruner, etc.</td>
      <td id="T_a496e_row6_col8" class="data row6 col8" >TPESampler</td>
      <td id="T_a496e_row6_col9" class="data row6 col9" >['TPESampler', 'RandomSampler', 'GridSampler', 'CmaEsSampler', 'NSGAIISampler', 'MOTPESampler', 'QMCSampler', 'BoTorchSampler']</td>
      <td id="T_a496e_row6_col10" class="data row6 col10" >DistributionLoss()</td>
      <td id="T_a496e_row6_col11" class="data row6 col11" >['Accuracy', 'AffineTransform', 'BaseISQF', 'BasePointLoss', 'Bernoulli', 'Beta', 'Categorical', 'Distribution', 'DistributionLoss', 'GMM', 'Gamma', 'HuberIQLoss', 'HuberLoss', 'HuberMQLoss', 'HuberQLoss', 'IQLoss', 'ISQF', 'MAE', 'MAPE', 'MASE', 'MQLoss', 'MSE', 'MixtureSameFamily', 'NBMM', 'NegativeBinomial', 'Normal', 'PMM', 'Poisson', 'QuantileLayer', 'QuantileLoss', 'RMSE', 'SMAPE', 'StudentT', 'TransformedDistribution', 'TukeyLoss', 'Tweedie']</td>
      <td id="T_a496e_row6_col12" class="data row6 col12" >MQLoss()</td>
      <td id="T_a496e_row6_col13" class="data row6 col13" >['Accuracy', 'AffineTransform', 'BaseISQF', 'BasePointLoss', 'Bernoulli', 'Beta', 'Categorical', 'Distribution', 'DistributionLoss', 'GMM', 'Gamma', 'HuberIQLoss', 'HuberLoss', 'HuberMQLoss', 'HuberQLoss', 'IQLoss', 'ISQF', 'MAE', 'MAPE', 'MASE', 'MQLoss', 'MSE', 'MixtureSameFamily', 'NBMM', 'NegativeBinomial', 'Normal', 'PMM', 'Poisson', 'QuantileLayer', 'QuantileLoss', 'RMSE', 'SMAPE', 'StudentT', 'TransformedDistribution', 'TukeyLoss', 'Tweedie']</td>
      <td id="T_a496e_row6_col14" class="data row6 col14" >None</td>
      <td id="T_a496e_row6_col15" class="data row6 col15" >Any callable(study, trial)</td>
      <td id="T_a496e_row6_col16" class="data row6 col16" >scaler_type</td>
      <td id="T_a496e_row6_col17" class="data row6 col17" >identity</td>
      <td id="T_a496e_row6_col18" class="data row6 col18" >['identity', 'standard', 'robust', 'minmax']</td>
      <td id="T_a496e_row6_col19" class="data row6 col19" >True</td>
      <td id="T_a496e_row6_col20" class="data row6 col20" >-1.000000</td>
      <td id="T_a496e_row6_col21" class="data row6 col21" >{'early_stop_patience_steps': 'int>=1 or -1(disable)'}</td>
      <td id="T_a496e_row6_col22" class="data row6 col22" >True</td>
      <td id="T_a496e_row6_col23" class="data row6 col23" >lstm_dropout</td>
      <td id="T_a496e_row6_col24" class="data row6 col24" >lstm_dropout=0.1</td>
      <td id="T_a496e_row6_col25" class="data row6 col25" >{'lstm_dropout': 'float in [0.0, 1.0]'}</td>
      <td id="T_a496e_row6_col26" class="data row6 col26" >True</td>
      <td id="T_a496e_row6_col27" class="data row6 col27" >True</td>
      <td id="T_a496e_row6_col28" class="data row6 col28" >True</td>
      <td id="T_a496e_row6_col29" class="data row6 col29" >{'futr_exog_list': 'list[str]', 'hist_exog_list': 'list[str]', 'stat_exog_list': 'list[str]'}</td>
      <td id="T_a496e_row6_col30" class="data row6 col30" >None</td>
      <td id="T_a496e_row6_col31" class="data row6 col31" >None</td>
      <td id="T_a496e_row6_col32" class="data row6 col32" >None</td>
      <td id="T_a496e_row6_col33" class="data row6 col33" >None</td>
    </tr>
    <tr>
      <th id="T_a496e_level0_row7" class="row_heading level0 row7" >7</th>
      <td id="T_a496e_row7_col0" class="data row7 col0" >AutoDeepAR</td>
      <td id="T_a496e_row7_col1" class="data row7 col1" >DeepAR</td>
      <td id="T_a496e_row7_col2" class="data row7 col2" >ray</td>
      <td id="T_a496e_row7_col3" class="data row7 col3" >['ray', 'optuna']</td>
      <td id="T_a496e_row7_col4" class="data row7 col4" >True</td>
      <td id="T_a496e_row7_col5" class="data row7 col5" >False</td>
      <td id="T_a496e_row7_col6" class="data row7 col6" >Available (Manual Configuration Required)</td>
      <td id="T_a496e_row7_col7" class="data row7 col7" >Requires explicit scheduler like ASHAScheduler</td>
      <td id="T_a496e_row7_col8" class="data row7 col8" >BasicVariantGenerator</td>
      <td id="T_a496e_row7_col9" class="data row7 col9" >['BasicVariantGenerator', 'OptunaSearch', 'HyperOptSearch', 'BayesOptSearch', 'NevergradSearch', 'SkoptSearch', 'AxSearch', 'DragonflySearch', 'HEBO', 'BlendSearch']</td>
      <td id="T_a496e_row7_col10" class="data row7 col10" >DistributionLoss()</td>
      <td id="T_a496e_row7_col11" class="data row7 col11" >['Accuracy', 'AffineTransform', 'BaseISQF', 'BasePointLoss', 'Bernoulli', 'Beta', 'Categorical', 'Distribution', 'DistributionLoss', 'GMM', 'Gamma', 'HuberIQLoss', 'HuberLoss', 'HuberMQLoss', 'HuberQLoss', 'IQLoss', 'ISQF', 'MAE', 'MAPE', 'MASE', 'MQLoss', 'MSE', 'MixtureSameFamily', 'NBMM', 'NegativeBinomial', 'Normal', 'PMM', 'Poisson', 'QuantileLayer', 'QuantileLoss', 'RMSE', 'SMAPE', 'StudentT', 'TransformedDistribution', 'TukeyLoss', 'Tweedie']</td>
      <td id="T_a496e_row7_col12" class="data row7 col12" >MQLoss()</td>
      <td id="T_a496e_row7_col13" class="data row7 col13" >['Accuracy', 'AffineTransform', 'BaseISQF', 'BasePointLoss', 'Bernoulli', 'Beta', 'Categorical', 'Distribution', 'DistributionLoss', 'GMM', 'Gamma', 'HuberIQLoss', 'HuberLoss', 'HuberMQLoss', 'HuberQLoss', 'IQLoss', 'ISQF', 'MAE', 'MAPE', 'MASE', 'MQLoss', 'MSE', 'MixtureSameFamily', 'NBMM', 'NegativeBinomial', 'Normal', 'PMM', 'Poisson', 'QuantileLayer', 'QuantileLoss', 'RMSE', 'SMAPE', 'StudentT', 'TransformedDistribution', 'TukeyLoss', 'Tweedie']</td>
      <td id="T_a496e_row7_col14" class="data row7 col14" >None</td>
      <td id="T_a496e_row7_col15" class="data row7 col15" >Any ray.tune.Callback</td>
      <td id="T_a496e_row7_col16" class="data row7 col16" >scaler_type</td>
      <td id="T_a496e_row7_col17" class="data row7 col17" >identity</td>
      <td id="T_a496e_row7_col18" class="data row7 col18" >['identity', 'standard', 'robust', 'minmax']</td>
      <td id="T_a496e_row7_col19" class="data row7 col19" >True</td>
      <td id="T_a496e_row7_col20" class="data row7 col20" >-1.000000</td>
      <td id="T_a496e_row7_col21" class="data row7 col21" >{'early_stop_patience_steps': 'int>=1 or -1(disable)'}</td>
      <td id="T_a496e_row7_col22" class="data row7 col22" >True</td>
      <td id="T_a496e_row7_col23" class="data row7 col23" >lstm_dropout</td>
      <td id="T_a496e_row7_col24" class="data row7 col24" >lstm_dropout=0.1</td>
      <td id="T_a496e_row7_col25" class="data row7 col25" >{'lstm_dropout': 'float in [0.0, 1.0]'}</td>
      <td id="T_a496e_row7_col26" class="data row7 col26" >True</td>
      <td id="T_a496e_row7_col27" class="data row7 col27" >True</td>
      <td id="T_a496e_row7_col28" class="data row7 col28" >True</td>
      <td id="T_a496e_row7_col29" class="data row7 col29" >{'futr_exog_list': 'list[str]', 'hist_exog_list': 'list[str]', 'stat_exog_list': 'list[str]'}</td>
      <td id="T_a496e_row7_col30" class="data row7 col30" >None</td>
      <td id="T_a496e_row7_col31" class="data row7 col31" >None</td>
      <td id="T_a496e_row7_col32" class="data row7 col32" >None</td>
      <td id="T_a496e_row7_col33" class="data row7 col33" >None</td>
    </tr>
    <tr>
      <th id="T_a496e_level0_row8" class="row_heading level0 row8" >8</th>
      <td id="T_a496e_row8_col0" class="data row8 col0" >AutoDeepNPTS</td>
      <td id="T_a496e_row8_col1" class="data row8 col1" >DeepNPTS</td>
      <td id="T_a496e_row8_col2" class="data row8 col2" >optuna</td>
      <td id="T_a496e_row8_col3" class="data row8 col3" >['ray', 'optuna']</td>
      <td id="T_a496e_row8_col4" class="data row8 col4" >True</td>
      <td id="T_a496e_row8_col5" class="data row8 col5" >True</td>
      <td id="T_a496e_row8_col6" class="data row8 col6" >Available (Enabled by Default)</td>
      <td id="T_a496e_row8_col7" class="data row8 col7" >Works with MedianPruner, HyperbandPruner, etc.</td>
      <td id="T_a496e_row8_col8" class="data row8 col8" >TPESampler</td>
      <td id="T_a496e_row8_col9" class="data row8 col9" >['TPESampler', 'RandomSampler', 'GridSampler', 'CmaEsSampler', 'NSGAIISampler', 'MOTPESampler', 'QMCSampler', 'BoTorchSampler']</td>
      <td id="T_a496e_row8_col10" class="data row8 col10" >MAE()</td>
      <td id="T_a496e_row8_col11" class="data row8 col11" >['Accuracy', 'AffineTransform', 'BaseISQF', 'BasePointLoss', 'Bernoulli', 'Beta', 'Categorical', 'Distribution', 'DistributionLoss', 'GMM', 'Gamma', 'HuberIQLoss', 'HuberLoss', 'HuberMQLoss', 'HuberQLoss', 'IQLoss', 'ISQF', 'MAE', 'MAPE', 'MASE', 'MQLoss', 'MSE', 'MixtureSameFamily', 'NBMM', 'NegativeBinomial', 'Normal', 'PMM', 'Poisson', 'QuantileLayer', 'QuantileLoss', 'RMSE', 'SMAPE', 'StudentT', 'TransformedDistribution', 'TukeyLoss', 'Tweedie']</td>
      <td id="T_a496e_row8_col12" class="data row8 col12" >None</td>
      <td id="T_a496e_row8_col13" class="data row8 col13" >['Accuracy', 'AffineTransform', 'BaseISQF', 'BasePointLoss', 'Bernoulli', 'Beta', 'Categorical', 'Distribution', 'DistributionLoss', 'GMM', 'Gamma', 'HuberIQLoss', 'HuberLoss', 'HuberMQLoss', 'HuberQLoss', 'IQLoss', 'ISQF', 'MAE', 'MAPE', 'MASE', 'MQLoss', 'MSE', 'MixtureSameFamily', 'NBMM', 'NegativeBinomial', 'Normal', 'PMM', 'Poisson', 'QuantileLayer', 'QuantileLoss', 'RMSE', 'SMAPE', 'StudentT', 'TransformedDistribution', 'TukeyLoss', 'Tweedie']</td>
      <td id="T_a496e_row8_col14" class="data row8 col14" >None</td>
      <td id="T_a496e_row8_col15" class="data row8 col15" >Any callable(study, trial)</td>
      <td id="T_a496e_row8_col16" class="data row8 col16" >scaler_type</td>
      <td id="T_a496e_row8_col17" class="data row8 col17" >standard</td>
      <td id="T_a496e_row8_col18" class="data row8 col18" >['identity', 'standard', 'robust', 'minmax']</td>
      <td id="T_a496e_row8_col19" class="data row8 col19" >True</td>
      <td id="T_a496e_row8_col20" class="data row8 col20" >-1.000000</td>
      <td id="T_a496e_row8_col21" class="data row8 col21" >{'early_stop_patience_steps': 'int>=1 or -1(disable)'}</td>
      <td id="T_a496e_row8_col22" class="data row8 col22" >True</td>
      <td id="T_a496e_row8_col23" class="data row8 col23" >dropout</td>
      <td id="T_a496e_row8_col24" class="data row8 col24" >dropout=0.1</td>
      <td id="T_a496e_row8_col25" class="data row8 col25" >{'dropout': 'float in [0.0, 1.0]'}</td>
      <td id="T_a496e_row8_col26" class="data row8 col26" >True</td>
      <td id="T_a496e_row8_col27" class="data row8 col27" >True</td>
      <td id="T_a496e_row8_col28" class="data row8 col28" >True</td>
      <td id="T_a496e_row8_col29" class="data row8 col29" >{'futr_exog_list': 'list[str]', 'hist_exog_list': 'list[str]', 'stat_exog_list': 'list[str]'}</td>
      <td id="T_a496e_row8_col30" class="data row8 col30" >None</td>
      <td id="T_a496e_row8_col31" class="data row8 col31" >None</td>
      <td id="T_a496e_row8_col32" class="data row8 col32" >None</td>
      <td id="T_a496e_row8_col33" class="data row8 col33" >None</td>
    </tr>
    <tr>
      <th id="T_a496e_level0_row9" class="row_heading level0 row9" >9</th>
      <td id="T_a496e_row9_col0" class="data row9 col0" >AutoDeepNPTS</td>
      <td id="T_a496e_row9_col1" class="data row9 col1" >DeepNPTS</td>
      <td id="T_a496e_row9_col2" class="data row9 col2" >ray</td>
      <td id="T_a496e_row9_col3" class="data row9 col3" >['ray', 'optuna']</td>
      <td id="T_a496e_row9_col4" class="data row9 col4" >True</td>
      <td id="T_a496e_row9_col5" class="data row9 col5" >False</td>
      <td id="T_a496e_row9_col6" class="data row9 col6" >Available (Manual Configuration Required)</td>
      <td id="T_a496e_row9_col7" class="data row9 col7" >Requires explicit scheduler like ASHAScheduler</td>
      <td id="T_a496e_row9_col8" class="data row9 col8" >BasicVariantGenerator</td>
      <td id="T_a496e_row9_col9" class="data row9 col9" >['BasicVariantGenerator', 'OptunaSearch', 'HyperOptSearch', 'BayesOptSearch', 'NevergradSearch', 'SkoptSearch', 'AxSearch', 'DragonflySearch', 'HEBO', 'BlendSearch']</td>
      <td id="T_a496e_row9_col10" class="data row9 col10" >MAE()</td>
      <td id="T_a496e_row9_col11" class="data row9 col11" >['Accuracy', 'AffineTransform', 'BaseISQF', 'BasePointLoss', 'Bernoulli', 'Beta', 'Categorical', 'Distribution', 'DistributionLoss', 'GMM', 'Gamma', 'HuberIQLoss', 'HuberLoss', 'HuberMQLoss', 'HuberQLoss', 'IQLoss', 'ISQF', 'MAE', 'MAPE', 'MASE', 'MQLoss', 'MSE', 'MixtureSameFamily', 'NBMM', 'NegativeBinomial', 'Normal', 'PMM', 'Poisson', 'QuantileLayer', 'QuantileLoss', 'RMSE', 'SMAPE', 'StudentT', 'TransformedDistribution', 'TukeyLoss', 'Tweedie']</td>
      <td id="T_a496e_row9_col12" class="data row9 col12" >None</td>
      <td id="T_a496e_row9_col13" class="data row9 col13" >['Accuracy', 'AffineTransform', 'BaseISQF', 'BasePointLoss', 'Bernoulli', 'Beta', 'Categorical', 'Distribution', 'DistributionLoss', 'GMM', 'Gamma', 'HuberIQLoss', 'HuberLoss', 'HuberMQLoss', 'HuberQLoss', 'IQLoss', 'ISQF', 'MAE', 'MAPE', 'MASE', 'MQLoss', 'MSE', 'MixtureSameFamily', 'NBMM', 'NegativeBinomial', 'Normal', 'PMM', 'Poisson', 'QuantileLayer', 'QuantileLoss', 'RMSE', 'SMAPE', 'StudentT', 'TransformedDistribution', 'TukeyLoss', 'Tweedie']</td>
      <td id="T_a496e_row9_col14" class="data row9 col14" >None</td>
      <td id="T_a496e_row9_col15" class="data row9 col15" >Any ray.tune.Callback</td>
      <td id="T_a496e_row9_col16" class="data row9 col16" >scaler_type</td>
      <td id="T_a496e_row9_col17" class="data row9 col17" >standard</td>
      <td id="T_a496e_row9_col18" class="data row9 col18" >['identity', 'standard', 'robust', 'minmax']</td>
      <td id="T_a496e_row9_col19" class="data row9 col19" >True</td>
      <td id="T_a496e_row9_col20" class="data row9 col20" >-1.000000</td>
      <td id="T_a496e_row9_col21" class="data row9 col21" >{'early_stop_patience_steps': 'int>=1 or -1(disable)'}</td>
      <td id="T_a496e_row9_col22" class="data row9 col22" >True</td>
      <td id="T_a496e_row9_col23" class="data row9 col23" >dropout</td>
      <td id="T_a496e_row9_col24" class="data row9 col24" >dropout=0.1</td>
      <td id="T_a496e_row9_col25" class="data row9 col25" >{'dropout': 'float in [0.0, 1.0]'}</td>
      <td id="T_a496e_row9_col26" class="data row9 col26" >True</td>
      <td id="T_a496e_row9_col27" class="data row9 col27" >True</td>
      <td id="T_a496e_row9_col28" class="data row9 col28" >True</td>
      <td id="T_a496e_row9_col29" class="data row9 col29" >{'futr_exog_list': 'list[str]', 'hist_exog_list': 'list[str]', 'stat_exog_list': 'list[str]'}</td>
      <td id="T_a496e_row9_col30" class="data row9 col30" >None</td>
      <td id="T_a496e_row9_col31" class="data row9 col31" >None</td>
      <td id="T_a496e_row9_col32" class="data row9 col32" >None</td>
      <td id="T_a496e_row9_col33" class="data row9 col33" >None</td>
    </tr>
    <tr>
      <th id="T_a496e_level0_row10" class="row_heading level0 row10" >10</th>
      <td id="T_a496e_row10_col0" class="data row10 col0" >AutoDilatedRNN</td>
      <td id="T_a496e_row10_col1" class="data row10 col1" >DilatedRNN</td>
      <td id="T_a496e_row10_col2" class="data row10 col2" >optuna</td>
      <td id="T_a496e_row10_col3" class="data row10 col3" >['ray', 'optuna']</td>
      <td id="T_a496e_row10_col4" class="data row10 col4" >True</td>
      <td id="T_a496e_row10_col5" class="data row10 col5" >True</td>
      <td id="T_a496e_row10_col6" class="data row10 col6" >Available (Enabled by Default)</td>
      <td id="T_a496e_row10_col7" class="data row10 col7" >Works with MedianPruner, HyperbandPruner, etc.</td>
      <td id="T_a496e_row10_col8" class="data row10 col8" >TPESampler</td>
      <td id="T_a496e_row10_col9" class="data row10 col9" >['TPESampler', 'RandomSampler', 'GridSampler', 'CmaEsSampler', 'NSGAIISampler', 'MOTPESampler', 'QMCSampler', 'BoTorchSampler']</td>
      <td id="T_a496e_row10_col10" class="data row10 col10" >MAE()</td>
      <td id="T_a496e_row10_col11" class="data row10 col11" >['Accuracy', 'AffineTransform', 'BaseISQF', 'BasePointLoss', 'Bernoulli', 'Beta', 'Categorical', 'Distribution', 'DistributionLoss', 'GMM', 'Gamma', 'HuberIQLoss', 'HuberLoss', 'HuberMQLoss', 'HuberQLoss', 'IQLoss', 'ISQF', 'MAE', 'MAPE', 'MASE', 'MQLoss', 'MSE', 'MixtureSameFamily', 'NBMM', 'NegativeBinomial', 'Normal', 'PMM', 'Poisson', 'QuantileLayer', 'QuantileLoss', 'RMSE', 'SMAPE', 'StudentT', 'TransformedDistribution', 'TukeyLoss', 'Tweedie']</td>
      <td id="T_a496e_row10_col12" class="data row10 col12" >None</td>
      <td id="T_a496e_row10_col13" class="data row10 col13" >['Accuracy', 'AffineTransform', 'BaseISQF', 'BasePointLoss', 'Bernoulli', 'Beta', 'Categorical', 'Distribution', 'DistributionLoss', 'GMM', 'Gamma', 'HuberIQLoss', 'HuberLoss', 'HuberMQLoss', 'HuberQLoss', 'IQLoss', 'ISQF', 'MAE', 'MAPE', 'MASE', 'MQLoss', 'MSE', 'MixtureSameFamily', 'NBMM', 'NegativeBinomial', 'Normal', 'PMM', 'Poisson', 'QuantileLayer', 'QuantileLoss', 'RMSE', 'SMAPE', 'StudentT', 'TransformedDistribution', 'TukeyLoss', 'Tweedie']</td>
      <td id="T_a496e_row10_col14" class="data row10 col14" >None</td>
      <td id="T_a496e_row10_col15" class="data row10 col15" >Any callable(study, trial)</td>
      <td id="T_a496e_row10_col16" class="data row10 col16" >scaler_type</td>
      <td id="T_a496e_row10_col17" class="data row10 col17" >robust</td>
      <td id="T_a496e_row10_col18" class="data row10 col18" >['identity', 'standard', 'robust', 'minmax']</td>
      <td id="T_a496e_row10_col19" class="data row10 col19" >True</td>
      <td id="T_a496e_row10_col20" class="data row10 col20" >-1.000000</td>
      <td id="T_a496e_row10_col21" class="data row10 col21" >{'early_stop_patience_steps': 'int>=1 or -1(disable)'}</td>
      <td id="T_a496e_row10_col22" class="data row10 col22" >False</td>
      <td id="T_a496e_row10_col23" class="data row10 col23" >None</td>
      <td id="T_a496e_row10_col24" class="data row10 col24" >None</td>
      <td id="T_a496e_row10_col25" class="data row10 col25" >None</td>
      <td id="T_a496e_row10_col26" class="data row10 col26" >True</td>
      <td id="T_a496e_row10_col27" class="data row10 col27" >True</td>
      <td id="T_a496e_row10_col28" class="data row10 col28" >True</td>
      <td id="T_a496e_row10_col29" class="data row10 col29" >{'futr_exog_list': 'list[str]', 'hist_exog_list': 'list[str]', 'stat_exog_list': 'list[str]'}</td>
      <td id="T_a496e_row10_col30" class="data row10 col30" >None</td>
      <td id="T_a496e_row10_col31" class="data row10 col31" >None</td>
      <td id="T_a496e_row10_col32" class="data row10 col32" >None</td>
      <td id="T_a496e_row10_col33" class="data row10 col33" >None</td>
    </tr>
    <tr>
      <th id="T_a496e_level0_row11" class="row_heading level0 row11" >11</th>
      <td id="T_a496e_row11_col0" class="data row11 col0" >AutoDilatedRNN</td>
      <td id="T_a496e_row11_col1" class="data row11 col1" >DilatedRNN</td>
      <td id="T_a496e_row11_col2" class="data row11 col2" >ray</td>
      <td id="T_a496e_row11_col3" class="data row11 col3" >['ray', 'optuna']</td>
      <td id="T_a496e_row11_col4" class="data row11 col4" >True</td>
      <td id="T_a496e_row11_col5" class="data row11 col5" >False</td>
      <td id="T_a496e_row11_col6" class="data row11 col6" >Available (Manual Configuration Required)</td>
      <td id="T_a496e_row11_col7" class="data row11 col7" >Requires explicit scheduler like ASHAScheduler</td>
      <td id="T_a496e_row11_col8" class="data row11 col8" >BasicVariantGenerator</td>
      <td id="T_a496e_row11_col9" class="data row11 col9" >['BasicVariantGenerator', 'OptunaSearch', 'HyperOptSearch', 'BayesOptSearch', 'NevergradSearch', 'SkoptSearch', 'AxSearch', 'DragonflySearch', 'HEBO', 'BlendSearch']</td>
      <td id="T_a496e_row11_col10" class="data row11 col10" >MAE()</td>
      <td id="T_a496e_row11_col11" class="data row11 col11" >['Accuracy', 'AffineTransform', 'BaseISQF', 'BasePointLoss', 'Bernoulli', 'Beta', 'Categorical', 'Distribution', 'DistributionLoss', 'GMM', 'Gamma', 'HuberIQLoss', 'HuberLoss', 'HuberMQLoss', 'HuberQLoss', 'IQLoss', 'ISQF', 'MAE', 'MAPE', 'MASE', 'MQLoss', 'MSE', 'MixtureSameFamily', 'NBMM', 'NegativeBinomial', 'Normal', 'PMM', 'Poisson', 'QuantileLayer', 'QuantileLoss', 'RMSE', 'SMAPE', 'StudentT', 'TransformedDistribution', 'TukeyLoss', 'Tweedie']</td>
      <td id="T_a496e_row11_col12" class="data row11 col12" >None</td>
      <td id="T_a496e_row11_col13" class="data row11 col13" >['Accuracy', 'AffineTransform', 'BaseISQF', 'BasePointLoss', 'Bernoulli', 'Beta', 'Categorical', 'Distribution', 'DistributionLoss', 'GMM', 'Gamma', 'HuberIQLoss', 'HuberLoss', 'HuberMQLoss', 'HuberQLoss', 'IQLoss', 'ISQF', 'MAE', 'MAPE', 'MASE', 'MQLoss', 'MSE', 'MixtureSameFamily', 'NBMM', 'NegativeBinomial', 'Normal', 'PMM', 'Poisson', 'QuantileLayer', 'QuantileLoss', 'RMSE', 'SMAPE', 'StudentT', 'TransformedDistribution', 'TukeyLoss', 'Tweedie']</td>
      <td id="T_a496e_row11_col14" class="data row11 col14" >None</td>
      <td id="T_a496e_row11_col15" class="data row11 col15" >Any ray.tune.Callback</td>
      <td id="T_a496e_row11_col16" class="data row11 col16" >scaler_type</td>
      <td id="T_a496e_row11_col17" class="data row11 col17" >robust</td>
      <td id="T_a496e_row11_col18" class="data row11 col18" >['identity', 'standard', 'robust', 'minmax']</td>
      <td id="T_a496e_row11_col19" class="data row11 col19" >True</td>
      <td id="T_a496e_row11_col20" class="data row11 col20" >-1.000000</td>
      <td id="T_a496e_row11_col21" class="data row11 col21" >{'early_stop_patience_steps': 'int>=1 or -1(disable)'}</td>
      <td id="T_a496e_row11_col22" class="data row11 col22" >False</td>
      <td id="T_a496e_row11_col23" class="data row11 col23" >None</td>
      <td id="T_a496e_row11_col24" class="data row11 col24" >None</td>
      <td id="T_a496e_row11_col25" class="data row11 col25" >None</td>
      <td id="T_a496e_row11_col26" class="data row11 col26" >True</td>
      <td id="T_a496e_row11_col27" class="data row11 col27" >True</td>
      <td id="T_a496e_row11_col28" class="data row11 col28" >True</td>
      <td id="T_a496e_row11_col29" class="data row11 col29" >{'futr_exog_list': 'list[str]', 'hist_exog_list': 'list[str]', 'stat_exog_list': 'list[str]'}</td>
      <td id="T_a496e_row11_col30" class="data row11 col30" >None</td>
      <td id="T_a496e_row11_col31" class="data row11 col31" >None</td>
      <td id="T_a496e_row11_col32" class="data row11 col32" >None</td>
      <td id="T_a496e_row11_col33" class="data row11 col33" >None</td>
    </tr>
    <tr>
      <th id="T_a496e_level0_row12" class="row_heading level0 row12" >12</th>
      <td id="T_a496e_row12_col0" class="data row12 col0" >AutoFEDformer</td>
      <td id="T_a496e_row12_col1" class="data row12 col1" >FEDformer</td>
      <td id="T_a496e_row12_col2" class="data row12 col...(truncated)
引数は上記の設定にしたいですが、そのように定義、設計されているか確認して教えてください。

## Response:
思考時間: 48s

了解。この表の仕様で“引数をこう定義する／できているか”という観点でざっと整合チェックしました。結論から言うと、設計としては筋が通っていて、実装に落としやすい一貫性になっています。細部の注意点だけ押さえれば、そのまま採用で問題ありません。

仕様として成立している点（OK）
================

*   **backend と探索器**
    *   行ごとに `backend` が `optuna` / `ray` で分かれ、`backend_choices=['ray','optuna']`。
    *   `optuna` 系は `search_alg=TPESampler` 既定、`ray` 系は `BasicVariantGenerator` 既定。自然です。
*   **プルーナ（途中打ち切り）**
    *   すべて `pruner_available=True`。`optuna` 行は `pruner_default_enabled=True`（＝既定で有効）、`ray` 行は `False`（＝明示スケジューラ必須）という整理は合理的。備考の「Ray は ASHAScheduler など明示要」も矛盾なし。
*   **損失関数**
    *   既定・候補ともに広く網羅。とくに **DeepAR** が `loss_default=DistributionLoss()`、`valid_loss_default=MQLoss()` になっているのは、分布予測モデルとして妥当。DLinear/Autoformer 系の `MAE()` 既定も違和感なし。
*   **スケーラ（前処理）**
    *   `scaler_param=scaler_type`、既定はモデルごとに `identity / standard / robust`。候補 `['identity','standard','robust','minmax']` で統一。
*   **早期終了**
    *   `early_stop_supported=True`、既定 `early_stop_default=-1`（無効化）、選択肢が `{'early_stop_patience_steps': 'int>=1 or -1(disable)'}` に集約。表現はシンプルで実装容易。
*   **ドロップアウト**
    *   モデルごとに可否が分かれており整合的。
        *   Autoformer/DeepNPTS は `dropout`、DeepAR は `lstm_dropout`、DLinear/DilatedRNN は `dropout_supported=False` で関連パラメタ一式 `None`。衝突なし。
*   **外生変数（exog）**
    *   `exog_F/H/S=True`、インタフェースを `{'futr_exog_list','hist_exog_list','stat_exog_list'}` に統一。API から渡す型が明確。

実装時にだけ注意してほしいポイント（要チェック）
========================

1.  **Ray 側の早期終了**
    *   表の `early_stop_*` は「学習ループの早期終了」パラメタに見えます。Ray では **探索の途中停止** は ASHA 等のスケジューラ側で行うため、**学習内部の patience と探索スケジューラの停止が二重にならない**よう、責務分離を確認（Ray 行の既定が `-1` で無効なのはその狙いとして正しい）。
2.  **コールバック型の厳密化**
    *   Optuna 行の `callbacks_choices=Any callable(study, trial)`、Ray 行の `Any ray.tune.Callback` は型が異なるので、**backend に応じた型チェック**をラッパーで確実に。`callbacks_state=None` は「未設定」を意味し、シリアライズ時に落ちないことを確認。
3.  **スケーラの適用順序**
    *   `scaler_type='identity'` のときは **fit/transform を完全スキップ**して漏れなく無処理に。学習・検証・予測で**同一パイプライン**が使われ、リークが起きないことをテストで担保。
4.  **損失の互換性**
    *   DeepAR のように「分布出力」を前提とするモデルで `MAE()` など **点予測用損失を誤って選択できない**ように、**モデル×損失の互換性バリデーション**を一箇所にまとめると安全。
5.  **ドロップアウトの分岐**
    *   `dropout_supported=False` のモデルへは、探索空間に `dropout` が出ない／コンストラクタに渡らないことをユニットテストで確認。DeepAR だけ `lstm_dropout` 名が異なる点もバリデーションに含める。
6.  **h（予測ホライズン）欄がすべて None**
    *   仕様として「ホライズンは fit/predict 時の引数で与える」設計なら OK。そうでない場合は、**モデル既定 or データセット由来**などの決め方を 1 箇所に定義し、`None` を許容するパスで例外にならないことを確認。

最小セットの動作テスト（提案）
===============

*   **バックエンド切替**：同一タスクで `backend=optuna` / `ray` を差し替え、プルーナ既定の有効/無効と探索器既定の切替を確認。
*   **外生変数**：`futr_exog_list/hist_exog_list/stat_exog_list` を各 1 つずつ与えて全モデルがクラッシュしないこと。
*   **ドロップアウト**：`dropout_supported=False` モデルで `dropout` を探索空間に入れても**無視 or エラー**のどちらかに統一（推奨：明示エラー）。
*   **損失の互換性**：DeepAR に `MAE()` を選ぶと即時バリデーションエラーになること。
*   **patience=-1**：両 backend で “学習は最後まで回る／探索はスケジューラ頼み（Ray）” の意図通りに振る舞うこと。

この表を「単一ソース・オブ・トゥルース」として定数化し、上のバリデータで弾けば、現場での事故はかなり抑えられます。次は “モデル×損失×外生×バックエンド” のクロスで 2–3 ケースずつスモークを回すと仕上がりが堅くなります。

## Prompt:
アップロードした資料を確認して設計に上記のパラメータが設定できるように設計されているか確認して状況を教えてください。

## Response:
思考時間: 1m 4s

了解しました。アップロード資料を横断であたり、設計上「そのパラメータを設定できるようにしているか」を項目別に確認しました。要点だけサクッと👇

### まとめ（対応状況）

*   **探索バックエンド（Optuna / Ray）**  
    対応あり。Optuna前提の探索パイプラインに加え、Ray 利用可否も検出・登録の設計が入っています。C4\_ARCHITECTURE\_DIAGRAMS SEQUENCE\_DIAGRAMS\_DETAILED
*   **探索アルゴリズム（TPE / CMA-ES / Random / Grid / ASHA）**  
    設計に明記。ASHA（非同期ハルビング）まで表で列挙済み。01\_REQUIREMENTS\_SPECIFICATION\_D…
*   **プルーニング（中間結果での打切り）**  
    探索ループで「Early Stop チェック」あり。ASHA採用と合わせて“打切り”の設計意図は読み取れますが、**「pruner\_enabled」のような明示フラグ**は資料内で未確認。C4\_ARCHITECTURE\_DIAGRAMS 01\_REQUIREMENTS\_SPECIFICATION\_D…
*   **Early Stopping / patience**  
    `ModelTrainer.train(..., early_stopping=True, early_stopping_patience=10)` で指定可。**patience=-1 で無効化**といった“特殊値仕様”は未記載。01\_REQUIREMENTS\_SPECIFICATION\_D…
*   **コールバック（Callbacks）**  
    `callbacks: Optional[List[Callback]]` を受ける想定で設計済み。01\_REQUIREMENTS\_SPECIFICATION\_D…
*   **損失関数（MAE/MSE/DistributionLoss/MQLoss 等）**  
    Loss のレジストリ化・自動検出を設計。分位点（τ）の扱いも用語集に明記され、分位損失系を前提にした記述があります。SEQUENCE\_DIAGRAMS\_DETAILED 05\_DATABASE\_DESIGN\_DETAILED
*   **分位点（quantiles/τ）**  
    τベクトルの概念説明あり（例：τ=\[0.1,0.5,0.9\]）。API例でもメトリクスや設定が JSON に載る前提。05\_DATABASE\_DESIGN\_DETAILED 06\_API\_DESIGN\_DETAILED
*   **スケーラー種別（identity / standard / robust / minmax）**  
    Scaler のレジストリ化と自動検出は設計済み。ただし**具体的に “Identity/Standard/Robust/MinMax” の4種を固定で持つ記述は未記載**（拡張で登録して使う想定）。ER\_AND\_CLASS\_DIAGRAMS SEQUENCE\_DIAGRAMS\_DETAILED
*   **外生変数（futr\_exog\_list / hist\_exog\_list / stat\_exog\_list）**  
    用語とデータ層のエンコーダ設計が明確。モデル能力分析でも外生・静的特徴のサポート検知が入っています。05\_DATABASE\_DESIGN\_DETAILED ER\_AND\_CLASS\_DIAGRAMS SEQUENCE\_DIAGRAMS\_DETAILED
*   **予測期間 h / 安全な h（safe\_h）**  
    `CombinationGenerator` で `calculate_safe_h` を呼ぶ設計が明記され、`h` と `safe_h` の両立を考慮しています。C4\_ARCHITECTURE\_DIAGRAMS
*   **検証分割（val\_size など）**  
    `ModelCapabilityAnalyzer` で `check_val_size_support()` を実装する想定。FAQ/ガイドでも検証分割の方針を触れています。SEQUENCE\_DIAGRAMS\_DETAILED 01\_REQUIREMENTS\_SPECIFICATION\_D…
*   **実行系パラメータ（並列・デバイス・精度・勾配クリップなど）**  
    `ExecutionConfig` に `max_workers / allow_ray_parallel / accelerator / devices / precision / gradient_clip_val / early_stopping_patience` 等が揃っており、環境変数経由の設定も設計済み。04\_CLASS\_DESIGN\_DETAILED 04\_CLASS\_DESIGN\_DETAILED
*   **モデル別 dropout 設定**  
    モデル能力分析・自動検知はあるものの、**ドロップアウトのマッピングは N-HiTS / N-BEATS / AutoLSTM / TFT / RNN/GRU 例が中心**。**DeepAR の `lstm_dropout` といった“モデル固有名のパラメータ”は資料では未記載**。05\_DATABASE\_DESIGN\_DETAILED

* * *

### 評価

*   「探索まわり（バックエンド/アルゴリズム/打切り）」「学習実行（ES/Callbacks）」「データ表現（外生変数）」「h／safe\_h」「実行系（並列/GPU/精度）」は**設計に反映済み**。
*   一方で、**“特定モデルの固有ハイパーパラメータ名まで固定化して指定できるか”**、**“スケーラーのプリセット種類を固定で持つか”**、**“patience=-1 で ES 無効化”のような特殊値仕様**は**未記載/要補足**です。SEQUENCE\_DIAGRAMS\_DETAILED ER\_AND\_CLASS\_DIAGRAMS 01\_REQUIREMENTS\_SPECIFICATION\_D…

* * *

### 次の一手（軽めの提案）

*   「**パラメータ互換表**」を 1 枚にまとめ、  
    `<論理名> ↔ <実装キー> ↔ <対応モデル> ↔ <許容値/デフォルト>` を列挙すると、運用での齟齬が消えます。Loss/Scaler/Callback/ES/ValSplit/Exog/h を横串に。根拠はレジストリ設計がすでにあるため（登録＝可視化が近道）。ER\_AND\_CLASS\_DIAGRAMS SEQUENCE\_DIAGRAMS\_DETAILED

他にも確認対象があれば、同じ基準で洗い出して追記します。

## Prompt:
パラメータ互換表を作成してください

## Response:
思考時間: 18s

了解。いただいた仕様テーブル（Autoformer/DeepAR/DLinear などの行を含む一覧）を基準に、「論理パラメータ ↔ 実装キー ↔ 型/許容値 ↔ 既定値 ↔ 対応モデル ↔ 設定箇所 ↔ 注意点」を一本化した“パラメータ互換表”を作りました。  
（※テーブルは長いのでテーマ別に分割。表記は「例：…」で代表モデルを示し、同系統は同じルールで解釈できます。）

* * *

探索バックエンド / 探索アルゴリズム / プルーニング
============================

| 論理名 | 実装キー | 型・許容値 | 既定値（例） | 対応モデル | 設定箇所 | 注意点 |
| --- | --- | --- | --- | --- | --- | --- |
| 探索バックエンド | `backend` | `{'optuna','ray'}` | モデル行の既定に準拠（例：Autoformer=optuna行/ ray行あり） | 全モデル | 実験設定（YAML/JSON）/API | バックエンドで下位の検索器・プルーナのクラスが変わる |
| 探索アルゴリズム（Optuna） | `search_alg` | `{'TPESampler','RandomSampler','GridSampler','CmaEsSampler','NSGAIISampler','MOTPESampler','QMCSampler','BoTorchSampler'}` | `TPESampler` | Optuna行すべて | 同上 | 連続・離散・多目的に応じて選択（NSGAII=多目的など） |
| 探索アルゴリズム（Ray） | `search_alg` | `{'BasicVariantGenerator','OptunaSearch','HyperOptSearch','BayesOptSearch','NevergradSearch','SkoptSearch','AxSearch','DragonflySearch','HEBO','BlendSearch'}` | `BasicVariantGenerator` | Ray行すべて | 同上 | Ray は“検索器”と“スケジューラ(ASHAScheduler 等)”を組合せる前提 |
| プルーナ可否 | `pruner_available` | `bool` | `True` | 全モデル | 仕様固定 | 利用可能かの宣言。実行有無は次行で分岐 |
| プルーナ既定 | `pruner_default_enabled` | `bool` | Optuna行=`True` / Ray行=`False` | 全モデル | 実験設定/API | Ray は明示スケジューラ必須（ASHAScheduler 等） |
| プルーナ備考 | `pruner_note` | 文字列 | 例：「MedianPruner, HyperbandPruner…」 | 全モデル | ドキュメント | 実体はバックエンド固有のクラスへマップ |

* * *

損失・検証損失・コールバック
==============

| 論理名 | 実装キー | 型・許容値 | 既定値（例） | 対応モデル | 設定箇所 | 注意点 |
| --- | --- | --- | --- | --- | --- | --- |
| 損失関数 | `loss` | 表に列挙の損失群（`MAE`,`MSE`,`RMSE`,`MAPE`,`SMAPE`,`Huber*`,`Quantile*`,`DistributionLoss`,`StudentT` など） | 例：Autoformer=MAE / DeepAR=DistributionLoss | 全モデル（互換に注意） | 学習設定/API | **分布出力モデル（例：DeepAR）は Distribution 系が前提**。不整合は起動前に検証 |
| 検証損失 | `valid_loss` | 上記同様 | 例：DeepAR=MQLoss / 多くの行で `None` | 全モデル | 学習設定/API | `None` は「学習損失を流用」or「フレームワーク既定」を意味する設計で統一 |
| コールバック | `callbacks` | Optuna：任意`callable(study, trial)` / Ray：`List[ray.tune.Callback]` | `None` | 全モデル | 実験設定/コード | **backend で型が異なる**ため、起動時に型バリデーションを実施 |

* * *

前処理（スケーラ）
=========

| 論理名 | 実装キー | 型・許容値 | 既定値（例） | 対応モデル | 設定箇所 | 注意点 |
| --- | --- | --- | --- | --- | --- | --- |
| スケーラ種別 | `scaler_type` | `{'identity','standard','robust','minmax'}` | モデル別：例）Autoformer=identity / DeepNPTS=standard / DilatedRNN=robust | 全モデル | 前処理設定/API | `identity` は完全スキップ。fit/transform の順守とリーク防止を徹底 |

* * *

早期終了（Early Stopping）
====================

| 論理名 | 実装キー | 型・許容値 | 既定値 | 対応モデル | 設定箇所 | 注意点 |
| --- | --- | --- | --- | --- | --- | --- |
| ES有効 | `early_stop_supported` | `bool` | `True` | 全モデル | 仕様固定 | 機構の有無 |
| ESパラメータ | `early_stop_patience_steps` | `int>=1` または `-1`（無効） | `-1` | 全モデル | 学習設定/API | Ray での“探索停止”は ASHA など**スケジューラ**側、学習内部 ES と二重化しない |

* * *

ドロップアウト（モデル別）
=============

| 論理名 | 実装キー | 型・許容値 | 既定値（例） | 対応モデル | 設定箇所 | 注意点 |
| --- | --- | --- | --- | --- | --- | --- |
| ドロップアウト対応 | `dropout_supported` | `bool` | モデル別 | 全モデル | 仕様固定 | 非対応モデルに値を渡さない（渡したら明示エラー推奨） |
| ドロップアウト率（汎用） | `dropout` | `[0.0,1.0]` | 例：Autoformer=0.05 / DeepNPTS=0.1 / BiTCN=0.5 | Autoformer, DeepNPTS, BiTCN ほか | モデル設定/探索 | モデルにより層の適用位置は異なる |
| LSTMドロップアウト | `lstm_dropout` | `[0.0,1.0]` | 例：DeepAR=0.1 | DeepAR | モデル設定/探索 | **DeepARのみキー名が異なる**。汎用`dropout`と混同しない |
| ドロップアウト未対応 | `dropout_supported=False` | ― | ― | 例：DLinear, DilatedRNN | ― | ハイパラ空間に含めない／指定時は検証で即時エラー |

* * *

外生変数（Exogenous）
===============

| 論理名 | 実装キー | 型・許容値 | 既定値 | 対応モデル | 設定箇所 | 注意点 |
| --- | --- | --- | --- | --- | --- | --- |
| 未来外生 | `futr_exog_list` | `list[str]` | `[]` | 多くのモデルで `exog_F=True` | データパイプライン/モデル | 予測時点で既知の未来説明変数のみ |
| 履歴外生 | `hist_exog_list` | `list[str]` | `[]` | `exog_H=True` | 同上 | 学習・予測で**同じ特徴前処理**を共有 |
| 静的外生 | `stat_exog_list` | `list[str]` | `[]` | `exog_S=True` | 同上 | エンティティ（系列）固定属性。ターゲットリークに注意 |

* * *

予測ホライズン / 分割
============

| 論理名 | 実装キー | 型・許容値 | 既定値 | 対応モデル | 設定箇所 | 注意点 |
| --- | --- | --- | --- | --- | --- | --- |
| 予測ホライズン | `h` | `int>=1` | ―（行では `None`） | 全モデル | `fit/predict` 引数/実験設定 | 設計は**呼出し側で指定**する流儀。データ量から `safe_h` を別途計算する設計が想定 |
| 最小ホライズン | `h_min` | `int>=1` | ―（`None`） | モデル/データ依存 | 仕様 | 不足時は警告 or 例外 |
| ホライズン由来 | `h_source` | `{'cli','config','api',...}` | ―（`None`） | 全モデル | ログ/メタ | 由来を残すと再現性が上がる |
| 検証分割サイズ | `val_size` 等 | `int>=1 or ratio(0,1)` | プロジェクト既定 | 全モデル | 実験設定/データ分割器 | シーズナリティや `h` と整合するよう設定 |

* * *

実行系（計算資源・精度ほか）
==============

| 論理名 | 実装キー（例） | 型・許容値 | 既定値 | 対応モデル | 設定箇所 | 注意点 |
| --- | --- | --- | --- | --- | --- | --- |
| 並列実行 | `max_workers`,`allow_ray_parallel` | `int>=1`,`bool` | 環境既定 | 全モデル | 実行設定 | Ray 併用時は試行レベルの並列と学習内部の並列の**競合**に注意 |
| デバイス | `accelerator`,`devices` | `{'cpu','gpu'}`, `int>=1` | 環境検出 | 全モデル | 実行設定 | GPU有無でバッチや勾配精度を調整 |
| 精度 | `precision` | 例：`32`,`16-mixed` | `32` | 全モデル | 実行設定 | 16bitは速度↔安定性のトレードオフ |
| 勾配クリップ | `gradient_clip_val` | `float>=0` | 0（無効） | 全モデル | 学習設定 | 競合タスクで発散防止に有効 |

* * *

使い方の目安（具体例）
-----------

*   **Autoformer（Optuna）で基本構成**
    ```yaml
    backend: optuna
    search_alg: TPESampler
    pruner_default_enabled: true
    loss: MAE
    scaler_type: identity
    early_stop_patience_steps: -1
    dropout_supported: true
    dropout: 0.05
    futr_exog_list: []
    hist_exog_list: []
    stat_exog_list: []
    ```
*   **DeepAR（Ray）で分布学習＋ASHA**
    ```yaml
    backend: ray
    search_alg: BasicVariantGenerator
    scheduler: ASHAScheduler   # Ray側
    pruner_default_enabled: false
    loss: DistributionLoss
    valid_loss: MQLoss
    scaler_type: identity
    lstm_dropout: 0.1
    early_stop_patience_steps: -1   # 学習内部ESは無効、停止はASHA側に委譲
    ```

* * *

### 運用メモ（互換を壊さないコツ）

*   **モデル×損失の互換性チェック**を起動前に必須化（DeepAR に MAE を選べない等）。
*   **ドロップアウトのキー名分岐**（`dropout` / `lstm_dropout`）をラッパー層で吸収。
*   **Ray の探索停止 vs 学習内部ES**の二重停止を避けるため、Ray運用時は `early_stop_patience_steps=-1` を推奨。
*   **`identity` スケーラ**時は前処理ステップ自体をスキップし、リーク検査は常時オン。

必要なら、この互換表をそのまま **CSV / YAML スキーマ**に落として、静的バリデータ（例：JSON Schema + 追加ルール）も付けます。

## Prompt:
予測や再学習に指定できるパラメータの記載内容も調査して教えてください。

## Response:
思考時間: 1m 15s

了解です。アップロード資料に基づき、「予測（推論）」と「再学習（学習・探索・トリガ）」で“指定できる”パラメータを、入口（CLI / REST / Python API / 実行設定）ごとに整理しました。

予測（推論）で指定できるパラメータ
=================

**CLI（nf-runner predict）**

*   `--model-id`（使用する学習済みモデル）
*   `--data`（入力データCSV）
*   `--h`（予測ホライズン）
*   `--output`（出力先パス）  
    ※ 入力データは `unique_id, ds, y` と外生変数（exogenous）。未来用は `futr_*`、過去用は `hist_*`、静的は `stat_*` という接頭辞ルールを採用。 18\_QUICKSTART

**REST API**

*   `/v1/predictions`（設計書の名称上、Predict API 相当）
    *   `model_id`, `prediction_date`, `horizon`
    *   `input_data`: 行配列（`unique_id`, `ds`, `y`, 任意の外生変数）
    *   `metadata.confidence_level`（信頼区間の期待度合い）  
        API 仕様のボディ例として上記キーが明示されています。 06\_API\_DESIGN\_DETAILED

**Python API（Forecaster）**

*   `predict_one_step(...)`
    *   `include_history`（履歴も返すか）
    *   `return_quantiles` / `quantiles`（分位点出力の制御）  
        推論パラメータの想定が要件定義に記載されています。 01\_REQUIREMENTS\_SPECIFICATION\_D…

**データ必須カラム**

*   `unique_id`, `ds`, `y` は必須。`ds` は datetime 型へ正規化。 15\_TROUBLESHOOTING\_GUIDE

再学習（学習・探索・評価・トリガ）で指定できるパラメータ
============================

**CLI（nf-runner train）**

*   学習系の主なフラグ：
    *   `--data`（学習データ）, `--models`（例: `AutoNHITS,AutoLSTM`）
    *   `--h`（評価ホライズン）, `--val-size`（検証分割比）
    *   `--batch-size`（バッチサイズ）, `--max-steps`（学習ステップ上限）
    *   `--backend`（`cpu`/`cuda` など）, `--max-workers`（並列度）
    *   探索系：`--search-alg`（例: `optuna`）, `--num-trials`（試行回数）
    *   ログ関連：`--log-level`  
        クイックスタートにコマンド例・デフォルトの目安がまとまっています。 18\_QUICKSTART

**Python API（ModelTrainer）**

*   `train(model, train_df, *, val_df=None, hyperparameters=None, callbacks=None, early_stopping=True, early_stopping_patience=10, checkpoint_dir=None)`  
    ハイパーパラメータ辞書・コールバック・Early Stopping の有無/Patience・チェックポイント保存先などを指定可能。 01\_REQUIREMENTS\_SPECIFICATION\_D…

**ハイパーパラメータ探索（設計）**

*   アルゴリズムと主な指定項目：
    *   **TPE**（`n_trials`, `n_startup_trials`）
    *   **CMA-ES**（`sigma0`, `n_trials`）
    *   **Random / Grid**（`n_trials` / `param_grid`）
    *   **ASHA**（`max_t`, `grace_period`）  
        探索アルゴリズムと調整パラメータが要件に定義されています。 01\_REQUIREMENTS\_SPECIFICATION\_D…

**実行設定（ExecutionConfig：環境変数で上書き可）**

*   乱数・探索・並列・保存：
    *   `RANDOM_STATE`, `TRIAL_NUM_SAMPLES`, `TRIAL_MAX_STEPS`
    *   `DEFAULT_H`, `H_RATIO`, `MAX_WORKERS`, `ALLOW_RAY_PARALLEL`
    *   `SAVE_MODEL`, `OVERWRITE_MODEL`
*   外生変数の上限：
    *   `MAX_EXOG_FUTR`, `MAX_EXOG_HIST`, `MAX_EXOG_STAT`
*   学習の安定化・デバイス：
    *   `EARLY_STOPPING_PATIENCE`, `GRADIENT_CLIP_VAL`
    *   `ACCELERATOR`（`cpu/cuda/mps`）, `DEVICES`, `PRECISION`（`32/16/bf16`）  
        上記はクラス定義と環境変数マッピングとして記述されています。 04\_CLASS\_DESIGN\_DETAILED

**性能・安定化のための運用上のノブ（参考）**

*   例：バッチサイズ縮小、GPUバックエンド指定、`max-steps`短縮、並列度調整。CLI 例が記載。 18\_QUICKSTART
*   トラブル時のチューニング例として、`precision='16-mixed'`（Mixed Precision）、`early_stopping_patience` などの調整がガイドに記載。 15\_TROUBLESHOOTING\_GUIDE

**評価・バックテストに関わる指定**

*   シーケンス図/設計では、`Evaluator.backtest` による評価→メトリクス保存（`mae`, `rmse` 例）が示されています。CLI の `--h` と `--val-size` が評価条件に効く位置づけです。 03\_ARCHITECTURE\_DESIGN\_DETAILED

**再学習トリガ（スケジュール/ドリフト検知）**

*   スケジューラ→データモニタ→ドリフト検知→`trigger_retrain(reason="drift")` の流れが定義。再学習イベント理由を保存して実行、通知までの線形が明示。※具体的なしきい値名は本文に未定義（フロー設計のみ）。

**予測結果スキーマ上の“horizon”**

*   予測テーブルのスキーマに `horizon` を保持（本番保存の観点）。学習・推論時の指定がそのまま追跡可能。 05\_DATABASE\_DESIGN\_DETAILED

* * *

使い分けの最短サンプル
-----------

**予測（CLI）**

```bash
nf-runner predict \
  --model-id 123 \
  --data ./inference.csv \
  --h 14 \
  --output ./pred.csv
```

未来外生は `futr_*` 列名で投入。 18\_QUICKSTART

**再学習（CLI + 探索）**

```bash
nf-runner train \
  --data ./train.csv \
  --models AutoNHITS,AutoLSTM \
  --h 14 \
  --val-size 0.2 \
  --backend cuda \
  --max-workers 4 \
  --search-alg optuna \
  --num-trials 50
```

各フラグの意味と推奨値がガイドに整理されています。 18\_QUICKSTART

* * *

### ひとことまとめ

*   **予測**は「モデルID・データ・ホライズン・（必要なら分位点や信頼水準）」を指定。データ列は `unique_id, ds, y`＋外生（`futr_/hist_/stat_`）。
*   **再学習**は「ホライズン/検証分割/並列・デバイス・早期打ち切り・探索試行数」などを CLI / Python / 環境変数で制御。探索アルゴリズムのパラメータも指定可。

続けて、上記を既存の設定ファイル/CIにどう織り込むか（例：環境変数と Hydra の上書きルールの併用）もまとめられます。必要なら、そのまま“運用時の標準パラメータプリセット”を作ってお渡しします。 19\_FAQ

## Prompt:
モデル学習保存後に出力されるファイルについて詳細かつ具体的に教えてください。

## Response:
思考時間: 1m 16s

了解です。学習完了後に“どこへ・何が・どんな形式で”出力されるかを、保存先とファイル内容ごとに整理します。

保存先とディレクトリ
==========

*   既定の出力ルートは `./nf_auto_runs`（環境変数で変更可）。主な環境変数は `NF_OUTPUT_DIR` / `NF_MODEL_DIR` / `NF_ARTIFACT_DIR` / `NF_CHECKPOINT_DIR` / `NF_PLOT_DIR` / `NF_LOG_DIR` です。これに応じて `models/`、`artifacts/`、`checkpoints/`、`plots/`、`logs/` 等が自動生成されます。04\_CLASS\_DESIGN\_DETAILED
*   もう一つの推奨構成例では、`models/{staging,production}` と `outputs/{runs,predictions,plots,reports}`、`logs/{app,training,inference}` を切る運用設計になっています。10\_DEPLOYMENT\_GUIDE

生成される主なファイルと具体像
===============

**1) モデル本体（保存済みアーティファクト）**

*   置き場所：`<OUTPUT_DIR>/models/`（例：`./outputs/models/` または `./nf_auto_runs/models/`）。
*   形式・命名例：
    *   `AutoNHITS_*.pkl`（CLIチュートリアルの既定例）。`nf-runner predict --model ./outputs/models/AutoNHITS_*.pkl` で直接読み込み可能。
    *   設計上は PyTorch の `torch.save`/`torch.load` を用いた `*.pth` でも保存・読込できる想定（保存は `ModelSaver`、読込は `ModelLoader`）。
*   役割：学習済みモデルのシリアライズデータ。推論時は `torch.load()` あるいはピクル経由で復元されます（API/予測パイプライン設計より）。03\_ARCHITECTURE\_DESIGN\_DETAILED

**2) チェックポイント**

*   置き場所：`<OUTPUT_DIR>/checkpoints/`。04\_CLASS\_DESIGN\_DETAILED
*   中身：学習途中のモデル状態を段階保存するためのファイル（再開・早期終了時の復元用途）。クラス設計に `save_checkpoint` / `list_checkpoints` があり、エポックや run\_id を含む命名でバージョン管理する前提です（正確なファイル名規約は実装依存）。03\_ARCHITECTURE\_DESIGN\_DETAILED

**3) 予測結果（CSV）**

*   置き場所：`<OUTPUT_DIR>/predictions/`（例：`./outputs/predictions/`）。18\_QUICKSTART
*   形式：`predictions_*.csv`。カラムは `unique_id, ds, y_pred, y_pred_lower, y_pred_upper`（不確実性区間つき）。18\_QUICKSTART
*   生成タイミング：学習後すぐの評価用出力、または `nf-runner predict` 実行時。18\_QUICKSTART

**4) 評価メトリクス（JSON）**

*   置き場所：`<OUTPUT_DIR>/metrics/`（例：`metrics_*.json`）。18\_QUICKSTART
*   代表的なキー：`mae`、`rmse`、`mape`、`smape` など（評価用語仕様より）。01\_REQUIREMENTS\_SPECIFICATION\_D…
*   生成タイミング：学習完了後の評価フェーズ。メトリクスはDBや実験管理（MLflow/W&B）にもログされる設計です。03\_ARCHITECTURE\_DESIGN\_DETAILED

**5) ログ（構造化 JSON / ほか）**

*   置き場所：`<OUTPUT_DIR>/logs/`（例：`run_*.log`、構成により JSONL など）。18\_QUICKSTART
*   形式：構造化JSON。例：`{"timestamp": "...", "level": "INFO", "logger": "...", "message": "Model training started", "context": {"run_id": "abc123", "model": "AutoNHITS"}}`。15\_TROUBLESHOOTING\_GUIDE
*   生成タイミング：学習・評価・保存の各段で逐次。MLflowやDBへのメトリクス連携もログから行われます。03\_ARCHITECTURE\_DESIGN\_DETAILED

**6) 可視化・レポート類**

*   置き場所：`<OUTPUT_DIR>/plots/`（学習曲線や比較図）、`<OUTPUT_DIR>/reports/`（運用構成例）。
*   例：`model_comparison.png` や `forecast_plot.png`、`param_importance.png` などが保存されるチュートリアルが示されています。18\_QUICKSTART

**7) 実行履歴（runs ディレクトリ）**

*   置き場所：`<OUTPUT_DIR>/runs/`（運用構成の例）。個々の Run ごとの成果物・設定・簡易サマリをまとめる用途で予約。10\_DEPLOYMENT\_GUIDE

生成フロー（ざっくり）
===========

学習 → 評価 → 保存のシーケンスで、モデルファイル（`*.pkl`/`*.pth`）、メトリクス（JSON/DB/MLflow）、予測結果（CSV）がそれぞれ保存されます。保存は `ModelSaver(torch.save)` 等、読込は `ModelLoader(torch.load)` を用いる設計で、出力層には「Model Files」「Metrics Report」「Prediction Results」が並びます。

よくある運用メモ
========

*   保存先が不明なときは既定で `outputs/models/` を確認（設定で変更可）。15\_TROUBLESHOOTING\_GUIDE
*   モデルサイズやログ肥大化時は、古い `*.pth` や `*.log` を日付でローテーション／削除する運用手順が用意されています。11\_OPERATIONS\_RUNBOOK

* * *

必要であれば、この出力群から「納品物パッケージ（モデル＋メトリクス＋再現ログ＋可視化）」の標準束ね方も雛形化できます。次は、実際のあなたの環境変数と現状の `outputs/` ツリーを見て、命名規則をプロジェクトに合わせて固めましょう。

## Prompt:
ディレクトリ構造で分かりやすく教えてください。

## Response:
思考時間: 51s

了解。学習完了後に生成される “標準の” 出力先は、設計上は `NF_OUTPUT_DIR`（既定は `./nf_auto_runs`）配下で、用途別サブフォルダが自動作成されます。クイックスタート例では `./outputs` レイアウトも提示されているので、両方のパターンをツリー図で示します。

nf\_auto\_runs（設計の既定レイアウト）
==========================

```
nf_auto_runs/
├─ logs/                    # 構造化ログ（JSON Lines）
│   └─ {run_id}.jsonl       # 例: abc123.jsonl
├─ models/                  # 保存済みモデル
│   └─ {run_id}_{Model}.pth # 例: abc123_AutoNHITS.pth
├─ artifacts/               # 生成物（メトリクス/予測/メタデータ など）
├─ checkpoints/             # 学習途中のチェックポイント
├─ plots/                   # 可視化プロット
└─ runs/
    └─ {run_id}/            # 各実行のワークスペース（実行ごとに作成）
```

*   既定ディレクトリと環境変数（`NF_OUTPUT_DIR`, `NF_LOG_DIR`, `NF_MODEL_DIR`, `NF_ARTIFACT_DIR`, `NF_CHECKPOINT_DIR`, `NF_PLOT_DIR`）は `PathConfig` に定義されています。既定は `./nf_auto_runs` 直下に各サブフォルダです。 04\_CLASS\_DESIGN\_DETAILED
*   モデルファイルは `{run_id}_{Model}.pth` となることがテストで確認されています（例: `run123_AutoNHITS.pth`）。ログは `{run_id}.jsonl`。
*   実行ごとのディレクトリは `runs/{run_id}` が作られます（`get_run_dir`）。 04\_CLASS\_DESIGN\_DETAILED

outputs（クイックスタート例のレイアウト）
========================

```
outputs/
├─ models/
│   └─ AutoNHITS_*.pkl      # 例: AutoNHITS_2025-11-04_1030.pkl
├─ predictions/
│   └─ predictions_*.csv    # 例: predictions_20251104_103000.csv
├─ metrics/
│   └─ metrics_*.json       # 例: metrics_20251104_103000.json
└─ logs/
    └─ run_*.log            # 例: run_20251104_103000.log
```

*   このレイアウトはクイックスタートの確認例として提示されています。実装・設定により `nf_auto_runs` 方式と同居/切替が可能です。 18\_QUICKSTART

* * *

使い分けの目安
-------

*   **厳密な設計準拠**：`nf_auto_runs` 配下（環境変数で可変）。目的別にフォルダが固定され、`get_*_path` 系で命名規則が一貫します。
*   **チュートリアル/最小構成**：`outputs` 配下（例示）。モデルが `*.pkl`、予測が `predictions_*.csv`、メトリクスが `metrics_*.json` として確認しやすい構成です。 18\_QUICKSTART

必要なら、あなたの環境変数や運用フローに合わせてどちらかに統一するためのサンプル `NF_*` 設定や、`artifacts/` 配下の細分（`predictions/`, `metrics/`, `metadata/` など）設計も提案します。



---
Powered by [ChatGPT Exporter](https://www.chatgptexporter.com)