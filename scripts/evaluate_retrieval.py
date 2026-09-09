import argparse
import asyncio
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "toutiao_backend"
sys.path.insert(0, str(BACKEND_DIR))

from crud.ai import search_news_for_chat
from utils.retrieval import detect_category, extract_search_terms


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate retrieval Hit@K")
    parser.add_argument(
        "--cases",
        type=Path,
        default=PROJECT_ROOT / "evals" / "rag_retrieval_cases.json",
    )
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--min-hit-rate", type=float, default=0.75)
    return parser.parse_args()


async def evaluate(cases, top_k: int):
    from config.db_cond import AsyncSessionLocal

    hits = 0
    async with AsyncSessionLocal() as db:
        for case in cases:
            question = case["question"]
            rows = await search_news_for_chat(
                db,
                search_terms=extract_search_terms(question),
                category_name=detect_category(question),
                limit=top_k,
            )
            titles = [dict(row._mapping)["title"] for row in rows]
            matched = case["expected_title"] in titles
            hits += int(matched)
            print(f"{'PASS' if matched else 'FAIL'} | {question} | {titles}")

    return hits / len(cases) if cases else 0.0


async def main():
    args = parse_args()
    if args.top_k < 1:
        raise ValueError("--top-k must be greater than zero")

    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    hit_rate = await evaluate(cases, args.top_k)
    print(f"Hit@{args.top_k}: {hit_rate:.1%} ({len(cases)} cases)")
    return 0 if hit_rate >= args.min_hit_rate else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
