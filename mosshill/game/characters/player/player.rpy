## ============================================================================
## characters/player/player.rpy — 주인공 (기본 이름 카이)
## 그림: images/characters/kai/ — 480x720, 3/4 측면, 오른쪽을 바라봄 (NPC 는 왼쪽을 봄).
## 대화 장면에서는 보통 안 보이고(1인칭), 전투와 특별한 장면에서 쓴다.
## ============================================================================

image kai_face_flap:
    "kai_face_talk"
    pause 0.13
    Null()
    pause 0.11
    repeat

layeredimage kai:
    always "kai_body"
    group face:
        attribute neutral default Null()
        attribute happy     "kai_face_happy"
        attribute surprised "kai_face_surprised"
        attribute sad       "kai_face_sad"
        attribute angry     "kai_face_angry"
    group talking:
        attribute speaking "kai_face_flap" if_not ["happy", "surprised", "sad", "angry"]

default player_name = "카이"

## 이름은 대사창에 [player_name] 으로 들어간다
define me = Character("[player_name]", image="kai", color="#ffd38a")
## 생각 (괄호 독백)
define think = Character("[player_name]", color="#ffd38a", what_prefix="( ", what_suffix=" )", what_italic=True)
## 해설
define n = Character(None, what_italic=True)
