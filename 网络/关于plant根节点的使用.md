## 服务器配置 
请放行以下端口：9994/tcp,9994/udp，3443/tcp，3000/tcp

## zerotier 面板网络管理
访问 http://8.148.184.96:3443 进行配置
默认用户名：admin
默认密码：password
及时修改密码
---------------------------
moon配置和planet配置在 /root/docker-zerotier-planet/data/zerotier/dist 目录下
moons 文件下载： http://8.148.184.96:3000/000000058f411d2d.moon?key=691b1a3a03a9ff91
planet文件下载： http://8.148.184.96:3000/planet?key=691b1a3a03a9ff91


#### 3.5.2 网络面板管理 创建网络

1. 登录后点击 "Networks" 菜单
2. 点击 "Add Network" 按钮创建新网络
3. 输入一个便于识别的网络名称，其他选项可保持默认
4. 点击 "Create Network" 按钮完成创建


创建成功后系统会自动生成一个网络 ID，这个 ID 在后续客户端配置时会用到，请记录下来!

#### 3.5.3 分配网络 IP

1. 选中 "Easy Setup"

2. 生成 IP 范围

---

## 入网配置

客户端官网下载地址 

### 4.1 Windows 配置

#### 步骤 1：下载客户端
首先去 ZeroTier 官网下载一个 ZeroTier 客户端

#### 步骤 2：替换 planet 文件
将 `planet` 文件覆盖粘贴到 `C:\ProgramData\ZeroTier\One` 中（这个目录是个隐藏目录，需要允许查看隐藏目录才行）

#### 步骤 3：重启服务
1. 按 `Win + S` 搜索 "服务"


2. 找到 ZeroTier One，并且重启服务


#### 步骤 4：加入网络
使用管理员身份打开 PowerShell，执行如下命令：

```powershell
PS C:\Windows\system32> zerotier-cli.bat join 网络id
200 join OK
PS C:\Windows\system32>
```

> **注意**：网络 ID 就是在网页里面创建的那个网络 ID

#### 步骤 5：授权设备
登录管理后台可以看到有个新的客户端，勾选 `Authorized` 即可



IP assignment 里面会出现 ZeroTier 的内网 IP



#### 步骤 6：验证连接
执行如下命令验证连接状态：

```powershell
PS C:\Windows\system32> zerotier-cli.bat peers
200 peers
<ztaddr>   <ver>  <role> <lat> <link> <lastTX> <lastRX> <path>
fcbaeb9b6c 1.8.7  PLANET    52 DIRECT 16       8994     1.1.1.1/9993
fe92971aad 1.8.7  LEAF      14 DIRECT -1       4150     2.2.2.2/9993
PS C:\Windows\system32>
```

可以看到有一个 `PLANET` 和 `LEAF` 角色，连接方式均为 `DIRECT`（直连）

到这里就加入网络成功了！

### 4.2 Linux 客户端

**配置步骤：**

1. 安装 Linux 客户端软件
2. 进入目录 `/var/lib/zerotier-one`
3. 替换目录下的 `planet` 文件
4. 重启 `zerotier-one` 服务：`service zerotier-one restart`
5. 加入网络：`zerotier-cli join 网络id`
6. 管理后台同意加入请求
7. 执行 `zerotier-cli peers` 可以看到 `PLANET` 角色

### 4.3 安卓客户端配置

推荐使用 [Zerotier 非官方安卓客户端](https://github.com/kaaass/ZerotierFix)

### 4.4 MacOS 客户端配置

**配置步骤：**

1. 进入 `/Library/Application\ Support/ZeroTier/One/` 目录，并替换目录下的 `planet` 文件
2. 重启 ZeroTier-One：`cat /Library/Application\ Support/ZeroTier/One/zerotier-one.pid | sudo xargs kill`
3. 加入网络：`zerotier-cli join 网络id`
4. 管理后台同意加入请求
5. 执行 `zerotier-cli peers` 可以看到 `PLANET` 角色

### 4.5 OpenWRT 客户端配置

**配置步骤：**

1. 安装 ZeroTier 客户端
2. 进入目录 `/etc/config/zero/planet`
3. 替换目录下的 `planet` 文件
4. 在 OpenWRT 网页后台先关闭 ZeroTier 服务，再开启 ZeroTier 服务
5. 在 OpenWRT 网页后台加入网络
6. 管理后台同意加入请求
7. 执行 `ln -s /etc/config/zero /var/lib/zerotier-one`
8. 执行 `zerotier-cli peers` 可以看到 `PLANET` 角色

### 4.6 iOS 客户端配置

**方案一：越狱方案**
越狱后安装 ZeroTier，然后替换 `planet` 文件

**方案二：WireGuard 方案**
使用 WireGuard 接入到 ZeroTier 网络

---

## 总结入网 
1. 下载客户端配置 
2. 配置客户端 客户端替换plant文件 重启服务（很重要）
3. 加入网络
4. 管理面板同意入网（这一步决定其他节点是否能访问网络 也是管理安全重要的一步）
