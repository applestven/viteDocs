## 编辑
```bash
sudo nano /etc/redis/redis.conf
```
- bind 127.0.0.1 ::1 改为
bind 0.0.0.0  # 或绑定到指定IP（如 bind 192.168.1.100 0.0.0.0）

## 如果未设置密码，需关闭保护模式（生产环境不推荐）
protected-mode no

## 设置密码（强烈建议）
requirepass your_strong_password

## 保存并重启Redis服务

``` bash
sudo systemctl restart redis-server
sudo systemctl status redis-server  # 检查服务状态

```

## 开放防火墙

ufw allow 6379

## 测试 
```bash
redis-cli -h <服务器IP> -p 6379 -a your_strong_password
```

## 其他
强密码保护
避免使用简单密码，推荐随机生成高强度密码。

限制IP访问（可选）
在防火墙或安全组中仅允许特定IP访问6379端口。

启用SSH隧道（推荐）
避免直接暴露Redis端口，通过SSH加密访问：

bash
ssh -L 6379:localhost:6379 user@your_server_ip
定期备份数据
使用 SAVE 或 BGSAAVE 命令备份Redis数据。