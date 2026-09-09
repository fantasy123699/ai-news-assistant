import logging

import jieba
import jieba.analyse


jieba.setLogLevel(logging.WARNING)

CATEGORY_NAMES = ("头条", "社会", "国内", "国际", "娱乐", "体育", "科技", "财经")
STOP_TERMS = {
    "一个",
    "一下",
    "了解",
    "什么",
    "介绍",
    "关于",
    "哪些",
    "如何",
    "怎样",
    "帮忙",
    "帮我",
    "推荐",
    "新闻",
    "最近",
    "最新",
    "相关",
    "请问",
}


def detect_category(question: str) -> str | None:
    for name in CATEGORY_NAMES:
        if name in question:
            return name
    return None


def extract_search_terms(question: str, limit: int = 5) -> list[str]:
    category_name = detect_category(question)
    cleaned_question = question.replace(category_name, " ") if category_name else question
    candidates = jieba.analyse.extract_tags(
        cleaned_question,
        topK=limit * 2,
        withWeight=False,
    )

    terms = []
    for candidate in candidates:
        term = candidate.strip().lower()
        if len(term) < 2 or term in STOP_TERMS or term in terms:
            continue
        terms.append(term)
        if len(terms) == limit:
            break

    return terms
