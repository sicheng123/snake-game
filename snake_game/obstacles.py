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
