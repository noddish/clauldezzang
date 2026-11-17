## ============================================================================
## locations/cave/cave.rpy — 이끼 동굴 (1층, 두꺼비 왕의 방)
## ============================================================================

default cave_chest_opened = False

init -5 python:
    place("cave_1", "이끼 동굴",      parent="forest", night_bg=False)
    place("cave_2", "두꺼비 왕의 방", parent="cave_1", night_bg=False)
    OBJECTS["cave_1"] = [
        Obj("exit",   (0, 30, 206, 351),    MoveTo("forest"),       "밖으로"),
        Obj("deeper", (860, 120, 266, 311), MoveTo("cave_2"),       "더 깊이"),
        Obj("chest",  (480, 370, 249, 176), Interact("cave_chest"), "낡은 상자",
            when=lambda: not store.cave_chest_opened),
    ]
    OBJECTS["cave_2"] = [
        Obj("back", (0, 60, 176, 311), MoveTo("cave_1"), "돌아가기"),
    ]
    event("cave_first", "cave_first_look", at="cave_1", priority=10, when=lambda: first_visit())
    event("cave_encounter", "cave_random_battle", at="cave_1", once=False,
          when=lambda: encounter_roll("cave_1"))
    event("cave_boss", "cave_boss_battle", at="cave_2", once=False, when=lambda: MAIN.is_state("cave"))

label cave_first_look:
    think "축축하고 미끄러운 동굴이다. 벽의 이끼가 희미하게 빛난다."
    $ tick()
    return

label cave_random_battle:
    n "어둠 속에서 무언가 다가온다!"
    call battle("cave_1")
    return

label cave_chest:
    $ cave_chest_opened = True
    think "낡은 상자 안에 회복약이 들어 있다."
    $ add_item("potion")
    jump main_loop

label cave_boss_battle:
    n "동굴 가장 안쪽, 집채만 한 두꺼비가 짐 꾸러미를 깔고 앉아 있다."
    scene expression location_backdrop(here, blur=True)
    show kai angry at stage_left
    show ruby angry at stage_right
    with dissolve
    r "저 녀석이 핍의 짐을 깔고 앉았어! 가자!"
    hide ruby
    hide kai
    call battle("boss_toad")
    if _return == "win":
        $ add_item("pip_cargo")
        $ MAIN.trigger("T_boss_done")
        $ tick()
    return
