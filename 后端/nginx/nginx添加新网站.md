## nginx 配置文件存放位置 - whereis nginx
```bash
cd /etc/nginx/sites-available
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
 sudo ln -s /etc/nginx/sites-available/tv.itclass.top /etc/nginx/sites-enabled/
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