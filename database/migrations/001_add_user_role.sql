USE news_app;

ALTER TABLE `user`
    ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user' COMMENT '权限角色' AFTER phone,
    ADD KEY idx_user_role (role);
