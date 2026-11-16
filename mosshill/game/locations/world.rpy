## ============================================================================
## locations/world.rpy — 장소 트리와 각 장소의 클릭할 물건
##
##   map (마을 지도)
##   ├─ guild_hall 길드 홀 ─┬─ guild_room 내 방 (2층)
##   │                     └─ guild_kitchen 부엌
##   ├─ square 마을 광장
##   ├─ tavern 선술집 '졸린 곰'
##   ├─ shop 핍의 잡화점
##   └─ forest 숲길 ── cave_1 이끼 동굴 ── cave_2 두꺼비 왕의 방
##
## rect 는 M1 임시 버튼 위치. M3 에서 배경을 그린 뒤 실제 물건 위치로 바꾼다.
## ============================================================================

init -5 python:
    place("map",           "마을 지도")
    place("guild_hall",    "길드 홀",          parent="map")
    place("guild_room",    "내 방",            parent="guild_hall")
    place("guild_kitchen", "부엌",             parent="guild_hall")
    place("square",        "마을 광장",        parent="map")
    place("tavern",        "선술집 '졸린 곰'",  parent="map")
    place("shop",          "핍의 잡화점",      parent="map")
    place("forest",        "숲길",             parent="map")
    place("cave_1",        "이끼 동굴",        parent="forest", night_bg=False)
    place("cave_2",        "두꺼비 왕의 방",   parent="cave_1", night_bg=False)

    ## ---------------------------------------------------------------- 지도
    OBJECTS["map"] = [
        Obj("guild",  (240, 430, 190, 110), MoveTo("guild_hall"), "길드하우스"),
        Obj("square", (560, 320, 190, 110), MoveTo("square"),     "마을 광장"),
        Obj("tavern", (840, 200, 190, 110), MoveTo("tavern"),     "선술집"),
        Obj("shop",   (840, 450, 190, 110), MoveTo("shop"),       "잡화점"),
        Obj("forest", (110, 140, 190, 110), MoveTo("forest"),     "숲길"),
    ]

    ## ---------------------------------------------------------------- 길드하우스
    OBJECTS["guild_hall"] = [
        Obj("stairs",  (180, 40, 300, 500),  MoveTo("guild_room"),    "2층 내 방"),
        Obj("door",    (620, 120, 180, 380), MoveTo("map"),           "밖으로"),
        Obj("kitchen", (1010, 90, 170, 450), MoveTo("guild_kitchen"), "부엌"),
        Obj("board",   (850, 150, 130, 160), Interact("guild_board"), "길드 의뢰판"),
        Obj("hearth",  (0, 200, 160, 330),   Interact("guild_hearth"), "벽난로"),
    ]
    OBJECTS["guild_room"] = [
        Obj("door", (1100, 40, 150, 560),  MoveTo("guild_hall"),  "1층으로"),
        Obj("bed",  (40, 300, 380, 320),   Interact("guild_bed"),  "침대 (자기)"),
        Obj("desk", (640, 280, 380, 240),  Interact("guild_desk"), "책상"),
    ]
    OBJECTS["guild_kitchen"] = [
        Obj("back",   (35, 40, 170, 490),    MoveTo("guild_hall"),     "길드 홀로"),
        Obj("pantry", (1130, 0, 150, 700),   Interact("guild_pantry"), "찬장"),
        Obj("hearth", (955, 230, 170, 350),  Interact("guild_stove"),  "화덕"),
    ]

    ## ---------------------------------------------------------------- 마을
    OBJECTS["square"] = [
        Obj("map",    (30, 560, 200, 110),   MoveTo("map"),             "지도"),
        Obj("well",   (560, 330, 160, 200),  Interact("square_well"),   "우물"),
        Obj("notice", (900, 250, 150, 200),  Interact("square_notice"), "마을 게시판"),
    ]
    OBJECTS["tavern"] = [
        Obj("exit",   (30, 200, 150, 450),   MoveTo("map"),             "밖으로"),
        Obj("board",  (380, 120, 200, 220),  Interact("tavern_board"),  "의뢰 게시판"),
        Obj("cellar", (1000, 330, 150, 300), Interact("tavern_cellar"), "지하 창고",
            when=lambda: MARTHA.is_state("cellar")),
    ]
    OBJECTS["shop"] = [
        Obj("exit",  (30, 200, 150, 450),  MoveTo("map"),           "밖으로"),
        Obj("shelf", (380, 150, 320, 300), Interact("shop_shelf"),  "진열장"),
    ]

    ## ---------------------------------------------------------------- 숲과 동굴
    OBJECTS["forest"] = [
        Obj("town", (30, 520, 220, 160),   MoveTo("map"),           "마을로"),
        Obj("cave", (880, 180, 260, 300),  MoveTo("cave_1"),        "이끼 동굴"),
        Obj("bush", (380, 430, 260, 170),  Interact("forest_bush"), "수풀"),
    ]
    OBJECTS["cave_1"] = [
        Obj("exit",   (30, 300, 180, 380),  MoveTo("forest"),         "밖으로"),
        Obj("deeper", (820, 150, 280, 360), MoveTo("cave_2"),         "더 깊이"),
        Obj("chest",  (480, 470, 200, 150), Interact("cave_chest"),   "낡은 상자",
            when=lambda: not store.cave_chest_opened),
    ]
    OBJECTS["cave_2"] = [
        Obj("back", (30, 300, 180, 380), MoveTo("cave_1"), "돌아가기"),
    ]

    ## ---------------------------------------------------------------- NPC 가 서는 자리
    ## 위치표(Machine.schedule)상 그 장소에 있을 때 이 x 위치에 선다.
    NPC_SPOTS["guild_kitchen"] = {"ruby": 0.58}
    NPC_SPOTS["guild_hall"]    = {"ruby": 0.66}
    NPC_SPOTS["tavern"]        = {"martha": 0.66}
    NPC_SPOTS["shop"]          = {"pip": 0.68}
    NPC_SPOTS["square"]        = {"pip": 0.62}

default cave_chest_opened = False
