#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EdgeNova（edgenova）节点优选 — Telegram 视频向

界面/协议与「超实惠加速」同系（UnrivaledSpeed / FlClash 魔改 + Mihomo）：
  - 控制: 优先 Clash External Controller；否则常驻 IPC 桥（127.0.0.1:19693）
  - 流量: mixed-port（默认 7892）

默认拉起一次常驻桥后复用，测速不再每次拆核心。

依赖: pip install requests
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
try:
    import flclash_ipc
    import telegramNodePick as tgp
except ImportError as e:
    print(f"需要同目录 telegramNodePick.py / flclash_ipc.py ({e})")
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


BRAND = flclash_ipc.EDGENOVA
APP_NAMES = ("edgenova", "edgenovacore")


def find_processes() -> dict:
    found = {}
    try:
        out = subprocess.check_output(
            ["tasklist", "/FO", "CSV", "/NH"],
            encoding="utf-8",
            errors="ignore",
        )
    except Exception:
        return found
    for line in out.splitlines():
        parts = [p.strip().strip('"') for p in line.split(",")]
        if len(parts) < 2:
            continue
        name, pid = parts[0], parts[1]
        base = name.lower().replace(".exe", "")
        if base in APP_NAMES:
            try:
                found[base] = int(pid)
            except ValueError:
                pass
    return found


def find_install_dir() -> Optional[Path]:
    candidates = [
        Path(r"E:\soft\edgenova"),
        Path(r"D:\soft\edgenova"),
        Path(os.environ.get("LOCALAPPDATA", "")) / "edgenova",
        Path(os.environ.get("ProgramFiles", "")) / "edgenova",
    ]
    for soft in (Path(r"E:\soft"), Path(r"D:\soft"), Path(r"C:\soft")):
        if soft.is_dir():
            for child in soft.iterdir():
                if child.is_dir() and "edgenova" in child.name.lower():
                    candidates.append(child)
    for p in candidates:
        if (p / BRAND.gui_exe).is_file():
            return p
    return None


def find_data_dir() -> Optional[Path]:
    p = BRAND.home_dir()
    if p.is_dir() and (p / "shared_preferences.json").is_file():
        return p
    return None


def fingerprint_core(install: Optional[Path]) -> dict:
    info = {
        "family": "unknown",
        "engine": "unknown",
        "control": "unknown",
        "detail": "",
    }
    if not install:
        return info
    core = install / BRAND.core_exe
    if not core.is_file():
        return info
    try:
        data = core.read_bytes()
    except OSError as e:
        info["detail"] = str(e)
        return info
    if b"metacubex/mihomo" in data or b"MetaCubeX" in data:
        info["engine"] = "Clash Meta / Mihomo"
    if b"UnrivaledSpeed" in data:
        info["family"] = "EdgeNova (UnrivaledSpeed / FlClash 魔改)"
        info["control"] = "FlClash IPC（主） / External Controller（可选）"
    elif info["engine"] != "unknown":
        info["family"] = "Clash Meta 系客户端"
        info["control"] = "Clash External Controller"
    info["detail"] = f"core={core.name} size={core.stat().st_size}"
    return info


def load_prefs(data_dir: Path) -> dict:
    prefs_path = data_dir / "shared_preferences.json"
    raw = json.loads(prefs_path.read_text(encoding="utf-8"))
    cfg = json.loads(raw.get("flutter.config") or "{}")
    return {"raw": raw, "config": cfg, "path": prefs_path}


def get_mixed_port(cfg: dict) -> int:
    patch = cfg.get("patchClashConfig") or {}
    return int(patch.get("mixed-port") or 7892)


def clash_api_alive(base: str, secret: str = "", timeout: float = 1.2) -> bool:
    try:
        tgp.ClashAPI(base, secret, timeout=timeout).version()
        return True
    except Exception:
        return False


def probe_existing_api(secret: str = "") -> Optional[str]:
    for port in (9090, 19690, 19691, 9097, 9091, 6170):
        base = f"http://127.0.0.1:{port}"
        if clash_api_alive(base, secret):
            return base
    return None


# 与软件/FlClash 默认测速 URL 一致（不是 Telegram）
SOFT_PREFLIGHT_URL = "http://www.gstatic.com/generate_204"


def soft_preflight(
    api,
    group: str,
    nodes: list[str],
    proxy_url: str,
    settle: float,
    log_fn,
    timeout: float = 2.0,
    abort_ms: float = 800.0,
    url: str = SOFT_PREFLIGHT_URL,
) -> list[tuple[int, str]]:
    """IPC 模式：切换后用与软件相同的 generate_204 做相对排序。

    注意：软件 UI 延迟是内核内 URLTest（常 <100ms）；本函数多一跳 local mixed-port，
    绝对值会偏高，但排序口径接近。Telegram 延迟/带宽留给精测。
    """
    results: list[tuple[int, str]] = []
    proxies = {"http": proxy_url, "https": proxy_url}
    total = len(nodes)
    req_timeout = (min(1.0, timeout), timeout)
    for i, name in enumerate(nodes, 1):
        try:
            api.switch(group, name)
            api.close_connections()
            time.sleep(settle)
            t0 = time.perf_counter()
            try:
                r = requests.get(
                    url,
                    proxies=proxies,
                    timeout=req_timeout,
                    stream=True,
                    allow_redirects=False,
                    headers={"User-Agent": "telegram-edgenova-pick/1.0"},
                )
                # 204/200 都算通；读一点数据触发首包
                _ = next(r.iter_content(256), b"")
                ms = (time.perf_counter() - t0) * 1000
                r.close()
            except Exception:
                log_fn(f"  [{i}/{total}] 失败     {name}")
                continue
            if ms > abort_ms:
                log_fn(f"  [{i}/{total}] 慢弃     {int(ms)}ms  {name}")
                continue
            log_fn(f"  [{i}/{total}] {int(round(ms))}ms     {name}")
            results.append((int(round(ms)), name))
        except Exception as e:
            log_fn(f"  [{i}/{total}] 错误     {name}  ({e})")
    results.sort()
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="EdgeNova Telegram 视频节点优选")
    parser.add_argument("--api", default=None, help="若已开 External Controller，如 http://127.0.0.1:9090")
    parser.add_argument("--secret", default="")
    parser.add_argument("--proxy", default=None)
    parser.add_argument("--group", default=None)
    parser.add_argument("--filter", default=None)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--duration", type=float, default=5.0)
    parser.add_argument("--settle", type=float, default=0.8)
    parser.add_argument("--preflight-top", type=int, default=8)
    parser.add_argument(
        "--preflight-timeout",
        type=float,
        default=2.0,
        help="软预筛单节点超时秒（默认 2.0）",
    )
    parser.add_argument(
        "--preflight-abort-ms",
        type=float,
        default=800.0,
        help="软预筛超过该毫秒视为慢弃（默认 800，对齐节点探测而非 TG）",
    )
    parser.add_argument(
        "--preflight-url",
        default=SOFT_PREFLIGHT_URL,
        help=f"软预筛 URL（默认与软件一致: {SOFT_PREFLIGHT_URL}）",
    )
    parser.add_argument("--no-preflight", action="store_true")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--tg-abort-ms", type=float, default=tgp.TG_ABORT_MS)
    parser.add_argument("--no-keep-stable", action="store_true")
    parser.add_argument("--restore-original", action="store_true")
    parser.add_argument("--no-apply", action="store_true")
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
    logfile = result_dir / f"tg_edgenova_{stamp}.log"
    top5_file = top5_dir / f"edgenova_{stamp}.txt"

    with logfile.open("w", encoding="utf-8") as fp:
        def log(msg: str = ""):
            tgp.log(msg, fp)

        log("=" * 60)
        log("EdgeNova · Telegram 视频节点优选")
        log(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log("=" * 60)

        procs = find_processes()
        install = find_install_dir()
        data_dir = find_data_dir()
        fpinfo = fingerprint_core(install)

        log()
        log(">>> [识别]")
        log(f"  进程: {procs or '未发现'}")
        log(f"  安装: {install or '未找到'}")
        log(f"  数据: {data_dir or '未找到'}")
        log(f"  家族: {fpinfo['family']}")
        log(f"  引擎: {fpinfo['engine']}")
        log(f"  控制面: {fpinfo['control']}")
        log(f"  细节: {fpinfo['detail']}")

        if "edgenova" not in procs and not data_dir:
            log("未检测到 EdgeNova，请先启动软件。")
            return 1
        if data_dir is None:
            log("找不到配置目录")
            return 1
        if install is None:
            log("找不到安装目录")
            return 1

        cfg = load_prefs(data_dir)["config"]
        mixed_port = get_mixed_port(cfg)
        proxy_url = args.proxy or f"http://127.0.0.1:{mixed_port}"
        log(f"  mixed-port: {mixed_port}")
        log(f"  测速代理: {proxy_url}")

        # ---- 控制面 ----
        secret = args.secret or os.environ.get("CLASH_SECRET", "")
        # 先认本品牌常驻桥，避免误连超实惠/Ninja 的控制器
        api_base = args.api
        if not api_base and clash_api_alive(BRAND.agent_base, ""):
            api_base = BRAND.agent_base
        if not api_base:
            api_base = probe_existing_api(secret)
        api = None
        control_mode = ""
        final_node: Optional[str] = None
        use_agent_soft_preflight = False

        if api_base and clash_api_alive(api_base, secret if api_base != BRAND.agent_base else ""):
            api = tgp.ClashAPI(api_base, "" if "19693" in api_base else secret)
            control_mode = f"HTTP {api_base}"
            log(f"  使用 HTTP API: {api_base}")
            use_agent_soft_preflight = api_base.rstrip("/") == BRAND.agent_base.rstrip("/")
        else:
            log()
            log(">>> [控制面] 常驻 IPC 桥（Clash 兼容口）")
            log("  原因: 软件无可用 external-controller；直接拆核心会导致界面显示断开")
            log("  策略: 首次接入重拉一次内核，之后复用，测速过程不再断开")
            try:
                agent = flclash_ipc.ensure_agent(install, log=log, brand=BRAND)
                api = tgp.ClashAPI(agent, "")
                control_mode = f"Agent {agent}"
                use_agent_soft_preflight = True
            except Exception as e:
                log(f"  常驻桥失败: {e}")
                log("  备选: 释放 9090 后在软件打开「外部控制器」，再 --api http://127.0.0.1:9090")
                return 3

        try:
            try:
                ver = api.version()
                clash_cfg = api.configs()
                proxies = api.proxies()
            except Exception as e:
                log(f"读取代理列表失败: {e}")
                return 3

            mode = (clash_cfg.get("mode") or "rule").lower()
            if args.group:
                group = args.group
            elif "GLOBAL" in proxies:
                group = "GLOBAL"
            else:
                group = tgp.pick_default_group(proxies, mode)

            if group not in proxies:
                groups = [k for k, v in proxies.items() if str(v.get("type")) in tgp.GROUP_TYPE]
                log(f"策略组不存在: {group}；可选: {groups[:15]}")
                return 1

            original = proxies[group].get("now")
            nodes = tgp.filter_nodes(tgp.list_nodes(proxies, group), args.filter)

            log()
            log(">>> [就绪]")
            log(f"  控制: {control_mode}  core={ver.get('version')}  mode={mode}")
            log(f"  策略组: {group}  当前: {original}")
            log(f"  候选: {len(nodes)}" + (f"  /{args.filter}/" if args.filter else ""))
            log(f"  日志: {logfile}")
            log(f"  Top5: {top5_file}")

            if not nodes:
                log("没有可测节点")
                return 1

            try:
                with socket.create_connection(("127.0.0.1", mixed_port), timeout=2):
                    pass
            except OSError:
                log(f"警告: mixed-port {mixed_port} 不可用")

            pre_map: dict[str, int] = {}
            if do_preflight:
                log()
                if use_agent_soft_preflight:
                    log(
                        f">>> [1/2 预筛] 节点探测 {args.preflight_url} "
                        f"（对齐软件延迟口径；非 TG）"
                        f" timeout={args.preflight_timeout:.1f}s"
                        f" abort={args.preflight_abort_ms:.0f}ms"
                    )
                    ranked_pre = soft_preflight(
                        api,
                        group,
                        nodes,
                        proxy_url,
                        min(args.settle, 0.35),
                        log,
                        timeout=args.preflight_timeout,
                        abort_ms=args.preflight_abort_ms,
                        url=args.preflight_url,
                    )
                else:
                    log(f">>> [1/2 预筛] delay → {tgp.PREFLIGHT_URL}（不切换）")
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
                    "api": control_mode,
                    "group": group,
                    "original": original,
                    "final": final_node,
                },
            )
            extra = (
                f"软件: EdgeNova\n"
                f"引擎: {fpinfo['engine']}\n"
                f"家族: {fpinfo['family']}\n"
                f"控制: {control_mode}\n"
                f"代理: {proxy_url}\n"
            )
            text = top5_file.read_text(encoding="utf-8")
            if not text.startswith("软件:"):
                top5_file.write_text(extra + text, encoding="utf-8")

            log()
            log(f"Top5: {top5_file}")
            log(f"日志: {logfile}")
            if use_agent_soft_preflight:
                log("常驻桥保持运行（下次测速不拆核心）；软件勿手动杀 python/handback")
            log("=" * 60)
            return 0
        finally:
            # 常驻桥由 handback 进程持有，测速进程不拆核心
            pass

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\n已中断", flush=True)
        raise SystemExit(130)
