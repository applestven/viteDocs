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
            server_name itclass.top apis.itclass.top;

            root /var/www/apis.itclass.top/html;
            index index.html;

            location / {
                try_files $uri $uri/ =404;
            }
        }
    ```
    - 4.5 启用站点：
    ```bash
        sudo ln -s /etc/nginx/sites-available/vmq.itclass.top /etc/nginx/sites-enabled/

        sudo ln -s /etc/nginx/sites-available/vmq.itclass.top /etc/nginx/sites-enabled/
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

打开浏览器，访问 http://apis.itclass.top 或 http://your_server_ip，你应该会看到你刚刚创建的页面



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

## 一步很重要 http { include /etc/nginx/sites-enabled/*;}
## nginx 初始化配置

```bash
worker_processes auto;

error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
```

## 配置music.itclass.top的过程
1. 添加域名解析 music.itclass.top
2. 在nginx中添加 nano /etc/nginx/sites-available/music.itclass.top
   ```
    server {
        listen 80;
        server_name music.itclass.top;

        location / {
            proxy_pass http://10.146.84.20:4533;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            }
        }

   ```
3. 检查添加文件是否有错误/重新加载nginx 
   ```
    sudo nginx -t
    sudo systemctl reload nginx
   ```
4. 查看sites-available目录下的文件没有反应，可能是因为该配置文件没有被链接到sites-enabled目录   
``` bash
    ls -l /etc/nginx/sites-enabled/
 ```
5. 查找是否有music.itclass.top的链接。如果没有，你需要创建它  重新启动
   ``` bash
    sudo ln -s /etc/nginx/sites-available/music.itclass.top /etc/nginx/sites-enabled/
   ```
