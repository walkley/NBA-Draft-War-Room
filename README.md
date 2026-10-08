# NBA 选秀作战室（nba-draft-warroom）

一个 Kiro Crew skill，用于 60 分钟的 Agent 动手环节。参与者扮演 NBA 球队老板，回答约 8 道关于用人标准的选择题。Agent 据此整理管理风格档案、写需求，再开发一套按其标准运行的选人网页，参与者在三个节点审核。全程不写代码。

## 安装

在 Kiro Crew 的 **Settings → Skills → Discover** 中输入本仓库地址（`owner/repo`，或粘贴 GitHub 链接），预览后点安装。

也可以手动克隆到 `~/.kiro/crew/skills/` 下的任意目录名。

## 准备数据

本仓库不附带球员数据和头像。把数据放到 `~/nba-warroom/data/`：

```
~/nba-warroom/data/
├── data.js           球员数据，格式见 DATA.md
└── headshots/        头像，<id>.png，可选
```

然后校验：

```
python3 <skill 目录>/scripts/check-data.py
```

没有准备数据时，会自动使用 `template/data.sample.js` 中的 40 名虚构球员，可以先用它体验流程。

## 启动

在 Kiro Crew 控制台新建对话，发送：

```
开始选秀作战室
```

没有触发时改发 `$nba-draft-warroom 开始`。Agent 会在 `~/nba-warroom/room-<时间戳>/` 新建一间作战室，按 `SKILL.md` 的五个步骤推进。成品是单个文件 `warroom/作战室.html`，用默认浏览器打开。

## 要求

- macOS（打包脚本用系统自带的 `sips` 压缩头像；没有时可装 Pillow）
- Python 3、Node.js
- 建议开启免确认执行，否则每一步操作都会弹出确认

## 目录

| 路径 | 内容 |
|---|---|
| `SKILL.md` | 给 Agent 的流程指令 |
| `interview.md` | 访谈题目及其与配置的对应关系 |
| `DATA.md` | 数据格式 |
| `template/` | 作战室网页骨架、开发说明、示例数据 |
| `scripts/` | 建房、数据校验、试算、打包脚本 |
