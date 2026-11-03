"""模块 01：CSV、DataFrame 与 read_csv

概念：
- CSV：纯文本表格。第一行通常是列名，每行一条记录，字段之间用逗号分隔。
- DataFrame：pandas 里的“表”。有行索引（index）、列名（columns），每一列是一个 Series。
- pd.read_csv：把 CSV 读成 DataFrame，是最常用的入口函数。

练习（改完再运行 `python3 pandas-learn/main.py 01`）：
1. 用 usecols 只读 date、product、qty 三列。
2. 用 nrows=5 只读前 5 行。
3. 用 index_col="order_id" 把订单号设成行索引，再看 df.loc[1003]。
"""

import pandas as pd

from .common import DATA, section


def run() -> None:
    # 1) 先看 CSV 本身就是文本
    section("CSV 原文（前 3 行）")
    with open(DATA / "sales.csv", encoding="utf-8") as f:
        for _ in range(3):
            print(f.readline().rstrip())

    # 2) 读成 DataFrame
    df = pd.read_csv(DATA / "sales.csv")

    section("df.head()：前 5 行")
    print(df.head())

    section("df.shape：(行数, 列数)")
    print(df.shape)

    section("df.dtypes：每列的类型")
    print(df.dtypes)
    # 注意 qty 是 float：因为有一行 qty 为空，整数列里出现缺失值会变成浮点。

    section("df.info()：类型 + 非空数量，一眼看出哪列有缺失")
    df.info()

    section("df.describe()：数值列的统计摘要")
    print(df.describe())

    # 3) read_csv 常用参数
    section("parse_dates：读取时把 date 解析成日期类型")
    df2 = pd.read_csv(DATA / "sales.csv", parse_dates=["date"])
    print(df2["date"].dtype, "| 最早:", df2["date"].min().date(), "| 最晚:", df2["date"].max().date())

    section("dtype：强制 order_id 当字符串（订单号不该参与计算）")
    df3 = pd.read_csv(DATA / "sales.csv", dtype={"order_id": "string"})
    print(df3["order_id"].dtype, df3["order_id"].head(3).tolist())

    section("从字符串读 CSV（调试/做小实验时很方便）")
    from io import StringIO

    text = "name;score\n小明;90\n小红;85\n"
    print(pd.read_csv(StringIO(text), sep=";"))  # sep 指定分隔符

    print("\n常见坑：Excel 导出的中文 CSV 若乱码，试试 encoding='gbk' 或 'utf-8-sig'。")
