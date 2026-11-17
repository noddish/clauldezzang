## ============================================================================
## locations/tavern/tavern.rpy — 선술집 '졸린 곰'
## ============================================================================

init -5 python:
    place("tavern", "선술집 '졸린 곰'", parent="map")
    OBJECTS["tavern"] = [
        Obj("exit",   (0, 74, 161, 532),   MoveTo("map"),             "밖으로"),
        Obj("board",  (222, 142, 161, 244), Interact("tavern_board"),  "의뢰 게시판"),
        Obj("cellar", (1125, 385, 155, 204), Interact("tavern_cellar"), "지하 창고",
            when=lambda: MARTHA.is_state("cellar")),
    ]
    NPC_SPOTS["tavern"] = {"martha": 0.55}        # 바 뒤에서 잔 닦기

label tavern_board:
    if MAIN.is_state("board"):
        think "의뢰 게시판에 '숲길 슬라임 퇴치'가 붙어 있다. 마르타에게 물어보자."
    else:
        think "지금은 받을 만한 의뢰가 없다."
    jump main_loop

label tavern_cellar:
    think "지하 창고 문을 열자 끈적한 소리가 들린다."
    call battle("tavern_cellar")
    if _return == "win":
        $ MARTHA.trigger("T_cleared")
        $ tick()
    jump main_loop
