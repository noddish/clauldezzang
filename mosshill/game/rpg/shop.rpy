## ============================================================================
## rpg/shop.rpy — 상점 (data/shops.json)
## 품목(stock)은 사고, buys 목록에 있는 것은 판다 (가격 × sell_rate).
## ============================================================================

init -20 python:
    def shop_buy(shop_id, iid):
        price = DATA.items[iid]["price"]
        if store.gold < price:
            renpy.notify("골드가 부족하다.")
            return
        store.gold -= price
        add_item(iid, notify=False)
        renpy.notify("%s 구입 (-%d 골드)" % (DATA.items[iid]["name"], price))

    def sell_price(shop_id, iid):
        return int(DATA.items[iid]["price"] * DATA.shops[shop_id]["sell_rate"])

    def shop_sell(shop_id, iid):
        if remove_item(iid):
            store.gold += sell_price(shop_id, iid)
            renpy.notify("%s 판매 (+%d 골드)" % (DATA.items[iid]["name"], sell_price(shop_id, iid)))

    def sellable(shop_id):
        buys = DATA.shops[shop_id]["buys"]
        return [(iid, n) for iid, n in sorted(store.inventory.items()) if iid in buys]


screen shop_view(shop_id):
    modal True
    zorder 50
    $ shop = DATA.shops[shop_id]
    add Solid("#000000b0")
    frame:
        style "battle_frame"
        style_prefix "mh"
        xalign 0.5 yalign 0.5 xsize 1180 ysize 620
        vbox:
            spacing 12
            hbox:
                text shop["name"] size 28 color "#ffd38a"
                null width 40
                text "보유 %d 골드" % gold size 22 color "#ffffff" yalign 0.5
            hbox:
                spacing 30
                vbox:
                    xsize 640 spacing 6
                    text "사기" size 22 color "#bcd7ff"
                    for iid in shop["stock"]:
                        $ it = DATA.items[iid]
                        $ owned = inventory.get(iid, 0)
                        hbox:
                            spacing 10
                            use item_icon(iid)
                            textbutton "%s  %dG" % (it["name"], it["price"]):
                                action Function(shop_buy, shop_id, iid)
                                sensitive gold >= it["price"]
                                text_size 20 xsize 220 yalign 0.5
                            text "%s%s" % (it["desc"], (" (보유 %d)" % owned) if owned else "") size 16 color "#bbbbbb" xsize 340 yalign 0.5
                vbox:
                    xsize 440 spacing 6
                    text "팔기" size 22 color "#bcd7ff"
                    for iid, cnt in sellable(shop_id):
                        textbutton "%s x%d  →  %dG" % (DATA.items[iid]["name"], cnt, sell_price(shop_id, iid)):
                            action Function(shop_sell, shop_id, iid)
                            text_size 20
                    if not sellable(shop_id):
                        text "팔 물건이 없다" size 18 color "#888888"
            textbutton "나가기" action Return(True) xalign 1.0
