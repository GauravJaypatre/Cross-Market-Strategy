# Cross-Market Strategy Backtest & Friction Impact Report

**Strategy Parsing Method:** `Deterministic Rule-Based Parser`

**Random Seed:** `42` (Deterministic Monte Carlo & Bootstrap Resampling)

**Tax & Brokerage Dataset Status:** `Reference / Preliminary Baseline (primary_statutory_single_source)`

> **Strategy Description**: *"Buy the index on November 1st each year and sell on April 30th the following year. Stay in cash the rest of the time. No leverage, no shorting."*

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
| 1 | Germany | DAX 40 | EUR | 7.96% | 5.98% | **5.98%** | [0.6%, 15.1%] | 5.92% | 7.23% | -1.25% | -45.93% | 0.13 | 0.43 | 16 | 2011-01-03 |
| 2 | United States | S&P 500 | USD | 6.24% | 4.78% | **4.77%** | [1.6%, 10.9%] | 4.49% | 10.97% | -6.19% | -38.05% | 0.13 | 0.38 | 16 | 2011-01-03 |
| 3 | Japan | Nikkei 225 | JPY | 4.54% | 3.07% | **2.95%** | [-2.5%, 13.2%] | -3.29% | 9.81% | -6.86% | -42.63% | 0.07 | 0.26 | 16 | 2011-01-04 |
| 4 | United Kingdom | FTSE 100 | GBP | 3.85% | 3.68% | **2.77%** | [-1.3%, 8.2%] | 1.66% | 2.71% | +0.06% | -38.02% | 0.07 | 0.28 | 16 | 2011-01-04 |
| 5 | India | Nifty 50 | INR | 2.35% | 2.20% | **1.98%** | [-3.0%, 7.9%] | 1.23% | 9.63% | -7.65% | -40.13% | 0.05 | 0.22 | 16 | 2011-01-03 |

## 2. Secondary Ranking: Calmar Ratio (Risk-Adjusted Efficiency)

Re-sorted by Calmar Ratio (CAGR / |Max Drawdown|) computed on the Net-of-Tax-and-Discount-Brokerage series.


| Calmar Rank | Country | Index | Calmar Ratio | Net-Disc CAGR | Max Drawdown | Sharpe | Total Trades |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|
| 1 | Germany | DAX 40 | **0.13** | 5.98% | -45.93% | 0.43 | 16 |
| 2 | United States | S&P 500 | **0.13** | 4.77% | -38.05% | 0.38 | 16 |
| 3 | United Kingdom | FTSE 100 | **0.07** | 2.77% | -38.02% | 0.28 | 16 |
| 4 | Japan | Nikkei 225 | **0.07** | 2.95% | -42.63% | 0.26 | 16 |
| 5 | India | Nifty 50 | **0.05** | 1.98% | -40.13% | 0.22 | 16 |

## 3. Skeptical Robustness & Overfitting Evaluation

In-Sample (2011–2018) vs Out-of-Sample (2019–2025) performance degradation, 1,000 Monte Carlo trade sequence permutations, and 95% bootstrap CAGR confidence intervals.


| Country | Index | IS CAGR (2011-18) | OOS CAGR (2019-25) | Degradation (OOS/IS) | IS Trades | OOS Trades | IS Guard | OOS Guard | MC Worst DD (P95) | 95% Bootstrap CI | Precision Flag |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Germany | DAX 40 | 4.33% | 7.86% | 1.82x (+3.53 pp) | 9 | 7 | PASS | PASS | -31.62% | [0.6%, 15.1%] | `Directional (n<30)` |
| United States | S&P 500 | 4.40% | 5.18% | 1.18x (+0.78 pp) | 9 | 7 | PASS | PASS | -17.56% | [1.6%, 10.9%] | `Directional (n<30)` |
| Japan | Nikkei 225 | 3.99% | 2.18% | 0.55x (-1.81 pp) | 9 | 7 | PASS | PASS | -35.69% | [-2.5%, 13.2%] | `Directional (n<30)` |
| United Kingdom | FTSE 100 | 1.80% | 3.86% | 2.14x (+2.06 pp) | 9 | 7 | PASS | PASS | -23.27% | [-1.3%, 8.2%] | `Directional (n<30)` |
| India | Nifty 50 | 1.31% | 2.86% | 2.19x (+1.55 pp) | 9 | 7 | PASS | PASS | -30.68% | [-3.0%, 7.9%] | `Directional (n<30)` |

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