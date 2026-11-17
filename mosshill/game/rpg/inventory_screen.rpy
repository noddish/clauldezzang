## ============================================================================
## rpg/inventory_screen.rpy — 소지품 · 장비 화면 (HUD 의 "소지품")
## 왼쪽: 파티원 스탯과 장비 / 오른쪽: 소모품·장비·중요 아이템
## ============================================================================

define SLOT_NAMES = {"weapon": "무기", "armor": "방어구", "accessory": "장신구"}
define TYPE_TABS = [("consumable", "소모품"), ("equip", "장비"), ("key", "중요"), ("material", "재료")]

init -20 python:
    def items_of(tab):
        out = []
        for iid, n in sorted(store.inventory.items()):
            t = DATA.items[iid]["type"]
            if (tab == "equip" and t in SLOT_NAMES) or t == tab:
                out.append((iid, n))
        return out

    def use_item_field(iid, who):
        """전투 밖에서 소모품 사용"""
        eff = DATA.items[iid].get("effect", {})
        m = store.party[who]
        used = False
        if "heal_hp" in eff:
            hp, mx = member_hp(who)
            if hp < mx:
                m["hp"] = min(mx, hp + eff["heal_hp"])
                used = True
        if "heal_mp" in eff:
            mp, mx = member_mp(who)
            if mp < mx:
                m["mp"] = min(mx, mp + eff["heal_mp"])
                used = True
        if not used:
            renpy.notify("지금은 쓸 필요가 없다.")
            return
        remove_item(iid)
        renpy.notify("%s 에게 %s 사용" % (member_name(who), DATA.items[iid]["name"]))

    def equip_item(who, iid):
        slot = DATA.items[iid]["type"]
        m = store.party[who]
        old = m["equip"].get(slot)
        if not remove_item(iid):
            return
        m["equip"][slot] = iid
        if old:
            add_item(old, notify=False)
        renpy.notify("%s: %s 장착" % (member_name(who), DATA.items[iid]["name"]))

    def unequip_item(who, slot):
        m = store.party[who]
        old = m["equip"].get(slot)
        if old:
            m["equip"][slot] = None
            add_item(old, notify=False)

    def field_usable(iid):
        eff = DATA.items[iid].get("effect", {})
        return "heal_hp" in eff or "heal_mp" in eff


## 아이템 아이콘 (images/items/icon_<id>.png, 96x96) — 없으면 빈칸
screen item_icon(iid, size=44):
    if renpy.has_image("icon_" + iid):
        add Transform("icon_" + iid, zoom=size / 96.0) yalign 0.5
    else:
        null width size height size


label open_inventory:
    call screen inventory_view
    jump main_loop


screen inventory_view():
    modal True
    zorder 50
    default who = "player"
    default tab = "consumable"

    add Solid("#000000b0")
    frame:
        style "battle_frame"
        style_prefix "mh"
        xalign 0.5 yalign 0.5 xsize 1180 ysize 640
        hbox:
            spacing 24

            ## ---- 파티원
            vbox:
                xsize 470 spacing 12
                text "파티" size 26 color "#ffd38a"
                for w in PARTY_ORDER:
                    $ s = member_stats(w)
                    $ hp, mhp = member_hp(w)
                    $ mp, mmp = member_mp(w)
                    frame:
                        background Frame(Solid("#ffd38a30" if who == w else "#ffffff10"), 4, 4)
                        padding (12, 10)
                        xfill True
                        vbox:
                            spacing 4
                            hbox:
                                spacing 12
                                text "%s  Lv %d" % (member_name(w), party[w]["lv"]) size 22 color "#ffffff"
                                text "경험치 %d" % party[w]["exp"] size 16 color "#aaaaaa" yalign 0.5
                                if who != w:
                                    textbutton "선택" action SetScreenVariable("who", w) text_size 18
                                else:
                                    text "선택됨" size 18 color "#ffd38a" yalign 0.5
                            text "HP %d/%d   MP %d/%d" % (hp, mhp, mp, mmp) size 18 color "#bcd7ff"
                            text "공격 %d   방어 %d   속도 %d" % (s["atk"], s["def"], s["spd"]) size 18 color "#ffffff"
                            for slot in ("weapon", "armor", "accessory"):
                                $ eq = party[w]["equip"].get(slot)
                                hbox:
                                    spacing 8
                                    text "%s: %s" % (SLOT_NAMES[slot], DATA.items[eq]["name"] if eq else "없음") size 17 color "#dddddd" yalign 0.5
                                    if eq:
                                        textbutton "해제" text_size 15 action Function(unequip_item, w, slot)
                text "오른쪽에서 '사용'·'장착'을 누르면 선택된 사람에게 적용" size 15 color "#aaaaaa"

            ## ---- 아이템
            vbox:
                xsize 640 spacing 10
                hbox:
                    spacing 8
                    for key, label in TYPE_TABS:
                        textbutton label action SetScreenVariable("tab", key) selected tab == key
                    null width 20
                    text "%d 골드" % gold size 20 color "#ffd38a" yalign 0.5
                viewport:
                    ysize 470 scrollbars "vertical" mousewheel True
                    vbox:
                        spacing 6
                        for iid, cnt in items_of(tab):
                            $ it = DATA.items[iid]
                            hbox:
                                spacing 12
                                use item_icon(iid)
                                text "%s x%d" % (it["name"], cnt) size 20 color "#ffffff" min_width 170 yalign 0.5
                                text it["desc"] size 16 color "#bbbbbb" xsize 280 yalign 0.5
                                if tab == "consumable" and field_usable(iid):
                                    textbutton "사용" action Function(use_item_field, iid, who)
                                elif tab == "equip":
                                    textbutton "장착" action Function(equip_item, who, iid)
                        if not items_of(tab):
                            text "없음" size 18 color "#888888"
                textbutton "닫기" action Return(True) xalign 1.0
