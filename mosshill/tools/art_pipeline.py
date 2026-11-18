#!/usr/bin/env python3
"""AI 로 만든 원본 그림 → 게임 규격 그림 (game/images/...)

원본 폴더(RAW)에는 이미지 서버에서 받은 PNG 를 이름만 바꿔 넣어 둔다.
    배경    <장소>.png            1536x1024
    인물    <이름>.png            1024x1536 (몸, 기본 표정)
    표정    <이름>_<표정>.png     같은 그림에서 표정만 바꾼 것
    적      <종류>.png            투명 배경
    아이템  items.png             4x4 칸
    장소 인물 pose_<장소>_<인물>_<busy|look>.png  인물만 단독으로 크게 (하던 일 / 앞을 봄)

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
    "ruby":   {"faces": ["happy", "angry", "sad", "surprised", "blink", "talk"], "face_box": (260, 150, 740, 540)},
    "kai":    {"faces": ["happy", "surprised", "sad", "angry", "talk"], "face_box": (400, 140, 730, 480)},
    "martha": {"faces": ["happy", "angry", "surprised", "talk"],        "face_box": (230, 140, 590, 470)},
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


def _on_paper(im):
    bg = Image.new("RGBA", im.size, (235, 225, 210, 255))
    bg.alpha_composite(im)
    return bg.convert("RGB")


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
            p = PAD // k                    # 줄인 그림이 원본보다 작아도 비교 범위가 모자라지 않게 흰색으로 채운다
            full = np.full((max(a.shape[0], b.shape[0]) + 2 * p, max(a.shape[1], b.shape[1]) + 2 * p), 255, np.float32)
            full[p:p + b.shape[0], p:p + b.shape[1]] = b
            cache[(s, k)] = (a, full)
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
    review = []                                     # 사람이 눈으로 확인할 점검용 그림 (원본 폴더에 저장)
    for name, spec in CHARS.items():
        out = os.path.join(IMG, "characters", name)
        body = Image.open(os.path.join(raw, name + ".png")).convert("RGBA")
        x0, y0, x1, y1 = spec["face_box"]
        ## 맞춤 비교 구역: 얼굴 상자 둘레 (머리카락, 목, 어깨)
        ring = (x0 - 70, y0 - 60, x1 + 70, y1 + 90)
        area = Image.new("L", body.size, 0)
        ImageDraw.Draw(area).rectangle((x0, y0, x1, y1), fill=255)
        area = area.filter(ImageFilter.GaussianBlur(10))
        look = (x0 - 50, y0 - 30, x1 + 30, y1 + 10)
        row = [_on_paper(body).crop(look)]
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
            ## 조각이 조금이라도 적용되는 곳 전부 (상자 경계의 흐린 띠 포함 — 경계에 걸친 눈이 반투명하게 남는 문제)
            left = (np.asarray(left) > 0) & (np.asarray(area) > 0)
            row.append(_on_paper(comp).crop(look))
            framed(piece, spec, body).resize(SPRITE, Image.LANCZOS).save(
                os.path.join(out, "%s_face_%s.png" % (name, face)), optimize=True)
            print("face %-7s %-9s scale=%.2f shift=(%d,%d) ring_diff=%.1f leftover=%.2f%%%s" % (
                name, face, s, dx, dy, d, left.mean() * 100, "  <-- 확인 필요" if left.mean() > 0.003 else ""))
        review.append(row)
    ## 점검용 그림: 인물마다 한 줄 (기본 얼굴 + 표정들). 경계에 걸친 눈이 반투명하게 남는 등
    ## 수치로 못 잡는 문제를 눈으로 확인한다.
    h = 200
    rows = [[im.resize((round(im.width * h / im.height), h)) for im in r] for r in review]
    sheet = Image.new("RGB", (max(sum(im.width + 4 for im in r) for r in rows), (h + 4) * len(rows)), "white")
    for i, r in enumerate(rows):
        x = 0
        for im in r:
            sheet.paste(im, (x, i * (h + 4)))
            x += im.width + 4
    sheet.save(os.path.join(raw, "_review_faces.png"))
    print("점검용 그림:", os.path.join(raw, "_review_faces.png"))


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


## ---------------------------------------------------------------- 장소 안 인물 (두 방식을 합친 것)
## 1) AI 에게 배경에 인물을 함께 그리게 하면 크기·비율·자세·조명이 자연스럽지만, 인물이 몇십 px 로 작게 그려져
##    얼굴·인상이 뭉개진다.
## 2) 원작(SS)처럼 인물만 단독으로 크게 그려 얹으면 얼굴은 또렷하지만, 크기·자세를 따로 정하면 어색하다.
## → 먼저 1) 로 장면을 그리고, 그 장면을 견본으로 '같은 자세·비율의 인물만' 크게 다시 그린다(2).
##   그 큰 그림을 1) 의 인물 실루엣에 자동으로 겹쳐 맞추고(배율·위치), 1) 의 인물 색감을 옮겨 얹는다.
##   외곽선은 두르지 않는다 (원작처럼 굵게 두르면 튀었다).
##
## RAW/<장소>.png                    배경 원본 (인물 없음)
## RAW/scene_<장소>_<인물>_busy.png  1) 배경에 인물을 함께 그린 그림 — 크기·위치·색감의 기준
## RAW/pose_<장소>_<인물>_busy.png   2) 1) 을 견본으로 인물만 크게 (1024x1536 투명) — 하던 일을 보는 모습
## RAW/pose_<장소>_<인물>_look.png   2) 에서 눈·입만 바꿔 앞(카메라)을 보는 모습 (look_from 이 "profile" 이면 안 씀)
## 얼굴이 대화 그림과 달라지지 않게 (look_from: "profile"):
##   2) 는 '대화 그림'을 고칠 대상(1번)으로 넣고 팔·손·소품만 바꾼다 (1) 장면은 자세 견본으로만) → 머리 위치·크기가 그대로.
##   앞을 보는 얼굴은 AI 로 그리지 않고 대화 그림(RAW/<인물>.png)의 얼굴 영역(CHARS face_box)을 맞춰 옮겨 붙인다
##   (얼굴 모양 타원, 턱선까지. 머리 크기가 대화 그림과 달라도 locate 가 넓게 찾아 맞춘다).
##   대화 그림과 구도가 다른 자세(앉은 전신)는 비율이 맞는 그림을 고칠 대상으로 하고 얼굴·머리카락만 대화 그림을 따르게 한다.
##   2) 의 투명 배경에 안개가 남으면 tools/cutout.py 로 먼저 정리한다.
## tools/art_scenes.json 의 place:
##   ref       1) 에서 인물이 있는 곳 다각형 (화면 1280x720 좌표) — 이 안에서 배경과 다른 곳 = 인물 실루엣
##   cut       이 y 아래는 가구(바·식탁·계산대) 뒤라 안 보임 (없으면 null) — 가구 윗면의 '뒤쪽' 끝.
##             앞쪽 모서리에서 자르면 몸이 가구 윗면을 덮어 '가구 위에 올려 놓은' 것처럼 보인다
##   show      cut 아래라도 보이는 곳 다각형 목록 (가구 위에 올린 손·도구) (선택)
##   show_from_scene  true 면 show 안(cut 아래)은 단독 그림 대신 1) 장면의 픽셀을 쓴다.
##             가구 위에 놓인 도구(도마 등)는 단독 그림에서 옆모습으로 그려져 원근이 안 맞기 때문 — 1) 은 배경과 같은 원근
##   hide      앞의 물건에 가려지는 곳 다각형 목록 (선택)
##   shadow    true 면 발밑 그림자 (바닥에 놓인 전신)
##   fit_cut   맞출 때 비교를 멈출 y (1) 그림에서 가구에 가려진 선이 cut 과 다를 때, 기본은 cut)
##   fit_upper 실루엣 위쪽 몇 %로 맞출지 (기본 0.6). 단독 그림의 머리 비율이 1) 과 다르면 줄여서 머리 위주로 맞춘다
##   scale     맞춘 뒤 크기 보정 (AI 는 1) 에서 인물을 실제보다 크게 그리는 버릇이 있다).
##             cut(가구 윗면) 높이와 실루엣 가운데를 기준으로 줄여서, 가구가 몸의 같은 곳(허리 등)을 가리게 한다
##   check     비율 검사 {"floor": 가구 뒤 바닥 y, "furniture_cm": 가구 높이, "height_cm": 인물 키, "hair_cm": 위로 솟은 머리(선택)}
##             → 가구 높이로 1cm 가 몇 px 인지 재서, 가구 위로 보이는 몸 길이가 실제(키 - 가구 높이)의 몇 배인지 출력.
##             1.25배를 넘거나 0.8배 아래면 '확인 필요' 와 맞는 scale 값을 알려 준다
## 결과: scene_<장소>_<인물>_<busy|look>_<day|night>.png (화면 크기, 인물만 불투명)
##       mask_scene_<장소>_<인물>.png (클릭 모양 = 인물 실루엣)
SCENE_STATES = ("busy", "look")
COLOR_AMOUNT = 0.6


def screen_of(path):
    """AI 원본(1536x1024) → 화면(1280x720), 배경과 같은 자르기"""
    return Image.open(path).convert("RGB").crop((0, 80, 1536, 944)).resize(SCREEN, Image.LANCZOS)


def ref_silhouette(bg, sc, poly):
    """1) 그림에서 인물 실루엣: 다각형(조금 넓힘) 안에서 배경과 확실히 다른 곳"""
    area = Image.new("L", SCREEN, 0)
    ImageDraw.Draw(area).polygon([tuple(p) for p in poly], fill=255)
    area = np.asarray(area.filter(ImageFilter.MaxFilter(9))) > 0
    d = np.asarray(ImageChops.difference(bg, sc).filter(ImageFilter.GaussianBlur(1.5))).max(axis=2) > 30
    m = Image.fromarray(((d & area) * 255).astype(np.uint8))
    m = m.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))     # 잡티
    m = m.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(7))     # 틈
    return np.asarray(m) > 0


def fit_to(sil, char, cut, upper=0.6):
    """큰 인물 그림을 실루엣 sil 에 겹쳐 맞추는 배율 k, 위치 (ox, oy) — 겹치는 비율(IoU)이 가장 큰 값.
    크기 느낌은 머리·상체가 정하므로 실루엣 위쪽 upper 비율만 비교한다 (팔·소품은 그림마다 조금씩 다르다).
    cut 아래는 1) 에서 가구에 가려졌으므로 비교하지 않는다."""
    A = char.getchannel("A")
    x0, y0, x1, y1 = A.point(lambda v: 255 if v > 16 else 0).getbbox()
    ys, xs = np.nonzero(sil)
    sy0, sy1, sx0, sx1 = ys.min(), ys.max(), xs.min(), xs.max()
    limit = min(cut if cut is not None else SCREEN[1], int(sy0 + (sy1 - sy0) * upper))
    k0 = (sy1 - sy0) / (y1 - y0) if cut is None else (sx1 - sx0) / (x1 - x0)
    pad = 120
    wx0, wy0 = max(0, sx0 - pad), max(0, sy0 - pad)                 # 비교는 실루엣 주변 창 안에서만
    wx1, wy1 = min(SCREEN[0], sx1 + pad), limit
    ref_full = sil[wy0:wy1, wx0:wx1]
    cache = {}

    def iou(k, ox, oy, step):
        key = (round(k, 5), step)
        if key not in cache:
            cache[key] = np.asarray(A.resize((max(1, round(A.width * k / step)), max(1, round(A.height * k / step))))) > 128
        small = cache[key]
        ref = ref_full[::step, ::step]
        canvas = np.zeros(ref.shape, bool)
        px, py = round((ox - wx0) / step), round((oy - wy0) / step)
        h, w = small.shape
        cx0, cy0, cx1, cy1 = max(0, px), max(0, py), min(canvas.shape[1], px + w), min(canvas.shape[0], py + h)
        if cx1 <= cx0 or cy1 <= cy0:
            return 0
        canvas[cy0:cy1, cx0:cx1] = small[cy0 - py:cy1 - py, cx0 - px:cx1 - px]
        return (canvas & ref).sum() / max(1, (canvas | ref).sum())

    best = (0, k0, 0, 0)
    for k in np.arange(0.7, 1.31, 0.02) * k0:
        ox0 = (sx0 + sx1) / 2 - (x0 + x1) / 2 * k
        oy0 = sy0 - y0 * k
        for dy in range(-40, 41, 4):
            for dx in range(-60, 61, 4):
                v = iou(k, ox0 + dx, oy0 + dy, 2)
                if v > best[0]:
                    best = (v, k, ox0 + dx, oy0 + dy)
    _, kb, oxb, oyb = best
    for k in (kb * 0.99, kb, kb * 1.01):
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                v = iou(k, oxb + dx, oyb + dy, 1)
                if v > best[0]:
                    best = (v, k, oxb + dx, oyb + dy)
    return best


def locate(body, ex, box, scales=np.arange(0.40, 1.16, 0.025), k=4):
    """ex 의 box 영역(얼굴)이 body 의 어디에 몇 배 크기로 있는지 넓은 범위에서 찾는다 (1/k 크기, FFT 상관).
    앉은 전신처럼 머리가 대화 그림보다 작게 그려진 그림에 대화 그림 얼굴을 옮길 때 쓴다.
    반환: (배율 s, 이동 dx, dy — place(ex, s, dx, dy) 로 맞춤, body 안의 얼굴 상자)"""
    a = np.asarray(gray_on_white(body).resize((body.width // k, body.height // k)), np.float64)
    patch = gray_on_white(ex).crop(box)
    H, W = a.shape
    ii = np.pad((a * a).cumsum(0).cumsum(1), ((1, 0), (1, 0)))      # 창 안 제곱합 (적분 영상)
    best = None
    for sc in scales:
        tw, th = max(4, round(patch.width * sc / k)), max(4, round(patch.height * sc / k))
        if tw >= W or th >= H:
            continue
        t = np.asarray(patch.resize((tw, th), Image.LANCZOS), np.float64)
        shape = (H + th - 1, W + tw - 1)
        full = np.fft.irfft2(np.fft.rfft2(a, shape) * np.fft.rfft2(t[::-1, ::-1], shape), shape)
        corr = full[th - 1:H, tw - 1:W]
        win = ii[th:, tw:] - ii[:-th, tw:] - ii[th:, :-tw] + ii[:-th, :-tw]
        ssd = (win - 2 * corr + (t * t).sum()) / t.size
        y, x = np.unravel_index(np.argmin(ssd), ssd.shape)
        if best is None or ssd[y, x] < best[0]:
            best = (ssd[y, x], sc, x * k, y * k, tw * k, th * k)
    _, sc, x, y, w, h = best
    return sc, round(x - box[0] * sc), round(y - box[1] * sc), (x, y, x + w, y + h)


def look_from_busy(busy, look, box=None, oval=False):
    """look 그림에서 머리 쪽의 달라진 곳만 busy 에 합친다 → 바뀔 때 몸이 흔들리지 않는다.
    box 가 없으면 테두리 상자 위 45%, 있으면 그 상자(얼굴 영역) 안만."""
    x0, y0, x1, y1 = busy.getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox()
    head = box or (x0, y0, x1, y0 + int((y1 - y0) * 0.45))
    d, s, dx, dy = register(busy, look, (head[0], head[1], head[2], head[3] + (0 if box else 60)))
    look = place(look, s, dx, dy)
    area = Image.new("L", busy.size, 0)
    if oval:        # 얼굴 모양 타원 — 상자 모서리(목·옷깃·어깨)는 옮기지 않는다 (자세가 달라 얼룩이 됨)
        ImageDraw.Draw(area).ellipse(head, fill=255)
    else:
        ImageDraw.Draw(area).rectangle(head, fill=255)
    area = area.filter(ImageFilter.GaussianBlur(10))
    diff = ImageChops.difference(gray_on_white(busy), gray_on_white(look)).filter(ImageFilter.GaussianBlur(2))
    mask = ImageChops.multiply(diff.point(lambda v: 255 if v > 14 else 0).filter(ImageFilter.MaxFilter(15)), area)
    ## busy 가 불투명한 곳(얼굴·머리) 안에서만 — look 그림의 투명 배경에 남은 옅은 얼룩이 끼어들지 않게
    mask = ImageChops.multiply(mask, busy.getchannel("A").point(lambda v: 255 if v > 128 else 0).filter(ImageFilter.MinFilter(3)))
    piece = look.copy()
    piece.putalpha(ImageChops.multiply(mask.filter(ImageFilter.GaussianBlur(5)), look.getchannel("A")))
    out = busy.copy()
    out.alpha_composite(piece)
    return out


def place_char(char, k, ox, oy, pl, color, scene=None, sil=None):
    """큰 인물 그림 → 화면 크기 레이어 (줄이기, 방 색감, 발밑 그림자, 가려지는 곳 잘라내기)"""
    from_scene = pl.get("show_from_scene") and scene is not None
    x0, y0, x1, y1 = char.getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox()
    small = char.resize((round(char.width * k), round(char.height * k)), Image.LANCZOS)
    layer = Image.new("RGBA", SCREEN, (0, 0, 0, 0))
    layer.alpha_composite(small, (round(ox), round(oy)))
    ## 방 색감: 인물 색 분포(평균·표준편차)를 1) 의 인물 색 분포 쪽으로 COLOR_AMOUNT 만큼 옮긴다
    arr = np.asarray(layer).astype(np.float32)
    solid = arr[..., 3] > 128
    for c in range(3):
        src = arr[..., c][solid]
        moved = (arr[..., c] - src.mean()) * (color[1][c] / (src.std() + 1e-6)) + color[0][c]
        arr[..., c] = np.clip(arr[..., c] * (1 - COLOR_AMOUNT) + moved * COLOR_AMOUNT, 0, 255)
    layer = Image.fromarray(arr.astype(np.uint8), "RGBA")
    layer.putalpha(layer.getchannel("A").filter(ImageFilter.GaussianBlur(0.6)))   # 경계만 살짝 부드럽게
    ## 가구 뒤: cut 아래와 hide 다각형 안은 투명
    keep = Image.new("L", SCREEN, 255)
    dr = ImageDraw.Draw(keep)
    if pl.get("cut") is not None:
        dr.rectangle((0, pl["cut"], SCREEN[0], SCREEN[1]), fill=0)
    for poly in ([] if from_scene else pl.get("show", [])):     # cut 아래라도 보이는 곳 (식탁 위에 올린 손 등)
        dr.polygon([tuple(p) for p in poly], fill=255)
    for poly in pl.get("hide", []):
        dr.polygon([tuple(p) for p in poly], fill=0)
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), keep))
    if from_scene:                                  # cut 아래 show 안은 1) 장면의 인물·도구 픽셀 (배경과 같은 원근)
        area = Image.new("L", SCREEN, 0)
        da = ImageDraw.Draw(area)
        for poly in pl.get("show", []):
            da.polygon([tuple(p) for p in poly], fill=255)
        da.rectangle((0, 0, SCREEN[0], pl["cut"] - 1), fill=0)
        m = ImageChops.multiply(area, Image.fromarray((sil * 255).astype(np.uint8)))
        piece = scene.convert("RGBA")
        piece.putalpha(m.filter(ImageFilter.GaussianBlur(0.6)))
        layer.alpha_composite(piece)
    full = Image.new("RGBA", SCREEN, (0, 0, 0, 0))
    if pl.get("shadow"):
        fx, fy, w = ox + (x0 + x1) / 2 * k, oy + y1 * k, (x1 - x0) * k * 0.75
        sh = Image.new("L", SCREEN, 0)
        ImageDraw.Draw(sh).ellipse((fx - w / 2, fy - 9, fx + w / 2, fy + 7), fill=110)
        shadow = Image.new("RGBA", SCREEN, (20, 12, 6, 0))
        shadow.putalpha(sh.filter(ImageFilter.GaussianBlur(6)))
        full.alpha_composite(shadow)
    full.alpha_composite(layer)
    return full


def do_scene(raw):
    with open(os.path.join(ROOT, "tools", "art_scenes.json"), encoding="utf-8") as f:
        spec = json.load(f)
    out = os.path.join(IMG, "scenes")
    os.makedirs(out, exist_ok=True)
    for loc, chars in spec.items():
        if loc.startswith("_"):
            continue
        for who, s in chars.items():
            pose = {"busy": Image.open(os.path.join(raw, "pose_%s_%s_busy.png" % (loc, who))).convert("RGBA")}
            if s.get("look_from") == "profile":
                ## 대화 그림(원본 몸)의 얼굴을 그대로 옮긴다 → 장소 안에서 마주 보는 얼굴이 대화 그림과 똑같다.
                ## busy 는 대화 그림을 고쳐 팔·소품만 바꾼 그림이라 머리 위치·크기가 같다
                ## 머리 크기·위치가 대화 그림과 다르면(앉은 전신 등) 먼저 얼굴을 넓게 찾아 대략 맞춘 뒤 다듬는다
                fb = CHARS[who]["face_box"]
                prof = Image.open(os.path.join(raw, who + ".png")).convert("RGBA")
                sc, dx, dy, (fx0, fy0, fx1, fy1) = locate(pose["busy"], prof, fb)
                prof = place(prof, sc, dx, dy)
                m = round(30 * sc)
                ## 아래쪽은 턱선까지만 (목은 자세마다 각도가 달라 옮기면 옷 위에 살색 얼룩이 생긴다)
                pose["look"] = look_from_busy(pose["busy"], prof, (fx0 - m, fy0 - m, fx1 + m, fy1 - 2 * m), oval=True)
                print("      대화 그림 얼굴: 배율 %.2f, 위치 %s" % (sc, (fx0, fy0, fx1, fy1)))
            else:
                look = Image.open(os.path.join(raw, "pose_%s_%s_look.png" % (loc, who))).convert("RGBA")
                pose["look"] = look_from_busy(pose["busy"], look)
            pl = s["place"]
            bg = screen_of(os.path.join(raw, loc + ".png"))
            ref = screen_of(os.path.join(raw, "scene_%s_%s_busy.png" % (loc, who)))
            sil = ref_silhouette(bg, ref, pl["ref"])
            fit, k, ox, oy = fit_to(sil, pose["busy"], pl.get("fit_cut", pl.get("cut")), pl.get("fit_upper", 0.6))
            if pl.get("scale", 1.0) != 1.0:
                sc, (sy, sx) = pl["scale"], np.nonzero(sil)
                ax = (sx.min() + sx.max()) / 2
                ay = pl["cut"] if pl.get("cut") is not None else sy.max()
                k, ox, oy = k * sc, ax - (ax - ox) * sc, ay - (ay - oy) * sc
            px = np.asarray(ref).astype(np.float32)[sil]
            color = (px.mean(axis=0), px.std(axis=0))
            layers = {st: place_char(pose[st], k, ox, oy, pl, color, ref, sil) for st in SCENE_STATES}
            for st, layer in layers.items():
                rgb = layer.convert("RGB")
                for tod, img in (("day", rgb), ("night", night_filter(rgb))):
                    piece = img.convert("RGBA")
                    piece.putalpha(layer.getchannel("A"))
                    piece.save(os.path.join(out, "scene_%s_%s_%s_%s.png" % (loc, who, st, tod)), optimize=True)
            ## 클릭 모양 = 두 자세 실루엣을 합친 것 (1비트)
            sil = ImageChops.lighter(layers["busy"].getchannel("A"), layers["look"].getchannel("A"))
            shape = sil.point(lambda v: 1 if v > 150 else 0).convert("P")      # 그림자(옅음)는 빼고 인물만
            shape.putpalette([0, 0, 0, 255, 255, 255])
            shape.save(os.path.join(out, "mask_scene_%s_%s.png" % (loc, who)), transparency=0, optimize=True)
            box = ImageChops.lighter(layers["busy"].getchannel("A"), layers["look"].getchannel("A")).getbbox()
            print("scene %-14s %-7s 겹침(IoU)=%.2f 배율=%.3f 화면 위치=%s" % (loc, who, fit, k, box))
            ck = pl.get("check")
            if ck and pl.get("cut") is not None:
                px_cm = (ck["floor"] - pl["cut"]) / ck["furniture_cm"]
                seen = (pl["cut"] - box[1]) / px_cm
                want = ck["height_cm"] - ck["furniture_cm"] + ck.get("hair_cm", 0)      # hair_cm: 머리 위로 솟은 머리카락
                ratio = seen / want
                warn = "" if 0.8 <= ratio <= 1.25 else "  ← 확인 필요: scale 을 %.2f 로" % (pl.get("scale", 1.0) / ratio)
                print("      비율: 가구 위로 보이는 몸 %.0fcm (실제라면 %.0fcm) = %.2f배%s" % (seen, want, ratio, warn))


STEPS = {"bg": do_bg, "sprite": do_sprite, "face": do_face, "enemy": do_enemy,
         "icon": do_icon, "object": do_object, "scene": do_scene}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    raw = sys.argv[1]
    names = list(STEPS) if sys.argv[2] == "all" else sys.argv[2:]
    for n in names:
        STEPS[n](raw)
