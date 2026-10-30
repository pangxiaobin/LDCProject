from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `study` MODIFY COLUMN `ai_status` VARCHAR(48)   COMMENT 'ai状态';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `study` MODIFY COLUMN `ai_status` VARCHAR(24)   COMMENT 'ai状态';"""
