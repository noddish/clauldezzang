#!/usr/bin/env python3
"""
AI가 그린 4x2 걷기 시트(1536x1024, 투명 배경)와 정지 포즈 시트를
게임용 스프라이트(칸 128x128, 기준점 = 골반 아래 지면 (64,120))로 가공한다.

  python3 build_sprites.py <walk_sheet.png> <idle_sheet.png> <idle_cell 0-7> <out_dir>

처리 순서
  1. 알파 임계값으로 깨끗한 마스크를 만들고 떨어진 부스러기를 지운다
  2. 프레임끼리 머리 위치를 맞춘다(머리가 항상 같은 픽셀 격자에 놓이도록)
  3. 프레임마다 키를 원본 리그의 상하 움직임(접지·하강 낮음 → 통과 → 상승 높음)에 맞춘다
     (머리는 그대로 두고 목 아래만 세로로 미세 조정, 발바닥은 지면선에 고정)
  4. 4배 → 1배로 줄이며 공용 팔레트로 색을 정리해 진짜 픽셀 아트로 만든다
  5. 걷기 8프레임은 가장 잘 나온 머리 하나를 공통으로 쓴다(얼굴이 깜빡이지 않게).
     머리는 정수 픽셀로만 움직이고, 머리카락 끝만 한 박자 늦게 1px 처진다
"""
import sys, os, json
import numpy as np
from PIL import Image

SC = 4                    # 생성 시트는 리그 좌표의 4배
CELL_W, CELL_H = 96, 128  # 시트 한 칸 (리그 셀의 x 16..112 구간)
CROP_X = 16
OUT = 128                 # 출력 칸 크기 (리그 셀과 동일)
OX, OY = 64, 120          # 기준점: 골반 아래 지면
HEAD = 100                # 머리(정수리~턱) 구간 높이(4배 좌표). 이 구간은 늘이거나 줄이지 않는다
REG_ROWS = 88             # 머리 정합에 쓰는 구간 높이(4배 좌표)
BOB = [0, 0, 2, 3]        # 리그의 머리 높이 변화(네이티브 px): 접지, 하강, 통과, 상승
IDLE_BOB = 2
REF_FRAME = 2             # 머리 정합의 기준 프레임(통과)
N_COLORS = 40
HEAD_ROWS_N = 28          # 네이티브 머리 창 높이(정수리~목)
HEAD_SRC = 3              # 걷기 프레임 공통 머리로 쓸 프레임
TIP_COLS = 7              # 머리카락 끝(뒤쪽) 구간 폭
JACKET_ROWS = 75          # 이 줄 위쪽의 빨강은 재킷(부츠·장갑 제외)
TIP_LAG = [0, 1, 1, 0]    # 머리카락 끝이 처지는 양(px): 접지, 하강, 통과, 상승


def load_cells(path):
    im = np.array(Image.open(path).convert('RGBA'))
    assert im.shape[:2] == (CELL_H * SC * 2, CELL_W * SC * 4), im.shape
    return [im[(i // 4) * CELL_H * SC:(i // 4 + 1) * CELL_H * SC, (i % 4) * CELL_W * SC:(i % 4 + 1) * CELL_W * SC].copy() for i in range(8)]


def clean_mask(alpha):
    """알파>127 인 픽셀 중 충분히 큰 덩어리만 남긴다."""
    m = alpha > 127
    h, w = m.shape
    lab = np.zeros((h, w), np.int32)
    sizes = [0]
    cur = 0
    ys, xs = np.nonzero(m)
    for y0, x0 in zip(ys.tolist(), xs.tolist()):
        if lab[y0, x0]:
            continue
        cur += 1
        lab[y0, x0] = cur
        stack = [(y0, x0)]
        n = 0
        while stack:
            y, x = stack.pop()
            n += 1
            for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= yy < h and 0 <= xx < w and m[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = cur
                    stack.append((yy, xx))
        sizes.append(n)
    if cur == 0:
        return m
    big = max(sizes)
    keep = np.array([s >= max(60, big * 0.004) for s in sizes])
    keep[0] = False
    return keep[lab]


def classes(rgb):
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    blue = (b > 110) & (b > r + 50) & (b > g + 30)
    gold = (r > 185) & (g > 135) & (g < 235) & (b < 105) & (r - b > 110)
    return blue, gold


def head_feature(cell, m):
    """머리 정합용 특징: 스카프(파랑)를 뺀 불투명 픽셀의 밝기."""
    rgb = cell[..., :3].astype(np.float64)
    blue, _ = classes(cell[..., :3])
    lum = rgb @ np.array([0.30, 0.59, 0.11]) + 40.0
    return np.where(m & ~blue, lum, 0.0)


def register(feat, top, ref_feat, ref_top, rx=16, ry=8):
    """기준 프레임의 머리와 가장 잘 겹치는 이동량(dx, dy)을 찾는다."""
    h, w = feat.shape
    R = ref_feat[ref_top:ref_top + REG_ROWS, rx:w - rx]
    best = None
    for dy in range(-ry, ry + 1):
        y0 = top + dy
        if y0 < 0 or y0 + REG_ROWS > h:
            continue
        for dx in range(-rx, rx + 1):
            F = feat[y0:y0 + REG_ROWS, rx + dx:w - rx + dx]
            c = np.abs(F - R).mean()
            if best is None or c < best[0]:
                best = (c, dx, dy)
    return best


def normalize(cell, m, top_s, xshift, bob_native, h_base):
    """칸(4배) → 512x512 캔버스. 발바닥을 지면선에, 키를 목표 높이에 맞춘다."""
    rgb = cell[..., :3]
    ys = np.nonzero(m.any(1))[0]
    bot_s = int(ys.max()) + 1
    G = OY * SC                                               # 지면선(발바닥 아래 경계)
    H = h_base + bob_native * SC                              # 목표 키
    top_t = G - H
    neck_s, neck_t = top_s + HEAD, top_t + HEAD
    s = (G - neck_t) / (bot_s - neck_s)                       # 목 아래 세로 배율
    canvas = np.zeros((OUT * SC, OUT * SC, 4), np.uint8)
    xo = CROP_X * SC + xshift
    for yt in range(0, G):
        ysrc = top_s + (yt - top_t) if yt < neck_t else neck_s + (yt - neck_t + 0.5) / s - 0.5
        yi = int(round(ysrc))
        if yi < 0 or yi >= cell.shape[0]:
            continue
        row_m = m[yi]
        canvas[yt, xo:xo + cell.shape[1], :3] = rgb[yi] * row_m[:, None]
        canvas[yt, xo:xo + cell.shape[1], 3] = row_m * 255
    return canvas, dict(height=bot_s - top_s, body_scale=round(s, 4), xshift=xshift)


def nearest(px, pal):
    """각 픽셀에 가장 가까운 팔레트 색 번호 (밝기 차이에 가중치를 준 거리)."""
    px = px.astype(np.float64)
    pal = pal.astype(np.float64)
    w = np.array([0.30, 0.59, 0.11]) * 3
    out = np.empty(len(px), np.int32)
    for s in range(0, len(px), 50000):
        d = ((px[s:s + 50000, None, :] - pal[None]) ** 2 * w).sum(2)
        out[s:s + 50000] = d.argmin(1)
    return out


def kmeans(pixels, k, iters=12, seed=1):
    """중앙값 분할로 초기화한 뒤 k-means 로 다듬은 팔레트."""
    rng = np.random.default_rng(seed)
    if len(pixels) > 120000:
        pixels = pixels[rng.choice(len(pixels), 120000, replace=False)]
    strip = Image.fromarray(pixels.reshape(1, -1, 3).astype(np.uint8), 'RGB')
    q = strip.quantize(colors=k, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = np.array(q.getpalette()[:k * 3], np.float64).reshape(-1, 3)
    px = pixels.astype(np.float64)
    for _ in range(iters):
        idx = nearest(px, pal)
        for c in range(len(pal)):
            sel = px[idx == c]
            if len(sel):
                pal[c] = sel.mean(0)
    return np.clip(np.round(pal), 0, 255).astype(np.uint8)


def downsample(canvas, pal, accent):
    """4x4 블록마다: 절반 이상 불투명하면 그 블록에서 가장 많이 나온 팔레트 색.
    금색(귀걸이·버클·끈)처럼 가는 포인트 색은 5/16 만 넘어도 살린다."""
    h, w = canvas.shape[0] // SC, canvas.shape[1] // SC
    a = canvas[..., 3] > 127
    idx = np.full(canvas.shape[:2], -1, np.int32)
    idx[a] = nearest(canvas[..., :3][a], pal)
    _, gold = classes(canvas[..., :3])
    gold &= a
    blocks = idx.reshape(h, SC, w, SC).transpose(0, 2, 1, 3).reshape(h, w, SC * SC)
    gblocks = gold.reshape(h, SC, w, SC).transpose(0, 2, 1, 3).reshape(h, w, SC * SC)
    out = np.full((h, w), -1, np.int32)
    k = len(pal)
    cover = (blocks >= 0).sum(2)
    for y, x in zip(*np.nonzero(cover >= SC * SC // 2)):
        b = blocks[y, x]
        gb = b[gblocks[y, x]]
        gb = gb[np.isin(gb, accent)]
        if len(gb) >= 5:
            out[y, x] = np.bincount(gb, minlength=k).argmax()
            continue
        b = b[b >= 0]
        cnt = np.bincount(b, minlength=k)
        best = np.nonzero(cnt == cnt.max())[0]
        if len(best) > 1:  # 동률이면 블록 평균색에 가까운 쪽
            mean = pal[b].astype(np.float64).mean(0)
            best = best[np.argmin(((pal[best].astype(np.float64) - mean) ** 2).sum(1))]
        else:
            best = best[0]
        out[y, x] = best
    return out


def pal_classes(pal):
    p = pal.astype(np.int32)
    r, g, b = p[:, 0], p[:, 1], p[:, 2]
    blue = (b > 90) & (b > r + 40) & (b > g + 25)        # 스카프
    red = (r > 80) & (g < 0.45 * r) & (b < 0.5 * r)       # 재킷·장갑
    return blue, red


def grow8(m):
    out = m.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            out |= np.roll(np.roll(m, dy, 0), dx, 1)
    return out


def flood(cand, seeds):
    out = np.zeros_like(cand)
    stack = [s for s in seeds if cand[s]]
    for s in stack:
        out[s] = True
    h, w = cand.shape
    while stack:
        y, x = stack.pop()
        for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= yy < h and 0 <= xx < w and cand[yy, xx] and not out[yy, xx]:
                out[yy, xx] = True
                stack.append((yy, xx))
    return out


def head_mask(win, blue_c, red_c, lum_c):
    """머리 창에서 머리(머리카락·얼굴·귀걸이)에 해당하는 픽셀과, 몸(스카프·재킷) 픽셀을 가른다."""
    op = win >= 0
    safe = np.where(op, win, 0)
    isblue = op & blue_c[safe]
    isred = op & red_c[safe]
    # 눈동자·입술처럼 머리 안에 갇힌 작은 파랑·빨강은 머리로 본다
    body = np.zeros_like(op)
    for cls in (isblue, isred):
        seen = np.zeros_like(cls)
        for y, x in zip(*np.nonzero(cls)):
            if seen[y, x]:
                continue
            comp = flood(cls, [(y, x)])
            seen |= comp
            if comp.sum() > 5 or comp[-1].any():
                body |= comp
    dark = op & (lum_c[safe] < 60)
    cand = op & ~body & ~(dark & grow8(body))
    # 씨앗: 얼굴 한가운데(눈높이 아래 몇 줄에서 가장 앞쪽 픽셀의 안쪽)
    seeds = []
    for r in (12, 16, 19):
        row = np.nonzero(cand[r])[0]
        if len(row):
            seeds += [(r, int(x)) for x in row if row.max() - 9 <= x <= row.max() - 2]
    return flood(cand, seeds), body


def to_rgba(ix, pal):
    out = np.zeros(ix.shape + (4,), np.uint8)
    m = ix >= 0
    out[m, :3] = pal[ix[m]]
    out[m, 3] = 255
    return out


def main():
    walk_path, idle_path, idle_cell, out_dir = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    os.makedirs(os.path.join(out_dir, 'frames'), exist_ok=True)
    cells = load_cells(walk_path) + [load_cells(idle_path)[idle_cell]]
    names = [f'walk_{i}' for i in range(8)] + ['idle']
    bobs = [BOB[i % 4] for i in range(8)] + [IDLE_BOB]

    masks = [clean_mask(c[..., 3]) for c in cells]
    tops = [int(np.nonzero(m.any(1))[0].min()) for m in masks]
    feats = [head_feature(c, m) for c, m in zip(cells, masks)]

    # 머리 정합: 기준 프레임의 머리에 대해 각 프레임 머리가 얼마나 어긋났는지
    reg = [register(f, t, feats[REF_FRAME], tops[REF_FRAME]) for f, t in zip(feats, tops)]

    # 정지 포즈의 키를 기준으로 삼는다
    iy = np.nonzero(masks[8].any(1))[0]
    idle_h = int(iy.max()) + 1 - (tops[8] + reg[8][2])
    h_base = int(round(idle_h / SC)) * SC - IDLE_BOB * SC

    canv, info, ox = [], [], []
    for i, (c, m) in enumerate(zip(cells, masks)):
        _, dx, dy = reg[i]
        nx = int(round(dx / SC))            # 네이티브 픽셀 단위의 머리 가로 위치 차이
        resid = dx - nx * SC                # 격자에 맞추기 위해 덜어낼 나머지(4배 좌표, -2..2)
        cv, inf = normalize(c, m, tops[i] + dy, -resid, bobs[i], h_base)
        inf.update(head_dx=dx, head_dy=dy, reg_cost=round(float(reg[i][0]), 2))
        canv.append(cv)
        info.append(inf)
        ox.append(nx)

    # 정지 포즈의 재킷 빨강을 걷기 프레임의 색 분포에 맞춘다(따로 그린 그림이라 밝기가 조금 다르다)
    def jacket(c):
        r, g, b = [c[..., k].astype(np.int32) for k in range(3)]
        m = (c[..., 3] > 127) & (r > 80) & (g < 0.45 * r) & (b < 0.5 * r)
        m[JACKET_ROWS * SC:] = False
        return m
    wpx = np.concatenate([c[..., :3][jacket(c)] for c in canv[:8]]).astype(np.float64)
    jm = jacket(canv[8])
    ipx = canv[8][..., :3][jm].astype(np.float64)
    if len(ipx) > 100 and len(wpx) > 100:
        fixed = (ipx - ipx.mean(0)) / np.maximum(ipx.std(0), 1e-6) * wpx.std(0) + wpx.mean(0)
        canv[8][..., :3][jm] = np.clip(np.round(fixed), 0, 255).astype(np.uint8)

    # 공용 팔레트 + 금색 포인트 2색
    allpx = np.concatenate([c[..., :3][c[..., 3] > 127] for c in canv])
    pal = kmeans(allpx, N_COLORS)
    _, gold = classes(allpx)
    gpal = kmeans(allpx[gold], 2, seed=2) if gold.sum() > 50 else np.zeros((0, 3), np.uint8)
    accent = np.arange(len(pal), len(pal) + len(gpal))
    pal = np.concatenate([pal, gpal])
    frames = [downsample(c, pal, accent) for c in canv]

    # 걷기 8프레임에 공통 머리를 이식한다
    top_n = [(OY * SC - (h_base + b * SC)) // SC for b in bobs]
    x0, x1 = 16, 112
    blue_c, red_c = pal_classes(pal)
    lum_c = pal.astype(np.float64) @ np.array([0.30, 0.59, 0.11])

    def window(i):
        return np.roll(frames[i], -ox[i], axis=1)[top_n[i]:top_n[i] + HEAD_ROWS_N, x0:x1].copy()

    def put(i, win):
        full = np.roll(frames[i], -ox[i], axis=1)
        full[top_n[i]:top_n[i] + HEAD_ROWS_N, x0:x1] = win
        frames[i] = np.roll(full, ox[i], axis=1)

    src = window(HEAD_SRC)
    src_m, _ = head_mask(src, blue_c, red_c, lum_c)
    cols = np.nonzero(src_m.any(0))[0]
    tip_x = int(cols.min()) + TIP_COLS
    iou = []
    for i in range(8):
        win = window(i)
        hm, body = head_mask(win, blue_c, red_c, lum_c)
        iou.append(round(float((hm & src_m).sum() / max(1, (hm | src_m).sum())), 3))
        lag = TIP_LAG[i % 4]
        sm, sp = src_m.copy(), src.copy()
        if lag:  # 머리카락 끝 구간만 아래로 lag px
            sm[:, :tip_x] = np.roll(src_m[:, :tip_x], lag, axis=0)
            sp[:, :tip_x] = np.roll(src[:, :tip_x], lag, axis=0)
            sm[:lag, :tip_x] = False
        new = win.copy()
        new[hm] = -1
        new[sm] = sp[sm]
        # 원래 머리가 있던 자리에 생긴 구멍은 맞닿은 스카프·재킷 색으로 메운다
        holes = hm & ~sm
        for _ in range(2):
            fill = new.copy()
            for y, x in zip(*np.nonzero(holes & (new < 0))):
                for yy, xx in ((y, x - 1), (y, x + 1), (y + 1, x), (y - 1, x)):
                    if 0 <= yy < new.shape[0] and 0 <= xx < new.shape[1] and new[yy, xx] >= 0 and body[yy, xx]:
                        fill[y, x] = new[yy, xx]
                        break
            body = body | ((fill >= 0) & (new < 0))
            new = fill
        put(i, new)

    for n, ix in zip(names, frames):
        Image.fromarray(to_rgba(ix, pal), 'RGBA').save(os.path.join(out_dir, 'frames', n + '.png'), optimize=True)
    strip = np.concatenate([to_rgba(ix, pal) for ix in frames[:8]], axis=1)
    Image.fromarray(strip, 'RGBA').save(os.path.join(out_dir, 'walk_strip_128.png'), optimize=True)
    full = np.concatenate([to_rgba(ix, pal) for ix in frames], axis=1)
    Image.fromarray(full, 'RGBA').save(os.path.join(out_dir, 'sheet_walk8_idle1_128.png'), optimize=True)
    hd = np.concatenate(canv, axis=1)
    Image.fromarray(hd, 'RGBA').save(os.path.join(out_dir, 'sheet_walk8_idle1_hd512.png'), optimize=True)

    meta = dict(cell=[OUT, OUT], anchor=[OX, OY], frames=names, order='접지,하강,통과,상승,접지,하강,통과,상승,정지',
                palette=['#%02x%02x%02x' % tuple(c) for c in pal.tolist()], head_offset_x=ox, head_top=top_n,
                normalize=info, h_base=h_base, head_src=HEAD_SRC, head_iou=iou)
    json.dump(meta, open(os.path.join(out_dir, 'sprites.json'), 'w'), ensure_ascii=False, indent=1)
    np.save(os.path.join(out_dir, '_indexed.npy'), np.stack(frames))
    for n, inf, o in zip(names, info, ox):
        print(n, inf, 'ox', o)
    print('palette', len(pal), 'h_base', h_base, 'head IoU vs source', iou)


if __name__ == '__main__':
    main()
