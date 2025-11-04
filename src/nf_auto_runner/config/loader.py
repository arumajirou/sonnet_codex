"""Utilities for loading and validating configuration objects."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Type

from .base import Config
from .execution import ExecutionConfig
from .model_selection import ModelSelectionConfig
from .path import PathConfig

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Load, validate, and persist configuration aggregates."""

    def __init__(self) -> None:
        """Initialise empty configuration store."""
        self.configs: Dict[Type[Config], Config] = {}

    def load_all(self) -> Dict[str, Config]:
        """Load all canonical configurations from environment variables."""
        logger.info("Loading all configurations from environment")

        try:
            path_config = PathConfig.from_env()
            execution_config = ExecutionConfig.from_env()
            model_selection_config = ModelSelectionConfig.from_env()

            path_config.validate()
            execution_config.validate()
            model_selection_config.validate()

            self.configs = {
                PathConfig: path_config,
                ExecutionConfig: execution_config,
                ModelSelectionConfig: model_selection_config,
            }

            result = {
                "path": path_config,
                "execution": execution_config,
                "model_selection": model_selection_config,
            }
            logger.info("Successfully loaded %s configurations", len(result))
            return result
        except Exception as exc:  # pragma: no cover - rewrapped for clarity
            logger.error("Failed to load configurations: %s", exc)
            raise ValueError(f"Configuration loading failed: {exc}") from exc

    def load_from_file(self, file_path: Path) -> Dict[str, Config]:
        """Load configurations from a JSON file."""
        path_obj = Path(file_path)
        logger.info("Loading configurations from file: %s", path_obj)

        if not path_obj.exists():
            raise FileNotFoundError(f"Configuration file not found: {path_obj}")

        with path_obj.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        loaded: Dict[str, Config] = {}

        if "path" in data:
            path_config = PathConfig.from_dict(data["path"])
            path_config.validate()
            loaded["path"] = path_config
            self.configs[PathConfig] = path_config

        if "execution" in data:
            execution_config = ExecutionConfig.from_dict(data["execution"])
            execution_config.validate()
            loaded["execution"] = execution_config
            self.configs[ExecutionConfig] = execution_config

        if "model_selection" in data:
            model_selection_config = ModelSelectionConfig.from_dict(
                data["model_selection"]
            )
            model_selection_config.validate()
            loaded["model_selection"] = model_selection_config
            self.configs[ModelSelectionConfig] = model_selection_config

        logger.info("Loaded %s configurations from %s", len(loaded), path_obj)
        return loaded

    def merge_configs(self, configs: List[Config], *, strategy: str = "last") -> Config:
        """Merge configurations of the same type using the requested strategy."""
        if not configs:
            raise ValueError("No configs to merge.")

        config_type = type(configs[0])
        if not all(isinstance(cfg, config_type) for cfg in configs):
            raise ValueError("All configs must be of the same type.")

        if strategy == "last":
            merged = configs[-1]
        elif strategy == "first":
            merged = configs[0]
        else:  # pragma: no cover - defensive branch
            raise ValueError(f"Unknown merge strategy: {strategy}")

        logger.info(
            "Merged %s configurations of %s using %s strategy",
            len(configs),
            config_type.__name__,
            strategy,
        )
        return merged

    def validate_all(self, configs: Optional[Dict[str, Config | None]] = None) -> bool:
        """Validate the provided configurations, defaulting to the internal set."""
        working: Dict[str, Config | None]
        if configs is None:
            working = {
                "path": self.configs.get(PathConfig),
                "execution": self.configs.get(ExecutionConfig),
                "model_selection": self.configs.get(ModelSelectionConfig),
            }
        else:
            working = configs

        errors: List[str] = []
        for name, config in working.items():
            if config is None:
                errors.append(f"{name}: config is None")
                continue
            try:
                config.validate()
            except ValueError as exc:
                errors.append(f"{name}: {exc}")

        if errors:
            message = "Configuration validation failed:\n" + "\n".join(errors)
            logger.error(message)
            raise ValueError(message)

        logger.info("All configurations validated successfully")
        return True

    def get(self, config_type: Type[Config]) -> Config:
        """Return a configuration instance keyed by its class."""
        if config_type not in self.configs:
            raise KeyError(f"Configuration not loaded: {config_type.__name__}")
        return self.configs[config_type]

    def save_all(self, file_path: Path, indent: int = 2) -> None:
        """Persist loaded configurations to the specified JSON file."""
        serialised = self._serialise_loaded()
        if not serialised:
            raise ValueError("No configurations to save.")

        path_obj = Path(file_path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)

        with path_obj.open("w", encoding="utf-8") as handle:
            json.dump(serialised, handle, indent=indent)

        logger.info("Saved %s configurations to %s", len(serialised), path_obj)

    def _serialise_loaded(self) -> Dict[str, Dict[str, object]]:
        """Return serialised payload for currently loaded configurations."""
        payload: Dict[str, Dict[str, object]] = {}

        if PathConfig in self.configs:
            payload["path"] = self.configs[PathConfig].to_dict()
        if ExecutionConfig in self.configs:
            payload["execution"] = self.configs[ExecutionConfig].to_dict()
        if ModelSelectionConfig in self.configs:
            payload["model_selection"] = self.configs[ModelSelectionConfig].to_dict()

        return payload
