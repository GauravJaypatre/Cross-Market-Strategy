"""Data loader with explicit provenance logging and hard-failure guards.

Production runs MUST use real market data (local files or yfinance).
Synthetic data is strictly quarantined in tests/ and cannot be used here.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re
from typing import Optional, Tuple
import pandas as pd


class DataSourceError(Exception):
    """Raised when market data cannot be retrieved from any authorized production source."""
    pass


@dataclass(frozen=True)
class DataProvenance:
    """Provenance audit metadata for an index data series."""
    vendor: str                    # 'local_csv' | 'yfinance' | 'stooq'
    source_identifier: str        # Filepath or ticker
    sha256: Optional[str]         # SHA256 of file if local_csv
    retrieval_timestamp_utc: str  # ISO 8601 UTC
    row_count: int
    data_start: str               # YYYY-MM-DD
    data_end: str                 # YYYY-MM-DD

    def to_dict(self) -> dict:
        return {
            "vendor": self.vendor,
            "source_identifier": self.source_identifier,
            "sha256": self.sha256,
            "retrieval_timestamp_utc": self.retrieval_timestamp_utc,
            "row_count": self.row_count,
            "data_start": self.data_start,
            "data_end": self.data_end,
        }


def _compute_sha256(filepath: Path) -> str:
    """Compute SHA256 checksum of a file for audit provenance."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def _sanitize_name(name: str) -> str:
    """Sanitize strings for filesystem matching."""
    return re.sub(r"[^\w\-_.]", "_", name)


def _standardize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure DataFrame meets standard OHLCV contract."""
    # Find column names case-insensitively
    cols_map = {}
    has_literal_close = any(str(c).strip().lower() == "close" for c in df.columns)
    for col in df.columns:
        c_low = str(col).strip().lower()
        if c_low in ["open", "high", "low", "close", "volume"]:
            cols_map[col] = c_low
        elif c_low in ["adj close", "adj_close"] and not has_literal_close:
            cols_map[col] = "close"

    df = df.rename(columns=cols_map)
    df = df.loc[:, ~df.columns.duplicated(keep="first")]
    required = ["open", "high", "low", "close"]
    for req in required:
        if req not in df.columns:
            raise ValueError(f"Missing required price column: '{req}'")

    if "volume" not in df.columns:
        df["volume"] = 0.0

    # Clean index to DatetimeIndex
    if not isinstance(df.index, pd.DatetimeIndex):
        if "date" in [str(c).lower() for c in df.columns]:
            date_col = [c for c in df.columns if str(c).lower() == "date"][0]
            df[date_col] = pd.to_datetime(df[date_col])
            df = df.set_index(date_col)
        else:
            df.index = pd.to_datetime(df.index)

    df.index = pd.to_datetime(df.index).tz_localize(None)
    df.index.name = "date"
    df = df.sort_index()
    df = df[~df.index.duplicated(keep="first")]

    # Cast to float64
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["open", "high", "low", "close"])
    return df[["open", "high", "low", "close", "volume"]]


def _fetch_stooq_data(ticker: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
    """
    Attempt to fetch daily OHLCV from Stooq with session handling.
    Supports standard Stooq tickers (e.g. ^spx, ^dji, ^nkx, ^dax, etc.).
    """
    import urllib.request
    import io

    stooq_sym = ticker.lower()
    mapping = {
        "^gspc": "^spx",
        "^ixic": "^ndq",
        "^dji": "^dji",
        "^n225": "^nkx",
        "^gdaxi": "^dax",
        "^ftse": "^ukx",
        "^fchi": "^cac",
    }
    stooq_sym = mapping.get(stooq_sym, stooq_sym)

    url = f"https://stooq.com/q/d/l/?s={stooq_sym}&i=d"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            if b"<html" in data.lower() or len(data) < 50:
                return None
            df = pd.read_csv(io.BytesIO(data))
            return df
    except Exception:
        return None


def load_index_data(
    data_source_id: str,
    country: str,
    index_name: str,
    start_date: str = "2011-01-01",
    end_date: str = "2025-12-31",
    data_dir: Optional[str | Path] = None,
) -> Tuple[pd.DataFrame, DataProvenance]:
    """
    Load OHLCV data for an index from local file, yfinance, or Stooq fallback.
    
    CRITICAL: Never falls back to synthetic data. If neither local file, yfinance, nor Stooq
    succeeds, raises DataSourceError.
    """
    retrieval_time = datetime.now(timezone.utc).isoformat()
    errors_encountered = []

    # 1. Attempt local file lookup
    candidate_paths = []
    if data_dir:
        dir_path = Path(data_dir)
        clean_id = _sanitize_name(data_source_id)
        clean_idx = _sanitize_name(index_name)
        clean_country = _sanitize_name(country)

        candidate_paths.extend([
            dir_path / f"{data_source_id}.csv",
            dir_path / f"{data_source_id.lstrip('^')}.csv",
            dir_path / f"{clean_id}.csv",
            dir_path / f"{clean_id.lstrip('_')}.csv",
            dir_path / f"{clean_idx}.csv",
            dir_path / f"{clean_country}_{clean_idx}.csv",
            dir_path / f"{data_source_id}.parquet",
            dir_path / f"{clean_id}.parquet",
        ])

    for p in candidate_paths:
        if p.exists():
            try:
                if p.suffix == ".parquet":
                    raw_df = pd.read_parquet(p)
                else:
                    raw_df = pd.read_csv(p)

                df = _standardize_ohlcv(raw_df)
                df = df.loc[start_date:end_date]

                if not df.empty:
                    try:
                        rel_source = p.relative_to(Path.cwd()).as_posix()
                    except Exception:
                        rel_source = f"data/{p.name}"
                    provenance = DataProvenance(
                        vendor="local_csv",
                        source_identifier=rel_source,
                        sha256=_compute_sha256(p),
                        retrieval_timestamp_utc=retrieval_time,
                        row_count=len(df),
                        data_start=df.index.min().strftime("%Y-%m-%d"),
                        data_end=df.index.max().strftime("%Y-%m-%d"),
                    )
                    return df, provenance
                else:
                    errors_encountered.append(f"Local file {p} contained no data within range [{start_date}, {end_date}].")
            except Exception as e:
                errors_encountered.append(f"Error reading local file {p}: {e}")

    # 2. Attempt yfinance download
    try:
        import yfinance as yf
        ticker = data_source_id.strip()
        # Fetch with a generous window so technical indicators before start_date can be computed if needed
        data = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            progress=False,
            auto_adjust=False,
        )

        if data is not None and not data.empty:
            # Handle MultiIndex columns returned by newer yfinance
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = [col[0] for col in data.columns]

            df = _standardize_ohlcv(data)
            df = df.loc[start_date:end_date]

            if not df.empty:
                provenance = DataProvenance(
                    vendor="yfinance",
                    source_identifier=ticker,
                    sha256=None,
                    retrieval_timestamp_utc=retrieval_time,
                    row_count=len(df),
                    data_start=df.index.min().strftime("%Y-%m-%d"),
                    data_end=df.index.max().strftime("%Y-%m-%d"),
                )
                return df, provenance
            else:
                errors_encountered.append(f"yfinance download for {ticker} returned zero rows in date window.")
        else:
            errors_encountered.append(f"yfinance returned empty dataset for ticker {ticker}.")
    except Exception as e:
        errors_encountered.append(f"yfinance exception for {data_source_id}: {e}")

    # 3. Attempt Stooq download as second remote fallback
    try:
        stooq_df = _fetch_stooq_data(data_source_id, start_date, end_date)
        if stooq_df is not None and not stooq_df.empty:
            df = _standardize_ohlcv(stooq_df)
            df = df.loc[start_date:end_date]
            if not df.empty:
                provenance = DataProvenance(
                    vendor="stooq",
                    source_identifier=data_source_id,
                    sha256=None,
                    retrieval_timestamp_utc=retrieval_time,
                    row_count=len(df),
                    data_start=df.index.min().strftime("%Y-%m-%d"),
                    data_end=df.index.max().strftime("%Y-%m-%d"),
                )
                return df, provenance
            else:
                errors_encountered.append(f"Stooq download for {data_source_id} returned zero rows in date window.")
        else:
            errors_encountered.append(f"Stooq returned empty/unreachable dataset for {data_source_id}.")
    except Exception as e:
        errors_encountered.append(f"Stooq exception for {data_source_id}: {e}")

    # 4. Hard failure: No silent synthetic fallback in production
    error_msg = (
        f"HARD FAILURE: Unable to load market data for '{index_name}' ({country}, id: '{data_source_id}').\n"
        f"Attempts made:\n  - " + "\n  - ".join(errors_encountered) + "\n"
        "Production runs will NEVER fall back to synthetic data. Ensure local files exist or network allows yfinance/stooq access."
    )
    raise DataSourceError(error_msg)
