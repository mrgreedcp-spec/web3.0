"""模块 03：缺失值、类型转换与新增列

要点：
- isna().sum() 统计每列缺失个数。
- dropna() 删掉含缺失的行；fillna() 用某个值填上。
- astype() 转类型；新列直接赋值：df["新列"] = 表达式。
- 修改时用 df = df.xxx(...) 或 df.loc[条件, 列] = 值，不要链式赋值 df[条件]["列"] = 值。

练习：
1. 不删行，而是把缺失的 customer_id 填成 "UNKNOWN"。
2. 新增列 weekday：用 df["date"].dt.day_name()。
3. 新增列 big_order：amount >= 100 时为 True。
"""

import pandas as pd

from .common import DATA, section


def run() -> None:
    df = pd.read_csv(DATA / "sales.csv", parse_dates=["date"])

    section("每列缺失个数")
    print(df.isna().sum())

    section("看看有缺失的是哪几行")
    print(df[df.isna().any(axis=1)])

    section("处理策略：qty 缺失按 1 件算；customer_id 缺失的行删掉")
    df["qty"] = df["qty"].fillna(1).astype(int)
    df = df.dropna(subset=["customer_id"])
    print(df.isna().sum().sum(), "个缺失值剩余；行数 =", len(df))

    section("新增列：金额 amount = qty * price")
    df["amount"] = df["qty"] * df["price"]
    print(df[["order_id", "qty", "price", "amount"]].head())

    section("新增列：从日期里拆出月、日")
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day
    print(df[["date", "month", "day"]].head(3))

    section("按条件改值：loc[条件, 列] = 值")
    df["tier"] = "普通单"
    df.loc[df["amount"] >= 100, "tier"] = "大单"
    print(df[["order_id", "amount", "tier"]])

    section("重命名列、删除列")
    tidy = df.rename(columns={"qty": "数量"}).drop(columns=["month", "day"])
    print(tidy.columns.tolist())
