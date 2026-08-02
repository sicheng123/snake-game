"""渲染器：所有绘制逻辑——只读不写游戏状态"""
import pygame
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, CELL_SIZE,
    COLOR_BLACK, COLOR_WHITE, COLOR_GREEN, COLOR_GREEN_DARK,
    COLOR_GREEN_LIGHT, COLOR_RED, COLOR_DARK_RED,
    COLOR_YELLOW, COLOR_GRAY, COLOR_GRAY_LIGHT,
    DifficultyLevel, DIFFICULTY_COLORS,
)
from game_state import Snake, GameState
from food import Food


# ── 跨平台中文字体加载 ──

# 各平台常见中文字体，按优先级排列
_CJK_FONT_CANDIDATES = [
    # Linux
    "Noto Sans CJK SC",
    "WenQuanYi Micro Hei",
    "Noto Sans SC",
    "Source Han Sans SC",
    "WenQuanYi Zen Hei",
    "Droid Sans Fallback",
    # Windows
    "Microsoft YaHei",
    "SimHei",
    "SimSun",
    "FangSong",
    "KaiTi",
    # macOS
    "PingFang SC",
    "Heiti SC",
    "STHeiti",
    "Apple LiGothic",
]


def _find_cjk_font_name() -> str | None:
    """在系统已安装字体中查找第一个可用的中文字体"""
    available = set(pygame.font.get_fonts())
    for name in _CJK_FONT_CANDIDATES:
        # pygame 的字体名是全小写
        if name.lower() in available:
            return name
        # 某些平台可能用下划线或空格
        normalized = name.lower().replace(" ", "")
        for f in available:
            if normalized == f.replace(" ", ""):
                return f
    return None


def _create_font(size: int) -> pygame.font.Font:
    """创建指定大小的字体，优先使用中文字体，失败则回退到默认字体"""
    cjk_name = _find_cjk_font_name()
    if cjk_name:
        return pygame.font.SysFont(cjk_name, size)
    # 找不到中文字体，用默认字体（中文会显示为方框）
    return pygame.font.Font(None, size)


class Renderer:
    """负责所有画面绘制，只读不写状态"""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self._title_font = _create_font(72)
        self._large_font = _create_font(48)
        self._medium_font = _create_font(36)
        self._small_font = _create_font(24)

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
        """绘制障碍物（暗红色方块）"""
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
                self._draw_eyes(sx, sy, snake.direction)
            else:
                # 蛇身：渐变色（靠近头更亮，靠近尾更暗）
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
        """颜色线性插值，t=0 接近 c1，t=1 接近 c2"""
        return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

    def draw_food(self, food: Food) -> None:
        """绘制食物，限时食物根据剩余时间缩小"""
        fx, fy = food.position
        cx = fx * CELL_SIZE + CELL_SIZE // 2
        cy = fy * CELL_SIZE + CELL_SIZE // 2

        # 限时食物根据 timer_ratio 缩小（0.5 ~ 1.0 倍）
        ratio = food.timer_ratio
        radius = int((CELL_SIZE // 2 - 2) * (0.5 + 0.5 * ratio))

        # 发光效果（半透明光晕）
        glow_radius = radius + 3
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*food.color, 60), (glow_radius, glow_radius), glow_radius)
        self.screen.blit(glow_surf, (cx - glow_radius, cy - glow_radius))

        # 食物本体
        pygame.draw.circle(self.screen, food.color, (cx, cy), radius)

    def draw_score(self, score: int, highscore: int) -> None:
        """绘制分数（左上角）"""
        text = self._small_font.render(
            f"分数: {score}  最高分: {highscore}", True, COLOR_WHITE
        )
        self.screen.blit(text, (10, 10))

    def draw_speed_indicator(self, state: GameState) -> None:
        """绘制速度效果指示器"""
        if state.speed_effect_active:
            remaining = state.speed_effect_timer
            text = self._small_font.render(
                f"速度效果: {remaining:.1f}s", True, COLOR_YELLOW
            )
            self.screen.blit(text, (10, 35))

    def draw_difficulty_indicator(self, difficulty: DifficultyLevel, highlight_timer: float = 0.0) -> None:
        """绘制难度指示器（左上角，分数下方）"""
        color = DIFFICULTY_COLORS[difficulty]
        # 高亮效果：timer > 0 时用白色
        if highlight_timer > 0:
            color = COLOR_WHITE
        text = self._small_font.render(f"难度: {difficulty.value}", True, color)
        self.screen.blit(text, (10, 35))

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

    def draw_pause(self) -> None:
        """绘制暂停遮罩"""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        self._draw_centered_text("暂  停  中", self._large_font, COLOR_WHITE, -20)
        self._draw_centered_text("按空格继续", self._small_font, COLOR_GRAY_LIGHT, 25)

    def draw_gameover(self, score: int, highscore: int, is_new_highscore: bool) -> None:
        """绘制游戏结束画面"""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        self._draw_centered_text("游 戏 结 束", self._large_font, COLOR_RED, -80)
        self._draw_centered_text(f"本局分数: {score}", self._medium_font, COLOR_WHITE, -20)
        if is_new_highscore:
            self._draw_centered_text(
                f"新最高分: {highscore}", self._medium_font, COLOR_YELLOW, 25
            )
        else:
            self._draw_centered_text(
                f"最高分: {highscore}", self._small_font, COLOR_GRAY_LIGHT, 25
            )
        self._draw_centered_text("按回车返回菜单", self._small_font, COLOR_WHITE, 70)

    def _draw_centered_text(
        self, text: str, font: pygame.font.Font,
        color: tuple, y_offset: int = 0,
    ) -> None:
        """在屏幕中央绘制文字，y_offset 为垂直偏移（像素）"""
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + y_offset))
        self.screen.blit(surf, rect)
