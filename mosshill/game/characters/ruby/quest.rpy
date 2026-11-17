## ============================================================================
## characters/ruby/quest.rpy — 루비의 위치표와 서브 퀘스트 (원작 characters/<이름>/<이름>_fsm.rpy)
## 단계 문장 = HUD 퀘스트 힌트. 트리거는 대사·이벤트 label 에서 발생시킨다.
## ============================================================================

default ruby_flame = False          # 불꽃베기 해금 (부싯돌 퀘스트 보상)

init -4 python:
    ## 위치표: 아침 부엌 / 오후 주인공과 동행(화면에 없음) / 저녁 길드 홀 / 밤 자기 방
    RUBY = Machine("ruby", "루비의 부싯돌", schedule=[
        ["guild_kitchen", None, "guild_hall", None],
        ["guild_kitchen", None, "guild_hall", None],
    ])
    RUBY.state("flint_lost",   "루비가 부싯돌을 잃어버렸다. 내 방 책상 근처를 찾아보자.")
    RUBY.state("flint_return", "부싯돌을 찾았다! 저녁에 길드 홀의 루비에게 돌려주자.")
    RUBY.state("done",         "")
    RUBY.on("flint_lost",   "T_found",  "flint_return")
    RUBY.on("flint_return", "T_return", "done")
