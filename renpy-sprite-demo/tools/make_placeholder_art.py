"""임시(플레이스홀더) 캐릭터 레이어를 그리는 스크립트.

모든 레이어는 같은 크기(600x720)의 투명 캔버스에 그린다.
→ Ren'Py에서 겹치기만 하면 위치가 정확히 맞는다 (좌표 맞출 필요 없음).
실제 그림이 생기면 같은 파일 이름으로 덮어쓰기만 하면 된다.

실행: python3 tools/make_placeholder_art.py   (renpy-sprite-demo 폴더에서)
"""
import os
from PIL import Image, ImageDraw

W, H = 600, 720
OUT = os.path.join(os.path.dirname(__file__), "..", "game", "images", "hero")
OUT_ENEMY = os.path.join(os.path.dirname(__file__), "..", "game", "images", "enemy")
LINE = (40, 30, 45, 255)
SKIN = (255, 222, 196, 255)
HAIR = (120, 72, 40, 255)
LW = 5
HX, HY, HR = 300, 200, 100          # 머리 중심/반지름 (얼굴 레이어들이 이 좌표를 공유)


def canvas():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def save(img, name, folder=OUT):
    os.makedirs(folder, exist_ok=True)
    img.save(os.path.join(folder, name + ".png"))


# ---------------------------------------------------------------- body (몸 + 머리 + 머리카락)
def body(tunic, trim, armor=False):
    im = canvas(); d = ImageDraw.Draw(im)
    # 다리
    d.rounded_rectangle((235, 520, 290, 715), 18, fill=(70, 60, 80, 255), outline=LINE, width=LW)
    d.rounded_rectangle((310, 520, 365, 715), 18, fill=(70, 60, 80, 255), outline=LINE, width=LW)
    # 몸통
    d.rounded_rectangle((200, 300, 400, 560), 50, fill=tunic, outline=LINE, width=LW)
    if armor:
        d.rounded_rectangle((225, 320, 375, 450), 30, fill=(200, 205, 215, 255), outline=LINE, width=LW)
        d.line((300, 325, 300, 445), fill=LINE, width=3)
    d.rectangle((205, 470, 395, 495), fill=trim, outline=LINE, width=4)       # 허리띠
    # 목
    d.rectangle((275, 280, 325, 315), fill=SKIN, outline=LINE, width=LW)
    # 머리
    d.ellipse((HX - HR, HY - HR, HX + HR, HY + HR), fill=SKIN, outline=LINE, width=LW)
    # 머리카락 (위쪽 반원 + 앞머리)
    d.chord((HX - HR - 8, HY - HR - 12, HX + HR + 8, HY + HR - 70), 180, 360, fill=HAIR, outline=LINE, width=LW)
    d.polygon([(212, 150), (250, 115), (268, 158), (300, 112), (332, 156), (352, 115), (388, 150), (392, 125), (208, 125)], fill=HAIR)
    return im


save(body((70, 110, 190, 255), (150, 100, 50, 255)), "hero_body_tunic")
save(body((90, 90, 110, 255), (180, 150, 60, 255), armor=True), "hero_body_armor")


# ---------------------------------------------------------------- arms (팔)
def arm(d, pts, sleeve):
    d.line(pts, fill=LINE, width=46, joint="curve")
    d.line(pts, fill=sleeve, width=36, joint="curve")
    x, y = pts[-1]
    d.ellipse((x - 22, y - 22, x + 22, y + 22), fill=SKIN, outline=LINE, width=LW)


SLEEVE = (60, 95, 170, 255)

im = canvas(); d = ImageDraw.Draw(im)
arm(d, [(215, 330), (185, 420), (180, 500)], SLEEVE)
arm(d, [(385, 330), (415, 420), (420, 500)], SLEEVE)
save(im, "hero_arms_down")

im = canvas(); d = ImageDraw.Draw(im)
arm(d, [(215, 330), (185, 420), (180, 500)], SLEEVE)
# 칼 (오른손 위로)
d.polygon([(468, 60), (488, 60), (486, 330), (470, 330)], fill=(220, 225, 235, 255), outline=LINE)
d.rectangle((445, 330, 512, 345), fill=(160, 120, 40, 255), outline=LINE, width=4)
d.rectangle((470, 345, 486, 395), fill=(110, 70, 40, 255), outline=LINE, width=4)
arm(d, [(385, 330), (440, 380), (478, 370)], SLEEVE)
save(im, "hero_arms_sword")

im = canvas(); d = ImageDraw.Draw(im)
arm(d, [(215, 330), (225, 420), (360, 415)], SLEEVE)
arm(d, [(385, 330), (375, 435), (240, 440)], SLEEVE)
save(im, "hero_arms_crossed")


# ---------------------------------------------------------------- brows (눈썹)
def brows(name, l, r):
    im = canvas(); d = ImageDraw.Draw(im)
    d.line(l, fill=LINE, width=9); d.line(r, fill=LINE, width=9)
    save(im, "hero_brows_" + name)


brows("normal", (240, 175, 280, 172), (320, 172, 360, 175))
brows("angry", (240, 166, 282, 182), (318, 182, 360, 166))
brows("sad", (240, 182, 282, 166), (318, 166, 360, 182))
brows("up", (238, 170, 280, 165), (320, 165, 362, 170))


# ---------------------------------------------------------------- eyes (눈)
def eyes(name, kind):
    im = canvas(); d = ImageDraw.Draw(im)
    for cx in (260, 340):
        if kind == "open":
            d.ellipse((cx - 14, 185, cx + 14, 222), fill=(40, 30, 45, 255))
            d.ellipse((cx - 6, 191, cx + 2, 200), fill=(255, 255, 255, 255))
        elif kind == "closed":
            d.line((cx - 16, 205, cx + 16, 205), fill=LINE, width=6)
        elif kind == "happy":
            d.arc((cx - 16, 192, cx + 16, 222), 200, 340, fill=LINE, width=6)
        elif kind == "wide":
            d.ellipse((cx - 17, 180, cx + 17, 226), fill=(255, 255, 255, 255), outline=LINE, width=4)
            d.ellipse((cx - 8, 195, cx + 8, 212), fill=(40, 30, 45, 255))
    save(im, "hero_eyes_" + name)


for k in ("open", "closed", "happy", "wide"):
    eyes(k, k)


# ---------------------------------------------------------------- mouth (입)
def mouth(name, fn):
    im = canvas(); d = ImageDraw.Draw(im); fn(d); save(im, "hero_mouth_" + name)


mouth("neutral", lambda d: d.line((285, 255, 315, 255), fill=LINE, width=5))
mouth("smile", lambda d: d.arc((275, 230, 325, 268), 20, 160, fill=LINE, width=5))
mouth("frown", lambda d: d.arc((280, 250, 320, 278), 200, 340, fill=LINE, width=5))
mouth("open", lambda d: d.ellipse((287, 245, 313, 275), fill=(150, 50, 60, 255), outline=LINE, width=4))
mouth("talk_a", lambda d: d.ellipse((288, 248, 312, 266), fill=(150, 50, 60, 255), outline=LINE, width=4))


# ---------------------------------------------------------------- 볼 터치 (overlay)
im = canvas(); d = ImageDraw.Draw(im)
d.ellipse((225, 228, 255, 245), fill=(255, 140, 150, 140)); d.ellipse((345, 228, 375, 245), fill=(255, 140, 150, 140))
save(im, "hero_overlay_blush")
im = canvas(); d = ImageDraw.Draw(im)
d.polygon([(395, 185), (387, 210), (403, 210)], fill=(120, 190, 255, 255), outline=LINE)
d.ellipse((385, 203, 405, 223), fill=(120, 190, 255, 255), outline=LINE, width=3)
save(im, "hero_overlay_sweat")


# ---------------------------------------------------------------- 적 (슬라임) - 단일 이미지 + 피격 이미지
def slime(name, hurt=False):
    im = Image.new("RGBA", (360, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    body_col = (110, 200, 120, 255) if not hurt else (240, 120, 120, 255)
    d.pieslice((20, 40, 340, 420), 180, 360, fill=body_col, outline=LINE, width=LW)
    d.line((20, 230, 340, 230), fill=LINE, width=LW)
    if hurt:
        for cx in (130, 230):
            d.line((cx - 15, 135, cx + 15, 165), fill=LINE, width=7); d.line((cx - 15, 165, cx + 15, 135), fill=LINE, width=7)
    else:
        for cx in (130, 230):
            d.ellipse((cx - 14, 130, cx + 14, 168), fill=(40, 30, 45, 255))
    d.arc((150, 160, 210, 200), 20, 160, fill=LINE, width=5)
    save(im, name, OUT_ENEMY)


slime("slime"); slime("slime_hurt", hurt=True)
# ---------------------------------------------------------------- 배경 (1280x720)
OUT_BG = os.path.join(os.path.dirname(__file__), "..", "game", "images", "bg")


def sky(d, top, bottom, h):
    for y in range(h):
        k = y / h
        d.line((0, y, 1280, y), fill=tuple(int(top[i] + (bottom[i] - top[i]) * k) for i in range(3)))


def town(name, night=False):
    im = Image.new("RGB", (1280, 720)); d = ImageDraw.Draw(im)
    sky(d, (25, 30, 70) if night else (120, 180, 240), (70, 60, 110) if night else (200, 230, 250), 480)
    d.rectangle((0, 480, 1280, 720), fill=(70, 80, 70) if night else (150, 170, 120))
    d.polygon([(0, 720), (520, 480), (760, 480), (1280, 720)], fill=(120, 110, 100) if night else (205, 190, 160))
    for x, w, h, c in [(40, 220, 230, (190, 120, 90)), (300, 180, 180, (120, 150, 190)), (860, 200, 210, (200, 170, 100)), (1090, 170, 250, (150, 110, 140))]:
        c = tuple(int(v * (0.45 if night else 1)) for v in c)
        d.rectangle((x, 480 - h, x + w, 480), fill=c, outline=LINE, width=4)
        d.polygon([(x - 15, 480 - h), (x + w // 2, 480 - h - 70), (x + w + 15, 480 - h)], fill=(110, 50, 50) if not night else (60, 30, 30), outline=LINE)
        d.rectangle((x + w // 2 - 22, 420, x + w // 2 + 22, 480), fill=(90, 60, 40), outline=LINE, width=3)
        win = (255, 220, 120) if night else (210, 235, 255)
        d.rectangle((x + 20, 480 - h + 30, x + 60, 480 - h + 70), fill=win, outline=LINE, width=3)
        d.rectangle((x + w - 60, 480 - h + 30, x + w - 20, 480 - h + 70), fill=win, outline=LINE, width=3)
    if night:
        d.ellipse((1100, 50, 1170, 120), fill=(250, 245, 210))
    os.makedirs(OUT_BG, exist_ok=True); im.save(os.path.join(OUT_BG, name + ".jpg"), quality=90)


def field():
    im = Image.new("RGB", (1280, 720)); d = ImageDraw.Draw(im)
    sky(d, (150, 200, 245), (230, 240, 220), 420)
    d.polygon([(0, 420), (250, 300), (520, 420)], fill=(110, 150, 120)); d.polygon([(380, 420), (760, 260), (1100, 420)], fill=(95, 135, 110))
    d.rectangle((0, 420, 1280, 720), fill=(120, 175, 95))
    for i in range(0, 1280, 160):
        d.ellipse((i + 20, 600, i + 140, 640), fill=(100, 155, 80))
    os.makedirs(OUT_BG, exist_ok=True); im.save(os.path.join(OUT_BG, "bg_field.jpg"), quality=90)


town("bg_town_day"); town("bg_town_night", night=True); field()
print("done")
