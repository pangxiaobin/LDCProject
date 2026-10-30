#!/bin/bash
set -e

# 更新
docker exec -i ldcts-web bash -c "cd /var/app/LdctsBackend && aerich upgrade"
# 初始化数据
docker exec -i ldcts-web bash -c "cd /var/app/LdctsBackend && python scripts/init_data.py"
# 生成视图
docker exec -i ldcts-web bash -c "cd /var/app/LdctsBackend && python scripts/init_views.py"
# 更新字典服务
docker exec -i ldcts-web bash -c "cd /var/app/LdctsBackend && python scripts/init_dict_data.py"

echo "done"