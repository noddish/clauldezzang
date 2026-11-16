## ============================================================================
## core/location.rpy — 장소, 클릭할 물건, 이동, 메인 루프
##
## 원작 방식: 장소마다 screen 을 따로 만들고 if 사슬로 버튼을 넣었다.
## 여기서는 장소의 물건을 "데이터 목록"으로 정의하고, 화면 하나(location_view)가 그린다.
##
##   place("tavern", "선술집 '졸린 곰'", bg="tavern", parent="map")
##   OBJECTS["tavern"] = [
##       Obj("exit",   (20, 200, 140, 420), MoveTo("map"), "밖으로"),
##       Obj("cellar", (900, 300, 160, 300), Interact("tavern_cellar"), "지하 창고",
##           when=lambda: SUB_MARTHA.is_state("cellar")),
##   ]
##
## 물건 그림: images/objects/object_<장소>_<물건>_<day|night>.png 가 있으면 그 그림을
## rect 의 왼쪽 위에 놓는다 (원작의 오려낸 조각 방식). 없으면 반투명 임시 버튼을 그린다.
## ============================================================================

default here = "guild_hall"
default destination = None
default visited = set()

init -25 python:

    LOC = {}
    OBJECTS = {}
    NPC_SPOTS = {}      # 장소 id → {머신 id: 화면 x 위치(0~1)}

    class Location(object):
        def __init__(self, id, name, bg=None, parent=None, night_bg=True):
            self.id = id
            self.name = name
            self.bg = bg or id
            self.parent = parent
            self.night_bg = night_bg     # False 면 밤에도 낮 그림 (동굴 등)

    def place(id, name, **kw):
        LOC[id] = Location(id, name, **kw)
        OBJECTS.setdefault(id, [])
        return LOC[id]

    class Obj(object):
        def __init__(self, id, rect, action, tip, when=None):
            self.id = id
            self.rect = rect             # (x, y, w, h) — 1280x720 기준
            self.action = action
            self.tip = tip
            self.when = when             # 보일 조건 (함수). None 이면 항상

        def visible(self):
            return self.when is None or self.when()

        def image(self, loc_id):
            tod = "night" if is_dark() else "day"
            for t in (tod, "day"):
                path = "images/objects/object_%s_%s_%s.png" % (loc_id, self.id, t)
                if renpy.loadable(path):
                    return path
            return None

    def location_bg(loc_id):
        loc = LOC[loc_id]
        names = []
        if is_dark() and loc.night_bg:
            names.append("bg_%s_night" % loc.bg)
        names.append("bg_%s_day" % loc.bg)
        for n in names:
            if renpy.has_image(n):
                return n
        color = "#2b3044" if is_dark() and loc.night_bg else "#4a4f5c"
        return Placeholder("%s — %s" % (loc.name, TODS[store.tod]), color)

    def visible_objects(loc_id):
        return [o for o in OBJECTS.get(loc_id, []) if o.visible()]

    def npcs_here(loc_id):
        """(머신 id, x 위치) — 위치표상 지금 이 장소에 있는 캐릭터"""
        out = []
        for mid, x in NPC_SPOTS.get(loc_id, {}).items():
            m = MACHINES[mid]
            if m.where() == loc_id:
                out.append((mid, x))
        return out


    ## ---------------------------------------------------------------- 화면 버튼 동작
    class MoveTo(Action):
        def __init__(self, loc_id):
            self.loc_id = loc_id
        def __call__(self):
            store.destination = self.loc_id
            renpy.jump("go_to")

    class Interact(Action):
        """물건 클릭 → label 로"""
        def __init__(self, label):
            self.label = label
        def __call__(self):
            renpy.jump(self.label)

    class TalkTo(Action):
        """캐릭터 클릭 → label <머신 id>_talk"""
        def __init__(self, machine_id):
            self.machine_id = machine_id
        def __call__(self):
            renpy.jump(self.machine_id + "_talk")

    class WaitTick(Action):
        """시간 보내기. 화면을 닫고 메인 루프를 다시 돌려 강제 이벤트(감사 등)를 확인한다."""
        def __call__(self):
            tick()
            return True
        def get_sensitive(self):
            return can_tick()


## ---------------------------------------------------------------- 메인 루프
## 원작의 game.main() 에 해당. 장소 화면을 띄우고, 클릭한 버튼이 다른 label 로 jump 한다.
label main_loop:
    if game_over:
        return
    $ _event = pending_event()
    if _event:
        call expression _event
        jump main_loop
    scene expression location_bg(here)
    call screen location_view(here)
    jump main_loop


## 장소 이동: 진입 검사 → 이동 → 진입 이벤트
label go_to:
    $ _dest = destination
    call lock_check(here, _dest)
    if _return:
        jump main_loop
    $ here = _dest
    $ _first = _dest not in visited
    $ visited.add(_dest)
    scene expression location_bg(here)
    with dissolve
    if renpy.has_label("enter_" + here):
        call expression "enter_" + here pass (_first)
    jump main_loop


## ---------------------------------------------------------------- 공용 장소 화면
transform obj_hover:
    matrixcolor BrightnessMatrix(0.18)

transform npc_spot(x):
    xcenter x yalign 1.0

screen location_view(loc_id):
    tag location
    add location_bg(loc_id)

    for o in visible_objects(loc_id):
        $ img = o.image(loc_id)
        if img:
            imagebutton:
                pos (o.rect[0], o.rect[1])
                idle img
                hover At(img, obj_hover)
                focus_mask True
                action o.action
                tooltip o.tip
        else:
            button:
                area o.rect
                background Frame(Solid("#ffffff22"), 4, 4)
                hover_background Frame(Solid("#ffe08a55"), 4, 4)
                action o.action
                tooltip o.tip
                text o.tip size 20 color "#ffffffcc" align (0.5, 0.5) text_align 0.5

    for mid, x in npcs_here(loc_id):
        imagebutton:
            at npc_spot(x)
            idle mid
            hover At(mid, obj_hover)
            focus_mask True
            action TalkTo(mid)
            tooltip "%s와 대화" % CHAR_NAMES.get(mid, mid)

    use hud
