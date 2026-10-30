#!/bin/bash
set -e
TARGET_DIR="./volumes"
SOURCE_DIR="./compose"

function create_path() {
  path_name=$1  # $1 表示函数的第一个参数
  if [ ! -d "$path_name" ]; then
    echo "目标目录不存在，正在创建: $path_name"
    mkdir -p "$path_name"
  else
    echo "目标目录已存在: $path_name"
  fi
}

create_path "$TARGET_DIR/var/nginx"
create_path "$TARGET_DIR/var/redis"
create_path "$TARGET_DIR/var/mysql"


cp -f $SOURCE_DIR/nginx/nginx.conf $TARGET_DIR/var/nginx/nginx.conf
cp -f $SOURCE_DIR/redis/redis.conf $TARGET_DIR/var/redis/redis.conf
cp -f $SOURCE_DIR/mysql/mysql.cnf $TARGET_DIR/var/mysql/mysql.cnf

# 创建前端需要的文件目录
create_path "$TARGET_DIR/front_end/ldcts"
if [ ! -d "$TARGET_DIR/front_end/ldcts/dist" ]; then
  cp -rf $SOURCE_DIR/front_end/dist $TARGET_DIR/front_end/ldcts
else
  echo "前端文件已存在"
fi


# 创建后端需要的文件目录
create_path "$TARGET_DIR/server/ldcts"

ldcts_backend_dir="$TARGET_DIR/server/ldcts"


if [ ! -d "$ldcts_backend_dir/LdctsBackend" ];then
    bash ./git_repo_manager.sh download $ldcts_backend_dir/LdctsBackend
else
    bash ./git_repo_manager.sh update $ldcts_backend_dir/LdctsBackend
fi



echo "启动服务"
if [ "$1" = "release" ]; then
    docker compose up -d
else
    docker compose -f docker-compose-environments.yml up -d
fi