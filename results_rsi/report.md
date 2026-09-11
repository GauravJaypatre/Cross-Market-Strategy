# Cross-Market Strategy Backtest & Friction Impact Report

**Strategy Parsing Method:** `Deterministic Rule-Based Parser`

**Random Seed:** `42` (Deterministic Monte Carlo & Bootstrap Resampling)

**Tax & Brokerage Dataset Status:** `Reference / Preliminary Baseline (primary_statutory_single_source)`

> **Strategy Description**: *"Buy the index when the 14-day RSI drops below 30, and sell when the RSI rises back above 70. Hold the full position size, no shorting, no leverage."*

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
| 1 | United States | S&P 500 | USD | 7.91% | 6.08% | **6.06%** | [4.0%, 11.6%] | 5.49% | 10.97% | -4.91% | -35.33% | 0.17 | 0.44 | 38 | 2011-01-03 |
| 2 | United Kingdom | FTSE 100 | GBP | 8.65% | 8.43% | **5.79%** | [4.6%, 12.0%] | 1.34% | 2.71% | +3.08% | -44.06% | 0.13 | 0.43 | 51 | 2011-01-04 |
| 3 | Japan | Nikkei 225 | JPY | 5.69% | 4.29% | **4.02%** | [0.7%, 10.1%] | 0.00% | 9.81% | -5.79% | -41.42% | 0.10 | 0.31 | 38 | 2011-01-04 |
| 4 | Germany | DAX 40 | EUR | 5.23% | 3.62% | **3.62%** | [-0.3%, 10.8%] | 3.42% | 7.23% | -3.61% | -39.90% | 0.09 | 0.30 | 41 | 2011-01-03 |
| 5 | India | Nifty 50 | INR | 2.80% | 2.28% | **1.69%** | [-1.6%, 6.5%] | -0.79% | 9.63% | -7.94% | -45.09% | 0.04 | 0.19 | 37 | 2011-01-03 |

## 2. Secondary Ranking: Calmar Ratio (Risk-Adjusted Efficiency)

Re-sorted by Calmar Ratio (CAGR / |Max Drawdown|) computed on the Net-of-Tax-and-Discount-Brokerage series.


| Calmar Rank | Country | Index | Calmar Ratio | Net-Disc CAGR | Max Drawdown | Sharpe | Total Trades |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|
| 1 | United States | S&P 500 | **0.17** | 6.06% | -35.33% | 0.44 | 38 |
| 2 | United Kingdom | FTSE 100 | **0.13** | 5.79% | -44.06% | 0.43 | 51 |
| 3 | Japan | Nikkei 225 | **0.10** | 4.02% | -41.42% | 0.31 | 38 |
| 4 | Germany | DAX 40 | **0.09** | 3.62% | -39.90% | 0.30 | 41 |
| 5 | India | Nifty 50 | **0.04** | 1.69% | -45.09% | 0.19 | 37 |

## 3. Skeptical Robustness & Overfitting Evaluation

In-Sample (2011–2018) vs Out-of-Sample (2019–2025) performance degradation, 1,000 Monte Carlo trade sequence permutations, and 95% bootstrap CAGR confidence intervals.


| Country | Index | IS CAGR (2011-18) | OOS CAGR (2019-25) | Degradation (OOS/IS) | IS Trades | OOS Trades | IS Guard | OOS Guard | MC Worst DD (P95) | 95% Bootstrap CI | Precision Flag |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| United States | S&P 500 | 7.00% | 4.97% | 0.71x (-2.04 pp) | 21 | 17 | PASS | PASS | -19.18% | [4.0%, 11.6%] | `Robust (n>=30)` |
| United Kingdom | FTSE 100 | 4.75% | 6.99% | 1.47x (+2.24 pp) | 29 | 22 | PASS | PASS | -17.90% | [4.6%, 12.0%] | `Robust (n>=30)` |
| Japan | Nikkei 225 | 0.98% | 8.03% | 8.18x (+7.05 pp) | 20 | 18 | PASS | PASS | -23.79% | [0.7%, 10.1%] | `Robust (n>=30)` |
| Germany | DAX 40 | 1.17% | 6.46% | 5.54x (+5.29 pp) | 21 | 20 | PASS | PASS | -31.64% | [-0.3%, 10.8%] | `Robust (n>=30)` |
| India | Nifty 50 | 2.67% | 0.57% | 0.21x (-2.10 pp) | 22 | 15 | PASS | PASS | -27.85% | [-1.6%, 6.5%] | `Robust (n>=30)` |

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