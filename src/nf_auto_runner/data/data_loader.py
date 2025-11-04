"""Data loading utilities for time series datasets."""

from __future__ import annotations

import logging
from collections.abc import Iterator
from importlib import import_module
from pathlib import Path
from typing import Any, cast

import pandas as pd  # type: ignore[import-untyped]

_chardet: Any
try:  # pragma: no cover - optional dependency
    _chardet = import_module("chardet")
except ModuleNotFoundError:  # pragma: no cover - executed when chardet missing
    _chardet = None
chardet = cast(Any, _chardet)

logger = logging.getLogger(__name__)

DEFAULT_REQUIRED_COLUMNS: tuple[str, str, str] = ("unique_id", "ds", "y")
MIN_ENCODING_CONFIDENCE = 0.7


class EncodingError(RuntimeError):
    """Raised when a text file cannot be decoded using the detected encoding."""


class DataLoader:
    """Load tabular datasets and normalise them to the canonical schema."""

    def __init__(self) -> None:
        """Initialise the loader with an encoding detection cache."""
        self.encoding_cache: dict[str, str] = {}

    def load_csv(
        self,
        file_path: Path,
        *,
        encoding: str | None = None,
        chunksize: int | None = None,
        date_format: str | None = None,
        parse_dates: bool = True,
        infer_datetime_format: bool = True,
        required_columns: list[str] | None = None,
    ) -> pd.DataFrame:
        """Load a CSV file and ensure the canonical schema is present."""
        path_obj = Path(file_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {path_obj}")

        logger.info("Loading CSV file: %s", path_obj)

        active_encoding = encoding or self.auto_detect_encoding(path_obj)

        parse_dates_arg: bool | list[str] = ["ds"] if parse_dates else False

        try:
            data = pd.read_csv(
                path_obj,
                encoding=active_encoding,
                chunksize=chunksize,
                parse_dates=parse_dates_arg,
                date_format=date_format,
                infer_datetime_format=infer_datetime_format,
            )
        except UnicodeDecodeError as exc:
            logger.error("Failed to decode CSV %s: %s", path_obj, exc)
            raise EncodingError(f"Failed to decode file {path_obj} with {active_encoding}") from exc
        except ValueError as exc:
            error_message = str(exc)
            if parse_dates and "parse_dates" in error_message:
                logger.warning(
                    "parse_dates failed for %s (%s); retrying without date parsing",
                    path_obj,
                    error_message,
                )
                data = pd.read_csv(
                    path_obj,
                    encoding=active_encoding,
                    chunksize=chunksize,
                    parse_dates=False,
                    date_format=date_format,
                    infer_datetime_format=infer_datetime_format,
                )
            else:
                logger.error("Failed to read CSV %s: %s", path_obj, exc)
                raise
        except Exception as exc:  # pragma: no cover - passthrough for unexpected errors
            logger.error("Failed to read CSV %s: %s", path_obj, exc)
            raise

        df = self._materialise_chunks(data)

        self._ensure_required_columns(df, required_columns)

        logger.info(
            "Successfully loaded CSV: %s rows, %s columns",
            len(df),
            len(df.columns),
        )
        return df

    def load_parquet(
        self,
        file_path: Path,
        *,
        columns: list[str] | None = None,
        filters: list[tuple[Any, ...]] | None = None,
    ) -> pd.DataFrame:
        """Load a Parquet file while validating the canonical schema."""
        path_obj = Path(file_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {path_obj}")

        logger.info("Loading Parquet file: %s", path_obj)

        try:
            df = pd.read_parquet(path_obj, columns=columns, filters=filters)
        except Exception as exc:  # pragma: no cover - passthrough for unexpected errors
            logger.error("Failed to read Parquet %s: %s", path_obj, exc)
            raise

        self._ensure_required_columns(df, None)

        logger.info(
            "Successfully loaded Parquet: %s rows, %s columns",
            len(df),
            len(df.columns),
        )
        return df

    def auto_detect_encoding(self, file_path: Path, sample_size: int = 10_000) -> str:
        """Detect the file encoding, caching results for subsequent calls."""
        path_obj = Path(file_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {path_obj}")
        cache_key = str(path_obj)
        if cache_key in self.encoding_cache:
            return self.encoding_cache[cache_key]

        with path_obj.open("rb") as handle:
            raw_data = handle.read(sample_size)

        if chardet is None:
            logger.info("chardet not available; defaulting to utf-8 for %s", path_obj)
            encoding = "utf-8"
        else:
            detection = chardet.detect(raw_data)
            encoding = detection.get("encoding")
            confidence = detection.get("confidence", 0.0) or 0.0

            logger.debug(
                "Encoding detection for %s: encoding=%s confidence=%.2f",
                path_obj,
                encoding,
                confidence,
            )

            if not encoding or confidence < MIN_ENCODING_CONFIDENCE:
                logger.warning(
                    "Low confidence encoding detection for %s "
                    "(confidence %.2f). Falling back to utf-8.",
                    path_obj,
                    confidence,
                )
                encoding = "utf-8"

        self.encoding_cache[cache_key] = encoding
        return encoding

    def infer_schema(self, df: pd.DataFrame) -> dict[str, str]:
        """Return a mapping of column names to dtype strings."""
        schema: dict[str, str] = {}
        for column in df.columns:
            schema[column] = str(df[column].dtype)
        logger.debug("Inferred schema: %s", schema)
        return schema

    def load(self, file_path: Path, **kwargs: Any) -> pd.DataFrame:
        """Load a dataset, dispatching to the appropriate reader by suffix."""
        suffix = Path(file_path).suffix.lower()
        if suffix == ".csv":
            return self.load_csv(file_path, **kwargs)
        if suffix in {".parquet", ".pq"}:
            return self.load_parquet(file_path, **kwargs)
        raise ValueError(
            f"Unsupported file format: {suffix}. Supported formats: .csv, .parquet, .pq"
        )

    def _ensure_required_columns(
        self, df: pd.DataFrame, required_columns: list[str] | None
    ) -> None:
        columns = required_columns or list(DEFAULT_REQUIRED_COLUMNS)
        missing = set(columns) - set(df.columns)
        if missing:
            raise ValueError(
                f"Missing required columns: {sorted(missing)}. "
                f"Found columns: {list(df.columns)}"
            )

    @staticmethod
    def _materialise_chunks(
        data: pd.DataFrame | Iterator[pd.DataFrame],
    ) -> pd.DataFrame:
        if isinstance(data, pd.DataFrame):
            return data
        if isinstance(data, Iterator):
            chunks = list(data)
            if not chunks:
                return pd.DataFrame()
            return pd.concat(chunks, ignore_index=True)
        if hasattr(data, "__iter__"):
            return pd.concat(list(data), ignore_index=True)
        return pd.DataFrame(data)  # pragma: no cover - defensive fallback
