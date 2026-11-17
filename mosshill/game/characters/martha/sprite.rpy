## ============================================================================
## characters/martha/sprite.rpy — 마르타 그림 — 선술집 '졸린 곰' 주인 (28세, 콘셉트 01 레나)
## ============================================================================

## 파일 images/characters/martha/ (480x720 같은 캔버스 — 루비와 같은 방식):
##   martha_body.png 몸 (기본 얼굴) / martha_face_<표정>.png 얼굴 조각 / martha_face_talk.png 입만 벌린 것 (말할 때)
## 입 움직임은 기본 표정일 때만 (루비와 같은 규칙).

init -20 python:
    CHAR_NAMES["martha"] = "마르타"

image martha_face_flap:
    "martha_face_talk"
    pause 0.13
    Null()
    pause 0.11
    repeat

layeredimage martha:
    always "martha_body"
    group face:
        attribute neutral default Null()
        attribute happy     "martha_face_happy"
        attribute angry     "martha_face_angry"
        attribute surprised "martha_face_surprised"
    group talking:
        attribute speaking "martha_face_flap" if_not ["happy", "angry", "surprised"]

define m = Character("마르타", image="martha", color="#e8a87c")
