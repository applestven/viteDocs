## powershell 设置中文

- 设置允许加载脚本


- 短期生效
1. 输入：
``` powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```
- 长期生效   

1. 可以通过修改PowerShell的profile文件来实现。首先，以管理员身份打开PowerShell，并运行下面指令来创建或覆盖profile文件

``` powershell
New-Item $PROFILE -ItemType File -Force

```
2. 然后，打开C盘，找到我的文档中搜索WindowsPowerShell文件夹，编辑里面ps1文件（默认是空的），加上以下代码$

``` powershell
[console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false
```
3. 重新打开即生效

## cmd 设置中文

- 短期生效
``` powershell
chcp 65001
```
- 长期生效
   
需要修改注册表。按win+r，输入regedit运行，进入注册表，找到HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Command Processor，新建一个名为autorun的字符串值，并将其值设为chcp 65001。这样每次启动cmd时都会自动更改编码为UTF-812




## window 打开自动运行 目录 命令 

``` bash
    shell:Common Startup
```

## window 给命令起别名 

在Windows命令行（CMD）中为命令创建别名，可以使用doskey命令或者创建一个批处理文件来持久化这些别名

1. 创建批处理文件 

``` bat 
    @echo off
    doskey p=pnpm $*
    doskey n=npm $*
```

2. 将批处理文件 放入到自动运行目录中 

