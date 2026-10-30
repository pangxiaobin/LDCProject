#!/bin/bash

# Git仓库的URL
REPO_URL="https://codeup.aliyun.com/648bf384a708906d745a5a53/LDCTS/LdctsBackend.git"
# 目标目录
TARGET_DIR=$2

# 函数定义：克隆仓库
function clone_repo {
    if [ ! -d "$TARGET_DIR" ]; then
        echo "Cloning repository..."
        git clone $REPO_URL $TARGET_DIR
        if [ $? -ne 0 ]; then
            echo "Error: Cloning repository failed."
            exit 1
        fi
    else
        echo "Target directory already exists. Use 'update' to update the repository."
        exit 1
    fi
}

# 函数定义：更新仓库
function update_repo {
    if [ -d "$TARGET_DIR/.git" ]; then
        echo "Updating repository..."
        cd $TARGET_DIR
        git pull
        if [ $? -ne 0 ]; then
            echo "Error: Updating repository failed."
            exit 1
        fi
    else
        echo "Error: Target directory does not appear to be a Git repository."
        exit 1
    fi
}

# 主脚本逻辑
case "$1" in
    download)
        clone_repo
        ;;
    update)
        update_repo
        ;;
    *)
        echo "No valid argument provided. Defaulting to 'download'."
        clone_repo
        ;;
esac

exit 0