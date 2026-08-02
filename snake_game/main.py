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

    # 主循环：处理事件 → 更新状态 → 渲染画面
    running = True
    while running:
        for event in pygame.event.get():
            if not manager.handle_event(event):
                running = False
                break

        manager.update()
        manager.draw()
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
