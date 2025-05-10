
# ubuntu
## 安装软件前
```bash
sudo -i 
apt update
```
## git的安装
```bash
apt install git 
```
```bash
git --version
```
## git的配置
```bash
git config --global user.name "apple"
git config --global user.email "beelink@gail.com"
```       
## linux允许ssh远程连接

1. 安装 OpenSSH 服务器
```bash
sudo apt update
sudo apt install openssh-server
```

2. 启动 SSH 服务并设置开机自启
```bash
sudo systemctl start ssh    # 启动服务
sudo systemctl enable ssh   # 开机自启
```

3. 检查服务状态
```bash
sudo systemctl status ssh
```
4. 配置防火墙（如果启用）​
```bash
sudo ufw allow ssh 
```
- or 直接指定
```bash
sudo ufw allow 22/tcp
```


5. 获取服务器 IP 地址
```bash
ip a
```
6. 从其他设备测试连接

ssh 用户名@服务器IP

7. 其他 
- 修改 SSH 端口​（编辑配置文件后重启服务）：
```bash
sudo nano /etc/ssh/sshd_config
```
- ​禁用密码登录（仅用密钥）​：在 sshd_config 中设置： 

PasswordAuthentication no


