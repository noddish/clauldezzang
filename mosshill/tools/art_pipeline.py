#!/usr/bin/env python3
"""AI 로 만든 원본 그림 → 게임 규격 그림 (game/images/...)

원본 폴더(RAW)에는 이미지 서버에서 받은 PNG 를 이름만 바꿔 넣어 둔다.
    배경    <장소>.png            1536x1024
    인물    <이름>.png            1024x1536 (몸, 기본 표정)
    표정    <이름>_<표정>.png     같은 그림에서 표정만 바꾼 것
    적      <종류>.png            투명 배경
    아이템  items.png             4x4 칸
    장소 인물 scene_<장소>_<인물>_<busy|look>.png  배경 원본에 인물을 그려 넣은 것 (하던 일 / 앞을 봄)

    python3 tools/art_pipeline.py RAW all        # 전부
    python3 tools/art_pipeline.py RAW bg         # 배경만 (bg, sprite, face, enemy, icon, object, scene)

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
## face_box: 원본(1024x1536) 좌표에서 표정이 바뀔 수 있는 곳 (이마·눈썹부터 턱까지, 넉넉하게).
##   이 안에서 '실제로 달라진 곳'만 조각으로 가져간다. 상자가 좁으면 움직인 눈썹의 원래 자리가
##   상자 밖에 남아 눈썹이 두 개로 보인다 (처음 만든 타원 영역에서 실제로 생긴 문제).
## frame: (배율, 머리 꼭대기 y) — 원본 그림의 크기·위치를 바꿀 때만.
##   핍은 전신을 작게 그려 와서 다른 인물 옆에 서면 너무 작다 → 1.3배 키우고 허벅지에서 자른다.
##   (머리는 다른 인물보다 낮게 둬서 키 작은 하플링으로 보이게)
CHARS = {
    "kai":    {"faces": ["happy", "surprised", "sad", "angry", "talk"], "face_box": (400, 140, 730, 480)},
    "martha": {"faces": ["happy", "angry", "surprised", "talk"],        "face_box": (260, 160, 630, 520)},
    "pip":    {"faces": ["happy", "sad", "surprised", "talk"],          "face_box": (300, 380, 630, 740),
               "frame": (1.3, 427)},
    "gregor": {"faces": ["happy", "angry", "talk"],                     "face_box": (290, 110, 620, 480)},
}
SPRITE = (480, 720)
SPRITE_RAW = (1024, 1536)


def framed(im, spec, body):
    """원본 캔버스에서 인물의 크기·위치를 바꾼다 (spec 의 frame). 몸과 표정 조각에 똑같이 적용."""
    if "frame" not in spec:
        return im
    s, top = spec["frame"]
    x0, y0, x1, y1 = body.getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox()
    cx = (x0 + x1) / 2
    return place(im, s, round(cx - cx * s), round(top - y0 * s))


def do_sprite(raw):
    for name, spec in CHARS.items():
        out = os.path.join(IMG, "characters", name)
        os.makedirs(out, exist_ok=True)
        im = Image.open(os.path.join(raw, name + ".png")).convert("RGBA")
        framed(im, spec, im).resize(SPRITE, Image.LANCZOS).save(os.path.join(out, "%s_body.png" % name), optimize=True)
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
        x0, y0, x1, y1 = spec["face_box"]
        ## 맞춤 비교 구역: 얼굴 상자 둘레 (머리카락, 목, 어깨)
        ring = (x0 - 70, y0 - 60, x1 + 70, y1 + 90)
        area = Image.new("L", body.size, 0)
        ImageDraw.Draw(area).rectangle((x0, y0, x1, y1), fill=255)
        area = area.filter(ImageFilter.GaussianBlur(10))
        for face in spec["faces"]:
            ex = Image.open(os.path.join(raw, "%s_%s.png" % (name, face))).convert("RGBA")
            d, s, dx, dy = register(body, ex, ring)
            ex = place(ex, s, dx, dy)
            ## 얼굴 조각 = 상자 안에서 '실제로 달라진 곳'만 (눈썹·눈·입, 원래 눈썹이 있던 자리 포함).
            ## 머리카락처럼 거의 같은 곳은 원래 몸 그림을 그대로 둬서 경계선이 안 보이게 한다.
            diff = ImageChops.difference(gray_on_white(body), gray_on_white(ex)).filter(ImageFilter.GaussianBlur(2))
            changed = diff.point(lambda v: 255 if v > 14 else 0).filter(ImageFilter.MaxFilter(15))
            mask = ImageChops.multiply(changed, area).filter(ImageFilter.GaussianBlur(5))
            piece = ex.copy()                       # 색은 그대로, 투명도만 조각 모양으로
            piece.putalpha(ImageChops.multiply(mask, ex.getchannel("A")))
            ## 검사: 몸 + 조각 이 표정 그림과 얼마나 다른가 (원래 눈썹 같은 흔적이 남으면 커진다).
            ## 맞춤이 1~2px 어긋나 생기는 가는 윤곽선 차이는 무시하고(MinFilter) 덩어리만 센다.
            comp = body.copy()
            comp.alpha_composite(piece)
            left = ImageChops.difference(gray_on_white(comp), gray_on_white(ex)).filter(ImageFilter.GaussianBlur(1.5))
            left = left.point(lambda v: 255 if v > 40 else 0).filter(ImageFilter.MinFilter(7))
            left = np.asarray(left.crop(spec["face_box"])) > 0
            framed(piece, spec, body).resize(SPRITE, Image.LANCZOS).save(
                os.path.join(out, "%s_face_%s.png" % (name, face)), optimize=True)
            print("face %-7s %-9s scale=%.2f shift=(%d,%d) ring_diff=%.1f leftover=%.2f%%%s" % (
                name, face, s, dx, dy, d, left.mean() * 100, "  <-- 확인 필요" if left.mean() > 0.003 else ""))


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


## ---------------------------------------------------------------- 장소 안 인물
## tools/art_scenes.json: {장소: {인물: {"box": [x0,y0,x1,y1], "shape": 다각형, ...}}}
## RAW/scene_<장소>_<인물>_<busy|look>.png = 배경 원본에 인물을 그려 넣은 그림 (같은 구도) 두 장.
##   busy: 하던 일을 보고 있음 / look: 카이가 들어와서 앞(카메라)을 봄 — 들어갈 때 busy → look 으로 바뀐다.
## 원래 배경과 다른 곳 = 인물 → 화면 크기(1280x720) 투명 PNG 로 저장 (위치 정보가 따로 필요 없다).
## 두 장은 '둘 중 하나라도 다른 곳'(합친 모양)으로 똑같이 오린다 → 겹쳐서 서서히 바꿔도 비치지 않는다.
## 식탁·계산대 뒤에 선 인물은 앞의 가구가 배경에 그대로 있으니 가려지는 것도 저절로 맞는다.
SCENE_STATES = ("busy", "look")


def largest_blob(m):
    """참/거짓 배열에서 가장 큰 덩어리만 남긴다 (4방향 연결)"""
    h, w = m.shape
    seen = np.zeros_like(m, dtype=bool)
    best = []
    for y0, x0 in zip(*np.nonzero(m)):
        if seen[y0, x0]:
            continue
        stack, blob = [(y0, x0)], []
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            blob.append((y, x))
            for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= ny < h and 0 <= nx < w and m[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    stack.append((ny, nx))
        if len(blob) > len(best):
            best = blob
    out = np.zeros_like(m, dtype=bool)
    if best:
        ys, xs = zip(*best)
        out[list(ys), list(xs)] = True
    return out


def match_colors(sc, bg, box):
    """AI 가 인물을 그려 넣으면서 방 전체 색조를 살짝 바꾸는 일이 있다 (바닥에 네모난 경계가 생김).
    인물 범위(box) 바깥은 원래 배경과 같아야 하므로, 그 부분으로 색 보정식(채널별 a*x+b)을 구해 그림 전체에 적용한다."""
    a = np.asarray(sc, np.float32)
    b = np.asarray(bg, np.float32)
    x0, y0, x1, y1 = box
    outside = np.ones(a.shape[:2], bool)
    outside[max(0, y0 - 30):y1 + 30, max(0, x0 - 30):x1 + 30] = False
    out = a.copy()
    for c in range(3):
        gain, offset = np.polyfit(a[..., c][outside], b[..., c][outside], 1)
        out[..., c] = a[..., c] * gain + offset
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def changed_mask(bg, sc, box):
    """배경과 다른 곳: 색 차이 → 잡티 제거 → 틈 메우기 → 가장 큰 덩어리 → 속 구멍 채우기 (box 크기 L 그림)"""
    d = np.asarray(ImageChops.difference(bg, sc).filter(ImageFilter.GaussianBlur(1.5))).max(axis=2)
    m = Image.fromarray(((d > 24) * 255).astype(np.uint8)).crop(box)
    m = m.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))      # 잡티
    m = m.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9))      # 틈
    m = Image.fromarray((largest_blob(np.asarray(m) > 0) * 255).astype(np.uint8))
    pad = Image.new("L", (m.width + 2, m.height + 2), 0)                          # 구멍: 테두리에서 못 닿는 빈칸
    pad.paste(m, (1, 1))
    ImageDraw.floodfill(pad, (0, 0), 128)
    return Image.fromarray(np.where(np.asarray(pad)[1:-1, 1:-1] == 128, 0, 255).astype(np.uint8))


def do_scene(raw):
    with open(os.path.join(ROOT, "tools", "art_scenes.json"), encoding="utf-8") as f:
        spec = json.load(f)
    out = os.path.join(IMG, "scenes")
    os.makedirs(out, exist_ok=True)
    for loc, chars in spec.items():
        if loc.startswith("_"):
            continue
        bg = Image.open(os.path.join(raw, loc + ".png")).convert("RGB").crop((0, 80, 1536, 944)).resize(SCREEN, Image.LANCZOS)
        for who, s in chars.items():
            box = tuple(s["box"])
            scenes = {}
            union = None
            for st in SCENE_STATES:
                sc = Image.open(os.path.join(raw, "scene_%s_%s_%s.png" % (loc, who, st))).convert("RGB")
                scenes[st] = match_colors(sc.crop((0, 80, 1536, 944)).resize(SCREEN, Image.LANCZOS), bg, box)
                m = changed_mask(bg, scenes[st], box)
                union = m if union is None else ImageChops.lighter(union, m)
            alpha = Image.new("L", SCREEN, 0)
            alpha.paste(union.filter(ImageFilter.GaussianBlur(1.2)), box[:2])
            for st, sc in scenes.items():
                for tod, img in (("day", sc), ("night", night_filter(sc))):
                    piece = Image.new("RGBA", SCREEN, (0, 0, 0, 0))
                    piece.paste(img, (0, 0), alpha)
                    piece.putalpha(alpha)
                    piece.save(os.path.join(out, "scene_%s_%s_%s_%s.png" % (loc, who, st, tod)), optimize=True)
            ## 클릭·하이라이트 모양: 인물 윤곽 다각형 (화면 크기 1비트 PNG)
            shape = Image.new("P", SCREEN, 0)
            shape.putpalette([0, 0, 0, 255, 255, 255])
            ImageDraw.Draw(shape).polygon([tuple(p) for p in s["shape"]], fill=1)
            shape.save(os.path.join(out, "mask_scene_%s_%s.png" % (loc, who)), transparency=0, optimize=True)
            x0, y0, x1, y1 = box
            outside = np.asarray(ImageChops.difference(scenes["busy"], scenes["look"]).convert("L")).astype(np.float32)
            outside[y0:y1, x0:x1] = np.nan
            print("scene %-14s %-7s 인물 영역=%s  두 장면 상자 밖 차이=%.1f (작을수록 구도가 그대로)" % (
                loc, who, alpha.getbbox(), np.nanmean(outside)))


STEPS = {"bg": do_bg, "sprite": do_sprite, "face": do_face, "enemy": do_enemy,
         "icon": do_icon, "object": do_object, "scene": do_scene}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    raw = sys.argv[1]
    names = list(STEPS) if sys.argv[2] == "all" else sys.argv[2:]
    for n in names:
        STEPS[n](raw)
