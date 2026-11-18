"""AI 가 '투명 배경'으로 그렸는데 인물 주변에 반투명 안개(회색·검은 얼룩)가 남은 그림을 정리한다.

이미지 서버의 투명 배경 출력은 가끔 안개를 남긴다 (게임에서 인물 옆 검은 자국이 됨).
애니메이션 그림체 전용 배경 제거 모델(rembg 의 isnet-anime)로 인물 모양을 찾고,
원래 투명도(부드러운 경계)는 그대로 둔 채 그 모양 밖의 안개만 지운다.

준비 (한 번만, 모델 약 170MB 는 처음 실행할 때 내려받는다):
    python3 -m venv ~/rembg_env && ~/rembg_env/bin/pip install "rembg[cpu]"
사용:
    ~/rembg_env/bin/python tools/cutout.py <원본폴더>/pose_tavern_martha_busy.png ...
원래 파일은 <이름>_hazy.png 로 남긴다 (이미 있으면 덮어쓰지 않음).
"""
import os
import sys

from PIL import Image, ImageChops, ImageFilter
from rembg import new_session, remove


def clean(path, session):
    base, ext = os.path.splitext(path)
    hazy = base + "_hazy" + ext
    src = hazy if os.path.exists(hazy) else path
    im = Image.open(src).convert("RGBA")
    if not os.path.exists(hazy):
        im.save(hazy)
    flat = Image.new("RGBA", im.size, (255, 255, 255, 255))     # 안개를 흰 바탕에 눌러서 모델에 준다
    flat.alpha_composite(im)
    shape = remove(flat.convert("RGB"), session=session, post_process_mask=True).getchannel("A")
    gate = shape.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.5))   # 경계 2px 여유
    out = im.copy()
    out.putalpha(ImageChops.multiply(im.getchannel("A"), gate))
    out.save(path)
    print("cutout", os.path.basename(path))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    s = new_session("isnet-anime")
    for p in sys.argv[1:]:
        clean(p, s)
