"""Tests for PathConfig configuration class."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
import sys
from typing import Dict

import pytest

ROOT_DIR = Path(__file__).resolve().parents[3]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from nf_auto_runner.config.path import PathConfig  # noqa: E402


class TestPathConfig:
    """Test suite for validating PathConfig behaviour."""

    def test_from_env_default_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Environment defaults should populate standard project layout."""
        for key in [
            "NF_DATA_CSV",
            "NF_OUTPUT_DIR",
            "NF_LOG_DIR",
            "NF_MODEL_DIR",
            "NF_ARTIFACT_DIR",
            "NF_CHECKPOINT_DIR",
            "NF_PLOT_DIR",
        ]:
            monkeypatch.delenv(key, raising=False)

        config = PathConfig.from_env()

        path_module = __import__("nf_auto_runner.config.path", fromlist=["__file__"])
        module_file = Path(path_module.__file__).resolve()

        assert config.data_csv == Path("./data.csv")
        assert config.output_dir == Path("./nf_auto_runs")
        assert config.log_dir == Path("./nf_auto_runs/logs")
        assert config.model_dir == Path("./nf_auto_runs/models")
        assert config.artifact_dir == Path("./nf_auto_runs/artifacts")
        assert config.checkpoint_dir == Path("./nf_auto_runs/checkpoints")
        assert config.plot_dir == Path("./nf_auto_runs/plots")
        assert config.project_root == module_file.parent.parent

    def test_from_env_custom_values(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Environment overrides should be reflected in resulting config."""
        monkeypatch.setenv("NF_DATA_CSV", str(tmp_path / "input/data.csv"))
        monkeypatch.setenv("NF_OUTPUT_DIR", str(tmp_path / "outputs"))
        monkeypatch.setenv("NF_LOG_DIR", str(tmp_path / "logs"))
        monkeypatch.setenv("NF_MODEL_DIR", str(tmp_path / "models"))
        monkeypatch.setenv("NF_ARTIFACT_DIR", str(tmp_path / "artifacts"))
        monkeypatch.setenv("NF_CHECKPOINT_DIR", str(tmp_path / "checkpoints"))
        monkeypatch.setenv("NF_PLOT_DIR", str(tmp_path / "plots"))

        config = PathConfig.from_env()

        assert config.data_csv == tmp_path / "input/data.csv"
        assert config.output_dir == tmp_path / "outputs"
        assert config.log_dir == tmp_path / "logs"
        assert config.model_dir == tmp_path / "models"
        assert config.artifact_dir == tmp_path / "artifacts"
        assert config.checkpoint_dir == tmp_path / "checkpoints"
        assert config.plot_dir == tmp_path / "plots"

    def test_validate_valid_paths(self, tmp_path: Path) -> None:
        """validate should pass when directories exist and are writable."""
        data_parent = tmp_path / "dataset"
        data_parent.mkdir()

        config = PathConfig(
            data_csv=data_parent / "train.csv",
            output_dir=tmp_path / "outputs",
            log_dir=tmp_path / "outputs" / "logs",
            project_root=tmp_path,
            model_dir=tmp_path / "outputs" / "models",
            artifact_dir=tmp_path / "outputs" / "artifacts",
            checkpoint_dir=tmp_path / "outputs" / "checkpoints",
            plot_dir=tmp_path / "outputs" / "plots",
        )

        config.validate()  # Should not raise.

    def test_validate_invalid_paths(self, tmp_path: Path) -> None:
        """validate should raise when data directory parent is missing."""
        missing_parent = tmp_path / "missing" / "train.csv"

        config = PathConfig(
            data_csv=missing_parent,
            output_dir=tmp_path / "outputs",
            log_dir=tmp_path / "outputs" / "logs",
            project_root=tmp_path,
            model_dir=tmp_path / "outputs" / "models",
            artifact_dir=tmp_path / "outputs" / "artifacts",
            checkpoint_dir=tmp_path / "outputs" / "checkpoints",
            plot_dir=tmp_path / "outputs" / "plots",
        )

        with pytest.raises(
            ValueError, match="Data CSV parent directory does not exist"
        ):
            config.validate()

    def test_ensure_dirs_creates_directories(self, tmp_path: Path) -> None:
        """ensure_dirs should re-create directories if they are missing."""
        output_dir = tmp_path / "outputs"

        config = PathConfig(
            data_csv=tmp_path / "dataset" / "train.csv",
            output_dir=output_dir,
            log_dir=output_dir / "logs",
            project_root=tmp_path,
            model_dir=output_dir / "models",
            artifact_dir=output_dir / "artifacts",
            checkpoint_dir=output_dir / "checkpoints",
            plot_dir=output_dir / "plots",
        )

        shutil.rmtree(output_dir)

        assert not output_dir.exists()

        config.ensure_dirs()

        assert output_dir.exists()
        assert (output_dir / "logs").exists()
        assert (output_dir / "models").exists()
        assert (output_dir / "artifacts").exists()
        assert (output_dir / "checkpoints").exists()
        assert (output_dir / "plots").exists()

    def test_to_dict_contains_all_paths(self, tmp_path: Path) -> None:
        """to_dict should contain stringified versions of all paths."""
        output_dir = tmp_path / "outputs"
        config = PathConfig(
            data_csv=tmp_path / "dataset" / "train.csv",
            output_dir=output_dir,
            log_dir=output_dir / "logs",
            project_root=tmp_path,
            model_dir=output_dir / "models",
            artifact_dir=output_dir / "artifacts",
            checkpoint_dir=output_dir / "checkpoints",
            plot_dir=output_dir / "plots",
        )

        config_dict: Dict[str, str] = config.to_dict()

        assert config_dict["data_csv"] == str(tmp_path / "dataset" / "train.csv")
        assert config_dict["output_dir"] == str(output_dir)
        assert config_dict["log_dir"] == str(output_dir / "logs")
        assert config_dict["model_dir"] == str(output_dir / "models")
        assert config_dict["artifact_dir"] == str(output_dir / "artifacts")
        assert config_dict["checkpoint_dir"] == str(output_dir / "checkpoints")
        assert config_dict["plot_dir"] == str(output_dir / "plots")
        assert config_dict["project_root"] == str(tmp_path)

    def test_from_json_file_round_trip(self, tmp_path: Path) -> None:
        """Saving and loading via JSON should round-trip the configuration."""
        output_dir = tmp_path / "outputs"
        config = PathConfig(
            data_csv=tmp_path / "dataset" / "train.csv",
            output_dir=output_dir,
            log_dir=output_dir / "logs",
            project_root=tmp_path,
            model_dir=output_dir / "models",
            artifact_dir=output_dir / "artifacts",
            checkpoint_dir=output_dir / "checkpoints",
            plot_dir=output_dir / "plots",
        )

        json_path = tmp_path / "path_config.json"
        config.save_to_file(json_path)

        reloaded = PathConfig.from_json_file(json_path)

        assert reloaded == config

    def test_run_specific_helpers(self, tmp_path: Path) -> None:
        """Helper methods should return deterministic derived paths."""
        output_dir = tmp_path / "outputs"
        config = PathConfig(
            data_csv=tmp_path / "dataset" / "train.csv",
            output_dir=output_dir,
            log_dir=output_dir / "logs",
            project_root=tmp_path,
            model_dir=output_dir / "models",
            artifact_dir=output_dir / "artifacts",
            checkpoint_dir=output_dir / "checkpoints",
            plot_dir=output_dir / "plots",
        )

        run_dir = config.get_run_dir("run-001")
        model_path = config.get_model_path("run-001", "AutoNHITS")
        log_path = config.get_log_path("run-001")
        artifact_path = config.get_artifact_path("run-001", "metrics.json")
        checkpoint_path = config.get_checkpoint_path("run-001", "epoch-1.ckpt")
        plot_path = config.get_plot_path("run-001", "loss.png")

        assert run_dir.exists()
        assert run_dir.name == "run-001"
        assert model_path.parent == config.model_dir
        assert model_path.name == "run-001_AutoNHITS.pth"
        assert log_path.parent == config.log_dir
        assert log_path.name == "run-001.jsonl"
        assert artifact_path.parent == config.artifact_dir / "run-001"
        assert artifact_path.parent.exists()
        assert artifact_path.name == "metrics.json"
        assert checkpoint_path.parent == config.checkpoint_dir / "run-001"
        assert checkpoint_path.parent.exists()
        assert checkpoint_path.name == "epoch-1.ckpt"
        assert plot_path.parent == config.plot_dir / "run-001"
        assert plot_path.parent.exists()
        assert plot_path.name == "loss.png"

    def test_run_specific_paths_respect_env_overrides(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Run-scoped directories should honour NF_* overrides."""
        monkeypatch.setenv("NF_OUTPUT_DIR", str(tmp_path / "outputs"))
        monkeypatch.setenv("NF_ARTIFACT_DIR", str(tmp_path / "custom_artifacts"))
        monkeypatch.setenv("NF_CHECKPOINT_DIR", str(tmp_path / "custom_checkpoints"))
        monkeypatch.setenv("NF_PLOT_DIR", str(tmp_path / "custom_plots"))

        config = PathConfig.from_env()

        artifact_path = config.get_artifact_path("run-xyz", "artifact.bin")
        checkpoint_path = config.get_checkpoint_path("run-xyz", "model.ckpt")
        plot_path = config.get_plot_path("run-xyz", "chart.png")

        assert artifact_path == (
            tmp_path / "custom_artifacts" / "run-xyz" / "artifact.bin"
        )
        assert checkpoint_path == (
            tmp_path / "custom_checkpoints" / "run-xyz" / "model.ckpt"
        )
        assert plot_path == (tmp_path / "custom_plots" / "run-xyz" / "chart.png")
        assert artifact_path.parent.exists()
        assert checkpoint_path.parent.exists()
        assert plot_path.parent.exists()
