#!/usr/bin/env node
// 试算：用 index.html 自带的推荐逻辑，按一份 boss 配置打印推荐阵容、核心、预算、六维平均，
// 并试渲染四个页面检查报错和 undefined。不启动任何服务。
// 用法：node trial.js <boss 配置文件> [作战室目录]
//   作战室目录默认为本脚本所在目录（new-room.sh 已把本脚本拷进作战室）。
const fs = require("fs"), path = require("path"), vm = require("vm");
const [bossFile, roomArg] = process.argv.slice(2);
if (!bossFile) { console.error("用法：node trial.js <boss 配置文件> [作战室目录]"); process.exit(2); }
const root = path.resolve(roomArg || __dirname);
const web = ["warroom", "template"].map(d => path.join(root, d)).find(d => fs.existsSync(path.join(d, "index.html")));
if (!web) { console.error(`找不到 ${root}/warroom/index.html`); process.exit(2); }

const html = fs.readFileSync(path.join(web, "index.html"), "utf8");
const inline = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const el = () => ({ style: {}, classList: { toggle() {} }, textContent: "", innerHTML: "" });
const els = {};
const ctx = { console, document: { getElementById: id => (els[id] ||= el()), querySelectorAll: () => [] } };
ctx.window = ctx; vm.createContext(ctx);
const run = (code, name) => vm.runInContext(code, ctx, { filename: name });
run(fs.readFileSync(path.join(web, "data.js"), "utf8"), "data.js");
run(fs.readFileSync(path.resolve(bossFile), "utf8"), path.basename(bossFile));
if (!ctx.BOSS) { console.error("配置文件没有定义 window.BOSS"); process.exit(2); }
run(inline + "\n;window.__T = { recommend, CTX, VIEWS, score, byId, BUDGET };", "index.html");

const T = ctx.__T, B = ctx.BOSS, C = T.CTX;
const wsum = Object.values(B.w).reduce((s, v) => s + v, 0);
console.log(`权重合计：${Math.round(wsum * 1000) / 1000}${Math.abs(wsum - 1) > 1e-6 ? "（不等于 1，需修正）" : ""}`);
console.log(`cap ${B.cap}，core ${typeof B.core === "function" ? "已设" : "未设"}，exclude ${typeof B.exclude === "function" ? "已设" : "未设"}`);
console.log("\n推荐阵容（按评分）：");
for (const p of C.roster) console.log(`  ${p.n}  薪资 ${p.c}  评分 ${T.score(p)}  ${p.big}  ${p.role}`);
const core = C.core;
console.log(core.length ? `\n核心：${core.map(p => p.n).join("、")}`
  : `\n核心：无（${typeof B.core === "function" ? "无人满足 core 条件" : "未设 core"}），评分最高两人：${C.roster.slice(0, 2).map(p => p.n).join("、")}`);
console.log(`预算：${C.spent} / ${T.BUDGET}（模拟值）${C.roster.length < 8 ? `；只选出 ${C.roster.length} 人，未满 8 人` : ""}`);
const prof = C.profile;
console.log("六维平均：" + C.DIM_KEYS.map(k => `${C.DIMS[k]} ${prof[k]}`).join("  "));
console.log(`短板：${C.gaps().join("、") || "无"}`);

let bad = 0;
for (const v of ["home", "pool", "pick", "report"]) {
  try {
    const out = T.VIEWS[v]();
    if (/undefined|NaN/.test(out)) { bad++; console.log(`页面 ${v}：输出中含 undefined 或 NaN`); }
  } catch (e) { bad++; console.log(`页面 ${v}：报错 ${e.message}`); }
}
console.log(bad ? `\n页面检查：${bad} 处问题` : "\n页面检查：四个页面渲染正常");
process.exit(bad ? 1 : 0);
