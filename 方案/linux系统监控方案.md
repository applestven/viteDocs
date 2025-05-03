# Glances 使用指南（Ubuntu 系统）

本文介绍 Ubuntu 系统下 **Glances** 的安装、配置与高级使用技巧，帮助你快速掌握这款强大的系统监控工具。

---

## 目录
- [Glances 使用指南（Ubuntu 系统）](#glances-使用指南ubuntu-系统)
  - [目录](#目录)
  - [Glances 简介](#glances-简介)
  - [安装 Glances](#安装-glances)
    - [方法 1：通过 APT 安装（推荐）](#方法-1通过-apt-安装推荐)
  - [基础使用](#基础使用)
  - [Web 服务器模式](#web-服务器模式)
  - [远程监控](#远程监控)
  - [数据导出与集成](#数据导出与集成)
  - [常见问题](#常见问题)

---

## Glances 简介
Glances 是一款跨平台的 **实时系统监控工具**，支持以下功能：
- 监控 CPU、内存、磁盘、网络、进程等核心指标
- 终端交互式界面 + Web 仪表盘
- 数据导出（CSV、InfluxDB、Prometheus 等）
- 远程服务器监控

---

## 安装 Glances

### 方法 1：通过 APT 安装（推荐）
```bash
sudo apt update
sudo apt install glances
```
## 基础使用 
1. 启动 Glances
```bahs
glances

```
2. 界面说明 
   
**顶部栏：系统基本信息（主机名、运行时间、系统版本）**

**CPU 使用率：总使用率 + 每个核心的独立数据**

**内存/交换分区：实时使用情况**

**磁盘 I/O：读写速度及分区占用**

**网络：上传/下载速度**

**进程列表：按 CPU 或内存排序的进程信息**

## Web 服务器模式
1.  启动 Web 服务
``` bash
glances -w  # 默认端口 61208
```
2. 浏览器访问 
``` bash
http://服务器IP:61208
```
3. 自定义端口 
``` bash
glances -w -p 8080  # 指定端口 8080
```

## 远程监控 

1. 服务端配置
``` bash
glances -s  # 启动服务端
```
2. 客户端连接 
```bash

glances -c @服务器IP  # 从本地监控远程服务器
```

3. 设置密码保护
``` bash
glances -s --password  # 启动服务端并要求客户端输入密码
```
## 数据导出与集成 
1. 导出到 CSV
```bash
glances --export csv --export-csv-file /path/to/output.csv
```
2. 集成 InfluxDB
``` bash
glances --export influxdb --influxdb-host 127.0.0.1 --influxdb-port 8086
```
3. 对接 Prometheus
``` bash
glances --export prometheus
# 访问指标端点：http://服务器IP:61208/metrics

```

## 常见问题 
1. Q1: Web 界面无法访问？
- 检查防火墙是否开放端口：

``` bash
sudo ufw allow 61208
```
- 确保 Glances 以 Web 模式启动：

``` bash
glances -w
```
2. Q2: 缺少某些监控项？
- 安装额外依赖：

```bash
sudo apt install sensors  # 温度监控支持
sudo apt install smartmontools  # 磁盘健康监控
```
3. Q3: 如何更新 Glances？
```bash
sudo pip3 install --upgrade glances
```