#!/bin/bash
# 在 Mac 上安装 Sayall 每日表达评估：每天 07:40（本机时间）评估前一天的 SayAll 语音记录。
# 卸载：bash install.sh --uninstall
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
LABEL="com.user.sayall-review"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
OUT="$HOME/outputs/sayall-reviews"

if [ "${1:-}" = "--uninstall" ]; then
  launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
  rm -f "$PLIST"
  security delete-generic-password -s sayall-review -a client_id >/dev/null 2>&1 || true
  security delete-generic-password -s sayall-review -a access_token >/dev/null 2>&1 || true
  echo "已卸载（报告保留在 $OUT）。记得在 SayAll「回眸 → 本地 Agent 访问」里撤销 sayall-review 的授权。"
  exit 0
fi

command -v claude >/dev/null || [ -x "$HOME/.claude/local/claude" ] || { echo "未找到 claude 命令，请先安装并登录 Claude Code。"; exit 1; }
python3 -c 'import zoneinfo' 2>/dev/null || { echo "需要 Python 3.9 以上。"; exit 1; }

cat <<'TXT'
第 1 步：在 SayAll 里给本工具单独建一个只读授权（不要复用 Claude Desktop 等其他客户端的令牌）
  打开 无线麦SayAll.app → 回眸 → 本地 Agent 访问 → 打开总开关
  → 客户端名称填 sayall-review → 创建 → 复制「标准 MCP JSON」
  JSON 里的 SAYALL_MCP_CLIENT_ID 和 SAYALL_MCP_ACCESS_TOKEN 就是下面要填的两项。
TXT
read -r -p "SAYALL_MCP_CLIENT_ID: " CID
read -r -s -p "SAYALL_MCP_ACCESS_TOKEN（输入不显示）: " TOK; echo
[ -n "$CID" ] && [ -n "$TOK" ] || { echo "两项都不能为空。"; exit 1; }
security add-generic-password -U -s sayall-review -a client_id -w "$CID"
security add-generic-password -U -s sayall-review -a access_token -w "$TOK"
echo "已存入钥匙串（服务名 sayall-review）。"

echo "第 2 步：试读一次 SayAll 记录…"
python3 "$DIR/sayall_daily.py" --dry-run | head -40 || { echo "读取失败，请检查授权或 Helper 路径（SAYALL_MCP_HELPER）。"; exit 1; }

chmod +x "$DIR/daily.sh" "$DIR/sayall_daily.py"
mkdir -p "$HOME/Library/LaunchAgents" "$OUT"
cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array><string>/bin/bash</string><string>$DIR/daily.sh</string></array>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>7</integer><key>Minute</key><integer>40</integer></dict>
  <key>StandardOutPath</key><string>$OUT/launchd.log</string>
  <key>StandardErrorPath</key><string>$OUT/launchd.log</string>
</dict>
</plist>
PL
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "已安装：每天 07:40（本机时间，Mac 时区需为北京时间）生成报告到 $OUT/"
echo "现在就评估昨天：bash \"$DIR/daily.sh\""
