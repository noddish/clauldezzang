"""아군 자동 행동 규칙 — 밸런스 시뮬레이터와 자동 플레이 테스트가 쓴다.
'평범한 플레이어가 할 법한' 선택을 흉내 낸다 (최적 플레이가 아님).
"""


def ally_command(b, u):
    allies = b.living("ally")
    foes = b.living("enemy")
    skills = b.usable_skills(u)
    items = b.usable_items()
    hurt = sorted(allies, key=lambda a: a.hp / float(a.max_hp))
    weakest = hurt[0]

    # 1) 누가 위험하면 회복
    if weakest.hp < weakest.max_hp * 0.35:
        if "first_aid" in skills:
            return ("skill", "first_aid", weakest.uid)
        for heal in ("hi_potion", "potion"):
            if heal in items:
                return ("item", heal, weakest.uid)

    # 2) 독이면 해독초 (여유 있을 때)
    for a in allies:
        if "poison" in a.status and "antidote" in items and a.hp < a.max_hp * 0.6:
            return ("item", "antidote", a.uid)

    target = min(foes, key=lambda f: f.hp)
    boss = next((f for f in foes if f.boss), None)

    # 3) 보스에게는 강한 단일기 (약점이면 더더욱)
    if boss:
        for s in ("duo_strike", "flame_slash"):
            if s in skills:
                return ("skill", s, boss.uid)
        if "taunt" in skills and u.uid == "player" and not any("taunt" in a.status for a in allies) \
                and any(a.uid == "ruby" and a.hp < a.max_hp * 0.6 for a in allies):
            return ("skill", "taunt", u.uid)

    # 4) 적이 여럿이면 전체기
    if len(foes) >= 2 and "spin_slash" in skills:
        return ("skill", "spin_slash", None)

    return ("attack", (boss or target).uid)
