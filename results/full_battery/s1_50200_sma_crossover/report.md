# Cross-Market Strategy Backtest & Friction Impact Report

**Strategy Parsing Method:** `Deterministic Rule-Based Parser`

**Random Seed:** `42` (Deterministic Monte Carlo & Bootstrap Resampling)

**Tax & Brokerage Dataset Status:** `Reference / Preliminary Baseline (primary_statutory_single_source)`

> **Strategy Description**: *"Buy when the 50-day moving average crosses above the 200-day moving average, sell when it crosses below, using the full index value as position size, no leverage, no shorting."*

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
| 1 | United States | Nasdaq Composite | USD | 11.82% | 10.71% | **10.70%** | [4.2%, 19.5%] | 10.64% | 14.43% | -3.73% | -32.55% | 0.33 | 0.65 | 8 | 2011-01-03 |
| 2 | United States | S&P 500 | USD | 8.08% | 7.13% | **7.13%** | [1.6%, 14.1%] | 7.04% | 10.97% | -3.83% | -36.18% | 0.20 | 0.54 | 7 | 2011-01-03 |
| 3 | India | Nifty Bank | INR | 6.06% | 6.06% | **5.96%** | [-4.8%, 16.6%] | 5.57% | 10.79% | -4.84% | -47.53% | 0.13 | 0.44 | 10 | 2011-01-03 |
| 4 | Japan | Nikkei 225 | JPY | 7.47% | 5.95% | **5.88%** | [-1.6%, 16.9%] | 3.15% | 9.81% | -3.92% | -43.72% | 0.13 | 0.41 | 13 | 2011-01-04 |
| 5 | Germany | TecDAX | EUR | 6.98% | 5.49% | **5.49%** | [0.3%, 16.1%] | 5.46% | 8.43% | -2.95% | -45.46% | 0.12 | 0.38 | 8 | 2011-01-03 |
| 6 | India | BSE Sensex | INR | 5.13% | 5.13% | **5.01%** | [-3.6%, 14.2%] | 4.58% | 9.48% | -4.47% | -40.08% | 0.12 | 0.45 | 11 | 2011-01-03 |
| 7 | India | Nifty 50 | INR | 4.96% | 4.96% | **4.84%** | [-3.7%, 13.7%] | 4.41% | 9.63% | -4.79% | -43.18% | 0.11 | 0.46 | 11 | 2011-01-03 |
| 8 | Germany | DAX 40 | EUR | 5.46% | 3.94% | **3.94%** | [-2.5%, 13.2%] | 3.90% | 7.23% | -3.29% | -46.54% | 0.08 | 0.33 | 8 | 2011-01-03 |
| 9 | United States | Dow Jones Industrial Average | USD | 4.42% | 3.53% | **3.52%** | [-2.4%, 11.2%] | 3.36% | 9.06% | -5.54% | -42.01% | 0.08 | 0.32 | 8 | 2011-01-03 |
| 10 | Indonesia | Jakarta Composite Index | IDR | 3.75% | 3.75% | **3.48%** | [0.5%, 7.4%] | 3.42% | 5.76% | -2.29% | -23.58% | 0.15 | 0.38 | 8 | 2011-01-03 |
| 11 | Italy | FTSE MIB | EUR | 4.14% | 2.68% | **2.61%** | [-5.4%, 15.9%] | 2.43% | 4.30% | -1.69% | -44.96% | 0.06 | 0.23 | 8 | 2011-01-03 |
| 12 | Spain | IBEX 35 | EUR | 3.20% | 1.98% | **1.93%** | [-6.0%, 14.1%] | 1.58% | 3.16% | -1.22% | -50.41% | 0.04 | 0.20 | 9 | 2011-01-03 |
| 13 | China | Shenzhen Component | CNY | 1.72% | 1.72% | **1.58%** | [-4.9%, 9.3%] | 1.56% | 0.45% | +1.13% | -56.73% | 0.03 | 0.18 | 11 | 2011-01-04 |
| 14 | Germany | MDAX | EUR | 3.62% | 1.57% | **1.56%** | [-4.1%, 12.7%] | 1.50% | 6.24% | -4.67% | -51.41% | 0.03 | 0.18 | 10 | 2011-01-03 |
| 15 | South Korea | KOSPI | KRW | 1.70% | 1.70% | **1.27%** | [-6.3%, 10.5%] | 0.48% | 4.86% | -3.59% | -51.54% | 0.02 | 0.17 | 16 | 2011-01-03 |
| 16 | Canada | S&P/TSX Composite | CAD | 1.69% | 0.87% | **0.86%** | [-6.5%, 10.0%] | 0.31% | 5.25% | -4.38% | -45.42% | 0.02 | 0.13 | 12 | 2011-01-04 |
| 17 | South Korea | KOSDAQ | KRW | 1.06% | 1.06% | **0.64%** | [-5.5%, 9.0%] | -0.18% | 3.94% | -3.30% | -47.06% | 0.01 | 0.12 | 13 | 2011-01-03 |
| 18 | Australia | All Ordinaries | AUD | 0.97% | 0.38% | **0.37%** | [-4.4%, 6.8%] | -0.18% | 3.73% | -3.37% | -36.50% | 0.01 | 0.09 | 10 | 2011-01-04 |
| 19 | United Kingdom | FTSE 100 | GBP | 0.89% | 0.59% | **-0.12%** | [-4.4%, 6.0%] | -0.96% | 2.71% | -2.83% | -41.93% | -0.00 | 0.05 | 11 | 2011-01-04 |
| 20 | China | Shanghai Composite | CNY | -0.00% | -0.00% | **-0.17%** | [-5.2%, 6.7%] | -0.19% | 2.22% | -2.39% | -58.04% | -0.00 | 0.06 | 11 | 2011-01-04 |
| 21 | Australia | ASX 200 | AUD | 0.37% | -0.19% | **-0.20%** | [-4.9%, 5.5%] | -0.83% | 3.66% | -3.85% | -37.44% | -0.01 | 0.04 | 11 | 2011-01-04 |
| 22 | United Kingdom | FTSE 250 | GBP | 0.84% | 0.39% | **-0.50%** | [-7.3%, 8.3%] | -1.57% | 3.60% | -4.10% | -51.95% | -0.01 | 0.02 | 11 | 2011-01-04 |
| 23 | Mexico | IPC Mexico | MXN | -0.54% | -0.77% | **-1.24%** | [-5.3%, 4.5%] | -1.75% | 3.17% | -4.42% | -52.43% | -0.02 | -0.05 | 12 | 2011-01-03 |
| 24 | France | CAC 40 | EUR | -0.13% | -1.69% | **-2.18%** | [-6.7%, 6.4%] | -3.24% | 3.83% | -6.00% | -52.71% | -0.04 | -0.06 | 11 | 2011-01-03 |
| 25 | Brazil | Ibovespa | BRL | -3.83% | -3.83% | **-3.91%** | [-9.2%, 3.2%] | -5.04% | 5.19% | -9.10% | -57.04% | -0.07 | -0.14 | 14 | 2011-01-03 |

## 2. Secondary Ranking: Calmar Ratio (Risk-Adjusted Efficiency)

Re-sorted by Calmar Ratio (CAGR / |Max Drawdown|) computed on the Net-of-Tax-and-Discount-Brokerage series.


| Calmar Rank | Country | Index | Calmar Ratio | Net-Disc CAGR | Max Drawdown | Sharpe | Total Trades |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|
| 1 | United States | Nasdaq Composite | **0.33** | 10.70% | -32.55% | 0.65 | 8 |
| 2 | United States | S&P 500 | **0.20** | 7.13% | -36.18% | 0.54 | 7 |
| 3 | Indonesia | Jakarta Composite Index | **0.15** | 3.48% | -23.58% | 0.38 | 8 |
| 4 | Japan | Nikkei 225 | **0.13** | 5.88% | -43.72% | 0.41 | 13 |
| 5 | India | Nifty Bank | **0.13** | 5.96% | -47.53% | 0.44 | 10 |
| 6 | India | BSE Sensex | **0.12** | 5.01% | -40.08% | 0.45 | 11 |
| 7 | Germany | TecDAX | **0.12** | 5.49% | -45.46% | 0.38 | 8 |
| 8 | India | Nifty 50 | **0.11** | 4.84% | -43.18% | 0.46 | 11 |
| 9 | Germany | DAX 40 | **0.08** | 3.94% | -46.54% | 0.33 | 8 |
| 10 | United States | Dow Jones Industrial Average | **0.08** | 3.52% | -42.01% | 0.32 | 8 |
| 11 | Italy | FTSE MIB | **0.06** | 2.61% | -44.96% | 0.23 | 8 |
| 12 | Spain | IBEX 35 | **0.04** | 1.93% | -50.41% | 0.20 | 9 |
| 13 | Germany | MDAX | **0.03** | 1.56% | -51.41% | 0.18 | 10 |
| 14 | China | Shenzhen Component | **0.03** | 1.58% | -56.73% | 0.18 | 11 |
| 15 | South Korea | KOSPI | **0.02** | 1.27% | -51.54% | 0.17 | 16 |
| 16 | Canada | S&P/TSX Composite | **0.02** | 0.86% | -45.42% | 0.13 | 12 |
| 17 | South Korea | KOSDAQ | **0.01** | 0.64% | -47.06% | 0.12 | 13 |
| 18 | Australia | All Ordinaries | **0.01** | 0.37% | -36.50% | 0.09 | 10 |
| 19 | China | Shanghai Composite | **-0.00** | -0.17% | -58.04% | 0.06 | 11 |
| 20 | United Kingdom | FTSE 100 | **-0.00** | -0.12% | -41.93% | 0.05 | 11 |
| 21 | Australia | ASX 200 | **-0.01** | -0.20% | -37.44% | 0.04 | 11 |
| 22 | United Kingdom | FTSE 250 | **-0.01** | -0.50% | -51.95% | 0.02 | 11 |
| 23 | Mexico | IPC Mexico | **-0.02** | -1.24% | -52.43% | -0.05 | 12 |
| 24 | France | CAC 40 | **-0.04** | -2.18% | -52.71% | -0.06 | 11 |
| 25 | Brazil | Ibovespa | **-0.07** | -3.91% | -57.04% | -0.14 | 14 |

## 3. Skeptical Robustness & Overfitting Evaluation

In-Sample (2011–2018) vs Out-of-Sample (2019–2025) performance degradation, 1,000 Monte Carlo trade sequence permutations, and 95% bootstrap CAGR confidence intervals.


| Country | Index | IS CAGR (2011-18) | OOS CAGR (2019-25) | Degradation (OOS/IS) | IS Trades | OOS Trades | IS Guard | OOS Guard | MC Worst DD (P95) | 95% Bootstrap CI | Precision Flag |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| United States | Nasdaq Composite | 8.22% | 13.62% | 1.66x (+5.39 pp) | 4 | 4 | PASS | PASS | -10.85% | [4.2%, 19.5%] | `Directional (n<30)` |
| United States | S&P 500 | 6.72% | 7.60% | 1.13x (+0.88 pp) | 3 | 4 | PASS | PASS | -13.13% | [1.6%, 14.1%] | `Directional (n<30)` |
| India | Nifty Bank | 8.71% | 2.89% | 0.33x (-5.82 pp) | 5 | 5 | PASS | PASS | -44.18% | [-4.8%, 16.6%] | `Directional (n<30)` |
| Japan | Nikkei 225 | 6.80% | 4.86% | 0.71x (-1.94 pp) | 5 | 8 | PASS | PASS | -34.96% | [-1.6%, 16.9%] | `Directional (n<30)` |
| Germany | TecDAX | 10.25% | 0.31% | 0.03x (-9.94 pp) | 3 | 5 | PASS | PASS | -11.44% | [0.3%, 16.1%] | `Directional (n<30)` |
| India | BSE Sensex | 5.19% | 4.81% | 0.93x (-0.38 pp) | 5 | 6 | PASS | PASS | -36.94% | [-3.6%, 14.2%] | `Directional (n<30)` |
| India | Nifty 50 | 5.69% | 3.88% | 0.68x (-1.81 pp) | 5 | 6 | PASS | PASS | -37.79% | [-3.7%, 13.7%] | `Directional (n<30)` |
| Germany | DAX 40 | 4.73% | 3.05% | 0.64x (-1.68 pp) | 4 | 4 | PASS | PASS | -30.46% | [-2.5%, 13.2%] | `Directional (n<30)` |
| United States | Dow Jones Industrial Average | 5.63% | 1.17% | 0.21x (-4.46 pp) | 3 | 5 | PASS | PASS | -29.58% | [-2.4%, 11.2%] | `Directional (n<30)` |
| Indonesia | Jakarta Composite Index | 2.85% | 4.20% | 1.47x (+1.35 pp) | 3 | 5 | PASS | PASS | -4.53% | [0.5%, 7.4%] | `Directional (n<30)` |
| Italy | FTSE MIB | 0.42% | 5.18% | 12.39x (+4.76 pp) | 5 | 3 | PASS | PASS | -42.40% | [-5.4%, 15.9%] | `Directional (n<30)` |
| Spain | IBEX 35 | 2.16% | 1.67% | 0.77x (-0.49 pp) | 4 | 5 | PASS | PASS | -43.47% | [-6.0%, 14.1%] | `Directional (n<30)` |
| China | Shenzhen Component | -1.88% | 5.68% | -3.02x (+7.56 pp) | 5 | 6 | PASS | PASS | -39.00% | [-4.9%, 9.3%] | `Directional (n<30)` |
| Germany | MDAX | 5.68% | -2.93% | -0.52x (-8.61 pp) | 5 | 5 | PASS | PASS | -38.48% | [-4.1%, 12.7%] | `Directional (n<30)` |
| South Korea | KOSPI | -1.92% | 5.04% | -2.62x (+6.96 pp) | 10 | 6 | PASS | PASS | -47.62% | [-6.3%, 10.5%] | `Directional (n<30)` |
| Canada | S&P/TSX Composite | -0.96% | 2.99% | -3.11x (+3.96 pp) | 7 | 5 | PASS | PASS | -45.06% | [-6.5%, 10.0%] | `Directional (n<30)` |
| South Korea | KOSDAQ | 1.58% | -0.41% | -0.26x (-1.99 pp) | 6 | 7 | PASS | PASS | -42.71% | [-5.5%, 9.0%] | `Directional (n<30)` |
| Australia | All Ordinaries | 1.77% | -1.21% | -0.69x (-2.98 pp) | 5 | 5 | PASS | PASS | -31.65% | [-4.4%, 6.8%] | `Directional (n<30)` |
| United Kingdom | FTSE 100 | 0.15% | -0.43% | -2.94x (-0.58 pp) | 5 | 6 | PASS | PASS | -35.01% | [-4.4%, 6.0%] | `Directional (n<30)` |
| China | Shanghai Composite | 0.97% | -1.45% | -1.50x (-2.43 pp) | 5 | 6 | PASS | PASS | -42.46% | [-5.2%, 6.7%] | `Directional (n<30)` |
| Australia | ASX 200 | 1.53% | -2.13% | -1.40x (-3.66 pp) | 5 | 6 | PASS | PASS | -32.86% | [-4.9%, 5.5%] | `Directional (n<30)` |
| United Kingdom | FTSE 250 | 2.01% | -3.29% | -1.64x (-5.29 pp) | 5 | 6 | PASS | PASS | -42.52% | [-7.3%, 8.3%] | `Directional (n<30)` |
| Mexico | IPC Mexico | -2.83% | 0.60% | -0.21x (+3.43 pp) | 7 | 5 | PASS | PASS | -39.96% | [-5.3%, 4.5%] | `Directional (n<30)` |
| France | CAC 40 | -0.38% | -4.19% | 10.89x (-3.80 pp) | 5 | 6 | PASS | PASS | -46.95% | [-6.7%, 6.4%] | `Directional (n<30)` |
| Brazil | Ibovespa | -3.74% | -4.58% | 1.22x (-0.83 pp) | 8 | 6 | PASS | PASS | -62.45% | [-9.2%, 3.2%] | `Directional (n<30)` |

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