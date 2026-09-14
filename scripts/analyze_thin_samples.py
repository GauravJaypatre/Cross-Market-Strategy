import pandas as pd

df_rob = pd.read_csv("results/full_battery/robustness_summary.csv")
df_lead = pd.read_csv("results/full_battery/leaderboard.csv")

oos_thin = df_rob[df_rob["n_trades_oos"] <= 5]
is_thin = df_rob[df_rob["n_trades_is"] <= 5]

with open("scripts/thin_samples_output.txt", "w", encoding="utf-8") as f:
    f.write(f"COUNT_OOS_THIN: {len(oos_thin)}\n")
    for i, (_, r) in enumerate(oos_thin.iterrows(), 1):
        f.write(f"{i}. {r['strategy']} | {r['country']} | {r['index']} | n_trades_is={r['n_trades_is']} | n_trades_oos={r['n_trades_oos']}\n")

    f.write(f"\nCOUNT_IS_THIN: {len(is_thin)}\n")
    for i, (_, r) in enumerate(is_thin.iterrows(), 1):
        f.write(f"{i}. {r['strategy']} | {r['country']} | {r['index']} | n_trades_is={r['n_trades_is']} | n_trades_oos={r['n_trades_oos']}\n")

    leader_winners = []
    for _, row in df_lead.iterrows():
        leader_winners.append({"strategy": row["strategy"], "winner": row["best_by_cagr_index"], "win_type": "best_by_cagr", "track": row["track"]})
        leader_winners.append({"strategy": row["strategy"], "winner": row["best_by_calmar_index"], "win_type": "best_by_calmar", "track": row["track"]})

    thin_union = df_rob[(df_rob["n_trades_oos"] <= 5) | (df_rob["n_trades_is"] <= 5)]
    f.write(f"\nCOUNT_THIN_UNION: {len(thin_union)}\n")

    matches = []
    for _, r in thin_union.iterrows():
        strat = r["strategy"]
        pair_str = f"{r['country']} - {r['index']}"
        for lw in leader_winners:
            if strat == lw["strategy"] and pair_str == lw["winner"]:
                matches.append({
                    "strategy": strat,
                    "country": r["country"],
                    "index": r["index"],
                    "track": lw["track"],
                    "win_type": lw["win_type"],
                    "n_trades_is": r["n_trades_is"],
                    "n_trades_oos": r["n_trades_oos"],
                    "is_oos_thin": r["n_trades_oos"] <= 5,
                    "is_is_thin": r["n_trades_is"] <= 5,
                })

    df_matches = pd.DataFrame(matches)
    unique_pairs = df_matches[["strategy", "country", "index", "n_trades_is", "n_trades_oos", "is_is_thin", "is_oos_thin"]].drop_duplicates()
    f.write(f"COUNT_LEADERBOARD_MATCHES: {len(unique_pairs)}\n")
    for i, (_, u) in enumerate(unique_pairs.iterrows(), 1):
        winning_contexts = df_matches[(df_matches["strategy"] == u["strategy"]) & (df_matches["index"] == u["index"])]
        contexts_str = "; ".join([f"{row['win_type']} on {row['track']}" for _, row in winning_contexts.iterrows()])
        tag = []
        if u["is_is_thin"]: tag.append("n_trades_is <= 5")
        if u["is_oos_thin"]: tag.append("n_trades_oos <= 5")
        tag_str = ", ".join(tag)
        f.write(f"{i}. {u['strategy']} | {u['country']} - {u['index']} | IS: {u['n_trades_is']}, OOS: {u['n_trades_oos']} ({tag_str}) | Titles won: {contexts_str}\n")
