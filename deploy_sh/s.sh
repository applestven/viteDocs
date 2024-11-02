#!/bin/bash

# 定义 SSH 账号列表
declare -A ssh_accounts=(
    ["4"]="gangzhouweixiao@192.168.191.76"
    ["3"]="root@83.229.123.43"
    ["2"]="ubuntu@43.139.236.50"
    ["1"]="apple@192.168.191.214"
)

# 显示 SSH 账号列表
echo "请选择一个 SSH 账号："
for key in "${!ssh_accounts[@]}"; do
    echo "$key) ${ssh_accounts[$key]}"
done

# 获取用户选择
read -p "请输入编号: " choice

# 检查用户输入是否有效
if [[ -z "${ssh_accounts[$choice]}" ]]; then
    echo "无效的选择！"
    exit 1
fi

# 获取选中的 SSH 地址
selected_ssh="${ssh_accounts[$choice]}"

# 执行 SSH 连接
ssh $selected_ssh