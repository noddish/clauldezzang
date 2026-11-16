## ============================================================================
## locations/home_locations.rpy — 장소 트리 (Summertime Saga location_init.rpy 와 같은 방식)
##
##   L_home_bedroom (내 방)
##     └ L_home_hallway (2층 복도)          ← 내 방의 부모
##          └ L_home_entrance (1층 현관)
##               ├ L_home_kitchen   (부엌)
##               └ L_home_livingroom (거실)
##
## 원작: L_home_bedroom = Location("Bedroom", background="home_bedroom", parents=[L_home_hallway, L_map])
## ============================================================================

init -5 python:
    L_home_entrance   = Location("1층 현관",  "home_entrance{}")
    L_home_hallway    = Location("2층 복도",  "home_hallway{}",    parent=L_home_entrance)
    L_home_bedroom    = Location("내 방",     "home_bedroom{}",    parent=L_home_hallway)
    L_home_kitchen    = Location("부엌",      "home_kitchen{}",    parent=L_home_entrance)
    L_home_livingroom = Location("거실",      "home_livingroom{}", parent=L_home_entrance)

    ## 이 데모에 배경이 없는 곳 — 잠긴 장소로만 존재 (lock check 에서 막힘)
    L_home_bathroom   = Location("욕실",      "home_bathroom{}",   parent=L_home_hallway, locked=True)
    L_town_map        = Location("마을",      "town_map{}",        locked=True)


## ----------------------------------------------------------------- 오브젝트 위치
## tools/cut_objects.py 가 배경에서 오려낸 조각의 왼쪽 위 좌표 (objects_pos.json 과 같음)
define OBJ_POS = {
    "bedroom_door": (1100, 0), "bedroom_bed": (0, 250), "bedroom_desk": (635, 225),
    "hallway_mydoor": (210, 0), "hallway_bath": (1035, 0), "hallway_stairs": (535, 270),
    "entrance_stairs": (175, 5), "entrance_door": (612, 85), "entrance_kitchen": (985, 25), "entrance_living": (0, 40),
    "kitchen_back": (30, 30), "kitchen_fridge": (1110, 0), "kitchen_stove": (935, 290),
    "living_door": (1125, 40), "living_couch": (300, 200), "living_tv": (0, 120),
}

init python:
    def obj(name):
        """낮/밤에 맞는 오브젝트 그림 (원작의 game.timer.image("objects/object_door_01{}.png"))"""
        return "images/objects/object_%s_%s.png" % (name, "night" if game.timer.is_dark() else "day")
