
## 生成密钥对
```bash
ssh-keygen -t rsa -b 4096  # 生成RSA 4096位密钥
```

## 上传公钥到服务器 (需要linux环境/git bash)

```bash
ssh-copy-id -i ~/.ssh/id_rsa.pub user@hostname  # 自动追加公钥到服务器的~/.ssh/authorized_keys[1,4](@ref)
```

## 配置~/.ssh/config

```bash

Host myserver
    HostName 192.168.1.100
    User username
    Port 2222
    IdentityFile ~/.ssh/id_rsa  # 指定私钥路径
    IdentitiesOnly yes          # 强制使用指定密钥[6](@ref)

Host 83.229.123.43
  HostName 83.229.123.43
  User root  


```

## SSH Agent管理密钥密码 (可选)
若生成密钥时设置了密码短语，可通过以下方式实现免重复输入：

```bash
eval $(ssh-agent)         # 启动Agent
ssh-add ~/.ssh/id_rsa     # 添加私钥并输入一次密码
```