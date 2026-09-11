# Cross-Market Strategy Backtest & Friction Impact Report

**Strategy Parsing Method:** `Deterministic Rule-Based Parser`

**Random Seed:** `42` (Deterministic Monte Carlo & Bootstrap Resampling)

**Tax & Brokerage Dataset Status:** `Reference / Preliminary Baseline (primary_statutory_single_source)`

> **Strategy Description**: *"At the start of each month, check the index's total return over the trailing 12 months. If it's positive, hold the index for the next month. If it's negative, stay in cash. No leverage, no shorting."*

## Methodological Disclosures

> [!NOTE]
> **Sharpe Annualization & Risk-Free Rate**: Sharpe ratios are calculated from daily returns using an annualization factor of sqrt(252) (252 trading days/year) and an annualized risk-free rate of 0.0%. This stated simplification avoids confounding 15 divergent sovereign yield curves over the 2011–2025 period. Cross-market risk-adjusted capital efficiency should also be evaluated via the Calmar ratio and net excess CAGR over Buy & Hold.


> [!NOTE]
> **Robustness Methodology (Sequence Risk vs Estimation Uncertainty)**: The Monte Carlo trade-shuffle (1,000 permutations) randomizes trade execution order to isolate sequence risk and path-dependent drawdown (P95), whereas the bootstrap confidence interval resamples trade returns with replacement to quantify parameter estimation uncertainty on annualized CAGR given small sample size (n < 30).


> [!IMPORTANT]
> **Currency Standard & Stated Limitation**: Rankings are computed within each currency's own terms (no FX adjustment); cross-country comparison does not account for exchange-rate fluctuations.


> [!WARNING]
> **Dataset Verification Notice**: Reference / Preliminary Baseline (Curated from statutory authorities e.g. IRS, HMRC, Indian Finance Acts; tagged as primary_statutory_single_source until user-supplied cross-verified datasets are provided).


> [!CAUTION]
> **Low-Sample Precision Notice**: Sample Size & Statistical Precision Notice (Low-n, Directional Only): Strategy trade counts range from 7 to 13 trades across the 2011–2025 period. Because n < 30, individual index CAGR estimates carry wide 95% bootstrap confidence intervals and must be interpreted as directional rather than definitive alpha.


## 1. Primary Ranking: Net-of-Tax-and-Discount-Brokerage CAGR

Qualified indices sorted by Net Discount CAGR. All four friction tracks and the Buy & Hold benchmark are displayed side by side.


| Rank | Country | Index | Ccy | Gross CAGR | Net-Tax CAGR | Net-Disc CAGR | 95% Bootstrap CI | Net-FS CAGR | B&H Net-Disc | Excess CAGR vs B&H | Max DD | Calmar | Sharpe | Trades | Data Start |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | United States | S&P 500 | USD | 7.82% | 6.95% | **6.95%** | [0.2%, 16.8%] | 6.84% | 10.97% | -4.02% | -35.80% | 0.19 | 0.52 | 8 | 2011-01-03 |
| 2 | Japan | Nikkei 225 | JPY | 6.68% | 5.26% | **5.20%** | [-2.5%, 17.3%] | 2.98% | 9.81% | -4.60% | -51.07% | 0.10 | 0.36 | 10 | 2011-01-04 |
| 3 | India | Nifty 50 | INR | 4.30% | 4.30% | **4.14%** | [-3.6%, 11.0%] | 3.58% | 9.63% | -5.49% | -42.84% | 0.10 | 0.37 | 12 | 2011-01-03 |
| 4 | Germany | DAX 40 | EUR | 3.34% | 1.98% | **1.98%** | [-3.9%, 13.2%] | 1.91% | 7.23% | -5.25% | -57.16% | 0.03 | 0.20 | 11 | 2011-01-03 |
| 5 | United Kingdom | FTSE 100 | GBP | 1.16% | 0.84% | **-0.13%** | [-2.4%, 5.7%] | -1.31% | 2.71% | -2.84% | -34.31% | -0.00 | 0.04 | 15 | 2011-01-04 |

## 2. Secondary Ranking: Calmar Ratio (Risk-Adjusted Efficiency)

Re-sorted by Calmar Ratio (CAGR / |Max Drawdown|) computed on the Net-of-Tax-and-Discount-Brokerage series.


| Calmar Rank | Country | Index | Calmar Ratio | Net-Disc CAGR | Max Drawdown | Sharpe | Total Trades |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|
| 1 | United States | S&P 500 | **0.19** | 6.95% | -35.80% | 0.52 | 8 |
| 2 | Japan | Nikkei 225 | **0.10** | 5.20% | -51.07% | 0.36 | 10 |
| 3 | India | Nifty 50 | **0.10** | 4.14% | -42.84% | 0.37 | 12 |
| 4 | Germany | DAX 40 | **0.03** | 1.98% | -57.16% | 0.20 | 11 |
| 5 | United Kingdom | FTSE 100 | **-0.00** | -0.13% | -34.31% | 0.04 | 15 |

## 3. Skeptical Robustness & Overfitting Evaluation

In-Sample (2011–2018) vs Out-of-Sample (2019–2025) performance degradation, 1,000 Monte Carlo trade sequence permutations, and 95% bootstrap CAGR confidence intervals.


| Country | Index | IS CAGR (2011-18) | OOS CAGR (2019-25) | Degradation (OOS/IS) | IS Trades | OOS Trades | IS Guard | OOS Guard | MC Worst DD (P95) | 95% Bootstrap CI | Precision Flag |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| United States | S&P 500 | 5.64% | 8.44% | 1.50x (+2.80 pp) | 5 | 3 | PASS | PASS | -16.33% | [0.2%, 16.8%] | `Directional (n<30)` |
| Japan | Nikkei 225 | 4.94% | 5.92% | 1.20x (+0.98 pp) | 5 | 5 | PASS | PASS | -36.00% | [-2.5%, 17.3%] | `Directional (n<30)` |
| India | Nifty 50 | 7.49% | 0.54% | 0.07x (-6.96 pp) | 4 | 8 | PASS | PASS | -30.61% | [-3.6%, 11.0%] | `Directional (n<30)` |
| Germany | DAX 40 | 2.81% | 1.05% | 0.37x (-1.76 pp) | 5 | 6 | PASS | PASS | -32.96% | [-3.9%, 13.2%] | `Directional (n<30)` |
| United Kingdom | FTSE 100 | -1.24% | 1.16% | -0.94x (+2.40 pp) | 7 | 8 | PASS | PASS | -26.25% | [-2.4%, 5.7%] | `Directional (n<30)` |

## Appendix: Excluded Indices & Data Guards

*No indices were excluded. All universe targets met coverage and sample size thresholds.*


## Data Provenance & Cryptographic Audit

Audit trail of market data sources used for each index.


| Country | Index | Ticker / ID | Vendor | Source Identifier | SHA256 Checksum | Rows | Date Window |
|:---|:---|:---:|:---:|:---|:---:|:---:|:---:|
| United States | S&P 500 | `GSPC` | `local_csv` | `GSPC.csv` | `fe3a9c20d1ae...` | 3771 | 2011-01-03 to 2025-12-30 |
| Germany | DAX 40 | `GDAXI` | `local_csv` | `GDAXI.csv` | `9729f4ad3f0b...` | 3803 | 2011-01-03 to 2025-12-30 |
| Japan | Nikkei 225 | `N225` | `local_csv` | `N225.csv` | `31c8677d263a...` | 3670 | 2011-01-04 to 2025-12-30 |
| India | Nifty 50 | `NSEI` | `local_csv` | `NSEI.csv` | `cc59b8e2309a...` | 3678 | 2011-01-03 to 2025-12-30 |
| United Kingdom | FTSE 100 | `FTSE` | `local_csv` | `FTSE.csv` | `7c70e6cca317...` | 3785 | 2011-01-04 to 2025-12-30 |