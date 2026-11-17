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
## 물건 모양: images/objects/mask_<장소>_<물건>.png (rect 크기, 물건 모양만 불투명) 가 있으면
## 그 모양대로만 클릭되고, 마우스를 올리면 지금 배경을 그 모양으로 잘라 밝게 그린다.
## (원작은 배경과 똑같은 조각 PNG 를 낮·밤 따로 얹었다 — 같은 효과를 그림 파일 없이 낸다)
## 마스크가 없으면 반투명 임시 버튼을 그린다.
## ============================================================================

default here = "guild_hall"
default npc_looking = False   # 장소 안 인물이 지금 앞을 보고 있는가 (물건을 눌러도 그 모습 그대로)
default npc_greet = False      # 방금 장소에 들어왔는가 (장소 안 인물이 고개를 드는 연출)
default destination = None
default visited = set()

init -25 python:

    LOC = {}
    OBJECTS = {}
    NPC_SPOTS = {}      # 장소 id → {머신 id: 화면 x 위치(0~1)}
    CHAR_NAMES = {}     # 머신 id → 보이는 이름 (characters/<이름>/sprite.rpy 가 등록)

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

        def mask(self, loc_id):
            path = "images/objects/mask_%s_%s.png" % (loc_id, self.id)
            return path if renpy.loadable(path) else None

        def hover_image(self, loc_id):
            """마우스를 올렸을 때: 지금 배경을 물건 모양으로 잘라 밝게"""
            piece = AlphaMask(Crop(self.rect, location_bg(loc_id)), self.mask(loc_id))
            return At(piece, obj_hover)

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

    class NpcScene(object):
        """장소 안 인물 그림 (원작처럼 그 장소에서 뭔가 하는 모습).
        images/scenes/scene_<장소>_<인물>_busy_<day|night>.png — 하던 일을 보는 모습
        images/scenes/scene_<장소>_<인물>_look_<day|night>.png — 고개를 들어 앞(들어온 카이)을 보는 모습
        images/scenes/mask_scene_<장소>_<인물>.png             — 클릭·하이라이트할 인물 윤곽
        그림은 모두 화면 크기, 인물 부분만 불투명 (두 자세가 같은 모양으로 오려져 있어 겹쳐 바꿔도 비치지 않는다)"""
        def __init__(self, loc_id, mid):
            base = "images/scenes/scene_%s_%s_%%s_%s.png" % (loc_id, mid, "night" if is_dark() else "day")
            self.busy = base % "busy"
            self.look = base % "look"
            self.mask = "images/scenes/mask_scene_%s_%s.png" % (loc_id, mid)

        def hover(self, picture):
            return At(AlphaMask(picture, self.mask), obj_hover)

    def npc_scene(loc_id, mid):
        """그 장소용 인물 그림이 있으면 NpcScene, 없으면 None (→ 대화용 큰 그림을 세운다)"""
        sc = NpcScene(loc_id, mid)
        if all(renpy.loadable(f) for f in (sc.busy, sc.look, sc.mask)):
            return sc
        return None


    ## ---------------------------------------------------------------- 대화·혼잣말 배경
    def npc_layer(loc_id, state="look", without=None):
        """장소 안 인물 그림들 — 대화·혼잣말 중에도 그 장소에 있는 사람이 사라지지 않게
        (원작은 물건을 누르면 장소 화면이 닫히면서 인물도 사라졌다)"""
        kids = []
        for mid, x in npcs_here(loc_id):
            sc = npc_scene(loc_id, mid) if mid != without else None
            if sc:
                kids.append(getattr(sc, state))
        return Fixed(*kids, xysize=(1280, 720)) if kids else Null()

    def location_backdrop(loc_id, blur=False, without=None):
        """장소 배경 + 장소 안 인물. blur=True 면 흐리게 (대화 장면 — 원작의 _blur 배경).
        원작은 장소마다 흐린 그림을 따로 저장했지만(279장) 여기서는 실행 중에 흐리게 한다
        → 파일이 필요 없고 낮·저녁·밤 어느 그림이든 그대로 흐려진다."""
        d = Fixed(location_bg(loc_id), npc_layer(loc_id, "look", without), xysize=(1280, 720))
        return At(d, dialogue_blur) if blur else d

    def blurred(d):
        return At(d, dialogue_blur)


    ## ---------------------------------------------------------------- 화면 버튼 동작
    class MoveTo(Action):
        def __init__(self, loc_id):
            self.loc_id = loc_id
        def __call__(self):
            store.destination = self.loc_id
            renpy.jump("go_to")

    class Interact(Action):
        """물건 클릭 → label 로. 장소 안 인물은 보이던 모습 그대로 남겨 둔다."""
        def __init__(self, label):
            self.label = label
        def __call__(self):
            renpy.show("npc_layer", what=npc_layer(store.here, "look" if store.npc_looking else "busy"))
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
    call run_events("idle")             # 강제 이벤트 (core/events.rpy, on="idle")
    if game_over:
        return
    scene expression location_bg(here)
    ## 방금 들어왔으면 장소 안 인물이 하던 일을 멈추고 고개를 든다 (한 번만)
    $ npc_looking, npc_greet = npc_greet, False
    call screen location_view(here, npc_looking)
    jump main_loop


## 장소 이동: 진입 검사 → 이동 → 진입 이벤트
label go_to:
    $ _dest = destination
    call lock_check(here, _dest)
    if _return:
        jump main_loop
    $ here = _dest
    $ npc_greet = True
    $ visit_count[_dest] = visit_count.get(_dest, 0) + 1
    $ visited.add(_dest)
    scene expression location_bg(here)
    with dissolve
    call run_events("enter")            # 진입 이벤트 (core/events.rpy, on="enter")
    jump main_loop


## ---------------------------------------------------------------- 공용 장소 화면
## 마우스를 올렸을 때: 색을 몇 배로 (밝기를 '더하면' 밤 그림이 뿌옇게 떠서 '곱한다'), 살짝 따뜻하게.
## 어두운 밤 그림은 곱해도 티가 덜 나서 더 세게.
init -10 python:
    def hover_matrix():
        k = 1.75 if is_dark() else 1.3
        return Matrix([k * 1.04, 0, 0, 0,
                       0, k, 0, 0,
                       0, 0, k * 0.92, 0,
                       0, 0, 0, 1])

transform obj_hover:
    matrixcolor hover_matrix()

## 장소 안 인물: 들어오면 잠깐 하던 일을 보다가 고개를 들어 앞을 본다 (look 그림이 서서히 겹쳐짐)
transform npc_look_up:
    alpha 0.0
    pause 0.6
    linear 0.3 alpha 1.0

## 대화 장면 배경 흐림 (원작은 흐린 배경 그림을 따로 저장, 여기서는 실행 중에)
transform dialogue_blur:
    blur 6

transform npc_spot(x):
    xcenter x yalign 1.0
    xzoom (-1.0 if x < 0.5 else 1.0)     # 왼쪽에 서면 화면 가운데를 보게 뒤집기
    matrixcolor light_matrix()            # 밤에는 푸르스름하게

screen location_view(loc_id, greet=False):
    tag location
    add location_bg(loc_id)

    for o in visible_objects(loc_id):
        $ mask = o.mask(loc_id)
        if mask:
            imagebutton:
                pos (o.rect[0], o.rect[1])
                idle Null(o.rect[2], o.rect[3])
                hover o.hover_image(loc_id)
                focus_mask mask
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
        $ sc = npc_scene(loc_id, mid)
        if sc:
            ## 그 장소에서 뭔가 하는 모습 (배경의 일부처럼). 방금 들어왔으면 고개를 들어 앞을 본다.
            ## 마우스를 올리면 인물만 밝게
            add sc.busy
            if greet:
                add sc.look at npc_look_up
            imagebutton:
                idle Null(1280, 720)
                hover sc.hover(sc.look if greet else sc.busy)
                focus_mask sc.mask
                action TalkTo(mid)
                tooltip "%s와 대화" % CHAR_NAMES.get(mid, mid)
        else:
            ## 장소용 그림이 없으면 대화용 큰 그림을 세운다
            imagebutton:
                at npc_spot(x)
                idle mid
                hover At(mid, obj_hover)
                focus_mask True
                action TalkTo(mid)
                tooltip "%s와 대화" % CHAR_NAMES.get(mid, mid)

    use hud
