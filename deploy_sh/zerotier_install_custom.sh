## 安装并 加入自定义的plant 节点

## 1. 安装 ZeroTier
sudo apt reemove zerotier-one

sudo apt install zerotier-one

## 启动 ZeroTier
sudo systemctl start zerotier-one

## 进入目录 /var/lib/zerotier-one

## 删除原pllant 文件
rm -rf /var/lib/zerotier-one/planet

## 使用wget下载文件并保存为指定名称和路径
wget -O /var/lib/zerotier-one/planet "http://83.229.123.43:3000/planet?key=c7b1299681198500"

## 重启 ZeroTier
service zerotier-one restart

## 加入网络
zerotier-cli join bd404f7ed432d4b8