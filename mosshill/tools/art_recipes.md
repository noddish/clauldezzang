# 그림 생성 규칙 (AI 이미지 생성 전에 반드시 읽기)

그림을 새로 만들거나 고칠 때는 **이 파일대로** 견본을 넣고 프롬프트를 쓴다.
견본을 빼먹거나 프롬프트를 짧게 쓰면 화풍·얼굴·크기가 달라진다 (아래 '실패 기록').

## 1. 견본 목록 (이미지 서버 id)

| 이름 | id | 용도 |
|---|---|---|
| **화풍 기준 — 루비** | `img_mwjcm7u5W3q5maZ1` | 모든 인물·장면 그림에 넣는다. 확정된 얼굴(5번) |
| **배경 화풍 기준 — 길드 홀** | `img_mwjzz6ejUwIEo3A9` | 모든 배경에 넣는다 |
| 카이 | `img_mwk04ey99961j7GF` | 몸 (오른쪽을 봄) |
| 마르타 (예전) | `img_mwk04p3zc4tZ1Zln` | 루비와 닮아서 교체 예정 |
| 마르타 새 후보 A / B / C | `img_mwk3t4rvcZF5sLeh` / `img_mwk3tedn5xGs0gof` / `img_mwk3tqbznKRo5MH0` | A 은퇴한 모험가 / B 푸근한 아줌마 / C 키 큰 무뚝뚝한 사장 |
| 핍 | `img_mwk04yuwDl5LkiiB` | 몸 (전신, 작게) |
| 그레고르 | `img_mwk05a0vTrlhPirv` | 몸. 이 화풍에서 **나이(주름)를 그리는 법**의 견본 |
| 배경: 내 방 / 부엌 / 길드 앞 | `img_mwk00f9bvTm6XvLx` / `img_mwk00ppuKfGbnYrw` / `img_mwk010ifbr0lNxiK` | |
| 배경: 광장 / 선술집 / 잡화점 | `img_mwk01cc9WcxxfKxh` / `img_mwk01nibyD82wGX9` / `img_mwk020slS8bQPtdR` | |
| 배경: 숲 / 동굴1 / 동굴2 / 지도 | `img_mwk02c108Sm3wYz9` / `img_mwk02mmcAUfpVboO` / `img_mwk02zsd7TnAykBH` / `img_mwk03bkheoQNSpy0` | |
| 장면(하던 일): 부엌 루비 / 홀 루비 | `img_mwk2b8ltoHvj1Qh2` / `img_mwk28cebpXWz68CU` | |
| 장면(하던 일): 선술집 마르타 / 잡화점 핍 / 광장 핍 | `img_mwk337koGb2kM4Zu` / `img_mwk33ey2wlWuSMdW` / `img_mwk33ndtudBcVSua` | |

## 2. 그림 종류별로 꼭 넣을 견본 (images 순서 = 역할)

첫 번째 그림이 고칠 대상이다. 프롬프트에 **몇 번째 그림이 무슨 역할인지** 반드시 적는다.

| 만들 것 | 1번 (고칠 대상) | 2번 이후 (견본) |
|---|---|---|
| 새 인물 몸 (처음부터) | 루비 = 화풍만 | (2) 비슷한 나이의 기존 인물 = 그 나이를 그리는 법 (예: 나이 든 인물이면 그레고르) |
| 인물 얼굴 다시 디자인 | 그 인물 몸 | (2) 루비 = 화풍 (3) 그레고르 = 나이 표현 (나이 든 인물일 때) |
| 표정 | 그 인물 몸 | (2) 루비 = 화풍 — 얼굴 크기·위치는 1번 그대로 |
| 배경 | 길드 홀 | (2) 루비 = 화풍 |
| 장면에 인물 넣기 | 그 장소 배경 | (2) 그 인물 몸 = 얼굴·옷 (3) 루비 = 화풍 |
| 장면 인물 시선만 바꾸기 | 그 장면 그림 | (2) 그 인물 몸 = 얼굴 (3) 루비 = 화풍 |
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
| 장면 인물이 고개를 들 때 머리가 10~20% 커지고 인상이 바뀜 | 머리를 통째로 다시 그리게 함 | 머리는 그대로, **눈과 입만** 바꾼다 |
| 장면 인물이 빤히 쳐다봐서 무서움 | "카메라를 정면으로 보라" | 편안한 눈꺼풀, 살짝 치켜뜬 눈길, 작은 미소 |
| 장면 인물 눈 색이 바뀜 | 인물 견본 없이 얼굴을 다시 그림 | 인물 몸을 2번 견본으로 넣는다 |
| 영역 지정(마스크) 편집 실패 | 이미지 서버가 마스크를 거부 ("Invalid image data") | 마스크 없이 "~만 바꿔"로 그리고 `art_pipeline.py` 가 바뀐 곳만 오린다 |
