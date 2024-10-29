
## ubuntu 桌面版的远程连接 

远程  https://www.cnblogs.com/misaka10212/p/18304934

## ubuntu 镜像下载 

https://cn.ubuntu.com/download/server/thank-you?version=24.04.1&architecture=amd64

## [rufus](https://rufus.ie/) 
rufuns 启动盘制作软件
[Ubuntu18.04详细安装指南](https://juejin.cn/post/6844904136811479053?searchId=20241028171004B1239FCD268C44FEF87C)
## ubuntu的安装 

https://www.163987.com/jiaocheng/113669.html  服务器版

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
## ubuntu查看可访问的端口


## ubuntu 查询开放端口

```bash
ss -tuln
```

## ubuntu 修改文件夹所属 所有者

1.  sudo chown newuser /path/to/folder 修改当前文件夹 
1.  sudo chown -R newuser /path/to/folder  子文件夹递归

## ubutn 修改文件 文件夹权限 

chmod [权限选项] /path/to/folder

1. 755 所有者有读写执行权限，其他用户有读执行权限
2. 777 所有用户都有读写执行权限

    八进制模式：

    4 表示读权限

    2 表示写权限

    1 表示执行权限

    组合这些数字来表示所需的权限

    7 (4+2+1) 表示读、写和执行权限

    6 (4+2) 表示读和写权限

    5 (4+1) 表示读和执行权限

## ubuntu 查询 文件 文件夹 权限所属

ls -ld /path/to/example_folder

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