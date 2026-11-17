"""성장(레벨·경험치·장비)과 전투 유닛 만들기

파티원 상태(member)는 저장 가능한 평범한 dict 다:
    {"lv": 1, "exp": 0, "hp": None, "mp": None,
     "equip": {"weapon": "short_sword", "armor": "leather_vest", "accessory": None}}
hp/mp 가 None 이면 최대치.
"""
from .battle import Unit

SLOTS = ("weapon", "armor", "accessory")


def new_member(weapon=None, armor=None, accessory=None):
    return {"lv": 1, "exp": 0, "hp": None, "mp": None,
            "equip": {"weapon": weapon, "armor": armor, "accessory": accessory}}


def stats_for(levels, lv):
    """레벨 표에서 그 레벨의 기본 스탯"""
    row = levels[str(lv)]
    return {k: row[k] for k in ("hp", "mp", "atk", "def", "spd")}


def level_for_exp(levels, exp):
    lv = 1
    for key in sorted(levels, key=int):
        if exp >= levels[key]["exp"]:
            lv = int(key)
    return lv


def equip_bonus(items, member):
    bonus = {"hp": 0, "mp": 0, "atk": 0, "def": 0, "spd": 0}
    for slot in SLOTS:
        iid = member["equip"].get(slot)
        if iid:
            for k, v in items[iid].get("stats", {}).items():
                bonus[k] += v
    return bonus


def total_stats(data, who, member):
    base = stats_for(data.levels[who], member["lv"])
    bonus = equip_bonus(data.items, member)
    return {k: base[k] + bonus[k] for k in base}


def member_skills(data, who, member, flags):
    """지금 쓸 수 있는 스킬 목록. flags: {"ruby_flame": bool, "bond": int}"""
    out = []
    for key in sorted(data.levels[who], key=int):
        if int(key) <= member["lv"]:
            out.extend(data.levels[who][key].get("learn", []))
    if who == "ruby":
        if flags.get("ruby_flame"):
            out.append("flame_slash")
        if flags.get("bond", 0) >= 60:
            out.append("duo_strike")
    return out


def build_unit(data, who, name, member, flags):
    s = total_stats(data, who, member)
    hp = s["hp"] if member["hp"] is None else min(member["hp"], s["hp"])
    mp = s["mp"] if member["mp"] is None else min(member["mp"], s["mp"])
    return Unit(who, name, "ally", s["hp"], hp, s["mp"], mp, s["atk"], s["def"], s["spd"],
                member_skills(data, who, member, flags))


def apply_exp(data, who, member, gained):
    """경험치를 더하고 레벨업 목록을 돌려준다: [(새 레벨, [새로 배운 스킬 id])]"""
    levels = data.levels[who]
    member["exp"] += gained
    ups = []
    new_lv = level_for_exp(levels, member["exp"])
    while member["lv"] < new_lv:
        member["lv"] += 1
        ups.append((member["lv"], list(levels[str(member["lv"])].get("learn", []))))
    if ups:                       # 레벨업하면 HP/MP 전부 회복
        member["hp"] = None
        member["mp"] = None
    return ups
