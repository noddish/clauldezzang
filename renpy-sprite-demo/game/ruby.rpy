## ============================================================================
## ruby.rpy — AI로 그린 미국 카툰풍 캐릭터 "루비"
## ============================================================================
##
## 만든 방법 (tools/AI_ART_WORKFLOW.md 참고)
##   1) AI 이미지 생성으로 전신 기본 그림 1장 (투명 배경, 무표정, 차렷)
##   2) "얼굴 부분만 다시 그리기"(마스크 편집)로 표정 6장 생성
##      → 몸·머리·옷은 그대로라서 얼굴 조각만 겹치면 된다
##   3) 전부 같은 캔버스(480x720)로 맞춰 저장
##
## 레온(sprites.rpy)은 눈썹·눈·입을 따로 나눴지만,
## 루비는 "얼굴 통째로 1장 = 표정 1개" 방식이다.
##   - 장점: AI로 만들기 쉽고, 표정이 자연스럽다
##   - 단점: 표정 수만큼 얼굴 그림이 필요하다 (조합은 불가)
## 실제 게임에서는 이 방식이 가장 현실적인 출발점이다.
##
## 파일:
##   images/ruby/ruby_body_base.png       몸 전체 (기본 얼굴 포함)
##   images/ruby/ruby_face_happy.png      얼굴 조각 (나머지는 투명)
##   images/ruby/ruby_face_angry.png ...
## ============================================================================


## 눈 깜빡임: 기본 얼굴(몸 그림에 포함) ↔ 눈 감은 얼굴
image ruby_face_neutral_blink:
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

## 말할 때: 기본 얼굴 ↔ 입 벌린 얼굴
image ruby_face_flap:
    "ruby_face_talk"
    pause 0.13
    Null()
    pause 0.11
    repeat


layeredimage ruby:

    always "ruby_body_base"                 # 항상 깔리는 몸 (기본 얼굴 포함)

    group face if_not ["speaking"]:
        attribute neutral default "ruby_face_neutral_blink"   # 기본 = 자동 깜빡임
        attribute happy     "ruby_face_happy"
        attribute angry     "ruby_face_angry"
        attribute sad       "ruby_face_sad"
        attribute surprised "ruby_face_surprised"
        attribute closed    "ruby_face_blink"

    group talking:
        attribute speaking "ruby_face_flap"   # 대사 중 자동 (config.speaking_attribute)


define r = Character("루비", image="ruby", color="#7fe0c8")


transform ruby_center:
    xcenter 0.5 yalign 1.0
transform ruby_left:
    xcenter 0.28 yalign 1.0
transform ruby_right:            # 원작 배치: 상대 캐릭터는 오른쪽, 주인공(왼쪽)을 바라봄
    xcenter 0.7 yalign 1.0


label demo_ruby:
    scene bg_town_day
    show ruby at ruby_center, slide_in_right
    with dissolve

    r "안녕! 나는 AI로 그린 미국 카툰 스타일 캐릭터, 루비야."
    r happy "기쁠 때는 이렇게!"
    show ruby happy at ruby_center, double_hop
    r "표정 바꾸기는 레온이랑 똑같이 'show ruby happy' 한 줄이야."

    show ruby angry at ruby_center, shiver
    r angry "화나면 이렇게 부들부들."

    show ruby sad at ruby_center, droop
    r sad "슬플 땐 살짝 가라앉고 어두워지고…"

    show ruby surprised at ruby_center, back_to_normal, hop
    r surprised "깜짝이야!"
    with vpunch

    show ruby neutral at ruby_center, breathing
    r neutral "가만히 있으면 숨쉬고, 가끔 눈도 깜빡여. 말할 땐 입도 저절로 움직이고."
    r "모션 코드는 레온이 쓰던 motions.rpy 를 그대로 같이 써. 그림만 바꾸면 되는 거지."

    show ruby at ruby_left, attack_lunge(220)
    pause 0.4
    show ruby happy at ruby_center, nod
    r happy "전투 모션도 똑같이 쓸 수 있어!"
    jump demo_menu
