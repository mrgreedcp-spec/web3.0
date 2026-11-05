# 资产清单

> 这个学习项目里做出来的所有数据、工具、文档、模板和笔记。所有数据都是模拟数据或公开数据，不含任何真实或机密信息。
> Obsidian 里有同样的清单（`obsidian-wiki/数据清洗 Wiki/资产/资产清单.md`），并和讲解笔记、代码片段互相链接。

## 数据集

| 名称 | 位置 | 用途 | 怎么复用 |
|---|---|---|---|
| 销售订单示例 | [`data/sales.csv`](data/sales.csv) | 12 笔订单，含 1 个缺失件数、1 个缺失客户编号 | 练习筛选、分组、合并 |
| 客户表 | [`data/customers.csv`](data/customers.csv) | 5 位客户及会员等级 | 练习 merge |
| 泰坦尼克号乘客（公开数据） | [`data/titanic.csv`](data/titanic.csv) | 891 行，pandas 官方教程数据 | 练习读取和完整清洗 |
| 故意弄脏的订单表 | [`data/messy_orders.csv`](data/messy_orders.csv) | 12 行，埋了 13 个格式问题 | 试用体检工具 |
| 模拟批次 · 原始 | [`batch-sim/data/batches_raw_SIMULATED.csv`](batch-sim/data/batches_raw_SIMULATED.csv) | 63 行模拟生产记录，含 9 处注入问题；只读 | 练习检查和清洗 |
| 模拟批次 · 答案 | [`batch-sim/data/injected_issues_KEY.csv`](batch-sim/data/injected_issues_KEY.csv) | 注入了哪 9 处问题 | 检验检查脚本有没有漏查 |
| 模拟批次 · 问题记录 | [`batch-sim/data/issues_found.csv`](batch-sim/data/issues_found.csv) | 按业务规则查出的 10 条问题记录 | 清洗计划的输入；第 7 步对账 |
| 模拟批次 · 清洗结果 | [`batch-sim/data/batches_clean_SIMULATED.csv`](batch-sim/data/batches_clean_SIMULATED.csv) | 60 行 × 15 列，带标记和指标 | 后续分析的起点 |
| 模拟批次 · 清洗日志 | [`batch-sim/data/cleaning_log.csv`](batch-sim/data/cleaning_log.csv) | 9 条改动记录 | 追溯每一处改动 |

## 工具

| 名称 | 位置 | 用途 | 怎么复用 |
|---|---|---|---|
| 统一入口 | [`main.py`](main.py) | 环境检查、运行学习模块、体检任意 CSV | `python3 pandas-learn/main.py inspect 文件.csv` |
| 通用 CSV 体检 | [`inspect_csv.py`](inspect_csv.py) | 自动识别编码和分隔符，输出 9 节报告和问题清单 | 拿到任何新 CSV 先跑一次 |
| 模拟数据生成器 | [`batch-sim/make_sim_data.py`](batch-sim/make_sim_data.py) | 固定种子生成数据并注入问题、写答案 | 改参数生成新的练习数据 |
| 业务规则检查 | [`batch-sim/check_issues.py`](batch-sim/check_issues.py) | R0–R8 逐条检查，并和答案核对 | 改规则用于新数据 |
| 分步清洗脚本 | [`batch-sim/clean_batches.py`](batch-sim/clean_batches.py) | 8 步清洗，`--step N` 可停在任意一步 | 新项目照着它的结构写 |
| 学习模块 00–06 | [`modules/`](modules/) | 读取、筛选、清洗、分组、合并、完整清洗 | `python3 pandas-learn/main.py 03` |

## 文档

| 名称 | 位置 | 用途 | 怎么复用 |
|---|---|---|---|
| CSV 速查 | [`CSV_TIPS.md`](CSV_TIPS.md) | CSV 规则、read_csv 参数、常见报错 | 遇到读取问题时查 |
| 数据字典 | [`batch-sim/DATA_DICTIONARY.md`](batch-sim/DATA_DICTIONARY.md) | 字段、单位、范围、派生指标、业务规则 | 照着结构写新数据的字典 |
| 问题清单 | [`batch-sim/ISSUES.md`](batch-sim/ISSUES.md) | 9 处问题、影响、建议、状态 | 照着结构写新数据的问题清单 |
| 清洗计划 | [`batch-sim/CLEANING_PLAN.md`](batch-sim/CLEANING_PLAN.md) | 本次计划 + 空白模板 | 复制模板部分 |

## 模板

| 名称 | 位置 | 用途 | 怎么复用 |
|---|---|---|---|
| 清洗计划模板 | `Wiki：模板/模板 · 清洗计划`（Obsidian） | 七项内容逐项填空 | 复制笔记后填写 |
| 数据字典模板 | `Wiki：模板/模板 · 数据字典`（Obsidian） | 基本信息、字段、指标、规则 | 复制笔记后填写 |
| 问题清单模板 | `Wiki：模板/模板 · 问题清单`（Obsidian） | 汇总、明细、影响 | 复制笔记后填写 |

## 笔记

| 名称 | 位置 | 用途 | 怎么复用 |
|---|---|---|---|
| 数据清洗 Wiki | [`obsidian-wiki/`](obsidian-wiki/) | 方法、概念、讲解、项目、资产 | 放进 Obsidian |

## 拿到一份新数据时，按这个顺序用
1. 体检：`python3 pandas-learn/main.py inspect 新文件.csv`
2. 写数据字典、问题清单、清洗计划：复制 Wiki 里的三个模板
3. 写清洗脚本：照着 `batch-sim/clean_batches.py` 的结构
4. 校验并导出：至少包括“原始文件没被改动”“行数对账”“每个问题都按计划处理”
