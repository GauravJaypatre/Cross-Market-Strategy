import json
import sys

with open("results_run1/report.json", encoding="utf-8") as f:
    r1 = json.load(f)
with open("results_run2/report.json", encoding="utf-8") as f:
    r2 = json.load(f)

# Keys expected to be dynamic execution timestamps:
DYNAMIC_KEYS = {"timestamp_utc", "loaded_at_utc", "retrieval_timestamp_utc"}

def strip_dynamic(obj):
    if isinstance(obj, dict):
        return {k: strip_dynamic(v) for k, v in obj.items() if k not in DYNAMIC_KEYS}
    elif isinstance(obj, list):
        return [strip_dynamic(item) for item in obj]
    return obj

clean_r1 = strip_dynamic(r1)
clean_r2 = strip_dynamic(r2)

print("Deterministic equality check (excluding execution timestamps):", clean_r1 == clean_r2)

diffs = []
def find_diffs(o1, o2, path=""):
    if type(o1) != type(o2):
        diffs.append(f"{path}: type mismatch {type(o1)} vs {type(o2)}")
        return
    if isinstance(o1, dict):
        all_keys = set(o1.keys()) | set(o2.keys())
        for k in all_keys:
            if k not in o1:
                diffs.append(f"{path}.{k}: missing in run 1")
            elif k not in o2:
                diffs.append(f"{path}.{k}: missing in run 2")
            else:
                find_diffs(o1[k], o2[k], f"{path}.{k}")
    elif isinstance(o1, list):
        if len(o1) != len(o2):
            diffs.append(f"{path}: length mismatch {len(o1)} vs {len(o2)}")
        else:
            for i, (i1, i2) in enumerate(zip(o1, o2)):
                find_diffs(i1, i2, f"{path}[{i}]")
    else:
        if o1 != o2:
            diffs.append(f"{path}: {o1} != {o2}")

find_diffs(clean_r1, clean_r2)

if diffs:
    print(f"Found {len(diffs)} differences:")
    for d in diffs:
        print(" ", d)
else:
    print("SUCCESS: 0 differences found across all 5 indices, all tracks, all CI bounds, and all Monte Carlo drawdowns!")

print("\nDetailed Robustness Metrics Comparison across both runs:")
for item in r1["primary_ranking_cagr"]:
    country = item["country"]
    idx = item["index_name"]
    rob1 = item["robustness"]
    # find in r2
    item2 = next(x for x in r2["primary_ranking_cagr"] if x["country"] == country)
    rob2 = item2["robustness"]
    
    print(f"\n[{country} - {idx}]")
    print(f"  Run 1 95% Bootstrap CI: [{rob1['cagr_ci_lower']*100:.4f}%, {rob1['cagr_ci_upper']*100:.4f}%]")
    print(f"  Run 2 95% Bootstrap CI: [{rob2['cagr_ci_lower']*100:.4f}%, {rob2['cagr_ci_upper']*100:.4f}%]")
    print(f"  CI Match: {rob1['cagr_ci_lower'] == rob2['cagr_ci_lower'] and rob1['cagr_ci_upper'] == rob2['cagr_ci_upper']}")
    print(f"  Run 1 MC P95 Worst MaxDD: {rob1['mc_p95_max_drawdown']*100:.4f}%")
    print(f"  Run 2 MC P95 Worst MaxDD: {rob2['mc_p95_max_drawdown']*100:.4f}%")
    print(f"  MC MaxDD Match: {rob1['mc_p95_max_drawdown'] == rob2['mc_p95_max_drawdown']}")
