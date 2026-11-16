"""통짜 배경에서 '클릭할 물건'만 오려내 오브젝트 PNG로 만든다. (Summertime Saga 의 images/objects 방식)

배경 위 같은 좌표에 다시 겹치면 원래 그림과 똑같이 보이고,
마우스를 올렸을 때 그 조각만 밝게 바꿔서 '클릭할 수 있다'는 걸 보여준다.

실행: python3 tools/cut_objects.py   (renpy-sprite-demo 폴더에서)
결과: game/images/objects/object_<이름>_day.png / _night.png + game/home/objects_pos.json
"""
import json, os
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
HOME = os.path.join(ROOT, "game", "images", "home")
OUT = os.path.join(ROOT, "game", "images", "objects")

# 이름: (배경, 다각형 꼭짓점들 — 1280x720 좌표)
OBJECTS = {
    "bedroom_door":   ("bedroom",   [(1100, 20), (1245, 0), (1245, 595), (1100, 505)]),
    "bedroom_bed":    ("bedroom",   [(0, 250), (280, 250), (290, 345), (395, 350), (395, 510), (265, 625), (0, 625)]),
    "bedroom_desk":   ("bedroom",   [(635, 225), (1020, 225), (1020, 520), (635, 520)]),
    "hallway_mydoor": ("hallway",   [(210, 0), (365, 30), (365, 525), (210, 590)]),
    "hallway_bath":   ("hallway",   [(1035, 30), (1160, 0), (1160, 610), (1035, 525)]),
    "hallway_stairs": ("hallway",   [(535, 270), (955, 270), (955, 465), (535, 465)]),
    "entrance_stairs":("entrance",  [(175, 545), (175, 460), (400, 60), (560, 5), (565, 120), (480, 545)]),
    "entrance_door":  ("entrance",  [(612, 85), (805, 85), (805, 440), (612, 440)]),
    "entrance_kitchen":("entrance", [(985, 75), (1175, 25), (1175, 545), (985, 455)]),
    "entrance_living":("entrance",  [(0, 40), (170, 40), (170, 540), (0, 540)]),
    "kitchen_back":   ("kitchen",   [(30, 30), (195, 30), (195, 520), (30, 520)]),
    "kitchen_fridge": ("kitchen",   [(1110, 0), (1280, 0), (1280, 680), (1110, 640)]),
    "kitchen_stove":  ("kitchen",   [(935, 290), (1110, 290), (1110, 545), (935, 545)]),
    "living_door":    ("livingroom",[(1125, 40), (1265, 40), (1265, 400), (1125, 400)]),
    "living_couch":   ("livingroom",[(300, 200), (900, 200), (900, 430), (300, 430)]),
    "living_tv":      ("livingroom",[(0, 120), (230, 120), (230, 345), (0, 345)]),
}

os.makedirs(OUT, exist_ok=True)
pos = {}
for name, (room, poly) in OBJECTS.items():
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    box = (min(xs), min(ys), max(xs), max(ys))
    mask = Image.new("L", (1280, 720), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    for tod in ("day", "night"):
        bg = Image.open(os.path.join(HOME, "home_%s_%s.jpg" % (room, tod))).convert("RGBA")
        bg.putalpha(mask)
        bg.crop(box).save(os.path.join(OUT, "object_%s_%s.png" % (name, tod)), optimize=True)
    pos[name] = [box[0], box[1]]
with open(os.path.join(ROOT, "game", "home", "objects_pos.json"), "w") as f:
    json.dump(pos, f, indent=1)
print(len(OBJECTS), "objects")
