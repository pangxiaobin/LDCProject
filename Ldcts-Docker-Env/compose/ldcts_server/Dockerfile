FROM  python:3.10.6

# 设置阿里云的apt源和设置时区
ENV TZ=Asia/Shanghai
RUN echo "${TZ}" > /etc/timezone && \ 
    ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime && \
    echo "deb http://mirrors.aliyun.com/debian/ buster main" > /etc/apt/sources.list && \
    echo "deb-src http://mirrors.aliyun.com/debian/ buster main" >> /etc/apt/sources.list && \
    apt-get update && apt-get install -y netcat tzdata && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


# 设置 python 环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV APP_HOME=/var/app/LdctsBackend
RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME

ADD ./requirements.txt $APP_HOME
ADD ./start.sh $APP_HOME

# 安装项目依赖
RUN /usr/local/bin/python -m pip install --upgrade pip && \
 pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 移除\r in windows
RUN sed -i 's/\r//' ./start.sh
# 给start.sh可执行权限
RUN chmod +x ./start.sh

# CMD [ "bash" "start.sh" ]
