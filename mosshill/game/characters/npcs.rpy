## ============================================================================
## characters/npcs.rpy — 마르타, 핍, 그레고르
##
## 파일 (images/characters/<이름>/, 전부 480x720 같은 캔버스 — 루비와 같은 방식):
##   <이름>_body.png            몸 전체 (기본 얼굴 포함)
##   <이름>_face_<표정>.png     얼굴 조각 (바뀐 부분만, 나머지는 투명)
##   <이름>_face_talk.png       기본 얼굴에서 입만 벌린 것 → 말할 때 입 움직임
##
## 핍은 키가 작아서 캔버스 아래쪽 60% 에 전신이 들어 있다 (그래서 같은 위치에 세워도 작게 보인다).
## ============================================================================

init -40 python:
    def PlaceholderSprite(name, color, height=640):
        """480x720 캔버스 바닥에 붙은 실루엣 + 이름 (그림이 없는 인물용 임시)"""
        body = Frame(Solid(color), 0, 0)
        return Fixed(
            Transform(body, xsize=300, ysize=height, xalign=0.5, yalign=1.0),
            Transform(Solid(color), xsize=150, ysize=150, xalign=0.5, ypos=720 - height - 120),
            Text(name, size=34, color="#ffffff", xalign=0.5, ypos=720 - height + 60),
            Text("임시", size=20, color="#ffffffaa", xalign=0.5, ypos=720 - height + 104),
            xysize=(480, 720),
        )

## 말할 때 입 움직임 (기본 표정일 때만 — 루비와 같은 규칙)
image martha_face_flap:
    "martha_face_talk"
    pause 0.13
    Null()
    pause 0.11
    repeat

image pip_face_flap:
    "pip_face_talk"
    pause 0.13
    Null()
    pause 0.11
    repeat

image gregor_face_flap:
    "gregor_face_talk"
    pause 0.14
    Null()
    pause 0.12
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

layeredimage pip:
    always "pip_body"
    group face:
        attribute neutral default Null()
        attribute happy     "pip_face_happy"
        attribute sad       "pip_face_sad"
        attribute surprised "pip_face_surprised"
    group talking:
        attribute speaking "pip_face_flap" if_not ["happy", "sad", "surprised"]

layeredimage gregor:
    always "gregor_body"
    group face:
        attribute neutral default Null()
        attribute happy "gregor_face_happy"
        attribute angry "gregor_face_angry"
    group talking:
        attribute speaking "gregor_face_flap" if_not ["happy", "angry"]

define m = Character("마르타", image="martha", color="#e8a87c")
define p = Character("핍", image="pip", color="#a8d86a")
define g = Character("그레고르", image="gregor", color="#9fb4e8")
