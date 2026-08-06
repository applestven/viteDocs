#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动切换 Clash 节点，挑选最适合看 Telegram 视频的节点。

默认策略（尽量少打断日常上网）:
  1. 无切换预筛：用 Clash delay API 测 Telegram URL（不改当前节点）
  2. 只对预筛前列做精测（切换 + TG延迟 + 下载）
  3. 精测期间保持“当前最佳节点”：测到更高分就切过去并保持；测完较差节点立刻切回当前最佳
  4. 慢节点早停（TG 过慢则跳过下载）
  5. 结束写出 Top5 到 result/top5/时间戳.txt，并切到最优

依赖: pip install requests
适用: Clash for Windows / Clash Meta / Clash Verge(需开启外部控制)
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from urllib.parse import quote

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


SKIP_NODE_NAMES = {
    "DIRECT",
    "REJECT",
    "REJECT-DROP",
    "PASS",
    "COMPATIBLE",
    "GLOBAL",
}

GROUP_TYPE = {"Selector", "URLTest", "Fallback", "LoadBalance"}

# 预筛用 Telegram 探测地址（不切换节点）
PREFLIGHT_URL = "https://api.telegram.org"
# 精测时 TG 首包超过此值则跳过下载，尽快切回
TG_ABORT_MS = 2500.0


@dataclass
class NodeResult:
    name: str
    ok: bool = False
    tg_ms: float = 9999.0
    tg_jitter: float = 9999.0
    download_mbs: float = 0.0
    download_detail: str = ""
    score: float = -1.0
    preflight_ms: Optional[int] = None
    error: str = ""
    samples: list = field(default_factory=list)


class ClashAPI:
    def __init__(self, base: str, secret: str = "", timeout: float = 8.0):
        self.base = base.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        if secret:
            self.session.headers["Authorization"] = f"Bearer {secret}"

    def _url(self, path: str) -> str:
        return self.base + path

    def get(self, path: str, **kw):
        return self.session.get(self._url(path), timeout=kw.pop("timeout", self.timeout), **kw)

    def put(self, path: str, **kw):
        return self.session.put(self._url(path), timeout=kw.pop("timeout", self.timeout), **kw)

    def delete(self, path: str, **kw):
        return self.session.delete(self._url(path), timeout=kw.pop("timeout", self.timeout), **kw)

    def version(self) -> dict:
        r = self.get("/version")
        r.raise_for_status()
        return r.json()

    def configs(self) -> dict:
        r = self.get("/configs")
        r.raise_for_status()
        return r.json()

    def proxies(self) -> dict:
        r = self.get("/proxies")
        r.raise_for_status()
        return r.json().get("proxies") or {}

    def switch(self, group: str, node: str) -> None:
        path = f"/proxies/{quote(group, safe='')}"
        r = self.put(path, json={"name": node})
        if r.status_code >= 400:
            raise RuntimeError(f"切换失败 HTTP {r.status_code}: {r.text[:200]}")

    def close_connections(self) -> None:
        try:
            self.delete("/connections")
        except Exception:
            pass

    def delay(self, node: str, url: str, timeout_ms: int = 5000) -> Optional[int]:
        """测指定出站延迟，不切换当前选中节点。"""
        path = f"/proxies/{quote(node, safe='')}/delay"
        try:
            r = self.get(
                path,
                params={"url": url, "timeout": timeout_ms},
                timeout=timeout_ms / 1000 + 2,
            )
            if r.status_code != 200:
                return None
            return int(r.json().get("delay") or 0) or None
        except Exception:
            return None


def log(msg: str = "", fp=None):
    print(msg, flush=True)
    if fp:
        fp.write(msg + "\n")
        fp.flush()


def discover_api(explicit: Optional[str] = None) -> tuple[str, str]:
    """返回 (api_base, secret)。优先显式参数，再扫常见 Clash 配置。"""
    if explicit:
        return explicit.rstrip("/"), ""

    env = os.environ.get("CLASH_API") or os.environ.get("CLASH_EXTERNAL_CONTROLLER")
    if env:
        if not env.startswith("http"):
            env = "http://" + env
        return env.rstrip("/"), os.environ.get("CLASH_SECRET", "")

    candidates = []
    home = os.path.expanduser("~")
    soft = [
        r"D:\soft\Clash.for.Windows-0.20.16-ikuuu\data\config.yaml",
        os.path.join(home, "AppData", "Roaming", "io.github.clash-verge-rev.clash-verge-rev", "config.yaml"),
        os.path.join(home, "AppData", "Roaming", "io.github.clash-verge-rev.clash-verge-rev", "clash-verge.yaml"),
        os.path.join(home, ".config", "clash", "config.yaml"),
        os.path.join(home, ".config", "mihomo", "config.yaml"),
    ]
    soft_root = r"D:\soft"
    if os.path.isdir(soft_root):
        for name in os.listdir(soft_root):
            if "clash" in name.lower() and "window" in name.lower():
                p = os.path.join(soft_root, name, "data", "config.yaml")
                if os.path.isfile(p):
                    soft.append(p)

    for path in soft:
        if not os.path.isfile(path):
            continue
        try:
            text = open(path, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        ctrl = None
        secret = ""
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("external-controller:"):
                ctrl = s.split(":", 1)[1].strip().strip("'\"")
            elif s.startswith("secret:"):
                secret = s.split(":", 1)[1].strip().strip("'\"")
                if secret.lower() in ("null", "~", ""):
                    secret = ""
        if ctrl and ctrl not in ("", "''", '""'):
            if not ctrl.startswith("http"):
                ctrl = "http://" + ctrl
            candidates.append((ctrl, secret, path))

    for base, secret, path in candidates:
        try:
            api = ClashAPI(base, secret)
            api.version()
            return base, secret
        except Exception:
            continue

    for port in (9090, 9097, 9091, 6170):
        base = f"http://127.0.0.1:{port}"
        try:
            ClashAPI(base).version()
            return base, ""
        except Exception:
            continue

    raise RuntimeError(
        "找不到可用的 Clash API。\n"
        "请确认 Clash 已启动；CFW 可看 General → External Controller；\n"
        "或手动指定: --api http://127.0.0.1:端口"
    )


def pick_default_group(proxies: dict, mode: str) -> str:
    if mode == "global" and "GLOBAL" in proxies:
        return "GLOBAL"
    preferred = ["🔰 选择节点", "PROXY", "Proxy", "节点选择", "手动选择", "🚀 节点选择"]
    for name in preferred:
        if name in proxies and proxies[name].get("type") in GROUP_TYPE:
            return name
    best, best_n = None, -1
    for name, info in proxies.items():
        if info.get("type") != "Selector":
            continue
        n = len(info.get("all") or [])
        if n > best_n:
            best, best_n = name, n
    if best:
        return best
    raise RuntimeError("未找到可切换的 Selector 策略组")


def list_nodes(proxies: dict, group: str) -> list[str]:
    info = proxies.get(group)
    if not info:
        raise RuntimeError(f"策略组不存在: {group}")
    nodes = []
    for name in info.get("all") or []:
        if name in SKIP_NODE_NAMES:
            continue
        child = proxies.get(name)
        if child and child.get("type") in GROUP_TYPE:
            continue
        nodes.append(name)
    return nodes


def filter_nodes(nodes: list[str], pattern: Optional[str]) -> list[str]:
    if not pattern:
        return nodes
    rx = re.compile(pattern, re.I)
    return [n for n in nodes if rx.search(n)]


def restore_stable(api: ClashAPI, group: str, original: Optional[str]) -> None:
    if not original:
        return
    try:
        api.switch(group, original)
        api.close_connections()
    except Exception:
        pass


def https_ttfb(
    url: str,
    proxies: dict,
    rounds: int = 1,
    timeout: float = 8.0,
) -> tuple[Optional[float], Optional[float], list[float]]:
    times: list[float] = []
    for _ in range(rounds):
        try:
            t0 = time.perf_counter()
            r = requests.get(
                url,
                proxies=proxies,
                timeout=timeout,
                stream=True,
                headers={"User-Agent": "telegram-node-pick/1.0"},
            )
            _ = next(r.iter_content(4096), b"")
            ms = (time.perf_counter() - t0) * 1000
            r.close()
            times.append(ms)
        except Exception:
            times.append(9999.0)
    ok = [x for x in times if x < 9999]
    if not ok:
        return None, None, times
    avg = sum(ok) / len(ok)
    if len(ok) >= 2:
        jitter = (sum((x - avg) ** 2 for x in ok) / len(ok)) ** 0.5
    else:
        jitter = 0.0
    return avg, jitter, times


def download_speed(
    url: str,
    proxies: dict,
    duration: float = 5.0,
    timeout: float = 15.0,
    min_mbs_early: float = 0.3,
    early_check_s: float = 2.0,
) -> tuple[Optional[float], str]:
    """下载测速；前 early_check_s 秒若极慢则提前结束。"""
    try:
        t0 = time.perf_counter()
        total = 0
        r = requests.get(
            url,
            proxies=proxies,
            stream=True,
            timeout=timeout,
            headers={"User-Agent": "telegram-node-pick/1.0"},
        )
        r.raise_for_status()
        aborted = False
        for chunk in r.iter_content(256 * 1024):
            if not chunk:
                continue
            total += len(chunk)
            elapsed = time.perf_counter() - t0
            if elapsed >= early_check_s and total > 0:
                cur = (total / 1024 / 1024) / elapsed
                if cur < min_mbs_early:
                    aborted = True
                    break
            if elapsed >= duration:
                break
        r.close()
        cost = time.perf_counter() - t0
        if cost <= 0 or total == 0:
            return None, "无数据"
        mbs = (total / 1024 / 1024) / cost
        tag = f"{total/1024/1024:.1f}MB/{cost:.1f}s"
        if aborted:
            tag += " 早停"
        return mbs, tag
    except Exception as e:
        return None, str(e)


def score_node(tg_ms: Optional[float], jitter: Optional[float], mbs: Optional[float]) -> float:
    """看视频导向: 带宽 50% + TG延迟 40% + 稳定 10%。满分 100。"""
    if tg_ms is None or mbs is None:
        return -1.0
    bw = max(0.0, min(mbs / 10.0, 1.0)) * 50.0
    lat = max(0.0, min(1.0, (3000.0 - tg_ms) / 2500.0)) * 40.0
    jit = jitter if jitter is not None else 0.0
    stab = max(0.0, min(1.0, (500.0 - jit) / 500.0)) * 10.0
    return round(bw + lat + stab, 2)


def preflight_nodes(
    api: ClashAPI,
    nodes: list[str],
    url: str,
    timeout_ms: int,
    workers: int,
    log_fn,
) -> list[tuple[int, str]]:
    """并行 delay，不切换当前节点。返回 [(delay_ms, name), ...] 升序。"""
    results: list[tuple[int, str]] = []
    done = 0
    total = len(nodes)

    def one(name: str):
        return name, api.delay(name, url, timeout_ms)

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futs = {pool.submit(one, n): n for n in nodes}
        for fut in as_completed(futs):
            name, delay = fut.result()
            done += 1
            tag = f"{delay}ms" if delay else "超时"
            log_fn(f"  [{done}/{total}] {tag:<8} {name}")
            if delay:
                results.append((delay, name))
    results.sort()
    return results


def benchmark_node(
    api: ClashAPI,
    group: str,
    node: str,
    http_proxy: str,
    duration: float,
    settle: float,
    original: Optional[str],
    keep_stable: bool,
    tg_abort_ms: float,
) -> NodeResult:
    result = NodeResult(name=node)
    proxies = {"http": http_proxy, "https": http_proxy}
    try:
        api.switch(group, node)
        api.close_connections()
        time.sleep(settle)

        # 先测 api.telegram.org；过慢则早停，少打断
        avg, jit, samples = https_ttfb(
            "https://api.telegram.org",
            proxies,
            rounds=1,
            timeout=min(8.0, tg_abort_ms / 1000 + 2),
        )
        result.samples.extend(samples)
        if avg is None:
            result.error = "TG 访问失败: api.telegram.org"
            return result
        if avg > tg_abort_ms:
            result.tg_ms = avg
            result.tg_jitter = jit or 0.0
            result.error = f"TG 过慢早停 ({avg:.0f}ms > {tg_abort_ms:.0f}ms)"
            return result

        avg2, jit2, samples2 = https_ttfb("https://t.me", proxies, rounds=1, timeout=8.0)
        result.samples.extend(samples2)
        if avg2 is None:
            result.tg_ms = avg
            result.tg_jitter = jit or 0.0
            result.error = "TG 访问失败: t.me"
            return result

        result.tg_ms = (avg + avg2) / 2
        result.tg_jitter = ((jit or 0.0) + (jit2 or 0.0)) / 2

        mbs, detail = download_speed(
            "http://speedtest.tele2.net/100MB.zip",
            proxies,
            duration=duration,
        )
        if mbs is None:
            result.error = f"下载失败: {detail}"
            return result
        result.download_mbs = mbs
        result.download_detail = detail
        result.score = score_node(result.tg_ms, result.tg_jitter, mbs)
        result.ok = True
        return result
    except Exception as e:
        result.error = str(e)
        return result
    finally:
        if keep_stable:
            restore_stable(api, group, original)


def format_table(results: list[NodeResult], only_ok: bool = False) -> list[str]:
    lines = []
    header = f"{'#':<4}{'得分':<8}{'带宽MB/s':<10}{'TG延迟':<10}{'抖动':<8}{'节点'}"
    lines.append(header)
    lines.append("-" * (len(header) + 24))
    ranked = sorted(results, key=lambda x: x.score, reverse=True)
    if only_ok:
        ranked = [r for r in ranked if r.ok]
    for i, r in enumerate(ranked, 1):
        if r.ok:
            lines.append(
                f"{i:<4}{r.score:<8.1f}{r.download_mbs:<10.2f}{r.tg_ms:<10.0f}{r.tg_jitter:<8.0f}{r.name}"
            )
        else:
            lines.append(
                f"{i:<4}{'--':<8}{'--':<10}{'--':<10}{'--':<8}{r.name}  ({r.error})"
            )
    return lines


def write_top5(path: str, top: list[NodeResult], meta: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = [
        "Telegram 视频节点 Top5",
        f"时间: {meta.get('time', '')}",
        f"API: {meta.get('api', '')}",
        f"策略组: {meta.get('group', '')}",
        f"原节点: {meta.get('original', '')}",
        f"最终节点: {meta.get('final', '')}",
        "",
        f"{'#':<4}{'得分':<8}{'带宽MB/s':<10}{'TG延迟ms':<10}{'抖动ms':<8}{'节点'}",
        "-" * 72,
    ]
    for i, r in enumerate(top, 1):
        lines.append(
            f"{i:<4}{r.score:<8.1f}{r.download_mbs:<10.2f}{r.tg_ms:<10.0f}{r.tg_jitter:<8.0f}{r.name}"
        )
    lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="自动切换 Clash 节点，选出最适合 Telegram 视频的节点（默认少打断）"
    )
    parser.add_argument("--api", default=None, help="Clash API 地址，如 http://127.0.0.1:9090")
    parser.add_argument("--secret", default="", help="Clash API secret（若有）")
    parser.add_argument("--proxy", default="http://127.0.0.1:7890", help="本地 HTTP 代理")
    parser.add_argument("--group", default=None, help="策略组名（默认自动：Global 模式用 GLOBAL）")
    parser.add_argument("--filter", default=None, help="节点名正则过滤，如 '香港|日本|新加坡'")
    parser.add_argument("--limit", type=int, default=0, help="精测最多 N 个（0=用预筛 top）")
    parser.add_argument("--duration", type=float, default=5.0, help="每个节点下载测速秒数")
    parser.add_argument("--settle", type=float, default=0.8, help="切换后等待秒数")
    parser.add_argument(
        "--preflight-top",
        type=int,
        default=8,
        help="无切换预筛后精测前 N 名（默认 8）",
    )
    parser.add_argument(
        "--no-preflight",
        action="store_true",
        help="关闭预筛（会对更多节点切换，打断更明显）",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="预筛并行数（默认 8，不切换节点）",
    )
    parser.add_argument(
        "--tg-abort-ms",
        type=float,
        default=TG_ABORT_MS,
        help=f"精测 TG 超过该毫秒则跳过下载并切回（默认 {int(TG_ABORT_MS)}）",
    )
    parser.add_argument(
        "--no-keep-stable",
        action="store_true",
        help="精测时不在每个节点后切回原节点（更快但全程网络不稳）",
    )
    parser.add_argument(
        "--restore-original",
        action="store_true",
        help="精测后始终切回初始原节点（旧行为）；默认是切回“当前最佳节点”。",
    )
    parser.add_argument("--no-apply", action="store_true", help="测完不切最优，保持原节点")
    parser.add_argument("--result-dir", default=None, help="日志根目录（默认仓库 result/）")
    args = parser.parse_args()

    keep_stable = not args.no_keep_stable
    restore_original = args.restore_original
    do_preflight = not args.no_preflight

    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    result_dir = args.result_dir or os.path.join(repo_root, "result")
    top5_dir = os.path.join(result_dir, "top5")
    os.makedirs(result_dir, exist_ok=True)
    os.makedirs(top5_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logfile = os.path.join(result_dir, f"tg_nodes_{stamp}.log")
    top5_file = os.path.join(top5_dir, f"{stamp}.txt")

    try:
        api_base, discovered_secret = discover_api(args.api)
    except RuntimeError as e:
        print(e)
        return 1

    secret = args.secret or discovered_secret or os.environ.get("CLASH_SECRET", "")
    api = ClashAPI(api_base, secret)

    with open(logfile, "w", encoding="utf-8") as fp:
        def L(msg: str = ""):
            log(msg, fp)

        try:
            ver = api.version()
            cfg = api.configs()
            proxies = api.proxies()
        except Exception as e:
            L(f"连接 Clash API 失败: {api_base} ({e})")
            return 1

        mode = (cfg.get("mode") or "rule").lower()
        group = args.group or pick_default_group(proxies, mode)
        if group not in proxies:
            L(f"策略组不存在: {group}")
            return 1

        original = proxies[group].get("now")
        nodes = list_nodes(proxies, group)
        nodes = filter_nodes(nodes, args.filter)

        L("=" * 60)
        L("Telegram 视频节点优选")
        L(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        L(f"API : {api_base}  core={ver.get('version')}  mode={mode}")
        L(f"代理: {args.proxy}")
        L(f"策略组: {group}  当前稳定节点: {original}")
        L(f"候选: {len(nodes)} 个" + (f"  filter=/{args.filter}/" if args.filter else ""))
        L(
            f"策略: 预筛={'开' if do_preflight else '关'}  "
            f"精测后切回={'原节点' if restore_original else '当前最佳'}（{'开' if keep_stable else '关'}）  "
            f"TG早停={args.tg_abort_ms:.0f}ms"
        )
        L(f"日志: {logfile}")
        L(f"Top5: {top5_file}")
        L("=" * 60)
        L("说明: 预筛不切换节点，上网不受影响；仅精测阶段短暂切换。")

        if not nodes:
            L("没有可测节点（检查 --group / --filter）")
            return 1

        pre_map: dict[str, int] = {}

        # ---- 阶段1: 无切换预筛 ----
        if do_preflight:
            L()
            L(f">>> [1/2 预筛] Clash delay → {PREFLIGHT_URL}（不切换，并行 {args.workers}）")
            ranked_pre = preflight_nodes(
                api,
                nodes,
                PREFLIGHT_URL,
                timeout_ms=4000,
                workers=args.workers,
                log_fn=L,
            )
            for d, n in ranked_pre:
                pre_map[n] = d

            fine_n = args.preflight_top
            if args.limit and args.limit > 0:
                fine_n = min(fine_n, args.limit)

            nodes = [n for _, n in ranked_pre[:fine_n]]
            if not nodes:
                L("预筛后无可用节点")
                restore_stable(api, group, original)
                return 1
            L(f"预筛通过 {len(ranked_pre)}，精测前 {len(nodes)} 名:")
            for i, name in enumerate(nodes, 1):
                L(f"  {i}. {pre_map.get(name)}ms  {name}")
        else:
            if args.limit and args.limit > 0:
                nodes = nodes[: args.limit]
                L(f"无预筛，截断为前 {len(nodes)} 个（--limit）")

        # 确认仍在原节点（预筛不应改动，双保险）
        restore_stable(api, group, original)

        # ---- 阶段2: 精测（短时切换）----
        results: list[NodeResult] = []
        L()
        L(
            f">>> [2/2 精测] 共 {len(nodes)} 个 | "
            f"下载≈{args.duration:.0f}s | "
            f"{'测完后切回当前最佳' if keep_stable else '连续切换不切回'}"
            + (f"（初始={original}）" if keep_stable else "")
        )

        best_node: Optional[str] = None
        best_score = float("-inf")

        try:
            for i, name in enumerate(nodes, 1):
                # 若要保持网络稳定，就在测候选前把“恢复目标”设为：
                #   - restore_original=True: 初始原节点
                #   - 否则：当前最佳节点（避免节点3这种差节点把日常长期切走）
                restore_target = original if (restore_original or best_node is None) else best_node

                L(f"\n--- ({i}/{len(nodes)}) {name}" + (f"  预筛{pre_map[name]}ms" if name in pre_map else ""))
                r = benchmark_node(
                    api,
                    group,
                    name,
                    args.proxy,
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
                    L(
                        f"  TG={r.tg_ms:.0f}ms  jitter={r.tg_jitter:.0f}ms  "
                        f"down={r.download_mbs:.2f}MB/s ({r.download_detail})  score={r.score}"
                    )
                else:
                    L(f"  跳过/失败: {r.error}")

                # 更新当前最佳：一旦测到更高分，就切到该节点并“保持”
                if r.ok and (best_node is None or r.score > best_score):
                    best_node = name
                    best_score = r.score
                    if keep_stable:
                        # benchmark_node 会在 finally 把网络切回 restore_target，
                        # 所以这里需要再切回“新的最佳节点”。
                        api.switch(group, best_node)
                        api.close_connections()
                        time.sleep(args.settle)
                    L(f"  → 发现更优，当前最佳节点: {best_node}")
                else:
                    if keep_stable:
                        L(f"  → 保持当前最佳: {best_node or original}")
        except KeyboardInterrupt:
            L("\n中断，恢复稳定节点...")
            restore_stable(api, group, original)
            raise

        L()
        L("=" * 60)
        L("排行榜（看视频综合分，越高越好）")
        L("=" * 60)
        for line in format_table(results):
            L(line)

        ok_results = [r for r in results if r.ok]
        if not ok_results:
            L()
            L("精测全部失败，保持原节点: " + str(original))
            restore_stable(api, group, original)
            return 2

        ok_results.sort(key=lambda x: x.score, reverse=True)
        best = ok_results[0]
        top5 = ok_results[:5]

        L()
        L(f">>> 最优节点: {best.name}")
        L(f"    得分={best.score}  带宽={best.download_mbs:.2f}MB/s  TG={best.tg_ms:.0f}ms")
        L()
        L("Top5:")
        for i, r in enumerate(top5, 1):
            L(f"  {i}. [{r.score:.1f}] {r.name}  {r.download_mbs:.2f}MB/s  TG={r.tg_ms:.0f}ms")

        final_node = original
        if args.no_apply:
            restore_stable(api, group, original)
            final_node = original
            L(f"已保持原节点: {original}（--no-apply）")
        else:
            api.switch(group, best.name)
            api.close_connections()
            final_node = best.name
            L(f"已切换到最优节点: {best.name}")
            if group != "GLOBAL" and mode == "global" and "GLOBAL" in proxies:
                try:
                    api.switch("GLOBAL", best.name)
                    L("已同步 GLOBAL 组")
                except Exception:
                    pass

        write_top5(
            top5_file,
            top5,
            {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "api": api_base,
                "group": group,
                "original": original,
                "final": final_node,
            },
        )
        L()
        L(f"Top5 已写入: {top5_file}")
        L(f"完整日志: {logfile}")
        L("=" * 60)
        return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\n已中断", flush=True)
        raise SystemExit(130)
