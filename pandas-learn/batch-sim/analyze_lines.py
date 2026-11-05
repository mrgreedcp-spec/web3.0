"""比较三条产线（基于清洗后的【模拟】数据）。只读不改。

    python3 pandas-learn/batch-sim/analyze_lines.py

输出：
    终端里打印 6 节分析
    data/line_comparison.csv   每条产线的汇总指标（Excel 打开中文不乱码）

注意：数据是模拟的，结论反映的是生成数据时设定的参数，只用来练习分析方法。
"""

from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
CLEAN = HERE / "data" / "batches_clean_SIMULATED.csv"
OUT = HERE / "data" / "line_comparison.csv"
LINES = ["L1", "L2", "L3"]
SEED = 20261105  # 自助法抽样用的随机种子，保证每次结果一样


def title(n, text):
    print(f"\n{'=' * 10} {n}. {text} {'=' * 10}")


def load() -> pd.DataFrame:
    # CSV 不保存类型：日期、类别、空白标记都要在读的时候恢复
    df = pd.read_csv(CLEAN, parse_dates=["date"], dtype={"line": "category"})
    df["issue_flags"] = df["issue_flags"].fillna("")
    assert (df["data_label"] == "SIMULATED").all()
    return df


def weighted(ok: pd.DataFrame) -> pd.DataFrame:
    """加权指标：先把各批次加总，再相除。大批次的权重更大。"""
    s = ok.groupby("line", observed=True)[["input_kg", "good_output_kg", "run_hours", "energy_kwh"]].sum()
    return pd.DataFrame({
        "合格率": s["good_output_kg"] / s["input_kg"],
        "产能_kg每h": s["input_kg"] / s["run_hours"],
        "每小时能耗_kWh每h": s["energy_kwh"] / s["run_hours"],
        "单位产出能耗_kWh每kg": s["energy_kwh"] / s["good_output_kg"],
    })


def bootstrap_mean_ci(x, rng, n=10_000):
    """自助法：有放回地重复抽样 n 次，看平均值的 95% 范围。"""
    x = np.asarray(x)
    means = rng.choice(x, size=(n, len(x))).mean(axis=1)
    return np.percentile(means, [2.5, 97.5])


def bootstrap_diff_ci(a, b, rng, n=10_000):
    a, b = np.asarray(a), np.asarray(b)
    diff = rng.choice(a, size=(n, len(a))).mean(axis=1) - rng.choice(b, size=(n, len(b))).mean(axis=1)
    return np.percentile(diff, [2.5, 97.5])


def main() -> None:
    pd.set_option("display.width", 160)
    rng = np.random.default_rng(SEED)
    df = load()
    ok = df[df["ok_for_efficiency"]]

    # ------------------------------------------------------------------ 1
    title(1, "数据覆盖：每条产线有多少批次能用")
    cover = df.groupby("line", observed=True).agg(
        批次=("batch_id", "size"),
        可算效率=("ok_for_efficiency", "sum"),
        取消=("cancelled", "sum"),
        有标记=("issue_flags", lambda s: (s != "").sum()),
    )
    print(cover.to_string())
    print("→ 效率指标只用“可算效率”的批次。L2 只有 17 个，结论的把握略低。")

    # ------------------------------------------------------------------ 2
    title(2, "四个效率指标（加权）")
    w = weighted(ok)
    print(w.round({"合格率": 4, "产能_kg每h": 1, "每小时能耗_kWh每h": 1, "单位产出能耗_kWh每kg": 3}).to_string())
    simple = ok.groupby("line", observed=True)[["yield_rate", "kg_per_hour"]].mean()
    print("\n对比：简单平均（每个批次一票）")
    print(simple.rename(columns={"yield_rate": "合格率", "kg_per_hour": "产能_kg每h"}).round(4).to_string())
    print("→ 这里两种算法差别很小，因为各批次投入量差不多；批次大小差别大时，要用加权。")

    # ------------------------------------------------------------------ 3
    title(3, "排名：每个指标谁最好")
    better_high = {"合格率": True, "产能_kg每h": True, "每小时能耗_kWh每h": False, "单位产出能耗_kWh每kg": False}
    rank = pd.DataFrame({m: w[m].rank(ascending=not hi).astype(int) for m, hi in better_high.items()})
    print(rank.to_string())
    print("（1 = 最好。合格率、产能越高越好；能耗越低越好）")

    # ------------------------------------------------------------------ 4
    title(4, "单位产出能耗 = 每小时能耗 ÷（产能 × 合格率）")
    for line in LINES:
        r = w.loc[line]
        print(f"{line}: {r['每小时能耗_kWh每h']:.2f} ÷ ({r['产能_kg每h']:.2f} × {r['合格率']:.4f}) = "
              f"{r['每小时能耗_kWh每h'] / (r['产能_kg每h'] * r['合格率']):.4f} kWh/kg")
    print("→ L2 每小时耗电最少，但产得慢、合格率也低，摊到每公斤合格品上反而最费电。")

    # ------------------------------------------------------------------ 5
    title(5, "差距靠谱吗：自助法 95% 区间")
    ci_rows = []
    for col, name, k in [("yield_rate", "合格率", 100), ("kwh_per_kg", "单位产出能耗", 1)]:
        for line in LINES:
            lo, hi = bootstrap_mean_ci(ok.loc[ok["line"] == line, col], rng)
            ci_rows.append((name, line, lo * k, hi * k))
    for name, line, lo, hi in ci_rows:
        unit = "%" if name == "合格率" else " kWh/kg"
        print(f"  {name:6} {line}: [{lo:.3f}, {hi:.3f}]{unit}")
    print("\n两两相减的 95% 区间（不包含 0 → 差距可信）：")
    verdicts = []
    for col, name, k, unit in [("yield_rate", "合格率", 100, " 个百分点"), ("kwh_per_kg", "单位产出能耗", 1, " kWh/kg")]:
        for a, b in [("L1", "L2"), ("L2", "L3"), ("L1", "L3")]:
            lo, hi = bootstrap_diff_ci(ok.loc[ok["line"] == a, col], ok.loc[ok["line"] == b, col], rng) * k
            v = "可信" if lo > 0 or hi < 0 else "看不出差别"
            if v == "可信" and min(abs(lo), abs(hi)) < 0.2 * max(abs(lo), abs(hi)):
                v = "可信但很弱"  # 区间的一端离 0 很近
            verdicts.append((name, a, b, lo, hi, v))
            print(f"  {name:6} {a}−{b}: [{lo:+.3f}, {hi:+.3f}]{unit} → {v}")

    # ------------------------------------------------------------------ 6
    title(6, "稳定性：前 10 天 vs 后 10 天的合格率")
    half = np.where(ok["date"] < "2026-10-11", "前10天", "后10天")
    trend = ok.assign(时段=half).pivot_table(index="line", columns="时段", values="yield_rate",
                                             aggfunc="mean", observed=True)[["前10天", "后10天"]]
    trend["变化_百分点"] = (trend["后10天"] - trend["前10天"]) * 100
    print(trend.round(4).to_string())
    print(f"\n每条线合格率的标准差（百分点）：{(ok.groupby('line', observed=True)['yield_rate'].std() * 100).round(2).to_dict()}")
    print("→ 三条线都没有明显的上升或下降趋势，波动幅度也差不多。")

    # ------------------------------------------------------------------ 导出
    out = cover.join(w).join(trend[["变化_百分点"]].rename(columns={"变化_百分点": "合格率前后变化_百分点"}))
    out.round(4).to_csv(OUT, encoding="utf-8-sig")
    print(f"\n已导出 {OUT.name}（{len(out)} 行 × {out.shape[1]} 列）")


if __name__ == "__main__":
    main()
