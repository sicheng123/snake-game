"""游戏核心状态：蛇的移动、碰撞检测、计分"""
import random
from config import (
    GRID_WIDTH, GRID_HEIGHT,
    SNAKE_START_X, SNAKE_START_Y, SNAKE_START_LENGTH,
    SNAKE_START_DIRECTION, OPPOSITE_DIRECTIONS,
    FOODS_PER_LEVEL, SPEED_EFFECT_DURATION,
    OBSTACLE_COUNT,
    DifficultyLevel, DIFFICULTY_CONFIG,
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
        self.difficulty = DifficultyLevel.MEDIUM
        self.obstacles: list[tuple[int, int]] = []
        self._speed_effect_timer = 0.0
        self._speed_modifier = 0  # 正=减速，负=加速
        self._generate_obstacles()

    @property
    def speed(self) -> int:
        """当前蛇的基础移动间隔（毫秒），取决于难度和等级"""
        cfg = DIFFICULTY_CONFIG[self.difficulty]
        level = self.foods_eaten // FOODS_PER_LEVEL
        return max(cfg["min_speed"], cfg["base_speed"] - level * cfg["speed_increment"])

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
        """获取考虑临时效果后的实际移动间隔（毫秒）"""
        cfg = DIFFICULTY_CONFIG[self.difficulty]
        speed = self.speed
        if self.speed_effect_active:
            speed = max(cfg["min_speed"], speed + self._speed_modifier)
        return speed

    def set_difficulty(self, difficulty: DifficultyLevel) -> None:
        """设置难度等级"""
        self.difficulty = difficulty

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

    def get_empty_positions(self) -> list[tuple[int, int]]:
        """获取所有未被占据的格子（蛇身 + 障碍物之外）"""
        occupied = set(self.snake.body) | set(self.obstacles)
        return [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in occupied
        ]
