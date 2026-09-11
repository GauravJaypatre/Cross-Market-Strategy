# Cross-Market Strategy Battery: Statutory Friction & Robustness Framework
**Manuscript Working Draft**

---

# Methods

## 2.1 Universe

We evaluate six canonical trading-strategy families against a 15-country, 25-index universe spanning the world's largest economies by GDP (IMF, October 2024 ranking), substituting Indonesia for Russia due to data-access constraints. Up to three liquid equity indices are included per country where available. All backtests cover 2011-01-01 to 2025-12-31, a window chosen to (a) align with the emergence of zero/low-commission discount brokerage platforms globally (e.g., Zerodha 2010, Robinhood 2013), which makes point-in-time brokerage-fee reconstruction tractable, and (b) ensure complete, non-restated index price history across all 25 constituent indices. This window excludes the 2008 Global Financial Crisis and the peak of the 2000 dot-com bubble; we treat this as a stated scoping limitation rather than an oversight (Section 5, Limitations).

## 2.2 Strategy Families

Six algorithmic strategy families were implemented via a validated natural-language-to-code parser (dual rule-based and LLM backend, cryptographically hash-verified for tamper-free code generation; see Section 2.5):

1. Trend-Following (50/200-day SMA Crossover)
2. Mean Reversion (14-day RSI Oscillator)
3. Absolute Momentum (12-month trailing, monthly rebalance)
4. Calendar Effect (Seasonal "Halloween" rule, long Nov–Apr)
5. Volatility Breakout (Bollinger Bands)
6. Drawdown Dip-Buying (52-week high drawdown trigger)

All strategies are long-only, cash-equity, single-index (no shorting, leverage, or derivatives), with signals computed at day *t* close and executed at day *t*+1 open to eliminate lookahead bias.

## 2.3 Friction Model

Each (strategy, index) pair is evaluated across four parallel return tracks plus a benchmark, all passed through an identical point-in-time statutory pipeline:

- **Track 1 (Gross):** Frictionless returns.
- **Track 2 (Net-of-Tax):** Adjusted for the resident investor's domestic capital-gains/securities-transaction tax, applied at the statutory rate in effect on each trade's closing date.
- **Track 3 (Net-Discount):** Track 2 plus discount/neo-broker commissions, exchange fees, and applicable transaction taxes (FTT/STT/stamp duty).
- **Track 4 (Net-Full-Service):** Track 2 plus full-service broker commissions.
- **Benchmark (Buy-and-Hold):** The same four-track pipeline applied to a passive buy-and-hold position, isolating the marginal cost of active trading from baseline market exposure.

Tax treatment is scoped to resident investors only (one statutory rate per country per period), avoiding the combinatorial bilateral-treaty matrix that non-resident treatment would require. Tax and brokerage schedules are point-in-time: statutory rates and fee structures are dated to their actual effective periods rather than applied as a single flat rate across the full window, with each transition sourced to a primary statutory or regulatory authority (e.g., national tax codes, Big-4 worldwide tax summaries, broker historical fee schedules via web archive snapshots).

## 2.4 Verification Pipeline

The tax and brokerage datasets underwent a two-stage verification process:

1. **Primary sourcing pass:** Each rate/fee row was extracted and dated against a primary source (government statute, regulatory filing, or archived broker fee schedule), with URL and exact source text recorded.
2. **Independent second-source audit:** A stratified sample of highest-risk rows — countries with only one or two rows across the full 14-year window (a signature of an under-specified, flattened multi-era rate) and brokerages known to have rebranded or changed pricing tiers — was independently re-verified by a separate model with no access to the original sourcing rationale.

This audit identified and corrected two errors prior to final analysis: (1) Japan's listed-equity capital gains tax was incorrectly modeled as a flat 20.315% for the full window; the correct rate was 10.147% from 2011–2013 (pre-reconstruction-surtax-expiry structure) before rising to 20.315% in 2014. (2) Germany's discount-brokerage track incorrectly back-applied Trade Republic's 2019-era €1.00 flat fee to 2011–2018; a representative pre-2019 discount broker fee (€5.90 flat, flatex) was substituted for that period. Both corrections were propagated through the full pipeline and all downstream results (46 of 750 summary rows affected); neither correction changed the identity of any leaderboard-winning strategy-index pair (Section 3.1).

## 2.5 Reproducibility and Determinism

All simulations use a fixed random seed (seed=42) for Monte Carlo and bootstrap procedures. Bit-level determinism was confirmed by independently re-executing sampled (strategy, index) pairs and diffing all outputs (CAGR, drawdown, trade logs, bootstrap bounds) against the original run, with zero differences observed. The natural-language strategy parser's generated code was verified via SHA-256 hash comparison across independent runs to rule out post-hoc tuning, and evaluated against a sealed blind set of paraphrased strategy descriptions to test generalization beyond the canonical phrasing.

## 2.6 Statistical Robustness

For each qualified pair (≥5 realized round-trip trades), we compute: (a) an in-sample (2011–2018) / out-of-sample (2019–2025) CAGR degradation ratio; (b) 1,000-permutation Monte Carlo trade-shuffling to establish the 95th-percentile maximum drawdown, isolating sequence risk from strategy edge; and (c) 1,000-iteration bootstrap resampling to establish a 95% confidence interval on annualized CAGR.

**Minimum-sample reporting threshold.** Trade-count guards (n≥3 in-sample, n≥2 out-of-sample) were applied throughout, but we found this threshold insufficient to support headline performance claims: several leaderboard-topping results rested on as few as four realized trades in each sub-period, producing bootstrap CAGR confidence intervals exceeding 15 percentage points in width — wider than the point estimate itself. We therefore impose a stricter reporting threshold of n≥10 trades in *both* the in-sample and out-of-sample periods for any result presented as a headline finding. Results below this threshold are retained in the full supplementary dataset but are not used to support comparative claims.

---

# Results

## 3.1 Full-Universe Overview

The complete battery (6 strategies × 25 indices × 5 tracks = 750 rows) qualified all 150 (strategy, index) pairs under the base trade-count guard (0 exclusions for late data start or n<5 trades). Zero friction-ordering anomalies were detected across all 150 pairs (Gross ≥ Net-Tax ≥ Net-Discount ≥ Net-Full-Service held universally), and zero near-zero fee-drag anomalies were flagged, supporting the internal consistency of the friction model.

At face value, the unrestricted leaderboard shows the 50/200 SMA Crossover on the Nasdaq Composite as the top performer (Net-Discount CAGR 10.70%, Calmar 0.33), followed by 12-Month Momentum on the same index (8.66%). However, both of these headline results rest on only 4–5 realized trades per sub-period, with bootstrap 95% confidence intervals spanning 4.2%–19.5% and 0.2%–20.7% respectively — intervals wide enough that the point estimates alone are not statistically meaningful (Section 2.6).

## 3.2 Trade-Frequency-Filtered Results (n≥10)

Applying the n≥10 in-sample/out-of-sample threshold retains exactly 50 of 150 pairs (33.3%), and the retained set is not randomly distributed across strategies — it is fully determined by trade frequency: the two mean-reversion/breakout strategies (14-day RSI, Bollinger Bands) qualify on all 25 indices each, while all four trend, momentum, calendar, and dip-buying strategies — which by construction generate only a handful of signals over a 14-year window on daily/monthly data — qualify on zero indices.

Within this statistically defensible n≥10 subset:

- **46 of 50 pairs (92.0%)** show Net-Discount CAGR below the corresponding Buy-and-Hold benchmark, i.e., active trading underperforms passive exposure to the same index once realistic tax and brokerage frictions are applied.
- Only four pairs beat their passive benchmark net of discount-brokerage friction: 14-day RSI on the UK FTSE 100 (+3.08 pp) and Italy's FTSE MIB (+0.33 pp); Bollinger Bands Breakout on China's Shenzhen Component (+5.79 pp) and Shanghai Composite (+1.45 pp).

## 3.3 Interpretation

Two independent findings emerge. First, active trading strategies broadly fail to compensate for transaction costs and taxes relative to a passive buy-and-hold position on the same instrument, consistent with prior efficient-markets literature — but here demonstrated across a substantially wider cross-country, tax-and-brokerage-adjusted setting than is typical in the backtesting literature. Second, and methodologically, naive leaderboard-style reporting of "best strategy per market" is systematically biased toward low-frequency strategies precisely because their small trade counts inflate the *variance*, not the *edge*, of the reported point estimate; a trade-count-aware reporting threshold reverses which strategy families appear to lead. We present this second finding as a direct, generalizable caveat for any comparative backtesting framework, independent of the specific strategies or markets studied here.
