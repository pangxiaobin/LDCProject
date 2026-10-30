from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `series` ADD `breath_artifact` VARCHAR(128)   COMMENT '序列是否有呼吸伪影';
        ALTER TABLE `series` MODIFY COLUMN `recon` VARCHAR(64)   COMMENT '序列的重建方式';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `series` DROP COLUMN `breath_artifact`;
        ALTER TABLE `series` MODIFY COLUMN `recon` VARCHAR(64)   COMMENT 'recon';"""
