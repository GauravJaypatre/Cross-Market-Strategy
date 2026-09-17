"""Generate three publication-quality figures/diagrams for docs/figures/:

1. fig3_universe_map.png:
   - World map highlighting 15 countries in the study universe
   - Discrete shaded categories (3 indices, 2 indices, 1 index)
   - Caption: "15 countries, 25 indices, 2011-2025"
   - 300 DPI PNG

2. fig4_pipeline_architecture.png:
   - Schematic methodology diagram (boxes & arrows)
   - NL Input -> Parser -> Signal Gen -> Engine (t close signal, t+1 open exec)
     -> 5 parallel tracks -> Robustness Layer -> Reporting
   - 300 DPI PNG

3. fig5_trade_count_distribution.png:
   - Box plot + jittered strip plot of realized trades (n_is + n_oos) by strategy family (N=150)
   - Horizontal reference line at n=10
   - 300 DPI PNG
"""

import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd
from PIL import Image
import plotly.graph_objects as go
import seaborn as sns


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


def generate_figure_3_map(out_path: Path):
    """Generate high-resolution world choropleth map."""
    countries_data = [
        ('United States', 'USA', '3 Constituent Indices (US, Germany, India)', 'S&P 500, Nasdaq, DJIA'),
        ('China', 'CHN', '2 Constituent Indices (China, UK, S. Korea, Australia)', 'Shanghai Comp., Shenzhen Comp.'),
        ('Germany', 'DEU', '3 Constituent Indices (US, Germany, India)', 'DAX 40, MDAX, TecDAX'),
        ('Japan', 'JPN', '1 Constituent Index (8 Markets)', 'Nikkei 225'),
        ('India', 'IND', '3 Constituent Indices (US, Germany, India)', 'Nifty 50, Sensex, Nifty Bank'),
        ('United Kingdom', 'GBR', '2 Constituent Indices (China, UK, S. Korea, Australia)', 'FTSE 100, FTSE 250'),
        ('France', 'FRA', '1 Constituent Index (8 Markets)', 'CAC 40'),
        ('Italy', 'ITA', '1 Constituent Index (8 Markets)', 'FTSE MIB'),
        ('Indonesia', 'IDN', '1 Constituent Index (8 Markets)', 'Jakarta Composite'),
        ('Canada', 'CAN', '1 Constituent Index (8 Markets)', 'S&P/TSX Composite'),
        ('Brazil', 'BRA', '1 Constituent Index (8 Markets)', 'Ibovespa'),
        ('South Korea', 'KOR', '2 Constituent Indices (China, UK, S. Korea, Australia)', 'KOSPI, KOSDAQ'),
        ('Australia', 'AUS', '2 Constituent Indices (China, UK, S. Korea, Australia)', 'ASX 200, All Ordinaries'),
        ('Mexico', 'MEX', '1 Constituent Index (8 Markets)', 'IPC Mexico'),
        ('Spain', 'ESP', '1 Constituent Index (8 Markets)', 'IBEX 35')
    ]

    df = pd.DataFrame(countries_data, columns=['country', 'iso', 'tier', 'indices'])

    fig = go.Figure()

    color_map = {
        '3 Constituent Indices (US, Germany, India)': '#1f4e79',
        '2 Constituent Indices (China, UK, S. Korea, Australia)': '#326295',
        '1 Constituent Index (8 Markets)': '#5c8bb7',
    }

    for tier in ['3 Constituent Indices (US, Germany, India)', '2 Constituent Indices (China, UK, S. Korea, Australia)', '1 Index (8 Markets)']:
        tier_label = tier if tier in color_map else '1 Constituent Index (8 Markets)'
        sub = df[df['tier'] == tier_label]
        fig.add_trace(go.Choropleth(
            locations=sub['iso'],
            z=[1]*len(sub),
            colorscale=[[0, color_map[tier_label]], [1, color_map[tier_label]]],
            showscale=False,
            showlegend=True,
            name=tier_label,
            marker_line_color='#ffffff',
            marker_line_width=0.8,
        ))

    fig.update_geos(
        projection_type='natural earth',
        projection_rotation_lon=11,
        showcoastlines=True,
        coastlinecolor='#b8c0c8',
        coastlinewidth=0.6,
        showcountries=True,
        countrycolor='#d5dadf',
        countrywidth=0.5,
        showland=True,
        landcolor='#f4f5f7',
        showocean=True,
        oceancolor='#ffffff',
        bgcolor='#ffffff'
    )

    fig.update_layout(
        title=dict(
            text='Global Equity Universe: 15 Economies and 25 Constituent Indices (2011–2025)',
            font=dict(family='DejaVu Sans, Arial, sans-serif', size=15, color='#111111'),
            x=0.5,
            y=0.96,
            xanchor='center',
            yanchor='top'
        ),
        legend=dict(
            title=dict(text='<b>Coverage Depth:</b>', font=dict(family='DejaVu Sans, Arial, sans-serif', size=10, color='#222222')),
            font=dict(family='DejaVu Sans, Arial, sans-serif', size=9.5, color='#333333'),
            orientation='h',
            yanchor='bottom',
            y=0.04,
            xanchor='center',
            x=0.5,
            bgcolor='rgba(255,255,255,0.95)',
            bordercolor='#bbbbbb',
            borderwidth=0.8,
            itemsizing='constant'
        ),
        annotations=[
            dict(
                text='<b>Universe Scope:</b> 15 countries, 25 indices, 2011–2025  |  IMF Oct 2024 GDP Ranking (Indonesia substituted for Russia)',
                xref='paper', yref='paper',
                x=0.5, y=0.11,
                showarrow=False,
                font=dict(family='DejaVu Sans, Arial, sans-serif', size=9.5, color='#333333'),
                bgcolor='rgba(255,255,255,0.95)',
                bordercolor='#bbbbbb',
                borderwidth=0.8,
                borderpad=5
            )
        ],
        margin=dict(l=15, r=15, t=50, b=30),
        width=1100,
        height=580,
        paper_bgcolor='#ffffff',
        plot_bgcolor='#ffffff'
    )

    temp_raw = out_path.parent / "temp_map_raw.png"
    fig.write_image(str(temp_raw), scale=3)

    # Re-save with PIL to ensure 300 DPI metadata
    im = Image.open(temp_raw)
    im.save(out_path, dpi=(300, 300))
    temp_raw.unlink(missing_ok=True)
    print(f"Figure 3 saved to: {out_path.resolve()}")


def generate_figure_4_architecture(out_path: Path):
    """Generate pipeline schematic diagram."""
    fig, ax = plt.subplots(figsize=(15, 8.5), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 8.5)
    ax.axis('off')

    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']

    # Palette
    LIGHT_BLUE = '#e8f1f8'
    BORDER_BLUE = '#94b8db'

    LIGHT_ORANGE = '#fef0e7'
    BORDER_ORANGE = '#f5b58c'

    LIGHT_GREEN = '#eaf5ed'
    BORDER_GREEN = '#99cca6'

    LIGHT_PURPLE = '#f2edf8'
    BORDER_PURPLE = '#bfaee0'

    LIGHT_GRAY = '#f8f9fa'
    BORDER_GRAY = '#d6dbdf'
    LINE_GRAY = '#4a5568'

    def draw_stage(x, y, w, h, title, fill_color, border_color):
        box = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.08,rounding_size=0.15',
                             facecolor=fill_color, edgecolor=border_color, linewidth=1.2, zorder=1)
        ax.add_patch(box)
        ax.text(x + w/2, y + h - 0.28, title, ha='center', va='center',
                fontsize=10.5, weight='bold', color='#1a252f', zorder=2)

    def draw_card(x, y, w, h, text, subtitle='', fill_color='#ffffff', border_color='#cccccc', text_color='#111111'):
        box = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.05,rounding_size=0.08',
                             facecolor=fill_color, edgecolor=border_color, linewidth=0.9, zorder=3)
        ax.add_patch(box)
        if subtitle:
            ax.text(x + w/2, y + h/2 + 0.1, text, ha='center', va='center',
                    fontsize=8.5, weight='bold', color=text_color, zorder=4)
            ax.text(x + w/2, y + h/2 - 0.14, subtitle, ha='center', va='center',
                    fontsize=7.2, color='#555555', zorder=4)
        else:
            ax.text(x + w/2, y + h/2, text, ha='center', va='center',
                    fontsize=8.5, weight='bold', color=text_color, zorder=4)

    def draw_arrow(x1, y1, x2, y2, color=LINE_GRAY, lw=1.2):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='-|>', color=color, lw=lw,
                                    mutation_scale=11), zorder=5)

    # Title Header
    ax.text(7.5, 8.18, 'Tax-and-Brokerage-Adjusted Backtesting & Robustness Architecture',
            ha='center', va='center', fontsize=13.5, weight='bold', color='#111111')
    ax.text(7.5, 7.85, 'End-to-End Methodology: Natural Language Strategy Parsing → Execution → Point-in-Time Frictions → Statistical Inference',
            ha='center', va='center', fontsize=9.2, color='#444444')

    # Stage 1: Strategy Ingestion
    draw_stage(0.4, 1.2, 2.5, 6.2, '1. Strategy Ingestion', LIGHT_BLUE, BORDER_BLUE)
    draw_card(0.6, 5.7, 2.1, 0.95, 'Canonical Natural Language', '6 Strategy Descriptions', '#ffffff', BORDER_BLUE)
    draw_card(0.6, 4.3, 2.1, 0.95, 'Dual Parsing Engine', 'Rule-Based AST + LLM Code Gen', '#ffffff', BORDER_BLUE)
    draw_card(0.6, 2.9, 2.1, 0.95, 'Cryptographic Integrity', 'SHA-256 Hash Lock & Paraphrase Set', '#ffffff', BORDER_BLUE)
    draw_card(0.6, 1.5, 2.1, 0.95, 'Pure Python Strategy Module', 'Vectorized/Event Logic Verified', '#ffffff', BORDER_BLUE)

    draw_arrow(1.65, 5.7, 1.65, 5.25)
    draw_arrow(1.65, 4.3, 1.65, 3.85)
    draw_arrow(1.65, 2.9, 1.65, 2.45)

    # Stage 2: Market & Engine
    draw_stage(3.25, 1.2, 2.5, 6.2, '2. Market & Engine', LIGHT_GRAY, BORDER_GRAY)
    draw_card(3.45, 5.7, 2.1, 0.95, 'Global Universe Data', '25 Indices, 15 Economies (2011–2025)', '#ffffff', BORDER_GRAY)
    draw_card(3.45, 4.1, 2.1, 1.15, 'Signal Generation', 'Computed at Day t Close\n(No Lookahead Bias)', '#ffffff', BORDER_GRAY)
    draw_card(3.45, 2.3, 2.1, 1.35, 'Next-Day Open Execution', 'Executed at Day t+1 Open\nCash-Equity, Long-Only', '#ffffff', BORDER_GRAY)

    draw_arrow(2.7, 4.77, 3.45, 4.77)
    draw_arrow(4.5, 5.7, 4.5, 5.25)
    draw_arrow(4.5, 4.1, 4.5, 3.65)

    # Stage 3: Friction Modeling
    draw_stage(6.1, 1.2, 2.8, 6.2, '3. Friction Modeling', LIGHT_ORANGE, BORDER_ORANGE)
    draw_card(6.3, 6.1, 2.4, 0.65, 'Track 1: Gross Baseline', 'Frictionless Execution', '#ffffff', '#cccccc')
    draw_card(6.3, 4.9, 2.4, 0.85, 'Track 2: Net-of-Tax', 'Statutory CGT on Close Date\n(35 Historical Regimes)', '#ffffff', '#e67e22')
    draw_card(6.3, 3.6, 2.4, 0.95, 'Track 3: Net-Discount', 'Track 2 + Discount Commissions\nExchange Fees & Stamp Duties', '#ffffff', '#2980b9')
    draw_card(6.3, 2.35, 2.4, 0.9, 'Track 4: Net-Full-Service', 'Track 2 + Full-Service Schedule\n(Historical Broker Tiers)', '#ffffff', '#8e44ad')
    draw_card(6.3, 1.45, 2.4, 0.65, 'Benchmark: Buy-and-Hold', 'Passive Position Net of Costs', '#ffffff', '#27ae60')

    draw_arrow(5.55, 3.0, 6.3, 6.42, color='#666666')
    draw_arrow(5.55, 3.0, 6.3, 5.32, color='#666666')
    draw_arrow(5.55, 3.0, 6.3, 4.07, color='#666666')
    draw_arrow(5.55, 3.0, 6.3, 2.80, color='#666666')
    draw_arrow(5.55, 3.0, 6.3, 1.77, color='#666666')

    # Stage 4: Robustness Layer
    draw_stage(9.25, 1.2, 2.7, 6.2, '4. Robustness Layer', LIGHT_PURPLE, BORDER_PURPLE)
    draw_card(9.45, 6.0, 2.3, 0.75, 'IS / OOS Degradation', '2011–2018 (IS) vs 2019–2025 (OOS)', '#ffffff', BORDER_PURPLE)
    draw_card(9.45, 4.9, 2.3, 0.75, 'Monte Carlo Permutation', '1,000 Shuffles → P95 MaxDD', '#ffffff', BORDER_PURPLE)
    draw_card(9.45, 3.8, 2.3, 0.75, 'Bootstrap Resampling', '1,000 Iterations → 95% CAGR CI', '#ffffff', BORDER_PURPLE)
    draw_card(9.45, 2.65, 2.3, 0.85, 'Trade-Count Filter', 'n_IS >= 10 and n_OOS >= 10\n(Filters Thin-Sample Noise)', '#fef9e7', '#f39c12')
    draw_card(9.45, 1.45, 2.3, 0.85, 'Benjamini–Hochberg FDR', 'Controls False Discovery Rate\n(q = 0.10 across 50 tests)', '#fbeee6', '#e74c3c')

    draw_arrow(8.7, 4.07, 9.45, 4.07)
    draw_arrow(10.6, 6.0, 10.6, 5.65)
    draw_arrow(10.6, 4.9, 10.6, 4.55)
    draw_arrow(10.6, 3.8, 10.6, 3.50)
    draw_arrow(10.6, 2.65, 10.6, 2.30)

    # Stage 5: Outputs & Publications
    draw_stage(12.3, 1.2, 2.3, 6.2, '5. Reporting & Audit', LIGHT_GREEN, BORDER_GREEN)
    draw_card(12.45, 5.8, 2.0, 0.95, 'Cross-Market Summary', '750 Rows (150 Pairs × 5 Tracks)\nsummary_cross_country.csv', '#ffffff', BORDER_GREEN)
    draw_card(12.45, 4.35, 2.0, 0.95, 'Robustness Matrix', '150 Pairs IS/OOS & Bounds\nrobustness_summary.csv', '#ffffff', BORDER_GREEN)
    draw_card(12.45, 2.9, 2.0, 0.95, 'Significance & Threshold', 'fdr_corrected_significance.csv\nthreshold_sensitivity.csv', '#ffffff', BORDER_GREEN)
    draw_card(12.45, 1.45, 2.0, 0.95, 'Audited Publications', 'HTML / MD / JSON Reports\n300 DPI Standalone Figures', '#ffffff', BORDER_GREEN)

    draw_arrow(11.75, 4.07, 12.45, 4.07, color='#666666')
    draw_arrow(11.75, 1.87, 12.45, 2.50, color='#666666')
    draw_arrow(11.75, 6.0, 12.45, 5.80, color='#666666')

    plt.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Figure 4 saved to: {out_path.resolve()}")


def generate_figure_5_trade_distribution(out_path: Path):
    """Generate trade count box plot with strip plot and reference line."""
    setup_academic_style()
    rob = pd.read_csv("results/full_battery/robustness_summary.csv")
    rob["total_trades"] = rob["n_trades_is"] + rob["n_trades_oos"]

    fig, ax = plt.subplots(figsize=(9.2, 5.2), dpi=300)

    order = [
        "52-Week High Drawdown Dip Buyer",
        "50/200 SMA Crossover",
        "12-Month Momentum (Monthly Rebalance)",
        "Seasonal Halloween Rule (Nov-Apr)",
        "14-Day RSI Oscillator",
        "Bollinger Bands Breakout",
    ]

    short_labels = [
        "52-Week High\nDrawdown",
        "50/200 SMA\nCrossover",
        "12-Month\nMomentum",
        "Halloween\nRule",
        "14-Day RSI\nOscillator",
        "Bollinger Bands\nBreakout",
    ]

    palette = ["#9bb3c7", "#9bb3c7", "#9bb3c7", "#9bb3c7", "#2b5c8f", "#1f4e79"]

    # Boxplot
    sns.boxplot(
        data=rob,
        x="strategy",
        y="total_trades",
        order=order,
        hue="strategy",
        palette=palette,
        legend=False,
        width=0.48,
        linewidth=1.0,
        fliersize=0,
        ax=ax,
        zorder=2,
    )

    # Jittered points
    sns.stripplot(
        data=rob,
        x="strategy",
        y="total_trades",
        order=order,
        color="#222222",
        alpha=0.52,
        size=5.2,
        jitter=0.2,
        ax=ax,
        zorder=3,
    )

    # Reference line at n=10
    ax.axhline(
        y=10,
        color="#b02a37",
        linestyle="--",
        linewidth=1.3,
        zorder=1,
        label=r"Reporting threshold ($n = 10$)",
    )

    # Shaded region below n=10
    ax.axhspan(0, 10, color="#f8d7da", alpha=0.35, zorder=0, label=r"Sub-threshold zone ($n < 10$)")

    ax.set_title(r"Realized Trade Count Distribution by Strategy Family ($N = 150$ Pairs)", pad=12, fontsize=11, weight="bold")
    ax.set_xlabel("Strategy Family", fontsize=10, weight="medium")
    ax.set_ylabel(r"Total Realized Trades ($n_{\mathrm{IS}} + n_{\mathrm{OOS}}$, 2011–2025)", fontsize=10, weight="medium")

    ax.set_xticks(range(len(short_labels)))
    ax.set_xticklabels(short_labels, fontsize=9)

    ax.set_ylim(0, 75)
    ax.grid(True, axis="y", linestyle="--", alpha=0.6, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.legend(loc="upper left", fontsize=9, framealpha=0.92, edgecolor="#dddddd")

    plt.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Figure 5 saved to: {out_path.resolve()}")


def main():
    docs_fig_dir = Path("docs/figures")
    docs_fig_dir.mkdir(parents=True, exist_ok=True)

    fig3_path = docs_fig_dir / "fig3_universe_map.png"
    fig4_path = docs_fig_dir / "fig4_pipeline_architecture.png"
    fig5_path = docs_fig_dir / "fig5_trade_count_distribution.png"

    print("Generating Figure 3 (Universe Map)...")
    generate_figure_3_map(fig3_path)

    print("Generating Figure 4 (Pipeline Architecture)...")
    generate_figure_4_architecture(fig4_path)

    print("Generating Figure 5 (Trade Count Distribution)...")
    generate_figure_5_trade_distribution(fig5_path)

    # Print dimensions and file sizes
    print("\n=== Generated Figures Verification ===")
    for p in [fig3_path, fig4_path, fig5_path]:
        im = Image.open(p)
        size_kb = p.stat().st_size / 1024.0
        dpi = im.info.get("dpi", (None, None))
        print(f"{p.name}: {im.size[0]}x{im.size[1]} px, {size_kb:.1f} KB, DPI: {dpi}")


if __name__ == "__main__":
    main()
