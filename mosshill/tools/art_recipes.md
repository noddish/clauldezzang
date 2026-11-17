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
| 배경: 내 방 / 부엌 / 길드 앞 | `img_mwk00f9bvTm6XvLx` / `img_mwk00ppuKfGbnYrw` / `img_mwk010ifbr0lNxiK` | |
| 배경: 광장 / 선술집 / 잡화점 | `img_mwk01cc9WcxxfKxh` / `img_mwk01nibyD82wGX9` / `img_mwk020slS8bQPtdR` | |
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
| 장소 안 인물 1) 장면 | 그 장소 배경 | (2) 그 인물 몸 = 얼굴·옷 (3) 카이 = 그림체 — 배경에 인물을 함께 그림 (크기·자세 기준) |
| 장소 안 인물 2) '하던 일' | 1) 장면 | (2) 그 인물 몸 (3) 카이 — **1) 의 인물만** 같은 자세·비율로 크게, 배경·가구 없이 (투명) |
| 장소 안 인물 '앞을 봄' | 2) 그림 | (2) 그 인물 몸 — 눈·입만 바꾼다 |
| 적·아이템 | 루비 | (2) 배경 1장 = 색감 |

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
| 영역 지정(마스크) 편집 실패 | 이미지 서버가 마스크를 거부 ("Invalid image data") | 마스크 없이 "~만 바꿔"로 그리고 `art_pipeline.py` 가 바뀐 곳만 오린다 |

## 5. 지금 게임에 들어간 그림의 원본 id (2026-11-17)

| 그림 | id |
|---|---|
| 마르타 몸 (= 콘셉트 01 레나) | `img_mwk4pph0U68HMxxT` |
| 마르타 표정 기쁨 / 화남 / 놀람 / 말하기 | `img_mwk5fs1nykP7cvOp` / `img_mwk5gla19Zqx0u4w` / `img_mwk5gvn65H1AW9uM` / `img_mwk5h46bAJqzY5hq` |
| 장소 인물 1) 장면 — 부엌 루비 / 길드 홀 루비 / 선술집 마르타 | `img_mwk5hezcIrN7DtBx` / `img_mwk5hr8xDOZxF9XX` / `img_mwk5j435FcIsnrxc` |
| 장소 인물 1) 장면 — 잡화점 핍 / 광장 핍 | `img_mwk33ey2wlWuSMdW` / `img_mwk33ndtudBcVSua` |
| 장소 인물 2) 하던 일 / 앞을 봄 — 부엌 루비 (도마·당근 포함) | `img_mwk7pc09G7ElWjcv` / `img_mwk7q63yNWNOkHvU` |
| 부엌 배경 (식탁 위 채소 치운 판) | `img_mwk7p1h5vMRQxjDf` — 원본 배경에서 식탁 가운데만 이 그림으로 교체 |
| 길드 홀 루비 | `img_mwk6o5dzKhYphXZU` / `img_mwk6yuuuSZxYZcY3` |
| 선술집 마르타 | `img_mwk6oedcaIUMwko8` / `img_mwk6z55aHqkz4brz` |
| 잡화점 핍 (안경 추가본) | `img_mwk78bq8hfBDZSQl` / `img_mwk78mczfQ4x80FA` |
| 광장 핍 (술통 포함) | `img_mwk6owfupJ7J4qRB` / `img_mwk6zn45hSa75y0G` |

이미지 서버 제한: **하루 100회, 분당 6회**. 여러 장은 6장씩 나눠 보낸다.
