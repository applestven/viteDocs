# Tailscale 使用指南

## 官方资源

- [官网](https://tailscale.com/)
- [官方文档](https://tailscale.com/kb/1017/tailscale-cli/)

## 一、基本部署（5分钟快速上手）

### 1. 注册账号

支持以下方式登录：
- Google
- Microsoft
- GitHub

注册地址：[https://tailscale.com](https://tailscale.com)

### 2. 安装客户端

支持平台：
- Windows / Mac / Linux
- NAS / 路由器 / 树莓派等设备

下载地址：[https://tailscale.com/download](https://tailscale.com/download)

### 3. 登录并授权

- 在客户端登录后，设备会出现在 Web 控制台的设备列表中。
- 可勾选「Enable subnet routes」以允许转发子网流量。
  + 子网路由的作用主要是实现“局域网访问穿透”
  + 子网路由 ≈ 家庭（或办公）内网的“集群入口” (子网路由可以理解为一个家庭内网集群 ， 开一个就行)
  + 公网服务器开启子网路由的双重作用 可能承担“中转加速”角色 (公网服务器多多加入)
  
``` bash

# 设备端如何开启广告子网路由
tailscale up --advertise-routes=你的子网段
# 例如 
sudo tailscale up --advertise-routes=192.168.0.0/24

#  192.168.0.0/24  广告整片局域网子网，允许远程访问子网内所有设备   效果 ：我这台设备可以帮大家访问这个局域网（子网）里的所有设备
# 203.0.113.5  单个公网地址 没必要设置

```

### 4. 测试直连

在终端运行命令测试连接：

```bash
tailscale ping <设备名或IP>
```

- 返回 `direct` 表示 P2P 直连成功；
- 返回 `via DERP` 表示通过中转节点通信。

## 二、优化直连成功率

Tailscale 的 P2P 连接依赖于 UDP 打洞技术，以下方法可提升成功率：

### 1. 使用公网 IP 或支持 UPnP 的路由器

- 家用宽带多为对称 NAT，较难打洞；
- 若有公网 IPv6，几乎可以保证直连。

### 2. 开启 IPv6 支持

- Tailscale 默认启用 IPv6；
- 若双方都有公网 IPv6，直连率接近 100%。

### 3. 多设备在线

- 更多设备在线有助于通过第三方中继建立连接（非 DERP）；
- 设备越多越容易打通网络。

## 三、自建 DERP 节点（核心提升方法）

DERP（Designated Encrypted Relay for Packets）是 Tailscale 的中转机制，自建节点的优势包括：

- **低延迟**：选择靠近你的 VPS 部署；
- **高可用性**：避免官方节点不稳定；
- **多点部署**：提高握手成功率。

### 部署步骤（Debian/Ubuntu 示例）

#### 1. 安装依赖

```bash
sudo apt update
sudo apt install git golang-go
```

#### 2. 拉取源码

```bash
git clone https://github.com/tailscale/tailscale.git
cd tailscale/cmd/derper
```

#### 3. 编译

```bash
go build
```

#### 4. 运行示例

```bash
./derper -hostname your.derp.domain.com -a :443
```

参数说明：
- `-hostname`：绑定域名（需提前解析到服务器 IP）
- 建议使用 HTTPS 证书（Let's Encrypt）

#### 5. 配置

在 Tailscale 控制台的 derpmap 配置文件里加入自己的节点

### 部署建议

- 香港 / 日本 / 新加坡 各放一个 VPS（低延迟）
- 服务器要有固定公网 IPv4 和 IPv6

## 四、最佳实践

1. 家里路由器、NAS、常开机的 PC 都装上 Tailscale → 充当"握手帮手"
2. 核心地区（如 HK、JP、新加坡）各部署一台 DERP 节点
3. 开启 IPv6，提升打洞成功率
4. 如果有公网 IPv4 设备，可以作为"超级节点"长期在线

✅ 这样部署后，一般家庭网络设备的 P2P 直连率能从 Zerotier 的 60-80% 提升到 90%+，而且中转时延迟也能压到 30-50ms 左右。