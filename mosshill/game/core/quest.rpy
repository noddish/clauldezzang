## ============================================================================
## core/quest.rpy — 퀘스트 상태 머신 (원작 FSM/state_machine.rpy 방식)
##
## 원작과 같은 점:
##   - 퀘스트(또는 캐릭터)마다 머신 1개. 단계(State) 문장 = 퀘스트 힌트.
##   - "이 단계에서 이 트리거가 오면 → 다음 단계" 표로 진행.
##   - 단계에 delay 를 주면 잠을 그 횟수만큼 자야 다음으로 넘어간다.
##   - NPC 위치표: [평일/주말][시간대] → 장소 id
##
## 원작보다 나아진 점:
##   - 현재 단계를 store 변수(quest_state)에 이름(문자열)으로 저장한다.
##     → 세이브·되감기와 어긋나지 않고, 업데이트로 단계가 추가돼도 이름으로 찾는다.
##   - 발생한 트리거를 quest_log 에 남긴다 (디버그·세이브 변환용).
##
## 사용 예:
##   MAIN = Machine("main", "메인")
##   MAIN.state("board", "선술집 의뢰판에서 의뢰를 받자.")
##   MAIN.on("board", "T_take_job", "forest")
##   MAIN.is_state("board")  /  MAIN.reached("forest")  /  MAIN.trigger("T_take_job")
## ============================================================================

default quest_state = {}     # 머신 id → 현재 단계 이름
default quest_delay = {}     # 머신 id → 남은 잠 횟수
default quest_log = []       # (일, 시간대, 머신 id, 트리거, 이전 단계, 다음 단계)

init -30 python:

    MACHINES = {}

    class Machine(object):
        def __init__(self, id, title, schedule=None, initial=None):
            self.id = id
            self.title = title                # HUD 에 보이는 퀘스트 이름
            self.schedule = schedule          # NPC 위치표 (없으면 None)
            self.initial = initial            # 처음 단계 (None = 아직 시작 안 함)
            self.order = []                   # 단계 순서 (reached 계산용)
            self.hints = {}
            self.delays = {}
            self.table = {}                   # (단계, 트리거) → (다음 단계, 동작)
            MACHINES[id] = self

        ## ---- 정의
        def state(self, name, hint, delay=0):
            self.order.append(name)
            self.hints[name] = hint
            self.delays[name] = delay
            return self

        def on(self, from_state, trigger, to_state, action=None):
            self.table[(from_state, trigger)] = (to_state, action)
            return self

        ## ---- 조회
        @property
        def current(self):
            return store.quest_state.get(self.id, self.initial)

        def is_state(self, *names):
            return self.current in names

        def started(self):
            return self.current is not None

        def reached(self, name):
            """지금 단계가 name 이거나 그 뒤인가?"""
            if self.current is None:
                return False
            return self.order.index(self.current) >= self.order.index(name)

        def hint(self):
            return self.hints.get(self.current, "")

        def where(self):
            """위치표상 지금 있는 장소 id (없으면 None)"""
            if not self.schedule:
                return None
            row = self.schedule[1 if is_weekend() else 0]
            return row[store.tod]

        ## ---- 변경
        def start(self, name=None):
            self._enter(name or self.order[0])

        def _enter(self, name):
            store.quest_state[self.id] = name
            store.quest_delay[self.id] = self.delays.get(name, 0)

        def trigger(self, trigger):
            cur = self.current
            if cur is None:
                return False
            if trigger == "T_all_sleep" and store.quest_delay.get(self.id, 0) > 0:
                store.quest_delay[self.id] -= 1
                return False
            if store.quest_delay.get(self.id, 0) > 0:
                return False
            key = (cur, trigger)
            if key not in self.table:
                return False
            nxt, action = self.table[key]
            store.quest_log.append((store.day, store.tod, self.id, trigger, cur, nxt))
            self._enter(nxt)
            if action:
                action()
            return True


    def quest_signal(trigger):
        """모든 머신에 트리거 전달 (잠자기, 시간 경과 등)"""
        for m in list(MACHINES.values()):
            m.trigger(trigger)

    def is_weekend():
        return False    # 맛보기판(3일)에는 주말이 없다. 요일이 생기면 여기서 계산.

    def active_quests():
        """HUD 에 보여줄 (제목, 힌트) 목록. 시작했고 'done' 이 아닌 것만."""
        out = []
        for m in MACHINES.values():
            if m.title and m.started() and m.current != "done" and m.hint():
                out.append((m.title, m.hint()))
        return out
