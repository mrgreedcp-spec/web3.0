# Sayall 每日表达评估

Sayall 的回顾和转写同步到 Google Drive，Claude 每天北京时间 07:40 自动读取前一天的记录，对照欧美本科生的口头表达水平给出严厉评估，报告写回 Drive。

## 你要做的：把 Sayall 的转写放进 Drive

把每次的转写导出到 **`我的云端硬盘/Sayall/transcripts`**：
https://drive.google.com/drive/folders/1viY9ypl0WS2ckSMgGBpm0fNpvUMM_ct6

- 格式：`.txt`、`.docx`、`.srt`/`.vtt`、`.pdf`、Google 文档都行。**带时间戳的格式（srt/vtt 或带时间的 txt）最好**，有时间戳才能算准语速。
- 文件名建议以日期开头：`2026-11-05 组会发言.txt`。不按这个命名也行，任务会按文件的创建时间归到对应日期。
- 如果 Sayall 能自动导出到 Google Drive，就把导出目录设成上面这个文件夹；不能的话，手机或电脑上手动保存过去，或者用 Zapier 之类的自动化工具同步。
- 一段录音里有别人说话的，尽量保留说话人标签，任务只评你自己的部分。

## 报告在哪里看

**`我的云端硬盘/Sayall/reviews`**：
https://drive.google.com/drive/folders/1xbWCODREwooKmdprU78ptwbbJsWOh6tL

每天一份，标题 `Sayall 评估 2026-11-05`，完成后手机会收到推送。

## 评分标准

见 [PROMPT.md](PROMPT.md)。这份文件就是定时任务执行时用的完整说明；改了标准之后，需要同步更新定时任务的 prompt。
