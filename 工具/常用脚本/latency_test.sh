#!/bin/bash

# 创建临时文件存储结果
TEMP_FILE=$(mktemp)

# 输出标题
echo "测试各个服务器的网络延迟..."
echo "================================="

# 定义服务器列表
# 格式: ["IP"]="服务器名称|公网或内网(public/private)"
declare -A SERVERS
SERVERS["121.43.123.105"]="Host 121.43.123.105|public"
SERVERS["83.229.123.43"]="野草云2h2g|public"
SERVERS["123.58.219.234"]="ucloud2h2g1|public"
SERVERS["43.139.236.50"]="腾讯云|public"
SERVERS["100.70.106.2"]="belink-8h32g|public"
SERVERS["10.146.84.20"]="beelink-zerotier|public"
SERVERS["10.146.84.168"]="中柏zerotier|public"

# 测试延迟函数
check_latency() {
    local host=$1
    local type=$2

    if [ "$type" = "public" ]; then
        # 公网服务器用 TCP 22 探测
        start=$(date +%s%3N)
        nc -z -w3 $host 22 >/dev/null 2>&1
        end=$(date +%s%3N)
        if [ $? -eq 0 ]; then
            echo $((end - start))  # 毫秒
        else
            echo "9999.999"
        fi
    else
        # 内网/局域网/zerotier用 ping 测延迟
        ping_result=$(ping -c 2 -W 1 "$host" 2>/dev/null)
        avg=$(echo "$ping_result" | tail -1 | awk -F'/' '{print $5}')
        if [ -n "$avg" ]; then
            echo "$avg"
        else
            echo "9999.999"
        fi
    fi
}

# 测试每个服务器
for hostname in "${!SERVERS[@]}"; do
    server_info="${SERVERS[$hostname]}"
    server_name="${server_info%%|*}"
    server_type="${server_info##*|}"

    avg_latency=$(check_latency "$hostname" "$server_type")

    # 记录结果到临时文件
    echo "$avg_latency $hostname" >> "$TEMP_FILE"

    # 输出结果
    if [ "$avg_latency" = "9999.999" ]; then
        printf "%-20s (%-15s): 超时\n" "$server_name" "$hostname"
    else
        printf "%-20s (%-15s): %s ms\n" "$server_name" "$hostname" "$avg_latency"
    fi
done

echo ""
echo "延迟前三的服务器:"
echo "=================="
# 按延迟排序并显示前三
sort -n "$TEMP_FILE" | head -3 | nl | while read number line; do
    latency=$(echo "$line" | awk '{print $1}')
    hostname=$(echo "$line" | awk '{print $2}')  # 直接取第二列即可
    
    # 查找服务器名称
    server_name="${SERVERS[$hostname]%%|*}"
    
    if [ "$latency" = "9999.999" ]; then
        printf "%d. %-20s (%-15s): 超时\n" "$number" "$server_name" "$hostname"
    else
        printf "%d. %-20s (%-15s): %s ms\n" "$number" "$server_name" "$hostname" "$latency"
    fi
done
