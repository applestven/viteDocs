#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram 看视频卡顿诊断

链路: 本地网络 --> 代理 --> Telegram
目标: 分段测速，明确瓶颈在哪一段。
"""

from __future__ import annotations

import argparse
import os
import socket
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("缺少依赖: pip install requests")
    sys.exit(1)

# Windows 控制台中文输出
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# ======================
# 阈值（经验值，用于诊断）
# ======================

THRESH = {
    "dns_ms": 100,
    "local_ping_ms": 80,
    "local_tcp_ms": 200,
    "proxy_connect_ms": 50,
    "proxy_https_ms": 800,
    "tg_https_ms": 1500,
    "download_mbs": 2.0,  # 低于此值看视频容易卡
    "jitter_ms": 200,
}


# ======================
# 数据结构
# ======================

@dataclass
class Sample:
    ok: bool
    value: float = 0.0
    detail: str = ""
    samples: list = field(default_factory=list)


@dataclass
class Report:
    local_dns: dict = field(default_factory=dict)
    local_ping: Optional[Sample] = None
    local_tcp: Optional[Sample] = None
    proxy_alive: Optional[Sample] = None
    proxy_https: dict = field(default_factory=dict)
    proxy_download: Optional[Sample] = None
    tg_https: dict = field(default_factory=dict)
    tg_vs_proxy_ratio: float = 0.0


# ======================
# 工具
# ======================

class Logger:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    def __call__(self, msg: str = ""):
        print(msg, flush=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(msg + "\n")


def mean_ok(values: list[float], fail: float = 9999.0) -> Optional[float]:
    ok = [v for v in values if v < fail]
    return statistics.mean(ok) if ok else None


def jitter(values: list[float], fail: float = 9999.0) -> Optional[float]:
    ok = [v for v in values if v < fail]
    if len(ok) < 2:
        return None
    return statistics.pstdev(ok)


def fmt_ms(v: Optional[float]) -> str:
    if v is None:
        return "失败"
    return f"{v:.1f}ms"


def fmt_mbs(v: Optional[float]) -> str:
    if v is None:
        return "失败"
    return f"{v:.2f} MB/s"


def grade(value: Optional[float], good: float, bad: float, higher_better: bool = False) -> str:
    if value is None:
        return "失败"
    if higher_better:
        if value >= good:
            return "良好"
        if value >= bad:
            return "一般"
        return "较差"
    if value <= good:
        return "良好"
    if value <= bad:
        return "一般"
    return "较差"


# ======================
# 探测函数
# ======================

def dns_lookup(host: str) -> Sample:
    try:
        t0 = time.perf_counter()
        ip = socket.gethostbyname(host)
        ms = (time.perf_counter() - t0) * 1000
        return Sample(True, ms, ip)
    except Exception as e:
        return Sample(False, detail=str(e))


def tcp_connect(host: str, port: int = 443, rounds: int = 5, timeout: float = 5.0) -> Sample:
    times: list[float] = []
    err = ""
    for _ in range(rounds):
        try:
            t0 = time.perf_counter()
            sock = socket.create_connection((host, port), timeout=timeout)
            sock.close()
            times.append((time.perf_counter() - t0) * 1000)
        except Exception as e:
            times.append(9999.0)
            err = str(e)
    avg = mean_ok(times)
    return Sample(avg is not None, avg or 9999.0, err, times)


def proxy_port_check(host: str, port: int, rounds: int = 5) -> Sample:
    return tcp_connect(host, port, rounds=rounds, timeout=2.0)


def https_ttfb(url: str, proxies: Optional[dict], rounds: int = 3, timeout: float = 15.0) -> Sample:
    times: list[float] = []
    err = ""
    status = 0
    for _ in range(rounds):
        try:
            t0 = time.perf_counter()
            r = requests.get(
                url,
                proxies=proxies,
                timeout=timeout,
                stream=True,
                allow_redirects=True,
                headers={"User-Agent": "telegram-speed-diag/1.0"},
            )
            # 读一点 body，更接近真实首包
            _ = next(r.iter_content(4096), b"")
            ms = (time.perf_counter() - t0) * 1000
            status = r.status_code
            r.close()
            times.append(ms)
        except Exception as e:
            times.append(9999.0)
            err = str(e)
    avg = mean_ok(times)
    detail = f"HTTP {status}" if avg is not None else err
    return Sample(avg is not None, avg or 9999.0, detail, times)


def download_speed(
    url: str,
    proxies: Optional[dict],
    duration: float = 15.0,
    timeout: float = 30.0,
) -> Sample:
    try:
        t0 = time.perf_counter()
        total = 0
        r = requests.get(
            url,
            proxies=proxies,
            stream=True,
            timeout=timeout,
            headers={"User-Agent": "telegram-speed-diag/1.0"},
        )
        r.raise_for_status()
        for chunk in r.iter_content(256 * 1024):
            if not chunk:
                continue
            total += len(chunk)
            if time.perf_counter() - t0 >= duration:
                break
        r.close()
        cost = time.perf_counter() - t0
        if cost <= 0 or total == 0:
            return Sample(False, detail="无数据")
        mbs = (total / 1024 / 1024) / cost
        return Sample(True, mbs, f"{total/1024/1024:.1f}MB / {cost:.1f}s")
    except Exception as e:
        return Sample(False, detail=str(e))


def ping_host(host: str, count: int = 8) -> Sample:
    """Windows: ping -n; 其他: ping -c"""
    is_win = sys.platform.startswith("win")
    cmd = ["ping", "-n" if is_win else "-c", str(count), host]
    try:
        out = subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT,
            timeout=count * 2 + 5,
            encoding="utf-8",
            errors="ignore",
        )
    except Exception as e:
        return Sample(False, detail=str(e))

    # 解析平均延迟
    avg = None
    for line in out.splitlines():
        line = line.strip()
        if "平均" in line or "Average" in line:
            # 中文: 平均 = 23ms / English: Average = 23ms
            for part in line.replace("=", " ").replace(",", " ").split():
                part = part.strip().lower().replace("ms", "")
                try:
                    avg = float(part)
                except ValueError:
                    continue
            break
        if "rtt min/avg/max" in line.lower() or "round-trip" in line.lower():
            # Linux: rtt min/avg/max/mdev = 1.2/2.3/4.5/0.6 ms
            try:
                nums = line.split("=")[-1].strip().split("/")
                avg = float(nums[1])
            except (IndexError, ValueError):
                pass
            break

    if avg is None:
        return Sample(False, detail="无法解析 ping 结果")
    return Sample(True, avg, f"{count} 次")


# ======================
# 诊断
# ======================

def diagnose(report: Report, log: Logger) -> None:
    log()
    log("=" * 56)
    log("诊断结论  本地 --> 代理 --> Telegram")
    log("=" * 56)

    issues: list[str] = []
    notes: list[str] = []

    # --- 本地（TCP 权重大于 ICMP：国内 ping 1.1.1.1 常虚高）---
    dns_vals = [s.value for s in report.local_dns.values() if s.ok]
    dns_avg = statistics.mean(dns_vals) if dns_vals else None
    local_hard_fail = False
    local_soft_warn = False

    if dns_avg is None or dns_avg > THRESH["dns_ms"]:
        local_hard_fail = True
        issues.append(f"本地 DNS 偏慢/失败 ({fmt_ms(dns_avg)})")
    if report.local_tcp and (not report.local_tcp.ok or report.local_tcp.value > THRESH["local_tcp_ms"]):
        local_hard_fail = True
        issues.append(
            f"本地直连 TCP 偏慢 ({fmt_ms(report.local_tcp.value if report.local_tcp.ok else None)})"
        )
    if report.local_ping and report.local_ping.ok and report.local_ping.value > THRESH["local_ping_ms"]:
        # ICMP 仅作提示，不单独判定本地故障
        local_soft_warn = True
        notes.append(
            f"Ping(1.1.1.1)={fmt_ms(report.local_ping.value)} 偏高，"
            f"但若 TCP 正常可忽略（ICMP 常被限速）"
        )

    local_label = "异常" if local_hard_fail else ("告警" if local_soft_warn else "正常")
    log(f"[1] 本地网络 ...... {local_label}")
    log(
        f"    DNS平均: {fmt_ms(dns_avg)}  |  "
        f"Ping(1.1.1.1): {fmt_ms(report.local_ping.value if report.local_ping and report.local_ping.ok else None)}"
    )
    log(
        f"    直连 Cloudflare TCP: "
        f"{fmt_ms(report.local_tcp.value if report.local_tcp and report.local_tcp.ok else None)}"
    )

    # --- 代理 ---
    proxy_alive_ok = report.proxy_alive is not None and report.proxy_alive.ok
    proxy_latency_ok = True
    bandwidth_ok = True

    if not proxy_alive_ok:
        issues.append("代理端口连不上（代理未开或端口不对）")
    elif report.proxy_alive and report.proxy_alive.value > THRESH["proxy_connect_ms"]:
        proxy_latency_ok = False
        issues.append(f"本机到代理端口偏慢 ({fmt_ms(report.proxy_alive.value)})")

    proxy_https_vals = [s.value for s in report.proxy_https.values() if s.ok]
    proxy_https_avg = statistics.mean(proxy_https_vals) if proxy_https_vals else None
    if proxy_https_avg is None or proxy_https_avg > THRESH["proxy_https_ms"]:
        proxy_latency_ok = False
        issues.append(f"经代理访问公共站点偏慢 ({fmt_ms(proxy_https_avg)})")

    dl = report.proxy_download
    if dl is None or not dl.ok:
        bandwidth_ok = False
        issues.append(f"经代理下载失败 ({dl.detail if dl else '无结果'})")
    elif dl.value < THRESH["download_mbs"]:
        bandwidth_ok = False
        issues.append(
            f"经代理带宽不足 ({fmt_mbs(dl.value)}，建议 ≥ {THRESH['download_mbs']} MB/s) —— 看视频卡顿主因之一"
        )

    proxy_ok = proxy_alive_ok and proxy_latency_ok and bandwidth_ok
    log(f"[2] 代理质量 ...... {'正常' if proxy_ok else '异常'}")
    log(
        f"    代理端口: "
        f"{fmt_ms(report.proxy_alive.value if report.proxy_alive and report.proxy_alive.ok else None)}"
    )
    log(
        f"    经代理 HTTPS: {fmt_ms(proxy_https_avg)}  |  "
        f"下载: {fmt_mbs(dl.value if dl and dl.ok else None)}"
    )

    # --- Telegram（api / t.me 更贴近业务，首页权重降低）---
    core_names = ("api.telegram.org", "t.me")
    core_vals = [report.tg_https[n].value for n in core_names if n in report.tg_https and report.tg_https[n].ok]
    all_vals = [s.value for s in report.tg_https.values() if s.ok]
    tg_core_avg = statistics.mean(core_vals) if core_vals else None
    tg_avg = statistics.mean(all_vals) if all_vals else None

    tg_jit_list = []
    for name in core_names:
        s = report.tg_https.get(name)
        if s:
            j = jitter(s.samples)
            if j is not None:
                tg_jit_list.append(j)
    tg_jit = statistics.mean(tg_jit_list) if tg_jit_list else None

    tg_ok = True
    tg_route_bad = False
    if tg_core_avg is None and tg_avg is None:
        tg_ok = False
        issues.append("经代理访问 Telegram 全部失败")
    else:
        use_avg = tg_core_avg if tg_core_avg is not None else tg_avg
        if use_avg is not None and use_avg > THRESH["tg_https_ms"]:
            tg_ok = False
            issues.append(f"Telegram 业务域名 HTTPS 偏慢 ({fmt_ms(use_avg)})")
        if proxy_https_avg and use_avg and proxy_https_avg > 0:
            report.tg_vs_proxy_ratio = use_avg / proxy_https_avg
            if report.tg_vs_proxy_ratio >= 2.5:
                tg_route_bad = True
                tg_ok = False
                issues.append(
                    f"Telegram 比公共站慢约 {report.tg_vs_proxy_ratio:.1f}x，"
                    f"节点/线路对 TG 不友好（代理 --> Telegram）"
                )
    if tg_jit is not None and tg_jit > THRESH["jitter_ms"]:
        tg_ok = False
        issues.append(f"Telegram 延迟抖动大 ({tg_jit:.0f}ms)，视频容易卡顿")

    log(f"[3] Telegram ...... {'正常' if tg_ok else '异常'}")
    log(
        f"    业务域名平均(api/t.me): {fmt_ms(tg_core_avg)}  |  "
        f"全部平均: {fmt_ms(tg_avg)}  |  抖动: {fmt_ms(tg_jit)}"
    )
    if report.tg_vs_proxy_ratio:
        log(f"    相对公共站倍率: {report.tg_vs_proxy_ratio:.2f}x")

    # --- 瓶颈定位（看视频优先级：带宽 > TG线路 > 代理延迟 > 本地）---
    log()
    if not proxy_alive_ok:
        bottleneck = "代理未启动或端口错误（本地 --> 代理）"
    elif not bandwidth_ok:
        bottleneck = "代理带宽不足（看视频卡顿主因）"
    elif tg_route_bad and proxy_latency_ok:
        bottleneck = "代理到 Telegram 的线路/节点差（代理 --> Telegram）"
    elif not tg_ok and proxy_ok:
        bottleneck = "代理到 Telegram 偏慢（代理 --> Telegram）"
    elif not proxy_latency_ok:
        bottleneck = "代理质量差（代理 --> 出口节点）"
    elif local_hard_fail:
        bottleneck = "本地网络（DNS/出口 TCP）"
    elif proxy_ok and tg_ok:
        bottleneck = "当前链路整体正常；若仍卡，多半是具体 CDN 节点或客户端未走代理"
    else:
        bottleneck = "混合问题，见下方条目"

    log(f">>> 瓶颈定位: {bottleneck}")
    log()
    if issues:
        log("问题明细:")
        for i, item in enumerate(issues, 1):
            log(f"  {i}. {item}")
    else:
        log("问题明细: 无")
    if notes:
        log("参考备注:")
        for n in notes:
            log(f"  - {n}")

    log()
    log("看视频建议:")
    suggestions: list[str] = []
    if not proxy_alive_ok:
        suggestions.append("确认代理软件已开启，端口与脚本 --proxy 一致")
    if not bandwidth_ok:
        suggestions.append("换带宽更高的代理节点；高清视频建议稳定 > 2–5 MB/s")
    if tg_route_bad or (tg_core_avg is not None and tg_core_avg > THRESH["tg_https_ms"]):
        suggestions.append("换对 Telegram 更友好的节点（常见：香港 / 新加坡 / 日韩）")
    if local_hard_fail:
        suggestions.append("先检查本机 Wi-Fi/网线、DNS（可试 223.5.5.5 / 1.1.1.1）")
    if proxy_ok and tg_ok and not local_hard_fail:
        suggestions.append("链路正常；可在客户端确认 Telegram 流量确实走了该代理")
    if not suggestions:
        suggestions.append("无明显瓶颈，可换节点对比或抓包确认 CDN")
    for s in suggestions:
        log(f"  - {s}")

    log("=" * 56)


# ======================
# 主流程
# ======================

def parse_proxy(proxy_url: str) -> tuple[str, int, dict]:
    if "://" not in proxy_url:
        proxy_url = "http://" + proxy_url
    u = urlparse(proxy_url)
    host = u.hostname or "127.0.0.1"
    port = u.port or 7890
    proxies = {"http": proxy_url, "https": proxy_url}
    return host, port, proxies


def main() -> int:
    parser = argparse.ArgumentParser(description="Telegram 视频卡顿链路诊断")
    parser.add_argument(
        "--proxy",
        default="http://127.0.0.1:7890",
        help="HTTP 代理地址 (默认 http://127.0.0.1:7890)",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=12.0,
        help="下载测速时长秒数 (默认 12)",
    )
    parser.add_argument(
        "--result-dir",
        default=None,
        help="日志目录 (默认 仓库根目录/result)",
    )
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    result_dir = args.result_dir or os.path.join(repo_root, "result")
    logfile = os.path.join(result_dir, datetime.now().strftime("%Y%m%d_%H%M%S.log"))
    log = Logger(logfile)

    proxy_host, proxy_port, proxies = parse_proxy(args.proxy)
    report = Report()

    log("=" * 56)
    log("Telegram Network Diagnostic")
    log(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"代理: {args.proxy}")
    log(f"日志: {logfile}")
    log("=" * 56)

    # ---------- 1. 本地 ----------
    log()
    log(">>> [1/3] 本地网络（不经代理）")
    local_hosts = ["cloudflare.com", "api.telegram.org", "telegram.org"]
    for host in local_hosts:
        s = dns_lookup(host)
        report.local_dns[host] = s
        if s.ok:
            log(f"  [DNS] {host:<22} {s.detail:<16} {s.value:.1f}ms  [{grade(s.value, 30, THRESH['dns_ms'])}]")
        else:
            log(f"  [DNS] {host:<22} 失败: {s.detail}")

    report.local_ping = ping_host("1.1.1.1")
    if report.local_ping.ok:
        log(f"  [PING] 1.1.1.1              avg {report.local_ping.value:.1f}ms  [{grade(report.local_ping.value, 40, THRESH['local_ping_ms'])}]")
    else:
        log(f"  [PING] 1.1.1.1              失败: {report.local_ping.detail}")

    # 直连公共站（应成功）；直连 TG 仅作对照，国内常失败属正常
    report.local_tcp = tcp_connect("cloudflare.com", 443, rounds=4)
    if report.local_tcp.ok:
        log(
            f"  [TCP ] cloudflare.com:443   avg {report.local_tcp.value:.1f}ms  "
            f"jitter {fmt_ms(jitter(report.local_tcp.samples))}  "
            f"[{grade(report.local_tcp.value, 80, THRESH['local_tcp_ms'])}]"
        )
    else:
        log(f"  [TCP ] cloudflare.com:443   失败: {report.local_tcp.detail}")

    tg_direct = tcp_connect("api.telegram.org", 443, rounds=2, timeout=3.0)
    if tg_direct.ok:
        log(f"  [TCP ] api.telegram.org:443 avg {tg_direct.value:.1f}ms  (直连可达)")
    else:
        log("  [TCP ] api.telegram.org:443 直连失败（国内常见，需走代理）")

    # ---------- 2. 代理 ----------
    log()
    log(">>> [2/3] 代理质量")
    report.proxy_alive = proxy_port_check(proxy_host, proxy_port)
    if report.proxy_alive.ok:
        log(
            f"  [PORT] {proxy_host}:{proxy_port}     avg {report.proxy_alive.value:.1f}ms  "
            f"[{grade(report.proxy_alive.value, 10, THRESH['proxy_connect_ms'])}]"
        )
    else:
        log(f"  [PORT] {proxy_host}:{proxy_port}     失败: {report.proxy_alive.detail}")
        log("  代理不可用，后续经代理测试可能全部失败")

    for name, url in [
        ("cloudflare", "https://www.cloudflare.com/cdn-cgi/trace"),
        ("google", "https://www.google.com/generate_204"),
    ]:
        s = https_ttfb(url, proxies, rounds=3)
        report.proxy_https[name] = s
        if s.ok:
            log(
                f"  [HTTPS] via proxy {name:<12} avg {s.value:.1f}ms  "
                f"samples {[round(x,1) if x<9999 else 'FAIL' for x in s.samples]}  "
                f"[{grade(s.value, 400, THRESH['proxy_https_ms'])}]"
            )
        else:
            log(f"  [HTTPS] via proxy {name:<12} 失败: {s.detail}")

    log(f"  [DOWN ] 测速中（约 {args.duration:.0f}s）...")
    report.proxy_download = download_speed(
        "http://speedtest.tele2.net/100MB.zip",
        proxies,
        duration=args.duration,
    )
    if report.proxy_download.ok:
        log(
            f"  [DOWN ] via proxy           {report.proxy_download.value:.2f} MB/s  "
            f"({report.proxy_download.detail})  "
            f"[{grade(report.proxy_download.value, 5.0, THRESH['download_mbs'], higher_better=True)}]"
        )
    else:
        log(f"  [DOWN ] via proxy           失败: {report.proxy_download.detail}")

    # ---------- 3. Telegram ----------
    log()
    log(">>> [3/3] Telegram（经代理）")
    tg_targets = [
        ("telegram.org", "https://telegram.org"),
        ("api.telegram.org", "https://api.telegram.org"),
        ("t.me", "https://t.me"),
    ]
    for name, url in tg_targets:
        s = https_ttfb(url, proxies, rounds=3)
        report.tg_https[name] = s
        if s.ok:
            log(
                f"  [HTTPS] {name:<20} avg {s.value:.1f}ms  "
                f"jitter {fmt_ms(jitter(s.samples))}  "
                f"samples {[round(x,1) if x<9999 else 'FAIL' for x in s.samples]}  "
                f"[{grade(s.value, 800, THRESH['tg_https_ms'])}]"
            )
        else:
            log(f"  [HTTPS] {name:<20} 失败: {s.detail}")

    diagnose(report, log)
    log(f"完整日志: {logfile}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\n已中断", flush=True)
        raise SystemExit(130)
