# nginx 基础
## whereis nginx  返回关于 Nginx 的一些路径信息
    
   通常情况下 Nginx 的配置文件位于 /etc/nginx 目录下  在该目录下找到 Nginx 的配置文件，如 nginx.conf 或者其他以 .conf 结尾的文件

 1.  编辑命令 
   sudo vim /etc/nginx/nginx.conf
   
   
## 重启使得修改的nginx配置文件生效
sudo nginx -s reload


## 查询 nginx 状态 

sudo systemctl status nginx

## 启动 Nginx 服务 

sudo systemctl start nginx

## ubuntu 安装nginx 并配置nginx

- 1. 确保你的系统包列表是最新的  sudo apt update

- 2. 安装 Nginx： sudo apt install nginx

- 3. 检查 Nginx 状态 是否正在运行：sudo systemctl status nginx

+ 4 配置 Nginx 

    - Nginx 的主配置文件位于 /etc/nginx/nginx.conf。通常情况下，你不需要修改这个文件，而是修改站点特定的配置文件
    - 创建站点配置文件 假设你要为一个名为 example.com 的网站创建配置文件，可以按照以下步骤操作
    - 4.1 创建示例 HTML 文件：sudo mkdir -p /var/www/example.com/html
    - 4.2 配置站点：设置权限
        ``` bash
            sudo chown -R www-data:www-data /var/www/example.com/html
            sudo chmod -R 755 /var/www/example.com
        ```
    - 4.3 创建示例 HTML 文件：

        ```bash
        sudo nano /var/www/example.com/html/index.html
        ```
    -   写入 HTML 文件：
        ``` html
        <!DOCTYPE html>
        <html>
        <head>
            <title>Welcome to Example.com</title>
        </head>
        <body>
            <h1>Success! The example.com server block is working!</h1>
        </body>
        </html>
        ```
    - 4.4  创建站点配置文件
    ``` bash
        sudo nano /etc/nginx/sites-available/example.com
    ```
    - 写入
    ```bash
        server {
            listen 80;
            server_name example.com www.example.com;

            root /var/www/example.com/html;
            index index.html;

            location / {
                try_files $uri $uri/ =404;
            }
        }
    ```
    - 4.5 启用站点：
    ```bash
        sudo ln -s /etc/nginx/sites-available/example.com /etc/nginx/sites-enabled/
    ```
    - 4.6 测试配置文件：
    ```bash
        sudo nginx -t
    ```
    - 如果配置文件没有问题，你会看到类似于 syntax is ok 和 test is successful 的输出。
    - 4.7 重新加载 Nginx
    ```bash
        sudo systemctl reload nginx
    ```
    
5. 配置防火墙    
    如果你的系统启用了 UFW（Uncomplicated Firewall），需要允许 HTTP 流量通过：
    
- sudo ufw allow 'Nginx Full'

6. 访问你的网站

打开浏览器，访问 http://example.com 或 http://your_server_ip，你应该会看到你刚刚创建的页面



## 配置代理服务器配置 



```
server {
    listen 80;
    server_name api.itclass.top;

    location / {
        proxy_pass http://43.139.236.50/api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```









# 其他笔记


1. 进入nginx容器进行相关配置
 ```bash 
 ## whereis nginx #可以在容器中查询出nginx的相关配置文件存放位置
 ```
文件夹 nodePro docke-compose 部署 两个node应用示例


2. 进入容器后 查询nginx配置文件存放位置
```bash
    /etc/nginx/nginx.conf
```

3. 查询nginx代理日志 
```bash
sudo tail -f /var/log/nginx/access.log
```
    


## nas配置nginx过程  
部署 vue前端应用
1. 通过containerStation 安装 nginx 
2. 查询nginx相关配置文件存放位置  进入nginx容器   whereis nginx 
3. 在finalshell上传需要部署的文件（/share/temporary） | 
    | 将本地文件拷贝到docker容器文件内（使用finalshell ssh连接nas ）
    | docker cp 你的文件路径 容器长ID:docker容器路径  

4. 配置nginx文件 ： 
```bash
user  nginx;
worker_processes  1;

error_log  /var/log/nginx/error.log warn;
pid        /var/run/nginx.pid;


events {
    worker_connections  1024;
}


http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    #tcp_nopush     on;

    keepalive_timeout  65;

    #gzip  on;

    server {
        listen       80;
        server_name  localhost;

        #charset koi8-r;

        #access_log  logs/host.access.log  main;
        location / {
            root /share/temporary/h5;
            try_files $uri $uri/ /index.html;
            index  index.html index.htm;
        }
    }
}
```

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




