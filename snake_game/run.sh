#!/bin/bash
# 贪吃蛇游戏 — 一键安装 & 启动脚本
# 用法: bash run.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "🐍 贪吃蛇游戏启动器"
echo "===================="

# 1. 创建虚拟环境（如果不存在）
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 首次运行，正在创建虚拟环境..."
    python3 -m venv "$VENV_DIR"
    echo "✅ 虚拟环境已创建"
else
    echo "✅ 虚拟环境已存在"
fi

# 2. 安装 pygame（如果未安装）
if ! "$VENV_DIR/bin/python" -c "import pygame" 2>/dev/null; then
    echo "📥 正在安装 pygame（使用清华镜像源）..."
    "$VENV_DIR/bin/pip" install pygame -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
    echo "✅ pygame 安装完成"
else
    echo "✅ pygame 已安装"
fi

# 3. 修补 Python 3.14 下 pygame 的字体模块循环导入 bug
SYSFONT_FILE=$(find "$VENV_DIR" -path "*/pygame/sysfont.py" -type f 2>/dev/null | head -1)
if [ -n "$SYSFONT_FILE" ]; then
    if grep -q "from pygame.font import Font$" "$SYSFONT_FILE" 2>/dev/null; then
        echo "🔧 修补 pygame 字体模块兼容性问题..."
        "$VENV_DIR/bin/python" -c "
import re
with open('$SYSFONT_FILE', 'r') as f:
    content = f.read()
# 1. 移除顶层的 from pygame.font import Font
content = re.sub(r'^from pygame\.font import Font$', '# patched: lazy import', content, flags=re.MULTILINE)
# 2. 在 _load_font 函数内加入延迟导入
content = content.replace(
    '    font = Font(fontpath, size)',
    '    from pygame.font import Font  # lazy import\n    font = Font(fontpath, size)'
)
with open('$SYSFONT_FILE', 'w') as f:
    f.write(content)
print('Patched successfully')
" && echo "✅ 修补完成" || echo "⚠️ 修补失败，游戏可能无法启动"
    else
        echo "✅ pygame 字体模块已修补"
    fi
else
    echo "⚠️ 未找到 pygame.sysfont.py，跳过修补"
fi

# 4. 启动游戏
echo "🚀 启动游戏..."
echo ""
echo "  操作提示："
echo "    方向键 / WASD  移动"
echo "    空格           暂停"
echo "    回车           确认"
echo "    Esc            退出"
echo ""

"$VENV_DIR/bin/python" "$SCRIPT_DIR/main.py"
