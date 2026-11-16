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
    "bedroom_door": (1110, 0),
    "bedroom_bed": (0, 250),
    "bedroom_desk": (635, 260),
    "hallway_mydoor": (225, 20),
    "hallway_bath": (1045, 20),
    "hallway_stairs": (530, 300),
    "entrance_stairs": (175, 0),
    "entrance_door": (625, 105),
    "entrance_kitchen": (1010, 50),
    "entrance_living": (0, 40),
    "kitchen_back": (35, 40),
    "kitchen_fridge": (1130, 0),
    "kitchen_stove": (955, 230),
    "living_door": (1120, 40),
    "living_couch": (330, 250),
    "living_tv": (0, 170),
}

init python:
    def obj(name):
        """낮/밤에 맞는 오브젝트 그림 (원작의 game.timer.image("objects/object_door_01{}.png"))"""
        return "images/objects/object_%s_%s.png" % (name, "night" if game.timer.is_dark() else "day")
