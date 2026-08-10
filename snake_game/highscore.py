"""最高分持久化管理"""
import json
import os


def _get_score_file() -> str:
    """获取最高分文件路径，兼容 Android 和桌面平台"""
    base = os.environ.get("ANDROID_APP_PATH", os.path.expanduser("~"))
    return os.path.join(base, ".snake_game_highscore.json")


SCORE_FILE = _get_score_file()


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
