import re


CITATION_PATTERN = re.compile(r"\[来源(\d+)\]")
CLOSING_HINTS = ("点击新闻列表", "查看新闻详情")


def split_factual_statements(answer: str) -> list[str]:
    statements = []
    normalized_answer = re.sub(
        r"([。！？!?])(\[来源\d+\])",
        r"\2\1",
        answer,
    )
    for fragment in re.split(r"[。！？!?\n]+", normalized_answer):
        statement = fragment.strip(" \t-*•0123456789.、：:")
        if len(statement) < 6 or any(hint in statement for hint in CLOSING_HINTS):
            continue
        statements.append(statement)
    return statements


def evaluate_citation_grounding(answer: str, reference_ids: list[str]) -> dict:
    valid_ids = set(reference_ids)
    cited_ids = [f"来源{number}" for number in CITATION_PATTERN.findall(answer)]
    invalid_ids = sorted(set(cited_ids) - valid_ids)
    statements = split_factual_statements(answer)
    supported_statements = sum(
        1
        for statement in statements
        if any(
            f"来源{number}" in valid_ids
            for number in CITATION_PATTERN.findall(statement)
        )
    )

    citation_validity = (
        sum(citation_id in valid_ids for citation_id in cited_ids) / len(cited_ids)
        if cited_ids
        else 0.0
    )
    statement_coverage = (
        supported_statements / len(statements) if statements else 0.0
    )

    return {
        "citation_validity": citation_validity,
        "statement_coverage": statement_coverage,
        "cited_ids": cited_ids,
        "invalid_citation_ids": invalid_ids,
        "statement_count": len(statements),
        "supported_statement_count": supported_statements,
        "passed": bool(statements)
        and citation_validity == 1.0
        and statement_coverage == 1.0,
    }
