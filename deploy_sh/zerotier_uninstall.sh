echo "开始卸载 ZeroTier..."

    # 停止 ZeroTier 服务
    sudo systemctl stop zerotier-one
    sudo systemctl stop zerotier-controller

    # 卸载 ZeroTier
    sudo apt-get remove --purge -y zerotier-one zerotier-controller

    # 删除 ZeroTier 配置文件和日志文件
    sudo rm -rf /etc/zerotier-one
    sudo rm -rf /var/lib/zerotier-one
    sudo rm -rf /var/log/zerotier-one

    # 如果有 Moon 节点，移除 Moon 节点
    if [ -d "/var/lib/zerotier-one/moon" ]; then
        sudo rm -rf /var/lib/zerotier-one/moon
    fi

    # 如果有 Plant 节点，移除 Plant 节点
    if [ -d "/var/lib/zerotier-one/plant" ]; then
        sudo rm -rf /var/lib/zerotier-one/plant
    fi

    # 删除 ZeroTier 存储的文件和缓存
    sudo apt-get autoremove -y
    sudo apt-get clean

    # 恢复防火墙规则
    sudo ufw delete allow in on zerotier-one
    sudo ufw delete allow out on zerotier-one
    sudo ufw delete allow 9993/tcp

    # 恢复 IP 转发和 NAT 配置
    sudo sed -i '/net.ipv4.ip_forward=1/d' /etc/sysctl.conf
    sudo sed -i '/net.ipv6.conf.all.forwarding=1/d' /etc/sysctl.conf
    sudo iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
    sudo ip6tables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

    # 重新加载 sysctl 配置
    sudo sysctl -p

    # 保存当前的 iptables 和 ip6tables 规则
    sudo iptables-save > /etc/iptables/rules.v4
    sudo ip6tables-save > /etc/iptables/rules.v6

    # 删除 ZeroTier Controller 配置文件
    sudo rm -rf /etc/zerotier

    # 删除本地代理配置
    # 从环境变量中删除代理配置
    # sed -i '/http_proxy=/d' /etc/environment
    # sed -i '/https_proxy=/d' /etc/environment
    # sed -i '/ftp_proxy=/d' /etc/environment
    # sed -i '/no_proxy=/d' /etc/environment

    # # 从系统配置文件中删除代理配置
    # sed -i '/http_proxy=/d' /etc/profile
    # sed -i '/https_proxy=/d' /etc/profile
    # sed -i '/ftp_proxy=/d' /etc/profile
    # sed -i '/no_proxy=/d' /etc/profile

    # sed -i '/http_proxy=/d' /etc/bash.bashrc
    # sed -i '/https_proxy=/d' /etc/bash.bashrc
    # sed -i '/ftp_proxy=/d' /etc/bash.bashrc
    # sed -i '/no_proxy=/d' /etc/bash.bashrc

    # # 从用户配置文件中删除代理配置
    # sed -i '/http_proxy=/d' ~/.bashrc
    # sed -i '/https_proxy=/d' ~/.bashrc
    # sed -i '/ftp_proxy=/d' ~/.bashrc
    # sed -i '/no_proxy=/d' ~/.bashrc

    # sed -i '/http_proxy=/d' ~/.profile
    # sed -i '/https_proxy=/d' ~/.profile
    # sed -i '/ftp_proxy=/d' ~/.profile
    # sed -i '/no_proxy=/d' ~/.profile

    # # 从应用程序配置文件中删除代理配置
    # sed -i '/proxy=/d' ~/.curlrc
    # sed -i '/proxy=/d' ~/.wgetrc

    # # 检查并删除 WSL 代理配置
    # if command -v wsl.exe &> /dev/null; then
    #     echo "检测到 WSL 环境，正在删除 WSL 代理配置..."
    #     wsl.exe -u root -e sh -c "sed -i '/http_proxy=/d' /etc/environment"
    #     wsl.exe -u root -e sh -c "sed -i '/https_proxy=/d' /etc/environment"
    #     wsl.exe -u root -e sh -c "sed -i '/ftp_proxy=/d' /etc/environment"
    #     wsl.exe -u root -e sh -c "sed -i '/no_proxy=/d' /etc/environment"
    #     wsl.exe -u root -e sh -c "sed -i '/http_proxy=/d' /etc/profile"
    #     wsl.exe -u root -e sh -c "sed -i '/https_proxy=/d' /etc/profile"
    #     wsl.exe -u root -e sh -c "sed -i '/ftp_proxy=/d' /etc/profile"
    #     wsl.exe -u root -e sh -c "sed -i '/no_proxy=/d' /etc/profile"
    #     wsl.exe -u root -e sh -c "sed -i '/http_proxy=/d' /etc/bash.bashrc"
    #     wsl.exe -u root -e sh -c "sed -i '/https_proxy=/d' /etc/bash.bashrc"
    #     wsl.exe -u root -e sh -c "sed -i '/ftp_proxy=/d' /etc/bash.bashrc"
    #     wsl.exe -u root -e sh -c "sed -i '/no_proxy=/d' /etc/bash.bashrc"
    #     wsl.exe -u root -e sh -c "sed -i '/http_proxy=/d' ~/.bashrc"
    #     wsl.exe -u root -e sh -c "sed -i '/https_proxy=/d' ~/.bashrc"
    #     wsl.exe -u root -e sh -c "sed -i '/ftp_proxy=/d' ~/.bashrc"
    #     wsl.exe -u root -e sh -c "sed -i '/no_proxy=/d' ~/.bashrc"
    #     wsl.exe -u root -e sh -c "sed -i '/http_proxy=/d' ~/.profile"
    #     wsl.exe -u root -e sh -c "sed -i '/https_proxy=/d' ~/.profile"
    #     wsl.exe -u root -e sh -c "sed -i '/ftp_proxy=/d' ~/.profile"
    #     wsl.exe -u root -e sh -c "sed -i '/no_proxy=/d' ~/.profile"
    #     wsl.exe -u root -e sh -c "sed -i '/proxy=/d' ~/.curlrc"
    #     wsl.exe -u root -e sh -c "sed -i '/proxy=/d' ~/.wgetrc"
    # else
    #     echo "未检测到 WSL 环境。"
    # fi

    # echo "ZeroTier 已成功卸载，并且相关配置已恢复。"