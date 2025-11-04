"""Execution configuration describing runtime behaviour."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from .base import Config

_DEFAULTS: dict[str, Any] = {
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
}

_TRUE_VALUES = {"1", "true", "yes", "on"}
_VALID_ACCELERATORS = {"auto", "cpu", "cuda", "mps", "tpu"}
_VALID_PRECISIONS = {"32", "16", "bf16"}


def _parse_bool(value: Any, field_name: str) -> bool:
    """Convert diverse truthy representations into a boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in _TRUE_VALUES
    raise TypeError(f"{field_name} must be castable to bool, got {value!r}.")


def _parse_int(value: Any, field_name: str) -> int:
    """Parse integer values while raising descriptive errors."""
    try:
        if isinstance(value, bool):
            raise TypeError
        return int(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{field_name} must be an integer, got {value!r}.") from exc


def _parse_float(value: Any, field_name: str) -> float:
    """Parse float values while raising descriptive errors."""
    try:
        if isinstance(value, bool):
            raise TypeError
        return float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{field_name} must be a float, got {value!r}.") from exc


def _parse_h_ratio(value: Any) -> float:
    """Parse forecasting horizon ratio."""
    parsed = _parse_float(value, "h_ratio")
    return parsed


def _normalise_precision(value: Any) -> str:
    """Normalise precision values into canonical string representation."""
    if isinstance(value, str):
        return value.strip().lower()
    return str(value).lower()


def _normalise_accelerator(value: Any) -> str:
    """Normalise accelerator names to lower-case strings."""
    if isinstance(value, str):
        return value.strip().lower()
    return str(value).lower()


@dataclass(frozen=True)
class ExecutionConfig(Config):
    """Runtime configuration describing execution characteristics."""

    random_state: int
    trial_num_samples: int
    trial_max_steps: int
    default_h: int
    h_ratio: float
    max_workers: int
    allow_ray_parallel: bool
    save_model: bool
    overwrite_model: bool
    dir_tokens_maxlen: int
    max_exog_futr: int
    max_exog_hist: int
    max_exog_stat: int
    early_stopping_patience: int
    gradient_clip_val: float
    accelerator: str
    devices: int
    precision: str

    def __post_init__(self) -> None:
        """Normalise derived attributes for consistent behaviour."""
        accelerator = _normalise_accelerator(self.accelerator)
        precision = _normalise_precision(self.precision)
        object.__setattr__(self, "accelerator", accelerator)
        object.__setattr__(self, "precision", precision)

    @classmethod
    def _merge_defaults(cls, overrides: dict[str, Any]) -> dict[str, Any]:
        """Merge overrides with class defaults."""
        payload = {**_DEFAULTS, **(overrides or {})}
        return payload

    @classmethod
    def from_env(cls) -> ExecutionConfig:
        """Construct configuration from environment variables."""
        env_payload: dict[str, Any] = {
            "random_state": os.getenv("RANDOM_STATE", _DEFAULTS["random_state"]),
            "trial_num_samples": os.getenv(
                "TRIAL_NUM_SAMPLES", _DEFAULTS["trial_num_samples"]
            ),
            "trial_max_steps": os.getenv(
                "TRIAL_MAX_STEPS", _DEFAULTS["trial_max_steps"]
            ),
            "default_h": os.getenv("DEFAULT_H", _DEFAULTS["default_h"]),
            "h_ratio": os.getenv("H_RATIO", _DEFAULTS["h_ratio"]),
            "max_workers": os.getenv("MAX_WORKERS", _DEFAULTS["max_workers"]),
            "allow_ray_parallel": os.getenv(
                "ALLOW_RAY_PARALLEL", str(_DEFAULTS["allow_ray_parallel"]).lower()
            ),
            "save_model": os.getenv("SAVE_MODEL", str(_DEFAULTS["save_model"]).lower()),
            "overwrite_model": os.getenv(
                "OVERWRITE_MODEL", str(_DEFAULTS["overwrite_model"]).lower()
            ),
            "dir_tokens_maxlen": os.getenv(
                "DIR_TOKENS_MAXLEN", _DEFAULTS["dir_tokens_maxlen"]
            ),
            "max_exog_futr": os.getenv("MAX_EXOG_FUTR", _DEFAULTS["max_exog_futr"]),
            "max_exog_hist": os.getenv("MAX_EXOG_HIST", _DEFAULTS["max_exog_hist"]),
            "max_exog_stat": os.getenv("MAX_EXOG_STAT", _DEFAULTS["max_exog_stat"]),
            "early_stopping_patience": os.getenv(
                "EARLY_STOPPING_PATIENCE", _DEFAULTS["early_stopping_patience"]
            ),
            "gradient_clip_val": os.getenv(
                "GRADIENT_CLIP_VAL", _DEFAULTS["gradient_clip_val"]
            ),
            "accelerator": os.getenv("ACCELERATOR", _DEFAULTS["accelerator"]),
            "devices": os.getenv("DEVICES", _DEFAULTS["devices"]),
            "precision": os.getenv("PRECISION", _DEFAULTS["precision"]),
        }
        return cls._from_mapping(env_payload)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExecutionConfig:
        """Construct configuration from dictionary data."""
        payload = cls._merge_defaults(data)
        return cls._from_mapping(payload)

    @classmethod
    def _from_mapping(cls, payload: dict[str, Any]) -> ExecutionConfig:
        """Internal helper to build configuration from arbitrary mapping."""
        return cls(
            random_state=_parse_int(payload["random_state"], "random_state"),
            trial_num_samples=_parse_int(
                payload["trial_num_samples"], "trial_num_samples"
            ),
            trial_max_steps=_parse_int(payload["trial_max_steps"], "trial_max_steps"),
            default_h=_parse_int(payload["default_h"], "default_h"),
            h_ratio=_parse_h_ratio(payload["h_ratio"]),
            max_workers=_parse_int(payload["max_workers"], "max_workers"),
            allow_ray_parallel=_parse_bool(
                payload["allow_ray_parallel"], "allow_ray_parallel"
            ),
            save_model=_parse_bool(payload["save_model"], "save_model"),
            overwrite_model=_parse_bool(payload["overwrite_model"], "overwrite_model"),
            dir_tokens_maxlen=_parse_int(
                payload["dir_tokens_maxlen"], "dir_tokens_maxlen"
            ),
            max_exog_futr=_parse_int(payload["max_exog_futr"], "max_exog_futr"),
            max_exog_hist=_parse_int(payload["max_exog_hist"], "max_exog_hist"),
            max_exog_stat=_parse_int(payload["max_exog_stat"], "max_exog_stat"),
            early_stopping_patience=_parse_int(
                payload["early_stopping_patience"], "early_stopping_patience"
            ),
            gradient_clip_val=_parse_float(
                payload["gradient_clip_val"], "gradient_clip_val"
            ),
            accelerator=_normalise_accelerator(payload["accelerator"]),
            devices=_parse_int(payload["devices"], "devices"),
            precision=_normalise_precision(payload["precision"]),
        )

    def validate(self) -> None:
        """Validate configuration values for runtime safety."""
        if self.random_state < 0:
            raise ValueError(f"random_state must be non-negative: {self.random_state}")

        positive_fields: dict[str, int] = {
            "trial_num_samples": self.trial_num_samples,
            "trial_max_steps": self.trial_max_steps,
            "default_h": self.default_h,
            "max_workers": self.max_workers,
            "dir_tokens_maxlen": self.dir_tokens_maxlen,
            "devices": self.devices,
        }
        for field, value in positive_fields.items():
            if value < 1:
                raise ValueError(f"{field} must be >= 1: {value}")

        if not 0 < self.h_ratio <= 1.0:
            raise ValueError(f"h_ratio must be in (0, 1]: {self.h_ratio}")

        non_negative_fields: dict[str, int] = {
            "max_exog_futr": self.max_exog_futr,
            "max_exog_hist": self.max_exog_hist,
            "max_exog_stat": self.max_exog_stat,
            "early_stopping_patience": self.early_stopping_patience,
        }
        for field, value in non_negative_fields.items():
            if value < 0:
                raise ValueError(f"{field} must be non-negative: {value}")

        if self.gradient_clip_val < 0:
            raise ValueError(
                f"gradient_clip_val must be >= 0: {self.gradient_clip_val}"
            )

        if self.accelerator not in _VALID_ACCELERATORS:
            raise ValueError(
                f"accelerator must be one of {_VALID_ACCELERATORS}: "
                f"{self.accelerator}"
            )
        if self.precision not in _VALID_PRECISIONS:
            raise ValueError(
                f"precision must be one of {_VALID_PRECISIONS}: {self.precision}"
            )

    def get_effective_h(self, data_length: int) -> int:
        """Return effective forecasting horizon."""
        horizon = int(data_length * self.h_ratio)
        return max(self.default_h, horizon)

    def should_use_gpu(self) -> bool:
        """Return True when GPU-capable accelerator selected."""
        return self.accelerator in {"cuda", "auto", "mps", "tpu"}

    def get_num_workers(self) -> int:
        """Return worker count constrained by CPU availability."""
        cpu_count = os.cpu_count() or 1
        return max(1, min(self.max_workers, cpu_count))
