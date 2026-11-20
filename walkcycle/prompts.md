# 이미지 생성에 쓴 프롬프트

모델 `gpt-image-2.6-flare`, 편집(edit) 호출, 크기 1536x1024, quality high, 배경 transparent, PNG.
두 번 호출했고 각각 한 장씩 받았다.

핵심은 입력 이미지의 순서다. **포즈가 그려진 시트를 첫 번째(편집 대상)로** 넣고 캐릭터 디자인은 두 번째로 넣어야
포즈와 칸 위치를 그대로 지킨다. 디자인을 첫 번째로 넣거나 이미 그린 시트를 참고로 같이 넣으면
모델이 그쪽 포즈를 베껴서 걷기 동작이 틀어졌다(뛰는 자세가 섞이고, 5~8번이 1~4번의 반복이 됨).

## 1. 걷기 8프레임

입력: ① `reference/pose_guide.png` (원본 리그의 걷기 8프레임, 4x2 격자) ② `reference/character_ref.png` (캐릭터 디자인)

```
Edit IMAGE 1: repaint each of its 8 crude placeholder sprites as a high-quality pixel-art sprite of the character from IMAGE 2, keeping every sprite's pose and position exactly.

IMAGE 1 (the image to edit) is a rough placeholder walk-cycle sheet: 8 frames in a 4x2 grid, walking to the right, seen in strict SIDE VIEW. It already shows the correct body pose for each frame. For every cell keep exactly the same pose as the placeholder in that cell: the same leg angles, knee bends, boot positions and boot tilt on the ground, the same arm angles, the same head position and head height. The brighter leg and arm are the NEAR ones (in front); the darker, bluish leg and arm are the FAR ones (behind the body). Do not move the figures, do not change which leg is forward, do not lift the feet higher than the placeholder does.

IMAGE 2 is the character design to apply. Her identity and impression must match it: voluminous wavy shoulder-length silver-gray hair (NOT the spiky hair of the placeholder), tan skin, blue eye, confident smile, gold hoop earring, blue scarf tied at the neck with a long tail, cropped red leather jacket with rolled-up sleeves and small gold studs, white tank top, black belt with square gold buckle, light-blue jeans, red lace-up combat boots with yellow laces, folded cuffs and chunky gray lug soles, red fingerless gloves. Use the rendering style of image 2: 16-bit arcade beat-'em-up pixel art with dark outlines and crisp 3-4 tone cel shading, rich detail, no blur.

VIEW - very important: strict side view of the whole figure, exactly like the placeholder. Her HEAD IS IN FULL PROFILE, looking straight ahead to the RIGHT in the walking direction. Only the side of her face is visible: one eye only, the forehead, nose, lips and chin form the right-hand silhouette of the head, the ear with the gold hoop earring is visible on the side of the head, the hair covers the back of the head and falls behind the neck. She must NOT look at the camera and the face must NOT be turned toward the viewer in any frame. Keep her recognisable in profile: same hair color and volume, same skin tone, blue eye, slight confident smile.

All 8 figures at exactly the same scale and proportions. The hair and the blue scarf tail trail behind her to the left and sway slightly between frames.

BACKGROUND: fully transparent (remove the dark navy background). No floor, no shadows, no text, no numbers, no borders, no grid lines.
```

결과: `source/walk_sheet_ai_raw.png`

## 2. 정지 포즈

입력: ① `reference/idle_guide.png` (윗줄 = 1번 결과의 완성 프레임 4장, 아랫줄 = 원본 리그의 정지 포즈 4장) ② `reference/character_ref.png`

완성된 프레임을 같은 그림 안에 넣어 두면 화풍·크기·얼굴이 걷기 프레임과 맞는다. 아랫줄 네 장 중 하나를 골라 썼다.

```
Edit IMAGE 1. It is a pixel-art sprite sheet in a 4x2 grid.

The 4 sprites in the TOP ROW are finished sprites of the character (walking frames). Leave the top row exactly as it is.

The 4 figures in the BOTTOM ROW are crude placeholders of the same character STANDING STILL (idle pose). Repaint each bottom-row placeholder as a finished sprite of the same character, matching the top-row sprites exactly: the same head and profile face, the same wavy silver-gray hair (NOT the spiky hair of the placeholder), the same outfit, the same pixel-art rendering style and colors, the same scale and proportions (same head size, same shoulder height, same leg length as the top-row sprites when their legs are straight).

Idle pose, same as the placeholder: standing still and relaxed in strict side view facing RIGHT. Head in full profile looking straight to the right (one eye only, never facing the camera). Body upright. Legs straight, both boots flat on the ground, close together, the far boot only slightly behind the near boot. Both arms hang relaxed straight down at her sides with loose fists (near arm in front of the torso side, far arm mostly hidden). The hair rests naturally. The blue scarf is tied at the neck and its long tail hangs down behind her back, gently curved, not blowing in the wind.

Keep each bottom-row figure in the placeholder's position and at the placeholder's size, with the boot soles on the same ground level as the placeholder. All 4 bottom-row figures identical in design.

IMAGE 2 is the original character design, for reference only: tan skin, blue eyes, gold hoop earring, blue scarf, cropped red leather jacket with rolled-up sleeves and small gold studs, white tank top, black belt with square gold buckle, light-blue jeans, red lace-up combat boots with yellow laces, folded cuffs and chunky gray lug soles, red fingerless gloves.

BACKGROUND: fully transparent (remove the dark navy background). No floor, no shadows, no text, no numbers, no borders, no grid lines.
```

결과: `source/idle_sheet_ai_raw.png` (아랫줄 왼쪽에서 두 번째 칸을 사용)
