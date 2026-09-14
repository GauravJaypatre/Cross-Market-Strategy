# Abstract

Backtested trading-strategy performance is routinely reported without accounting for two frictions that materially determine an investor's realized return: statutory taxation and brokerage costs, both of which vary by jurisdiction and change over time. We introduce a reproducible, tax-and-brokerage-adjusted backtesting framework spanning 15 of the world's largest economies by GDP (25 constituent equity indices) and evaluate six canonical strategy families — trend-following, mean reversion, absolute momentum, a calendar effect, volatility breakout, and drawdown dip-buying — against resident-investor tax regimes and both discount and full-service brokerage fee schedules, each dated to its actual effective period from 2011–2025. Every reported result is accompanied by in-sample/out-of-sample degradation, Monte Carlo sequence-risk bounds, and bootstrap confidence intervals. We find that naive comparison across all 150 strategy-index pairs is misleading: headline-topping results systematically coincide with the lowest trade counts, producing confidence intervals wider than the point estimates themselves. Restricting comparison to statistically defensible pairs (≥10 trades in-sample and out-of-sample) retains only two of six strategy families — both mean-reversion or breakout strategies, which trade frequently enough to be estimated reliably — and shows that 92% of these pairs underperform a simple buy-and-hold position on the same index once realistic frictions are applied. Beyond the strategy-performance findings, we contribute a reusable, source-verified panel dataset of point-in-time capital-gains tax rates and brokerage fee schedules across 15 countries, built via a primary-sourcing-plus-independent-audit pipeline, intended for reuse in future cross-market backtesting research.

# 1. Introduction

Academic and practitioner backtests of trading strategies are frequently reported as gross, frictionless returns, or with frictions applied inconsistently — a flat brokerage assumption held constant across decades, or a single national tax rate applied without regard to legislative change. This creates two distinct problems. First, it overstates achievable returns, since real investors pay taxes and fees that shift with jurisdiction and time. Second, and less widely recognized, it obscures a statistical hazard specific to comparative multi-market backtesting: strategies that trade infrequently by construction (trend-following, calendar effects, long-horizon momentum) generate few realized trades over any fixed historical window, so their headline performance metrics carry wide uncertainty even when reported without acknowledgment of that uncertainty. A cross-market leaderboard built from point estimates alone will systematically favor these high-variance, low-trade-count results over strategies whose more modest but statistically reliable edge is masked by frequent, well-estimated trading.

This paper addresses both problems within a single framework. We restrict scope in two deliberate ways to keep the framework tractable without sacrificing realism: taxation is modeled for resident investors only (avoiding the combinatorial bilateral tax-treaty matrix that non-resident treatment requires across 15×14 country pairs), and the evaluation window is fixed to 2011–2025, a period for which both index price data and brokerage/tax documentation are reliably recoverable across all 15 countries in the universe. We treat both choices as explicit, stated scoping decisions rather than silent omissions (Section 6).

Our contributions are threefold. First, a point-in-time, source-verified dataset of resident capital-gains tax rates and discount/full-service brokerage fee schedules across 15 major economies, built through a primary-sourcing pipeline with independent second-source audit — itself a reusable artifact for future cross-market research, independent of any strategy results. Second, a reproducible (fixed-seed, hash-verified) backtesting framework that applies this dataset across six canonical strategy families and reports Monte Carlo and bootstrap-based robustness statistics alongside every point estimate. Third, an empirical demonstration that a naive, unfiltered comparison of strategy performance across markets is misleading in a specific, generalizable way — headline results concentrate in the lowest-trade-count strategies — and that a trade-count-aware reporting threshold both corrects this bias and yields a clear, defensible finding: the large majority of statistically reliable active strategies fail to beat passive exposure once realistic frictions are applied.

---

# 2. Related Work

**Technical trading rule profitability and transaction costs.** A substantial empirical literature examines whether technical trading rules outperform passive benchmarks once transaction costs are applied. Cross-market evidence is mixed but highly transaction-cost-sensitive: a large-sample study across developed and emerging equity indices found that trading-rule predictability, while present in roughly half of markets studied under zero costs, diminished sharply over time and largely disappeared once moderate transaction costs were introduced (Hanauer & Lauterbach, 2023). Earlier work applying rigorous statistical correction for data-snooping bias found that, once the full universe of tested rules is accounted for, technical trading rules generally fail to significantly outperform buy-and-hold on major indices such as the Dow Jones Industrial Average (Sullivan, Timmermann, & White, 1999). Our framework extends this line of inquiry by applying jurisdiction-specific, point-in-time statutory tax and brokerage costs -- rather than a single assumed cost rate -- across a substantially larger cross-country universe than is typical in this literature.

**Data snooping and the bootstrap.** The statistical machinery we use to establish confidence around each strategy-index result descends from White's Reality Check bootstrap methodology, developed to correct for the inflation in apparent trading-rule performance that arises from testing many rules and reporting only the best (White, 2000; Sullivan, Timmermann, & White, 1999). We apply the same underlying logic -- bootstrap resampling to characterize the uncertainty of a reported performance statistic -- at the level of individual strategy-index pairs rather than across a rule universe, using it to demonstrate that headline point estimates from low-trade-count strategies are statistically unreliable even without any rule-selection step.

**Backtest length, sample size, and overfitting.** Our trade-count reporting threshold is conceptually related to the minimum backtest length and minimum track record length literature, which formalizes how much historical data, or how many independent trials, are needed before a reported Sharpe ratio or similar performance statistic can be trusted (Bailey & Lopez de Prado, 2014; Bailey, Borwein, Lopez de Prado, & Zhu, 2014). That literature primarily addresses overfitting from searching across many strategy configurations; our finding is a related but distinct hazard specific to comparative, cross-market backtesting -- that strategies with structurally low trading frequency produce wide-uncertainty point estimates even without any parameter search, and that a naive leaderboard will systematically surface these unreliable results ahead of better-estimated ones. The broader point that standard significance thresholds are inadequate once many comparisons are being made is also central to the asset-pricing multiple-testing literature, which argues that a newly discovered factor needs to clear a much higher hurdle than conventional practice, given the extensive data mining involved in typical published findings (Harvey, Liu, & Zhu, 2016). Our n>=10 trade-count threshold serves an analogous, if simpler, role of guarding against overconfident inference from an underpowered comparison.

**Cross-country tax- and cost-adjusted backtesting.** To our knowledge, no existing framework combines point-in-time, jurisdiction-specific capital-gains taxation with dated, rather than static, discount and full-service brokerage fee schedules across a comparably broad multi-country equity universe. Most cross-country technical-analysis studies either ignore transaction costs entirely, apply a single assumed cost level uniformly across countries and time, or restrict comparison to a small number of developed markets. The point-in-time tax and brokerage dataset introduced here (Section 3.4, Section 7) is intended as a reusable contribution independent of the specific strategy results, addressing this gap.

---

# 3. Methods

## 3.1 Universe

We evaluate six canonical trading-strategy families against a 15-country, 25-index universe spanning the world's largest economies by GDP (IMF, October 2024 ranking), substituting Indonesia for Russia due to data-access constraints. Up to three liquid equity indices are included per country where available. All backtests cover 2011-01-01 to 2025-12-31, a window chosen to (a) align with the emergence of zero/low-commission discount brokerage platforms globally (e.g., Zerodha 2010, Robinhood 2013), which makes point-in-time brokerage-fee reconstruction tractable, and (b) ensure complete, non-restated index price history across all 25 constituent indices. This window excludes the 2008 Global Financial Crisis and the peak of the 2000 dot-com bubble; we treat this as a stated scoping limitation rather than an oversight (Section 6, Limitations).

## 3.2 Strategy Families

Six algorithmic strategy families were implemented via a validated natural-language-to-code parser (dual rule-based and LLM backend, cryptographically hash-verified for tamper-free code generation; see Section 3.5):

1. Trend-Following (50/200-day SMA Crossover)
2. Mean Reversion (14-day RSI Oscillator)
3. Absolute Momentum (12-month trailing, monthly rebalance)
4. Calendar Effect (Seasonal "Halloween" rule, long Nov–Apr)
5. Volatility Breakout (Bollinger Bands)
6. Drawdown Dip-Buying (52-week high drawdown trigger)

All strategies are long-only, cash-equity, single-index (no shorting, leverage, or derivatives), with signals computed at day *t* close and executed at day *t*+1 open to eliminate lookahead bias.

## 3.3 Friction Model

Each (strategy, index) pair is evaluated across four parallel return tracks plus a benchmark, all passed through an identical point-in-time statutory pipeline:

- **Track 1 (Gross):** Frictionless returns.
- **Track 2 (Net-of-Tax):** Adjusted for the resident investor's domestic capital-gains/securities-transaction tax, applied at the statutory rate in effect on each trade's closing date.
- **Track 3 (Net-Discount):** Track 2 plus discount/neo-broker commissions, exchange fees, and applicable transaction taxes (FTT/STT/stamp duty).
- **Track 4 (Net-Full-Service):** Track 2 plus full-service broker commissions.
- **Benchmark (Buy-and-Hold):** The same four-track pipeline applied to a passive buy-and-hold position, isolating the marginal cost of active trading from baseline market exposure.

Tax treatment is scoped to resident investors only (one statutory rate per country per period), avoiding the combinatorial bilateral-treaty matrix that non-resident treatment would require. Tax and brokerage schedules are point-in-time: statutory rates and fee structures are dated to their actual effective periods rather than applied as a single flat rate across the full window, with each transition sourced to a primary statutory or regulatory authority (e.g., national tax codes, Big-4 worldwide tax summaries, broker historical fee schedules via web archive snapshots).

## 3.4 Verification Pipeline

The tax and brokerage datasets underwent a two-stage verification process:

1. **Primary sourcing pass:** Each rate/fee row was extracted and dated against a primary source (government statute, regulatory filing, or archived broker fee schedule), with URL and exact source text recorded.
2. **Independent second-source audit:** A stratified sample of highest-risk rows — countries with only one or two rows across the full 14-year window (a signature of an under-specified, flattened multi-era rate) and brokerages known to have rebranded or changed pricing tiers — was independently re-verified by a separate model with no access to the original sourcing rationale.

This audit identified and corrected two errors prior to final analysis: (1) Japan's listed-equity capital gains tax was incorrectly modeled as a flat 20.315% for the full window; the correct rate was 10.147% from 2011–2013 (pre-reconstruction-surtax-expiry structure) before rising to 20.315% in 2014. (2) Germany's discount-brokerage track incorrectly back-applied Trade Republic's 2019-era €1.00 flat fee to 2011–2018; a representative pre-2019 discount broker fee (€5.90 flat, flatex, sourced to its BaFin-regulated historical fee schedule) was substituted for that period. Both corrections were propagated through the full pipeline and all downstream results (46 of 750 summary rows affected); neither correction changed the identity of any leaderboard-winning strategy-index pair (Section 4.1).

## 3.5 Reproducibility and Determinism

All simulations use a fixed random seed (seed=42) for Monte Carlo and bootstrap procedures. Bit-level determinism was confirmed by independently re-executing sampled (strategy, index) pairs and diffing all outputs (CAGR, drawdown, trade logs, bootstrap bounds) against the original run, with zero differences observed. The natural-language strategy parser's generated code was verified via SHA-256 hash comparison across independent runs to rule out post-hoc tuning, and evaluated against a sealed blind set of paraphrased strategy descriptions to test generalization beyond the canonical phrasing.

## 3.6 Statistical Robustness

For each qualified pair (≥5 realized round-trip trades), we compute: (a) an in-sample (2011–2018) / out-of-sample (2019–2025) CAGR degradation ratio; (b) 1,000-permutation Monte Carlo trade-shuffling to establish the 95th-percentile maximum drawdown, isolating sequence risk from strategy edge; and (c) 1,000-iteration bootstrap resampling to establish a 95% confidence interval on annualized CAGR.

**Minimum-sample reporting threshold.** Trade-count guards (n≥3 in-sample, n≥2 out-of-sample) were applied throughout, but we found this threshold insufficient to support headline performance claims: several leaderboard-topping results rested on as few as four realized trades in each sub-period, producing bootstrap CAGR confidence intervals exceeding 15 percentage points in width — wider than the point estimate itself. We therefore impose a stricter reporting threshold of n≥10 trades in *both* the in-sample and out-of-sample periods for any result presented as a headline finding. Results below this threshold are retained in the full supplementary dataset but are not used to support comparative claims.

---

# 4. Results

## 4.1 Full-Universe Overview

The complete battery (6 strategies × 25 indices × 5 tracks = 750 rows) qualified all 150 (strategy, index) pairs under the base trade-count guard (0 exclusions for late data start or n<5 trades). Zero friction-ordering anomalies were detected across all 150 pairs (Gross ≥ Net-Tax ≥ Net-Discount ≥ Net-Full-Service held universally), and zero near-zero fee-drag anomalies were flagged, supporting the internal consistency of the friction model.

At face value, the unrestricted leaderboard shows the 50/200 SMA Crossover on the Nasdaq Composite as the top performer across the full 150-pair universe (Net-Discount CAGR 10.70%, Calmar 0.33), followed on the same index by 12-Month Momentum (8.66%). The second-highest Net-Discount CAGR across the *entire* universe was in fact a different pair — 52-Week High Drawdown Dip-Buying on India's Nifty Bank (9.31%) — underscoring that these are index-specific rather than universe-wide rankings. All three of these headline results rest on only 4–5 realized trades per sub-period; for the two Nasdaq pairs, bootstrap 95% confidence intervals span 4.2%–19.5% and 0.2%–20.7% respectively — intervals wide enough that the point estimates alone are not statistically meaningful (Section 3.6). This relationship holds systematically across the full universe, not just these two pairs: across all 150 pairs, bootstrap CI width on the Net-Discount track is negatively correlated with minimum trade count (Pearson *r* = −0.268, *p* < 0.001), with pairs below the *n* = 10 threshold showing CI widths of up to 21.5 percentage points, tightening to roughly 4–14 percentage points above it (**Figure 1**).

**Figure 1.** Bootstrap 95% confidence interval width (percentage points) versus minimum in-sample/out-of-sample trade count, Net-Discount track, all 150 strategy-index pairs. The shaded region marks the thin-sample zone (*n* < 10); the vertical line marks the *n* = 10 reporting threshold adopted in this study.

## 4.2 Trade-Frequency-Filtered Results (n≥10)

Applying the n≥10 in-sample/out-of-sample threshold retains exactly 50 of 150 pairs (33.3%), and the retained set is not randomly distributed across strategies — it is fully determined by trade frequency: the two mean-reversion/breakout strategies (14-day RSI, Bollinger Bands) qualify on all 25 indices each, while all four trend, momentum, calendar, and dip-buying strategies — which by construction generate only a handful of signals over a 14-year window on daily/monthly data — qualify on zero indices.

Within this statistically defensible n≥10 subset:

- **46 of 50 pairs (92.0%)** show Net-Discount CAGR below the corresponding Buy-and-Hold benchmark, i.e., active trading underperforms passive exposure to the same index once realistic tax and brokerage frictions are applied.
- Only four pairs beat their passive benchmark net of discount-brokerage friction: 14-day RSI on the UK FTSE 100 (+3.08 pp) and Italy's FTSE MIB (+0.33 pp); Bollinger Bands Breakout on China's Shenzhen Component (+5.79 pp) and Shanghai Composite (+1.45 pp).

**Figure 2** shows this pattern directly for the top five indices (by Net-Discount CAGR) within each of the two qualifying strategies. The 14-day RSI Oscillator trails Buy-and-Hold on four of its five top markets — including a wide gap on the Nasdaq Composite (4.9% vs. 14.4%) — with the FTSE 100 as its sole outperformance case. Bollinger Bands Breakout shows the inverse pattern concentrated in mainland China: it outperforms Buy-and-Hold on both the Shenzhen Component and Shanghai Composite, but underperforms on its other top markets (South Korea, Brazil, India) once frictions are applied.

**Figure 2.** Net-Discount CAGR versus Buy-and-Hold CAGR for the top five indices (by Net-Discount CAGR) within each *n* ≥ 10-qualifying strategy. Panel A: 14-Day RSI Oscillator. Panel B: Bollinger Bands Breakout.

## 4.3 Interpretation

Two independent findings emerge. First, active trading strategies broadly fail to compensate for transaction costs and taxes relative to a passive buy-and-hold position on the same instrument, consistent with prior efficient-markets literature — but here demonstrated across a substantially wider cross-country, tax-and-brokerage-adjusted setting than is typical in the backtesting literature. Second, and methodologically, naive leaderboard-style reporting of "best strategy per market" is systematically biased toward low-frequency strategies precisely because their small trade counts inflate the *variance*, not the *edge*, of the reported point estimate; a trade-count-aware reporting threshold reverses which strategy families appear to lead. We present this second finding as a direct, generalizable caveat for any comparative backtesting framework, independent of the specific strategies or markets studied here.

---

# 5. Discussion

The trade-count effect documented in Section 4.2 is not specific to our strategy set or universe; it follows directly from the mathematics of bootstrap and confidence-interval estimation on small samples, and should generalize to any comparative backtest that spans strategies with structurally different trading frequencies. This has a direct methodological implication for the broader backtesting literature: a leaderboard, ranking, or "best strategy" claim is only as trustworthy as the trade count behind it, and frameworks that report point estimates without a matched confidence interval or a stated minimum-sample threshold risk systematically favoring exactly the results least deserving of confidence. We suggest that future comparative backtesting work adopt an explicit minimum-trade-count reporting threshold as a matter of course, analogous to a minimum sample size in any other empirical discipline, rather than treating trade-count adequacy as an afterthought addressed only in a robustness appendix.

Substantively, the finding that 92% of statistically reliable (n≥10) active strategy-index pairs underperform buy-and-hold once discount-brokerage frictions are applied is consistent with a large body of prior evidence on the difficulty of beating passive benchmarks net of costs, but extends that evidence to a considerably broader cross-country setting — 15 economies under point-in-time, jurisdiction-specific tax and brokerage treatment — than is typical in single-market studies. The four exceptions that do outperform (14-day RSI on the FTSE 100 and FTSE MIB; Bollinger Bands Breakout on the Shenzhen Component and Shanghai Composite) share a mean-reversion or volatility-breakout character and Chinese or UK/Italian venues; whether this reflects a genuine, exploitable market inefficiency or a feature of these particular index-strategy pairings within a 14-year window is not resolvable from a single non-overlapping evaluation period, and we do not claim the former. We report these four pairs descriptively rather than as evidence of a persistent edge.

# 6. Limitations

**Resident-investor tax scope.** All tax treatment is modeled for resident investors under domestic statutory rates. Non-resident investors are subject to bilateral tax-treaty provisions that vary by country pair and change independently of domestic tax law; modeling this fully would require up to 15×14 treaty combinations, each with its own historical amendment record, which we judged infeasible within the scope of this study. Results should not be interpreted as applicable to non-resident investors without further adjustment.

**Evaluation window (2011–2025).** The window excludes both the 2008 Global Financial Crisis and the peak of the 2000–2001 dot-com bubble. It was chosen because index price data and, more critically, brokerage fee-schedule and tax-code documentation are reliably recoverable across all 15 countries only from approximately 2010 onward, coinciding with the emergence of discount/neo-broker platforms globally. Findings here should not be read as claims about strategy robustness across earlier crisis regimes; a G7/US-only robustness extension to 2008 or earlier is a natural direction for future work where data permits.

**Retroactive and substituted fee/rate data.** Where a primary source for a specific period could not be located (e.g., a discount broker's pre-launch era in a given country), we substituted a representative contemporaneous alternative (Section 3.4, Germany pre-2019) rather than leaving the period unmodeled. These substitutions are flagged in the underlying dataset (`confidence` field) and should be treated as approximations rather than exact historical fee schedules.

**Index-level, not constituent-level, strategy execution.** Strategies are evaluated against index price series directly (as a proxy for an index-tracking instrument), not against constituent stocks within each index. This avoids survivorship bias and point-in-time index-membership complexity but means results characterize strategy performance on index-level exposure rather than active stock selection within a market.

**Single non-overlapping evaluation period.** In-sample and out-of-sample statistics are computed on one fixed split (2011–2018 / 2019–2025) rather than via walk-forward or rolling-window validation. This was a deliberate simplification to keep the point-in-time tax/brokerage pipeline tractable across 150 pairs; it means degradation ratios reflect a single historical regime shift rather than an average over multiple such shifts, and should be interpreted accordingly.

**Verification coverage.** The independent second-source audit (Section 3.4) covered a stratified, risk-prioritized sample of dataset rows — those most likely to contain a flattened multi-era rate or an outdated fee schedule — rather than every row in the dataset. While this sample-based approach identified and corrected two substantive errors, rows outside the audited sample have not received independent second-source verification and rely on the primary sourcing pass alone.

# 7. Data Availability

The complete point-in-time tax dataset (`tax_dataset.csv`, 35 statutory tax regimes across 15 countries, 2011–2025) and brokerage dataset (`brokerage_dataset.csv`, 58 fee schedules across discount and full-service brokers in 15 countries, 2011–2025), together with the full backtest output (`summary_cross_country.csv`, 750 rows; `robustness_summary.csv`, 150 rows; `leaderboard.csv` and `leaderboard_n10.csv`), have been deposited on Zenodo with the persistent identifier https://doi.org/10.5281/zenodo.22737302 alongside this manuscript. Each dataset row carries a `confidence` field indicating its sourcing tier (primary statutory source, independently cross-verified, or LLM-extracted pending further verification), allowing downstream users to filter to their required evidentiary standard. The backtesting framework's source code, including the tax and brokerage calculation engines, the natural-language strategy parser, and the full test suite (30 tests, 100% passing at time of submission), will be made available in a public code repository referenced in the final manuscript.

# References

Bailey, D. H., Borwein, J., López de Prado, M., & Zhu, Q. J. (2014). Pseudo-mathematics and financial charlatanism: The effects of backtest overfitting on out-of-sample performance. *Notices of the American Mathematical Society*, 61(5), 458-471.

Bailey, D. H., & López de Prado, M. (2014). The deflated Sharpe ratio: Correcting for selection bias, backtest overfitting, and non-normality. *Journal of Portfolio Management*, 40(5), 94-107.

Hanauer, M. X., & Lauterbach, J. G. (2023). The predictive ability of technical trading rules: An empirical analysis of developed and emerging equity markets. *Financial Markets and Portfolio Management*, 37, 461-506.

Harvey, C. R., Liu, Y., & Zhu, H. (2016). ...and the cross-section of expected returns. *The Review of Financial Studies*, 29(1), 5-68.

Sullivan, R., Timmermann, A., & White, H. (1999). Data-snooping, technical trading rule performance, and the bootstrap. *The Journal of Finance*, 54(5), 1647-1691.

White, H. (2000). A reality check for data snooping. *Econometrica*, 68(5), 1097-1126.
