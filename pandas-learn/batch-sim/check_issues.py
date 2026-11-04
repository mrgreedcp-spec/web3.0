"""按业务规则检查【模拟】批次数据，输出问题清单，并和注入记录核对。只读不改。

    python3 pandas-learn/batch-sim/check_issues.py

输出：
    data/issues_found.csv   问题清单（每个问题一行，可以用 Excel 打开）
    终端里打印清单，以及和 injected_issues_KEY.csv 的核对结果
"""

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
RAW = HERE / "data" / "batches_raw_SIMULATED.csv"
KEY = HERE / "data" / "injected_issues_KEY.csv"
OUT = HERE / "data" / "issues_found.csv"

REQUIRED = ["date", "batch_id", "line", "input_kg", "good_output_kg", "run_hours", "energy_kwh"]
NUMERIC = ["input_kg", "good_output_kg", "run_hours", "energy_kwh"]
YIELD_RANGE = (0.80, 1.00)  # 合格率的合理范围（模拟设定）
KWH_PER_H_TOL = 0.20  # 每小时能耗偏离本产线中位数超过 20% 算异常


def main() -> None:
    df = pd.read_csv(RAW)
    df["file_line"] = df.index + 2  # 在 CSV 文件里的行号（第 1 行是表头）
    issues: list[dict] = []

    def add(rule, row, column, value, why, action):
        issues.append(
            {
                "rule": rule,
                "file_line": int(row["file_line"]),
                "batch_id": row["batch_id"],
                "column": column,
                "value": value,
                "why": why,
                "suggested_action": action,
            }
        )

    # R0 标注：每行都必须标成模拟数据
    for _, r in df[df["data_label"] != "SIMULATED"].iterrows():
        add("R0 未标注模拟", r, "data_label", r["data_label"], "这份数据必须全部标注为模拟", "停止使用，查明来源")

    # R1 整行重复
    dup_all = df.drop(columns="file_line").duplicated(keep="first")
    for _, r in df[dup_all].iterrows():
        add("R1 整行重复", r, "全部列", "", "和上一行完全相同，像是重复录入", "确认后删除重复行，保留一行")

    # R2 批次号重复，但数值不同（去掉整行重复之后再看）
    rest = df[~dup_all]
    conflict = rest[rest["batch_id"].duplicated(keep=False)]
    for bid, g in conflict.groupby("batch_id"):
        diff_cols = [c for c in NUMERIC if g[c].nunique(dropna=False) > 1]
        vals = " / ".join(f"{c}={v}" for c in diff_cols for v in g[c])
        for _, r in g.iterrows():
            add("R2 批次号重复且数值不同", r, ",".join(diff_cols), vals,
                "同一批次有两条不同的记录，不知道哪条是对的", "向记录人确认哪条有效；不要自己挑一条")

    # R3 必填字段缺失
    for col in REQUIRED:
        for _, r in df[df[col].isna()].iterrows():
            add("R3 缺失值", r, col, "空", f"{col} 没有记录", "向记录人补录；补不到的话保留为空，并在分析时说明")

    # R4 运行时间为 0
    for _, r in df[df["run_hours"] == 0].iterrows():
        if r["good_output_kg"] > 0:
            why = f"有 {r['good_output_kg']} kg 合格产出和 {r['energy_kwh']} kWh 能耗，运行时间却是 0，自相矛盾"
            action = "多半是漏填或填错：向记录人核实；核实前设为缺失，不要直接删除"
        else:
            why = f"产出为 0，只有 {r['energy_kwh']} kWh 能耗，像是取消或没开机的批次"
            action = "确认是否为取消批次：是的话加标记，计算效率指标时排除"
        add("R4 零运行时间", r, "run_hours", 0, why, action)

    # R5 数值不能为负
    for col in NUMERIC:
        for _, r in df[df[col] < 0].iterrows():
            add("R5 负数", r, col, r[col], "重量、时间、能耗不可能为负", "查原因后修正")

    # R6 合格产出不能超过投入；合格率要在合理范围内（只看正常运行的批次）
    ran = df[(df["run_hours"] > 0) & df["good_output_kg"].notna()].copy()
    ran["yield_rate"] = ran["good_output_kg"] / ran["input_kg"]
    lo, hi = YIELD_RANGE
    for _, r in ran[(ran["yield_rate"] < lo) | (ran["yield_rate"] > hi)].iterrows():
        add("R6 合格率异常", r, "good_output_kg", f"合格率 {r['yield_rate']:.1%}",
            f"超出合理范围 {lo:.0%}–{hi:.0%}", "核对投入和产出的记录")

    # R7 每小时能耗异常：和本产线的中位数比
    ran = df[(df["run_hours"] > 0) & df["energy_kwh"].notna()].copy()
    ran["kwh_per_h"] = ran["energy_kwh"] / ran["run_hours"]
    med = ran.groupby("line")["kwh_per_h"].transform("median")
    off = (ran["kwh_per_h"] / med - 1).abs() > KWH_PER_H_TOL
    for _, r in ran[off].iterrows():
        add("R7 每小时能耗异常", r, "energy_kwh/run_hours", f"{r['kwh_per_h']:.1f} kWh/h",
            f"偏离本产线中位数超过 {KWH_PER_H_TOL:.0%}", "核对能耗表读数和运行时间")

    # R8 批次号要和日期、产线对得上：SIM-YYYYMMDD-Lx
    expected = "SIM-" + df["date"].str.replace("-", "", regex=False) + "-" + df["line"].astype(str)
    for _, r in df[df["batch_id"] != expected].iterrows():
        add("R8 批次号格式不符", r, "batch_id", r["batch_id"], "批次号和日期、产线对不上", "核对批次号")

    found = pd.DataFrame(issues).sort_values(["file_line", "rule"]).reset_index(drop=True)
    found.insert(0, "issue_no", range(1, len(found) + 1))
    found.to_csv(OUT, index=False, encoding="utf-8-sig")

    print(f"检查 {RAW.name}：{len(df)} 行，发现 {len(found)} 条问题记录，已写入 {OUT.name}\n")
    with pd.option_context("display.width", 200, "display.max_colwidth", 60, "display.max_columns", 10):
        print(found[["issue_no", "rule", "file_line", "batch_id", "column", "value"]].to_string(index=False))
    print("\n按规则汇总：")
    print(found["rule"].value_counts().sort_index().to_string())

    # 核对：注入的每个问题都应该被查出来
    key = pd.read_csv(KEY)
    rule_of = {"缺失值": "R3", "零运行时间": "R4", "整行重复": "R1", "批次号重复且数值不同": "R2"}
    found_pairs = set(zip(found["rule"].str[:2], found["batch_id"]))
    key["查出"] = [(rule_of[t], b) in found_pairs for t, b in zip(key["issue_type"], key["batch_id"])]
    print(f"\n和注入记录核对：注入 {len(key)} 处，查出 {key['查出'].sum()} 处")
    missed = key[~key["查出"]]
    if len(missed):
        print("漏查：")
        print(missed.to_string(index=False))
    else:
        print("全部查出 ✓")
    injected = {(rule_of[t], b) for t, b in zip(key["issue_type"], key["batch_id"])}
    extra = found[[(r[:2], b) not in injected for r, b in zip(found["rule"], found["batch_id"])]]
    print(f"注入之外的问题：{len(extra)} 条" + ("（数据本身的波动，要逐条判断）" if len(extra) else ""))
    if len(extra):
        print(extra[["issue_no", "rule", "batch_id", "value"]].to_string(index=False))


if __name__ == "__main__":
    main()
