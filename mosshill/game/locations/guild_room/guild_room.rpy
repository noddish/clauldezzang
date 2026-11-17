## ============================================================================
## locations/guild_room/guild_room.rpy — 내 방 (2층)
## ============================================================================

init -5 python:
    place("guild_room", "내 방", parent="guild_hall")
    OBJECTS["guild_room"] = [
        Obj("door", (1065, 30, 216, 541), MoveTo("guild_hall"),  "1층으로"),
        Obj("bed",  (0, 262, 491, 399),   Interact("guild_bed"),  "침대 (자기)"),
        Obj("desk", (580, 240, 356, 301), Interact("guild_desk"), "책상"),
    ]

label guild_bed:
    if tod < 2:
        think "아직 잘 시간은 아니다."
        jump main_loop
    think "오늘은 이만 자자."
    scene black
    with fade
    $ sleep_to_next_day()
    scene expression location_bg(here)
    with fade
    n "[day]일차 아침이 밝았다."
    jump main_loop

label guild_desk:
    if RUBY.is_state("flint_lost"):
        think "책상 서랍 안쪽에… 있다. 루비의 부싯돌이다."
        $ add_item("flint")
        $ RUBY.trigger("T_found")
    else:
        think "삼촌의 길드 일지다. 마지막 장에 '루비를 잘 부탁한다'라고 적혀 있다."
    jump main_loop
