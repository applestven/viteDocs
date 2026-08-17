# Nextcloud 找回 / 重置密码

Docker 部署的 Nextcloud，忘记密码时用容器内 `occ` 命令处理（无需邮件找回）。

访问地址示例：`http://10.146.84.20:8800` / `https://cloud.itclass.top`

---

## 准备工作

先确认 Nextcloud 容器名：

```bash
docker ps | grep -i nextcloud
```

---

## 列出当前 Docker 部署的 Nextcloud 账号

```bash
# 列出所有用户
docker exec -u www-data 832b63643d79 php occ user:list

# 查看某个用户详情（含显示名、邮箱等）
docker exec -u www-data nextcloud php occ user:info apple

# 查看用户是否启用
docker exec -u www-data nextcloud php occ user:info apple | grep -i enabled
```

输出示例：

```text
  - admin: admin
  - apple: apple
  - applestven: applestven
```

---

## 对当前账号（如 apple）修改密码

### 方式一：交互式重置（推荐）

```bash
docker exec -it -u www-data nextcloud php occ user:resetpassword apple
```

按提示输入两次新密码即可。

### 方式二：一行命令直接设置

适合脚本，注意密码会出现在命令历史中：

```bash
docker exec -u www-data nextcloud php occ user:resetpassword apple --password-from-env NC_PASS
```

或（部分版本可用管道，不推荐在共享机器用）：

```bash
# 交互式更安全；若必须非交互，优先用环境变量方式
docker exec -e OC_PASS='你的新密码' -u www-data nextcloud \
  php occ user:resetpassword apple --password-from-env
```

> 不同 Nextcloud / 镜像版本环境变量名可能是 `OC_PASS` 或 `NC_PASS`，以本机 `occ user:resetpassword --help` 为准。

查看帮助：

```bash
docker exec -u www-data nextcloud php occ user:resetpassword --help
```

### 重置后验证登录

浏览器打开登录页，用新密码登录：

- 内网：`http://10.146.84.20:8800/login`
- 域名：`https://cloud.itclass.top/login`

WebDAV 也可测：

```bash
curl -u apple:新密码 -I 'https://cloud.itclass.top/remote.php/dav/files/apple/'
```

返回 `200` / `207` 一般表示账号密码正确。

---

## 补充：管理员相关

```bash
# 把用户提升为管理员（如需要）
docker exec -u www-data nextcloud php occ group:adduser admin apple

# 从管理员组移除
docker exec -u www-data nextcloud php occ group:removeuser admin apple

# 禁用 / 启用用户
docker exec -u www-data nextcloud php occ user:disable apple
docker exec -u www-data nextcloud php occ user:enable apple
```

---

## 常见问题

| 现象                 | 处理                                     |
| -------------------- | ---------------------------------------- |
| `occ` 报权限错误     | 必须加 `-u www-data`                     |
| 找不到容器           | 先 `docker ps` 确认真实容器名            |
| 改密成功但网页登不上 | 清浏览器缓存 / 确认访问的是正确域名或 IP |
| 提示 trusted_domains | 见 `方案/nextcloud/疑难杂症.md`          |

---

## 速查

```bash
docker ps | grep -i nextcloud
docker exec -u www-data nextcloud php occ user:list
docker exec -it -u www-data nextcloud php occ user:resetpassword apple
```
