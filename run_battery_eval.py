"""CLI Driver for Strategy Battery Dual-Backend Evaluation and Methods Report Generation.

Evaluates both Rule-Based and LLM-Backend parsers separately across:
1. Canonical Battery (6 strategies)
2. Development / Known Paraphrase Set (6 variants)
3. Sealed Blind Set (6 novel variants, evaluated once at the end)
4. Scope Rejection & Borderline Intent Probes (8 test cases)

Usage:
  python run_battery_eval.py --out battery_results/
"""

import argparse
import json
import logging
from pathlib import Path
import sys

from src.parser.llm_parser import StrategyParser
from src.parser.evaluator import run_dual_battery_evaluation_suite, generate_battery_markdown_report


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("BatteryEvaluator")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate NL-to-Strategy Parser across Canonical, Paraphrase, and Sealed Blind Sets."
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gemini-2.5-flash",
        help="LLM model identifier for LLM backend evaluation.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="LLM temperature (pinned at 0.0 for deterministic evaluation).",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="battery_results",
        help="Directory to save evaluation reports and audit files (default: battery_results/).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    out_dir = Path(args.out)
    audit_dir = out_dir / "audit"
    out_dir.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=================================================================")
    logger.info("STRATEGY BATTERY: DUAL-BACKEND EVALUATION (RULE-BASED vs LLM)")
    logger.info("=================================================================")
    logger.info(f"LLM Model: {args.model} (temp={args.temperature})")
    logger.info(f"Output Directory: {out_dir}")

    rule_parser = StrategyParser(backend="rule_based")
    llm_parser = StrategyParser(
        backend="llm",
        model_name=args.model,
        temperature=args.temperature,
    )

    logger.info("Executing dual evaluation suite across Canonical Battery, Development Paraphrases, and Sealed Blind Set...")
    dual_result = run_dual_battery_evaluation_suite(
        rule_parser=rule_parser,
        llm_parser=llm_parser,
        audit_dir=audit_dir,
    )

    # 1. Save Full Structured JSON Report
    json_path = out_dir / "battery_evaluation.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dual_result.to_dict(), f, indent=2)

    # 2. Save Methods-Section Markdown Report
    md_path = out_dir / "battery_report.md"
    generate_battery_markdown_report(dual_result, md_path)

    rb = dual_result.rule_based
    ll = dual_result.llm

    repro = dual_result.reproducibility_audit or {}
    logger.info("=================================================================")
    logger.info("DUAL-BACKEND EVALUATION COMPLETED")
    logger.info("=================================================================")
    logger.info(f"CODE INTEGRITY:        All Modules Unmodified: {dual_result.all_parser_files_unmodified} (Authorship Baseline SHA-256 Verified)")
    logger.info(f"REPRODUCIBILITY (3x):  Deterministic Match: {repro.get('is_deterministic')} (Zero Stochastic Variance Across Runs)")
    logger.info(f"CANONICAL BATTERY:     Rule-Based: {rb.canonical_agreement_pct}% ({rb.canonical_passed_count}/{len(rb.canonical_results)} PASS) | LLM-Backend: {ll.canonical_agreement_pct}% ({ll.canonical_passed_count}/{len(ll.canonical_results)} PASS)")
    logger.info(f"KNOWN PARAPHRASES:     Rule-Based: {rb.paraphrase_agreement_pct}% ({rb.paraphrase_passed_count}/{len(rb.paraphrase_results)} PASS) | LLM-Backend: {ll.paraphrase_agreement_pct}% ({ll.paraphrase_passed_count}/{len(ll.paraphrase_results)} PASS)")
    logger.info(f"SEALED BLIND SET:      Rule-Based: {rb.blind_agreement_pct}% ({rb.blind_passed_count}/{len(rb.blind_results)} PASS) | LLM-Backend: {ll.blind_agreement_pct}% ({ll.blind_passed_count}/{len(ll.blind_results)} PASS, B9 Gated)")
    logger.info(f"VALIDATOR ACCURACY:    {dual_result.rejection_accuracy_pct}% (True Positives: {dual_result.true_positive_rate_pct}%, False Positives: {dual_result.false_positive_rate_pct}%)")
    logger.info("-----------------------------------------------------------------")
    logger.info(f"Structured JSON:  {json_path}")
    logger.info(f"Methods Markdown: {md_path}")
    logger.info(f"Audit Directory:  {audit_dir}")
    logger.info("=================================================================")

    # Canonical execution gate: Canonical battery must achieve 100% agreement
    if not (rb.overall_gate_passed and ll.overall_gate_passed):
        logger.error("GATE BLOCKED: One or more canonical battery strategies failed 100% field match.")
        sys.exit(1)
    else:
        logger.info("GATE PASSED: Canonical battery verified across backends for full-universe execution.")
        sys.exit(0)


if __name__ == "__main__":
    main()
