# DuckDB 超市 SQL 练习

一套从入门到进阶的 SQL 练习：虚构连锁超市的销售数据，33 道题，分 7 个等级，带自动判题。
在本地用 DuckDB 运行，不用注册账号，也不花钱。大部分写法可以直接用到 Snowflake 和 Databricks 上，每一级末尾都列出了三个平台的差异。

## 准备（Mac，一次就好）

```bash
pip3 install duckdb
```
```bash
cd ~/web3.0/sql-practice && python3 build_db.py
```

`build_db.py` 会先生成数据（`data/` 目录，约 8 MB），再建好 `shop.duckdb`。数据用固定随机种子生成，每次都一样。

## 写 SQL 的三种方式

1. **DuckDB 命令行**（推荐，需要 `brew install duckdb`）：`duckdb shop.duckdb` 进入后直接写 SQL。用 `duckdb -ui shop.duckdb` 会打开一个浏览器界面，可以像 Notebook 一样写查询。
2. **图形化工具**：DBeaver、VS Code 的 SQLTools 插件都能直接打开 `shop.duckdb`。
3. **Python**：`duckdb.connect("shop.duckdb").sql("SELECT ...").show()`

注意：命令行或图形工具正在打开 `shop.duckdb` 时，`check.py` 可能会因为文件被锁而报错，先关掉再判题。

## 做题与判题

题目都在 [exercises.md](exercises.md)。

```bash
python3 check.py 5 answers/q05.sql      # 判第 5 题
python3 check.py 5 -e "SELECT ..."      # 直接写 SQL 判题
python3 check.py 5 --peek               # 偷看答案结果的前几行
```

标准答案在 [solutions.sql](solutions.sql)，做完再看。

## 文件

| 文件 | 作用 |
|---|---|
| `exercises.md` | 题目、提示、平台差异、配合 AI 的练习方法 |
| `solutions.sql` | 标准答案 |
| `check.py` | 自动判题 |
| `generate_data.py` | 生成练习数据（只用 Python 标准库） |
| `setup.sql` / `build_db.py` | 建表并导入数据 |

## 数据

6 张业务表加 1 张 JSON 行为日志，时间范围 2025-01 至 2026-10：约 1.4 万笔订单、5.7 万行订单明细、2,900 条每周促销、2.7 万条 App 事件。
数据里刻意加入了季节性（12 月旺季、夏天草莓和冰淇淋卖得多）、周末高峰、促销拉动销量、常一起购买的商品组合，以及几类数据质量问题，这些在练习里都会遇到。
