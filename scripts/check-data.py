#!/usr/bin/env python3
"""校验数据目录里的 data.js 与 headshots/ 是否符合 README.md 的格式。

用法：python3 scripts/check-data.py [数据目录]
不给目录时依次查找 $NBA_WARROOM_DATA、~/nba-warroom/data/、本 skill 的 template/。
全部通过时退出码为 0；有错误时逐条打印并以 1 退出。
"""
import json
import os
import re
import sys
from pathlib import Path

SKILL_TEMPLATE = Path(__file__).resolve().parent.parent / "template"


def find_data_dir():
    if len(sys.argv) > 1:
        return Path(sys.argv[1]).expanduser().resolve()
    for d in (os.environ.get("NBA_WARROOM_DATA"), Path.home() / "nba-warroom" / "data", SKILL_TEMPLATE):
        if d and (Path(d) / "data.js").exists():
            return Path(d)
    return Path.home() / "nba-warroom" / "data"


TEMPLATE = find_data_dir()
DIM_KEYS = ["score", "create", "rebound", "defense", "steady", "gravity"]
ROLES = {"外线持球", "外线空间", "内线进攻", "内线接应"}
BIGS = {"季后赛更强", "季后赛下滑", "季后赛稳定", "未进季后赛"}
REQUIRED = ["id", "n", "t", "c", "pr", "role", "big", "img"]
OPTIONAL = ["en", "age", "yr", "fame", "pts", "reb", "ast", "o"]


def load(text, name):
    m = re.search(r"window\." + name + r"\s*=\s*(.*?);\s*(?:\n|$)", text, re.S)
    if not m:
        raise ValueError(f"data.js 中找不到 window.{name}")
    return json.loads(m.group(1))


def main():
    src = TEMPLATE / "data.js"
    if not src.exists():
        print(f"缺少 {src}，请按 README.md 准备数据。")
        return 1
    text = src.read_text(encoding="utf-8")
    errors, warns = [], []
    try:
        dims = load(text, "DIMS")
        players = load(text, "PLAYERS")
    except (ValueError, json.JSONDecodeError) as e:
        print(f"data.js 解析失败：{e}")
        return 1

    if sorted(dims) != sorted(DIM_KEYS):
        errors.append(f"DIMS 的键必须是 {DIM_KEYS}")
    if len(players) < 30:
        errors.append(f"只有 {len(players)} 名球员，至少需要 30 名才能组出有取舍的阵容")

    seen, no_img, remote = set(), 0, 0
    missing_opt = {k: 0 for k in OPTIONAL}
    for i, p in enumerate(players):
        tag = f"第 {i + 1} 名（{p.get('n', '?')}）"
        for k in REQUIRED:
            if p.get(k) in (None, ""):
                errors.append(f"{tag} 缺少必需字段 {k}")
        if p.get("id") in seen:
            errors.append(f"{tag} id 重复：{p.get('id')}")
        seen.add(p.get("id"))
        c = p.get("c")
        if isinstance(c, bool) or not isinstance(c, int) or c < 4:
            errors.append(f"{tag} 薪资 c 必须是不小于 4 的整数")
        pr = p.get("pr") or {}
        for k in DIM_KEYS:
            v = pr.get(k)
            if not isinstance(v, (int, float)) or not 0 <= v <= 100:
                errors.append(f"{tag} pr.{k} 必须在 0-100 之间")
        if p.get("role") and p["role"] not in ROLES:
            errors.append(f"{tag} role 取值无效：{p['role']}")
        if p.get("big") and p["big"] not in BIGS:
            errors.append(f"{tag} big 取值无效：{p['big']}")
        img = p.get("img") or ""
        if img.startswith("https://"):
            remote += 1
        elif img and img != f"headshots/{p.get('id')}.png":
            errors.append(f"{tag} img 必须是 https:// 地址或 headshots/{p.get('id')}.png，实际为 {img}")
        elif img and not (TEMPLATE / img).exists():
            no_img += 1
        for k in OPTIONAL:
            if p.get(k) is None:
                missing_opt[k] += 1

    # cap=14（「尽量省」）时，薪资不超过 14 的球员要足以组满 8 人且不超总预算 100
    cheap = sorted(p["c"] for p in players if isinstance(p.get("c"), int) and p["c"] <= 14)
    if len(cheap) < 8:
        warns.append(f"薪资不超过 14 的球员只有 {len(cheap)} 名，cap=14 时组不满 8 人")
    elif sum(cheap[:8]) > 100:
        warns.append("薪资不超过 14 的球员中最便宜的 8 人合计超过 100，cap=14 时组不满 8 人")

    if remote:
        warns.append(f"{remote} 名球员的头像是在线地址，需要联网才能显示，加载失败时显示灰色占位")
    if no_img:
        warns.append(f"{no_img} 名球员的头像文件不存在，将显示灰色占位")
    for k, n in missing_opt.items():
        if n:
            warns.append(f"{n} 名球员缺少可选字段 {k}")

    for w in warns[:20]:
        print("提示：" + w)
    for e in errors[:50]:
        print("错误：" + e)
    if errors:
        print(f"校验未通过：{len(errors)} 处错误。")
        return 1
    print(f"校验通过：{len(players)} 名球员。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
