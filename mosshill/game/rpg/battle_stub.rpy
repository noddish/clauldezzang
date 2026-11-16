## ============================================================================
## rpg/battle_stub.rpy — 전투 임시판 (M2 에서 파티 턴제로 교체)
## 지금은 조우표(data/encounters.json)에서 적을 읽어 이름만 보여주고 자동 승리.
## 호출하는 쪽은 M2 이후에도 그대로:  call battle("forest")  →  _return == "win"
## ============================================================================

label battle(zone):
    $ _group = DATA.encounters[zone]["groups"][0]["enemies"]
    $ _names = ", ".join(DATA.enemies[e]["name"] for e in _group)
    scene expression Placeholder("전투 — " + _names, "#5a2a2a")
    with vpunch
    n "[_names]와(과) 전투! (전투 시스템은 M2 에서 — 지금은 자동 승리)"
    $ add_gold(sum(DATA.enemies[e]["gold"] for e in _group))
    return "win"
