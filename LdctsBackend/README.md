# LDCTS 后端服务


### 数据库迁移
```shell
# Initialize the config file and migrations location:
aerich init -t db.database.TORTOISE_ORM_MIGRATE
# (初始化db)
aerich init-db
aerich migrate --name xxx
aerich upgrade
# 数据库字段更新时执行，生成新的migration文件 (更新数据库表)
python3 scripts/migrate.py
```

### 代码格式化
```shell
# 安装测试依赖
pip install -r requirements-dev.txt

# 安装格式化依赖
pre-commit install

#  对所有提交数据进行格式
pre-commit run --all-files

```

### 运行celery
```shell
# 启动redis
docker run --rm -d --name redis -p 6380:6379 redis:7.2.4
# 启动celery
celery -A workers.celery_app worker -l info -c 1
```

### 参考文档
- fastapi: https://fastapi.tiangolo.com/
- tortoise： https://tortoise.github.io/index.html
- aerich: https://github.com/tortoise/aerich
- pre-commit: https://pre-commit.com/
