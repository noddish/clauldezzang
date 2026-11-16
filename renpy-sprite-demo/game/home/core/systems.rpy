## ============================================================================
## core/systems.rpy — Summertime Saga 의 core/systems 를 단순화해 옮긴 것
##   DayTimer  : day_timer.rpy  (하루 4칸, 요일, 낮/밤 이미지 자동 선택)
##   Location  : locations.rpy  (장소 트리, 잠금, 배경)
##   Machine   : FSM/state_machine.rpy (캐릭터별 퀘스트 상태 + 위치표)
##   MoveTo / TalkTo : actions.rpy (화면 버튼이 쓰는 동작)
## ============================================================================

init -10 python:

    ## ------------------------------------------------------------ 시간
    class DayTimer(object):
        TODS = ["아침", "오후", "저녁", "밤"]
        DOWS = ["월", "화", "수", "목", "금", "토", "일"]

        def __init__(self):
            self.day = 0      # 게임 시작 후 지난 날 수
            self.tod = 0      # 0 아침, 1 오후, 2 저녁, 3 밤

        @property
        def dow(self):
            return self.day % 7

        def is_dark(self):
            return self.tod >= 2

        def is_weekend(self):
            return self.dow >= 5

        def tick(self):
            """시간대를 한 칸 넘긴다. 밤에서는 더 넘어가지 않는다(잠을 자야 함)."""
            if self.tod < 3:
                self.tod += 1
                Machine.trigger_all("T_all_tick")

        def sleep(self):
            self.day += 1
            self.tod = 0
            Machine.trigger_all("T_all_sleep")     # 모든 캐릭터에게 "하루 지남" 알림

        def image(self, name):
            """'home_bedroom{}' → 낮이면 home_bedroom_day, 밤이면 home_bedroom_night"""
            return name.format("_night" if self.is_dark() else "_day")

        def label(self):
            return "%d일차 %s요일 %s" % (self.day + 1, self.DOWS[self.dow], self.TODS[self.tod])


    ## ------------------------------------------------------------ 장소
    class Location(object):
        def __init__(self, name, background, parent=None, locked=False):
            self.name = name
            self.background = background      # "home_bedroom{}" 형식
            self.parent = parent
            self.locked = locked
            self.children = []
            if parent is not None:
                parent.children.append(self)

        @property
        def ref(self):
            """screen 이름 / label 이름의 기준. L_home_bedroom → 'home_bedroom'"""
            return self.background.replace("{}", "")

        @property
        def bg(self):
            return game.timer.image(self.background)

        def is_child_of(self, other):
            p = self.parent
            while p is not None:
                if p is other:
                    return True
                p = p.parent
            return False

        def is_here(self, machine):
            return machine.where() is self


    ## ------------------------------------------------------------ 퀘스트 상태 머신
    class State(object):
        def __init__(self, hint, delay=0):
            self.hint = hint          # 퀘스트 힌트 문장 (HUD에 표시)
            self.delay = delay        # 잠을 몇 번 자야 다음 단계가 열리는지
            self.table = {}           # 트리거 이름 → (다음 상태, 실행할 함수)

        def add(self, trigger, next_state, action=None):
            self.table[trigger] = (next_state, action)


    class Machine(object):
        all = []

        def __init__(self, name, schedule):
            ## schedule = [평일 4칸, 주말 4칸]  (Summertime Saga 의 default_loc 와 같은 모양)
            self.name = name
            self.schedule = schedule
            self.state = None
            self.delay_left = 0
            self.vars = {}
            Machine.all.append(self)

        def start(self, state):
            self.state = state
            self.delay_left = state.delay

        def is_state(self, *states):
            return self.state in states

        def trigger(self, trigger):
            if self.state is None:
                return False
            if trigger == "T_all_sleep" and self.delay_left > 0:
                self.delay_left -= 1
                return False
            if trigger in self.state.table and self.delay_left == 0:
                nxt, action = self.state.table[trigger]
                if action:
                    action()
                self.start(nxt)
                return True
            return False

        @classmethod
        def trigger_all(cls, trigger):
            for m in cls.all:
                m.trigger(trigger)

        def where(self):
            day = self.schedule[1 if game.timer.is_weekend() else 0]
            return day[game.timer.tod]


    ## ------------------------------------------------------------ 게임 전체
    class Game(object):
        def __init__(self):
            self.timer = DayTimer()
            self.location = None
            self.inventory = set()

        def main(self):
            """현재 장소의 화면을 띄우고 클릭을 기다린다 (Summertime Saga 의 game.main())."""
            renpy.jump("game_main")


    ## ------------------------------------------------------------ 화면 버튼용 동작
    class MoveTo(Action):
        def __init__(self, location):
            self.location = location

        def __call__(self):
            store.destination = self.location
            renpy.jump("global_lock_check")


    class TalkTo(Action):
        def __init__(self, machine):
            self.machine = machine

        def __call__(self):
            renpy.jump(self.machine.name + "_button_dialogue")


    class Interact(Action):
        """사물 클릭 → label 로 점프"""
        def __init__(self, label):
            self.label = label

        def __call__(self):
            renpy.jump(self.label)


default game = Game()
default destination = None


## --------------------------------------------------------------- 메인 루프
label game_main:
    scene expression game.location.bg
    $ renpy.call_screen(game.location.ref)
    jump game_main


## --------------------------------------------------------------- 장소 이동
## Summertime Saga: MoveTo → global_lock_check → <구역>_lock_check → go_to → <장소>_dialogue
label global_lock_check:
    call home_lock_check(game.location, destination)
    if _return:                       # True 면 이동 취소
        jump game_main
    $ game.location = destination
    $ renpy.transition(dissolve)
    if renpy.has_label(destination.ref + "_dialogue"):
        jump expression destination.ref + "_dialogue"
    jump game_main
