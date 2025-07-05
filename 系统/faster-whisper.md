## ubuntu 系统安装python可能出现冲突 问题
[ubuntu-python冲突](./ubuntu-python冲突.md)

## 安装必需依赖
sudo apt update && sudo apt install -y python3-pip ffmpeg

## 安装 faster-whisper
pip install faster-whisper
pip3 install faster-whisper

## 安装 CUDA 支持（如果有 NVIDIA GPU）
pip install ctranslate2 --extra-index-url https://pypi.nvidia.com


## 提供命令行脚本

./transcribe.py /home/apple/temp/1.m4a --model small 

``` python
#!/usr/bin/env python3
import argparse
import os
import tempfile
import subprocess
import time
import psutil
from faster_whisper import WhisperModel

class HardwareOptimizer:
    @staticmethod
    def auto_detect(debug=False):
        """自动检测硬件并返回最佳配置"""
        # 获取系统信息
        cpu_count = os.cpu_count() or 4
        mem_total = psutil.virtual_memory().total / (1024**3)  # GB
        cpu_model = "unknown"
        
        try:
            with open('/proc/cpuinfo') as f:
                for line in f:
                    if line.startswith('model name'):
                        cpu_model = line.split(':')[1].strip()
                        break
        except:
            pass

        # 配置模板
        base_config = {
            "max_threads": min(4, cpu_count),  # 默认保守配置
            "chunk_size": 300,
            "vad_threshold": 0.5,
            "beam_size": 3,
            "model": "base-int8",
            "compute_type": "int8",
            "num_workers": 1,
            "cpu_model": cpu_model,
            "mem_total": mem_total
        }

        # 已知硬件配置覆盖规则
        if "N100" in cpu_model:
            """ Intel N100 低功耗CPU配置 """
            if debug: print("[DEBUG] 检测到N100低功耗CPU")
            config = {
                "max_threads": 4,
                "chunk_size": 300,
                "model": "base-int8",
                "compute_type": "int8",
                "num_workers": 1
            }
        elif "5800H" in cpu_model or "Ryzen 7" in cpu_model:
            """ AMD 5800H 高性能配置 """
            if debug: print("[DEBUG] 检测到AMD 5800H高性能CPU")
            config = {
                "max_threads": min(16, cpu_count),
                "chunk_size": 600,
                "beam_size": 5,
                "model": "medium",
                "compute_type": "int8_float32",
                "num_workers": 4
            }
        elif mem_total > 16:
            """ 大内存通用配置 """
            if debug: print("[DEBUG] 检测到大内存系统")
            config = {
                "max_threads": min(8, cpu_count),
                "chunk_size": 450,
                "model": "medium",
                "compute_type": "int8_float16",
                "num_workers": 2
            }
        else:
            """ 默认保守配置 """
            if debug: print("[DEBUG] 使用默认保守配置")
            config = {}

        # 合并配置（用户指定参数优先）
        return {**base_config, **config}

def get_duration(file_path, debug=False):
    try:
        cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {file_path}"
        duration = float(subprocess.check_output(cmd, shell=True).decode().strip())
        if debug: print(f"[DEBUG] 文件时长: {duration}s")
        return duration
    except:
        if debug: print("[DEBUG] 无法获取时长，使用默认值0")
        return 0

def split_audio(input_path, chunk_size, debug=False):
    """按秒数分割音频，返回分段文件路径列表"""
    duration = get_duration(input_path, debug)
    segment_paths = []
    temp_dir = tempfile.mkdtemp()

    for i in range(0, int(duration), chunk_size):
        start = i
        output_path = os.path.join(temp_dir, f"chunk_{i}.wav")
        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            "-ss", str(start),
            "-t", str(chunk_size),
            "-i", input_path,
            "-ac", "1",
            "-ar", "16000",
            output_path
        ]
        subprocess.run(cmd, check=True)
        segment_paths.append((output_path, start))

    if debug: print(f"[DEBUG] 分割生成 {len(segment_paths)} 段音频")
    return segment_paths

def main():
    parser = argparse.ArgumentParser(description='智能语音转录工具')
    parser.add_argument('input_path', help='输入音频路径')
    parser.add_argument('--model', 
                       help='强制指定模型(覆盖自动配置)',
                       choices=["tiny", "base", "small", "medium", "large", "large-v3"])
    parser.add_argument('--chunk', type=int, help='分段时长(秒)')
    parser.add_argument('--threads', type=int, help='强制指定线程数')
    parser.add_argument('--debug', action='store_true', help='启用调试信息')
    args = parser.parse_args()

    # 自动检测硬件配置
    config = HardwareOptimizer.auto_detect(args.debug)
    
    # 用户参数覆盖
    if args.model: config["model"] = args.model
    if args.chunk: config["chunk_size"] = args.chunk
    if args.threads: config["max_threads"] = args.threads

    # 环境设置
    os.environ["OMP_NUM_THREADS"] = str(config["max_threads"])
    if args.debug:
        print(f"[DEBUG] 最终配置: {config}")
        print(f"[DEBUG] 物理核心: {os.cpu_count()} | 内存: {config['mem_total']:.1f}GB")

    try:
        if args.debug: print("[DEBUG] 正在加载模型...")
        model = WhisperModel(
            "base",  # 直接使用基本模型名称
            device="cpu",
            compute_type="int8",  # 在这里指定量化类型
            cpu_threads=config["max_threads"],
            local_files_only=True
        )

        duration = get_duration(args.input_path, args.debug)
        print(f"▶ 文件时长: {duration//60:.0f}分{duration%60:.0f}秒")
        print(f"⚙ 使用配置: {config['model']}模型 | {config['max_threads']}线程 | 分段{config['chunk_size']}秒")

        start_time = time.time()
        segments = []

        if duration > config["chunk_size"]:
            chunks = split_audio(args.input_path, config["chunk_size"], args.debug)
            for chunk_path, offset in chunks:
                if args.debug: print(f"[DEBUG] 转录分段：{chunk_path}（偏移 {offset}s）")
                chunk_segments, _ = model.transcribe(
                    chunk_path,
                    beam_size=config["beam_size"],
                    vad_filter=True
                )
                for seg in chunk_segments:
                    seg.start += offset
                    seg.end += offset
                    segments.append(seg)
        else:
            if args.debug: print("[DEBUG] 音频无需分段，直接转录")
            segments, _ = model.transcribe(
                args.input_path,
                beam_size=config["beam_size"],
                vad_filter=True
            )

        print("\n转录结果:")
        for seg in sorted(segments, key=lambda x: x.start):
            print(f"{seg.start:.1f}s\t{seg.text}")

        print(f"\n✅ 处理完成 | 用时: {time.time() - start_time:.2f}秒 | 平均速度: {duration/(time.time()-start_time):.1f}x")

    except Exception as e:
        print(f"错误: {str(e)}")
        if args.debug:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
```


## 转录音频文件：
``` bash
faster-whisper 1.m4a --model small --language zh
```

# ✅ 安全推荐方式：并行安装 Python 并设置默认版本（不破坏系统）

步骤 1：安装所需 Python 版本（以 3.10 为例）

```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3.10-dev
```
步骤 2：设置 python3 指向你想要的版本（使用 update-alternatives）

``` bash
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 2
sudo update-alternatives --config python3
```
然后系统会提示你选择默认版本。

⚠️ 注意：不要去动 /usr/bin/python（没有后缀的），Ubuntu 24 默认已经不再使用它来跑系统服务了，但 python3 是关键的系统依赖，请小心。


## 给你当前的 python3.10 安装 pip

```bash
python3.10 -m ensurepip --upgrade
```