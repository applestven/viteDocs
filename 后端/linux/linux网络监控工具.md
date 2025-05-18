# linux网络监控工具


## bmon 图像工具监控网络带宽
```bash
sudo apt install bmon
bmon
```

## nload（简单直观）
虽然不是测速工具，但可实时查看网络流量，辅助排查问题。
```bash
sudo apt install nload
nload  # 按左右箭头切换网卡
```

##  使用 wget/curl 快速测试下载速度

通过下载大文件估算当前下载速度

``` bash
# 使用 wget 测试（例如 Ubuntu 官方镜像）
wget -O /dev/null http://releases.ubuntu.com/22.04/ubuntu-22.04-live-server-amd64.iso

# 使用 curl 测试
curl -o /dev/null https://example.com/largefile.zip

```

## fast-cli（测试 Netflix 的 Fast.com）
测试通过 Netflix 的服务器测速，适合检测未被 ISP 优化的真实速度。
```bash
# 需要 Node.js 环境
sudo apt install nodejs npm
sudo npm install -g fast-cli
```

## iperf3（内网速度测试）
安装：
```bash
sudo apt install iperf3
```
服务端：
```bash
iperf3 -s
``` 
客户端：
```bash
iperf3 -c <服务器IP>
```

## speedtest-cli（常用推荐）

```bash
# 通过 apt 安装（版本可能较旧）
sudo apt install speedtest-cli

# 或通过 pip 安装最新版（需先安装 pip）
sudo apt install python3-pip
pip3 install speedtest-cli

# 直接运行测试（自动选择最优服务器）
speedtest-cli

# 仅显示简洁结果（单位：Mbps）
speedtest-cli --simple

# 指定服务器（先列出可用服务器 ID）
speedtest-cli --list | head -n 10
speedtest-cli --server <服务器ID>
```


## 自动化定时测试（可选） 

```bash
# 编辑 cron 任务
crontab -e

# 添加以下行（使用 speedtest-cli 并输出到日志文件）
0 * * * * speedtest-cli --simple >> ~/speedtest.log  # 每小时执行
* * * * * /usr/bin/speedtest-cli --simple >> /home/apple/speedtest.log  #慎用 花了几十块钱 把我cpe流量跑完了 每分钟执行 可选快速查


# 查看完整日志
cat ~/speedtest.log

# 分页查看（支持翻页）
less ~/speedtest.log

# 查看最后 N 行（例如最后 5 次测试）
tail -n 5 ~/speedtest.log

# 实时监控新记录
# 持续跟踪日志更新（按 Ctrl+C 退出）
tail -f ~/speedtest.log
```


2. 日志格式解析
每行日志的默认格式如下（单位：Mbps）：

Ping: 12.345 ms
Download: 567.89 Mbit/s
Upload: 123.45 Mbit/s
示例日志片段：
Ping: 24.618 ms
Download: 256.34 Mbit/s
Upload: 45.67 Mbit/s
Ping: 18.742 ms
Download: 302.12 Mbit/s
Upload: 48.91 Mbit/s
3. 日志数据分析
通过命令行工具提取关键信息：

提取下载速度历史记录
```bash
grep "Download" ~/speedtest.log
```
计算平均下载速度
```bash
grep "Download" ~/speedtest.log | awk -F' ' '{sum+=$2} END {print "平均下载速度: " sum/NR " Mbit/s"}'
```
生成简易报告
```bash
echo "=== 网络速度统计 ==="
grep "Download" ~/speedtest.log | awk '{print "下载速度: "$2" Mbit/s"}'
grep "Upload" ~/speedtest.log | awk '{print "上传速度: "$2" Mbit/s"}'
```
4. 日志文件管理
自动分割日志（按日期）
修改 cron 任务，添加日期标记：

```bash
# 编辑 crontab
crontab -e
```
# 修改为以下内容（每天生成一个带日期的日志文件）
0 * * * * speedtest-cli --simple >> ~/speedtest_$(date +\%Y\%m\%d).log
手动清理旧日志
```bash
# 删除超过 30 天的日志
find ~/ -name "speedtest_*.log" -mtime +30 -delete
5. 常见问题排查
问题1：日志文件未生成
检查 cron 服务是否运行：
```
```bash
systemctl status cron
查看 cron 任务日志：
```
```bash
grep CRON /var/log/syslog
确保路径正确：~ 代表当前用户的家目录（如 /home/username/）。
```
问题2：权限不足
如果使用 sudo 设置 cron 任务，日志会写入 root 的家目录（/root/），建议以普通用户身份运行。

问题3：数据单位混淆
speedtest-cli 默认使用 Mbit/s（兆比特每秒），实际下载速度需除以 8 换算为 MB/s（兆字节每秒）。

6. 高级用法（可选）
生成可视化报告
使用 Python 脚本或工具（如 gnuplot）将日志转换为图表：

python
# 示例：安装 pandas + matplotlib 分析日志
pip3 install pandas matplotlib
编写脚本提取数据并绘制趋势图。

邮件报警
当速度低于阈值时自动发送通知：

``bash
# 在 cron 任务中添加条件判断
0 * * * * speedtest-cli --simple | awk '/Download/ {if ($2 < 100) print "警报: 低网速！"}' | mail -s "网络警报" your@email.com
```