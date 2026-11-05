"""一步一步清洗【模拟】批次数据。原始文件只读，结果另存。

    python3 pandas-learn/batch-sim/clean_batches.py            # 跑完全部 8 步并导出
    python3 pandas-learn/batch-sim/clean_batches.py --step 3   # 只跑到第 3 步，看当时的数据

8 个步骤（对应 ISSUES.md 的问题清单）：
    1 读取，复制一份，记下每行在原始文件里的行号
    2 删除整行重复                     → 问题 #1 #2
    3 处理“批次号重复且数值不同”       → 问题 #3（练习用的假设：保留后录入的那条）
    4 处理零运行时间                   → 问题 #8 #9
    5 缺失值：不填补，只做标记         → 问题 #4–#7
    6 整理类型，计算派生指标（不允许出现 inf）
    7 用 assert 校验
    8 导出清洗后的数据和清洗日志

输出（第 8 步）：
    data/batches_clean_SIMULATED.csv   清洗后的数据
    data/cleaning_log.csv              每一处改动的记录：哪一步、哪个批次、改了什么、为什么
"""

import argparse
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RAW = HERE / "data" / "batches_raw_SIMULATED.csv"
CLEAN = HERE / "data" / "batches_clean_SIMULATED.csv"
LOG = HERE / "data" / "cleaning_log.csv"
RAW_SHA256 = "de9417aec2b4880c6fa9230b12b58dbf90623b7d47c40cd395c816c0df49dcee"

SHOW = ["raw_line", "batch_id", "input_kg", "good_output_kg", "run_hours", "energy_kwh"]
log: list[dict] = []  # 清洗日志


def record(step, batch_id, action, before, after, reason):
    log.append({"step": step, "batch_id": batch_id, "action": action,
                "before": before, "after": after, "reason": reason})


def title(n, text):
    print(f"\n{'=' * 10} 第 {n} 步：{text} {'=' * 10}")


def add_flag(df, mask, flag):
    """在 issue_flags 列里追加一个标记，多个标记用 ; 隔开。"""
    df.loc[mask, "issue_flags"] = (df.loc[mask, "issue_flags"] + ";" + flag).str.strip(";")


# ---------------------------------------------------------------- 第 1 步
def step1_load() -> pd.DataFrame:
    title(1, "读取，复制一份，记下原始行号")
    raw = pd.read_csv(RAW, parse_dates=["date"])
    df = raw.copy()  # 之后所有修改都在 df 上，raw 不动
    df.insert(0, "raw_line", df.index + 2)  # 原始 CSV 里的行号（第 1 行是表头），方便追溯
    df["issue_flags"] = ""  # 用来记录每行有什么问题
    print(f"读入 {len(df)} 行 × {raw.shape[1]} 列；date 已转成 {df['date'].dtype}")
    print(f"每行都标注为模拟数据：{(df['data_label'] == 'SIMULATED').all()}")
    return df


# ---------------------------------------------------------------- 第 2 步
def step2_exact_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    title(2, "删除整行重复")
    cols = [c for c in df.columns if c not in ("raw_line", "issue_flags")]  # 比较时不看行号
    dup = df.duplicated(subset=cols, keep="first")
    print(f"找到 {dup.sum()} 行和前面某行完全相同：")
    print(df.loc[dup, SHOW].to_string(index=False))
    for _, r in df[dup].iterrows():
        record(2, r["batch_id"], "删除整行重复", f"原始第 {r['raw_line']} 行", "已删除", "与上一行完全相同")
    df = df[~dup]
    print(f"删除后剩 {len(df)} 行")
    return df


# ---------------------------------------------------------------- 第 3 步
def step3_conflicting_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    title(3, "处理“批次号重复且数值不同”")
    conflict = df[df["batch_id"].duplicated(keep=False)]
    print("同一个批次号还有多条记录：")
    print(conflict[SHOW].to_string(index=False))
    # 真实工作中要问记录人。这里是练习，假设“后录入的是更正后的数据”，并写进日志
    drop = df["batch_id"].duplicated(keep="last")
    for _, r in df[drop].iterrows():
        kept = df[(df["batch_id"] == r["batch_id"]) & ~drop].iloc[0]
        record(3, r["batch_id"], "删除冲突记录（假设）",
               f"原始第 {r['raw_line']} 行 good_output_kg={r['good_output_kg']}",
               f"保留原始第 {kept['raw_line']} 行 good_output_kg={kept['good_output_kg']}",
               "【假设】后录入的是更正后的数据；真实数据必须向记录人确认")
    df = df[~drop].copy()
    add_flag(df, df["batch_id"].isin(conflict["batch_id"]), "冲突记录_按假设保留")
    print(f"按假设保留后录入的那条，剩 {len(df)} 行；批次号已唯一：{df['batch_id'].is_unique}")
    return df


# ---------------------------------------------------------------- 第 4 步
def step4_zero_run_hours(df: pd.DataFrame) -> pd.DataFrame:
    title(4, "处理零运行时间")
    zero = df["run_hours"] == 0
    print(df.loc[zero, SHOW].to_string(index=False))

    # 情况 A：有产出却是 0 小时 → 记录错误。改成缺失（未知），不删除这个批次
    a = zero & (df["good_output_kg"] > 0)
    for _, r in df[a].iterrows():
        record(4, r["batch_id"], "run_hours 改为缺失", 0, "空",
               f"有 {r['good_output_kg']} kg 产出却记 0 小时，前后矛盾，视为记录错误")
    df.loc[a, "run_hours"] = np.nan
    add_flag(df, a, "run_hours_原为0_疑似错误")

    # 情况 B：0 小时、0 产出 → 视为取消的批次。保留，加标记
    b = zero & (df["good_output_kg"] == 0)
    df["cancelled"] = b
    for _, r in df[b].iterrows():
        record(4, r["batch_id"], "标记为取消批次", "cancelled=False", "cancelled=True",
               f"0 小时、0 产出，只有 {r['energy_kwh']} kWh 待机能耗")
    add_flag(df, b, "取消批次")
    print(f"情况 A（有产出、0 小时）：{a.sum()} 个 → run_hours 改为缺失，并加标记")
    print(f"情况 B（无产出、0 小时）：{b.sum()} 个 → 标记 cancelled=True，保留原值")
    return df


# ---------------------------------------------------------------- 第 5 步
def step5_missing(df: pd.DataFrame) -> pd.DataFrame:
    title(5, "缺失值：不填补，只做标记")
    for col in ["good_output_kg", "run_hours", "energy_kwh"]:
        miss = df[col].isna()
        new = miss & ~df["issue_flags"].str.contains(f"{col}_", regex=False)  # 第 4 步已经标过的不重复标
        for _, r in df[new].iterrows():
            record(5, r["batch_id"], f"{col} 缺失，保留为空", "空", "空", "生产记录不凭空填补，等待补录")
        add_flag(df, new, f"{col}_缺失")
    print("各列缺失个数（第 4 步改出来的 1 个也算在内）：")
    print(df[["good_output_kg", "run_hours", "energy_kwh"]].isna().sum().to_string())
    print("\n有标记的行：")
    print(df.loc[df["issue_flags"] != "", ["batch_id", "issue_flags"]].to_string(index=False))
    return df


# ---------------------------------------------------------------- 第 6 步
def step6_types_and_metrics(df: pd.DataFrame) -> pd.DataFrame:
    title(6, "整理类型，计算派生指标")
    df["line"] = df["line"].astype("category")
    # 只有“正常运行、数据齐全”的批次才能算效率指标
    df["ok_for_efficiency"] = (
        ~df["cancelled"]
        & (df["run_hours"] > 0)
        & df[["good_output_kg", "run_hours", "energy_kwh"]].notna().all(axis=1)
    )
    ok = df["ok_for_efficiency"]
    df["yield_rate"] = np.where(ok, df["good_output_kg"] / df["input_kg"], np.nan).round(4)
    df["kg_per_hour"] = np.where(ok, df["input_kg"] / df["run_hours"], np.nan).round(1)
    df["kwh_per_hour"] = np.where(ok, df["energy_kwh"] / df["run_hours"], np.nan).round(1)
    df["kwh_per_kg"] = np.where(ok, df["energy_kwh"] / df["good_output_kg"], np.nan).round(3)
    print(f"可以计算效率指标的批次：{ok.sum()} / {len(df)}")
    print(f"派生指标里的 inf 个数：{np.isinf(df[['yield_rate', 'kg_per_hour', 'kwh_per_hour', 'kwh_per_kg']]).sum().sum()}")
    print("\n各产线指标（只用可计算的批次）：")
    summary = df[ok].groupby("line", observed=True).agg(
        批次数=("batch_id", "count"),
        平均合格率=("yield_rate", "mean"),
        平均产能_kg每小时=("kg_per_hour", "mean"),
        平均每小时能耗=("kwh_per_hour", "mean"),
        平均单位产出能耗=("kwh_per_kg", "mean"),
    ).round(3)
    print(summary.to_string())
    return df


# ---------------------------------------------------------------- 第 7 步
def step7_validate(df: pd.DataFrame) -> pd.DataFrame:
    title(7, "用 assert 校验")
    metrics = ["yield_rate", "kg_per_hour", "kwh_per_hour", "kwh_per_kg"]
    checks = {
        "原始文件没有被改动": hashlib.sha256(RAW.read_bytes()).hexdigest() == RAW_SHA256,
        "每行都标注为模拟数据": (df["data_label"] == "SIMULATED").all(),
        "共 60 个批次": len(df) == 60,
        "批次号唯一": df["batch_id"].is_unique,
        "没有运行时间为 0 却不是取消批次的行": not ((df["run_hours"] == 0) & ~df["cancelled"]).any(),
        "合格产出不超过投入": (df["good_output_kg"].dropna() <= df.loc[df["good_output_kg"].notna(), "input_kg"]).all(),
        "派生指标里没有 inf": not np.isinf(df[metrics]).any().any(),
        "有标记的行都写进了清洗日志": set(df.loc[df["issue_flags"] != "", "batch_id"]) <= {x["batch_id"] for x in log},
        # 对账：原始行数 = 现在的行数 + 日志里记录删除的行数
        "行数对得上账（原始 = 现在 + 已删除）": len(pd.read_csv(RAW)) == len(df) + sum("删除" in x["action"] for x in log),
        # 问题清单里的每个问题，都按计划的方式处理了（防止某一步被跳过、问题被别的步骤“顺手”处理掉）
        "每个问题都按计划处理": plan_matches_log(),
    }
    # 先把所有检查都打印出来，再统一判断，这样一次能看到所有失败的项
    for name, ok in checks.items():
        print(f"  {'✓' if ok else '✗'} {name}")
    failed = [name for name, ok in checks.items() if not ok]
    assert not failed, f"校验失败：{failed}"
    print("全部通过")
    return df


# 问题清单里的规则 → 计划中对应的处理动作（见 CLEANING_PLAN.md 第 3 项）
PLANNED_ACTION = {
    "R1": ("删除整行重复",),
    "R2": ("删除冲突记录（假设）",),
    "R3": ("缺失，保留为空",),
    "R4": ("run_hours 改为缺失", "标记为取消批次"),
}


def plan_matches_log() -> bool:
    """问题清单（check_issues.py 的结果）和清洗日志逐条对账。"""
    issues = pd.read_csv(HERE / "data" / "issues_found.csv")
    expected = {(r["batch_id"], r["rule"][:2]) for _, r in issues.iterrows()}
    done = set()
    for x in log:
        for rule, actions in PLANNED_ACTION.items():
            if any(a in x["action"] for a in actions):
                done.add((x["batch_id"], rule))
    if expected != done:
        print(f"    计划了但没按计划处理：{sorted(expected - done)}")
        print(f"    处理了但不在计划里：{sorted(done - expected)}")
    return expected == done


# ---------------------------------------------------------------- 第 8 步
def step8_export(df: pd.DataFrame) -> pd.DataFrame:
    title(8, "导出")
    out = df.drop(columns=["raw_line"]).sort_values(["date", "line"])
    out.to_csv(CLEAN, index=False)
    pd.DataFrame(log).to_csv(LOG, index=False, encoding="utf-8-sig")
    print(f"{CLEAN.name}：{out.shape[0]} 行 × {out.shape[1]} 列")
    print(f"{LOG.name}：{len(log)} 条改动记录")
    print(f"原始文件 {RAW.name} 未改动")
    return df


STEPS = [step2_exact_duplicates, step3_conflicting_duplicates, step4_zero_run_hours,
         step5_missing, step6_types_and_metrics, step7_validate, step8_export]


def main() -> None:
    parser = argparse.ArgumentParser(description="一步一步清洗模拟批次数据")
    parser.add_argument("--step", type=int, default=8, choices=range(1, 9), help="运行到第几步（1–8），默认全部")
    args = parser.parse_args()

    df = step1_load()
    for fn in STEPS[: args.step - 1]:
        df = fn(df)

    if args.step < 8:
        print(f"\n—— 停在第 {args.step} 步，没有导出文件。当前 {len(df)} 行，前 5 行：")
        with pd.option_context("display.width", 160, "display.max_columns", 20):
            print(df.head())


if __name__ == "__main__":
    main()
