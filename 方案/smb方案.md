

```bash
sudo apt update && sudo apt install -y samba && sudo bash -c 'echo -e "[share]\n   path = /home/apple/nextcloud/share\n   browsable = yes\n   read only = no\n   guest ok = yes\n" >> /etc/samba/smb.conf' && sudo systemctl restart smbd

```

解释一下这个命令做了什么：

apt update && apt install -y samba → 安装 Samba。

bash -c 'echo ... >> /etc/samba/smb.conf' → 在 Samba 配置文件里添加共享定义。

[share] → 共享名字

path = /home/apple/nextcloud/share → 共享的本地路径

browsable = yes → 可以在网络浏览器中看到

read only = no → 可写

guest ok = yes → 不需要账号即可访问

systemctl restart smbd → 重启 Samba 服务使配置生效。

✅ 之后在 Windows 或 Mac 上可以直接通过 \\<ubuntu-ip>\share 访问。


## 配置文件
sudo nano /etc/samba/smb.conf



[share]
   path = /home/apple/nextcloud/share
   browsable = yes
   read only = no
   guest ok = no
   valid users = apple

- 说明
guest ok = no → 禁止访客访问
valid users = apple → 只有 apple 用户能访问


sudo systemctl restart smbd nmbd

## 创建账号 

sudo smbpasswd -a apple

sudo systemctl restart smbd nmbd
