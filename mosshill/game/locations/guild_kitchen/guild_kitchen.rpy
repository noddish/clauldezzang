## ============================================================================
## locations/guild_kitchen/guild_kitchen.rpy — 부엌
## ============================================================================

init -5 python:
    place("guild_kitchen", "부엌", parent="guild_hall")
    OBJECTS["guild_kitchen"] = [
        Obj("back",   (0, 0, 206, 563),   MoveTo("guild_hall"),     "길드 홀로"),
        Obj("pantry", (1148, 0, 132, 651), Interact("guild_pantry"), "찬장"),
        Obj("hearth", (910, 0, 236, 549), Interact("guild_stove"),  "화덕"),
    ]
    NPC_SPOTS["guild_kitchen"] = {"ruby": 0.50}   # 아침: 식탁 뒤에서 당근 썰기

label guild_pantry:
    think "찬장에 빵과 치즈가 조금 있다. 길드 재정이 눈에 보인다."
    jump main_loop

label guild_stove:
    think "화덕 위 냄비에 루비가 끓인 수프가 남아 있다."
    jump main_loop
