# FTP 常用命令

配合本方案的 FTP 服务使用（账号密码为服务器系统用户）。

| 场景           | 主机              | 端口   |
| -------------- | ----------------- | ------ |
| 内网直连       | `10.147.47.20`    | `21`   |
| 公网（经 FRP） | `139.199.192.179` | `7011` |

> 公网连接务必开启**被动模式（PASV）**。

---

## 1. 登录

```bash
# 内网
ftp 10.147.47.20
ftp 192.168.0.112

# 公网（非标准端口）
ftp 139.199.192.179 7011
```

登录后按提示输入用户名、密码。成功后进入交互模式（提示符一般为 `ftp>`）。

用 `curl` 测试连通（不进入交互）：

```bash
# 列出根目录
curl -u 用户名:密码 ftp://10.147.47.20/

# 公网 + 被动模式
curl -u 用户名:密码 --ftp-pasv ftp://139.199.192.179:7011/
```

---

## 2. 目录相关

| 命令           | 说明                              |
| -------------- | --------------------------------- |
| `pwd`          | 显示当前远程目录                  |
| `ls` / `dir`   | 列出当前目录文件                  |
| `cd 目录名`    | 进入远程目录                      |
| `cd ..`        | 返回上一级                        |
| `mkdir 目录名` | 新建远程目录                      |
| `rmdir 目录名` | 删除空目录                        |
| `lcd 本地路径` | 切换本地工作目录                  |
| `!pwd` / `!ls` | 在本地执行 shell 命令（`!` 前缀） |

```bash
ftp> pwd
ftp> ls
ftp> cd photos
ftp> mkdir sony_a7m4
ftp> lcd /home/ubuntu/download
```

---

## 3. 上传 / 下载

| 命令                        | 说明                     |
| --------------------------- | ------------------------ |
| `put 本地文件 [远程文件名]` | 上传单个文件             |
| `mput 文件1 文件2 ...`      | 上传多个文件（可通配符） |
| `get 远程文件 [本地文件名]` | 下载单个文件             |
| `mget 文件1 文件2 ...`      | 下载多个文件             |
| `append 本地文件 远程文件`  | 追加上传（续传场景少用） |

```bash
# 上传
ftp> put DSC00104.JPG
ftp> put ./local.jpg remote.jpg
ftp> mput *.JPG

# 下载
ftp> get DSC00104.JPG
ftp> get remote.jpg ./local.jpg
ftp> mget *.JPG
```

`mput` / `mget` 默认会逐个确认。关闭交互确认：

```bash
ftp> prompt
```

再用 `mput` / `mget` 即可批量操作。

用 `curl` 上传 / 下载：

```bash
# 上传
curl -u 用户名:密码 -T ./DSC00104.JPG ftp://10.147.47.20/sony_a7m4/

# 下载
curl -u 用户名:密码 ftp://10.147.47.20/sony_a7m4/DSC00104.JPG -o DSC00104.JPG
```

---

## 4. 传输模式

| 命令               | 说明                                   |
| ------------------ | -------------------------------------- |
| `binary` / `bin`   | 二进制模式（**图片、视频必须用这个**） |
| `ascii`            | 文本模式（仅适合 `.txt` 等）           |
| `passive` / `pasv` | 切换被动模式（公网 / 相机场景必须开）  |

```bash
ftp> binary
ftp> passive
ftp> put DSC00104.JPG
```

> 上传照片前先执行 `binary`，否则 JPG 可能损坏。

---

## 5. 文件管理

| 命令                      | 说明                  |
| ------------------------- | --------------------- |
| `rename 旧名 新名`        | 重命名远程文件 / 目录 |
| `delete 文件名`           | 删除远程文件          |
| `mdelete 文件1 文件2 ...` | 删除多个远程文件      |
| `size 文件名`             | 查看远程文件大小      |
| `status`                  | 查看当前连接状态      |

```bash
ftp> rename old.jpg new.jpg
ftp> delete DSC00104.JPG
ftp> mdelete *.TMP
```

---

## 6. 会话控制

| 命令                    | 说明               |
| ----------------------- | ------------------ |
| `help` / `?`            | 查看可用命令       |
| `help 命令名`           | 查看某命令说明     |
| `hash`                  | 传输时显示进度标记 |
| `bye` / `quit` / `exit` | 退出 FTP           |

```bash
ftp> help put
ftp> hash
ftp> bye
```

---

## 7. 常用操作示例

### 内网上传一张照片

```bash
ftp 10.147.47.20
# 输入用户名、密码
ftp> binary
ftp> cd sony_a7m4
ftp> put DSC00104.JPG
ftp> bye
```

### 公网下载目录中的文件

```bash
ftp 139.199.192.179 7011
ftp> binary
ftp> passive
ftp> cd sony_a7m4
ftp> ls
ftp> get DSC00104.JPG
ftp> bye
```

### 一行命令上传（适合脚本）

```bash
curl -u 用户名:密码 --ftp-pasv -T ./DSC00104.JPG \
  ftp://139.199.192.179:7011/sony_a7m4/
```

---

## 8. 服务端常用检查（vsftpd）

在 FTP 所在机器上执行：

```bash
# 服务状态
sudo systemctl status vsftpd

# 是否在监听 21
ss -lntp | grep ':21'

# 本机自测登录
ftp localhost
```

---

## 速查表

```
登录:     ftp 主机 [端口]
上传:     binary → put / mput
下载:     binary → get / mget
目录:     pwd / ls / cd / mkdir
公网:     passive（PASV）必须开
退出:     bye
```
