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
| 2 | Germany | TecDAX | EUR | 7.76% | 5.91% | **5.91%** | [2.0%, 13.6%] | 5.77% | 8.43% | -2.52% | -31.42% | 0.19 | 0.43 | 39 | 2011-01-03 |
| 3 | United Kingdom | FTSE 100 | GBP | 8.65% | 8.43% | **5.79%** | [4.6%, 12.0%] | 1.34% | 2.71% | +3.08% | -44.06% | 0.13 | 0.43 | 51 | 2011-01-04 |
| 4 | United States | Dow Jones Industrial Average | USD | 6.71% | 5.14% | **5.12%** | [3.2%, 10.0%] | 4.40% | 9.06% | -3.94% | -37.01% | 0.14 | 0.40 | 42 | 2011-01-03 |
| 5 | United States | Nasdaq Composite | USD | 6.81% | 4.94% | **4.92%** | [2.6%, 11.1%] | 4.29% | 14.43% | -9.52% | -31.34% | 0.16 | 0.35 | 36 | 2011-01-03 |
| 6 | Italy | FTSE MIB | EUR | 7.41% | 5.11% | **4.63%** | [-1.2%, 15.3%] | 3.29% | 4.30% | +0.33% | -47.14% | 0.10 | 0.31 | 47 | 2011-01-03 |
| 7 | Japan | Nikkei 225 | JPY | 5.69% | 4.29% | **4.02%** | [0.7%, 10.1%] | 0.00% | 9.81% | -5.79% | -41.42% | 0.10 | 0.31 | 38 | 2011-01-04 |
| 8 | Germany | MDAX | EUR | 6.06% | 3.78% | **3.78%** | [0.4%, 11.5%] | 3.57% | 6.24% | -2.46% | -47.81% | 0.08 | 0.31 | 44 | 2011-01-03 |
| 9 | Germany | DAX 40 | EUR | 5.23% | 3.62% | **3.62%** | [-0.3%, 10.8%] | 3.42% | 7.23% | -3.61% | -39.90% | 0.09 | 0.30 | 41 | 2011-01-03 |
| 10 | Canada | S&P/TSX Composite | CAD | 4.06% | 3.20% | **3.18%** | [0.2%, 7.4%] | 1.20% | 5.25% | -2.06% | -39.63% | 0.08 | 0.31 | 40 | 2011-01-04 |
| 11 | India | BSE Sensex | INR | 4.01% | 3.61% | **3.10%** | [-0.7%, 8.3%] | 1.05% | 9.48% | -6.38% | -42.11% | 0.07 | 0.30 | 36 | 2011-01-03 |
| 12 | Mexico | IPC Mexico | MXN | 4.89% | 4.34% | **2.92%** | [0.5%, 9.5%] | 1.15% | 3.17% | -0.26% | -36.64% | 0.08 | 0.28 | 47 | 2011-01-03 |
| 13 | Brazil | Ibovespa | BRL | 2.79% | 2.79% | **2.66%** | [-3.9%, 9.0%] | 0.37% | 5.19% | -2.54% | -41.25% | 0.06 | 0.24 | 40 | 2011-01-03 |
| 14 | Australia | ASX 200 | AUD | 4.76% | 2.68% | **2.65%** | [0.8%, 8.3%] | 0.02% | 3.66% | -1.01% | -40.31% | 0.07 | 0.26 | 42 | 2011-01-04 |
| 15 | Australia | All Ordinaries | AUD | 4.31% | 2.16% | **2.12%** | [0.1%, 7.6%] | -0.77% | 3.73% | -1.61% | -41.82% | 0.05 | 0.22 | 42 | 2011-01-04 |
| 16 | South Korea | KOSDAQ | KRW | 3.43% | 3.43% | **1.89%** | [-0.8%, 7.7%] | -2.18% | 3.94% | -2.05% | -49.87% | 0.04 | 0.20 | 45 | 2011-01-03 |
| 17 | India | Nifty 50 | INR | 2.80% | 2.28% | **1.69%** | [-1.6%, 6.5%] | -0.79% | 9.63% | -7.94% | -45.09% | 0.04 | 0.19 | 37 | 2011-01-03 |
| 18 | Spain | IBEX 35 | EUR | 2.90% | 1.44% | **1.09%** | [-4.7%, 9.5%] | -0.91% | 3.16% | -2.07% | -39.45% | 0.03 | 0.15 | 42 | 2011-01-03 |
| 19 | South Korea | KOSPI | KRW | 2.56% | 2.56% | **0.91%** | [-1.3%, 6.6%] | -3.33% | 4.86% | -3.95% | -36.44% | 0.02 | 0.14 | 43 | 2011-01-03 |
| 20 | India | Nifty Bank | INR | 1.74% | 1.29% | **0.66%** | [-5.3%, 7.4%] | -1.90% | 10.79% | -10.14% | -51.97% | 0.01 | 0.13 | 41 | 2011-01-03 |
| 21 | China | Shanghai Composite | CNY | 1.09% | 1.09% | **0.50%** | [-4.1%, 5.8%] | 0.44% | 2.22% | -1.72% | -41.60% | 0.01 | 0.11 | 45 | 2011-01-04 |
| 22 | France | CAC 40 | EUR | 4.86% | 1.89% | **0.01%** | [-1.0%, 10.2%] | -6.29% | 3.83% | -3.82% | -52.31% | 0.00 | 0.11 | 42 | 2011-01-03 |
| 23 | Indonesia | Jakarta Composite Index | IDR | 1.10% | 1.10% | **-0.21%** | [-3.8%, 5.4%] | -0.53% | 5.76% | -5.98% | -45.92% | -0.00 | 0.05 | 31 | 2011-01-03 |
| 24 | United Kingdom | FTSE 250 | GBP | 2.75% | 2.67% | **-0.63%** | [-2.7%, 7.7%] | -7.68% | 3.60% | -4.24% | -53.33% | -0.01 | 0.05 | 44 | 2011-01-04 |
| 25 | China | Shenzhen Component | CNY | -1.37% | -1.37% | **-2.06%** | [-8.6%, 5.1%] | -2.12% | 0.45% | -2.50% | -51.27% | -0.04 | -0.03 | 40 | 2011-01-04 |

## 2. Secondary Ranking: Calmar Ratio (Risk-Adjusted Efficiency)

Re-sorted by Calmar Ratio (CAGR / |Max Drawdown|) computed on the Net-of-Tax-and-Discount-Brokerage series.


| Calmar Rank | Country | Index | Calmar Ratio | Net-Disc CAGR | Max Drawdown | Sharpe | Total Trades |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|
| 1 | Germany | TecDAX | **0.19** | 5.91% | -31.42% | 0.43 | 39 |
| 2 | United States | S&P 500 | **0.17** | 6.06% | -35.33% | 0.44 | 38 |
| 3 | United States | Nasdaq Composite | **0.16** | 4.92% | -31.34% | 0.35 | 36 |
| 4 | United States | Dow Jones Industrial Average | **0.14** | 5.12% | -37.01% | 0.40 | 42 |
| 5 | United Kingdom | FTSE 100 | **0.13** | 5.79% | -44.06% | 0.43 | 51 |
| 6 | Italy | FTSE MIB | **0.10** | 4.63% | -47.14% | 0.31 | 47 |
| 7 | Japan | Nikkei 225 | **0.10** | 4.02% | -41.42% | 0.31 | 38 |
| 8 | Germany | DAX 40 | **0.09** | 3.62% | -39.90% | 0.30 | 41 |
| 9 | Canada | S&P/TSX Composite | **0.08** | 3.18% | -39.63% | 0.31 | 40 |
| 10 | Mexico | IPC Mexico | **0.08** | 2.92% | -36.64% | 0.28 | 47 |
| 11 | Germany | MDAX | **0.08** | 3.78% | -47.81% | 0.31 | 44 |
| 12 | India | BSE Sensex | **0.07** | 3.10% | -42.11% | 0.30 | 36 |
| 13 | Australia | ASX 200 | **0.07** | 2.65% | -40.31% | 0.26 | 42 |
| 14 | Brazil | Ibovespa | **0.06** | 2.66% | -41.25% | 0.24 | 40 |
| 15 | Australia | All Ordinaries | **0.05** | 2.12% | -41.82% | 0.22 | 42 |
| 16 | South Korea | KOSDAQ | **0.04** | 1.89% | -49.87% | 0.20 | 45 |
| 17 | India | Nifty 50 | **0.04** | 1.69% | -45.09% | 0.19 | 37 |
| 18 | Spain | IBEX 35 | **0.03** | 1.09% | -39.45% | 0.15 | 42 |
| 19 | South Korea | KOSPI | **0.02** | 0.91% | -36.44% | 0.14 | 43 |
| 20 | India | Nifty Bank | **0.01** | 0.66% | -51.97% | 0.13 | 41 |
| 21 | China | Shanghai Composite | **0.01** | 0.50% | -41.60% | 0.11 | 45 |
| 22 | France | CAC 40 | **0.00** | 0.01% | -52.31% | 0.11 | 42 |
| 23 | Indonesia | Jakarta Composite Index | **-0.00** | -0.21% | -45.92% | 0.05 | 31 |
| 24 | United Kingdom | FTSE 250 | **-0.01** | -0.63% | -53.33% | 0.05 | 44 |
| 25 | China | Shenzhen Component | **-0.04** | -2.06% | -51.27% | -0.03 | 40 |

## 3. Skeptical Robustness & Overfitting Evaluation

In-Sample (2011–2018) vs Out-of-Sample (2019–2025) performance degradation, 1,000 Monte Carlo trade sequence permutations, and 95% bootstrap CAGR confidence intervals.


| Country | Index | IS CAGR (2011-18) | OOS CAGR (2019-25) | Degradation (OOS/IS) | IS Trades | OOS Trades | IS Guard | OOS Guard | MC Worst DD (P95) | 95% Bootstrap CI | Precision Flag |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| United States | S&P 500 | 7.00% | 4.97% | 0.71x (-2.04 pp) | 21 | 17 | PASS | PASS | -19.18% | [4.0%, 11.6%] | `Robust (n>=30)` |
| Germany | TecDAX | 3.55% | 8.57% | 2.42x (+5.03 pp) | 17 | 22 | PASS | PASS | -29.80% | [2.0%, 13.6%] | `Robust (n>=30)` |
| United Kingdom | FTSE 100 | 4.75% | 6.99% | 1.47x (+2.24 pp) | 29 | 22 | PASS | PASS | -17.90% | [4.6%, 12.0%] | `Robust (n>=30)` |
| United States | Dow Jones Industrial Average | 3.76% | 6.69% | 1.78x (+2.93 pp) | 20 | 22 | PASS | PASS | -17.46% | [3.2%, 10.0%] | `Robust (n>=30)` |
| United States | Nasdaq Composite | 4.65% | 5.15% | 1.11x (+0.50 pp) | 18 | 18 | PASS | PASS | -18.87% | [2.6%, 11.1%] | `Robust (n>=30)` |
| Italy | FTSE MIB | 1.43% | 8.40% | 5.85x (+6.96 pp) | 27 | 20 | PASS | PASS | -44.20% | [-1.2%, 15.3%] | `Robust (n>=30)` |
| Japan | Nikkei 225 | 0.98% | 8.03% | 8.18x (+7.05 pp) | 20 | 18 | PASS | PASS | -23.79% | [0.7%, 10.1%] | `Robust (n>=30)` |
| Germany | MDAX | 5.93% | 1.29% | 0.22x (-4.64 pp) | 23 | 21 | PASS | PASS | -33.10% | [0.4%, 11.5%] | `Robust (n>=30)` |
| Germany | DAX 40 | 1.17% | 6.46% | 5.54x (+5.29 pp) | 21 | 20 | PASS | PASS | -31.64% | [-0.3%, 10.8%] | `Robust (n>=30)` |
| Canada | S&P/TSX Composite | 1.03% | 5.67% | 5.48x (+4.63 pp) | 20 | 20 | PASS | PASS | -22.68% | [0.2%, 7.4%] | `Robust (n>=30)` |
| India | BSE Sensex | 3.02% | 3.20% | 1.06x (+0.18 pp) | 20 | 16 | PASS | PASS | -25.36% | [-0.7%, 8.3%] | `Robust (n>=30)` |
| Mexico | IPC Mexico | -1.99% | 8.56% | -4.30x (+10.55 pp) | 21 | 26 | PASS | PASS | -24.52% | [0.5%, 9.5%] | `Robust (n>=30)` |
| Brazil | Ibovespa | 1.22% | 3.80% | 3.12x (+2.59 pp) | 22 | 18 | PASS | PASS | -42.61% | [-3.9%, 9.0%] | `Robust (n>=30)` |
| Australia | ASX 200 | 2.99% | 2.54% | 0.85x (-0.45 pp) | 23 | 19 | PASS | PASS | -23.68% | [0.8%, 8.3%] | `Robust (n>=30)` |
| Australia | All Ordinaries | 3.72% | 0.58% | 0.16x (-3.14 pp) | 25 | 17 | PASS | PASS | -24.47% | [0.1%, 7.6%] | `Robust (n>=30)` |
| South Korea | KOSDAQ | 3.16% | 0.47% | 0.15x (-2.68 pp) | 22 | 23 | PASS | PASS | -26.50% | [-0.8%, 7.7%] | `Robust (n>=30)` |
| India | Nifty 50 | 2.67% | 0.57% | 0.21x (-2.10 pp) | 22 | 15 | PASS | PASS | -27.85% | [-1.6%, 6.5%] | `Robust (n>=30)` |
| Spain | IBEX 35 | -1.43% | 4.02% | -2.82x (+5.45 pp) | 24 | 18 | PASS | PASS | -43.00% | [-4.7%, 9.5%] | `Robust (n>=30)` |
| South Korea | KOSPI | 3.14% | -1.58% | -0.50x (-4.72 pp) | 26 | 17 | PASS | PASS | -26.02% | [-1.3%, 6.6%] | `Robust (n>=30)` |
| India | Nifty Bank | 0.44% | 0.90% | 2.03x (+0.46 pp) | 20 | 21 | PASS | PASS | -43.69% | [-5.3%, 7.4%] | `Robust (n>=30)` |
| China | Shanghai Composite | -3.92% | 5.98% | -1.53x (+9.90 pp) | 25 | 20 | PASS | PASS | -40.48% | [-4.1%, 5.8%] | `Robust (n>=30)` |
| France | CAC 40 | -0.19% | 0.42% | -2.22x (+0.61 pp) | 23 | 19 | PASS | PASS | -35.91% | [-1.0%, 10.2%] | `Robust (n>=30)` |
| Indonesia | Jakarta Composite Index | -0.15% | -0.28% | 1.89x (-0.13 pp) | 14 | 17 | PASS | PASS | -35.14% | [-3.8%, 5.4%] | `Robust (n>=30)` |
| United Kingdom | FTSE 250 | -0.20% | -1.21% | 6.04x (-1.01 pp) | 22 | 22 | PASS | PASS | -35.98% | [-2.7%, 7.7%] | `Robust (n>=30)` |
| China | Shenzhen Component | -4.72% | 1.26% | -0.27x (+5.98 pp) | 23 | 17 | PASS | PASS | -57.08% | [-8.6%, 5.1%] | `Robust (n>=30)` |

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