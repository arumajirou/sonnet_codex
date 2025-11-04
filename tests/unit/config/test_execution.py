"""Tests for ExecutionConfig covering environment parsing and validation."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[3]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from nf_auto_runner.config.execution import ExecutionConfig  # noqa: E402


class TestExecutionConfig:
    """ExecutionConfig behavioural tests."""

    def test_from_env_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Environment defaults should match documented configuration values."""
        keys = [
            "RANDOM_STATE",
            "TRIAL_NUM_SAMPLES",
            "TRIAL_MAX_STEPS",
            "DEFAULT_H",
            "H_RATIO",
            "MAX_WORKERS",
            "ALLOW_RAY_PARALLEL",
            "SAVE_MODEL",
            "OVERWRITE_MODEL",
            "DIR_TOKENS_MAXLEN",
            "MAX_EXOG_FUTR",
            "MAX_EXOG_HIST",
            "MAX_EXOG_STAT",
            "EARLY_STOPPING_PATIENCE",
            "GRADIENT_CLIP_VAL",
            "ACCELERATOR",
            "DEVICES",
            "PRECISION",
        ]
        for key in keys:
            monkeypatch.delenv(key, raising=False)

        config = ExecutionConfig.from_env()

        assert config.random_state == 42
        assert config.trial_num_samples == 10
        assert config.trial_max_steps == 1000
        assert config.default_h == 7
        assert config.h_ratio == pytest.approx(0.2)
        assert config.max_workers == 4
        assert config.allow_ray_parallel is False
        assert config.save_model is True
        assert config.overwrite_model is False
        assert config.dir_tokens_maxlen == 50
        assert config.max_exog_futr == 10
        assert config.max_exog_hist == 10
        assert config.max_exog_stat == 5
        assert config.early_stopping_patience == 10
        assert config.gradient_clip_val == pytest.approx(1.0)
        assert config.accelerator == "auto"
        assert config.devices == 1
        assert config.precision == "32"

    def test_from_env_custom(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Custom environment overrides should populate the dataclass."""
        monkeypatch.setenv("RANDOM_STATE", "123")
        monkeypatch.setenv("TRIAL_NUM_SAMPLES", "20")
        monkeypatch.setenv("TRIAL_MAX_STEPS", "2000")
        monkeypatch.setenv("DEFAULT_H", "30")
        monkeypatch.setenv("H_RATIO", "0.5")
        monkeypatch.setenv("MAX_WORKERS", "8")
        monkeypatch.setenv("ALLOW_RAY_PARALLEL", "true")
        monkeypatch.setenv("SAVE_MODEL", "false")
        monkeypatch.setenv("OVERWRITE_MODEL", "true")
        monkeypatch.setenv("DIR_TOKENS_MAXLEN", "64")
        monkeypatch.setenv("MAX_EXOG_FUTR", "12")
        monkeypatch.setenv("MAX_EXOG_HIST", "14")
        monkeypatch.setenv("MAX_EXOG_STAT", "7")
        monkeypatch.setenv("EARLY_STOPPING_PATIENCE", "25")
        monkeypatch.setenv("GRADIENT_CLIP_VAL", "0.5")
        monkeypatch.setenv("ACCELERATOR", "cuda")
        monkeypatch.setenv("DEVICES", "2")
        monkeypatch.setenv("PRECISION", "bf16")

        config = ExecutionConfig.from_env()

        assert config.random_state == 123
        assert config.trial_num_samples == 20
        assert config.trial_max_steps == 2000
        assert config.default_h == 30
        assert config.h_ratio == pytest.approx(0.5)
        assert config.max_workers == 8
        assert config.allow_ray_parallel is True
        assert config.save_model is False
        assert config.overwrite_model is True
        assert config.dir_tokens_maxlen == 64
        assert config.max_exog_futr == 12
        assert config.max_exog_hist == 14
        assert config.max_exog_stat == 7
        assert config.early_stopping_patience == 25
        assert config.gradient_clip_val == pytest.approx(0.5)
        assert config.accelerator == "cuda"
        assert config.devices == 2
        assert config.precision == "bf16"

    def test_from_dict_merges_defaults(self) -> None:
        """from_dict should fall back to documented defaults when omitted."""
        config = ExecutionConfig.from_dict(
            {
                "random_state": 99,
                "allow_ray_parallel": True,
                "save_model": False,
                "accelerator": "cpu",
                "precision": "16",
            }
        )

        assert config.random_state == 99
        assert config.allow_ray_parallel is True
        assert config.save_model is False
        assert config.accelerator == "cpu"
        assert config.precision == "16"
        assert config.trial_num_samples == 10
        assert config.trial_max_steps == 1000

    def test_from_dict_numeric_boolean(self) -> None:
        """Numeric values should be accepted for boolean fields."""
        config = ExecutionConfig.from_dict({"allow_ray_parallel": 1})
        assert config.allow_ray_parallel is True

    def test_from_dict_invalid_boolean(self) -> None:
        """Invalid boolean-like values should raise TypeError."""
        with pytest.raises(TypeError, match="allow_ray_parallel"):
            ExecutionConfig.from_dict({"allow_ray_parallel": object()})

    def test_from_dict_invalid_integer(self) -> None:
        """Invalid integer-like values should raise TypeError."""
        with pytest.raises(TypeError, match="trial_max_steps"):
            ExecutionConfig.from_dict({"trial_max_steps": "not-an-int"})

    def test_from_dict_boolean_for_integer(self) -> None:
        """Boolean values for integer fields should raise TypeError."""
        with pytest.raises(TypeError, match="max_workers"):
            ExecutionConfig.from_dict({"max_workers": True})

    def test_from_dict_invalid_float(self) -> None:
        """Invalid float-like values should raise TypeError."""
        with pytest.raises(TypeError, match="gradient_clip_val"):
            ExecutionConfig.from_dict({"gradient_clip_val": "N/A"})

    def test_from_dict_boolean_for_float(self) -> None:
        """Boolean values for float fields should raise TypeError."""
        with pytest.raises(TypeError, match="gradient_clip_val"):
            ExecutionConfig.from_dict({"gradient_clip_val": True})

    def test_from_dict_normalises_strings(self) -> None:
        """Whitespace and numeric precision values should be normalised."""
        config = ExecutionConfig.from_dict(
            {"accelerator": " CUDA ", "precision": 16, "devices": "2"}
        )

        assert config.accelerator == "cuda"
        assert config.precision == "16"
        assert config.devices == 2

    def test_from_dict_non_string_accelerator(self) -> None:
        """Non-string accelerator values should be coerced to string."""
        config = ExecutionConfig.from_dict({"accelerator": 123})
        assert config.accelerator == "123"
        with pytest.raises(ValueError, match="accelerator must be one of"):
            config.validate()

    def test_validate_success(self) -> None:
        """validate should no-op for a properly populated configuration."""
        config = ExecutionConfig(
            random_state=42,
            trial_num_samples=10,
            trial_max_steps=1000,
            default_h=7,
            h_ratio=0.2,
            max_workers=4,
            allow_ray_parallel=False,
            save_model=True,
            overwrite_model=False,
            dir_tokens_maxlen=50,
            max_exog_futr=10,
            max_exog_hist=10,
            max_exog_stat=5,
            early_stopping_patience=10,
            gradient_clip_val=1.0,
            accelerator="auto",
            devices=1,
            precision="32",
        )

        config.validate()  # Should not raise.

    def test_validate_failure_negative_random_state(self) -> None:
        """Negative random_state should raise ValueError."""
        config = ExecutionConfig(
            random_state=-1,
            trial_num_samples=10,
            trial_max_steps=1000,
            default_h=7,
            h_ratio=0.2,
            max_workers=4,
            allow_ray_parallel=False,
            save_model=True,
            overwrite_model=False,
            dir_tokens_maxlen=50,
            max_exog_futr=10,
            max_exog_hist=10,
            max_exog_stat=5,
            early_stopping_patience=10,
            gradient_clip_val=1.0,
            accelerator="auto",
            devices=1,
            precision="32",
        )

        with pytest.raises(ValueError, match="random_state must be non-negative"):
            config.validate()

    def test_validate_failure_invalid_h_ratio(self) -> None:
        """Invalid h_ratio outside (0, 1] should raise ValueError."""
        config = ExecutionConfig(
            random_state=42,
            trial_num_samples=10,
            trial_max_steps=1000,
            default_h=7,
            h_ratio=1.5,
            max_workers=4,
            allow_ray_parallel=False,
            save_model=True,
            overwrite_model=False,
            dir_tokens_maxlen=50,
            max_exog_futr=10,
            max_exog_hist=10,
            max_exog_stat=5,
            early_stopping_patience=10,
            gradient_clip_val=1.0,
            accelerator="auto",
            devices=1,
            precision="32",
        )

        with pytest.raises(ValueError, match="h_ratio must be in"):
            config.validate()

    def test_validate_failure_invalid_accelerator(self) -> None:
        """Unexpected accelerator strings should be rejected."""
        config = ExecutionConfig(
            random_state=42,
            trial_num_samples=10,
            trial_max_steps=1000,
            default_h=7,
            h_ratio=0.2,
            max_workers=4,
            allow_ray_parallel=False,
            save_model=True,
            overwrite_model=False,
            dir_tokens_maxlen=50,
            max_exog_futr=10,
            max_exog_hist=10,
            max_exog_stat=5,
            early_stopping_patience=10,
            gradient_clip_val=1.0,
            accelerator="invalid",
            devices=1,
            precision="32",
        )

        with pytest.raises(ValueError, match="accelerator must be one of"):
            config.validate()

    def test_validate_failure_precision(self) -> None:
        """Precision outside the supported set should be rejected."""
        config = ExecutionConfig(
            random_state=42,
            trial_num_samples=10,
            trial_max_steps=1000,
            default_h=7,
            h_ratio=0.2,
            max_workers=4,
            allow_ray_parallel=False,
            save_model=True,
            overwrite_model=False,
            dir_tokens_maxlen=50,
            max_exog_futr=10,
            max_exog_hist=10,
            max_exog_stat=5,
            early_stopping_patience=10,
            gradient_clip_val=1.0,
            accelerator="auto",
            devices=1,
            precision="64",
        )

        with pytest.raises(ValueError, match="precision must be one of"):
            config.validate()

    def test_validate_failure_devices(self) -> None:
        """Devices less than one should raise ValueError."""
        config = ExecutionConfig.from_dict({"devices": 0})
        with pytest.raises(ValueError, match="devices must be >= 1"):
            config.validate()

    def test_validate_failure_max_exog(self) -> None:
        """Negative exogenous limits should raise ValueError."""
        config = ExecutionConfig.from_dict({"max_exog_hist": -1})
        with pytest.raises(ValueError, match="max_exog_hist must be non-negative"):
            config.validate()

    def test_validate_failure_gradient_clip(self) -> None:
        """Negative gradient clip values should raise ValueError."""
        config = ExecutionConfig.from_dict({"gradient_clip_val": -0.1})
        with pytest.raises(ValueError, match="gradient_clip_val must be >= 0"):
            config.validate()

    def test_get_effective_h(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_effective_h should respect default_h and ratio limits."""
        monkeypatch.setenv("DEFAULT_H", "10")
        monkeypatch.setenv("H_RATIO", "0.3")
        config = ExecutionConfig.from_env()

        assert config.get_effective_h(100) == max(10, int(100 * 0.3))
        assert config.get_effective_h(20) == 10

    def test_should_use_gpu(self) -> None:
        """should_use_gpu should reflect accelerator selection."""
        config_gpu = ExecutionConfig(
            random_state=42,
            trial_num_samples=10,
            trial_max_steps=1000,
            default_h=7,
            h_ratio=0.2,
            max_workers=4,
            allow_ray_parallel=False,
            save_model=True,
            overwrite_model=False,
            dir_tokens_maxlen=50,
            max_exog_futr=10,
            max_exog_hist=10,
            max_exog_stat=5,
            early_stopping_patience=10,
            gradient_clip_val=1.0,
            accelerator="cuda",
            devices=1,
            precision="32",
        )
        assert config_gpu.should_use_gpu() is True

        config_cpu = ExecutionConfig(
            random_state=42,
            trial_num_samples=10,
            trial_max_steps=1000,
            default_h=7,
            h_ratio=0.2,
            max_workers=4,
            allow_ray_parallel=False,
            save_model=True,
            overwrite_model=False,
            dir_tokens_maxlen=50,
            max_exog_futr=10,
            max_exog_hist=10,
            max_exog_stat=5,
            early_stopping_patience=10,
            gradient_clip_val=1.0,
            accelerator="cpu",
            devices=1,
            precision="32",
        )
        assert config_cpu.should_use_gpu() is False

    def test_get_num_workers(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_num_workers should cap worker count by cpu availability."""
        monkeypatch.setenv("MAX_WORKERS", "16")

        def fake_cpu_count() -> int:
            return 6

        monkeypatch.setattr(os, "cpu_count", fake_cpu_count)
        config = ExecutionConfig.from_env()

        assert config.max_workers == 16
        assert config.get_num_workers() == 6

    def test_to_json_round_trip(self, tmp_path: Path) -> None:
        """Serialisation to/from JSON should retain values."""
        config = ExecutionConfig(
            random_state=1,
            trial_num_samples=2,
            trial_max_steps=3,
            default_h=4,
            h_ratio=0.25,
            max_workers=5,
            allow_ray_parallel=True,
            save_model=False,
            overwrite_model=True,
            dir_tokens_maxlen=60,
            max_exog_futr=7,
            max_exog_hist=8,
            max_exog_stat=9,
            early_stopping_patience=11,
            gradient_clip_val=0.1,
            accelerator="cuda",
            devices=2,
            precision="16",
        )
        json_path = tmp_path / "execution_config.json"
        config.save_to_file(json_path)

        reloaded = ExecutionConfig.from_json_file(json_path)

        assert reloaded == config
