#!/usr/bin/env python3
"""
이미지 생성 모델에 "편집 대상"으로 넣을 포즈 가이드 시트(1536x1024, 4x2 격자)를 만든다.

  # 1) 원본 리그의 걷기 8프레임 → 걷기 가이드
  python3 make_pose_guide.py walk <rig_dir> <out.png>
  # 2) 완성된 걷기 프레임 4장(윗줄) + 원본 리그의 정지 포즈 4장(아랫줄) → 정지 포즈 가이드
  python3 make_pose_guide.py idle <rig_dir> <walk_sheet_ai.png> <out.png>

<rig_dir> 에는 rig_frames.js 가 뽑은 walk0.rgba..walk7.rgba, idle.rgba (128x128 RGBA) 가 있어야 한다.
한 칸은 리그 셀의 x 16..112 구간(96x128)을 4배 한 384x512 이다.
"""
import sys
import numpy as np
from PIL import Image

BG = (16, 21, 60, 255)
SC = 4


def rig_frame(rig_dir, name):
    a = np.frombuffer(open(f'{rig_dir}/{name}.rgba', 'rb').read(), dtype=np.uint8).reshape(128, 128, 4)
    return Image.fromarray(a, 'RGBA').crop((16, 0, 112, 128)).resize((96 * SC, 128 * SC), Image.NEAREST)


def walk(rig_dir, out):
    sheet = Image.new('RGBA', (96 * SC * 4, 128 * SC * 2), BG)
    for i in range(8):
        sheet.alpha_composite(rig_frame(rig_dir, f'walk{i}'), ((i % 4) * 96 * SC, (i // 4) * 128 * SC))
    sheet.convert('RGB').save(out, optimize=True)


def idle(rig_dir, walk_sheet, out):
    done = Image.open(walk_sheet).convert('RGBA')
    sheet = Image.new('RGBA', (96 * SC * 4, 128 * SC * 2), BG)
    cw, ch = 96 * SC, 128 * SC
    for k, i in enumerate((2, 3, 6, 7)):  # 서 있는 자세에 가까운 통과·상승 프레임
        cell = done.crop(((i % 4) * cw, (i // 4) * ch, (i % 4) * cw + cw, (i // 4) * ch + ch))
        cell.putalpha(cell.split()[3].point(lambda x: 255 if x > 127 else 0))
        sheet.alpha_composite(cell, (k * cw, 0))
    ip = rig_frame(rig_dir, 'idle')
    for k in range(4):
        sheet.alpha_composite(ip, (k * cw, ch))
    sheet.convert('RGB').save(out, optimize=True)


if __name__ == '__main__':
    if sys.argv[1] == 'walk':
        walk(sys.argv[2], sys.argv[3])
    else:
        idle(sys.argv[2], sys.argv[3], sys.argv[4])
