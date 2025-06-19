#!/bin/bash

# Nginx静态服务配置脚本
# 需要以root权限运行

# 检查root权限
if [ "$(id -u)" != "0" ]; then
   echo "错误：此脚本必须以root权限运行" 
   exit 1
fi

# 获取用户输入
read -p "请输入域名（如 update.itclass.top）: " domain_name
read -p "请输入静态资源目录（如 /home/ubuntu/www）: " resource_dir

# 验证输入
if [[ -z "$domain_name" || -z "$resource_dir" ]]; then
    echo "错误：域名和目录不能为空！"
    exit 1
fi

# 解决父目录权限问题（关键修复）
echo "正在设置父目录权限..."
parent_dir=$(dirname "$resource_dir")
while [ "$parent_dir" != "/" ]; do
    # 确保父目录有执行权限
    chmod o+x "$parent_dir" 2>/dev/null
    parent_dir=$(dirname "$parent_dir")
done

# 确保资源目录权限
echo "正在设置资源目录权限..."
mkdir -p "$resource_dir"
chown -R www-data:www-data "$resource_dir"
chmod -R 755 "$resource_dir"

# 创建Nginx配置文件
config_file="/etc/nginx/sites-available/$domain_name"

cat > "$config_file" <<EOF
server {
    listen 80;
    server_name $domain_name;
    
    root $resource_dir;
    index index.html index.htm;
    
    # 关键修复：关闭sendfile
    sendfile off;
    
    # 安全设置
    server_tokens off;
    add_header X-Content-Type-Options "nosniff";
    add_header X-Frame-Options "SAMEORIGIN";
    
    location / {
        try_files \$uri \$uri/ =404;
        
        # 缓存静态资源
        location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
            expires 30d;
            add_header Cache-Control "public, no-transform";
        }
    }
    
    # 禁止访问隐藏文件
    location ~ /\. {
        deny all;
    }
    
    # 自定义错误页
    error_page 403 /403.html;
    error_page 404 /404.html;
    location = /403.html {
        internal;
    }
    location = /404.html {
        internal;
    }
}
EOF

# 创建启用链接
if [ ! -f "/etc/nginx/sites-enabled/$domain_name" ]; then
    ln -s "$config_file" "/etc/nginx/sites-enabled/"
fi

# 测试并重载Nginx配置
echo "正在测试Nginx配置..."
nginx -t

if [ $? -eq 0 ]; then
    systemctl restart nginx
    echo "✅ 配置成功！"
    
    # 创建测试文件
    test_file="$resource_dir/test.html"
    cat > "$test_file" <<EOF
<!DOCTYPE html>
<html>
<head>
    <title>$domain_name 测试页</title>
</head>
<body>
    <h1>恭喜！$domain_name 已配置成功</h1>
    <p>静态资源目录: $resource_dir</p>
    <p>服务器时间: $(date)</p>
</body>
</html>
EOF
    chown www-data:www-data "$test_file"
    
    echo "----------------------------------------"
    echo "域名: $domain_name"
    echo "资源目录: $resource_dir"
    echo "测试命令: curl http://$domain_name/test.html"
    
    # 显示完整权限路径
    echo -e "\n完整路径权限:"
    namei -l "$resource_dir"
    echo -e "\n测试文件内容:"
    curl -s "http://$domain_name/test.html"
else
    echo "❌ Nginx配置测试失败，请检查错误日志"
    echo "查看错误日志: tail -f /var/log/nginx/error.log"
    exit 1
fi