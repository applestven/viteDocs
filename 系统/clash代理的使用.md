## 测试代理是否通畅

curl -x http://192.168.8.108:7890 https://www.google.com -I

或 SOCKS5 代理测试：

curl --socks5 192.168.8.108:7890 https://www.google.com -I


如果提示 Connection refused 或卡住，说明代理没开或不是这个 IP/端口。


## 临时设置代理 

```bash
cmd

set http_proxy=http://192.168.8.108:7890 & set https_proxy=http://192.168.8.108:7890


powershell

$Env:http_proxy="http://192.168.8.108:7890";$Env:https_proxy="http://192.168.8.108:7890"


ubuntu

export http_proxy=http://192.168.8.105:7890
export https_proxy=http://192.168.8.105:7890
export all_proxy=socks5://192.168.8.105:7890
```

## 去掉代理

unset https_proxy
unset http_proxy
unset all_proxy

## 永久设置代理

``` bash
nano ~/.bashrc

# 文件末尾添加

# === Proxy Settings ===
export http_proxy="http://10.146.84.213:7890"
export https_proxy="http://10.146.84.213:7890"
export all_proxy="socks5://10.146.84.213:7890"


# 保存后执行    
source ~/.bashrc


```
