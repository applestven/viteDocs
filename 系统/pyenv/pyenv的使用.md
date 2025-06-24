## 使用 pyenv-win 管理 python 版本

``` bash
# 查看所有可安装的 python 版本
pyenv install -l
# 安装指定版本的 python
pyenv install 3.5.2
# 一个命令中安装多个版本
pyenv install 2.4.3 3.6.8
# 卸载 指定 版本 的 python
pyenv uninstall 3.5.2
# 查看已安装的版本 （版本文件夹）
pyenv versions
# 查看当前使用版本
pyenv version
# 设置 全局的 python 版本
pyenv global 3.5.2
# 设置指定文件夹下的 python 版本；在指定 文件夹下执行该命令，文件夹下会生成一个配置文件（不能删除）
pyenv local 3.5.2
## 查当前python版本文件夹位置 