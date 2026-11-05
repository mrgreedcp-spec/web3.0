# pandas 入门练习

一个入口、几份示例数据、七个按顺序学的模块，外加一个通用的 CSV 体检工具。**不新建虚拟环境、不重复安装**：直接用你机器上已有的 `python3` 和 pandas。

## 1. 先检查环境（只看不装）

```bash
python3 pandas-learn/main.py check
```

会打印当前 Python 路径、pandas / numpy 版本。缺 pandas 时，它会提示用**同一个解释器**安装（`python3 -m pip install pandas`），避免装到另一个 Python 里。

## 2. 唯一入口

```bash
python3 pandas-learn/main.py          # 检查环境 + 列出模块
python3 pandas-learn/main.py 01       # 运行某个模块（写 1 也行）
python3 pandas-learn/main.py all      # 全部跑一遍
```

## 3. 学习顺序

| 编号 | 主题 | 学会这些 | 建议时长 |
|---|---|---|---|
| 00 | 官方教程：读写泰坦尼克号 CSV | 对照[官方入门教程第 2 章](https://pandas.pydata.org/docs/getting_started/intro_tutorials/02_read_write.html)：`read_csv`、`head` / `tail`、`dtypes`、`info`、`to_excel` / `read_excel`、`to_csv` | 30 分钟 |
| 01 | CSV、DataFrame 与 read_csv | `read_csv`、`head`、`shape`、`dtypes`、`info`、`describe`、`parse_dates`、`dtype`、`sep`、`encoding` | 30 分钟 |
| 02 | 选列、选行与条件筛选 | `df["列"]`、`df[[...]]`、`loc` / `iloc`、`&` `\|` `~`、`isin`、`query`、`between` | 30 分钟 |
| 03 | 缺失值、类型转换与新增列 | `isna`、`fillna`、`dropna`、`astype`、新增列、`.dt`、`loc[条件, 列] = 值`、`rename` / `drop` | 30 分钟 |
| 04 | 分组聚合与排序 | `value_counts`、`groupby`、`agg`、`sort_values`、`pivot_table` | 30 分钟 |
| 05 | 合并两张表并导出 | `merge`（left / inner）、`indicator`、`to_csv` | 30 分钟 |
| 06 | 泰坦尼克号数据完整清洗 | 重复值、去空格、`str.extract` 提取称谓、`groupby().transform("median")` 分组填充、标记列、`category` 类型、`assert` 校验 | 45 分钟 |

每个模块的用法都一样：

1. **先运行**：`python3 pandas-learn/main.py 02`，对着输出看每一节在做什么。
2. **再读代码**：打开 `modules/m02_select_filter.py`，每个 `section(...)` 对应输出里的一节。
3. **做练习**：文件顶部的注释里有 3 道练习，直接加到 `run()` 末尾，再运行一次看结果。
4. **换成自己的数据**：把 `data/sales.csv` 换成你自己的 CSV，或在代码里改 `read_csv` 的路径。

CSV 的格式规则、`read_csv` 常用参数、常见报错和解决办法，见 [CSV_TIPS.md](CSV_TIPS.md)。

## 4. 体检任意 CSV（只读不改）

拿到一份新表格，先跑一次体检，得到问题清单，再决定怎么清洗：

```bash
python3 pandas-learn/main.py inspect 你的文件.csv
python3 pandas-learn/main.py inspect 你的文件.csv --encoding gbk --sep ";"   # 自动识别不准时手动指定
python3 pandas-learn/main.py inspect 你的文件.csv > 报告.txt                  # 把报告存下来
```

编码（UTF-8 / GBK）和分隔符（逗号、分号、制表符、竖线）默认会自动识别。报告共 9 节：

| 节 | 检查什么 |
|---|---|
| 1 基本信息 | 编码、分隔符、行列数、内存；列名带空格、`Unnamed: 0` 列、只读出 1 列（分隔符可能不对） |
| 2–3 前后几行 | `head(3)` / `tail(3)` |
| 4 每列概览 | 类型、非空、缺失数和比例、唯一值个数、示例值 |
| 5 重复与主键 | 整行重复、可能的主键、编号列里的重复值 |
| 6 数值列 | `describe()`；负数、少见的 0、极端值（超出四分位距 3 倍） |
| 7 文本列 | 首尾空格、`-` / `无` 之类的占位符、开头的 0 丢失、数字或日期被存成文本、大小写和空格造成的不同写法 |
| 8 类别列 | 唯一值不多的文本列，列出每个取值和出现次数 |
| 9 问题清单 | 汇总上面所有问题，每条附处理建议 |

练手用的 `data/messy_orders.csv` 里故意埋了 13 个问题，可以先拿它试试。

**实战项目：**[`batch-sim/`](batch-sim/README.md) 是一份模拟的生产批次数据（63 行），配有数据字典、问题清单和业务规则检查脚本。体检只能发现**格式上**的问题，看起来合理、实际却错了的数值，还要靠业务知识判断。

## 5. 目录

```
pandas-learn/
├── main.py              # 唯一入口：环境检查 + 模块调度
├── inspect_csv.py       # 通用 CSV 体检工具（main.py inspect 调用它）
├── batch-sim/           # 实战：模拟生产批次数据 + 数据字典 + 问题清单 + 清洗计划
├── obsidian-wiki/       # 数据清洗笔记，可以直接放进 Obsidian
├── CSV_TIPS.md          # CSV 速查：格式规则、read_csv 参数、常见报错
├── data/
│   ├── sales.csv        # 12 条订单，故意留了 1 个缺失 qty、1 个缺失 customer_id
│   ├── customers.csv    # 客户表，模块 05 合并用
│   ├── titanic.csv      # 官方教程用的泰坦尼克号乘客数据（891 行），模块 00、06 用
│   └── messy_orders.csv # 故意弄脏的订单表，练习体检工具用
├── modules/
│   ├── common.py        # 路径和打印小工具
│   └── m00_... m06_...  # 每个模块一个文件，入口函数都叫 run()
└── output/              # 导出的结果（不进 git）
```

## 6. 新增模块

1. 在 `modules/` 里新建 `m07_xxx.py`，写一个 `run()` 函数。
2. 在 `main.py` 的 `MODULES` 里登记一行：`"07": ("m07_xxx", "标题")`。

## 版本说明

示例在 pandas 3.0 上测过，pandas 2.x 也能跑。有一处输出不同：文本列在 pandas 3 显示为 `str`，在 pandas 2 显示为 `object`，都是正常的。
