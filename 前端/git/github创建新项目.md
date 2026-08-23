

## 1. 安装

如果你还没用过 GitHub CLI，需要先安装并登录一次：

```bash
macOS: brew install gh

Windows: winget install --id GitHub.cli

Linux (Ubuntu/Debian): sudo apt install gh
```

## 2. 登录

按提示选择 GitHub 账号并完成浏览器授权即可 : 

```bash
gh auth login

gh auth logout 退出使用别的登录/切换token
```

## 3. 场景一：本地已有代码，想直接推送到新仓库

### 当前目录还没有.git? 先初始化
```bash
git init
```

### 一键创建远程仓库，并推送已有代码
```bash
gh repo create uiautomator2 --public --source=. --remote=origin --push
```
这条命令的含义：

--public：创建公开仓库（--private 为私有）

--source=.：把当前目录作为代码源

--remote=origin：设置远程仓库别名为 origin

--push：创建完成后自动将本地代码推送到 GitHub


### 场景二：从零开始，创建后自动克隆到本地
先在 GitHub 上建好空仓库，再自动拉取到本地执行：
```bash

gh repo create uiautomator2 --public --clone

```
本地和远程已经关联好  和 git clone 只是获取代码 有本质区别

### 场景三：使用模板快速起步
如果想基于某个现成模板创建新项目：

```bash

gh repo create my-project --public --template=owner/template-repo --clone

```

## 更多 ：用 API 实现更灵活的自动创建

对于追求极致自动化的场景（如脚本、CI/CD），也可以直接调用 GitHub API

``` bash
# 先创建仓库
curl -X POST -H "Authorization: token 你的Personal_Access_Token" \
     -H "Accept: application/vnd.github.v3+json" \
     https://api.github.com/user/repos -d '{"name":"my-new-repo"}'

# 再手动关联本地仓库
git remote add origin git@github.com:你的用户名/my-new-repo.git
git push -u origin main

```



## 深度理解 ：

git clone 和 gh repo create my-project --public --clone （场景二）

核心区别：远程仓库的创建时机和所有权
gh repo create --clone	git clone
本地文件夹	✅ 会创建	✅ 会创建
远程仓库	✅ 新建的（之前不存在）	❌ 已存在的
你拥有远程仓库吗	✅ 是（你是 owner）	❌ 通常不是
用一个比喻理解
想象 GitHub 是一个图书馆：

git clone：你复制了一本已经存在的书（别人写的），放在你桌上

书📖本来就在图书馆里

你只是抄了一份到本地

gh repo create --clone：你先在新白纸上写一本书放上图书馆书架，然后抄了一份到自己桌上

书📖是你新创建的

先有了图书馆里的书，再抄到本地