# Cross-Market Strategy Backtest & Friction Impact Report

**Strategy Parsing Method:** `Deterministic Rule-Based Parser`

**Random Seed:** `42` (Deterministic Monte Carlo & Bootstrap Resampling)

**Tax & Brokerage Dataset Status:** `Reference / Preliminary Baseline (primary_statutory_single_source)`

> **Strategy Description**: *"Buy when the 50-day moving average crosses above the 200-day moving average, sell when it crosses below, using the full index value as position size, no leverage, no shorting"*

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
| 1 | United States | S&P 500 | USD | 8.08% | 7.13% | **7.13%** | [1.6%, 14.1%] | 7.04% | 10.97% | -3.83% | -36.18% | 0.20 | 0.54 | 7 | 2011-01-03 |
| 2 | Japan | Nikkei 225 | JPY | 7.47% | 5.95% | **5.88%** | [-1.6%, 16.9%] | 3.15% | 9.81% | -3.92% | -43.72% | 0.13 | 0.41 | 13 | 2011-01-04 |
| 3 | India | Nifty 50 | INR | 4.96% | 4.96% | **4.84%** | [-3.7%, 13.7%] | 4.41% | 9.63% | -4.79% | -43.18% | 0.11 | 0.46 | 11 | 2011-01-03 |
| 4 | Germany | DAX 40 | EUR | 5.46% | 3.94% | **3.94%** | [-2.5%, 13.2%] | 3.90% | 7.23% | -3.29% | -46.54% | 0.08 | 0.33 | 8 | 2011-01-03 |
| 5 | United Kingdom | FTSE 100 | GBP | 0.89% | 0.59% | **-0.12%** | [-4.4%, 6.0%] | -0.96% | 2.71% | -2.83% | -41.93% | -0.00 | 0.05 | 11 | 2011-01-04 |

## 2. Secondary Ranking: Calmar Ratio (Risk-Adjusted Efficiency)

Re-sorted by Calmar Ratio (CAGR / |Max Drawdown|) computed on the Net-of-Tax-and-Discount-Brokerage series.


| Calmar Rank | Country | Index | Calmar Ratio | Net-Disc CAGR | Max Drawdown | Sharpe | Total Trades |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|
| 1 | United States | S&P 500 | **0.20** | 7.13% | -36.18% | 0.54 | 7 |
| 2 | Japan | Nikkei 225 | **0.13** | 5.88% | -43.72% | 0.41 | 13 |
| 3 | India | Nifty 50 | **0.11** | 4.84% | -43.18% | 0.46 | 11 |
| 4 | Germany | DAX 40 | **0.08** | 3.94% | -46.54% | 0.33 | 8 |
| 5 | United Kingdom | FTSE 100 | **-0.00** | -0.12% | -41.93% | 0.05 | 11 |

## 3. Skeptical Robustness & Overfitting Evaluation

In-Sample (2011–2018) vs Out-of-Sample (2019–2025) performance degradation, 1,000 Monte Carlo trade sequence permutations, and 95% bootstrap CAGR confidence intervals.


| Country | Index | IS CAGR (2011-18) | OOS CAGR (2019-25) | Degradation (OOS/IS) | IS Trades | OOS Trades | IS Guard | OOS Guard | MC Worst DD (P95) | 95% Bootstrap CI | Precision Flag |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| United States | S&P 500 | 6.72% | 7.60% | 1.13x (+0.88 pp) | 3 | 4 | PASS | PASS | -13.13% | [1.6%, 14.1%] | `Directional (n<30)` |
| Japan | Nikkei 225 | 6.80% | 4.86% | 0.71x (-1.94 pp) | 5 | 8 | PASS | PASS | -34.96% | [-1.6%, 16.9%] | `Directional (n<30)` |
| India | Nifty 50 | 5.69% | 3.88% | 0.68x (-1.81 pp) | 5 | 6 | PASS | PASS | -37.79% | [-3.7%, 13.7%] | `Directional (n<30)` |
| Germany | DAX 40 | 4.73% | 3.05% | 0.64x (-1.68 pp) | 4 | 4 | PASS | PASS | -30.46% | [-2.5%, 13.2%] | `Directional (n<30)` |
| United Kingdom | FTSE 100 | 0.15% | -0.43% | -2.94x (-0.58 pp) | 5 | 6 | PASS | PASS | -35.01% | [-4.4%, 6.0%] | `Directional (n<30)` |

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