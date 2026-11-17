# 모스힐 길드 일지 (Ren'Py 8)

기획서: [`../docs/game-design.md`](../docs/game-design.md)

## 실행

1. [Ren'Py SDK 8.3](https://www.renpy.org/latest.html) 설치
2. 런처의 프로젝트 폴더를 이 저장소로 지정 → `mosshill` → 프로젝트 실행

## 자동 검사 (사람이 클릭하지 않고 확인)

```bash
tools/run_autotest.sh m1 /tmp/shots ~/renpy-8.3.7-sdk
```

| 테스트 | 내용 |
|---|---|
| `m0` | 데이터 상호 참조 검사, 그림 파일 검사(빠진 그림, 물건 마스크 크기, 장소 인물 그림), 인물 전원·밤 색조·마우스 올림 스크린샷 |
| `m1` | 3일 전체 자동 플레이: 메인 + 서브 2개, 잠김 규칙 3개, 강제 감사 → 실적 4/4 |
| `m1_lazy` | 아무 의뢰도 안 하고 잠만 잤을 때 → 3일차 감사가 강제로 열리고 0/4 |
| `m2` | m1 경로를 진짜 전투로 + 상점 구매, 소지품 화면, 경험치·레벨 검사 |
| `m2_lose` | HP 1 로 보스전 → 패배 처리 (길드에서 깨어남, 골드 절반, HP 절반) |
| `ui` | 소지품·장비·상점 화면: 장착, 회복약 사용, 판매 + 스크린샷 |

전부 한 번에 (실패가 하나라도 있으면 exit 1):

```bash
tools/run_all_tests.sh /tmp/test-results ~/renpy-8.3.7-sdk
```

Ren'Py 없이 도는 검사:

```bash
python3 tools/test_engine.py        # 전투 엔진 단위 테스트 (피해 공식, 방어, 약점, 독, 도발, 레벨업 …)
python3 tools/balance_sim.py 5000   # 밸런스 시뮬레이터 → 결과는 docs/balance_report.txt
```

- 문법 검사(lint) → 가상 화면에서 게임 실행 → 스크린샷과 `autotest.log` 를 `/tmp/shots` 에 저장.
- Linux 는 `xvfb-run` 이 필요하다. 테스트 내용은 `game/dev/autotest.rpy` 의 `label autotest_<이름>`.
- `game/dev/` 는 배포판에서 빠진다.

## 진행 상황

| 단계 | 상태 |
|---|---|
| M0 뼈대 (폴더, 루비, 데이터 틀, 자동 검사) | 완료 |
| M1 마을 시스템 (시간, 장소, 지도, 잠김 규칙, 퀘스트 4개, HUD, 자동 플레이어) | 완료 — 임시 회색 배경 |
| M2 전투 시스템 (파티 턴제, 스킬·상태이상, 레벨업, 장비, 소지품·상점 화면, 밸런스 시뮬레이터) | 완료 — 임시 그림 |
| M3 아트 (배경 11, 인물 4 + 표정 16, 장소 안 인물 5, 적 4, 아이콘 16, 클릭 모양 31) | 완료 — 그림 생성 약 $2.3 |
| M4 이야기 | |
| M5 다듬기 | |

## 폴더

| 폴더 | 내용 |
|---|---|
| `game/core/` | 설정, 데이터 로더, 시간, 장소·메인 루프·대화 배경(`location.rpy`), 이벤트 등록부(`events.rpy`), 잠김 규칙, 퀘스트 머신, 신뢰도 |
| `game/locations/<장소>/` | 장소 1곳 = 파일 1개: 등록(`place`), 클릭할 물건, 그 장소의 인물 자리, 물건 클릭 대사, 그 장소 이벤트. 장소 트리는 `map/map.rpy` |
| `game/rpg/` | 파티, 전투 화면·연출, 소지품·장비 화면, 상점 |
| `game/python-packages/mhrpg/` | 전투·성장 계산 엔진 (순수 파이썬 — 게임과 시뮬레이터가 같이 씀) |
| `game/ui/` | 모션(ATL), HUD |
| `game/characters/<인물>/` | 인물 1명 = 폴더 1개: 그림(`sprite.rpy`), 퀘스트 머신·위치표(`quest.rpy`), 대화(`talk.rpy`). 주인공은 `player/` (혼잣말 때 자동 등장) |
| `game/story/` | 1일차 도입, 메인 퀘스트(`main_quest.rpy`), 3일차 감사(`day3.rpy`) |
| `game/data/` | 아이템·스킬·적·조우표·상점·레벨업 표 (JSON) |
| `game/dev/` | 자동 검사(`autotest.rpy`), 자동 플레이어(`autodrive.rpy`) |
| `tools/` | 자동 검사 실행, 엔진 테스트, 밸런스 시뮬레이터, 그림 가공(`art_pipeline.py`), 클릭 모양(`art_objects.json`) |

## 에셋

모든 그림은 AI 로 생성했고, 루비(`game/images/characters/ruby/`)를 **화풍 기준**으로 같이 넣어 만들었다.

| 폴더 | 내용 |
|---|---|
| `images/bg/` | 배경 11곳 `bg_<장소>_day.jpg` (+ `_night.jpg` — 낮 그림을 어둡고 푸르게 보정) |
| `images/characters/<이름>/` | 몸 `<이름>_body.png` + 표정 조각 `<이름>_face_<표정>.png` (480×720 같은 캔버스) |
| `images/enemies/` | `enemy_<종류>.png` (바닥 정렬) |
| `images/items/` | `icon_<아이템>.png` (96×96) |
| `images/objects/` | 클릭할 물건 모양 `mask_<장소>_<물건>.png` |
| `images/scenes/` | 장소 안 인물 `scene_<장소>_<인물>_<busy\|look>_<day\|night>.png` + 클릭 모양 `mask_scene_<장소>_<인물>.png` |

원본(서버에서 받은 큰 PNG)은 저장소에 넣지 않는다. 원본 폴더를 정해 두고 가공만 다시 할 수 있다:

```bash
python3 tools/art_pipeline.py <원본폴더> all       # bg sprite face enemy icon object scene
python3 tools/art_pipeline.py <원본폴더> object    # 클릭 모양만 (tools/art_objects.json 을 고친 뒤)
```

- 표정: AI 에게 "표정만 바꿔서" 다시 그리게 하면 그림이 조금 밀리거나 커져서 나온다.
  `face` 단계가 원본과 위치·크기를 맞춘 뒤 이마~턱 상자 안에서 **달라진 곳(눈썹·눈·입, 원래 눈썹 자리 포함)만**
  오려내서 경계선이 보이지 않는다. 몸+조각이 표정 그림과 덩어리로 다르면(눈썹이 두 개 남는 등) `확인 필요` 를 찍는다.
- 핍은 전신으로 작게 그려져서 `frame` 으로 1.3배 키우고 허벅지에서 자른다 (머리는 다른 인물보다 낮게 → 키 작은 하플링).
- 장소 안 인물 (원작처럼 대화용 큰 그림 대신 그 장소에서 뭔가 하는 모습) — **두 방식을 합친 것**:
  1) AI 에게 배경에 인물을 함께 그리게 한다 → 크기·비율·자세·조명이 자연스럽지만 얼굴이 작게 뭉개진다.
  2) 1) 을 견본으로 넣고 **같은 자세·비율의 인물만** 크게 다시 그린다 → 얼굴이 또렷하다 (원작처럼 인물만 따로 있는 그림).
  `scene` 단계가 2) 를 1) 의 인물 실루엣에 자동으로 겹쳐 맞추고(배율·위치), 1) 의 색감을 옮기고, 가구 뒤는 잘라낸다.
  외곽선은 두르지 않는다. 장면별 값은 `tools/art_scenes.json` 의 `place`. 클릭 모양은 인물 실루엣에서 자동으로 만든다.
  하던 일(`busy`)과 눈만 들어 앞을 보는 모습(`look`) 두 장 — 장소에 들어가면 busy 에서 look 으로 바뀐다.
- 밤(저녁·밤)에는 인물에도 푸른 색조를 입힌다 (`motions.rpy` 의 `light_matrix`).
- 마우스를 올리면 색을 몇 배로 곱해 밝힌다 (밝기를 더하면 밤 그림이 뿌옇게 뜸, `location.rpy` 의 `hover_matrix`).

## 밸런스 (M2 기준, `docs/balance_report.txt`)

| 준비 정도 | 두꺼비 왕 승률 |
|---|---|
| 서브 퀘스트 없음 | 약 63% |
| 창고 서브만 | 약 84% |
| 서브 둘 다 (불꽃베기 해금) | 약 95% |
| 서브 둘 다 + 회복약 2 | 약 97% |

일반 전투는 승률 100%, 이겼을 때 남은 HP 65~88%. 수치는 `game/data/*.json` 에서 고치고 시뮬레이터로 확인한다.
