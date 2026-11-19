# Summertime Saga 0.20.16 구조 분석 — 턴제 RPG 설계 참고용

> 목적: 에셋/코드를 가져다 쓰는 것이 아니라 **구조를 배우기 위한** 분석 노트.
> 원본은 컴파일된 `.rpyc`만 포함되어 있어, 실행 없이 구조만 복원하는 자체 해석기로 1,625개 파일(약 28만 줄)을 복원해 읽었다.
> 성인 콘텐츠는 다루지 않고 시스템 구조만 정리했다. 아래 코드 예시는 구조 설명을 위해 단순화한 발췌다.

## 규모 (Ren'Py 7.3.5)

| 항목 | 수량 |
|---|---|
| 스크립트 파일 | 1,625개 |
| label(장면 단위) | 5,633개 |
| screen(화면) | 572개 |
| 선택지(menu) | 404개 |
| 퀘스트 트리거 호출 | 967곳 |
| 이미지 | 19,573장 (캐릭터 14,410 · 배경 1,999 · 오브젝트 1,523) |
| 오디오 | 70개 |
| 아이템 | 219개 |

---

## 1. 전체 폴더 구조

```
SummertimeSaga/
├─ SummertimeSaga.exe / .sh / .py   ← 실행 파일 (Ren'Py 런처)
├─ renpy/  lib/                     ← 엔진 본체
└─ game/
   ├─ scripts.rpa   (27MB)   스크립트 묶음
   ├─ images.rpa    (1.03GB) 이미지 묶음
   ├─ audio.rpa     (111MB)  음악·효과음
   ├─ data.rpa / fonts.rpa   JSON 데이터, 폰트
   └─ cache/, legal/, changelog.txt …
```

`.rpa`는 배포용으로 파일을 묶은 아카이브. 개발 중에는 일반 폴더로 둔다.

### scripts 내부

```
scripts/
├─ script.rpy           시작점 (스플래시, 메인메뉴, 세이브 로드 후처리)
├─ core/                자체 게임 시스템
│  ├─ systems/
│  │  ├─ day_timer.rpy     날짜·시간대
│  │  ├─ game.rpy          전체 관리 (잠자기, 메인 루프)
│  │  ├─ player.rpy        플레이어·인벤토리·스탯
│  │  ├─ FSM/              캐릭터별 퀘스트 상태 머신
│  │  └─ locations/        장소 트리
│  ├─ inventory/           상점, 아이템 사용 대사
│  ├─ user_interface/      HUD, 팝업, 메뉴
│  └─ variables/           default 변수 모음
├─ defines/             캐릭터·이미지·트랜지션·스타일 정의
├─ characters/<이름>/   캐릭터 1명 = 폴더 1개 (100명 이상)
│  ├─ <이름>_fsm.rpy       퀘스트 단계·전이
│  ├─ button.rpy           클릭 시 대화 분기
│  ├─ button_dialogues.rpy 대사 본문
│  ├─ layeredimage.rpy     스프라이트 조립
│  └─ dialogue/            이벤트 대사
├─ locations/<장소>/    장소 1개 = 폴더 1개
│  ├─ screens.rpy          클릭 가능한 화면
│  └─ <장소>.rpy            진입 이벤트
├─ locks/               장소 진입 조건 검사 (31개)
├─ minigames/           미니게임 34종 (combat, fishing, poker …)
└─ data/*.json          아이템, 업적, 데이트, 문자 등 데이터
```

**배울 점:** 시스템/캐릭터/장소/미니게임으로 나누고, 캐릭터·장소는 1개 = 폴더 1개. 콘텐츠가 늘어도 위치를 예측할 수 있다.

---

## 2. 스크립트 구성 방식

| 용도 | 위치 | 방식 |
|---|---|---|
| 메인 흐름 | `script.rpy` → `game_main` | 거의 비어 있음. 바로 "현재 장소 화면 띄우기"로 위임 |
| 캐릭터 대화 | `characters/X/button*.rpy` | `label X_button_dialogue:` 하나에 if/elif로 상황 분기 |
| 이벤트 | `characters/X/dialogue/`, `locations/*/` | label 단위로 쪼개고 `call` |
| 선택지 | `menu:` | `'선택지' if 조건:` |
| 변수 | `core/variables/defaults.rpy`, FSM `vars` | 전역 `default` + 캐릭터별 변수 딕셔너리 |

```renpy
define erik = Character('Erik', color='57a43b', image='erik')
define player_name = Character('[firstname]', color='ffffff')
```

```renpy
label erik_talk:
    menu:
        'Cafeteria Duty.' if L_school_cafeteria.is_here(M_erik) and M_kevin.finished_state(S_kevin_gym_tomorrow):
            call erik_cafeteria_duty
        'Lenses.' if M_okita.is_state(S_okita_get_bifocal_lenses):
            call expression game.dialog_select("button_erik_lenses")
        'Leave.':
            $ game.main()
```

선택지 노출 여부가 **다른 캐릭터의 퀘스트 상태**로 결정된다.

---

## 3. 에셋 정리 방식

### 이미지

```
images/
├─ characters/<이름>/          스프라이트 (전체의 74%)
│   ├─ char_erik_01.png, 01b …       번호 + 알파벳 변형
│   ├─ buttons/character_*.png        맵에서 클릭하는 캐릭터
│   └─ layeredimage/                  부위별 조각 (몸/팔/얼굴/옷)
├─ backgrounds/location_<장소>_<변형>.jpg   (_day, _night, _blur, _closeup)
├─ objects/          클릭 가능한 사물
├─ map/              마을 지도 + 건물 미니어처
├─ buttons/, ui/, popups/, boxes/   UI
└─ minigames/<게임명>/
```

핵심 기법:

1. **시간대 자동 치환** — `game.timer.image("objects/object_bench_02{}.png")`의 `{}`에 시간대·계절(크리스마스/할로윈) 접미사가 자동으로 들어간다. 코드는 하나, 이미지만 변형별로 추가.
2. **layeredimage** — `show anon f_worried a_backpack`처럼 얼굴/팔/옷을 조합. 구형 캐릭터는 통짜 이미지라 장수가 폭증했다 → 처음부터 layeredimage 권장.
3. **blur 배경** — 대화 중에는 `_blur` 배경으로 캐릭터 강조.

### 오디오

접두사로 분류: `ambience_*`(환경음), `music_*`(BGM), `sfx_*`(효과음).
장소↔환경음 매핑은 `data/location_sounds.json`으로 데이터 분리.

```json
"town_map":    { "ambience": "ambience_suburb.ogg", "ambience_night": "ambience_suburb_night.ogg" },
"school_hall": { "ambience": "ambience_school_hallway.ogg" }
```

---

## 4. 게임 진행 로직

### 날짜·시간 (`day_timer.rpy`)

- 하루 4칸: morning → afternoon → evening → night. 요일 0(월)~6(일).
- `game.timer.tick()` 시간대 +1 (264곳), `game.sleep()` 다음 날 아침.
- `is_morning()`, `is_dark()`, `is_weekend()`, `is_date(tod=[1,2], dow=5)`.
- 잠잘 때 일괄 처리:

```python
self.timer.sleep()
Machine.trigger(T_all_tick);  Machine.trigger(T_all_sleep)   # 모든 캐릭터에 "하루 지남"
if self.timer._dow == 0: Machine.trigger(T_all_new_week)   # 주간 이벤트
MailBoxManager.randomize_all()                              # 우편함 갱신
if self.timer._dow == 0 and player.has_item('atm_card'): player.calculate_interests()
```

→ RPG의 "하루 종료 → 회복, 상점 재고, 리스폰"에 그대로 쓸 수 있다.

### 이벤트 플래그: 캐릭터별 상태 머신 (FSM)

플래그 변수를 늘어놓는 대신 **캐릭터마다 Machine 하나**.

```python
M_erik = Machine('erik',
    default_loc=[[L_school_scienceclassroom, L_erikhouse_erikroom, L_erikhouse_erikroom, L_erikhouse_erikroom],  # 평일 시간대별
                 [L_erikhouse_erikroom, L_erikhouse_erikroom, L_erikhouse_erikroom, L_erikhouse_erikroom]],       # 주말
    vars={'card_outcome': False, 'confessed': -1})

T_erik_cards_lost  = Trigger()          # 사건
T_erik_cards_found = Trigger()

S_erik_cards_ready = State(_("I should stop by after school."))     # 단계 + 퀘스트 힌트 문구
S_erik_cards_lost  = State(_("Erik needs help finding his cards."))
S_erik_cards_found = State(_("I should return these cards to Erik."))

S_erik_cards_ready.add(T_erik_cards_lost, S_erik_cards_lost,
                       actions=('location', {'place': L_erikhouse_erikroom}))
S_erik_cards_lost.add(T_erik_cards_found, S_erik_cards_found)
```

사용:

```renpy
if M_erik.is_state(S_erik_cards_lost):
if M_erik.finished_state(S_erik_intro_done):
$ M_erik.trigger(T_erik_cards_found)
$ M_erik.set('confessed', 1)
```

장점:
- 퀘스트 힌트·NPC 위치·다음 단계가 한곳에.
- `State(delay=2)` → 잠 2번 뒤 진행.
- **세이브는 발생한 트리거 목록만 저장**하고 로드 시 재생(`fsm_data.rpy`) → 업데이트로 퀘스트가 바뀌어도 세이브가 잘 안 깨진다.

### 호감도

`data/dating.json`에 활동·선물 점수와 임계값. 하지만 실질적인 관계 진행은 FSM 단계가 담당.

### 플레이어 (`player.rpy`)

- 스탯 `str/int/dex/chr` (최대 10)
- 인벤토리 `items`, `picked_up`, `money`, `savings`, 이자
- 아이템 정의는 `items.json` → `Item("id")`

```json
{ "id": "1", "name": "Homework", "cost": "0", "image": "objects/item_homework1.png",
  "description": "...", "closeup": "", "dialogue_label": "" }
```

---

## 5. 마을 맵과 장소 시스템

### 장소 트리

```python
L_map          = Location("Town Map", locked=True)
L_school_front = Location("School Frontyard", background="school_frontyard", parents=L_map, locked=True)
L_school_hall  = Location("School Hall",      background="school",           parents=L_school_front)
L_school_floor2      = Location("School Second Floor", parents=L_school_hall)
L_school_computerlab = Location("Computer Lab",        parents=L_school_floor2)
```

### 이동 흐름

```
[클릭] action MoveTo(L_park)
   ↓
global_lock_check(destination)     ← 구역별로 분기
   ↓
park_lock_check                     ← 막아야 하면 대사 후 return True(이동 취소)
   ↓ 통과
player.go_to(L_park) → label park_dialogue   ← 도착 이벤트 검사
   ↓
game.main()                          ← 장소 screen 표시, 클릭 대기
```

### 장소 화면 = 조건부 버튼 모음

```renpy
screen park():
    add L_park.background
    imagebutton pos (318,377) idle game.timer.image("objects/object_fountain_01{}.png") action MoveTo(L_park_fountain)
    if L_park.is_here(M_eve):
        imagebutton pos (297,473) idle M_eve.get_button_path(3) action TalkTo(M_eve)
    if M_ross.is_state(S_ross_find_eve_backpack) and not player.has_picked_up_item("eve_backpack"):
        imagebutton pos (883,499) idle "objects/object_backpack_01.png" action Jump("backpack_pickup_dialogue")
```

마을 지도도 동일: `if not L_park.locked:`일 때만 건물 버튼 표시, 퀘스트의 `unlocklocation` 액션으로 해금.

### 진행 조건 = 4가지 질문의 조합

- 언제? `game.timer.is_evening()`
- 어디? `player.location == L_park`
- 누구의 몇 단계? `M_eve.is_state(...)`
- 무엇을 가졌나? `player.has_item(...)`

---

## 6. Ren'Py 기능별 실제 활용

| 기능 | 활용 |
|---|---|
| `label` | 장면 1개 = label 1개 (`park_dialogue`, `erik_button_dialogue`) |
| `jump` | 돌아오지 않는 이동 (`Jump("park_bushes_dialogue")`) |
| `call`/`return` | 하위 대사 호출 후 복귀 |
| `call expression` | label 이름 계산. `game.dialog_select(...)`로 번역 label 자동 전환 |
| `if/elif` | 퀘스트·시간·아이템 조건 |
| `menu:` | 조건부 선택지 |
| `screen` | 장소, 지도, HUD, 팝업, 미니게임 UI (572개) |
| `imagebutton` | 클릭 가능한 캐릭터·사물·건물 |
| `$`/`python:` | 상태 변경, 시스템 클래스 정의 |
| `default`/`define` | 세이브되는 변수 / 상수 |
| `scene`/`show`/`with` | 배경 / 캐릭터 / 전환 효과 |
| `init python` | 시스템 클래스(Machine, Location, DayTimer) 사전 정의 |

```renpy
label park_night_closed:
    scene expression player.location.background_blur
    show player 10
    with dissolve
    player_name "( It's getting late. I should go home. )"
    hide player
    $ game.main()
```

---

## 7. 턴제 RPG 적용 방법

### 그대로 가져올 것

1. 장소 트리 + 진입 검사(lock check) → "열쇠가 있어야 던전 입장", "밤엔 상점 닫힘"
2. 캐릭터/퀘스트별 상태 머신 → NPC·퀘스트 진행의 뼈대
3. 4칸 시간대 + 잠자기 일괄 처리 → 회복, 재고 갱신, 리스폰
4. 데이터 JSON 분리 → 아이템, 몬스터, 스킬, 상점, 드롭 테이블
5. 캐릭터 1명 = 폴더 1개, 장소 1개 = 폴더 1개

### 고쳐서 가져올 것 (원작의 약점)

- **거대한 if/elif 사슬** (`erik/button_dialogues.rpy` 1,762줄, 화면마다 타 캐릭터 조건이 얽힘) → 이벤트를 "조건 + label" 데이터로 등록
- **세이브 호환 땜질 누적** (`after_load`에 버전별 패치) → 세이브에 버전 번호, 퀘스트는 트리거 기록 방식
- **전투는 연출용 미니게임 수준** (`minigames/combat`은 HP 칸 깎기) → 전투는 별도 모듈로 설계

### 추천 구조 (Ren'Py)

```
game/
├─ core/       time.rpy · locations.rpy · quests.rpy(FSM) · events.rpy · save_migrate.rpy
├─ rpg/
│  ├─ stats.rpy          Actor (HP/MP/공/방/속, 레벨, 경험치)
│  ├─ inventory.rpy      아이템·장비 슬롯
│  ├─ battle.rpy         턴 로직 (순수 Python)
│  └─ battle_screen.rpy  전투 UI
├─ data/       items.json · monsters.json · skills.json · shops.json · encounters.json
├─ characters/<npc>/  quest.rpy · talk.rpy · sprite.rpy(layeredimage)
└─ locations/<장소>/   screen.rpy · enter.rpy · lock.rpy
```

이벤트 데이터 등록:

```python
EVENTS = [
  # 장소,    조건,                                                     label,              1회?
  ("forest", lambda: time.is_night() and Q_guard.is_state("missing"), "ev_forest_ambush", True),
  ("town",   lambda: player.level >= 5,                               "ev_guild_invite",  True),
]
def check_events(place):
    for loc, cond, label, once in EVENTS:
        if loc == place and cond() and not (once and label in seen_events):
            seen_events.add(label); renpy.call(label)
```

전투 진입:

```renpy
label forest_enter:
    $ check_events("forest")
    if renpy.random.random() < encounter_rate("forest"):
        call battle(["slime", "slime"])
        if _return == "lose":
            jump game_over
    $ game.main()

label battle(enemies):
    $ b = Battle(party, [Monster(e) for e in enemies])
    while not b.finished:
        call screen battle_ui(b)
        $ b.run_turn(_return)
    return b.result
```

전투 계산은 화면과 분리된 순수 Python으로 → 엔진 이전·자동 테스트가 쉬워진다.

---

## 8. 엔진 선택

| | Ren'Py | Godot | Unity |
|---|---|---|---|
| 대화·분기·선택지 | ◎ 기본 | △ 플러그인 (Dialogic 등) | △ 플러그인 |
| 세이브/로드·되감기 | ◎ 자동 | △ 직접 구현 | △ 직접 구현 |
| 클릭형 마을 (SS 방식) | ◎ | ○ | ○ |
| 걸어다니는 맵 | ✕ | ◎ 타일맵 | ◎ |
| 턴제 전투 | ○ 메뉴형 충분 | ◎ | ◎ |
| 연출 | △ | ◎ | ◎ |
| 비개발자 진입 장벽 | 가장 낮음 | 중간 | 높음 |
| AI 도움 효율 | ◎ 전부 텍스트 | ○ 씬도 텍스트, 에디터 작업 일부 | △ 에디터 수작업 많음 |
| 모바일·웹 | ○ | ◎ | ◎ |
| 비용 | 무료 | 무료 | 조건부 무료 |

**추천**

- **지도/장소를 클릭해 이동 (SS 방식)** → **Ren'Py 8.x**. 위 구조를 거의 그대로 이식 가능, 비개발자 + AI 조합에서 실패 확률이 가장 낮다.
- **캐릭터가 마을을 걸어다니고 전투 연출을 화려하게** → **Godot 4** (대화는 Dialogic / Dialogue Manager).
- **Unity**는 이 규모의 2D 서사형 게임에는 무겁고 AI 도움이 가장 불리 → 비추천.

기본 추천은 **Ren'Py**. 먼저 장소 3곳, NPC 2명, 퀘스트 1개, 전투 1종으로 작은 프로토타입을 만들어 엔진 적합성을 판단할 것.

---

## 9. 모스힐 적용 점검 — 원작보다 나은 방법 (2026-11-17)

원작 분석을 다시 훑어 **우리 게임에 쓸 만한 기법을 빠짐없이** 뽑고, 항목마다 "원작 그대로"보다 나은 방법이 있는지 비교했다.

### 이미 적용한 것

| 항목 | 원작 방식 | 모스힐 방식 | 나은 점 |
|---|---|---|---|
| 장소 안 인물 | 인물만 따로 그린 작은 PNG 를 고정 위치에 얹음 | 배경에 인물을 같이 그린 그림으로 크기·자세·조명을 정하고, 같은 자세로 크게 다시 그린 인물을 자동으로 겹쳐 맞춤 | 배경과 크기·조명이 맞고 얼굴은 또렷함. 가구 뒤는 잘라내고 손에 든 물건은 인물과 함께 그림 |
| 들어왔을 때 반응 | 같은 그림 그대로 | 하던 일(busy) → 0.6초 뒤 눈만 들어 앞을 봄(look) | 누가 들어온 걸 알아채는 느낌 |
| 대화 배경 | 흐린 배경 그림을 279장 따로 저장 | 실행 중에 흐리게 (`blur`) | 그림 0장 추가. 대화 상대만 배경에서 빠지고 나머지 인물은 흐리게 남음 |
| 혼잣말 주인공 | 대사마다 `show player 13` 을 손으로 (수천 번) | 대사 시작 콜백이 카이를 자동으로 왼쪽에 세움 | 빼먹을 수 없음. 혼잣말엔 입을 안 움직임 |
| 혼잣말 중 주변 | 배경만 남음 | 장소 안 인물이 그대로 있음 | 장소가 살아 있는 느낌 |
| 표정 | 표정마다 전체 그림 | 몸 1장 + 달라진 곳만 오린 얼굴 조각, 자동 깜빡임, 말할 때 입 움직임 | 그림 수가 적고 살아 있는 느낌 |
| 이벤트 | 장소 label 안의 if 사슬, 강제 이벤트는 메인 루프 곳곳 | `event(id, label, at, on, when, once, priority)` 등록부 | 어디에 무슨 이벤트가 있는지 한눈에. 1회 이벤트는 id 로 기록 → 이벤트를 추가해도 옛 세이브가 안 깨짐 |
| 연결 검사 | 없음 (label 오타가 진행을 멈춤) | 자동 검사가 이벤트·물건·인물 대화·이동 장소가 실제로 있는지 확인 | 오타를 실행 전에 잡음 |
| 폴더 | 인물 1명 = 폴더 1개 | 인물과 **장소도** 폴더 1개 (물건 목록·이벤트·클릭 대사가 한 파일) | 장소 하나 고칠 때 파일 하나만 봄 |
| 시간대별 물건 | 물건마다 낮·밤 PNG | 클릭 모양(마스크)으로 지금 배경에서 오려냄 | 배경만 바꾸면 물건 그림은 따라옴 |
| 마우스 올림 | 밝기 +0.07, 대비 ×1.07 | 색을 곱해서 밝힘 | 밤 그림이 뿌옇게 뜨지 않음 |

| 지도 장식 | 바닥 지도 위에 차 3대가 길을 달리고(낮/밤 그림), 화면만 한 구름 1장이 80초에 걸쳐 대각선으로, 굴뚝 연기·반짝임 | 크기가 다른 구름 3개가 속도를 달리해 흐르며 땅에 그림자, 갈매기 무리가 날갯짓 4장 반복으로 가끔 지나감 (방향 무작위, 밤엔 없음) | 지도를 열 때마다 구름 위치가 달라지고, 그림자로 지도가 입체적으로 보임 |

원작 지도는 **한 장이 아니다**: 건물 없는 바닥 지도 + 장소마다 따로 그린 건물 그림(클릭 버튼, 잠긴 곳은 안 그림) + 움직이는 장식.
본편에서 장소가 늘어나는 것을 생각하면 같은 구조가 맞다 (모스힐은 아직 건물까지 한 장 — 바꿀 계획).

### 계획만 세운 것

| 항목 | 원작 방식 | 모스힐 계획 | 나은 점 |
|---|---|---|---|
| 저녁·밤 그림 | 낮·저녁·밤을 따로 그림 (274 / 118 / 238장) | 저녁(불 켜짐)만 AI 로 다시 그리고, 밤은 저녁에서 계산 (불빛만 남기고 어둡게). 낮 그림에 위치 자동 맞춤 | 그림 수 절반 이하, 클릭 모양이 어긋나지 않음. 계획: `mosshill/tools/art_recipes.md` 6장 |

### 이번에 새로 찾은 것 (아직 안 함)

| 항목 | 원작 방식 | 원작보다 나은 방법 | 비용 |
|---|---|---|---|
| 지도의 잠긴 곳 | 잠긴 곳은 아예 숨김. 퀘스트에 따라 건물 그림 교체 | 흐리게 보여 주고 마우스를 올리면 잠긴 이유 (`lock_reason` 그대로 사용) | 코드만 |
| 할 일 기록 | 휴대폰 '목표' 앱: 인물별 사진 + 손으로 쓴 목표 문장 | '길드 일지' 화면 (게임 제목과 맞음): 인물 얼굴 + 퀘스트 단계를 **상태 머신에서 자동으로** 표시 | 코드만 |
| 알림 | 토스트 + 구매 때 동전 소리 | 아이콘 붙은 토스트 + 효과음 | 효과음 몇 개 (M5) |
| 물건 클로즈업 | 중요한 물건을 누르면 확대 그림 | 부싯돌·의뢰서 같은 2~3개만 | 그림 2~3장 |
| 장소 소리 | `location_sounds.json`: 장소별 환경음·음악, 반복 지점, 낮·밤 | 같은 데이터 방식 + 같은 음악이면 이어서 틀고 다르면 교차 페이드 | 무료 음원 (M5) |
| 세이브 버전 | `after_load` 에 버전별 땜질이 쌓임 | `save_version` + 이벤트·퀘스트는 id 기록이라 땜질이 거의 필요 없음 | 코드만 |
| 번역 | `dialog_select` 모드 | 대사가 `story/` 와 `characters/*/talk.rpy` 에만 있어 Ren'Py 기본 번역 기능을 바로 씀 | 구조는 이미 준비됨 |
