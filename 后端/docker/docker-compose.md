## 通过 docker-compose 部署 多应用程序 （nas）

1. 通过 docker-compose部署demo  : 
隐藏参考文件 ： nodePro （包括前后端的访问 内外网映射）
- docker-compose多容器启动 node项目、 nginx（）   docker-compose.yml
- nginx nginx映射配置 前端项目地址访问  default.conf 
- nodejs nodejs2 两个后端项目 
- statc文件夹 前端项目存放地址  
（未完待续 完成水平扩展 负载均衡 nginx的水平扩展  不停机更新 版本回滚等）

2. 仿照demo nodePro 去部署一个前后端一体的项目 千里云课堂 （mysql + vue + express ）


## docker mysql 导入sql文件 

在容器内操作 ：  
mysql -uroot -p test < test.sql

mysql -uroot -p payment < /home/temporary/payment.sql 

mysql 基础操作 ： 
show databases  ;  显示数据库表 
USE payment;  选中数据库 
DESCRIBE adminpay;  // 查询数据库表结构 

## mysql 查询 对外端口 
进入mysql 

show global variables like 'port';

## docker启动MySQL后 其他应用如何连接 MySQL

##  查看 启动的nodejs的日志

 pm2 logs

## docker 查可用版本  


