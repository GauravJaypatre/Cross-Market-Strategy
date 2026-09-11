"""Configuration models and loaders for cross-market backtesting system."""

from dataclasses import dataclass
from pathlib import Path
from typing import List
import yaml


@dataclass(frozen=True)
class UniverseItem:
    """Represents a single country-index target."""
    country: str
    index_name: str
    data_source_id: str
    currency: str


def load_universe(filepath: str | Path) -> List[UniverseItem]:
    """
    Load universe items from a YAML configuration file.
    Schema expected in universe.yaml:
      indices:
        - country: "United States"
          index_name: "S&P 500"
          data_source_id: "^GSPC"
          currency: "USD"
      (or top-level list)
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Universe config file not found: {filepath}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    items: List[UniverseItem] = []
    raw_list = data.get("indices", data) if isinstance(data, dict) else data

    if not isinstance(raw_list, list):
        raise ValueError(f"Invalid universe structure in {filepath}: expected a list of index items.")

    for entry in raw_list:
        if not isinstance(entry, dict):
            continue
        try:
            item = UniverseItem(
                country=str(entry["country"]).strip(),
                index_name=str(entry["index_name"]).strip(),
                data_source_id=str(entry["data_source_id"]).strip(),
                currency=str(entry["currency"]).strip().upper(),
            )
            items.append(item)
        except KeyError as e:
            raise KeyError(f"Missing required key in universe item {entry}: {e}")

    if not items:
        raise ValueError(f"Universe file {filepath} contains no valid index entries.")

    return items
