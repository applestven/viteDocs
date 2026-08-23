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

## telegramCshPick.py 超实惠加速专用（FlClash IPC / External Controller）

自动识别本机「超实惠加速」(chaoshihui = UnrivaledSpeed / FlClash 魔改 + Mihomo)：

- **优先** HTTP External Controller（若已可用，体验最接近 Clash）
- **否则** 常驻 IPC 桥：`127.0.0.1:19692`（Clash 兼容口）；**首次**短暂重拉内核，之后测速**不再拆核心**
- 流量口：`mixed-port`（常见 **7892**）
- 桥模式下无可用 `delay`（会崩内核），预筛为「切换 + TG TTFB」；精测仍切节点测带宽

```bash
# 推荐：软件已打开时直接跑（第二次起不再闪断）
python 工具/script/telegramCshPick.py

# 只测港日新
python 工具/script/telegramCshPick.py --filter "香港|日本|新加坡|HK|JP|SG"

# 精测更少更快
python 工具/script/telegramCshPick.py --preflight-top 5 --duration 4

# 已手动打开外部控制器时（最丝滑）
python 工具/script/telegramCshPick.py --api http://127.0.0.1:9090
```

说明：软件会清空 `external-controller`；UI「外部控制」常固定 `9090`（易被 Docker 占用）。想完全等同 Clash：释放 9090 → 软件内打开外部控制器 → `--api`。

日志：`result/tg_csh_时间戳.log`  
Top5：`result/top5/csh_时间戳.txt`

## telegramNinjaPick.py NinjaDesktop 专用（Clash Meta External Controller）

自动识别本机 [NinjaDesktop](https://github.com/kachetong1314/ninja)（`ninja-mihomo`）：

- WebUI（默认 `9190`）检测并 **自动 start 内核**（若未开）
- External Controller（默认 `127.0.0.1:9799` + `controller_secret`）
- mixed-port（默认 **7897**；系统代理未开也可测）
- 支持无切换并行 delay，体验接近 Clash

```bash
# 推荐：软件已打开即可（脚本会按需启动内核）
python 工具/script/telegramNinjaPick.py

# 港日新 / PRO 专线
python 工具/script/telegramNinjaPick.py --filter "香港|日本|新加坡|PRO"

# 指定策略组
python 工具/script/telegramNinjaPick.py --group "🚀 节点选择"
python 工具/script/telegramNinjaPick.py --group "📲 电报信息"

# 精测更少
python 工具/script/telegramNinjaPick.py --preflight-top 5 --duration 4
```

日志：`result/tg_ninja_时间戳.log`  
Top5：`result/top5/ninja_时间戳.txt`

## telegramEdgenovaPick.py EdgeNova 专用（同超实惠 FlClash IPC）

自动识别本机 EdgeNova（`edgenova` / `edgenovaCore`，UnrivaledSpeed 同系）：

- 常驻 IPC 桥：`127.0.0.1:19693`（与超实惠 `19692` 互不占用）
- mixed-port（常见 **7892**）
- 预筛：切换式 `generate_204`；精测 TG + 下载

```bash
python 工具/script/telegramEdgenovaPick.py
python 工具/script/telegramEdgenovaPick.py --filter "香港|日本|新加坡"
python 工具/script/telegramEdgenovaPick.py --preflight-top 5 --duration 4
```

日志：`result/tg_edgenova_时间戳.log`  
Top5：`result/top5/edgenova_时间戳.txt`

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

