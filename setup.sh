#!/bin/bash
# 快速开始脚本

echo "=========================================="
echo "  照片和视频处理脚本 - 快速开始"
echo "=========================================="
echo ""

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python版本: $python_version"
echo ""

# 检查ffmpeg
if command -v ffmpeg &> /dev/null; then
    ffmpeg_version=$(ffmpeg -version 2>&1 | head -n 1)
    echo "✓ ffmpeg已安装: $ffmpeg_version"
else
    echo "✗ ffmpeg未安装"
    echo "  请安装ffmpeg:"
    echo "    Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "    macOS: brew install ffmpeg"
    echo "    Windows: https://ffmpeg.org/download.html"
    echo ""
fi

echo "正在安装Python依赖..."
pip3 install -r requirements.txt

echo ""
echo "=========================================="
echo "  安装完成！"
echo "=========================================="
echo ""
echo "使用方法:"
echo "  python3 main.py <目录名>"
echo ""
echo "示例:"
echo "  python3 main.py ./20070922_mcm"
echo ""
