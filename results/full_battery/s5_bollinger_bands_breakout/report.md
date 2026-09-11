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
| 1 | China | Shenzhen Component | CNY | 6.78% | 6.78% | **6.24%** | [0.6%, 14.7%] | 6.17% | 0.45% | +5.79% | -23.80% | 0.26 | 0.55 | 49 | 2011-01-04 |
| 2 | China | Shanghai Composite | CNY | 4.43% | 4.43% | **3.67%** | [-0.3%, 10.2%] | 3.56% | 2.22% | +1.45% | -20.59% | 0.18 | 0.40 | 58 | 2011-01-04 |
| 3 | South Korea | KOSPI | KRW | 4.35% | 4.35% | **3.00%** | [-0.2%, 10.0%] | -0.21% | 4.86% | -1.85% | -28.29% | 0.11 | 0.39 | 53 | 2011-01-03 |
| 4 | Brazil | Ibovespa | BRL | 2.75% | 2.75% | **2.56%** | [-2.1%, 7.9%] | -0.99% | 5.19% | -2.63% | -34.52% | 0.07 | 0.30 | 57 | 2011-01-03 |
| 5 | India | Nifty Bank | INR | 4.13% | 3.37% | **2.29%** | [-2.2%, 12.1%] | -3.68% | 10.79% | -8.51% | -30.54% | 0.07 | 0.25 | 64 | 2011-01-03 |
| 6 | India | Nifty 50 | INR | 3.11% | 2.76% | **1.89%** | [-0.7%, 7.8%] | -2.24% | 9.63% | -7.74% | -28.57% | 0.07 | 0.29 | 55 | 2011-01-03 |
| 7 | India | BSE Sensex | INR | 3.05% | 2.69% | **1.76%** | [-1.1%, 7.3%] | -2.84% | 9.48% | -7.72% | -33.38% | 0.05 | 0.28 | 56 | 2011-01-03 |
| 8 | Japan | Nikkei 225 | JPY | 3.44% | 2.08% | **1.48%** | [-0.8%, 7.9%] | 0.00% | 9.81% | -8.33% | -29.39% | 0.05 | 0.19 | 62 | 2011-01-04 |
| 9 | Germany | MDAX | EUR | 2.84% | 1.46% | **1.45%** | [-1.0%, 7.3%] | 1.08% | 6.24% | -4.79% | -22.16% | 0.07 | 0.21 | 57 | 2011-01-03 |
| 10 | South Korea | KOSDAQ | KRW | 2.51% | 2.51% | **1.06%** | [-0.8%, 6.9%] | -2.73% | 3.94% | -2.88% | -23.09% | 0.05 | 0.17 | 40 | 2011-01-03 |
| 11 | United States | Dow Jones Industrial Average | USD | 1.87% | 0.89% | **0.85%** | [-0.3%, 4.4%] | -1.24% | 9.06% | -8.22% | -16.75% | 0.05 | 0.16 | 62 | 2011-01-03 |
| 12 | Germany | DAX 40 | EUR | 1.80% | 0.50% | **0.49%** | [-1.6%, 6.1%] | 0.03% | 7.23% | -6.74% | -23.23% | 0.02 | 0.10 | 61 | 2011-01-03 |
| 13 | United States | S&P 500 | USD | 0.98% | 0.16% | **0.12%** | [-1.1%, 3.3%] | -1.97% | 10.97% | -10.85% | -14.17% | 0.01 | 0.05 | 56 | 2011-01-03 |
| 14 | Canada | S&P/TSX Composite | CAD | 0.55% | 0.05% | **0.01%** | [-1.3%, 2.7%] | -4.01% | 5.25% | -5.24% | -14.55% | 0.00 | 0.03 | 60 | 2011-01-04 |
| 15 | United States | Nasdaq Composite | USD | 1.21% | 0.02% | **-0.04%** | [-1.8%, 5.1%] | -2.49% | 14.43% | -14.48% | -24.31% | -0.00 | 0.04 | 63 | 2011-01-03 |
| 16 | Australia | All Ordinaries | AUD | 0.52% | -0.82% | **-0.91%** | [-1.6%, 2.8%] | -6.84% | 3.73% | -4.64% | -23.32% | -0.04 | -0.13 | 65 | 2011-01-04 |
| 17 | Germany | TecDAX | EUR | 0.34% | -1.01% | **-1.02%** | [-3.1%, 4.1%] | -1.61% | 8.43% | -9.45% | -22.36% | -0.05 | -0.08 | 62 | 2011-01-03 |
| 18 | Australia | ASX 200 | AUD | 0.18% | -1.19% | **-1.28%** | [-1.9%, 2.7%] | -7.48% | 3.66% | -4.93% | -24.10% | -0.05 | -0.17 | 66 | 2011-01-04 |
| 19 | Spain | IBEX 35 | EUR | -0.46% | -1.57% | **-2.32%** | [-3.8%, 2.8%] | -6.96% | 3.16% | -5.47% | -32.10% | -0.07 | -0.24 | 61 | 2011-01-03 |
| 20 | France | CAC 40 | EUR | 1.42% | -0.52% | **-2.90%** | [-1.9%, 4.7%] | -15.29% | 3.83% | -6.72% | -36.08% | -0.08 | -0.25 | 53 | 2011-01-03 |
| 21 | Italy | FTSE MIB | EUR | -0.04% | -1.95% | **-2.97%** | [-4.4%, 4.6%] | -6.43% | 4.30% | -7.26% | -41.19% | -0.07 | -0.25 | 61 | 2011-01-03 |
| 22 | Indonesia | Jakarta Composite Index | IDR | 0.05% | 0.05% | **-3.20%** | [-3.4%, 4.0%] | -4.15% | 5.76% | -8.97% | -46.57% | -0.07 | -0.30 | 68 | 2011-01-03 |
| 23 | Mexico | IPC Mexico | MXN | -0.02% | -0.42% | **-3.87%** | [-2.8%, 2.9%] | -11.25% | 3.17% | -7.05% | -45.50% | -0.09 | -0.36 | 68 | 2011-01-03 |
| 24 | United Kingdom | FTSE 100 | GBP | -1.40% | -1.40% | **-7.68%** | [-3.5%, 0.9%] | 0.00% | 2.71% | -10.39% | -70.39% | -0.11 | -0.92 | 57 | 2011-01-04 |
| 25 | United Kingdom | FTSE 250 | GBP | 0.09% | 0.09% | **-7.84%** | [-2.1%, 2.9%] | 0.00% | 3.60% | -11.44% | -73.37% | -0.11 | -0.75 | 65 | 2011-01-04 |

## 2. Secondary Ranking: Calmar Ratio (Risk-Adjusted Efficiency)

Re-sorted by Calmar Ratio (CAGR / |Max Drawdown|) computed on the Net-of-Tax-and-Discount-Brokerage series.


| Calmar Rank | Country | Index | Calmar Ratio | Net-Disc CAGR | Max Drawdown | Sharpe | Total Trades |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|
| 1 | China | Shenzhen Component | **0.26** | 6.24% | -23.80% | 0.55 | 49 |
| 2 | China | Shanghai Composite | **0.18** | 3.67% | -20.59% | 0.40 | 58 |
| 3 | South Korea | KOSPI | **0.11** | 3.00% | -28.29% | 0.39 | 53 |
| 4 | India | Nifty Bank | **0.07** | 2.29% | -30.54% | 0.25 | 64 |
| 5 | Brazil | Ibovespa | **0.07** | 2.56% | -34.52% | 0.30 | 57 |
| 6 | India | Nifty 50 | **0.07** | 1.89% | -28.57% | 0.29 | 55 |
| 7 | Germany | MDAX | **0.07** | 1.45% | -22.16% | 0.21 | 57 |
| 8 | India | BSE Sensex | **0.05** | 1.76% | -33.38% | 0.28 | 56 |
| 9 | United States | Dow Jones Industrial Average | **0.05** | 0.85% | -16.75% | 0.16 | 62 |
| 10 | Japan | Nikkei 225 | **0.05** | 1.48% | -29.39% | 0.19 | 62 |
| 11 | South Korea | KOSDAQ | **0.05** | 1.06% | -23.09% | 0.17 | 40 |
| 12 | Germany | DAX 40 | **0.02** | 0.49% | -23.23% | 0.10 | 61 |
| 13 | United States | S&P 500 | **0.01** | 0.12% | -14.17% | 0.05 | 56 |
| 14 | Canada | S&P/TSX Composite | **0.00** | 0.01% | -14.55% | 0.03 | 60 |
| 15 | United States | Nasdaq Composite | **-0.00** | -0.04% | -24.31% | 0.04 | 63 |
| 16 | Australia | All Ordinaries | **-0.04** | -0.91% | -23.32% | -0.13 | 65 |
| 17 | Germany | TecDAX | **-0.05** | -1.02% | -22.36% | -0.08 | 62 |
| 18 | Australia | ASX 200 | **-0.05** | -1.28% | -24.10% | -0.17 | 66 |
| 19 | Indonesia | Jakarta Composite Index | **-0.07** | -3.20% | -46.57% | -0.30 | 68 |
| 20 | Italy | FTSE MIB | **-0.07** | -2.97% | -41.19% | -0.25 | 61 |
| 21 | Spain | IBEX 35 | **-0.07** | -2.32% | -32.10% | -0.24 | 61 |
| 22 | France | CAC 40 | **-0.08** | -2.90% | -36.08% | -0.25 | 53 |
| 23 | Mexico | IPC Mexico | **-0.09** | -3.87% | -45.50% | -0.36 | 68 |
| 24 | United Kingdom | FTSE 250 | **-0.11** | -7.84% | -73.37% | -0.75 | 65 |
| 25 | United Kingdom | FTSE 100 | **-0.11** | -7.68% | -70.39% | -0.92 | 57 |

## 3. Skeptical Robustness & Overfitting Evaluation

In-Sample (2011–2018) vs Out-of-Sample (2019–2025) performance degradation, 1,000 Monte Carlo trade sequence permutations, and 95% bootstrap CAGR confidence intervals.


| Country | Index | IS CAGR (2011-18) | OOS CAGR (2019-25) | Degradation (OOS/IS) | IS Trades | OOS Trades | IS Guard | OOS Guard | MC Worst DD (P95) | 95% Bootstrap CI | Precision Flag |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| China | Shenzhen Component | 6.63% | 5.80% | 0.87x (-0.83 pp) | 23 | 26 | PASS | PASS | -25.48% | [0.6%, 14.7%] | `Robust (n>=30)` |
| China | Shanghai Composite | 4.11% | 3.18% | 0.77x (-0.93 pp) | 30 | 28 | PASS | PASS | -21.12% | [-0.3%, 10.2%] | `Robust (n>=30)` |
| South Korea | KOSPI | -2.10% | 9.16% | -4.37x (+11.26 pp) | 30 | 23 | PASS | PASS | -16.76% | [-0.2%, 10.0%] | `Robust (n>=30)` |
| Brazil | Ibovespa | -0.58% | 6.27% | -10.79x (+6.86 pp) | 31 | 26 | PASS | PASS | -31.35% | [-2.1%, 7.9%] | `Robust (n>=30)` |
| India | Nifty Bank | 3.29% | 1.16% | 0.35x (-2.12 pp) | 32 | 32 | PASS | PASS | -36.81% | [-2.2%, 12.1%] | `Robust (n>=30)` |
| India | Nifty 50 | 1.68% | 2.12% | 1.26x (+0.44 pp) | 30 | 25 | PASS | PASS | -22.23% | [-0.7%, 7.8%] | `Robust (n>=30)` |
| India | BSE Sensex | 2.10% | 1.38% | 0.66x (-0.72 pp) | 28 | 28 | PASS | PASS | -23.82% | [-1.1%, 7.3%] | `Robust (n>=30)` |
| Japan | Nikkei 225 | -0.05% | 3.26% | -71.33x (+3.30 pp) | 31 | 31 | PASS | PASS | -23.34% | [-0.8%, 7.9%] | `Robust (n>=30)` |
| Germany | MDAX | 1.42% | 1.49% | 1.05x (+0.07 pp) | 30 | 27 | PASS | PASS | -21.75% | [-1.0%, 7.3%] | `Robust (n>=30)` |
| South Korea | KOSDAQ | 2.85% | -0.95% | -0.33x (-3.80 pp) | 20 | 20 | PASS | PASS | -18.84% | [-0.8%, 6.9%] | `Robust (n>=30)` |
| United States | Dow Jones Industrial Average | 0.64% | 1.09% | 1.71x (+0.45 pp) | 32 | 30 | PASS | PASS | -13.14% | [-0.3%, 4.4%] | `Robust (n>=30)` |
| Germany | DAX 40 | -0.61% | 1.77% | -2.88x (+2.38 pp) | 34 | 27 | PASS | PASS | -25.70% | [-1.6%, 6.1%] | `Robust (n>=30)` |
| United States | S&P 500 | -0.15% | 0.42% | -2.87x (+0.56 pp) | 28 | 28 | PASS | PASS | -14.74% | [-1.1%, 3.3%] | `Robust (n>=30)` |
| Canada | S&P/TSX Composite | -1.00% | 1.18% | -1.17x (+2.18 pp) | 29 | 31 | PASS | PASS | -16.54% | [-1.3%, 2.7%] | `Robust (n>=30)` |
| United States | Nasdaq Composite | -2.14% | 2.41% | -1.13x (+4.54 pp) | 37 | 26 | PASS | PASS | -23.28% | [-1.8%, 5.1%] | `Robust (n>=30)` |
| Australia | All Ordinaries | 0.14% | -2.10% | -14.68x (-2.24 pp) | 27 | 38 | PASS | PASS | -19.49% | [-1.6%, 2.8%] | `Robust (n>=30)` |
| Germany | TecDAX | -1.12% | -0.91% | 0.81x (+0.22 pp) | 35 | 27 | PASS | PASS | -31.24% | [-3.1%, 4.1%] | `Robust (n>=30)` |
| Australia | ASX 200 | -0.39% | -2.28% | 5.89x (-1.90 pp) | 28 | 38 | PASS | PASS | -21.81% | [-1.9%, 2.7%] | `Robust (n>=30)` |
| Spain | IBEX 35 | -2.78% | -1.78% | 0.64x (+1.00 pp) | 29 | 32 | PASS | PASS | -35.11% | [-3.8%, 2.8%] | `Robust (n>=30)` |
| France | CAC 40 | -2.43% | -3.43% | 1.41x (-1.00 pp) | 26 | 27 | PASS | PASS | -23.70% | [-1.9%, 4.7%] | `Robust (n>=30)` |
| Italy | FTSE MIB | -3.70% | -2.12% | 0.57x (+1.59 pp) | 28 | 33 | PASS | PASS | -40.52% | [-4.4%, 4.6%] | `Robust (n>=30)` |
| Indonesia | Jakarta Composite Index | -6.12% | 0.28% | -0.05x (+6.41 pp) | 40 | 28 | PASS | PASS | -31.19% | [-3.4%, 4.0%] | `Robust (n>=30)` |
| Mexico | IPC Mexico | -3.23% | -4.60% | 1.42x (-1.36 pp) | 32 | 36 | PASS | PASS | -27.64% | [-2.8%, 2.9%] | `Robust (n>=30)` |
| United Kingdom | FTSE 100 | -3.99% | -11.73% | 2.94x (-7.74 pp) | 24 | 33 | PASS | PASS | -30.59% | [-3.5%, 0.9%] | `Robust (n>=30)` |
| United Kingdom | FTSE 250 | -2.68% | -13.41% | 5.01x (-10.73 pp) | 30 | 35 | PASS | PASS | -23.02% | [-2.1%, 2.9%] | `Robust (n>=30)` |

## Appendix: Excluded Indices & Data Guards

*No indices were excluded. All universe targets met coverage and sample size thresholds.*


## Data Provenance & Cryptographic Audit

Audit trail of market data sources used for each index.


| Country | Index | Ticker / ID | Vendor | Source Identifier | SHA256 Checksum | Rows | Date Window |
|:---|:---|:---:|:---:|:---|:---:|:---:|:---:|
| United States | S&P 500 | `^GSPC` | `local_csv` | `GSPC.csv` | `fe3a9c20d1ae...` | 3771 | 2011-01-03 to 2025-12-30 |
| United States | Nasdaq Composite | `^IXIC` | `yfinance` | `^IXIC` | `N/A (API)` | 3771 | 2011-01-03 to 2025-12-30 |
| United States | Dow Jones Industrial Average | `^DJI` | `yfinance` | `^DJI` | `N/A (API)` | 3771 | 2011-01-03 to 2025-12-30 |
| China | Shanghai Composite | `000001.SS` | `yfinance` | `000001.SS` | `N/A (API)` | 3640 | 2011-01-04 to 2025-12-30 |
| China | Shenzhen Component | `399001.SZ` | `yfinance` | `399001.SZ` | `N/A (API)` | 3639 | 2011-01-04 to 2025-12-30 |
| Germany | DAX 40 | `^GDAXI` | `local_csv` | `GDAXI.csv` | `9729f4ad3f0b...` | 3803 | 2011-01-03 to 2025-12-30 |
| Germany | MDAX | `^MDAXI` | `yfinance` | `^MDAXI` | `N/A (API)` | 3803 | 2011-01-03 to 2025-12-30 |
| Germany | TecDAX | `^TECDAX` | `yfinance` | `^TECDAX` | `N/A (API)` | 3796 | 2011-01-03 to 2025-12-30 |
| Japan | Nikkei 225 | `^N225` | `local_csv` | `N225.csv` | `31c8677d263a...` | 3670 | 2011-01-04 to 2025-12-30 |
| India | Nifty 50 | `^NSEI` | `local_csv` | `NSEI.csv` | `cc59b8e2309a...` | 3678 | 2011-01-03 to 2025-12-30 |
| India | BSE Sensex | `^BSESN` | `yfinance` | `^BSESN` | `N/A (API)` | 3683 | 2011-01-03 to 2025-12-30 |
| India | Nifty Bank | `^NSEBANK` | `yfinance` | `^NSEBANK` | `N/A (API)` | 3693 | 2011-01-03 to 2025-12-30 |
| United Kingdom | FTSE 100 | `^FTSE` | `local_csv` | `FTSE.csv` | `7c70e6cca317...` | 3785 | 2011-01-04 to 2025-12-30 |
| United Kingdom | FTSE 250 | `^FTMC` | `yfinance` | `^FTMC` | `N/A (API)` | 3786 | 2011-01-04 to 2025-12-30 |
| France | CAC 40 | `^FCHI` | `yfinance` | `^FCHI` | `N/A (API)` | 3834 | 2011-01-03 to 2025-12-30 |
| Italy | FTSE MIB | `FTSEMIB.MI` | `yfinance` | `FTSEMIB.MI` | `N/A (API)` | 3806 | 2011-01-03 to 2025-12-30 |
| Indonesia | Jakarta Composite Index | `^JKSE` | `yfinance` | `^JKSE` | `N/A (API)` | 3640 | 2011-01-03 to 2025-12-30 |
| Canada | S&P/TSX Composite | `^GSPTSE` | `yfinance` | `^GSPTSE` | `N/A (API)` | 3762 | 2011-01-04 to 2025-12-30 |
| Brazil | Ibovespa | `^BVSP` | `yfinance` | `^BVSP` | `N/A (API)` | 3718 | 2011-01-03 to 2025-12-30 |
| South Korea | KOSPI | `^KS11` | `yfinance` | `^KS11` | `N/A (API)` | 3683 | 2011-01-03 to 2025-12-30 |
| South Korea | KOSDAQ | `^KQ11` | `yfinance` | `^KQ11` | `N/A (API)` | 3684 | 2011-01-03 to 2025-12-30 |
| Australia | ASX 200 | `^AXJO` | `yfinance` | `^AXJO` | `N/A (API)` | 3784 | 2011-01-04 to 2025-12-30 |
| Australia | All Ordinaries | `^AORD` | `yfinance` | `^AORD` | `N/A (API)` | 3789 | 2011-01-04 to 2025-12-30 |
| Mexico | IPC Mexico | `^MXX` | `yfinance` | `^MXX` | `N/A (API)` | 3762 | 2011-01-03 to 2025-12-30 |
| Spain | IBEX 35 | `^IBEX` | `yfinance` | `^IBEX` | `N/A (API)` | 3834 | 2011-01-03 to 2025-12-30 |