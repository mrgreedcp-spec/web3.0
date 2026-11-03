# CSV 速查（今日里程碑：读懂并清洗数据）

依据：pandas 官方入门教程第 2 章 [How do I read and write tabular data?](https://pandas.pydata.org/docs/getting_started/intro_tutorials/02_read_write.html)。
可运行示例：`python3 pandas-learn/main.py 00`（官方的泰坦尼克数据），`python3 pandas-learn/main.py 01`（本项目的销售数据）。
下面的报错信息和输出都是在 pandas 3.0.5 上实际跑出来的。

## 1. 官方教程的三条 REMEMBER

1. **读数据用 `read_*`**：`read_csv`、`read_excel`、`read_json`、`read_sql`、`read_parquet`……
2. **写数据用 `to_*`**：`to_csv`、`to_excel`……
3. **读完先检查**：`head` / `tail` / `info` 三个方法，加上 `dtypes` 属性。

另外两个小点：
- 直接 `print(df)`，默认显示**前 5 行和后 5 行**，中间用 `...` 省略。
- `dtypes` 是**属性，不加括号**；`head()`、`info()` 是**方法，要加括号**。属性描述“它是什么”，方法表示“对它做什么”。

## 2. CSV 文件本身的规则

| 规则 | 例子（titanic.csv 原文） | 读入后 |
|---|---|---|
| 第一行是列名 | `PassengerId,Survived,Pclass,Name,...` | 变成 `df.columns` |
| 逗号分隔字段 | `1,0,3,...` | 每个字段一列 |
| **字段里本身有逗号，就用双引号包起来** | `"Braund, Mr. Owen Harris"` | `Braund, Mr. Owen Harris` |
| **引号里的引号写成两个 `""`** | `"Johnston, Miss Catherine Helen ""Carrie"""` | `Johnston, Miss Catherine Helen "Carrie"` |
| 空字段表示缺失 | `...,7.25,,S`（Cabin 是空的） | `NaN` |
| 文件里没有类型，都是文本 | `22`、`7.25` | pandas 自动推断成 `int64` / `float64` / `str` |

## 3. `read_csv` 常用参数

| 参数 | 解决什么问题 | 例子 |
|---|---|---|
| `sep` | 分隔符不是逗号 | `sep=";"`，`sep="\t"` |
| `encoding` | 中文乱码，或报 `UnicodeDecodeError` | `encoding="gbk"` / `"utf-8-sig"` |
| `usecols` | 只读需要的列（省内存） | `usecols=["Name", "Age"]` |
| `nrows` | 先读几行看看 | `nrows=100` |
| `index_col` | 用某列当行索引 | `index_col="PassengerId"` |
| `dtype` | 指定列类型，**防止开头的 0 丢失** | `dtype={"zip": str}` |
| `parse_dates` | 把日期文本解析成日期 | `parse_dates=["date"]` |
| `na_values` | 把 `-`、`N/A` 之类也当作缺失 | `na_values=["-", "N/A"]` |
| `thousands` | `"1,234"` 这种带千分位的数字 | `thousands=","` |
| `skiprows` / `header` | 文件开头有说明文字，或没有列名 | `skiprows=2`，`header=None, names=[...]` |
| `skipinitialspace` | 逗号后面有空格，导致列名变成 `" b"` | `skipinitialspace=True` |
| `on_bad_lines` | 个别行的字段数不对 | `on_bad_lines="skip"`（会丢数据，先查原因再用） |
| `chunksize` | 文件太大，一次读不进内存 | `for chunk in pd.read_csv(f, chunksize=100_000): ...` |

## 4. 读完必做的检查

```python
df.shape            # 多少行、多少列，和预期一样吗？
df.head()           # 列名、内容对不对？
df.dtypes           # 数字列是不是数字？日期列是不是日期？
df.info()           # 每列有多少非空值？
df.isna().sum()     # 每列缺几个？
df.describe()       # 数值范围合理吗？（有没有负数年龄、0 元票价？）
```

用 titanic.csv 检查的结果：891 行、12 列；`Age` 缺 177 个，`Cabin` 缺 687 个，`Embarked` 缺 2 个；`Fare` 最小值是 0，值得追查一下。

## 5. 写出 CSV

```python
df.to_csv("out.csv", index=False)                       # 不把行号写进文件
df.to_csv("给Excel.csv", index=False, encoding="utf-8-sig")  # Excel 打开中文不乱码
df.to_excel("out.xlsx", sheet_name="passengers", index=False)  # 需要 openpyxl（本环境已装）
```

不加 `index=False`，读回来时会多出一列 `Unnamed: 0`。

## 6. 常见报错和对应办法

| 现象 / 报错 | 原因 | 办法 |
|---|---|---|
| `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xb3 ...` | 文件是 GBK 编码（中文 Excel 常见） | `encoding="gbk"` |
| `ParserError: Error tokenizing data. C error: Expected 2 fields in line 3, saw 3` | 某行字段数不对：分隔符选错了，或字段里有逗号却没加引号 | 先打开原文看那一行；确认 `sep`；实在不行用 `on_bad_lines="skip"` |
| `FileNotFoundError` | 相对路径是相对于**运行命令时所在的目录**，不是脚本所在的目录 | 用绝对路径，或 `Path(__file__).parent / "data" / "x.csv"` |
| 数字列变成了 `str` | 里面混了 `"1,234"`、`-`、`N/A` 之类的文本 | `thousands=","`，`na_values=[...]` |
| `00123` 读成了 `123` | 被当成了整数 | `dtype={"zip": str}` |
| 整数列显示成 `2.0` | 列里有缺失值，只能用 float 存 | 先 `fillna` 再 `astype(int)`（见模块 03） |
| 列名前面多了空格 | 逗号后有空格 | `skipinitialspace=True`，或 `df.columns = df.columns.str.strip()` |
| 读回的文件多了 `Unnamed: 0` 列 | 写出时没加 `index=False` | 写出时加上；或读入时用 `index_col=0` |

## 7. 版本差异

官方教程说文本列的类型是 `object`，这是 pandas 2 的显示方式。在 pandas 3 里显示为 `str`，两者都表示文本列，用法一样。
