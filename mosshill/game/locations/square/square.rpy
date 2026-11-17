## ============================================================================
## locations/square/square.rpy — 마을 광장
## ============================================================================

init -5 python:
    place("square", "마을 광장", parent="map")
    OBJECTS["square"] = [
        Obj("map",    (0, 560, 381, 161),   MoveTo("map"),             "지도"),
        Obj("well",   (437, 130, 424, 439), Interact("square_well"),   "우물"),
        Obj("notice", (906, 200, 265, 331), Interact("square_notice"), "마을 게시판"),
    ]
    NPC_SPOTS["square"] = {"pip": 0.28}           # 저녁: 술통에 앉아 동전 세기

label square_well:
    think "마을 우물. 동전을 던지면 소원이 이루어진다는데… 그럴 돈이 없다."
    jump main_loop

label square_notice:
    think "마을 게시판: '이끼 동굴 출입 주의 — 큰 두꺼비 목격'"
    jump main_loop
