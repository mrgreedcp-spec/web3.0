#!/bin/bash
# launchd 每天调用：评估昨天（北京时间）的 SayAll 语音记录。日志：~/outputs/sayall-reviews/launchd.log
set -uo pipefail
export PATH="$HOME/.local/bin:$HOME/.claude/local:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
DIR="$(cd "$(dirname "$0")" && pwd)"
echo "=== $(date '+%F %T') ==="
# Mac 晚上没开机时 launchd 会在唤醒后补跑；再顺手补跑最近 3 天里漏掉的日子。
for back in 3 2; do
  d="$(python3 -c "import datetime as d,zoneinfo as z;print((d.datetime.now(z.ZoneInfo('Asia/Shanghai')).date()-d.timedelta(days=$back)).isoformat())")"
  [ -f "${SAYALL_REPORT_DIR:-$HOME/outputs/sayall-reviews}/$d.md" ] || python3 "$DIR/sayall_daily.py" --date "$d"
done
python3 "$DIR/sayall_daily.py" "$@"
