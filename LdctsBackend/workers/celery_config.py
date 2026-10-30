# celery_config.py
from conf.settings import settings

# docker run --rm -d --name redis -p 6380:6379 redis:7.2.4
# Broker的URL地址，我们使用了Redis作为broker。
broker_url = settings.BROKER_URL

# 结果后端的URL，用于存储任务的结果，同样使用Redis。
result_backend = settings.BROKER_URL

# 定义Celery接受的内容类型。在这里，我们只接受 JSON 类型。
accept_content = ["json"]

# 任务序列化方式，我们选择 'json'，你可以选择其他比如 'pickle' 或者 'yaml'
task_serializer = "json"

# 结果序列化方式，我们选择 'json'，你可以选择其他比如 'pickle' 或者 'yaml'
result_serializer = "json"

# 时区设置为中国时区
timezone = "Asia/Shanghai"
enable_utc = False


# 如果设置为True，任务被worker执行完毕后不立即确认，而是等到worker执行完所有任务后再确认。这有助于在worker突然关闭时，任务可以重新继续执行，而不会丢失。
task_acks_late = True

# 预取任务数量，最小值为1，如果设置为1，表示每个worker每次只取一条任务来执行，这有利于分散任务到更多的worker进行处理。
worker_prefetch_multiplier = 1

# worker并发数，默认为机器的CPU数量。在这里我们设置为2，你可以根据你的实际需要进行修改
worker_concurrency = 2

# broker连接池大小，如果所有的worker都占据了broker连接，新到来的任务会阻塞直到有可用的连接。建议设置一个比较大的数值，具体的数值需要结合实际的任务负载来进行调整。
broker_pool_limit = 10

# broker的心跳，默认是4秒，如果broker在这段时间内未收到worker的心跳，将会断开连接，然后worker会尝试重新连接。
broker_heartbeat = 4

# 任务执行的超时时间，如果任务没有在这个时间内完成，会被终止。1800，即半小时。
task_time_limit = 1800

imports = ("workers.tasks",)

# 日志
worker_log_format = (
    "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)s - %(funcName)s: %(message)s}"
)
