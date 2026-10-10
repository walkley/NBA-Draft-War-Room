#!/usr/bin/env python3
"""把作战室打包成一个自包含的 HTML 文件。

用法：python3 bundle.py <warroom 目录>
输出：<warroom 目录>/作战室.html

index.html 用 <script src> 引用 data.js 和 boss.js，打包后脚本都内联在一个文件里，可以单独拷贝（如 AirDrop 到投屏主控机），用默认浏览器打开。
头像默认是 NBA CDN 的在线地址，保持外链不内联，打开时需要联网。
如果作战室目录下有 headshots/<id>.png（使用者自备的本地头像），会压缩后内联进文件，断网也能显示。
dashboard 右侧面板预览 HTML 时禁用脚本，作战室在面板里只会显示空白，不要用面板打开。
"""
import base64
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


#: 单文件体积提醒线。只在内联本地头像时有意义：原尺寸内联约 6.5MB，压成 160px 宽的 JPEG 后整页约 2MB。
LIMIT = 4 * 1024 * 1024
MARGIN = 3_800_000


def thumbnails(src: Path) -> dict:
    """返回 {球员 id: data URI}。优先用 macOS 自带的 sips，没有就试 Pillow，都没有就不带头像。"""
    pngs = sorted(src.glob("*.png"))
    out = {}
    with tempfile.TemporaryDirectory() as tmp:
        for png in pngs:
            dst = Path(tmp) / (png.stem + ".jpg")
            ok = False
            if shutil.which("sips"):
                r = subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "70",
                                    "--resampleWidth", "160", str(png), "--out", str(dst)],
                                   capture_output=True)
                ok = r.returncode == 0 and dst.exists()
            if not ok:
                try:
                    from PIL import Image
                    im = Image.open(png).convert("RGBA")
                    bg = Image.new("RGB", im.size, (17, 24, 39))
                    bg.paste(im, mask=im.split()[3])
                    bg.thumbnail((160, 160))
                    bg.save(dst, "JPEG", quality=70)
                    ok = True
                except Exception:
                    ok = False
            if not ok:
                print("没有 sips 也没有 Pillow，打包文件不带头像")
                return {}
            out[png.stem] = "data:image/jpeg;base64," + base64.b64encode(dst.read_bytes()).decode()
    return out


def main() -> int:
    if len(sys.argv) != 2:
        print("用法：python3 bundle.py <warroom 目录>")
        return 2
    room = Path(sys.argv[1]).expanduser().resolve()
    html = (room / "index.html").read_text(encoding="utf-8")
    data = (room / "data.js").read_text(encoding="utf-8")
    boss = (room / "boss.js").read_text(encoding="utf-8")

    shots = thumbnails(room / "headshots")
    fix = (
        "window.__HS=" + json.dumps(shots) + ";"
        "window.PLAYERS.forEach(function(p){var s=window.__HS[String(p.id)];if(s)p.img=s;});"
    )

    def inline(code: str) -> str:
        return "<script>\n" + code.replace("</script", "<\\/script") + "\n</script>"

    for tag, code in (('<script src="data.js"></script>', data + "\n" + fix),
                      ('<script src="boss.js"></script>', boss)):
        if tag not in html:
            print(f"index.html 里找不到 {tag}，骨架可能被改过，打包中止")
            return 1
        html = html.replace(tag, inline(code), 1)

    out = room / "作战室.html"
    out.write_text(html, encoding="utf-8")
    print(f"已生成 {out}（{len(html) // 1024} K 字符，头像 {len(shots)} 张）")
    if len(html) > MARGIN:
        print(f"打包文件接近 {LIMIT // 1024 // 1024}MB，头像可能过大；仍可用默认浏览器打开")
    return 0


if __name__ == "__main__":
    sys.exit(main())
