#!/usr/bin/env python3
"""按主题统计 Claude Code 的 token 用量，并生成每周报告。

数据来源：本机 ~/.claude/projects/**/*.jsonl（Claude Code 自动记录的会话 transcript）。
只读本地文件，不调用任何模型，运行本身不消耗 token。

用法：
  python3 token_stats.py                 # 最近 14 天，按主题汇总
  python3 token_stats.py --days 30       # 最近 30 天
  python3 token_stats.py --week          # 上一个完整自然周（周一到周日）的周报，含周环比
  python3 token_stats.py --week --out ~/outputs/token-reports   # 周报另存为 Markdown
  python3 token_stats.py --csv sessions.csv                    # 导出每个会话的明细

主题分类规则在下方 TOPICS 里，按自己的习惯增删关键词即可。
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------- 主题规则
# 按顺序匹配会话标题 + 第一条提问，命中第一个即归入该主题。关键词不区分大小写。
TOPICS: list[tuple[str, list[str]]] = [
    ("编程 / 自建工具", [
        "speechcoach", "录音", "whisper", "rust", "reader", "翻译工具", "plist", "自测",
        "selftest", "代码", "bug", "修复", "ci ", "pr ", "github", "仓库", "ios", "git ",
        "脚本", "api 翻译", "字幕", "meetnotes", "审查", "phase", "热键", "mac 说",
        "简历修改工具", "resume", "egui", "部署",
    ]),
    ("知识库 / Obsidian / Anki / 拆书", [
        "obsidian", "wiki", "anki", "拆书", "双链", "笔记", "经济学人", "纽约客", "书籍",
        "hacker laws", "无限的游戏", "learning to see", "专有名词", "资产库", "卡片",
    ]),
    ("3D 打印 / 硬件 / 机器人", [
        "3d", "打印", "pla ", "petg", "p1s", "拓竹", "so101", "so-arm", "机器人", "ros2", "ros 2",
        "烙铁", "切片", "电机", "自由度", "机械鸭", "kindle", "硬盘", "t7",
    ]),
    ("求职 / 面试", [
        "招聘", "面试", "求职", "job", "简历", "岗位", "teaching", "childcare",
    ]),
    ("投资 / 商业调研", [
        "polymarket", "投资", "市场调研", "蓝海", "供应链", "招股", "做空", "产品介绍",
    ]),
    ("AI / 计算机概念问答", [
        "attention", "kvq", "transformer", "llm", "token", "haiku", "opus", "claude",
        "cli", "json", "vps", "vpn", "tailscale", "exfat", "end to end", "环境变量",
        "azw3", "mobi", "scrum", "链表", "agent", "提示词", "decisions api", "格式",
        "fast mode", "reset", "积分",
    ]),
    ("生活 / 购物 / 健康 / 出行", [
        "超市", "costco", "价格", "薯饼", "蛋白", "他汀", "柚子", "药", "嘌呤", "咖啡",
        "税", "电池", "iphone", "一日游", "行程", "温哥华", "博物馆", "签证", "fsd",
        "cyber", "stanley", "登山跳", "盲打", "下载文件夹", "储存空间", "清理", "整理",
    ]),
]
OTHER_TOPIC = "其他"

# 相对“普通输入 token”的计价倍率（Anthropic 公开定价结构），用来算缓存节约比例。
W_INPUT, W_CACHE_5M, W_CACHE_1H, W_CACHE_READ, W_OUTPUT = 1.0, 1.25, 2.0, 0.1, 5.0

SHORT_SESSION_PROMPTS = 2    # 提问次数 ≤ 这个数视为“短问答会话”
LONG_CONTEXT_TOKENS = 150_000  # 单次请求上下文超过这个数视为“长上下文请求”


# ---------------------------------------------------------------- 数据结构
@dataclass
class Req:
    ts: datetime
    model: str
    speed: str
    input: int = 0
    cache_5m: int = 0
    cache_1h: int = 0
    cache_read: int = 0
    output: int = 0

    @property
    def context(self) -> int:
        return self.input + self.cache_5m + self.cache_1h + self.cache_read

    @property
    def total(self) -> int:
        return self.context + self.output

    @property
    def weighted(self) -> float:
        return (self.input * W_INPUT + self.cache_5m * W_CACHE_5M + self.cache_1h * W_CACHE_1H
                + self.cache_read * W_CACHE_READ + self.output * W_OUTPUT)

    @property
    def weighted_no_cache(self) -> float:
        return self.context * W_INPUT + self.output * W_OUTPUT


@dataclass
class Session:
    sid: str
    project: str
    title: str = ""
    first_prompt: str = ""
    prompts: int = 0
    reqs: dict[str, Req] = field(default_factory=dict)  # 按 message.id 去重

    @property
    def label(self) -> str:
        return (self.title or self.first_prompt or self.sid)[:40].replace("\n", " ")


# ---------------------------------------------------------------- 解析
def _text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
        return " ".join(parts)
    return ""


def _parse_ts(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def load_sessions(root: Path) -> dict[str, Session]:
    sessions: dict[str, Session] = {}
    for path in root.rglob("*.jsonl"):
        rel = path.relative_to(root)
        project = rel.parts[0]
        # 子代理 transcript 位于 <session>/subagents/xxx.jsonl，计入父会话
        sid = rel.parts[1] if len(rel.parts) > 2 else path.stem
        is_sub = len(rel.parts) > 2
        s = sessions.setdefault(sid, Session(sid=sid, project=project))
        try:
            fh = path.open(encoding="utf-8", errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                t = d.get("type")
                if t in ("custom-title", "ai-title", "summary"):
                    title = d.get("customTitle") or d.get("aiTitle") or d.get("title") or d.get("summary")
                    if title and (t == "custom-title" or not s.title):
                        s.title = str(title)
                elif t == "user" and not is_sub and not d.get("isMeta") and not d.get("isSidechain"):
                    msg = d.get("message") or {}
                    content = msg.get("content")
                    if isinstance(content, list) and any(
                            isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
                        continue
                    text = _text_of(content).strip()
                    if not text or text.startswith("<"):
                        continue
                    s.prompts += 1
                    if not s.first_prompt:
                        s.first_prompt = text
                elif t == "assistant":
                    msg = d.get("message") or {}
                    u = msg.get("usage")
                    ts = _parse_ts(d.get("timestamp"))
                    if not u or ts is None:
                        continue
                    key = msg.get("id") or d.get("requestId") or d.get("uuid")
                    cc = u.get("cache_creation") or {}
                    c1h = int(cc.get("ephemeral_1h_input_tokens") or 0)
                    c5m = int(cc.get("ephemeral_5m_input_tokens") or 0)
                    if not cc:
                        c5m = int(u.get("cache_creation_input_tokens") or 0)
                    new = Req(ts=ts, model=msg.get("model") or "?", speed=u.get("speed") or "standard",
                              input=int(u.get("input_tokens") or 0), cache_5m=c5m, cache_1h=c1h,
                              cache_read=int(u.get("cache_read_input_tokens") or 0),
                              output=int(u.get("output_tokens") or 0))
                    old = s.reqs.get(key)
                    if old is None:
                        s.reqs[key] = new
                    else:  # 同一请求被拆成多行记录时取各字段最大值
                        for f in ("input", "cache_5m", "cache_1h", "cache_read", "output"):
                            setattr(old, f, max(getattr(old, f), getattr(new, f)))
    return {k: v for k, v in sessions.items() if v.reqs}


def topic_of(s: Session) -> str:
    hay = f"{s.title} {s.first_prompt[:300]}".lower()
    for name, kws in TOPICS:
        if any(k in hay for k in kws):
            return name
    return OTHER_TOPIC


# ---------------------------------------------------------------- 统计
@dataclass
class Agg:
    sessions: set = field(default_factory=set)
    reqs: int = 0
    input: int = 0
    cache_write: int = 0
    cache_read: int = 0
    output: int = 0
    weighted: float = 0.0
    weighted_no_cache: float = 0.0

    def add(self, sid: str, r: Req):
        self.sessions.add(sid)
        self.reqs += 1
        self.input += r.input
        self.cache_write += r.cache_5m + r.cache_1h
        self.cache_read += r.cache_read
        self.output += r.output
        self.weighted += r.weighted
        self.weighted_no_cache += r.weighted_no_cache

    @property
    def total(self) -> int:
        return self.input + self.cache_write + self.cache_read + self.output

    @property
    def cache_saving(self) -> float:
        return 1 - self.weighted / self.weighted_no_cache if self.weighted_no_cache else 0.0


def summarize(sessions: dict[str, Session], start: datetime, end: datetime) -> dict:
    by_topic: dict[str, Agg] = defaultdict(Agg)
    by_model: dict[str, Agg] = defaultdict(Agg)
    overall = Agg()
    per_session: dict[str, Agg] = defaultdict(Agg)
    first_req_ctx: list[int] = []
    short_overhead = 0
    short_count = 0
    long_ctx_reqs = 0
    fast_reqs = 0
    for s in sessions.values():
        reqs = sorted((r for r in s.reqs.values() if start <= r.ts < end), key=lambda r: r.ts)
        if not reqs:
            continue
        topic = topic_of(s)
        for r in reqs:
            by_topic[topic].add(s.sid, r)
            by_model[r.model].add(s.sid, r)
            overall.add(s.sid, r)
            per_session[s.sid].add(s.sid, r)
            if r.context >= LONG_CONTEXT_TOKENS:
                long_ctx_reqs += 1
            if r.speed == "fast":
                fast_reqs += 1
        all_reqs = sorted(s.reqs.values(), key=lambda r: r.ts)
        if all_reqs[0].ts >= start:  # 会话在本区间内开始
            first_req_ctx.append(all_reqs[0].context)
            if s.prompts <= SHORT_SESSION_PROMPTS:
                short_count += 1
                short_overhead += per_session[s.sid].total
    return {
        "by_topic": by_topic,
        "by_model": by_model,
        "overall": overall,
        "per_session": per_session,
        "first_req_ctx": first_req_ctx,
        "short_count": short_count,
        "short_overhead": short_overhead,
        "long_ctx_reqs": long_ctx_reqs,
        "fast_reqs": fast_reqs,
    }


# ---------------------------------------------------------------- 输出
def fmt(n: float) -> str:
    n = float(n)
    if abs(n) >= 1e6:
        return f"{n / 1e6:.2f}M"
    if abs(n) >= 1e3:
        return f"{n / 1e3:.1f}k"
    return f"{n:.0f}"


def pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def render(sessions, res, start, end, prev=None) -> str:
    o: Agg = res["overall"]
    L = []
    last_day = end - timedelta(seconds=1)
    L.append(f"# Claude Code token 统计 {start.astimezone():%Y-%m-%d} ~ {last_day.astimezone():%Y-%m-%d}\n")
    if not o.reqs:
        L.append("这段时间没有找到用量记录。\n")
        return "\n".join(L)

    L.append("## 总览\n")
    L.append("| 指标 | 本期 |" + (" 上期 | 变化 |" if prev else ""))
    L.append("|---|---|" + ("---|---|" if prev else ""))

    # 上期没有任何请求时，比例和均值没有意义，环比也无从谈起，统一显示 "-"
    prev_empty = prev is not None and not prev["overall"].reqs

    def row(name, cur, old=None, f=fmt, derived=False):
        if prev is None:
            L.append(f"| {name} | {f(cur)} |")
            return
        old_cell = "-" if prev_empty and derived else f(old)
        if prev_empty:
            delta = "-"
        elif isinstance(cur, float) and f is pct:
            delta = f"{(cur - old) * 100:+.1f} 个百分点"
        else:
            delta = f"{(cur / old - 1) * 100:+.0f}%" if old else "-"
        L.append(f"| {name} | {f(cur)} | {old_cell} | {delta} |")

    po: Agg | None = prev["overall"] if prev else None
    row("会话数", len(o.sessions), len(po.sessions) if po else None, f=lambda x: str(int(x)))
    row("API 请求数", o.reqs, po.reqs if po else None, f=lambda x: str(int(x)))
    row("总 token（含缓存读）", o.total, po.total if po else None)
    row("　其中 普通输入", o.input, po.input if po else None)
    row("　其中 缓存写入", o.cache_write, po.cache_write if po else None)
    row("　其中 缓存读取", o.cache_read, po.cache_read if po else None)
    row("　其中 输出", o.output, po.output if po else None)
    row("折算 token（按计价倍率）", o.weighted, po.weighted if po else None)
    row("缓存节约比例", o.cache_saving, po.cache_saving if po else None, f=pct, derived=True)
    fr = res["first_req_ctx"]
    pfr = prev["first_req_ctx"] if prev else []
    avg_fr = sum(fr) / len(fr) if fr else 0
    avg_pfr = sum(pfr) / len(pfr) if pfr else 0
    row("新会话首轮固定开销（均值）", avg_fr, avg_pfr if prev else None, derived=True)
    avg_ctx = (o.input + o.cache_write + o.cache_read) / o.reqs
    pavg_ctx = (po.input + po.cache_write + po.cache_read) / po.reqs if po and po.reqs else 0
    row("每次请求平均上下文", avg_ctx, pavg_ctx if prev else None, derived=True)
    L.append("")

    # 节约比例说明
    L.append("**节约比例怎么算：**缓存节约比例 = 1 − 实际折算 token ÷ 不用缓存时的折算 token。"
             "缓存读取按 0.1 倍、写入按 1.25/2 倍、输出按 5 倍折算。这个数越高越好；"
             "频繁开新会话、离开超过缓存有效期再回来，都会把它拉低。\n")
    if prev:
        saved = po.weighted - o.weighted
        if po.weighted:
            L.append(f"**和上期相比：**折算 token {'减少' if saved >= 0 else '增加'} "
                     f"{fmt(abs(saved))}（{pct(abs(saved) / po.weighted)}）。\n")

    L.append("## 按主题\n")
    L.append("| 主题 | 会话 | 请求 | 总 token | 折算 token | 占比 | 缓存节约 |")
    L.append("|---|---|---|---|---|---|---|")
    for name, a in sorted(res["by_topic"].items(), key=lambda kv: -kv[1].weighted):
        L.append(f"| {name} | {len(a.sessions)} | {a.reqs} | {fmt(a.total)} | {fmt(a.weighted)} | "
                 f"{pct(a.weighted / o.weighted)} | {pct(a.cache_saving)} |")
    L.append("")

    L.append("## 按模型\n")
    L.append("| 模型 | 请求 | 总 token | 折算 token | 占比 |")
    L.append("|---|---|---|---|---|")
    for name, a in sorted(res["by_model"].items(), key=lambda kv: -kv[1].weighted):
        L.append(f"| {name} | {a.reqs} | {fmt(a.total)} | {fmt(a.weighted)} | {pct(a.weighted / o.weighted)} |")
    L.append("")

    L.append("## 用量最多的 10 个会话\n")
    L.append("| 会话 | 主题 | 提问数 | 请求 | 总 token | 折算 token |")
    L.append("|---|---|---|---|---|---|")
    top = sorted(res["per_session"].items(), key=lambda kv: -kv[1].weighted)[:10]
    for sid, a in top:
        s = sessions[sid]
        L.append(f"| {s.label} | {topic_of(s)} | {s.prompts} | {a.reqs} | {fmt(a.total)} | {fmt(a.weighted)} |")
    L.append("")

    L.append("## 可以省的地方\n")
    tips = []
    if res["short_count"]:
        tips.append(f"- **短问答会话 {res['short_count']} 个**（提问 ≤ {SHORT_SESSION_PROMPTS} 次），共用掉 "
                    f"{fmt(res['short_overhead'])} token，几乎全是固定开销。这类问题改到 claude.ai 普通聊天，"
                    f"或在 Claude Code 里先 `/model` 切到 Haiku/Sonnet。")
    if avg_fr > 40_000:
        tips.append(f"- **新会话首轮固定开销均值 {fmt(avg_fr)}**。停用用不到的插件/MCP 后，这个数会明显下降，"
                    "可以用它来检验清理效果。")
    if res["long_ctx_reqs"]:
        tips.append(f"- **{res['long_ctx_reqs']} 次请求的上下文超过 {fmt(LONG_CONTEXT_TOKENS)}**。"
                    "换话题时 `/clear`，长任务中途 `/compact`。")
    if o.cache_saving < 0.6:
        tips.append(f"- **缓存节约比例只有 {pct(o.cache_saving)}**。连续工作、少开碎片会话，"
                    "离开超过 1 小时前先 `/compact`。")
    opus = sum(a.weighted for m, a in res["by_model"].items() if "opus" in m)
    if o.weighted and opus / o.weighted > 0.9:
        tips.append(f"- **Opus 占折算用量 {pct(opus / o.weighted)}**。简单问答、改格式、查资料可以交给 Sonnet/Haiku。")
    if res["fast_reqs"]:
        tips.append(f"- **Fast mode 请求 {res['fast_reqs']} 次**，按更高单价计费，不赶时间就关掉。")
    L.extend(tips or ["- 本期没有明显的浪费点。"])
    L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--week", action="store_true", help="上一个完整自然周的周报，含周环比")
    ap.add_argument("--out", help="把报告存成 Markdown 的目录")
    ap.add_argument("--csv", help="导出会话明细 CSV")
    args = ap.parse_args()

    root = Path(args.root)
    if not root.exists():
        sys.exit(f"找不到 {root}")
    sessions = load_sessions(root)

    now = datetime.now().astimezone()
    if args.week:
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = today - timedelta(days=today.weekday())  # 本周一 0 点
        start = end - timedelta(days=7)
        prev = summarize(sessions, start - timedelta(days=7), start)
    else:
        end = now + timedelta(seconds=1)
        start = end - timedelta(days=args.days)
        prev = None
    res = summarize(sessions, start, end)
    report = render(sessions, res, start, end, prev)
    print(report)

    if args.out:
        out = Path(os.path.expanduser(args.out))
        out.mkdir(parents=True, exist_ok=True)
        name = f"{start:%G-W%V}.md" if args.week else f"{start:%Y%m%d}-{now:%Y%m%d}.md"
        (out / name).write_text(report, encoding="utf-8")
        print(f"\n已保存：{out / name}", file=sys.stderr)

    if args.csv:
        with open(os.path.expanduser(args.csv), "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(["session_id", "title", "topic", "prompts", "requests", "input", "cache_write",
                        "cache_read", "output", "total", "weighted", "cache_saving"])
            for sid, a in sorted(res["per_session"].items(), key=lambda kv: -kv[1].weighted):
                s = sessions[sid]
                w.writerow([sid, s.label, topic_of(s), s.prompts, a.reqs, a.input, a.cache_write,
                            a.cache_read, a.output, a.total, round(a.weighted), round(a.cache_saving, 4)])


if __name__ == "__main__":
    main()
