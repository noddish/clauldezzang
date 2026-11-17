## ============================================================================
## characters/player/player.rpy — 주인공 (기본 이름 카이)
## 그림: images/characters/kai/ — 480x720, 3/4 측면, 오른쪽을 바라봄 (NPC 는 왼쪽을 봄).
## 대화에서는 왼쪽에 서서 오른쪽 상대를 본다.
## 카이가 말하거나 생각할 때(me / think) 카이가 화면에 없으면 저절로 왼쪽에 나타난다.
## 원작은 혼잣말마다 'show player 14' 를 손으로 적었다(수천 곳) — 여기서는 빠뜨릴 수 없게 자동.
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
default kai_auto_show = True        # 연출상 카이를 안 보이게 할 장면에서만 False

transform kai_appear:
    stage_left
    alpha 0.0
    linear 0.2 alpha 1.0

init -1 python:
    def kai_on_stage(event, interact=True, **kwargs):
        """me / think 가 말하기 시작할 때 카이가 화면에 없으면 왼쪽에 세운다"""
        if event == "begin" and interact and store.kai_auto_show and not renpy.showing("kai"):
            renpy.show("kai", at_list=[kai_appear])

## 이름은 대사창에 [player_name] 으로 들어간다
define me = Character("[player_name]", image="kai", color="#ffd38a", callback=kai_on_stage)
## 생각 (괄호 독백) — 입이 움직이면 안 되므로 image 는 연결하지 않는다 (표정은 show kai sad 처럼 따로)
define think = Character("[player_name]", color="#ffd38a", what_prefix="( ", what_suffix=" )", what_italic=True,
                         callback=kai_on_stage)
## 해설
define n = Character(None, what_italic=True)
