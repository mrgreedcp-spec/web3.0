"""各模块共用的小工具：数据路径、打印分节。"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUTPUT = ROOT / "output"


def section(title: str) -> None:
    print(f"\n--- {title} ---")
