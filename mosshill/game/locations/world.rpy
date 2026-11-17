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
## rect 는 배경 그림 속 물건의 테두리 상자 (1280x720). 실제 클릭 모양은
## images/objects/mask_<장소>_<물건>.png — tools/art_objects.json 의 다각형에서 만든다.
## 물건을 옮기려면 art_objects.json 을 고치고 art_pipeline.py object 를 돌린 뒤 여기 rect 도 맞춘다
## (자동 검사 m0 가 마스크 크기와 rect 가 다르면 실패로 잡는다).
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
        Obj("guild",  (180, 320, 321, 281), MoveTo("guild_hall"), "길드하우스"),
        Obj("square", (490, 245, 321, 166), MoveTo("square"),     "마을 광장"),
        Obj("tavern", (720, 20, 326, 246), MoveTo("tavern"),     "선술집"),
        Obj("shop",   (840, 370, 346, 246), MoveTo("shop"),       "잡화점"),
        Obj("forest", (200, 30, 251, 161), MoveTo("forest"),     "숲길"),
    ]

    ## ---------------------------------------------------------------- 길드하우스
    OBJECTS["guild_hall"] = [
        Obj("stairs",  (185, 0, 261, 421),  MoveTo("guild_room"),    "2층 내 방"),
        Obj("door",    (530, 180, 223, 296), MoveTo("map"),           "밖으로"),
        Obj("kitchen", (1125, 175, 116, 306), MoveTo("guild_kitchen"), "부엌"),
        Obj("board",   (812, 190, 245, 217), Interact("guild_board"), "길드 의뢰판"),
        Obj("hearth",  (0, 190, 176, 311),   Interact("guild_hearth"), "벽난로"),
    ]
    OBJECTS["guild_room"] = [
        Obj("door", (1065, 30, 216, 541),  MoveTo("guild_hall"),  "1층으로"),
        Obj("bed",  (0, 262, 491, 399),   Interact("guild_bed"),  "침대 (자기)"),
        Obj("desk", (580, 240, 356, 301),  Interact("guild_desk"), "책상"),
    ]
    OBJECTS["guild_kitchen"] = [
        Obj("back",   (0, 10, 201, 566),    MoveTo("guild_hall"),     "길드 홀로"),
        Obj("pantry", (1135, 0, 146, 657),   Interact("guild_pantry"), "찬장"),
        Obj("hearth", (895, 60, 236, 496),  Interact("guild_stove"),  "화덕"),
    ]

    ## ---------------------------------------------------------------- 마을
    OBJECTS["square"] = [
        Obj("map",    (0, 560, 381, 161),   MoveTo("map"),             "지도"),
        Obj("well",   (437, 130, 424, 439),  Interact("square_well"),   "우물"),
        Obj("notice", (906, 200, 265, 331),  Interact("square_notice"), "마을 게시판"),
    ]
    OBJECTS["tavern"] = [
        Obj("exit",   (0, 131, 196, 357),   MoveTo("map"),             "밖으로"),
        Obj("board",  (259, 160, 240, 216),  Interact("tavern_board"),  "의뢰 게시판"),
        Obj("cellar", (1115, 356, 148, 139), Interact("tavern_cellar"), "지하 창고",
            when=lambda: MARTHA.is_state("cellar")),
    ]
    OBJECTS["shop"] = [
        Obj("exit",  (0, 55, 226, 514),  MoveTo("map"),           "밖으로"),
        Obj("shelf", (320, 15, 346, 516), Interact("shop_shelf"),  "진열장"),
    ]

    ## ---------------------------------------------------------------- 숲과 동굴
    OBJECTS["forest"] = [
        Obj("town", (0, 30, 371, 621),   MoveTo("map"),           "마을로"),
        Obj("cave", (975, 190, 241, 281),  MoveTo("cave_1"),        "이끼 동굴"),
        Obj("bush", (375, 250, 496, 311),  Interact("forest_bush"), "수풀"),
    ]
    OBJECTS["cave_1"] = [
        Obj("exit",   (0, 30, 206, 351),  MoveTo("forest"),         "밖으로"),
        Obj("deeper", (860, 120, 266, 311), MoveTo("cave_2"),         "더 깊이"),
        Obj("chest",  (480, 370, 249, 176), Interact("cave_chest"),   "낡은 상자",
            when=lambda: not store.cave_chest_opened),
    ]
    OBJECTS["cave_2"] = [
        Obj("back", (0, 60, 176, 311), MoveTo("cave_1"), "돌아가기"),
    ]

    ## ---------------------------------------------------------------- NPC 가 있는 곳
    ## 위치표(Machine.schedule)상 그 장소에 있을 때 나타난다.
    ## images/scenes/ 에 그 장소용 그림(원작처럼 그 자리에서 뭔가 하는 모습)이 있으면 그 그림을 쓰고
    ## (tools/art_scenes.json — 자세·시선 메모 포함), 없으면 대화용 큰 그림을 이 x 위치에 세운다.
    ## 큰 그림은 화면 폭의 30% 쯤이라 물건을 가리니 덜 중요한 물건 앞에, 왼쪽 절반이면 좌우를 뒤집는다.
    ## (x 는 장소용 그림이 없을 때만 쓰는 자리)
    NPC_SPOTS["guild_hall"]    = {"ruby": 0.14}      # 벽난로 앞 (저녁) — 의뢰판·문·계단은 비워 둔다
    NPC_SPOTS["guild_kitchen"] = {"ruby": 0.55}      # 식탁과 화덕 사이
    NPC_SPOTS["tavern"]        = {"martha": 0.68}    # 바 앞
    NPC_SPOTS["shop"]          = {"pip": 0.70}       # 계산대 앞
    NPC_SPOTS["square"]        = {"pip": 0.28}       # 우물 왼쪽

default cave_chest_opened = False
