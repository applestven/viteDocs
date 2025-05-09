#!/bin/bash
#!/bin/bash

#!/bin/bash

# ███████ 配置区 ███████
PORT=3388                                # 服务端口
DEFAULT_SHARE_DIR="/home/ubuntu/soft/sharefile"  # 默认共享目录
HOSTNAME="43.139.236.50"                 # ★ 手动指定访问地址（IP/域名）★ 注释掉则为默认地址
# ███████ 配置结束 ███████

# 自动获取本机IP（如果未手动配置HOSTNAME）
if [ -z "$HOSTNAME" ] || [ "$HOSTNAME" == "auto" ]; then
  IP_ADDR=$(hostname -I | awk '{print $1}')
else
  IP_ADDR="$HOSTNAME"
fi

# 检查Python3
if ! command -v python3 &> /dev/null; then
  echo "错误：Python3 未安装，请先执行 sudo apt install python3"
  exit 1
fi

# 生成URL列表函数
generate_urls() {
  local dir=$(realpath "$1")
  echo -e "\n\033[32m[文件列表] 共享地址 ($dir)\033[0m"
  echo "---------------------------------------------"
  
  cd "$dir" && find . -mindepth 1 | while read -r entry; do
    entry=$(echo "$entry" | sed 's|^\./||')
    if [ -d "$dir/$entry" ]; then
      echo "http://${IP_ADDR}:${PORT}/${entry}/"
    else
      echo "http://${IP_ADDR}:${PORT}/${entry}"
    fi
  done
  
  echo "---------------------------------------------"
  echo -e "文件总数：\033[33m$(find "$dir" -type f | wc -l)\033[0m"
}

# 处理命令
case "$1" in
  "list")
    SHARE_DIR="${2:-$DEFAULT_SHARE_DIR}"
    [ ! -d "$SHARE_DIR" ] && echo "错误：目录不存在" && exit 1
    generate_urls "$SHARE_DIR"
    ;;
  "stop")
    echo -e "\n\033[32m[服务停止]\033[0m 正在终止进程..."
    pkill -f "python3 -m http.server $PORT" && echo "成功停止服务" || echo "未找到运行中的服务"
    ;;
  *)
    SHARE_DIR="${1:-$DEFAULT_SHARE_DIR}"
    [ ! -d "$SHARE_DIR" ] && echo "错误：目录不存在" && exit 1
    echo -e "\n\033[32m[服务启动]\033[0m 共享目录: \033[34m$(realpath "$SHARE_DIR")\033[0m"
    echo "访问地址：http://${IP_ADDR}:${PORT}"
    echo "监控日志：按 Ctrl+C 停止"
    cd "$SHARE_DIR" && python3 -m http.server "$PORT"
    ;;
esac


# 使用

## 赋予权限
# chmod +x share_file.sh

## 启动服务
# ./share_file.sh

# 列出当前目录文件地址
# ./share_file.sh list

## 停止服务
# ./share_file.sh stop



## 运行成功示例
# [服务启动] 文件共享服务已启用
# ---------------------------------------------
# 共享目录：/home/ubuntu/soft/sharefile
# 访问地址：http://10.0.12.6:3388
# 终端监控：按 Ctrl+C 停止服务
# ---------------------------------------------
# Serving HTTP on 0.0.0.0 port 3388 (http://0.0.0.0:3388/) ...
# ^C
# Keyboard interrupt received, exiting.


## 
