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
    "bedroom_door":   ("bedroom",   [(1110, 40), (1170, 0), (1250, 0), (1250, 610), (1110, 560)]),
    "bedroom_bed":    ("bedroom",   [(0, 250), (290, 250), (290, 340), (395, 370), (395, 520), (260, 640), (0, 640)]),
    "bedroom_desk":   ("bedroom",   [(635, 260), (1040, 260), (1040, 525), (635, 525)]),
    "hallway_mydoor": ("hallway",   [(225, 20), (350, 40), (350, 560), (225, 620)]),
    "hallway_bath":   ("hallway",   [(1045, 40), (1175, 20), (1175, 620), (1045, 560)]),
    "hallway_stairs": ("hallway",   [(530, 300), (970, 300), (970, 500), (530, 500)]),
    "entrance_stairs":("entrance",  [(175, 545), (175, 460), (420, 60), (550, 0), (570, 120), (480, 545)]),
    "entrance_door":  ("entrance",  [(625, 105), (795, 105), (795, 470), (625, 470)]),
    "entrance_kitchen":("entrance", [(1010, 90), (1185, 50), (1185, 555), (1010, 480)]),
    "entrance_living":("entrance",  [(0, 40), (160, 40), (160, 540), (0, 540)]),
    "kitchen_back":   ("kitchen",   [(35, 40), (200, 40), (200, 530), (35, 530)]),
    "kitchen_fridge": ("kitchen",   [(1130, 0), (1280, 0), (1280, 700), (1130, 700)]),
    "kitchen_stove":  ("kitchen",   [(955, 230), (1125, 230), (1125, 580), (955, 580)]),
    "living_door":    ("livingroom",[(1120, 40), (1240, 40), (1240, 340), (1120, 340)]),
    "living_couch":   ("livingroom",[(330, 250), (885, 250), (885, 480), (330, 480)]),
    "living_tv":      ("livingroom",[(0, 170), (280, 170), (280, 530), (0, 530)]),
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
