
## ubuntu 桌面版的远程连接 

远程  https://www.cnblogs.com/misaka10212/p/18304934

## ubuntu 镜像下载 

https://cn.ubuntu.com/download/server/thank-you?version=24.04.1&architecture=amd64

## [rufus](https://rufus.ie/) 
https://rufus.ie/
rufuns 启动盘制作软件
[Ubuntu18.04详细安装指南](https://juejin.cn/post/6844904136811479053?searchId=20241028171004B1239FCD268C44FEF87C)
## ubuntu的安装 

https://ubuntu.com/download/desktop  桌面版

## ubuntu测网速

1. 安装speedtest-cli
```bash
sudo apt update
sudo apt install speedtest-cli
```
2. 测速
```bash
speedtest-cli
```

## ubuntu查询内存 
cat /proc/meminfo

## ubuntu查询内存状态 
free -h

## ubuntu 查询cpu状态

top

## ubuntu 查询磁盘状态

df -h

## ubuntu 查询磁盘使用情况

du -sh /path/to/folder


## ubuntu 查询进程

ps -ef | grep process_name

## ubuntu 查询进程id

ps -ef | grep process_name | grep -v grep | awk '{print $2}'

## ubuntu 查询进程id并杀死

ps -ef | grep process_name | grep -v grep | awk '{print $2}' | xargs kill -9