基本使用
1. 创建环境

``` bash
conda create -n myenv python=3.9.9
```
1. 激活环境

```bash
conda activate myenv
```
2. 安装包

```bash
conda install numpy pandas matplotlib
```
3. 列出已安装的包

```bash
conda list
```
4. 退出环境

```bash
conda deactivate
```
5. 删除环境

``` bash
conda env remove -n myenv
```


- 常用命令
查看所有环境：conda env list

搜索包：conda search package_name

更新包：conda update package_name

更新conda自身：conda update conda

导出环境配置：conda env export > environment.yml

从文件创建环境：conda env create -f environment.yml