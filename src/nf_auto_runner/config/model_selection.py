"""Configuration for selecting which automated models are eligible to run."""

from __future__ import annotations

import json
import os
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

from .base import Config

_TRUE_VALUES = {"1", "true", "yes", "on"}
_AUTO_MODEL_FLAGS = {
    "AutoNHITS": "ENABLE_AUTO_NHITS",
    "AutoLSTM": "ENABLE_AUTO_LSTM",
    "AutoTFT": "ENABLE_AUTO_TFT",
    "AutoInformer": "ENABLE_AUTO_INFORMER",
    "AutoAutoformer": "ENABLE_AUTO_AUTOFORMER",
    "AutoPatchTST": "ENABLE_AUTO_PATCHTST",
}


def _parse_bool(value: object, default: bool = False) -> bool:
    """Normalise diverse truthy representations into a boolean."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in _TRUE_VALUES
    raise TypeError(f"Cannot interpret {value!r} as boolean.")


def _parse_json_list(raw: str) -> list[str]:
    """Parse JSON array strings into string lists, returning [] on failure."""
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if isinstance(payload, list):
        return [str(item) for item in payload]
    return []


def _normalise_sequence(items: Sequence[str] | Iterable[str]) -> list[str]:
    """Return a defensive copy of iterable items as strings."""
    return [str(item) for item in items]


@dataclass(frozen=True)
class ModelSelectionConfig(Config):
    """Configuration describing which automated models are enabled."""

    enable_auto_nhits: bool
    enable_auto_lstm: bool
    enable_auto_tft: bool
    enable_auto_informer: bool
    enable_auto_autoformer: bool
    enable_auto_patchtst: bool
    model_whitelist: list[str] = field(default_factory=list)
    model_blacklist: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Normalise whitelist/blacklist values after initialisation."""
        whitelist = _normalise_sequence(self.model_whitelist)
        blacklist = _normalise_sequence(self.model_blacklist)
        object.__setattr__(self, "model_whitelist", whitelist)
        object.__setattr__(self, "model_blacklist", blacklist)

    @classmethod
    def from_env(cls) -> ModelSelectionConfig:
        """Construct configuration from environment variables."""
        whitelist_raw = os.getenv("MODEL_WHITELIST", "[]")
        blacklist_raw = os.getenv("MODEL_BLACKLIST", "[]")
        whitelist = _parse_json_list(whitelist_raw)
        blacklist = _parse_json_list(blacklist_raw)

        return cls(
            enable_auto_nhits=_parse_bool(os.getenv(_AUTO_MODEL_FLAGS["AutoNHITS"]), default=True),
            enable_auto_lstm=_parse_bool(os.getenv(_AUTO_MODEL_FLAGS["AutoLSTM"]), default=True),
            enable_auto_tft=_parse_bool(os.getenv(_AUTO_MODEL_FLAGS["AutoTFT"]), default=False),
            enable_auto_informer=_parse_bool(
                os.getenv(_AUTO_MODEL_FLAGS["AutoInformer"]), default=False
            ),
            enable_auto_autoformer=_parse_bool(
                os.getenv(_AUTO_MODEL_FLAGS["AutoAutoformer"]), default=False
            ),
            enable_auto_patchtst=_parse_bool(
                os.getenv(_AUTO_MODEL_FLAGS["AutoPatchTST"]), default=False
            ),
            model_whitelist=whitelist,
            model_blacklist=blacklist,
        )

    def validate(self) -> None:
        """Validate configuration for conflicting or unsafe values."""
        if not any(
            [
                self.enable_auto_nhits,
                self.enable_auto_lstm,
                self.enable_auto_tft,
                self.enable_auto_informer,
                self.enable_auto_autoformer,
                self.enable_auto_patchtst,
            ]
        ):
            raise ValueError("At least one model must be enabled.")

        whitelist_set = set(self.model_whitelist)
        blacklist_set = set(self.model_blacklist)
        overlap = whitelist_set & blacklist_set
        if overlap:
            raise ValueError(f"Models appear in both whitelist and blacklist: {sorted(overlap)}")

    def get_enabled_models(self) -> list[str]:
        """Return model identifiers that are enabled after filters are applied."""
        flag_map = {
            "AutoNHITS": self.enable_auto_nhits,
            "AutoLSTM": self.enable_auto_lstm,
            "AutoTFT": self.enable_auto_tft,
            "AutoInformer": self.enable_auto_informer,
            "AutoAutoformer": self.enable_auto_autoformer,
            "AutoPatchTST": self.enable_auto_patchtst,
        }

        enabled = [name for name, flag in flag_map.items() if flag]

        if self.model_whitelist:
            whitelist = set(self.model_whitelist)
            enabled = [name for name in enabled if name in whitelist]

        if self.model_blacklist:
            blacklist = set(self.model_blacklist)
            enabled = [name for name in enabled if name not in blacklist]

        return enabled

    def is_model_enabled(self, model_name: str) -> bool:
        """Return True if the given model name is enabled."""
        return model_name in self.get_enabled_models()

    def get_disabled_models(self) -> list[str]:
        """Return models that are not enabled, respecting filters."""
        all_models = list(_AUTO_MODEL_FLAGS.keys())
        enabled = set(self.get_enabled_models())
        return [name for name in all_models if name not in enabled]
