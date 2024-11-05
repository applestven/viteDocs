## nvm node版本管理

1. nvm 下载地址 ： 
https://github.com/coreybutler/nvm-windows/releases

安装成功后 node -v npm -v 测试不成功 

- 更改配置文件，自动下载npm
    + 命令行运行：nvm root 显示出nvm的安装目录
    + 打开nvm文件夹下的settings.txt文件，在最后添加以下代码：
    node_mirror: https://npm.taobao.org/mirrors/node/
    npm_mirror: https://npm.taobao.org/mirrors/npm/

- nvm install 14.20.0
- nvm use 14.20.0

## 常用命令 
 nvm list available    显示可下载版本的部分列表
nvm install node@8.12.0         // 安装8.12.0版本的node 
nvm install 8.12.0
nvm uninstall node@8.12.0       	// 卸载node
nvm -v(-version)              // 查看nvm版本（检测是否安装上）
nvm ls                   //查看当前通过nvm管理的node
nvm use    10.12.0             //切换node版本，node10.12.0版本
node -v      

## linux安装nvm
## linux安装nvm方法一 使用 curl 或者weget命令获取 nvm 安装脚本（这种执行慢，需要看几率 有墙）
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.38.0/install.sh | bash
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.2/install.sh | bash
```

## linux安装nvm方法一（推荐，多几个步骤，但是安装快）
```bash
wget https://github.com/nvm-sh/nvm/archive/refs/tags/v0.38.0.tar.gz

mkdir -p /root/.nvm

tar -zxvf v0.38.0.tar.gz -C /home/apple/soft

vim ~/.bashrc 
```

1. 插入文件.bashrc 

```bash
export NVM_DIR="/home/apple/soft"
[ -s "$NVM_DIR/nvm-0.38.0/nvm.sh" ] && \. "$NVM_DIR/nvm-0.38.0/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/nvm-0.38.0/bash_completion" ] && \. "$NVM_DIR/nvm-0.38.0/bash_completion"  # This loads nvm 
```

1. 使用配置
```bash

source ~/.bashrc

```

3. 检查版本 测试是否安装

```bash
nvm -v
```