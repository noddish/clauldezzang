## ============================================================================
## core/time.rpy — 날짜와 시간대 (원작 day_timer.rpy 를 단순화)
##
## 하루 = 4칸 (0 아침, 1 오후, 2 저녁, 3 밤). 맛보기판은 3일.
## 값은 전부 store 변수라서 세이브·되감기(rollback)에 안전하다.
## ============================================================================

define TODS = ["아침", "오후", "저녁", "밤"]
define LAST_DAY = 3

default day = 1
default tod = 0

init -20 python:

    def is_dark():
        return store.tod >= 2

    def time_label():
        return "%d일차 %s" % (store.day, TODS[store.tod])

    def can_tick():
        return store.tod < 3

    def tick(n=1):
        """시간대를 n칸 넘긴다. 밤에서는 더 넘어가지 않는다 (잠을 자야 함)."""
        for _ in range(n):
            if store.tod >= 3:
                return
            store.tod += 1
            quest_signal("T_all_tick")

    def sleep_to_next_day():
        """잠자기: 다음 날 아침 + 모든 퀘스트에 T_all_sleep + 파티 회복(M2)"""
        store.day += 1
        store.tod = 0
        quest_signal("T_all_sleep")
        for hook in SLEEP_HOOKS:
            hook()

    ## 다른 시스템이 "잠잘 때 할 일"을 등록하는 곳 (상점 재고, 파티 회복 등)
    SLEEP_HOOKS = []
