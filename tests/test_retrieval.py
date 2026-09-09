import json
import os
import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1] / "toutiao_backend"
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault("DATABASE_URL", "mysql+aiomysql://test:test@localhost/news_app")

from crud.ai import search_news_for_chat
from routers.ai import build_news_context
from utils.retrieval import detect_category, extract_search_terms


class FakeResult:
    def __init__(self, rows):
        self.rows = rows

    def fetchall(self):
        return self.rows


class FakeDb:
    def __init__(self, *row_sets):
        self.row_sets = list(row_sets)
        self.calls = []

    async def execute(self, statement, params):
        self.calls.append((str(statement), params))
        return FakeResult(self.row_sets.pop(0))


class RetrievalUtilityTests(unittest.TestCase):
    def test_category_and_search_terms_are_extracted(self):
        question = "最近科技类检索增强如何支持站内问答新闻"

        self.assertEqual(detect_category(question), "科技")
        terms = extract_search_terms(question)
        self.assertIn("检索", terms)
        self.assertIn("增强", terms)
        self.assertNotIn("新闻", terms)
        self.assertLessEqual(len(terms), 5)

    def test_context_uses_citation_labels(self):
        row = type("Row", (), {"_mapping": {"id": 1, "title": "示例标题"}})()
        context = build_news_context([row])

        self.assertIn("[来源1]", context)
        self.assertIn("新闻ID：1", context)

    def test_evaluation_cases_are_valid(self):
        cases_path = Path(__file__).resolve().parents[1] / "evals" / "rag_retrieval_cases.json"
        cases = json.loads(cases_path.read_text(encoding="utf-8"))

        self.assertEqual(len(cases), 4)
        self.assertTrue(all(case.get("question") for case in cases))
        self.assertTrue(all(case.get("expected_title") for case in cases))


class RetrievalQueryTests(unittest.IsolatedAsyncioTestCase):
    async def test_query_scores_fields_and_filters_category(self):
        expected_row = object()
        db = FakeDb([expected_row])

        rows = await search_news_for_chat(
            db,
            search_terms=["检索", "问答"],
            category_name="科技",
            limit=6,
        )

        sql, params = db.calls[0]
        self.assertEqual(rows, [expected_row])
        self.assertEqual(len(db.calls), 1)
        self.assertIn("THEN 5", sql)
        self.assertIn("THEN 3", sql)
        self.assertIn("THEN 1", sql)
        self.assertIn("c.name = :category_name", sql)
        self.assertIn("ORDER BY retrieval_score DESC", sql)
        self.assertNotIn("检索", sql)
        self.assertEqual(params["keyword_0"], "%检索%")
        self.assertEqual(params["category_name"], "科技")

    async def test_no_keyword_match_falls_back_to_category(self):
        category_row = object()
        db = FakeDb([], [category_row])

        rows = await search_news_for_chat(
            db,
            search_terms=["不存在的词"],
            category_name="科技",
            limit=6,
        )

        self.assertEqual(rows, [category_row])
        self.assertEqual(len(db.calls), 2)
        self.assertIn("c.name = :category_name", db.calls[1][0])

    async def test_empty_category_falls_back_to_recent_news(self):
        recent_row = object()
        db = FakeDb([], [recent_row])

        rows = await search_news_for_chat(
            db,
            search_terms=[],
            category_name="科技",
            limit=6,
        )

        self.assertEqual(rows, [recent_row])
        self.assertEqual(len(db.calls), 2)
        self.assertNotIn("WHERE c.name", db.calls[1][0])


if __name__ == "__main__":
    unittest.main()
