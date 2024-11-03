#!/bin/bash

# 更新系统包
echo "开始更新系统包..."
sudo apt-get update
sudo apt-get upgrade -y
echo "系统包更新完成。"

# 检查 ztncui 目录是否存在
if [ -d "/opt/ztncui" ]; then
    echo "/opt/ztncui 目录已存在，正在删除..."
    sudo rm -rf /opt/ztncui
fi

# 安装 ztncui
echo "开始安装 ztncui..."
git clone https://github.com/key-networks/ztncui.git /opt/ztncui
cd /opt/ztncui

# 检查 install.sh 是否存在
if [ ! -f "./install.sh" ]; then
    echo "安装脚本 install.sh 未找到，请检查 Git 仓库。"
    exit 1
fi

sudo ./install.sh
echo "ztncui 安装完成。"

# 配置 ztncui
echo "配置 ztncui..."
API_KEY=$(openssl rand -hex 16)  # 生成随机 API 密钥
sudo tee /opt/ztncui/ztncui.conf > /dev/null <<EOF
ZTNCUI_API=$API_KEY
ZTNCUI_CONTROLLER=http://localhost:9993
ZTNCUI_PORT=3000
ZTNCUI_SSL=false
EOF
echo "ztncui 配置完成。"

# 创建 ztncui.service 文件
echo "创建 ztncui.service 文件..."
sudo tee /etc/systemd/system/ztncui.service > /dev/null <<EOF
[Unit]
Description=ZeroTier Network Controller UI
After=network.target

[Service]
ExecStart=/opt/ztncui/ztncui
Restart=always
User=root
Environment=ZTNCUI_API=$API_KEY
Environment=ZTNCUI_CONTROLLER=http://localhost:9993
Environment=ZTNCUI_PORT=3000
Environment=ZTNCUI_SSL=false

[Install]
WantedBy=multi-user.target
EOF

# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启动 ztncui 服务
echo "启动 ztncui 服务..."
sudo systemctl start ztncui

# 检查 ztncui 服务是否启动成功
if ! sudo systemctl is-active --quiet ztncui; then
    echo "ztncui 服务启动失败，请检查日志。"
    sudo journalctl -u ztncui.service --no-pager | tail -n 20  # 查看最后20行日志
    exit 1
fi

# 启用开机自启
sudo systemctl enable ztncui
echo "ztncui 服务启动完成，已设置为开机自启。"

# 配置防火墙以允许访问 ztncui
echo "配置防火墙以允许访问 ztncui..."
sudo ufw allow 9993/tcp
echo "防火墙配置完成。"

# 输出配置信息
echo "ztncui 管理界面可以通过 http://<your_server_ip>:9993 访问。"
