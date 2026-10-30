from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `seriesqualitycontrol` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `create_time` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `breath_artifact` VARCHAR(40) NOT NULL  COMMENT '呼吸伪影 breath_artifact_not_found--无伪影 breath_artifact_low--有伪影,不影响诊断 breath_artifact_medium--有伪影,勉强可以诊断 breath_artifact_high--伪影严重,不能诊断' DEFAULT 'breath_artifact_not_found',
    `metal_artifact` VARCHAR(40) NOT NULL  COMMENT '金属伪影 metal_artifact_not_found--无伪影 metal_artifact_low--有伪影,不影响诊断 metal_artifact_medium--有伪影,勉强可以诊断 metal_artifact_high--伪影严重,不能诊断' DEFAULT 'metal_artifact_not_found',
    `heart_artifact` VARCHAR(40) NOT NULL  COMMENT '心脏伪影 heart_artifact_not_found--无伪影 heart_artifact_low--有伪影,不影响诊断 heart_artifact_medium--有伪影,勉强可以诊断 heart_artifact_high--伪影严重,不能诊断' DEFAULT 'heart_artifact_not_found',
    `position` VARCHAR(40) NOT NULL  COMMENT '体位 normal_position--正常体位 prone_position--俯卧位 oblique_position--倾斜位' DEFAULT 'normal_position',
    `image_quality` VARCHAR(40) NOT NULL  COMMENT '图像质量 normal_quality--正常质量 low_quality--质量偏低,勉强可以诊断 bad_quality--图像质量低,不能诊断' DEFAULT 'normal_quality',
    `image_integrity` VARCHAR(40) NOT NULL  COMMENT '图像完整性 normal_integrity--完整图像 low_integrity--部分缺失,仍可用 bad_integrity--图像缺失,不能诊断' DEFAULT 'normal_integrity',
    `specialty` VARCHAR(40) NOT NULL  COMMENT '特殊案例 no_specialty--正常案例 specialty_case--特殊案例' DEFAULT 'no_specialty',
    `series_id` BIGINT NOT NULL UNIQUE,
    CONSTRAINT `fk_seriesqu_series_21403e5f` FOREIGN KEY (`series_id`) REFERENCES `series` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `seriesqualitycontrol`;"""
