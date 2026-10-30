from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `series` ADD `nifti_size` JSON   COMMENT '影像大小x,y,x';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `series` DROP COLUMN `nifti_size`;"""
