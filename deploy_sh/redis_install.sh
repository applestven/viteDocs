#!/bin/bash

# 更新软件包列表
sudo apt update

# 安装Redis服务器
sudo apt install redis-server -y

# 检查Redis服务状态
sudo systemctl status redis.service

# 如果需要，可以编辑Redis配置文件
# sudo nano /etc/redis/redis.conf

# 重启Redis服务以应用更改
# sudo systemctl restart redis.service

# 验证Redis是否正常运行
redis-cli ping