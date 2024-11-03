#!/bin/bash

# 更新系统包
echo "开始更新系统包..."
sudo apt-get update
sudo apt-get upgrade -y
echo "系统包更新完成。"

# 安装 ZeroTier
echo "开始安装 ZeroTier..."
sudo apt-get install -y curl
curl -s https://install.zerotier.com | sudo bash
echo "ZeroTier 安装完成。"

# 检查 ZeroTier 是否已安装
if ! command -v zerotier-one &> /dev/null; then
    echo "ZeroTier One 安装失败，请检查网络连接或手动安装。"
    exit 1
fi

# 启动 ZeroTier 服务
echo "启动 ZeroTier 服务..."
sudo systemctl start zerotier-one
# sudo systemctl enable zerotier-one
echo "ZeroTier 服务启动完成。"

# 创建 ZeroTier 网络并获取网络 ID
echo "创建 ZeroTier 网络并获取网络 ID..."
NETWORK_ID=$(sudo zerotier-cli info | grep -oP '^\d+ info \K[0-9a-fA-F]+')
echo "##########网络 ID: $NETWORK_ID"
if [ -z "$NETWORK_ID" ]; then
    echo "无法获取网络 ID，请检查 ZeroTier 服务是否正常运行。"
    exit 1
fi
echo "ZeroTier 网络已创建，网络 ID: $NETWORK_ID"

# 配置防火墙以允许 ZeroTier 流量
echo "配置防火墙以允许 ZeroTier 流量..."
sudo ufw allow in on zerotier-one
sudo ufw allow out on zerotier-one
echo "防火墙配置完成。"

# 启用 IP 转发并配置 NAT
echo "启用 IP 转发并配置 NAT..."
sudo sysctl -w net.ipv4.ip_forward=1
sudo sysctl -w net.ipv6.conf.all.forwarding=1
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo ip6tables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
echo "IP 转发和 NAT 配置完成。"

# 保存 IP 转发和 NAT 配置
echo "保存 IP 转发和 NAT 配置..."
sudo sh -c "echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.conf"
sudo sh -c "echo 'net.ipv6.conf.all.forwarding=1' >> /etc/sysctl.conf"
sudo iptables-save > /etc/iptables/rules.v4
sudo ip6tables-save > /etc/iptables/rules.v6
echo "IP 转发和 NAT 配置保存完成。"

# 安装 ztncui
echo "开始安装 ztncui..."
sudo apt-get install -y git
git clone https://github.com/key-networks/ztncui.git /opt/ztncui
cd /opt/ztncui
sudo ./install.sh
echo "ztncui 安装完成。"

# 配置 ztncui
echo "配置 ztncui..."
sudo tee /opt/ztncui/ztncui.conf > /dev/null <<EOF
ZTNCUI_API=$(openssl rand -hex 16)
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
Environment=ZTNCUI_API=$(openssl rand -hex 16)
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
sudo systemctl enable ztncui
echo "ztncui 服务启动完成。"

# 检查 ztncui 服务是否启动成功
if ! sudo systemctl is-active --quiet ztncui; then
    echo "ztncui 服务启动失败，请检查日志。"
    exit 1
fi

# 配置防火墙以允许访问 ztncui
echo "配置防火墙以允许访问 ztncui..."
sudo ufw allow 9993/tcp
echo "防火墙配置完成。"

# 输出配置信息
echo "ZeroTier Planet 服务器及 ztncui 管理界面已成功配置。"
echo "网络 ID: $NETWORK_ID"
echo "请将此网络 ID 分享给其他 ZeroTier 客户端以加入网络。"
echo "ztncui 管理界面可以通过 http://<your_server_ip>:9993 访问。"
