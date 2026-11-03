"""模块 05：合并两张表并导出结果

要点：
- pd.merge(左表, 右表, on="键", how=...)：类似 SQL 的 JOIN。
  how="left" 保留左表全部行；"inner" 只保留两边都有的。
- indicator=True 会多一列 _merge，告诉你每行来自哪边，排查对不上的数据很好用。
- to_csv(..., index=False) 导出；给 Excel 打开的中文 CSV 用 encoding="utf-8-sig"。

练习：
1. 把 how 改成 "inner"，比较行数变化，想想少了哪些行。
2. 统计每个会员等级（level）的总消费。
3. 把练习 2 的结果导出为 output/level_summary.csv。
"""

import pandas as pd

from .common import DATA, OUTPUT, section
from .m04_groupby import load


def run() -> None:
    sales = load()
    customers = pd.read_csv(DATA / "customers.csv")

    section("客户表")
    print(customers)

    section('left merge：订单表补上客户姓名和等级')
    merged = pd.merge(sales, customers, on="customer_id", how="left", indicator=True)
    print(merged[["order_id", "customer_id", "name", "level", "amount", "_merge"]])

    section("对不上的行（客户表里没有这个客户，或订单没填客户）")
    print(merged[merged["_merge"] == "left_only"][["order_id", "customer_id"]])

    section("每个客户的消费排行")
    ranking = (
        merged.dropna(subset=["name"])
        .groupby(["customer_id", "name", "level"], as_index=False)["amount"]
        .sum()
        .sort_values("amount", ascending=False)
    )
    print(ranking)

    OUTPUT.mkdir(exist_ok=True)
    out = OUTPUT / "customer_ranking.csv"
    ranking.to_csv(out, index=False, encoding="utf-8-sig")
    section("已导出")
    print(out)
    print("读回来验证：")
    print(pd.read_csv(out).head(3))
