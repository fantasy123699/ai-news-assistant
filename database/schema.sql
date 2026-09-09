CREATE DATABASE IF NOT EXISTS news_app
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE news_app;

CREATE TABLE IF NOT EXISTS news_category (
    id INT NOT NULL AUTO_INCREMENT COMMENT '分类ID',
    name VARCHAR(50) NOT NULL COMMENT '分类名称',
    sort_order INT NOT NULL DEFAULT 0 COMMENT '排序顺序',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_news_category_name (name),
    KEY idx_news_category_sort (sort_order, id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `user` (
    id INT NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(50) NOT NULL COMMENT '登录名',
    password VARCHAR(255) NOT NULL COMMENT '密码哈希',
    nickname VARCHAR(50) NULL COMMENT '昵称',
    avatar VARCHAR(255) NULL COMMENT '头像URL',
    gender VARCHAR(10) NOT NULL DEFAULT 'unknown' COMMENT '性别',
    bio VARCHAR(500) NULL COMMENT '个人简介',
    phone VARCHAR(20) NULL COMMENT '手机号',
    role VARCHAR(20) NOT NULL DEFAULT 'user' COMMENT '权限角色',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_user_username (username),
    UNIQUE KEY uk_user_phone (phone),
    KEY idx_user_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS news (
    id INT NOT NULL AUTO_INCREMENT COMMENT '新闻ID',
    title VARCHAR(255) NOT NULL COMMENT '新闻标题',
    description VARCHAR(500) NULL COMMENT '新闻简介',
    content TEXT NOT NULL COMMENT '新闻内容',
    image VARCHAR(255) NULL COMMENT '封面图片URL',
    author VARCHAR(50) NULL COMMENT '作者',
    category_id INT NOT NULL COMMENT '分类ID',
    views INT NOT NULL DEFAULT 0 COMMENT '浏览量',
    publish_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    KEY idx_news_category_publish (category_id, publish_time, id),
    KEY idx_news_publish_views (publish_time, views, id),
    CONSTRAINT fk_news_category
        FOREIGN KEY (category_id) REFERENCES news_category (id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS related_news (
    id INT NOT NULL AUTO_INCREMENT COMMENT '关联ID',
    news_id INT NOT NULL COMMENT '新闻ID',
    related_news_id INT NOT NULL COMMENT '相关新闻ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY news_related_unique (news_id, related_news_id),
    KEY idx_related_news_target (related_news_id),
    CONSTRAINT fk_related_news_source
        FOREIGN KEY (news_id) REFERENCES news (id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_related_news_target
        FOREIGN KEY (related_news_id) REFERENCES news (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS user_token (
    id INT NOT NULL AUTO_INCREMENT COMMENT '令牌ID',
    user_id INT NOT NULL COMMENT '用户ID',
    token CHAR(32) NOT NULL COMMENT '登录令牌',
    expires_at DATETIME NOT NULL COMMENT '过期时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_user_token_token (token),
    KEY idx_user_token_user_expiry (user_id, expires_at),
    KEY idx_user_token_expiry (expires_at),
    CONSTRAINT fk_user_token_user
        FOREIGN KEY (user_id) REFERENCES `user` (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS favorite (
    id INT NOT NULL AUTO_INCREMENT COMMENT '收藏ID',
    user_id INT NOT NULL COMMENT '用户ID',
    news_id INT NOT NULL COMMENT '新闻ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_favorite_user_news (user_id, news_id),
    KEY idx_favorite_user_created (user_id, created_at, id),
    KEY idx_favorite_news (news_id),
    CONSTRAINT fk_favorite_user
        FOREIGN KEY (user_id) REFERENCES `user` (id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_favorite_news
        FOREIGN KEY (news_id) REFERENCES news (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS history (
    id INT NOT NULL AUTO_INCREMENT COMMENT '历史记录ID',
    user_id INT NOT NULL COMMENT '用户ID',
    news_id INT NOT NULL COMMENT '新闻ID',
    view_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '浏览时间',
    PRIMARY KEY (id),
    KEY idx_history_user_view (user_id, view_time, id),
    KEY idx_history_news (news_id),
    CONSTRAINT fk_history_user
        FOREIGN KEY (user_id) REFERENCES `user` (id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_history_news
        FOREIGN KEY (news_id) REFERENCES news (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ai_chat (
    id INT NOT NULL AUTO_INCREMENT COMMENT '对话ID',
    user_id INT NOT NULL COMMENT '用户ID',
    message TEXT NOT NULL COMMENT '用户消息',
    response TEXT NOT NULL COMMENT '模型回复',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_ai_chat_user_created (user_id, created_at, id),
    CONSTRAINT fk_ai_chat_user
        FOREIGN KEY (user_id) REFERENCES `user` (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
