## ============================================================================
## locations/forest/forest.rpy — 숲길
## ============================================================================

init -5 python:
    place("forest", "숲길", parent="map")
    OBJECTS["forest"] = [
        Obj("town", (0, 30, 371, 621),    MoveTo("map"),           "마을로"),
        Obj("cave", (975, 190, 241, 281), MoveTo("cave_1"),        "이끼 동굴"),
        Obj("bush", (375, 250, 496, 311), Interact("forest_bush"), "수풀"),
    ]
    event("forest_slimes", "forest_slime_story", at="forest", once=False, priority=10,
          when=lambda: MAIN.is_state("forest"))
    event("forest_first", "forest_first_look", at="forest",
          when=lambda: first_visit() and not MAIN.is_state("forest"))

label forest_slime_story:
    scene expression location_backdrop(here, blur=True)
    show kai at stage_left
    show ruby at stage_right
    with dissolve
    r "저기 봐, 슬라임이야! 길드장님, 첫 실전이지? 내 뒤에 바짝 붙어!"
    hide ruby
    hide kai
    call battle("forest", group=1)
    if _return == "win":
        $ MAIN.trigger("T_slimes_done")
        $ tick()
        scene expression location_backdrop(here, blur=True)
        show kai happy at stage_left
        show ruby happy at stage_right
        with dissolve
        r "해냈다! 마르타한테 보고하러 가자!"
        hide ruby
        hide kai
    return

label forest_first_look:
    think "약초 냄새가 나는 숲길이다."
    return

label forest_bush:
    think "수풀을 헤쳐 봤다…"
    call battle("forest")
    $ tick()
    jump main_loop
