## 网络节点 
zerotier-cli join e5cd7a9e1c1a655b

## zerotier官网下载地址 

https://www.zerotier.com/download/#entry-3

## ubuntu卸载zerotier
```bash
sudo apt-get remove zerotier-one
sudo rm -rf /etc/zerotier-one /var/lib/zerotier-one
```
## window卸载zerotier
1. 打开控制面板：
   - 按 `Win + R` 键，输入 `control`，然后按回车键。

2. 进入程序和功能：
   - 在控制面板中，找到并点击“程序和功能”。

3. 卸载 ZeroTier：
   - 在程序和功能列表中，找到 ZeroTier One，右键点击它，然后选择“卸载”。

4. 按照提示完成卸载：
   - 按照卸载向导的提示操作，直到完成卸载过程。

##  加入 Moon 节点 
```bash
zerotier-cli join 000000afd4acfeb5 
```
## 查询节点是否已经加入 Moon 节点
``` bash
zerotier-cli listnetworks <node-id>

zerotier-cli listnetworks 也可以列出已经加入的网络 以及 moon节点
```
## 要检查是否成功加入 Moon 节点，可以运行
``` bash
zerotier-cli listpeers // 查所有的设备

zerotier-cli listmoons // 查所有的moon
```

## 脚本安装plant
https://github.com/xubiaolin/docker-zerotier-planet

---------------------------
请访问 http://83.229.123.43:9999 进行配置
默认用户名：admin
默认密码：7796~36aA
请及时修改密码
---------------------------
moon配置和planet配置在 /root/docker-zerotier-planet/data/zerotier/dist 目录下
moons 文件下载： http://83.229.123.43:3000/000000bd404f7ed4.moon?key=c7b1299681198500 
planet文件下载： http://83.229.123.43:3000/planet?key=c7b1299681198500


## 网络id 
zerotier-cli.bat join bd404f7ed432d4b8