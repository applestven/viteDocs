## mysql基操
##  mysql的安装和常用命令（window）
1. 详细安装介绍 ： 
（下载免安装  二百多M的）

https://dev.mysql.com/downloads/mysql/

打开管理员权限的cmd窗口  ！

mysqld --install   安装  

mysqld --initialize --console  初始化   在返回得到随机密码 root@localhost: ves#jqrw&7vK

net start mysql 开启msql服务 ； 

mysql -u root -p登入   输入前面得到的随机密码   

alter user 'root'@'localhost' identified by '7796~36';     (by 接着的是密码)    修改密码


2. 配置sqlyog   在百度网盘  =》 学习工具有相关安装包

sqlyog链接报 2058   ； 百度tip:mysql加密方式不一样了 
执行下面的命令
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '123456';   
可以链接了 ？？？ QAQ  鬼知道为什么  

3. 常用命令   
 show global variables like 'port';      查看数据库端口  ；

show databases ;   查看数据库

再次在电脑安装 需要执行以下步骤才能解决：

1. 打开cmd：mysql -u root -p 
输入密码root
2.进入mysql依次执行下面语句
ALTER USER'root'@'localhost' IDENTIFIED BY 'root' PASSWORD EXPIRE NEVER; #修改加密规则 
ALTER USER'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root'; #更新一下用户的密码 
FLUSH PRIVILEGES; #刷新权限
重置密码：alter user'root'@'localhost' identified by '7796~36';

#忘记密码重新设置  ： https://www.cnblogs.com/wsl-/p/10688292.html


## ubuntu 数据库安装 初始化

  1. 安装
  sudo apt-get update 
  sudo apt-get install mysql-server


  1. 设置账号密码
  安装后 直接使用 sudo mysql  登陆root用户数据库
  修改账号密码 ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '2134567';
  刷新权限使更改生效 FLUSH PRIVILEGES;


  3. 数据库状态
   sudo systemctl status mysql

   开启服务 ：sudo systemctl start mysql 
   停止服务 ：sudo systemctl stop mysql

  4. 进行安全性配置：
  sudo mysql_secure_installation
  按照提示设置密码、删除匿名用户、禁止远程root登录等。

  5. 查询数据库端口 

netstat -tuln | grep mysql
