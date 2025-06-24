## 前置依赖（必须安装）

```bash
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
  libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
  libffi-dev liblzma-dev git

```


## 起冲突 修复 

``` bash
sudo apt update
sudo apt --fix-broken install
sudo apt upgrade
```

重新尝试安装 pyenv 所需依赖


或者 

``` bash
sudo apt install -f
```

这个命令会尝试自动解决所有依赖冲突。
## 安装 pyenv


``` bash
curl https://pyenv.run | bash
```


## 配置 shell 启动文件（必须）

``` bash
echo -e '\n# pyenv config' >> ~/.bashrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

```

## 刷新配置文件

source ~/.bashrc