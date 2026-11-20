# 그림 생성 규칙 (AI 이미지 생성 전에 반드시 읽기)

그림을 새로 만들거나 고칠 때는 **이 파일대로** 견본을 넣고 프롬프트를 쓴다.
견본을 빼먹거나 프롬프트를 짧게 쓰면 화풍·얼굴·크기가 달라진다 (아래 '실패 기록').

## 1. 견본 목록 (이미지 서버 id)

| 이름 | id | 용도 |
|---|---|---|
| **화풍 기준 — 카이** | `img_mwk04ey99961j7GF` | 인물 그림체의 기준 (새 루비도 카이를 견본으로 다시 그림) |
| **루비 (확정, 2차)** | `img_mwk42de2VhNaQR34` | 카이 그림체로 다시 그린 루비 (머리 94%, 눈 작게, 눈동자는 3번 크기). 게임 파일은 이 그림에서 눈만 합친 것 |
| 루비 (예전) | `img_mwjcm7u5W3q5maZ1` | 붓칠이 부드러운 예전 그림체 — 쓰지 않음 |
| **배경 화풍 기준 — 길드 홀** | `img_mwjzz6ejUwIEo3A9` | 모든 배경에 넣는다 |
| 카이 | `img_mwk04ey99961j7GF` | 몸 (오른쪽을 봄) |
| 마르타 (예전) | `img_mwk04p3zc4tZ1Zln` | 루비와 닮아서 교체됨 → 지금 마르타는 콘셉트 01 레나 |
| 마르타 새 후보 A / B / C | `img_mwk3t4rvcZF5sLeh` / `img_mwk3tedn5xGs0gof` / `img_mwk3tqbznKRo5MH0` | A 은퇴한 모험가 / B 푸근한 아줌마 / C 키 큰 무뚝뚝한 사장 |
| 마르타 성숙한 후보 1 / 2 | `img_mwk4etfk9wjDt7JE` / `img_mwk4f33wxOsIhdvF` | 1 화려한 사장님 / 2 다정하게 놀리는 누님 |
| 마르타 매혹적인 후보 3 / 4 | `img_mwk4iohqq12tH346` / `img_mwk4iwruJiDxqgw5` | 3 = 1번을 고쳐 분위기만 (머리 만지는 손, 나른한 눈) / 4 = 1번 얼굴 견본으로 새로 |
| 마르타 매혹적인 후보 3·4 얼굴 부드럽게 | `img_mwk4lev6V6ZxHKtp` / `img_mwk4lnxmpxNW9dCD` | 턱선·광대를 둥글게 ("얼굴이 너무 각졌다") |
| 핍 | `img_mwk04yuwDl5LkiiB` | 몸 (전신, 작게) |
| 그레고르 | `img_mwk05a0vTrlhPirv` | 몸. 이 화풍에서 **나이(주름)를 그리는 법**의 견본 |
| 여성 후보 10명 (40세 미만) | 레나 `img_mwk4pph0U68HMxxT` · 이졸데 `img_mwk4pwg3bFu67AQ1` · 자라 `img_mwk4q7t4iIdGqDBx` · 하나 `img_mwk4qgtywx6u2ZP6` · 브리짓 `img_mwk4qogq5pn4Z3jN` · 셀레스트 `img_mwk4smg88Psimnwd` · 엘로디 `img_mwk4stgr8dxk6OMC` · 닉스 `img_mwk4rh90Gge9A6ra` · 로사 `img_mwk4rns6l3dnN338` · 세라핀 `img_mwk4rv56xs6vpHgX` | 카이 견본 하나로 처음부터. 나이 든 인물은 만들지 않는다 (40세 미만) |
| 배경: 내 방 / 길드 앞 | `img_mwk00f9bvTm6XvLx` / `img_mwk010ifbr0lNxiK` | |
| 배경: 부엌 (식탁을 가까이 잡은 판, 지금 쓰는 것) | `img_mwkknsql1wyx241h` | 식탁 85cm·긴 의자 45cm 실제 비율 |
| 배경: 부엌 (넓게 잡은 예전 판) | `img_mwk00ppuKfGbnYrw` | |
| 배경: 광장 | `img_mwk01cc9WcxxfKxh` | |
| 배경: 선술집 / 잡화점 (바·계산대를 가까이 잡은 판, 지금 쓰는 것) | `img_mwketo5muLfRunxQ` / `img_mwkf4h896XJ8x4Jn` | 바 105cm·의자 75cm·계산대 95cm 실제 비율 |
| 배경: 선술집 / 잡화점 (멀리서 넓게 잡은 예전 판) | `img_mwk01nibyD82wGX9` / `img_mwk020slS8bQPtdR` | 가구 뒤 인물이 거인처럼 보여 교체 |
| 배경: 숲 / 동굴1 / 동굴2 / 지도 | `img_mwk02c108Sm3wYz9` / `img_mwk02mmcAUfpVboO` / `img_mwk02zsd7TnAykBH` / `img_mwk03bkheoQNSpy0` | |
| 장면(하던 일): 부엌 루비 / 홀 루비 | `img_mwk2b8ltoHvj1Qh2` / `img_mwk28cebpXWz68CU` | |
| 장면(하던 일): 선술집 마르타 / 잡화점 핍 / 광장 핍 | `img_mwk337koGb2kM4Zu` / `img_mwk33ey2wlWuSMdW` / `img_mwk33ndtudBcVSua` | |

## 2. 그림 종류별로 꼭 넣을 견본 (images 순서 = 역할)

첫 번째 그림이 고칠 대상이다. 프롬프트에 **몇 번째 그림이 무슨 역할인지** 반드시 적는다.

| 만들 것 | 1번 (고칠 대상) | 2번 이후 (견본) |
|---|---|---|
| 새 인물 몸 (처음부터) | 카이 = 화풍만 | (2) 그레고르 = 나이 표현 (3) 비슷한 나이·성별의 기존 인물 = 얼굴 비율. **젊은 여성 견본(루비)은 넣지 않는다** — 얼굴까지 따라간다 |
| 인물 얼굴 다시 디자인 | 그 인물 몸 | (2) 루비 = 화풍 (3) 그레고르 = 나이 표현 (나이 든 인물일 때) |
| 표정 | 그 인물 몸 | (2) 루비 = 화풍 — 얼굴 크기·위치는 1번 그대로 |
| 배경 | 길드 홀 | (2) 루비 = 화풍 |
| 장소 안 인물 1) 장면 | 그 장소 배경 | (2) 그 인물 몸 = 얼굴·옷 (3) 카이 = 그림체 — 배경에 인물을 함께 그림 (자세·위치 기준). 프롬프트에 **가구 높이와 키를 cm 로** 쓴다. 그래도 AI 는 인물을 1.4~2배 크게 그리므로 `art_scenes.json` 의 `check` 로 재고 `scale` 로 줄인다 |
| 장소 안 인물 2) '하던 일' | **그 인물의 대화 그림** (얼굴·머리카락·비율을 지키는 대상) | (2) 1) 장면 또는 예전 그림 = 자세·동작만 ('얼굴·눈·머리카락·비율은 따라 하지 말 것'). 머리는 그대로 두고 팔·손·소품만 바꾸고, 시선만 하던 일 쪽으로. 앉은 자세도 '머리 크기·위치는 그대로, 몸은 그 아래에'. **단, 대화 그림과 구도가 다른 자세(앉은 전신 등)는** 비율이 맞는 그림(예전 장면 그림)을 고칠 대상으로 두고 얼굴·머리카락·옷만 대화 그림을 따르게 한다 |
| 장소 안 인물 '앞을 봄' | 고개 각도가 대화 그림과 같으면 그리지 않는다 | 대화 그림의 얼굴(CHARS face_box)을 가공 단계가 그대로 옮겨 붙인다 (`look_from: profile`). **고개를 숙이는 등 각도가 다르면** 2) 그림을 정밀 모드로 눈·입만 바꾼다 (얼굴을 옮기면 눈·코·턱이 머리와 어긋남) |
| 적 | 카이 전투 그림 `img_mwowkjbqz34hCgSu` = 화풍(사람형 적은 3.5등신 비율도) | 하나만 넣고 디자인은 글로 자세히. **좌우 전투라 적은 오른쪽에 서서 왼쪽을 본다.** 투명 배경 |
| 아이템 | 루비 | (2) 배경 1장 = 색감 |

## 3. 프롬프트 틀 (영어로, 빠짐없이)

```
[ROLES] The FIRST image is the one to edit. The SECOND image is <역할>. The THIRD image is <역할>.
[KEEP] Keep EXACTLY the same: <포즈, 옷, 소품, 머리, 구도, 크기, 위치, 배경 …>.
[CHANGE] Change ONLY: <바꿀 것 — 구체적으로>.
[STYLE] Match the art style of the SECOND image exactly: (아래 화풍 문단 그대로)
[AVOID] (아래 금지 문단 그대로)
```

**화풍 문단 (그대로 붙여 넣기)**

> thin dark outlines of even weight around every shape; simplified, smooth shapes; soft shading in 2–3 gentle gradient steps;
> eyes drawn simply — white sclera, a flat single-colour iris with a darker pupil and ONE small white highlight dot,
> the upper lash line as one thick dark stroke with two or three short flicks, no lower lashes;
> nose as a small simple shape with a soft shadow; lips simple and matte; skin flat and smooth with a soft blush;
> hair in grouped locks with only a few strand lines; age shown only with one or two simple thin lines

**금지 문단 (그대로 붙여 넣기)**

> no realistic skin texture or pores, no detailed or glossy irises, no makeup, no glossy lips, no fine hair strands,
> no photorealism, no change of head size, no change of the art style

## 4. 실패 기록 (같은 실수를 하지 않기)

| 실패 | 원인 | 해결 |
|---|---|---|
| 배경이 실사처럼 나옴 | 화풍 견본 없이 생성 | 루비 + 길드 홀을 같이 넣는다 |
| 마르타 얼굴 후보가 실사 쪽으로 감 | 견본 없이 "주름·주근깨" 같은 세부를 요구 | 루비(화풍) + 그레고르(나이 표현) 견본, 화풍·금지 문단 |
| 루비와 마르타가 닮음 | 같은 또래 여성을 루비 견본으로 그리면 루비 얼굴로 끌려감. 그 그림을 고쳐 봐야 얼굴만 조금 바뀜 | **처음부터 새 인물로** 만든다. 얼굴만이 아니라 체형·나이·머리 모양·소품까지 루비와 다르게 정하고, 1번 그림(루비)은 '화풍만 참고, 얼굴·몸·머리·옷은 따라 하지 말 것'이라고 쓴다 |
| 성숙한 마르타 후보가 또 루비처럼 나옴 | 화풍 견본으로 루비를 넣음 → '매력적인 여성'을 그리면 루비 얼굴로 감 | 루비를 빼고 카이·그레고르·마르타 A 를 견본으로, 중년 얼굴 특징(긴 얼굴, 광대, 코 옆 선, 작은 눈)을 구체적으로 |
| 루비 눈 감기에서 먼 쪽 눈이 반투명하게 남음 | 얼굴 영역 경계에 눈이 걸림 | 얼굴 영역을 넉넉히 + `face` 단계가 만드는 점검용 그림(`원본폴더/_review_faces.png`)을 꼭 눈으로 본다 |
| 성숙한 마르타가 '친근한 아줌마' 같고 매혹적이지 않음 | 나이 특징만 지정하고 분위기(표정·자세·옷차림)는 지정 안 함 | 나른한 눈매·기울인 고개·은근한 미소·붉은 입술, 머리를 만지는 손, 어깨 드러난 블라우스·조인 코르셋 (노출 없이) |
| 장소 안 인물의 얼굴·인상이 뭉개짐 | 배경 그림 안에 인물을 그려 넣게 함 → 인물이 몇십 px 로 작게 그려지고 다시 줄이며 더 뭉개짐 | 인물만 단독으로 크게 그린다 |
| 단독 인물을 얹었더니 크기·비율이 어색하고 굵은 외곽선이 튐 | 자세·크기를 따로 정함, 원작 흉내로 외곽선을 두름 | 1) 장면을 견본으로 같은 자세의 인물만 다시 그리고, 1) 의 실루엣에 자동으로 겹쳐 맞춘다. 외곽선은 뺀다 |
| 식탁 뒤에 선 인물이 '식탁 위에 올려 놓은' 것처럼 보임 | 가구 윗면의 앞쪽 모서리에서 잘라 몸이 윗면과 그 위 물건을 덮음 | 윗면 '뒤쪽' 끝에서 자르고(cut), 가구 위에 올린 손만 보이게(show), 가구 위 물건은 인물 앞에(hide) |
| 다시 그린 인물에서 소품(핍의 안경)이 빠짐 | 장면 견본을 따라 그리며 디자인 일부를 놓침 | 결과를 디자인과 나란히 놓고 확인, 빠진 것만 추가로 그려 넣기 |
| 인물이 하는 일(당근 썰기)이 배경의 물건(당근 더미)에 가려져 안 보임 | 배경에 원래 있던 물건 뒤에 인물을 세움 | 원작처럼 손에 쓰는 물건(도마·당근)은 인물 그림에 같이 그리고, 배경에서 그 자리 물건은 치운다 |
| 장면 인물이 고개를 들 때 머리가 10~20% 커지고 인상이 바뀜 | 머리를 통째로 다시 그리게 함 | 머리는 그대로, **눈과 입만** 바꾼다 |
| 장면 인물이 빤히 쳐다봐서 무서움 | "카메라를 정면으로 보라" | 편안한 눈꺼풀, 살짝 치켜뜬 눈길, 작은 미소 |
| 장면 인물 눈 색이 바뀜 | 인물 견본 없이 얼굴을 다시 그림 | 인물 몸을 2번 견본으로 넣는다 |
| 바·계산대 뒤 인물이 거인처럼 보임 — 가구 아래 남은 길이에 허리·다리가 들어갈 수 없음 (마르타 2.2배, 핍 1.7배) | 배경이 가구를 멀리서 넓게 잡았고, AI 가 얼굴이 보이게 인물을 크게 그림. 실제 비율로 줄이면 얼굴이 뭉개지고 의자가 커 보임 | 인물이 가구 뒤에 서는 장소는 **배경을 가구 가까이 잡아** 다시 그린다 (가구 높이를 화면 % 와 cm 로 지정). 장면 단계의 `check` 가 가구 높이로 비율을 재고 `scale` 로 맞춘다 (0.8~1.25배 밖이면 경고) |
| 크기 보정 뒤 손이 배경 물건(저울)에서 떨어짐 | 인물을 줄이면 뻗은 손도 몸 쪽으로 따라 줄어든다 | 손·소품이 몸 앞(가구 윗면 위)에 있는 자세로. 배경 물건을 만지는 자세는 피한다 |
| '앞을 봄' 그림에서 고개가 정면으로 돌아감 | 보통 모드가 머리를 다시 그림 | 정밀 모드 + '머리 그대로, 눈동자와 입만' |
| 가구 위 도마가 식탁 앞 모서리에 얇은 선처럼 보이고 칼이 식탁에 박힌 것 같음 | 단독 그림(2)은 눈높이에서 그려서 도마가 옆모습. 배경은 위에서 내려다본 원근 | `show_from_scene`: 가구 윗면 아래(show 안)는 1) 장면의 손·도구 픽셀을 쓴다 — 배경과 같은 원근 |
| '앞을 봄' 그림 투명 배경에 옅은 얼룩 → 머리 옆 검은 자국 | 정밀 모드 결과의 투명 배경이 완전히 투명하지 않음 | 가공에서 몸 그림이 불투명한 곳 안에서만 합친다 (`look_from_busy`) |
| 장소 안 인물의 눈매·눈 크기·머리카락 표현이 대화 그림과 다름 (잡화점 핍은 아이처럼 됨) | 2) 를 1) 장면(배경 속 작게 뭉개진 얼굴)을 보고 새로 그림 → 복사본의 복사본. 핍은 견본으로 대화 그림 대신 예전 장면 그림을 넣음 | 2) 는 **대화 그림을 고칠 대상(1번)으로** 넣고 팔·손·소품만 바꾼다. 앞을 보는 얼굴은 대화 그림에서 옮겨 붙인다 (`look_from: profile`) |
| 앉은 홀 루비가 머리 큰 인형처럼 됨 (몸이 작고 짧음) | 대화 그림은 허벅지까지인데 '머리 크기·위치 그대로' 앉은 전신을 넣으라고 해서 AI 가 몸만 줄임 | 구도가 다른 자세는 비율이 맞는 그림을 고칠 대상으로, 대화 그림은 얼굴·머리카락 견본으로. 얼굴 옮기기는 머리 크기가 달라도 되게 넓게 찾는다(`locate`) |
| 고개 숙인 홀 루비의 '앞을 봄'이 이상함 (눈·코·턱 위치가 머리와 어긋남, 턱 옆 얼룩) | 똑바로 선 대화 그림 얼굴을 기울어진 머리에 붙임 | 고개 각도가 다른 장면은 얼굴 옮기기 대신 정밀 모드로 눈·입만 바꾼다 (`look_from` 빼기). 하던 일 얼굴이 이미 대화 그림 얼굴이라 인상은 유지된다 |
| 얼굴을 옮겨 붙인 '앞을 봄'에서 목·옷깃에 살색 얼룩 | 사각형 영역이라 대화 그림의 목·옷깃까지 옮겨짐 (자세가 달라 어긋남) | 얼굴 모양 타원, 아래는 턱선까지만 |
| '투명 배경'으로 그렸는데 인물 주변에 반투명 안개(회색·검은 얼룩), 일부는 불투명 | 이미지 서버의 투명 배경 출력이 불안정 | `tools/cutout.py` (애니메이션용 배경 제거 모델 isnet-anime) 로 인물 모양 밖 안개만 지운다. 원래 경계의 부드러운 투명도는 유지 |
| 영역 지정(마스크) 편집 실패 | 이미지 서버가 마스크를 거부 ("Invalid image data") | 마스크 없이 "~만 바꿔"로 그리고 `art_pipeline.py` 가 바뀐 곳만 오린다 |

## 5. 지금 게임에 들어간 그림의 원본 id (2026-11-17)

| 그림 | id |
|---|---|
| 마르타 몸 (= 콘셉트 01 레나) | `img_mwk4pph0U68HMxxT` |
| 마르타 표정 기쁨 / 화남 / 놀람 / 말하기 | `img_mwk5fs1nykP7cvOp` / `img_mwk5gla19Zqx0u4w` / `img_mwk5gvn65H1AW9uM` / `img_mwk5h46bAJqzY5hq` |
| 장소 인물 1) 장면 — 부엌 루비 / 길드 홀 루비 / 선술집 마르타 | `img_mwk5hezcIrN7DtBx` / `img_mwk5hr8xDOZxF9XX` / `img_mwk5j435FcIsnrxc` |
| 장소 인물 1) 장면 — 잡화점 핍 / 광장 핍 | `img_mwk33ey2wlWuSMdW` / `img_mwk33ndtudBcVSua` |
| 부엌 루비 (가까운 배경판) — 1) 장면 / 2) 하던 일 / 앞을 봄 | `img_mwkkp0yg6PxIIVWL` / `img_mwkkq2npdOSyO0qa` / `img_mwkkrav3xvZHIELF` (scale 없음, 비율 1.07배) |
| 장소 인물 2) 하던 일 / 앞을 봄 — 부엌 루비 (예전 넓은 배경판, 도마·당근 포함) | `img_mwk7pc09G7ElWjcv` / `img_mwk7q63yNWNOkHvU` |
| 부엌 배경 (예전 넓은 판, 식탁 위 채소 치운 것) | `img_mwk7p1h5vMRQxjDf` — 새 부엌 배경의 1번 견본으로 씀 |
| 길드 홀 루비 | `img_mwk6o5dzKhYphXZU` / `img_mwk6yuuuSZxYZcY3` |
| 장소 안 인물 2) 하던 일 — 대화 그림을 고친 판 (지금 쓰는 것): 선술집 마르타 / 부엌 루비 / 홀 루비 / 잡화점 핍 / 광장 핍 | `img_mwlrlsaqYfMcFXEL` / `img_mwlrm2l4cwVHQJMt` / `img_mwls9z8eVbANVgSF` (예전 홀 그림을 고쳐 얼굴만 대화 그림으로 — 대화 그림을 고친 `img_mwlrmeckxxxaUxFy` 는 머리가 커서 버림) / `img_mwlrix6yHwRgeGRn` / `img_mwlrmnsx7VHiRsXv` (모두 cutout 처리, 앞을 봄 = 대화 그림 얼굴 — 홀 루비만 정밀 모드 눈·입 `img_mwluc999LL7gLhmV`) |
| 선술집 마르타 (가까운 배경판) — 1) 장면 / 2) 하던 일 / 앞을 봄 | `img_mwkevd8k42sjW1jn` / `img_mwkewnqqXXwNxBNb` / `img_mwkeyo6bqUR647Bs` (scale 0.66) |
| 잡화점 핍 (가까운 배경판, 금화를 눈앞에 들고 살핌) — 1) 장면 / 2) 하던 일 / 앞을 봄 | `img_mwkf5ohi9lqOiGCF` / `img_mwkf7ariy6pdxx7U` / `img_mwkf8fifRo3DwyRV` (scale 0.74) |
| 선술집 마르타 (예전 넓은 배경판) | `img_mwk6oedcaIUMwko8` / `img_mwk6z55aHqkz4brz` |
| 잡화점 핍 (예전 넓은 배경판, 안경 추가본) | `img_mwk78bq8hfBDZSQl` / `img_mwk78mczfQ4x80FA` |
| 광장 핍 (술통 포함) | `img_mwk6owfupJ7J4qRB` / `img_mwk6zn45hSa75y0G` |

| 지도 장식 (구름 3 + 갈매기 날갯짓 4단계, 투명 배경 한 장) | `img_mwn4x49yTdbjTHoJ` — 지도를 화풍 견본으로. `art_pipeline.py mapfx` 가 잘라 크기를 맞춤 |

| 적 (카이 전투 그림 화풍, 왼쪽을 봄) — 슬라임 / 고블린 / 독버섯 / 두꺼비 왕 | `img_mwoyxiftap1UjEjq` / `img_mwoyxp3hhynICtxE` / `img_mwoyxwc0RbON4xf5` / `img_mwoyy5qzwO0t0cxj` |
| 카이 전투 그림 (3.5등신, 오른쪽을 봄) | `img_mwowkjbqz34hCgSu` |

이미지 서버 제한: **하루 100회, 분당 6회**. 여러 장은 6장씩 나눠 보낸다.

## 6. 저녁·밤 배경 — 다시 그리기 계획 (아직 실행하지 않음)

**지금:** 밤 그림 = 낮 그림을 어둡고 푸르게 보정한 것. 창문 햇빛 자국이 그대로 남고 등불이 켜지지 않아 "어두운 낮"처럼 보인다.
**원작:** 낮·저녁·밤을 따로 그렸다 (저녁 = 어둡고 창문·등불 켜짐 / 밤 = 불 꺼짐). 274 / 118 / 238장. 저녁 그림이 없으면 밤 → 낮 순서로 대신 쓴다.
**계획:** AI 로 **저녁(불 켜짐)** 만 다시 그리고, **밤은 저녁 그림에서 계산**으로 만든다 (돈 안 듦).

| 장소 | 저녁(시간대 2) | 밤(시간대 3) | 이유 |
|---|---|---|---|
| 길드 홀 · 내 방 · 부엌 · 광장 · 선술집 · 지도 | 다시 그림 | 저녁에서 계산 | 저녁·밤 모두 들어갈 수 있음 |
| 숲 | 다시 그림 | 없음 | 밤에는 잠김 |
| 잡화점 | 없음 | 없음 | 저녁부터 문 닫음 → 지금 `bg_shop_night` 도 지울 수 있음 |
| 동굴 1·2 · 길드 앞 | 없음 | 없음 | 동굴은 시간과 무관, 길드 앞은 도입(낮)에만 |

**견본 (2번 규칙의 '배경' 줄 + 1번에 그 장소 낮 그림)**
1. 그 장소 낮 배경 (고칠 대상 — 구도·물건 위치를 그대로 지켜야 클릭 모양이 맞는다)
2. 길드 홀 배경 `img_mwjzz6ejUwIEo3A9` (배경 화풍)
3. 카이 `img_mwk04ey99961j7GF` (선 굵기·색칠 방식)

**프롬프트 (영어, 장소마다 [CHANGE] 의 불빛 목록만 바꾼다)**
```
[ROLES] The FIRST image is the scene to edit. The SECOND image is the background art-style reference.
The THIRD image is the line and colouring style reference.
[KEEP] Keep EXACTLY the same: camera, framing, perspective, every piece of furniture and every object
in the same position and size, the same doors, windows, shelves and props. Do not add or remove anything.
[CHANGE] Change ONLY the lighting to early evening after sunset: the windows show a deep blue-violet dusk sky;
remove every patch of sunlight on the floor, walls and tables; light every lamp, candle, lantern and the
hearth (<장소별 불빛 목록>) with warm orange light, soft glow around each light and gentle warm light pools
on nearby surfaces; the rest of the room falls into cool blue-grey shadow.
[STYLE] Match the SECOND image: (화풍 문단 중 배경에 해당하는 부분 — 얇은 진한 외곽선, 단순한 형태, 2~3단 부드러운 음영)
[AVOID] no new objects, no people, no change of layout, no photorealism, no lens flare, no bloom haze over the whole image
```

**가공 (`art_pipeline.py bg` 에 추가할 것)**
- 저녁 그림을 낮 그림에 **자동으로 위치·크기 맞춤** (표정 단계와 같은 방식). 어긋남이 4px 를 넘으면 `확인 필요` → 클릭 모양이 안 맞을 위험.
- 밤 = 저녁 그림을 어둡고 푸르게 + **밝은 곳(불빛)은 그대로 둔다** (밝기 기준으로 섞기). 그래서 등불만 켜진 늦은 밤이 된다.
- 장소 안 인물(`scene`)도 저녁판을 만든다: AI 를 다시 쓰지 않고, 인물 주변 저녁 배경의 색감을 옮긴다 (지금 낮 장면에서 하는 색 옮기기와 같은 함수).

**코드 (`location_bg`)**: 시간대 2 → `_evening`, 3 → `_night`, 없으면 `_night` → `_evening` → `_day` 순서로 대신 (원작과 같은 대체 사슬).
인물 색조(`light_matrix`)도 저녁은 따뜻하게, 밤은 푸르게 나눈다.

**비용:** 7장 × 약 0.07달러 + 다시 그리기 여유 → **약 0.9달러**, 서버 호출 약 12번 (하루 100번 한도 안).
