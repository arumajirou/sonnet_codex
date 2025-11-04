"""Tests for ExecutionConfig covering environment parsing and validation."""

from __future__ import annotations

import multiprocessing
from pathlib import Path
import sys
from typing import Dict

import pytest

ROOT_DIR = Path(__file__).resolve().parents[3]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from nf_auto_runner.config.execution import (  # noqa: E402
    ExecutionConfig,
    ExecutionMode,
    ParallelBackend,
)


class TestExecutionConfig:
    """ExecutionConfig behavioural tests."""

    def setup_method(self) -> None:
        """Store the original cpu_count for restoration."""
        self._original_cpu_count = multiprocessing.cpu_count

    def teardown_method(self) -> None:
        """Restore multiprocessing.cpu_count."""
        multiprocessing.cpu_count = self._original_cpu_count

    def test_from_env_default_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Environment defaults should match documented configuration values."""
        for var_name in [
            "EXECUTION_MODE",
            "N_WORKERS",
            "PARALLEL_BACKEND",
            "MAX_MEMORY_GB",
            "USE_GPU",
            "GPU_DEVICES",
            "TIMEOUT_SECONDS",
            "MAX_RETRIES",
            "LOG_LEVEL",
            "DEBUG",
            "RANDOM_SEED",
        ]:
            monkeypatch.delenv(var_name, raising=False)

        cpu_count = multiprocessing.cpu_count()
        config = ExecutionConfig.from_env()

        assert config.mode == ExecutionMode.DEVELOPMENT
        assert config.n_workers == cpu_count
        assert config.backend == ParallelBackend.MULTIPROCESSING
        assert config.max_memory_gb is None
        assert config.use_gpu is False
        assert config.gpu_devices is None
        assert config.timeout_seconds == 3600
        assert config.max_retries == 3
        assert config.log_level == "INFO"
        assert config.debug is False
        assert config.random_seed == 42

    def test_from_env_custom_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Custom environment overrides should populate the dataclass."""
        monkeypatch.setenv("EXECUTION_MODE", "production")
        monkeypatch.setenv("N_WORKERS", "8")
        monkeypatch.setenv("PARALLEL_BACKEND", "ray")
        monkeypatch.setenv("MAX_MEMORY_GB", "64.5")
        monkeypatch.setenv("USE_GPU", "true")
        monkeypatch.setenv("GPU_DEVICES", "0, 2,3")
        monkeypatch.setenv("TIMEOUT_SECONDS", "7200")
        monkeypatch.setenv("MAX_RETRIES", "5")
        monkeypatch.setenv("LOG_LEVEL", "warning")
        monkeypatch.setenv("DEBUG", "1")
        monkeypatch.setenv("RANDOM_SEED", "1234")

        config = ExecutionConfig.from_env()

        assert config.mode == ExecutionMode.PRODUCTION
        assert config.n_workers == 8
        assert config.backend == ParallelBackend.RAY
        assert config.max_memory_gb == pytest.approx(64.5)
        assert config.use_gpu is True
        assert config.gpu_devices == (0, 2, 3)
        assert config.timeout_seconds == 7200
        assert config.max_retries == 5
        assert config.log_level == "WARNING"
        assert config.debug is True
        assert config.random_seed == 1234

    def test_validate_valid_config(self) -> None:
        """validate should no-op for a properly populated configuration."""
        config = ExecutionConfig(
            mode=ExecutionMode.STAGING,
            n_workers=4,
            backend=ParallelBackend.THREADING,
            max_memory_gb=32.0,
            use_gpu=True,
            gpu_devices=(0,),
            timeout_seconds=1800,
            max_retries=2,
            log_level="INFO",
            debug=False,
            random_seed=7,
        )

        config.validate()  # Should not raise.

    def test_validate_invalid_n_workers(self) -> None:
        """n_workers <= 0 should raise ValueError."""
        config = ExecutionConfig(
            mode=ExecutionMode.DEVELOPMENT,
            n_workers=0,
            backend=ParallelBackend.SEQUENTIAL,
            max_memory_gb=None,
            use_gpu=False,
            gpu_devices=None,
            timeout_seconds=100,
            max_retries=1,
            log_level="INFO",
            debug=False,
            random_seed=5,
        )

        with pytest.raises(ValueError, match="n_workers"):
            config.validate()

    def test_validate_invalid_memory(self) -> None:
        """max_memory_gb <= 0 should raise ValueError."""
        config = ExecutionConfig(
            mode=ExecutionMode.DEVELOPMENT,
            n_workers=2,
            backend=ParallelBackend.SEQUENTIAL,
            max_memory_gb=0.0,
            use_gpu=False,
            gpu_devices=None,
            timeout_seconds=100,
            max_retries=1,
            log_level="INFO",
            debug=False,
            random_seed=5,
        )

        with pytest.raises(ValueError, match="max_memory_gb"):
            config.validate()

    def test_validate_invalid_log_level(self) -> None:
        """Unexpected log level strings should be rejected."""
        config = ExecutionConfig(
            mode=ExecutionMode.DEVELOPMENT,
            n_workers=2,
            backend=ParallelBackend.SEQUENTIAL,
            max_memory_gb=None,
            use_gpu=False,
            gpu_devices=None,
            timeout_seconds=100,
            max_retries=1,
            log_level="TRACE",
            debug=False,
            random_seed=5,
        )

        with pytest.raises(ValueError, match="log_level"):
            config.validate()

    def test_is_production_true(self) -> None:
        """is_production should return True only for production mode."""
        config = ExecutionConfig(
            mode=ExecutionMode.PRODUCTION,
            n_workers=4,
            backend=ParallelBackend.MULTIPROCESSING,
            max_memory_gb=None,
            use_gpu=False,
            gpu_devices=None,
            timeout_seconds=100,
            max_retries=1,
            log_level="INFO",
            debug=False,
            random_seed=5,
        )

        assert config.is_production() is True

    def test_is_production_false(self) -> None:
        """Non-production modes should return False."""
        config = ExecutionConfig(
            mode=ExecutionMode.STAGING,
            n_workers=4,
            backend=ParallelBackend.MULTIPROCESSING,
            max_memory_gb=None,
            use_gpu=False,
            gpu_devices=None,
            timeout_seconds=100,
            max_retries=1,
            log_level="INFO",
            debug=False,
            random_seed=5,
        )

        assert config.is_production() is False

    def test_get_worker_count_respects_limit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_worker_count should cap the value at cpu_count."""
        monkeypatch.setenv("N_WORKERS", "16")
        monkeypatch.setenv("PARALLEL_BACKEND", "multiprocessing")

        def fake_cpu_count() -> int:
            return 6

        monkeypatch.setenv("EXECUTION_MODE", "staging")
        monkeypatch.setenv("TIMEOUT_SECONDS", "100")
        monkeypatch.setenv("MAX_RETRIES", "1")
        monkeypatch.setenv("LOG_LEVEL", "INFO")
        monkeypatch.setenv("RANDOM_SEED", "10")
        multiprocessing.cpu_count = fake_cpu_count

        config = ExecutionConfig.from_env()

        assert config.n_workers == 16
        assert config.get_worker_count() == 6

    def test_to_dict_includes_all_fields(self) -> None:
        """to_dict should include serialisable values for every field."""
        config = ExecutionConfig(
            mode=ExecutionMode.STAGING,
            n_workers=3,
            backend=ParallelBackend.THREADING,
            max_memory_gb=12.5,
            use_gpu=True,
            gpu_devices=(1, 2),
            timeout_seconds=450,
            max_retries=2,
            log_level="DEBUG",
            debug=True,
            random_seed=9,
        )

        config_dict: Dict[str, object] = config.to_dict()

        assert config_dict["mode"] == "staging"
        assert config_dict["n_workers"] == 3
        assert config_dict["backend"] == "threading"
        assert config_dict["max_memory_gb"] == pytest.approx(12.5)
        assert config_dict["use_gpu"] is True
        assert config_dict["gpu_devices"] == [1, 2]
        assert config_dict["timeout_seconds"] == 450
        assert config_dict["max_retries"] == 2
        assert config_dict["log_level"] == "DEBUG"
        assert config_dict["debug"] is True
        assert config_dict["random_seed"] == 9

    def test_from_json_file_round_trip(self, tmp_path: Path) -> None:
        """Persisting to JSON and reloading should retain values and enums."""
        config = ExecutionConfig(
            mode=ExecutionMode.STAGING,
            n_workers=5,
            backend=ParallelBackend.DASK,
            max_memory_gb=24.0,
            use_gpu=False,
            gpu_devices=None,
            timeout_seconds=600,
            max_retries=3,
            log_level="WARNING",
            debug=False,
            random_seed=21,
        )

        json_path = tmp_path / "execution_config.json"
        config.save_to_file(json_path)

        reloaded = ExecutionConfig.from_json_file(json_path)

        assert reloaded == config
        assert isinstance(reloaded.mode, ExecutionMode)
        assert isinstance(reloaded.backend, ParallelBackend)

    def test_gpu_devices_is_immutable_tuple(self) -> None:
        """gpu_devices should be a tuple and disallow item assignment."""
        config = ExecutionConfig(
            mode=ExecutionMode.STAGING,
            n_workers=2,
            backend=ParallelBackend.THREADING,
            max_memory_gb=None,
            use_gpu=True,
            gpu_devices=(0, 1),
            timeout_seconds=100,
            max_retries=1,
            log_level="INFO",
            debug=False,
            random_seed=5,
        )

        assert isinstance(config.gpu_devices, tuple)
        with pytest.raises(TypeError):
            config.gpu_devices[0] = 2
