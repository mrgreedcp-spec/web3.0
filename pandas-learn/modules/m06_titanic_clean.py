"""模块 06：泰坦尼克号数据完整清洗

清洗流程（每一步都先“查”，再“改”，最后“验”）：
  0. 读取并留一份原始数据，方便最后对比
  1. 重复值：整行重复、乘客编号重复
  2. 文本：去掉首尾空格
  3. 从姓名里提取称谓 Title（Mr / Mrs / Miss / Master / Rare）
  4. Age 缺 177 个：按称谓分组，用各组的中位数填，并记录哪些是填出来的
  5. Embarked 缺 2 个：查原因，填出现最多的港口
  6. Cabin 缺 687 个：填不了，改成 has_cabin（有没有舱号）和 deck（甲板字母）
  7. Fare：0 元票价和超高票价，查原因后加标记，不删
  8. 类型：0/1 改成布尔值，类别列改成 category
  9. 校验 + 前后对比 + 导出

练习：
1. 把第 4 步换成“全体乘客年龄的中位数”来填，对比 Master（小男孩）组的年龄会被填成多少，想想哪种更合理。
2. 用清洗后的数据算：各 Title 的幸存率（groupby + mean）。
3. 用清洗后的数据做透视表：行=Pclass，列=Sex，值=Survived，算法=mean。
"""

import pandas as pd

from .common import DATA, OUTPUT, section

# 称谓归并规则：法语/少见写法并入常见称谓，其余少见称谓归为 Rare
TITLE_MAP = {"Mlle": "Miss", "Ms": "Miss", "Mme": "Mrs"}
COMMON_TITLES = {"Mr", "Mrs", "Miss", "Master"}
PORT_NAMES = {"S": "Southampton", "C": "Cherbourg", "Q": "Queenstown"}


def run() -> None:
    # 显示设置只在本模块内生效，不影响其他模块
    with pd.option_context("display.width", 140, "display.max_columns", 20):
        clean()


def clean() -> None:
    # 0) 读取，原始数据 raw 保持不动，所有修改都在 df 上做
    raw = pd.read_csv(DATA / "titanic.csv")
    df = raw.copy()
    section("0. 清洗前：每列缺失个数")
    print(df.isna().sum()[lambda s: s > 0])

    # 1) 重复值
    section("1. 重复值检查")
    print("整行重复：", df.duplicated().sum(), "| PassengerId 重复：", df["PassengerId"].duplicated().sum())

    # 2) 文本首尾空格
    section("2. 文本首尾空格")
    bad = df["Name"] != df["Name"].str.strip()
    print("Name 带首尾空格的：", [repr(x) for x in df.loc[bad, "Name"]])
    text_cols = ["Name", "Sex", "Ticket", "Cabin", "Embarked"]
    df[text_cols] = df[text_cols].apply(lambda s: s.str.strip())
    print("去空格后还剩：", (df["Name"] != df["Name"].str.strip()).sum())

    # 3) 提取称谓。坑：Miss / Master 后面没有句号，所以不能用“称谓.”去匹配
    section("3. 从 Name 提取称谓 Title")
    df["Title"] = df["Name"].str.extract(r",\s*(the Countess|[A-Za-z]+)")[0]
    print("原始称谓：", df["Title"].value_counts().to_dict())
    df["Title"] = df["Title"].replace(TITLE_MAP)
    df.loc[~df["Title"].isin(COMMON_TITLES), "Title"] = "Rare"
    print("归并后：  ", df["Title"].value_counts().to_dict())

    # 4) Age：按称谓分组的中位数填充
    section("4. Age：按称谓分组，用中位数填")
    medians = df.groupby("Title")["Age"].median()
    print("各称谓年龄中位数：", medians.to_dict())
    print("缺失的 Age 分布在：", df.loc[df["Age"].isna(), "Title"].value_counts().to_dict())
    df["age_imputed"] = df["Age"].isna()  # 先记下哪些是填出来的
    df["Age"] = df["Age"].fillna(df.groupby("Title")["Age"].transform("median"))
    print("填完后 Age 缺失：", df["Age"].isna().sum(), "| 被填的行数：", df["age_imputed"].sum())

    # 5) Embarked
    section("5. Embarked：先看缺失的是谁")
    print(df.loc[df["Embarked"].isna(), ["PassengerId", "Name", "Pclass", "Ticket", "Fare", "Cabin"]])
    mode = df["Embarked"].mode()[0]
    print(f"两人同一张船票、同一个船舱，是同行的。用出现最多的港口 {mode} 来填。")
    df["Embarked"] = df["Embarked"].fillna(mode)
    df["port"] = df["Embarked"].map(PORT_NAMES)

    # 6) Cabin
    section("6. Cabin：缺 77%，改成两个新列再删掉")
    df["has_cabin"] = df["Cabin"].notna()
    df["deck"] = df["Cabin"].str[0].fillna("Unknown")
    print("deck 分布：", df["deck"].value_counts().to_dict())
    print("有舱号的幸存率：", round(df.loc[df["has_cabin"], "Survived"].mean(), 3),
          "| 没舱号的：", round(df.loc[~df["has_cabin"], "Survived"].mean(), 3))
    df = df.drop(columns=["Cabin"])

    # 7) Fare
    section("7. Fare：0 元票价")
    free = df["Fare"] == 0
    print(df.loc[free, ["PassengerId", "Name", "Pclass", "Ticket"]].head(6))
    print(f"共 {free.sum()} 人，全是男性，船票多为 LINE 或连号，像是员工/受邀乘客。是真实情况，不删，只加标记。")
    df["fare_free"] = free

    section("7. Fare：超高票价，其实是一张票多人共用")
    df["ticket_group_size"] = df.groupby("Ticket")["Ticket"].transform("size")
    df["fare_per_person"] = (df["Fare"] / df["ticket_group_size"]).round(2)
    print(df.nlargest(3, "Fare")[["Name", "Ticket", "Fare", "ticket_group_size", "fare_per_person"]])

    # 8) 类型
    section("8. 类型整理")
    df["Survived"] = df["Survived"].astype(bool)
    df["Pclass"] = pd.Categorical(df["Pclass"], categories=[1, 2, 3], ordered=True)
    for col in ["Sex", "Embarked", "Title", "deck", "port"]:
        df[col] = df[col].astype("category")
    print(df.dtypes)

    # 9) 校验：用 assert 把“清洗目标”写成代码，不满足就直接报错
    section("9. 校验")
    assert len(df) == len(raw), "行数不该变"
    assert df[["Age", "Embarked", "Fare"]].notna().all().all(), "关键列不该有缺失"
    assert df["Age"].between(0, 100).all(), "年龄超出范围"
    assert set(df["Sex"].unique()) == {"male", "female"}
    print("全部通过 ✓  行数", len(df), "| 剩余缺失", int(df.isna().sum().sum()))

    section("前后对比：Age 的分布")
    compare = pd.DataFrame({"清洗前": raw["Age"].describe(), "清洗后": df["Age"].describe()}).round(2)
    print(compare)

    section("清洗后的数据（前 5 行，只看关键列和新增列）")
    print(df[["PassengerId", "Survived", "Pclass", "Sex", "Age", "age_imputed",
              "Title", "port", "has_cabin", "deck", "fare_per_person"]].head())

    OUTPUT.mkdir(exist_ok=True)
    out = OUTPUT / "titanic_clean.csv"
    df.to_csv(out, index=False)
    section("已导出")
    print(out, "| 形状：", df.shape)
