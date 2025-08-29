## 常用脚本说明 

## latency_test.sh 测试各个服务器到本机的延迟 给出延迟排行前三的服务器



### 使用示例
```bash
./latency_test.sh
```

## nginx-port-proxy.sh  快速创建nginx端口代理



### 使用示例

1. 添加映射：

``` bash
sudo ./nginx-port-proxy.sh add 9000:100.123.18.75:3333 8080:192.168.1.50:80

# 将服务器本地9000端口映射到100.123.18.75:3333
sudo ./nginx-port-proxy.sh add 9000:100.123.18.75:3333
```


2. 删除映射：

``` bash
# 删除服务器使用脚本创建的9000 8000 端口映射
sudo ./nginx-port-proxy.sh del 9000 8080
```

