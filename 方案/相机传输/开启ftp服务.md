# 1. 安装 vsftpd
sudo apt update
sudo apt install vsftpd -y

# 2. 启动服务并设置为开机自启
sudo systemctl enable vsftpd
sudo systemctl start vsftpd

# 3. 再次验证是否成功
sudo systemctl status vsftpd
ftp localhost   # 这时应该能看到欢迎信息了