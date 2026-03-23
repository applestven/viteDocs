# 在 Nginx 上通过站点暴露日志目录（logs 目录）

本文档说明如何通过在 /etc/nginx/sites-available 下创建站点配置，向外暴露 Nginx 日志目录（/var/log/nginx）。适用于调试与运维查看日志场景。请注意安全风险，避免在公网直接暴露敏感日志。

前提：已安装 Nginx 并具有 sudo 权限。

## 1. 创建站点配置文件

使用编辑器创建文件：

```bash
sudo nano /etc/nginx/sites-available/log-panel.conf
```

## 2. 在nginx日志目录下创建index.html文件 
<!-- [index文件示例](./index.html) -->

## 3. 站点配置（可直接粘贴）

```nginx
server {
    listen 9797;
    server_name _;

    # 面板页面
    location /nginx/ {
        alias /var/log/nginx/;
        index index.html;
    }

    # 日志 API（强制 JSON 目录索引）
    location /nginx-files/ {
        alias /var/log/nginx/;

        # 禁用所有索引文件
        index nothing_here;  # 设置一个不存在的索引文件

        autoindex on;
        autoindex_format json;

        # 或者更彻底的方法：直接返回目录列表
        try_files $uri $uri/ =404;
    }

    error_log /var/log/nginx/log-panel-error.log;
    access_log /var/log/nginx/log-panel-access.log;
}
```

保存并退出：

- Ctrl + O
- Enter
- Ctrl + X

## 4. 启用站点（建立软链接）

```bash
sudo ln -s /etc/nginx/sites-available/log-panel.conf /etc/nginx/sites-enabled/log-panel.conf
```

如果提示已存在软链接：

```bash
sudo rm /etc/nginx/sites-enabled/log-panel.conf
sudo ln -s /etc/nginx/sites-available/log-panel.conf /etc/nginx/sites-enabled/log-panel.conf
```

## 5.（可选）禁用默认站点，避免端口冲突

```bash
sudo rm /etc/nginx/sites-enabled/default
```

```bash
sudo nginx -t
sudo systemctl reload nginx
# 如果 nginx 未运行：
sudo systemctl start nginx
```

## 7. 访问示例

在浏览器或 curl 中访问：

```
http://43.139.236.50:9943/nginx
http://43.139.236.50:9797/nginx-files/ 访问的是日志文件列表
```

示例：

```
http://192.168.191.222:9943/logs/access.log
```

## 8. 安全建议（强烈推荐）

直接暴露日志风险较高，建议至少采取一项保护措施：

- 使用 IP 白名单限制访问（allow / deny）；
- 使用 HTTP 基本认证（auth_basic + htpasswd）；
- 仅在内网或通过 VPN 访问；
- 若需对外提供，只导出需要的日志副本到受控目录并对其权限与访问做严格控制。

示例：在 location 中启用基本认证（需先用 htpasswd 创建密码文件）：

```nginx
location /logs/ {
    auth_basic "Restricted";
    auth_basic_user_file /etc/nginx/.htpasswd;
    alias /var/log/nginx/;
    autoindex on;
}
```

---

如需将文档内容调整为更严格的运维规范或加入示例脚本（如自动导出日志到指定目录并限制访问），可继续说明需求。
