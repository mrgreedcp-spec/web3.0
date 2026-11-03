"""通用 CSV 体检：只读不改，输出数据概况和问题清单。

用法：
    python3 pandas-learn/main.py inspect 文件.csv
    python3 pandas-learn/main.py inspect 文件.csv --encoding gbk --sep ";"
    python3 pandas-learn/inspect_csv.py 文件.csv            # 也可以直接运行

不指定 --encoding / --sep 时会自动识别。想把报告存下来：
    python3 pandas-learn/main.py inspect 文件.csv > 报告.txt
"""

import argparse
import csv
import re
import sys
import warnings
from pathlib import Path

import pandas as pd

ENCODINGS = ["utf-8-sig", "gbk"]  # utf-8-sig 同时兼容带 BOM 和不带 BOM 的 UTF-8
# pandas 默认不会当作缺失、但实际常用来表示“没有”的写法
PLACEHOLDERS = {"-", "--", "—", "?", "？", "/", "无", "空", "未知", "暂无", "缺失", "不详"}
MAX_CATEGORIES = 20  # 唯一值不超过这个数的文本列，当作类别列展示取值


def section(title: str) -> None:
    print(f"\n{'=' * 8} {title} {'=' * 8}")


def detect_encoding(path: Path) -> str:
    data = path.read_bytes()
    for enc in ENCODINGS:
        try:
            data.decode(enc)
            return enc
        except UnicodeDecodeError:
            continue
    return "latin1"  # 兜底：一定能读，但中文会乱码


def detect_sep(path: Path, encoding: str) -> str:
    with open(path, encoding=encoding, errors="replace") as f:
        sample = "".join(f.readline() for _ in range(20))
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
    except csv.Error:
        return ","


def show_sep(sep: str) -> str:
    return {"\t": "制表符 \\t", ",": "逗号 ,", ";": "分号 ;", "|": "竖线 |"}.get(sep, repr(sep))


def is_text(s: pd.Series) -> bool:
    return not (
        pd.api.types.is_numeric_dtype(s)
        or pd.api.types.is_bool_dtype(s)
        or pd.api.types.is_datetime64_any_dtype(s)
    )


def inspect(path: Path, encoding: str | None, sep: str | None) -> int:
    if not path.exists():
        print(f"找不到文件：{path}\n提示：相对路径是相对于【运行命令时所在的目录】。")
        return 1

    auto_enc, auto_sep = encoding is None, sep is None
    encoding = encoding or detect_encoding(path)
    sep = sep or detect_sep(path, encoding)
    read = dict(encoding=encoding, sep=sep)
    try:
        df = pd.read_csv(path, **read)
        # 再按“全部当文本、不做缺失转换”读一遍，用来检查原始写法（空格、开头的 0、占位符）
        raw = pd.read_csv(path, dtype=str, keep_default_na=False, **read)
    except pd.errors.EmptyDataError:
        print("文件是空的，或者只有空行。")
        return 1
    except pd.errors.ParserError as e:
        print(f"读取失败（ParserError）：{e}")
        print("常见原因：分隔符不对，或某个字段里有逗号却没加引号。可以试试 --sep 指定分隔符。")
        return 1

    issues: list[str] = []  # 问题清单，每条是 “问题 → 建议”

    def issue(text: str) -> None:
        issues.append(text)

    def check_numbers(c: str, s: pd.Series) -> None:
        """负数、0、极端值检查。s 是去掉缺失后的数字。"""
        if len(s) == 0:
            return
        neg, zero = int((s < 0).sum()), int((s == 0).sum())
        if neg:
            issue(f"[{c}] 有 {neg} 个负数 → 确认负数在业务上是否合理（如退款），不合理就查原因")
        if zero and zero / len(s) < 0.1 and s.nunique() > 2:  # 0 很少见时才可疑；人数类的列 0 很常见
            issue(f"[{c}] 有 {zero} 个 0 → 确认 0 是真实值还是“没填”；是真实值就加标记列，是没填就改成缺失")
        if len(s) >= 10:
            q1, q3 = s.quantile([0.25, 0.75])
            iqr = q3 - q1
            if iqr > 0:
                out = s[(s < q1 - 3 * iqr) | (s > q3 + 3 * iqr)]
                if len(out):
                    issue(f"[{c}] 有 {len(out)} 个极端值（最大的是 {out.max():g}）→ 先查原因，真实的保留并加标记，错误的再修正")

    converted: set[str] = set()  # 被识别为“数字/日期存成了文本”的列

    # ---------- 1. 基本信息 ----------
    section("1. 基本信息")
    print(f"文件    ：{path}")
    print(f"编码    ：{encoding}" + ("（自动识别）" if auto_enc else ""))
    print(f"分隔符  ：{show_sep(sep)}" + ("（自动识别）" if auto_sep else ""))
    print(f"行 × 列 ：{df.shape[0]} 行 × {df.shape[1]} 列")
    print(f"内存    ：{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    if encoding == "latin1":
        issue("编码无法识别为 UTF-8 / GBK，中文可能是乱码 → 向数据提供方确认编码，用 --encoding 指定")
    if df.shape[1] == 1 and df.shape[0] > 0:
        issue("只读出 1 列，分隔符可能不对 → 打开原文看看用的是什么分隔符，用 --sep 指定")

    bad_names = [c for c in df.columns if c != c.strip()]
    if bad_names:
        issue(f"列名前后有空格：{bad_names} → df.columns = df.columns.str.strip()，或 read_csv(..., skipinitialspace=True)")
    unnamed = [c for c in df.columns if c.startswith("Unnamed:")]
    if unnamed:
        issue(f"有没有列名的列 {unnamed}（常见于导出时多写了行号）→ 确认是否需要；不需要就 drop，或 read_csv(..., index_col=0)")

    # ---------- 2. 前后几行 ----------
    with pd.option_context("display.width", 160, "display.max_columns", 12, "display.max_colwidth", 30):
        section("2. 前 3 行 head(3)")
        print(df.head(3))
        section("3. 后 3 行 tail(3)")
        print(df.tail(3))

    # ---------- 4. 每列概览 ----------
    section("4. 每列概览")
    n = len(df)
    overview = pd.DataFrame(
        {
            "类型": df.dtypes.astype(str),
            "非空": df.notna().sum(),
            "缺失": df.isna().sum(),
            "缺失%": (df.isna().mean() * 100).round(1),
            "唯一值": df.nunique(),
            "示例": [", ".join(map(str, df[c].dropna().unique()[:3]))[:40] for c in df.columns],
        }
    )
    with pd.option_context("display.width", 160, "display.max_colwidth", 40):
        print(overview)

    for col in df.columns:
        miss = df[col].isna().mean()
        if miss == 1:
            issue(f"[{col}] 整列为空 → 直接删除这一列")
        elif miss > 0.5:
            issue(f"[{col}] 缺失 {miss:.0%}，太多了填不了 → 改造成“有没有”的标记列（如 has_{col}），或删除这一列")
        elif miss > 0.05 and df[col].isna().sum() > 5:
            issue(f"[{col}] 缺失 {miss:.0%} → 按相关的列分组填（groupby + transform），并加一列标记哪些是填出来的")
        elif miss > 0:
            issue(f"[{col}] 缺失 {df[col].isna().sum()} 个 → 先把这几行拿出来看看；可以删掉，或填众数 / 中位数")
        if n > 1 and df[col].nunique(dropna=False) == 1:
            issue(f"[{col}] 所有行都是同一个值 → 对分析没用，可以考虑删除")

    # ---------- 5. 重复与主键 ----------
    section("5. 重复与主键")
    dup = int(df.duplicated().sum())
    print(f"整行完全重复：{dup} 行")
    if dup:
        issue(f"有 {dup} 行完全重复 → 先确认是重复录入，再 df.drop_duplicates()")
    keys = [c for c in df.columns if df[c].notna().all() and df[c].is_unique]
    print(f"可能的主键（每行都不同、没有缺失）：{keys or '没有'}")
    id_like = [c for c in df.columns if re.search(r"(^id$|_id$|id$|编号|单号|号$)", c, re.I) and c not in keys]
    for c in id_like:
        s = df[c].dropna()
        d = int(s.duplicated().sum())
        # 几乎每行都不同、却有少量重复，才可疑；像 customer_id 这种本来就会重复的不提醒
        if d and s.nunique() >= 0.9 * len(s):
            issue(f"[{c}] 看起来是编号，但有 {d} 个重复值 → 确认是不是重复录入，或者编号本来就允许重复")

    # ---------- 6. 数值列 ----------
    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and not pd.api.types.is_bool_dtype(df[c])]
    section("6. 数值列 describe()")
    if num_cols:
        with pd.option_context("display.width", 160, "display.max_columns", 20):
            print(df[num_cols].describe().round(2))
        for c in num_cols:
            check_numbers(c, df[c].dropna())
            if pd.api.types.is_float_dtype(df[c]) and (df[c].dropna() % 1 == 0).all() and df[c].isna().any():
                issue(f"[{c}] 本该是整数，因为有缺失值变成了小数 → 处理完缺失后 astype(int)")
    else:
        print("（没有数值列）")

    # ---------- 7. 文本列的写法问题 ----------
    section("7. 文本列检查")
    found = False
    for c in df.columns:
        r = raw[c]
        nonempty = r[r != ""]

        # 首尾空格（只查文本列；数字列 pandas 读的时候已经忽略了空格）
        ws = int((nonempty != nonempty.str.strip()).sum()) if is_text(df[c]) else 0
        if ws:
            found = True
            print(f"[{c}] {ws} 个值前后带空格，例如 {nonempty[nonempty != nonempty.str.strip()].iloc[0]!r}")
            issue(f"[{c}] {ws} 个值前后带空格 → df['{c}'] = df['{c}'].str.strip()")

        # 占位符：pandas 默认不当缺失的“-”“无”等
        ph = nonempty.str.strip()
        ph = ph[ph.isin(PLACEHOLDERS)]
        if len(ph):
            found = True
            print(f"[{c}] 有 {len(ph)} 个占位符：{ph.value_counts().to_dict()}")
            vals = sorted(ph.unique())
            issue(f"[{c}] 用 {vals} 表示缺失，pandas 不会自动识别 → read_csv(..., na_values={vals})")

        # 开头的 0 被吃掉：pandas 读成了数字，但原文有 0 开头的值
        if pd.api.types.is_numeric_dtype(df[c]):
            lead = nonempty[nonempty.str.strip().str.match(r"^0\d+$")]
            if len(lead):
                found = True
                print(f"[{c}] 原文有 {len(lead)} 个以 0 开头的值（如 {lead.iloc[0]!r}），读成数字后开头的 0 丢了")
                issue(f"[{c}] 开头的 0 会丢失 → read_csv(..., dtype={{'{c}': str}})")
            continue

        if not is_text(df[c]):
            continue
        s = df[c].dropna().astype(str).str.strip()
        s = s[~s.isin(PLACEHOLDERS)]
        if len(s) == 0:
            continue

        # 数字被存成了文本
        as_num = pd.to_numeric(s.str.replace(",", "", regex=False), errors="coerce")
        if as_num.notna().mean() >= 0.9:
            found = True
            converted.add(c)
            if s.str.contains(",", regex=False).any():
                reason, fix = "含千分位逗号，如 '1,234'", "read_csv(..., thousands=',')"
            elif df[c].dropna().astype(str).str.strip().isin(PLACEHOLDERS).any():
                reason, fix = "混有占位符", "先用 na_values 把占位符当缺失，就能读成数字"
            else:
                reason, fix = "混有非数字的值", f"pd.to_numeric(df['{c}'], errors='coerce')，转不了的会变成缺失"
            print(f"[{c}] 看起来是数字，但被读成了文本（{reason}）")
            issue(f"[{c}] 数字列被读成了文本（{reason}）→ {fix}")
            check_numbers(c, as_num.dropna())
            continue

        # 日期被存成了文本
        looks_date = s.str.contains(r"\d", regex=True) & s.str.contains(r"[-/年:.]", regex=True)
        if looks_date.mean() >= 0.9:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                as_date = pd.to_datetime(s, errors="coerce", format="mixed")
            if as_date.notna().mean() >= 0.9:
                found = True
                converted.add(c)
                print(f"[{c}] 看起来是日期，但还是文本，例如 {s.iloc[0]!r}")
                issue(f"[{c}] 日期列还是文本 → read_csv(..., parse_dates=['{c}'])，或 pd.to_datetime(df['{c}'])")
                continue

        # 同一个值的不同写法（大小写 / 空格）
        if df[c].nunique() <= 50:
            norm = df[c].dropna().astype(str).str.strip().str.lower()
            groups = df[c].dropna().astype(str).groupby(norm).unique()
            variants = {k: list(v) for k, v in groups.items() if len(v) > 1}
            if variants:
                found = True
                print(f"[{c}] 同一个值有不同写法：{variants}")
                issue(f"[{c}] 写法不统一 {list(variants.values())} → 先 str.strip()，再用 replace 统一成一种写法")
    if not found:
        print("没发现空格、占位符、开头的 0、数字或日期被存成文本、写法不统一等问题。")

    # ---------- 8. 类别列的取值 ----------
    section(f"8. 类别列取值（唯一值 ≤ {MAX_CATEGORIES} 的文本列）")
    def id_like(c: str) -> bool:  # 几乎每行都不同 → 是编号，不是类别
        cnt = df[c].notna().sum()
        return cnt >= 10 and df[c].nunique() >= 0.9 * cnt

    cats = [
        c for c in df.columns
        if is_text(df[c]) and c not in converted and not id_like(c) and 0 < df[c].nunique() <= MAX_CATEGORIES
    ]
    for c in cats:
        print(f"[{c}] {df[c].value_counts(dropna=False).to_dict()}")
    if not cats:
        print("（没有）")
    print("提示：逐个看一遍。“上海”和“上海市”、“上海”和“shanghai”这类写法，工具认不出来，要靠人看。")

    # ---------- 9. 问题清单 ----------
    section("9. 问题清单")
    if issues:
        for i, text in enumerate(issues, 1):
            print(f"{i:>2}. {text}")
    else:
        print("没有发现明显问题 ✓")
    print(
        "\n注意：体检只能发现“格式上”的问题。数值看起来合理、实际却是错的，只能靠业务知识判断。\n"
        "清洗步骤参考 pandas-learn/modules/m06_titanic_clean.py，常见报错见 pandas-learn/CSV_TIPS.md。"
    )
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="inspect", description="通用 CSV 体检（只读不改）")
    parser.add_argument("path", help="CSV 文件路径")
    parser.add_argument("--encoding", help="文件编码，如 utf-8、gbk；不填则自动识别")
    parser.add_argument("--sep", help=r"分隔符，如 , ; \t；不填则自动识别")
    args = parser.parse_args(argv)
    sep = "\t" if args.sep in ("\\t", "tab") else args.sep
    return inspect(Path(args.path), args.encoding, sep)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
