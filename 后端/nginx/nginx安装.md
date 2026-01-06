
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
        sudo ln -s /etc/nginx/sites-available/ip-proxy.conf /etc/nginx/sites-enabled/ip-proxy.conf

        sudo ln -s /etc/nginx/sites-available/dv-tv-8686.conf /etc/nginx/sites-enabled/dv-tv-8686.conf

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

