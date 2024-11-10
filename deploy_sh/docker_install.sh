#!/bin/bash

# 更新软件包索引
sudo apt-get update

# 安装必要的软件包以允许apt通过HTTPS使用仓库
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common

# 添加Docker的官方GPG密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 设置稳定版Docker仓库
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 再次更新软件包索引
sudo apt-get update

# 安装Docker CE
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# 验证Docker是否正确安装
sudo docker run hello-world

# 可选：将当前用户添加到docker组，以便无需sudo即可运行Docker命令
sudo usermod -aG docker ${USER}

# 提示重启计算机
echo "安装完成，请重启您的计算机以应用更改。"


