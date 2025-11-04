"""Tests for ConfigLoader orchestration of configuration objects."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[3]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from nf_auto_runner.config.execution import ExecutionConfig, ExecutionMode  # noqa: E402
from nf_auto_runner.config.loader import ConfigLoader  # noqa: E402
from nf_auto_runner.config.model_selection import ModelSelectionConfig  # noqa: E402
from nf_auto_runner.config.path import PathConfig  # noqa: E402


class TestConfigLoader:
    """Exercise high-level loader capabilities."""

    @staticmethod
    def _prepare_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Point configuration directories to a temporary root."""
        data_dir = tmp_path / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("NF_DATA_CSV", str(data_dir / "train.csv"))

        output_dir = tmp_path / "nf_auto_runs"
        monkeypatch.setenv("NF_OUTPUT_DIR", str(output_dir))
        monkeypatch.setenv("NF_LOG_DIR", str(output_dir / "logs"))
        monkeypatch.setenv("NF_MODEL_DIR", str(output_dir / "models"))
        monkeypatch.setenv("NF_ARTIFACT_DIR", str(output_dir / "artifacts"))
        monkeypatch.setenv("NF_CHECKPOINT_DIR", str(output_dir / "checkpoints"))
        monkeypatch.setenv("NF_PLOT_DIR", str(output_dir / "plots"))

        # Ensure at least one model enabled by default
        monkeypatch.delenv("ENABLE_AUTO_NHITS", raising=False)
        monkeypatch.delenv("ENABLE_AUTO_LSTM", raising=False)
        monkeypatch.delenv("MODEL_WHITELIST", raising=False)
        monkeypatch.delenv("MODEL_BLACKLIST", raising=False)

    def test_load_all_from_environment(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """load_all should populate loader state with validated configs."""
        self._prepare_env(monkeypatch, tmp_path)

        loader = ConfigLoader()
        configs = loader.load_all()

        assert isinstance(configs["path"], PathConfig)
        assert isinstance(configs["execution"], ExecutionConfig)
        assert isinstance(configs["model_selection"], ModelSelectionConfig)
        assert loader.get(PathConfig) is configs["path"]

    def test_load_from_file_round_trip(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Persisted JSON payloads should reload into equivalent configs."""
        self._prepare_env(monkeypatch, tmp_path)

        loader = ConfigLoader()
        loader.load_all()
        payload_path = tmp_path / "config.json"
        loader.save_all(payload_path)

        reloaded = ConfigLoader()
        configs = reloaded.load_from_file(payload_path)

        assert set(configs.keys()) == {"path", "execution", "model_selection"}
        assert isinstance(reloaded.get(ModelSelectionConfig), ModelSelectionConfig)

    def test_load_from_file_missing(self, tmp_path: Path) -> None:
        """Missing configuration files should raise FileNotFoundError."""
        loader = ConfigLoader()
        missing = tmp_path / "missing.json"

        with pytest.raises(FileNotFoundError):
            loader.load_from_file(missing)

    def test_merge_configs_last_strategy(self, tmp_path: Path) -> None:
        """merge_configs should select the last config when requested."""
        base_dir = tmp_path / "runs"
        (tmp_path / "data").mkdir(parents=True, exist_ok=True)
        cfg1 = PathConfig(
            data_csv=tmp_path / "data" / "a.csv",
            output_dir=base_dir / "one",
            log_dir=base_dir / "one" / "logs",
            project_root=ROOT_DIR,
            model_dir=base_dir / "one" / "models",
            artifact_dir=base_dir / "one" / "artifacts",
            checkpoint_dir=base_dir / "one" / "checkpoints",
            plot_dir=base_dir / "one" / "plots",
        )
        cfg2 = PathConfig(
            data_csv=tmp_path / "data" / "b.csv",
            output_dir=base_dir / "two",
            log_dir=base_dir / "two" / "logs",
            project_root=ROOT_DIR,
            model_dir=base_dir / "two" / "models",
            artifact_dir=base_dir / "two" / "artifacts",
            checkpoint_dir=base_dir / "two" / "checkpoints",
            plot_dir=base_dir / "two" / "plots",
        )

        loader = ConfigLoader()
        merged = loader.merge_configs([cfg1, cfg2], strategy="last")

        assert merged is cfg2

    def test_merge_configs_different_types(self, tmp_path: Path) -> None:
        """merge_configs should reject heterogeneous configuration lists."""
        path_config = PathConfig(
            data_csv=tmp_path / "data.csv",
            output_dir=tmp_path / "out",
            log_dir=tmp_path / "out" / "logs",
            project_root=ROOT_DIR,
            model_dir=tmp_path / "out" / "models",
            artifact_dir=tmp_path / "out" / "artifacts",
            checkpoint_dir=tmp_path / "out" / "checkpoints",
            plot_dir=tmp_path / "out" / "plots",
        )
        execution_config = ExecutionConfig(
            mode=ExecutionMode.DEVELOPMENT,
            n_workers=1,
            backend=ExecutionConfig.from_env().backend,
            max_memory_gb=None,
            use_gpu=False,
            gpu_devices=None,
            timeout_seconds=10,
            max_retries=1,
            log_level="INFO",
            debug=False,
            random_seed=1,
        )

        loader = ConfigLoader()

        with pytest.raises(ValueError, match="same type"):
            loader.merge_configs([path_config, execution_config])

    def test_validate_all_success(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """validate_all should return True when every config passes."""
        self._prepare_env(monkeypatch, tmp_path)

        loader = ConfigLoader()
        loader.load_all()

        assert loader.validate_all() is True

    def test_validate_all_missing_config(self) -> None:
        """Missing configuration entries should produce a validation error."""
        loader = ConfigLoader()

        with pytest.raises(ValueError, match="config is None"):
            loader.validate_all({"path": None})

    def test_get_not_loaded(self) -> None:
        """Accessing unloaded configuration should raise KeyError."""
        loader = ConfigLoader()

        with pytest.raises(KeyError, match="Configuration not loaded"):
            loader.get(PathConfig)

    def test_save_all_success(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """save_all should persist a JSON artefact with all loaded configs."""
        self._prepare_env(monkeypatch, tmp_path)
        loader = ConfigLoader()
        loader.load_all()

        output_path = tmp_path / "saved" / "config.json"
        loader.save_all(output_path)

        with output_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        assert {"path", "execution", "model_selection"} <= data.keys()

    def test_save_all_without_configs(self, tmp_path: Path) -> None:
        """Attempting to save without configs should raise ValueError."""
        loader = ConfigLoader()
        target = tmp_path / "config.json"

        with pytest.raises(ValueError, match="No configurations to save"):
            loader.save_all(target)
