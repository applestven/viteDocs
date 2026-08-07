#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NinjaDesktop 节点优选 — Telegram 视频向

自动识别本机「NinjaDesktop」(https://github.com/kachetong1314/ninja)：
  - 内核: ninja-mihomo（Clash Meta / Mihomo）
  - 控制: WebUI(常 9190) 拉起内核 + External Controller（默认 127.0.0.1:9799）
  - 流量: mixed-port（默认 7897；系统代理未开也可测）

体验接近 Clash：支持无切换并行 delay 预筛。

依赖: pip install requests
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
try:
    import telegramNodePick as tgp
except ImportError as e:
    print(f"需要同目录 telegramNodePick.py ({e})")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("缺少依赖: pip install requests")
    sys.exit(1)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


PREFERRED_GROUPS = (
    "🚀 节点选择",
    "📲 电报信息",
    "🟦 专线节点",
    "🟩 公网节点",
    "GLOBAL",
)


def find_processes() -> dict:
    found: dict[str, int] = {}
    try:
        out = subprocess.check_output(
            ["tasklist", "/FO", "CSV", "/NH"],
            encoding="utf-8",
            errors="ignore",
        )
    except Exception:
        return found
    want_bases = {"ninjadesktop", "ninja-mihomo"}
    for line in out.splitlines():
        parts = [p.strip().strip('"') for p in line.split(",")]
        if len(parts) < 2:
            continue
        name, pid = parts[0], parts[1]
        base = name.lower().replace(".exe", "")
        if base not in want_bases or not pid.isdigit():
            continue
        key = "ninja-mihomo" if base == "ninja-mihomo" else "NinjaDesktop"
        found[key] = int(pid)
    return found


def find_install_dir() -> Optional[Path]:
    cands = [
        Path(r"E:\soft\Ninja\NinjaDesktop"),
        Path(r"D:\soft\Ninja\NinjaDesktop"),
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "NinjaDesktop",
        Path(os.environ.get("LOCALAPPDATA", "")) / "NinjaDesktop",
    ]
    for soft in (Path(r"E:\soft"), Path(r"D:\soft"), Path(r"C:\soft")):
        if soft.is_dir():
            for child in soft.rglob("NinjaDesktop.exe"):
                cands.append(child.parent)
                break
    for p in cands:
        if (p / "NinjaDesktop.exe").is_file():
            return p
    return None


def find_data_dir() -> Optional[Path]:
    p = Path(os.environ.get("LOCALAPPDATA", "")) / "NinjaDesktop"
    if p.is_dir() and (p / "appconfig.yaml").is_file():
        return p
    return None


def load_appconfig(data_dir: Path) -> dict:
    """极简 YAML（仅顶层 key: value）。"""
    cfg: dict = {}
    text = (data_dir / "appconfig.yaml").read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or ":" not in s:
            continue
        k, v = s.split(":", 1)
        k, v = k.strip(), v.strip().strip("'\"")
        if v.lower() in ("true", "false"):
            cfg[k] = v.lower() == "true"
        else:
            try:
                cfg[k] = int(v)
            except ValueError:
                cfg[k] = v
    return cfg


def read_controller_secret(data_dir: Path) -> str:
    p = data_dir / "controller_secret"
    if p.is_file():
        return p.read_text(encoding="utf-8", errors="ignore").strip()
    return ""


def discover_webui(cfg: dict) -> tuple[str, str]:
    """返回 (webui_base, token)。"""
    host = cfg.get("webui_listen") or "127.0.0.1"
    port = int(cfg.get("webui_port") or 9190)
    base = f"http://{host}:{port}"
    token = str(cfg.get("webui_token") or "")
    try:
        with urllib.request.urlopen(base + "/", timeout=2) as r:
            html = r.read().decode("utf-8", "replace")
        m = re.search(r'"webui_token"\s*:\s*"([^"]+)"', html)
        if m:
            token = m.group(1)
    except Exception:
        pass
    return base, token


def webui_request(base: str, token: str, method: str, path: str, data=None, timeout: float = 8.0):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = None if data is None else json.dumps(data).encode("utf-8")
    req = urllib.request.Request(base.rstrip("/") + path, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            try:
                return resp.status, json.loads(raw)
            except Exception:
                return resp.status, raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw
    except Exception as e:
        return None, str(e)


def ensure_kernel(webui: str, token: str, log) -> bool:
    st, body = webui_request(webui, token, "GET", "/api/kernel/status")
    running = isinstance(body, dict) and body.get("running")
    if running:
        log(f"  内核已运行 pid={body.get('pid')} uptime={body.get('uptime')}")
        return True
    log("  内核未运行，正在 /api/kernel/start ...")
    st, body = webui_request(webui, token, "POST", "/api/kernel/start", {})
    if not (isinstance(body, dict) and body.get("running")):
        log(f"  启动失败: HTTP {st} {body}")
        return False
    log(f"  内核已启动 pid={body.get('pid')}")
    # 等 controller / mixed-port
    time.sleep(1.0)
    return True


def controller_base_from_cfg(cfg: dict) -> str:
    addr = str(cfg.get("controller_addr") or "127.0.0.1:9799").strip()
    if not addr.startswith("http"):
        addr = "http://" + addr
    return addr.rstrip("/")


def clash_alive(base: str, secret: str, timeout: float = 1.5) -> bool:
    try:
        tgp.ClashAPI(base, secret, timeout=timeout).version()
        return True
    except Exception:
        return False


def wait_clash(base: str, secret: str, log, seconds: float = 12.0) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if clash_alive(base, secret):
            return True
        time.sleep(0.4)
    log(f"  External Controller 未就绪: {base}")
    return False


def pick_ninja_group(proxies: dict, mode: str, explicit: Optional[str]) -> str:
    if explicit:
        return explicit
    if (mode or "").lower() == "global" and "GLOBAL" in proxies:
        return "GLOBAL"
    for name in PREFERRED_GROUPS:
        if name in proxies:
            return name
    return tgp.pick_default_group(proxies, mode)


def main() -> int:
    parser = argparse.ArgumentParser(description="NinjaDesktop Telegram 视频节点优选")
    parser.add_argument("--api", default=None, help="覆盖 External Controller，如 http://127.0.0.1:9799")
    parser.add_argument("--secret", default="", help="覆盖 controller secret")
    parser.add_argument("--proxy", default=None, help="覆盖测速用 HTTP 代理")
    parser.add_argument("--group", default=None, help="策略组（默认优先 电报信息/节点选择）")
    parser.add_argument("--filter", default=None, help="节点名正则，如 '香港|日本|新加坡|PRO'")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--duration", type=float, default=5.0)
    parser.add_argument("--settle", type=float, default=0.8)
    parser.add_argument("--preflight-top", type=int, default=8)
    parser.add_argument("--no-preflight", action="store_true")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--tg-abort-ms", type=float, default=tgp.TG_ABORT_MS)
    parser.add_argument("--no-keep-stable", action="store_true")
    parser.add_argument("--restore-original", action="store_true")
    parser.add_argument("--no-apply", action="store_true")
    parser.add_argument("--no-start-kernel", action="store_true", help="不自动 start 内核")
    parser.add_argument("--result-dir", default=None)
    args = parser.parse_args()

    keep_stable = not args.no_keep_stable
    do_preflight = not args.no_preflight

    repo_root = SCRIPT_DIR.parent.parent
    result_dir = Path(args.result_dir) if args.result_dir else repo_root / "result"
    top5_dir = result_dir / "top5"
    result_dir.mkdir(parents=True, exist_ok=True)
    top5_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logfile = result_dir / f"tg_ninja_{stamp}.log"
    top5_file = top5_dir / f"ninja_{stamp}.txt"

    with logfile.open("w", encoding="utf-8") as fp:
        def log(msg: str = ""):
            tgp.log(msg, fp)

        log("=" * 60)
        log("NinjaDesktop · Telegram 视频节点优选")
        log(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log("=" * 60)

        procs = find_processes()
        install = find_install_dir()
        data_dir = find_data_dir()

        log()
        log(">>> [识别]")
        log(f"  进程: {procs or '未发现'}")
        log(f"  安装: {install or '未找到'}")
        log(f"  数据: {data_dir or '未找到'}")
        log("  家族: NinjaDesktop (ninja-mihomo / Clash Meta)")
        log("  发布: https://github.com/kachetong1314/ninja/releases/tag/0.1.10")

        if not procs and data_dir is None:
            log("未检测到 NinjaDesktop，请先启动软件。")
            return 1
        if data_dir is None:
            log("找不到 %LOCALAPPDATA%\\NinjaDesktop\\appconfig.yaml")
            return 1

        cfg = load_appconfig(data_dir)
        mixed_port = int(cfg.get("mixed_port") or 7897)
        secret = args.secret or read_controller_secret(data_dir) or os.environ.get("CLASH_SECRET", "")
        api_base = (args.api or controller_base_from_cfg(cfg)).rstrip("/")
        webui, token = discover_webui(cfg)
        proxy_url = args.proxy or f"http://127.0.0.1:{mixed_port}"

        log(f"  WebUI: {webui}")
        log(f"  External Controller: {api_base}")
        log(f"  mixed-port(配置): {mixed_port}")
        log(f"  测速代理: {proxy_url}")
        log(f"  system_proxy(配置): {cfg.get('system_proxy')}")

        log()
        log(">>> [内核]")
        if args.no_start_kernel:
            log("  跳过自动启动（--no-start-kernel）")
        else:
            if not ensure_kernel(webui, token, log):
                return 3

        if not wait_clash(api_base, secret, log):
            # 兼容 Clash V-Ninja 同机占用时误探
            for alt in ("http://127.0.0.1:9799", "http://127.0.0.1:9097"):
                if alt.rstrip("/") == api_base.rstrip("/"):
                    continue
                for sec in (secret, "set-your-secret", ""):
                    if clash_alive(alt, sec):
                        log(f"  改用可用控制器 {alt}")
                        api_base, secret = alt, sec
                        break
                else:
                    continue
                break
            else:
                return 3

        api = tgp.ClashAPI(api_base, secret)

        try:
            ver = api.version()
            clash_cfg = api.configs()
            proxies = api.proxies()
        except Exception as e:
            log(f"读取 Clash API 失败: {e}")
            return 3

        # 以运行时 mixed-port 为准
        runtime_mixed = int(clash_cfg.get("mixed-port") or mixed_port)
        if not args.proxy:
            proxy_url = f"http://127.0.0.1:{runtime_mixed}"
        mode = (clash_cfg.get("mode") or "rule").lower()
        group = pick_ninja_group(proxies, mode, args.group)
        if group not in proxies:
            groups = [k for k, v in proxies.items() if str(v.get("type")) in tgp.GROUP_TYPE]
            log(f"策略组不存在: {group}；可选: {groups[:20]}")
            return 1

        original = proxies[group].get("now")
        nodes = tgp.filter_nodes(tgp.list_nodes(proxies, group), args.filter)

        log()
        log(">>> [就绪]")
        log(f"  core={ver.get('version')} meta={ver.get('meta')} mode={mode}")
        log(f"  策略组: {group}  当前: {original}")
        log(f"  候选: {len(nodes)}" + (f"  /{args.filter}/" if args.filter else ""))
        log(f"  日志: {logfile}")
        log(f"  Top5: {top5_file}")

        if not nodes:
            log("没有可测节点（若组指向自动选择，请 --group \"🚀 节点选择\" 或加 --filter）")
            return 1

        try:
            with socket.create_connection(("127.0.0.1", runtime_mixed), timeout=2):
                pass
        except OSError:
            log(f"警告: mixed-port {runtime_mixed} 不可用（系统代理未开也可测，但需内核监听）")

        pre_map: dict[str, int] = {}
        if do_preflight:
            log()
            log(f">>> [1/2 预筛] Clash delay → {tgp.PREFLIGHT_URL}（不切换，并行 {args.workers}）")
            ranked_pre = tgp.preflight_nodes(
                api, nodes, tgp.PREFLIGHT_URL, 4000, args.workers, log
            )
            for d, n in ranked_pre:
                pre_map[n] = d
            fine_n = args.preflight_top
            if args.limit > 0:
                fine_n = min(fine_n, args.limit)
            nodes = [n for _, n in ranked_pre[:fine_n]]
            if not nodes:
                log("预筛后无可用节点")
                tgp.restore_stable(api, group, original)
                return 1
            log(f"精测前 {len(nodes)} 名:")
            for i, name in enumerate(nodes, 1):
                log(f"  {i}. {pre_map.get(name)}ms  {name}")
        elif args.limit > 0:
            nodes = nodes[: args.limit]

        tgp.restore_stable(api, group, original)

        results: list[tgp.NodeResult] = []
        best_node: Optional[str] = None
        best_score = float("-inf")

        log()
        log(
            f">>> [2/2 精测] {len(nodes)} 个 | ≈{args.duration:.0f}s | "
            f"{'保持当前最佳' if keep_stable else '连续切换'}"
        )

        try:
            for i, name in enumerate(nodes, 1):
                restore_target = (
                    original
                    if (args.restore_original or best_node is None)
                    else best_node
                )
                log(
                    f"\n--- ({i}/{len(nodes)}) {name}"
                    + (f"  预筛{pre_map[name]}ms" if name in pre_map else "")
                )
                r = tgp.benchmark_node(
                    api,
                    group,
                    name,
                    proxy_url,
                    duration=args.duration,
                    settle=args.settle,
                    original=restore_target,
                    keep_stable=keep_stable,
                    tg_abort_ms=args.tg_abort_ms,
                )
                if name in pre_map:
                    r.preflight_ms = pre_map[name]
                results.append(r)
                if r.ok:
                    log(
                        f"  TG={r.tg_ms:.0f}ms  down={r.download_mbs:.2f}MB/s  score={r.score}"
                    )
                else:
                    log(f"  跳过/失败: {r.error}")

                if r.ok and (best_node is None or r.score > best_score):
                    best_node = name
                    best_score = r.score
                    if keep_stable:
                        api.switch(group, best_node)
                        api.close_connections()
                        time.sleep(args.settle)
                    log(f"  → 发现更优，当前最佳: {best_node}")
                elif keep_stable:
                    log(f"  → 保持当前最佳: {best_node or original}")
        except KeyboardInterrupt:
            log("\n中断，恢复...")
            tgp.restore_stable(api, group, original)
            raise

        log()
        log("=" * 60)
        log("排行榜")
        log("=" * 60)
        for line in tgp.format_table(results):
            log(line)

        ok_results = [r for r in results if r.ok]
        if not ok_results:
            log("精测全部失败，恢复原节点")
            tgp.restore_stable(api, group, original)
            return 2

        ok_results.sort(key=lambda x: x.score, reverse=True)
        best = ok_results[0]
        top5 = ok_results[:5]

        log()
        log(
            f">>> 最优: {best.name}  score={best.score}  "
            f"{best.download_mbs:.2f}MB/s  TG={best.tg_ms:.0f}ms"
        )
        for i, r in enumerate(top5, 1):
            log(
                f"  Top{i}: [{r.score:.1f}] {r.name}  "
                f"{r.download_mbs:.2f}MB/s  TG={r.tg_ms:.0f}ms"
            )

        final_node = original
        if args.no_apply:
            tgp.restore_stable(api, group, original)
            log(f"保持原节点: {original}")
        else:
            api.switch(group, best.name)
            api.close_connections()
            final_node = best.name
            log(f"已切换到最优: {best.name}")

        tgp.write_top5(
            str(top5_file),
            top5,
            {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "api": api_base,
                "group": group,
                "original": original,
                "final": final_node,
            },
        )
        extra = (
            f"软件: NinjaDesktop\n"
            f"引擎: ninja-mihomo / Clash Meta\n"
            f"控制: {api_base}\n"
            f"代理: {proxy_url}\n"
            f"WebUI: {webui}\n"
        )
        text = top5_file.read_text(encoding="utf-8")
        if not text.startswith("软件:"):
            top5_file.write_text(extra + text, encoding="utf-8")

        log()
        log(f"Top5: {top5_file}")
        log(f"日志: {logfile}")
        log("=" * 60)
        return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\n已中断", flush=True)
        raise SystemExit(130)
