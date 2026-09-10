SET NAMES utf8mb4;

USE news_app;

INSERT INTO news_category (name, sort_order) VALUES
    ('头条', 10),
    ('社会', 20),
    ('国内', 30),
    ('国际', 40),
    ('娱乐', 50),
    ('体育', 60),
    ('科技', 70),
    ('财经', 80)
ON DUPLICATE KEY UPDATE sort_order = VALUES(sort_order);

INSERT INTO news (title, description, content, author, category_id, views, publish_time)
SELECT
    '[示例] 本地大模型新闻助手完成基础联调',
    '用于验证新闻列表、详情与站内 AI 问答流程。',
    '项目完成了新闻数据查询与本地大模型调用的基础联调。该内容仅用于本地开发环境演示，不代表真实新闻事件。',
    'Demo Bot',
    category.id,
    32,
    '2026-09-01 10:00:00'
FROM news_category AS category
WHERE category.name = '科技'
  AND NOT EXISTS (
      SELECT 1 FROM news WHERE title = '[示例] 本地大模型新闻助手完成基础联调'
  );

INSERT INTO news (title, description, content, author, category_id, views, publish_time)
SELECT
    '[示例] 检索增强让站内问答引用新闻内容',
    '演示基于新闻库检索结果生成回答的应用场景。',
    '系统先从新闻库筛选相关内容，再把结果交给模型生成回答，并在页面展示引用新闻。该内容仅用于本地开发环境演示。',
    'Demo Bot',
    category.id,
    25,
    '2026-09-02 11:30:00'
FROM news_category AS category
WHERE category.name = '科技'
  AND NOT EXISTS (
      SELECT 1 FROM news WHERE title = '[示例] 检索增强让站内问答引用新闻内容'
  );

INSERT INTO news (title, description, content, author, category_id, views, publish_time)
SELECT
    '[示例] 用户浏览与收藏支持个性化推荐',
    '用于验证历史记录、收藏和推荐接口。',
    '示例系统会汇总用户最近浏览和收藏的新闻，再提取兴趣关键词用于推荐。该内容仅用于本地开发环境演示。',
    'Demo Bot',
    category.id,
    18,
    '2026-09-03 09:15:00'
FROM news_category AS category
WHERE category.name = '头条'
  AND NOT EXISTS (
      SELECT 1 FROM news WHERE title = '[示例] 用户浏览与收藏支持个性化推荐'
  );

INSERT INTO news (title, description, content, author, category_id, views, publish_time)
SELECT
    '[示例] 新闻摘要接口输出简洁中文摘要',
    '用于验证单篇新闻的 AI 摘要功能。',
    '用户打开新闻详情后可以请求模型生成简短摘要。系统把新闻标题、分类、作者、简介和正文作为上下文。该内容仅用于本地开发环境演示。',
    'Demo Bot',
    category.id,
    12,
    '2026-09-04 14:20:00'
FROM news_category AS category
WHERE category.name = '国内'
  AND NOT EXISTS (
      SELECT 1 FROM news WHERE title = '[示例] 新闻摘要接口输出简洁中文摘要'
  );

INSERT INTO related_news (news_id, related_news_id)
SELECT source_news.id, target_news.id
FROM news AS source_news
JOIN news AS target_news
  ON target_news.title = '[示例] 检索增强让站内问答引用新闻内容'
WHERE source_news.title = '[示例] 本地大模型新闻助手完成基础联调'
ON DUPLICATE KEY UPDATE updated_at = CURRENT_TIMESTAMP;

INSERT INTO related_news (news_id, related_news_id)
SELECT source_news.id, target_news.id
FROM news AS source_news
JOIN news AS target_news
  ON target_news.title = '[示例] 新闻摘要接口输出简洁中文摘要'
WHERE source_news.title = '[示例] 检索增强让站内问答引用新闻内容'
ON DUPLICATE KEY UPDATE updated_at = CURRENT_TIMESTAMP;
