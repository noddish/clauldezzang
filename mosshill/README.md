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
| `m0` | 데이터 파일 상호 참조 검사, 루비 표정·입 움직임 |
| `m1` | 3일 전체 자동 플레이: 메인 + 서브 2개, 잠김 규칙 3개, 강제 감사 → 실적 4/4 |
| `m1_lazy` | 아무 의뢰도 안 하고 잠만 잤을 때 → 3일차 감사가 강제로 열리고 0/4 |

- 문법 검사(lint) → 가상 화면에서 게임 실행 → 스크린샷과 `autotest.log` 를 `/tmp/shots` 에 저장.
- Linux 는 `xvfb-run` 이 필요하다. 테스트 내용은 `game/dev/autotest.rpy` 의 `label autotest_<이름>`.
- `game/dev/` 는 배포판에서 빠진다.

## 진행 상황

| 단계 | 상태 |
|---|---|
| M0 뼈대 (폴더, 루비, 데이터 틀, 자동 검사) | 완료 |
| M1 마을 시스템 (시간, 장소, 지도, 잠김 규칙, 퀘스트 4개, HUD, 자동 플레이어) | 완료 — 임시 회색 배경 |
| M2 전투 시스템 | |
| M3 아트 | |
| M4 이야기 | |
| M5 다듬기 | |

## 폴더

| 폴더 | 내용 |
|---|---|
| `game/core/` | 설정, 데이터 로더, 시간, 장소·메인 루프, 잠김 규칙, 퀘스트 머신, 신뢰도 |
| `game/locations/` | 장소 트리·물건 목록(`world.rpy`), 진입 이벤트·물건 클릭(`events.rpy`) |
| `game/rpg/` | 소지품·골드, 전투 임시판 (M2 에서 파티 턴제) |
| `game/ui/` | 모션(ATL), HUD |
| `game/characters/` | 루비 그림, NPC 임시 그림(`npcs.rpy`), 대화(`talk.rpy`), 주인공 |
| `game/story/` | 1일차 도입, 퀘스트 단계·NPC 위치표(`quests.rpy`) |
| `game/data/` | 아이템·스킬·적·조우표·상점·레벨업 표 (JSON) |
| `game/dev/` | 자동 검사(`autotest.rpy`), 자동 플레이어(`autodrive.rpy`) |
| `tools/` | 자동 검사 실행 스크립트 등 |

## 에셋

- 루비: `game/images/characters/ruby/` — 몸 1장 + 표정 6장 (480×720). 이 프로젝트의 **화풍 기준**.
- 그 외 그림은 M3 에서 기획서 7장 목록대로 만든다. 그 전에는 회색 임시 배경(`Placeholder`)을 쓴다.
