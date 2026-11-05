---
tags: [数据清洗, pandas, 检查]
created: 2026-11-05
updated: 2026-11-05
aliases: [assert, 断言]
sources:
  - https://github.com/mrgreedcp-spec/web3.0/blob/claude/upbeat-allen-7jtgdz/pandas-learn/batch-sim/clean_batches.py
---
# 验收标准与 assert

**把“数据干净了”写成一条条可以检查的条件，再写成 assert：条件成立就放行，不成立就报错停下。**

## assert 是什么
```python
assert 条件, "条件不成立时显示的提示"
```
Python 的关键字，中文叫“断言”。像流水线上的质检员：合格就放行，不出声；不合格就立刻停线。

## 好的验收标准
- 能检查：“共 60 个批次”，而不是“数据干净了”
- 每条对应一个清洗步骤
- 包括“原始文件没被改动”

## 例子：模拟批次数据的 8 条
1. 原始文件的 SHA-256 不变
2. 每行都标注 `SIMULATED`
3. 共 60 个批次
4. 批次号唯一
5. 除取消批次外，没有运行时间为 0 的行
6. 合格产出不超过投入
7. 派生指标里没有 inf
8. 有标记的行都写进了 [[清洗日志]]

## 为什么不用 print 看
print 要靠人看，容易漏；assert 由机器判断。数据更新或脚本改动后重跑一次，有问题立刻报错。

## 注意
用 `python -O` 运行时会跳过所有 assert。生产程序里重要的检查写成 `if ...: raise ValueError(...)`。

## 相关
- [[清洗计划]]：验收标准写在计划第 5 项
- [[零运行时间与 inf]]：第 7 条
