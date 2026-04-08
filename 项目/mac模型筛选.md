

[Qwen3.5-35B无限制版：需要什么配置？怎么部署？](https://zhuanlan.zhihu.com/p/2019198240344524572)
Qwen3.5 27B


## 模型选择 
HauhauCS/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive
最近Qwen 35b登顶，开源模型热门榜第一了！不过，不是Qwen官方的模型，而是去审查破解版。破解后，这个模型几乎不拒绝回答任何问题，内容过滤墙被拆了，可以接入龙虾opencalw，无限token的成人版龙虾，原生多模态，内容非常震撼，具体细节我就不方便贴出来了。


## 如何部署？

### 路线A：Ollama（有一点技术基础的用户）最省事
Ollama是目前最主流的本地大模型管理工具，Windows和Mac都支持。

去 http://ollama.com 下载安装
打开终端，输入对应的模型拉取命令（在HuggingFace模型页面可以找到Ollama命令格式）
第一次运行会自动下载模型（约20GB，耐心等），下载完直接开始对话
Mac用户建议在搜索时优先找MLX版本，推理速度更快。

brew install ollama

ollama run qwen:14b


### 路线B：LM Studio（推荐小白，纯图形界面）
去 lmstudio.ai 下载安装，Windows和Mac都有
打开后在搜索栏输入：HauhauCS/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive，找到Q4_K_M量化版下载
加载模型后直接在内置对话界面使用

LM Studio的优势是能实时显示显存占用，方便判断当前配置能不能撑住

踩坑提醒：模型文件约20GB，下载前先确认硬盘空间够用；第一次加载较慢，这是正常现象，等就完了，不是卡死。