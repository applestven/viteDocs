## docker的安装
```bash  
apt  install docker.io 

```

## docker-compose的安装 

https://github.com/docker/compose/releases/ 

注意:需要根据你的服务器架构下载  这一步可能导致下面的安装失败

下载最新版本的docker-compose 

然后将文件下载到linux服务器

- 完整命令（一键执行）​：

``` bash
sudo curl -L "http://192.168.0.108:5421/api/download?filename=docker-compose-linux-x86_64&token=530e364fb62efef7a5f79dcefdbed5b1&timestamp=1746893110878" -o /usr/local/bin/docker-compose \
&& sudo chmod +x /usr/local/bin/docker-compose \
&& sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose \
&& docker-compose --version

```
