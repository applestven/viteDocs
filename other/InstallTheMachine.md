
## 零刻ser5 max 装macOS黑苹果

https://baijiahao.baidu.com/s?id=1773166315272261509&wfr=spider&for=pc


## windows11系统安装ubuntu系统详细步骤

https://baijiahao.baidu.com/s?id=1769726314600485510&wfr=spider&for=pc

1. 打开windows功能，安装适用于linux的windows子系统、虚拟机平台

- win  搜索-windows 功能 
- 适用于linux的windows子系统、虚拟机平台 （勾上）
- 虚拟平台 （勾上）
- miscrosaft store 安装 windows Subsystem   for Linux 
- miscrosaft store 安装 ubuntu 
 
## 安装ubuntu系统详细步骤 

https://blog.csdn.net/wjz110201/article/details/129842440


1. 确认Windows系统
安装前需要确定Windows系统版本是否满足？

WSL 2 仅在 Windows 11 或 Windows 10 版本 1903、内部版本 18362 或更高版本中可用。通过按 Windows 徽标键 + R，检查你的 Windows 版本，然后键入 winver，选择“确定”。（或者在 Windows 命令提示符下输入 ver 命令）

2. 自动安装wsl
在管理员模式下打开 PowerShell 或 Windows 命令提示符，方法是右键单击并选择“以管理员身份运行”，输入 wsl --install 命令，然后重启计算机

wsl --install

3. 旧版WSL的手动安装步骤 （参考第一种安装方式）
为简单起见，通常建议使用 wsl --install 安装适用于 Linux 的 Windows 子系统，但如果运行的是旧版 Windows，则可能不支持这种方式。就必须使用手动安装！

4. 自动安装 以管理员身份打开 PowerShell（“开始”菜单 >“PowerShell” >单击右键 >“以管理员身份运行”），然后输入以下命令：
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
启用上面的功能后，重启电脑Windows系统

5. 启用虚拟机功能
安装 WSL 2 之前，必须启用“虚拟机平台”可选功能。 计算机需要虚拟化功能才能使用此功能。

以管理员身份打开 PowerShell 并运行：

6. 下载 Linux 内核更新包
   下载最新包：
软件下载链接：https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi

如果使用的是 ARM64 计算机，请下载 ARM64 包：https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_arm64.msi。 如果不确定自己计算机的类型，请打开命令提示符或 PowerShell，并输入：systeminfo | find “System Type”。 Caveat： 在非英文版 Windows 上，你可能必须修改搜索文本，对“System Type”字符串进行翻译。 你可能还需要对引号进行转义来用于 find 命令。 例如，在德语版中使用 systeminfo | find ‘“Systemtyp”’。

7. 将 WSL 2 设置为默认版本
打开 PowerShell，然后在安装新的 Linux 发行版时运行以下命令，将 WSL 2 设置为默认版本：

wsl --set-default-version 2

8. 安装所选的 Linux 分发
打开 Microsoft Store：https://aka.ms/wslstore，并选择你偏好的 Linux 分发版

9. 单击以下链接会打开每个分发版的 Microsoft Store 页面：

Ubuntu 20.04 LTS：https://www.microsoft.com/store/apps/9n6svws3rx71
Ubuntu 22.04 LTS：https://www.microsoft.com/store/apps/9PN20MSR04DW
Kali Linux：https://www.microsoft.com/store/apps/9PKR34TNCV07
Debian GNU/Linux：https://www.microsoft.com/store/apps/9MSVKQC78PK6
在分发版的页面中，选择“获取”

首次启动新安装的 Linux 分发版时，将打开一个控制台窗口，系统会要求你等待一分钟或两分钟，以便文件解压缩并存储到电脑上。 未来的所有启动时间应不到一秒。

然后，需要为新的 Linux 分发版创建用户帐户和密码：

这样就安装成功了，在PowerShell或cmd下输入wsl就可以切换到Linux子系统。有时会长时间无法进入，这可能是由于电脑内存空间不足造成，重启或等待

如果想退出wsl，只需要执行exit即可

10. WSL中使用adb
参考文章：https://blog.csdn.net/YuZhuQue/article/details/105773966（使用的是windows系统的adb）

找到你的adb 安装路径，我的是/mnt/c/tool/android-develpe-SDK/platform-tools/adb.exe,这里的 /mnt/c 对应的是C盘

vi ~/.bashrc 添加如下

``` js
# Android Debug Bridge
export PATH=$PATH:/mnt/c/tool/android-develpe-SDK/platform-tools/
alias adb='/mnt/c/tool/android-develpe-SDK/platform-tools/adb.exe'
```
重新打开终端或者执行 source ~/.bashrc

如果adb识别不到设备，可以使用adb kill-server杀一下server先



## wsl的相关命令 
- 列出可用的 Linux 发行版
wsl --list --online
- 列出已安装的 Linux 发行版
wsl --list --verbose  
- 进入Linux子系统
wsl
- 进入Linux的主目录
wsl ~
- 检查 WSL 版本
wsl --version   
- 关闭
wsl --shutdown
- Terminate
```shell
wsl --terminate <Distribution Name>
```
- 导入和导出发行版
```shell
wsl --export <Distribution Name> <FileName>
wsl --import <Distribution Name> <InstallLocation> <FileName>
```
- 注销或卸载 Linux 发行版
```shell
wsl --unregister <DistributionName>

```
如果将 DistributionName 替换为目标 Linux 发行版的名称，则将从 WSL 取消注册该发行版，以便可以重新安装或清理它。 警告：取消注册后，与该分发版关联的所有数据、设置和软件将永久丢失
- 安装
wsl --install
- 设置默认 Linux 发行版
```shell
wsl --set-default <Distribution Name>
```
- 更新 WSL
wsl --update
- 取消挂载磁盘
```shell
wsl --unmount <DiskPath>
```