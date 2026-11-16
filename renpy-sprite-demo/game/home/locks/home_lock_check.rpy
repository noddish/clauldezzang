## ============================================================================
## locks/home_lock_check.rpy — 장소 진입 검사 (원작 locks/home_lock_check.rpy)
##
## 원작:
##   label home_lock_check:
##       if M_anon.is_state(S_ano02_food) and motion not in route(L_home_bedroom, …):
##           anon '( That smell is coming from the kitchen! )'
##   → 막을 때는 return True, 통과는 return (False)
## ============================================================================

label home_lock_check(origin, dest):

    ## 밖으로 나가기 — 이 데모는 집 안까지
    if dest is L_town_map:
        me "( 마을로 나가는 건 다음에 하자. — 마을 지도는 다음 단계에서 )"
        return True

    ## 욕실 — 아침엔 사용 중, 그 외엔 데모에 없음
    if dest is L_home_bathroom:
        if game.timer.tod == 0:
            "{i}*덜컹*{/i}"
            r "거기 창고방이야! 함부로 열지 마!"
        else:
            me "( 지금은 볼일이 없다. )"
        return True

    ## 밤에는 아래층으로 못 내려감 (원작 park_night_closed 같은 시간 제한)
    if game.timer.tod == 3 and origin is L_home_hallway and dest is L_home_entrance:
        me "( 다들 자는 시간이다. 나도 자야지. )"
        return True

    ## 퀘스트 유도: 아침 첫 이동 때 부엌으로 안내 (막지는 않음)
    if M_ruby.is_state(S_ruby_start) and dest is L_home_livingroom:
        me "( 냄새는 부엌 쪽에서 나는데… )"

    return False
