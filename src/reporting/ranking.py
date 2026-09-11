"""Ranking and exclusion filtering engine."""

from typing import List, Tuple
from src.engine.models import BacktestResult


def partition_and_rank_results(
    results: List[BacktestResult],
) -> Tuple[List[BacktestResult], List[BacktestResult], List[BacktestResult]]:
    """
    Partition results into:
    1. primary_ranked: Qualified indices sorted by Net-Discount CAGR descending
    2. calmar_ranked: Qualified indices sorted by Calmar Ratio (on Net-Discount track) descending
    3. excluded: Indices excluded due to late start (> 2011-01-01) or < 5 trades
    """
    qualified: List[BacktestResult] = []
    excluded: List[BacktestResult] = []

    for r in results:
        if r.exclusion_reason:
            excluded.append(r)
        else:
            qualified.append(r)

    # Primary ranking: Net-Discount CAGR descending
    primary_ranked = sorted(
        qualified,
        key=lambda x: (
            x.net_discount_metrics.cagr if x.net_discount_metrics else -999.0
        ),
        reverse=True,
    )

    # Secondary ranking: Calmar ratio on Net-Discount track descending
    calmar_ranked = sorted(
        qualified,
        key=lambda x: (
            x.net_discount_metrics.calmar_ratio if x.net_discount_metrics else -999.0
        ),
        reverse=True,
    )

    # Sort excluded by country, then index name
    excluded.sort(key=lambda x: (x.country, x.index_name))

    return primary_ranked, calmar_ranked, excluded
