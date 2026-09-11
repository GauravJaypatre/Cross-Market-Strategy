"""Validation tests for the 15-country full universe configuration and statutory datasets."""

import yaml
import pandas as pd
from pathlib import Path


def test_universe_and_statutory_coverage(universe_path, tax_dataset_path, brokerage_dataset_path):
    """Verify that universe.yaml, tax_dataset.csv, and brokerage_dataset.csv are strictly aligned."""
    assert universe_path.exists(), "universe.yaml does not exist"
    assert tax_dataset_path.exists(), "tax_dataset.csv does not exist"
    assert brokerage_dataset_path.exists(), "brokerage_dataset.csv does not exist"

    with open(universe_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    indices = cfg["indices"]
    assert len(indices) == 25, f"Expected 25 indices, got {len(indices)}"

    universe_countries = sorted(list(set(idx["country"] for idx in indices)))
    assert len(universe_countries) == 15, f"Expected 15 countries, got {len(universe_countries)}"

    # Check that Switzerland is NOT present and Indonesia IS present
    assert "Switzerland" not in universe_countries, "Switzerland should not be in universe.yaml"
    assert "Indonesia" in universe_countries, "Indonesia must be in universe.yaml as IMF rank 16 sub"

    # Check China indices (must be authentic mainland A-shares, no ^HSCE)
    china_tickers = [idx["data_source_id"] for idx in indices if idx["country"] == "China"]
    assert "^HSCE" not in china_tickers, "^HSCE must not be in China index list"
    assert set(china_tickers) == {"000001.SS", "399001.SZ"}

    # Validate tax dataset
    df_tax = pd.read_csv(tax_dataset_path)
    tax_countries = sorted(df_tax["country"].unique().tolist())
    assert tax_countries == universe_countries, f"Tax countries mismatch: {set(universe_countries) ^ set(tax_countries)}"
    valid_confidences = {"primary_statutory_single_source", "single_source", "llm_extracted_unverified"}
    assert set(df_tax["confidence"]).issubset(valid_confidences), f"Unexpected confidence in tax: {set(df_tax['confidence'])}"
    # Demo countries + Indonesia must be primary_statutory_single_source
    demo_and_sub = {"United States", "Germany", "Japan", "India", "United Kingdom", "Indonesia"}
    demo_tax = df_tax[df_tax["country"].isin(demo_and_sub)]
    assert (demo_tax["confidence"] == "primary_statutory_single_source").all()
    assert "Switzerland" not in tax_countries
    assert "Indonesia" in tax_countries

    # Validate brokerage dataset
    df_broker = pd.read_csv(brokerage_dataset_path)
    broker_countries = sorted(df_broker["country"].unique().tolist())
    assert broker_countries == universe_countries, f"Brokerage countries mismatch: {set(universe_countries) ^ set(broker_countries)}"
    assert set(df_broker["confidence"]).issubset(valid_confidences), f"Unexpected confidence in brokerage: {set(df_broker['confidence'])}"
    demo_broker = df_broker[df_broker["country"].isin(demo_and_sub)]
    assert (demo_broker["confidence"] == "primary_statutory_single_source").all()
    assert "Switzerland" not in broker_countries
    assert "Indonesia" in broker_countries

    # Each country must have both discount and full_service tiers
    for c in universe_countries:
        c_brokers = df_broker[df_broker["country"] == c]
        b_types = set(c_brokers["broker_type"].unique())
        assert {"discount", "full_service"}.issubset(b_types), f"Country {c} missing discount or full_service broker: {b_types}"
