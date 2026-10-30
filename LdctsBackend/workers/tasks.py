from db.database import do_stuff
from tortoise import run_async, Tortoise
from apps.study.utils import save_study
from workers.celery_app import celery_instance
import traceback
from models.base import *

from common.log import logger


async def async_save_study(study_info: dict):
    await do_stuff()
    try:
        await save_study(study_info)
    except Exception as e:
        logger.error(
            f"Save_study error: {traceback.format_exc()} \n save_study_info: {study_info}"
        )
    logger.info(f"Save_study success")


@celery_instance.task(max_retries=2)
def save_study_task(study_info: dict):
    try:
        run_async(async_save_study(study_info))
    except Exception as e:
        logger.error(e)


async def test_tortoise_in_celery():
    await do_stuff()
    res = await Study.all()
    for i in res:
        print(i)


@celery_instance.task()
def test_celery(item):
    print(item)
    run_async(test_tortoise_in_celery())
    print("test tortoise in celery")
