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
