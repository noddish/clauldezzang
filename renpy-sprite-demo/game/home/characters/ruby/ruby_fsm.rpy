## ============================================================================
## characters/ruby/ruby_fsm.rpy — 루비의 위치표 + 퀘스트 (원작 characters/erik/erik_fsm.rpy 방식)
## ============================================================================

init -4 python:
    ## 위치표: [평일 아침/오후/저녁/밤], [주말 아침/오후/저녁/밤]   None = 집에 없음(외출, 자는 중)
    M_ruby = Machine("ruby", schedule=[
        [L_home_kitchen,    None,           L_home_livingroom, None],
        [L_home_livingroom, L_home_kitchen, L_home_livingroom, None],
    ])

    ## 퀘스트 단계 — 문장은 그대로 HUD 의 퀘스트 힌트가 된다 (원작과 동일)
    S_ruby_start  = State("아래층 부엌에서 맛있는 냄새가 난다. 내려가 볼까?")
    S_ruby_remote = State("루비가 TV 리모컨을 잃어버렸다. 내 방 책상 근처에 있나?")
    S_ruby_give   = State("리모컨을 찾았다! 저녁에 거실에 있는 루비에게 돌려주자.")
    S_ruby_movie  = State("루비가 내일 저녁에 같이 영화 보자고 했다. (침대에서 자고 내일 저녁 거실로)")
    S_ruby_night  = State("저녁에 거실에서 루비와 영화 보기!")
    S_ruby_end    = State("퀘스트 완료! (데모 끝 — 자유롭게 돌아다녀 보세요)")

    ## 전이: 이 상태에서 이 트리거가 오면 → 다음 상태
    S_ruby_start.add("T_ruby_breakfast", S_ruby_remote)
    S_ruby_remote.add("T_ruby_found", S_ruby_give, action=lambda: game.inventory.add("remote"))
    S_ruby_give.add("T_ruby_given", S_ruby_movie, action=lambda: game.inventory.discard("remote"))
    S_ruby_movie.add("T_all_sleep", S_ruby_night)          # 잠을 자면 다음 단계
    S_ruby_night.add("T_ruby_watched", S_ruby_end)

    M_ruby.start(S_ruby_start)
