"""游戏常量配置"""
from enum import Enum

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

# 蛇的设置
SNAKE_START_LENGTH = 3
SNAKE_START_X = GRID_WIDTH // 2
SNAKE_START_Y = GRID_HEIGHT // 2
SNAKE_START_DIRECTION = (1, 0)  # 初始向右

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

# ── 触屏控件布局（x, y, w, h 像素坐标） ──
DPAD_UP    = (695, 400, 50, 50)
DPAD_DOWN  = (695, 500, 50, 50)
DPAD_LEFT  = (645, 450, 50, 50)
DPAD_RIGHT = (745, 450, 50, 50)
TOUCH_PAUSE_BTN    = (WINDOW_WIDTH - 50, 8, 40, 30)
TOUCH_CONFIRM_BTN  = (WINDOW_WIDTH // 2 - 80, WINDOW_HEIGHT // 2 - 25, 160, 50)
TOUCH_DIFF_LEFT_BTN  = (WINDOW_WIDTH // 2 - 140, WINDOW_HEIGHT // 2 - 35, 50, 50)
TOUCH_DIFF_RIGHT_BTN = (WINDOW_WIDTH // 2 + 90, WINDOW_HEIGHT // 2 - 35, 50, 50)
# 滑动判定阈值（像素）
SWIPE_THRESHOLD = 35
