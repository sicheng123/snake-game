"""食物系统：类型定义、生成逻辑、计时器"""
import random
from enum import Enum, auto
from config import (
    FOOD_NORMAL_CHANCE, FOOD_SPEED_UP_CHANCE, FOOD_SLOW_DOWN_CHANCE,
    FOOD_NORMAL_SCORE, FOOD_SPEED_UP_SCORE, FOOD_SLOW_DOWN_SCORE,
    FOOD_TIMED_DURATION,
    COLOR_GREEN, COLOR_YELLOW, COLOR_BLUE,
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


def spawn_food(empty_positions: list) -> "Food | None":
    """在空位列表中随机生成食物，无空位返回 None"""
    if not empty_positions:
        return None
    pos = random.choice(empty_positions)
    return Food(_random_food_type(), pos)
