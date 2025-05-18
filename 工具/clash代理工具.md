
## clash临时终端代理配置（仅当前会话）

```bash
export http_proxy="http://192.168.0.108:7890"
export https_proxy="http://192.168.0.108:7890"
```

```bash
export http_proxy="http://10.146.84.9:7890"
export https_proxy="http://10.146.84.9:7890"
```

## 测试代理
```bash
curl -x http://192.168.1.100:7890 https://ipinfo.io/ip
# 或直接使用环境变量
curl https://ipinfo.io/ip
```
若返回Clash服务器的IP，则代理成功


## 关闭代理
```bash
unset http_proxy https_proxy all_proxy
```

## 常见问题
​连接失败：检查Clash防火墙规则，确保端口开放（如Ubuntu使用UFW：sudo ufw allow out 7890）。
​协议不匹配：确认环境变量中的协议（http:// 或 socks5://）与端口一致。


## clash的使用 

1. 命令窗口需要另外配置才能使用代理 ，有没有办法直接使用代理 
**cmd:**
   set http_proxy=http://127.0.0.1:7890 & set https_proxy=http://127.0.0.1:7890

**powerShell:**
    $Env:http_proxy="http://127.0.0.1:7890";$Env:https_proxy="http://127.0.0.1:7890"

2. clash配置文件能不能使用node代码来切换代理 

预想步骤：

获取所有的能够使用的代理地址 

切换第几个地址