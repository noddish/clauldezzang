## ============================================================================
## locations/guild_hall/guild_hall.rpy — 길드 홀 (1층)
## ============================================================================

init -5 python:
    place("guild_hall", "길드 홀", parent="map")
    OBJECTS["guild_hall"] = [
        Obj("stairs",  (185, 0, 261, 421),    MoveTo("guild_room"),     "2층 내 방"),
        Obj("door",    (530, 180, 223, 296),  MoveTo("map"),            "밖으로"),
        Obj("kitchen", (1125, 175, 116, 306), MoveTo("guild_kitchen"),  "부엌"),
        Obj("board",   (812, 190, 245, 217),  Interact("guild_board"),  "길드 의뢰판"),
        Obj("hearth",  (0, 190, 176, 311),    Interact("guild_hearth"), "벽난로"),
    ]
    NPC_SPOTS["guild_hall"] = {"ruby": 0.14}      # 저녁: 의자에 앉아 칼 손질

label guild_board:
    think "길드 의뢰판. 붙어 있는 건 '고양이 찾음 (해결됨)' 한 장뿐이다."
    jump main_loop

label guild_hearth:
    if ruby_flame:
        think "루비가 부싯돌로 피운 불이 따뜻하게 타오른다."
    else:
        think "불이 꺼진 벽난로. 부싯돌이 있어야 피울 수 있다."
    jump main_loop
