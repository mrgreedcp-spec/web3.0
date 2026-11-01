#!/usr/bin/env python3
"""生成数据（如果还没有）并建库 shop.duckdb。需要先 pip3 install duckdb。"""
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.chdir(HERE)
try:
    import duckdb
except ImportError:
    sys.exit("请先安装：pip3 install duckdb")

if not (HERE / "data" / "orders.csv").exists():
    subprocess.run([sys.executable, "generate_data.py"], check=True)

db = HERE / "shop.duckdb"
if db.exists():
    db.unlink()
con = duckdb.connect(str(db))
statements = (HERE / "setup.sql").read_text(encoding="utf-8")
result = None
for stmt in [s.strip() for s in statements.split(";") if s.strip()]:
    lines = [l for l in stmt.splitlines() if not l.strip().startswith("--")]
    if lines:
        result = con.execute("\n".join(lines))
for name, n in result.fetchall():
    print(f"{name:12s} {n:>7,}")
con.close()
print(f"已建库：{db}")
