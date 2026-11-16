## ============================================================================
## characters/ruby/ruby_dialogue.rpy — 루비를 클릭했을 때 (원작 button.rpy 의 <이름>_button_dialogue)
## 퀘스트 단계(is_state)에 따라 다른 대사로 분기한다.
## ============================================================================

label ruby_button_dialogue:
    scene expression game.location.bg
    show ruby at ruby_center
    with dissolve

    if M_ruby.is_state(S_ruby_start):
        r happy "일어났어? 팬케이크 구웠으니까 먹어."
        r neutral "아 맞다, 혹시 TV 리모컨 못 봤어? 어제부터 안 보이네."
        r "네 방에 굴러들어간 거 아니야? 찾으면 좀 갖다줘."
        $ M_ruby.trigger("T_ruby_breakfast")

    elif M_ruby.is_state(S_ruby_give) and "remote" in game.inventory:
        r surprised "어? 리모컨! 어디 있었어?"
        show ruby happy at ruby_center, double_hop
        r happy "고마워! 그럼 내일 저녁에 같이 영화 보자. 팝콘은 내가 준비할게."
        $ M_ruby.trigger("T_ruby_given")

    elif M_ruby.is_state(S_ruby_night) and game.location == L_home_livingroom and game.timer.tod == 2:
        r happy "왔구나! 앉아, 시작한다."
        scene expression game.location.bg
        with fade
        "( 둘이서 소파에 앉아 영화를 봤다. )"
        show ruby happy at ruby_center
        with dissolve
        r "재밌었다! 또 보자."
        $ M_ruby.trigger("T_ruby_watched")
        $ game.timer.tick()

    else:
        menu:
            r "응? 왜?"
            "요즘 어때?":
                r happy "나야 늘 똑같지 뭐. 너는 학교 잘 다니고?"
            "리모컨 말인데…" if M_ruby.is_state(S_ruby_remote):
                r angry "아직 못 찾았어? 네 방 책상 근처 잘 봐봐!"
            "아무것도 아니야.":
                r neutral "싱겁기는."

    hide ruby
    with dissolve
    jump game_main
