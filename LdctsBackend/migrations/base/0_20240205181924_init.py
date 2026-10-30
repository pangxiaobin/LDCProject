from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `dictserverdata` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `create_time` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL  COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `url_path` VARCHAR(128) NOT NULL UNIQUE,
    `dict_data` JSON
) CHARACTER SET utf8mb4 COMMENT='字典缓存服务';
CREATE TABLE IF NOT EXISTS `study` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `create_time` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL  COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `study_instance_id` VARCHAR(256) NOT NULL UNIQUE,
    `patient_age` VARCHAR(6),
    `patient_gender` VARCHAR(20),
    `save_time` VARCHAR(30)   COMMENT '保存时间',
    `study_time` VARCHAR(128)   COMMENT '检查时间',
    `study_ai_result` JSON   COMMENT 'ai 结果',
    `ai_status` VARCHAR(24)   COMMENT 'ai状态',
    KEY `idx_study_study_i_a82a16` (`study_instance_id`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `series` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `create_time` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `series_filename` VARCHAR(128) NOT NULL UNIQUE,
    `recon` VARCHAR(64)   COMMENT 'recon',
    `instance_num` INT NOT NULL  COMMENT '影像数据量',
    `image_orientation_patient` VARCHAR(64) NOT NULL,
    `image_position_patient` VARCHAR(64) NOT NULL,
    `pixel_spacing` VARCHAR(64) NOT NULL,
    `study_id` BIGINT NOT NULL,
    CONSTRAINT `fk_series_study_96394a97` FOREIGN KEY (`study_id`) REFERENCES `study` (`id`) ON DELETE CASCADE,
    KEY `idx_series_series__581677` (`series_filename`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `user` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `create_time` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL  COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `username` VARCHAR(32) NOT NULL UNIQUE COMMENT '账号',
    `password` VARCHAR(128) NOT NULL  COMMENT '密码',
    `last_login` DATETIME(6)   COMMENT '最近登录时间',
    `is_active` BOOL NOT NULL  COMMENT '状态' DEFAULT 1,
    `role` VARCHAR(1) NOT NULL  COMMENT '角色 ADMIN--1 NORMAL--2 FIRST_AUDIT--3 LAST_AUDIT--4' DEFAULT '2',
    KEY `idx_user_usernam_9987ab` (`username`)
) CHARACTER SET utf8mb4 COMMENT='用户';
CREATE TABLE IF NOT EXISTS `seriesauditlog` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `create_time` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL  COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `ai_audit` JSON   COMMENT 'ai结果',
    `user_audit` JSON   COMMENT '用户标注结果',
    `series_id` BIGINT NOT NULL,
    `user_id` BIGINT NOT NULL,
    CONSTRAINT `fk_seriesau_series_693d33ec` FOREIGN KEY (`series_id`) REFERENCES `series` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_seriesau_user_e0c5464c` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='序列审核记录';
CREATE TABLE IF NOT EXISTS `studyaudit` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `create_time` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL  COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `check_status` VARCHAR(30)   COMMENT '用户审核状态: audit_not_audit--audit_not_audit audit_in_first_round--audit_in_first_round audit_finish_first_round--audit_finish_first_round audit_in_final_round--audit_in_final_round audit_finish_final_round--audit_finish_final_round',
    `first_status` VARCHAR(64)   COMMENT '一审状态： ai_correct--aicomment_ai_correct ai_not_correct--aicomment_ai_not_correct',
    `first_mark` LONGTEXT,
    `first_check_time` DATETIME(6),
    `first_classifier` JSON   COMMENT 'first_classifier',
    `first_report` JSON   COMMENT 'first_report',
    `last_status` VARCHAR(64)   COMMENT '二审状态：auditor_correct--auditorcomment_first_auditor_correct auditor_not_correct--auditorcomment_first_auditor_not_correct',
    `last_status_ai` VARCHAR(64)   COMMENT '二审ai审状态： ai_correct--aicomment_ai_correct ai_not_correct--aicomment_ai_not_correct',
    `last_mark` LONGTEXT,
    `last_check_time` DATETIME(6),
    `last_classifier` JSON   COMMENT 'last_classifier',
    `last_report` JSON   COMMENT 'last_report',
    `first_check_user_id` BIGINT,
    `last_check_user_id` BIGINT,
    `study_id` BIGINT NOT NULL UNIQUE,
    CONSTRAINT `fk_studyaud_user_150bc7b2` FOREIGN KEY (`first_check_user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_studyaud_user_2d17a268` FOREIGN KEY (`last_check_user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_studyaud_study_08c3edb4` FOREIGN KEY (`study_id`) REFERENCES `study` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
