"""最高分持久化管理"""
import json
import os


SCORE_FILE = os.path.expanduser("~/.snake_game_highscore.json")


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
