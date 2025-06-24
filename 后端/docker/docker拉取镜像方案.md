
## 1. 本地下载拉取

[docker镜像打包本地文件和本地文件转为镜像](https://blog.csdn.net/qq_30071431/article/details/144889123?fromshare=blogdetail&sharetype=blogdetail&sharerId=144889123&sharerefer=PC&sharesource=qq_30071431&sharefrom=from_link)


主要命令 ：

``` bash 
# 导出
docker save -o navidrome.tar deluan/navidrome:latest
# 下载
curl -L -o "nextcloud_latest.tar" "http://192.168.0.106:5421/api/download?filename=nextcloud_latest.tar&token=172325025886ced8b0fe9743dddd9fbb&timestamp=1735805233506"
# 导入
docker load -i nextcloud_image.tar
# 确认是否存在
docker images
```

## 2.使用clash代理局域网代理

1. 为 Docker 守护进程配置代理
- 使用 systemd 为 Docker 服务添加代理设置

```bash
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo nano /etc/systemd/system/docker.service.d/http-proxy.conf
```

- 输入以下内容（替换 192.168.8.105:7890 为你的代理地址）：

```bash
[Service]
Environment="HTTP_PROXY=http://192.168.8.105:7890"
Environment="HTTPS_PROXY=http://192.168.8.105:7890"
Environment="NO_PROXY=localhost,127.0.0.1,docker-registry.example.com"  # 可选，排除某些地址

```

- 保存后执行 
```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
``` 

2. 验证 Docker 代理配置

- 检查 Docker 服务是否加载了代理变量

```bash
sudo systemctl show docker --property Environment
```
如果输出包含你的代理地址，说明配置成功。

3. 测试 Docker 拉取镜像

```bash
docker pull redis
```

4. 可能的问题排查 
- DNS 解析：尝试在 Docker 配置中指定 DNS，如编辑 /etc/docker/daemon.json

```bash
sudo nona /etc/docker/daemon.json
```

```json

{
  "dns": ["8.8.8.8", "1.1.1.1"]
}
```