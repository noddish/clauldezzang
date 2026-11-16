# 모스힐 길드 일지 (Ren'Py 8)

기획서: [`../docs/game-design.md`](../docs/game-design.md)

## 실행

1. [Ren'Py SDK 8.3](https://www.renpy.org/latest.html) 설치
2. 런처의 프로젝트 폴더를 이 저장소로 지정 → `mosshill` → 프로젝트 실행

## 자동 검사 (사람이 클릭하지 않고 확인)

```bash
tools/run_autotest.sh m0 /tmp/shots ~/renpy-8.3.7-sdk
```

- 문법 검사(lint) → 가상 화면에서 게임 실행 → 스크린샷과 `autotest.log` 를 `/tmp/shots` 에 저장.
- Linux 는 `xvfb-run` 이 필요하다. 테스트 내용은 `game/dev/autotest.rpy` 의 `label autotest_<이름>`.
- `game/dev/` 는 배포판에서 빠진다.

## 진행 상황

| 단계 | 상태 |
|---|---|
| M0 뼈대 (폴더, 루비, 데이터 틀, 자동 검사) | 완료 |
| M1 마을 시스템 | |
| M2 전투 시스템 | |
| M3 아트 | |
| M4 이야기 | |
| M5 다듬기 | |

## 폴더

| 폴더 | 내용 |
|---|---|
| `game/core/` | 설정, 데이터 로더, (M1) 시간·장소·퀘스트 |
| `game/rpg/` | (M2) 스탯·전투·인벤토리 |
| `game/ui/` | 모션(ATL), (M1) HUD |
| `game/characters/<인물>/` | 그림 정의, 퀘스트, 대사 |
| `game/story/` | 날짜별 대본 |
| `game/data/` | 아이템·스킬·적·조우표·상점·레벨업 표 (JSON) |
| `game/dev/` | 자동 검사 |
| `tools/` | 자동 검사 실행 스크립트 등 |

## 에셋

- 루비: `game/images/characters/ruby/` — 몸 1장 + 표정 6장 (480×720). 이 프로젝트의 **화풍 기준**.
- 그 외 그림은 M3 에서 기획서 7장 목록대로 만든다. 그 전에는 회색 임시 배경(`Placeholder`)을 쓴다.
