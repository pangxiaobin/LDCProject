from celery import Celery, platforms


from workers import celery_config


def make_celery():
    celery = Celery(
        "workers", broker=celery_config.broker_url, backend=celery_config.result_backend
    )
    # 允许celery 已root账号运行
    platforms.C_FORCE_ROOT = True
    celery.config_from_object(celery_config)
    return celery


celery_instance = make_celery()
