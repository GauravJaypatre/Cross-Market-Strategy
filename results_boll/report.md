# Cross-Market Strategy Backtest & Friction Impact Report

**Strategy Parsing Method:** `Deterministic Rule-Based Parser`

**Random Seed:** `42` (Deterministic Monte Carlo & Bootstrap Resampling)

**Tax & Brokerage Dataset Status:** `Reference / Preliminary Baseline (primary_statutory_single_source)`

> **Strategy Description**: *"Buy when the index closes above its upper Bollinger Band, using a 20-day moving average and 2 standard deviations. Sell when it closes back below the 20-day moving average. No leverage, no shorting."*

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
| 1 | India | Nifty 50 | INR | 3.11% | 2.76% | **1.89%** | [-0.7%, 7.8%] | -2.24% | 9.63% | -7.74% | -28.57% | 0.07 | 0.29 | 55 | 2011-01-03 |
| 2 | Japan | Nikkei 225 | JPY | 3.44% | 2.08% | **1.48%** | [-0.8%, 7.9%] | 0.00% | 9.81% | -8.33% | -29.39% | 0.05 | 0.19 | 62 | 2011-01-04 |
| 3 | Germany | DAX 40 | EUR | 1.80% | 0.50% | **0.49%** | [-1.6%, 6.1%] | 0.03% | 7.23% | -6.74% | -23.23% | 0.02 | 0.10 | 61 | 2011-01-03 |
| 4 | United States | S&P 500 | USD | 0.98% | 0.16% | **0.12%** | [-1.1%, 3.3%] | -1.97% | 10.97% | -10.85% | -14.17% | 0.01 | 0.05 | 56 | 2011-01-03 |
| 5 | United Kingdom | FTSE 100 | GBP | -1.40% | -1.40% | **-7.68%** | [-3.5%, 0.9%] | 0.00% | 2.71% | -10.39% | -70.39% | -0.11 | -0.92 | 57 | 2011-01-04 |

## 2. Secondary Ranking: Calmar Ratio (Risk-Adjusted Efficiency)

Re-sorted by Calmar Ratio (CAGR / |Max Drawdown|) computed on the Net-of-Tax-and-Discount-Brokerage series.


| Calmar Rank | Country | Index | Calmar Ratio | Net-Disc CAGR | Max Drawdown | Sharpe | Total Trades |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|
| 1 | India | Nifty 50 | **0.07** | 1.89% | -28.57% | 0.29 | 55 |
| 2 | Japan | Nikkei 225 | **0.05** | 1.48% | -29.39% | 0.19 | 62 |
| 3 | Germany | DAX 40 | **0.02** | 0.49% | -23.23% | 0.10 | 61 |
| 4 | United States | S&P 500 | **0.01** | 0.12% | -14.17% | 0.05 | 56 |
| 5 | United Kingdom | FTSE 100 | **-0.11** | -7.68% | -70.39% | -0.92 | 57 |

## 3. Skeptical Robustness & Overfitting Evaluation

In-Sample (2011–2018) vs Out-of-Sample (2019–2025) performance degradation, 1,000 Monte Carlo trade sequence permutations, and 95% bootstrap CAGR confidence intervals.


| Country | Index | IS CAGR (2011-18) | OOS CAGR (2019-25) | Degradation (OOS/IS) | IS Trades | OOS Trades | IS Guard | OOS Guard | MC Worst DD (P95) | 95% Bootstrap CI | Precision Flag |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| India | Nifty 50 | 1.68% | 2.12% | 1.26x (+0.44 pp) | 30 | 25 | PASS | PASS | -22.23% | [-0.7%, 7.8%] | `Robust (n>=30)` |
| Japan | Nikkei 225 | -0.05% | 3.26% | -71.33x (+3.30 pp) | 31 | 31 | PASS | PASS | -23.34% | [-0.8%, 7.9%] | `Robust (n>=30)` |
| Germany | DAX 40 | -0.61% | 1.77% | -2.88x (+2.38 pp) | 34 | 27 | PASS | PASS | -25.70% | [-1.6%, 6.1%] | `Robust (n>=30)` |
| United States | S&P 500 | -0.15% | 0.42% | -2.87x (+0.56 pp) | 28 | 28 | PASS | PASS | -14.74% | [-1.1%, 3.3%] | `Robust (n>=30)` |
| United Kingdom | FTSE 100 | -3.99% | -11.73% | 2.94x (-7.74 pp) | 24 | 33 | PASS | PASS | -30.59% | [-3.5%, 0.9%] | `Robust (n>=30)` |

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