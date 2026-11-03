"""模块 00：照着官方教程读 CSV（泰坦尼克号乘客数据）

对应官方入门教程第 2 章 "How do I read and write tabular data?"：
https://pandas.pydata.org/docs/getting_started/intro_tutorials/02_read_write.html
数据 data/titanic.csv 来自 pandas 官方仓库：
https://github.com/pandas-dev/pandas/raw/main/doc/data/titanic.csv

列含义（官方说明）：
- PassengerId 乘客编号      - Survived 是否幸存（0 否，1 是）
- Pclass 船票等级（1/2/3）  - Name 姓名      - Sex 性别      - Age 年龄
- SibSp 同船的兄弟姐妹/配偶人数     - Parch 同船的父母/子女人数
- Ticket 船票号    - Fare 票价    - Cabin 船舱号    - Embarked 登船港口（S/C/Q）

练习：
1. 打印最后 10 行：titanic.tail(10)。
2. 只读 Name、Age、Survived 三列（usecols），再看 info() 里内存变小了多少。
3. 把 Survived 为 1 的乘客导出成 output/survivors.csv（index=False），再读回来数一数行数。
"""

import pandas as pd

from .common import DATA, OUTPUT, section


def run() -> None:
    # ① 读取：read_csv 把 CSV 文件变成 DataFrame
    titanic = pd.read_csv(DATA / "titanic.csv")

    section("直接打印 DataFrame：默认显示前 5 行 + 后 5 行，中间用 ... 省略")
    with pd.option_context("display.max_columns", 6, "display.width", 100):
        print(titanic)

    cols = ["PassengerId", "Survived", "Pclass", "Name", "Age"]
    with pd.option_context("display.width", 140, "display.max_columns", 10):
        section("head(8)：前 8 行（只挑几列，方便看）")
        print(titanic[cols].head(8))

        section("tail(3)：最后 3 行")
        print(titanic[cols].tail(3))

    section("dtypes：每列的类型（属性，不加括号）")
    print(titanic.dtypes)

    section("info()：技术摘要（方法，要加括号）")
    titanic.info()

    section("CSV 细节：字段里本身有逗号时，会用双引号包起来")
    with open(DATA / "titanic.csv", encoding="utf-8") as f:
        f.readline()
        print("原文：", f.readline().rstrip())
    print("读入后 Name：", titanic.loc[0, "Name"])

    section("CSV 里的空字段 → 读入后是 NaN（缺失值）")
    print(titanic.isna().sum()[lambda s: s > 0])

    # ② 写出：to_* 系列。官方教程这里演示的是导出 Excel
    OUTPUT.mkdir(exist_ok=True)
    xlsx = OUTPUT / "titanic.xlsx"
    titanic.to_excel(xlsx, sheet_name="passengers", index=False)
    back = pd.read_excel(xlsx, sheet_name="passengers", engine="openpyxl")
    section("to_excel 导出 → read_excel 读回")
    print(xlsx, "| 读回形状：", back.shape)

    csv_out = OUTPUT / "titanic_first20.csv"
    titanic.head(20).to_csv(csv_out, index=False)
    section("to_csv 导出前 20 行（index=False：不把行号写进文件）")
    print(csv_out, "| 读回形状：", pd.read_csv(csv_out).shape)
