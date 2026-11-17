## ============================================================================
## characters/talk.rpy — 캐릭터를 클릭했을 때 (원작 button.rpy 의 <이름>_button_dialogue)
## 퀘스트 단계에 따라 분기한다. M1 은 흐름 검증용 짧은 대사. 본 대사는 M4 에서 쓴다.
## ============================================================================

default ruby_chat_day = 0       # 루비 잡담 신뢰도 보너스를 하루 한 번만

## ---------------------------------------------------------------- 루비
label ruby_talk:
    scene expression location_bg(here)
    show ruby at stage_right
    with dissolve

    if RUBY.is_state("flint_return") and has_item("flint"):
        r surprised "어?! 내 부싯돌! 어디 있었어?"
        me "내 방 책상 서랍에. 네가 어제 거기서 촛불 붙이다 두고 갔겠지."
        show ruby happy at stage_right, double_hop
        r "고마워, 길드장님! 이걸로 칼날에 불을 붙이는 기술이 있거든. 다음 전투에서 보여줄게!"
        $ remove_item("flint")
        $ RUBY.trigger("T_return")
        $ ruby_flame = True
        $ add_bond("ruby", 20)

    elif here == "guild_hall" and tod == 2 and not RUBY.started():
        show ruby sad at stage_right
        r "길드장님… 혹시 내 부싯돌 못 봤어? 벽난로를 피워야 하는데 없어졌어."
        me "어디서 마지막으로 썼는데?"
        r "음… 어제 2층에서 촛불 켤 때?"
        $ RUBY.start()

    elif here == "guild_kitchen" and tod == 0:
        if day == 1:
            r happy "아침 먹고 나가자! 오늘은 선술집 게시판부터야."
        elif day == 2:
            r "어제 슬라임 덕에 돈이 좀 생겼어. 오늘은 더 큰 일을 받아 보자!"
        else:
            r sad "오늘 오후에 감사관이 온대… 떨려."

    else:
        menu:
            r "응? 왜 불러?"
            "요즘 길드 생활 어때?":
                r happy "길드장님이 온 뒤로 훨씬 좋아! 혼자일 땐 진짜 심심했거든."
            "부싯돌 말인데…" if RUBY.is_state("flint_lost"):
                r "2층 어딘가에 있을 거야. 책상 쪽 한번 봐 줄래?"
            "아무것도 아니야.":
                r "싱겁기는."
        if ruby_chat_day != day:
            $ ruby_chat_day = day
            $ add_bond("ruby", 2)

    hide ruby
    with dissolve
    jump main_loop


## ---------------------------------------------------------------- 마르타
label martha_talk:
    scene expression location_bg(here)
    show martha at stage_right
    with dissolve

    if MAIN.is_state("board"):
        m happy "오, 네가 그 조카구나. 길드가 망하기 직전이라며?"
        m "마침 일이 하나 있지. 숲길에 슬라임이 늘어서 약초꾼들이 못 다닌대."
        m "치우고 오면 40골드. 해볼래?"
        me "할게요."
        $ MAIN.trigger("T_take_job")

    elif MAIN.is_state("report_martha"):
        m happy "벌써 다 치웠다고? 제법인데!"
        $ add_gold(40)
        $ MAIN.trigger("T_report")
        m "그리고… 하나 더 부탁하자. 우리 지하 창고에도 슬라임이 들어앉았거든."
        m "시간 될 때 치워 주면 회복약 두 병 줄게."
        $ MARTHA.start()

    elif MARTHA.is_state("cellar_report"):
        m happy "창고가 깨끗해졌네! 약속한 거야."
        $ add_item("potion", 2)
        $ MARTHA.trigger("T_paid")

    else:
        m "뭐 마실래? …농담이야, 넌 아직 일할 시간이잖아."

    hide martha
    with dissolve
    jump main_loop


## ---------------------------------------------------------------- 핍
label pip_talk:
    scene expression location_bg(here)
    show pip at stage_right
    with dissolve

    if MAIN.is_state("pip_job"):
        p surprised "아이고 길드장님! 마침 잘 왔어요!"
        p "어제 짐마차가 이끼 동굴 앞을 지나다 짐 하나를 떨어뜨렸는데, 두꺼비 놈이 물고 들어갔지 뭐예요!"
        p "찾아 주시면 80골드! 협회 실적에도 딱이죠?"
        $ MAIN.trigger("T_take_cave")

    elif MAIN.is_state("return_cargo") and has_item("pip_cargo"):
        p happy "제 짐! 두꺼비 침 범벅이지만… 무사하네요!"
        $ remove_item("pip_cargo")
        $ add_gold(80)
        $ MAIN.trigger("T_cargo")

    else:
        p "어서 오세요~ 물건 구경은 진열장에서! 슬라임 젤리나 고블린 송곳니도 사들여요."

    hide pip
    with dissolve
    jump main_loop
