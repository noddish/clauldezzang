"""밸런스 시뮬레이터 — 실제 진행 순서대로 전투를 수천 번 돌려 승률을 본다.

실행:  python3 tools/balance_sim.py [반복 횟수]

게임과 같은 엔진(game/python-packages/mhrpg)과 같은 데이터(game/data/*.json)를 쓴다.
아군은 mhrpg.policy.ally_command (평범한 플레이어 흉내)로 행동한다.

진행 순서 (기획서 3장):
  1일차: 숲 슬라임(스토리) → [선술집 창고 슬라임 3] → 잠(전부 회복)
  2일차: 이끼 동굴 임의 조우 1회 → 두꺼비 왕
"""
import copy
import json
import os
import random
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "game")
sys.path.insert(0, os.path.join(ROOT, "python-packages"))
import mhrpg  # noqa: E402


class Data(object):
    def __init__(self):
        for name in ("items", "skills", "enemies", "encounters", "shops", "levels"):
            with open(os.path.join(ROOT, "data", name + ".json"), encoding="utf-8") as f:
                setattr(self, name, json.load(f))


DATA = Data()
NAMES = {"player": "카이", "ruby": "루비"}


def pick_group(zone, rng):
    groups = DATA.encounters[zone]["groups"]
    r = rng.random() * sum(g["weight"] for g in groups)
    for g in groups:
        r -= g["weight"]
        if r <= 0:
            return g["enemies"]
    return groups[-1]["enemies"]


def fight(party, items, enemies, flags, rng, max_rounds=60):
    """한 판. 파티 상태(hp/mp/exp)를 갱신하고 결과와 라운드 수를 돌려준다."""
    allies = [mhrpg.build_unit(DATA, who, NAMES[who], party[who], flags) for who in ("player", "ruby")]
    foes = [mhrpg.make_enemy(DATA, k, i) for i, k in enumerate(enemies)]
    b = mhrpg.Battle(DATA, allies, foes, items, rng)
    while b.result is None and b.round <= max_rounds:
        u, _, can = b.next_actor()
        if b.result or not can:
            continue
        cmd = mhrpg.ally_command(b, u) if u.side == "ally" else b.enemy_command(u)
        b.execute(u, cmd)
    for a in allies:
        party[a.uid]["hp"] = max(1, a.hp) if b.result == "win" else 1
        party[a.uid]["mp"] = a.mp
    if b.result == "win":
        exp, gold, drops = b.rewards()
        for who in party:
            mhrpg.apply_exp(DATA, who, party[who], exp)
        for d in drops:
            items[d] = items.get(d, 0) + 1
    return b.result or "timeout", b.round, sum(a.hp for a in allies) / float(sum(a.max_hp for a in allies))


def full_heal(party):
    for m in party.values():
        m["hp"] = None
        m["mp"] = None


def new_party():
    return {"player": mhrpg.new_member("short_sword", "leather_vest"),
            "ruby": mhrpg.new_member("ruby_blade", "leather_vest")}


START_ITEMS = {"potion": 1}


def run(profile, rng):
    """profile: cellar(서브 했나), flame(부싯돌), shop(물약 몇 개 샀나)"""
    party = new_party()
    items = dict(START_ITEMS)
    flags = {"ruby_flame": profile["flame"], "bond": 20 if profile["flame"] else 4}
    out = {}

    r = fight(party, items, ["slime", "slime"], flags, rng)
    out["숲 슬라임"] = r
    if r[0] != "win":
        return out, party
    if profile["cellar"]:
        out["창고 슬라임"] = fight(party, items, DATA.encounters["tavern_cellar"]["groups"][0]["enemies"], flags, rng)
        if out["창고 슬라임"][0] == "win":
            items["potion"] = items.get("potion", 0) + 2      # 마르타 보상
    full_heal(party)

    items["potion"] = items.get("potion", 0) + profile["shop"]
    r = fight(party, items, pick_group("cave_1", rng), flags, rng)
    out["동굴 조우"] = r
    if r[0] != "win":
        return out, party
    out["두꺼비 왕"] = fight(party, items, ["toad_king"], flags, rng)
    return out, party


PROFILES = [
    ("서브 없음, 쇼핑 없음", {"cellar": False, "flame": False, "shop": 0}),
    ("창고만, 쇼핑 없음",    {"cellar": True,  "flame": False, "shop": 0}),
    ("서브 둘 다",           {"cellar": True,  "flame": True,  "shop": 0}),
    ("서브 둘 다 + 물약 2",  {"cellar": True,  "flame": True,  "shop": 2}),
]


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    rng = random.Random(12345)
    print("반복 %d회\n" % n)
    for title, prof in PROFILES:
        stats = {}
        lv_before_boss = []
        for _ in range(n):
            out, party = run(prof, rng)
            for k, (res, rounds, hp_left) in out.items():
                s = stats.setdefault(k, {"win": 0, "n": 0, "rounds": 0, "hp": 0.0})
                s["n"] += 1
                s["rounds"] += rounds
                if res == "win":
                    s["win"] += 1
                    s["hp"] += hp_left
            lv_before_boss.append(party["player"]["lv"])
        print("[%s]" % title)
        for k in ("숲 슬라임", "창고 슬라임", "동굴 조우", "두꺼비 왕"):
            if k in stats:
                s = stats[k]
                print("  %-8s 승률 %5.1f%%  평균 %4.1f라운드  이겼을 때 남은 HP %3.0f%%" % (
                    k, 100.0 * s["win"] / s["n"], s["rounds"] / float(s["n"]),
                    100.0 * s["hp"] / max(1, s["win"])))
        avg_lv = sum(lv_before_boss) / float(len(lv_before_boss))
        print("  끝났을 때 평균 레벨 %.1f\n" % avg_lv)


if __name__ == "__main__":
    main()
