## ============================================================================
## core/events.rpy — 이벤트 등록부
##
## 원작은 장소마다 진입 label 안에 if 사슬로 이벤트를 넣었고(어디에 무슨 이벤트가 있는지 코드를 다 읽어야 앎),
## 강제 이벤트는 메인 루프 곳곳에 흩어져 있었다. 여기서는 이벤트를 데이터로 등록한다:
##
##   event("forest_slimes", "forest_slime_story", at="forest",
##         when=lambda: MAIN.is_state("forest"), once=False)
##
##   at        장소 id (None 이면 어디서든)
##   on        "enter" = 그 장소에 막 들어왔을 때 / "idle" = 메인 루프가 장소 화면을 띄우기 직전 (강제 이벤트)
##   when      조건 (함수). None 이면 항상
##   once      True 면 한 번 본 뒤 다시 안 나온다 (seen_events 에 기록 — 세이브된다)
##   priority  여러 개가 동시에 맞으면 큰 것부터 차례로
##
## 이벤트 label 은 call 로 불리므로 return 으로 끝낸다.
## 자동 검사(m0)가 등록된 모든 이벤트 label 이 실제로 있는지 확인한다.
## ============================================================================

default seen_events = set()
default visit_count = {}

init -30 python:

    EVENTS = []

    class GameEvent(object):
        def __init__(self, id, label, at=None, on="enter", when=None, once=True, priority=0):
            self.id, self.label, self.at, self.on = id, label, at, on
            self.when, self.once, self.priority = when, once, priority

        def ready(self, on, loc):
            if self.on != on or (self.at is not None and self.at != loc):
                return False
            if self.once and self.id in store.seen_events:
                return False
            return self.when is None or bool(self.when())

    def event(id, label, **kw):
        if any(e.id == id for e in EVENTS):
            raise Exception("이벤트 id 중복: " + id)
        EVENTS.append(GameEvent(id, label, **kw))

    def next_event(on, loc, done):
        """지금 실행할 이벤트 하나 (이번 차례에 이미 실행한 것은 빼고)"""
        for e in sorted(EVENTS, key=lambda e: -e.priority):
            if e.id not in done and e.ready(on, loc):
                if e.once:
                    store.seen_events.add(e.id)
                return e
        return None

    def first_visit(loc=None):
        """그 장소에 처음 들어온 것인가 (enter 이벤트의 조건용)"""
        return store.visit_count.get(loc or store.here, 0) <= 1


## 등록된 이벤트를 차례로 실행. 실행 중에 상태가 바뀌면 다음 이벤트 조건에 반영된다.
label run_events(on):
    $ _ev_done = set()
    while not game_over:
        $ _ev = next_event(on, here, _ev_done)
        if _ev is None:
            return
        $ _ev_done.add(_ev.id)
        call expression _ev.label
    return
