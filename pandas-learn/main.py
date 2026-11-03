"""pandas 学习项目的唯一入口。

用法（在仓库根目录或本目录运行都可以）：
    python3 pandas-learn/main.py            # 检查环境 + 列出所有模块
    python3 pandas-learn/main.py check      # 只检查环境（不安装任何东西）
    python3 pandas-learn/main.py 01         # 运行第 1 个模块
    python3 pandas-learn/main.py all        # 依次运行全部模块
    python3 pandas-learn/main.py inspect 文件.csv   # 体检任意 CSV（只读不改）
"""

import importlib
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# 编号 -> (模块文件名, 标题)。加新模块只需在 modules/ 里放文件并在这里登记一行。
MODULES = {
    "00": ("m00_titanic_read", "官方教程：读写泰坦尼克号 CSV"),
    "01": ("m01_read_csv", "CSV、DataFrame 与 read_csv"),
    "02": ("m02_select_filter", "选列、选行与条件筛选"),
    "03": ("m03_clean", "缺失值、类型转换与新增列"),
    "04": ("m04_groupby", "分组聚合与排序"),
    "05": ("m05_merge_export", "合并两张表并导出结果"),
    "06": ("m06_titanic_clean", "泰坦尼克号数据完整清洗"),
}


def check_env() -> bool:
    """只检查、不安装：告诉你当前用的是哪个 Python、pandas 在不在。"""
    print(f"Python  : {platform.python_version()}  ({sys.executable})")
    ok = True
    for name in ("pandas", "numpy"):
        try:
            mod = importlib.import_module(name)
            print(f"{name:<8}: {mod.__version__}")
        except ImportError:
            ok = False
            print(f"{name:<8}: 未安装")
    if not ok:
        print("\n缺少依赖时，用【同一个】解释器安装，避免装到别的 Python 里：")
        print(f"    {sys.executable} -m pip install pandas")
    return ok


def list_modules() -> None:
    print("\n可运行的模块：")
    for key, (_, title) in MODULES.items():
        print(f"  {key}  {title}")
    print("\n运行示例：python3 pandas-learn/main.py 01")
    print("体检任意 CSV：python3 pandas-learn/main.py inspect 文件.csv")


def run_module(key: str) -> None:
    filename, title = MODULES[key]
    print(f"\n{'=' * 60}\n模块 {key}：{title}\n{'=' * 60}")
    importlib.import_module(f"modules.{filename}").run()


def main(argv: list[str]) -> int:
    arg = argv[1] if len(argv) > 1 else ""
    if arg == "inspect":
        from inspect_csv import main as inspect_main

        return inspect_main(argv[2:])
    if arg == "check":
        return 0 if check_env() else 1
    if not check_env():
        return 1
    if arg == "":
        list_modules()
    elif arg == "all":
        for key in MODULES:
            run_module(key)
    elif arg.zfill(2) in MODULES:
        run_module(arg.zfill(2))
    else:
        print(f"\n不认识的参数：{arg}")
        list_modules()
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
