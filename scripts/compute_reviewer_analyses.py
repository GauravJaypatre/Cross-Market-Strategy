"""Script to perform the three reviewer analyses:
1. Trade-count threshold sensitivity across T in [5, 8, 10, 12, 15]
2. Dataset confidence tier breakdown for tax and brokerage datasets
3. Slippage sensitivity (10 bps and 25 bps) on the 4 nominal outperformer pairs
"""

import os
import sys
import pandas as pd
import numpy as np

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# -------------------------------------------------------------
# 1. OBJECTION 2: Trade-count threshold sensitivity
# -------------------------------------------------------------
rob = pd.read_csv('results/full_battery/robustness_summary.csv')
summ = pd.read_csv('results/full_battery/summary_cross_country.csv')

net_disc = summ[summ['track'] == 'Net-Discount'].rename(columns={'CAGR': 'net_discount_cagr'})
bh = summ[summ['track'] == 'Buy-and-Hold'].rename(columns={'CAGR': 'bh_cagr'})

merged = pd.merge(rob, net_disc[['strategy', 'country', 'index', 'net_discount_cagr']], on=['strategy', 'country', 'index'])
merged = pd.merge(merged, bh[['strategy', 'country', 'index', 'bh_cagr']], on=['strategy', 'country', 'index'])

thresholds = [5, 8, 10, 12, 15]
rows = []

for T in thresholds:
    subset = merged[(merged['n_trades_is'] >= T) & (merged['n_trades_oos'] >= T)]
    n_qual = len(subset)
    strategies = sorted(subset['strategy'].unique().tolist())
    strategies_str = "; ".join(strategies)
    underperform_count = (subset['net_discount_cagr'] < subset['bh_cagr']).sum()
    pct_underperform = round((underperform_count / n_qual * 100), 2) if n_qual > 0 else 0.0
    
    rows.append({
        'threshold': T,
        'n_qualifying_pairs': n_qual,
        'strategies_represented': strategies_str,
        'pct_underperform': pct_underperform
    })

df_threshold = pd.DataFrame(rows)
output_path = 'results/full_battery/threshold_sensitivity.csv'
df_threshold.to_csv(output_path, index=False)
print(f"Written threshold sensitivity to {output_path}:")
print(df_threshold.to_string(index=False))
print()

# -------------------------------------------------------------
# 2. OBJECTION 4: Dataset confidence tier breakdown
# -------------------------------------------------------------
tax = pd.read_csv('tax_dataset.csv')
brok = pd.read_csv('brokerage_dataset.csv')

tax_counts = tax['confidence'].value_counts()
brok_counts = brok['confidence'].value_counts()

all_tiers = sorted(list(set(tax_counts.index.tolist() + brok_counts.index.tolist())))
total_rows = len(tax) + len(brok)

conf_rows = []
for tier in all_tiers:
    tc = int(tax_counts.get(tier, 0))
    bc = int(brok_counts.get(tier, 0))
    tot = tc + bc
    pct = round((tot / total_rows) * 100, 2)
    conf_rows.append({
        'tier': tier,
        'tax_dataset_count': tc,
        'brokerage_dataset_count': bc,
        'pct_of_total': pct
    })

# Add total row
conf_rows.append({
    'tier': 'Total',
    'tax_dataset_count': len(tax),
    'brokerage_dataset_count': len(brok),
    'pct_of_total': 100.00
})

df_conf = pd.DataFrame(conf_rows)
print("Dataset Confidence Tier Breakdown:")
print(df_conf.to_string(index=False))
print()

# -------------------------------------------------------------
# 3. OBJECTION 5: Slippage sensitivity on 4 outperformer pairs
# -------------------------------------------------------------
pairs = [
    ('14-Day RSI Oscillator', 'United Kingdom', 'FTSE 100'),
    ('14-Day RSI Oscillator', 'Italy', 'FTSE MIB'),
    ('Bollinger Bands Breakout', 'China', 'Shenzhen Component'),
    ('Bollinger Bands Breakout', 'China', 'Shanghai Composite')
]

slip_rows = []
for s, c, idx in pairs:
    sub_summ = summ[(summ['strategy'] == s) & (summ['country'] == c) & (summ['index'] == idx)]
    sub_rob = rob[(rob['strategy'] == s) & (rob['country'] == c) & (rob['index'] == idx)].iloc[0]
    
    bh_cagr = sub_summ[sub_summ['track'] == 'Buy-and-Hold']['CAGR'].values[0]
    orig_cagr = sub_summ[sub_summ['track'] == 'Net-Discount']['CAGR'].values[0]
    n_is = int(sub_rob['n_trades_is'])
    n_oos = int(sub_rob['n_trades_oos'])
    n_trades = n_is + n_oos
    
    # Exact calendar span:
    years = 5475 / 365.25 if idx == 'FTSE MIB' else 5474 / 365.25
    
    # 10 bps compounding
    s10 = 10 / 10000.0
    cagr_10bps = (1 + orig_cagr) * ((1 - s10) ** (n_trades / years)) - 1
    exceeds_10bps = cagr_10bps > bh_cagr
    
    # 25 bps compounding
    s25 = 25 / 10000.0
    cagr_25bps = (1 + orig_cagr) * ((1 - s25) ** (n_trades / years)) - 1
    exceeds_25bps = cagr_25bps > bh_cagr
    
    # Linear alternative for sensitivity reference
    cagr_10bps_lin = orig_cagr - (n_trades * s10) / years
    cagr_25bps_lin = orig_cagr - (n_trades * s25) / years
    
    slip_rows.append({
        'strategy': s,
        'country': c,
        'index': idx,
        'realized_trades': n_trades,
        'bh_cagr': bh_cagr,
        'original_net_discount_cagr': orig_cagr,
        'cagr_10bps_slippage': cagr_10bps,
        'exceeds_bh_at_10bps': exceeds_10bps,
        'cagr_25bps_slippage': cagr_25bps,
        'exceeds_bh_at_25bps': exceeds_25bps,
        'cagr_10bps_lin': cagr_10bps_lin,
        'cagr_25bps_lin': cagr_25bps_lin,
    })

df_slip = pd.DataFrame(slip_rows)
print("Slippage Sensitivity on 4 Nominal Outperformers:")
print(df_slip[['strategy', 'country', 'index', 'realized_trades', 'bh_cagr', 'original_net_discount_cagr', 'cagr_10bps_slippage', 'exceeds_bh_at_10bps', 'cagr_25bps_slippage', 'exceeds_bh_at_25bps']].to_string(index=False))
