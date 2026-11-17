#!/usr/bin/env python3
"""AI 로 만든 원본 그림 → 게임 규격 그림 (game/images/...)

원본 폴더(RAW)에는 이미지 서버에서 받은 PNG 를 이름만 바꿔 넣어 둔다.
    배경    <장소>.png            1536x1024
    인물    <이름>.png            1024x1536 (몸, 기본 표정)
    표정    <이름>_<표정>.png     같은 그림에서 표정만 바꾼 것
    적      <종류>.png            투명 배경
    아이템  items.png             4x4 칸

    python3 tools/art_pipeline.py RAW all        # 전부
    python3 tools/art_pipeline.py RAW bg         # 배경만 (bg, sprite, face, enemy, icon, object)

원본은 커서 저장소에 넣지 않는다. 결과물만 커밋한다.
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "game", "images")
SCREEN = (1280, 720)

## ---------------------------------------------------------------- 배경
## 1536x1024 → 위아래 80px 잘라 3:2 → 16:9 → 1280x720
## night: 밤 그림을 따로 그리지 않고 어둡게 + 파랗게 (원작도 밤 배경은 대부분 보정본)
BGS = {
    "guild_hall": True, "guild_room": True, "guild_kitchen": True, "guild_front": False,
    "square": True, "tavern": True, "shop": True, "forest": True, "map": True,
    "cave_1": False, "cave_2": False,
}


def night_filter(im):
    im = ImageEnhance.Brightness(im).enhance(0.42)
    im = ImageEnhance.Color(im).enhance(0.7)
    return Image.blend(im, Image.new("RGB", im.size, (25, 35, 95)), 0.28)


def do_bg(raw):
    out = os.path.join(IMG, "bg")
    os.makedirs(out, exist_ok=True)
    for name, night in BGS.items():
        im = Image.open(os.path.join(raw, name + ".png")).convert("RGB")
        im = im.crop((0, 80, 1536, 944)).resize(SCREEN, Image.LANCZOS)
        im.save(os.path.join(out, "bg_%s_day.jpg" % name), quality=88)
        if night:
            night_filter(im).save(os.path.join(out, "bg_%s_night.jpg" % name), quality=88)
        print("bg", name, "+night" if night else "")


## ---------------------------------------------------------------- 인물
## 1024x1536 → 480x720 (루비와 같은 캔버스). 얼굴 조각은 같은 캔버스에 얼굴만 남기고 투명.
## FACES: 원본(1024x1536) 좌표의 얼굴 타원 (중심 x, y, 반지름 x, y) — 눈썹부터 턱까지
CHARS = {
    "kai":    {"faces": ["happy", "surprised", "sad", "angry", "talk"], "ellipse": (560, 320, 128, 142)},
    "martha": {"faces": ["happy", "angry", "surprised", "talk"],        "ellipse": (440, 350, 140, 150)},
    "pip":    {"faces": ["happy", "sad", "surprised", "talk"],          "ellipse": (465, 555, 120, 118)},
    "gregor": {"faces": ["happy", "angry", "talk"],                     "ellipse": (450, 300, 132, 152)},
}
SPRITE = (480, 720)
SPRITE_RAW = (1024, 1536)


def do_sprite(raw):
    for name in CHARS:
        out = os.path.join(IMG, "characters", name)
        os.makedirs(out, exist_ok=True)
        im = Image.open(os.path.join(raw, name + ".png")).convert("RGBA")
        im.resize(SPRITE, Image.LANCZOS).save(os.path.join(out, "%s_body.png" % name), optimize=True)
        print("sprite", name)


def gray_on_white(im):
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    return bg.convert("L")


def place(ex, s, dx, dy):
    """표정 그림을 s 배 키우고 (dx, dy) 옮긴 것 (캔버스 크기는 그대로)"""
    if s != 1.0:
        ex = ex.resize((round(ex.width * s), round(ex.height * s)), Image.LANCZOS)
    canvas = Image.new("RGBA", SPRITE_RAW, (0, 0, 0, 0))
    sx, sy = max(0, -dx), max(0, -dy)
    ex = ex.crop((sx, sy, min(ex.width, sx + SPRITE_RAW[0] - max(0, dx)), min(ex.height, sy + SPRITE_RAW[1] - max(0, dy))))
    canvas.alpha_composite(ex, (max(0, dx), max(0, dy)))
    return canvas


def register(body, ex, box):
    """표정 그림이 원본과 어긋나게(밀리거나 크기가 달라져) 나왔을 때 맞추는 배율·이동을 찾는다.
    box(얼굴 주변 머리카락·목·어깨) 의 차이가 가장 작아지는 값. 반 크기로 대충 찾고 원래 크기로 다듬는다."""
    PAD = 120
    ga, ge = gray_on_white(body), gray_on_white(ex)
    cache = {}

    def arrays(s, k):
        if (s, k) not in cache:
            a = np.asarray(ga.resize((ga.width // k, ga.height // k)), np.float32)
            b = np.asarray(ge.resize((round(ge.width * s / k), round(ge.height * s / k))), np.float32)
            cache[(s, k)] = (a, np.pad(b, PAD // k, constant_values=255))
        return cache[(s, k)]

    def cost(s, dx, dy, k):
        a, b = arrays(s, k)
        x0, y0, x1, y1 = [v // k for v in box]
        p, ox, oy = PAD // k, dx // k, dy // k
        return float(np.abs(a[y0:y1, x0:x1] - b[y0 - oy + p:y1 - oy + p, x0 - ox + p:x1 - ox + p]).mean())

    best = (cost(1.0, 0, 0, 1), 1.0, 0, 0)
    if best[0] < 12:                       # 거의 그대로 나온 경우 (대부분)
        return best
    for s in np.round(np.arange(0.90, 1.101, 0.02), 2):
        for dy in range(-96, 97, 8):
            for dx in range(-96, 97, 8):
                c = cost(s, dx, dy, 4)
                if c < best[0]:
                    best = (c, s, dx, dy)
    _, s0, dx0, dy0 = best
    best = (cost(s0, dx0, dy0, 1), s0, dx0, dy0)
    for s in np.round((s0 - 0.01, s0, s0 + 0.01), 2):
        for dy in range(dy0 - 8, dy0 + 9):
            for dx in range(dx0 - 8, dx0 + 9):
                c = cost(s, dx, dy, 1)
                if c < best[0]:
                    best = (c, s, dx, dy)
    return best


def do_face(raw):
    for name, spec in CHARS.items():
        out = os.path.join(IMG, "characters", name)
        body = Image.open(os.path.join(raw, name + ".png")).convert("RGBA")
        cx, cy, rx, ry = spec["ellipse"]
        ## 맞춤 비교 구역: 얼굴 타원 바깥 둘레 (머리카락, 목, 어깨)
        ring = (cx - rx - 90, cy - ry - 60, cx + rx + 90, cy + ry + 90)
        area = Image.new("L", body.size, 0)
        ImageDraw.Draw(area).ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=255)
        for face in spec["faces"]:
            ex = Image.open(os.path.join(raw, "%s_%s.png" % (name, face))).convert("RGBA")
            d, s, dx, dy = register(body, ex, ring)
            ex = place(ex, s, dx, dy)
            ## 얼굴 조각 = 타원 안에서 '실제로 달라진 곳'만 (눈썹·눈·입).
            ## 머리카락처럼 거의 같은 곳은 원래 몸 그림을 그대로 둬서 경계선이 안 보이게 한다.
            diff = ImageChops.difference(gray_on_white(body), gray_on_white(ex)).filter(ImageFilter.GaussianBlur(2))
            changed = diff.point(lambda v: 255 if v > 14 else 0).filter(ImageFilter.MaxFilter(15))
            mask = ImageChops.multiply(changed, area).filter(ImageFilter.GaussianBlur(5))
            piece = ex.copy()                       # 색은 그대로, 투명도만 조각 모양으로
            piece.putalpha(ImageChops.multiply(mask, ex.getchannel("A")))
            piece.resize(SPRITE, Image.LANCZOS).save(
                os.path.join(out, "%s_face_%s.png" % (name, face)), optimize=True)
            print("face %-7s %-9s scale=%.2f shift=(%d,%d) ring_diff=%.1f" % (name, face, s, dx, dy, d))


## ---------------------------------------------------------------- 적
## 투명 여백을 잘라내고 키를 맞춘다. 바닥(발)이 그림 아래 끝.
ENEMIES = {"slime": 160, "goblin": 250, "mushroom": 220, "toad_king": 380}


def do_enemy(raw):
    out = os.path.join(IMG, "enemies")
    os.makedirs(out, exist_ok=True)
    for name, h in ENEMIES.items():
        im = Image.open(os.path.join(raw, name + ".png")).convert("RGBA")
        im = im.crop(im.getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox())
        w = round(im.width * h / im.height)
        im.resize((w, h), Image.LANCZOS).save(os.path.join(out, "enemy_%s.png" % name), optimize=True)
        print("enemy", name, (w, h))


## ---------------------------------------------------------------- 아이템 아이콘
ICON_GRID = [
    ["potion", "hi_potion", "ether", "antidote"],
    ["bomb", "short_sword", "iron_sword", "ruby_blade"],
    ["leather_vest", "chain_vest", "lucky_charm", "flint"],
    ["pip_cargo", "guild_notice", "slime_jelly", "goblin_fang"],
]
ICON = 96


def do_icon(raw):
    out = os.path.join(IMG, "items")
    os.makedirs(out, exist_ok=True)
    sheet = Image.open(os.path.join(raw, "items.png")).convert("RGBA")
    cw, ch = sheet.width // 4, sheet.height // 4
    for r, row in enumerate(ICON_GRID):
        for c, iid in enumerate(row):
            cell = sheet.crop((c * cw, r * ch, (c + 1) * cw, (r + 1) * ch))
            cell = cell.crop(cell.getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox())
            s = (ICON - 8) / max(cell.size)
            cell = cell.resize((max(1, round(cell.width * s)), max(1, round(cell.height * s))), Image.LANCZOS)
            icon = Image.new("RGBA", (ICON, ICON), (0, 0, 0, 0))
            icon.alpha_composite(cell, ((ICON - cell.width) // 2, (ICON - cell.height) // 2))
            icon.save(os.path.join(out, "icon_%s.png" % iid), optimize=True)
    print("icons", sum(len(r) for r in ICON_GRID))


## ---------------------------------------------------------------- 클릭할 물건 모양
## tools/art_objects.json: {장소: {물건: [[x,y], ...] 다각형 (1280x720 좌표)}}
## 다각형 모양 마스크(bbox 크기, 1비트 PNG)만 저장한다 → world.rpy 의 rect 는 그 bbox.
## 원작은 배경과 똑같은 조각 PNG 를 낮·밤 따로 얹었지만(물건 하나에 수백 KB),
## 여기서는 게임이 현재 배경을 마스크 모양으로 잘라 마우스를 올렸을 때만 밝게 그린다.
def do_object(raw):
    with open(os.path.join(ROOT, "tools", "art_objects.json"), encoding="utf-8") as f:
        spec = json.load(f)
    out = os.path.join(IMG, "objects")
    os.makedirs(out, exist_ok=True)
    for loc, objs in spec.items():
        if loc.startswith("_"):
            continue
        for oid, poly in objs.items():
            poly = [tuple(p) for p in poly]
            xs, ys = [p[0] for p in poly], [p[1] for p in poly]
            box = (min(xs), min(ys), max(xs) + 1, max(ys) + 1)
            mask = Image.new("P", SCREEN, 0)
            mask.putpalette([0, 0, 0, 255, 255, 255])
            ImageDraw.Draw(mask).polygon(poly, fill=1)
            mask.crop(box).save(os.path.join(out, "mask_%s_%s.png" % (loc, oid)), transparency=0, optimize=True)
            print("object %-14s %-8s rect=%s" % (loc, oid, (box[0], box[1], box[2] - box[0], box[3] - box[1])))


STEPS = {"bg": do_bg, "sprite": do_sprite, "face": do_face, "enemy": do_enemy,
         "icon": do_icon, "object": do_object}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    raw = sys.argv[1]
    names = list(STEPS) if sys.argv[2] == "all" else sys.argv[2:]
    for n in names:
        STEPS[n](raw)
