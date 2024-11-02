## 网络节点 
zerotier-cli join e5cd7a9e1c1a655b

## ubuntu卸载zerotier
```bash
sudo apt-get remove zerotier-one
sudo rm -rf /etc/zerotier-one /var/lib/zerotier-one
```
##  加入 Moon 节点 
```bash
zerotier-cli join 000000afd4acfeb5 
```
## 查询节点是否已经加入 Moon 节点
``` bash
zerotier-cli listnetworks <node-id>

zerotier-cli listnetworks 也可以列出已经加入的网络 以及 moon节点
```
## 要检查是否成功加入 Moon 节点，可以运行
``` bash
zerotier-cli listpeers // 查所有的设备

zerotier-cli listmoons // 查所有的moon
```

