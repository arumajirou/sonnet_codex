"""Execution configuration for controlling runtime behaviour."""

from __future__ import annotations

import multiprocessing
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, TypeVar

from .base import Config

_TRUE_VALUES = {"1", "true", "yes", "on"}
E = TypeVar("E", bound=Enum)


def _parse_bool(value: Any) -> bool:
    """Convert diverse truthy representations into a boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in _TRUE_VALUES
    raise TypeError(f"Cannot interpret {value!r} as boolean.")


def _parse_optional_float(value: Any) -> float | None:
    """Parse optional float values allowing empty strings."""
    if value is None:
        return None
    if isinstance(value, (float, int)):
        return float(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        return float(stripped)
    raise TypeError(f"Cannot interpret {value!r} as float.")


def _parse_gpu_devices(value: Any) -> tuple[int, ...] | None:
    """Parse GPU device identifiers from strings, lists or tuples."""
    if value is None:
        return None
    if isinstance(value, str):
        tokens = [token.strip() for token in value.split(",") if token.strip()]
        if not tokens:
            return None
        return tuple(int(token) for token in tokens)
    if isinstance(value, (list, tuple)):
        return tuple(int(token) for token in value)
    raise TypeError(f"Cannot interpret {value!r} as GPU devices.")


def _parse_enum(enum_cls: type[E], value: Any, field_name: str) -> E:
    """Parse enum members from strings while accepting existing members."""
    if isinstance(value, enum_cls):
        return value
    if isinstance(value, str):
        normalised = value.strip().lower()
        for member in enum_cls:
            if member.value == normalised:
                return member
    raise ValueError(f"Invalid {field_name}: {value!r}")


class ExecutionMode(Enum):
    """Supported execution environments."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class ParallelBackend(Enum):
    """Parallel execution backends."""

    SEQUENTIAL = "sequential"
    THREADING = "threading"
    MULTIPROCESSING = "multiprocessing"
    DASK = "dask"
    RAY = "ray"


@dataclass(frozen=True)
class ExecutionConfig(Config):
    """Runtime configuration describing execution characteristics."""

    mode: ExecutionMode
    n_workers: int
    backend: ParallelBackend
    max_memory_gb: float | None
    use_gpu: bool
    gpu_devices: tuple[int, ...] | None
    timeout_seconds: int
    max_retries: int
    log_level: str
    debug: bool
    random_seed: int

    def __post_init__(self) -> None:
        """Normalise derived attributes for consistent behaviour."""
        object.__setattr__(self, "log_level", self.log_level.upper())
        normalised_devices = _parse_gpu_devices(self.gpu_devices)
        object.__setattr__(self, "gpu_devices", normalised_devices)

    @classmethod
    def from_env(cls) -> ExecutionConfig:
        """Construct configuration from environment variables."""
        mode = _parse_enum(
            ExecutionMode, os.getenv("EXECUTION_MODE", "development"), "mode"
        )
        backend = _parse_enum(
            ParallelBackend, os.getenv("PARALLEL_BACKEND", "multiprocessing"), "backend"
        )
        n_workers = int(os.getenv("N_WORKERS", str(multiprocessing.cpu_count())))
        max_memory_gb = _parse_optional_float(os.getenv("MAX_MEMORY_GB"))
        use_gpu = _parse_bool(os.getenv("USE_GPU", "false"))
        gpu_devices = _parse_gpu_devices(os.getenv("GPU_DEVICES"))
        timeout_seconds = int(os.getenv("TIMEOUT_SECONDS", "3600"))
        max_retries = int(os.getenv("MAX_RETRIES", "3"))
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        debug = _parse_bool(os.getenv("DEBUG", "false"))
        random_seed = int(os.getenv("RANDOM_SEED", "42"))

        return cls(
            mode=mode,
            n_workers=n_workers,
            backend=backend,
            max_memory_gb=max_memory_gb,
            use_gpu=use_gpu,
            gpu_devices=gpu_devices,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            log_level=log_level,
            debug=debug,
            random_seed=random_seed,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExecutionConfig:
        """Construct configuration from dictionary data."""
        mode = _parse_enum(
            ExecutionMode, data.get("mode", ExecutionMode.DEVELOPMENT), "mode"
        )
        backend = _parse_enum(
            ParallelBackend,
            data.get("backend", ParallelBackend.MULTIPROCESSING),
            "backend",
        )
        n_workers = int(data.get("n_workers", multiprocessing.cpu_count()))
        max_memory_gb = _parse_optional_float(data.get("max_memory_gb"))
        use_gpu = _parse_bool(data.get("use_gpu", False))
        gpu_devices = _parse_gpu_devices(data.get("gpu_devices"))
        timeout_seconds = int(data.get("timeout_seconds", 3600))
        max_retries = int(data.get("max_retries", 3))
        log_level_raw = data.get("log_level", "INFO")
        if not isinstance(log_level_raw, str):
            raise TypeError("log_level must be a string.")
        debug = _parse_bool(data.get("debug", False))
        random_seed = int(data.get("random_seed", 42))

        return cls(
            mode=mode,
            n_workers=n_workers,
            backend=backend,
            max_memory_gb=max_memory_gb,
            use_gpu=use_gpu,
            gpu_devices=gpu_devices,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            log_level=log_level_raw,
            debug=debug,
            random_seed=random_seed,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialise configuration into JSON-friendly dictionary."""
        return {
            "mode": self.mode.value,
            "n_workers": self.n_workers,
            "backend": self.backend.value,
            "max_memory_gb": self.max_memory_gb,
            "use_gpu": self.use_gpu,
            "gpu_devices": (
                list(self.gpu_devices) if self.gpu_devices is not None else None
            ),
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "log_level": self.log_level,
            "debug": self.debug,
            "random_seed": self.random_seed,
        }

    def validate(self) -> None:
        """Validate configuration values for runtime safety."""
        if self.n_workers <= 0:
            raise ValueError(f"n_workers must be > 0, got {self.n_workers}")

        if self.max_memory_gb is not None and self.max_memory_gb <= 0:
            raise ValueError(f"max_memory_gb must be > 0, got {self.max_memory_gb}")

        if self.timeout_seconds <= 0:
            raise ValueError(f"timeout_seconds must be > 0, got {self.timeout_seconds}")

        if self.max_retries < 0:
            raise ValueError(f"max_retries must be >= 0, got {self.max_retries}")

        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR"}
        if self.log_level.upper() not in valid_log_levels:
            raise ValueError(
                f"log_level must be one of {valid_log_levels}, got {self.log_level}"
            )

        if self.random_seed < 0:
            raise ValueError(f"random_seed must be >= 0, got {self.random_seed}")

    def is_production(self) -> bool:
        """Return True when running in production mode."""
        return self.mode is ExecutionMode.PRODUCTION

    def get_worker_count(self) -> int:
        """Return effective worker count constrained by system resources."""
        return min(self.n_workers, max(1, multiprocessing.cpu_count()))
