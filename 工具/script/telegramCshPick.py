#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超实惠加速（chaoshihui）节点优选 — Telegram 视频向

自动识别本机正在运行的「超实惠加速」：
  - 内核: Clash Meta / Mihomo（UnrivaledSpeed，FlClash 魔改）
  - 控制: 优先 Clash External Controller HTTP API
  - 流量: mixed-port（默认 7892）

功能对齐 telegramNodePick.py：
  预筛(不切换) → 精测 → 保持当前最佳 → Top5 落盘

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

# 复用已有测速/打分逻辑
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
try:
    import telegramNodePick as tgp
except ImportError:
    print("需要同目录的 telegramNodePick.py")
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


APP_NAMES = ("chaoshihui", "chaoshihuiCore")
DEFAULT_API_PORT = 19690  # 避开本机常见 9090(Docker) / CFW 随机口
PROCESS_TITLE_HINT = "超实惠"


def L(msg: str = "", fp=None):
    tgp.log(msg, fp)


# ---------------------------------------------------------------------------
# 探测 / 指纹
# ---------------------------------------------------------------------------

def find_processes() -> dict:
    """返回 {name: pid}。"""
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
        Path(r"D:\soft\chaoshihui"),
        Path(os.environ.get("LOCALAPPDATA", "")) / "chaoshihui",
        Path(os.environ.get("ProgramFiles", "")) / "chaoshihui",
    ]
    for soft in (Path(r"D:\soft"), Path(r"C:\soft")):
        if soft.is_dir():
            for child in soft.iterdir():
                if child.is_dir() and "chaoshihui" in child.name.lower():
                    candidates.append(child)
    for p in candidates:
        if (p / "chaoshihui.exe").is_file():
            return p
    return None


def find_data_dir() -> Optional[Path]:
    p = Path(os.environ.get("APPDATA", "")) / "chaoshihui" / "chaoshihui"
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
    core = install / "chaoshihuiCore.exe"
    if not core.is_file():
        return info
    try:
        data = core.read_bytes()
    except OSError as e:
        info["detail"] = str(e)
        return info

    # 特征串
    if b"metacubex/mihomo" in data or b"MetaCubeX" in data:
        info["engine"] = "Clash Meta / Mihomo"
    if b"UnrivaledSpeed" in data:
        info["family"] = "超实惠加速 (UnrivaledSpeed / FlClash 魔改)"
        info["control"] = "FlClash IPC + Clash External Controller"
    elif b"FlClash" in data or b"fl_clash" in data:
        info["family"] = "FlClash 系"
        info["control"] = "FlClash IPC + Clash External Controller"
    elif info["engine"] != "unknown":
        info["family"] = "Clash Meta 系客户端"
        info["control"] = "Clash External Controller (HTTP)"
    if b"/proxies" in data and b"external-controller" in data:
        if info["control"] == "unknown":
            info["control"] = "Clash External Controller (HTTP)"
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


def get_external_controller(cfg: dict) -> str:
    patch = cfg.get("patchClashConfig") or {}
    return (patch.get("external-controller") or "").strip()


def listening_ports_of(pid: int) -> list[int]:
    ports = []
    try:
        out = subprocess.check_output(["netstat", "-ano"], encoding="utf-8", errors="ignore")
    except Exception:
        return ports
    for line in out.splitlines():
        if "LISTENING" not in line.upper():
            continue
        parts = line.split()
        if len(parts) < 5:
            continue
        if parts[-1] != str(pid):
            continue
        local = parts[1]
        if ":" not in local:
            continue
        try:
            ports.append(int(local.rsplit(":", 1)[-1]))
        except ValueError:
            pass
    return ports


def port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def pick_api_port(preferred: int = DEFAULT_API_PORT) -> int:
    for p in [preferred, 19690, 19691, 19090, 9097, 9096]:
        if port_free(p):
            return p
    # 最后随便找
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def clash_api_alive(base: str, secret: str = "", timeout: float = 1.5) -> bool:
    try:
        api = tgp.ClashAPI(base, secret, timeout=timeout)
        api.version()
        return True
    except Exception:
        return False


def probe_existing_api(secret: str = "") -> Optional[str]:
    """扫描本机可能的 Clash API 口。"""
    for port in (DEFAULT_API_PORT, 19690, 19691, 9097, 9090, 9091, 6170):
        base = f"http://127.0.0.1:{port}"
        if clash_api_alive(base, secret):
            return base
    return None


# ---------------------------------------------------------------------------
# 开启 External Controller
# ---------------------------------------------------------------------------

def enable_external_controller(
    data_dir: Path,
    api_hostport: str,
    log_fn,
) -> bool:
    """写入 shared_preferences.json 的 patchClashConfig.external-controller。"""
    prefs = load_prefs(data_dir)
    cfg = prefs["config"]
    patch = dict(cfg.get("patchClashConfig") or {})
    old = (patch.get("external-controller") or "").strip()
    if old == api_hostport:
        log_fn(f"external-controller 已是 {api_hostport}")
        return False
    patch["external-controller"] = api_hostport
    cfg["patchClashConfig"] = patch
    raw = prefs["raw"]
    raw["flutter.config"] = json.dumps(cfg, ensure_ascii=False, separators=(",", ":"))
    path: Path = prefs["path"]
    backup = path.with_suffix(".json.bak_tg")
    if not backup.exists():
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        log_fn(f"已备份偏好设置: {backup}")
    path.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    log_fn(f"已写入 external-controller: {old!r} -> {api_hostport!r}")
    return True


def restart_chaoshihui(install: Path, log_fn) -> None:
    log_fn("正在重启 超实惠加速 以加载 External Controller...")
    for name in ("chaoshihuiCore", "chaoshihui"):
        try:
            r = subprocess.run(
                ["taskkill", "/F", "/IM", f"{name}.exe"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )
            if r.returncode != 0 and r.stderr:
                log_fn(f"  taskkill {name}: {r.stderr.strip() or r.stdout.strip()}")
        except Exception as e:
            log_fn(f"  taskkill {name} 异常: {e}")
    # 单实例锁
    lock = Path(os.environ.get("APPDATA", "")) / "chaoshihui" / "chaoshihui" / "chaoshihui.lock"
    for _ in range(10):
        left = find_processes()
        if "chaoshihui" not in left and "chaoshihuiCore" not in left:
            break
        time.sleep(0.5)
    left = find_processes()
    if left:
        log_fn(f"  警告: 仍有残留进程 {left}（可能无权限结束）。请在任务管理器结束「chaoshihui」后重试。")
        if lock.exists():
            try:
                lock.unlink()
                log_fn(f"  已删除锁文件: {lock}")
            except OSError as e:
                log_fn(f"  无法删除锁文件: {e}")
    time.sleep(1.0)
    exe = install / "chaoshihui.exe"
    subprocess.Popen([str(exe)], cwd=str(install))
    log_fn(f"已启动: {exe}")
    log_fn("若内核未自动起来，请在软件里手动打开「系统代理」或点击启动。")


def wait_for_api(base: str, secret: str, timeout: float, log_fn) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if clash_api_alive(base, secret):
            return True
        time.sleep(1.0)
    return False


def wait_for_proxy(port: int, timeout: float, log_fn) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True
        except OSError:
            time.sleep(0.8)
    return False


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="超实惠加速：自动识别协议并优选 Telegram 视频节点"
    )
    parser.add_argument("--api", default=None, help="已开启的 Clash API，如 http://127.0.0.1:19690")
    parser.add_argument("--secret", default="", help="API secret（若有）")
    parser.add_argument("--proxy", default=None, help="HTTP 代理，默认读软件 mixed-port")
    parser.add_argument("--group", default=None, help="策略组（默认自动）")
    parser.add_argument("--filter", default=None, help="节点名正则，如 '香港|日本|HK|JP'")
    parser.add_argument("--limit", type=int, default=0, help="精测最多 N 个")
    parser.add_argument("--duration", type=float, default=5.0, help="下载测速秒数")
    parser.add_argument("--settle", type=float, default=0.8, help="切换后等待秒数")
    parser.add_argument("--preflight-top", type=int, default=8, help="预筛后精测数量")
    parser.add_argument("--no-preflight", action="store_true")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--tg-abort-ms", type=float, default=tgp.TG_ABORT_MS)
    parser.add_argument(
        "--no-keep-stable",
        action="store_true",
        help="精测后不切回当前最佳",
    )
    parser.add_argument("--restore-original", action="store_true")
    parser.add_argument("--no-apply", action="store_true", help="测完不切最优")
    parser.add_argument(
        "--no-enable-api",
        action="store_true",
        help="禁止自动写入 external-controller",
    )
    parser.add_argument(
        "--restart",
        action="store_true",
        help="写入 API 后自动重启超实惠加速（首次启用 API 时建议加）",
    )
    parser.add_argument("--api-port", type=int, default=DEFAULT_API_PORT)
    parser.add_argument("--result-dir", default=None)
    args = parser.parse_args()

    do_enable = not args.no_enable_api
    keep_stable = not args.no_keep_stable
    do_preflight = not args.no_preflight

    repo_root = SCRIPT_DIR.parent.parent
    result_dir = Path(args.result_dir) if args.result_dir else repo_root / "result"
    top5_dir = result_dir / "top5"
    result_dir.mkdir(parents=True, exist_ok=True)
    top5_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logfile = result_dir / f"tg_csh_{stamp}.log"
    top5_file = top5_dir / f"csh_{stamp}.txt"

    with logfile.open("w", encoding="utf-8") as fp:
        def log(msg: str = ""):
            L(msg, fp)

        log("=" * 60)
        log("超实惠加速 · Telegram 视频节点优选")
        log(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log("=" * 60)

        # ---- 1. 识别软件 ----
        procs = find_processes()
        install = find_install_dir()
        data_dir = find_data_dir()
        fpinfo = fingerprint_core(install)

        log()
        log(">>> [识别]")
        log(f"  进程: {procs or '未发现（请先打开超实惠加速）'}")
        log(f"  安装: {install or '未找到'}")
        log(f"  数据: {data_dir or '未找到'}")
        log(f"  家族: {fpinfo['family']}")
        log(f"  引擎: {fpinfo['engine']}")
        log(f"  控制面: {fpinfo['control']}")
        log(f"  细节: {fpinfo['detail']}")

        if "chaoshihui" not in procs and not data_dir:
            log()
            log("未检测到超实惠加速。请先启动该软件后再运行本脚本。")
            return 1

        if data_dir is None:
            log("找不到 AppData 配置目录，无法读取 mixed-port / 开启 API。")
            return 1

        prefs = load_prefs(data_dir)
        cfg = prefs["config"]
        mixed_port = get_mixed_port(cfg)
        proxy_url = args.proxy or f"http://127.0.0.1:{mixed_port}"
        ext = get_external_controller(cfg)
        log(f"  mixed-port: {mixed_port}")
        ext_disp = repr(ext) if ext else "(空)"
        log(f"  当前 external-controller 配置: {ext_disp}")
        log(f"  测速代理: {proxy_url}")

        # ---- 2. 找到 / 开启 Clash API ----
        api_base = args.api
        secret = args.secret or os.environ.get("CLASH_SECRET", "")

        if not api_base:
            api_base = probe_existing_api(secret)
            if api_base:
                log(f"  发现已可用 API: {api_base}")

        if not api_base:
            port = args.api_port
            if not port_free(port):
                port = pick_api_port(port)
            hostport = f"127.0.0.1:{port}"
            api_base = f"http://{hostport}"

            if do_enable:
                log()
                log(">>> [开启 External Controller]")
                log("  协议结论: 该软件基于 Clash Meta，节点切换走 Clash REST API。")
                log("  GUI↔内核另有 FlClash 私有 IPC（配置加密），脚本不走 IPC。")
                changed = enable_external_controller(data_dir, hostport, log)
                if args.restart or changed:
                    if not args.restart:
                        log("  已写入配置，但内核需重启后才会监听 API。")
                        log("  请加参数 --restart，或手动重启「超实惠加速」后再跑。")
                        log(f"  示例: python 工具/script/telegramCshPick.py --restart")
                        if not clash_api_alive(api_base, secret):
                            return 3
                    else:
                        if not install:
                            log("  找不到安装目录，无法自动重启。请手动重启软件。")
                            return 3
                        restart_chaoshihui(install, log)
                        log("  等待内核 / API ...")
                        if not wait_for_proxy(mixed_port, 45, log):
                            log(f"  mixed-port {mixed_port} 未就绪，请在软件内打开系统代理。")
                        if not wait_for_api(api_base, secret, 45, log):
                            log(f"  API {api_base} 未就绪。")
                            log("  可能原因:")
                            log("    1) 软件残留进程未退出（任务管理器结束全部 chaoshihui）")
                            log("    2) 内核未启动（在软件内打开「系统代理」）")
                            log("    3) 设置里把外部控制器改回了空（应保留 127.0.0.1:端口）")
                            log(f"  当前期望 API: {api_base}")
                            log("  处理完后重新执行本脚本（已写入过配置则不必再 --restart）。")
                            return 3
                else:
                    if not wait_for_api(api_base, secret, 5, log):
                        log(f"  API 仍不可用: {api_base}")
                        return 3
            else:
                log("未找到 Clash API，且未允许自动开启（--no-enable-api）。")
                log("请在超实惠加速设置中开启外部控制器，或使用 --api / --restart。")
                return 3

        if not clash_api_alive(api_base, secret):
            log(f"Clash API 不可用: {api_base}")
            return 3

        api = tgp.ClashAPI(api_base, secret)
        try:
            ver = api.version()
            clash_cfg = api.configs()
            proxies = api.proxies()
        except Exception as e:
            log(f"读取 Clash API 失败: {e}")
            return 3

        mode = (clash_cfg.get("mode") or "rule").lower()
        group = args.group or tgp.pick_default_group(proxies, mode)
        if group not in proxies:
            log(f"策略组不存在: {group}")
            return 1

        original = proxies[group].get("now")
        nodes = tgp.filter_nodes(tgp.list_nodes(proxies, group), args.filter)

        log()
        log(">>> [就绪]")
        log(f"  API: {api_base}  core={ver.get('version')}  mode={mode}")
        log(f"  策略组: {group}  当前: {original}")
        log(f"  候选: {len(nodes)}" + (f"  filter=/{args.filter}/" if args.filter else ""))
        log(f"  日志: {logfile}")
        log(f"  Top5: {top5_file}")

        if not nodes:
            log("没有可测节点")
            return 1

        # 确认代理口可用
        try:
            with socket.create_connection(("127.0.0.1", mixed_port), timeout=2):
                pass
        except OSError:
            log(f"警告: mixed-port {mixed_port} 连不上，请先在软件内开启系统代理。")

        # ---- 3. 预筛 + 精测（与 telegramNodePick 同策略）----
        pre_map: dict[str, int] = {}
        if do_preflight:
            log()
            log(f">>> [1/2 预筛] Clash delay → {tgp.PREFLIGHT_URL}（不切换）")
            ranked_pre = tgp.preflight_nodes(
                api, nodes, tgp.PREFLIGHT_URL, 4000, args.workers, log
            )
            for d, n in ranked_pre:
                pre_map[n] = d
            fine_n = args.preflight_top
            if args.limit and args.limit > 0:
                fine_n = min(fine_n, args.limit)
            nodes = [n for _, n in ranked_pre[:fine_n]]
            if not nodes:
                log("预筛后无可用节点")
                tgp.restore_stable(api, group, original)
                return 1
            log(f"精测前 {len(nodes)} 名:")
            for i, name in enumerate(nodes, 1):
                log(f"  {i}. {pre_map.get(name)}ms  {name}")
        elif args.limit and args.limit > 0:
            nodes = nodes[: args.limit]

        tgp.restore_stable(api, group, original)

        results: list[tgp.NodeResult] = []
        best_node: Optional[str] = None
        best_score = float("-inf")
        restore_original = args.restore_original

        log()
        log(
            f">>> [2/2 精测] {len(nodes)} 个 | 下载≈{args.duration:.0f}s | "
            f"{'保持当前最佳' if keep_stable else '不保持'}"
        )

        try:
            for i, name in enumerate(nodes, 1):
                restore_target = (
                    original if (restore_original or best_node is None) else best_node
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
        log(f">>> 最优: {best.name}  score={best.score}  {best.download_mbs:.2f}MB/s  TG={best.tg_ms:.0f}ms")
        for i, r in enumerate(top5, 1):
            log(f"  Top{i}: [{r.score:.1f}] {r.name}  {r.download_mbs:.2f}MB/s  TG={r.tg_ms:.0f}ms")

        final_node = original
        if args.no_apply:
            tgp.restore_stable(api, group, original)
            final_node = original
            log(f"保持原节点: {original}")
        else:
            api.switch(group, best.name)
            api.close_connections()
            final_node = best.name
            log(f"已切换到最优: {best.name}")
            if group != "GLOBAL" and mode == "global" and "GLOBAL" in proxies:
                try:
                    api.switch("GLOBAL", best.name)
                except Exception:
                    pass

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
        # 文件头补充软件信息
        extra = (
            f"软件: 超实惠加速\n"
            f"引擎: {fpinfo['engine']}\n"
            f"家族: {fpinfo['family']}\n"
            f"控制: Clash External Controller\n"
            f"代理: {proxy_url}\n"
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
