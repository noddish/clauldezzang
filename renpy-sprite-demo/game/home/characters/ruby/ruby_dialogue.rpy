## ============================================================================
## characters/ruby/ruby_dialogue.rpy — 루비를 클릭했을 때 (원작 button.rpy 의 <이름>_button_dialogue)
## 퀘스트 단계(is_state)에 따라 다른 대사로 분기한다.
## ============================================================================

label ruby_button_dialogue:
    scene expression game.location.bg
    show ruby at ruby_right
    with dissolve

    if M_ruby.is_state(S_ruby_start):
        r happy "일어났어? 스튜 끓여놨으니까 먹어."
        r neutral "아 맞다, 혹시 내 부싯돌 못 봤어? 저녁에 벽난로 피워야 하는데."
        r "네 방에 굴러들어간 거 아니야? 찾으면 좀 갖다줘."
        $ M_ruby.trigger("T_ruby_breakfast")

    elif M_ruby.is_state(S_ruby_give) and "remote" in game.inventory:
        r surprised "어? 내 부싯돌! 어디 있었어?"
        show ruby happy at ruby_right, double_hop
        r happy "고마워! 내일 저녁엔 벽난로 앞에서 내가 던전 갔던 얘기 해줄게."
        $ M_ruby.trigger("T_ruby_given")

    elif M_ruby.is_state(S_ruby_night) and game.location == L_home_livingroom and game.timer.tod == 2:
        r happy "왔구나! 앉아, 불 피웠어."
        scene expression game.location.bg
        with fade
        "( 벽난로 앞에서 루비의 던전 모험담을 들었다. )"
        show ruby happy at ruby_right
        with dissolve
        r "다음엔 너도 같이 가자. 장비부터 챙겨!"
        $ M_ruby.trigger("T_ruby_watched")
        $ game.timer.tick()

    else:
        menu:
            r "응? 왜?"
            "요즘 어때?":
                r happy "나야 늘 똑같지 뭐. 너는 학교 잘 다니고?"
            "부싯돌 말인데…" if M_ruby.is_state(S_ruby_remote):
                r angry "아직 못 찾았어? 네 방 책상 근처 잘 봐봐!"
            "아무것도 아니야.":
                r neutral "싱겁기는."

    hide ruby
    with dissolve
    jump game_main
