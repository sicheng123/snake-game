"""音效系统：程序生成 WAV 并通过系统播放器播放"""
import struct
import math
import io
import wave
import os
import sys
import subprocess
import tempfile
import threading


SAMPLE_RATE = 44100
BITS_PER_SAMPLE = 16
MAX_AMP = 32767


def _sine_wave(freq: float, duration: float, amp: float = 0.5) -> bytes:
    """生成正弦波原始数据"""
    n_samples = int(SAMPLE_RATE * duration)
    data = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        value = int(MAX_AMP * amp * math.sin(2 * math.pi * freq * t))
        data.append(struct.pack("<h", value))
    return b"".join(data)


def _chirp(freq_start: float, freq_end: float, duration: float, amp: float = 0.5) -> bytes:
    """扫频音效（频率从 start 线性变化到 end）"""
    n_samples = int(SAMPLE_RATE * duration)
    data = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        progress = i / n_samples
        freq = freq_start + (freq_end - freq_start) * progress
        value = int(MAX_AMP * amp * math.sin(2 * math.pi * freq * t))
        data.append(struct.pack("<h", value))
    return b"".join(data)


def _make_wav(frames: bytes) -> bytes:
    """将原始 PCM 数据封装为 WAV 格式"""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(BITS_PER_SAMPLE // 8)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(frames)
    return buf.getvalue()


def _compose(*segments: bytes) -> bytes:
    """拼接多个原始数据段"""
    return b"".join(segments)


def _silence(duration: float) -> bytes:
    """生成静音段"""
    n_samples = int(SAMPLE_RATE * duration)
    return b"\x00" * n_samples * (BITS_PER_SAMPLE // 8)


def _get_player_cmd(wav_path: str) -> list[str] | None:
    """根据平台返回系统播放器命令"""
    if sys.platform == "win32":
        return [
            "powershell", "-c",
            f'(New-Object Media.SoundPlayer "{wav_path}").Play();'
        ]
    elif sys.platform == "darwin":
        return ["afplay", wav_path]
    else:
        # Linux: 优先 aplay（ALSA），其次 paplay（PulseAudio）
        if os.path.exists("/usr/bin/aplay") or os.path.exists("/bin/aplay"):
            return ["aplay", "-q", wav_path]
        return ["paplay", wav_path]


class SoundManager:
    """音效管理器"""

    def __init__(self):
        self._enabled = True

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value

    def _play(self, frames: bytes) -> None:
        """播放原始音频数据（写入临时文件，系统播放器异步播放）"""
        if not self._enabled:
            return
        try:
            wav_data = _make_wav(frames)
            cmd = _get_player_cmd("-")
            if cmd is None:
                return
            # 写入临时文件（aplay/afplay 不支持 stdin 管道）
            fd, tmp_path = tempfile.mkstemp(suffix=".wav", prefix="snake_")
            with os.fdopen(fd, "wb") as f:
                f.write(wav_data)
            cmd[-1] = tmp_path
            # 后台线程播放，播完后清理临时文件
            def _play_and_clean():
                try:
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
                except Exception:
                    pass
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
            threading.Thread(target=_play_and_clean, daemon=True).start()
        except Exception:
            pass  # 音频播放失败不影响游戏

    def play_eat(self) -> None:
        """吃食物：短促升调 440Hz→660Hz, 0.1s"""
        frames = _chirp(440, 660, 0.1, amp=0.4)
        self._play(frames)

    def play_die(self) -> None:
        """死亡：下降低音 400Hz→200Hz, 0.3s"""
        frames = _chirp(400, 200, 0.3, amp=0.6)
        self._play(frames)

    def play_pause(self) -> None:
        """暂停：双音 ping 800Hz 0.05s + 600Hz 0.05s"""
        a = _sine_wave(800, 0.05, amp=0.3)
        b = _sine_wave(600, 0.05, amp=0.3)
        frames = _compose(a, b)
        self._play(frames)

    def play_level_up(self) -> None:
        """升级：三连升调 523→659→784Hz，各 0.08s，间隔 0.03s"""
        a = _sine_wave(523, 0.08, amp=0.4)
        s1 = _silence(0.03)
        b = _sine_wave(659, 0.08, amp=0.4)
        s2 = _silence(0.03)
        c = _sine_wave(784, 0.08, amp=0.4)
        frames = _compose(a, s1, b, s2, c)
        self._play(frames)

    def play_difficulty(self) -> None:
        """切换难度：单提示音 1000Hz, 0.06s"""
        frames = _sine_wave(1000, 0.06, amp=0.35)
        self._play(frames)
