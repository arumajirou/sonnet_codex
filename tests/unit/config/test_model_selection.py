"""Tests for ModelSelectionConfig behaviour."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[3]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from nf_auto_runner.config.model_selection import ModelSelectionConfig  # noqa: E402


class TestModelSelectionConfig:
    """Test suite covering environment parsing and helper utilities."""

    @staticmethod
    def _clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
        """Remove relevant environment variables for clean defaults."""
        for var in [
            "ENABLE_AUTO_NHITS",
            "ENABLE_AUTO_LSTM",
            "ENABLE_AUTO_TFT",
            "ENABLE_AUTO_INFORMER",
            "ENABLE_AUTO_AUTOFORMER",
            "ENABLE_AUTO_PATCHTST",
            "MODEL_WHITELIST",
            "MODEL_BLACKLIST",
        ]:
            monkeypatch.delenv(var, raising=False)

    def test_from_env_default_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Defaults should match documented expectations."""
        self._clear_env(monkeypatch)

        config = ModelSelectionConfig.from_env()

        assert config.enable_auto_nhits is True
        assert config.enable_auto_lstm is True
        assert config.enable_auto_tft is False
        assert config.enable_auto_informer is False
        assert config.enable_auto_autoformer is False
        assert config.enable_auto_patchtst is False
        assert config.model_whitelist == []
        assert config.model_blacklist == []

    def test_from_env_custom_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Custom environment overrides should be respected."""
        self._clear_env(monkeypatch)
        monkeypatch.setenv("ENABLE_AUTO_NHITS", "false")
        monkeypatch.setenv("ENABLE_AUTO_TFT", "1")
        monkeypatch.setenv("ENABLE_AUTO_PATCHTST", "yes")
        monkeypatch.setenv(
            "MODEL_WHITELIST", '["AutoNHITS", "AutoTFT", "AutoPatchTST"]'
        )
        monkeypatch.setenv("MODEL_BLACKLIST", '["AutoLSTM"]')

        config = ModelSelectionConfig.from_env()

        assert config.enable_auto_nhits is False
        assert config.enable_auto_tft is True
        assert config.enable_auto_patchtst is True
        assert config.model_whitelist == ["AutoNHITS", "AutoTFT", "AutoPatchTST"]
        assert config.model_blacklist == ["AutoLSTM"]

    def test_from_env_invalid_json_lists(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Malformed JSON should fall back to empty lists."""
        self._clear_env(monkeypatch)
        monkeypatch.setenv("MODEL_WHITELIST", "[invalid")
        monkeypatch.setenv("MODEL_BLACKLIST", '{"not": "a list"}')

        config = ModelSelectionConfig.from_env()

        assert config.model_whitelist == []
        assert config.model_blacklist == []

    def test_validate_success(self) -> None:
        """validate should pass when at least one model remains enabled."""
        config = ModelSelectionConfig(
            enable_auto_nhits=True,
            enable_auto_lstm=False,
            enable_auto_tft=False,
            enable_auto_informer=False,
            enable_auto_autoformer=False,
            enable_auto_patchtst=False,
            model_whitelist=[],
            model_blacklist=[],
        )

        config.validate()  # Should not raise.

    def test_validate_failure_no_model_enabled(self) -> None:
        """Disallow configurations that disable every model."""
        config = ModelSelectionConfig(
            enable_auto_nhits=False,
            enable_auto_lstm=False,
            enable_auto_tft=False,
            enable_auto_informer=False,
            enable_auto_autoformer=False,
            enable_auto_patchtst=False,
            model_whitelist=[],
            model_blacklist=[],
        )

        with pytest.raises(ValueError, match="At least one model must be enabled"):
            config.validate()

    def test_validate_failure_overlap(self) -> None:
        """Reject overlaps between whitelist and blacklist entries."""
        config = ModelSelectionConfig(
            enable_auto_nhits=True,
            enable_auto_lstm=True,
            enable_auto_tft=False,
            enable_auto_informer=False,
            enable_auto_autoformer=False,
            enable_auto_patchtst=False,
            model_whitelist=["AutoNHITS", "AutoLSTM"],
            model_blacklist=["AutoLSTM"],
        )

        with pytest.raises(ValueError, match="Models appear in both whitelist"):
            config.validate()

    def test_get_enabled_models_respects_filters(self) -> None:
        """Whitelist and blacklist filters should be applied after flags."""
        config = ModelSelectionConfig(
            enable_auto_nhits=True,
            enable_auto_lstm=True,
            enable_auto_tft=True,
            enable_auto_informer=False,
            enable_auto_autoformer=False,
            enable_auto_patchtst=False,
            model_whitelist=["AutoNHITS", "AutoTFT"],
            model_blacklist=["AutoNHITS"],
        )

        enabled = config.get_enabled_models()

        assert enabled == ["AutoTFT"]

    def test_is_model_enabled(self) -> None:
        """is_model_enabled should surface flag + filter resolution."""
        config = ModelSelectionConfig(
            enable_auto_nhits=True,
            enable_auto_lstm=False,
            enable_auto_tft=False,
            enable_auto_informer=False,
            enable_auto_autoformer=False,
            enable_auto_patchtst=False,
            model_whitelist=[],
            model_blacklist=[],
        )

        assert config.is_model_enabled("AutoNHITS") is True
        assert config.is_model_enabled("AutoLSTM") is False

    def test_get_disabled_models(self) -> None:
        """Disabled models should list every non-enabled entry."""
        config = ModelSelectionConfig(
            enable_auto_nhits=True,
            enable_auto_lstm=True,
            enable_auto_tft=False,
            enable_auto_informer=False,
            enable_auto_autoformer=False,
            enable_auto_patchtst=True,
            model_whitelist=[],
            model_blacklist=[],
        )

        disabled = config.get_disabled_models()

        assert set(disabled) == {"AutoTFT", "AutoInformer", "AutoAutoformer"}
