"""Tests for structured logging utilities."""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest

from nf_auto_runner.config.path import PathConfig
from nf_auto_runner.logging import LogContext, StructuredLogger


@pytest.fixture(autouse=True)
def reset_log_context() -> None:
    """Ensure log context is cleared between tests."""
    LogContext.clear()
    yield
    LogContext.clear()


def _read_single_entry(log_file: Path) -> dict[str, object]:
    contents = log_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(contents) == 1, contents
    return json.loads(contents[0])


def test_structured_logger_writes_json_line(tmp_path: Path) -> None:
    log_file = tmp_path / "logs" / "run-001.jsonl"
    logger = StructuredLogger.get_logger(
        "nf_auto_runner.tests",
        log_file=log_file,
        log_to_console=False,
    )

    logger.info("Training started", run_id="run-001", epoch=1)

    entry = _read_single_entry(log_file)
    assert entry["message"] == "Training started"
    assert entry["level"] == "INFO"
    assert entry["logger"] == "nf_auto_runner.tests"
    assert entry["run_id"] == "run-001"
    assert entry["epoch"] == 1
    assert "hostname" in entry["context"]
    assert "pid" in entry["context"]


def test_log_level_threshold_filters_entries(tmp_path: Path) -> None:
    log_file = tmp_path / "logs" / "filtered.jsonl"
    logger = StructuredLogger.get_logger(
        "nf_auto_runner.tests",
        level="WARNING",
        log_file=log_file,
        log_to_console=False,
    )

    logger.info("Skipped info")  # Should be filtered out
    assert not log_file.exists()

    logger.error("Failure detected", code=503)
    entry = _read_single_entry(log_file)
    assert entry["level"] == "ERROR"
    assert entry["code"] == 503
    assert "hostname" in entry["context"]


def test_log_context_is_included(tmp_path: Path) -> None:
    LogContext.set_correlation_id("cid-123")
    LogContext.set_run_id("ctx-run")

    log_file = tmp_path / "logs" / "context.jsonl"
    logger = StructuredLogger.get_logger(
        "nf_auto_runner.tests",
        log_file=log_file,
        log_to_console=False,
    )

    logger.info("Context capture", user="alice")

    entry = _read_single_entry(log_file)
    assert entry["correlation_id"] == "cid-123"
    assert entry["run_id"] == "ctx-run"
    assert entry["user"] == "alice"
    assert "hostname" in entry["context"]


def test_structured_logger_for_run_uses_path_config(tmp_path: Path) -> None:
    path_config = PathConfig(
        data_csv=tmp_path / "data.csv",
        output_dir=tmp_path / "outputs",
        log_dir=tmp_path / "outputs" / "logs",
        project_root=tmp_path,
        model_dir=tmp_path / "outputs" / "models",
        artifact_dir=tmp_path / "outputs" / "artifacts",
        checkpoint_dir=tmp_path / "outputs" / "checkpoints",
        plot_dir=tmp_path / "outputs" / "plots",
    )

    logger = StructuredLogger.for_run(
        "nf_auto_runner.tests",
        path_config,
        "run-xyz",
        log_to_console=False,
    )

    logger.info("Run specific entry", stage="training")

    run_log_file = path_config.get_log_path("run-xyz")
    entry = _read_single_entry(run_log_file)
    assert run_log_file == tmp_path / "outputs" / "logs" / "run-xyz.jsonl"
    assert entry["run_id"] == "run-xyz"
    assert entry["stage"] == "training"


def test_log_execution_time_records_duration(tmp_path: Path) -> None:
    log_file = tmp_path / "logs" / "timing.jsonl"
    logger = StructuredLogger.get_logger(
        "nf_auto_runner.tests",
        log_file=log_file,
        log_to_console=False,
    )

    with logger.log_execution_time("data_loading", dataset="train.csv"):
        pass

    entry = _read_single_entry(log_file)
    assert entry["message"].startswith("Operation completed: data_loading")
    assert entry["operation"] == "data_loading"
    assert entry["dataset"] == "train.csv"
    assert entry["duration_seconds"] >= 0.0
    assert "hostname" in entry["context"]


def test_extra_payload_overrides_runtime_context(tmp_path: Path) -> None:
    log_file = tmp_path / "logs" / "extra.jsonl"
    logger = StructuredLogger.get_logger(
        "nf_auto_runner.tests",
        log_file=log_file,
        log_to_console=False,
    )

    logger.info(
        "Extra context",
        extra={
            "hostname": "custom-host",
            "details": {"role": "trainer"},
        },
    )

    entry = _read_single_entry(log_file)
    assert entry["context"]["hostname"] == "custom-host"
    assert entry["context"]["details"] == {"role": "trainer"}


def test_invalid_log_level_raises() -> None:
    with pytest.raises(ValueError):
        StructuredLogger.get_logger("nf_auto_runner.tests", level="TRACE")


def test_missing_log_file_when_required(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        StructuredLogger.get_logger(
            "nf_auto_runner.tests",
            log_to_console=False,
            log_to_file=True,
        )


def test_log_context_generates_uuid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("nf_auto_runner.logging.structured.uuid4", lambda: "generated-id")
    generated = LogContext.set_correlation_id()
    assert generated == "generated-id"
    assert LogContext.get_correlation_id() == "generated-id"


def test_log_context_user_id_roundtrip() -> None:
    LogContext.set_user_id("user-123")
    assert LogContext.get_user_id() == "user-123"
    assert LogContext.get_context()["user_id"] == "user-123"


def test_helper_shortcuts_call_log(tmp_path: Path) -> None:
    log_file = tmp_path / "logs" / "shortcut.jsonl"
    logger = StructuredLogger.get_logger(
        "nf_auto_runner.tests",
        log_file=log_file,
        log_to_console=False,
        level="DEBUG",
    )

    logger.debug("debug message")
    logger.warning("warn message")
    logger.error("error message")
    logger.critical("critical message", status="fatal")

    entries = [json.loads(line) for line in log_file.read_text(encoding="utf-8").splitlines()]
    assert [e["level"] for e in entries] == ["DEBUG", "WARNING", "ERROR", "CRITICAL"]
    assert entries[-1]["status"] == "fatal"


def test_runtime_context_injects_gpu_id(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    log_file = tmp_path / "logs" / "gpu.jsonl"
    monkeypatch.setattr("nf_auto_runner.logging.structured._detect_gpu_id", lambda: 3)
    logger = StructuredLogger.get_logger(
        "nf_auto_runner.tests", log_file=log_file, log_to_console=False
    )

    logger.info("GPU context check")
    entry = _read_single_entry(log_file)
    assert entry["context"]["gpu_id"] == 3


def test_detect_gpu_id_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    class _DummyCUDA:  # pragma: no cover - helper for test
        @staticmethod
        def is_available() -> bool:
            return False

    dummy_torch = type(
        "DummyTorch",
        (),
        {"cuda": _DummyCUDA},
    )
    monkeypatch.setitem(sys.modules, "torch", dummy_torch)
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "1,2")

    from nf_auto_runner.logging.structured import _detect_gpu_id

    assert _detect_gpu_id() == 1


def test_logger_log_invalid_level_raises(tmp_path: Path) -> None:
    logger = StructuredLogger.get_logger(
        "nf_auto_runner.tests",
        log_file=tmp_path / "logs" / "out.jsonl",
        log_to_console=False,
    )
    with pytest.raises(ValueError):
        logger.log("TRACE", "invalid")


def test_logger_emits_experiment_id_to_console() -> None:
    buffer = io.StringIO()
    logger = StructuredLogger.get_logger(
        "nf_auto_runner.tests",
        log_to_console=True,
        log_to_file=False,
        stream=buffer,
    )

    logger.info("Console emission", experiment_id="exp-123")
    payload = json.loads(buffer.getvalue().strip())
    assert payload["experiment_id"] == "exp-123"
    assert "hostname" in payload["context"]


def test_uuid4_returns_string() -> None:
    from nf_auto_runner.logging.structured import uuid4

    generated = uuid4()
    assert isinstance(generated, str)
    assert len(generated) == 36
