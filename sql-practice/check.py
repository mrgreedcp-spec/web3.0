#!/usr/bin/env python3
"""自动判题：把你的 SQL 结果和标准答案比对。

用法：
  python3 check.py 5 my_q05.sql          # 用文件里的 SQL 答第 5 题
  python3 check.py 5 -e "SELECT ..."     # 直接写 SQL
  python3 check.py 5 --peek              # 只看标准答案的前几行结果（不看 SQL）
  python3 check.py --selftest            # 跑一遍全部标准答案

比对规则：只比结果，不比写法；列名不比，列数和每行的值要一致；
行的先后顺序不计；数字保留 2 位小数后比较。
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE / "shop.duckdb"


def split_statements(sql: str) -> list[str]:
    lines = [l for l in sql.splitlines() if not l.strip().startswith("--")]
    return [s.strip() for s in "\n".join(lines).split(";") if s.strip()]


def load_solutions() -> dict[int, str]:
    text = (HERE / "solutions.sql").read_text(encoding="utf-8")
    parts = re.split(r"^-- Q(\d+)[^\n]*$", text, flags=re.M)
    sols = {}
    for i in range(1, len(parts), 2):
        sols[int(parts[i])] = parts[i + 1].split("-- ====")[0]
    return sols


def run(con, sql: str):
    stmts = split_statements(sql)
    if not stmts:
        raise ValueError("没有可执行的 SQL")
    res = None
    for s in stmts:
        res = con.execute(s)
    return [d[0] for d in res.description], res.fetchall()


def norm(v):
    if isinstance(v, (float, Decimal)):
        return round(float(v), 2) + 0.0
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    return v


def as_bag(rows):
    return sorted((tuple(norm(v) for v in r) for r in rows), key=repr)


def show(cols, rows, n=8):
    print("  " + " | ".join(cols))
    for r in rows[:n]:
        print("  " + " | ".join(str(v) for v in r))
    if len(rows) > n:
        print(f"  …共 {len(rows)} 行")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("question", nargs="?", type=int)
    ap.add_argument("file", nargs="?")
    ap.add_argument("-e", "--sql")
    ap.add_argument("--peek", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    try:
        import duckdb
    except ImportError:
        sys.exit("请先安装：pip3 install duckdb")
    if not DB.exists():
        sys.exit("还没有 shop.duckdb，先运行：python3 build_db.py")
    con = duckdb.connect(str(DB))
    sols = load_solutions()

    if args.selftest:
        for q, sql in sorted(sols.items()):
            cols, rows = run(con, sql)
            print(f"Q{q:02d} ok  {len(rows):>5} 行  {', '.join(cols)}")
        return

    if args.question not in sols:
        sys.exit(f"没有第 {args.question} 题，可选 {min(sols)}–{max(sols)}")
    exp_cols, exp_rows = run(con, sols[args.question])

    if args.peek:
        print(f"Q{args.question:02d} 标准答案结果：")
        show(exp_cols, exp_rows)
        return

    sql = args.sql or (Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read())
    try:
        cols, rows = run(con, sql)
    except Exception as e:  # noqa: BLE001
        print(f"✗ 运行出错：{e}")
        sys.exit(1)

    if as_bag(rows) == as_bag(exp_rows):
        print(f"✓ Q{args.question:02d} 正确（{len(rows)} 行）")
        return
    print(f"✗ Q{args.question:02d} 结果不一致")
    if len(cols) != len(exp_cols):
        print(f"  列数不同：你的 {len(cols)} 列，答案 {len(exp_cols)} 列（{', '.join(exp_cols)}）")
    if len(rows) != len(exp_rows):
        print(f"  行数不同：你的 {len(rows)} 行，答案 {len(exp_rows)} 行")
    print("你的结果：")
    show(cols, rows, 5)
    print("提示：用 --peek 可以看答案结果的前几行。")
    sys.exit(1)


if __name__ == "__main__":
    main()
