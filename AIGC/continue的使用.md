## 参考资料

https://zhuanlan.zhihu.com/p/1905949565015790407



## 常规配置文件
``` yaml
name: Local Config
version: 1.0.0
schema: v1

models:
  - name: Qwen3-Coder-30B
    provider: openai
    model: qwen3-coder-30b-a3b-instruct
    apiBase: http://10.147.47.99:1234/v1
    apiKey: lm-studio
    roles:
      - chat
      - edit
      - apply

context:
  - provider: code
  - provider: docs
  - provider: diff
  - provider: terminal
```

