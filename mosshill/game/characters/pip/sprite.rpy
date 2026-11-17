## ============================================================================
## characters/pip/sprite.rpy — 핍 그림 — 하플링 잡화점 주인
## ============================================================================

## 파일 images/characters/pip/ (480x720 같은 캔버스 — 루비와 같은 방식):
##   pip_body.png 몸 (기본 얼굴) / pip_face_<표정>.png 얼굴 조각 / pip_face_talk.png 입만 벌린 것 (말할 때)
## 입 움직임은 기본 표정일 때만 (루비와 같은 규칙).

## 하플링이라 키가 작다: 원본을 1.3배 키워 허벅지에서 자르되 머리는 다른 인물보다 낮게 (tools/art_pipeline.py frame).

init -20 python:
    CHAR_NAMES["pip"] = "핍"

image pip_face_flap:
    "pip_face_talk"
    pause 0.13
    Null()
    pause 0.11
    repeat

layeredimage pip:
    always "pip_body"
    group face:
        attribute neutral default Null()
        attribute happy     "pip_face_happy"
        attribute sad       "pip_face_sad"
        attribute surprised "pip_face_surprised"
    group talking:
        attribute speaking "pip_face_flap" if_not ["happy", "sad", "surprised"]

define p = Character("핍", image="pip", color="#a8d86a")
