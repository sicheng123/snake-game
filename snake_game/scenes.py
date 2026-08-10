"""场景管理器：菜单/游戏/暂停/结束 四场景状态机"""
import pygame
from enum import Enum, auto

from config import (
    DIRECTION_UP, DIRECTION_DOWN, DIRECTION_LEFT, DIRECTION_RIGHT,
    SPEED_EFFECT_AMOUNT, FOODS_PER_LEVEL,
    WINDOW_WIDTH, WINDOW_HEIGHT,
    DPAD_UP, DPAD_DOWN, DPAD_LEFT, DPAD_RIGHT,
    TOUCH_PAUSE_BTN, TOUCH_CONFIRM_BTN,
    TOUCH_DIFF_LEFT_BTN, TOUCH_DIFF_RIGHT_BTN,
    SWIPE_THRESHOLD,
    DifficultyLevel, DIFFICULTY_ORDER,
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


# ── 触屏按钮区域（基于 config 坐标创建的 pygame.Rect） ──

_D_PAD_BTNS = {
    DIRECTION_UP:    pygame.Rect(DPAD_UP),
    DIRECTION_DOWN:  pygame.Rect(DPAD_DOWN),
    DIRECTION_LEFT:  pygame.Rect(DPAD_LEFT),
    DIRECTION_RIGHT: pygame.Rect(DPAD_RIGHT),
}

_PAUSE_BTN      = pygame.Rect(TOUCH_PAUSE_BTN)
_CONFIRM_BTN     = pygame.Rect(TOUCH_CONFIRM_BTN)
_DIFF_LEFT_BTN  = pygame.Rect(TOUCH_DIFF_LEFT_BTN)
_DIFF_RIGHT_BTN = pygame.Rect(TOUCH_DIFF_RIGHT_BTN)


class SceneManager:
    """场景管理器：持有当前场景和所有游戏状态"""

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock):
        self.screen = screen
        self.clock = clock
        self.renderer = Renderer(screen)
        self.scene = Scene.MENU
        self.game_state: GameState | None = None
        self.food = None
        self.highscore = load_highscore()
        self.menu_difficulty = DifficultyLevel.MEDIUM
        self.difficulty_highlight_timer = 0.0
        self._move_timer = 0  # 控制蛇移动的累计时间（毫秒）
        # 触屏状态
        self._pointer_start: tuple[int, int] | None = None
        self.is_mobile = False  # 检测到触屏事件后设为 True，渲染器据此绘制控件

    # ── 场景切换 ──────────────────────────────────────

    def start_game(self) -> None:
        """开始新一局游戏"""
        self.game_state = GameState()
        self.game_state.set_difficulty(self.menu_difficulty)
        self.food = spawn_food(self.game_state.get_empty_positions())
        self._move_timer = 0
        self.difficulty_highlight_timer = 0.0

    # ── 事件处理 ──────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> bool:
        """统一事件分发，返回 False 表示退出游戏"""
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            return self._dispatch_key(event.key)

        # 触屏 / 鼠标事件
        if event.type == pygame.FINGERDOWN:
            self.is_mobile = True
            self._on_pointer_down(event.x * WINDOW_WIDTH, event.y * WINDOW_HEIGHT)
        elif event.type == pygame.FINGERUP:
            self._on_pointer_up(event.x * WINDOW_WIDTH, event.y * WINDOW_HEIGHT)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._on_pointer_down(*event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            self._on_pointer_up(*event.pos)

        return True

    def _dispatch_key(self, key: int) -> bool:
        """键盘事件分发"""
        if key == pygame.K_ESCAPE:
            return False

        if self.scene == Scene.MENU:
            self._handle_menu_key(key)
        elif self.scene == Scene.GAME:
            self._handle_game_key(key)
        elif self.scene == Scene.PAUSE:
            self._handle_pause_key(key)
        elif self.scene == Scene.GAMEOVER:
            self._handle_gameover_key(key)
        return True

    # ── 触屏 / 鼠标事件 ──────────────────────────────

    def _on_pointer_down(self, x: float, y: float) -> None:
        self._pointer_start = (int(x), int(y))

    def _on_pointer_up(self, x: float, y: float) -> None:
        if self._pointer_start is None:
            return
        start = self._pointer_start
        self._pointer_start = None
        end_x, end_y = int(x), int(y)
        dx = end_x - start[0]
        dy = end_y - start[1]

        # 判断滑动 vs 点击
        if max(abs(dx), abs(dy)) >= SWIPE_THRESHOLD:
            self._handle_swipe(dx, dy)
        else:
            self._handle_tap(end_x, end_y)

    def _handle_swipe(self, dx: int, dy: int) -> None:
        """滑动 → 在游戏场景中改变方向"""
        if self.scene != Scene.GAME or self.game_state is None:
            return
        if abs(dx) > abs(dy):
            new_dir = DIRECTION_LEFT if dx < 0 else DIRECTION_RIGHT
        else:
            new_dir = DIRECTION_UP if dy < 0 else DIRECTION_DOWN
        self.game_state.snake.set_direction(new_dir)

    def _handle_tap(self, x: int, y: int) -> None:
        """点击 → 根据场景和按钮区域分发"""
        pos = (x, y)

        # 暂停按钮（全局，游戏/暂停场景）
        if self.scene in (Scene.GAME, Scene.PAUSE) and _PAUSE_BTN.collidepoint(pos):
            if self.scene == Scene.GAME:
                self.scene = Scene.PAUSE
            else:
                self.scene = Scene.GAME
            return

        # D-pad 方向按钮（游戏场景）
        if self.scene == Scene.GAME and self.game_state is not None:
            for direction, rect in _D_PAD_BTNS.items():
                if rect.collidepoint(pos):
                    self.game_state.snake.set_direction(direction)
                    return

        # 菜单场景
        if self.scene == Scene.MENU:
            if _CONFIRM_BTN.collidepoint(pos):
                self.scene = Scene.GAME
                self.start_game()
            elif _DIFF_LEFT_BTN.collidepoint(pos):
                self._cycle_menu_difficulty(-1)
            elif _DIFF_RIGHT_BTN.collidepoint(pos):
                self._cycle_menu_difficulty(1)

        # 游戏结束场景
        elif self.scene == Scene.GAMEOVER:
            if _CONFIRM_BTN.collidepoint(pos):
                self.scene = Scene.MENU

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

    def _handle_pause_key(self, key: int) -> None:
        if key == pygame.K_SPACE:
            self.scene = Scene.GAME

    def _handle_gameover_key(self, key: int) -> None:
        if key == pygame.K_RETURN:
            self.scene = Scene.MENU

    # ── 状态更新 ──────────────────────────────────────

    def update(self) -> None:
        """更新游戏逻辑（仅在 GAME 场景下）"""
        if self.scene != Scene.GAME or self.game_state is None:
            return

        # delta time，用于食物和速度效果的倒计时
        dt = self.clock.get_time() / 1000.0

        # 更新速度效果计时器
        self.game_state.update(dt)

        # 递减难度高亮计时器
        if self.difficulty_highlight_timer > 0:
            self.difficulty_highlight_timer -= dt
            if self.difficulty_highlight_timer < 0:
                self.difficulty_highlight_timer = 0

        # 更新食物计时器
        if self.food:
            self.food.update(dt)

        # 累积时间，到了间隔就移动蛇一步
        self._move_timer += self.clock.get_time()
        interval = self.game_state.get_effective_speed()

        if self._move_timer >= interval:
            self._move_timer = 0
            self._move_snake()

    def _move_snake(self) -> None:
        """蛇移动一步：碰撞检测 + 食物检测"""
        if self.game_state is None:
            return

        self.game_state.snake.move()

        # 碰撞检测（任一触发即游戏结束）
        if (self.game_state.snake.check_wall_collision() or
                self.game_state.snake.check_self_collision() or
                self.game_state.check_obstacle_collision()):
            self.scene = Scene.GAMEOVER
            score = self.game_state.score
            if score > self.highscore:
                self.highscore = score
                save_highscore(score)
            return

        # 食物过期 → 重新生成
        if self.food and self.food.is_expired:
            if self.game_state:
                self.food = spawn_food(self.game_state.get_empty_positions())

        # 吃到食物
        if self.food and self.game_state.snake.head == self.food.position:
            self._eat_food()

    def _eat_food(self) -> None:
        """处理吃到食物的逻辑"""
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

    # ── 渲染分发 ──────────────────────────────────────

    def draw(self) -> None:
        """根据当前场景绘制画面"""
        if self.scene == Scene.MENU:
            self.renderer.draw_menu(self.highscore, self.menu_difficulty)
            if self.is_mobile:
                self.renderer.draw_touch_controls_menu()

        elif self.scene in (Scene.GAME, Scene.PAUSE):
            self._draw_game_scene()
            if self.scene == Scene.PAUSE:
                self.renderer.draw_pause()
            if self.is_mobile:
                self.renderer.draw_touch_controls_game()

        elif self.scene == Scene.GAMEOVER:
            self._draw_game_scene()
            if self.game_state:
                is_new = (
                    self.game_state.score >= self.highscore
                    and self.game_state.score > 0
                )
                self.renderer.draw_gameover(
                    self.game_state.score, self.highscore, is_new
                )
            if self.is_mobile:
                self.renderer.draw_touch_controls_gameover()

    def _draw_game_scene(self) -> None:
        """绘制游戏场景（背景+网格+蛇+食物+障碍物+UI）"""
        self.renderer.draw_background()
        self.renderer.draw_grid()
        if self.game_state:
            self.renderer.draw_obstacles(self.game_state.obstacles)
            self.renderer.draw_snake(self.game_state.snake)
            self.renderer.draw_score(self.game_state.score, self.highscore)
            self.renderer.draw_speed_indicator(self.game_state)
            self.renderer.draw_difficulty_indicator(
                self.game_state.difficulty,
                self.difficulty_highlight_timer
            )
        if self.food:
            self.renderer.draw_food(self.food)
