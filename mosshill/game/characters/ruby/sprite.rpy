## ============================================================================
## characters/ruby/sprite.rpy — 루비 그림 정의
##
## 파일 (images/characters/ruby/, 전부 480x720 같은 캔버스):
##   ruby_body.png              몸 전체 (기본 얼굴 포함)
##   ruby_face_<표정>.png       얼굴 조각 (나머지는 투명)
##
## 사용법:
##   show ruby at stage_right              기본 얼굴, 자동 깜빡임
##   show ruby happy                       표정만 교체
##   r angry "대사"                        대사와 표정을 한 줄로
##   (말하는 동안 입은 자동으로 움직임 — config.speaking_attribute)
## ============================================================================

## 기본 얼굴일 때 가끔 눈 깜빡이기
image ruby_face_idle:
    Null()
    choice:
        pause 2.5
    choice:
        pause 3.5
    choice:
        pause 5.0
    "ruby_face_blink"
    pause 0.12
    repeat

## 말할 때 입 움직임
image ruby_face_flap:
    "ruby_face_talk"
    pause 0.13
    Null()
    pause 0.11
    repeat

## 말할 때 입이 움직이는 그림은 기본 표정 1장뿐이다.
## 그래서 입 움직임은 기본 표정일 때만 쓰고, 다른 표정은 말하는 동안에도 그대로 둔다.
## (원작은 표정마다 '말하는 얼굴'을 따로 그렸다 — 필요해지면 ruby_face_<표정>_talk 를 추가)
define RUBY_FACES = ["happy", "angry", "sad", "surprised", "closed"]

layeredimage ruby:
    always "ruby_body"

    group face:
        attribute neutral default "ruby_face_idle" if_not ["speaking"]
        attribute happy     "ruby_face_happy"
        attribute angry     "ruby_face_angry"
        attribute sad       "ruby_face_sad"
        attribute surprised "ruby_face_surprised"
        attribute closed    "ruby_face_blink"

    group talking:
        attribute speaking "ruby_face_flap" if_not RUBY_FACES

define r = Character("루비", image="ruby", color="#7fe0c8")
