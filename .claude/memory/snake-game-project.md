---
name: snake-game-project
description: 贪吃蛇游戏项目概览——架构、技术栈、关键问题和解决方案
metadata:
  type: project
---

# 贪吃蛇游戏项目

## 基本信息

- **仓库路径：** `/home/weilei/code/vibeCoding`
- **游戏代码：** [snake_game/](../snake_game/)
- **语言：** Python 3.14
- **GUI 库：** pygame 2.6.1
- **架构：** 多模块 MVC（Model-View-Controller）
- **Git：** 已初始化，初始提交 `c2b339e`

## 架构说明

采用多模块分离设计，每个文件职责单一：

| 模块 | 文件 | 职责 |
|------|------|------|
| 配置 | [config.py](../snake_game/config.py) | 所有常量：窗口大小、颜色、速度参数、食物概率 |
| 游戏状态 | [game_state.py](../snake_game/game_state.py) | `Snake` 类（蛇的身体、方向、移动、碰撞检测）和 `GameState` 类（分数、速度、速度效果） |
| 食物 | [food.py](../snake_game/food.py) | `FoodType` 枚举（NORMAL/SPEED_UP/SLOW_DOWN）、`Food` 类（位置、计时器、颜色） |
| 障碍物 | [obstacles.py](../snake_game/obstacles.py) | 随机生成障碍物位置 |
| 渲染器 | [renderer.py](../snake_game/renderer.py) | 所有绘制逻辑：网格、蛇、食物、UI 文字、各场景画面 |
| 场景管理 | [scenes.py](../snake_game/scenes.py) | `Scene` 枚举（MENU/GAME/PAUSE/GAMEOVER）、状态机、事件分发、移动逻辑 |
| 最高分 | [highscore.py](../snake_game/highscore.py) | JSON 文件读写（`~/.snake_game_highscore.json`） |
| 主入口 | [main.py](../snake_game/main.py) | pygame 初始化、游戏循环（事件→更新→渲染→刷新） |

场景流转：**主菜单 → 游戏中 ↔ 暂停 → 游戏结束 → 主菜单**

## 关键技术问题和解决方案

### 1. Python 3.14 + pygame 2.6.1 循环导入 Bug

**问题：** `pygame.font` 和 `pygame.sysfont` 互相导入，导致 `ImportError: cannot import name 'Font' from partially initialized module 'pygame.font'`

**解决方案：** 修改 `pygame/sysfont.py`：
- 移除顶层的 `from pygame.font import Font`
- 改为在 `_load_font()` 函数内部延迟导入（lazy import）

**自动化：** [run.sh](../snake_game/run.sh) 中第 32-56 行使用 Python 正则自动检测并修补：
```bash
# 检测并替换顶层导入
content = re.sub(r'^from pygame\.font import Font$', '# patched: lazy import', content, flags=re.MULTILINE)
# 在函数内加入延迟导入
content = content.replace('    font = Font(fontpath, size)',
    '    from pygame.font import Font  # lazy import\n    font = Font(fontpath, size)')
```

此问题在每次重建 venv 后需要重新修补（`run.sh` 会自动处理）。

### 2. 中文渲染（CJK 字体检测）

**问题：** `pygame.font.Font(None, size)` 使用默认字体，只支持 ASCII，中文显示为方框/乱码。

**解决方案：** [renderer.py](../snake_game/renderer.py) 中实现跨平台中文字体自动检测：
- `_CJK_FONT_CANDIDATES` 列表覆盖 Linux/Windows/macOS 常见中文字体
- `_find_cjk_font_name()` 在系统已安装字体中搜索匹配
- `_create_font(size)` 优先使用找到的中文字体，失败则回退默认字体
- 所有 UI 文字（菜单、暂停、游戏结束、分数）通过 `_create_font` 渲染

注意：`pygame.font.get_fonts()` 返回的字体名是全小写，匹配时需要转换。

### 3. 无头渲染（Headless Rendering）

**问题：** 远程服务器没有物理显示器，pygame 需要 display 才能运行。

**解决方案：** 使用 Xvfb（X Virtual Framebuffer）虚拟显示：
- 下载 Xvfb 的 `.deb` 包，用 `dpkg-deb -x` 解压提取
- 运行：`Xvfb :99 -screen 0 800x600x24`
- 设置环境变量：`export DISPLAY=:99`

[headless_demo.py](../snake_game/headless_demo.py) 用于自动运行游戏并截图到 `/tmp/snake_screenshots/`。

### 4. pip 安装镜像

**问题：** PyPI 官方源在某些网络环境下超时。

**解决方案：** [run.sh](../snake_game/run.sh) 使用清华镜像源：
```
pip install pygame -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

## 运行方式

### 用户本地运行（推荐）
```bash
cd snake_game
bash run.sh
```
一键完成：创建 venv → 安装 pygame → 修补字体 bug → 启动游戏

### 服务器无头截图
```bash
export DISPLAY=:99
cd snake_game
.venv/bin/python headless_demo.py
```

## 设计文档

- 设计规范：[docs/superpowers/specs/2026-08-02-snake-game-design.md](../docs/superpowers/specs/2026-08-02-snake-game-design.md)
- 实施计划：[docs/superpowers/plans/2026-08-02-snake-game.md](../docs/superpowers/plans/2026-08-02-snake-game.md)

**Why:** 记录项目的架构决策、已知问题和解决方案，避免未来会话中重复排查相同问题。

**How to apply:** 当需要修改游戏代码、添加新功能、排查运行问题时，先查阅此记忆了解已有的技术方案和注意事项。

相关记忆：[[technical-novice-user]]
