#!/bin/bash

# 递归设置目录及其所有子孙文件和文件夹权限为777
# 用法: ./chmod-recursive.sh <目录路径>

if [ $# -eq 0 ]; then
    echo "请提供目录路径"
    echo "用法: $0 <目录路径>"
    exit 1
fi

if [ ! -d "$1" ]; then
    echo "错误: $1 不是一个有效的目录"
    exit 1
fi

# 递归设置权限为777
chmod -R 777 "$1"

if [ $? -eq 0 ]; then
    echo "成功将目录 $1 及其所有子孙文件和文件夹设置为777权限"
else
    echo "设置权限时出错"
    exit 1
fi