"""Script to generate publication-ready figures for the full battery results.

Figure 1: fig1_ci_width_vs_trades.png
- Scatter plot from robustness_summary.csv
- x-axis: min(n_trades_is, n_trades_oos)
- y-axis: bootstrap CI width (bootstrap_ci_high - bootstrap_ci_low)
- Vertical reference line at n=10
- Title: "Bootstrap CI Width vs. Minimum Trade Count"
- Annotate Pearson r = -0.268 in the corner

Figure 2: fig2_n10_leaderboard.png
- Grouped bar chart for the two qualifying strategies: 14-Day RSI Oscillator, Bollinger Bands Breakout
- Top 5 indices by Net-Discount CAGR for each strategy
- Side-by-side bars for Net-Discount CAGR vs Buy-and-Hold CAGR
- Consistent colors and shared legend across panels
"""

from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
from scipy.stats import pearsonr


def setup_academic_style():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
        "axes.edgecolor": "#333333",
        "axes.linewidth": 0.8,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.labelsize": 10,
        "axes.labelweight": "medium",
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "xtick.major.size": 4,
        "ytick.major.size": 4,
        "xtick.color": "#333333",
        "ytick.color": "#333333",
        "figure.titlesize": 12,
        "figure.titleweight": "bold",
        "grid.color": "#e0e0e0",
        "grid.linestyle": "--",
        "grid.linewidth": 0.5,
        "grid.alpha": 0.7,
    })


def generate_figure_1(out_path: Path):
    rob = pd.read_csv("results/full_battery/robustness_summary.csv")
    
    # Calculate x and y
    rob["min_trades"] = rob[["n_trades_is", "n_trades_oos"]].min(axis=1)
    rob["ci_width"] = rob["bootstrap_ci_high"] - rob["bootstrap_ci_low"]
    
    r, p_val = pearsonr(rob["min_trades"], rob["ci_width"])
    
    fig, ax = plt.subplots(figsize=(6.2, 4.2), dpi=300)
    
    # Shaded region for thin-sample zone (n < 10)
    ax.axvspan(0, 10, color="#f8d7da", alpha=0.35, zorder=1, label="Thin-sample zone ($n < 10$)")
    
    # Vertical reference line at n=10
    ax.axvline(x=10, color="#b02a37", linestyle="--", linewidth=1.2, zorder=2, label="Reporting threshold ($n = 10$)")
    
    # Scatter points (150 pairs)
    ax.scatter(
        rob["min_trades"],
        rob["ci_width"] * 100,  # in percentage points
        color="#1f4e79",
        edgecolor="#ffffff",
        linewidth=0.6,
        s=38,
        alpha=0.78,
        zorder=3,
        label="Strategy × Index pairs ($N=150$)",
    )
    
    # Formatting
    ax.set_title("Bootstrap CI Width vs. Minimum Trade Count", pad=12)
    ax.set_xlabel("Minimum Sub-Period Realized Trades, $\\min(n_{\\mathrm{IS}}, n_{\\mathrm{OOS}})$")
    ax.set_ylabel("Bootstrap 95% CI Width on Annualized CAGR (pp)")
    
    ax.set_xlim(0, max(rob["min_trades"]) + 2)
    ax.set_ylim(0, max(rob["ci_width"] * 100) + 3)
    
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.grid(True, axis="y", zorder=0)
    
    # Remove top and right spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    
    # Annotate Pearson r in the corner
    annotation_text = f"Pearson $r = {r:.3f}$\n($p < 0.001$, $N = 150$)"
    ax.text(
        0.96, 0.94,
        annotation_text,
        transform=ax.transAxes,
        fontsize=9,
        verticalalignment="top",
        horizontalalignment="right",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#ffffff", edgecolor="#cccccc", alpha=0.9),
        zorder=4,
    )
    
    # Legend
    ax.legend(loc="upper center", bbox_to_anchor=(0.48, 0.97), fontsize=8, frameon=True, framealpha=0.9, edgecolor="#dddddd")
    
    plt.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Figure 1 saved to: {out_path.resolve()}")


def generate_figure_2(out_path: Path):
    n10_detail = pd.read_csv("results/full_battery/n10_full_detail.csv")
    
    strategies = [
        ("14-Day RSI Oscillator", "Panel A: 14-Day RSI Oscillator (Mean Reversion)"),
        ("Bollinger Bands Breakout", "Panel B: Bollinger Bands Breakout (Volatility)"),
    ]
    
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6), dpi=300, sharey=True)
    
    # Distinct, standard academic colors
    color_active = "#2b5c8f"    # Deep Slate Blue
    color_bh = "#d95f02"        # Terracotta / Burnt Orange
    
    for ax_idx, (strat_name, panel_title) in enumerate(strategies):
        ax = axes[ax_idx]
        s_df = n10_detail[n10_detail["strategy"] == strat_name]
        
        # Get top 5 indices by Net-Discount CAGR
        top5_disc = s_df[s_df["track"] == "Net-Discount"].sort_values(by="CAGR", ascending=False).head(5)
        
        index_labels = []
        active_cagrs = []
        bh_cagrs = []
        
        # Friendly abbreviations or clean labels
        label_map = {
            ("United States", "S&P 500"): "US (S&P 500)",
            ("Germany", "TecDAX"): "Germany (TecDAX)",
            ("United Kingdom", "FTSE 100"): "UK (FTSE 100)",
            ("United States", "Dow Jones Industrial Average"): "US (DJIA)",
            ("United States", "Nasdaq Composite"): "US (Nasdaq Comp)",
            ("China", "Shenzhen Component"): "China (Shenzhen)",
            ("China", "Shanghai Composite"): "China (Shanghai)",
            ("South Korea", "KOSPI"): "S. Korea (KOSPI)",
            ("Brazil", "Ibovespa"): "Brazil (Ibovespa)",
            ("India", "Nifty Bank"): "India (Nifty Bank)",
        }
        
        for _, row in top5_disc.iterrows():
            c, i = row["country"], row["index"]
            lbl = label_map.get((c, i), f"{c}\n({i})")
            index_labels.append(lbl)
            
            act_val = row["CAGR"] * 100
            bh_val = s_df[(s_df["country"] == c) & (s_df["index"] == i) & (s_df["track"] == "Buy-and-Hold")]["CAGR"].iloc[0] * 100
            active_cagrs.append(act_val)
            bh_cagrs.append(bh_val)
            
        x = np.arange(len(index_labels))
        width = 0.36
        
        rects1 = ax.bar(x - width/2, active_cagrs, width, label="Active Strategy (Net-Discount)", color=color_active, edgecolor="#ffffff", linewidth=0.5, zorder=3)
        rects2 = ax.bar(x + width/2, bh_cagrs, width, label="Buy-and-Hold Benchmark", color=color_bh, edgecolor="#ffffff", linewidth=0.5, zorder=3)
        
        # Add value labels on top of bars
        for r in rects1:
            h = r.get_height()
            ax.annotate(f"{h:.1f}%",
                        xy=(r.get_x() + r.get_width() / 2, h),
                        xytext=(0, 2.5),
                        textcoords="offset points",
                        ha="center", va="bottom", fontsize=7.5, color="#222222")
                        
        for r in rects2:
            h = r.get_height()
            ax.annotate(f"{h:.1f}%",
                        xy=(r.get_x() + r.get_width() / 2, h),
                        xytext=(0, 2.5),
                        textcoords="offset points",
                        ha="center", va="bottom", fontsize=7.5, color="#222222")
        
        ax.set_title(panel_title, pad=10)
        ax.set_xticks(x)
        ax.set_xticklabels(index_labels, rotation=25, ha="right")
        ax.grid(True, axis="y", zorder=0)
        
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        
        if ax_idx == 0:
            ax.set_ylabel("Annualized CAGR (%)")
            
    # Format y-axis as percentage
    axes[0].yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    axes[0].set_ylim(0, 16.5)
    
    # Shared figure legend at the top
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.02), ncol=2, frameon=False, fontsize=9.5)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Figure 2 saved to: {out_path.resolve()}")


def main():
    setup_academic_style()
    fig_dir = Path("results/full_battery/figures")
    fig_dir.mkdir(parents=True, exist_ok=True)
    
    fig1_path = fig_dir / "fig1_ci_width_vs_trades.png"
    fig2_path = fig_dir / "fig2_n10_leaderboard.png"
    
    generate_figure_1(fig1_path)
    generate_figure_2(fig2_path)


if __name__ == "__main__":
    main()
