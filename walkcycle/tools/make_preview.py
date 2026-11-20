#!/usr/bin/env python3
"""
미리보기 파일을 만든다: 4배 확대 시트, 걷기 GIF, 원본 리그와의 비교 이미지.

  python3 make_preview.py <assets_dir> [rig_frames.js 가 뽑은 원본 리그 프레임 폴더]
"""
import sys, os
import numpy as np
from PIL import Image

d = sys.argv[1]
rig = sys.argv[2] if len(sys.argv) > 2 else None
Z = 4
BG = (16, 21, 60)
STRIDE = 93.3333          # 한 주기 동안 나아가는 거리(px) — 원본 리그 값
FRAME_MS = 132            # 1000 / (8장 x 초당 0.95주기)

sheet = Image.open(os.path.join(d, 'sheet_walk8_idle1_128.png')).convert('RGBA')
sheet.resize((sheet.width * Z, sheet.height * Z), Image.NEAREST).save(os.path.join(d, 'sheet_walk8_idle1_128@4x.png'), optimize=True)
frames = [sheet.crop((i * 128, 0, i * 128 + 128, 128)) for i in range(9)]

# 걷기 GIF: 바닥 눈금이 걸음 속도에 맞춰 흘러가므로 발이 미끄러지는지 눈으로 확인할 수 있다
gif = []
for i in range(8):
    im = Image.new('RGBA', (128, 136), BG + (255,))
    px = im.load()
    off = i * STRIDE / 8
    for x in range(128):
        px[x, 121] = (42, 51, 130, 255)
        wx = x + off
        if int(wx // (STRIDE / 4)) != int((wx - 1) // (STRIDE / 4)):
            for y in range(122, 128):
                px[x, y] = (80, 104, 224, 255)
    im.alpha_composite(frames[i], (0, 0))
    gif.append(im.convert('RGB').resize((128 * Z, 136 * Z), Image.NEAREST))
gif[0].save(os.path.join(d, 'walk_preview.gif'), save_all=True, append_images=gif[1:], duration=FRAME_MS, loop=0, optimize=False)

# 투명 배경 GIF (제자리 걷기)
tg = []
for i in range(8):
    f = frames[i].resize((128 * Z, 128 * Z), Image.NEAREST)
    p = f.convert('RGB').convert('P', palette=Image.Palette.ADAPTIVE, colors=255)
    mask = f.split()[3].point(lambda a: 255 if a < 128 else 0)
    p.paste(255, mask)
    tg.append(p)
tg[0].save(os.path.join(d, 'walk_inplace_transparent.gif'), save_all=True, append_images=tg[1:], duration=FRAME_MS, loop=0, transparency=255, disposal=2)

# 원본 리그와 비교: 위 = 원본, 아래 = 새 스프라이트
if rig:
    cw = 96
    cmp_ = Image.new('RGBA', (cw * 8, 128 * 2 + 4), BG + (255,))
    for i in range(8):
        raw = np.frombuffer(open(os.path.join(rig, f'walk{i}.rgba'), 'rb').read(), dtype=np.uint8).reshape(128, 128, 4)
        r = Image.fromarray(raw, 'RGBA').crop((16, 0, 112, 128))
        cmp_.alpha_composite(r, (i * cw, 0))
        cmp_.alpha_composite(frames[i].crop((16, 0, 112, 128)), (i * cw, 132))
    cmp_.convert('RGB').resize((cmp_.width * 2, cmp_.height * 2), Image.NEAREST).save(os.path.join(d, 'compare_before_after.png'), optimize=True)
print('ok')
