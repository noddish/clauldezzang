## ============================================================================
## locations/map/map.rpy — 마을 지도 (장소 트리의 뿌리)
##
##   map (마을 지도)
##   ├─ guild_hall 길드 홀 ─┬─ guild_room 내 방 (2층)
##   │                     └─ guild_kitchen 부엌
##   ├─ square 마을 광장
##   ├─ tavern 선술집 '졸린 곰'
##   ├─ shop 핍의 잡화점
##   └─ forest 숲길 ── cave_1 이끼 동굴 ── cave_2 두꺼비 왕의 방
##
## 장소 1곳 = 폴더 1개 (원작 방식). 각 장소 파일에 그 장소의 모든 것이 있다:
##   place()        장소 등록 (이름, 부모)
##   OBJECTS        클릭할 물건 — rect 는 배경 속 물건의 테두리 상자 (1280x720),
##                  실제 클릭 모양은 images/objects/mask_<장소>_<물건>.png (tools/art_objects.json 에서 생성).
##                  물건을 옮기면 art_objects.json 을 고치고 art_pipeline.py object 를 돌린 뒤 rect 도 맞춘다
##                  (자동 검사 m0 가 마스크 크기와 rect 가 다르면 실패로 잡는다).
##   NPC_SPOTS      위치표(Machine.schedule)상 여기 있는 인물. images/scenes/ 에 장소용 그림이 있으면 그 그림,
##                  없으면 대화용 큰 그림을 x 위치(0~1)에 세운다.
##   event(...)     진입·강제 이벤트 (core/events.rpy)
##   label          물건을 눌렀을 때, 이벤트 내용
## ============================================================================

init -5 python:
    place("map", "마을 지도")
    OBJECTS["map"] = [
        Obj("guild",  (180, 320, 321, 281), MoveTo("guild_hall"), "길드하우스"),
        Obj("square", (490, 245, 321, 166), MoveTo("square"),     "마을 광장"),
        Obj("tavern", (720, 20, 326, 246),  MoveTo("tavern"),     "선술집"),
        Obj("shop",   (840, 370, 346, 246), MoveTo("shop"),       "잡화점"),
        Obj("forest", (200, 30, 251, 161),  MoveTo("forest"),     "숲길"),
    ]
