## ============================================================================
## characters/ruby/talk.rpy — 루비와 대화
## ============================================================================

## 인물을 눌렀을 때 (원작 button.rpy 의 <이름>_button_dialogue). 퀘스트 단계에 따라 분기한다.
## 배경은 흐리게(원작처럼 인물이 돋보이게), 장소 안의 다른 인물은 그대로 보인다.

default ruby_chat_day = 0       # 루비 잡담 신뢰도 보너스를 하루 한 번만

label ruby_talk:
    scene expression location_backdrop(here, blur=True, without="ruby")
    show kai at stage_left
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
    hide kai
    with dissolve
    jump main_loop
