#!/bin/bash

# 函数：列出已加入的网络
list_networks() {
    echo "列出已加入的网络:"
    sudo zerotier-cli listnetworks
}

# 函数：列出所有设备
list_peers() {
    echo "列出所有设备:"
    sudo zerotier-cli listpeers
}

# 函数：列出所有Moon节点
list_moons() {
    echo "列出所有Moon节点:"
    sudo zerotier-cli listmoons
}

# 函数：检查是否成功加入Moon节点
check_moon_membership() {
    echo "检查是否成功加入Moon节点:"
    MOONS=$(sudo zerotier-cli listmoons)
    if [[ $MOONS == *"OK"* ]]; then
        echo "已成功加入Moon节点。"
    else
        echo "未加入任何Moon节点。"
    fi
}

# 主程序
echo "ZeroTier 常用信息查询"

# 列出已加入的网络
list_networks

# 列出所有设备
list_peers

# 列出所有Moon节点
list_moons

# 检查是否成功加入Moon节点
check_moon_membership