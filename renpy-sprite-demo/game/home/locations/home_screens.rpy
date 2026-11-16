## ============================================================================
## locations/home_screens.rpy — 장소마다 screen 하나 (원작 locations/*/screens.rpy)
##
## 원작 패턴:
##   screen park():
##       add L_park.background                                  ← 통짜 배경
##       imagebutton pos (318,377) idle game.timer.image("objects/object_fountain_01{}.png")
##                   hover HoverImage(...) action MoveTo(L_park_fountain)   ← 오려낸 물건 = 버튼
##       if L_park.is_here(M_eve):
##           imagebutton ... action TalkTo(M_eve)              ← 위치표상 여기 있으면 캐릭터 표시
## ============================================================================

transform obj_hover:
    matrixcolor BrightnessMatrix(0.18)

## 오브젝트 버튼 하나 — 이름, 동작, 마우스 올렸을 때 설명
screen object_button(name, action, tip):
    imagebutton:
        pos OBJ_POS[name]
        idle obj(name)
        hover At(obj(name), obj_hover)
        focus_mask True
        action action
        tooltip tip

## 캐릭터 버튼 (원작: imagebutton idle M_eve.get_button_path(...) action TalkTo(M_eve))
screen npc_button(machine, xcenter_pos):
    imagebutton:
        xcenter xcenter_pos yalign 1.0
        idle At("ruby", npc_size)
        hover At("ruby", npc_size, obj_hover)
        focus_mask True
        action TalkTo(machine)
        tooltip "루비와 대화"

transform npc_size:
    zoom 1.0


## ----------------------------------------------------------------- HUD (원작 screen ui)
screen hud():
    frame:
        xalign 0.0 yalign 0.0 xmargin 12 ymargin 12 padding (16, 10)
        background Frame(Solid("#000000b0"), 8, 8)
        vbox:
            text game.timer.label() size 22 bold True
            text game.location.name size 18 color "#bcd7ff"
    frame:
        xalign 1.0 yalign 0.0 xmargin 12 ymargin 12 padding (16, 10) xmaximum 520
        background Frame(Solid("#000000b0"), 8, 8)
        vbox:
            text "퀘스트" size 16 color "#ffd38a"
            text M_ruby.state.hint size 18
    hbox:
        xalign 1.0 yalign 1.0 xoffset -12 yoffset -12 spacing 10
        textbutton "시간 보내기" action Interact("home_wait") sensitive game.timer.tod < 3
    $ tip = GetTooltip()
    if tip:
        frame:
            xalign 0.5 yalign 1.0 yoffset -16 padding (16, 8)
            background Frame(Solid("#000000c0"), 8, 8)
            text tip size 22


## ----------------------------------------------------------------- 장소별 화면
screen home_bedroom():
    add game.location.bg
    use object_button("bedroom_door", MoveTo(L_home_hallway), "2층 복도로")
    use object_button("bedroom_bed", Interact("home_bed"), "침대 (자기)")
    use object_button("bedroom_desk", Interact("home_desk"), "책상")
    use hud

screen home_hallway():
    add game.location.bg
    use object_button("hallway_mydoor", MoveTo(L_home_bedroom), "내 방")
    use object_button("hallway_bath", MoveTo(L_home_bathroom), "욕실")
    use object_button("hallway_stairs", MoveTo(L_home_entrance), "1층으로 내려가기")
    if L_home_hallway.is_here(M_ruby):
        use npc_button(M_ruby, 0.7)
    use hud

screen home_entrance():
    add game.location.bg
    use object_button("entrance_stairs", MoveTo(L_home_hallway), "2층으로 올라가기")
    use object_button("entrance_door", MoveTo(L_town_map), "밖으로 나가기")
    use object_button("entrance_kitchen", MoveTo(L_home_kitchen), "부엌")
    use object_button("entrance_living", MoveTo(L_home_livingroom), "거실")
    use hud

screen home_kitchen():
    add game.location.bg
    use object_button("kitchen_back", MoveTo(L_home_entrance), "현관으로")
    use object_button("kitchen_fridge", Interact("home_fridge"), "냉장고")
    use object_button("kitchen_stove", Interact("home_stove"), "가스레인지")
    if L_home_kitchen.is_here(M_ruby):
        use npc_button(M_ruby, 0.58)   # 냉장고를 가리지 않게
    use hud

screen home_livingroom():
    add game.location.bg
    use object_button("living_door", MoveTo(L_home_entrance), "현관으로")
    use object_button("living_tv", Interact("home_tv"), "TV")
    use object_button("living_couch", Interact("home_couch"), "소파")
    if L_home_livingroom.is_here(M_ruby):
        use npc_button(M_ruby, 0.7)
    use hud
