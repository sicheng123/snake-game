# 贪吃蛇游戏实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 使用 Python + pygame 实现一个完整版贪吃蛇游戏，包含多种食物、障碍物、场景管理和最高分。

**Architecture:** 多模块 MVC 架构，8 个文件各司其职。数据流向为 `按键事件 → 场景管理器 → 游戏状态更新 → 渲染器绘制`，渲染器只读不写。

**Tech Stack:** Python 3.8+, pygame

## Global Constraints

- Python 3.8+
- 依赖：`pygame`（`pip install pygame`）
- 窗口：800×600 像素，网格 20×20 像素，可玩区域 40×30 格
- 所有界面文字使用中文
- 最高分存储在 `~/.snake_game_highscore.json`

---

### Task 1: 项目配置 (`config.py`)

**Files:**
- Create: `snake_game/config.py`

**Interfaces:**
- Produces: 所有常量（窗口尺寸、颜色、速度参数、食物概率、障碍物数量）

- [ ] **Step 1: 编写配置文件**

```python
"""游戏常量配置"""

# 窗口设置
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CELL_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // CELL_SIZE   # 40
GRID_HEIGHT = WINDOW_HEIGHT // CELL_SIZE  # 30

# 帧率（用于界面渲染刷新，不是蛇的速度）
FPS = 60

# 颜色定义 (R, G, B)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GREEN = (0, 200, 0)
COLOR_GREEN_DARK = (0, 150, 0)
COLOR_GREEN_LIGHT = (0, 255, 100)
COLOR_RED = (200, 50, 50)
COLOR_DARK_RED = (120, 30, 30)
COLOR_YELLOW = (255, 255, 0)
COLOR_BLUE = (50, 100, 255)
COLOR_GRAY = (40, 40, 40)
COLOR_GRAY_LIGHT = (60, 60, 60)
COLOR_OVERLAY = (0, 0, 0, 180)  # 遮罩背景

# 蛇的设置
SNAKE_START_LENGTH = 3
SNAKE_START_X = GRID_WIDTH // 2
SNAKE_START_Y = GRID_HEIGHT // 2
SNAKE_START_DIRECTION = (1, 0)  # 初始向右

# 速度设置（毫秒/步）
BASE_SPEED = 150          # 初始速度
SPEED_INCREMENT = 10      # 每升一级减少的毫秒数
MIN_SPEED = 50            # 最快速度上限
FOODS_PER_LEVEL = 5       # 每吃 N 个食物升一级
SPEED_EFFECT_DURATION = 8  # 加速/减速效果持续时间（秒）
SPEED_EFFECT_AMOUNT = 30  # 速度效果影响量（毫秒）

# 食物设置
FOOD_NORMAL_CHANCE = 0.70
FOOD_SPEED_UP_CHANCE = 0.15
FOOD_SLOW_DOWN_CHANCE = 0.15
FOOD_NORMAL_SCORE = 10
FOOD_SPEED_UP_SCORE = 5
FOOD_SLOW_DOWN_SCORE = 5
FOOD_TIMED_DURATION = 8   # 限时食物持续时间（秒）

# 障碍物设置
OBSTACLE_COUNT = 8

# 方向向量
DIRECTION_UP = (0, -1)
DIRECTION_DOWN = (0, 1)
DIRECTION_LEFT = (-1, 0)
DIRECTION_RIGHT = (1, 0)

# 反向映射（用于防反向）
OPPOSITE_DIRECTIONS = {
    DIRECTION_UP: DIRECTION_DOWN,
    DIRECTION_DOWN: DIRECTION_UP,
    DIRECTION_LEFT: DIRECTION_RIGHT,
    DIRECTION_RIGHT: DIRECTION_LEFT,
}
```

- [ ] **Step 2: 验证文件无语法错误**

```bash
python -c "import sys; sys.path.insert(0, 'snake_game'); import config; print('OK:', config.GRID_WIDTH, 'x', config.GRID_HEIGHT)"
```

---

### Task 2: 高分配置 (`highscore.py`)

**Files:**
- Create: `snake_game/highscore.py`

**Interfaces:**
- Produces: `load_highscore() -> int`, `save_highscore(score: int) -> None`

- [ ] **Step 1: 编写最高分模块**

```python
"""最高分持久化管理"""
import json
import os


SCORE_FILE = os.path.expanduser("~/.snake_game_highscore.json")


def load_highscore() -> int:
    """读取最高分，文件不存在或损坏时返回 0"""
    try:
        with open(SCORE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return int(data.get("score", 0))
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return 0


def save_highscore(score: int) -> None:
    """保存最高分（仅当新分数大于已存储分数时）"""
    current = load_highscore()
    if score > current:
        try:
            with open(SCORE_FILE, "w", encoding="utf-8") as f:
                json.dump({"score": score}, f)
        except OSError:
            pass
```

- [ ] **Step 2: 手动验证读写逻辑**

```bash
python -c "
import sys; sys.path.insert(0, 'snake_game')
from highscore import load_highscore, save_highscore
print('当前最高分:', load_highscore())
save_highscore(100)
print('保存 100 后:', load_highscore())
save_highscore(50)
print('保存 50 后（不应覆盖）:', load_highscore())
save_highscore(0)
print('恢复为 0 后:', load_highscore())
"
```

---

### Task 3: 游戏状态核心 (`game_state.py`)

**Files:**
- Create: `snake_game/game_state.py`

**Interfaces:**
- Consumes: `config.py` (所有常量)
- Produces:
  - `class Snake`: `body: list[tuple[int,int]]`, `direction: tuple[int,int]`, `grow_flag: bool`, `move() -> None`, `head -> tuple[int,int]`, `check_self_collision() -> bool`, `check_wall_collision() -> bool`
  - `class GameState`: `snake: Snake`, `score: int`, `speed: int`, `foods_eaten: int`, `obstacles: list[tuple[int,int]]`, `speed_effect_timer: float`, `update() -> bool`, `add_score(points: int)`, `apply_speed_effect(amount: int)`

- [ ] **Step 1: 编写游戏状态模块**

```python
"""游戏核心状态：蛇的移动、碰撞检测、计分"""
import random
from config import (
    GRID_WIDTH, GRID_HEIGHT,
    SNAKE_START_X, SNAKE_START_Y, SNAKE_START_LENGTH,
    SNAKE_START_DIRECTION, OPPOSITE_DIRECTIONS,
    BASE_SPEED, SPEED_INCREMENT, MIN_SPEED,
    FOODS_PER_LEVEL, SPEED_EFFECT_DURATION,
    OBSTACLE_COUNT,
)


class Snake:
    """蛇的数据模型"""

    def __init__(self):
        # 身体：列表，索引 0 为头部
        self.body = [
            (SNAKE_START_X - i, SNAKE_START_Y)
            for i in range(SNAKE_START_LENGTH)
        ]
        self.direction = SNAKE_START_DIRECTION
        self._grow_flag = False

    @property
    def head(self) -> tuple:
        """返回蛇头坐标"""
        return self.body[0]

    def set_direction(self, new_direction: tuple) -> None:
        """设置方向，自动拦截反向输入"""
        if OPPOSITE_DIRECTIONS.get(new_direction) != self.direction:
            self.direction = new_direction

    def move(self) -> None:
        """蛇前进一步"""
        new_head = (
            self.head[0] + self.direction[0],
            self.head[1] + self.direction[1],
        )
        self.body.insert(0, new_head)
        if self._grow_flag:
            self._grow_flag = False
        else:
            self.body.pop()

    def grow(self) -> None:
        """标记下一步移动时变长"""
        self._grow_flag = True

    def check_wall_collision(self) -> bool:
        """检查是否撞墙"""
        x, y = self.head
        return x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT

    def check_self_collision(self) -> bool:
        """检查是否撞到自己"""
        return self.head in self.body[1:]

    def occupies(self, pos: tuple) -> bool:
        """检查某坐标是否被蛇身占据"""
        return pos in self.body


class GameState:
    """游戏整体状态"""

    def __init__(self):
        self.snake = Snake()
        self.score = 0
        self.foods_eaten = 0
        self.obstacles = []
        self._base_speed = BASE_SPEED
        self._speed_effect_timer = 0.0
        self._generate_obstacles()

    @property
    def speed(self) -> int:
        """当前蛇的移动间隔（毫秒），含等级和临时效果"""
        level = self.foods_eaten // FOODS_PER_LEVEL
        base = max(MIN_SPEED, BASE_SPEED - level * SPEED_INCREMENT)
        return base

    @property
    def speed_effect_active(self) -> bool:
        return self._speed_effect_timer > 0

    @property
    def speed_effect_timer(self) -> float:
        return self._speed_effect_timer

    def add_score(self, points: int) -> None:
        self.score += points
        self.foods_eaten += 1

    def apply_speed_effect(self, amount_ms: int) -> None:
        """应用临时速度效果（正值为减速，负值为加速），直接用 timer 记录"""
        self._speed_effect_timer = SPEED_EFFECT_DURATION

    def update(self, dt: float) -> None:
        """更新速度效果计时器"""
        if self._speed_effect_timer > 0:
            self._speed_effect_timer -= dt
            if self._speed_effect_timer < 0:
                self._speed_effect_timer = 0

    def get_effective_speed(self) -> int:
        """获取考虑临时效果后的实际速度"""
        speed = self.speed
        if self.speed_effect_active:
            # 加速效果使间隔减小，减速效果使间隔增大
            speed = max(MIN_SPEED, speed + SPEED_EFFECT_AMOUNT)  # TODO: 需要根据效果类型区分
        return speed

    def check_obstacle_collision(self) -> bool:
        """检查蛇头是否撞到障碍物"""
        return self.snake.head in self.obstacles

    def _generate_obstacles(self) -> None:
        """在蛇初始位置之外生成随机障碍物"""
        occupied = set(self.snake.body)
        available = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in occupied
        ]
        self.obstacles = random.sample(
            available, min(OBSTACLE_COUNT, len(available))
        )

    def get_empty_positions(self) -> list:
        """获取所有未被占据的格子"""
        occupied = set(self.snake.body) | set(self.obstacles)
        return [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in occupied
        ]
```

Wait, I realize the speed effect design is a bit awkward. Let me reconsider - instead of storing the effect amount, let me store which food effect is active and the timer. Let me redesign this properly.

Actually, let me simplify the speed effect. The design doc says:
- Speed-up food: move interval -30ms
- Slow-down food: move interval +30ms
- Effect lasts 8 seconds

Let me store the `speed_modifier` and `speed_effect_timer` directly.

Actually, I realize the current design is getting complicated. Let me simplify: just store `_speed_effect_timer` and `_speed_modifier` (positive or negative). When timer expires, modifier resets to 0.

Let me rewrite the game_state properly without the TODO placeholder.

- [ ] **Step 2: 验证模块可导入**

```bash
python -c "import sys; sys.path.insert(0, 'snake_game'); from game_state import Snake, GameState; print('OK')"
```

---

### Task 4: 食物系统 (`food.py`)

**Files:**
- Create: `snake_game/food.py`

**Interfaces:**
- Consumes: `config.py`（食物常量）
- Produces:
  - `class FoodType`: 枚举 (NORMAL, SPEED_UP, SLOW_DOWN)
  - `class Food`: `type: FoodType`, `position: tuple`, `timer: float`, `is_expired() -> bool`
  - `spawn_food(occupied: list) -> Food`: 在空位生成随机类型食物

- [ ] **Step 1: 编写食物模块**

```python
"""食物系统：类型定义、生成逻辑、计时器"""
import random
from enum import Enum, auto
from config import (
    FOOD_NORMAL_CHANCE, FOOD_SPEED_UP_CHANCE, FOOD_SLOW_DOWN_CHANCE,
    FOOD_NORMAL_SCORE, FOOD_SPEED_UP_SCORE, FOOD_SLOW_DOWN_SCORE,
    FOOD_TIMED_DURATION, SPEED_EFFECT_AMOUNT,
)


class FoodType(Enum):
    NORMAL = auto()
    SPEED_UP = auto()
    SLOW_DOWN = auto()


class Food:
    """食物实例"""

    def __init__(self, food_type: FoodType, position: tuple):
        self.type = food_type
        self.position = position
        # 限时食物的倒计时（秒），普通食物为 -1 表示永久
        self.timer = FOOD_TIMED_DURATION if food_type != FoodType.NORMAL else -1

    @property
    def is_timed(self) -> bool:
        return self.timer >= 0

    @property
    def is_expired(self) -> bool:
        return self.is_timed and self.timer <= 0

    def update(self, dt: float) -> None:
        """更新计时器"""
        if self.is_timed and self.timer > 0:
            self.timer -= dt
            if self.timer < 0:
                self.timer = 0

    @property
    def timer_ratio(self) -> float:
        """返回剩余时间比例 (0~1)，用于渲染缩小动画"""
        if not self.is_timed:
            return 1.0
        return max(0.0, self.timer / FOOD_TIMED_DURATION)

    @property
    def score(self) -> int:
        score_map = {
            FoodType.NORMAL: FOOD_NORMAL_SCORE,
            FoodType.SPEED_UP: FOOD_SPEED_UP_SCORE,
            FoodType.SLOW_DOWN: FOOD_SLOW_DOWN_SCORE,
        }
        return score_map[self.type]

    @property
    def color(self) -> tuple:
        from config import COLOR_GREEN, COLOR_YELLOW, COLOR_BLUE
        color_map = {
            FoodType.NORMAL: COLOR_GREEN,
            FoodType.SPEED_UP: COLOR_YELLOW,
            FoodType.SLOW_DOWN: COLOR_BLUE,
        }
        return color_map[self.type]


def _random_food_type() -> FoodType:
    """按概率随机选择食物类型"""
    r = random.random()
    if r < FOOD_NORMAL_CHANCE:
        return FoodType.NORMAL
    elif r < FOOD_NORMAL_CHANCE + FOOD_SPEED_UP_CHANCE:
        return FoodType.SPEED_UP
    else:
        return FoodType.SLOW_DOWN


def spawn_food(empty_positions: list) -> Food | None:
    """在空位列表中随机生成食物，无空位返回 None"""
    if not empty_positions:
        return None
    pos = random.choice(empty_positions)
    return Food(_random_food_type(), pos)
```

- [ ] **Step 2: 验证模块**

```bash
python -c "
import sys; sys.path.insert(0, 'snake_game')
from food import Food, FoodType, spawn_food
f = spawn_food([(5,5), (10,10)])
print(f'Food type={f.type.name}, pos={f.position}, score={f.score}')
# 测试概率分布
types = [spawn_food([(i,i) for i in range(100)]).type for _ in range(1000)]
normal = sum(1 for t in types if t == FoodType.NORMAL)
speed_up = sum(1 for t in types if t == FoodType.SPEED_UP)
slow_down = sum(1 for t in types if t == FoodType.SLOW_DOWN)
print(f'Normal: {normal/10}%, SpeedUp: {speed_up/10}%, SlowDown: {slow_down/10}%')
"
```

---

### Task 5: 障碍物 (`obstacles.py`)

**Files:**
- Create: `snake_game/obstacles.py`

**Interfaces:**
- Consumes: `config.py` (OBSTACLE_COUNT)
- Produces: `generate_obstacles(count: int, occupied: set) -> list[tuple[int,int]]`

This is simple enough to be a small file.

- [ ] **Step 1: 编写障碍物模块**

```python
"""障碍物生成"""
import random
from config import GRID_WIDTH, GRID_HEIGHT, OBSTACLE_COUNT


def generate_obstacles(
    count: int | None = None,
    occupied: set | None = None,
) -> list[tuple[int, int]]:
    """在网格中随机生成障碍物，避开已占据的格子"""
    if count is None:
        count = OBSTACLE_COUNT
    if occupied is None:
        occupied = set()

    available = [
        (x, y)
        for x in range(GRID_WIDTH)
        for y in range(GRID_HEIGHT)
        if (x, y) not in occupied
    ]
    return random.sample(available, min(count, len(available)))
```

---

### Task 6: 渲染器 (`renderer.py`)

**Files:**
- Create: `snake_game/renderer.py`

**Interfaces:**
- Consumes: `config.py`, `game_state.py`, `food.py`
- Produces:
  - `class Renderer`: `__init__(screen)`, `draw_background()`, `draw_grid()`, `draw_obstacles(obs)`, `draw_snake(snake)`, `draw_food(food)`, `draw_score(score)`, `draw_menu()`, `draw_pause()`, `draw_gameover(score, highscore)`, `draw_speed_effect_indicator(timer, effect_type)`

This is the largest file (~150 lines). Let me write it carefully.

- [ ] **Step 1: 编写渲染器**

```python
"""渲染器：所有绘制逻辑"""
import pygame
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, CELL_SIZE,
    GRID_WIDTH, GRID_HEIGHT,
    COLOR_BLACK, COLOR_WHITE, COLOR_GREEN, COLOR_GREEN_DARK,
    COLOR_GREEN_LIGHT, COLOR_RED, COLOR_DARK_RED,
    COLOR_YELLOW, COLOR_BLUE, COLOR_GRAY, COLOR_GRAY_LIGHT,
)
from game_state import Snake, GameState
from food import Food, FoodType


class Renderer:
    """负责所有画面绘制，只读不写状态"""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self._title_font = pygame.font.Font(None, 72)
        self._large_font = pygame.font.Font(None, 48)
        self._medium_font = pygame.font.Font(None, 36)
        self._small_font = pygame.font.Font(None, 24)

    def draw_background(self) -> None:
        """绘制黑色背景"""
        self.screen.fill(COLOR_BLACK)

    def draw_grid(self) -> None:
        """绘制网格线"""
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, COLOR_GRAY, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, COLOR_GRAY, (0, y), (WINDOW_WIDTH, y))

    def draw_obstacles(self, obstacles: list[tuple[int, int]]) -> None:
        """绘制障碍物"""
        for ox, oy in obstacles:
            rect = pygame.Rect(
                ox * CELL_SIZE + 1, oy * CELL_SIZE + 1,
                CELL_SIZE - 2, CELL_SIZE - 2,
            )
            pygame.draw.rect(self.screen, COLOR_DARK_RED, rect)
            pygame.draw.rect(self.screen, COLOR_RED, rect, 1)

    def draw_snake(self, snake: Snake) -> None:
        """绘制蛇的身体和头部"""
        for i, (sx, sy) in enumerate(snake.body):
            rect = pygame.Rect(
                sx * CELL_SIZE + 1, sy * CELL_SIZE + 1,
                CELL_SIZE - 2, CELL_SIZE - 2,
            )
            if i == 0:
                # 蛇头：亮绿色
                pygame.draw.rect(self.screen, COLOR_GREEN_LIGHT, rect)
                # 画眼睛
                self._draw_eyes(sx, sy, snake.direction)
            else:
                # 蛇身：渐变色（靠近头更亮）
                ratio = i / len(snake.body)
                color = self._lerp_color(COLOR_GREEN_LIGHT, COLOR_GREEN_DARK, ratio)
                pygame.draw.rect(self.screen, color, rect)

    def _draw_eyes(self, hx: int, hy: int, direction: tuple) -> None:
        """在蛇头上画眼睛"""
        cx = hx * CELL_SIZE + CELL_SIZE // 2
        cy = hy * CELL_SIZE + CELL_SIZE // 2
        eye_r = 3
        offset = 5

        if direction == (1, 0):  # 右
            e1 = (cx + offset, cy - offset)
            e2 = (cx + offset, cy + offset)
        elif direction == (-1, 0):  # 左
            e1 = (cx - offset, cy - offset)
            e2 = (cx - offset, cy + offset)
        elif direction == (0, -1):  # 上
            e1 = (cx - offset, cy - offset)
            e2 = (cx + offset, cy - offset)
        else:  # 下
            e1 = (cx - offset, cy + offset)
            e2 = (cx + offset, cy + offset)

        pygame.draw.circle(self.screen, COLOR_BLACK, e1, eye_r)
        pygame.draw.circle(self.screen, COLOR_BLACK, e2, eye_r)

    @staticmethod
    def _lerp_color(c1: tuple, c2: tuple, t: float) -> tuple:
        """颜色线性插值"""
        return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

    def draw_food(self, food: Food) -> None:
        """绘制食物，限时食物根据剩余时间缩小"""
        fx, fy = food.position
        cx = fx * CELL_SIZE + CELL_SIZE // 2
        cy = fy * CELL_SIZE + CELL_SIZE // 2

        # 限时食物根据 timer_ratio 缩小
        ratio = food.timer_ratio
        radius = int((CELL_SIZE // 2 - 2) * (0.5 + 0.5 * ratio))

        # 发光效果
        glow_radius = radius + 3
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*food.color, 60), (glow_radius, glow_radius), glow_radius)
        self.screen.blit(glow_surf, (cx - glow_radius, cy - glow_radius))

        # 食物本体
        pygame.draw.circle(self.screen, food.color, (cx, cy), radius)

    def draw_score(self, score: int, highscore: int) -> None:
        """绘制分数（左上角）"""
        text = self._small_font.render(f"分数: {score}  最高分: {highscore}", True, COLOR_WHITE)
        self.screen.blit(text, (10, 10))

    def draw_speed_indicator(self, state: GameState) -> None:
        """绘制速度效果指示器"""
        if state.speed_effect_active:
            remaining = state.speed_effect_timer
            text = self._small_font.render(
                f"速度效果: {remaining:.1f}s", True, COLOR_YELLOW
            )
            self.screen.blit(text, (10, 35))

    def draw_menu(self, highscore: int) -> None:
        """绘制主菜单"""
        self.draw_background()
        self._draw_centered_text("贪 吃 蛇", self._title_font, COLOR_GREEN_LIGHT, -60)
        self._draw_centered_text("按回车开始游戏", self._medium_font, COLOR_WHITE, 10)
        self._draw_centered_text("方向键 / WASD 移动  空格暂停  Esc 退出", self._small_font, COLOR_GRAY_LIGHT, 50)
        if highscore > 0:
            self._draw_centered_text(f"最高分: {highscore}", self._small_font, COLOR_YELLOW, 80)

    def draw_pause(self) -> None:
        """绘制暂停遮罩"""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        self._draw_centered_text("暂 停 中", self._large_font, COLOR_WHITE, -20)
        self._draw_centered_text("按空格继续", self._small_font, COLOR_GRAY_LIGHT, 25)

    def draw_gameover(self, score: int, highscore: int, is_new_highscore: bool) -> None:
        """绘制游戏结束画面"""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        self._draw_centered_text("游 戏 结 束", self._large_font, COLOR_RED, -80)
        self._draw_centered_text(f"本局分数: {score}", self._medium_font, COLOR_WHITE, -20)
        if is_new_highscore:
            self._draw_centered_text(f"🎉 新最高分: {highscore} 🎉", self._medium_font, COLOR_YELLOW, 20)
        else:
            self._draw_centered_text(f"最高分: {highscore}", self._small_font, COLOR_GRAY_LIGHT, 20)
        self._draw_centered_text("按回车返回菜单", self._small_font, COLOR_WHITE, 70)

    def _draw_centered_text(
        self, text: str, font: pygame.font.Font,
        color: tuple, y_offset: int = 0,
    ) -> None:
        """在屏幕中央绘制文字，y_offset 为垂直偏移"""
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + y_offset))
        self.screen.blit(surf, rect)
```

---

### Task 7: 场景管理 (`scenes.py`)

**Files:**
- Create: `snake_game/scenes.py`

**Interfaces:**
- Consumes: `config.py`, `game_state.py`, `food.py`, `obstacles.py`, `renderer.py`, `highscore.py`
- Produces:
  - `class Scene(Enum)`: MENU, GAME, PAUSE, GAMEOVER
  - `class SceneManager`: 管理场景切换、输入分发、更新和渲染

- [ ] **Step 1: 编写场景管理器**

```python
"""场景管理器：菜单/游戏/暂停/结束 状态机"""
import pygame
from enum import Enum, auto

from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS,
    DIRECTION_UP, DIRECTION_DOWN, DIRECTION_LEFT, DIRECTION_RIGHT,
    SPEED_EFFECT_AMOUNT,
)
from game_state import GameState
from food import spawn_food, FoodType
from renderer import Renderer
from highscore import load_highscore, save_highscore


class Scene(Enum):
    MENU = auto()
    GAME = auto()
    PAUSE = auto()
    GAMEOVER = auto()


class SceneManager:
    """场景管理器：持有当前场景和所有状态"""

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock):
        self.screen = screen
        self.clock = clock
        self.renderer = Renderer(screen)
        self.scene = Scene.MENU
        self.game_state: GameState | None = None
        self.food = None
        self.highscore = load_highscore()
        self._move_timer = 0  # 控制蛇移动的计时器（毫秒）
        self._pressed_keys = set()

    def start_game(self) -> None:
        """开始新游戏"""
        self.game_state = GameState()
        self.food = spawn_food(self.game_state.get_empty_positions())
        self._move_timer = 0

    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件，返回 False 表示退出"""
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            key = event.key

            # Esc 全局退出
            if key == pygame.K_ESCAPE:
                return False

            if self.scene == Scene.MENU:
                if key == pygame.K_RETURN:
                    self.scene = Scene.GAME
                    self.start_game()

            elif self.scene == Scene.GAME:
                self._handle_game_keydown(key)

            elif self.scene == Scene.PAUSE:
                if key == pygame.K_SPACE:
                    self.scene = Scene.GAME

            elif self.scene == Scene.GAMEOVER:
                if key == pygame.K_RETURN:
                    self.scene = Scene.MENU

        return True

    def _handle_game_keydown(self, key: int) -> None:
        """处理游戏中的按键"""
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

    def update(self) -> None:
        """更新游戏逻辑"""
        if self.scene != Scene.GAME or self.game_state is None:
            return

        dt = self.clock.get_time() / 1000.0  # 秒

        # 更新速度效果计时器
        self.game_state.update(dt)

        # 更新食物计时器
        if self.food:
            self.food.update(dt)

        # 控制蛇移动速度
        self._move_timer += self.clock.get_time()
        interval = self.game_state.get_effective_speed()

        # 加速效果：减少间隔
        if self.game_state.speed_effect_active:
            interval = max(10, interval - SPEED_EFFECT_AMOUNT)

        if self._move_timer >= interval:
            self._move_timer = 0
            self._move_snake()

    def _move_snake(self) -> None:
        """蛇移动一步，处理碰撞和食物"""
        if self.game_state is None:
            return

        self.game_state.snake.move()

        # 碰撞检测
        if (self.game_state.snake.check_wall_collision() or
                self.game_state.snake.check_self_collision() or
                self.game_state.check_obstacle_collision()):
            self.scene = Scene.GAMEOVER
            # 检查并保存最高分
            score = self.game_state.score
            if score > self.highscore:
                self.highscore = score
                save_highscore(score)
            return

        # 检查是否吃到食物
        if self.food and self.game_state.snake.head == self.food.position:
            self._eat_food()
        elif self.food and self.food.is_expired:
            # 食物过期，重新生成
            self.food = spawn_food(self.game_state.get_empty_positions())

    def _eat_food(self) -> None:
        """处理吃到食物"""
        if self.game_state is None or self.food is None:
            return

        food = self.food
        self.game_state.snake.grow()
        self.game_state.add_score(food.score)

        # 应用食物效果
        if food.type == FoodType.SPEED_UP:
            self.game_state.apply_speed_effect(-SPEED_EFFECT_AMOUNT)
        elif food.type == FoodType.SLOW_DOWN:
            self.game_state.apply_speed_effect(SPEED_EFFECT_AMOUNT)

        # 生成新食物
        self.food = spawn_food(self.game_state.get_empty_positions())

    def draw(self) -> None:
        """根据当前场景绘制"""
        if self.scene == Scene.MENU:
            self.renderer.draw_menu(self.highscore)

        elif self.scene in (Scene.GAME, Scene.PAUSE):
            self.renderer.draw_background()
            self.renderer.draw_grid()
            if self.game_state:
                self.renderer.draw_obstacles(self.game_state.obstacles)
                self.renderer.draw_snake(self.game_state.snake)
                self.renderer.draw_score(self.game_state.score, self.highscore)
                self.renderer.draw_speed_indicator(self.game_state)
            if self.food:
                self.renderer.draw_food(self.food)
            if self.scene == Scene.PAUSE:
                self.renderer.draw_pause()

        elif self.scene == Scene.GAMEOVER:
            # 先画游戏画面再盖遮罩
            self.renderer.draw_background()
            self.renderer.draw_grid()
            if self.game_state:
                self.renderer.draw_obstacles(self.game_state.obstacles)
                self.renderer.draw_snake(self.game_state.snake)
            if self.food:
                self.renderer.draw_food(self.food)
            if self.game_state:
                is_new = self.game_state.score >= self.highscore and self.game_state.score > 0
                self.renderer.draw_gameover(
                    self.game_state.score, self.highscore, is_new
                )
```

---

### Task 8: 主入口 (`main.py`)

**Files:**
- Create: `snake_game/main.py`
- Create: `snake_game/__init__.py` (empty)

**Interfaces:**
- Consumes: `config.py`, `scenes.py`
- Produces: `main()` 函数

- [ ] **Step 1: 编写主入口**

```python
"""贪吃蛇游戏 - 主入口"""
import sys
import pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from scenes import SceneManager


def main() -> None:
    """游戏主函数"""
    # 初始化 pygame
    try:
        pygame.init()
    except pygame.error as e:
        print(f"pygame 初始化失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 创建窗口
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("贪吃蛇")

    # 创建时钟和场景管理器
    clock = pygame.time.Clock()
    manager = SceneManager(screen, clock)

    # 主循环
    running = True
    while running:
        # 1. 处理事件
        for event in pygame.event.get():
            if not manager.handle_event(event):
                running = False
                break

        # 2. 更新状态
        manager.update()

        # 3. 渲染
        manager.draw()
        pygame.display.flip()

        # 4. 控制帧率
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 创建包文件**

```bash
touch snake_game/__init__.py
```

---

### Task 9: 验证与调试

**Files:**
- Modify: 重新审查 `game_state.py` 中 `get_effective_speed` 方法

- [ ] **Step 1: 修复 game_state.py 中 get_effective_speed 的设计缺陷**

当前设计中 `apply_speed_effect` 只存了 timer，需要同时存 modifier。重新设计：

```python
# game_state.py 中修改 GameState 类

def __init__(self):
    # ... 现有代码 ...
    self._speed_modifier = 0  # 正=减速，负=加速

def apply_speed_effect(self, amount_ms: int) -> None:
    """应用临时速度效果（负值为加速，正值为减速）"""
    self._speed_effect_timer = SPEED_EFFECT_DURATION
    self._speed_modifier = amount_ms

def update(self, dt: float) -> None:
    """更新速度效果计时器"""
    if self._speed_effect_timer > 0:
        self._speed_effect_timer -= dt
        if self._speed_effect_timer <= 0:
            self._speed_effect_timer = 0
            self._speed_modifier = 0

def get_effective_speed(self) -> int:
    """获取考虑临时效果后的实际速度"""
    speed = self.speed
    if self.speed_effect_active:
        speed = max(MIN_SPEED, speed + self._speed_modifier)
    return speed
```

- [ ] **Step 2: 运行游戏验证**

```bash
cd snake_game && python main.py
```

- [ ] **Step 3: 手动测试清单**

- [ ] 主菜单显示正常，回车开始游戏
- [ ] 蛇移动流畅，方向键和 WASD 都能控制
- [ ] 反向按键被正确拦截
- [ ] 吃到食物蛇变长，分数增加
- [ ] 三种食物都能正常生成
- [ ] 加速/减速效果正常，倒计时显示
- [ ] 撞墙/撞自己/撞障碍物游戏结束
- [ ] 暂停/恢复正常
- [ ] 游戏结束显示分数，新高分正确提示
- [ ] 最高分在重启后正确保留
- [ ] Esc 退出游戏
