"""Structured logging utilities following project specifications."""

from __future__ import annotations

import contextvars
import json
import os
import socket
import sys
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from multiprocessing import current_process
from pathlib import Path
from typing import TYPE_CHECKING, Any, TextIO

if TYPE_CHECKING:  # pragma: no cover - typing only
    from ..config.path import PathConfig

_LEVEL_MAP: dict[str, int] = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50,
}


@dataclass(frozen=True)
class StructuredLogEntry:
    """Representation of a single structured log entry."""

    timestamp: str
    level: str
    logger: str
    message: str
    attributes: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        """Return JSON representation compliant with project requirements."""
        payload: dict[str, Any] = {
            "timestamp": self.timestamp,
            "level": self.level,
            "logger": self.logger,
            "message": self.message,
        }
        if self.attributes:
            payload.update(self.attributes)
        if self.context:
            payload["context"] = self.context
        return json.dumps(payload, ensure_ascii=False, default=str)


class LogContext:
    """Manage per-execution logging context shared across entries."""

    _correlation_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
        "correlation_id", default=None
    )
    _run_id: contextvars.ContextVar[str | None] = contextvars.ContextVar("run_id", default=None)
    _user_id: contextvars.ContextVar[str | None] = contextvars.ContextVar("user_id", default=None)

    @staticmethod
    def set_correlation_id(correlation_id: str | None = None) -> str:
        """Set correlation identifier, generating one when absent."""
        if correlation_id is None:
            correlation_id = uuid4()
        LogContext._correlation_id.set(correlation_id)
        return correlation_id

    @staticmethod
    def get_correlation_id() -> str | None:
        """Return currently active correlation identifier."""
        return LogContext._correlation_id.get()

    @staticmethod
    def set_run_id(run_id: str) -> None:
        """Associate run identifier with the current context."""
        LogContext._run_id.set(run_id)

    @staticmethod
    def get_run_id() -> str | None:
        """Retrieve run identifier stored in the context."""
        return LogContext._run_id.get()

    @staticmethod
    def set_user_id(user_id: str) -> None:
        """Associate user identifier with the current context."""
        LogContext._user_id.set(user_id)

    @staticmethod
    def get_user_id() -> str | None:
        """Return user identifier from the context."""
        return LogContext._user_id.get()

    @staticmethod
    def get_context() -> dict[str, Any]:
        """Provide a shallow copy of active context values."""
        context: dict[str, Any] = {}

        if (correlation_id := LogContext.get_correlation_id()) is not None:
            context["correlation_id"] = correlation_id
        if (run_id := LogContext.get_run_id()) is not None:
            context["run_id"] = run_id
        if (user_id := LogContext.get_user_id()) is not None:
            context["user_id"] = user_id

        return context

    @staticmethod
    def clear() -> None:
        """Reset all stored context information."""
        LogContext._correlation_id.set(None)
        LogContext._run_id.set(None)
        LogContext._user_id.set(None)


class StructuredLogger:
    """Emit structured JSONL log entries to console and disk."""

    def __init__(
        self,
        name: str,
        *,
        level: str = "INFO",
        log_file: Path | None = None,
        log_to_console: bool = True,
        log_to_file: bool = True,
        add_context: bool = True,
        base_context: dict[str, Any] | None = None,
        stream: TextIO = sys.stdout,
    ) -> None:
        self.name = name
        self._level_name = level.upper()
        if self._level_name not in _LEVEL_MAP:
            raise ValueError(f"Unsupported log level: {level!r}")
        self._level_threshold = _LEVEL_MAP[self._level_name]
        self._log_file = Path(log_file) if log_file is not None else None
        self._log_to_console = log_to_console
        self._log_to_file = log_to_file
        if self._log_to_file and self._log_file is None:
            raise ValueError("log_file must be provided when log_to_file is True.")
        self._add_context = add_context
        self._base_context = dict(base_context) if base_context else {}
        self._stream = stream

    @classmethod
    def get_logger(
        cls,
        name: str,
        *,
        level: str = "INFO",
        log_file: Path | None = None,
        log_to_console: bool = True,
        log_to_file: bool = True,
        add_context: bool = True,
        stream: TextIO = sys.stdout,
        **initial_context: Any,
    ) -> StructuredLogger:
        """Factory returning logger with optional initial context."""
        return cls(
            name,
            level=level,
            log_file=log_file,
            log_to_console=log_to_console,
            log_to_file=log_to_file,
            add_context=add_context,
            base_context=initial_context or None,
            stream=stream,
        )

    @classmethod
    def for_run(
        cls,
        name: str,
        path_config: PathConfig,
        run_id: str,
        *,
        level: str = "INFO",
        log_to_console: bool = True,
        log_to_file: bool = True,
        add_context: bool = True,
        stream: TextIO = sys.stdout,
        **additional_context: Any,
    ) -> StructuredLogger:
        """Create logger targeting the JSONL file allocated for a run."""
        log_path = path_config.get_log_path(run_id)
        base_context = {"run_id": run_id}
        base_context.update(additional_context)
        return cls(
            name,
            level=level,
            log_file=log_path,
            log_to_console=log_to_console,
            log_to_file=log_to_file,
            add_context=add_context,
            base_context=base_context,
            stream=stream,
        )

    def log(
        self,
        level: str,
        message: str,
        *,
        run_id: str | None = None,
        experiment_id: str | None = None,
        extra: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Emit log entry at specified level with structured payload."""
        level_name = level.upper()
        if level_name not in _LEVEL_MAP:
            raise ValueError(f"Unsupported log level: {level!r}")
        if _LEVEL_MAP[level_name] < self._level_threshold:
            return

        attributes: dict[str, Any] = {}
        if self._base_context:
            attributes.update(self._base_context)

        if self._add_context:
            attributes.update(LogContext.get_context())

        if run_id is not None:
            attributes["run_id"] = run_id
        if experiment_id is not None:
            attributes["experiment_id"] = experiment_id

        if extra:
            extra_context = dict(extra)
        else:
            extra_context = {}
        if kwargs:
            attributes.update(kwargs)

        top_level: dict[str, Any] = {
            key: value
            for key, value in attributes.items()
            if value is not None and key != "context"
        }

        context_payload: dict[str, Any] = {}
        if self._add_context:
            context_payload.update(_runtime_context())
        if extra_context:
            context_payload.update(extra_context)

        entry = StructuredLogEntry(
            timestamp=_current_timestamp(),
            level=level_name,
            logger=self.name,
            message=message,
            attributes=top_level,
            context=context_payload,
        )
        self._write_entry(entry)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Shortcut for DEBUG level entries."""
        self.log("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Shortcut for INFO level entries."""
        self.log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Shortcut for WARNING level entries."""
        self.log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Shortcut for ERROR level entries."""
        self.log("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Shortcut for CRITICAL level entries."""
        self.log("CRITICAL", message, **kwargs)

    @contextmanager
    def log_execution_time(self, operation: str, **metadata: Any) -> Iterator[None]:
        """Context manager logging execution duration of an operation."""
        start = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start
            payload = {"operation": operation, "duration_seconds": duration}
            payload.update(metadata)
            self.info(
                f"Operation completed: {operation}",
                **payload,
            )

    def _write_entry(self, entry: StructuredLogEntry) -> None:
        """Persist entry to configured destinations."""
        json_line = entry.to_json()

        if self._log_to_file and self._log_file is not None:
            self._log_file.parent.mkdir(parents=True, exist_ok=True)
            with self._log_file.open("a", encoding="utf-8") as file_handle:
                file_handle.write(json_line + "\n")

        if self._log_to_console:
            print(json_line, file=self._stream)


def _current_timestamp() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(UTC).isoformat()


def _runtime_context() -> dict[str, Any]:
    """Collect runtime diagnostics for log context."""
    context: dict[str, Any] = {
        "hostname": socket.gethostname(),
        "pid": os.getpid(),
        "process_name": current_process().name,
        "thread_id": threading.get_ident(),
        "thread_name": threading.current_thread().name,
    }
    gpu_id = _detect_gpu_id()
    if gpu_id is not None:
        context["gpu_id"] = gpu_id
    return context


def _detect_gpu_id() -> int | None:
    """Best-effort detection of active CUDA device."""
    try:
        import torch

        if torch.cuda.is_available():  # pragma: no cover - depends on runtime
            return int(torch.cuda.current_device())
    except Exception:  # pragma: no cover - torch optional
        pass

    visible_devices = os.getenv("CUDA_VISIBLE_DEVICES")
    if visible_devices:
        first_device = visible_devices.split(",")[0].strip()
        if first_device and first_device.isdigit():
            return int(first_device)
    return None


def uuid4() -> str:
    """Generate a RFC 4122 UUID4 string; isolated for test patching."""
    from uuid import uuid4 as _uuid4

    return str(_uuid4())
