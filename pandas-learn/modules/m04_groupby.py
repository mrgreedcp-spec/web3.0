"""模块 04：分组聚合与排序

要点：
- groupby("列")["值列"].sum()：按某列分组，对另一列求和。
- agg：一次算多个统计量，可以给结果列起名。
- sort_values：排序；value_counts：计数最快的写法。
- pivot_table：做 Excel 里的“数据透视表”。

练习：
1. 每个城市卖了多少件（qty 求和），从多到少排序。
2. 每个品类的平均单价。
3. 透视表：行=date，列=category，值=amount 求和。
"""

import pandas as pd

from .common import DATA, section


def load() -> pd.DataFrame:
    df = pd.read_csv(DATA / "sales.csv", parse_dates=["date"])
    df["qty"] = df["qty"].fillna(1).astype(int)
    df["amount"] = df["qty"] * df["price"]
    return df


def run() -> None:
    df = load()

    section("value_counts：每个城市有几笔订单")
    print(df["city"].value_counts())

    section("groupby + sum：每个城市的销售额")
    print(df.groupby("city")["amount"].sum())

    section("排序：销售额从高到低")
    print(df.groupby("city")["amount"].sum().sort_values(ascending=False))

    section("agg：每个品类的订单数、总件数、总金额、平均单价")
    summary = df.groupby("category").agg(
        订单数=("order_id", "count"),
        总件数=("qty", "sum"),
        总金额=("amount", "sum"),
        平均单价=("price", "mean"),
    )
    print(summary.round(1))

    section("多列分组：城市 × 品类")
    print(df.groupby(["city", "category"])["amount"].sum().reset_index())

    section("pivot_table：行=城市，列=品类，值=销售额")
    pivot = df.pivot_table(index="city", columns="category", values="amount", aggfunc="sum", fill_value=0)
    print(pivot)

    section("按天汇总销售额（时间序列的雏形）")
    print(df.groupby("date")["amount"].sum())
