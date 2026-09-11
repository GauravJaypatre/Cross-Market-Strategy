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
| 1 | United States | Nasdaq Composite | USD | 9.65% | 8.66% | **8.66%** | [0.2%, 20.7%] | 8.56% | 14.43% | -5.78% | -41.13% | 0.21 | 0.54 | 9 | 2011-01-03 |
| 2 | United States | S&P 500 | USD | 7.82% | 6.95% | **6.95%** | [0.2%, 16.8%] | 6.84% | 10.97% | -4.02% | -35.80% | 0.19 | 0.52 | 8 | 2011-01-03 |
| 3 | India | BSE Sensex | INR | 5.55% | 5.55% | **5.44%** | [-1.4%, 13.1%] | 5.04% | 9.48% | -4.03% | -38.48% | 0.14 | 0.47 | 9 | 2011-01-03 |
| 4 | Japan | Nikkei 225 | JPY | 6.68% | 5.26% | **5.20%** | [-2.5%, 17.3%] | 2.98% | 9.81% | -4.60% | -51.07% | 0.10 | 0.36 | 10 | 2011-01-04 |
| 5 | Germany | TecDAX | EUR | 6.41% | 4.58% | **4.58%** | [-2.0%, 18.9%] | 4.54% | 8.43% | -3.85% | -48.72% | 0.09 | 0.33 | 10 | 2011-01-03 |
| 6 | India | Nifty 50 | INR | 4.30% | 4.30% | **4.14%** | [-3.6%, 11.0%] | 3.58% | 9.63% | -5.49% | -42.84% | 0.10 | 0.37 | 12 | 2011-01-03 |
| 7 | India | Nifty Bank | INR | 4.18% | 4.17% | **4.07%** | [-5.7%, 14.6%] | 3.74% | 10.79% | -6.72% | -51.01% | 0.08 | 0.32 | 8 | 2011-01-03 |
| 8 | Spain | IBEX 35 | EUR | 4.78% | 3.76% | **3.71%** | [-2.6%, 17.0%] | 3.44% | 3.16% | +0.56% | -35.18% | 0.11 | 0.35 | 8 | 2011-01-03 |
| 9 | United States | Dow Jones Industrial Average | USD | 4.46% | 3.68% | **3.67%** | [-2.1%, 11.6%] | 3.45% | 9.06% | -5.39% | -42.40% | 0.09 | 0.32 | 11 | 2011-01-03 |
| 10 | South Korea | KOSPI | KRW | 3.36% | 3.36% | **2.94%** | [-0.7%, 8.5%] | 2.16% | 4.86% | -1.91% | -30.07% | 0.10 | 0.31 | 16 | 2011-01-03 |
| 11 | Italy | FTSE MIB | EUR | 3.77% | 2.63% | **2.57%** | [-3.3%, 12.2%] | 2.41% | 4.30% | -1.73% | -43.90% | 0.06 | 0.23 | 6 | 2011-01-03 |
| 12 | China | Shenzhen Component | CNY | 2.56% | 2.56% | **2.45%** | [-1.9%, 8.8%] | 2.44% | 0.45% | +2.00% | -58.60% | 0.04 | 0.23 | 10 | 2011-01-04 |
| 13 | China | Shanghai Composite | CNY | 2.13% | 2.13% | **2.01%** | [-1.5%, 6.1%] | 1.99% | 2.22% | -0.21% | -52.23% | 0.04 | 0.21 | 9 | 2011-01-04 |
| 14 | Germany | DAX 40 | EUR | 3.34% | 1.98% | **1.98%** | [-3.9%, 13.2%] | 1.91% | 7.23% | -5.25% | -57.16% | 0.03 | 0.20 | 11 | 2011-01-03 |
| 15 | Canada | S&P/TSX Composite | CAD | 2.47% | 1.79% | **1.78%** | [-3.9%, 9.7%] | 1.31% | 5.25% | -3.46% | -40.47% | 0.04 | 0.21 | 10 | 2011-01-04 |
| 16 | United Kingdom | FTSE 250 | GBP | 2.63% | 2.28% | **1.56%** | [-0.8%, 7.4%] | 0.71% | 3.60% | -2.05% | -30.60% | 0.05 | 0.20 | 10 | 2011-01-04 |
| 17 | Indonesia | Jakarta Composite Index | IDR | 1.90% | 1.90% | **1.45%** | [-1.3%, 5.7%] | 1.35% | 5.76% | -4.31% | -26.95% | 0.05 | 0.19 | 13 | 2011-01-03 |
| 18 | South Korea | KOSDAQ | KRW | 1.68% | 1.68% | **1.27%** | [-2.2%, 6.4%] | 0.51% | 3.94% | -2.67% | -37.40% | 0.03 | 0.16 | 14 | 2011-01-03 |
| 19 | Germany | MDAX | EUR | 2.91% | 1.22% | **1.22%** | [-4.5%, 14.2%] | 1.13% | 6.24% | -5.02% | -49.51% | 0.02 | 0.16 | 13 | 2011-01-03 |
| 20 | Brazil | Ibovespa | BRL | 1.27% | 1.22% | **1.16%** | [-3.2%, 6.4%] | 0.35% | 5.19% | -4.03% | -58.86% | 0.02 | 0.16 | 13 | 2011-01-03 |
| 21 | Australia | All Ordinaries | AUD | 0.37% | -0.09% | **-0.10%** | [-3.1%, 4.7%] | -0.71% | 3.73% | -3.83% | -39.40% | -0.00 | 0.05 | 11 | 2011-01-04 |
| 22 | United Kingdom | FTSE 100 | GBP | 1.16% | 0.84% | **-0.13%** | [-2.4%, 5.7%] | -1.31% | 2.71% | -2.84% | -34.31% | -0.00 | 0.04 | 15 | 2011-01-04 |
| 23 | Mexico | IPC Mexico | MXN | 0.33% | 0.14% | **-0.51%** | [-2.3%, 3.2%] | -1.22% | 3.17% | -3.68% | -40.27% | -0.01 | 0.01 | 15 | 2011-01-03 |
| 24 | Australia | ASX 200 | AUD | -0.45% | -0.91% | **-0.92%** | [-4.0%, 4.2%] | -1.53% | 3.66% | -4.57% | -43.27% | -0.02 | -0.02 | 10 | 2011-01-04 |
| 25 | France | CAC 40 | EUR | 0.52% | -0.50% | **-0.94%** | [-4.7%, 5.7%] | -1.82% | 3.83% | -4.76% | -52.20% | -0.02 | 0.02 | 10 | 2011-01-03 |

## 2. Secondary Ranking: Calmar Ratio (Risk-Adjusted Efficiency)

Re-sorted by Calmar Ratio (CAGR / |Max Drawdown|) computed on the Net-of-Tax-and-Discount-Brokerage series.


| Calmar Rank | Country | Index | Calmar Ratio | Net-Disc CAGR | Max Drawdown | Sharpe | Total Trades |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|
| 1 | United States | Nasdaq Composite | **0.21** | 8.66% | -41.13% | 0.54 | 9 |
| 2 | United States | S&P 500 | **0.19** | 6.95% | -35.80% | 0.52 | 8 |
| 3 | India | BSE Sensex | **0.14** | 5.44% | -38.48% | 0.47 | 9 |
| 4 | Spain | IBEX 35 | **0.11** | 3.71% | -35.18% | 0.35 | 8 |
| 5 | Japan | Nikkei 225 | **0.10** | 5.20% | -51.07% | 0.36 | 10 |
| 6 | South Korea | KOSPI | **0.10** | 2.94% | -30.07% | 0.31 | 16 |
| 7 | India | Nifty 50 | **0.10** | 4.14% | -42.84% | 0.37 | 12 |
| 8 | Germany | TecDAX | **0.09** | 4.58% | -48.72% | 0.33 | 10 |
| 9 | United States | Dow Jones Industrial Average | **0.09** | 3.67% | -42.40% | 0.32 | 11 |
| 10 | India | Nifty Bank | **0.08** | 4.07% | -51.01% | 0.32 | 8 |
| 11 | Italy | FTSE MIB | **0.06** | 2.57% | -43.90% | 0.23 | 6 |
| 12 | Indonesia | Jakarta Composite Index | **0.05** | 1.45% | -26.95% | 0.19 | 13 |
| 13 | United Kingdom | FTSE 250 | **0.05** | 1.56% | -30.60% | 0.20 | 10 |
| 14 | Canada | S&P/TSX Composite | **0.04** | 1.78% | -40.47% | 0.21 | 10 |
| 15 | China | Shenzhen Component | **0.04** | 2.45% | -58.60% | 0.23 | 10 |
| 16 | China | Shanghai Composite | **0.04** | 2.01% | -52.23% | 0.21 | 9 |
| 17 | Germany | DAX 40 | **0.03** | 1.98% | -57.16% | 0.20 | 11 |
| 18 | South Korea | KOSDAQ | **0.03** | 1.27% | -37.40% | 0.16 | 14 |
| 19 | Germany | MDAX | **0.02** | 1.22% | -49.51% | 0.16 | 13 |
| 20 | Brazil | Ibovespa | **0.02** | 1.16% | -58.86% | 0.16 | 13 |
| 21 | Australia | All Ordinaries | **-0.00** | -0.10% | -39.40% | 0.05 | 11 |
| 22 | United Kingdom | FTSE 100 | **-0.00** | -0.13% | -34.31% | 0.04 | 15 |
| 23 | Mexico | IPC Mexico | **-0.01** | -0.51% | -40.27% | 0.01 | 15 |
| 24 | France | CAC 40 | **-0.02** | -0.94% | -52.20% | 0.02 | 10 |
| 25 | Australia | ASX 200 | **-0.02** | -0.92% | -43.27% | -0.02 | 10 |

## 3. Skeptical Robustness & Overfitting Evaluation

In-Sample (2011–2018) vs Out-of-Sample (2019–2025) performance degradation, 1,000 Monte Carlo trade sequence permutations, and 95% bootstrap CAGR confidence intervals.


| Country | Index | IS CAGR (2011-18) | OOS CAGR (2019-25) | Degradation (OOS/IS) | IS Trades | OOS Trades | IS Guard | OOS Guard | MC Worst DD (P95) | 95% Bootstrap CI | Precision Flag |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| United States | Nasdaq Composite | 7.53% | 9.89% | 1.31x (+2.36 pp) | 4 | 5 | PASS | PASS | -21.17% | [0.2%, 20.7%] | `Directional (n<30)` |
| United States | S&P 500 | 5.64% | 8.44% | 1.50x (+2.80 pp) | 5 | 3 | PASS | PASS | -16.33% | [0.2%, 16.8%] | `Directional (n<30)` |
| India | BSE Sensex | 7.98% | 2.69% | 0.34x (-5.30 pp) | 3 | 6 | PASS | PASS | -26.13% | [-1.4%, 13.1%] | `Directional (n<30)` |
| Japan | Nikkei 225 | 4.94% | 5.92% | 1.20x (+0.98 pp) | 5 | 5 | PASS | PASS | -36.00% | [-2.5%, 17.3%] | `Directional (n<30)` |
| Germany | TecDAX | 11.70% | -3.08% | -0.26x (-14.79 pp) | 3 | 7 | PASS | PASS | -23.31% | [-2.0%, 18.9%] | `Directional (n<30)` |
| India | Nifty 50 | 7.49% | 0.54% | 0.07x (-6.96 pp) | 4 | 8 | PASS | PASS | -30.61% | [-3.6%, 11.0%] | `Directional (n<30)` |
| India | Nifty Bank | 8.09% | -0.46% | -0.06x (-8.55 pp) | 4 | 4 | PASS | PASS | -38.20% | [-5.7%, 14.6%] | `Directional (n<30)` |
| Spain | IBEX 35 | 1.42% | 6.40% | 4.52x (+4.98 pp) | 5 | 3 | PASS | PASS | -22.38% | [-2.6%, 17.0%] | `Directional (n<30)` |
| United States | Dow Jones Industrial Average | 5.18% | 1.96% | 0.38x (-3.22 pp) | 5 | 6 | PASS | PASS | -25.77% | [-2.1%, 11.6%] | `Directional (n<30)` |
| South Korea | KOSPI | -0.12% | 6.56% | -56.73x (+6.67 pp) | 10 | 6 | PASS | PASS | -14.90% | [-0.7%, 8.5%] | `Directional (n<30)` |
| Italy | FTSE MIB | 2.42% | 2.73% | 1.13x (+0.31 pp) | 3 | 3 | PASS | PASS | -22.29% | [-3.3%, 12.2%] | `Directional (n<30)` |
| China | Shenzhen Component | -2.22% | 8.05% | -3.63x (+10.27 pp) | 8 | 2 | PASS | PASS | -17.15% | [-1.9%, 8.8%] | `Directional (n<30)` |
| China | Shanghai Composite | 1.37% | 2.75% | 2.01x (+1.38 pp) | 4 | 5 | PASS | PASS | -17.55% | [-1.5%, 6.1%] | `Directional (n<30)` |
| Germany | DAX 40 | 2.81% | 1.05% | 0.37x (-1.76 pp) | 5 | 6 | PASS | PASS | -32.96% | [-3.9%, 13.2%] | `Directional (n<30)` |
| Canada | S&P/TSX Composite | 2.02% | 1.51% | 0.75x (-0.51 pp) | 3 | 7 | PASS | PASS | -30.47% | [-3.9%, 9.7%] | `Directional (n<30)` |
| United Kingdom | FTSE 250 | 4.83% | -2.05% | -0.43x (-6.88 pp) | 3 | 7 | PASS | PASS | -13.30% | [-0.8%, 7.4%] | `Directional (n<30)` |
| Indonesia | Jakarta Composite Index | 0.71% | 2.34% | 3.28x (+1.63 pp) | 8 | 5 | PASS | PASS | -15.60% | [-1.3%, 5.7%] | `Directional (n<30)` |
| South Korea | KOSDAQ | -1.18% | 4.14% | -3.52x (+5.31 pp) | 10 | 4 | PASS | PASS | -25.38% | [-2.2%, 6.4%] | `Directional (n<30)` |
| Germany | MDAX | 6.26% | -4.25% | -0.68x (-10.51 pp) | 5 | 8 | PASS | PASS | -38.38% | [-4.5%, 14.2%] | `Directional (n<30)` |
| Brazil | Ibovespa | 5.34% | -3.89% | -0.73x (-9.23 pp) | 6 | 7 | PASS | PASS | -29.57% | [-3.2%, 6.4%] | `Directional (n<30)` |
| Australia | All Ordinaries | 0.99% | -1.32% | -1.34x (-2.31 pp) | 5 | 6 | PASS | PASS | -26.93% | [-3.1%, 4.7%] | `Directional (n<30)` |
| United Kingdom | FTSE 100 | -1.24% | 1.16% | -0.94x (+2.40 pp) | 7 | 8 | PASS | PASS | -26.25% | [-2.4%, 5.7%] | `Directional (n<30)` |
| Mexico | IPC Mexico | 1.42% | -2.67% | -1.88x (-4.09 pp) | 6 | 9 | PASS | PASS | -21.68% | [-2.3%, 3.2%] | `Directional (n<30)` |
| Australia | ASX 200 | 1.40% | -3.50% | -2.50x (-4.91 pp) | 4 | 6 | PASS | PASS | -33.40% | [-4.0%, 4.2%] | `Directional (n<30)` |
| France | CAC 40 | 0.91% | -3.00% | -3.30x (-3.91 pp) | 4 | 6 | PASS | PASS | -31.86% | [-4.7%, 5.7%] | `Directional (n<30)` |

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