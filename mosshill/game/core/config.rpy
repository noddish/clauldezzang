## ============================================================================
## core/config.rpy — 게임 전체 설정
## ============================================================================

## 세이브 형식 버전. 저장 구조가 바뀌면 올리고 core/save.rpy 에서 변환한다.
define SAVE_VERSION = 1

## 대사가 나오는 동안 말하는 캐릭터에 'speaking' 속성을 자동으로 붙인다 (입 움직임)
define config.speaking_attribute = "speaking"

## 개발 중에만 켜는 기능
define config.developer = "auto"


## ---------------------------------------------------------------- 임시 그림
## M3(아트) 전까지 배경 대신 쓰는 회색 박스. 장소 이름이 가운데에 찍힌다.
init python:
    def Placeholder(label, color="#4a4f5c"):
        return Fixed(
            Solid(color),
            Text(label, size=48, color="#ffffff88", xalign=0.5, yalign=0.45),
            Text("임시 배경", size=22, color="#ffffff55", xalign=0.5, yalign=0.55),
        )
