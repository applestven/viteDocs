#!/bin/bash

# ========== 配置区域 ==========

declare -A ssh_accounts=(
    ["9"]="ubuntu@154.81.14.81"
    ["8"]="root@8.148.184.96"
    ["7"]="ubuntu@123.58.219.234"
    ["6"]="apple@192.168.0.110"
    ["5"]="gangzhouweixiao@192.168.191.76"
    ["4"]="apple@10.254.91.20"
    ["3"]="ubuntu@43.139.236.50"
    ["2"]="root@83.229.123.43"
    ["1"]="apple@10.254.91.6"
)

declare -A ssh_hosts=(
    ["9"]="ubuntu@154.81.14.81"
    ["8"]="咸鱼客户的zerotier服务器"
    ["7"]="ubuntu@123.58.219.234"
    ["6"]="apple@192.168.0.110"
    ["5"]="gangzhouweixiao@192.168.191.76"
    ["4"]="apple@10.254.91.20"
    ["3"]="ubuntu@43.139.236.50"
    ["2"]="root@83.229.123.43"
    ["1"]="apple@10.254.91.6"
    ["0"]="local"
)

# ========== 展示账号列表 ==========
echo -e "\n📡 请选择一个 SSH 账号："
for key in $(printf "%s\n" "${!ssh_accounts[@]}" | sort -nr); do
    name="${ssh_accounts[$key]}"
    alias="${ssh_hosts[$key]:-"未配置"}"
    printf "  %s) %-25s [别名: %s]\n" "$key" "$name" "$alias"
done

read -rp $'\n👉 请输入编号: ' choice

# ========== 输入合法性检查 ==========
selected_ssh="${ssh_accounts[$choice]}"
host_alias="${ssh_hosts[$choice]}"

# 如果没有别名，默认使用 IP 地址作为别名
if [[ -z "$host_alias" ]]; then
    host_alias="${selected_ssh#*@}"
    host_alias="${host_alias//./_}"  # 将 . 替换为 _ 以避免 VS Code 中的命名问题
fi

if [[ -z "$selected_ssh" ]]; then
    echo "❌ 无效编号！"
    exit 1
fi

user=${selected_ssh%@*}
host=${selected_ssh#*@}
ssh_config="$HOME/.ssh/config"

# ========== 检查公钥 ==========
if [[ ! -f "$HOME/.ssh/id_rsa.pub" ]]; then
    echo "🔐 未检测到 SSH 公钥，正在创建..."
    ssh-keygen -t rsa -b 4096 -N "" -f "$HOME/.ssh/id_rsa"
fi

# ========== 检查是否已免密登录 ==========
check_ssh_login() {
    ssh -o BatchMode=yes -o ConnectTimeout=5 "${user}@${host}" true &>/dev/null
    return $?
}

if ! check_ssh_login; then
    echo "🔗 尚未配置免密登录，尝试上传 SSH 公钥..."
    ssh-keygen -R "$host" &>/dev/null
    ssh-keyscan -H "$host" >> ~/.ssh/known_hosts 2>/dev/null

    for i in {1..3}; do
        echo "👉 第 $i 次尝试 ssh-copy-id..."
        ssh-copy-id "${user}@${host}" && break
        echo "⚠️ 上传失败，请检查密码或网络问题。"
    done

    if ! check_ssh_login; then
        echo "❌ 自动上传失败，请手动检查远程 SSH 设置（是否允许密码登录/公钥登录）。"
        exit 1
    fi
fi

# ========== 写入 ~/.ssh/config ==========
if ! grep -q "Host $host_alias" "$ssh_config" 2>/dev/null; then
    echo "🛠 正在添加 VS Code SSH 配置项：$host_alias"
    {
        echo ""
        echo "Host $host_alias"
        echo "    HostName $host"
        echo "    User $user"
        echo "    IdentityFile ~/.ssh/id_rsa"
    } >> "$ssh_config"
fi

# ========== 输出当前选中配置 ==========
echo -e "\n🎯 当前选中的配置如下："
echo "Host $host_alias"
echo "    HostName $host"
echo "    User $user"

# ========== 输出提示 ==========
echo -e "\n✅ SSH 配置完成。你现在可以使用以下方式连接远程主机："
echo "  👉 ssh $host_alias"
echo "  👉 VS Code 中 Ctrl+Shift+P -> Remote-SSH -> Connect to Host -> $host_alias"
echo ""

# ========== 自动连接 ==========
ssh "$host_alias"
