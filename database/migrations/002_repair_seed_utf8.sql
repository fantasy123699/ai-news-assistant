SET NAMES utf8mb4;

USE news_app;

START TRANSACTION;

UPDATE news_category
SET name = CONVERT(CAST(CONVERT(name USING latin1) AS BINARY) USING utf8mb4)
WHERE sort_order IN (10, 20, 30, 40, 50, 60, 70, 80)
  AND HEX(name) LIKE 'C3%';

UPDATE news
SET title = CONVERT(CAST(CONVERT(title USING latin1) AS BINARY) USING utf8mb4),
    description = CONVERT(CAST(CONVERT(description USING latin1) AS BINARY) USING utf8mb4),
    content = CONVERT(CAST(CONVERT(content USING latin1) AS BINARY) USING utf8mb4)
WHERE author = 'Demo Bot'
  AND HEX(title) LIKE '5BC3%';

COMMIT;
