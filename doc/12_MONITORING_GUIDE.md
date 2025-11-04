# 監視ガイド
**Monitoring Guide for Time Series Forecasting System**

---

## 📋 ドキュメント情報

| 項目 | 内容 |
|-----|------|
| **ドキュメントタイトル** | 時系列予測システム 監視ガイド |
| **バージョン** | v1.0.0 |
| **作成日** | 2025-11-03 |
| **最終更新日** | 2025-11-03 |
| **対象システム** | NeuralForecast Auto Runner + Time Series Forecasting System |
| **対象読者** | SRE、運用エンジニア、開発者、システム管理者 |

---

## 目次

1. [監視の概要](#1-監視の概要)
2. [監視アーキテクチャ](#2-監視アーキテクチャ)
3. [メトリクス収集](#3-メトリクス収集)
4. [ロギング戦略](#4-ロギング戦略)
5. [アラート設定](#5-アラート設定)
6. [ダッシュボード設計](#6-ダッシュボード設計)
7. [トレーシング](#7-トレーシング)
8. [監視ツール設定](#8-監視ツール設定)
9. [運用監視手順](#9-運用監視手順)
10. [トラブルシューティング](#10-トラブルシューティング)
11. [ベストプラクティス](#11-ベストプラクティス)
12. [付録](#12-付録)

---

## 1. 監視の概要

### 1.1 監視の目的

時系列予測システムの監視は、以下の3つの主要目的を持ちます:

#### 1. **可観測性の確保** (Observability)
- システムの内部状態を外部から理解可能にする
- 問題発生時の迅速な原因特定
- パフォーマンスのボトルネック発見

#### 2. **信頼性の維持** (Reliability)
- システムの稼働率99%以上を維持
- MTTR (Mean Time To Repair) < 1時間
- MTTD (Mean Time To Detect) < 10分

#### 3. **予防的な対応** (Proactive Operations)
- 障害の予兆検知
- リソース不足の事前警告
- パフォーマンス劣化の早期発見

---

### 1.2 監視の3つの柱

```
┌─────────────────────────────────────────────────┐
│           可観測性の3つの柱                        │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Metrics  │  │   Logs   │  │  Traces  │     │
│  │ (メトリクス)│  │ (ログ)    │  │(トレース) │     │
│  └──────────┘  └──────────┘  └──────────┘     │
│       │              │              │          │
│       │              │              │          │
│       └──────────────┴──────────────┘          │
│                     │                          │
│              ┌──────▼──────┐                   │
│              │ 統合された    │                   │
│              │ 可観測性     │                   │
│              └─────────────┘                   │
└─────────────────────────────────────────────────┘
```

---

### 1.3 監視の階層

| 階層 | 内容 | ツール | 優先度 |
|-----|------|-------|--------|
| **インフラ層** | CPU, メモリ, ディスク, ネットワーク | Prometheus + Node Exporter | P0 |
| **プラットフォーム層** | Docker, PostgreSQL, Ray | Prometheus + 各種Exporter | P0 |
| **アプリケーション層** | 実行中Run数、エラー率、レイテンシ | Prometheus + カスタムメトリクス | P0 |
| **ビジネス層** | 予測精度、モデル数、学習頻度 | Grafana + カスタムダッシュボード | P1 |

---

## 2. 監視アーキテクチャ

### 2.1 監視スタック全体像

```mermaid
graph TB
    subgraph "Application"
        App[NF Auto Runner]
        App --> |metrics| PromClient[Prometheus Client]
        App --> |logs| StdOut[stdout/stderr]
        App --> |traces| OTel[OpenTelemetry<br/>Collector]
    end
    
    subgraph "Collection"
        PromClient --> |pull| Prometheus[Prometheus]
        StdOut --> |forward| Loki[Loki]
        OTel --> |push| Jaeger[Jaeger]
        
        NodeExp[Node Exporter] --> |pull| Prometheus
        PgExp[Postgres Exporter] --> |pull| Prometheus
        RayMetrics[Ray Metrics] --> |pull| Prometheus
    end
    
    subgraph "Storage"
        Prometheus --> |TSDB| PromDB[(Prometheus DB)]
        Loki --> |chunks| LokiDB[(Loki Store)]
        Jaeger --> |spans| JaegerDB[(Jaeger Store)]
    end
    
    subgraph "Visualization & Alerting"
        Prometheus --> Grafana[Grafana]
        Loki --> Grafana
        Jaeger --> Grafana
        
        Prometheus --> AlertMgr[Alert Manager]
        AlertMgr --> Email[Email]
        AlertMgr --> Slack[Slack]
        AlertMgr --> PagerDuty[PagerDuty]
    end
    
    subgraph "Users"
        Ops[Operations Team]
        Dev[Development Team]
        Ops --> Grafana
        Dev --> Grafana
    end
```

---

### 2.2 コンポーネント一覧

#### 2.2.1 メトリクス収集

| コンポーネント | 役割 | 収集間隔 | 保持期間 |
|------------|------|---------|---------|
| **Prometheus** | メトリクス収集・保存 | 1分 | 30日 |
| **Node Exporter** | システムメトリクス | 1分 | 30日 |
| **Postgres Exporter** | DB メトリクス | 1分 | 30日 |
| **Prometheus Client** | アプリメトリクス | リアルタイム | - |

---

#### 2.2.2 ログ収集

| コンポーネント | 役割 | フォーマット | 保持期間 |
|------------|------|------------|---------|
| **structlog** | 構造化ロギング | JSON | - |
| **Loki** | ログ集約・保存 | LogQL | 90日 |
| **Promtail** | ログ転送 | - | - |

---

#### 2.2.3 トレーシング

| コンポーネント | 役割 | プロトコル | 保持期間 |
|------------|------|-----------|---------|
| **OpenTelemetry** | トレース収集 | OTLP | - |
| **Jaeger** | トレース可視化 | - | 7日 |

---

### 2.3 データフロー

```
Application Layer:
├─ Metrics → Prometheus Client → Prometheus (pull)
├─ Logs → structlog → stdout → Loki (push)
└─ Traces → OpenTelemetry → Jaeger (push)

Infrastructure Layer:
├─ System Metrics → Node Exporter → Prometheus (pull)
├─ Database Metrics → Postgres Exporter → Prometheus (pull)
└─ Container Metrics → cAdvisor → Prometheus (pull)

Visualization Layer:
├─ Prometheus → Grafana (query)
├─ Loki → Grafana (query)
└─ Jaeger → Grafana (query)

Alerting Layer:
└─ Prometheus → Alert Manager → Notification Channels
```

---

## 3. メトリクス収集

### 3.1 メトリクスの分類

#### 3.1.1 The Four Golden Signals

| Signal | 説明 | メトリクス例 | SLO |
|--------|------|------------|-----|
| **Latency** | 応答時間 | 学習時間、予測レイテンシ | p95<10秒 |
| **Traffic** | リクエスト量 | 実行中Run数、API QPS | - |
| **Errors** | エラー率 | 失敗Run率 | <10% |
| **Saturation** | リソース使用率 | CPU/メモリ/ディスク使用率 | <80% |

---

### 3.2 システムメトリクス

#### 3.2.1 ハードウェアメトリクス

```python
# prometheus_metrics.py

from prometheus_client import Gauge, Counter, Histogram, Info
import psutil
import time

# CPU メトリクス
cpu_usage = Gauge(
    'system_cpu_usage_percent',
    'CPU usage percentage',
    ['core']
)

cpu_count = Gauge(
    'system_cpu_count',
    'Number of CPU cores'
)

# メモリメトリクス
memory_usage = Gauge(
    'system_memory_usage_bytes',
    'Memory usage in bytes',
    ['type']  # total, available, used, free
)

memory_usage_percent = Gauge(
    'system_memory_usage_percent',
    'Memory usage percentage'
)

# ディスクメトリクス
disk_usage = Gauge(
    'system_disk_usage_bytes',
    'Disk usage in bytes',
    ['path', 'type']  # used, free, total
)

disk_usage_percent = Gauge(
    'system_disk_usage_percent',
    'Disk usage percentage',
    ['path']
)

disk_io = Counter(
    'system_disk_io_bytes_total',
    'Total disk I/O in bytes',
    ['device', 'direction']  # read, write
)

# ネットワークメトリクス
network_bytes = Counter(
    'system_network_bytes_total',
    'Total network traffic in bytes',
    ['interface', 'direction']  # sent, received
)

network_errors = Counter(
    'system_network_errors_total',
    'Total network errors',
    ['interface', 'direction']  # sent, received
)

# GPU メトリクス (GPUがある場合)
gpu_usage = Gauge(
    'system_gpu_usage_percent',
    'GPU usage percentage',
    ['gpu_id']
)

gpu_memory = Gauge(
    'system_gpu_memory_bytes',
    'GPU memory in bytes',
    ['gpu_id', 'type']  # used, free, total
)

gpu_temperature = Gauge(
    'system_gpu_temperature_celsius',
    'GPU temperature in Celsius',
    ['gpu_id']
)


class SystemMetricsCollector:
    """システムメトリクスを収集"""
    
    def __init__(self, interval: int = 60):
        """
        Args:
            interval: 収集間隔（秒）
        """
        self.interval = interval
    
    def collect_cpu_metrics(self):
        """CPU メトリクスを収集"""
        # CPU使用率（コアごと）
        for i, percent in enumerate(psutil.cpu_percent(percpu=True)):
            cpu_usage.labels(core=f'cpu{i}').set(percent)
        
        # CPU総数
        cpu_count.set(psutil.cpu_count())
    
    def collect_memory_metrics(self):
        """メモリメトリクスを収集"""
        mem = psutil.virtual_memory()
        
        memory_usage.labels(type='total').set(mem.total)
        memory_usage.labels(type='available').set(mem.available)
        memory_usage.labels(type='used').set(mem.used)
        memory_usage.labels(type='free').set(mem.free)
        
        memory_usage_percent.set(mem.percent)
    
    def collect_disk_metrics(self):
        """ディスクメトリクスを収集"""
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                
                disk_usage.labels(
                    path=partition.mountpoint,
                    type='total'
                ).set(usage.total)
                
                disk_usage.labels(
                    path=partition.mountpoint,
                    type='used'
                ).set(usage.used)
                
                disk_usage.labels(
                    path=partition.mountpoint,
                    type='free'
                ).set(usage.free)
                
                disk_usage_percent.labels(
                    path=partition.mountpoint
                ).set(usage.percent)
            
            except PermissionError:
                # 一部のマウントポイントはアクセス不可
                continue
        
        # ディスクI/O
        disk_io_counters = psutil.disk_io_counters(perdisk=True)
        for device, counters in disk_io_counters.items():
            disk_io.labels(device=device, direction='read').inc(
                counters.read_bytes
            )
            disk_io.labels(device=device, direction='write').inc(
                counters.write_bytes
            )
    
    def collect_network_metrics(self):
        """ネットワークメトリクスを収集"""
        net_io = psutil.net_io_counters(pernic=True)
        
        for interface, counters in net_io.items():
            network_bytes.labels(
                interface=interface,
                direction='sent'
            ).inc(counters.bytes_sent)
            
            network_bytes.labels(
                interface=interface,
                direction='received'
            ).inc(counters.bytes_recv)
            
            network_errors.labels(
                interface=interface,
                direction='sent'
            ).inc(counters.errout)
            
            network_errors.labels(
                interface=interface,
                direction='received'
            ).inc(counters.errin)
    
    def collect_gpu_metrics(self):
        """GPU メトリクスを収集"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            
            for gpu in gpus:
                gpu_usage.labels(gpu_id=gpu.id).set(gpu.load * 100)
                
                gpu_memory.labels(
                    gpu_id=gpu.id,
                    type='used'
                ).set(gpu.memoryUsed * 1024 * 1024)  # MB to bytes
                
                gpu_memory.labels(
                    gpu_id=gpu.id,
                    type='free'
                ).set(gpu.memoryFree * 1024 * 1024)
                
                gpu_memory.labels(
                    gpu_id=gpu.id,
                    type='total'
                ).set(gpu.memoryTotal * 1024 * 1024)
                
                gpu_temperature.labels(gpu_id=gpu.id).set(gpu.temperature)
        
        except ImportError:
            # GPU がない、またはGPUtilがインストールされていない
            pass
    
    def collect_all(self):
        """全メトリクスを収集"""
        self.collect_cpu_metrics()
        self.collect_memory_metrics()
        self.collect_disk_metrics()
        self.collect_network_metrics()
        self.collect_gpu_metrics()
    
    def start(self):
        """定期収集を開始"""
        while True:
            self.collect_all()
            time.sleep(self.interval)
```

**収集間隔**: 1分
**保持期間**: 30日

---

### 3.3 アプリケーションメトリクス

#### 3.3.1 実行メトリクス

```python
# application_metrics.py

from prometheus_client import Counter, Gauge, Histogram, Summary
from typing import List
import time

# Run実行メトリクス
runs_total = Counter(
    'nf_runs_total',
    'Total number of runs',
    ['status', 'model_name', 'backend']
)

runs_active = Gauge(
    'nf_runs_active',
    'Number of currently active runs'
)

runs_queued = Gauge(
    'nf_runs_queued',
    'Number of runs in queue'
)

# 学習時間メトリクス
training_duration_seconds = Histogram(
    'nf_training_duration_seconds',
    'Model training duration in seconds',
    ['model_name', 'backend'],
    buckets=[60, 120, 300, 600, 1200, 1800, 3600]  # 1分〜1時間
)

# 予測レイテンシメトリクス
prediction_latency_seconds = Histogram(
    'nf_prediction_latency_seconds',
    'Prediction latency in seconds',
    ['model_name'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]  # 10ms〜5秒
)

# データサイズメトリクス
dataset_size = Histogram(
    'nf_dataset_size_rows',
    'Dataset size in number of rows',
    buckets=[100, 1000, 10000, 100000, 1000000, 10000000]
)

unique_ids_count = Histogram(
    'nf_unique_ids_count',
    'Number of unique IDs',
    buckets=[10, 100, 1000, 10000]
)

# エラーメトリクス
errors_total = Counter(
    'nf_errors_total',
    'Total number of errors',
    ['error_type', 'component']
)

# パフォーマンスメトリクス
model_accuracy = Gauge(
    'nf_model_accuracy',
    'Model accuracy metric (e.g., sMAPE)',
    ['model_name', 'metric_type']
)

# リソース使用メトリクス
memory_usage_bytes = Gauge(
    'nf_memory_usage_bytes',
    'Memory usage by component',
    ['component']
)

# データベースメトリクス
db_connections = Gauge(
    'nf_db_connections_active',
    'Number of active database connections'
)

db_query_duration_seconds = Histogram(
    'nf_db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type'],
    buckets=[0.001, 0.01, 0.1, 0.5, 1.0, 5.0]  # 1ms〜5秒
)


class ApplicationMetricsCollector:
    """アプリケーションメトリクスを収集"""
    
    @staticmethod
    def record_run_start(model_name: str, backend: str):
        """Run開始を記録"""
        runs_active.inc()
        runs_total.labels(
            status='started',
            model_name=model_name,
            backend=backend
        ).inc()
    
    @staticmethod
    def record_run_success(
        model_name: str,
        backend: str,
        duration: float
    ):
        """Run成功を記録"""
        runs_active.dec()
        runs_total.labels(
            status='success',
            model_name=model_name,
            backend=backend
        ).inc()
        
        training_duration_seconds.labels(
            model_name=model_name,
            backend=backend
        ).observe(duration)
    
    @staticmethod
    def record_run_failure(
        model_name: str,
        backend: str,
        error_type: str
    ):
        """Run失敗を記録"""
        runs_active.dec()
        runs_total.labels(
            status='failed',
            model_name=model_name,
            backend=backend
        ).inc()
        
        errors_total.labels(
            error_type=error_type,
            component='training'
        ).inc()
    
    @staticmethod
    def record_prediction(model_name: str, duration: float):
        """予測実行を記録"""
        prediction_latency_seconds.labels(
            model_name=model_name
        ).observe(duration)
    
    @staticmethod
    def record_dataset_info(n_rows: int, n_unique_ids: int):
        """データセット情報を記録"""
        dataset_size.observe(n_rows)
        unique_ids_count.observe(n_unique_ids)
    
    @staticmethod
    def update_model_accuracy(
        model_name: str,
        metric_type: str,
        value: float
    ):
        """モデル精度を更新"""
        model_accuracy.labels(
            model_name=model_name,
            metric_type=metric_type
        ).set(value)
    
    @staticmethod
    def record_db_query(query_type: str, duration: float):
        """データベースクエリを記録"""
        db_query_duration_seconds.labels(
            query_type=query_type
        ).observe(duration)
```

**収集間隔**: リアルタイム（イベント駆動）
**保持期間**: 30日

---

### 3.4 ビジネスメトリクス

#### 3.4.1 KPI メトリクス

```python
# business_metrics.py

from prometheus_client import Gauge, Counter
from datetime import datetime, timedelta

# 日次KPI
daily_runs_count = Counter(
    'nf_daily_runs_count',
    'Number of runs per day',
    ['date']
)

daily_models_trained = Counter(
    'nf_daily_models_trained',
    'Number of models trained per day',
    ['date']
)

# 週次KPI
weekly_average_accuracy = Gauge(
    'nf_weekly_average_accuracy',
    'Weekly average model accuracy',
    ['week', 'metric_type']
)

# システム稼働率
system_uptime_seconds = Counter(
    'nf_system_uptime_seconds_total',
    'Total system uptime in seconds'
)

system_availability_percent = Gauge(
    'nf_system_availability_percent',
    'System availability percentage'
)

# ユーザーアクティビティ
user_sessions = Gauge(
    'nf_user_sessions_active',
    'Number of active user sessions'
)

# コスト効率
cost_per_prediction = Gauge(
    'nf_cost_per_prediction_usd',
    'Estimated cost per prediction in USD',
    ['model_type']
)


class BusinessMetricsCollector:
    """ビジネスメトリクスを収集"""
    
    def __init__(self, db_session):
        self.db_session = db_session
    
    def collect_daily_kpis(self):
        """日次KPIを収集"""
        today = datetime.now().date()
        
        # 今日のRun数
        run_count = self.db_session.query(Run).filter(
            Run.created_at >= today
        ).count()
        
        daily_runs_count.labels(date=str(today)).inc(run_count)
        
        # 今日学習したモデル数
        model_count = self.db_session.query(Model).filter(
            Model.created_at >= today
        ).count()
        
        daily_models_trained.labels(date=str(today)).inc(model_count)
    
    def collect_weekly_kpis(self):
        """週次KPIを収集"""
        # 今週の開始日
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        # 今週の平均精度
        avg_accuracy = self.db_session.query(
            func.avg(Model.smape)
        ).filter(
            Model.created_at >= week_start
        ).scalar()
        
        if avg_accuracy:
            weekly_average_accuracy.labels(
                week=str(week_start),
                metric_type='smape'
            ).set(avg_accuracy)
    
    def update_availability(self, downtime_seconds: float):
        """稼働率を更新"""
        # 月間の総時間（秒）
        total_seconds = 30 * 24 * 60 * 60  # 30日
        
        # 稼働率を計算
        availability = (
            (total_seconds - downtime_seconds) / total_seconds
        ) * 100
        
        system_availability_percent.set(availability)
```

**収集間隔**: 1時間
**保持期間**: 180日

---

### 3.5 メトリクスのエクスポート

#### 3.5.1 Prometheus Exporter設定

```python
# prometheus_exporter.py

from prometheus_client import start_http_server
import time
import logging

logger = logging.getLogger(__name__)


class PrometheusExporter:
    """Prometheus メトリクスエクスポーター"""
    
    def __init__(self, port: int = 9090):
        """
        Args:
            port: メトリクスエクスポート用ポート
        """
        self.port = port
        self.collectors = []
    
    def register_collector(self, collector):
        """コレクターを登録"""
        self.collectors.append(collector)
    
    def start(self):
        """エクスポーターを起動"""
        try:
            # HTTPサーバーを起動
            start_http_server(self.port)
            logger.info(
                f"Prometheus exporter started on port {self.port}"
            )
            
            # メトリクス収集を開始
            for collector in self.collectors:
                if hasattr(collector, 'start'):
                    collector.start()
            
            # メインループ
            while True:
                time.sleep(60)
        
        except Exception as e:
            logger.error(f"Failed to start Prometheus exporter: {e}")
            raise


# 使用例
if __name__ == '__main__':
    # エクスポーターを作成
    exporter = PrometheusExporter(port=9090)
    
    # コレクターを登録
    system_collector = SystemMetricsCollector(interval=60)
    exporter.register_collector(system_collector)
    
    # エクスポーターを起動
    exporter.start()
```

---

## 4. ロギング戦略

### 4.1 ログレベル

#### 4.1.1 ログレベル定義

| レベル | 用途 | 例 | 出力先 |
|-------|------|---|--------|
| **CRITICAL** | システムクラッシュ | データベース接続不可 | stdout, file, alert |
| **ERROR** | エラーだが継続可能 | モデル学習失敗 | stdout, file |
| **WARNING** | 警告 | メモリ使用量高い | stdout, file |
| **INFO** | 通常動作の記録 | モデル学習開始 | stdout, file |
| **DEBUG** | デバッグ情報 | 変数値、関数呼び出し | file (開発時のみ) |

---

### 4.2 構造化ロギング

#### 4.2.1 ログフォーマット

```json
{
  "timestamp": "2025-11-03T12:34:56.789Z",
  "level": "INFO",
  "logger": "nf_auto_runner.service.execution",
  "message": "Model training started",
  "context": {
    "run_id": "abc123",
    "experiment_id": "exp456",
    "model_name": "AutoNHITS",
    "backend": "optuna",
    "dataset_version": "v1.0",
    "user_id": "user123"
  },
  "metadata": {
    "hostname": "server01",
    "process_id": 12345,
    "thread_id": 67890,
    "correlation_id": "req-xyz789"
  },
  "performance": {
    "cpu_percent": 45.2,
    "memory_mb": 2048,
    "duration_ms": 1250
  }
}
```

---

#### 4.2.2 構造化ロガー実装

```python
# structured_logger.py

import structlog
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional
import json


class StructuredLogger:
    """構造化ログ出力クラス"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton パターン"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初期化"""
        if not hasattr(self, 'initialized'):
            self._configure_logging()
            self.initialized = True
    
    def _configure_logging(self):
        """ロギング設定"""
        # structlog設定
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(
                    fmt="iso",
                    utc=True
                ),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            wrapper_class=structlog.make_filtering_bound_logger(
                logging.INFO
            ),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
        
        # 標準ロガー設定
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=logging.INFO,
        )
    
    @classmethod
    def get_logger(
        cls,
        name: str,
        **initial_context: Any
    ) -> structlog.BoundLogger:
        """
        ロガーを取得
        
        Args:
            name: ロガー名
            **initial_context: 初期コンテキスト
        
        Returns:
            structlog.BoundLogger
        """
        instance = cls()
        logger = structlog.get_logger(name)
        
        # 初期コンテキストをバインド
        if initial_context:
            logger = logger.bind(**initial_context)
        
        return logger
    
    @staticmethod
    def log_event(
        logger: structlog.BoundLogger,
        event: str,
        level: str = 'info',
        **context: Any
    ):
        """
        イベントをログ
        
        Args:
            logger: ロガー
            event: イベント名
            level: ログレベル
            **context: コンテキスト情報
        """
        log_method = getattr(logger, level.lower())
        log_method(event, **context)


# 使用例
logger = StructuredLogger.get_logger(
    'nf_auto_runner.training',
    component='training_service',
    environment='production'
)

# ログ出力
logger.info(
    'model_training_started',
    run_id='abc123',
    model_name='AutoLSTM',
    backend='optuna'
)

logger.error(
    'model_training_failed',
    run_id='abc123',
    model_name='AutoLSTM',
    error_type='ResourceExhausted',
    error_message='Out of memory'
)
```

---

### 4.3 ログ出力先

#### 4.3.1 出力先設定

| 出力先 | 用途 | ローテーション | 優先度 |
|-------|------|--------------|--------|
| **ファイル** | 永続化 | 日次 or 100MB | P0 |
| **標準出力** | リアルタイム確認 | なし | P0 |
| **Loki** | 集約・検索 | サーバー側 | P2 |
| **Elasticsearch** | 分析 | サーバー側 | P3 |

---

#### 4.3.2 ファイルロガー設定

```python
# file_logger.py

import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path


class FileLogger:
    """ファイルロガー"""
    
    @staticmethod
    def setup_rotating_file_handler(
        log_file: Path,
        max_bytes: int = 100 * 1024 * 1024,  # 100MB
        backup_count: int = 10
    ) -> RotatingFileHandler:
        """
        サイズベースのローテーションハンドラー
        
        Args:
            log_file: ログファイルパス
            max_bytes: 最大ファイルサイズ
            backup_count: バックアップ数
        
        Returns:
            RotatingFileHandler
        """
        # ディレクトリ作成
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # ハンドラー作成
        handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        
        # フォーマット設定
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        return handler
    
    @staticmethod
    def setup_timed_rotating_handler(
        log_file: Path,
        when: str = 'midnight',
        interval: int = 1,
        backup_count: int = 30
    ) -> TimedRotatingFileHandler:
        """
        時間ベースのローテーションハンドラー
        
        Args:
            log_file: ログファイルパス
            when: ローテーションタイミング
            interval: ローテーション間隔
            backup_count: バックアップ数
        
        Returns:
            TimedRotatingFileHandler
        """
        # ディレクトリ作成
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # ハンドラー作成
        handler = TimedRotatingFileHandler(
            filename=log_file,
            when=when,
            interval=interval,
            backupCount=backup_count,
            encoding='utf-8'
        )
        
        # フォーマット設定
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        return handler


# 使用例
from pathlib import Path

# アプリケーションログ
app_logger = logging.getLogger('nf_auto_runner')
app_logger.setLevel(logging.INFO)

# サイズベースローテーション
app_handler = FileLogger.setup_rotating_file_handler(
    log_file=Path('logs/app/nf_runner.log'),
    max_bytes=100 * 1024 * 1024,  # 100MB
    backup_count=10
)
app_logger.addHandler(app_handler)

# 時間ベースローテーション
daily_handler = FileLogger.setup_timed_rotating_handler(
    log_file=Path('logs/daily/nf_runner.log'),
    when='midnight',
    interval=1,
    backup_count=30
)
app_logger.addHandler(daily_handler)
```

---

### 4.4 ログコンテキスト管理

#### 4.4.1 コンテキスト変数

```python
# log_context.py

import contextvars
from typing import Any, Dict, Optional
import uuid


# コンテキスト変数
correlation_id_var = contextvars.ContextVar(
    'correlation_id',
    default=None
)

run_id_var = contextvars.ContextVar(
    'run_id',
    default=None
)

user_id_var = contextvars.ContextVar(
    'user_id',
    default=None
)


class LogContext:
    """ログコンテキスト管理"""
    
    @staticmethod
    def set_correlation_id(correlation_id: Optional[str] = None) -> str:
        """
        相関IDを設定
        
        Args:
            correlation_id: 相関ID（Noneの場合は自動生成）
        
        Returns:
            設定された相関ID
        """
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())
        
        correlation_id_var.set(correlation_id)
        return correlation_id
    
    @staticmethod
    def get_correlation_id() -> Optional[str]:
        """相関IDを取得"""
        return correlation_id_var.get()
    
    @staticmethod
    def set_run_id(run_id: str):
        """Run IDを設定"""
        run_id_var.set(run_id)
    
    @staticmethod
    def get_run_id() -> Optional[str]:
        """Run IDを取得"""
        return run_id_var.get()
    
    @staticmethod
    def set_user_id(user_id: str):
        """ユーザーIDを設定"""
        user_id_var.set(user_id)
    
    @staticmethod
    def get_user_id() -> Optional[str]:
        """ユーザーIDを取得"""
        return user_id_var.get()
    
    @staticmethod
    def get_context() -> Dict[str, Any]:
        """全コンテキストを取得"""
        context = {}
        
        if (correlation_id := correlation_id_var.get()) is not None:
            context['correlation_id'] = correlation_id
        
        if (run_id := run_id_var.get()) is not None:
            context['run_id'] = run_id
        
        if (user_id := user_id_var.get()) is not None:
            context['user_id'] = user_id
        
        return context
    
    @staticmethod
    def clear():
        """コンテキストをクリア"""
        correlation_id_var.set(None)
        run_id_var.set(None)
        user_id_var.set(None)


# 使用例
from nf_auto_runner.logging import StructuredLogger, LogContext

# コンテキスト設定
LogContext.set_correlation_id()
LogContext.set_run_id('run-123')
LogContext.set_user_id('user-456')

# ロガー取得（コンテキスト自動付与）
logger = StructuredLogger.get_logger(
    'nf_auto_runner.training',
    **LogContext.get_context()
)

# ログ出力
logger.info('model_training_started', model_name='AutoLSTM')
# 出力: {"timestamp": "...", "correlation_id": "...", "run_id": "run-123", ...}
```

---

## 5. アラート設定

### 5.1 アラートルール

#### 5.1.1 Critical アラート

| アラート名 | 条件 | 重要度 | 通知先 | アクション |
|----------|------|-------|-------|----------|
| **SystemDown** | プロセス停止 | Critical | Email, Slack, PagerDuty | 即座に対応 |
| **DatabaseDown** | DB接続不可 for 1分 | Critical | Email, Slack, PagerDuty | 即座に対応 |
| **DiskFull** | ディスク使用率>95% | Critical | Email, Slack | 1時間以内に対応 |

---

#### 5.1.2 High アラート

| アラート名 | 条件 | 重要度 | 通知先 | アクション |
|----------|------|-------|-------|----------|
| **HighMemoryUsage** | メモリ使用率>90% for 5分 | High | Email, Slack | 2時間以内に対応 |
| **HighErrorRate** | エラー率>10% for 5分 | High | Email, Slack | 2時間以内に対応 |
| **SlowResponse** | p95レイテンシ>10秒 for 10分 | High | Slack | 4時間以内に対応 |

---

#### 5.1.3 Medium アラート

| アラート名 | 条件 | 重要度 | 通知先 | アクション |
|----------|------|-------|-------|----------|
| **HighCPUUsage** | CPU使用率>80% for 10分 | Medium | Slack | 翌営業日に確認 |
| **LongRunningTask** | 実行時間>2x平均 | Medium | Slack | 翌営業日に確認 |
| **QueueBacklog** | キュー>50 for 10分 | Medium | Slack | 翌営業日に確認 |

---

### 5.2 Prometheusアラートルール

#### 5.2.1 アラートルール設定

```yaml
# prometheus/alerts/nf_runner_alerts.yml

groups:
  - name: nf_runner_critical
    interval: 1m
    rules:
      # システムダウン
      - alert: SystemDown
        expr: up{job="nf-runner"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "NF Runner is down"
          description: "NF Runner process has been down for more than 1 minute"
          dashboard: "https://grafana.example.com/d/nf-runner"
      
      # データベースダウン
      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL is down"
          description: "PostgreSQL has been down for more than 1 minute"
      
      # ディスク満杯
      - alert: DiskFull
        expr: |
          (
            node_filesystem_avail_bytes{mountpoint="/"}
            / node_filesystem_size_bytes{mountpoint="/"}
          ) * 100 < 5
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Disk space is critically low"
          description: "Disk usage is above 95% (current: {{ $value }}%)"

  - name: nf_runner_high
    interval: 1m
    rules:
      # 高メモリ使用率
      - alert: HighMemoryUsage
        expr: |
          (
            node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes
          ) / node_memory_MemTotal_bytes * 100 > 90
        for: 5m
        labels:
          severity: high
        annotations:
          summary: "Memory usage is high"
          description: "Memory usage is above 90% for 5 minutes (current: {{ $value }}%)"
      
      # 高エラー率
      - alert: HighErrorRate
        expr: |
          (
            rate(nf_runs_total{status="failed"}[5m])
            / rate(nf_runs_total[5m])
          ) * 100 > 10
        for: 5m
        labels:
          severity: high
        annotations:
          summary: "High error rate detected"
          description: "Error rate is above 10% for 5 minutes (current: {{ $value }}%)"
      
      # 遅い応答
      - alert: SlowResponse
        expr: |
          histogram_quantile(0.95,
            rate(nf_training_duration_seconds_bucket[10m])
          ) > 600
        for: 10m
        labels:
          severity: high
        annotations:
          summary: "Training duration is slow"
          description: "95th percentile training duration is above 10 minutes (current: {{ $value }}s)"

  - name: nf_runner_medium
    interval: 5m
    rules:
      # 高CPU使用率
      - alert: HighCPUUsage
        expr: |
          100 - (avg by (instance) (
            rate(node_cpu_seconds_total{mode="idle"}[5m])
          ) * 100) > 80
        for: 10m
        labels:
          severity: medium
        annotations:
          summary: "CPU usage is high"
          description: "CPU usage is above 80% for 10 minutes (current: {{ $value }}%)"
      
      # 長時間実行タスク
      - alert: LongRunningTask
        expr: |
          nf_training_duration_seconds > (
            avg_over_time(nf_training_duration_seconds[24h]) * 2
          )
        labels:
          severity: medium
        annotations:
          summary: "Long running task detected"
          description: "Task duration is more than 2x the average (current: {{ $value }}s)"
      
      # キュー滞留
      - alert: QueueBacklog
        expr: nf_runs_queued > 50
        for: 10m
        labels:
          severity: medium
        annotations:
          summary: "Queue backlog detected"
          description: "More than 50 runs are queued for 10 minutes (current: {{ $value }})"
```

---

### 5.3 Alert Manager設定

#### 5.3.1 Alert Manager設定ファイル

```yaml
# alertmanager/alertmanager.yml

global:
  # メール設定
  smtp_smarthost: 'smtp.example.com:587'
  smtp_from: 'alerts@example.com'
  smtp_auth_username: 'alerts@example.com'
  smtp_auth_password: '${SMTP_PASSWORD}'
  
  # Slack Webhook URL
  slack_api_url: '${SLACK_WEBHOOK_URL}'

# ルーティング設定
route:
  # デフォルト受信者
  receiver: 'team-email'
  
  # グループ化設定
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  
  # ルーティングルール
  routes:
    # Critical アラート
    - match:
        severity: critical
      receiver: 'critical-alerts'
      continue: true
      repeat_interval: 1h
    
    # High アラート
    - match:
        severity: high
      receiver: 'high-alerts'
      repeat_interval: 2h
    
    # Medium アラート
    - match:
        severity: medium
      receiver: 'medium-alerts'
      repeat_interval: 6h

# 受信者設定
receivers:
  # Critical アラート受信者
  - name: 'critical-alerts'
    email_configs:
      - to: 'oncall@example.com'
        headers:
          Subject: '[CRITICAL] {{ .GroupLabels.alertname }}'
    slack_configs:
      - channel: '#alerts-critical'
        title: '[CRITICAL] {{ .GroupLabels.alertname }}'
        text: |
          {{ range .Alerts }}
          *Alert:* {{ .Labels.alertname }}
          *Description:* {{ .Annotations.description }}
          *Dashboard:* {{ .Annotations.dashboard }}
          {{ end }}
    pagerduty_configs:
      - service_key: '${PAGERDUTY_SERVICE_KEY}'
  
  # High アラート受信者
  - name: 'high-alerts'
    email_configs:
      - to: 'team@example.com'
        headers:
          Subject: '[HIGH] {{ .GroupLabels.alertname }}'
    slack_configs:
      - channel: '#alerts-high'
        title: '[HIGH] {{ .GroupLabels.alertname }}'
        text: |
          {{ range .Alerts }}
          *Alert:* {{ .Labels.alertname }}
          *Description:* {{ .Annotations.description }}
          {{ end }}
  
  # Medium アラート受信者
  - name: 'medium-alerts'
    slack_configs:
      - channel: '#alerts-medium'
        title: '[MEDIUM] {{ .GroupLabels.alertname }}'
        text: |
          {{ range .Alerts }}
          *Alert:* {{ .Labels.alertname }}
          *Description:* {{ .Annotations.description }}
          {{ end }}
  
  # デフォルト受信者
  - name: 'team-email'
    email_configs:
      - to: 'team@example.com'

# 抑制ルール
inhibit_rules:
  # SystemDownアラートが発火中は他のアラートを抑制
  - source_match:
      alertname: 'SystemDown'
    target_match_re:
      alertname: '.*'
    equal: ['instance']
  
  # DatabaseDownアラートが発火中はDB関連アラートを抑制
  - source_match:
      alertname: 'DatabaseDown'
    target_match_re:
      alertname: 'Database.*'
    equal: ['instance']
```

---

### 5.4 アラート通知フォーマット

#### 5.4.1 Email通知テンプレート

```html
<!-- alertmanager/templates/email.html -->

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ .GroupLabels.alertname }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        .alert-critical {
            background-color: #ff4444;
            color: white;
            padding: 15px;
            border-radius: 5px;
        }
        .alert-high {
            background-color: #ff8800;
            color: white;
            padding: 15px;
            border-radius: 5px;
        }
        .alert-medium {
            background-color: #ffbb33;
            color: white;
            padding: 15px;
            border-radius: 5px;
        }
        .details {
            margin-top: 20px;
            padding: 15px;
            background-color: #f5f5f5;
            border-radius: 5px;
        }
        .actions {
            margin-top: 20px;
            padding: 15px;
            background-color: #e3f2fd;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="alert-{{ .GroupLabels.severity }}">
        <h2>[{{ .GroupLabels.severity | toUpper }}] {{ .GroupLabels.alertname }}</h2>
    </div>
    
    <div class="details">
        <h3>Details</h3>
        {{ range .Alerts }}
        <p>
            <strong>Time:</strong> {{ .StartsAt.Format "2006-01-02 15:04:05 MST" }}<br>
            <strong>Instance:</strong> {{ .Labels.instance }}<br>
            <strong>Description:</strong> {{ .Annotations.description }}
        </p>
        {{ end }}
    </div>
    
    <div class="actions">
        <h3>Recommended Actions</h3>
        <ol>
            <li>Check the dashboard: <a href="{{ .Annotations.dashboard }}">{{ .Annotations.dashboard }}</a></li>
            <li>Review recent logs</li>
            <li>Check system resources</li>
            <li>Follow the runbook</li>
        </ol>
    </div>
    
    <p>
        <small>
            This alert was generated by Prometheus Alert Manager.<br>
            Dashboard: <a href="{{ .ExternalURL }}">{{ .ExternalURL }}</a>
        </small>
    </p>
</body>
</html>
```

---

#### 5.4.2 Slack通知テンプレート

```yaml
# alertmanager/templates/slack.tmpl

{{ define "slack.default.title" }}
[{{ .Status | toUpper }}{{ if eq .Status "firing" }}:{{ .Alerts.Firing | len }}{{ end }}] {{ .GroupLabels.alertname }}
{{ end }}

{{ define "slack.default.text" }}
{{ range .Alerts }}
*Alert:* {{ .Labels.alertname }}
*Severity:* {{ .Labels.severity }}
*Instance:* {{ .Labels.instance }}
*Description:* {{ .Annotations.description }}
*Dashboard:* {{ .Annotations.dashboard }}
*Started:* {{ .StartsAt.Format "2006-01-02 15:04:05 MST" }}
---
{{ end }}
{{ end }}
```

---

## 6. ダッシュボード設計

### 6.1 Grafanaダッシュボード構成

#### 6.1.1 ダッシュボード一覧

| ダッシュボード名 | 目的 | 主要パネル | 更新頻度 |
|-------------|------|----------|---------|
| **System Overview** | システム全体の概要 | 稼働率、リソース、Run数 | 1分 |
| **Application Metrics** | アプリケーション監視 | 実行時間、エラー率、QPS | 1分 |
| **Model Performance** | モデルパフォーマンス | 精度、学習時間、予測レイテンシ | 5分 |
| **Database Monitoring** | データベース監視 | 接続数、クエリ時間、容量 | 1分 |
| **Business KPIs** | ビジネスKPI | 日次Run数、週次精度、コスト | 1時間 |

---

### 6.2 System Overview ダッシュボード

#### 6.2.1 パネル構成

```json
{
  "dashboard": {
    "title": "NF Runner - System Overview",
    "tags": ["nf-runner", "system"],
    "timezone": "browser",
    "refresh": "1m",
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "panels": [
      {
        "id": 1,
        "title": "System Uptime",
        "type": "stat",
        "gridPos": {"x": 0, "y": 0, "w": 6, "h": 4},
        "targets": [
          {
            "expr": "time() - process_start_time_seconds{job=\"nf-runner\"}",
            "legendFormat": "Uptime",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "s",
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"value": 0, "color": "red"},
                {"value": 3600, "color": "yellow"},
                {"value": 86400, "color": "green"}
              ]
            }
          }
        }
      },
      {
        "id": 2,
        "title": "CPU Usage",
        "type": "graph",
        "gridPos": {"x": 6, "y": 0, "w": 6, "h": 4},
        "targets": [
          {
            "expr": "100 - (avg by (instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "CPU %",
            "refId": "A"
          }
        ],
        "yaxes": [
          {
            "format": "percent",
            "max": 100,
            "min": 0
          }
        ],
        "alert": {
          "conditions": [
            {
              "evaluator": {"params": [80], "type": "gt"},
              "operator": {"type": "and"},
              "query": {"params": ["A", "5m", "now"]},
              "reducer": {"params": [], "type": "avg"},
              "type": "query"
            }
          ],
          "executionErrorState": "alerting",
          "frequency": "1m",
          "handler": 1,
          "name": "CPU Usage Alert",
          "noDataState": "no_data",
          "notifications": []
        }
      },
      {
        "id": 3,
        "title": "Memory Usage",
        "type": "graph",
        "gridPos": {"x": 12, "y": 0, "w": 6, "h": 4},
        "targets": [
          {
            "expr": "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100",
            "legendFormat": "Memory %",
            "refId": "A"
          }
        ],
        "yaxes": [
          {
            "format": "percent",
            "max": 100,
            "min": 0
          }
        ]
      },
      {
        "id": 4,
        "title": "Disk Usage",
        "type": "graph",
        "gridPos": {"x": 18, "y": 0, "w": 6, "h": 4},
        "targets": [
          {
            "expr": "(node_filesystem_size_bytes{mountpoint=\"/\"} - node_filesystem_avail_bytes{mountpoint=\"/\"}) / node_filesystem_size_bytes{mountpoint=\"/\"} * 100",
            "legendFormat": "Disk %",
            "refId": "A"
          }
        ],
        "yaxes": [
          {
            "format": "percent",
            "max": 100,
            "min": 0
          }
        ]
      },
      {
        "id": 5,
        "title": "Active Runs",
        "type": "stat",
        "gridPos": {"x": 0, "y": 4, "w": 6, "h": 4},
        "targets": [
          {
            "expr": "nf_runs_active",
            "legendFormat": "Active Runs",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "short",
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"value": 0, "color": "green"},
                {"value": 50, "color": "yellow"},
                {"value": 100, "color": "red"}
              ]
            }
          }
        }
      },
      {
        "id": 6,
        "title": "Run Success Rate",
        "type": "gauge",
        "gridPos": {"x": 6, "y": 4, "w": 6, "h": 4},
        "targets": [
          {
            "expr": "(sum(rate(nf_runs_total{status=\"success\"}[5m])) / sum(rate(nf_runs_total[5m]))) * 100",
            "legendFormat": "Success Rate %",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "max": 100,
            "min": 0,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"value": 0, "color": "red"},
                {"value": 90, "color": "yellow"},
                {"value": 95, "color": "green"}
              ]
            }
          }
        }
      },
      {
        "id": 7,
        "title": "Training Duration (p50, p95, p99)",
        "type": "graph",
        "gridPos": {"x": 12, "y": 4, "w": 12, "h": 4},
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(nf_training_duration_seconds_bucket[5m]))",
            "legendFormat": "p50",
            "refId": "A"
          },
          {
            "expr": "histogram_quantile(0.95, rate(nf_training_duration_seconds_bucket[5m]))",
            "legendFormat": "p95",
            "refId": "B"
          },
          {
            "expr": "histogram_quantile(0.99, rate(nf_training_duration_seconds_bucket[5m]))",
            "legendFormat": "p99",
            "refId": "C"
          }
        ],
        "yaxes": [
          {
            "format": "s",
            "logBase": 1,
            "min": 0
          }
        ]
      },
      {
        "id": 8,
        "title": "Error Rate by Type",
        "type": "graph",
        "gridPos": {"x": 0, "y": 8, "w": 12, "h": 4},
        "targets": [
          {
            "expr": "sum(rate(nf_errors_total[5m])) by (error_type)",
            "legendFormat": "{{ error_type }}",
            "refId": "A"
          }
        ],
        "yaxes": [
          {
            "format": "ops",
            "logBase": 1,
            "min": 0
          }
        ]
      },
      {
        "id": 9,
        "title": "Database Connections",
        "type": "graph",
        "gridPos": {"x": 12, "y": 8, "w": 12, "h": 4},
        "targets": [
          {
            "expr": "nf_db_connections_active",
            "legendFormat": "Active Connections",
            "refId": "A"
          }
        ],
        "yaxes": [
          {
            "format": "short",
            "logBase": 1,
            "min": 0
          }
        ]
      }
    ]
  }
}
```

---

### 6.3 Application Metrics ダッシュボード

このダッシュボードは、アプリケーション固有のメトリクスを表示します。

**主要パネル**:
- Run実行統計（成功/失敗/実行中）
- モデル別実行時間
- バックエンド別パフォーマンス
- エラー率トレンド
- キュー長推移

---

### 6.4 Model Performance ダッシュボード

このダッシュボードは、機械学習モデルのパフォーマンスを監視します。

**主要パネル**:
- モデル別精度（sMAPE, RMSE, MAE）
- 学習時間トレンド
- 予測レイテンシ
- モデル更新頻度
- 最新モデルの性能比較

---

## 7. トレーシング

### 7.1 分散トレーシングの概要

#### 7.1.1 トレーシング目的

| 目的 | 説明 | ツール |
|-----|------|-------|
| **処理フロー可視化** | リクエストの流れを追跡 | Jaeger |
| **ボトルネック特定** | 遅い処理を発見 | Jaeger |
| **依存関係把握** | サービス間の依存関係 | Jaeger |
| **エラー追跡** | エラーの発生箇所特定 | Jaeger |

---

### 7.2 OpenTelemetry統合

#### 7.2.1 トレーシング設定

```python
# tracing.py

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from typing import Optional
import os


class TracingManager:
    """トレーシング管理"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton パターン"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初期化"""
        if not self._initialized:
            self._setup_tracing()
            self._initialized = True
    
    def _setup_tracing(self):
        """トレーシングをセットアップ"""
        # リソース設定
        resource = Resource(attributes={
            SERVICE_NAME: "nf-auto-runner"
        })
        
        # TracerProvider設定
        provider = TracerProvider(resource=resource)
        
        # Jaeger Exporter設定
        jaeger_host = os.getenv("JAEGER_HOST", "localhost")
        jaeger_port = int(os.getenv("JAEGER_PORT", "6831"))
        
        jaeger_exporter = JaegerExporter(
            agent_host_name=jaeger_host,
            agent_port=jaeger_port,
        )
        
        # SpanProcessor追加
        provider.add_span_processor(
            BatchSpanProcessor(jaeger_exporter)
        )
        
        # グローバルTracerProviderを設定
        trace.set_tracer_provider(provider)
        
        # 自動インストルメンテーション
        RequestsInstrumentor().instrument()
        SQLAlchemyInstrumentor().instrument()
    
    @staticmethod
    def get_tracer(name: str) -> trace.Tracer:
        """
        Tracerを取得
        
        Args:
            name: Tracer名
        
        Returns:
            trace.Tracer
        """
        return trace.get_tracer(name)


# 使用例
from opentelemetry import trace

# トレーシングマネージャー初期化
tracing_manager = TracingManager()

# Tracer取得
tracer = tracing_manager.get_tracer('nf_auto_runner.training')

# スパン作成
with tracer.start_as_current_span('train_model') as span:
    # モデル学習処理
    span.set_attribute('model_name', 'AutoLSTM')
    span.set_attribute('backend', 'optuna')
    span.add_event('Training started')
    
    # ... 学習処理 ...
    
    span.add_event('Training completed')
```

---

### 7.3 カスタムスパン

#### 7.3.1 関数デコレーター

```python
# trace_decorator.py

from opentelemetry import trace
from functools import wraps
from typing import Callable, Any
import time


def trace_function(
    name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None
):
    """
    関数をトレースするデコレーター
    
    Args:
        name: スパン名（Noneの場合は関数名）
        attributes: スパン属性
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            span_name = name or func.__name__
            
            with tracer.start_as_current_span(span_name) as span:
                # 属性を追加
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                
                # 関数引数を記録
                span.set_attribute('function.args', str(args))
                span.set_attribute('function.kwargs', str(kwargs))
                
                # 実行開始イベント
                span.add_event(f'{span_name} started')
                
                start_time = time.time()
                
                try:
                    # 関数実行
                    result = func(*args, **kwargs)
                    
                    # 成功イベント
                    span.add_event(f'{span_name} completed')
                    span.set_attribute('success', True)
                    
                    return result
                
                except Exception as e:
                    # エラー記録
                    span.record_exception(e)
                    span.set_attribute('success', False)
                    span.set_attribute('error.type', type(e).__name__)
                    span.set_attribute('error.message', str(e))
                    
                    raise
                
                finally:
                    # 実行時間記録
                    duration = time.time() - start_time
                    span.set_attribute('duration_seconds', duration)
        
        return wrapper
    return decorator


# 使用例
@trace_function(
    name='train_neural_forecast_model',
    attributes={'component': 'training'}
)
def train_model(model_name: str, data: pd.DataFrame):
    """モデルを学習"""
    # ... 学習処理 ...
    pass
```

---

## 8. 監視ツール設定

### 8.1 Prometheus設定

#### 8.1.1 Prometheus設定ファイル

```yaml
# prometheus/prometheus.yml

global:
  scrape_interval: 1m
  evaluation_interval: 1m
  external_labels:
    cluster: 'production'
    region: 'us-west-1'

# アラートルール読み込み
rule_files:
  - '/etc/prometheus/alerts/*.yml'

# Alert Manager設定
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - 'alertmanager:9093'

# スクレイプ設定
scrape_configs:
  # Prometheus自身
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  # NF Runner アプリケーション
  - job_name: 'nf-runner'
    static_configs:
      - targets: ['nf-runner:9090']
    metric_relabel_configs:
      # 高カーディナリティメトリクスを除外
      - source_labels: [__name__]
        regex: 'nf_.*_bucket'
        action: drop
  
  # Node Exporter (システムメトリクス)
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
  
  # Postgres Exporter (データベースメトリクス)
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
  
  # cAdvisor (コンテナメトリクス)
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
  
  # Blackbox Exporter (死活監視)
  - job_name: 'blackbox'
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
          - http://nf-runner:8000/health
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115

# ストレージ設定
storage:
  tsdb:
    path: /prometheus/data
    retention.time: 30d
    retention.size: 50GB
```

---

### 8.2 Grafana設定

#### 8.2.1 Grafana設定ファイル

```ini
# grafana/grafana.ini

[server]
protocol = http
http_port = 3000
domain = grafana.example.com
root_url = %(protocol)s://%(domain)s:%(http_port)s/
serve_from_sub_path = false

[database]
type = postgres
host = postgres:5432
name = grafana
user = grafana
password = ${GRAFANA_DB_PASSWORD}
ssl_mode = require

[auth]
disable_login_form = false
disable_signout_menu = false

[auth.anonymous]
enabled = false

[security]
admin_user = admin
admin_password = ${GRAFANA_ADMIN_PASSWORD}
secret_key = ${GRAFANA_SECRET_KEY}

[users]
allow_sign_up = false
allow_org_create = false
auto_assign_org = true
auto_assign_org_role = Viewer

[snapshots]
external_enabled = false

[alerting]
enabled = true
execute_alerts = true

[unified_alerting]
enabled = true

[log]
mode = console file
level = info
```

---

#### 8.2.2 Grafanaデータソース設定

```yaml
# grafana/provisioning/datasources/datasource.yml

apiVersion: 1

datasources:
  # Prometheus
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
    jsonData:
      httpMethod: POST
      timeInterval: 1m
  
  # Loki
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    editable: false
    jsonData:
      maxLines: 1000
  
  # Jaeger
  - name: Jaeger
    type: jaeger
    access: proxy
    url: http://jaeger:16686
    editable: false
  
  # PostgreSQL
  - name: PostgreSQL
    type: postgres
    access: proxy
    url: postgres:5432
    database: ts_forecast_system
    user: grafana_readonly
    secureJsonData:
      password: ${POSTGRES_READONLY_PASSWORD}
    jsonData:
      sslmode: require
      maxOpenConns: 10
      maxIdleConns: 10
      connMaxLifetime: 14400
```

---

### 8.3 Loki設定

#### 8.3.1 Loki設定ファイル

```yaml
# loki/loki.yml

auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2023-01-01
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

ruler:
  alertmanager_url: http://alertmanager:9093

# ログの保持期間
limits_config:
  retention_period: 90d
  max_streams_per_user: 0
  max_query_length: 721h
  max_query_parallelism: 16
```

---

### 8.4 Docker Compose設定

#### 8.4.1 監視スタックDocker Compose

```yaml
# docker-compose.monitoring.yml

version: '3.8'

services:
  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    volumes:
      - ./monitoring/prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"
    networks:
      - monitoring
    restart: unless-stopped
  
  # Alert Manager
  alertmanager:
    image: prom/alertmanager:latest
    container_name: alertmanager
    volumes:
      - ./monitoring/alertmanager:/etc/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    ports:
      - "9093:9093"
    networks:
      - monitoring
    restart: unless-stopped
  
  # Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    volumes:
      - ./monitoring/grafana:/etc/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_USER=${GRAFANA_ADMIN_USER}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
    ports:
      - "3000:3000"
    networks:
      - monitoring
    restart: unless-stopped
  
  # Loki
  loki:
    image: grafana/loki:latest
    container_name: loki
    volumes:
      - ./monitoring/loki:/etc/loki
      - loki_data:/loki
    command: -config.file=/etc/loki/loki.yml
    ports:
      - "3100:3100"
    networks:
      - monitoring
    restart: unless-stopped
  
  # Promtail
  promtail:
    image: grafana/promtail:latest
    container_name: promtail
    volumes:
      - ./monitoring/promtail:/etc/promtail
      - /var/log:/var/log:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
    command: -config.file=/etc/promtail/promtail.yml
    networks:
      - monitoring
    restart: unless-stopped
  
  # Jaeger
  jaeger:
    image: jaegertracing/all-in-one:latest
    container_name: jaeger
    environment:
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411
    ports:
      - "5775:5775/udp"
      - "6831:6831/udp"
      - "6832:6832/udp"
      - "5778:5778"
      - "16686:16686"
      - "14268:14268"
      - "14250:14250"
      - "9411:9411"
    networks:
      - monitoring
    restart: unless-stopped
  
  # Node Exporter
  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    command:
      - '--path.rootfs=/host'
    volumes:
      - '/:/host:ro,rslave'
    ports:
      - "9100:9100"
    networks:
      - monitoring
    restart: unless-stopped
  
  # Postgres Exporter
  postgres-exporter:
    image: wrouesnel/postgres_exporter:latest
    container_name: postgres-exporter
    environment:
      - DATA_SOURCE_NAME=postgresql://exporter:${POSTGRES_EXPORTER_PASSWORD}@postgres:5432/ts_forecast_system?sslmode=require
    ports:
      - "9187:9187"
    networks:
      - monitoring
    restart: unless-stopped
  
  # cAdvisor
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    ports:
      - "8080:8080"
    networks:
      - monitoring
    restart: unless-stopped

networks:
  monitoring:
    driver: bridge

volumes:
  prometheus_data:
  grafana_data:
  loki_data:
```

---

## 9. 運用監視手順

### 9.1 日次監視チェックリスト

#### 9.1.1 朝のチェック（毎日9:00）

```markdown
## 日次監視チェックリスト

### システムヘルス
- [ ] Grafanaダッシュボード確認
  - System Overview: 稼働率、リソース使用状況
  - Active Runs: 実行中Run数が正常範囲内か
  - Error Rate: 過去24時間のエラー率 <10%

### アラート確認
- [ ] Alert Manager確認
  - 未解決のCriticalアラートがないか
  - 繰り返し発生しているアラートがないか

### ログ確認
- [ ] エラーログレビュー
  - CRITICALレベルのログがないか
  - ERROR頻度の異常な増加がないか

### リソース確認
- [ ] システムリソース
  - CPU使用率 <80%
  - メモリ使用率 <80%
  - ディスク使用率 <85%
  - GPU使用率（GPUがある場合）

### データベース確認
- [ ] PostgreSQL状態
  - 接続数が正常範囲内か
  - クエリパフォーマンスの劣化がないか
  - ディスク容量が十分か

### バックアップ確認
- [ ] 前日のバックアップが成功したか
- [ ] バックアップファイルのサイズが正常か

### ビジネスKPI
- [ ] 前日のRun実行数が通常範囲内か
- [ ] 前日の成功率が95%以上か
```

---

### 9.2 週次監視タスク

#### 9.2.1 週次レビュー（毎週月曜10:00）

```markdown
## 週次監視タスク

### パフォーマンストレンド分析
- [ ] 過去1週間の学習時間トレンド確認
- [ ] 過去1週間の予測レイテンシトレンド確認
- [ ] リソース使用率のピーク時間帯特定

### エラー分析
- [ ] 週次エラー統計レビュー
  - エラータイプ別集計
  - エラー発生パターン分析
  - 再発防止策検討

### モデルパフォーマンス
- [ ] 週次平均精度の確認
- [ ] モデル別パフォーマンス比較
- [ ] パフォーマンス劣化の兆候検出

### キャパシティプランニング
- [ ] リソース使用傾向の分析
- [ ] 今後2週間の需要予測
- [ ] スケーリング必要性の評価

### セキュリティ
- [ ] アクセスログレビュー
- [ ] 異常なアクセスパターンの検出
- [ ] 脆弱性スキャン結果確認

### メンテナンス
- [ ] ログローテーション実行確認
- [ ] データベースVACUUM実行確認
- [ ] 古いログファイルのアーカイブ

### ドキュメント更新
- [ ] 運用ログの更新
- [ ] インシデントレポートの作成（必要な場合）
- [ ] ナレッジベースの更新
```

---

### 9.3 月次監視タスク

#### 9.3.1 月次レビュー（毎月1日）

```markdown
## 月次監視タスク

### SLO/SLI レビュー
- [ ] 月間稼働率の計算と評価
- [ ] SLO達成状況の確認
- [ ] SLO未達成の場合の原因分析

### 容量管理
- [ ] ディスク容量トレンド分析
- [ ] データベースサイズ増加率確認
- [ ] ストレージ拡張計画の見直し

### コスト分析
- [ ] 月次運用コストの集計
- [ ] リソース使用効率の評価
- [ ] コスト最適化機会の特定

### バックアップ検証
- [ ] バックアップからの復旧テスト
- [ ] バックアップ完全性の検証
- [ ] リカバリ手順の見直し

### セキュリティ監査
- [ ] 月次セキュリティログレビュー
- [ ] アクセス権限の棚卸し
- [ ] セキュリティパッチ適用状況確認

### 依存関係更新
- [ ] Pythonパッケージの脆弱性チェック
- [ ] 重要なセキュリティアップデートの適用
- [ ] 依存関係の最新化

### パフォーマンス最適化
- [ ] ボトルネック分析
- [ ] クエリ最適化機会の特定
- [ ] キャッシュ戦略の見直し

### レポート作成
- [ ] 月次運用レポート作成
- [ ] 経営層向けサマリー作成
- [ ] 改善提案のドキュメント化
```

---

## 10. トラブルシューティング

### 10.1 一般的な問題と対処法

#### 10.1.1 システムダウン

**症状**: アプリケーションが応答しない

**診断手順**:
1. プロセス確認
```bash
ps aux | grep nf-runner
systemctl status nf-runner
```

2. ログ確認
```bash
tail -100 /var/log/nf-runner/error.log
journalctl -u nf-runner -n 100
```

3. リソース確認
```bash
top
free -h
df -h
```

**対処法**:
```bash
# 1. プロセス再起動
systemctl restart nf-runner

# 2. 設定ファイル確認
cat /etc/nf-runner/config.yml

# 3. データベース接続確認
psql -U postgres -d ts_forecast_system -c "SELECT 1"

# 4. 依存サービス確認
systemctl status postgresql
systemctl status prometheus
```

---

#### 10.1.2 高メモリ使用率

**症状**: メモリ使用率が90%以上

**診断手順**:
1. メモリ使用状況確認
```bash
free -h
ps aux --sort=-%mem | head -20
```

2. アプリケーションメモリ確認
```python
import psutil

process = psutil.Process()
print(f"Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB")
```

3. Prometheusメトリクス確認
```promql
process_resident_memory_bytes{job="nf-runner"}
```

**対処法**:
```bash
# 1. 不要なプロセス終了
pkill -f "old_process"

# 2. アプリケーション再起動
systemctl restart nf-runner

# 3. メモリリーク調査
# メモリプロファイリングツールを使用
python -m memory_profiler script.py

# 4. スワップ使用状況確認
swapon --show
```

---

#### 10.1.3 高エラー率

**症状**: エラー率が10%を超える

**診断手順**:
1. エラーログ確認
```bash
grep ERROR /var/log/nf-runner/app.log | tail -100
```

2. エラータイプ別集計
```bash
grep ERROR /var/log/nf-runner/app.log | \
  jq -r '.error_type' | \
  sort | uniq -c | sort -rn
```

3. Prometheusメトリクス確認
```promql
sum(rate(nf_errors_total[5m])) by (error_type)
```

**対処法**:
```bash
# 1. データ検証
python -m nf_auto_runner.utils.data_validator

# 2. 設定確認
python -m nf_auto_runner.utils.config_validator

# 3. データベース接続確認
psql -U postgres -d ts_forecast_system -c "SELECT version()"

# 4. 詳細ログ有効化
# config.ymlでlog_levelをDEBUGに変更
```

---

#### 10.1.4 遅い実行時間

**症状**: 学習時間が通常の2倍以上

**診断手順**:
1. CPU/GPU使用率確認
```bash
top
nvidia-smi  # GPUがある場合
```

2. I/O待ち確認
```bash
iostat -x 1
```

3. トレース確認（Jaeger）
- Jaeger UIで遅いスパンを特定

4. プロファイリング
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# ... 処理 ...

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

**対処法**:
```bash
# 1. 並列実行数調整
# config.ymlでmax_parallel_runsを調整

# 2. データサイズ確認
SELECT COUNT(*) FROM time_series_data;

# 3. データベースインデックス確認
\d+ time_series_data

# 4. キャッシュクリア
python -m nf_auto_runner.utils.cache_cleaner
```

---

### 10.2 アラート対応フローチャート

```mermaid
graph TD
    A[アラート受信] --> B{重要度は?}
    
    B -->|Critical| C[即座に対応開始]
    B -->|High| D[2時間以内に対応]
    B -->|Medium| E[翌営業日に確認]
    
    C --> F[ダッシュボード確認]
    D --> F
    E --> F
    
    F --> G[ログ確認]
    G --> H[メトリクス分析]
    H --> I{原因特定?}
    
    I -->|Yes| J[対処実施]
    I -->|No| K[エスカレーション]
    
    J --> L{解決?}
    L -->|Yes| M[アラート解除]
    L -->|No| K
    
    K --> N[上位者に連絡]
    N --> O[詳細調査]
    O --> J
    
    M --> P[事後レポート作成]
    P --> Q[ナレッジベース更新]
    Q --> R[完了]
```

---

### 10.3 デバッグコマンド集

#### 10.3.1 システム診断

```bash
#!/bin/bash
# system_diagnostic.sh

echo "=== System Diagnostic ==="
echo ""

# システム情報
echo "--- System Information ---"
uname -a
uptime

# CPU情報
echo ""
echo "--- CPU Usage ---"
top -bn1 | grep "Cpu(s)"

# メモリ情報
echo ""
echo "--- Memory Usage ---"
free -h

# ディスク情報
echo ""
echo "--- Disk Usage ---"
df -h

# プロセス情報
echo ""
echo "--- NF Runner Process ---"
ps aux | grep nf-runner | grep -v grep

# ネットワーク情報
echo ""
echo "--- Network Connections ---"
netstat -tuln | grep -E ':(8000|9090|5432)'

# データベース接続
echo ""
echo "--- Database Connection ---"
psql -U postgres -d ts_forecast_system -c "SELECT version();"

# Prometheusメトリクス
echo ""
echo "--- Prometheus Metrics ---"
curl -s http://localhost:9090/api/v1/query?query=up | jq '.data.result'

echo ""
echo "=== Diagnostic Complete ==="
```

---

## 11. ベストプラクティス

### 11.1 監視のベストプラクティス

#### 11.1.1 The Four Golden Signals

常に以下の4つの指標を監視:

1. **Latency** (レイテンシ)
   - 学習時間、予測時間の分布（p50, p95, p99）
   - 目標: p95 < 10秒

2. **Traffic** (トラフィック)
   - 実行中Run数、API QPS
   - 目標: 安定した処理量

3. **Errors** (エラー)
   - 失敗Run率
   - 目標: <10%

4. **Saturation** (飽和度)
   - CPU/メモリ/ディスク使用率
   - 目標: <80%

---

#### 11.1.2 アラート設計原則

**Good Alert**:
- ✅ 実際の問題を示す
- ✅ 対応可能である
- ✅ 緊急性が明確
- ✅ 対処法が明確

**Bad Alert**:
- ❌ ノイズが多い
- ❌ 対応不可能
- ❌ 誤検知が多い
- ❌ 対処法が不明

---

#### 11.1.3 ダッシュボード設計原則

1. **階層化**
   - Overview → Detail → Debug
   - トップレベルは全体像を1画面で

2. **標準化**
   - 同じメトリクスは同じ色
   - 閾値は明示的に表示

3. **アクション可能性**
   - 問題発見 → 原因特定 → 対処
   - 関連ダッシュボードへのリンク

---

### 11.2 ロギングのベストプラクティス

#### 11.2.1 ログレベルの使い分け

```python
# 良い例
logger.debug(f"Processing item {item_id}")  # 開発時のみ
logger.info(f"Model training started: {model_name}")  # 正常動作
logger.warning(f"Memory usage high: {memory_percent}%")  # 警告
logger.error(f"Model training failed: {error}")  # エラー
logger.critical(f"Database connection lost")  # クリティカル

# 悪い例
logger.info("Error occurred")  # エラーなのにINFO
logger.error("Processing started")  # 正常動作なのにERROR
```

---

#### 11.2.2 構造化ロギング

```python
# 良い例: 構造化
logger.info(
    'model_training_completed',
    run_id='abc123',
    model_name='AutoLSTM',
    duration_seconds=245.3,
    accuracy=0.92
)

# 悪い例: 非構造化
logger.info(
    f"Training completed for AutoLSTM in 245.3 seconds with accuracy 0.92"
)
```

---

### 11.3 メトリクスのベストプラクティス

#### 11.3.1 メトリクス命名規則

```python
# 良い例
training_duration_seconds  # 単位が明確
http_requests_total  # totalサフィックス
memory_usage_bytes  # 単位が明確

# 悪い例
training_time  # 単位不明
requests  # 累積か現在値か不明
memory  # 単位不明
```

---

#### 11.3.2 カーディナリティ管理

```python
# 良い例: 低カーディナリティ
model_type = Gauge(
    'model_type',
    'Model type',
    ['model_family']  # 'AutoLSTM', 'AutoNHITS' など数種類
)

# 悪い例: 高カーディナリティ
model_id = Gauge(
    'model_id',
    'Model ID',
    ['run_id']  # 無限に増える可能性
)
```

---

## 12. 付録

### 12.1 用語集

| 用語 | 説明 |
|-----|------|
| **SLO** | Service Level Objective - サービスレベル目標 |
| **SLI** | Service Level Indicator - サービスレベル指標 |
| **MTBF** | Mean Time Between Failures - 平均故障間隔 |
| **MTTR** | Mean Time To Repair - 平均修復時間 |
| **MTTD** | Mean Time To Detect - 平均検出時間 |
| **RTO** | Recovery Time Objective - 目標復旧時間 |
| **RPO** | Recovery Point Objective - 目標復旧時点 |
| **p50/p95/p99** | パーセンタイル（中央値/95パーセンタイル/99パーセンタイル） |

---

### 12.2 参考資料

#### 12.2.1 公式ドキュメント

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)

---

#### 12.2.2 書籍

- **Site Reliability Engineering** - Google
- **The Art of Monitoring** - James Turnbull
- **Distributed Systems Observability** - Cindy Sridharan

---

#### 12.2.3 関連ドキュメント

- 📄 `00_INTEGRATED_DESIGN_OVERVIEW.md` - 統合設計概要
- 📄 `02_NON_FUNCTIONAL_REQUIREMENTS.md` - 非機能要件
- 📄 `03_ARCHITECTURE_DESIGN_DETAILED.md` - アーキテクチャ設計
- 📄 `09_TESTING_STRATEGY.md` - テスト戦略
- 📄 `10_DEPLOYMENT_GUIDE.md` - デプロイガイド
- 📄 `11_OPERATIONS_RUNBOOK.md` - 運用手順書

---

### 12.3 監視チェックリスト

#### 12.3.1 初期セットアップチェックリスト

```markdown
## 監視システムセットアップチェックリスト

### Prometheus
- [ ] Prometheus設定ファイル作成
- [ ] スクレイプ対象の設定
- [ ] アラートルールの作成
- [ ] ストレージ保持期間の設定
- [ ] Alert Manager連携設定

### Grafana
- [ ] Grafana設定ファイル作成
- [ ] データソース設定
- [ ] ダッシュボードのインポート
- [ ] ユーザー権限の設定
- [ ] アラート通知の設定

### Alert Manager
- [ ] Alert Manager設定ファイル作成
- [ ] 受信者の設定
- [ ] 通知チャネルの設定（Email, Slack）
- [ ] ルーティングルールの設定
- [ ] 抑制ルールの設定

### Loki
- [ ] Loki設定ファイル作成
- [ ] ログ保持期間の設定
- [ ] Promtail設定
- [ ] ログラベルの設定

### Application Instrumentation
- [ ] Prometheusクライアントの統合
- [ ] 構造化ロギングの実装
- [ ] トレーシングの実装
- [ ] メトリクスエクスポーターの起動

### Testing
- [ ] メトリクス収集の動作確認
- [ ] ログ転送の動作確認
- [ ] アラート発火のテスト
- [ ] ダッシュボード表示の確認

### Documentation
- [ ] 監視ドキュメントの作成
- [ ] Runbookの作成
- [ ] アラート対応手順の作成
- [ ] トラブルシューティングガイドの作成
```

---

## ✨ まとめ

本監視ガイドは、時系列予測システムの包括的な監視戦略を提供します。

### 監視の重要ポイント

- ✅ **3つの柱**: Metrics, Logs, Traces の統合
- ✅ **4つのGolden Signals**: Latency, Traffic, Errors, Saturation
- ✅ **階層的監視**: インフラ → プラットフォーム → アプリケーション → ビジネス
- ✅ **プロアクティブな対応**: 予防的な監視とアラート
- ✅ **自動化**: 監視・アラート・対応の自動化

### 監視システムの成功要因

1. **明確なSLO/SLI**: 測定可能な目標設定
2. **適切なアラート**: ノイズを減らし、実際の問題に集中
3. **包括的なダッシュボード**: 全体像から詳細まで
4. **効率的なトラブルシューティング**: 迅速な原因特定と対応
5. **継続的な改善**: 監視システム自体の改善

### 次のステップ

1. ✅ **本監視ガイドを読了**
2. 🔧 監視スタックのセットアップ
   - Prometheus, Grafana, Loki, Jaeger
3. 📊 ダッシュボードの作成
   - System Overview, Application Metrics など
4. 🚨 アラートの設定
   - Critical, High, Medium アラート
5. 📝 運用手順の確立
   - 日次/週次/月次チェックリスト
6. 🔄 継続的な改善
   - メトリクス追加、アラート調整、ダッシュボード改善

---

**Observe, Alert, Act - Build Reliable Systems! 📊🚨🔧**

---
**End of Document**
