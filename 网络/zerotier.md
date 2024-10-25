## zerotier 组网 
搭建根 plant
https://zhuanlan.zhihu.com/p/544807922     可以参考其思路 ，但下载链接不能使用
https://blog.csdn.net/smzq123/article/details/128760942  可以参考其思路 ，但下载链接不能使用
https://zhuanlan.zhihu.com/p/573746661?utm_id=0    有一定基础再参考 
https://www.west.cn/docs/408273.html    安装 zerotier 服务端



https://blog.csdn.net/smzq123/article/details/128760942  

https://zhuanlan.zhihu.com/p/605544905      主要参考



#zerotier安全组说明
#ztncui Web控制面板使用的端口。可以自行选择端口，根据自己选择端口配置安全组
TCP:3443
# Zerotier节点与控制器通讯的端口，可自行选择端口，根据自己选择的端口配置安全组
TCP:9993
#MOON节点与控制器通讯的中继端口，可自行选择端口，根据自己选择的端口配置安全组
UDP:9993
#需要分别设置ipv4和ipv6的规则

## ubuntu卸载zerotier

sudo apt-get remove zerotier-one
sudo rm -rf /etc/zerotier-one /var/lib/zerotier-one

## zeriter moon 节点 000000afd4acfeb5


###  加入 Moon 节点
zerotier-cli join 000000afd4acfeb5 

### 要检查是否成功加入 Moon 节点，可以运行

zerotier-cli listpeers // 查所有的设备

zerotier-cli listmoons // 查所有的moon
