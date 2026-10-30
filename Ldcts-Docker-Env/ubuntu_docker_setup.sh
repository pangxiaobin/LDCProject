#!/bin/bash

echo ""
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "+"
echo "+                      docker environment setup"
echo "+"
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo ""

sudo grep &> /dev/null

print () {
    printf "$1"
}

step=1;
print_check() {
    printf "\n| Step - %2d | $1\n\n" "$step"
    step=$((step + 1));
}

print_ok() {
    print "\n[     OK    ]\n\n"
}

print_warn() {
    print "\n[   WARN    ]: $1\n\n"
}

throw_error() {
    print "\n[   ERROR   ]: $1\n\n"
    exit 1;
}

print_check "Install docker"
docker --version  &> /dev/null
if [ $? -ne 0 ]; then
    print "Set up the repository"
    sudo apt-get update
    sudo apt-get install ca-certificates curl gnupg
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    echo "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
   "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    # 执行lsb_release -a命令，并将输出保存到变量中
    release_info=$(lsb_release -a)

    # 从输出中提取版本号和代号
    version=$(echo "$release_info" | awk '/Release:/ {print $2}')
    codename=$(echo "$release_info" | awk '/Codename:/ {print $2}')

    # 拼接字符串
    result="ubuntu.$version~$codename"
    VERSION_STRING="5:24.0.7-1~$resultl"
    sudo apt-get install -y docker-ce=$VERSION_STRING docker-ce-cli=$VERSION_STRING containerd.io docker-buildx-plugin docker-compose-plugin
    #  sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    if [ $? -ne 0 ]; then
        throw_error "docker install error"
    else
        print_ok
    fi 
else
    print "docker has Installed \n\n"
    
fi
print_ok

# Ensure user is part of docker group
print_check "Check docker group"
groups $USER | grep -Eq docker &> /dev/null
if [ $? -ne 0 ]; then
    # Ignore if docker group existed
    sudo groupadd -f docker
    sudo usermod -aG docker $USER
    if [ -f ~/.docker ]; then
        rm -rf ~/.docker
    fi
    sudo su $USER # Switch user to gain docker permission
    print "added $USER to group docker\n\n"
fi
print_ok

# Check docker enabled
print_check "Check docker enabled"
systemctl is-enabled docker &> /dev/null
if [ $? -ne 0 ]; then
    sudo systemctl enable --now docker
    if [ $? -eq 0 ]; then
        print "docker enabled\n\n"
    else
        print "docker enable failed\n\n"
    fi
fi
print_ok


print_check "Check docker registry-mirrors config"
# 配置镜像加速
path="/etc/docker"
# 检查文件路径是否存在
if [ ! -d "$path" ]; then
  # 如果路径不存在，则创建路径
  sudo mkdir -p "$path"
  # 写入配置文件
  sudo tee /etc/docker/daemon.json <<-'EOF'
  {
       "registry-mirrors": ["https://2f7k1a6k.mirror.aliyuncs.com"]
    }
EOF
    sudo systemctl daemon-reload
    sudo systemctl restart docker
fi
print_ok