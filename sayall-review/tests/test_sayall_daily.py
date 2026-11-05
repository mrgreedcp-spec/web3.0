import datetime as dt
import importlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FIXTURE = HERE / "fixture_records.json"
DAY = dt.date(2026, 11, 4)


def load(env):
    os.environ.update(env)
    sys.path.insert(0, str(ROOT))
    import sayall_daily
    return importlib.reload(sayall_daily)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name) / "out"
        helper = Path(self.tmp.name) / "SayAllMCP"
        helper.write_text(f"#!/bin/sh\nMOCK_RECORDS='{FIXTURE}' exec {sys.executable} {HERE / 'mock_sayall_mcp.py'}\n")
        helper.chmod(0o755)
        fake = Path(self.tmp.name) / "claude"
        fake.write_text("#!/bin/sh\ncat > \"$FAKE_CLAUDE_STDIN\"\n"
                        "printf '# Sayall 评估\\n\\n**总分：5.4 / 10**（触发封顶：无）\\n\\n"
                        "| 结构 | 5.0 | - | - | x |\\n'\n")
        fake.chmod(0o755)
        self.stdin_dump = Path(self.tmp.name) / "stdin.txt"
        self.env = {"SAYALL_REPORT_DIR": str(self.out), "SAYALL_MCP_HELPER": str(helper),
                    "MOCK_RECORDS": str(FIXTURE), "SAYALL_MCP_CLIENT_ID": "c",
                    "SAYALL_MCP_ACCESS_TOKEN": "test-token", "SAYALL_CLAUDE_BIN": str(fake),
                    "FAKE_CLAUDE_STDIN": str(self.stdin_dump), "SAYALL_DRIVE_DIR": str(Path(self.tmp.name) / "drive")}
        self.m = load(self.env)

    def tearDown(self):
        self.tmp.cleanup()


class FetchTest(Base):
    def test_fetch_paginates_and_filters_by_local_day(self):
        recs, skipped = self.m.fetch_records(DAY)
        self.assertEqual([r["id"][-1] for r in recs], ["1", "2", "3", "4"])
        self.assertEqual(skipped, 0)

    def test_bad_token_raises(self):
        os.environ["SAYALL_MCP_ACCESS_TOKEN"] = "wrong"
        with self.assertRaises(self.m.MCPError) as cm:
            self.m.fetch_records(DAY)
        self.assertIn("invalid credentials", str(cm.exception))

    def test_missing_helper(self):
        self.m.HELPER = "/nonexistent/SayAllMCP"
        with self.assertRaises(self.m.MCPError):
            self.m.fetch_records(DAY)


class StatsTest(Base):
    def test_mixed_language_stats(self):
        recs = [r for r in json.loads(FIXTURE.read_text()) if r["localDateKey"] == "2026-11-04"]
        s, rows = self.m.analyze(recs)
        self.assertEqual(s["primary_language"], "en")
        self.assertEqual(s["records"], 4)
        en, zh = s["en"], s["zh"]
        # 1 秒那条不计入语速；中文那条按中文单独统计
        self.assertEqual(en["records"], 3)
        self.assertEqual(en["records_timed"], 2)
        self.assertEqual(rows[0]["en_words"], 23)
        self.assertEqual(rows[1]["en_words"], 24)
        self.assertEqual(rows[0]["rate"], 46.0)
        self.assertIsNone(rows[2]["rate"])
        self.assertEqual(en["rate_per_min"], round(47 / (50 / 60), 1))
        self.assertEqual(dict(en["fillers_top"]), {"um": 2, "uh": 1, "you know": 1})
        self.assertEqual(en["fillers_per_min"], round(4 / (50 / 60), 2))
        self.assertEqual(dict(en["soft_fillers_top"]), {"like": 1, "basically": 1})
        self.assertGreaterEqual(dict(en["weak_top"])["very"], 1)
        self.assertEqual(rows[3]["lang"], "zh")
        self.assertEqual(rows[3]["rate"], round(rows[3]["zh_chars"] / (40 / 60), 1))
        self.assertEqual(zh["rate_per_min"], rows[3]["rate"])
        self.assertEqual(dict(zh["fillers_top"]), {"就是说": 1, "然后": 1, "那个": 1, "这个": 1})
        self.assertTrue(s["sample_too_small"])

    def test_chinese_fillers_not_double_counted(self):
        c = self.m.count_zh("就是说我们然后那个就是", self.m.ZH_FILLERS)
        self.assertEqual(c, {"就是说": 1, "就是": 1, "然后": 1, "那个": 1})

    def test_word_boundaries(self):
        c = self.m.count_phrases("umbrella um, uhh. likely like", ["um+", "uh+", "like"])
        self.assertEqual(dict(c), {"um": 1, "uh": 1, "like": 1})

    def test_empty(self):
        s, rows = self.m.analyze([])
        self.assertEqual(rows, [])
        self.assertNotIn("en", s)
        self.assertIsNone(s["avg_sentence_len"])


class EndToEndTest(Base):
    def run_main(self, *args):
        return self.m.main(list(args))

    def test_full_run_writes_report_and_mirror(self):
        self.assertEqual(self.run_main("--date", "2026-11-04"), 0)
        rep = (self.out / "2026-11-04.md").read_text()
        self.assertIn("5.4 / 10", rep)
        self.assertTrue((Path(self.env["SAYALL_DRIVE_DIR"]) / "Sayall 评估 2026-11-04.md").exists())
        payload = self.stdin_dump.read_text()
        self.assertIn("we discuss about".lower(), payload.lower())
        self.assertNotIn("should be excluded", payload)
        data = json.loads((self.out / "data" / "2026-11-04.json").read_text())
        self.assertEqual(data["stats"]["records"], 4)

    def test_idempotent_and_history(self):
        self.run_main("--date", "2026-11-04")
        self.stdin_dump.unlink()
        self.assertEqual(self.run_main("--date", "2026-11-04"), 0)
        self.assertFalse(self.stdin_dump.exists(), "已有报告时不应再次调用 claude")
        h = self.m.history(dt.date(2026, 11, 5))
        self.assertEqual(h[0]["total"], 5.4)
        self.assertEqual(h[0]["dims"], {"结构": 5.0})

    def test_no_record_streak(self):
        for d in ("2026-11-06", "2026-11-07", "2026-11-08"):
            self.assertEqual(self.run_main("--date", d), 0)
        rep = (self.out / "2026-11-08.md").read_text()
        self.assertTrue(rep.startswith("# Sayall 评估 2026-11-08（无记录）"))
        self.assertIn("已连续 **3** 天", rep)

    def test_claude_failure_returns_error_and_writes_no_report(self):
        bad = Path(self.tmp.name) / "badclaude"
        bad.write_text("#!/bin/sh\necho boom >&2\nexit 1\n")
        bad.chmod(0o755)
        os.environ["SAYALL_CLAUDE_BIN"] = str(bad)
        self.assertEqual(self.run_main("--date", "2026-11-04"), 3)
        self.assertFalse((self.out / "2026-11-04.md").exists())


class CliFlagsTest(unittest.TestCase):
    def test_claude_flags_exist(self):
        """确认调用 claude 时用到的参数在当前 CLI 里存在。"""
        import shutil
        if not shutil.which("claude"):
            self.skipTest("no claude CLI")
        h = subprocess.run(["claude", "--help"], capture_output=True, text=True).stdout
        for flag in ("--tools", "--strict-mcp-config", "--no-session-persistence", "--output-format"):
            self.assertIn(flag, h)


if __name__ == "__main__":
    unittest.main()
