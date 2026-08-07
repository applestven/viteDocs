#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超实惠加速 / UnrivaledSpeed IPC 桥接。

协议: 换行分隔 JSON（NDJSON），与原版 FlClash 二进制 length-frame 不同。
在 GUI 与内核之间插入桥接，注入 getProxies / changeProxy / asyncTestDelay。
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import threading
import time
import uuid
import urllib.parse
from concurrent.futures import Future
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Optional

# 常驻桥对外控制口（Clash 兼容子集），测速脚本复用它，避免每次拆核心
AGENT_HOST = "127.0.0.1"
AGENT_PORT = 19692
AGENT_BASE = f"http://{AGENT_HOST}:{AGENT_PORT}"


def read_line(sock: socket.socket) -> bytes:
    buf = bytearray()
    while True:
        ch = sock.recv(1)
        if not ch:
            raise ConnectionError("socket closed")
        if ch == b"\n":
            break
        buf.extend(ch)
        if len(buf) > 64 * 1024 * 1024:
            raise ValueError("line too large")
    return bytes(buf)


def write_line(sock: socket.socket, data: bytes) -> None:
    if not data.endswith(b"\n"):
        data += b"\n"
    sock.sendall(data)


def find_gui_control_port() -> Optional[int]:
    try:
        task = subprocess.check_output(
            ["tasklist", "/FI", "IMAGENAME eq chaoshihui.exe", "/FO", "CSV", "/NH"],
            encoding="utf-8",
            errors="ignore",
        )
    except Exception:
        return None
    pids = set()
    for line in task.splitlines():
        parts = [x.strip().strip('"') for x in line.split(",")]
        if len(parts) >= 2 and parts[1].isdigit():
            pids.add(parts[1])
    if not pids:
        return None
    try:
        out = subprocess.check_output(["netstat", "-ano"], encoding="utf-8", errors="ignore")
    except Exception:
        return None
    candidates = []
    for line in out.splitlines():
        if "LISTENING" not in line.upper():
            continue
        parts = line.split()
        if len(parts) < 5 or parts[-1] not in pids:
            continue
        local = parts[1]
        if "127.0.0.1:" not in local:
            continue
        try:
            port = int(local.rsplit(":", 1)[-1])
        except ValueError:
            continue
        if port in (7890, 7891, 7892, 7897, 7898, 7899, 9090, 53):
            continue
        candidates.append(port)
    return max(candidates) if candidates else None


def find_core_control_port() -> Optional[int]:
    try:
        out = subprocess.check_output(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "(Get-CimInstance Win32_Process -Filter \"Name='chaoshihuiCore.exe'\").CommandLine",
            ],
            encoding="utf-8",
            errors="ignore",
        ).strip()
    except Exception:
        out = ""
    if out:
        for token in reversed(out.replace('"', " ").split()):
            if token.isdigit() and 1024 <= int(token) <= 65535:
                return int(token)
    return find_gui_control_port()


def kill_core() -> None:
    subprocess.run(
        ["taskkill", "/F", "/IM", "chaoshihuiCore.exe"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    time.sleep(0.35)


class FlClashBridge:
    def __init__(self):
        self.gui_sock: Optional[socket.socket] = None
        self.core_sock: Optional[socket.socket] = None
        self.core_proc: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()
        self._pending: dict[str, Future] = {}
        self._stop = threading.Event()
        self._threads: list[threading.Thread] = []
        self.gui_port: Optional[int] = None
        self.install: Optional[Path] = None
        self.alive = False
        self._seen_methods: set[str] = set()

    def start(self, install: Path, gui_port: Optional[int] = None, log=print) -> None:
        install = Path(install)
        self.install = install
        core_exe = install / "chaoshihuiCore.exe"
        if not core_exe.is_file():
            raise FileNotFoundError(core_exe)

        self.gui_port = gui_port or find_core_control_port()
        if not self.gui_port:
            raise RuntimeError("无法定位 GUI 控制端口（请确认超实惠加速已打开）")

        log(f"  IPC 控制口: GUI 监听 {self.gui_port}（NDJSON 协议）")
        log("  接入 IPC 桥接（短暂重拉内核）...")

        for _ in range(4):
            kill_core()
            time.sleep(0.2)

        deadline = time.time() + 8
        last_err = None
        while time.time() < deadline:
            kill_core()
            try:
                self.gui_sock = socket.create_connection(("127.0.0.1", self.gui_port), timeout=1.5)
                break
            except OSError as e:
                last_err = e
                time.sleep(0.2)
        if not self.gui_sock:
            raise RuntimeError(f"无法连接 GUI 控制口 {self.gui_port}: {last_err}")

        lst = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lst.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lst.bind(("127.0.0.1", 0))
        lst.listen(1)
        local_port = lst.getsockname()[1]

        self.core_proc = subprocess.Popen(
            [str(core_exe), str(local_port)],
            cwd=str(install),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        lst.settimeout(10)
        self.core_sock, _ = lst.accept()
        lst.close()

        self._stop.clear()
        t1 = threading.Thread(target=self._relay_gui_to_core, name="csh-g2c", daemon=True)
        t2 = threading.Thread(target=self._relay_core_to_gui, name="csh-c2g", daemon=True)
        t1.start()
        t2.start()
        self._threads = [t1, t2]
        self.alive = True
        log(f"  IPC 桥接就绪（本地内核口 {local_port}）")

        # GUI 重连后不会重发 init/setup；由脚本自行初始化。
        # UnrivaledSpeed 内核能解密 home-dir/config.yaml。
        home = Path(os.environ.get("APPDATA", "")) / "chaoshihui" / "chaoshihui"
        if not (home / "config.yaml").is_file():
            raise RuntimeError(f"找不到配置目录: {home}")
        selected = {}
        try:
            import sqlite3

            db = sqlite3.connect(str(home / "database.sqlite"))
            row = db.execute("select selected_map from profiles").fetchone()
            if row and row[0]:
                selected = json.loads(row[0])
        except Exception:
            selected = {}

        init_payload = json.dumps({"home-dir": str(home), "version": 1}, ensure_ascii=False)
        ok = self.call("initClash", init_payload, timeout=10)
        log(f"  initClash -> {ok!r}")
        setup_payload = json.dumps(
            {
                "selected-map": selected,
                "test-url": "http://www.gstatic.com/generate_204",
            },
            ensure_ascii=False,
        )
        setup_res = self.call("setupConfig", setup_payload, timeout=30)
        log(f"  setupConfig -> {setup_res!r}")
        try:
            self.call("startListener", None, timeout=10)
            log("  startListener ok")
        except Exception as e:
            log(f"  startListener: {e}")

        inited = self.call("getIsInit", None, timeout=5)
        if not inited:
            raise RuntimeError("init 后 getIsInit 仍为 false")
        log(f"  内核就绪 selected-map keys={list(selected.keys())}")

    def _relay_gui_to_core(self) -> None:
        """GUI 断开时保留内核连接，脚本仍可 changeProxy。"""
        assert self.gui_sock and self.core_sock
        try:
            while not self._stop.is_set():
                line = read_line(self.gui_sock)
                try:
                    m = json.loads(line.decode("utf-8")).get("method")
                    if m:
                        self._seen_methods.add(str(m))
                except Exception:
                    pass
                with self._lock:
                    write_line(self.core_sock, line)
        except Exception:
            pass

    def _relay_core_to_gui(self) -> None:
        assert self.gui_sock and self.core_sock
        try:
            while not self._stop.is_set():
                line = read_line(self.core_sock)
                try:
                    msg = json.loads(line.decode("utf-8"))
                except Exception:
                    try:
                        with self._lock:
                            if self.gui_sock:
                                write_line(self.gui_sock, line)
                    except Exception:
                        pass
                    continue

                rid = msg.get("id")
                method = msg.get("method")
                if method == "message":
                    try:
                        with self._lock:
                            if self.gui_sock:
                                write_line(self.gui_sock, line)
                    except Exception:
                        pass
                    continue

                fut = None
                if rid:
                    with self._lock:
                        fut = self._pending.get(rid)
                if fut is not None:
                    if not fut.done():
                        fut.set_result(msg)
                    with self._lock:
                        self._pending.pop(rid, None)
                    continue

                try:
                    with self._lock:
                        if self.gui_sock:
                            write_line(self.gui_sock, line)
                except Exception:
                    pass
        except Exception:
            self.alive = False
            self._fail_all("Core 断开")

    def _fail_all(self, reason: str) -> None:
        with self._lock:
            for fut in list(self._pending.values()):
                if not fut.done():
                    fut.set_exception(RuntimeError(reason))
            self._pending.clear()

    def call(self, method: str, data: Any = None, timeout: float = 15.0) -> Any:
        if not self.alive or not self.core_sock:
            raise RuntimeError("IPC 未就绪")
        aid = str(uuid.uuid4())
        action = {"id": aid, "method": method, "data": data}
        payload = json.dumps(action, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        fut: Future = Future()
        with self._lock:
            self._pending[aid] = fut
            write_line(self.core_sock, payload)
        try:
            result = fut.result(timeout=timeout)
        except Exception:
            with self._lock:
                self._pending.pop(aid, None)
            raise
        if result.get("code", 0) != 0:
            raise RuntimeError(f"{method} failed: {result.get('data')!r}")
        return result.get("data")

    def get_proxies(self) -> dict:
        data = self.call("getProxies", None, timeout=25)
        if isinstance(data, str):
            data = json.loads(data)
        return data or {}

    def change_proxy(self, group: str, node: str) -> None:
        payload = json.dumps({"group-name": group, "proxy-name": node}, ensure_ascii=False)
        err = self.call("changeProxy", payload, timeout=15)
        if isinstance(err, str) and err.strip():
            raise RuntimeError(err)

    def close_connections(self) -> None:
        try:
            self.call("closeConnections", None, timeout=8)
        except Exception:
            pass

    def test_delay(self, node: str, url: str, timeout_ms: int = 4000) -> Optional[int]:
        # UnrivaledSpeed 的 asyncTestDelay 会弄崩内核；IPC 模式改用切换式软预筛。
        return None

    def stop(self, respawn_for_gui: bool = True, preferred_node: Optional[str] = None) -> None:
        self._stop.set()
        self.alive = False
        gui_port = self.gui_port
        install = self.install
        for s in (self.gui_sock, self.core_sock):
            try:
                if s:
                    s.close()
            except Exception:
                pass
        self.gui_sock = None
        self.core_sock = None
        if self.core_proc and self.core_proc.poll() is None:
            try:
                self.core_proc.terminate()
            except Exception:
                pass
            try:
                self.core_proc.wait(timeout=2)
            except Exception:
                pass
        self.core_proc = None
        time.sleep(0.25)
        # GUI 不会对重连内核重发 init；拉起后台 handback 桥接并自助初始化。
        if respawn_for_gui and gui_port and install:
            spawn_handback(install, gui_port, preferred_node)


def spawn_handback(
    install: Path,
    gui_port: int,
    preferred_node: Optional[str] = None,
) -> None:
    script = Path(__file__).resolve()
    cmd = [
        sys.executable,
        str(script),
        "--handback",
        str(install),
        str(gui_port),
    ]
    # 节点名含 emoji/特殊字符，走环境变量避免 Windows 命令行编码丢失
    env = os.environ.copy()
    if preferred_node:
        env["CSH_HANDBACK_NODE"] = preferred_node
    else:
        env.pop("CSH_HANDBACK_NODE", None)
    kwargs: dict[str, Any] = {
        "cwd": str(script.parent),
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "stdin": subprocess.DEVNULL,
        "env": env,
    }
    if sys.platform == "win32":
        kwargs["creationflags"] = (
            subprocess.DETACHED_PROCESS
            | subprocess.CREATE_NEW_PROCESS_GROUP
            | getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
        kwargs["close_fds"] = True
    subprocess.Popen(cmd, **kwargs)
    time.sleep(1.2)


def _agent_http_ok(base: str = AGENT_BASE, timeout: float = 1.0) -> bool:
    try:
        import urllib.request

        with urllib.request.urlopen(base.rstrip("/") + "/version", timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
        if not isinstance(data, dict):
            return False
        with urllib.request.urlopen(base.rstrip("/") + "/proxies", timeout=max(timeout, 3.0)) as r:
            body = json.loads(r.read().decode("utf-8", "replace"))
        proxies = (body or {}).get("proxies") or {}
        return bool(proxies)
    except Exception:
        return False


def ensure_agent(install: Path, log=print, preferred_node: Optional[str] = None) -> str:
    """确保常驻桥 + Clash 兼容控制口可用；已存在则不拆核心。"""
    if _agent_http_ok():
        log(f"  复用常驻控制桥 {AGENT_BASE}（不拆核心）")
        return AGENT_BASE

    gui_port = find_gui_control_port()
    if not gui_port:
        raise RuntimeError("找不到 GUI 控制口（请确认超实惠加速主界面已打开）")

    log(f"  首次接入常驻桥：短暂重拉内核一次，之后测速不再断开")
    log(f"  GUI 控制口 {gui_port} → 控制面 {AGENT_BASE}")
    spawn_handback(install, gui_port, preferred_node)

    deadline = time.time() + 25
    while time.time() < deadline:
        if _agent_http_ok():
            log(f"  常驻桥就绪 {AGENT_BASE}")
            return AGENT_BASE
        time.sleep(0.5)
    raise RuntimeError(f"常驻桥未在 25s 内就绪（{AGENT_BASE}）")


def start_agent_server(controller: "FlClashController", host: str = AGENT_HOST, port: int = AGENT_PORT):
    """在 handback 进程内提供 Clash 兼容 HTTP（供测速脚本复用）。"""

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            return

        def _send(self, code: int, obj: Any = None, empty: bool = False):
            if empty or obj is None:
                body = b""
            else:
                body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if body:
                self.wfile.write(body)

        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path
            try:
                if path == "/version":
                    return self._send(200, controller.version())
                if path == "/configs":
                    return self._send(200, controller.configs())
                if path == "/proxies":
                    return self._send(200, {"proxies": controller.proxies()})
                if path.startswith("/proxies/") and path.endswith("/delay"):
                    # asyncTestDelay 会崩内核；显式不支持（脚本走软预筛）
                    return self._send(501, {"message": "delay unsupported over IPC agent"})
                if path.startswith("/proxies/"):
                    name = urllib.parse.unquote(path[len("/proxies/") :])
                    px = controller.proxies()
                    if name in px:
                        return self._send(200, px[name])
                    return self._send(404, {"message": "not found"})
                return self._send(404, {"message": "not found"})
            except Exception as e:
                return self._send(500, {"message": str(e)})

        def do_PUT(self):
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length else b"{}"
            try:
                data = json.loads(raw.decode("utf-8") or "{}")
            except Exception:
                return self._send(400, {"message": "bad json"})
            try:
                if path.startswith("/proxies/"):
                    group = urllib.parse.unquote(path[len("/proxies/") :])
                    node = data.get("name") or ""
                    if not node:
                        return self._send(400, {"message": "missing name"})
                    controller.switch(group, node)
                    return self._send(204, empty=True)
                return self._send(404, {"message": "not found"})
            except Exception as e:
                return self._send(500, {"message": str(e)})

        def do_DELETE(self):
            parsed = urllib.parse.urlparse(self.path)
            try:
                if parsed.path == "/connections":
                    controller.close_connections()
                    return self._send(204, empty=True)
                return self._send(404, {"message": "not found"})
            except Exception as e:
                return self._send(500, {"message": str(e)})

    srv = ThreadingHTTPServer((host, port), Handler)
    t = threading.Thread(target=srv.serve_forever, name="csh-agent-http", daemon=True)
    t.start()
    return srv


def handback_loop(install: Path, gui_port: int, preferred_node: Optional[str] = None) -> None:
    """后台维持已初始化内核 + Agent HTTP，直到 GUI 或内核退出。"""
    kill_core()
    time.sleep(0.3)
    bridge = FlClashBridge()

    def _silent(msg: str = "") -> None:
        return None

    bridge.start(install, gui_port=gui_port, log=_silent)
    controller = FlClashController(bridge)
    if preferred_node:
        try:
            bridge.change_proxy("GLOBAL", preferred_node)
            bridge.close_connections()
        except Exception:
            pass
    try:
        start_agent_server(controller)
    except OSError:
        # 端口被旧 agent 占用时再试一次
        time.sleep(0.5)
        start_agent_server(controller)
    try:
        while bridge.core_proc and bridge.core_proc.poll() is None and bridge.alive:
            time.sleep(2)
    finally:
        bridge.stop(respawn_for_gui=False)


class FlClashController:
    """兼容 telegramNodePick.ClashAPI 常用接口。"""

    def __init__(self, bridge: FlClashBridge):
        self.bridge = bridge

    def version(self) -> dict:
        return {"premium": True, "version": "unrivaled-ipc-ndjson"}

    def configs(self) -> dict:
        return {"mode": "rule"}

    def proxies(self) -> dict:
        data = self.bridge.get_proxies()
        raw_proxies = data.get("proxies") if isinstance(data, dict) else None
        if not isinstance(raw_proxies, dict):
            raw_proxies = data if isinstance(data, dict) else {}
        out = {}
        type_map = {
            0: "Direct",
            1: "Reject",
            8: "Selector",
            9: "URLTest",
            10: "Fallback",
            11: "LoadBalance",
        }
        for name, info in raw_proxies.items():
            if not isinstance(info, dict):
                continue
            ptype = info.get("type") or info.get("Type") or ""
            if isinstance(ptype, int):
                ptype = type_map.get(ptype, str(ptype))
            out[name] = {
                "name": name,
                "type": str(ptype),
                "now": info.get("now") or info.get("Now") or "",
                "all": info.get("all") or info.get("All") or [],
            }
        return out

    def switch(self, group: str, node: str) -> None:
        self.bridge.change_proxy(group, node)

    def close_connections(self) -> None:
        self.bridge.close_connections()

    def delay(self, node: str, url: str, timeout_ms: int = 5000) -> Optional[int]:
        return self.bridge.test_delay(node, url, timeout_ms)


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "--handback":
        _install = Path(sys.argv[2])
        _port = int(sys.argv[3])
        _node = sys.argv[4] if len(sys.argv) > 4 else os.environ.get("CSH_HANDBACK_NODE")
        handback_loop(_install, _port, _node)
        raise SystemExit(0)
    print("Usage: python flclash_ipc.py --handback <install_dir> <gui_port> [node]")
    raise SystemExit(2)
