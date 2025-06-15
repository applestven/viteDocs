
## 搭建自己的服务网络 

``` pgsql
[每台服务器]
  ⬇️
运行 install-singbox.sh ⬅️ 自动输出 UUID、Reality 公钥等参数
  ⬇️
保存这些参数（可以存在本地 JSON 文件）

合并这些json文件 merge-nodes.js 

[主控端 / 本机]
  ⬇️
读取多个节点配置（JSON 文件或数组）
  ⬇️
运行 gen-subscription.js ⬅️ 合并为 clash.yaml
  ⬇️
提供 clash.yaml 给 Clash 客户端订阅
```




1. Docker 一键安装脚本（Ubuntu）
   
- install-singbox.sh

```bash
#!/bin/bash

echo "🧹 清理旧的 sing-box 容器..."
docker stop sing-box >/dev/null 2>&1
docker rm sing-box >/dev/null 2>&1

echo "🔧 安装 Docker..."
sudo apt update
sudo apt install -y docker.io

echo "📁 创建配置目录..."
mkdir -p /etc/sing-box

echo "🔑 生成 VMess UUID..."
uuid=$(cat /proc/sys/kernel/random/uuid)

read -p "请输入伪装域名（server_name）： " server_name

echo "📝 生成配置文件（使用 VMess + WebSocket + TLS）..."
cat > /etc/sing-box/config.json <<EOF
{
  "log": {
    "level": "info"
  },
  "inbounds": [
    {
      "type": "vmess",
      "listen": "0.0.0.0",
      "listen_port": 443,
      "users": [
        {
          "uuid": "$uuid"
        }
      ],
      "transport": {
        "type": "ws",
        "path": "/ws"
      },
      "tls": {
        "enabled": true,
        "server_name": "$server_name",
        "certificate_path": "/etc/sing-box/cert.pem",
        "key_path": "/etc/sing-box/private.key"
      }
    }
  ],
  "outbounds": [
    {
      "type": "direct"
    }
  ]
}
EOF

echo "📦 请确认 TLS 证书文件 cert.pem 和 private.key 已放入 /etc/sing-box/"

if [[ ! -f "/etc/sing-box/cert.pem" || ! -f "/etc/sing-box/private.key" ]]; then
  echo "❌ 未找到证书文件，请将 cert.pem 和 private.key 放入 /etc/sing-box/ 后重新执行此脚本"
  exit 1
fi

echo "🚀 启动 sing-box 容器..."
sudo docker run -d --name sing-box \
  -v /etc/sing-box/config.json:/etc/sing-box/config.json \
  -v /etc/sing-box/cert.pem:/etc/sing-box/cert.pem \
  -v /etc/sing-box/private.key:/etc/sing-box/private.key \
  -p 8443:443 \
  --restart unless-stopped \
  ghcr.io/sagernet/sing-box run -c /etc/sing-box/config.json

echo
echo "✅ sing-box 已部署完毕！连接信息如下："
echo "协议类型: vmess"
echo "地址: $(curl -s ifconfig.me)"
echo "端口: 8443"
echo "UUID: $uuid"
echo "TLS: ✅"
echo "WebSocket路径: /ws"
echo "伪装域名: $server_name"




# 使用方式：
# chmod +x install-singbox.sh
# sudo ./install-singbox.sh

# 生成的配置文件在 /etc/sing-box/node.json

# 野草云
# ✅ sing-box 已部署完毕！连接信息如下：
# 协议类型: vmess
# 地址: 2001:df1:7880:2::1883
# 端口: 443
# UUID: 03824724-b56b-41f1-b8c4-6a8e14737833
# TLS: ✅
# WebSocket路径: /ws
# 伪装域名: www.lovelive-anime.jp

# ucloud
# ✅ sing-box 已部署完毕！连接信息如下：
# 协议类型: vmess
# 地址: 123.58.219.234
# 端口: 8443
# UUID: 98c9535d-cc79-459c-aa10-c136efb79f0b
# TLS: ✅
# WebSocket路径: /ws
# 伪装域名: ucloud.itclass.top

```

2. 自动生成https 
  install-certbot.sh 

``` bash
 #!/bin/bash

read -p "请输入你的域名（已解析到当前服务器）: " domain

# echo "🧹 清理旧的 Nginx..."
# sudo apt update
# sudo apt install -y nginx

# echo "🛠️ 安装 Certbot..."
# sudo apt install -y certbot python3-certbot-nginx

echo "📁 启用域名配置..."
cat > /etc/nginx/sites-available/singbox <<EOF
server {
    listen 80;
    server_name $domain;

    location / {
        return 301 https://\$host\$request_uri;
    }
}
EOF

ln -sf /etc/nginx/sites-available/singbox /etc/nginx/sites-enabled/singbox
nginx -t && systemctl restart nginx

echo "🔐 申请 Let's Encrypt TLS 证书..."
sudo certbot --nginx --non-interactive --agree-tos --register-unsafely-without-email -d "$domain"

if [ ! -f /etc/letsencrypt/live/$domain/fullchain.pem ]; then
  echo "❌ 证书申请失败，请确认域名是否已正确解析。"
  exit 1
fi

echo "✅ 证书已申请成功，配置路径如下："
echo "/etc/letsencrypt/live/$domain/fullchain.pem"
echo "/etc/letsencrypt/live/$domain/privkey.pem"

echo "📁 拷贝证书到 sing-box 配置目录..."
mkdir -p /etc/sing-box
cp /etc/letsencrypt/live/$domain/fullchain.pem /etc/sing-box/cert.pem
cp /etc/letsencrypt/live/$domain/privkey.pem /etc/sing-box/private.key

echo "✅ 完成！请重新运行 sing-box 安装脚本以加载新证书。"


```

3. 查询服务器的uuid 

``` bash
cat /etc/sing-box/config.json | grep uuid
```



4. 合并各个服务器的json文件 

merge-nodes.js

```js
// merge-nodes.js
const fs = require('fs');
const path = require('path');

const folderPath = path.resolve(__dirname, 'nodes');
const outputPath = path.resolve(__dirname, 'nodes.json');

const files = fs.readdirSync(folderPath).filter(file => file.endsWith('.json'));

const nodes = files.map(file => {
  const fullPath = path.join(folderPath, file);
  const content = fs.readFileSync(fullPath, 'utf-8');
  try {
    return JSON.parse(content);
  } catch (err) {
    console.error(`❌ 无法解析文件 ${file}：${err.message}`);
    return null;
  }
}).filter(Boolean);

fs.writeFileSync(outputPath, JSON.stringify(nodes, null, 2));
console.log(`✅ 合并完成：${nodes.length} 个节点写入 nodes.json`);

```

# 3. 生成 clash.yaml
node gen-subscription.js


``` js
const fs = require('fs');
const yaml = require('yaml');

// 从 nodes.json 加载节点列表
const nodes = JSON.parse(fs.readFileSync('./nodes.json', 'utf8'));

const clashConfig = {
  proxies: nodes.map(n => ({
    name: n.name,
    type: "vless",
    server: n.server,
    port: n.port,
    uuid: n.uuid,
    network: "tcp",
    tls: true,
    "reality-opts": {
      "public-key": n.publicKey,
      "short-id": n.shortId,
      "server-name": n.serverName
    }
  })),
  "proxy-groups": [
    {
      name: "🚀 节点选择",
      type: "select",
      proxies: nodes.map(n => n.name)
    }
  ],
  rules: ["MATCH,🚀 节点选择"]
};

fs.writeFileSync('clash.yaml', yaml.stringify(clashConfig));
console.log("✅ 成功生成 clash.yaml");


```
