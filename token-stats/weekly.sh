#!/bin/bash
# 每周一由 launchd 调用：生成上周的 token 周报，存到 ~/outputs/token-reports/，并弹出 macOS 通知。
set -euo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
DIR="$(cd "$(dirname "$0")" && pwd)"
OUT="${TOKEN_REPORT_DIR:-$HOME/outputs/token-reports}"
mkdir -p "$OUT"

python3 "$DIR/token_stats.py" --week --out "$OUT" > /dev/null
REPORT="$(ls -t "$OUT"/*-W*.md | head -1)"

# 从报告里取两项做通知摘要
weighted="$(grep -m1 '^| 折算 token' "$REPORT" | awk -F'|' '{gsub(/ /,"",$3); gsub(/ /,"",$5); print $3 (NF>5 ? "（环比 " $5 "）" : "")}' || true)"
saving="$(grep -m1 '^| 缓存节约比例' "$REPORT" | awk -F'|' '{gsub(/ /,"",$3); print $3}' || true)"
msg="折算 token ${weighted:-无记录}，缓存节约 ${saving:--}"

osascript -e "display notification \"$msg\" with title \"Claude Code 上周 token 周报\" subtitle \"$(basename "$REPORT")\"" 2>/dev/null || true
echo "$msg -> $REPORT"
