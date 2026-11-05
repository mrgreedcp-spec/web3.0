#!/usr/bin/env python3
"""Sayall 每日表达评估：读取 SayAll 本地语音转写历史，统计后交给本机 claude 写严格评估。

流程：
  1. 以 MCP 客户端身份启动 SayAll 自带的只读 Helper（stdio），调用 query_transcripts
     取出评估日（默认：北京时间昨天）的全部记录；
  2. 用程序统计词数、时长、WPM、填充词、句长、弱词等，不让模型去"估"；
  3. 把统计、近 7 天历史分数和原文交给 `claude -p`（禁用全部工具和 MCP），按 PROMPT.md 写报告；
  4. 报告存到 ~/outputs/sayall-reviews/，如装了 Google Drive 桌面版再同步一份，并弹 macOS 通知。

凭据：SayAll "回眸 → 本地 Agent 访问" 里为本工具单独创建的只读授权，install.sh 会存进钥匙串。
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import queue
import re
import shutil
import statistics
import subprocess
import sys
import threading
from collections import Counter
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
TZ = ZoneInfo(os.environ.get("SAYALL_TZ", "Asia/Shanghai"))
OUT_DIR = Path(os.environ.get("SAYALL_REPORT_DIR", Path.home() / "outputs" / "sayall-reviews"))
HELPER = os.environ.get("SAYALL_MCP_HELPER", "/Applications/SayAll.app/Contents/Helpers/SayAllMCP")
KEYCHAIN_SERVICE = "sayall-review"
MIN_RECORD_SECONDS = 3.0      # 短于此的记录不计入 WPM（时长误差占比太大）
MAX_TRANSCRIPT_CHARS = 120_000  # 交给模型的原文上限
PROTOCOL_VERSION = "2025-06-18"

EN_WORD = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)*")
CJK_CHAR = re.compile(r"[㐀-䶿一-鿿]")
SENTENCE_SPLIT = re.compile(r"(?<=[.!?。！？；;])\s*|\n+")

# 填充词：只收"几乎总是填充"的形式；like / so / actually 这类多义词单列为"疑似"，不混进主指标。
EN_FILLERS = [r"um+", r"uh+", r"erm*", r"hmm+", r"you know", r"i mean", r"kind of", r"sort of"]
EN_SOFT_FILLERS = [r"like", r"actually", r"basically", r"literally", r"so yeah", r"right\?"]
ZH_FILLERS = ["嗯", "呃", "额", "就是说", "就是", "然后", "那个", "这个", "对吧", "其实"]
EN_WEAK = ["very", "really", "good", "bad", "nice", "thing", "things", "stuff", "a lot", "just",
           "kind of", "sort of", "pretty", "big", "get", "got"]


# ---------------------------------------------------------------- MCP 客户端

class MCPError(RuntimeError):
    pass


class StdioMCP:
    """最小的 MCP stdio 客户端：按行收发 JSON-RPC。"""

    def __init__(self, command: list[str], env: dict[str, str], timeout: float = 60.0):
        self.timeout = timeout
        self.proc = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=env, text=True, encoding="utf-8", bufsize=1,
        )
        self._q: queue.Queue = queue.Queue()
        self._stderr: list[str] = []
        threading.Thread(target=self._read_stdout, daemon=True).start()
        threading.Thread(target=self._read_stderr, daemon=True).start()
        self._next_id = 0

    def _read_stdout(self):
        for line in self.proc.stdout:
            line = line.strip()
            if line:
                self._q.put(line)
        self._q.put(None)

    def _read_stderr(self):
        for line in self.proc.stderr:
            self._stderr.append(line.rstrip())

    def _send(self, msg: dict):
        try:
            self.proc.stdin.write(json.dumps(msg, ensure_ascii=False) + "\n")
            self.proc.stdin.flush()
        except BrokenPipeError as e:
            raise MCPError(f"SayAll Helper 已退出：{self.stderr_tail()}") from e

    def request(self, method: str, params: dict | None = None) -> dict:
        self._next_id += 1
        rid = self._next_id
        self._send({"jsonrpc": "2.0", "id": rid, "method": method, "params": params or {}})
        while True:
            try:
                line = self._q.get(timeout=self.timeout)
            except queue.Empty:
                raise MCPError(f"{method} 超时（{self.timeout:.0f}s）")
            if line is None:
                raise MCPError(f"SayAll Helper 意外退出：{self.stderr_tail()}")
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue  # 非协议输出，忽略
            if msg.get("id") != rid:
                continue  # 通知或其他消息
            if "error" in msg:
                raise MCPError(f"{method} 失败：{msg['error'].get('message', msg['error'])}")
            return msg.get("result", {})

    def notify(self, method: str, params: dict | None = None):
        self._send({"jsonrpc": "2.0", "method": method, "params": params or {}})

    def initialize(self):
        self.request("initialize", {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "sayall-review", "version": "1.0"},
        })
        self.notify("notifications/initialized")

    def call_tool(self, name: str, arguments: dict) -> dict:
        res = self.request("tools/call", {"name": name, "arguments": arguments})
        text = "".join(c.get("text", "") for c in res.get("content", []) if c.get("type") == "text")
        if res.get("isError"):
            raise MCPError(f"{name} 返回错误：{text or res}")
        if isinstance(res.get("structuredContent"), dict):
            return res["structuredContent"]
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise MCPError(f"{name} 返回内容不是 JSON：{text[:200]}") from e

    def stderr_tail(self) -> str:
        return " | ".join(self._stderr[-5:]) or "（无错误输出）"

    def close(self):
        try:
            self.proc.stdin.close()
        except Exception:
            pass
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait()
        for f in (self.proc.stdout, self.proc.stderr):
            try:
                f.close()
            except Exception:
                pass


def keychain_get(account: str) -> str | None:
    if sys.platform != "darwin":
        return None
    r = subprocess.run(["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-a", account, "-w"],
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def credentials() -> tuple[str, str]:
    cid = os.environ.get("SAYALL_MCP_CLIENT_ID") or keychain_get("client_id")
    tok = os.environ.get("SAYALL_MCP_ACCESS_TOKEN") or keychain_get("access_token")
    if not cid or not tok:
        raise MCPError("找不到 SayAll 授权。请先运行 install.sh，或设置 SAYALL_MCP_CLIENT_ID / SAYALL_MCP_ACCESS_TOKEN。")
    return cid, tok


def fetch_records(day: dt.date) -> tuple[list[dict], int]:
    """取 localDateKey == day 的全部记录。查询窗口前后各放宽 14 小时，以覆盖跨时区记录。"""
    if not Path(HELPER).exists():
        raise MCPError(f"找不到 SayAll Helper：{HELPER}。App 不在 /Applications 时，请把 SAYALL_MCP_HELPER 设成 SayAll 页面里显示的 Helper 路径。")
    cid, tok = credentials()
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(Path.home()),
           "SAYALL_MCP_CLIENT_ID": cid, "SAYALL_MCP_ACCESS_TOKEN": tok}
    start_local = dt.datetime.combine(day, dt.time(0), TZ)
    window_start = (start_local - dt.timedelta(hours=14)).astimezone(dt.timezone.utc)
    window_end = (start_local + dt.timedelta(days=1, hours=14)).astimezone(dt.timezone.utc)

    client = StdioMCP([HELPER, "serve"], env)
    records, skipped, cursor = [], 0, None
    try:
        client.initialize()
        for _ in range(200):  # 最多 10 万条，防止游标异常导致死循环
            args = {"startedAtOrAfter": iso_z(window_start), "endedAtBefore": iso_z(window_end),
                    "order": "ascending", "limit": 500}
            if cursor:
                args["cursor"] = cursor
            page = client.call_tool("query_transcripts", args)
            records.extend(page.get("records", []))
            skipped = max(skipped, int(page.get("skippedFileCount", 0) or 0))
            cursor = page.get("nextCursor")
            if not page.get("hasMore") or not cursor:
                break
    finally:
        client.close()
    key = day.isoformat()
    return [r for r in records if r.get("localDateKey") == key], skipped


def iso_z(t: dt.datetime) -> str:
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_ts(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


# ---------------------------------------------------------------- 统计

def count_phrases(text_lower: str, patterns: list[str]) -> Counter:
    c = Counter()
    for p in patterns:
        n = len(re.findall(rf"(?<![A-Za-z']){p}(?![A-Za-z'])", text_lower))
        if n:
            c[p.replace("+", "").replace("*", "").replace("\\?", "?")] += n
    return c


def count_zh(text: str, words: list[str]) -> Counter:
    c, rest = Counter(), text
    for w in sorted(words, key=len, reverse=True):  # 先数长词，避免"就是说"被重复计成"就是"
        n = rest.count(w)
        if n:
            c[w] = n
            rest = rest.replace(w, "\0")
    return c


def sentences(text: str) -> list[str]:
    return [s.strip() for s in SENTENCE_SPLIT.split(text) if s and s.strip()]


def units(text: str) -> int:
    """表达单位：英文按词，中文按字。"""
    return len(EN_WORD.findall(text)) + len(CJK_CHAR.findall(text))


def _lang_block(lang: str, recs: list[dict]) -> dict:
    """一种语言的统计。recs 为主语言是 lang 的记录；语速只用时长 ≥ MIN_RECORD_SECONDS 的记录。"""
    text = "\n".join(r["text"] for r in recs)
    lower = text.lower()
    total = sum(r["units"] for r in recs)
    timed = [r for r in recs if r["rate"] is not None]
    sec = sum(r["seconds"] for r in timed)
    per = [r["rate"] for r in timed]
    minutes = sec / 60 if sec else None
    b = {
        "unit": "词" if lang == "en" else "字",
        "records": len(recs),
        "records_timed": len(timed),
        "units": total,
        "seconds": round(sum(r["seconds"] for r in recs), 1),
        "rate_per_min": round(sum(r["units"] for r in timed) / minutes, 1) if minutes else None,
        "rate_note": None if minutes else f"没有时长 ≥ {MIN_RECORD_SECONDS:.0f}s 的记录，语速不可靠",
        "rate_median": round(statistics.median(per), 1) if per else None,
        "rate_stdev": round(statistics.pstdev(per), 1) if len(per) > 1 else None,
        "rate_min": min(per) if per else None,
        "rate_max": max(per) if per else None,
    }
    if lang == "en":
        fillers = count_phrases(lower, EN_FILLERS)
        soft = count_phrases(lower, EN_SOFT_FILLERS)
        weak = count_phrases(lower, [re.escape(w) for w in EN_WEAK])
        words = [w.lower() for w in EN_WORD.findall(text)]
        chunks = [words[i:i + 100] for i in range(0, len(words) - 99, 100)]
        b.update({
            "soft_fillers_top": soft.most_common(5),
            "soft_fillers_note": "like / actually 等为多义词，可能是正常用法，未计入填充词，仅供参考",
            "weak_words_total": sum(weak.values()),
            "weak_per_100": round(sum(weak.values()) / len(words) * 100, 2) if words else None,
            "weak_top": weak.most_common(5),
            "type_token_ratio": round(len(set(words)) / len(words), 3) if words else None,
            # 标准化 TTR：每 100 词一段取平均，不受样本长短影响；不足 100 词时为 null
            "standardized_ttr_100": round(statistics.mean(len(set(c)) / 100 for c in chunks), 3) if chunks else None,
        })
    else:
        fillers = count_zh(text, ZH_FILLERS)
        b["fillers_note"] = "这个 / 那个 / 其实 也可能是正常指代或用法，已计入填充词，判断时结合原文"
    ft = sum(fillers.values())
    b.update({"fillers_total": ft, "fillers_per_min": round(ft / minutes, 2) if minutes else None,
              "fillers_top": fillers.most_common(5)})
    if ft == 0:
        b["fillers_zero_note"] = "填充词为 0，可能被语音识别过滤，不代表真的没有"
    return b


def analyze(records: list[dict]) -> tuple[dict, list[dict]]:
    rows = []
    for r in records:
        try:
            dur = max((parse_ts(r["endedAt"]) - parse_ts(r["startedAt"])).total_seconds(), 0.0)
        except (KeyError, ValueError, TypeError):
            dur = 0.0
        text = (r.get("text") or "").strip()
        en, zh = len(EN_WORD.findall(text)), len(CJK_CHAR.findall(text))
        lang = "en" if en >= zh else "zh"
        n = en if lang == "en" else zh
        ok = dur >= MIN_RECORD_SECONDS and n > 0
        rows.append({"id": r.get("id"), "startedAt": r.get("startedAt"), "app": r.get("applicationName") or "?",
                     "seconds": round(dur, 1), "lang": lang, "units": n, "en_words": en, "zh_chars": zh,
                     "rate": round(n / (dur / 60), 1) if ok else None, "text": text})

    en_total = sum(r["en_words"] for r in rows)
    zh_total = sum(r["zh_chars"] for r in rows)
    primary = "en" if en_total >= zh_total else "zh"

    sents = [s for r in rows for s in sentences(r["text"])]
    lens = [(units(s), s) for s in sents if units(s) > 0]
    longest = max(lens, key=lambda x: x[0]) if lens else (None, "")
    by_app = Counter()
    for r in rows:
        by_app[r["app"]] += r["units"]

    stats = {
        "primary_language": primary,
        "records": len(rows),
        "total_seconds": round(sum(r["seconds"] for r in rows), 1),
        "en_words": en_total,
        "zh_chars": zh_total,
        "duration_note": "时长取 SayAll 记录的开始到结束，包含开口前和句间停顿，因此语速低于纯发音语速；偏低本身反映犹豫和停顿",
        "sentences": len(lens),
        "avg_sentence_len": round(statistics.mean(n for n, _ in lens), 1) if lens else None,
        "longest_sentence_len": longest[0],
        "longest_sentence_start": longest[1][:120],
        "turns_ge_40_units": sum(1 for r in rows if r["units"] >= 40),
        "by_app": by_app.most_common(),
        "sample_too_small": (en_total < 150) if primary == "en" else (zh_total < 300),
    }
    for lang in ("en", "zh"):
        recs = [r for r in rows if r["lang"] == lang]
        if recs:
            stats[lang] = _lang_block(lang, recs)
    return stats, rows


# ---------------------------------------------------------------- 报告

SCORE_RE = re.compile(r"\*\*总分[:：]\s*([0-9]+(?:\.[0-9])?)\s*/\s*10")
DIM_ROW_RE = re.compile(r"^\|\s*(结构|逻辑与论证|语言准确度|词汇与地道度|流利度与简洁|语速与节奏)\s*\|\s*([0-9]+(?:\.[0-9])?)")


def history(day: dt.date, n: int = 7) -> list[dict]:
    out = []
    for i in range(1, 31):
        d = day - dt.timedelta(days=i)
        p = OUT_DIR / f"{d.isoformat()}.md"
        if not p.exists():
            continue
        body = p.read_text(encoding="utf-8")
        m = SCORE_RE.search(body)
        dims = {}
        for line in body.splitlines():
            mm = DIM_ROW_RE.match(line)
            if mm:
                dims[mm.group(1)] = float(mm.group(2))
        out.append({"date": d.isoformat(), "no_record": "（无记录）" in body.splitlines()[0],
                    "total": float(m.group(1)) if m else None, "dims": dims})
        if len(out) >= n:
            break
    return out


def missed_streak(day: dt.date) -> int:
    """连续几天没有记录（含当天）。"""
    streak, d = 0, day
    while streak < 365:
        p = OUT_DIR / f"{d.isoformat()}.md"
        if p.exists() and "（无记录）" not in p.read_text(encoding="utf-8").splitlines()[0]:
            break
        if not p.exists() and d != day:
            break  # 当时脚本没跑，不算
        streak += 1
        d -= dt.timedelta(days=1)
    return streak


def build_input(day: dt.date, stats: dict, rows: list[dict], hist: list[dict]) -> str:
    parts = [f"# 评估日：{day.isoformat()}（{TZ.key}）\n",
             "## 1. 脚本统计（以此为准）\n```json\n" + json.dumps(stats, ensure_ascii=False, indent=1) + "\n```\n",
             "## 2. 最近 7 天历史分数\n```json\n" + json.dumps(hist, ensure_ascii=False, indent=1) + "\n```\n",
             "## 3. 当天全部转写（时间为当地时间）\n"]
    used, truncated = 0, 0
    for i, r in enumerate(rows, 1):
        try:
            t = parse_ts(r["startedAt"]).astimezone(TZ).strftime("%H:%M:%S")
        except Exception:
            t = "?"
        unit = "词" if r["lang"] == "en" else "字"
        rate = f"{r['rate']} {unit}/min" if r["rate"] else f"时长 < {MIN_RECORD_SECONDS:.0f}s，不计语速"
        block = f"### [{i}] {t} · {r['app']} · {r['seconds']}s · {rate}\n{r['text']}\n"
        if used + len(block) > MAX_TRANSCRIPT_CHARS:
            truncated += 1
            continue
        parts.append(block)
        used += len(block)
    if truncated:
        parts.append(f"\n（另有 {truncated} 条因长度上限未附原文，统计已包含它们。）\n")
    return "\n".join(parts)


def run_claude(prompt: str, payload: str) -> str:
    claude = os.environ.get("SAYALL_CLAUDE_BIN") or shutil.which("claude")
    for cand in ("~/.claude/local/claude", "~/.local/bin/claude", "/opt/homebrew/bin/claude", "/usr/local/bin/claude"):
        if claude:
            break
        p = Path(cand).expanduser()
        claude = str(p) if p.exists() else None
    if not claude:
        raise RuntimeError("找不到 claude 命令。请确认已安装 Claude Code 并登录。")
    cmd = [claude, "-p", prompt, "--tools", "", "--strict-mcp-config", "--no-session-persistence",
           "--output-format", "text"]
    if os.environ.get("SAYALL_MODEL"):
        cmd += ["--model", os.environ["SAYALL_MODEL"]]
    r = subprocess.run(cmd, input=payload, capture_output=True, text=True, timeout=900, cwd=str(HERE))
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError(f"claude 执行失败（{r.returncode}）：{(r.stderr or r.stdout)[-800:]}")
    return r.stdout.strip() + "\n"


def no_record_report(day: dt.date, streak: int, skipped: int) -> str:
    lines = [f"# Sayall 评估 {day.isoformat()}（无记录）", "",
             f"**{day.isoformat()} 没有任何 SayAll 语音记录。** 没有练习，就没有进步。", "",
             f"- 已连续 **{streak}** 天没有记录。"]
    if streak >= 3:
        lines.append("- 连续 3 天以上不练，前面建立的语感会明显退化。今天至少用语音输入完成 3 条 40 词以上的表达。")
    if skipped:
        lines.append(f"- 注意：SayAll 报告有 {skipped} 个历史文件被跳过（损坏或过大），可能有记录没读到。")
    return "\n".join(lines) + "\n"


def drive_mirror_dirs() -> list[Path]:
    if os.environ.get("SAYALL_DRIVE_DIR"):
        return [Path(os.environ["SAYALL_DRIVE_DIR"]).expanduser()]
    roots = glob.glob(str(Path.home() / "Library/CloudStorage/GoogleDrive-*"))
    out = []
    for root in roots:
        for mydrive in ("My Drive", "我的云端硬盘"):
            base = Path(root) / mydrive / "Sayall"
            if base.exists():
                out.append(base / "reviews")
    return out


def notify(title: str, msg: str):
    if sys.platform != "darwin":
        return
    esc = lambda s: s.replace("\\", "\\\\").replace('"', '\\"')
    subprocess.run(["osascript", "-e", f'display notification "{esc(msg)}" with title "{esc(title)}"'],
                   capture_output=True)


def headline(report: str) -> str:
    m = SCORE_RE.search(report)
    if m:
        return f"总分 {m.group(1)} / 10"
    return report.splitlines()[0].lstrip("# ").strip() if report else "完成"


# ---------------------------------------------------------------- 入口

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--date", help="评估日 YYYY-MM-DD，默认为昨天（北京时间）")
    ap.add_argument("--force", action="store_true", help="已有报告也重新生成")
    ap.add_argument("--dry-run", action="store_true", help="只取数据和统计，打印给模型的输入，不调用 claude、不写报告")
    ap.add_argument("--from-json", help="不连 SayAll，改从 JSON 文件读记录（测试或补跑用）")
    a = ap.parse_args(argv)

    day = dt.date.fromisoformat(a.date) if a.date else dt.datetime.now(TZ).date() - dt.timedelta(days=1)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "data").mkdir(exist_ok=True)
    report_path = OUT_DIR / f"{day.isoformat()}.md"
    if report_path.exists() and not a.force and not a.dry_run:
        print(f"已存在：{report_path}（用 --force 重新生成）")
        return 0

    try:
        if a.from_json:
            data = json.loads(Path(a.from_json).read_text(encoding="utf-8"))
            recs = data.get("records", data) if isinstance(data, dict) else data
            records, skipped = [r for r in recs if r.get("localDateKey") == day.isoformat()], 0
        else:
            records, skipped = fetch_records(day)
    except MCPError as e:
        notify("Sayall 评估失败", str(e)[:180])
        print(f"错误：{e}", file=sys.stderr)
        return 2

    stats, rows = analyze(records)
    stats["skipped_history_files"] = skipped
    hist = history(day)

    if a.dry_run:
        print(build_input(day, stats, rows, hist))
        return 0

    (OUT_DIR / "data" / f"{day.isoformat()}.json").write_text(
        json.dumps({"date": day.isoformat(), "stats": stats, "records": rows}, ensure_ascii=False, indent=1),
        encoding="utf-8")

    if not rows:
        report = no_record_report(day, missed_streak(day), skipped)
    else:
        prompt = (HERE / "PROMPT.md").read_text(encoding="utf-8")
        try:
            report = run_claude(prompt, build_input(day, stats, rows, hist))
        except (RuntimeError, subprocess.TimeoutExpired) as e:
            notify("Sayall 评估失败", str(e)[:180])
            print(f"错误：{e}", file=sys.stderr)
            return 3

    report_path.write_text(report, encoding="utf-8")
    for d in drive_mirror_dirs():
        try:
            d.mkdir(parents=True, exist_ok=True)
            (d / f"Sayall 评估 {day.isoformat()}.md").write_text(report, encoding="utf-8")
        except OSError as e:
            print(f"同步到 Drive 失败：{e}", file=sys.stderr)

    hl = headline(report)
    notify(f"Sayall 评估 {day.isoformat()}", hl)
    print(f"{hl} -> {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
