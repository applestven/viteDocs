## 常用脚本说明 

## telegramSpeed.py 诊断 Telegram 看视频卡顿瓶颈

分段测试：本地网络 → 代理 → Telegram，并给出瓶颈定位。

```bash
python 工具/script/telegramSpeed.py
python 工具/script/telegramSpeed.py --proxy http://127.0.0.1:7890 --duration 12
```

日志写入仓库根目录 `result/时间戳.log`。

## telegramNodePick.py 自动切换 Clash 节点，选出最适合 Telegram 视频的

默认少打断：先无切换并行预筛（Clash delay → Telegram），再只精测前 8 名；精测过程中会“保持在当前最佳节点”，测到更高分才切过去；慢节点早停。Top5 写入 `result/top5/时间戳.txt`。

```bash
# 推荐：全量预筛 + 精测前列，测完切最优
python 工具/script/telegramNodePick.py

# 只看港日新
python 工具/script/telegramNodePick.py --filter "香港|日本|新加坡"

# 精测更多/更少
python 工具/script/telegramNodePick.py --preflight-top 12
python 工具/script/telegramNodePick.py --preflight-top 5 --duration 4

# 精测期间也切回“初始原节点”（旧行为）
python 工具/script/telegramNodePick.py --restore-original

# 测完不切最优
python 工具/script/telegramNodePick.py --no-apply
```

日志：`result/tg_nodes_时间戳.log`  
Top5：`result/top5/时间戳.txt`

## telegramCshPick.py 超实惠加速专用（自动识别 Clash Meta 协议）

检测正在运行的「超实惠加速」(chaoshihui)：判定为 Clash Meta / FlClash 魔改，自动开启 External Controller，再按 Telegram 视频标准选节点。

```bash
# 首次：写入 API 并重启软件，然后测速选节点
python 工具/script/telegramCshPick.py --restart

# 之后软件已开着、API 已启用时
python 工具/script/telegramCshPick.py

# 只测港日等
python 工具/script/telegramCshPick.py --filter "香港|日本|HK|JP|新加坡"
```

识别结论：超实惠加速 = Clash Meta（UnrivaledSpeed/FlClash 魔改），节点切换走 Clash External Controller；流量口为 mixed-port（常见 7892）。

若 `--restart` 后 API 仍不可用：在任务管理器结束全部 `chaoshihui`，软件内打开系统代理，再重跑。

日志：`result/tg_csh_时间戳.log`  
Top5：`result/top5/csh_时间戳.txt`

## latency_test.sh 测试各个服务器到本机的延迟 给出延迟排行前三的服务器



### 使用示例
```bash
./latency_test.sh
```

## nginx-port-proxy.sh  快速创建nginx端口代理



### 使用示例

1. 添加映射：

``` bash
sudo ./nginx-port-proxy.sh add 9000:100.123.18.75:3333 8080:192.168.1.50:80

# 将服务器本地9000端口映射到100.123.18.75:3333
sudo ./nginx-port-proxy.sh add 9000:100.123.18.75:3333
```


2. 删除映射：

``` bash
# 删除服务器使用脚本创建的9000 8000 端口映射
sudo ./nginx-port-proxy.sh del 9000 8080
```

