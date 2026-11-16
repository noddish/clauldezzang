"""home_demo.html 생성: 집 배경·오브젝트 조각·루비 그림을 data URI로 넣어 한 파일로 만든다.
실행: python3 tools/build_home_demo.py   (renpy-sprite-demo 폴더에서)
"""
import base64, glob, json, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
IMG = os.path.join(ROOT, "game", "images")
assets = {}
for sub in ("home", "objects", "ruby"):
    for path in sorted(glob.glob(os.path.join(IMG, sub, "*"))):
        name, ext = os.path.splitext(os.path.basename(path))
        mime = "image/png" if ext == ".png" else "image/jpeg"
        assets[name] = "data:%s;base64,%s" % (mime, base64.b64encode(open(path, "rb").read()).decode())
pos = json.load(open(os.path.join(ROOT, "game", "home", "objects_pos.json")))
html = open(os.path.join(ROOT, "tools", "home_demo_template.html"), encoding="utf-8").read()
html = html.replace("/*ASSETS*/{}", json.dumps(assets)).replace("/*POS*/{}", json.dumps(pos))
open(os.path.join(ROOT, "home_demo.html"), "w", encoding="utf-8").write(html)
print("home_demo.html", len(html) // 1024, "KB,", len(assets), "images")
