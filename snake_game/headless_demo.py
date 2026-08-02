"""无头模式演示脚本 — 自动运行游戏并保存各场景截图"""
import os
# 不强制 dummy driver，由环境变量 DISPLAY 决定

import pygame
import pygame.event
from PIL import Image

from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from scenes import SceneManager, Scene


def save_frame(screen: pygame.Surface, filename: str) -> None:
    """将 pygame surface 保存为 PNG"""
    raw = pygame.image.tobytes(screen, 'RGB')
    img = Image.frombytes('RGB', (WINDOW_WIDTH, WINDOW_HEIGHT), raw)
    img.save(filename)
    print(f'  📸 截图已保存: {filename}')


def inject_keydown(manager: SceneManager, key: int) -> None:
    """模拟按键事件"""
    event = pygame.event.Event(pygame.KEYDOWN, key=key)
    manager.handle_event(event)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    manager = SceneManager(screen, clock)

    output_dir = '/tmp/snake_screenshots'
    os.makedirs(output_dir, exist_ok=True)

    # ── 1. 主菜单画面 ──
    print('📺 场景 1: 主菜单')
    manager.draw()
    pygame.display.flip()
    save_frame(screen, f'{output_dir}/01_menu.png')

    # ── 2. 开始游戏 → 游戏画面 ──
    print('📺 场景 2: 游戏开始')
    inject_keydown(manager, pygame.K_RETURN)  # 回车开始
    # 让蛇走几步
    for _ in range(10):
        manager.update()
        clock.tick(FPS)
    manager.draw()
    pygame.display.flip()
    save_frame(screen, f'{output_dir}/02_gameplay.png')

    # ── 3. 暂停画面 ──
    print('📺 场景 3: 暂停')
    inject_keydown(manager, pygame.K_SPACE)
    manager.draw()
    pygame.display.flip()
    save_frame(screen, f'{output_dir}/03_pause.png')

    # ── 4. 继续游戏，让蛇走更多步 ──
    print('📺 场景 4: 继续游戏（蛇变长、加速）')
    inject_keydown(manager, pygame.K_SPACE)  # 取消暂停
    # 模拟吃很多食物让蛇变长
    for _ in range(30):
        manager.update()
        clock.tick(FPS)
    manager.draw()
    pygame.display.flip()
    save_frame(screen, f'{output_dir}/04_later_game.png')

    # ── 5. 让蛇撞墙 → 游戏结束 ──
    print('📺 场景 5: 游戏结束（撞墙）')
    # 让蛇一直往上走直到撞墙
    if manager.game_state:
        manager.game_state.snake.set_direction((0, -1))
    for _ in range(50):
        manager.update()
        clock.tick(FPS)
    manager.draw()
    pygame.display.flip()
    save_frame(screen, f'{output_dir}/05_gameover.png')

    pygame.quit()
    print(f'\n✅ 所有截图保存在: {output_dir}/')
    print('你可以通过文件管理器或终端查看这些图片。')


if __name__ == '__main__':
    main()
