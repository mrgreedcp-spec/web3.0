---
tags: [数据清洗, 问题类型, pandas]
created: 2026-11-05
updated: 2026-11-05
aliases: [inf, 除以零]
sources:
  - https://github.com/mrgreedcp-spec/web3.0/blob/claude/upbeat-allen-7jtgdz/pandas-learn/batch-sim/ISSUES.md
---
# 零运行时间与 inf

**pandas 里除以 0 不报错，直接得到 inf（无穷大）；接着平均值也悄悄变成 inf，要到算标准差时才出现警告。没有提示的错误，比报错更危险。**

## 实际表现（pandas 3.0.5 实测）
```python
r = df["input_kg"] / df["run_hours"]   # 有一行 run_hours 为 0
r.max()    # inf，没有任何提示
r.mean()   # inf，没有任何提示
r.std()    # 出现 RuntimeWarning，结果是 NaN
```

## 两种零运行时间，处理不同
| 情况 | 例子 | 判断 | 处理 |
|---|---|---|---|
| 有产出，却记了 0 小时 | SIM-20261005-L1：1135.1 kg、550.8 kWh | 前后矛盾，记录错误 | 设为缺失并加标记；**不删批次**，产出和能耗有效 |
| 0 产出、0 小时 | SIM-20261013-L3：只有 3.2 kWh | 像取消的批次 | 保留，标记 `cancelled`，算效率时排除 |

## 怎样计算指标才安全
只对“正常运行、数据齐全”的行计算，其余填 NaN：
```python
ok = ~df["cancelled"] & (df["run_hours"] > 0) & 三列都不缺
df["kg_per_hour"] = np.where(ok, df["input_kg"] / df["run_hours"], np.nan)
```
再用 assert 确认没有 inf，见 [[验收标准与 assert]]。

## 相关
- [[处理方式选择]]：“设为缺失”
- [[清洗步骤顺序]]：指标放在最后算
