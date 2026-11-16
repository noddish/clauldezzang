## ============================================================================
## core/locks.rpy — 장소 진입 검사 (원작 locks/*_lock_check.rpy)
##
## 원작은 구역마다 label 을 만들고 if 사슬로 막았다.
## 여기서는 규칙을 (조건 함수, 생각 대사) 목록으로 등록한다. 위에서부터 검사.
## 조건 함수는 (출발 장소 id, 도착 장소 id) 를 받는다.
## ============================================================================

init -10 python:
    LOCK_RULES = []

    def lock_rule(message):
        """데코레이터: @lock_rule("메시지") 를 붙인 함수가 True 면 이동을 막는다"""
        def deco(fn):
            LOCK_RULES.append((fn, message))
            return fn
        return deco

    def lock_reason(origin, dest):
        for fn, msg in LOCK_RULES:
            if fn(origin, dest):
                return msg
        return None

    WILD = ("forest", "cave_1", "cave_2")

    @lock_rule("밤에 숲에 들어가는 건 위험하다. 내일 가자.")
    def _night_wild(o, d):
        return d in WILD and store.tod == 3

    @lock_rule("핍의 가게는 문을 닫았다. 내일 다시 오자.")
    def _shop_closed(o, d):
        return d == "shop" and is_dark()

    @lock_rule("아직 숲에 갈 일이 없다. 먼저 선술집에서 의뢰를 받자.")
    def _forest_locked(o, d):
        return d == "forest" and not MAIN.reached("forest")

    @lock_rule("이끼 동굴은 위험하다고 들었다. 볼일이 생기면 가자.")
    def _cave_locked(o, d):
        return d == "cave_1" and not MAIN.reached("cave")

    @lock_rule("동굴 안쪽에서 굵직한 울음소리가 들린다… 짐을 찾는 일이 아니면 들어갈 이유가 없다.")
    def _boss_room(o, d):
        return d == "cave_2" and not MAIN.is_state("cave")


label lock_check(origin, dest):
    $ _msg = lock_reason(origin, dest)
    if _msg:
        think "[_msg!t]"
        return True
    return False
