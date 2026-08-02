# 速度控制功能实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为贪吃蛇游戏添加三档难度选择功能（慢速/中速/快速），支持菜单选择和游戏中切换。

**Architecture:** 在 config.py 中新增 DifficultyLevel 枚举和 DIFFICULTY_CONFIG 字典，GameState 根据当前难度从配置读取速度参数。SceneManager 管理菜单难度选择和游戏内切换，Renderer 负责难度显示和高亮效果。

**Tech Stack:** Python 3, Pygame

## Global Constraints

- 三档难度：慢速(200/8/80)、中速(150/10/50)、快速(100/12/30)，单位均为毫秒
- 菜单中用左/右方向键或A/D键循环切换难度，回车开始游戏
- 游戏中 1/2/3 键直接选择难度，+/- 键逐步切换
- 难度切换时立即生效，临时速度效果保持不变
- 难度指示器在左上角显示，切换时高亮约1秒

---

### Task 1: 创建 Git 分支

**Files:** 无

- [ ] **Step 1: 创建并切换到新分支**

```bash
git checkout -b feature/speed-control
```

- [ ] **Step 2: 验证分支创建成功**

```bash
git branch --show-current
```

Expected: 输出 `feature/speed-control`

---

### Task 2: 新增难度配置到 config.py

**Files:**
- Modify: `snake_game/config.py`

**Interfaces:**
- Produces: `DifficultyLevel` 枚举, `DIFFICULTY_CONFIG` 字典, `DIFFICULTY_COLORS` 字典

- [ ] **Step 1: 在 config.py 中添加难度枚举和配置**

在 `config.py` 文件顶部（`"""游戏常量配置"""` 之后）添加 `from enum import Enum`，然后在文件末尾添加：

```python
# 难度等级
class DifficultyLevel(Enum):
    SLOW = "慢速"
    MEDIUM = "中速"
    FAST = "快速"

# 难度参数配置
DIFFICULTY_CONFIG = {
    DifficultyLevel.SLOW:   {"base_speed": 200, "speed_increment": 8,  "min_speed": 80},
    DifficultyLevel.MEDIUM: {"base_speed": 150, "speed_increment": 10, "min_speed": 50},
    DifficultyLevel.FAST:   {"base_speed": 100, "speed_increment": 12, "min_speed": 30},
}

# 难度颜色
DIFFICULTY_COLORS = {
    DifficultyLevel.SLOW:   COLOR_GREEN,
    DifficultyLevel.MEDIUM: COLOR_YELLOW,
    DifficultyLevel.FAST:   COLOR_RED,
}

# 难度循环顺序（用于逐步切换）
DIFFICULTY_ORDER = [DifficultyLevel.SLOW, DifficultyLevel.MEDIUM, DifficultyLevel.FAST]
```

- [ ] **Step 2: 验证语法正确**

```bash
cd snake_game && python -c "from config import DifficultyLevel, DIFFICULTY_CONFIG, DIFFICULTY_COLORS, DIFFICULTY_ORDER; print('OK')"
```

Expected: 输出 `OK`

- [ ] **Step 3: 提交**

```bash
git add snake_game/config.py
git commit -m "feat: 添加难度等级枚举和配置"
```

---

### Task 3: 改造 GameState 使用难度配置

**Files:**
- Modify: `snake_game/game_state.py`

**Interfaces:**
- Consumes: `DifficultyLevel`, `DIFFICULTY_CONFIG` from config
- Produces: `GameState.difficulty` 属性, 改造后的 `speed` 和 `get_effective_speed()`

- [ ] **Step 1: 修改 import 和添加 difficulty 属性**

在 `game_state.py` 的 import 部分，将 `BASE_SPEED, SPEED_INCREMENT, MIN_SPEED` 替换为 `DifficultyLevel, DIFFICULTY_CONFIG`：

```python
from config import (
    GRID_WIDTH, GRID_HEIGHT,
    SNAKE_START_X, SNAKE_START_Y, SNAKE_START_LENGTH,
    SNAKE_START_DIRECTION, OPPOSITE_DIRECTIONS,
    FOODS_PER_LEVEL, SPEED_EFFECT_DURATION,
    OBSTACLE_COUNT,
    DifficultyLevel, DIFFICULTY_CONFIG,
)
```

在 `GameState.__init__()` 中添加 `self.difficulty = DifficultyLevel.MEDIUM`。

- [ ] **Step 2: 改造 speed 属性**

将 `GameState.speed` 属性改为从 `DIFFICULTY_CONFIG` 读取：

```python
@property
def speed(self) -> int:
    """当前蛇的基础移动间隔（毫秒），取决于难度和等级"""
    cfg = DIFFICULTY_CONFIG[self.difficulty]
    level = self.foods_eaten // FOODS_PER_LEVEL
    return max(cfg["min_speed"], cfg["base_speed"] - level * cfg["speed_increment"])
```

- [ ] **Step 3: 改造 get_effective_speed 方法**

将 `get_effective_speed()` 中的 `MIN_SPEED` 替换为配置中的 `min_speed`：

```python
def get_effective_speed(self) -> int:
    """获取考虑临时效果后的实际移动间隔（毫秒）"""
    cfg = DIFFICULTY_CONFIG[self.difficulty]
    speed = self.speed
    if self.speed_effect_active:
        speed = max(cfg["min_speed"], speed + self._speed_modifier)
    return speed
```

- [ ] **Step 4: 添加 set_difficulty 方法**

在 `GameState` 类中添加：

```python
def set_difficulty(self, difficulty: DifficultyLevel) -> None:
    """设置难度等级"""
    self.difficulty = difficulty
```

- [ ] **Step 5: 验证语法正确**

```bash
cd snake_game && python -c "from game_state import GameState; from config import DifficultyLevel; gs = GameState(); print(gs.speed); gs.set_difficulty(DifficultyLevel.FAST); print(gs.speed)"
```

Expected: 输出两行数字，第二行比第一行小（快速模式基础速度更快，间隔更短）

- [ ] **Step 6: 提交**

```bash
git add snake_game/game_state.py
git commit -m "feat: GameState 支持难度等级配置"
```

---

### Task 4: 改造 Renderer 支持难度显示

**Files:**
- Modify: `snake_game/renderer.py`

**Interfaces:**
- Consumes: `DifficultyLevel`, `DIFFICULTY_COLORS` from config
- Produces: `draw_difficulty_indicator()` 方法, 改造后的 `draw_menu()`

- [ ] **Step 1: 添加 import**

在 `renderer.py` 的 import 部分，添加 `DifficultyLevel, DIFFICULTY_COLORS`：

```python
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, CELL_SIZE,
    COLOR_BLACK, COLOR_WHITE, COLOR_GREEN, COLOR_GREEN_DARK,
    COLOR_GREEN_LIGHT, COLOR_RED, COLOR_DARK_RED,
    COLOR_YELLOW, COLOR_GRAY, COLOR_GRAY_LIGHT,
    DifficultyLevel, DIFFICULTY_COLORS,
)
```

- [ ] **Step 2: 添加 draw_difficulty_indicator 方法**

在 `Renderer` 类中添加方法（在 `draw_speed_indicator` 之后）：

```python
def draw_difficulty_indicator(self, difficulty: DifficultyLevel, highlight_timer: float = 0.0) -> None:
    """绘制难度指示器（左上角，分数下方）"""
    color = DIFFICULTY_COLORS[difficulty]
    # 高亮效果：timer > 0 时用白色
    if highlight_timer > 0:
        color = COLOR_WHITE
    text = self._small_font.render(f"难度: {difficulty.value}", True, color)
    self.screen.blit(text, (10, 35))
```

- [ ] **Step 3: 改造 draw_menu 方法**

将 `draw_menu` 方法签名改为接受 `difficulty` 参数，并显示难度选择：

```python
def draw_menu(self, highscore: int, difficulty: DifficultyLevel) -> None:
    """绘制主菜单"""
    self.draw_background()
    self._draw_centered_text("贪  吃  蛇", self._title_font, COLOR_GREEN_LIGHT, -80)
    self._draw_centered_text(
        f"难度: {difficulty.value}  ← →切换",
        self._medium_font, DIFFICULTY_COLORS[difficulty], -10
    )
    self._draw_centered_text("按回车开始游戏", self._medium_font, COLOR_WHITE, 40)
    self._draw_centered_text(
        "方向键 / WASD 移动    空格暂停    Esc 退出",
        self._small_font, COLOR_GRAY_LIGHT, 85
    )
    if highscore > 0:
        self._draw_centered_text(
            f"最高分: {highscore}", self._small_font, COLOR_YELLOW, 120
        )
```

- [ ] **Step 4: 验证语法正确**

```bash
cd snake_game && python -c "from renderer import Renderer; print('OK')"
```

Expected: 输出 `OK`

- [ ] **Step 5: 提交**

```bash
git add snake_game/renderer.py
git commit -m "feat: Renderer 支持难度指示器和菜单难度显示"
```

---

### Task 5: 改造 SceneManager 菜单难度选择

**Files:**
- Modify: `snake_game/scenes.py`

**Interfaces:**
- Consumes: `DifficultyLevel`, `DIFFICULTY_ORDER` from config, `Renderer.draw_menu(highscore, difficulty)`
- Produces: `SceneManager.menu_difficulty` 属性, 菜单切换逻辑

- [ ] **Step 1: 添加 import**

在 `scenes.py` 的 import 部分，添加 `DifficultyLevel, DIFFICULTY_ORDER`：

```python
from config import (
    DIRECTION_UP, DIRECTION_DOWN, DIRECTION_LEFT, DIRECTION_RIGHT,
    SPEED_EFFECT_AMOUNT,
    DifficultyLevel, DIFFICULTY_ORDER,
)
```

- [ ] **Step 2: 在 __init__ 中添加 menu_difficulty**

在 `SceneManager.__init__()` 中添加：

```python
self.menu_difficulty = DifficultyLevel.MEDIUM
```

- [ ] **Step 3: 改造 start_game 方法**

修改 `start_game()` 方法，将当前菜单难度传递给 GameState：

```python
def start_game(self) -> None:
    """开始新一局游戏"""
    self.game_state = GameState()
    self.game_state.set_difficulty(self.menu_difficulty)
    self.food = spawn_food(self.game_state.get_empty_positions())
    self._move_timer = 0
    self.difficulty_highlight_timer = 0.0
```

- [ ] **Step 4: 改造 _handle_menu_key 方法**

修改 `_handle_menu_key()` 方法，添加难度切换逻辑：

```python
def _handle_menu_key(self, key: int) -> None:
    if key == pygame.K_RETURN:
        self.scene = Scene.GAME
        self.start_game()
    elif key in (pygame.K_LEFT, pygame.K_a):
        self._cycle_menu_difficulty(-1)
    elif key in (pygame.K_RIGHT, pygame.K_d):
        self._cycle_menu_difficulty(1)

def _cycle_menu_difficulty(self, direction: int) -> None:
    """在菜单中循环切换难度"""
    idx = DIFFICULTY_ORDER.index(self.menu_difficulty)
    idx = (idx + direction) % len(DIFFICULTY_ORDER)
    self.menu_difficulty = DIFFICULTY_ORDER[idx]
```

- [ ] **Step 5: 改造 draw 方法中的菜单调用**

修改 `draw()` 方法中的菜单绘制调用：

```python
if self.scene == Scene.MENU:
    self.renderer.draw_menu(self.highscore, self.menu_difficulty)
```

- [ ] **Step 6: 验证语法正确**

```bash
cd snake_game && python -c "from scenes import SceneManager; print('OK')"
```

Expected: 输出 `OK`

- [ ] **Step 7: 提交**

```bash
git add snake_game/scenes.py
git commit -m "feat: 菜单支持难度选择"
```

---

### Task 6: 添加游戏中难度切换

**Files:**
- Modify: `snake_game/scenes.py`

**Interfaces:**
- Consumes: `GameState.set_difficulty()`, `DifficultyLevel`
- Produces: 游戏中 1/2/3 和 +/- 键切换难度

- [ ] **Step 1: 在 __init__ 中添加 difficulty_highlight_timer**

确保 `SceneManager.__init__()` 中已添加（Task 5 的 start_game 中已初始化）：

```python
self.difficulty_highlight_timer = 0.0
```

同时在 `__init__` 末尾添加初始值：

```python
self.difficulty_highlight_timer = 0.0
```

- [ ] **Step 2: 在 _handle_game_key 中添加难度切换按键**

在 `_handle_game_key()` 方法中添加新的按键处理：

```python
def _handle_game_key(self, key: int) -> None:
    if self.game_state is None:
        return
    if key == pygame.K_SPACE:
        self.scene = Scene.PAUSE
    elif key in (pygame.K_UP, pygame.K_w):
        self.game_state.snake.set_direction(DIRECTION_UP)
    elif key in (pygame.K_DOWN, pygame.K_s):
        self.game_state.snake.set_direction(DIRECTION_DOWN)
    elif key in (pygame.K_LEFT, pygame.K_a):
        self.game_state.snake.set_direction(DIRECTION_LEFT)
    elif key in (pygame.K_RIGHT, pygame.K_d):
        self.game_state.snake.set_direction(DIRECTION_RIGHT)
    elif key == pygame.K_1:
        self._set_game_difficulty(DifficultyLevel.SLOW)
    elif key == pygame.K_2:
        self._set_game_difficulty(DifficultyLevel.MEDIUM)
    elif key == pygame.K_3:
        self._set_game_difficulty(DifficultyLevel.FAST)
    elif key in (pygame.K_EQUALS, pygame.K_PLUS):
        self._cycle_game_difficulty(1)
    elif key == pygame.K_MINUS:
        self._cycle_game_difficulty(-1)
```

- [ ] **Step 3: 添加辅助方法**

在 `SceneManager` 类中添加：

```python
def _set_game_difficulty(self, difficulty: DifficultyLevel) -> None:
    """在游戏中设置难度"""
    if self.game_state:
        self.game_state.set_difficulty(difficulty)
        self.difficulty_highlight_timer = 1.0

def _cycle_game_difficulty(self, direction: int) -> None:
    """在游戏中逐步切换难度"""
    if self.game_state is None:
        return
    idx = DIFFICULTY_ORDER.index(self.game_state.difficulty)
    idx = (idx + direction) % len(DIFFICULTY_ORDER)
    self.game_state.set_difficulty(DIFFICULTY_ORDER[idx])
    self.difficulty_highlight_timer = 1.0
```

- [ ] **Step 4: 在 update 中递减高亮计时器**

在 `update()` 方法中，在 `self.game_state.update(dt)` 之后添加：

```python
if self.difficulty_highlight_timer > 0:
    self.difficulty_highlight_timer -= dt
    if self.difficulty_highlight_timer < 0:
        self.difficulty_highlight_timer = 0
```

- [ ] **Step 5: 验证语法正确**

```bash
cd snake_game && python -c "from scenes import SceneManager; print('OK')"
```

Expected: 输出 `OK`

- [ ] **Step 6: 提交**

```bash
git add snake_game/scenes.py
git commit -m "feat: 游戏中支持难度切换（1/2/3键和+/-键）"
```

---

### Task 7: 集成难度指示器到游戏画面

**Files:**
- Modify: `snake_game/scenes.py`

**Interfaces:**
- Consumes: `Renderer.draw_difficulty_indicator(difficulty, highlight_timer)`
- Produces: 游戏画面中显示难度指示器

- [ ] **Step 1: 修改 _draw_game_scene 方法**

在 `_draw_game_scene()` 方法中，在 `self.renderer.draw_speed_indicator(self.game_state)` 之后添加：

```python
self.renderer.draw_difficulty_indicator(
    self.game_state.difficulty,
    self.difficulty_highlight_timer
)
```

- [ ] **Step 2: 运行游戏手动测试**

```bash
cd snake_game && bash run.sh
```

测试项：
1. 菜单中按左/右方向键切换难度，显示正确
2. 按回车开始游戏，难度与菜单选择一致
3. 游戏中按 1/2/3 切换难度，指示器高亮
4. 游戏中按 +/- 逐步切换难度
5. 难度切换后蛇的速度立即变化
6. 加速/减速食物效果在新难度上仍正常生效

- [ ] **Step 3: 提交最终代码**

```bash
git add snake_game/scenes.py
git commit -m "feat: 游戏画面显示难度指示器"
```

---

### Task 8: 清理旧常量

**Files:**
- Modify: `snake_game/config.py`

- [ ] **Step 1: 检查旧常量是否还被引用**

```bash
cd snake_game && grep -rn "BASE_SPEED\|SPEED_INCREMENT\|MIN_SPEED" --include="*.py" .
```

Expected: 只有 config.py 中定义这些常量，没有其他文件引用它们（如果还有引用，需要先更新那些文件）

- [ ] **Step 2: 移除未使用的常量**

在 `config.py` 中删除以下三行（已被 `DIFFICULTY_CONFIG` 替代）：

```python
BASE_SPEED = 150          # 初始速度
SPEED_INCREMENT = 10      # 每升一级减少的毫秒数
MIN_SPEED = 50            # 最快速度上限
```

- [ ] **Step 3: 验证游戏仍可运行**

```bash
cd snake_game && python -c "from scenes import SceneManager; from game_state import GameState; print('OK')"
```

Expected: 输出 `OK`

- [ ] **Step 4: 提交**

```bash
git add snake_game/config.py
git commit -m "refactor: 移除旧的硬编码速度常量"
```
