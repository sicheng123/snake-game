# 速度控制功能设计文档

## 概述

为贪吃蛇游戏添加难度选择功能，允许玩家在三档难度（慢速/中速/快速）之间选择，支持游戏前在菜单中选择初始难度，以及在游戏中随时切换难度。

## 数据模型

### 难度枚举

在 `config.py` 中新增：

```python
from enum import Enum, auto

class DifficultyLevel(Enum):
    SLOW = "慢速"
    MEDIUM = "中速"
    FAST = "快速"

# 难度参数配置：(基础速度ms, 升级加速量ms, 最快上限ms)
DIFFICULTY_CONFIG = {
    DifficultyLevel.SLOW:   {"base_speed": 200, "speed_increment": 8,  "min_speed": 80},
    DifficultyLevel.MEDIUM: {"base_speed": 150, "speed_increment": 10, "min_speed": 50},
    DifficultyLevel.FAST:   {"base_speed": 100, "speed_increment": 12, "min_speed": 30},
}
```

### 难度参数对照表

| 档位 | 基础速度 | 升级加速量 | 最快上限 |
|------|---------|-----------|---------|
| 慢速 | 200ms | 8ms | 80ms |
| 中速 | 150ms | 10ms | 50ms |
| 快速 | 100ms | 12ms | 30ms |

### GameState 改造

- 新增 `difficulty` 属性（默认 `DifficultyLevel.MEDIUM`）
- `speed` 属性和 `get_effective_speed()` 方法改为从 `DIFFICULTY_CONFIG[difficulty]` 读取参数
- 移除对 `BASE_SPEED`、`SPEED_INCREMENT`、`MIN_SPEED` 常量的直接引用

## 菜单难度选择

### 交互方式

- 菜单界面显示当前难度（默认"中速"）
- 按**左/右方向键**或**A/D键**循环切换难度（慢速 → 中速 → 快速 → 慢速...）
- 按**回车键**开始游戏（使用选中的难度）

### 菜单界面布局

```
    贪吃蛇
    
    难度: [慢速] ← →切换
    
    按回车开始游戏
    按Esc退出
```

- 当前选中的难度用高亮颜色显示
- 切换时有简单的视觉反馈（颜色闪烁或短暂放大效果）

### SceneManager 改造

- 新增 `menu_difficulty` 属性，在菜单场景中跟踪当前选择的难度
- `start_game()` 方法接受难度参数，初始化 `GameState.difficulty`

## 游戏中切换难度

### 按键绑定

- **1/2/3 键** — 直接切换到 慢速/中速/快速
- **+/- 键**（即 `=` 和 `-` 键）— 逐步切换（慢速 → 中速 → 快速 → 慢速...循环）

### 切换逻辑

- 蛇的速度**立即**更新为新档位的基础速度
- 已有的临时速度效果（加速/减速食物）保持不变，继续生效到新档位上
- 当前等级进度（已吃食物数）不变

### 事件处理

在 `SceneManager._handle_game_key()` 中新增难度切换按键的处理逻辑：
- 检查按键是否为 1/2/3 或 +/-
- 更新 `game_state.difficulty`
- 设置难度指示器高亮计时器

## 视觉指示器

### 显示位置

游戏界面**左上角**（分数下方）显示当前难度标签，如 `难度: 中速`

### 高亮效果

- 难度切换时，标签**短暂高亮**（约1秒内从普通颜色渐变为高亮色再恢复）
- `SceneManager` 维护 `difficulty_highlight_timer`，切换难度时设为 1.0 秒，每帧递减

### 颜色区分

三档难度用不同颜色区分：
- 慢速 → 绿色 `COLOR_GREEN`
- 中速 → 黄色 `COLOR_YELLOW`
- 快速 → 红色 `COLOR_RED`

### Renderer 改造

新增方法：
- `draw_difficulty_indicator(difficulty: DifficultyLevel, highlight_timer: float)` — 绘制难度标签和高亮效果

## 文件变更清单

| 文件 | 变更内容 |
|------|---------|
| `config.py` | 新增 `DifficultyLevel` 枚举、`DIFFICULTY_CONFIG` 字典、难度颜色映射 |
| `game_state.py` | 新增 `difficulty` 属性，改造 `speed` 和 `get_effective_speed()` 从配置读取 |
| `scenes.py` | 菜单新增难度选择逻辑，游戏新增难度切换按键，新增 `difficulty_highlight_timer` |
| `renderer.py` | 新增 `draw_difficulty_indicator()` 方法，改造 `draw_menu()` 显示难度选择 |

## 不变的部分

- 蛇的移动逻辑、碰撞检测、食物系统保持不变
- 临时速度效果（加速/减速食物）机制不变，只是作用于新档位的基础速度
- 最高分记录逻辑不变
- 障碍物系统不变
