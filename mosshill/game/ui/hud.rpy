## ============================================================================
## ui/hud.rpy — 화면 위 정보 (원작 screen ui)
## 왼쪽 위: 날짜·시간대·장소·골드 / 오른쪽 위: 진행 중인 퀘스트 / 오른쪽 아래: 시간 보내기
## ============================================================================

style hud_frame:
    background Frame(Solid("#0c0e18c8"), 8, 8)
    padding (16, 10)
style hud_text:
    size 20
    color "#ffffff"
## 오른쪽 아래 버튼: 밝은 배경 위에서도 보이게 어두운 바탕
style hud_button:
    background Frame(Solid("#0c0e18c8"), 8, 8)
    hover_background Frame(Solid("#3a2e18e0"), 8, 8)
    padding (18, 10)
style hud_button_text:
    size 22
    idle_color "#ffffff"
    hover_color "#ffd38a"

screen hud():
    frame:
        style "hud_frame"
        xalign 0.0 yalign 0.0 xoffset 12 yoffset 12
        vbox:
            text time_label() size 24 bold True color "#ffffff"
            text LOC[here].name size 19 color "#bcd7ff"
            text "%d 골드" % gold size 17 color "#ffd38a"

    $ quests = active_quests()
    if quests:
        frame:
            style "hud_frame"
            xalign 1.0 yalign 0.0 xoffset -12 yoffset 12 xmaximum 520
            vbox:
                spacing 6
                for title, hint in quests:
                    vbox:
                        text title size 15 color "#ffd38a"
                        text hint size 18 color "#ffffff"

    hbox:
        xalign 1.0 yalign 1.0 xoffset -12 yoffset -12 spacing 10
        textbutton "소지품" action Jump("open_inventory") style "hud_button"
        textbutton "시간 보내기" action WaitTick() style "hud_button"

    $ tip = GetTooltip()
    if tip:
        frame:
            style "hud_frame"
            xalign 0.5 yalign 1.0 yoffset -16
            text tip size 22 color "#ffffff"


## ---------------------------------------------------------------- 알림 위치
## renpy.notify 기본 위치(왼쪽 위)는 HUD 와 겹치므로 위쪽 가운데로 옮긴다.
style notify_frame:
    xalign 0.5
    ypos 76            # 전투 메시지(위쪽 가운데) 아래
