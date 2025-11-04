"""Tests for the configuration base class."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any, Dict

import pytest

ROOT_DIR = Path(__file__).resolve().parents[3]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from nf_auto_runner.config.base import Config  # noqa: E402


@dataclass(frozen=True)
class SampleConfig(Config):
    """Concrete config implementation reserved for tests."""

    value: int
    path_dir: Path

    @classmethod
    def from_env(cls) -> "SampleConfig":
        """Construct configuration from environment variables."""
        value = int(os.getenv("SAMPLE_VALUE", "0"))
        path_raw = os.getenv("SAMPLE_PATH_DIR", "./runs")
        return cls(value=value, path_dir=Path(path_raw))

    def validate(self) -> None:
        """Ensure value is non-negative."""
        if self.value < 0:
            raise ValueError("value must be non-negative")


class TestConfigBase:
    """Test suite exercising Config base class behaviours."""

    def test_from_env_reads_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Ensure subclass can leverage the abstract constructor."""
        monkeypatch.setenv("SAMPLE_VALUE", "42")
        monkeypatch.setenv("SAMPLE_PATH_DIR", "/tmp/sample")

        config = SampleConfig.from_env()

        assert config.value == 42
        assert config.path_dir == Path("/tmp/sample")

    def test_from_dict_coerces_paths(self) -> None:
        """Path-like keys ending with _path or _dir become Path objects."""
        data: Dict[str, Any] = {"value": 10, "path_dir": "/tmp/runs", "other": "keep"}

        config = SampleConfig.from_dict(data)

        assert config.value == 10
        assert isinstance(config.path_dir, Path)
        assert config.path_dir == Path("/tmp/runs")

    def test_from_json_round_trip(self) -> None:
        """JSON serialisation and deserialisation stays consistent."""
        payload = {"value": 99, "path_dir": "./workspace"}

        config = SampleConfig.from_json(json.dumps(payload))

        assert config.value == 99
        assert config.path_dir == Path("./workspace")

    def test_from_json_file_reads_disk(self, tmp_path: Path) -> None:
        """Read configuration definitions from filesystem JSON."""
        config_path = tmp_path / "config.json"
        config_path.write_text('{"value": 7, "path_dir": "./cache"}', encoding="utf-8")

        config = SampleConfig.from_json_file(config_path)

        assert config.value == 7
        assert config.path_dir == Path("./cache")

    def test_to_dict_normalises_paths(self) -> None:
        """Path objects convert to string during dictionary materialisation."""
        config = SampleConfig(value=5, path_dir=Path("/tmp/foo"))

        result = config.to_dict()

        assert result == {"value": 5, "path_dir": "/tmp/foo"}

    def test_to_json_uses_utf8(self) -> None:
        """JSON payload includes the configured values."""
        config = SampleConfig(value=12, path_dir=Path("./bar"))

        json_str = config.to_json(indent=2)

        assert '"value": 12' in json_str
        assert '"path_dir": "bar"' in json_str

    def test_save_to_file_persists_configuration(self) -> None:
        """Persist configuration to disk via JSON payload."""
        config = SampleConfig(value=15, path_dir=Path("./baz"))

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "config.json"

            config.save_to_file(output_path)

            assert output_path.exists()
            loaded = SampleConfig.from_json_file(output_path)
            assert loaded == config

    def test_validate_allows_valid_state(self) -> None:
        """Custom validate hook should no-op when values are valid."""
        config = SampleConfig(value=1, path_dir=Path("./runs"))

        config.validate()  # Should not raise.

    def test_validate_raises_on_invalid_state(self) -> None:
        """Custom validate hook should raise ValueError on invalid state."""
        config = SampleConfig(value=-1, path_dir=Path("./runs"))

        with pytest.raises(ValueError):
            config.validate()

    def test_dataclass_is_immutable(self) -> None:
        """dataclass(frozen=True) ensures attributes cannot mutate."""
        config = SampleConfig(value=3, path_dir=Path("./frozen"))

        with pytest.raises(AttributeError):
            config.value = 4
