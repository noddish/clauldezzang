## ============================================================================
## locations/home_events.rpy — 장소 진입 이벤트 + 물건 클릭 (원작 locations/*/<장소>.rpy)
## ============================================================================

define me = Character("나", color="#ffffff")

## 시작: 내 방에서 눈을 뜬다
label home_start:
    $ game.location = L_home_bedroom
    scene expression game.location.bg
    with fade
    me "( 하암… 아침이다. )"
    me "( 아래층에서 뭔가 맛있는 냄새가 나는데. )"
    jump game_main


## ----------------------------------------------------------------- 진입 이벤트
## 원작: label park_dialogue: … 첫 방문이면 이벤트 … $ game.main()
label home_kitchen_dialogue:
    if M_ruby.is_state(S_ruby_start) and game.timer.tod == 0:
        scene expression game.location.bg
        show ruby happy at ruby_right
        with dissolve
        r "어, 내려왔네? 마침 다 됐어."
        hide ruby
        with dissolve
    jump game_main


## ----------------------------------------------------------------- 물건
label home_bed:
    if game.timer.tod < 2:
        me "( 아직 잘 시간은 아니다. )"
        jump game_main
    me "( 오늘은 이만 자자. )"
    scene black
    with fade
    $ game.timer.sleep()          # 날짜 +1, 아침으로 + 모든 캐릭터에 T_all_sleep
    scene expression game.location.bg
    with fade
    me "( 아침이다. )"
    jump game_main

label home_desk:
    if M_ruby.is_state(S_ruby_remote):
        me "( 책상 위 책 사이에… 있다! 루비의 부싯돌이다. )"
        $ M_ruby.trigger("T_ruby_found")
    else:
        me "( 마법서를 좀 읽으며 시간을 보냈다. )"
        $ game.timer.tick()
    jump game_main

label home_fridge:
    me "( 찬장에서 사과를 하나 꺼내 먹었다. )"
    jump game_main

label home_stove:
    if game.timer.tod == 0 and game.timer.dow < 5:
        me "( 냄비 속 스튜가 아직 따뜻하다. )"
    else:
        me "( 지금은 아무것도 없다. )"
    jump game_main

label home_tv:
    if M_ruby.state in (S_ruby_start, S_ruby_remote, S_ruby_give):
        me "( 부싯돌이 없으면 불을 못 피운다… )"
    else:
        me "( 장작이 타닥타닥 탄다. )"
    jump game_main

label home_couch:
    me "( 긴 의자에 잠깐 누워 있었다. )"
    $ game.timer.tick()
    jump game_main

label home_wait:
    $ game.timer.tick()
    jump game_main
