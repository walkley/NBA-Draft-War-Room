#!/bin/bash
# 为一位参与者新建一间作战室：找到数据并校验，复制模板、访谈问题和脚本，打印工作目录。
# 用法：bash scripts/new-room.sh [目标目录]
#
# 数据按以下顺序查找，用第一个存在 data.js 的目录：
#   1. 环境变量 NBA_WARROOM_DATA 指定的目录
#   2. ~/nba-warroom/data/
#   3. 本 skill 的 template/（本地开发时的旧位置）
# 都没有时使用 template/data.sample.js 的虚构示例数据，并给出提示。
# 数据目录内放 data.js 和 headshots/<id>.png，格式见 README.md。
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ROOM="${1:-$HOME/nba-warroom/room-$(date +%Y%m%d-%H%M%S)}"

DATA_DIR=""
for d in "${NBA_WARROOM_DATA:-}" "$HOME/nba-warroom/data" "$SKILL_DIR/template"; do
  if [ -n "$d" ] && [ -f "$d/data.js" ]; then
    DATA_DIR="$d"
    break
  fi
done

if [ -n "$DATA_DIR" ]; then
  python3 "$SKILL_DIR/scripts/check-data.py" "$DATA_DIR"
else
  echo "提示：未找到数据，使用虚构示例数据。正式使用请按 README.md 把数据放到 ~/nba-warroom/data/。" >&2
fi

if [ -e "$ROOM" ]; then
  echo "目标目录已存在：$ROOM" >&2
  exit 1
fi
mkdir -p "$ROOM/warroom"
for f in index.html DEV-NOTES.md; do
  cp "$SKILL_DIR/template/$f" "$ROOM/warroom/$f"
done
if [ -n "$DATA_DIR" ]; then
  cp "$DATA_DIR/data.js" "$ROOM/warroom/data.js"
  if [ -d "$DATA_DIR/headshots" ]; then
    cp -R "$DATA_DIR/headshots" "$ROOM/warroom/headshots"
  fi
else
  cp "$SKILL_DIR/template/data.sample.js" "$ROOM/warroom/data.js"
fi
cp "$SKILL_DIR/interview.md" "$ROOM/interview.md"
cp "$SKILL_DIR/scripts/trial.js" "$ROOM/trial.js"
cp "$SKILL_DIR/scripts/bundle.py" "$ROOM/bundle.py"
echo "作战室已就绪：$ROOM"
