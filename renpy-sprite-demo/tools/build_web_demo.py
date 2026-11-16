"""웹 데모 페이지 생성: 템플릿에 game/images 의 그림을 data URI로 넣어 한 파일로 만든다.

실행: python3 tools/build_web_demo.py   (renpy-sprite-demo 폴더에서)
결과: web_demo.html  (브라우저로 바로 열 수 있음)
"""
import base64, glob, json, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
assets = {}
for path in sorted(glob.glob(os.path.join(ROOT, "game", "images", "*", "*"))):
    name, ext = os.path.splitext(os.path.basename(path))
    mime = "image/png" if ext == ".png" else "image/jpeg"
    with open(path, "rb") as f:
        assets[name] = "data:%s;base64,%s" % (mime, base64.b64encode(f.read()).decode())

with open(os.path.join(ROOT, "tools", "web_demo_template.html"), encoding="utf-8") as f:
    html = f.read()
html = html.replace("/*ASSETS*/{}", json.dumps(assets))
with open(os.path.join(ROOT, "web_demo.html"), "w", encoding="utf-8") as f:
    f.write(html)
print("web_demo.html", len(html) // 1024, "KB,", len(assets), "images")
