#!/bin/bash

# 获取当前脚本的目录
SCRIPT_DIR="$(dirname "$0")"

# 获取当前父文件夹下的所有 sh 脚本，排除自身
SCRIPTS=($(find "$SCRIPT_DIR" -maxdepth 1 -type f -name "*.sh" ! -name "$(basename "$0")"))

# 检查是否找到任何脚本
if [ ${#SCRIPTS[@]} -eq 0 ]; then
    echo "当前目录下没有找到其他 sh 脚本。"
    exit 0
fi

# 显示脚本列表供用户选择
echo "请选择要执行的脚本："
for i in "${!SCRIPTS[@]}"; do
    echo "$((i+1))) ${SCRIPTS[$i]}"
done

# 读取用户输入
read -p "输入脚本的编号: " choice

# 检查用户输入是否有效
if ! [[ "$choice" =~ ^[0-9]+$ ]] || [ "$choice" -lt 1 ] || [ "$choice" -gt ${#SCRIPTS[@]} ]; then
    echo "无效的选择。"
    exit 1
fi

# 执行用户选择的脚本
SELECTED_SCRIPT="${SCRIPTS[$((choice-1))]}"
echo "执行脚本: $SELECTED_SCRIPT"
bash "$SELECTED_SCRIPT"
