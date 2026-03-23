## pm2的日志管理 包（轮转）和压缩管理
pm2 install pm2-logrotate

```bash
# 单个日志文件超过 10MB 自动分包
pm2 set pm2-logrotate:max_size 1M

# 每天凌晨 0 点轮转一次
pm2 set pm2-logrotate:rotateInterval '0 0 * * *'

# 保留最近 10 个轮转日志
pm2 set pm2-logrotate:retain 5

# 压缩轮转后的日志（gzip）
pm2 set pm2-logrotate:compress true

# 日志文件按天或大小切割后保留旧日志，避免占满磁盘
pm2 set pm2-logrotate:workerInterval 30
```



## pm2的日志位置

1. Linux / macOS

cd ~/.pm2/logs/     一般全路径   /home/apple/.pm2/logs 


2. Windows

C:\Users\<用户名>\.pm2\logs\


## pm2日志文件的转发

1. nginx 配置 
``` bash
server {
    listen 9797;
    server_name localhost;

    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
    }

    # TV 日志 UI + 文件访问
    location /logs/tv/ {
        alias /home/apple/code/tv/logs/;
        autoindex on;
        autoindex_exact_size off;
        autoindex_localtime on;

        charset utf-8;

        # 允许前端 fetch
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods GET,OPTIONS;
        add_header Access-Control-Allow-Headers *;
    }

    # pm2 日志 UI + 文件访问
    location /logs/pm2/ {
        alias /home/apple/.pm2/logs/;
        index index.html;
    }

    # 日志 API（强制 JSON 目录索引）
    location /logs/pm2/nginx-files/ {
        alias /home/apple/.pm2/logs/;
        autoindex on;
        autoindex_format json;
        index none;   # 不使用索引文件
    }


    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
```

重启nginx
sudo systemctl restart nginx

