"""模块 02：选列、选行与条件筛选

要点：
- df["列"] 得到 Series；df[["列1", "列2"]] 得到 DataFrame（注意双层方括号）。
- df.loc[行标签, 列名]：按“标签”取；df.iloc[行号, 列号]：按“位置”取。
- 条件筛选：df[条件]，多个条件用 & | ~，并且每个条件要加括号。

练习：
1. 找出 price 大于 50 的订单，只显示 product 和 price。
2. 找出“器具”类且城市不是北京的订单（提示：~ 或 !=）。
3. 用 query 写出：qty >= 3 and category == "饮品"。
"""

import pandas as pd

from .common import DATA, section


def run() -> None:
    df = pd.read_csv(DATA / "sales.csv", parse_dates=["date"])

    section('选一列：df["product"] → Series')
    print(df["product"].head(3))

    section('选多列：df[["date", "product", "qty"]] → DataFrame')
    print(df[["date", "product", "qty"]].head(3))

    section("iloc：按位置取，第 0~2 行、第 0~2 列")
    print(df.iloc[0:3, 0:3])

    section('loc：按标签取，行标签 0~2（含 2！）、指定列')
    print(df.loc[0:2, ["city", "product"]])

    section('单条件：city == "上海"')
    print(df[df["city"] == "上海"])

    section('多条件：饮品 且 qty >= 3（每个条件都要加括号）')
    print(df[(df["category"] == "饮品") & (df["qty"] >= 3)])

    section('isin：城市在 [北京, 深圳] 里')
    print(df[df["city"].isin(["北京", "深圳"])][["order_id", "city", "product"]])

    section("query：用字符串写条件，更易读")
    print(df.query('price > 50 and city != "北京"')[["order_id", "city", "product", "price"]])

    section("按日期范围筛选")
    mask = df["date"].between("2026-10-02", "2026-10-04")
    print(df.loc[mask, ["date", "product"]])
