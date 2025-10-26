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
