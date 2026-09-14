# Cross-Market Strategy Battery: Statutory Friction & Robustness Framework

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22737302.svg)](https://doi.org/10.5281/zenodo.22737302)

An empirical evaluation framework testing canonical algorithmic trading strategies across a global 15-country, 25-index universe (2011–2025) with point-in-time statutory friction modeling (Gross, Net-of-Tax, Net-Discount Brokerage, Net-Full-Service Brokerage, and Buy-and-Hold benchmark).

![Figure 1: Bootstrap CI Width vs. Minimum Trade Count](results/full_battery/figures/fig1_ci_width_vs_trades.png)

---

## Key Research Findings

1. **Active Underperformance Under Realistic Frictions:** Across the statistically defensible subset of strategy-index pairs ($n \ge 10$ in-sample and out-of-sample realized trades), **46 of 50 pairs (92.0%)** show Net-Discount CAGR below a passive Buy-and-Hold benchmark on the same instrument.
2. **Leaderboard Thin-Sample Distortion:** Unrestricted backtest leaderboards systematically over-index on low-frequency strategies with wide confidence intervals ($r = -0.268$ between trade count and CI width). Imposing $n \ge 10$ trade guards filters out lottery-winner artifacts.

![Figure 2: Top 5 Markets vs. Buy-and-Hold Benchmark](results/full_battery/figures/fig2_n10_leaderboard.png)

---

## Strategy Universe & Friction Model

### Canonical Strategy Families
1. **Trend-Following:** 50/200-day Simple Moving Average (SMA) Crossover
2. **Mean Reversion:** 14-day Relative Strength Index (RSI) Oscillator
3. **Absolute Momentum:** 12-month trailing return, monthly rebalanced
4. **Calendar Effect:** Seasonal "Halloween" rule (long Nov–Apr, cash May–Oct)
5. **Volatility Breakout:** 20-day Bollinger Bands breakout
6. **Drawdown Dip-Buying:** 52-week high drawdown trigger

### 5-Track Execution Pipeline
* **Track 1 (Gross):** Frictionless baseline.
* **Track 2 (Net-of-Tax):** Resident investor domestic capital gains / transaction taxes applied on closing dates.
* **Track 3 (Net-Discount):** Track 2 + historical discount/neo-broker commissions and exchange fees.
* **Track 4 (Net-Full-Service):** Track 2 + historical full-service broker fees.
* **Benchmark (Buy-and-Hold):** Passive market position with identical statutory friction adjustments.

---

## Project Structure

```
├── universe.yaml                   # 15-country, 25-index canonical universe specification
├── tax_dataset.csv                 # Point-in-time statutory capital gains tax rates (2011-2025)
├── brokerage_dataset.csv           # Historical discount & full-service brokerage fee schedules
├── run_full_battery.py             # Full canonical battery execution runner (150 pairs x 5 tracks)
├── data/                           # Pre-cached daily OHLCV index price histories (2011-2025)
├── results/full_battery/           # Battery outputs, summary CSVs, and publication figures
│   ├── figures/                    # Publication-ready 300 DPI figures
│   │   ├── fig1_ci_width_vs_trades.png
│   │   └── fig2_n10_leaderboard.png
│   ├── summary_cross_country.csv   # Consolidated 750-row metrics across all pairs and tracks
│   ├── leaderboard.csv             # Unrestricted top performers per strategy and track
│   ├── leaderboard_n10.csv         # Stricter n>=10 trade-count filtered leaderboard
│   └── robustness_summary.csv      # IS/OOS degradation, Monte Carlo P95 MaxDD, bootstrap CIs
├── src/                            # Core engine modules
│   ├── config.py                   # Universe loader and models
│   ├── data/                       # Market data loaders and provenance tracking
│   ├── engine/                     # Simulation engine, performance metrics, robustness
│   ├── multi_track/                # Multi-track simulator (Gross, Tax, Discount, Full-Service)
│   ├── parser/                     # Dual rule-based and LLM strategy parser with SHA-256 validation
│   ├── tax/                        # Statutory tax calculator and calendar adjustment
│   ├── brokerage/                  # Historical brokerage fee calculator
│   └── reporting/                  # Automated HTML/MD/JSON reporting
└── tests/                          # Automated pytest suite (30 tests)
```

---

## Quickstart & Verification

### 1. Run Automated Test Suite
```bash
pytest tests/ -v
```

### 2. Execute Full Battery
```bash
python run_full_battery.py --universe universe.yaml --out results/full_battery/
```

### 3. Generate Publication Figures
```bash
python scratch/generate_publication_figures.py
```

---

## Citation

This repository is archived on Zenodo for long-term preservation and citation. If you use this framework, statutory datasets, or empirical findings in your research, please refer to [CITATION.cff](CITATION.cff) or cite the canonical Zenodo release:

```bibtex
@software{jaypatre2026crossmarket,
  author       = {Gaurav Jaypatre},
  title        = {Cross-Market Strategy Battery: Statutory Friction \& Robustness Framework},
  month        = sep,
  year         = 2026,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.22737302},
  url          = {https://doi.org/10.5281/zenodo.22737302}
}
```

Canonical DOI: [https://doi.org/10.5281/zenodo.22737302](https://doi.org/10.5281/zenodo.22737302)

---

## License
MIT License
