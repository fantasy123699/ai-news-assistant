USE news_app;

ALTER TABLE user_token
    MODIFY COLUMN token CHAR(64) NOT NULL COMMENT '登录令牌 SHA-256 摘要';

UPDATE user_token
SET token = SHA2(token, 256)
WHERE CHAR_LENGTH(token) = 32;
