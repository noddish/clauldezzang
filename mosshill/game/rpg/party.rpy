## ============================================================================
## rpg/party.rpy — 파티 (주인공 + 루비)
##
## 파티원 상태는 저장 가능한 dict (mhrpg.new_member 참고):
##   party["ruby"] = {"lv": 1, "exp": 0, "hp": None, "mp": None, "equip": {...}}
## 계산(레벨·스탯·스킬)은 game/python-packages/mhrpg 가 한다 — 시뮬레이터와 같은 코드.
## ============================================================================

init -60 python:
    import mhrpg
    import mhrpg.stats

## RPG 는 HP·소지품이 되감기(rollback)와 어긋나기 쉬워서 되감기를 끈다.
define config.rollback_enabled = False

define PARTY_ORDER = ["player", "ruby"]

default party = {
    "player": mhrpg.new_member("short_sword", "leather_vest"),
    "ruby":   mhrpg.new_member("ruby_blade", "leather_vest"),
}

init -20 python:
    def member_name(who):
        return store.player_name if who == "player" else CHAR_NAMES.get(who, who)

    def party_flags():
        return {"ruby_flame": store.ruby_flame, "bond": store.bond.get("ruby", 0)}

    def member_stats(who):
        return mhrpg.stats.total_stats(DATA, who, store.party[who])

    def member_hp(who):
        m = store.party[who]
        s = member_stats(who)
        return (s["hp"] if m["hp"] is None else m["hp"]), s["hp"]

    def member_mp(who):
        m = store.party[who]
        s = member_stats(who)
        return (s["mp"] if m["mp"] is None else m["mp"]), s["mp"]

    def party_units():
        return [mhrpg.build_unit(DATA, who, member_name(who), store.party[who], party_flags())
                for who in PARTY_ORDER]

    def heal_party():
        for m in store.party.values():
            m["hp"] = None
            m["mp"] = None

    SLEEP_HOOKS.append(heal_party)      # 잠자면 전부 회복
