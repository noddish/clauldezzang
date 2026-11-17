## ============================================================================
## rpg/battle_screens.rpy — 전투 화면 (상태창, 명령 메뉴, 대상 선택)
## ============================================================================

style battle_frame:
    background Frame(Solid("#0c0e18e0"), 8, 8)
    padding (16, 12)

## 전투·상점·소지품 화면의 버튼 글자 (기본 회색은 어두운 배경에서 잘 안 보인다)
style mh_button_text:
    idle_color "#e8e8f0"
    hover_color "#ffd38a"
    selected_color "#ffd38a"
    insensitive_color "#5e6070"
    size 24

screen battle_bar(value, maximum, color, width=230):
    fixed:
        xysize (width, 12)
        add Solid("#ffffff22")
        add Solid(color) xsize max(0, int(width * value / float(max(1, maximum))))

## ---------------------------------------------------------------- 상태창 (항상)
screen battle_hud(b, actor=None):
    zorder 20
    if battle_msg:
        frame:
            style "battle_frame"
            xalign 0.5 ypos 14
            text battle_msg size 26 color "#ffffff"

    frame:
        style "battle_frame"
        xpos 12 yalign 1.0 yoffset -12 xsize 620
        vbox:
            spacing 8
            for u in b.allies:
                hbox:
                    spacing 14
                    text ("▶ " if actor is u else "   ") + u.name size 22 color ("#ffd38a" if actor is u else "#ffffff") min_width 140
                    vbox:
                        text "HP %d/%d" % (u.hp, u.max_hp) size 16 color "#ffffff"
                        use battle_bar(u.hp, u.max_hp, "#3fb36b" if u.hp > u.max_hp * 0.3 else "#e0584f")
                    vbox:
                        text "MP %d/%d" % (u.mp, u.max_mp) size 16 color "#ffffff"
                        use battle_bar(u.mp, u.max_mp, "#4a8ae8", 140)
                    text " ".join({"poison": "독", "stun": "기절", "taunt": "도발"}[s] for s in u.status) size 18 color "#d89cff"

    ## 적 이름과 HP 바 (머리 위)
    for e in b.enemies:
        if e.alive:
            $ ex, ey = unit_pos(b, e)
            vbox:
                xcenter ex ypos (ey - (380 if e.boss else 240))
                text e.name size 18 color "#ffffff" xalign 0.5 outlines [(2, "#000000", 0, 0)]
                use battle_bar(e.hp, e.max_hp, "#e0584f", 160 if not e.boss else 300)


## ---------------------------------------------------------------- 명령 메뉴
screen battle_command(b, actor):
    zorder 30
    default mode = "main"         # main / skill / item / target
    default pending = None        # ("attack"|"skill"|"item", id, 대상 종류)

    use battle_hud(b, actor)

    frame:
        style "battle_frame"
        style_prefix "mh"
        xalign 1.0 yalign 1.0 xoffset -12 yoffset -12 xsize 560

        if mode == "main":
            grid 3 2:
                spacing 10
                textbutton "공격" action [SetScreenVariable("pending", ("attack", None, "enemy")), SetScreenVariable("mode", "target")]
                textbutton "기술" action SetScreenVariable("mode", "skill") sensitive bool(actor.skills)
                textbutton "아이템" action SetScreenVariable("mode", "item") sensitive bool(b.usable_items())
                textbutton "방어" action Return(("guard",))
                textbutton "도망" action Return(("escape",)) sensitive b.can_escape
                null

        elif mode == "skill":
            vbox:
                spacing 6
                for sid in actor.skills:
                    $ sk = DATA.skills[sid]
                    $ need_target = sk["target"] in ("enemy", "ally")
                    textbutton "%s  (MP %d) — %s" % (sk["name"], sk["mp"], sk["desc"]):
                        sensitive sk["mp"] <= actor.mp
                        text_size 20
                        if need_target:
                            action [SetScreenVariable("pending", ("skill", sid, sk["target"])), SetScreenVariable("mode", "target")]
                        else:
                            action Return(("skill", sid, None))
                textbutton "← 뒤로" action SetScreenVariable("mode", "main")

        elif mode == "item":
            vbox:
                spacing 6
                for iid in b.usable_items():
                    $ it = DATA.items[iid]
                    $ need_target = it.get("target", "ally") in ("enemy", "ally")
                    textbutton "%s x%d — %s" % (it["name"], b.items[iid], it["desc"]):
                        text_size 20
                        if need_target:
                            action [SetScreenVariable("pending", ("item", iid, it.get("target", "ally"))), SetScreenVariable("mode", "target")]
                        else:
                            action Return(("item", iid, None))
                textbutton "← 뒤로" action SetScreenVariable("mode", "main")

        elif mode == "target":
            vbox:
                spacing 6
                text "대상을 고르세요" size 20 color "#ffd38a"
                textbutton "← 뒤로" action [SetScreenVariable("mode", "main"), SetScreenVariable("pending", None)]

    ## 대상 선택: 유닛 위에 클릭 영역
    if mode == "target" and pending:
        $ kind, pid, tkind = pending
        $ targets = b.living("enemy") if tkind == "enemy" else b.living("ally")
        for t in targets:
            $ tx, ty = unit_pos(b, t)
            button:
                xcenter tx ypos ty yanchor 1.0 xysize (220, 420 if t.side == "ally" or t.boss else 240)
                background Frame(Solid("#ffe08a33"), 4, 4)
                hover_background Frame(Solid("#ffe08a88"), 4, 4)
                if kind == "attack":
                    action Return(("attack", t.uid))
                else:
                    action Return((kind, pid, t.uid))
