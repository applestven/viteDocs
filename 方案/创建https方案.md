魔法通道 ：Let's Encrypt获取以及部署最佳方式  ubuntu nginx   pay.itclass.top vmq.itclass.top

## 获取证书 安装 Certbot
Certbot 是一个用于从 Let's Encrypt 获取 SSL 证书的工具。首先，更新你的软件包列表并安装 Certbot：
``` bash
sudo apt update
sudo apt install certbot python3-certbot-nginx

```

中间省略nginx配置好了pay.itclass.top vmq.itclass.top

## 使用 Certbot 获取 SSL 证书

``` bash

sudo certbot --nginx -d pay.itclass.top -d vmq.itclass.top

```

Certbot 会自动进行以下操作：

自动验证域名。

安装 SSL 证书并配置 Nginx 使用 HTTPS。

配置自动续期。

## 配置自动续期
Let's Encrypt 的证书有效期为 90 天，因此你需要定期续期它们。Certbot 会自动为你配置续期任务，默认情况下会在 /etc/cron.d 中设置续期任务

你可以手动测试续期是否工作：

```bash
sudo certbot renew --dry-run

```
到这里就完成了 。。。

## 为其他域名添加证书步骤 

1. 使用 Certbot 获取并配置 HTTPS
``` bash
sudo certbot --nginx -d tv.itclass.top
```

这就完成了 一般都是90天 续期手动测试 

```bash
sudo certbot renew --dry-run


```