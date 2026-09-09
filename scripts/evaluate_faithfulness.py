import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "toutiao_backend"
sys.path.insert(0, str(BACKEND_DIR))

from utils.faithfulness import evaluate_citation_grounding


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate answer citation grounding")
    parser.add_argument(
        "--cases",
        type=Path,
        default=PROJECT_ROOT / "evals" / "answer_faithfulness_cases.json",
    )
    parser.add_argument("--min-accuracy", type=float, default=1.0)
    return parser.parse_args()


def main():
    args = parse_args()
    if not 0.0 <= args.min_accuracy <= 1.0:
        raise ValueError("--min-accuracy must be between 0 and 1")

    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    correct = 0
    for case in cases:
        result = evaluate_citation_grounding(case["answer"], case["reference_ids"])
        matched = result["passed"] == case["expected_pass"]
        correct += int(matched)
        print(
            f"{'PASS' if matched else 'FAIL'} | {case['name']} | "
            f"validity={result['citation_validity']:.1%} | "
            f"coverage={result['statement_coverage']:.1%}"
        )

    accuracy = correct / len(cases) if cases else 0.0
    print(f"Fixture accuracy: {accuracy:.1%} ({correct}/{len(cases)})")
    return 0 if accuracy >= args.min_accuracy else 1


if __name__ == "__main__":
    raise SystemExit(main())
