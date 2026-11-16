## ============================================================================
## script.rpy — 데모 대본
## ============================================================================
## 캐릭터 정의: image="hero" 로 연결하면
##   h smile "대사"  처럼 대사 앞에 속성을 붙여 표정을 바꿀 수 있다.
##   대사가 나오는 동안에는 speaking 속성이 자동으로 붙어 입이 움직인다.

define h = Character("레온", image="hero", color="#8fc3ff")
define n = Character(None, what_italic=True)          # 해설

## 화면 전체 흔들림 (Ren'Py 기본 제공 hpunch/vpunch 외에 약한 버전 추가)
define small_shake = Move((6, 0), (-6, 0), .08, bounce=True, repeat=True, delay=.3)


label start:
    scene bg_town_day
    with fade

    n "조립형 캐릭터 + 모션 데모입니다. 클릭하면서 진행해 보세요."

    show hero at stage_center, slide_in_right
    pause 0.5

    h "안녕! 나는 이 데모의 주인공 레온이야."
    h "지금 내 몸은 그림 한 장이 아니라 여러 장의 조각이 겹쳐진 거야."

    jump demo_menu


## ---------------------------------------------------------------- 메뉴
label demo_menu:
    scene bg_town_day
    show hero tunic a_down normal_brows blink neutral -blush -sweat at stage_center, breathing
    with dissolve

    menu:
        h "뭘 보여줄까?"

        "① 레이어 조립 원리":
            jump demo_layers
        "② 표정 바꾸기":
            jump demo_expressions
        "③ 옷 / 팔 포즈 바꾸기":
            jump demo_outfits
        "④ 감정 모션 (그림 추가 없이 코드만)":
            jump demo_motions
        "⑤ 연출 (클로즈업, 실루엣, 밤)":
            jump demo_staging
        "⑥ 미니 턴제 전투":
            jump demo_battle
        "끝내기":
            return


## ---------------------------------------------------------------- ① 레이어 원리
label demo_layers:
    scene bg_town_day
    n "레이어를 하나씩 쌓아 보겠습니다. 모든 조각은 같은 크기(600x720)의 투명 그림입니다."

    show hero_body_tunic as l1 at stage_center
    with dissolve
    n "1층: 몸 + 머리  (hero_body_tunic.png)"

    show hero_arms_down as l2 at stage_center
    with dissolve
    n "2층: 팔  (hero_arms_down.png)"

    show hero_brows_normal as l3 at stage_center
    with dissolve
    n "3층: 눈썹  (hero_brows_normal.png)"

    show hero_eyes_open as l4 at stage_center
    with dissolve
    n "4층: 눈  (hero_eyes_open.png)"

    show hero_mouth_neutral as l5 at stage_center
    with dissolve
    n "5층: 입  (hero_mouth_neutral.png)  — 완성!"

    n "좌표를 하나도 지정하지 않았는데 정확히 맞습니다. 캔버스 크기를 통일했기 때문입니다."

    hide l1
    hide l2
    hide l3
    hide l4
    hide l5
    show hero at stage_center
    with dissolve
    h "그리고 실제로는 sprites.rpy 의 layeredimage 덕분에 'show hero' 한 줄이면 끝이야."
    jump demo_menu


## ---------------------------------------------------------------- ② 표정
label demo_expressions:
    h "표정은 눈썹 + 눈 + 입의 조합이야. 조각 13장으로 수십 가지가 나와."

    show hero happy_eyes smile blush at stage_center, hop
    h "기쁨: happy_eyes smile blush"

    show hero angry_brows blink frown -blush at stage_center, shiver
    h "화남: angry_brows frown  (+ shiver 모션)"

    show hero up_brows wide_eyes open at stage_center, hop
    h "놀람: up_brows wide_eyes open  (+ hop 모션)"

    show hero sad_brows blink frown at stage_center, droop
    h "슬픔: sad_brows frown  (+ droop 모션: 살짝 가라앉고 어두워짐)"

    show hero sad_brows blink neutral sweat at stage_center, back_to_normal
    h "당황: sad_brows neutral sweat"

    h "그리고 대사 앞에 속성을 붙이면 표정 바꾸기와 대사를 한 줄에 쓸 수 있어."
    h normal_brows happy_eyes smile -sweat "이렇게!  →  h happy_eyes smile \"대사\""
    h blink neutral "말하는 동안 입이 저절로 움직이는 것도 봤지? config.speaking_attribute 덕분이야."
    jump demo_menu


## ---------------------------------------------------------------- ③ 옷 / 포즈
label demo_outfits:
    show hero a_crossed angry_brows at stage_center
    with dissolve
    h "팔 포즈: a_crossed (팔짱)"

    show hero armor a_sword up_brows smile at stage_center, nod
    with dissolve
    h "옷 + 팔 교체: armor a_sword — 장비를 바꾸면 겉모습도 바뀌는 RPG에 바로 쓸 수 있어."

    show hero tunic a_down normal_brows neutral at stage_center
    with dissolve
    h "옷만 그리면 표정 조각은 그대로 재사용돼. 그림 수가 곱셈이 아니라 덧셈으로 늘어나지."
    jump demo_menu


## ---------------------------------------------------------------- ④ 모션
label demo_motions:
    h "지금부터는 그림을 한 장도 추가하지 않고 코드(ATL)만으로 움직여 볼게."

    show hero at stage_center, hop
    h "hop — 깡충"

    show hero happy_eyes smile at stage_center, double_hop
    h "double_hop — 신나서 두 번"

    show hero blink neutral at stage_center, nod
    h "nod — 끄덕"

    show hero angry_brows frown at stage_center, shiver
    h "shiver — 부들부들"

    show hero normal_brows at stage_center, flipped
    with dissolve
    h "flipped — 좌우 반전. 반대쪽을 보는 그림이 따로 필요 없어."

    hide hero
    with dissolve
    show hero at stage_left, slide_in_left
    h "slide_in_left — 왼쪽에서 등장"

    show hero at stage_left, fade_out_down
    pause 0.8
    show hero at stage_center, slide_in_right
    h "fade_out_down 으로 퇴장, slide_in_right 로 재등장."

    show hero up_brows wide_eyes open at stage_center
    with vpunch
    h "화면 전체 흔들기: with vpunch / with hpunch"
    jump demo_menu


## ---------------------------------------------------------------- ⑤ 연출
label demo_staging:
    show hero at stage_center, close_up
    h "close_up — 중요한 대사에서 얼굴 클로즈업."

    show hero at stage_center, back_to_normal
    pause 0.4
    show hero at stage_center, silhouette
    with dissolve
    n "silhouette — 아직 정체를 밝히지 않은 인물."

    scene bg_town_night
    show hero at stage_center
    with Fade(0.4, 0.3, 0.4)
    h "배경만 밤 버전으로 바꾸면 같은 캐릭터로 밤 장면 완성. (Summertime Saga도 이 방식이야)"

    show hero at stage_center
    with dissolve
    jump demo_menu


## ---------------------------------------------------------------- ⑥ 전투
label demo_battle:
    h armor a_sword up_brows "좋아, 전투 화면에서는 어떻게 움직이는지 보자!"
    call battle_slime
    if _return == "win":
        scene bg_town_day
        show hero armor a_sword happy_eyes smile at stage_center, double_hop
        h "승리! 전투 연출도 전부 motions.rpy 의 transform 이야."
    else:
        scene bg_town_day
        show hero tunic a_down sad_brows frown sweat at stage_center
        h "졌다… 그래도 데모니까 괜찮아."
    jump demo_menu
