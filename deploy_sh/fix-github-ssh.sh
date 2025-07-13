#!/bin/bash

set -e

KEY_PATH="$HOME/.ssh/id_rsa"
CONFIG_PATH="$HOME/.ssh/config"

echo "🔍 检查私钥文件是否存在：$KEY_PATH"
if [ ! -f "$KEY_PATH" ]; then
  echo "❌ 找不到 SSH 私钥: $KEY_PATH"
  echo "请先运行 ssh-keygen -t rsa -b 4096 -C \"your_email@example.com\""
  exit 1
fi

echo "✅ 找到私钥，继续..."

# 创建或修复 ~/.ssh/config 文件
echo "🛠️ 修复 ~/.ssh/config..."
mkdir -p ~/.ssh
touch "$CONFIG_PATH"

# 删除旧的 github.com 配置段（如果有）
sed -i.bak '/^Host github.com$/,/^Host /{/^Host /!d}' "$CONFIG_PATH"

# 追加正确配置
cat <<EOF >> "$CONFIG_PATH"
Host github.com
  HostName github.com
  User git
  IdentityFile $KEY_PATH
  IdentitiesOnly yes
EOF

chmod 600 "$CONFIG_PATH"
echo "✅ 写入完成：$CONFIG_PATH"

# 启动 ssh-agent 并添加密钥
echo "🚀 启动 ssh-agent..."
eval "$(ssh-agent -s)"
ssh-add "$KEY_PATH"

# 测试连接 GitHub
echo "🔗 测试连接 GitHub..."
ssh -T git@github.com || echo "⚠️ SSH 验证失败，确保你已将公钥添加到 GitHub"

# 显示公钥供添加（如果尚未添加）
PUB_KEY="$KEY_PATH.pub"
if [ -f "$PUB_KEY" ]; then
  echo -e "\n📋 请将以下公钥添加到 GitHub: https://github.com/settings/keys\n"
  cat "$PUB_KEY"
else
  echo "⚠️ 找不到公钥文件: $PUB_KEY"
fi

echo -e "\n🎉 修复完成！你现在可以使用 git clone ssh 链接正常访问 GitHub 了。"
