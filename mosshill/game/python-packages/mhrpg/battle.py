"""파티 턴제 전투 계산

흐름 (화면 쪽에서):
    b = Battle(data, allies, enemies, items, rng)
    while b.result is None:
        actor, events, can_act = b.next_actor()     # 턴 시작 처리 (독, 기절, 방어 해제)
        (events 연출)
        if can_act:
            cmd = 플레이어 선택 if actor.side == "ally" else b.enemy_command(actor)
            events = b.execute(actor, cmd)          # 행동 결과
            (events 연출)
    b.rewards()  → 경험치·골드·드롭

명령(cmd) 모양:
    ("attack", 대상 uid)
    ("skill", 스킬 id, 대상 uid 또는 None)
    ("item", 아이템 id, 대상 uid 또는 None)
    ("guard",)
    ("escape",)

이벤트(event)는 dict. 화면 쪽이 종류별로 연출한다:
    {"type": "act", "actor", "name"}               행동 이름 표시
    {"type": "damage", "target", "amount", "crit", "weak"}
    {"type": "heal", "target", "amount", "stat": "hp"|"mp"}
    {"type": "status", "target", "status", "on": bool}
    {"type": "ko", "target"}
    {"type": "skip", "actor", "reason"}
    {"type": "message", "text"}
    {"type": "escape", "ok": bool}
"""
import random

POISON_TURNS = 3
STUN_TURNS = 1
CRIT_RATE = 0.05


class Unit(object):
    def __init__(self, uid, name, side, max_hp, hp, max_mp, mp, atk, df, spd,
                 skills=(), ai=None, boss=False, weak=(), kind=None):
        self.uid = uid
        self.name = name
        self.side = side
        self.max_hp, self.hp = max_hp, hp
        self.max_mp, self.mp = max_mp, mp
        self.atk, self.df, self.spd = atk, df, spd
        self.skills = list(skills)
        self.ai = dict(ai or {})
        self.boss = boss
        self.weak = list(weak)
        self.kind = kind or uid          # 적 종류 id (그림 찾기용)
        self.status = {}                 # "poison": 남은 턴, "stun": 남은 턴, "taunt": 남은 턴
        self.guard = False

    @property
    def alive(self):
        return self.hp > 0

    def __repr__(self):
        return "<%s %d/%d>" % (self.uid, self.hp, self.max_hp)


def make_enemy(data, kind, index):
    e = data.enemies[kind]
    return Unit("%s_%d" % (kind, index), e["name"], "enemy", e["hp"], e["hp"], e.get("mp", 0), e.get("mp", 0),
                e["atk"], e["def"], e["spd"], e.get("skills", []), e.get("ai"), e.get("boss", False),
                e.get("weak", []), kind)


class Battle(object):
    def __init__(self, data, allies, enemies, items, rng=None, can_escape=True):
        self.data = data
        self.allies = list(allies)
        self.enemies = list(enemies)
        self.items = items              # 소지품 dict (id → 개수). 사용하면 줄어든다.
        self.rng = rng or random.Random()
        self.can_escape = can_escape and not any(e.boss for e in enemies)
        self.round = 0
        self.queue = []
        self.result = None              # "win" | "lose" | "escape"
        self.log = []

    ## ------------------------------------------------------------ 조회
    def units(self):
        return self.allies + self.enemies

    def unit(self, uid):
        for u in self.units():
            if u.uid == uid:
                return u
        raise KeyError(uid)

    def living(self, side):
        return [u for u in (self.allies if side == "ally" else self.enemies) if u.alive]

    def foes_of(self, u):
        return self.living("enemy" if u.side == "ally" else "ally")

    def friends_of(self, u):
        return self.living(u.side)

    def usable_skills(self, u):
        return [s for s in u.skills if self.data.skills[s]["mp"] <= u.mp]

    def usable_items(self):
        return [i for i, n in sorted(self.items.items())
                if n > 0 and self.data.items[i]["type"] == "consumable"]

    ## ------------------------------------------------------------ 턴 진행
    def _new_round(self):
        self.round += 1
        units = [u for u in self.units() if u.alive]
        self.queue = sorted(units, key=lambda u: (u.spd + self.rng.random() * 2), reverse=True)

    def next_actor(self):
        """다음 행동자. (유닛, 턴 시작 이벤트, 행동 가능 여부)"""
        while True:
            if not self.queue:
                self._new_round()
            u = self.queue.pop(0)
            if u.alive:
                break
        events = []
        u.guard = False
        if "taunt" in u.status:
            u.status["taunt"] -= 1
            if u.status["taunt"] <= 0:
                del u.status["taunt"]
        if "poison" in u.status:
            dmg = max(2, int(u.max_hp * 0.08))
            events += self._hurt(u, dmg, crit=False, weak=False, source="poison")
            if not u.alive:                      # 독으로 쓰러짐 (_hurt 가 상태를 이미 지움)
                self._check_end()
                return u, events, False
            u.status["poison"] -= 1
            if u.status["poison"] <= 0:
                del u.status["poison"]
                events.append({"type": "status", "target": u.uid, "status": "poison", "on": False})
        if "stun" in u.status:
            u.status["stun"] -= 1
            if u.status["stun"] <= 0:
                del u.status["stun"]
            events.append({"type": "skip", "actor": u.uid, "reason": "stun"})
            return u, events, False
        return u, events, True

    ## ------------------------------------------------------------ 행동 실행
    def execute(self, u, cmd):
        kind = cmd[0]
        events = []
        if kind == "attack":
            t = self._retarget(u, cmd[1])
            events.append({"type": "act", "actor": u.uid, "name": "공격", "targets": [t.uid]})
            events += self._strike(u, t, 1.0, None)
        elif kind == "skill":
            sk = self.data.skills[cmd[1]]
            u.mp -= sk["mp"]
            targets = self._targets(u, sk["target"], cmd[2] if len(cmd) > 2 else None)
            events.append({"type": "act", "actor": u.uid, "name": sk["name"], "skill": cmd[1],
                           "targets": [t.uid for t in targets]})
            for t in targets:
                events += self._apply(u, t, sk["power"], sk.get("effect", {}))
        elif kind == "item":
            it = self.data.items[cmd[1]]
            self.items[cmd[1]] -= 1
            if self.items[cmd[1]] <= 0:
                del self.items[cmd[1]]
            targets = self._targets(u, it.get("target", "ally"), cmd[2] if len(cmd) > 2 else None)
            events.append({"type": "act", "actor": u.uid, "name": it["name"], "item": cmd[1],
                           "targets": [t.uid for t in targets]})
            for t in targets:
                events += self._apply(u, t, 0, it.get("effect", {}))
        elif kind == "guard":
            u.guard = True
            events.append({"type": "act", "actor": u.uid, "name": "방어", "targets": [u.uid]})
        elif kind == "escape":
            ok = self.can_escape and self.rng.random() < 0.6
            events.append({"type": "escape", "ok": ok, "actor": u.uid})
            if ok:
                self.result = "escape"
                return events
        else:
            raise ValueError(cmd)
        self._check_end()
        self.log.extend(events)
        return events

    def _retarget(self, u, uid):
        """대상이 이미 쓰러졌으면 살아 있는 다른 적으로"""
        foes = self.foes_of(u)
        for f in foes:
            if f.uid == uid:
                return f
        return foes[0]

    def _targets(self, u, kind, uid):
        if kind == "enemy":
            return [self._retarget(u, uid)]
        if kind == "all_enemies":
            return self.foes_of(u)
        if kind == "all_allies":
            return self.foes_of(u) if u.side == "enemy" else self.friends_of(u)
        if kind == "self":
            return [u]
        if kind == "ally":
            for f in self.friends_of(u):
                if f.uid == uid:
                    return [f]
            return [u]
        raise ValueError(kind)

    def _apply(self, u, t, power, eff):
        """스킬·아이템 효과 하나를 대상 하나에"""
        events = []
        # 아군에게 쓰는 기술(all_allies)이 적 쪽에서 쓰이면 공격이다 — target 은 이미 반대편으로 계산됨
        if power > 0:
            events += self._strike(u, t, power, eff.get("element"))
            if not t.alive:
                return events
        if "damage" in eff:
            events += self._hurt(t, eff["damage"], crit=False, weak=False)
        if "heal_hp" in eff and t.alive:
            amt = min(eff["heal_hp"], t.max_hp - t.hp)
            t.hp += amt
            events.append({"type": "heal", "target": t.uid, "amount": amt, "stat": "hp"})
        if "heal_mp" in eff and t.alive:
            amt = min(eff["heal_mp"], t.max_mp - t.mp)
            t.mp += amt
            events.append({"type": "heal", "target": t.uid, "amount": amt, "stat": "mp"})
        if "cure" in eff and eff["cure"] in t.status:
            del t.status[eff["cure"]]
            events.append({"type": "status", "target": t.uid, "status": eff["cure"], "on": False})
        if "taunt" in eff:
            t.status["taunt"] = eff["taunt"] + 1      # 자기 턴 시작에 1 줄어드므로 +1
            events.append({"type": "status", "target": t.uid, "status": "taunt", "on": True})
        if "poison" in eff and t.alive and "poison" not in t.status and self.rng.random() < eff["poison"]:
            t.status["poison"] = POISON_TURNS
            events.append({"type": "status", "target": t.uid, "status": "poison", "on": True})
        if "stun" in eff and t.alive and "stun" not in t.status and self.rng.random() < eff["stun"]:
            t.status["stun"] = STUN_TURNS
            events.append({"type": "status", "target": t.uid, "status": "stun", "on": True})
        return events

    def _strike(self, u, t, power, element):
        """피해 = max(1, 공격력×위력 − 방어력÷2) × (0.9~1.1), 치명타 ×1.5, 약점 ×1.5, 방어 ÷2"""
        base = u.atk * power - t.df / 2.0
        dmg = max(1.0, base) * self.rng.uniform(0.9, 1.1)
        crit = self.rng.random() < CRIT_RATE
        weak = element is not None and element in t.weak
        if crit:
            dmg *= 1.5
        if weak:
            dmg *= 1.5
        if t.guard:
            dmg /= 2.0
        return self._hurt(t, max(1, int(round(dmg))), crit, weak)

    def _hurt(self, t, amount, crit, weak, source=None):
        t.hp = max(0, t.hp - amount)
        ev = [{"type": "damage", "target": t.uid, "amount": amount, "crit": crit, "weak": weak, "source": source}]
        if not t.alive:
            t.status.clear()
            ev.append({"type": "ko", "target": t.uid})
        return ev

    def _check_end(self):
        if self.result:
            return
        if not self.living("enemy"):
            self.result = "win"
        elif not self.living("ally"):
            self.result = "lose"

    ## ------------------------------------------------------------ 적 인공지능
    def enemy_command(self, u):
        options = []
        for key, w in u.ai.items():
            if key == "attack" or (key in u.skills and self.data.skills[key]["mp"] <= u.mp):
                options.append((key, w))
        if not options:
            options = [("attack", 1.0)]
        r = self.rng.random() * sum(w for _, w in options)
        for key, w in options:
            r -= w
            if r <= 0:
                break
        foes = self.living("ally")
        taunting = [f for f in foes if "taunt" in f.status]
        if taunting:
            target = taunting[0]
        else:
            # 체력이 적은 쪽을 조금 더 노린다
            weights = [1.0 + (1.0 - f.hp / float(f.max_hp)) for f in foes]
            r2 = self.rng.random() * sum(weights)
            target = foes[-1]
            for f, w in zip(foes, weights):
                r2 -= w
                if r2 <= 0:
                    target = f
                    break
        if key == "attack":
            return ("attack", target.uid)
        return ("skill", key, target.uid)

    ## ------------------------------------------------------------ 보상
    def rewards(self):
        """승리 보상: (경험치, 골드, [드롭 아이템 id])"""
        exp = gold = 0
        drops = []
        for e in self.enemies:
            d = self.data.enemies[e.kind]
            exp += d["exp"]
            gold += d["gold"]
            for drop in d.get("drops", []):
                if self.rng.random() < drop["rate"]:
                    drops.append(drop["item"])
        return exp, gold, drops
