# pandas 入门练习

一个入口、一份示例数据、五个按顺序学的模块。**不新建虚拟环境、不重复安装**：直接用你机器上已有的 `python3` 和 pandas。

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

每个模块的用法都一样：

1. **先运行**：`python3 pandas-learn/main.py 02`，对着输出看每一节在做什么。
2. **再读代码**：打开 `modules/m02_select_filter.py`，每个 `section(...)` 对应输出里的一节。
3. **做练习**：文件顶部的注释里有 3 道练习，直接加到 `run()` 末尾，再运行一次看结果。
4. **换成自己的数据**：把 `data/sales.csv` 换成你自己的 CSV，或在代码里改 `read_csv` 的路径。

CSV 的格式规则、`read_csv` 常用参数、常见报错和解决办法，见 [CSV_TIPS.md](CSV_TIPS.md)。

## 4. 目录

```
pandas-learn/
├── main.py              # 唯一入口：环境检查 + 模块调度
├── CSV_TIPS.md          # CSV 速查：格式规则、read_csv 参数、常见报错
├── data/
│   ├── sales.csv        # 12 条订单，故意留了 1 个缺失 qty、1 个缺失 customer_id
│   ├── customers.csv    # 客户表，模块 05 合并用
│   └── titanic.csv      # 官方教程用的泰坦尼克号乘客数据（891 行），模块 00 用
├── modules/
│   ├── common.py        # 路径和打印小工具
│   └── m00_... m05_...  # 每个模块一个文件，入口函数都叫 run()
└── output/              # 导出的结果（不进 git）
```

## 5. 新增模块

1. 在 `modules/` 里新建 `m06_xxx.py`，写一个 `run()` 函数。
2. 在 `main.py` 的 `MODULES` 里登记一行：`"06": ("m06_xxx", "标题")`。

## 版本说明

示例在 pandas 3.0 上测过，pandas 2.x 也能跑。有一处输出不同：文本列在 pandas 3 显示为 `str`，在 pandas 2 显示为 `object`，都是正常的。
