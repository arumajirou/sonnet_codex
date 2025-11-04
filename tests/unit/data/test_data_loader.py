"""Tests for the DataLoader utility."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from nf_auto_runner.data import DataLoader, EncodingError


@pytest.fixture
def loader() -> DataLoader:
    """Return a fresh DataLoader instance for each test."""
    return DataLoader()


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    """Create a simple CSV file conforming to the canonical schema."""
    path = tmp_path / "sample.csv"
    path.write_text(
        "\n".join(
            [
                "unique_id,ds,y",
                "store_1,2025-01-01,100.0",
                "store_1,2025-01-02,110.0",
                "store_2,2025-01-01,200.0",
                "store_2,2025-01-02,210.0",
            ]
        ),
        encoding="utf-8",
    )
    return path


@pytest.fixture
def sample_parquet(tmp_path: Path) -> Path:
    """Create a Parquet file with the canonical schema."""
    pytest.importorskip("pyarrow")
    df = pd.DataFrame(
        {
            "unique_id": ["store_1", "store_1", "store_2", "store_2"],
            "ds": pd.to_datetime(
                ["2025-01-01", "2025-01-02", "2025-01-01", "2025-01-02"]
            ),
            "y": [100.0, 110.0, 200.0, 210.0],
        }
    )
    path = tmp_path / "sample.parquet"
    df.to_parquet(path, index=False)
    return path


def test_load_csv_success(loader: DataLoader, sample_csv: Path) -> None:
    """Ensure CSV files load into DataFrames containing required columns."""
    df = loader.load_csv(sample_csv)

    assert len(df) == 4
    assert set(df.columns) >= {"unique_id", "ds", "y"}
    assert set(df["unique_id"]) == {"store_1", "store_2"}


def test_load_csv_not_found(loader: DataLoader, tmp_path: Path) -> None:
    """Expect FileNotFoundError when the CSV path does not exist."""
    missing = tmp_path / "missing.csv"
    with pytest.raises(FileNotFoundError):
        loader.load_csv(missing)


def test_load_csv_missing_columns(loader: DataLoader, tmp_path: Path) -> None:
    """Ensure missing required columns raise ValueError."""
    path = tmp_path / "invalid.csv"
    path.write_text(
        "\n".join(["id,date,value", "1,2025-01-01,100"]),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Missing required columns"):
        loader.load_csv(path)


def test_load_csv_with_chunksize(loader: DataLoader, sample_csv: Path) -> None:
    """Ensure chunked CSV reads are materialised into a single DataFrame."""
    df = loader.load_csv(sample_csv, chunksize=2)

    assert len(df) == 4
    assert isinstance(df, pd.DataFrame)


def test_load_csv_encoding_error(loader: DataLoader, tmp_path: Path) -> None:
    """Raise EncodingError when decoding fails with the provided encoding."""
    path = tmp_path / "shiftjis.csv"
    invalid_payload = b"unique_id,ds,y\n\x80\x80,2025-01-01,100.0\n"
    path.write_bytes(invalid_payload)

    with pytest.raises(EncodingError):
        loader.load_csv(path, encoding="utf-8")


def test_load_parquet_success(loader: DataLoader, sample_parquet: Path) -> None:
    """Ensure Parquet files load successfully when schema is valid."""
    df = loader.load_parquet(sample_parquet)

    assert len(df) == 4
    assert set(df.columns) >= {"unique_id", "ds", "y"}


def test_load_parquet_missing_columns(loader: DataLoader, tmp_path: Path) -> None:
    """Parquet files missing required columns should raise ValueError."""
    pytest.importorskip("pyarrow")
    df = pd.DataFrame(
        {
            "unique_id": ["store_1"],
            "ds": pd.to_datetime(["2025-01-01"]),
        }
    )
    path = tmp_path / "invalid.parquet"
    df.to_parquet(path, index=False)

    with pytest.raises(ValueError, match="Missing required columns"):
        loader.load_parquet(path)


def test_load_parquet_missing_file(loader: DataLoader, tmp_path: Path) -> None:
    """Missing Parquet files should raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        loader.load_parquet(tmp_path / "missing.parquet")


def test_auto_detect_encoding_utf8(loader: DataLoader, sample_csv: Path) -> None:
    """auto_detect_encoding should return UTF-8 for UTF-8 files."""
    encoding = loader.auto_detect_encoding(sample_csv)
    assert encoding.lower() in {"utf-8", "ascii"}


def test_auto_detect_encoding_cache(loader: DataLoader, sample_csv: Path) -> None:
    """Detected encodings should be cached by file path."""
    first = loader.auto_detect_encoding(sample_csv)
    second = loader.auto_detect_encoding(sample_csv)

    assert first == second
    assert str(sample_csv) in loader.encoding_cache


def test_auto_detect_encoding_missing_file(loader: DataLoader, tmp_path: Path) -> None:
    """Expect FileNotFoundError when detecting encoding for missing file."""
    missing = tmp_path / "missing.csv"
    with pytest.raises(FileNotFoundError):
        loader.auto_detect_encoding(missing)


def test_infer_schema(loader: DataLoader) -> None:
    """infer_schema should return dtype strings for each column."""
    df = pd.DataFrame(
        {
            "unique_id": ["a", "b"],
            "ds": pd.to_datetime(["2025-01-01", "2025-01-02"]),
            "y": [1.0, 2.0],
            "temperature": [15.5, 16.2],
        }
    )

    schema = loader.infer_schema(df)

    assert schema["unique_id"].startswith("object")
    assert "datetime" in schema["ds"]
    assert "float" in schema["y"]
    assert "temperature" in schema


def test_load_dispatch_csv(loader: DataLoader, sample_csv: Path) -> None:
    """load should delegate to load_csv for CSV inputs."""
    df = loader.load(sample_csv)
    assert len(df) == 4


def test_load_dispatch_parquet(loader: DataLoader, sample_parquet: Path) -> None:
    """load should delegate to load_parquet for Parquet inputs."""
    df = loader.load(sample_parquet)
    assert len(df) == 4


def test_load_unsupported_format(loader: DataLoader, tmp_path: Path) -> None:
    """Unsupported extensions should raise ValueError."""
    with pytest.raises(ValueError, match="Unsupported file format"):
        loader.load(tmp_path / "data.xlsx")


def test_load_csv_value_error_passthrough(
    loader: DataLoader, sample_csv: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """ValueError that is not parse_dates-related should propagate."""

    def raise_value_error(*args: object, **kwargs: object) -> None:
        raise ValueError("general failure")

    monkeypatch.setattr(pd, "read_csv", raise_value_error)

    with pytest.raises(ValueError, match="general failure"):
        loader.load_csv(sample_csv, parse_dates=False)


def test_auto_detect_encoding_with_chardet_stub(
    loader: DataLoader, sample_csv: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Validate chardet integration and low-confidence fallback."""

    class StubChardet:
        def __init__(self) -> None:
            self.calls = 0

        def detect(self, _: bytes) -> dict[str, object]:
            self.calls += 1
            return {"encoding": "shift-jis", "confidence": 0.3}

    stub = StubChardet()
    monkeypatch.setattr(
        "nf_auto_runner.data.data_loader.chardet",
        stub,
        raising=False,
    )
    loader.encoding_cache.clear()

    encoding = loader.auto_detect_encoding(sample_csv)

    assert encoding == "utf-8"
    assert stub.calls == 1


def test_materialise_chunks_helpers() -> None:
    """Ensure helper handles iterators and generic iterables."""
    empty_result = DataLoader._materialise_chunks(iter([]))
    assert empty_result.empty

    df = pd.DataFrame(
        {
            "unique_id": ["a"],
            "ds": pd.to_datetime(["2025-01-01"]),
            "y": [1.0],
        }
    )
    combined = DataLoader._materialise_chunks([df])
    assert len(combined) == 1
