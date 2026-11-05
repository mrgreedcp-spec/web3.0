# 模拟生产批次数据（今日里程碑：读懂并清洗数据）

> ⚠️ **这里的所有数据都是模拟数据（SIMULATED）**：由脚本用固定随机种子生成，不含任何真实或机密信息，也不涉及任何真实或虚构的客户。

## 验收清单

| 要求 | 交付物 | 状态 |
|---|---|---|
| 一份模拟 CSV（≥ 50 条，明确标注为模拟） | [`data/batches_raw_SIMULATED.csv`](data/batches_raw_SIMULATED.csv)：60 个批次 + 3 行重复 = 63 行。每行都有 `data_label = SIMULATED`，批次号以 `SIM-` 开头，文件名也带 `SIMULATED` | ✅ |
| 包含日期、批次、产线、投入 kg、合格产出 kg、运行小时、能耗 kWh | 字段依次为 `date`、`batch_id`、`line`、`input_kg`、`good_output_kg`、`run_hours`、`energy_kwh` | ✅ |
| 少量缺失、重复和零运行时间 | 4 个缺失值、2 行整行重复、1 个批次号重复但数值不同、2 个零运行时间 | ✅ |
| 保存原始版本 | 原始文件生成后不修改，SHA-256 见下方，可随时校验 | ✅ |
| 一份字段说明 | [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md) | ✅ |
| 一份问题清单 | [`ISSUES.md`](ISSUES.md)（给人看），[`data/issues_found.csv`](data/issues_found.csv)（给机器读） | ✅ |
| 不使用真实机密，不虚构客户经历 | 产线、批次、参数全部虚构，数据里没有任何客户、人员或公司信息 | ✅ |

## 目录

```
batch-sim/
├── README.md                 # 本文件：步骤指导和验收清单
├── DATA_DICTIONARY.md        # 字段说明
├── ISSUES.md                 # 问题清单（含处理建议）
├── CLEANING_PLAN.md          # 清洗计划（本次的计划 + 空白模板）
├── make_sim_data.py          # 生成模拟数据
├── check_issues.py           # 按业务规则检查，并和注入记录核对
├── clean_batches.py          # 一步一步清洗（可以用 --step N 停在任意一步）
└── data/
    ├── batches_raw_SIMULATED.csv   # 原始版本，不要手工修改
    ├── injected_issues_KEY.csv     # 注入问题的“答案”，用来核对
    ├── issues_found.csv            # 检查结果
    ├── batches_clean_SIMULATED.csv # 清洗后的数据：60 行，带标记列和派生指标
    └── cleaning_log.csv            # 清洗日志：每一处改动的记录
```

## 怎么运行

```bash
python3 pandas-learn/batch-sim/make_sim_data.py
```

```bash
python3 pandas-learn/batch-sim/check_issues.py
```

```bash
python3 pandas-learn/main.py inspect pandas-learn/batch-sim/data/batches_raw_SIMULATED.csv
```

第一条重新生成数据（结果和现有文件完全一样），第二条按业务规则检查，第三条用通用体检工具做交叉检查。

校验原始文件有没有被改过：

```bash
echo "de9417aec2b4880c6fa9230b12b58dbf90623b7d47c40cd395c816c0df49dcee  pandas-learn/batch-sim/data/batches_raw_SIMULATED.csv" | sha256sum -c
```

输出 `OK` 就说明原始文件没有被改动过。

## 步骤指导：这份数据是怎么做出来的

以后要做类似的模拟数据，可以照着这 7 步走。

### 第 1 步：先定字段和含义，再写代码
先想清楚三件事：**每行代表什么**（一个批次）、**每列的单位**（kg、h、kWh）、**哪一列是主键**（`batch_id`）。然后把它们写进数据字典。

### 第 2 步：数字之间要有合理的关系
不能每一列各自随机。这份数据里：
- 运行时间 = 投入量 ÷ 产能
- 合格产出 = 投入量 × 合格率
- 能耗 = 运行时间 × 功率 + 开机能耗

这样生成的数据才像真的，之后检查“每小时能耗”“合格率”这些规则时才有意义。

### 第 3 步：明确标注“模拟”
用三重标注，确保不会被误当成真实数据：
- **文件名**带 `SIMULATED`
- **每一行**都有 `data_label = SIMULATED`
- **批次号**以 `SIM-` 开头

### 第 4 步：固定随机种子
代码里写 `np.random.default_rng(20261104)`，**谁重跑都得到一模一样的文件**。这样别人可以复现你的结果。

### 第 5 步：先生成干净数据，再故意注入问题，并记下“答案”
先生成 60 条没有问题的数据，再有意识地注入少量问题，同时把注入了什么写进 `injected_issues_KEY.csv`。**有了答案，才能检验检查脚本有没有漏查。**

### 第 6 步：保存原始版本，以后不再改它
原始文件生成后就不再改动，清洗结果另存成新文件。用 SHA-256 校验值随时可以确认原始文件没被动过。

### 第 7 步：两层检查，并和答案核对
1. **通用体检**（`main.py inspect`）：找格式上的问题
2. **业务规则检查**（`check_issues.py`）：找业务上不合理的地方，比如运行 0 小时却有产出

核对结果：**注入 9 处，查出 9 处，没有误报。**

## 清洗

先写计划，再写脚本：处理决定、步骤顺序和验收标准都在 [`CLEANING_PLAN.md`](CLEANING_PLAN.md) 里，文件末尾附有空白模板。

```bash
python3 pandas-learn/batch-sim/clean_batches.py
```

```bash
python3 pandas-learn/batch-sim/clean_batches.py --step 3
```

第一条跑完全部 8 步并导出，第二条只跑到第 3 步，打印当时的数据（用来一步一步学）。

| 步骤 | 做什么 | 对应问题 | 行数变化 |
|---|---|---|---|
| 1 | 读取，`raw.copy()` 复制一份，记下原始行号 | — | 63 |
| 2 | 删除整行重复 | #1 #2 | 63 → 61 |
| 3 | 批次号冲突：按确认表 `CONFIRMED` 保留已确认的那条（SIM-20261017-L3 保留 840.9）；没有确认结果的才按假设处理 | #3 | 61 → 60 |
| 4 | 零运行时间：有产出的改为缺失并标记；无产出的标记为取消 | #8 #9 | 60 |
| 5 | 缺失值不填补，只标记 | #4–#7 | 60 |
| 6 | 整理类型，计算合格率、产能、能耗等指标（只算数据齐全的 54 个批次，不会出现 inf） | — | 60 |
| 7 | 用 `assert` 校验 10 项：原始文件没被改动、行数对账、每个问题都按计划处理等 | — | 60 |
| 8 | 导出清洗后的数据和清洗日志 | — | 60 |

新增的列：`issue_flags`（这一行有什么问题）、`cancelled`（是否为取消批次）、`ok_for_efficiency`（能不能用来算效率），以及 4 个派生指标 `yield_rate`、`kg_per_hour`、`kwh_per_hour`、`kwh_per_kg`。
