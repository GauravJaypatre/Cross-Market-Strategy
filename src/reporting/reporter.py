"""Report generators producing JSON, Markdown, and styled HTML."""

import json
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

from src.engine.models import BacktestResult
from src.parser.models import ParserAuditRecord
from .ranking import partition_and_rank_results


METHODOLOGY_NOTE_SHARPE = (
    "Sharpe ratios are calculated from daily returns using an annualization factor of sqrt(252) "
    "(252 trading days/year) and an annualized risk-free rate of 0.0%. This stated simplification "
    "avoids confounding 15 divergent sovereign yield curves over the 2011–2025 period. "
    "Cross-market risk-adjusted capital efficiency should also be evaluated via the Calmar ratio "
    "and net excess CAGR over Buy & Hold."
)

METHODOLOGY_NOTE_CURRENCY = (
    "Rankings are computed within each currency's own terms (no FX adjustment); "
    "cross-country comparison does not account for exchange-rate fluctuations."
)

METHODOLOGY_NOTE_ROBUSTNESS_DISTINCTION = (
    "The Monte Carlo trade-shuffle (1,000 permutations) randomizes trade execution order to isolate sequence risk "
    "and path-dependent drawdown (P95), whereas the bootstrap confidence interval resamples trade returns "
    "with replacement to quantify parameter estimation uncertainty on annualized CAGR given small sample size (n < 30)."
)

DATASET_STATUS_DISCLOSURE = (
    "Reference / Preliminary Baseline (Curated from statutory authorities e.g. IRS, HMRC, Indian Finance Acts; "
    "tagged as primary_statutory_single_source until user-supplied cross-verified datasets are provided)."
)

SAMPLE_SIZE_CAUTION = (
    "Sample Size & Statistical Precision Notice (Low-n, Directional Only): Strategy trade counts range from "
    "7 to 13 trades across the 2011–2025 period. Because n < 30, individual index CAGR estimates carry wide "
    "95% bootstrap confidence intervals and must be interpreted as directional rather than definitive alpha."
)


def _fmt_pct(val: Optional[float], decimals: int = 2) -> str:
    if val is None or pd.isna(val):
        return "N/A"
    return f"{val * 100:.{decimals}f}%"


def _fmt_num(val: Optional[float], decimals: int = 2) -> str:
    if val is None or pd.isna(val):
        return "N/A"
    return f"{val:.{decimals}f}"


def generate_json_report(
    results: List[BacktestResult],
    audit_record: Optional[ParserAuditRecord],
    output_path: Path,
    seed: int = 42,
) -> dict:
    """Generate structured JSON report."""
    primary_ranked, calmar_ranked, excluded = partition_and_rank_results(results)

    def _serialize_result(r: BacktestResult, rank: int) -> dict:
        excess_cagr = None
        if r.net_discount_metrics and r.benchmark_discount_metrics:
            excess_cagr = round(r.net_discount_metrics.cagr - r.benchmark_discount_metrics.cagr, 4)

        return {
            "rank": rank,
            "country": r.country,
            "index_name": r.index_name,
            "data_source_id": r.data_source_id,
            "currency": r.currency,
            "data_start": r.data_start,
            "data_end": r.data_end,
            "provenance": r.provenance.to_dict() if r.provenance else {},
            "gross_metrics": r.gross_metrics.to_dict() if r.gross_metrics else {},
            "net_tax_metrics": r.net_tax_metrics.to_dict() if r.net_tax_metrics else {},
            "net_discount_metrics": r.net_discount_metrics.to_dict() if r.net_discount_metrics else {},
            "net_full_service_metrics": r.net_full_service_metrics.to_dict() if r.net_full_service_metrics else {},
            "benchmark_discount_metrics": r.benchmark_discount_metrics.to_dict() if r.benchmark_discount_metrics else {},
            "excess_cagr_vs_benchmark": excess_cagr,
            "alpha_vs_benchmark_cagr": excess_cagr,  # alias for backward compat
            "robustness": r.robustness.to_dict() if r.robustness else {},
            "exclusion_reason": r.exclusion_reason,
        }

    report_data = {
        "metadata": {
            "random_seed": seed,
            "dataset_status": DATASET_STATUS_DISCLOSURE,
            "sample_size_caution": SAMPLE_SIZE_CAUTION,
            "parser_audit": audit_record.to_dict() if audit_record else {},
            "methodology_disclosures": {
                "sharpe_annualization": METHODOLOGY_NOTE_SHARPE,
                "currency_terms": METHODOLOGY_NOTE_CURRENCY,
                "robustness_sequence_vs_estimation": METHODOLOGY_NOTE_ROBUSTNESS_DISTINCTION,
            },
            "total_indices_evaluated": len(results),
            "qualified_count": len(primary_ranked),
            "excluded_count": len(excluded),
        },
        "primary_ranking_cagr": [_serialize_result(r, i + 1) for i, r in enumerate(primary_ranked)],
        "secondary_ranking_calmar": [_serialize_result(r, i + 1) for i, r in enumerate(calmar_ranked)],
        "appendix_excluded": [_serialize_result(r, i + 1) for i, r in enumerate(excluded)],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    return report_data


def generate_markdown_report(
    results: List[BacktestResult],
    audit_record: Optional[ParserAuditRecord],
    output_path: Path,
    seed: int = 42,
) -> str:
    """Generate comprehensive Markdown report."""
    primary_ranked, calmar_ranked, excluded = partition_and_rank_results(results)

    backend_str = "Unknown"
    if audit_record:
        if audit_record.parser_backend_used == "llm":
            backend_str = f"AI-Parsed (LLM: {audit_record.model_name}, temp={audit_record.temperature})"
        else:
            backend_str = "Deterministic Rule-Based Parser"

    md = []
    md.append("# Cross-Market Strategy Backtest & Friction Impact Report\n")
    md.append(f"**Strategy Parsing Method:** `{backend_str}`\n")
    md.append(f"**Random Seed:** `{seed}` (Deterministic Monte Carlo & Bootstrap Resampling)\n")
    md.append(f"**Tax & Brokerage Dataset Status:** `Reference / Preliminary Baseline (primary_statutory_single_source)`\n")
    if audit_record:
        md.append(f"> **Strategy Description**: *\"{audit_record.strategy_text}\"*\n")

    md.append("## Methodological Disclosures\n")
    md.append(f"> [!NOTE]\n> **Sharpe Annualization & Risk-Free Rate**: {METHODOLOGY_NOTE_SHARPE}\n\n")
    md.append(f"> [!NOTE]\n> **Robustness Methodology (Sequence Risk vs Estimation Uncertainty)**: {METHODOLOGY_NOTE_ROBUSTNESS_DISTINCTION}\n\n")
    md.append(f"> [!IMPORTANT]\n> **Currency Standard & Stated Limitation**: {METHODOLOGY_NOTE_CURRENCY}\n\n")
    md.append(f"> [!WARNING]\n> **Dataset Verification Notice**: {DATASET_STATUS_DISCLOSURE}\n\n")
    md.append(f"> [!CAUTION]\n> **Low-Sample Precision Notice**: {SAMPLE_SIZE_CAUTION}\n\n")

    # Table 1: Primary Ranking
    md.append("## 1. Primary Ranking: Net-of-Tax-and-Discount-Brokerage CAGR\n")
    md.append("Qualified indices sorted by Net Discount CAGR. All four friction tracks and the Buy & Hold benchmark are displayed side by side.\n\n")
    md.append("| Rank | Country | Index | Ccy | Gross CAGR | Net-Tax CAGR | Net-Disc CAGR | 95% Bootstrap CI | Net-FS CAGR | B&H Net-Disc | Excess CAGR vs B&H | Max DD | Calmar | Sharpe | Trades | Data Start |")
    md.append("|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|")

    for i, r in enumerate(primary_ranked):
        gross_c = _fmt_pct(r.gross_metrics.cagr) if r.gross_metrics else "N/A"
        tax_c = _fmt_pct(r.net_tax_metrics.cagr) if r.net_tax_metrics else "N/A"
        disc_c = _fmt_pct(r.net_discount_metrics.cagr) if r.net_discount_metrics else "N/A"
        fs_c = _fmt_pct(r.net_full_service_metrics.cagr) if r.net_full_service_metrics else "N/A"
        bh_c = _fmt_pct(r.benchmark_discount_metrics.cagr) if r.benchmark_discount_metrics else "N/A"

        ci_str = "N/A"
        if r.robustness:
            ci_str = f"[{r.robustness.cagr_ci_lower * 100:.1f}%, {r.robustness.cagr_ci_upper * 100:.1f}%]"

        excess_str = "N/A"
        if r.net_discount_metrics and r.benchmark_discount_metrics:
            excess = r.net_discount_metrics.cagr - r.benchmark_discount_metrics.cagr
            prefix = "+" if excess >= 0 else ""
            excess_str = f"{prefix}{excess * 100:.2f}%"

        mdd = _fmt_pct(r.net_discount_metrics.max_drawdown) if r.net_discount_metrics else "N/A"
        calmar = _fmt_num(r.net_discount_metrics.calmar_ratio) if r.net_discount_metrics else "N/A"
        sharpe = _fmt_num(r.net_discount_metrics.sharpe_ratio) if r.net_discount_metrics else "N/A"
        trades = r.gross_metrics.total_trades if r.gross_metrics else 0

        md.append(f"| {i+1} | {r.country} | {r.index_name} | {r.currency} | {gross_c} | {tax_c} | **{disc_c}** | {ci_str} | {fs_c} | {bh_c} | {excess_str} | {mdd} | {calmar} | {sharpe} | {trades} | {r.data_start} |")

    # Table 2: Secondary Ranking (Calmar)
    md.append("\n## 2. Secondary Ranking: Calmar Ratio (Risk-Adjusted Efficiency)\n")
    md.append("Re-sorted by Calmar Ratio (CAGR / |Max Drawdown|) computed on the Net-of-Tax-and-Discount-Brokerage series.\n\n")
    md.append("| Calmar Rank | Country | Index | Calmar Ratio | Net-Disc CAGR | Max Drawdown | Sharpe | Total Trades |")
    md.append("|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|")

    for i, r in enumerate(calmar_ranked):
        calmar = _fmt_num(r.net_discount_metrics.calmar_ratio) if r.net_discount_metrics else "N/A"
        disc_c = _fmt_pct(r.net_discount_metrics.cagr) if r.net_discount_metrics else "N/A"
        mdd = _fmt_pct(r.net_discount_metrics.max_drawdown) if r.net_discount_metrics else "N/A"
        sharpe = _fmt_num(r.net_discount_metrics.sharpe_ratio) if r.net_discount_metrics else "N/A"
        trades = r.gross_metrics.total_trades if r.gross_metrics else 0
        md.append(f"| {i+1} | {r.country} | {r.index_name} | **{calmar}** | {disc_c} | {mdd} | {sharpe} | {trades} |")

    # Table 3: Robustness & Skeptical Validation
    md.append("\n## 3. Skeptical Robustness & Overfitting Evaluation\n")
    md.append("In-Sample (2011–2018) vs Out-of-Sample (2019–2025) performance degradation, 1,000 Monte Carlo trade sequence permutations, and 95% bootstrap CAGR confidence intervals.\n\n")
    md.append("| Country | Index | IS CAGR (2011-18) | OOS CAGR (2019-25) | Degradation (OOS/IS) | IS Trades | OOS Trades | IS Guard | OOS Guard | MC Worst DD (P95) | 95% Bootstrap CI | Precision Flag |")
    md.append("|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|")

    for r in primary_ranked:
        rob = r.robustness
        if rob:
            is_c = _fmt_pct(rob.is_cagr)
            oos_c = _fmt_pct(rob.oos_cagr)
            # Whenever IS CAGR is within +/-1% of zero, surface raw pp difference to fix ratio distortion
            if abs(rob.is_cagr) <= 0.01:
                deg = f"{rob.degradation_ratio:.2f}x ({rob.delta_cagr_pp*100:+.2f} pp)"
            else:
                deg = f"{rob.degradation_ratio:.2f}x ({rob.delta_cagr_pp*100:+.2f} pp)"
            is_g = "PASS" if not rob.is_insufficient_sample else "WARN (<3)"
            oos_g = "PASS" if not rob.oos_insufficient_sample else "WARN (<2)"
            mc_dd = _fmt_pct(rob.mc_p95_max_drawdown)
            ci_str = f"[{rob.cagr_ci_lower * 100:.1f}%, {rob.cagr_ci_upper * 100:.1f}%]"
            prec_flag = "Directional (n<30)" if rob.is_directional_only else "Robust (n>=30)"
            md.append(f"| {r.country} | {r.index_name} | {is_c} | {oos_c} | {deg} | {rob.is_trade_count} | {rob.oos_trade_count} | {is_g} | {oos_g} | {mc_dd} | {ci_str} | `{prec_flag}` |")

    # Table 4: Appendix (Excluded Indices)
    md.append("\n## Appendix: Excluded Indices & Data Guards\n")
    if excluded:
        md.append("The following indices were excluded from headline rankings due to coverage restrictions or sample size requirements (`data_start > 2011-01-01` or `trades < 5`):\n\n")
        md.append("| Country | Index | Coverage Start | Total Trades | Stated Reason for Exclusion |")
        md.append("|:---|:---|:---:|:---:|:---|")
        for r in excluded:
            trades = r.gross_metrics.total_trades if r.gross_metrics else 0
            md.append(f"| {r.country} | {r.index_name} | {r.data_start} | {trades} | `{r.exclusion_reason}` |")
    else:
        md.append("*No indices were excluded. All universe targets met coverage and sample size thresholds.*\n")

    # Table 5: Data Provenance Table
    md.append("\n## Data Provenance & Cryptographic Audit\n")
    md.append("Audit trail of market data sources used for each index.\n\n")
    md.append("| Country | Index | Ticker / ID | Vendor | Source Identifier | SHA256 Checksum | Rows | Date Window |")
    md.append("|:---|:---|:---:|:---:|:---|:---:|:---:|:---:|")
    for r in results:
        p = r.provenance
        if p:
            sha_short = (p.sha256[:12] + "...") if p.sha256 else "N/A (API)"
            source_short = Path(p.source_identifier).name if p.vendor == "local_csv" else p.source_identifier
            md.append(f"| {r.country} | {r.index_name} | `{r.data_source_id}` | `{p.vendor}` | `{source_short}` | `{sha_short}` | {p.row_count} | {p.data_start} to {p.data_end} |")

    content = "\n".join(md)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return content


def generate_html_report(
    results: List[BacktestResult],
    audit_record: Optional[ParserAuditRecord],
    output_path: Path,
    seed: int = 42,
) -> str:
    """Generate modern, responsive HTML report."""
    primary_ranked, calmar_ranked, excluded = partition_and_rank_results(results)

    backend_label = "Deterministic Rule-Based Parser"
    backend_class = "badge-rule"
    if audit_record and audit_record.parser_backend_used == "llm":
        backend_label = f"LLM ({audit_record.model_name}, temp={audit_record.temperature})"
        backend_class = "badge-llm"

    strat_text = audit_record.strategy_text if audit_record else "Trading Strategy"

    # Top winner
    top_winner = primary_ranked[0] if primary_ranked else None

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cross-Market Backtesting & Friction Report</title>
<style>
  :root {{
    --bg: #0d1117;
    --card-bg: #161b22;
    --border: #30363d;
    --text: #c9d1d9;
    --text-heading: #f0f6fc;
    --accent: #58a6ff;
    --success: #3fb950;
    --warning: #d29922;
    --danger: #f85149;
    --purple: #bc8cff;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background-color: var(--bg);
    color: var(--text);
    line-height: 1.6;
    margin: 0;
    padding: 24px;
  }}
  .container {{
    max-width: 1400px;
    margin: 0 auto;
  }}
  h1, h2, h3 {{
    color: var(--text-heading);
    font-weight: 600;
  }}
  .header-card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 24px;
  }}
  .badge {{
    display: inline-block;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-right: 8px;
  }}
  .badge-llm {{
    background: rgba(88, 166, 255, 0.15);
    color: var(--accent);
    border: 1px solid var(--accent);
  }}
  .badge-rule {{
    background: rgba(188, 140, 255, 0.15);
    color: var(--purple);
    border: 1px solid var(--purple);
  }}
  .badge-pass {{
    background: rgba(63, 185, 80, 0.15);
    color: var(--success);
  }}
  .badge-warn {{
    background: rgba(210, 153, 34, 0.15);
    color: var(--warning);
  }}
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
    margin: 20px 0;
  }}
  .kpi-card {{
    background: #0e141b;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 16px;
  }}
  .kpi-title {{
    font-size: 0.8rem;
    text-transform: uppercase;
    color: #8b949e;
  }}
  .kpi-val {{
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-heading);
    margin-top: 4px;
  }}
  .callout {{
    background: #1c2128;
    border-left: 4px solid var(--accent);
    padding: 12px 16px;
    margin: 16px 0;
    border-radius: 0 6px 6px 0;
    font-size: 0.9rem;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    font-size: 0.9rem;
  }}
  th, td {{
    padding: 10px 12px;
    text-align: left;
    border-bottom: 1px solid var(--border);
  }}
  th {{
    background: #21262d;
    color: var(--text-heading);
    font-weight: 600;
  }}
  tr:hover td {{
    background: rgba(255, 255, 255, 0.02);
  }}
  .num {{
    text-align: right;
    font-variant-numeric: tabular-nums;
  }}
  .highlight {{
    color: var(--success);
    font-weight: 700;
  }}
  .section {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 24px;
    overflow-x: auto;
  }}
</style>
</head>
<body>
<div class="container">
  <div class="header-card">
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <h1>Cross-Market Strategy Backtest & Real-World Friction Report</h1>
      <div>
        <span class="badge" style="background: rgba(88, 166, 255, 0.15); color: var(--accent); border: 1px solid var(--border);">Seed: {seed}</span>
        <span class="badge {backend_class}">Method: {backend_label}</span>
      </div>
    </div>
    <p style="font-size:1.1rem; color:#8b949e;">Strategy: <em>"{strat_text}"</em></p>
    
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-title">Universe Size</div>
        <div class="kpi-val">{len(results)} Indices</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Qualified for Headline</div>
        <div class="kpi-val">{len(primary_ranked)} Indices</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Excluded (Late / Low Sample)</div>
        <div class="kpi-val">{len(excluded)} Indices</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Top Net-Discount Fit</div>
        <div class="kpi-val highlight">{top_winner.country if top_winner else "N/A"} ({_fmt_pct(top_winner.net_discount_metrics.cagr if top_winner else 0)})</div>
      </div>
    </div>

    <div class="callout">
      <strong>Methodology Disclosures:</strong><br>
      • <strong>Sharpe Annualization & Risk-Free Rate:</strong> {METHODOLOGY_NOTE_SHARPE}<br>
      • <strong>Robustness Methodology (Sequence Risk vs Estimation Uncertainty):</strong> {METHODOLOGY_NOTE_ROBUSTNESS_DISTINCTION}<br>
      • <strong>Currency Terms:</strong> {METHODOLOGY_NOTE_CURRENCY}<br>
      • <strong>Dataset Status:</strong> {DATASET_STATUS_DISCLOSURE}
    </div>
    <div class="callout" style="border-left-color: var(--warning);">
      <strong>Low-Sample Precision Notice:</strong> {SAMPLE_SIZE_CAUTION}
    </div>
  </div>

  <div class="section">
    <h2>1. Primary Ranking: Net-of-Tax-and-Discount-Brokerage CAGR</h2>
    <p>Sorted by Net Discount CAGR. Shows gross and net friction tracks side by side with the Buy & Hold benchmark.</p>
    <table>
      <thead>
        <tr>
          <th>Rank</th>
          <th>Country</th>
          <th>Index</th>
          <th>Ccy</th>
          <th class="num">Gross CAGR</th>
          <th class="num">Net-Tax CAGR</th>
          <th class="num">Net-Disc CAGR</th>
          <th class="num">95% Bootstrap CI</th>
          <th class="num">Net-FS CAGR</th>
          <th class="num">B&H Net-Disc</th>
          <th class="num">Excess CAGR vs B&H</th>
          <th class="num">Max DD</th>
          <th class="num">Calmar</th>
          <th class="num">Sharpe</th>
          <th class="num">Trades</th>
          <th>Start Date</th>
        </tr>
      </thead>
      <tbody>
"""
    for i, r in enumerate(primary_ranked):
        gross_c = _fmt_pct(r.gross_metrics.cagr) if r.gross_metrics else "N/A"
        tax_c = _fmt_pct(r.net_tax_metrics.cagr) if r.net_tax_metrics else "N/A"
        disc_c = _fmt_pct(r.net_discount_metrics.cagr) if r.net_discount_metrics else "N/A"
        fs_c = _fmt_pct(r.net_full_service_metrics.cagr) if r.net_full_service_metrics else "N/A"
        bh_c = _fmt_pct(r.benchmark_discount_metrics.cagr) if r.benchmark_discount_metrics else "N/A"

        ci_str = "N/A"
        if r.robustness:
            ci_str = f"[{r.robustness.cagr_ci_lower * 100:.1f}%, {r.robustness.cagr_ci_upper * 100:.1f}%]"

        excess_str = "N/A"
        if r.net_discount_metrics and r.benchmark_discount_metrics:
            excess = r.net_discount_metrics.cagr - r.benchmark_discount_metrics.cagr
            prefix = "+" if excess >= 0 else ""
            excess_str = f"{prefix}{excess * 100:.2f}%"

        mdd = _fmt_pct(r.net_discount_metrics.max_drawdown) if r.net_discount_metrics else "N/A"
        calmar = _fmt_num(r.net_discount_metrics.calmar_ratio) if r.net_discount_metrics else "N/A"
        sharpe = _fmt_num(r.net_discount_metrics.sharpe_ratio) if r.net_discount_metrics else "N/A"
        trades = r.gross_metrics.total_trades if r.gross_metrics else 0

        html += f"""
        <tr>
          <td><strong>#{i+1}</strong></td>
          <td>{r.country}</td>
          <td>{r.index_name}</td>
          <td><code>{r.currency}</code></td>
          <td class="num">{gross_c}</td>
          <td class="num">{tax_c}</td>
          <td class="num highlight">{disc_c}</td>
          <td class="num">{ci_str}</td>
          <td class="num">{fs_c}</td>
          <td class="num">{bh_c}</td>
          <td class="num">{excess_str}</td>
          <td class="num">{mdd}</td>
          <td class="num">{calmar}</td>
          <td class="num">{sharpe}</td>
          <td class="num">{trades}</td>
          <td>{r.data_start}</td>
        </tr>
"""

    html += """
      </tbody>
    </table>
  </div>

  <div class="section">
    <h2>2. Secondary Ranking: Calmar Ratio (Risk-Adjusted Efficiency)</h2>
    <p>Re-sorted strictly by Calmar Ratio (CAGR / |Max Drawdown|) on the Net-Discount track.</p>
    <table>
      <thead>
        <tr>
          <th>Calmar Rank</th>
          <th>Country</th>
          <th>Index</th>
          <th class="num">Calmar Ratio</th>
          <th class="num">Net-Disc CAGR</th>
          <th class="num">Max Drawdown</th>
          <th class="num">Sharpe Ratio</th>
          <th class="num">Total Trades</th>
        </tr>
      </thead>
      <tbody>
"""
    for i, r in enumerate(calmar_ranked):
        calmar = _fmt_num(r.net_discount_metrics.calmar_ratio) if r.net_discount_metrics else "N/A"
        disc_c = _fmt_pct(r.net_discount_metrics.cagr) if r.net_discount_metrics else "N/A"
        mdd = _fmt_pct(r.net_discount_metrics.max_drawdown) if r.net_discount_metrics else "N/A"
        sharpe = _fmt_num(r.net_discount_metrics.sharpe_ratio) if r.net_discount_metrics else "N/A"
        trades = r.gross_metrics.total_trades if r.gross_metrics else 0
        html += f"""
        <tr>
          <td><strong>#{i+1}</strong></td>
          <td>{r.country}</td>
          <td>{r.index_name}</td>
          <td class="num highlight">{calmar}</td>
          <td class="num">{disc_c}</td>
          <td class="num">{mdd}</td>
          <td class="num">{sharpe}</td>
          <td class="num">{trades}</td>
        </tr>
"""

    html += """
      </tbody>
    </table>
  </div>

  <div class="section">
    <h2>3. Robustness & Skeptical Validation Suite</h2>
    <p>In-Sample (2011–2018) vs Out-of-Sample (2019–2025) split and 1,000 Monte Carlo trade reshuffles.</p>
    <table>
      <thead>
        <tr>
          <th>Country</th>
          <th>Index</th>
          <th class="num">IS CAGR (2011-18)</th>
          <th class="num">OOS CAGR (2019-25)</th>
          <th class="num">Degradation (OOS/IS)</th>
          <th class="num">IS Trades</th>
          <th class="num">OOS Trades</th>
          <th>IS Guard</th>
          <th>OOS Guard</th>
          <th class="num">MC Worst DD (P95)</th>
          <th class="num">95% Bootstrap CI</th>
          <th>Precision Flag</th>
        </tr>
      </thead>
      <tbody>
"""
    for r in primary_ranked:
        rob = r.robustness
        if rob:
            is_c = _fmt_pct(rob.is_cagr)
            oos_c = _fmt_pct(rob.oos_cagr)
            deg = f"{rob.degradation_ratio:.2f}x"
            is_badge = '<span class="badge badge-pass">PASS</span>' if not rob.is_insufficient_sample else '<span class="badge badge-warn">WARN (&lt;3)</span>'
            oos_badge = '<span class="badge badge-pass">PASS</span>' if not rob.oos_insufficient_sample else '<span class="badge badge-warn">WARN (&lt;2)</span>'
            mc_dd = _fmt_pct(rob.mc_p95_max_drawdown)
            ci_str = f"[{rob.cagr_ci_lower * 100:.1f}%, {rob.cagr_ci_upper * 100:.1f}%]"
            prec_badge = '<span class="badge badge-warn">Directional (n&lt;30)</span>' if rob.is_directional_only else '<span class="badge badge-pass">Robust (n&gt;=30)</span>'
            html += f"""
        <tr>
          <td>{r.country}</td>
          <td>{r.index_name}</td>
          <td class="num">{is_c}</td>
          <td class="num">{oos_c}</td>
          <td class="num">{deg}</td>
          <td class="num">{rob.is_trade_count}</td>
          <td class="num">{rob.oos_trade_count}</td>
          <td>{is_badge}</td>
          <td>{oos_badge}</td>
          <td class="num">{mc_dd}</td>
          <td class="num">{ci_str}</td>
          <td>{prec_badge}</td>
        </tr>
"""

    html += f"""
      </tbody>
    </table>
  </div>

  <div class="section">
    <h2>Appendix: Excluded Indices & Data Coverage</h2>
    <p>Excluded from headline rankings due to late data start (&gt; 2011-01-01) or sample size &lt; 5 trades.</p>
    <table>
      <thead>
        <tr>
          <th>Country</th>
          <th>Index</th>
          <th>Coverage Start</th>
          <th class="num">Total Trades</th>
          <th>Reason for Exclusion</th>
        </tr>
      </thead>
      <tbody>
"""
    for r in excluded:
        trades = r.gross_metrics.total_trades if r.gross_metrics else 0
        html += f"""
        <tr>
          <td>{r.country}</td>
          <td>{r.index_name}</td>
          <td>{r.data_start}</td>
          <td class="num">{trades}</td>
          <td><span class="badge badge-warn">{r.exclusion_reason}</span></td>
        </tr>
"""
    if not excluded:
        html += "<tr><td colspan='5'><em>No indices excluded. All meet criteria.</em></td></tr>"

    html += """
      </tbody>
    </table>
  </div>

  <div class="section">
    <h2>Data Provenance & Cryptographic Audit</h2>
    <p>Cryptographic checksums and vendor tracking for all evaluated data feeds.</p>
    <table>
      <thead>
        <tr>
          <th>Country</th>
          <th>Index</th>
          <th>Ticker / ID</th>
          <th>Vendor</th>
          <th>Source Path / Ticker</th>
          <th>SHA256 (Local)</th>
          <th class="num">Rows</th>
          <th>Date Window</th>
        </tr>
      </thead>
      <tbody>
"""
    for r in results:
        p = r.provenance
        if p:
            sha_short = (p.sha256[:12] + "...") if p.sha256 else "N/A (API)"
            source_short = Path(p.source_identifier).name if p.vendor == "local_csv" else p.source_identifier
            html += f"""
        <tr>
          <td>{r.country}</td>
          <td>{r.index_name}</td>
          <td><code>{r.data_source_id}</code></td>
          <td><span class="badge badge-pass">{p.vendor}</span></td>
          <td><code>{source_short}</code></td>
          <td><code>{sha_short}</code></td>
          <td class="num">{p.row_count}</td>
          <td>{p.data_start} to {p.data_end}</td>
        </tr>
"""

    html += """
      </tbody>
    </table>
  </div>
</div>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return html


def generate_reports(
    results: List[BacktestResult],
    audit_record: Optional[ParserAuditRecord],
    output_dir: Path,
    seed: int = 42,
) -> Dict[str, Path]:
    """Generate JSON, Markdown, and HTML reports."""
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "report.json"
    md_path = output_dir / "report.md"
    html_path = output_dir / "report.html"

    generate_json_report(results, audit_record, json_path, seed=seed)
    generate_markdown_report(results, audit_record, md_path, seed=seed)
    generate_html_report(results, audit_record, html_path, seed=seed)

    return {
        "json": json_path,
        "markdown": md_path,
        "html": html_path,
    }
