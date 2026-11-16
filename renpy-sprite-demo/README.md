# 조립형 캐릭터 + 모션 데모 (Ren'Py 8)

Summertime Saga 구조 분석(`../docs/summertime-saga-structure-analysis.md`)에서 배운
**layeredimage(조각 겹치기) + ATL(코드로 움직이기)** 방식을 직접 실습하는 예제입니다.
그림은 전부 코드로 그린 임시 그림이라, 실제 그림이 생기면 **같은 파일 이름으로 덮어쓰기만** 하면 됩니다.

## 실행

1. [Ren'Py SDK](https://www.renpy.org/latest.html) 설치 (8.x)
2. 런처 → 설정의 "프로젝트 폴더"를 이 저장소 폴더로 지정 → `renpy-sprite-demo` 선택 → **프로젝트 실행**

설치 없이 보려면 `web_demo.html`을 브라우저로 여세요. (같은 그림·같은 동작을 웹으로 흉내 낸 것)

## 파일 구성

| 파일 | 내용 |
|---|---|
| `game/sprites.rpy` | ★ 조립형 캐릭터 정의 (layeredimage), 눈 깜빡임, 말할 때 입 움직임 |
| `game/motions.rpy` | ★ 움직임 모음 (깡충, 끄덕, 부들부들, 등장/퇴장, 클로즈업, 피격, 회복 …) |
| `game/script.rpy` | 데모 대본 — 메뉴에서 ①~⑥ 골라 보기 |
| `game/battle.rpy` | 미니 턴제 전투 (계산=Python 클래스, 선택=screen, 연출=transform) |
| `game/images/hero/` | 캐릭터 조각 20장 — **전부 600×720 투명 캔버스** |
| `game/images/enemy/`, `bg/` | 슬라임, 배경 |
| `game/fonts/` | 나눔고딕 (한글 표시용, SIL OFL) |
| `tools/make_placeholder_art.py` | 임시 그림 생성 스크립트 |
| `tools/build_web_demo.py` | `web_demo.html` 생성 스크립트 |

## 그림을 직접 만들 때 규칙 (가장 중요)

1. **모든 조각을 같은 크기 캔버스에 그린다.** (예: 600×720, 투명 배경)
   Krita/포토샵에서 레이어를 나눠 그리고, 레이어마다 *캔버스 전체 크기 그대로* PNG로 내보낸다. 잘라내지 않는다.
2. **파일 이름 = `캐릭터_그룹_속성.png`**
   `hero_body_tunic.png`, `hero_arms_sword.png`, `hero_eyes_happy.png` …
3. **레이어 순서(아래→위):** 몸 → 팔 → 눈썹 → 눈 → 입 → 덧씌우기(볼터치, 땀 …)
4. 표정은 통째로 그리지 말고 **눈썹·눈·입을 따로** 그린다. 조각 13장 → 표정 수십 가지.

## 대본에서 쓰는 법

```renpy
show hero                                   # 기본 모습
show hero happy_eyes smile blush            # 기쁨
show hero angry_brows frown at stage_center, shiver   # 화남 + 부들부들
show hero armor a_sword                     # 장비 교체
show hero -blush                            # 볼터치 끄기
h happy_eyes smile "대사와 표정을 한 줄로!"  # 말하는 동안 입은 자동으로 움직임
```
