#!/bin/bash

# 提示用户选择是否使用代理
read -p "是否使用代理？(y/n): " use_proxy

# 根据用户选择设置或清除代理环境变量
if [ "$use_proxy" = "y" ] || [ "$use_proxy" = "Y" ]; then
    # 设置代理环境变量
    export http_proxy="http://127.0.0.1:7890"
    export https_proxy="http://127.0.0.1:7890"
    export ftp_proxy="http://127.0.0.1:7890"
    echo "代理已设置为 http://127.0.0.1:7890"
else
    # 清除代理环境变量
    unset http_proxy
    unset https_proxy
    unset ftp_proxy
    echo "代理已禁用"
fi
