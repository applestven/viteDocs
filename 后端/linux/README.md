# 待完善
##  Ubuntu防火墙

1. sudo ufw status   inactive是关闭，active是开启 
2. sudo ufw disable  关闭防火墙
3. sudo ufw enable 开启防火墙 开启防火墙的状态下，只有系统允许的端口才能被其他主机访问。
4. sudo ufw reload 重启防火墙
5. sudo ufw allow [端口号]   开放指定端口号
6. sudo ufw delete allow [端口号]  关闭指定端口
7. sudo ufw deny [端口号] 不允许访问指定端口号 

## 开放SSH服务
sudo apt update
sudo apt install openssh-server
sudo systemctl start ssh
sudo systemctl enable ssh
sudo systemctl status ssh

如开防火墙 则 ：
sudo ufw allow 22

## vim 的使用  


## 改密
    passwd username 
## 改名
sudo mv oldname newname
## linux 命令收集 

netstat  -tunlp  v查看可访问的端口



## vim 工具使用 

### vim工具之自动排版
1. 进入命令行模式，按下ESC键。
2. 使用“gg”将光标移动到文档开头。
3. 输入“v”，进入visual模式。
4. 输入大写的“G”，这样就选中了全文。
5. 输入“=”，即可完成整个文档的自动排版。 

### vim 常用命令 

1. 保存和退出命令
`
:w  保存修改
:q  不保存修改退出
:wq   保存修改并退出；或者用 x!，在或者用 ESC+shift+ZZ；
:w 文件名；表示把当前文件的内容另存到指定文件里；相当于备份；

`

### vim 常用命令 
Linux vm编辑器中常用的命令有：
- 编辑命令：
    - vim +fileName ：进入vi编辑器。
    -ioa3个键其中一个：进入插入模式。
    -ESC键：退出插入模式。
    -回车键：结束命令。
    -Shift+;：进入底行模式。
    -Ctrl+zz：保存退出。
    -:wq ：写入退出。
    -:q ：退出，不保存。
    -:wq! ：写入退出，强制。
    -:q! ：强制退出，不保存。
- 行号命令：
    -:set nu ：显示行号。
    -:set nonu ：隐藏行号。
- 快速锁定命令：
    -gg ：到第一行。
    -G ：到最后一行。
    -:n ：到第n行。
- 撤销和恢复命令：
    -u ：相当于win下的ctrl+z。
    -ctrl+r ：相当于win下的ctrl+y。
- 替换字符命令：
    -R ：进入替换模式，按ESC结束。
- 删除命令：
    -x ：单个字符。
    -xn ：删除光标所在位置的n个字符。
    -dd ：删除本行。
    -ndd ：删除第n行。
    -dG ：删除本行以下的所有内容。
    -:x,yd ：删除第x~y行的内容。

这些命令在实际使用中可能会因版本不同而有所差异，具体的使用方法请参考vm编辑器的官方文档或相关教程。
