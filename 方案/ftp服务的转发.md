# FTP 服务转发配置指南

## 目标
将内网服务器的 FTP 服务转发到外网服务器，实现相机等设备通过公网访问内网 FTP 服务。

## 环境信息
- **公网服务器**: `43.139.236.50`
- **内网服务器**: `192.168.191.20`
- **FTP 服务**: `192.168.191.20:21`
- **连接方式**: 公网服务器与内网服务器通过 ZeroTier 连接
- **可用端口**: 公网服务器端口 `7000-7010`，内网服务器端口不限制
- **映射端口**: FTP 端口 `21` 映射到公网端口 `7010`

## 方案特点
- ✅ 支持相机 FTP 上传
- ✅ 完整支持 FTP 被动模式 (PASV)
- ✅ 最佳兼容性方案



## 完整配置方案

> 📘 下面是完整的可用配置（直接复制即可）

### 一、内网服务器（192.168.191.20）配置

#### 1. 配置 FTP 被动模式端口（非常关键）

打开 FTP 配置文件：

```bash
sudo nano /etc/vsftpd.conf
```

添加以下配置：

```ini
pasv_enable=YES
pasv_min_port=50000
pasv_max_port=50010
pasv_address=43.139.236.50
```

> ⚠️ **注意**: `pasv_address` 必须填写公网服务器 IP（不是 Zerotier IP）

重启 FTP 服务：

```bash
sudo systemctl restart vsftpd
```

#### 2. 安装和配置 frpc

下载并安装 frp：

```bash
wget https://github.com/fatedier/frp/releases/download/v0.57.0/frp_0.57.0_linux_amd64.tar.gz
tar -zxvf frp_0.57.0_linux_amd64.tar.gz
cd frp_0.57.0_linux_amd64

或者 cd /home/ubuntu/frp_0.57.0_linux_amd64/frpc
```

编辑 `frpc.ini` 配置文件：

```ini
[common]
server_addr = 43.139.236.50
server_port = 7000

# FTP 控制端口（21 -> 7010）
[ftp-control]
type = tcp
local_ip = 192.168.191.20
local_port = 21
remote_port = 7010

# PASV 端口映射 50000~50010 -> 7001~7010
[ftp-data-50000]
type = tcp
local_ip = 192.168.191.20
local_port = 50000
remote_port = 7001

[ftp-data-50001]
type = tcp
local_ip = 192.168.191.20
local_port = 50001
remote_port = 7002

[ftp-data-50002]
type = tcp
local_ip = 192.168.191.20
local_port = 50002
remote_port = 7003

[ftp-data-50003]
type = tcp
local_ip = 192.168.191.20
local_port = 50003
remote_port = 7004

[ftp-data-50004]
type = tcp
local_ip = 192.168.191.20
local_port = 50004
remote_port = 7005

[ftp-data-50005]
type = tcp
local_ip = 192.168.191.20
local_port = 50005
remote_port = 7006

[ftp-data-50006]
type = tcp
local_ip = 192.168.191.20
local_port = 50006
remote_port = 7007

[ftp-data-50007]
type = tcp
local_ip = 192.168.191.20
local_port = 50007
remote_port = 7008

[ftp-data-50008]
type = tcp
local_ip = 192.168.191.20
local_port = 50008
remote_port = 7009

[ftp-data-50009]
type = tcp
local_ip = 192.168.191.20
local_port = 50009
remote_port = 7010
```

启动 frpc：

```bash
sudo ./frpc -c frpc.ini
```

### 二、公网服务器（43.139.236.50）配置

#### 1. 安装 frps

下载并安装 frp：

```bash
wget https://github.com/fatedier/frp/releases/download/v0.57.0/frp_0.57.0_linux_amd64.tar.gz
tar -zxvf frp_0.57.0_linux_amd64.tar.gz
cd frp_0.57.0_linux_amd64

或者 cd /root/frp_0.57.0_linux_amd64
```

#### 2. 配置 frps

编辑 `frps.ini` 配置文件：

```ini
[common]
bind_port = 7000
```

#### 3. 启动 frps

```bash
sudo ./frps -c frps.ini
```

### 三、FTP 客户端 / 相机的连接方式

相机或 FTP 客户端设置：

- **主机**: `43.139.236.50`
- **端口**: `7010`
- **模式**: 被动模式（PASV）必须打开

🎉 **这样即可让相机 FTP 完整通过公网服务器工作！**

## 为什么这是最佳兼容方案？

| 技术              | 是否支持 FTP / 相机 FTP | 稳定性 |
| ----------------- | ----------------------- | ------ |
| SSH 隧道          | ❌ 不支持被动模式        | 差     |
| Nginx/TCP 转发    | ❌ 无法处理 PASV         | 差     |
| Zerotier 直接访问 | ❌ 相机无法跑 Zerotier   | 不可用 |
| **FRP（推荐）**   | ✔️ ✔️ ✔️ 完整支持 FTP PASV | 强     |
| Tailscale Funnel  | ❌ 不支持 FTP            | 不可用 |



## 可以更多：

✅ 帮你生成自动启动脚本（systemd）
✅ 把 FRP 配置压缩到最少端口占用
✅ 根据你的相机品牌（Sony、Canon、Nikon）优化 FTP 设置
✅ 帮你测试 FTP 连接脚本

