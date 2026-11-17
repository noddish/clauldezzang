## ============================================================================
## characters/gregor/sprite.rpy — 그레고르 그림 — 모험가 협회 감사관
## ============================================================================

## 파일 images/characters/gregor/ (480x720 같은 캔버스 — 루비와 같은 방식):
##   gregor_body.png 몸 (기본 얼굴) / gregor_face_<표정>.png 얼굴 조각 / gregor_face_talk.png 입만 벌린 것 (말할 때)
## 입 움직임은 기본 표정일 때만 (루비와 같은 규칙).

init -20 python:
    CHAR_NAMES["gregor"] = "그레고르"

image gregor_face_flap:
    "gregor_face_talk"
    pause 0.14
    Null()
    pause 0.12
    repeat

layeredimage gregor:
    always "gregor_body"
    group face:
        attribute neutral default Null()
        attribute happy "gregor_face_happy"
        attribute angry "gregor_face_angry"
    group talking:
        attribute speaking "gregor_face_flap" if_not ["happy", "angry"]

define g = Character("그레고르", image="gregor", color="#9fb4e8")
