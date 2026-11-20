#!/usr/bin/env python3
"""
build_sprites.py 가 만든 스프라이트(_indexed.npy + sprites.json)를
sprite-skin.js 한 파일로 묶는다. 원본 페이지에서 character.js 바로 다음에 불러오면
Character.render 가 리그 그림 대신 이 스프라이트를 찍는다.

  python3 make_skin.py <build_dir> <out.js>
"""
import sys, os, json, base64
import numpy as np

build, out = sys.argv[1], sys.argv[2]
meta = json.load(open(os.path.join(build, 'sprites.json'), encoding='utf-8'))
frames = np.load(os.path.join(build, '_indexed.npy'))          # (9, 128, 128), -1 = 투명
n, h, w = frames.shape

# 런 길이 부호화: (색번호+1, 길이) 바이트 쌍. 0 = 투명
buf = bytearray()
for v in (frames.reshape(-1) + 1).astype(np.uint8).reshape(n, -1):
    i = 0
    while i < len(v):
        j = i
        while j < len(v) and v[j] == v[i] and j - i < 255:
            j += 1
        buf += bytes((int(v[i]), j - i))
        i = j
data = base64.b64encode(bytes(buf)).decode('ascii')
lines = '\n'.join("    '" + data[i:i + 100] + "'" + (' +' if i + 100 < len(data) else '') for i in range(0, len(data), 100))

js = '''/*
 * sprite-skin.js — 걷기 스프라이트 스킨
 *
 * 쓰는 법: 원본 페이지에서 character.js 바로 다음 줄에 이 파일을 불러온다.
 *     <script src="character.js"></script>
 *     <script src="sprite-skin.js"></script>
 * 그러면 Character.render 가 뼈대로 찍던 그림 대신 아래 스프라이트(걷기 8장 + 정지 1장)를 찍는다.
 * 칸 크기(128x128)와 기준점(골반 아래 지면 = 64,120)이 원본과 같아서 다른 코드는 고칠 필요가 없다.
 * 걸음 위상·속도·뼈대 보기는 원본 리그(Character.pose)를 그대로 쓴다.
 *
 * Character.spriteSkin.enabled = false 로 두면 원본 그림으로 돌아간다.
 * 이 파일은 tools/make_skin.py 가 만든다. 직접 고치지 말 것.
 */
(function (global) {
  'use strict';
  var Ch = global.Character;
  if (!Ch || !Ch.render) return;

  var W = __W__, H = __H__, WALK = 8, IDLE = 8;
  var PALETTE = __PAL__;
  // 프레임 9장: (색번호+1, 길이) 바이트 쌍의 런 길이 부호, base64
  var DATA =
__DATA__;

  var pal = new Uint32Array(PALETTE.length + 1); // ABGR, 0번 = 투명
  PALETTE.forEach(function (hex, i) {
    var v = parseInt(hex.slice(1), 16);
    pal[i + 1] = (0xff000000 | ((v & 0xff) << 16) | (v & 0xff00) | (v >>> 16)) >>> 0;
  });
  var bin = atob(DATA), frames = [], px = new Uint32Array(W * H), at = 0;
  for (var i = 0; i < bin.length; i += 2) {
    var color = pal[bin.charCodeAt(i)], run = bin.charCodeAt(i + 1);
    while (run--) {
      px[at++] = color;
      if (at === W * H) { frames.push(px); px = new Uint32Array(W * H); at = 0; }
    }
  }

  var rigRender = Ch.render;
  var skin = { enabled: true, frames: frames, palette: PALETTE, width: W, height: H, walkFrames: WALK, idleFrame: IDLE, rigRender: rigRender };

  /** 걷기 위상(0..1)과 보폭 스케일 g 로 프레임 번호를 고른다. 거의 멈췄으면 정지 포즈. */
  skin.frameFor = function (phase, g) {
    if (!(g > 0.35)) return IDLE;
    var t = phase - Math.floor(phase);
    return Math.floor(t * WALK + 0.5) % WALK; // 가장 가까운 프레임
  };

  Ch.render = function (out, p, scarf) {
    if (!skin.enabled) return rigRender(out, p, scarf);
    out.set(frames[skin.frameFor(p.phase, p.g)]);
  };
  Ch.spriteSkin = skin;
})(typeof window !== 'undefined' ? window : this);
'''
js = (js.replace('__W__', str(w)).replace('__H__', str(h))
        .replace('__PAL__', json.dumps(meta['palette']))
        .replace('__DATA__', lines))
open(out, 'w', encoding='utf-8').write(js)
print('runs', len(buf) // 2, 'bytes', len(js))
