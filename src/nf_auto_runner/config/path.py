"""Configuration module for filesystem paths used across the project."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .base import Config


def _env_path(env_name: str, default: Path) -> Path:
    """Resolve path-like environment variable with fallback."""
    value = os.getenv(env_name)
    if value is None or not value.strip():
        return Path(default).expanduser()
    return Path(value).expanduser()


@dataclass(frozen=True)
# pylint: disable=too-many-instance-attributes
class PathConfig(Config):
    """Configuration object encapsulating important filesystem paths."""

    data_csv: Path
    output_dir: Path
    log_dir: Path
    project_root: Path
    model_dir: Path
    artifact_dir: Path
    checkpoint_dir: Path
    plot_dir: Path

    def __post_init__(self) -> None:
        """Ensure critical directories exist right after initialisation."""
        self.ensure_dirs()

    @classmethod
    def from_env(cls) -> "PathConfig":
        """Build configuration from environment variables."""
        project_root = Path(__file__).resolve().parent.parent
        output_dir = _env_path("NF_OUTPUT_DIR", Path("./nf_auto_runs"))
        data_csv = _env_path("NF_DATA_CSV", Path("./data.csv"))
        log_dir = _env_path("NF_LOG_DIR", output_dir / "logs")
        model_dir = _env_path("NF_MODEL_DIR", output_dir / "models")
        artifact_dir = _env_path("NF_ARTIFACT_DIR", output_dir / "artifacts")
        checkpoint_dir = _env_path("NF_CHECKPOINT_DIR", output_dir / "checkpoints")
        plot_dir = _env_path("NF_PLOT_DIR", output_dir / "plots")

        return cls(
            data_csv=data_csv,
            output_dir=output_dir,
            log_dir=log_dir,
            project_root=project_root,
            model_dir=model_dir,
            artifact_dir=artifact_dir,
            checkpoint_dir=checkpoint_dir,
            plot_dir=plot_dir,
        )

    def ensure_dirs(self) -> None:
        """Create required directories when missing."""
        for directory in self._managed_directories:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)

    def validate(self) -> None:
        """Validate path configuration for readiness."""
        data_parent = self.data_csv.parent
        if not data_parent.exists():
            raise ValueError(f"Data CSV parent directory does not exist: {data_parent}")

        for directory in self._managed_directories:
            if directory.exists() and not os.access(directory, os.W_OK):
                raise ValueError(f"Directory is not writable: {directory}")

    def get_run_dir(self, run_id: str) -> Path:
        """Return directory for storing run artefacts."""
        run_dir = self.output_dir / "runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def get_model_path(self, run_id: str, model_name: str) -> Path:
        """Return destination path for a persisted model checkpoint."""
        self.model_dir.mkdir(parents=True, exist_ok=True)
        return self.model_dir / f"{run_id}_{model_name}.pth"

    def get_log_path(self, run_id: str) -> Path:
        """Return structured log file path for the provided run identifier."""
        self.log_dir.mkdir(parents=True, exist_ok=True)
        return self.log_dir / f"{run_id}.jsonl"

    @property
    def _managed_directories(self) -> Iterable[Path]:
        """Return iterable of directories managed by this configuration."""
        return (
            self.output_dir,
            self.log_dir,
            self.model_dir,
            self.artifact_dir,
            self.checkpoint_dir,
            self.plot_dir,
        )
