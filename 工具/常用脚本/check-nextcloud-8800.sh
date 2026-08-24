#!/bin/bash
# 在公网服务器 139.199.192.179 上运行，排查 139.199.192.179:8800 无法访问的原因
#
# 架构（见 方案/相机传输/疑难.md、方案/nextcloud/疑难杂症.md）：
#   用户 → 139.199.192.179:8800 (nginx 反向代理) → ZeroTier 内网 NextCloud
#
# 用法：
#   chmod +x check-nextcloud-8800.sh
#   ./check-nextcloud-8800.sh
#   ./check-nextcloud-8800.sh --fix-hint   # 额外输出常见修复命令

# scp 工具/常用脚本/check-nextcloud-8800.sh root@139.199.192.179:/root/
# 上传脚本后
# chmod +x check-nextcloud-8800.sh
# ./check-nextcloud-8800.sh

# 需要时附带修复命令参考
# ./check-nextcloud-8800.sh --fix-hint
# 保存完整日志
# ./check-nextcloud-8800.sh 2>&1 | tee /tmp/nextcloud-8800-check.log
# set -uo pipefail

PUBLIC_IP="139.199.192.179"
PORT=8800
# 文档中出现过两个内网 NextCloud 地址，均检测
BACKEND_HOSTS=("10.147.47.20" "10.147.47.168")
NGINX_SITE="nextcloud"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

PASS=0
WARN=0
FAIL=0

SHOW_FIX=false
[[ "${1:-}" == "--fix-hint" ]] && SHOW_FIX=true

section() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

ok()   { echo -e "  ${GREEN}[OK]${NC}   $1"; ((PASS++)); }
warn() { echo -e "  ${YELLOW}[WARN]${NC} $1"; ((WARN++)); }
fail() { echo -e "  ${RED}[FAIL]${NC} $1"; ((FAIL++)); }
info() { echo -e "  [INFO] $1"; }

run_cmd() {
    local desc="$1"
    shift
    info "$desc"
    "$@" 2>&1 | sed 's/^/         /'
    echo ""
}

# ── 0. 基本信息 ──────────────────────────────────────────────
section "0. 基本信息"
info "主机名: $(hostname)"
info "时间:   $(date '+%Y-%m-%d %H:%M:%S %Z')"
info "目标:   http://${PUBLIC_IP}:${PORT}"
info "本机 IP: $(hostname -I 2>/dev/null | awk '{print $1}' || echo '未知')"

# ── 1. 本机 8800 端口监听 ────────────────────────────────────
section "1. 本机 ${PORT} 端口是否在监听"

if command -v ss >/dev/null 2>&1; then
    LISTEN_INFO=$(ss -lntp 2>/dev/null | grep ":${PORT} " || true)
elif command -v netstat >/dev/null 2>&1; then
    LISTEN_INFO=$(netstat -lntp 2>/dev/null | grep ":${PORT} " || true)
else
    LISTEN_INFO=""
    warn "未找到 ss/netstat，跳过端口监听检查"
fi

if [[ -n "$LISTEN_INFO" ]]; then
    ok "端口 ${PORT} 正在监听"
    echo "$LISTEN_INFO" | sed 's/^/         /'

    if echo "$LISTEN_INFO" | grep -q nginx; then
        ok "监听进程为 nginx（符合预期）"
    elif echo "$LISTEN_INFO" | grep -q docker; then
        warn "监听进程为 docker，可能未走 nginx 代理"
    else
        warn "监听进程不是 nginx，请确认是否为预期服务"
    fi
else
    fail "端口 ${PORT} 未监听 — 这是无法访问的直接原因"
    info "可能原因: nginx 未启动 / nextcloud 站点未启用 / 配置 listen ${PORT} 缺失"
fi

# ── 2. nginx 服务状态 ────────────────────────────────────────
section "2. nginx 服务状态"

if command -v nginx >/dev/null 2>&1; then
    if systemctl is-active --quiet nginx 2>/dev/null; then
        ok "nginx 服务运行中"
    else
        fail "nginx 服务未运行"
        run_cmd "systemctl status nginx:" systemctl status nginx --no-pager -l || true
    fi

    if sudo nginx -t 2>&1 | grep -q "successful"; then
        ok "nginx 配置语法正确"
    else
        fail "nginx 配置语法有误"
        run_cmd "nginx -t 输出:" sudo nginx -t || true
    fi
else
    fail "未安装 nginx"
fi

# ── 3. nginx 8800 站点配置 ───────────────────────────────────
section "3. nginx ${PORT} 反向代理配置"

SITE_AVAILABLE="/etc/nginx/sites-available/${NGINX_SITE}"
SITE_ENABLED="/etc/nginx/sites-enabled/${NGINX_SITE}"

if [[ -f "$SITE_AVAILABLE" ]]; then
    ok "找到配置文件: $SITE_AVAILABLE"
elif [[ -f "/etc/nginx/conf.d/${NGINX_SITE}.conf" ]]; then
    SITE_AVAILABLE="/etc/nginx/conf.d/${NGINX_SITE}.conf"
    ok "找到配置文件: $SITE_AVAILABLE"
else
    fail "未找到 nextcloud nginx 配置（sites-available/${NGINX_SITE}）"
    info "文档参考: 方案/nextcloud/疑难杂症.md"
fi

if [[ -f "${SITE_AVAILABLE:-}" ]]; then
    if grep -q "listen ${PORT}" "$SITE_AVAILABLE" 2>/dev/null; then
        ok "配置中有 listen ${PORT}"
    else
        fail "配置中缺少 listen ${PORT}"
    fi

    PROXY_PASS=$(grep -E '^\s*proxy_pass' "$SITE_AVAILABLE" 2>/dev/null | head -1 || true)
    if [[ -n "$PROXY_PASS" ]]; then
        ok "proxy_pass: $(echo "$PROXY_PASS" | xargs)"
        # 提取后端地址
        BACKEND_FROM_NGINX=$(echo "$PROXY_PASS" | grep -oP 'http://[^/;]+' | head -1 | sed 's|http://||')
        info "nginx 配置的后端: ${BACKEND_FROM_NGINX:-未知}"
    else
        fail "配置中缺少 proxy_pass"
    fi

    if grep -q 'proxy_set_header Host \$http_host' "$SITE_AVAILABLE" 2>/dev/null; then
        ok "Host 头使用 \$http_host（文档推荐，保留端口号）"
    elif grep -q 'proxy_set_header Host \$host' "$SITE_AVAILABLE" 2>/dev/null; then
        warn "Host 头使用 \$host，可能导致 NextCloud 登录重定向异常（见 方案/相机传输/疑难.md）"
        info "建议改为: proxy_set_header Host \$http_host;"
    else
        warn "未找到 proxy_set_header Host 配置"
    fi

    echo ""
    info "完整配置内容:"
    sed 's/^/         /' "$SITE_AVAILABLE"
fi

if [[ -L "$SITE_ENABLED" ]] || [[ -f "$SITE_ENABLED" ]]; then
    ok "站点已启用: $SITE_ENABLED"
else
    fail "站点未启用（缺少 sites-enabled/${NGINX_SITE} 软链接）"
    info "修复: sudo ln -sf $SITE_AVAILABLE $SITE_ENABLED && sudo nginx -t && sudo systemctl reload nginx"
fi

# ── 4. 本机 HTTP 探测 ────────────────────────────────────────
section "4. 本机 HTTP 探测"

probe_http() {
    local url="$1"
    local label="$2"
    local resp http_code time_total

    if ! command -v curl >/dev/null 2>&1; then
        warn "未安装 curl，跳过 HTTP 探测"
        return
    fi

    resp=$(curl -sS -o /dev/null -w '%{http_code} %{time_total}' \
        --connect-timeout 5 --max-time 10 \
        -H "Host: ${PUBLIC_IP}:${PORT}" \
        "$url" 2>&1) || resp="000 0"

    http_code=$(echo "$resp" | awk '{print $1}')
    time_total=$(echo "$resp" | awk '{print $2}')

    case "$http_code" in
        200|301|302|303|307|308)
            ok "${label}: HTTP ${http_code} (${time_total}s) — $url"
            ;;
        000)
            fail "${label}: 连接失败/超时 — $url"
            ;;
        502|503|504)
            fail "${label}: HTTP ${http_code} — 上游不可达或超时 — $url"
            ;;
        404)
            warn "${label}: HTTP 404 — $url（nginx 可达但路由/重定向可能有问题）"
            ;;
        *)
            warn "${label}: HTTP ${http_code} (${time_total}s) — $url"
            ;;
    esac
}

probe_http "http://127.0.0.1:${PORT}/" "本机回环"
probe_http "http://${PUBLIC_IP}:${PORT}/" "公网 IP 本机"

# 带 verbose 看响应头（仅当上面失败时详细输出）
if command -v curl >/dev/null 2>&1; then
    info "详细响应头 (curl -i http://127.0.0.1:${PORT}/):"
    curl -sS -i --connect-timeout 5 --max-time 10 \
        -H "Host: ${PUBLIC_IP}:${PORT}" \
        "http://127.0.0.1:${PORT}/" 2>&1 | head -20 | sed 's/^/         /'
    echo ""
fi

# ── 5. ZeroTier 网络连通性 ───────────────────────────────────
section "5. ZeroTier 网络（公网服务器 ↔ 内网 NextCloud）"

if command -v zerotier-cli >/dev/null 2>&1; then
    ZT_STATUS=$(zerotier-cli info 2>/dev/null || true)
    if echo "$ZT_STATUS" | grep -q "ONLINE"; then
        ok "ZeroTier 在线"
    else
        fail "ZeroTier 未在线"
        info "输出: $ZT_STATUS"
    fi

    info "ZeroTier 网络列表:"
    zerotier-cli listnetworks 2>/dev/null | sed 's/^/         /' || true

    info "ZeroTier 对等节点 (peers):"
    zerotier-cli listpeers 2>/dev/null | head -15 | sed 's/^/         /' || true
else
    warn "未安装 zerotier-cli，跳过 ZeroTier 检查"
    info "文档: ZeroTier network 772b37df07cbd51f，planet 在 139.199.192.179:3000"
fi

echo ""
for host in "${BACKEND_HOSTS[@]}"; do
    info "检测内网后端 ${host}:${PORT} ..."

    # ping
    if ping -c 2 -W 2 "$host" >/dev/null 2>&1; then
        ok "ping ${host} 可达"
    else
        fail "ping ${host} 不可达 — ZeroTier 隧道可能断开"
    fi

    # TCP
    if (echo >/dev/tcp/"$host"/"$PORT") 2>/dev/null; then
        ok "TCP ${host}:${PORT} 端口开放"
    elif command -v nc >/dev/null 2>&1 && nc -z -w3 "$host" "$PORT" 2>/dev/null; then
        ok "TCP ${host}:${PORT} 端口开放"
    else
        fail "TCP ${host}:${PORT} 不可连接 — 内网 NextCloud 可能未运行"
    fi

    # HTTP
    if command -v curl >/dev/null 2>&1; then
        backend_code=$(curl -sS -o /dev/null -w '%{http_code}' \
            --connect-timeout 5 --max-time 10 \
            "http://${host}:${PORT}/" 2>/dev/null || echo "000")
        if [[ "$backend_code" =~ ^(200|301|302|303|307|308)$ ]]; then
            ok "HTTP http://${host}:${PORT}/ → ${backend_code}"
        elif [[ "$backend_code" == "000" ]]; then
            fail "HTTP http://${host}:${PORT}/ 连接失败"
        else
            warn "HTTP http://${host}:${PORT}/ → ${backend_code}"
        fi
    fi
    echo ""
done

# ── 6. 防火墙 / 安全组 ───────────────────────────────────────
section "6. 本机防火墙"

if command -v ufw >/dev/null 2>&1; then
    UFW_STATUS=$(ufw status 2>/dev/null || true)
    if echo "$UFW_STATUS" | grep -qi "inactive"; then
        ok "ufw 未启用"
    else
        info "ufw 已启用，检查 ${PORT} 规则:"
        if echo "$UFW_STATUS" | grep -q "${PORT}"; then
            echo "$UFW_STATUS" | grep "${PORT}" | sed 's/^/         /'
        else
            warn "ufw 中未找到 ${PORT} 放行规则"
        fi
    fi
elif command -v firewall-cmd >/dev/null 2>&1; then
    if firewall-cmd --list-ports 2>/dev/null | grep -q "${PORT}"; then
        ok "firewalld 已放行 ${PORT}"
    else
        warn "firewalld 可能未放行 ${PORT}/tcp"
    fi
else
    info "未检测到 ufw/firewalld"
fi

if command -v iptables >/dev/null 2>&1; then
    DROP_RULES=$(iptables -L INPUT -n 2>/dev/null | grep -i drop | head -3 || true)
    if [[ -n "$DROP_RULES" ]]; then
        warn "iptables 存在 DROP 规则，请确认 ${PORT} 未被拦截"
        echo "$DROP_RULES" | sed 's/^/         /'
    fi
fi

info "腾讯云安全组: 文档记录 ${PORT}/tcp 已放行（见 资源/腾讯云开放端口.csv）"
info "若外网仍无法访问但本机 curl 正常，请到腾讯云控制台确认安全组/Inbound 规则"

# ── 7. nginx 错误日志 ────────────────────────────────────────
section "7. nginx 最近错误日志"

LOG_PATHS=(
    "/var/log/nginx/error.log"
    "/var/log/nginx/nextcloud.error.log"
)

found_log=false
for log in "${LOG_PATHS[@]}"; do
    if [[ -f "$log" ]]; then
        found_log=true
        info "最近 20 行: $log"
        tail -20 "$log" 2>/dev/null | sed 's/^/         /'
        echo ""

        ERR_COUNT=$(grep -ci "connect() failed\|upstream timed out\|no live upstreams" "$log" 2>/dev/null || echo 0)
        if [[ "$ERR_COUNT" -gt 0 ]]; then
            fail "日志中有 ${ERR_COUNT} 条 upstream 连接失败/超时（内网 NextCloud 不可达）"
        fi
    fi
done

if [[ "$found_log" == false ]]; then
    warn "未找到 nginx 错误日志"
fi

# ── 8. Docker（若 NextCloud 跑在本机） ───────────────────────
section "8. Docker 容器（本机是否直接运行 NextCloud）"

if command -v docker >/dev/null 2>&1; then
    NC_CONTAINERS=$(docker ps --format '{{.Names}}\t{{.Ports}}' 2>/dev/null | grep -iE 'nextcloud|8800' || true)
    if [[ -n "$NC_CONTAINERS" ]]; then
        info "本机 NextCloud 相关容器:"
        echo "$NC_CONTAINERS" | sed 's/^/         /'
    else
        info "本机无 NextCloud 容器（符合架构：NextCloud 在内网 ZeroTier 服务器上）"
    fi
else
    info "未安装 docker"
fi

# ── 9. 诊断总结 ──────────────────────────────────────────────
section "9. 诊断总结"

echo -e "  通过: ${GREEN}${PASS}${NC}  警告: ${YELLOW}${WARN}${NC}  失败: ${RED}${FAIL}${NC}"
echo ""

if [[ $FAIL -eq 0 && $WARN -eq 0 ]]; then
    echo -e "  ${GREEN}本机服务看起来正常。若外网仍无法访问，请检查:${NC}"
    echo "    1. 腾讯云安全组 Inbound ${PORT}/tcp"
    echo "    2. 客户端网络/DNS 是否解析到 ${PUBLIC_IP}"
    echo "    3. NextCloud trusted_domains 是否包含 ${PUBLIC_IP}:${PORT}"
elif [[ $FAIL -gt 0 ]]; then
    echo -e "  ${RED}发现 ${FAIL} 个问题，按优先级排查:${NC}"
    echo ""

    # 根据常见失败模式给出建议
    cat <<'DIAG'
  ┌─────────────────────────────────────────────────────────────────┐
  │ 问题场景                          │ 处理方向                      │
  ├─────────────────────────────────────────────────────────────────┤
  │ 8800 未监听 / nginx 未运行        │ systemctl start nginx         │
  │ sites-enabled 缺少软链接          │ ln -sf sites-available/...    │
  │ 内网后端 ping/TCP 失败            │ 检查 ZeroTier: zerotier-cli   │
  │                                   │   info / listpeers            │
  │ HTTP 502/504                      │ 内网 NextCloud 未启动或 IP 错 │
  │                                   │ 确认 proxy_pass 指向正确后端  │
  │ 能访问但登录重定向异常            │ Host 改为 \$http_host         │
  │ 不被信任的域名                    │ 内网 NextCloud config.php     │
  │                                   │   trusted_domains 加公网 IP   │
  │ 本机正常外网不通                  │ 腾讯云安全组放行 8800/tcp     │
  └─────────────────────────────────────────────────────────────────┘
DIAG
fi

if [[ "$SHOW_FIX" == true ]]; then
    section "常见修复命令（来自文档）"
    cat <<'FIX'
  # 重新部署 nginx 反向代理（后端改为实际 ZeroTier IP）
  sudo tee /etc/nginx/sites-available/nextcloud <<'EOF'
  server {
      listen 8800;
      server_name nextcloud;

      location / {
          proxy_pass http://10.147.47.20:8800/;
          proxy_set_header Host $http_host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
          proxy_set_header X-Forwarded-Host $http_host;
          proxy_buffering off;
          client_max_body_size 10G;
      }
  }
  EOF
  sudo ln -sf /etc/nginx/sites-available/nextcloud /etc/nginx/sites-enabled/
  sudo nginx -t && sudo systemctl reload nginx

  # 内网 NextCloud 添加信任域名（在内网服务器 docker 内执行）
  # occ config:system:set trusted_domains 3 --value='139.199.192.179:8800'
  # occ config:system:set trusted_domains 4 --value='139.199.192.179'
  # occ config:system:set overwrite.cli.url --value='http://139.199.192.179:8800'

  # ZeroTier 重连
  sudo systemctl restart zerotier-one
  zerotier-cli listpeers
FIX
    echo ""
fi

echo ""
info "脚本执行完毕。可将完整输出保存: ./check-nextcloud-8800.sh 2>&1 | tee /tmp/nextcloud-8800-check.log"
