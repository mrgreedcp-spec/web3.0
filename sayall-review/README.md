# Sayall 每日表达评估

每天北京时间 07:40，Mac 自动读取前一天的 **无线麦SayAll.app** 语音转写历史，用程序统计语速、填充词、句长、弱词，再交给本机的 Claude Code 写一份评估。对标欧美一流大学高年级本科生的口头表达，按硬性封顶规则打分，不放水。安装后不需要任何手动操作。

## 为什么在 Mac 上跑

SayAll 的 MCP 是装在 App 里的本机程序（stdio），只读本地历史，不上传，云端会话连不到它。所以由 Mac 上的 launchd 每天调起，全程在本机完成，只有交给 Claude 写评估的那一步会把当天转写发给 Anthropic。

## 安装（一次）

前提：Mac 上已装 SayAll（含 MCP Helper）并在「回眸」里开启了「记录回眸」；已安装并登录 Claude Code（终端里能运行 `claude`）；Python 3.9 以上。

```bash
bash sayall-review/install.sh
```

脚本会：

1. 提示你在 SayAll「回眸 → 本地 Agent 访问」里为本工具**单独创建**一个名为 `sayall-review` 的只读授权，然后把 client ID 和令牌存进钥匙串（不写进任何文件）；
2. 试读一次 SayAll 记录，确认授权可用；
3. 装好 launchd 任务：每天 07:40（本机时间）运行。Mac 在那个时间睡眠的话，唤醒后补跑；关机错过的日子，下次运行时自动补最近 3 天。

现在就评估昨天：

```bash
bash sayall-review/daily.sh
```

卸载：

```bash
bash sayall-review/install.sh --uninstall
```

卸载后，到 SayAll 里撤销 `sayall-review` 的授权。

## 报告在哪里

- `~/outputs/sayall-reviews/2026-11-05.md`：每天一份；`data/` 子目录是当天的原始统计和转写（JSON）。
- 装了 **Google Drive 桌面版**的话，会同步一份到 `我的云端硬盘/Sayall/reviews/`，手机上也能看。这个文件夹已经建好。
- 生成后弹 macOS 通知，显示当天总分。
- 前一天没有任何语音记录也会出一份「无记录」报告，并统计连续几天没练。
- 日志：`~/outputs/sayall-reviews/launchd.log`。

## 评分标准

完整标准见 [PROMPT.md](PROMPT.md)。要点：

- 对标美国前 30、英国 G5 一档大学高年级本科生在 seminar、office hour、presentation 里的表达。不因为非母语或语音输入降低标准，拿不准时取低分。
- 6 个维度：结构 20%、逻辑与论证 20%、语言准确度 20%、词汇与地道度 15%、流利度与简洁 15%、语速与节奏 10%。
- **硬性封顶**：例如每百词语法错误超过 3 处，总分最高 6.0；超过 40 词的发言从不先给结论，结构最高 5 分；填充词超过 6 次/分钟，流利度最高 4 分；当天不足 150 词，总分最高 7.0。
- 报告包括：最严重的 3 个问题（原句 → 问题 → 母语本科生的说法）、**完整错误清单**、语速和填充词数据、2–3 个可量化的当天练习任务、7 天趋势。
- 中文记录对标受过良好教育的中文母语者在正式讨论中的表达，语速基准 200–260 字/分钟。

## 统计口径（程序算，不让模型估）

- **语速**：每条记录的词数（中文为字数）÷ 录音时长。短于 3 秒的记录不计入。时长包含开口前和句间的停顿，所以会低于纯发音语速。
- **填充词**：um / uh / er / hmm / you know / I mean / kind of / sort of；中文为 嗯 / 呃 / 就是（说）/ 然后 / 那个 / 这个 / 对吧 / 其实。like / actually / basically 等多义词单独列为「疑似」，不计入主指标。
- **弱词**：very、really、good、thing、stuff、a lot、just 等，按每百词统计。
- **词汇多样度**：每 100 词一段的标准化 TTR。
- 语音识别可能过滤掉填充词，所以填充词为 0 时，报告会注明，不直接给满分。

## 可调参数（环境变量）

| 变量 | 默认 | 用途 |
|---|---|---|
| `SAYALL_MCP_HELPER` | `/Applications/SayAll.app/Contents/Helpers/SayAllMCP` | App 不在默认位置时，填 SayAll 页面显示的 Helper 路径 |
| `SAYALL_REPORT_DIR` | `~/outputs/sayall-reviews` | 报告目录 |
| `SAYALL_DRIVE_DIR` | 自动查找 Drive 桌面版里的 `Sayall/reviews` | 同步目录 |
| `SAYALL_MODEL` | Claude Code 默认模型 | 指定写评估用的模型 |
| `SAYALL_TZ` | `Asia/Shanghai` | 「昨天」按哪个时区算 |

补跑某一天：`python3 sayall-review/sayall_daily.py --date 2026-11-03 --force`；只看统计、不调用模型：加 `--dry-run`。

## 测试

```bash
python3 -m unittest discover -s sayall-review/tests -v
```

测试用一个模拟的 SayAll MCP Helper 覆盖了：分页、按当地日期过滤、授权失败、中英混合统计、填充词边界、重复运行不重复调用模型、无记录连续天数、模型调用失败时不写报告。
