# NBA 选秀作战室（nba-draft-warroom）

这是一个 Kiro Crew skill，用于 60 分钟的 Agent 动手环节。参与者扮演一支 NBA 球队的老板，先回答 8 道关于用人标准的选择题。Agent 根据回答整理出管理风格档案，写成需求，再开发一套按这套标准选人的网页。参与者在档案、需求、成品三处审核，全程不写代码。

## 安装

在 Kiro Crew 里打开 **Settings → Skills → Discover**，输入 `walkley/NBA-Draft-War-Room`（也可以直接粘贴仓库链接），预览后点安装。

也可以把仓库克隆到 `~/.kiro/crew/skills/` 下，目录名随意。

## 准备数据

仓库里不带球员数据和头像，需要自己准备，放到 `~/nba-warroom/data/`：

```
~/nba-warroom/data/
├── data.js           球员数据，格式见 DATA.md
└── headshots/        头像，文件名为 <id>.png，可以不放
```

数据放在 skill 目录之外，重新导入或更新 skill 时不会被覆盖。准备好后运行校验：

```
python3 <skill 目录>/scripts/check-data.py
```

没有数据也能先体验：Agent 会改用 `template/data.sample.js` 里的 40 名虚构球员。

## 启动

在 Kiro Crew 控制台新建一个对话，发送：

```
开始选秀作战室
```

如果 Agent 没有进入流程，改发：

```
请找到 nba-draft-warroom 这个 skill，读取它的 SKILL.md，按里面的步骤开始
```

Agent 会在 `~/nba-warroom/room-<时间戳>/` 新建一间作战室，按 `SKILL.md` 的五个步骤往下走。成品是一个单独的文件 `warroom/作战室.html`，会用默认浏览器打开。

## 运行要求

- macOS。打包脚本用系统自带的 `sips` 压缩头像，没有 `sips` 时可以装 Pillow 代替。
- Python 3 和 Node.js。
- 建议开启免确认执行，不然每一步操作都会弹出确认框。

## 目录

| 路径 | 内容 |
|---|---|
| `SKILL.md` | 给 Agent 的流程指令 |
| `interview.md` | 访谈题目，以及每个选项对应的配置 |
| `DATA.md` | 数据格式 |
| `template/` | 作战室网页骨架、开发说明、示例数据 |
| `scripts/` | 建房、数据校验、试算、打包脚本 |
