#!/bin/bash
# 在 Mac 上安装每周 token 周报：每周一 9:07（本机时间）运行 weekly.sh。
# 卸载：launchctl bootout gui/$(id -u)/com.user.claude-token-weekly && rm ~/Library/LaunchAgents/com.user.claude-token-weekly.plist
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
LABEL="com.user.claude-token-weekly"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
chmod +x "$DIR/weekly.sh" "$DIR/token_stats.py"
mkdir -p "$HOME/Library/LaunchAgents" "$HOME/outputs/token-reports"

cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array><string>/bin/bash</string><string>$DIR/weekly.sh</string></array>
  <key>StartCalendarInterval</key>
  <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>9</integer><key>Minute</key><integer>7</integer></dict>
  <key>StandardOutPath</key><string>$HOME/outputs/token-reports/launchd.log</string>
  <key>StandardErrorPath</key><string>$HOME/outputs/token-reports/launchd.log</string>
</dict>
</plist>
PL

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "已安装：每周一 9:07 生成周报到 ~/outputs/token-reports/"
echo "立即试跑一次：bash \"$DIR/weekly.sh\""
