"""Abstract base class for configuration objects."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any, Dict, Optional, Type, TypeVar, get_type_hints
import json
T = TypeVar("T", bound="Config")


@dataclass(frozen=True)
class Config(ABC):
    """Base configuration type."""

    @classmethod
    @abstractmethod
    def from_env(cls: Type[T]) -> T:
        """Construct configuration from environment variables."""

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Construct configuration from dictionary data."""
        converted: Dict[str, Any] = {}
        dataclass_fields = {field.name: field for field in fields(cls)} if hasattr(cls, "__dataclass_fields__") else {}
        type_hints = get_type_hints(cls)
        for key, value in data.items():
            if dataclass_fields and key not in dataclass_fields:
                continue
            target_type = type_hints.get(key)
            if isinstance(value, str) and (
                target_type is Path or key.endswith(("_path", "_dir"))
            ):
                converted[key] = Path(value)
            else:
                converted[key] = value
        return cls(**converted)

    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        """Construct configuration from JSON string."""
        payload = json.loads(json_str)
        if not isinstance(payload, dict):
            raise TypeError("JSON content must decode to a dictionary.")
        return cls.from_dict(payload)

    @classmethod
    def from_json_file(cls: Type[T], file_path: Path) -> T:
        """Construct configuration from JSON file located at `file_path`."""
        path_obj = Path(file_path)
        with path_obj.open("r", encoding="utf-8") as file_handle:
            return cls.from_json(file_handle.read())

    def validate(self) -> None:
        """Validate configuration fields."""

    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        result: Dict[str, Any] = {}
        for key, value in asdict(self).items():
            if isinstance(value, Path):
                result[key] = str(value)
            else:
                result[key] = value
        return result

    def to_json(self, indent: Optional[int] = 2) -> str:
        """Serialize configuration to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save_to_file(self, file_path: Path, indent: Optional[int] = 2) -> None:
        """Persist configuration to JSON file."""
        path_obj = Path(file_path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        path_obj.write_text(self.to_json(indent=indent), encoding="utf-8")
