## ============================================================================
## rpg/inventory.rpy — 소지품과 돈 (M1: 최소 기능. 화면·장비·상점은 M2)
##
## 아이템은 data/items.json 의 id 로만 다룬다:  add_item("potion", 2)
## ============================================================================

default gold = 50
default inventory = {}      # 아이템 id → 개수

init -20 python:
    def add_item(item_id, count=1, notify=True):
        if item_id not in DATA.items:
            raise Exception("없는 아이템 id: %s" % item_id)
        store.inventory[item_id] = store.inventory.get(item_id, 0) + count
        if notify:
            renpy.notify("%s 획득%s" % (DATA.items[item_id]["name"], "" if count == 1 else " x%d" % count))

    def remove_item(item_id, count=1):
        have = store.inventory.get(item_id, 0)
        if have < count:
            return False
        if have == count:
            del store.inventory[item_id]
        else:
            store.inventory[item_id] = have - count
        return True

    def has_item(item_id, count=1):
        return store.inventory.get(item_id, 0) >= count

    def add_gold(amount):
        store.gold = max(0, store.gold + amount)
        if amount:
            renpy.notify("%+d 골드  (보유 %d)" % (amount, store.gold))
