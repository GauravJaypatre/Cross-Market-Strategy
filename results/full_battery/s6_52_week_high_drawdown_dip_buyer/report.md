# Cross-Market Strategy Backtest & Friction Impact Report

**Strategy Parsing Method:** `Deterministic Rule-Based Parser`

**Random Seed:** `42` (Deterministic Monte Carlo & Bootstrap Resampling)

**Tax & Brokerage Dataset Status:** `Reference / Preliminary Baseline (primary_statutory_single_source)`

> **Strategy Description**: *"Buy the index whenever it falls 10% or more below its trailing 52-week high. Sell when it recovers to within 2% of that same 52-week high. No leverage, no shorting."*

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
| 1 | India | Nifty Bank | INR | 9.64% | 9.44% | **9.31%** | [7.6%, 12.3%] | 8.86% | 10.79% | -1.48% | -45.92% | 0.20 | 0.56 | 13 | 2011-01-03 |
| 2 | Germany | TecDAX | EUR | 9.49% | 7.82% | **7.82%** | [6.2%, 12.2%] | 7.78% | 8.43% | -0.61% | -35.20% | 0.22 | 0.53 | 16 | 2011-01-03 |
| 3 | Japan | Nikkei 225 | JPY | 8.16% | 7.08% | **7.02%** | [6.4%, 10.1%] | 4.94% | 9.81% | -2.79% | -27.86% | 0.25 | 0.46 | 12 | 2011-01-04 |
| 4 | India | Nifty 50 | INR | 7.22% | 7.07% | **6.95%** | [6.1%, 8.3%] | 6.53% | 9.63% | -2.68% | -30.58% | 0.23 | 0.62 | 11 | 2011-01-03 |
| 5 | India | BSE Sensex | INR | 7.02% | 6.88% | **6.76%** | [5.9%, 8.2%] | 6.34% | 9.48% | -2.71% | -31.05% | 0.22 | 0.62 | 11 | 2011-01-03 |
| 6 | United States | Nasdaq Composite | USD | 7.44% | 6.05% | **6.05%** | [4.2%, 9.8%] | 5.86% | 14.43% | -8.39% | -35.40% | 0.17 | 0.43 | 13 | 2011-01-03 |
| 7 | Brazil | Ibovespa | BRL | 5.86% | 5.86% | **5.82%** | [3.5%, 8.2%] | 5.27% | 5.19% | +0.63% | -44.13% | 0.13 | 0.39 | 12 | 2011-01-03 |
| 8 | France | CAC 40 | EUR | 7.69% | 5.82% | **5.50%** | [6.2%, 9.3%] | 4.85% | 3.83% | +1.67% | -39.61% | 0.14 | 0.39 | 11 | 2011-01-03 |
| 9 | Mexico | IPC Mexico | MXN | 5.30% | 4.90% | **4.61%** | [3.5%, 7.1%] | 4.30% | 3.17% | +1.43% | -21.40% | 0.22 | 0.44 | 10 | 2011-01-03 |
| 10 | Australia | All Ordinaries | AUD | 5.97% | 4.52% | **4.52%** | [5.0%, 6.8%] | 4.08% | 3.73% | +0.78% | -34.70% | 0.13 | 0.44 | 10 | 2011-01-04 |
| 11 | Indonesia | Jakarta Composite Index | IDR | 4.62% | 4.62% | **4.34%** | [3.2%, 5.7%] | 4.27% | 5.76% | -1.43% | -35.39% | 0.12 | 0.41 | 9 | 2011-01-03 |
| 12 | Germany | DAX 40 | EUR | 5.38% | 4.32% | **4.32%** | [2.7%, 8.2%] | 4.28% | 7.23% | -2.91% | -35.79% | 0.12 | 0.35 | 8 | 2011-01-03 |
| 13 | Italy | FTSE MIB | EUR | 5.49% | 4.40% | **4.28%** | [2.8%, 7.7%] | 3.97% | 4.30% | -0.02% | -45.27% | 0.09 | 0.31 | 11 | 2011-01-03 |
| 14 | Germany | MDAX | EUR | 5.57% | 4.18% | **4.18%** | [1.2%, 8.8%] | 4.13% | 6.24% | -2.06% | -41.45% | 0.10 | 0.33 | 10 | 2011-01-03 |
| 15 | United Kingdom | FTSE 100 | GBP | 4.84% | 4.60% | **4.12%** | [3.3%, 6.1%] | 3.57% | 2.71% | +1.41% | -29.14% | 0.14 | 0.42 | 9 | 2011-01-04 |
| 16 | United States | Dow Jones Industrial Average | USD | 4.84% | 3.95% | **3.95%** | [3.6%, 6.2%] | 3.81% | 9.06% | -5.11% | -33.17% | 0.12 | 0.37 | 7 | 2011-01-03 |
| 17 | Australia | ASX 200 | AUD | 5.04% | 3.76% | **3.76%** | [4.2%, 5.8%] | 3.35% | 3.66% | +0.10% | -34.15% | 0.11 | 0.38 | 9 | 2011-01-04 |
| 18 | United States | S&P 500 | USD | 4.32% | 3.45% | **3.44%** | [2.7%, 5.6%] | 3.28% | 10.97% | -7.52% | -30.63% | 0.11 | 0.32 | 8 | 2011-01-03 |
| 19 | Canada | S&P/TSX Composite | CAD | 3.65% | 3.16% | **3.16%** | [2.0%, 5.4%] | 2.84% | 5.25% | -2.09% | -27.04% | 0.12 | 0.33 | 7 | 2011-01-04 |
| 20 | United Kingdom | FTSE 250 | GBP | 3.50% | 3.34% | **2.84%** | [1.0%, 5.3%] | 2.28% | 3.60% | -0.76% | -37.70% | 0.08 | 0.28 | 8 | 2011-01-04 |
| 21 | South Korea | KOSPI | KRW | 2.73% | 2.73% | **2.48%** | [-0.7%, 5.7%] | 2.02% | 4.86% | -2.37% | -33.18% | 0.07 | 0.26 | 8 | 2011-01-03 |
| 22 | Spain | IBEX 35 | EUR | 2.97% | 2.07% | **1.97%** | [-0.9%, 6.3%] | 1.46% | 3.16% | -1.19% | -50.22% | 0.04 | 0.20 | 11 | 2011-01-03 |
| 23 | South Korea | KOSDAQ | KRW | 1.96% | 1.96% | **1.60%** | [-1.9%, 5.2%] | 0.93% | 3.94% | -2.34% | -53.81% | 0.03 | 0.18 | 10 | 2011-01-03 |
| 24 | China | Shanghai Composite | CNY | 1.26% | 1.26% | **1.17%** | [-4.8%, 6.0%] | 1.15% | 2.22% | -1.05% | -46.44% | 0.03 | 0.16 | 8 | 2011-01-04 |
| 25 | China | Shenzhen Component | CNY | -0.78% | -0.78% | **-0.88%** | [-7.0%, 4.9%] | -0.90% | 0.45% | -1.33% | -62.50% | -0.01 | 0.07 | 8 | 2011-01-04 |

## 2. Secondary Ranking: Calmar Ratio (Risk-Adjusted Efficiency)

Re-sorted by Calmar Ratio (CAGR / |Max Drawdown|) computed on the Net-of-Tax-and-Discount-Brokerage series.


| Calmar Rank | Country | Index | Calmar Ratio | Net-Disc CAGR | Max Drawdown | Sharpe | Total Trades |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|
| 1 | Japan | Nikkei 225 | **0.25** | 7.02% | -27.86% | 0.46 | 12 |
| 2 | India | Nifty 50 | **0.23** | 6.95% | -30.58% | 0.62 | 11 |
| 3 | Germany | TecDAX | **0.22** | 7.82% | -35.20% | 0.53 | 16 |
| 4 | India | BSE Sensex | **0.22** | 6.76% | -31.05% | 0.62 | 11 |
| 5 | Mexico | IPC Mexico | **0.22** | 4.61% | -21.40% | 0.44 | 10 |
| 6 | India | Nifty Bank | **0.20** | 9.31% | -45.92% | 0.56 | 13 |
| 7 | United States | Nasdaq Composite | **0.17** | 6.05% | -35.40% | 0.43 | 13 |
| 8 | United Kingdom | FTSE 100 | **0.14** | 4.12% | -29.14% | 0.42 | 9 |
| 9 | France | CAC 40 | **0.14** | 5.50% | -39.61% | 0.39 | 11 |
| 10 | Brazil | Ibovespa | **0.13** | 5.82% | -44.13% | 0.39 | 12 |
| 11 | Australia | All Ordinaries | **0.13** | 4.52% | -34.70% | 0.44 | 10 |
| 12 | Indonesia | Jakarta Composite Index | **0.12** | 4.34% | -35.39% | 0.41 | 9 |
| 13 | Germany | DAX 40 | **0.12** | 4.32% | -35.79% | 0.35 | 8 |
| 14 | United States | Dow Jones Industrial Average | **0.12** | 3.95% | -33.17% | 0.37 | 7 |
| 15 | Canada | S&P/TSX Composite | **0.12** | 3.16% | -27.04% | 0.33 | 7 |
| 16 | United States | S&P 500 | **0.11** | 3.44% | -30.63% | 0.32 | 8 |
| 17 | Australia | ASX 200 | **0.11** | 3.76% | -34.15% | 0.38 | 9 |
| 18 | Germany | MDAX | **0.10** | 4.18% | -41.45% | 0.33 | 10 |
| 19 | Italy | FTSE MIB | **0.09** | 4.28% | -45.27% | 0.31 | 11 |
| 20 | United Kingdom | FTSE 250 | **0.08** | 2.84% | -37.70% | 0.28 | 8 |
| 21 | South Korea | KOSPI | **0.07** | 2.48% | -33.18% | 0.26 | 8 |
| 22 | Spain | IBEX 35 | **0.04** | 1.97% | -50.22% | 0.20 | 11 |
| 23 | South Korea | KOSDAQ | **0.03** | 1.60% | -53.81% | 0.18 | 10 |
| 24 | China | Shanghai Composite | **0.03** | 1.17% | -46.44% | 0.16 | 8 |
| 25 | China | Shenzhen Component | **-0.01** | -0.88% | -62.50% | 0.07 | 8 |

## 3. Skeptical Robustness & Overfitting Evaluation

In-Sample (2011–2018) vs Out-of-Sample (2019–2025) performance degradation, 1,000 Monte Carlo trade sequence permutations, and 95% bootstrap CAGR confidence intervals.


| Country | Index | IS CAGR (2011-18) | OOS CAGR (2019-25) | Degradation (OOS/IS) | IS Trades | OOS Trades | IS Guard | OOS Guard | MC Worst DD (P95) | 95% Bootstrap CI | Precision Flag |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| India | Nifty Bank | 9.10% | 9.42% | 1.03x (+0.32 pp) | 7 | 6 | PASS | PASS | 0.00% | [7.6%, 12.3%] | `Directional (n<30)` |
| Germany | TecDAX | 6.57% | 9.19% | 1.40x (+2.62 pp) | 8 | 8 | PASS | PASS | -7.75% | [6.2%, 12.2%] | `Directional (n<30)` |
| Japan | Nikkei 225 | 7.42% | 6.98% | 0.94x (-0.44 pp) | 8 | 4 | PASS | PASS | 0.00% | [6.4%, 10.1%] | `Directional (n<30)` |
| India | Nifty 50 | 6.10% | 8.04% | 1.32x (+1.94 pp) | 6 | 5 | PASS | PASS | 0.00% | [6.1%, 8.3%] | `Directional (n<30)` |
| India | BSE Sensex | 5.77% | 8.00% | 1.39x (+2.23 pp) | 6 | 5 | PASS | PASS | 0.00% | [5.9%, 8.2%] | `Directional (n<30)` |
| United States | Nasdaq Composite | 2.36% | 10.36% | 4.39x (+8.00 pp) | 5 | 8 | PASS | PASS | -9.36% | [4.2%, 9.8%] | `Directional (n<30)` |
| Brazil | Ibovespa | 3.31% | 8.78% | 2.65x (+5.47 pp) | 5 | 7 | PASS | PASS | -5.98% | [3.5%, 8.2%] | `Directional (n<30)` |
| France | CAC 40 | 2.73% | 8.94% | 3.28x (+6.21 pp) | 6 | 5 | PASS | PASS | 0.00% | [6.2%, 9.3%] | `Directional (n<30)` |
| Mexico | IPC Mexico | 2.85% | 6.42% | 2.25x (+3.57 pp) | 6 | 4 | PASS | PASS | -1.25% | [3.5%, 7.1%] | `Directional (n<30)` |
| Australia | All Ordinaries | 1.65% | 8.14% | 4.94x (+6.49 pp) | 4 | 6 | PASS | PASS | 0.00% | [5.0%, 6.8%] | `Directional (n<30)` |
| Indonesia | Jakarta Composite Index | 2.60% | 6.40% | 2.46x (+3.80 pp) | 4 | 5 | PASS | PASS | -0.37% | [3.2%, 5.7%] | `Directional (n<30)` |
| Germany | DAX 40 | 0.12% | 9.30% | 77.74x (+9.18 pp) | 4 | 4 | PASS | PASS | -3.08% | [2.7%, 8.2%] | `Directional (n<30)` |
| Italy | FTSE MIB | 1.90% | 7.06% | 3.72x (+5.16 pp) | 7 | 4 | PASS | PASS | -5.64% | [2.8%, 7.7%] | `Directional (n<30)` |
| Germany | MDAX | 4.62% | 3.59% | 0.78x (-1.03 pp) | 6 | 4 | PASS | PASS | -16.34% | [1.2%, 8.8%] | `Directional (n<30)` |
| United Kingdom | FTSE 100 | 3.99% | 4.26% | 1.07x (+0.27 pp) | 6 | 3 | PASS | PASS | -0.87% | [3.3%, 6.1%] | `Directional (n<30)` |
| United States | Dow Jones Industrial Average | 1.32% | 7.03% | 5.32x (+5.71 pp) | 3 | 4 | PASS | PASS | 0.00% | [3.6%, 6.2%] | `Directional (n<30)` |
| Australia | ASX 200 | 1.56% | 6.58% | 4.22x (+5.02 pp) | 4 | 5 | PASS | PASS | 0.00% | [4.2%, 5.8%] | `Directional (n<30)` |
| United States | S&P 500 | 1.95% | 5.16% | 2.65x (+3.22 pp) | 4 | 4 | PASS | PASS | -1.94% | [2.7%, 5.6%] | `Directional (n<30)` |
| Canada | S&P/TSX Composite | 1.05% | 5.59% | 5.31x (+4.54 pp) | 4 | 3 | PASS | PASS | 0.00% | [2.0%, 5.4%] | `Directional (n<30)` |
| United Kingdom | FTSE 250 | 3.26% | 2.29% | 0.70x (-0.98 pp) | 5 | 3 | PASS | PASS | -9.23% | [1.0%, 5.3%] | `Directional (n<30)` |
| South Korea | KOSPI | 1.19% | 4.22% | 3.54x (+3.03 pp) | 4 | 4 | PASS | PASS | -15.72% | [-0.7%, 5.7%] | `Directional (n<30)` |
| Spain | IBEX 35 | 0.15% | 4.07% | 26.28x (+3.91 pp) | 7 | 4 | PASS | PASS | -20.02% | [-0.9%, 6.3%] | `Directional (n<30)` |
| South Korea | KOSDAQ | -0.10% | 3.73% | -37.04x (+3.83 pp) | 5 | 5 | PASS | PASS | -20.78% | [-1.9%, 5.2%] | `Directional (n<30)` |
| China | Shanghai Composite | -5.78% | 9.91% | -1.71x (+15.69 pp) | 4 | 4 | PASS | PASS | -28.09% | [-4.8%, 6.0%] | `Directional (n<30)` |
| China | Shenzhen Component | -9.43% | 10.06% | -1.07x (+19.49 pp) | 3 | 5 | PASS | PASS | -43.87% | [-7.0%, 4.9%] | `Directional (n<30)` |

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