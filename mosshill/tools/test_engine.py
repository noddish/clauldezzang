"""전투 엔진 단위 테스트 — Ren'Py 없이 몇 초 만에 돈다.
실행:  python3 tools/test_engine.py
"""
import random
import sys

sys.path.insert(0, __import__("os").path.dirname(__file__))
from balance_sim import DATA, mhrpg, new_party  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("  PASS  " if cond else "  FAIL  ") + msg)
    if not cond:
        FAILS.append(msg)


def units(flags=None):
    party = new_party()
    return [mhrpg.build_unit(DATA, w, w, party[w], flags or {}) for w in ("player", "ruby")]


def test_damage_formula():
    a, r = units()
    slime = mhrpg.make_enemy(DATA, "slime", 0)
    b = mhrpg.Battle(DATA, [a, r], [slime], {}, random.Random(1))
    hits = []
    for _ in range(300):
        slime.hp = slime.max_hp
        hits += [e["amount"] for e in b._strike(r, slime, 1.0, None) if e["type"] == "damage"]
    base = r.atk - slime.df / 2.0
    check(min(hits) >= int(base * 0.9) and max(hits) <= int(base * 1.1 * 1.5) + 1,
          "피해량이 공식 범위 안 (%d~%d, 기준 %.1f)" % (min(hits), max(hits), base))


def test_guard_halves():
    a, r = units()
    toad = mhrpg.make_enemy(DATA, "toad_king", 0)
    b = mhrpg.Battle(DATA, [a, r], [toad], {}, random.Random(2))
    normal = [b._strike(toad, a, 1.0, None)[0]["amount"] for _ in range(200)]
    a.hp = a.max_hp
    a.guard = True
    guarded = [b._strike(toad, a, 1.0, None)[0]["amount"] for _ in range(200)]
    a.hp = a.max_hp
    check(sum(guarded) < sum(normal) * 0.6, "방어하면 받는 피해가 절반 정도")


def test_fire_weakness():
    a, r = units({"ruby_flame": True})
    toad = mhrpg.make_enemy(DATA, "toad_king", 0)
    b = mhrpg.Battle(DATA, [a, r], [toad], {}, random.Random(3))
    ev = b._strike(r, toad, 2.0, "fire")
    check(ev[0]["weak"], "불꽃베기는 두꺼비 왕의 약점")
    check("flame_slash" in r.skills, "부싯돌 퀘스트 완료 시 루비가 불꽃베기 보유")


def test_poison_kill_no_crash():
    a, r = units()
    a.hp = 1
    a.status["poison"] = 2
    slime = mhrpg.make_enemy(DATA, "slime", 0)
    b = mhrpg.Battle(DATA, [a, r], [slime], {}, random.Random(4))
    b.queue = [a]
    u, ev, can = b.next_actor()
    check(not u.alive and not can and any(e["type"] == "ko" for e in ev), "독으로 쓰러져도 오류 없이 처리")


def test_boss_no_escape():
    b = mhrpg.Battle(DATA, units(), [mhrpg.make_enemy(DATA, "toad_king", 0)], {}, random.Random(5))
    check(not b.can_escape, "보스전은 도망 불가")


def test_taunt_draws_attacks():
    a, r = units()
    a.status["taunt"] = 3
    goblin = mhrpg.make_enemy(DATA, "goblin", 0)
    b = mhrpg.Battle(DATA, [a, r], [goblin], {}, random.Random(6))
    targets = [b.enemy_command(goblin)[-1] for _ in range(50)]
    check(all(t == "player" for t in targets), "도발 중에는 적이 주인공만 노림")


def test_item_consumed():
    a, r = units()
    a.hp = 10
    items = {"potion": 1}
    b = mhrpg.Battle(DATA, [a, r], [mhrpg.make_enemy(DATA, "slime", 0)], items, random.Random(7))
    b.execute(a, ("item", "potion", "player"))
    check(a.hp == 50 and "potion" not in items, "회복약: HP +40, 소지품에서 빠짐")


def test_level_up():
    m = mhrpg.new_member("short_sword", "leather_vest")
    ups = mhrpg.apply_exp(DATA, "player", m, 60)
    check(m["lv"] == 3 and [u[0] for u in ups] == [2, 3], "경험치 60 → 레벨 3 (2, 3 단계로)")
    check(ups[-1][1] == ["taunt"], "레벨 3 에서 도발 습득")


def test_full_battle_terminates():
    rng = random.Random(8)
    for _ in range(200):
        b = mhrpg.Battle(DATA, units(), [mhrpg.make_enemy(DATA, k, i) for i, k in enumerate(["goblin", "mushroom", "slime"])], {"potion": 2}, rng)
        while b.result is None and b.round < 200:
            u, _, can = b.next_actor()
            if can and b.result is None:
                b.execute(u, mhrpg.ally_command(b, u) if u.side == "ally" else b.enemy_command(u))
        if b.result is None:
            break
    check(b.result is not None, "전투 200판이 모두 끝까지 진행됨 (무한 루프 없음)")


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            print(name)
            fn()
    print("\n결과: 실패 %d개" % len(FAILS))
    sys.exit(1 if FAILS else 0)
