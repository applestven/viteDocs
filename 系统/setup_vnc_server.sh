#!/bin/bash

# VNC服务器完整设置脚本
# 解决黑屏问题，提供完整的桌面环境

set -e  # 遇到错误时停止执行

echo "=== VNC服务器设置脚本 ==="

# 检查是否以root权限运行
if [ "$EUID" -eq 0 ]; then
  echo "请不要以root用户运行此脚本"
  exit 1
fi

# 定义颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印带颜色的信息
print_info() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# 检查系统信息
print_info "检查系统信息..."
if ! command -v lsb_release &> /dev/null; then
  print_error "无法确定系统版本，确保在Ubuntu上运行"
  exit 1
fi

OS_VERSION=$(lsb_release -rs)
print_info "检测到Ubuntu $OS_VERSION"

# 更新系统包列表
print_info "更新系统包列表..."
sudo apt update

# 安装必要软件包
print_info "安装必要软件包..."
sudo apt install -y \
  xvfb \
  x11vnc \
  xfce4 \
  xfce4-goodies \
  openbox \
  lightdm \
  xorg \
  xserver-xorg-video-dummy

# 创建VNC密码目录
print_info "创建VNC配置目录..."
mkdir -p ~/.vnc

# 设置VNC密码
print_info "设置VNC密码..."
x11vnc -storepasswd

# 创建启动脚本
print_info "创建VNC启动脚本..."
cat > ~/start_vnc.sh << 'EOF'
#!/bin/bash

# VNC启动脚本
# 设置显示环境变量
export DISPLAY=:1
export XDG_SESSION_TYPE=x11
export XDG_CURRENT_DESKTOP=XFCE
export XDG_SESSION_DESKTOP=xfce

# 启动X虚拟帧缓冲器
echo "启动Xvfb..."
Xvfb :1 -screen 0 1920x1080x24 &> ~/.vnc/Xvfb.log &
XVFB_PID=$!

# 等待Xvfb启动
sleep 3

# 检查Xvfb是否成功启动
if ! pgrep -P $$ | grep -q Xvfb; then
  echo "Xvfb未能成功启动，请检查~/.vnc/Xvfb.log"
  exit 1
fi

echo "Xvfb已启动 (PID: $XVFB_PID)"

# 启动窗口管理器
echo "启动XFCE桌面环境..."
startxfce4 &> ~/.vnc/xfce4.log &
DESKTOP_PID=$!

# 等待桌面环境启动
sleep 5

# 检查桌面环境是否成功启动
if ! pgrep -P $$ | grep -q xfce4-session; then
  echo "XFCE桌面环境未能成功启动，请检查~/.vnc/xfce4.log"
  echo "尝试启动轻量级openbox窗口管理器..."
  openbox-session &> ~/.vnc/openbox.log &
  OPENBOX_PID=$!
  sleep 3
  
  if ! pgrep -P $$ | grep -q openbox; then
    echo "openbox窗口管理器也未能成功启动，请检查~/.vnc/openbox.log"
    # 杀掉Xvfb进程
    kill $XVFB_PID 2>/dev/null || true
    exit 1
  else
    echo "openbox已启动 (PID: $OPENBOX_PID)"
  fi
else
  echo "XFCE桌面环境已启动 (PID: $DESKTOP_PID)"
fi

# 启动x11vnc服务器
echo "启动x11vnc服务器..."
x11vnc -display :1 -forever -shared -rfbauth ~/.vnc/passwd -o ~/.vnc/x11vnc.log -bg

# 等待x11vnc启动
sleep 2

# 检查x11vnc是否成功启动
if ! pgrep -f "x11vnc.*display.*:1" > /dev/null; then
  echo "x11vnc未能成功启动，请检查~/.vnc/x11vnc.log"
  # 杀掉所有相关进程
  kill $XVFB_PID 2>/dev/null || true
  kill $DESKTOP_PID 2>/dev/null || true
  kill $OPENBOX_PID 2>/dev/null || true
  exit 1
fi

echo "x11vnc服务器已启动"

# 显示进程信息
echo "=== 运行中的相关进程 ==="
echo "Xvfb PID: $XVFB_PID"
echo "桌面环境 PID: $DESKTOP_PID"
if [ ! -z "$OPENBOX_PID" ]; then
  echo "Openbox PID: $OPENBOX_PID"
fi

echo ""
echo "VNC服务器已成功启动！"
echo "请使用VNC客户端连接: vnc://<你的IP地址>:5900"
echo "日志文件位于 ~/.vnc/ 目录中"

# 等待用户中断或进程结束
wait
EOF

chmod +x ~/start_vnc.sh

# 创建系统服务文件
print_info "创建系统服务..."
sudo tee /etc/systemd/system/vnc-server.service > /dev/null << 'EOF'
[Unit]
Description=VNC Server with Full Desktop
After=network.target

[Service]
Type=forking
User=%i
ExecStart=/bin/bash /home/%i/start_vnc.sh
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 重新加载systemd配置
print_info "重新加载systemd配置..."
sudo systemctl daemon-reload

# 启用防火墙端口
print_info "配置防火墙..."
if command -v ufw &> /dev/null; then
  sudo ufw allow 5900/tcp
  print_info "已允许5900端口通过防火墙"
else
  print_warn "未检测到ufw防火墙，如果你使用其他防火墙，请手动允许5900端口"
fi

# 创建使用说明
cat > ~/VNC_USAGE.md << 'EOF'
# VNC服务器使用说明

## 启动VNC服务器

### 方法1: 使用systemd服务（推荐）
```bash
# 启用并启动服务
sudo systemctl enable --now vnc-server@$USER

# 检查服务状态
sudo systemctl status vnc-server@$USER
```

### 方法2: 直接运行脚本
```bash
# 运行启动脚本
~/start_vnc.sh
```

## 连接到VNC服务器

使用任何VNC客户端连接到以下地址：
```
vnc://<你的服务器IP>:5900
```

使用设置时创建的密码进行连接。

## 停止VNC服务器

### 如果使用systemd服务：
```bash
# 停止服务
sudo systemctl stop vnc-server@$USER

# 禁用服务
sudo systemctl disable vnc-server@$USER
```

### 如果直接运行脚本：
按 `Ctrl+C` 停止脚本，或者找到并杀死相关进程：
```bash
pkill -f "Xvfb\|x11vnc\|xfce4\|openbox"
```

## 故障排除

### 查看日志
所有日志都保存在 `~/.vnc/` 目录中：
```bash
# 查看Xvfb日志
tail -f ~/.vnc/Xvfb.log

# 查看桌面环境日志
tail -f ~/.vnc/xfce4.log

# 查看x11vnc日志
tail -f ~/.vnc/x11vnc.log
```

### 黑屏问题
如果连接后看到黑屏：
1. 确保已安装桌面环境：
   ```bash
   sudo apt install -y xfce4 xfce4-goodies
   ```

2. 重启VNC服务：
   ```bash
   sudo systemctl restart vnc-server@$USER
   ```

3. 尝试使用不同的窗口管理器

### 连接被拒绝
1. 检查防火墙设置：
   ```bash
   sudo ufw status
   sudo ufw allow 5900/tcp
   ```

2. 检查服务是否正在运行：
   ```bash
   sudo systemctl status vnc-server@$USER
   ```

3. 检查端口是否监听：
   ```bash
   netstat -tulnp | grep 5900
   ```

## 文件说明

- `~/start_vnc.sh` - VNC启动脚本
- `~/.vnc/passwd` - VNC密码文件
- `~/.vnc/*.log` - 各种日志文件
- `/etc/systemd/system/vnc-server.service` - systemd服务文件
EOF

# 显示完成信息
print_info "VNC服务器设置完成！"

echo ""
echo "=========================================="
echo "           设置完成！"
echo "=========================================="
echo ""
echo "下一步操作："
echo ""
echo "1. 启动VNC服务器（推荐使用systemd服务）："
echo "   sudo systemctl enable --now vnc-server@$USER"
echo ""
echo "2. 检查服务状态："
echo "   sudo systemctl status vnc-server@$USER"
echo ""
echo "3. 使用VNC客户端连接："
echo "   vnc://<你的服务器IP>:5900"
echo ""
echo "4. 查看使用说明："
echo "   cat ~/VNC_USAGE.md"
echo ""
echo "5. 查看日志文件："
echo "   ~/.vnc/*.log"
echo ""
echo "=========================================="