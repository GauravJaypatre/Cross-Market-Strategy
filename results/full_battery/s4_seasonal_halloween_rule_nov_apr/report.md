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
| 1 | South Korea | KOSDAQ | KRW | 7.60% | 7.60% | **7.23%** | [2.5%, 12.9%] | 6.48% | 3.94% | +3.28% | -39.65% | 0.18 | 0.53 | 16 | 2011-01-03 |
| 2 | Germany | TecDAX | EUR | 8.92% | 6.87% | **6.87%** | [2.1%, 15.2%] | 6.82% | 8.43% | -1.56% | -39.16% | 0.18 | 0.47 | 16 | 2011-01-03 |
| 3 | Germany | DAX 40 | EUR | 7.96% | 5.98% | **5.98%** | [0.6%, 15.1%] | 5.92% | 7.23% | -1.25% | -45.93% | 0.13 | 0.43 | 16 | 2011-01-03 |
| 4 | Germany | MDAX | EUR | 7.32% | 5.36% | **5.36%** | [0.6%, 14.4%] | 5.30% | 6.24% | -0.88% | -45.50% | 0.12 | 0.40 | 16 | 2011-01-03 |
| 5 | United States | Nasdaq Composite | USD | 6.50% | 4.85% | **4.84%** | [0.7%, 12.1%] | 4.56% | 14.43% | -9.59% | -34.94% | 0.14 | 0.35 | 16 | 2011-01-03 |
| 6 | United States | S&P 500 | USD | 6.24% | 4.78% | **4.77%** | [1.6%, 10.9%] | 4.49% | 10.97% | -6.19% | -38.05% | 0.13 | 0.38 | 16 | 2011-01-03 |
| 7 | Italy | FTSE MIB | EUR | 6.37% | 4.38% | **4.21%** | [-2.1%, 14.4%] | 3.75% | 4.30% | -0.09% | -48.52% | 0.09 | 0.31 | 16 | 2011-01-03 |
| 8 | South Korea | KOSPI | KRW | 4.62% | 4.62% | **4.18%** | [-0.1%, 10.1%] | 3.31% | 4.86% | -0.67% | -37.48% | 0.11 | 0.39 | 16 | 2011-01-03 |
| 9 | United States | Dow Jones Industrial Average | USD | 5.54% | 4.09% | **4.08%** | [0.4%, 10.6%] | 3.77% | 9.06% | -4.99% | -41.72% | 0.10 | 0.34 | 16 | 2011-01-03 |
| 10 | China | Shanghai Composite | CNY | 3.78% | 3.78% | **3.56%** | [-3.5%, 14.0%] | 3.53% | 2.22% | +1.34% | -32.49% | 0.11 | 0.33 | 16 | 2011-01-04 |
| 11 | Canada | S&P/TSX Composite | CAD | 4.21% | 3.49% | **3.49%** | [0.3%, 7.9%] | 2.77% | 5.25% | -1.76% | -39.25% | 0.09 | 0.34 | 16 | 2011-01-04 |
| 12 | United Kingdom | FTSE 250 | GBP | 4.80% | 4.29% | **3.28%** | [-1.3%, 11.1%] | 2.03% | 3.60% | -0.32% | -46.40% | 0.07 | 0.31 | 16 | 2011-01-04 |
| 13 | India | Nifty Bank | INR | 3.75% | 3.39% | **3.18%** | [-4.8%, 10.7%] | 2.41% | 10.79% | -7.62% | -51.10% | 0.06 | 0.27 | 16 | 2011-01-03 |
| 14 | France | CAC 40 | EUR | 6.09% | 3.52% | **2.96%** | [-0.6%, 12.8%] | 1.72% | 3.83% | -0.86% | -52.06% | 0.06 | 0.25 | 16 | 2011-01-03 |
| 15 | Japan | Nikkei 225 | JPY | 4.54% | 3.07% | **2.95%** | [-2.5%, 13.2%] | -3.29% | 9.81% | -6.86% | -42.63% | 0.07 | 0.26 | 16 | 2011-01-04 |
| 16 | United Kingdom | FTSE 100 | GBP | 3.85% | 3.68% | **2.77%** | [-1.3%, 8.2%] | 1.66% | 2.71% | +0.06% | -38.02% | 0.07 | 0.28 | 16 | 2011-01-04 |
| 17 | Indonesia | Jakarta Composite Index | IDR | 3.25% | 3.25% | **2.58%** | [-3.3%, 8.6%] | 2.43% | 5.76% | -3.19% | -41.11% | 0.06 | 0.28 | 16 | 2011-01-03 |
| 18 | Brazil | Ibovespa | BRL | 2.54% | 2.50% | **2.44%** | [-4.5%, 8.3%] | 1.49% | 5.19% | -2.75% | -47.03% | 0.05 | 0.23 | 16 | 2011-01-03 |
| 19 | Mexico | IPC Mexico | MXN | 3.26% | 2.92% | **2.43%** | [-1.8%, 8.6%] | 1.91% | 3.17% | -0.74% | -34.74% | 0.07 | 0.26 | 16 | 2011-01-03 |
| 20 | Australia | ASX 200 | AUD | 3.88% | 2.22% | **2.21%** | [-1.5%, 8.3%] | 1.30% | 3.66% | -1.45% | -41.62% | 0.05 | 0.23 | 16 | 2011-01-04 |
| 21 | Spain | IBEX 35 | EUR | 3.67% | 2.22% | **2.08%** | [-5.5%, 12.1%] | 1.43% | 3.16% | -1.08% | -45.26% | 0.05 | 0.21 | 16 | 2011-01-03 |
| 22 | Australia | All Ordinaries | AUD | 3.69% | 2.06% | **2.05%** | [-1.7%, 8.4%] | 1.14% | 3.73% | -1.68% | -42.05% | 0.05 | 0.22 | 16 | 2011-01-04 |
| 23 | India | Nifty 50 | INR | 2.35% | 2.20% | **1.98%** | [-3.0%, 7.9%] | 1.23% | 9.63% | -7.65% | -40.13% | 0.05 | 0.22 | 16 | 2011-01-03 |
| 24 | India | BSE Sensex | INR | 2.10% | 1.96% | **1.74%** | [-3.6%, 7.4%] | 0.98% | 9.48% | -7.74% | -39.68% | 0.04 | 0.20 | 16 | 2011-01-03 |
| 25 | China | Shenzhen Component | CNY | 1.69% | 1.69% | **1.44%** | [-6.5%, 13.4%] | 1.40% | 0.45% | +0.99% | -44.76% | 0.03 | 0.17 | 16 | 2011-01-04 |

## 2. Secondary Ranking: Calmar Ratio (Risk-Adjusted Efficiency)

Re-sorted by Calmar Ratio (CAGR / |Max Drawdown|) computed on the Net-of-Tax-and-Discount-Brokerage series.


| Calmar Rank | Country | Index | Calmar Ratio | Net-Disc CAGR | Max Drawdown | Sharpe | Total Trades |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|
| 1 | South Korea | KOSDAQ | **0.18** | 7.23% | -39.65% | 0.53 | 16 |
| 2 | Germany | TecDAX | **0.18** | 6.87% | -39.16% | 0.47 | 16 |
| 3 | United States | Nasdaq Composite | **0.14** | 4.84% | -34.94% | 0.35 | 16 |
| 4 | Germany | DAX 40 | **0.13** | 5.98% | -45.93% | 0.43 | 16 |
| 5 | United States | S&P 500 | **0.13** | 4.77% | -38.05% | 0.38 | 16 |
| 6 | Germany | MDAX | **0.12** | 5.36% | -45.50% | 0.40 | 16 |
| 7 | South Korea | KOSPI | **0.11** | 4.18% | -37.48% | 0.39 | 16 |
| 8 | China | Shanghai Composite | **0.11** | 3.56% | -32.49% | 0.33 | 16 |
| 9 | United States | Dow Jones Industrial Average | **0.10** | 4.08% | -41.72% | 0.34 | 16 |
| 10 | Canada | S&P/TSX Composite | **0.09** | 3.49% | -39.25% | 0.34 | 16 |
| 11 | Italy | FTSE MIB | **0.09** | 4.21% | -48.52% | 0.31 | 16 |
| 12 | United Kingdom | FTSE 100 | **0.07** | 2.77% | -38.02% | 0.28 | 16 |
| 13 | United Kingdom | FTSE 250 | **0.07** | 3.28% | -46.40% | 0.31 | 16 |
| 14 | Mexico | IPC Mexico | **0.07** | 2.43% | -34.74% | 0.26 | 16 |
| 15 | Japan | Nikkei 225 | **0.07** | 2.95% | -42.63% | 0.26 | 16 |
| 16 | Indonesia | Jakarta Composite Index | **0.06** | 2.58% | -41.11% | 0.28 | 16 |
| 17 | India | Nifty Bank | **0.06** | 3.18% | -51.10% | 0.27 | 16 |
| 18 | France | CAC 40 | **0.06** | 2.96% | -52.06% | 0.25 | 16 |
| 19 | Australia | ASX 200 | **0.05** | 2.21% | -41.62% | 0.23 | 16 |
| 20 | Brazil | Ibovespa | **0.05** | 2.44% | -47.03% | 0.23 | 16 |
| 21 | India | Nifty 50 | **0.05** | 1.98% | -40.13% | 0.22 | 16 |
| 22 | Australia | All Ordinaries | **0.05** | 2.05% | -42.05% | 0.22 | 16 |
| 23 | Spain | IBEX 35 | **0.05** | 2.08% | -45.26% | 0.21 | 16 |
| 24 | India | BSE Sensex | **0.04** | 1.74% | -39.68% | 0.20 | 16 |
| 25 | China | Shenzhen Component | **0.03** | 1.44% | -44.76% | 0.17 | 16 |

## 3. Skeptical Robustness & Overfitting Evaluation

In-Sample (2011–2018) vs Out-of-Sample (2019–2025) performance degradation, 1,000 Monte Carlo trade sequence permutations, and 95% bootstrap CAGR confidence intervals.


| Country | Index | IS CAGR (2011-18) | OOS CAGR (2019-25) | Degradation (OOS/IS) | IS Trades | OOS Trades | IS Guard | OOS Guard | MC Worst DD (P95) | 95% Bootstrap CI | Precision Flag |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| South Korea | KOSDAQ | 7.17% | 7.46% | 1.04x (+0.29 pp) | 9 | 7 | PASS | PASS | -12.36% | [2.5%, 12.9%] | `Directional (n<30)` |
| Germany | TecDAX | 7.44% | 6.13% | 0.82x (-1.31 pp) | 9 | 7 | PASS | PASS | -29.15% | [2.1%, 15.2%] | `Directional (n<30)` |
| Germany | DAX 40 | 4.33% | 7.86% | 1.82x (+3.53 pp) | 9 | 7 | PASS | PASS | -31.62% | [0.6%, 15.1%] | `Directional (n<30)` |
| Germany | MDAX | 5.73% | 4.87% | 0.85x (-0.86 pp) | 9 | 7 | PASS | PASS | -29.64% | [0.6%, 14.4%] | `Directional (n<30)` |
| United States | Nasdaq Composite | 4.07% | 5.64% | 1.38x (+1.57 pp) | 9 | 7 | PASS | PASS | -25.08% | [0.7%, 12.1%] | `Directional (n<30)` |
| United States | S&P 500 | 4.40% | 5.18% | 1.18x (+0.78 pp) | 9 | 7 | PASS | PASS | -17.56% | [1.6%, 10.9%] | `Directional (n<30)` |
| Italy | FTSE MIB | 2.96% | 5.65% | 1.91x (+2.69 pp) | 9 | 7 | PASS | PASS | -42.05% | [-2.1%, 14.4%] | `Directional (n<30)` |
| South Korea | KOSPI | 2.74% | 6.11% | 2.23x (+3.36 pp) | 9 | 7 | PASS | PASS | -21.20% | [-0.1%, 10.1%] | `Directional (n<30)` |
| United States | Dow Jones Industrial Average | 4.92% | 3.11% | 0.63x (-1.82 pp) | 9 | 7 | PASS | PASS | -20.77% | [0.4%, 10.6%] | `Directional (n<30)` |
| China | Shanghai Composite | 4.21% | 3.00% | 0.71x (-1.22 pp) | 9 | 7 | PASS | PASS | -31.33% | [-3.5%, 14.0%] | `Directional (n<30)` |
| Canada | S&P/TSX Composite | 1.57% | 5.70% | 3.62x (+4.12 pp) | 9 | 7 | PASS | PASS | -15.84% | [0.3%, 7.9%] | `Directional (n<30)` |
| United Kingdom | FTSE 250 | 4.32% | 2.03% | 0.47x (-2.28 pp) | 9 | 7 | PASS | PASS | -30.37% | [-1.3%, 11.1%] | `Directional (n<30)` |
| India | Nifty Bank | 4.70% | 1.33% | 0.28x (-3.37 pp) | 9 | 7 | PASS | PASS | -42.63% | [-4.8%, 10.7%] | `Directional (n<30)` |
| France | CAC 40 | 1.42% | 4.93% | 3.46x (+3.51 pp) | 9 | 7 | PASS | PASS | -31.76% | [-0.6%, 12.8%] | `Directional (n<30)` |
| Japan | Nikkei 225 | 3.99% | 2.18% | 0.55x (-1.81 pp) | 9 | 7 | PASS | PASS | -35.69% | [-2.5%, 13.2%] | `Directional (n<30)` |
| United Kingdom | FTSE 100 | 1.80% | 3.86% | 2.14x (+2.06 pp) | 9 | 7 | PASS | PASS | -23.27% | [-1.3%, 8.2%] | `Directional (n<30)` |
| Indonesia | Jakarta Composite Index | 6.93% | -2.14% | -0.31x (-9.06 pp) | 9 | 7 | PASS | PASS | -33.16% | [-3.3%, 8.6%] | `Directional (n<30)` |
| Brazil | Ibovespa | 3.73% | 0.48% | 0.13x (-3.25 pp) | 9 | 7 | PASS | PASS | -39.76% | [-4.5%, 8.3%] | `Directional (n<30)` |
| Mexico | IPC Mexico | -0.58% | 5.74% | -9.88x (+6.33 pp) | 9 | 7 | PASS | PASS | -22.91% | [-1.8%, 8.6%] | `Directional (n<30)` |
| Australia | ASX 200 | 3.38% | 1.15% | 0.34x (-2.23 pp) | 9 | 7 | PASS | PASS | -22.91% | [-1.5%, 8.3%] | `Directional (n<30)` |
| Spain | IBEX 35 | -1.15% | 5.88% | -5.09x (+7.03 pp) | 9 | 7 | PASS | PASS | -50.41% | [-5.5%, 12.1%] | `Directional (n<30)` |
| Australia | All Ordinaries | 3.08% | 1.13% | 0.37x (-1.95 pp) | 9 | 7 | PASS | PASS | -22.95% | [-1.7%, 8.4%] | `Directional (n<30)` |
| India | Nifty 50 | 1.31% | 2.86% | 2.19x (+1.55 pp) | 9 | 7 | PASS | PASS | -30.68% | [-3.0%, 7.9%] | `Directional (n<30)` |
| India | BSE Sensex | 1.11% | 2.54% | 2.28x (+1.42 pp) | 9 | 7 | PASS | PASS | -30.42% | [-3.6%, 7.4%] | `Directional (n<30)` |
| China | Shenzhen Component | 1.37% | 1.70% | 1.25x (+0.34 pp) | 9 | 7 | PASS | PASS | -47.30% | [-6.5%, 13.4%] | `Directional (n<30)` |

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