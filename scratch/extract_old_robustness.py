import json
import pandas as pd

df_curr = pd.read_csv('results/full_battery/robustness_summary.csv')
curr_map = {(r['strategy'], r['country'], r['index']): r for _, r in df_curr.iterrows() if r['country'] in ['Japan', 'Germany']}

old_rows = {}
with open(r'C:\Users\HP\.gemini\antigravity-ide\brain\af6e970c-ca21-48cf-866b-2a4208643c95\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if 'robustness_summary.csv' in line:
            data = json.loads(line)
            for tc in data.get('tool_calls', []):
                args = tc.get('args', {})
                if 'robustness_summary.csv' in args.get('TargetFile', ''):
                    code = args.get('CodeContent', '')
                    for row_line in code.split('\n'):
                        parts = [p.strip() for p in row_line.split(',')]
                        if len(parts) >= 12 and parts[1] in ['Japan', 'Germany']:
                            old_rows[(parts[0], parts[1], parts[2])] = parts

print(f"Total old rows found: {len(old_rows)}")
deltas = []
for k, old in sorted(old_rows.items()):
    curr = curr_map.get(k)
    if curr is None:
        continue
    # columns: strategy,country,index,track,is_cagr,oos_cagr,degradation_ratio,mc_p95_maxdd,bootstrap_ci_low,bootstrap_ci_high,n_trades_is,n_trades_oos,guard_triggered
    old_is = float(old[4])
    old_oos = float(old[5])
    old_deg = float(old[6]) if old[6] != 'N/A' else 'N/A'
    old_mc = float(old[7])
    old_ci_l = float(old[8])
    old_ci_h = float(old[9])

    new_is = float(curr['is_cagr'])
    new_oos = float(curr['oos_cagr'])
    new_deg = float(curr['degradation_ratio']) if curr['degradation_ratio'] != 'N/A' else 'N/A'
    new_mc = float(curr['mc_p95_maxdd'])
    new_ci_l = float(curr['bootstrap_ci_low'])
    new_ci_h = float(curr['bootstrap_ci_high'])

    diffs = {}
    if abs(old_is - new_is) > 1e-4:
        diffs['is_cagr'] = (old_is, new_is)
    if abs(old_oos - new_oos) > 1e-4:
        diffs['oos_cagr'] = (old_oos, new_oos)
    if old_deg != 'N/A' and new_deg != 'N/A' and abs(old_deg - new_deg) > 1e-4:
        diffs['degradation_ratio'] = (old_deg, new_deg)
    if abs(old_mc - new_mc) > 1e-4:
        diffs['mc_p95_maxdd'] = (old_mc, new_mc)
    if abs(old_ci_l - new_ci_l) > 1e-4:
        diffs['bootstrap_ci_low'] = (old_ci_l, new_ci_l)
    if abs(old_ci_h - new_ci_h) > 1e-4:
        diffs['bootstrap_ci_high'] = (old_ci_h, new_ci_h)

    if diffs:
        deltas.append((k, diffs))

print(f"Robustness rows with changes: {len(deltas)}")
for k, diffs in deltas:
    print(f"\n{k}:")
    for metric, (o, n) in diffs.items():
        print(f"  {metric}: {o} -> {n} (delta: {n - o:+.6f})")
