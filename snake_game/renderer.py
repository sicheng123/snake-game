"""渲染器：所有绘制逻辑——只读不写游戏状态"""
import pygame
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, CELL_SIZE,
    COLOR_BLACK, COLOR_WHITE, COLOR_GREEN, COLOR_GREEN_DARK,
    COLOR_GREEN_LIGHT, COLOR_RED, COLOR_DARK_RED,
    COLOR_YELLOW, COLOR_GRAY, COLOR_GRAY_LIGHT,
    DPAD_UP, DPAD_DOWN, DPAD_LEFT, DPAD_RIGHT,
    TOUCH_PAUSE_BTN, TOUCH_CONFIRM_BTN,
    TOUCH_DIFF_LEFT_BTN, TOUCH_DIFF_RIGHT_BTN,
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

# Android 系统字体文件路径（pygame.font.Font 直接加载）
_ANDROID_CJK_PATHS = [
    "/system/fonts/DroidSansFallback.ttf",
    "/system/fonts/NotoSansCJK-Regular.ttc",
    "/system/fonts/NotoSansSC-Regular.otf",
]


def _find_cjk_font_path() -> str | None:
    """查找可用的中日韩字体文件路径"""
    import os as _os
    for path in _ANDROID_CJK_PATHS:
        if _os.path.isfile(path):
            return path
    return None


def _find_cjk_font_name() -> str | None:
    """在系统已安装字体中查找第一个可用的中文字体"""
    available = set(pygame.font.get_fonts())
    for name in _CJK_FONT_CANDIDATES:
        if name.lower() in available:
            return name
        normalized = name.lower().replace(" ", "")
        for f in available:
            if normalized == f.replace(" ", ""):
                return f
    return None


def _create_font(size: int) -> pygame.font.Font:
    """创建指定大小的字体，优先中文字体 → Android 系统路径 → 默认字体"""
    # 1. 尝试 SysFont（桌面平台）
    cjk_name = _find_cjk_font_name()
    if cjk_name:
        return pygame.font.SysFont(cjk_name, size)
    # 2. 尝试 Android 系统字体文件
    cjk_path = _find_cjk_font_path()
    if cjk_path:
        return pygame.font.Font(cjk_path, size)
    # 3. 回退到默认字体（中文会显示为方框）
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
        self.screen.blit(text, (10, 60))

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

    # ── 触屏控件绘制 ───────────────────────────────────

    def _draw_touch_btn_rect(self, rect: tuple[int, int, int, int], alpha: int = 100) -> None:
        """绘制半透明按钮背景"""
        x, y, w, h = rect
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((255, 255, 255, alpha))
        # 圆角边框
        pygame.draw.rect(surf, (255, 255, 255, 180), surf.get_rect(), 2, border_radius=8)
        self.screen.blit(surf, (x, y))

    def _draw_arrow(self, cx: int, cy: int, direction: str, color: tuple, size: int = 12) -> None:
        """在 (cx, cy) 中心绘制三角箭头"""
        half = size // 2
        if direction == "up":
            pts = [(cx, cy - half), (cx - half, cy + half), (cx + half, cy + half)]
        elif direction == "down":
            pts = [(cx, cy + half), (cx - half, cy - half), (cx + half, cy - half)]
        elif direction == "left":
            pts = [(cx - half, cy), (cx + half, cy - half), (cx + half, cy + half)]
        else:  # right
            pts = [(cx + half, cy), (cx - half, cy - half), (cx - half, cy + half)]
        pygame.draw.polygon(self.screen, color, pts)

    def draw_touch_controls_menu(self) -> None:
        """菜单场景触屏控件：开始按钮 + 难度切换箭头"""
        # 开始按钮
        x, y, w, h = TOUCH_CONFIRM_BTN
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((0, 200, 0, 120))
        pygame.draw.rect(surf, COLOR_GREEN_LIGHT, surf.get_rect(), 2, border_radius=10)
        self.screen.blit(surf, (x, y))
        txt = self._small_font.render("开始", True, COLOR_WHITE)
        tr = txt.get_rect(center=(x + w // 2, y + h // 2))
        self.screen.blit(txt, tr)

        # 难度左箭头
        lx, ly, lw, lh = TOUCH_DIFF_LEFT_BTN
        self._draw_touch_btn_rect((lx, ly, lw, lh), 80)
        self._draw_arrow(lx + lw // 2, ly + lh // 2, "left", COLOR_WHITE, 14)

        # 难度右箭头
        rx, ry, rw, rh = TOUCH_DIFF_RIGHT_BTN
        self._draw_touch_btn_rect((rx, ry, rw, rh), 80)
        self._draw_arrow(rx + rw // 2, ry + rh // 2, "right", COLOR_WHITE, 14)

    def draw_touch_controls_game(self) -> None:
        """游戏场景触屏控件：D-pad + 暂停按钮"""
        # D-pad 四个方向键
        for rect_tuple, arrow_dir in [
            (DPAD_UP, "up"), (DPAD_DOWN, "down"),
            (DPAD_LEFT, "left"), (DPAD_RIGHT, "right"),
        ]:
            self._draw_touch_btn_rect(rect_tuple, 70)
            x, y, w, h = rect_tuple
            self._draw_arrow(x + w // 2, y + h // 2, arrow_dir, COLOR_WHITE, 14)

        # 暂停按钮（右上角）
        px, py, pw, ph = TOUCH_PAUSE_BTN
        self._draw_touch_btn_rect((px, py, pw, ph), 100)
        # 双竖线暂停图标
        bar_w = 4
        gap = 6
        for offset in (-gap, gap):
            bx = px + pw // 2 + offset - bar_w // 2
            pygame.draw.rect(self.screen, COLOR_WHITE,
                             (bx, py + ph // 2 - 7, bar_w, 14), border_radius=2)

    def draw_touch_controls_gameover(self) -> None:
        """游戏结束场景触屏控件：返回菜单按钮"""
        x, y, w, h = TOUCH_CONFIRM_BTN
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((200, 50, 50, 140))
        pygame.draw.rect(surf, COLOR_RED, surf.get_rect(), 2, border_radius=10)
        self.screen.blit(surf, (x, y))
        txt = self._small_font.render("返回菜单", True, COLOR_WHITE)
        tr = txt.get_rect(center=(x + w // 2, y + h // 2))
        self.screen.blit(txt, tr)
