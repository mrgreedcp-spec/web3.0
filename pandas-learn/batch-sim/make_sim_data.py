"""生成【模拟】生产批次数据（不含任何真实数据）。

    python3 pandas-learn/batch-sim/make_sim_data.py

输出：
    data/batches_raw_SIMULATED.csv   原始版本（含故意注入的问题），生成后不要手工修改
    data/injected_issues_KEY.csv     注入问题的“答案”，用来核对体检有没有漏查

说明：
- 所有数字由固定随机种子生成，重跑结果完全一样。
- 产线编号 L1/L2/L3、批次号、参数都是虚构的，不对应任何真实工厂、公司或客户。
- 每一行都带 data_label = SIMULATED，批次号也以 SIM- 开头，防止被误当成真实数据。
"""

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 20261104
HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

START, DAYS = "2026-10-01", 20  # 20 天 × 3 条产线 = 60 个批次

# 模拟参数（虚构）：产能 kg/h、平均合格率、功率 kW
LINES = {
    "L1": {"rate": 120, "yield": 0.95, "power": 55},
    "L2": {"rate": 100, "yield": 0.92, "power": 48},
    "L3": {"rate": 140, "yield": 0.90, "power": 62},
}
IDLE_KWH = 5.0  # 每批次的固定能耗：开机、预热

COLUMNS = ["data_label", "date", "batch_id", "line", "input_kg", "good_output_kg", "run_hours", "energy_kwh"]


def make_clean(rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for day in pd.date_range(START, periods=DAYS, freq="D"):
        for line, p in LINES.items():
            input_kg = rng.uniform(800, 1600)
            yield_ = np.clip(rng.normal(p["yield"], 0.015), 0.80, 0.99)
            run_hours = input_kg / p["rate"] * rng.uniform(0.95, 1.08)
            energy = run_hours * p["power"] * rng.uniform(0.95, 1.05) + IDLE_KWH
            rows.append(
                {
                    "data_label": "SIMULATED",
                    "date": day.strftime("%Y-%m-%d"),
                    "batch_id": f"SIM-{day:%Y%m%d}-{line}",
                    "line": line,
                    "input_kg": round(input_kg, 1),
                    "good_output_kg": round(input_kg * yield_, 1),
                    "run_hours": round(run_hours, 2),
                    "energy_kwh": round(energy, 1),
                }
            )
    return pd.DataFrame(rows, columns=COLUMNS)


def inject(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """注入少量问题，并记下注入了什么。"""
    df = df.copy()
    log: list[dict] = []

    def note(kind, batch_id, column, detail):
        log.append({"issue_type": kind, "batch_id": batch_id, "column": column, "detail": detail})

    # 1) 缺失值：4 个格子
    for idx, col in [(7, "good_output_kg"), (19, "run_hours"), (31, "energy_kwh"), (44, "energy_kwh")]:
        note("缺失值", df.at[idx, "batch_id"], col, f"原值 {df.at[idx, col]} 被清空")
        df[col] = df[col].astype("float64")
        df.at[idx, col] = np.nan

    # 2) 零运行时间：2 种情况
    i = 12  # 有产出、有能耗，却记成 0 小时 → 记录错误
    note("零运行时间", df.at[i, "batch_id"], "run_hours", f"原值 {df.at[i, 'run_hours']} 被改成 0，产出和能耗正常")
    df.at[i, "run_hours"] = 0.0
    i = 38  # 没开机：产出 0，只有少量待机能耗 → 可能是取消的批次
    note("零运行时间", df.at[i, "batch_id"], "run_hours/good_output_kg/energy_kwh",
         "改成 0 小时、0 合格产出、3.2 kWh 待机能耗（像取消的批次）")
    df.at[i, "run_hours"], df.at[i, "good_output_kg"], df.at[i, "energy_kwh"] = 0.0, 0.0, 3.2

    # 3) 重复：2 行完全重复 + 1 个批次号重复但数值不同（像二次录入时改过数）
    extra = []
    for i in [5, 27]:
        note("整行重复", df.at[i, "batch_id"], "全部列", "整行被录入了两次")
        extra.append((i, df.loc[i].copy()))
    i = 50
    corrected = df.loc[i].copy()
    corrected["good_output_kg"] = round(corrected["good_output_kg"] - 40.0, 1)
    note("批次号重复且数值不同", df.at[i, "batch_id"], "good_output_kg",
         f"同一批次出现两次：{df.at[i, 'good_output_kg']} 和 {corrected['good_output_kg']}")
    extra.append((i, corrected))

    # 重复行紧跟在原行后面，像真实的重复录入
    parts, last = [], 0
    for i, row in sorted(extra, key=lambda x: x[0]):
        parts.append(df.iloc[last : i + 1])
        parts.append(row.to_frame().T)
        last = i + 1
    parts.append(df.iloc[last:])
    out = pd.concat(parts, ignore_index=True)[COLUMNS]
    return out, log


def main() -> None:
    rng = np.random.default_rng(SEED)
    clean = make_clean(rng)
    raw, log = inject(clean)

    DATA.mkdir(exist_ok=True)
    raw_path = DATA / "batches_raw_SIMULATED.csv"
    key_path = DATA / "injected_issues_KEY.csv"
    raw.to_csv(raw_path, index=False)
    pd.DataFrame(log).to_csv(key_path, index=False)

    print(f"已生成 {raw_path.relative_to(HERE.parent.parent)}：{len(raw)} 行（{len(clean)} 个批次 + {len(raw) - len(clean)} 行重复）")
    print(f"已生成 {key_path.relative_to(HERE.parent.parent)}：注入了 {len(log)} 处问题")
    for item in log:
        print(f"  - [{item['issue_type']}] {item['batch_id']} / {item['column']}：{item['detail']}")


if __name__ == "__main__":
    main()
