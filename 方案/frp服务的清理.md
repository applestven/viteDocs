📌 总原则

不删除系统关键软件（vsftpd 等）

只清除 frp 旧版本、残留配置、冲突端口占用、systemd 服务

清理后不会影响内网/公网的其他服务

为干净重装做准备

-----------------------------------------
🟦 一、内网服务器（192.168.191.20）清理环境
-----------------------------------------
① 停止旧 frpc（如果有）
sudo pkill -f frpc

② 删除旧 FRP 文件夹（如果存在）

常见安装目录可能在：

/usr/local/frp

/etc/frp

当前用户目录解压的 frp_0.XX.X_linux_amd64

全部可以安全删除：

sudo rm -rf /usr/local/frp
sudo rm -rf /etc/frp
rm -rf frp_*/  # 在你的家目录或临时目录

③ 删除旧的 systemd 启动项（如果曾注册过）
sudo rm -f /etc/systemd/system/frpc.service
sudo systemctl daemon-reload


检查是否还在：

systemctl status frpc


若显示 "Unit frpc.service could not be found"，说明已清干净。

④ 清理残留端口占用（21, 50000–50010）

查看占用：

sudo lsof -i:21
sudo lsof -i:50000-50010


如果看到 frpc、dockerd 或 unknown 占用，直接 kill：

sudo fuser -k 21/tcp
sudo fuser -k 50000-50010/tcp

⑤ 不动 FTP 服务，只重置被动端口设置（可选）

如果之前改乱了 vsftpd 配置，恢复为最小工作状态：

sudo sed -i '/pasv/d' /etc/vsftpd.conf
sudo systemctl restart vsftpd


稍后会重新写入新的 PASV 配置。

-----------------------------------------
🟦 二、公网服务器（43.139.236.50）清理环境
-----------------------------------------
① 停止旧 frps
sudo pkill -f frps

② 删除旧 FRP 目录
sudo rm -rf /usr/local/frp
sudo rm -rf /etc/frp
rm -rf frp_*/ 

③ 删除 systemd 残留
sudo rm -f /etc/systemd/system/frps.service
sudo systemctl daemon-reload


检查：

systemctl status frps


正常输出应是找不到 service。

④ 清理端口占用（7000 ~ 7010）

检查：

sudo lsof -i:7000-7010


清理：

sudo fuser -k 7000-7010/tcp


确保所有端口都释放，避免影响新的 FRP。

-----------------------------------------
🟦 三、ZeroTier 环境不会影响 FTP/FRP（无需清理）
-----------------------------------------

ZeroTier 在这套方案中只负责让公网服务器访问内网服务器
并不会影响 FTP/FRP
无需停止或清除。

-----------------------------------------
🟦 四、最终确认（两台机器都执行）
-----------------------------------------

执行以下命令确保系统中没有 FRP 残留：

pgrep -f frp


若没有输出 → 表示干净。

检查 FRP 配置文件：

sudo find / -name "frpc.ini"
sudo find / -name "frps.ini"


如果需要清除：

sudo rm -f 路径

✅ 清理完成后，你就可以继续执行我之前提供的「最佳 FRP 配置方案」。