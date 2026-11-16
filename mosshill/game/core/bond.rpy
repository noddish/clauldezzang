## ============================================================================
## core/bond.rpy — 신뢰도 (루비만, 0~100)
## 30 / 60 에서 대사와 합동 스킬이 열린다 (기획서 5-4).
## ============================================================================

default bond = {"ruby": 0}
define BOND_NAMES = {"ruby": "루비"}

init -20 python:
    def add_bond(who, amount):
        before = store.bond.get(who, 0)
        after = max(0, min(100, before + amount))
        store.bond[who] = after
        if amount:
            renpy.notify("%s 신뢰도 %+d  (%d)" % (BOND_NAMES.get(who, who), amount, after))
        return after

    def bond_at_least(who, value):
        return store.bond.get(who, 0) >= value
