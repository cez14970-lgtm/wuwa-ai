#!/bin/bash
# WuwaAI 一键安装脚本

set -e

echo "========================================"
echo "  WuwaAI 鸣潮智能自动化 - 安装脚本"
echo "========================================"

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python版本需要 >= 3.11, 当前版本: $python_version"
    exit 1
fi

echo "✅ Python版本检查通过: $python_version"

# 检查操作系统
if [[ "$OSTYPE" != "msys" && "$OSTYPE" != "win32" ]]; then
    echo "⚠️ 警告: 本项目主要针对Windows系统"
fi

# 创建虚拟环境
echo "📦 创建虚拟环境..."
python3 -m venv venv

# 激活虚拟环境
source venv/Scripts/activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
echo "📥 安装Python依赖..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# 安装ok-script (可选)
echo "📥 安装ok-script..."
pip install ok-script || echo "⚠️ ok-script安装失败，将使用备用方案"

# 配置环境变量
if [ ! -f backend/.env ]; then
    echo "📝 创建配置文件..."
    cp backend/.env.example backend/.env
    echo "⚠️ 请编辑 backend/.env 填入API密钥"
fi

# 创建必要目录
echo "📁 创建数据目录..."
mkdir -p data logs

echo ""
echo "========================================"
echo "  ✅ 安装完成！"
echo "========================================"
echo ""
echo "下一步:"
echo "1. 编辑 backend/.env 填入API密钥"
echo "2. 运行: source venv/Scripts/activate"
echo "3. 运行: python backend/main.py"
echo ""
