import json
import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1] / "toutiao_backend"
sys.path.insert(0, str(BACKEND_DIR))

from utils.faithfulness import evaluate_citation_grounding
from utils.prompts import SITE_NEWS_CHAT_PROMPT_VERSION, build_site_news_chat_messages


class PromptVersionTests(unittest.TestCase):
    def test_site_chat_prompt_is_versioned_and_contains_inputs(self):
        messages = build_site_news_chat_messages("有什么科技新闻", "[来源1]\n标题：示例")

        self.assertEqual(SITE_NEWS_CHAT_PROMPT_VERSION, "site-news-chat-v1")
        self.assertEqual([message["role"] for message in messages], ["system", "user"])
        self.assertIn("有什么科技新闻", messages[1]["content"])
        self.assertIn("[来源1]", messages[1]["content"])
        self.assertIn("每个事实或推荐都要使用 [来源N]", messages[1]["content"])


class CitationGroundingTests(unittest.TestCase):
    def test_valid_citations_cover_every_statement(self):
        result = evaluate_citation_grounding(
            "检索结果介绍了站内问答。[来源1]\n该功能支持来源追溯。[来源2]",
            ["来源1", "来源2"],
        )

        self.assertTrue(result["passed"])
        self.assertEqual(result["citation_validity"], 1.0)
        self.assertEqual(result["statement_coverage"], 1.0)

    def test_unknown_citation_fails(self):
        result = evaluate_citation_grounding(
            "该功能支持来源追溯。[来源3]",
            ["来源1", "来源2"],
        )

        self.assertFalse(result["passed"])
        self.assertEqual(result["invalid_citation_ids"], ["来源3"])

    def test_uncited_statement_fails(self):
        result = evaluate_citation_grounding(
            "该功能支持来源追溯。",
            ["来源1"],
        )

        self.assertFalse(result["passed"])
        self.assertEqual(result["statement_coverage"], 0.0)

    def test_evaluation_cases_are_valid(self):
        cases_path = Path(__file__).resolve().parents[1] / "evals" / "answer_faithfulness_cases.json"
        cases = json.loads(cases_path.read_text(encoding="utf-8"))

        self.assertEqual(len(cases), 4)
        self.assertTrue(all(isinstance(case.get("expected_pass"), bool) for case in cases))


if __name__ == "__main__":
    unittest.main()
