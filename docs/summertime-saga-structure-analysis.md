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
