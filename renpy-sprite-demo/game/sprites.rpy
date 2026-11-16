## ============================================================================
## sprites.rpy — 조립형 캐릭터 (layeredimage)
## ============================================================================
##
## [핵심 규칙]
## 1. 모든 조각 이미지는 "같은 크기(600x720)의 투명 캔버스"에 그린다.
##    → 겹치기만 하면 위치가 딱 맞는다. 좌표를 맞출 필요가 없다.
## 2. 파일 이름 규칙:  캐릭터_그룹_속성.png
##       images/hero/hero_body_tunic.png   →  그룹 body,  속성 tunic
##       images/hero/hero_eyes_happy.png   →  그룹 eyes,  속성 happy
##    Ren'Py는 images 폴더 안의 파일을 자동으로 이미지로 등록한다(하위 폴더 무관).
## 3. 같은 그룹 안에서는 하나만 보인다. (표정 smile 을 켜면 frown 은 자동으로 꺼짐)
##
## 사용 예:
##     show hero                              # 기본 상태 (default 로 지정한 것들)
##     show hero smile                        # 입만 웃는 입으로 교체 (나머지 그대로)
##     show hero angry_brows frown a_crossed  # 여러 부위를 한 번에 교체
##     show hero -blush                       # 앞에 - 를 붙이면 그 속성을 끔
##
## 실제 그림이 생기면 같은 파일 이름으로 덮어쓰기만 하면 된다. 코드는 그대로.
## ============================================================================


## ---------------------------------------------------------------- 움직이는 조각
## 눈 깜빡임: '뜬 눈'과 '감은 눈' 두 장만 있으면 된다.
## choice 로 깜빡이는 간격을 랜덤하게 해서 기계적인 느낌을 줄인다.
image hero_eyes_blink:
    "hero_eyes_open"
    choice:
        pause 2.5
    choice:
        pause 3.5
    choice:
        pause 5.0
    "hero_eyes_closed"
    pause 0.12
    repeat

## 말할 때 입 움직임 (립싱크 흉내): 두 장을 번갈아 보여준다.
image hero_mouth_flap:
    "hero_mouth_talk_a"
    pause 0.12
    "hero_mouth_neutral"
    pause 0.10
    repeat


## ---------------------------------------------------------------- 캐릭터 본체
layeredimage hero:

    ## 레이어는 위에서 아래 순서로 쌓인다. (먼저 쓴 것이 뒤쪽)

    group body:                       # 몸 + 머리 (옷 교체 = 이 그룹 교체)
        attribute tunic default       # → hero_body_tunic.png
        attribute armor               # → hero_body_armor.png

    group arms prefix "a":            # prefix 를 쓰면 속성 이름이 a_down, a_sword ... 가 된다
        attribute down default        # show hero a_down
        attribute sword               # show hero a_sword
        attribute crossed             # show hero a_crossed

    group brows:                      # 눈썹 (감정 표현의 절반은 눈썹이다)
        attribute normal_brows default "hero_brows_normal"
        attribute angry_brows "hero_brows_angry"
        attribute sad_brows   "hero_brows_sad"
        attribute up_brows    "hero_brows_up"

    group eyes:
        attribute blink default "hero_eyes_blink"   # 기본 = 자동으로 깜빡이는 눈
        attribute happy_eyes  "hero_eyes_happy"
        attribute closed_eyes "hero_eyes_closed"
        attribute wide_eyes   "hero_eyes_wide"

    group mouth if_not ["speaking"]:  # 말하는 중(speaking)에는 이 그룹을 숨긴다
        attribute neutral default "hero_mouth_neutral"
        attribute smile "hero_mouth_smile"
        attribute frown "hero_mouth_frown"
        attribute open  "hero_mouth_open"

    group talking:
        attribute speaking "hero_mouth_flap"   # 대사가 출력되는 동안 Ren'Py가 자동으로 붙여줌

    group overlay multiple:           # multiple = 여러 개를 동시에 켤 수 있음
        attribute blush "hero_overlay_blush"
        attribute sweat "hero_overlay_sweat"


## 대사 중일 때 자동으로 'speaking' 속성을 붙였다 떼어 준다.
## → 대사 한 줄마다 입이 저절로 움직인다. (Ren'Py 7.4+ 기능)
define config.speaking_attribute = "speaking"


## ---------------------------------------------------------------- 자주 쓰는 표정 묶음
## 표정 = 눈썹 + 눈 + 입 조합. 이름을 붙여두면 대본 쓰기가 편하다.
##   show hero expr_angry   대신   $ hero_expr("angry")   처럼 써도 되지만,
## 가장 간단한 방법은 아래처럼 "주석으로 레시피를 적어두는 것"이다.
##
##   기본 : normal_brows blink neutral
##   기쁨 : normal_brows happy_eyes smile blush
##   화남 : angry_brows blink frown
##   슬픔 : sad_brows blink frown
##   놀람 : up_brows wide_eyes open
##   당황 : sad_brows blink neutral sweat


## ---------------------------------------------------------------- 적 (통짜 이미지)
## 적은 표정 변화가 적으니 그냥 통짜 이미지 2장(평소/피격)으로 충분하다.
## images/enemy/slime.png, slime_hurt.png → 이미지 이름 "slime", "slime_hurt"
