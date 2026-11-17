## ============================================================================
## locations/shop/shop.rpy — 핍의 잡화점 (상점 화면은 rpg/shop.rpy)
## ============================================================================

init -5 python:
    place("shop", "핍의 잡화점", parent="map")
    OBJECTS["shop"] = [
        Obj("exit",  (0, 10, 161, 616),  MoveTo("map"),          "밖으로"),
        Obj("shelf", (205, 0, 396, 581), Interact("shop_shelf"), "진열장"),
    ]
    NPC_SPOTS["shop"] = {"pip": 0.70}             # 계산대 뒤에서 금화를 눈앞에 들고 살피기

label shop_shelf:
    call screen shop_view("pip")
    jump main_loop
