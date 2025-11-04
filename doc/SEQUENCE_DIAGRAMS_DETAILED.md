# 時系列予測システム - 詳細シーケンス図集

## 📋 目次

1. [Configuration読み込み](#1-configuration読み込み)
2. [データパイプライン](#2-データパイプライン)
3. [モデル検出フロー](#3-モデル検出フロー)
4. [実行計画生成](#4-実行計画生成)
5. [並列実行フロー](#5-並列実行フロー)
6. [ロギングフロー](#6-ロギングフロー)
7. [完全な学習パイプライン](#7-完全な学習パイプライン)
8. [予測パイプライン](#8-予測パイプライン)
9. [再学習トリガーフロー](#9-再学習トリガーフロー)
10. [ハイパーパラメータ探索](#10-ハイパーパラメータ探索)
11. [アーティファクト管理](#11-アーティファクト管理)
12. [エラーハンドリング](#12-エラーハンドリング)

---

## 1. Configuration読み込み

### 1.1 環境変数からの設定読み込み

```mermaid
sequenceDiagram
    participant App as Application
    participant CL as ConfigLoader
    participant PC as PathConfig
    participant EC as ExecutionConfig
    participant MC as ModelSelectionConfig
    participant Env as Environment Variables
    participant FS as File System
    
    App->>CL: load_all()
    
    Note over CL: Configuration読み込み開始
    
    %% PathConfig読み込み
    CL->>PC: from_env()
    PC->>Env: getenv("NF_DATA_CSV")
    Env-->>PC: "./data/input.csv"
    PC->>Env: getenv("NF_OUTPUT_DIR")
    Env-->>PC: "./outputs"
    PC->>Env: getenv("NF_MODELS_DIR")
    Env-->>PC: "./models"
    PC->>Env: getenv("NF_LOGS_DIR")
    Env-->>PC: "./logs"
    
    PC->>PC: validate()
    alt データパスが存在しない
        PC-->>CL: ValidationError
        CL-->>App: Error: Data file not found
    else パス検証成功
        PC->>FS: mkdir(outputs_dir)
        PC->>FS: mkdir(models_dir)
        PC->>FS: mkdir(logs_dir)
        FS-->>PC: Directories created
        PC-->>CL: PathConfig
    end
    
    %% ExecutionConfig読み込み
    CL->>EC: from_env()
    EC->>Env: getenv("NF_RANDOM_STATE")
    Env-->>EC: "42"
    EC->>Env: getenv("NF_MAX_WORKERS")
    Env-->>EC: "4"
    EC->>Env: getenv("NF_ALLOW_RAY_PARALLEL")
    Env-->>EC: "false"
    EC->>Env: getenv("NF_TRIAL_NUM_SAMPLES")
    Env-->>EC: "10"
    
    EC->>EC: validate()
    alt max_workers が CPU数を超える
        EC->>EC: max_workers = min(max_workers, cpu_count)
    end
    EC-->>CL: ExecutionConfig
    
    %% ModelSelectionConfig読み込み
    CL->>MC: from_env()
    MC->>Env: getenv("NF_MODELS")
    Env-->>MC: "AutoNBEATS,AutoLSTM"
    MC->>Env: getenv("NF_BACKENDS")
    Env-->>MC: "pytorch_lightning"
    MC->>Env: getenv("NF_SEARCH_ALGS")
    Env-->>MC: "optuna"
    MC->>Env: getenv("NF_LOSSES")
    Env-->>MC: "auto"
    
    MC->>MC: parse_list_values()
    MC->>MC: validate()
    alt モデルリストが空
        MC-->>CL: ValidationError
        CL-->>App: Error: No models specified
    else 検証成功
        MC-->>CL: ModelSelectionConfig
    end
    
    %% 全設定を統合
    CL->>CL: combine_configs()
    CL-->>App: Dict[str, Config]
    
    Note over App: 設定読み込み完了
```

---

## 2. データパイプライン

### 2.1 データ読み込みから前処理まで

```mermaid
sequenceDiagram
    participant App as Application
    participant DL as DataLoader
    participant DP as DataPreprocessor
    participant FI as FrequencyInferrer
    participant EE as ExogeneousEncoder
    participant DV as DataValidator
    participant DF as DataFrame
    
    App->>DL: load(data_path)
    
    %% データ読み込み
    DL->>DL: detect_file_format()
    alt CSV形式
        DL->>DF: pd.read_csv(data_path)
    else Parquet形式
        DL->>DF: pd.read_parquet(data_path)
    else Excel形式
        DL->>DF: pd.read_excel(data_path)
    end
    DF-->>DL: raw_df
    
    %% 初期検証
    DL->>DV: validate_schema(raw_df)
    DV->>DV: check_required_columns()
    alt 必須カラム不足
        DV-->>DL: ValidationError
        DL-->>App: Error: Missing columns
    else スキーマ検証成功
        DV-->>DL: OK
    end
    
    %% カラム標準化
    DL->>DP: standardize_columns(raw_df)
    DP->>DP: detect_id_column()
    DP->>DP: detect_date_column()
    DP->>DP: detect_target_column()
    DP->>DP: rename_columns()
    Note over DP: unique_id, ds, y に標準化
    DP-->>DL: standardized_df
    
    %% 日付解析
    DL->>DP: parse_dates(standardized_df)
    DP->>DP: to_datetime(ds_column)
    alt 日付パース失敗
        DP-->>DL: ValueError
        DL-->>App: Error: Invalid date format
    else 日付パース成功
        DP-->>DL: df_with_dates
    end
    
    %% 外生変数の検出と分類
    DL->>EE: detect_exogenous(df_with_dates)
    EE->>EE: identify_futr_columns()
    EE->>EE: identify_hist_columns()
    EE->>EE: identify_stat_columns()
    EE-->>DL: exog_metadata
    
    %% 周期性推定
    DL->>FI: infer_frequency(df_with_dates)
    FI->>FI: group_by_unique_id()
    loop 各時系列
        FI->>FI: pd.infer_freq(dates)
        alt 頻度推定成功
            FI->>FI: record_frequency()
        else 推定失敗
            FI->>FI: calculate_median_diff()
            FI->>FI: map_to_pandas_freq()
        end
    end
    FI->>FI: determine_dominant_freq()
    FI-->>DL: frequency_info
    
    %% 欠損値処理
    DL->>DP: handle_missing(df_with_dates)
    DP->>DP: detect_missing_patterns()
    loop 各カラム
        alt 数値カラム
            DP->>DP: forward_fill()
            DP->>DP: interpolate()
        else カテゴリカラム
            DP->>DP: mode_fill()
        end
    end
    DP-->>DL: df_no_missing
    
    %% 外れ値検出
    DL->>DV: detect_outliers(df_no_missing)
    DV->>DV: calculate_zscore()
    DV->>DV: calculate_iqr()
    DV->>DV: flag_outliers()
    DV-->>DL: outlier_info
    
    %% 外生変数エンコーディング
    DL->>EE: encode_exogenous(df_no_missing)
    loop 各カテゴリカル変数
        EE->>EE: label_encode()
        EE->>EE: store_mapping()
    end
    EE-->>DL: df_encoded
    
    %% 最終検証
    DL->>DV: validate_processed(df_encoded)
    DV->>DV: check_data_integrity()
    DV->>DV: verify_time_series_continuity()
    DV->>DV: validate_value_ranges()
    alt 検証失敗
        DV-->>DL: ValidationError
        DL-->>App: Error: Data validation failed
    else 検証成功
        DV-->>DL: OK
        DL-->>App: ProcessedData
    end
    
    Note over App: データパイプライン完了
```

---

## 3. モデル検出フロー

### 3.1 Autoモデルとバックエンドの検出

```mermaid
sequenceDiagram
    participant App as Application
    participant MR as ModelRegistry
    participant MC as ModelCapabilityAnalyzer
    participant BD as BackendDetector
    participant MV as ModelValidator
    participant Sys as System
    
    App->>MR: discover_models()
    
    %% インストール済みモジュール検出
    MR->>Sys: scan_installed_packages()
    Sys-->>MR: package_list
    
    %% モデル検出
    MR->>MR: detect_auto_models()
    loop NeuralForecastモジュール内
        MR->>MR: inspect_module(neuralforecast)
        alt Autoで始まるクラス発見
            MR->>MR: import_class()
            MR->>MC: analyze_capabilities(model_class)
            
            %% モデル能力分析
            MC->>MC: check_exog_support()
            MC->>MC: check_static_features()
            MC->>MC: check_val_size_support()
            MC->>MC: extract_required_params()
            MC-->>MR: capability_info
            
            MR->>MR: register_model(model_class, capability_info)
        end
    end
    
    %% バックエンド検出
    MR->>BD: detect_backends()
    
    BD->>Sys: check_pytorch_lightning()
    alt PyTorch Lightning利用可能
        BD->>Sys: check_cuda_availability()
        alt CUDA利用可能
            BD->>Sys: get_cuda_version()
            Sys-->>BD: cuda_version
            BD->>BD: register_backend("pytorch_lightning", gpu=True)
        else CPUのみ
            BD->>BD: register_backend("pytorch_lightning", gpu=False)
        end
    end
    
    BD->>Sys: check_pytorch()
    alt PyTorch利用可能
        BD->>BD: register_backend("pytorch")
    end
    
    BD->>Sys: check_ray()
    alt Ray利用可能
        BD->>Sys: check_ray_cluster()
        alt Rayクラスタ実行中
            BD->>BD: register_backend("ray", distributed=True)
        else ローカル実行
            BD->>BD: register_backend("ray", distributed=False)
        end
    end
    
    BD-->>MR: backend_info
    
    %% 損失関数検出
    MR->>MR: detect_loss_functions()
    loop NeuralForecast損失モジュール
        MR->>MR: import_loss_class()
        MR->>MR: register_loss(loss_class)
    end
    
    %% スケーラー検出
    MR->>MR: detect_scalers()
    loop 標準スケーラー
        MR->>MR: register_scaler(scaler_class)
    end
    
    %% 探索アルゴリズム検出
    MR->>MR: detect_search_algorithms()
    
    MR->>Sys: check_optuna()
    alt Optuna利用可能
        MR->>MR: register_search_algo("optuna")
    end
    
    MR->>Sys: check_ray_tune()
    alt Ray Tune利用可能
        MR->>MR: register_search_algo("ray_tune")
    end
    
    %% 互換性検証
    MR->>MV: validate_combinations(registry)
    
    loop 各モデル×バックエンドの組み合わせ
        MV->>MV: check_backend_compatibility()
        MV->>MV: check_loss_compatibility()
        MV->>MV: check_search_algo_compatibility()
        alt 非互換
            MV->>MV: mark_incompatible()
        end
    end
    
    MV-->>MR: validation_results
    
    %% レジストリ完成
    MR->>MR: finalize_registry()
    MR-->>App: ModelRegistry
    
    Note over App: モデル検出完了
```

---

## 4. 実行計画生成

### 4.1 組み合わせ生成と重複排除

```mermaid
sequenceDiagram
    participant App as Application
    participant CG as CombinationGenerator
    participant EP as ExecutionPlan
    participant DD as DuplicateDetector
    participant RE as ResourceEstimator
    participant Config as Configuration
    participant Data as ProcessedData
    
    App->>CG: generate_combinations(config, data, registry)
    
    %% 展開軸の決定
    CG->>Config: get_expand_axes()
    Config-->>CG: ["model", "backend", "search_alg", "loss"]
    
    CG->>Config: get_combo_depth()
    Config-->>CG: depth=3
    
    %% 安全なhの計算
    CG->>Data: get_min_series_length()
    Data-->>CG: min_length=100
    
    CG->>Config: get_h_config()
    Config-->>CG: h_config={h: 24, h_ratio: 0.2}
    
    CG->>CG: calculate_safe_h()
    Note over CG: h = min(24, floor(100 * 0.2))
    CG->>CG: safe_h = 20
    
    %% 展開軸ごとの値生成
    CG->>CG: expand_models()
    loop 各モデル
        alt モデルが有効
            CG->>CG: add_to_axis(model)
        end
    end
    
    CG->>CG: expand_backends()
    CG->>CG: expand_search_algos()
    CG->>CG: expand_losses()
    CG->>CG: expand_scalers()
    CG->>CG: expand_early_stops()
    
    %% 直積計算
    CG->>CG: cartesian_product(axes, depth)
    Note over CG: 組み合わせの総数を計算
    
    %% フィンガープリント生成
    loop 各組み合わせ
        CG->>DD: generate_fingerprint(combination)
        
        DD->>DD: serialize_params()
        DD->>DD: calculate_sha256()
        DD-->>CG: fingerprint
        
        %% 重複チェック
        CG->>DD: check_duplicate(fingerprint)
        DD->>DD: lookup_in_database()
        alt 重複あり
            DD-->>CG: duplicate=True
            CG->>CG: skip_combination()
        else 新規
            DD-->>CG: duplicate=False
            
            %% リソース見積もり
            CG->>RE: estimate_resources(combination, data)
            
            RE->>RE: estimate_memory()
            Note over RE: 時系列数 × モデルサイズ × パラメータ数
            
            RE->>RE: estimate_training_time()
            Note over RE: データ量 × モデル複雑度 × エポック数
            
            RE->>RE: estimate_gpu_memory()
            alt GPUモデル
                RE->>RE: calculate_vram_usage()
            end
            
            RE-->>CG: resource_estimate
            
            %% 実行計画エントリ作成
            CG->>EP: create_execution_entry()
            EP->>EP: assign_run_id()
            EP->>EP: set_parameters(combination)
            EP->>EP: set_safe_h(safe_h)
            EP->>EP: set_resource_estimate(resource_estimate)
            EP->>EP: set_fingerprint(fingerprint)
            EP-->>CG: execution_entry
            
            CG->>CG: add_to_plan(execution_entry)
        end
    end
    
    %% 計画の最適化
    CG->>EP: optimize_plan()
    
    EP->>EP: sort_by_priority()
    Note over EP: GPU優先、軽量モデル優先など
    
    EP->>EP: group_by_resource_type()
    Note over EP: GPU/CPUグループに分割
    
    EP->>RE: validate_resource_constraints()
    alt リソース超過
        RE->>EP: split_into_batches()
    end
    
    EP-->>CG: optimized_plan
    
    %% 実行計画の永続化
    CG->>EP: save_to_database()
    EP->>EP: serialize_plan()
    EP->>DB: insert(execution_plan)
    DB-->>EP: plan_id
    
    EP-->>CG: persisted_plan
    CG-->>App: ExecutionPlan
    
    Note over App: 実行計画生成完了<br/>組み合わせ数: N<br/>推定時間: X時間
```

---

## 5. 並列実行フロー

### 5.1 ThreadPoolExecutorによる並列実行

```mermaid
sequenceDiagram
    participant App as Application
    participant PE as ParallelExecutor
    participant RM as ResourceMonitor
    participant SE as SerialExecutor
    participant Worker as Worker Thread
    participant Model as NeuralForecast Model
    participant AS as ArtifactSaver
    participant Logger as StructuredLogger
    
    App->>PE: execute_plan(execution_plan, max_workers=4)
    
    %% リソースモニタ起動
    PE->>RM: start_monitoring()
    RM->>RM: spawn_monitor_thread()
    loop 監視ループ
        RM->>System: get_cpu_usage()
        RM->>System: get_memory_usage()
        RM->>System: get_gpu_usage()
        RM->>Logger: log_metrics()
    end
    
    %% 実行計画の分割
    PE->>PE: split_by_backend(execution_plan)
    PE->>PE: gpu_tasks = filter(backend="pytorch_lightning")
    PE->>PE: cpu_tasks = filter(backend!="pytorch_lightning")
    
    %% ThreadPoolExecutor初期化
    PE->>PE: create_executor(max_workers=4)
    
    %% 進捗トラッカー初期化
    PE->>Logger: init_progress(total_tasks)
    Logger->>Logger: create_tqdm_bar()
    
    %% Rayタスクの安全性チェック
    alt Rayバックエンド含む AND allow_ray_parallel=False
        PE->>Logger: warn("Ray tasks will run serially")
        PE->>SE: execute_ray_tasks_serially(ray_tasks)
        loop 各Rayタスク
            SE->>SE: execute_single(task)
        end
    end
    
    %% 並列実行開始
    PE->>PE: submit_tasks(cpu_tasks)
    
    par Worker 1
        PE->>Worker: execute_task(task_1)
        Worker->>Worker: setup_environment()
        Worker->>Worker: set_random_seed(task_1.seed)
        
        %% モデル初期化
        Worker->>Model: initialize(task_1.params)
        Model->>Model: load_hyperparameters()
        Model->>Model: setup_backend()
        Model-->>Worker: model_instance
        
        %% 学習実行
        Worker->>Model: fit(train_data)
        Model->>Model: run_training_loop()
        loop エポックごと
            Model->>Model: forward_pass()
            Model->>Model: calculate_loss()
            Model->>Model: backward_pass()
            Model->>Model: update_weights()
            Model->>Logger: log_epoch_metrics()
        end
        Model-->>Worker: trained_model
        
        %% 予測
        Worker->>Model: predict(test_data)
        Model-->>Worker: predictions
        
        %% メトリクス計算
        Worker->>Worker: calculate_metrics(predictions)
        
        %% アーティファクト保存
        Worker->>AS: save_model(trained_model)
        Worker->>AS: save_predictions(predictions)
        Worker->>AS: save_metrics(metrics)
        
        %% 進捗更新
        Worker->>Logger: update_progress()
        Worker->>Logger: log_completion(task_1)
        
    and Worker 2
        PE->>Worker: execute_task(task_2)
        Note over Worker: 同様の処理
        
    and Worker 3
        PE->>Worker: execute_task(task_3)
        Note over Worker: 同様の処理
        
    and Worker 4
        PE->>Worker: execute_task(task_4)
        Note over Worker: 同様の処理
    end
    
    %% エラーハンドリング
    alt タスク実行中にエラー
        Worker->>Worker: catch_exception()
        Worker->>Logger: log_error(exception)
        Worker->>AS: save_error_metadata()
        Worker->>Worker: extract_traceback()
        Worker->>PE: return_error_result()
    end
    
    %% すべてのタスク完了待ち
    PE->>PE: wait_for_completion()
    
    %% 結果集約
    PE->>PE: collect_results()
    loop 各Worker結果
        PE->>PE: aggregate_metrics()
        PE->>PE: check_for_errors()
    end
    
    %% リソースモニタ停止
    PE->>RM: stop_monitoring()
    RM->>RM: save_final_metrics()
    RM->>Logger: log_resource_summary()
    
    %% ExecutorPool終了
    PE->>PE: shutdown_executor(wait=True)
    
    %% 最終レポート
    PE->>Logger: log_execution_summary()
    Note over Logger: 成功: X件<br/>失敗: Y件<br/>総時間: Z秒
    
    PE-->>App: ExecutionResults
    
    Note over App: 並列実行完了
```

---

## 6. ロギングフロー

### 6.1 構造化ログとメトリクストラッキング

```mermaid
sequenceDiagram
    participant App as Application
    participant SL as StructuredLogger
    participant PT as ProgressTracker
    participant MB as MLflowBridge
    participant WB as WandBBridge
    participant FS as File System
    participant Console as Console Output
    
    App->>SL: initialize(config)
    
    %% ロガー設定
    SL->>SL: setup_structlog()
    SL->>SL: configure_processors()
    Note over SL: JSON formatter<br/>Timestamp<br/>Log level<br/>Context
    
    SL->>FS: create_log_file(log_path)
    FS-->>SL: file_handle
    
    %% MLflow初期化（オプション）
    alt MLflow有効
        SL->>MB: initialize(tracking_uri)
        MB->>MB: create_experiment()
        MB-->>SL: experiment_id
    end
    
    %% W&B初期化（オプション）
    alt W&B有効
        SL->>WB: initialize(project_name)
        WB->>WB: create_run()
        WB-->>SL: run_id
    end
    
    %% 実行開始ログ
    App->>SL: log_execution_start(config)
    SL->>SL: create_log_entry()
    SL->>SL: add_context(run_id, timestamp)
    SL->>FS: write_log(entry)
    SL->>Console: print_info()
    
    alt MLflow有効
        SL->>MB: log_params(config)
    end
    
    alt W&B有効
        SL->>WB: log_config(config)
    end
    
    %% 進捗トラッキング開始
    App->>PT: start_tracking(total_tasks)
    PT->>PT: initialize_tqdm(total_tasks)
    PT->>PT: create_progress_bar()
    
    %% タスク実行中のログ
    loop 各タスク
        App->>SL: log_task_start(task_id)
        SL->>FS: write_log(task_start)
        SL->>Console: print_task_info()
        
        %% エポックごとのメトリクス
        loop 各エポック
            App->>SL: log_metrics(epoch, metrics)
            SL->>SL: format_metrics()
            
            SL->>FS: write_log(metrics)
            
            alt MLflow有効
                SL->>MB: log_metrics(metrics, step=epoch)
            end
            
            alt W&B有効
                SL->>WB: log(metrics, step=epoch)
            end
            
            %% 進捗更新
            App->>PT: update(1)
            PT->>PT: increment_progress()
            PT->>Console: update_bar()
        end
        
        %% タスク完了ログ
        App->>SL: log_task_complete(task_id, results)
        SL->>SL: calculate_task_duration()
        SL->>SL: extract_final_metrics()
        
        SL->>FS: write_log(task_complete)
        SL->>Console: print_task_summary()
        
        alt MLflow有効
            SL->>MB: log_metrics(final_metrics)
            SL->>MB: log_artifact(model_path)
        end
        
        alt W&B有効
            SL->>WB: log_summary(final_metrics)
            SL->>WB: log_model(model_path)
        end
        
        %% エラーハンドリング
        alt タスク失敗
            App->>SL: log_error(task_id, exception)
            SL->>SL: extract_traceback()
            SL->>SL: extract_error_metadata()
            
            SL->>FS: write_error_log()
            SL->>Console: print_error()
            
            alt MLflow有効
                SL->>MB: log_error_artifact()
            end
            
            alt W&B有効
                SL->>WB: log_error()
            end
        end
    end
    
    %% 進捗完了
    PT->>PT: close_progress_bar()
    PT->>Console: clear_bar()
    
    %% 実行完了ログ
    App->>SL: log_execution_complete(summary)
    SL->>SL: calculate_total_duration()
    SL->>SL: aggregate_metrics()
    SL->>SL: generate_summary()
    
    SL->>FS: write_summary_log()
    SL->>Console: print_summary()
    
    Note over Console: ===== Execution Summary =====<br/>Total Tasks: X<br/>Successful: Y<br/>Failed: Z<br/>Total Time: T seconds
    
    alt MLflow有効
        SL->>MB: log_final_summary()
        SL->>MB: end_run()
    end
    
    alt W&B有効
        SL->>WB: log_final_summary()
        SL->>WB: finish_run()
    end
    
    %% ログファイルクローズ
    SL->>FS: close_log_file()
    
    SL-->>App: LoggingComplete
    
    Note over App: ロギング完了
```

---

## 7. 完全な学習パイプライン

### 7.1 エンドツーエンドの学習フロー

```mermaid
sequenceDiagram
    participant User as User/CLI
    participant Orch as MainOrchestrator
    participant CL as ConfigLoader
    participant DL as DataLoader
    participant MR as ModelRegistry
    participant CG as CombinationGenerator
    participant PE as ParallelExecutor
    participant Model as NeuralForecast
    participant AS as ArtifactSaver
    participant DB as Database
    participant Logger as StructuredLogger
    
    %% 1. 初期化フェーズ
    User->>Orch: run_training(cli_args)
    
    Note over Orch: === Phase 1: Initialization ===
    
    Orch->>Logger: initialize_logging()
    Logger-->>Orch: logger_ready
    
    Orch->>CL: load_all_configs(cli_args)
    CL->>CL: merge_env_and_cli()
    CL->>CL: validate_configs()
    CL-->>Orch: configs
    
    Orch->>Logger: log_config(configs)
    
    %% 2. データ準備フェーズ
    Note over Orch: === Phase 2: Data Preparation ===
    
    Orch->>DL: load_and_preprocess(data_path)
    
    DL->>DL: load_csv()
    DL->>DL: standardize_columns()
    DL->>DL: parse_dates()
    DL->>DL: infer_frequency()
    DL->>DL: handle_missing()
    DL->>DL: encode_exogenous()
    DL->>DL: validate_data()
    
    DL-->>Orch: processed_data
    
    Orch->>Logger: log_data_info(processed_data)
    Orch->>DB: save_dataset_metadata(processed_data)
    
    %% 3. モデル検出フェーズ
    Note over Orch: === Phase 3: Model Discovery ===
    
    Orch->>MR: discover_all()
    
    MR->>MR: detect_auto_models()
    MR->>MR: detect_backends()
    MR->>MR: detect_losses()
    MR->>MR: detect_scalers()
    MR->>MR: detect_search_algos()
    MR->>MR: validate_combinations()
    
    MR-->>Orch: registry
    
    Orch->>Logger: log_registry_info(registry)
    
    %% 4. 実行計画生成フェーズ
    Note over Orch: === Phase 4: Execution Planning ===
    
    Orch->>CG: generate_plan(configs, processed_data, registry)
    
    CG->>CG: calculate_safe_h()
    CG->>CG: expand_axes()
    CG->>CG: cartesian_product()
    CG->>CG: generate_fingerprints()
    CG->>CG: filter_duplicates()
    CG->>CG: estimate_resources()
    CG->>CG: optimize_plan()
    
    CG-->>Orch: execution_plan
    
    Orch->>Logger: log_plan_summary(execution_plan)
    Orch->>DB: save_execution_plan(execution_plan)
    
    %% 5. 実行フェーズ
    Note over Orch: === Phase 5: Execution ===
    
    Orch->>PE: execute_plan(execution_plan)
    
    PE->>PE: start_resource_monitor()
    PE->>PE: create_thread_pool()
    
    loop 各組み合わせ
        PE->>PE: assign_to_worker()
        
        par Worker Thread
            PE->>PE: setup_environment()
            PE->>PE: set_random_seed()
            
            %% モデル初期化
            PE->>Model: initialize(params)
            Model->>Model: setup_backend()
            Model->>Model: configure_hyperparams()
            Model-->>PE: model_instance
            
            %% 学習
            PE->>Model: fit(train_data, val_data)
            
            loop エポック
                Model->>Model: train_epoch()
                Model->>Model: validate()
                Model->>Logger: log_metrics()
                
                alt Early Stopping条件
                    Model->>Model: stop_training()
                end
            end
            
            Model-->>PE: trained_model
            
            %% 評価
            PE->>Model: predict(test_data)
            Model-->>PE: predictions
            
            PE->>PE: calculate_metrics(predictions)
            
            %% アーティファクト保存
            PE->>AS: save_model(trained_model)
            AS->>AS: generate_model_path()
            AS->>FS: write_model()
            AS-->>PE: model_path
            
            PE->>AS: save_predictions(predictions)
            AS->>FS: write_predictions()
            AS-->>PE: predictions_path
            
            PE->>AS: save_metadata(run_info)
            AS->>FS: write_metadata()
            AS-->>PE: metadata_path
            
            %% データベース記録
            PE->>DB: insert_run(run_info)
            PE->>DB: insert_metrics(metrics)
            PE->>DB: insert_artifacts(paths)
            
            PE->>Logger: log_run_complete()
            PE->>Logger: update_progress()
            
            alt エラー発生
                PE->>Logger: log_error(exception)
                PE->>DB: insert_error(error_info)
                PE->>AS: save_error_metadata()
            end
        end
    end
    
    PE->>PE: wait_all_workers()
    PE->>PE: stop_resource_monitor()
    PE->>PE: shutdown_thread_pool()
    
    PE-->>Orch: execution_results
    
    %% 6. 集約フェーズ
    Note over Orch: === Phase 6: Aggregation ===
    
    Orch->>Orch: aggregate_results(execution_results)
    Orch->>Orch: calculate_summary_stats()
    Orch->>Orch: identify_best_models()
    
    Orch->>Logger: log_final_summary()
    Orch->>DB: save_experiment_summary()
    
    %% 7. クリーンアップフェーズ
    Note over Orch: === Phase 7: Cleanup ===
    
    Orch->>Logger: flush_logs()
    Orch->>Logger: close_handlers()
    
    Orch-->>User: TrainingComplete
    
    Note over User: 学習完了<br/>成功: X件<br/>失敗: Y件<br/>総時間: Z
```

---

## 8. 予測パイプライン

### 8.1 モデル読み込みから予測まで

```mermaid
sequenceDiagram
    participant User as User/API
    participant FC as Forecaster
    participant MLoader as ModelLoader
    participant DL as DataLoader
    participant DP as DataPreprocessor
    participant Model as LoadedModel
    participant PP as PostProcessor
    participant AS as ArtifactSaver
    participant DB as Database
    
    %% 1. 予測リクエスト
    User->>FC: predict(model_id, input_data)
    
    %% 2. モデル読み込み
    FC->>MLoader: load_model(model_id)
    
    MLoader->>DB: get_model_metadata(model_id)
    DB-->>MLoader: metadata
    
    MLoader->>MLoader: validate_metadata()
    
    MLoader->>FS: read_model_file(model_path)
    FS-->>MLoader: model_bytes
    
    MLoader->>MLoader: deserialize_model()
    MLoader->>Model: restore_state()
    
    Model->>Model: load_weights()
    Model->>Model: load_hyperparameters()
    Model->>Model: setup_backend()
    
    Model-->>MLoader: loaded_model
    MLoader-->>FC: model_instance
    
    %% 3. データ準備
    FC->>DL: load_input(input_data)
    DL->>DL: validate_format()
    DL->>DL: parse_dates()
    DL-->>FC: raw_data
    
    FC->>DP: preprocess(raw_data, metadata)
    
    DP->>DP: standardize_columns()
    DP->>DP: infer_frequency()
    DP->>DP: align_with_training()
    
    alt 外生変数あり
        DP->>DP: load_encoders(metadata)
        DP->>DP: encode_exogenous()
    end
    
    DP->>DP: validate_input()
    DP-->>FC: preprocessed_data
    
    %% 4. 予測実行
    FC->>FC: setup_prediction_context()
    FC->>FC: set_random_seed()
    
    FC->>Model: predict(preprocessed_data, h)
    
    Model->>Model: prepare_input()
    Model->>Model: forward_pass()
    Model->>Model: generate_forecast()
    
    alt 確率予測
        Model->>Model: compute_quantiles()
    end
    
    Model-->>FC: raw_predictions
    
    %% 5. 後処理
    FC->>PP: postprocess(raw_predictions, metadata)
    
    PP->>PP: denormalize()
    
    alt スケーラー使用
        PP->>PP: inverse_transform()
    end
    
    PP->>PP: format_output()
    PP->>PP: add_timestamps()
    PP->>PP: add_confidence_intervals()
    
    PP-->>FC: formatted_predictions
    
    %% 6. 保存
    FC->>AS: save_predictions(formatted_predictions)
    AS->>AS: generate_prediction_path()
    AS->>FS: write_csv(formatted_predictions)
    AS-->>FC: predictions_path
    
    FC->>DB: insert_prediction_record()
    DB-->>FC: prediction_id
    
    %% 7. 応答
    FC-->>User: PredictionResult
    
    Note over User: 予測完了<br/>Horizon: h<br/>Series: N
```

---

## 9. 再学習トリガーフロー

### 9.1 ドリフト検出から再学習まで

```mermaid
sequenceDiagram
    participant Scheduler as Scheduler/Cron
    participant RT as RetrainTrigger
    participant DD as DriftDetector
    participant MLoader as ModelLoader
    participant Orch as MainOrchestrator
    participant DB as Database
    participant Logger as StructuredLogger
    participant Alert as AlertSystem
    
    %% 1. スケジュール起動
    Scheduler->>RT: trigger_check()
    
    RT->>Logger: log_check_start()
    
    %% 2. トリガー条件チェック
    RT->>DB: get_last_training_time()
    DB-->>RT: last_training_time
    
    RT->>RT: check_time_threshold()
    Note over RT: 最終学習から7日以上?
    
    alt 時間閾値未達
        RT-->>Scheduler: No action needed
    end
    
    %% 3. ドリフト検出
    RT->>DD: detect_drift(model_id)
    
    DD->>MLoader: load_model(model_id)
    MLoader-->>DD: model_instance
    
    DD->>DB: get_training_data()
    DB-->>DD: training_data
    
    DD->>DB: get_recent_data()
    DB-->>DD: recent_data
    
    %% 統計的ドリフト検出
    DD->>DD: compute_statistics(training_data)
    DD->>DD: compute_statistics(recent_data)
    
    DD->>DD: kolmogorov_smirnov_test()
    DD->>DD: chi_square_test()
    DD->>DD: population_stability_index()
    
    %% モデル性能ドリフト
    DD->>DD: compute_model_performance(training_data)
    DD->>DD: compute_model_performance(recent_data)
    DD->>DD: compare_metrics()
    
    %% データ分布ドリフト
    DD->>DD: jensen_shannon_divergence()
    DD->>DD: wasserstein_distance()
    
    DD->>DD: aggregate_drift_scores()
    
    alt ドリフト検出
        DD->>Logger: log_drift_detected(scores)
        DD-->>RT: drift_detected=True, scores
    else ドリフトなし
        DD->>Logger: log_no_drift()
        DD-->>RT: drift_detected=False
        RT-->>Scheduler: No retraining needed
    end
    
    %% 4. 再学習判定
    RT->>RT: evaluate_retrain_criteria()
    
    alt 高ドリフト（スコア > 0.8）
        RT->>RT: priority=HIGH
    else 中ドリフト（スコア > 0.5）
        RT->>RT: priority=MEDIUM
    else 低ドリフト（スコア > 0.3）
        RT->>RT: priority=LOW
    end
    
    %% 5. アラート送信
    RT->>Alert: send_alert(drift_info)
    Alert->>Alert: format_message()
    Alert->>Email: send_email(stakeholders)
    Alert->>Slack: post_message(channel)
    
    %% 6. 再学習計画作成
    RT->>DB: get_model_config(model_id)
    DB-->>RT: config
    
    RT->>RT: prepare_retrain_config()
    RT->>RT: update_hyperparams()
    RT->>RT: set_data_window()
    
    %% 7. 再学習実行
    RT->>Orch: trigger_retraining(retrain_config)
    
    Orch->>Logger: log_retrain_start()
    
    %% データ準備
    Orch->>DB: get_updated_data()
    DB-->>Orch: updated_data
    
    %% 学習実行
    Orch->>Orch: run_training(retrain_config, updated_data)
    Note over Orch: 通常の学習フロー実行
    
    %% 新旧モデル比較
    Orch->>Orch: compare_models(old_model, new_model)
    
    alt 新モデルが優れている
        Orch->>DB: promote_model(new_model_id)
        Orch->>DB: archive_model(old_model_id)
        Orch->>Logger: log_model_promotion()
    else 旧モデルの方が良い
        Orch->>DB: keep_current_model()
        Orch->>Logger: log_keep_current()
    end
    
    Orch-->>RT: retrain_result
    
    %% 8. 記録と通知
    RT->>DB: insert_retrain_record()
    RT->>Logger: log_retrain_complete()
    RT->>Alert: send_completion_notification()
    
    RT-->>Scheduler: Retrain complete
    
    Note over Scheduler: 次回チェック: 7日後
```

---

## 10. ハイパーパラメータ探索

### 10.1 Optunaを使った探索フロー

```mermaid
sequenceDiagram
    participant App as Application
    participant SM as SearchManager
    participant Study as Optuna Study
    participant Trial as Trial
    participant Model as NeuralForecast
    participant Eval as Evaluator
    participant DB as Database
    
    %% 1. 探索初期化
    App->>SM: run_hyperparameter_search(config)
    
    SM->>SM: parse_search_space(config)
    SM->>SM: define_objective_function()
    
    SM->>Study: create_study()
    Study->>Study: set_direction("minimize")
    Study->>Study: set_sampler(TPESampler())
    Study->>Study: set_pruner(MedianPruner())
    
    %% 2. 探索ループ
    SM->>Study: optimize(objective, n_trials=100)
    
    loop Trial 1 to 100
        Study->>Trial: create_trial()
        
        %% パラメータサジェスト
        Trial->>Trial: suggest_int("hidden_size", 32, 256)
        Trial->>Trial: suggest_float("learning_rate", 1e-5, 1e-2, log=True)
        Trial->>Trial: suggest_categorical("optimizer", ["Adam", "SGD"])
        Trial->>Trial: suggest_int("n_layers", 1, 4)
        Trial->>Trial: suggest_float("dropout", 0.0, 0.5)
        
        Trial-->>SM: trial_params
        
        %% モデル初期化
        SM->>Model: initialize(trial_params)
        Model->>Model: setup_architecture()
        Model->>Model: configure_optimizer()
        Model-->>SM: model_instance
        
        %% 学習
        SM->>Model: fit(train_data, val_data)
        
        loop Epoch
            Model->>Model: train_epoch()
            Model->>Model: validate()
            
            Model->>Eval: calculate_metrics(val_predictions)
            Eval-->>Model: val_loss
            
            %% 中間値報告
            Model->>Trial: report(val_loss, step=epoch)
            
            %% Pruning判定
            Trial->>Trial: should_prune()
            alt Pruning条件満たす
                Trial->>SM: TrialPruned
                Note over SM: この試行を打ち切り
            end
        end
        
        Model-->>SM: final_val_loss
        
        %% 試行記録
        SM->>DB: save_trial(trial_params, final_val_loss)
        SM->>Trial: set_user_attrs(custom_metrics)
        
        Trial-->>Study: trial_result
        
        %% 最良モデル更新
        alt 新しいベストスコア
            Study->>Study: update_best_trial()
            SM->>DB: save_best_model(model_instance)
        end
    end
    
    %% 3. 探索完了
    Study-->>SM: study_results
    
    SM->>SM: analyze_results(study_results)
    SM->>SM: get_best_params()
    SM->>SM: generate_importance_plot()
    SM->>SM: generate_optimization_history()
    
    SM->>DB: save_study_summary()
    
    SM-->>App: SearchResults
    
    Note over App: 探索完了<br/>Best params found<br/>Best score: X
```

---

## 11. アーティファクト管理

### 11.1 モデル保存とバージョニング

```mermaid
sequenceDiagram
    participant App as Application
    participant AM as ArtifactManager
    participant MS as ModelSaver
    participant PS as PredictionSaver
    participant MM as MetadataManager
    participant FS as File System
    participant DB as Database
    participant Hash as HashCalculator
    
    %% 1. モデル保存開始
    App->>AM: save_run_artifacts(run_info, model, predictions)
    
    AM->>AM: generate_run_id()
    AM->>AM: create_artifact_structure()
    
    %% 2. ディレクトリパス生成
    AM->>AM: encode_params_to_path(run_info.params)
    
    loop 各パラメータ
        AM->>AM: format_param_name(key, value)
        alt 値が長い（> 50文字）
            AM->>Hash: calculate_sha256_short(value)
            Hash-->>AM: hash_value
            AM->>AM: append(f"{key}={hash_value}")
        else 値が短い
            AM->>AM: append(f"{key}={value}")
        end
    end
    
    AM->>AM: check_path_length()
    alt パスが長すぎる（> 255文字）
        AM->>AM: truncate_path()
        AM->>Hash: calculate_dir_hash()
        Hash-->>AM: dir_hash
        AM->>AM: append_hash_suffix(dir_hash)
    end
    
    AM->>FS: mkdir(artifact_path)
    FS-->>AM: path_created
    
    %% 3. モデル保存
    AM->>MS: save_model(model, artifact_path)
    
    MS->>MS: serialize_model(model)
    MS->>MS: extract_model_metadata()
    
    MS->>FS: write(model_path, model_bytes)
    FS-->>MS: model_file_path
    
    MS->>Hash: calculate_file_hash(model_file_path)
    Hash-->>MS: model_hash
    
    MS->>MM: record_model_info(model_hash, model_metadata)
    
    MS-->>AM: model_saved
    
    %% 4. 予測結果保存
    AM->>PS: save_predictions(predictions, artifact_path)
    
    PS->>PS: format_predictions_df(predictions)
    PS->>PS: add_metadata_columns()
    
    PS->>FS: write_csv(predictions_path, predictions_df)
    FS-->>PS: predictions_file_path
    
    PS->>Hash: calculate_file_hash(predictions_file_path)
    Hash-->>PS: predictions_hash
    
    PS-->>AM: predictions_saved
    
    %% 5. メタデータ保存
    AM->>MM: save_metadata(run_info, artifact_path)
    
    MM->>MM: create_metadata_dict()
    MM->>MM: add_run_info(run_info)
    MM->>MM: add_model_hash(model_hash)
    MM->>MM: add_predictions_hash(predictions_hash)
    MM->>MM: add_timestamps()
    MM->>MM: add_environment_info()
    
    MM->>FS: write_json(metadata_path, metadata_dict)
    FS-->>MM: metadata_file_path
    
    MM-->>AM: metadata_saved
    
    %% 6. データベース記録
    AM->>DB: insert_run_record()
    DB-->>AM: run_id
    
    AM->>DB: insert_artifact_paths()
    DB-->>AM: artifact_id
    
    AM->>DB: insert_hashes()
    DB-->>AM: hash_id
    
    %% 7. インデックス更新
    AM->>DB: update_run_index()
    AM->>FS: create_symlink(latest_run)
    
    %% 8. クリーンアップ（オプション）
    alt 古いアーティファクト削除が有効
        AM->>DB: get_old_runs(retention_days)
        DB-->>AM: old_run_ids
        
        loop 各古いRun
            AM->>FS: delete_directory(old_artifact_path)
            AM->>DB: mark_as_archived(old_run_id)
        end
    end
    
    AM-->>App: ArtifactsSaved
    
    Note over App: アーティファクト保存完了<br/>Run ID: XXX<br/>Path: /outputs/...
```

---

## 12. エラーハンドリング

### 12.1 例外処理とリトライ

```mermaid
sequenceDiagram
    participant App as Application
    participant EH as ErrorHandler
    participant Retry as RetryManager
    participant Logger as StructuredLogger
    participant Model as NeuralForecast
    participant DB as Database
    participant Alert as AlertSystem
    
    %% 1. タスク実行開始
    App->>EH: execute_with_error_handling(task)
    
    EH->>EH: wrap_task(task)
    EH->>Retry: init_retry_policy(max_retries=3)
    
    loop 試行回数（最大3回）
        EH->>EH: try_execute(task)
        
        alt 実行成功
            EH-->>App: task_result
        else エラー発生
            Model->>Model: raise_exception(error)
            Model-->>EH: exception
            
            %% 2. エラー分類
            EH->>EH: classify_error(exception)
            
            alt データエラー
                EH->>EH: error_type = "DATA_ERROR"
                EH->>EH: recoverable = False
                
            else メモリエラー
                EH->>EH: error_type = "MEMORY_ERROR"
                EH->>EH: recoverable = True
                EH->>EH: suggest_reduce_batch_size()
                
            else GPUエラー
                EH->>EH: error_type = "GPU_ERROR"
                EH->>EH: recoverable = True
                EH->>EH: suggest_use_cpu()
                
            else ネットワークエラー
                EH->>EH: error_type = "NETWORK_ERROR"
                EH->>EH: recoverable = True
                
            else タイムアウト
                EH->>EH: error_type = "TIMEOUT"
                EH->>EH: recoverable = True
                EH->>EH: suggest_increase_timeout()
                
            else その他
                EH->>EH: error_type = "UNKNOWN_ERROR"
                EH->>EH: recoverable = True
            end
            
            %% 3. ログ記録
            EH->>Logger: log_error(error_info)
            Logger->>Logger: format_error_message()
            Logger->>Logger: extract_traceback()
            Logger->>Logger: add_context(task_info)
            Logger->>FS: write_error_log()
            
            %% 4. メタデータ保存
            EH->>EH: extract_error_metadata()
            EH->>DB: insert_error_record(error_metadata)
            
            %% 5. リトライ判定
            alt recoverable AND retries_left > 0
                EH->>Retry: should_retry(error_type, attempt)
                Retry-->>EH: retry=True
                
                Retry->>Retry: calculate_backoff(attempt)
                Note over Retry: Exponential backoff:<br/>2^attempt seconds
                
                Retry->>Retry: sleep(backoff_time)
                
                EH->>Logger: log_retry_attempt(attempt)
                
                %% リトライ前の修正
                alt メモリエラー
                    EH->>EH: reduce_batch_size()
                else GPUエラー
                    EH->>EH: switch_to_cpu()
                end
                
                Note over EH: 次の試行へ
                
            else 回復不能 OR リトライ上限
                Retry-->>EH: retry=False
                
                %% 6. 最終エラー処理
                EH->>EH: handle_final_failure()
                
                %% アラート送信
                EH->>Alert: send_alert(critical_error)
                Alert->>Email: send_error_notification()
                Alert->>Slack: post_error_message()
                
                %% フォールバック戦略
                alt フォールバックあり
                    EH->>EH: execute_fallback_strategy()
                    EH->>Logger: log_fallback_execution()
                else フォールバックなし
                    EH->>Logger: log_final_failure()
                    EH->>DB: mark_task_failed()
                    EH-->>App: TaskFailedError
                end
            end
        end
    end
    
    %% 7. 統計更新
    EH->>DB: update_error_statistics()
    EH->>DB: update_task_statistics()
    
    Note over App: エラーハンドリング完了
```

---

## 📊 シーケンス図の読み方

### 記号の説明

- **→**: 同期呼び出し（レスポンス待ち）
- **--→**: 非同期レスポンス
- **Note**: 補足説明
- **alt/else/end**: 条件分岐
- **loop/end**: 繰り返し
- **par/and/end**: 並列処理

### 色分けの意味（実装時）

- **青**: 正常フロー
- **赤**: エラーパス
- **黄**: 警告・注意
- **緑**: 成功

---

## 🎯 使用方法

### Mermaidレンダリング

これらのシーケンス図は、Mermaid対応のマークダウンビューアで表示できます：

1. **GitHub/GitLab**: 自動レンダリング
2. **VS Code**: Mermaid Preview拡張機能
3. **Mermaid Live Editor**: https://mermaid.live
4. **Confluence/Notion**: Mermaidプラグイン

### ドキュメント生成

```bash
# Mermaid CLIを使ってPNG/SVG生成
mmdc -i SEQUENCE_DIAGRAMS_DETAILED.md -o output/
```

---

## 📚 関連ドキュメント

- **00_INTEGRATED_DESIGN_OVERVIEW.md**: システム全体設計
- **03_ARCHITECTURE_DESIGN_DETAILED.md**: アーキテクチャ詳細
- **04_CLASS_DESIGN_DETAILED.md**: クラス設計詳細
- **07_IMPLEMENTATION_GUIDE.md**: 実装ガイド

---

**ドキュメントバージョン**: 1.0  
**最終更新日**: 2025-11-04  
**作成者**: System Architect  
**ステータス**: Complete
