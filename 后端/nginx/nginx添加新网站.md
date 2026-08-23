## 快捷命令 将本地8800端口转发局域网服务http://10.147.47.168:8800/

``` bash
sudo tee /etc/nginx/sites-available/nextcloud <<'EOF'
server {
    listen 8800;
    server_name nextcloud;
    location / {
        proxy_pass http://10.147.47.168:8800/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        client_max_body_size 10G;
    }
}
EOF
sudo ln -sf /etc/nginx/sites-available/nextcloud /etc/nginx/sites-enabled/ && sudo nginx -t && sudo systemctl reload nginx

```

## 快捷命令 删除相关软连接

``` bash
# 1. 删除软链接（禁用站点）
sudo rm -f /etc/nginx/sites-enabled/nextcloud

# 2. 删除配置文件
sudo rm -f /etc/nginx/sites-available/nextcloud

# 3. 测试配置
sudo nginx -t

# 4. 重载 Nginx
sudo systemctl reload nginx
```







## nginx 配置文件存放位置 - whereis nginx
```bash
cd /etc/nginx/sites-available
```

## 新建配置文件
```bash
sudo nano /etc/nginx/sites-available/tv.itclass.top
```

## default 模板

```bash
server {
    listen 80;
    server_name cloud.itclass.top;

    location / {
        proxy_pass http://10.146.84.20:8800;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

9191 转 7001

sudo nano /etc/nginx/sites-available/9191-7001.conf

server {
    listen 7001;
    
    location / {
        proxy_pass http://127.0.0.1:9191;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

```

## 启用站点

```bash
 sudo ln -s /etc/nginx/sites-available/nextcloud /etc/nginx/sites-enabled/

 sudo rm /etc/nginx/sites-enabled/nextcloud
```

## 测试配置文件

```bash
sudo nginx -t
```

## 重新加载 Nginx
```bash
sudo systemctl reload nginx
```

## 测试访问 

## nginx日志访问命令


# 实时监控访问日志（最常用）
tail -f /var/log/nginx/access.log

# 查看最后100行
tail -n 100 /var/log/nginx/access.log

# 查看全部内容
cat /var/log/nginx/access.log
