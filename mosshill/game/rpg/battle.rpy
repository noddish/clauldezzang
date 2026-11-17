## ============================================================================
## rpg/battle.rpy — 파티 턴제 전투 (화면·연출 담당. 계산은 mhrpg.Battle)
##
##   call battle("forest")            조우표(data/encounters.json)에서 무리를 골라 싸움
##   call battle("forest", group=1)   특정 무리
##   → _return 은 "win" / "lose" / "escape"
##
## 배치: 아군은 왼쪽(오른쪽을 봄), 적은 오른쪽. 그림이 없으면 임시 실루엣.
## 연출: ui/motions.rpy 의 attack_lunge, hit_flash, heal_glow, fade_out_down 등을 쓴다.
## ============================================================================

default battle_seed = None      # 숫자면 전투 결과가 재현된다 (자동 테스트용)
default battle_counter = 0
default battle_msg = ""
default battle_speed = 1.0      # 연출 속도 (자동 테스트에서는 줄인다)

init -15 python:
    import random as _random

    def battle_rng():
        store.battle_counter += 1
        if store.battle_seed is None:
            return _random.Random()
        return _random.Random(store.battle_seed * 1000 + store.battle_counter)

    def pick_group(zone, group, rng):
        groups = DATA.encounters[zone]["groups"]
        if group is not None:
            return groups[group]["enemies"]
        r = rng.random() * sum(g["weight"] for g in groups)
        for g in groups:
            r -= g["weight"]
            if r <= 0:
                return g["enemies"]
        return groups[-1]["enemies"]

    def encounter_roll(zone):
        """임의 조우가 일어나는가 (조우표의 rate)"""
        return battle_rng().random() < DATA.encounters[zone]["rate"]

    ## ---------------------------------------------------------------- 배치와 그림
    ALLY_X = {"player": 0.13, "ruby": 0.31}
    STAGE_FLOOR = 575          # 유닛 발 위치 (아래 상태창 위)

    def enemy_x(i, n):
        return {1: [0.74], 2: [0.64, 0.84], 3: [0.58, 0.74, 0.9]}[n][i]

    def unit_pos(b, u):
        if u.side == "ally":
            return ALLY_X[u.uid], STAGE_FLOOR
        i = b.enemies.index(u)
        return enemy_x(i, len(b.enemies)), STAGE_FLOOR - 20

    def EnemyPlaceholder(name, boss):
        w, h = (380, 340) if boss else (200, 200)
        return Fixed(
            Transform(Solid("#6a3a3a"), xsize=w, ysize=h, xalign=0.5, yalign=1.0),
            Text(name, size=30 if boss else 24, color="#ffffff", xalign=0.5, yalign=0.55),
            xysize=(w, h))

    def unit_displayable(u):
        if u.side == "ally":
            if u.uid == "ruby":
                return Transform("ruby", zoom=0.62, xzoom=-1.0)      # 오른쪽(적)을 보게 뒤집기
            img = "player_battle"
            if renpy.has_image(img):
                return Transform(img, zoom=0.62)
            return Transform(PlaceholderSprite(u.name, "#4a5a7a", 600), zoom=0.62)
        img = "enemy_" + u.kind
        if renpy.has_image(img):
            return img
        return EnemyPlaceholder(u.name, u.boss)

    def show_unit(b, u, anim=None):
        x, y = unit_pos(b, u)
        at = [Transform(xcenter=x, ypos=y, yanchor=1.0)]
        if anim is not None:
            at.append(anim)
        elif u.side == "enemy":
            at.append(enemy_idle)
        renpy.show("unit_" + u.uid, what=unit_displayable(u), at_list=at, zorder=10)

    _pop_n = [0]
    def pop_number(b, u, text, color):
        x, y = unit_pos(b, u)
        _pop_n[0] += 1
        renpy.show("pop%d" % _pop_n[0],
                   what=Text(text, size=52, bold=True, color=color, outlines=[(4, "#000000", 0, 0)]),
                   at_list=[Transform(xcenter=x, ypos=y - 330), damage_pop], zorder=40)

    def bpause(t):
        renpy.pause(t * store.battle_speed)

    ## ---------------------------------------------------------------- 이벤트 연출
    STATUS_ON = {"poison": "%s 은(는) 독에 걸렸다!", "stun": "%s 은(는) 기절했다!", "taunt": "%s 이(가) 적을 도발한다!"}
    STATUS_OFF = {"poison": "%s 의 독이 풀렸다."}

    def play_events(b, events):
        for ev in events:
            t = ev["type"]
            if t == "act":
                u = b.unit(ev["actor"])
                store.battle_msg = "%s — %s" % (u.name, ev["name"])
                offensive = any(b.unit(x).side != u.side for x in ev.get("targets", []))
                if offensive:
                    show_unit(b, u, attack_lunge(160 if u.side == "ally" else -160))
                elif ev["name"] == "방어":
                    show_unit(b, u, defend_pose)
                bpause(0.3)
            elif t == "damage":
                u = b.unit(ev["target"])
                label = str(ev["amount"])
                if ev.get("weak"):
                    label = "약점! " + label
                elif ev.get("crit"):
                    label = "치명타! " + label
                color = "#b48cff" if ev.get("source") == "poison" else ("#ff8080" if u.side == "ally" else "#ffffff")
                show_unit(b, u, hit_flash)
                pop_number(b, u, label, color)
                if ev.get("crit") or ev.get("weak"):
                    renpy.with_statement(hpunch)
                bpause(0.35)
            elif t == "heal":
                u = b.unit(ev["target"])
                show_unit(b, u, heal_glow)
                pop_number(b, u, "+%d%s" % (ev["amount"], "" if ev["stat"] == "hp" else " MP"),
                           "#7dff7d" if ev["stat"] == "hp" else "#7dc8ff")
                bpause(0.35)
            elif t == "status":
                u = b.unit(ev["target"])
                fmt = (STATUS_ON if ev["on"] else STATUS_OFF).get(ev["status"])
                if fmt:
                    store.battle_msg = fmt % u.name
                    bpause(0.45)
            elif t == "ko":
                u = b.unit(ev["target"])
                store.battle_msg = "%s 쓰러짐!" % u.name
                show_unit(b, u, fade_out_down)
                bpause(0.5)
            elif t == "skip":
                store.battle_msg = "%s 은(는) 기절해서 움직일 수 없다!" % b.unit(ev["actor"]).name
                bpause(0.5)
            elif t == "escape":
                store.battle_msg = "도망쳤다!" if ev["ok"] else "도망치지 못했다!"
                bpause(0.5)

    ## ---------------------------------------------------------------- 시작과 끝
    def start_battle(zone, group):
        rng = battle_rng()
        kinds = pick_group(zone, group, rng)
        foes = [mhrpg.make_enemy(DATA, k, i) for i, k in enumerate(kinds)]
        return mhrpg.Battle(DATA, party_units(), foes, store.inventory, rng)

    def finish_battle(b):
        """파티에 결과 반영. 보상·레벨업 요약 dict 를 돌려준다."""
        summary = {"result": b.result, "exp": 0, "gold": 0, "drops": [], "levelups": []}
        for u in b.allies:
            m = store.party[u.uid]
            m["hp"] = max(1, u.hp)       # 쓰러진 동료는 전투 후 HP 1 로 일어난다
            m["mp"] = u.mp
        if b.result == "win":
            exp, gold, drops = b.rewards()
            summary.update(exp=exp, gold=gold, drops=drops)
            for who in PARTY_ORDER:
                for lv, learned in mhrpg.apply_exp(DATA, who, store.party[who], exp):
                    summary["levelups"].append((member_name(who), lv,
                                                [DATA.skills[s]["name"] for s in learned]))
            store.gold += gold
            for d in drops:
                add_item(d, notify=False)
        elif b.result == "lose":
            store.gold //= 2
            for who in PARTY_ORDER:
                hp, mx = member_hp(who)
                store.party[who]["hp"] = max(1, mx // 2)
        return summary


## ---------------------------------------------------------------- 전투 진행
label battle(zone, group=None):
    $ _b = start_battle(zone, group)
    scene expression location_bg(here)
    show screen battle_hud(_b)
    python:
        for _u in _b.units():
            show_unit(_b, _u)
        battle_msg = "%s 출현!" % ", ".join(e.name for e in _b.enemies)
    with dissolve
    $ bpause(0.8)

    while _b.result is None:
        $ _actor, _evs, _can = _b.next_actor()
        $ play_events(_b, _evs)
        if _can and _b.result is None:
            if _actor.side == "ally":
                $ battle_msg = "%s 의 차례" % _actor.name
                $ _cmd = renpy.call_screen("battle_command", b=_b, actor=_actor)
            else:
                $ _cmd = _b.enemy_command(_actor)
            $ play_events(_b, _b.execute(_actor, _cmd))

    $ _sum = finish_battle(_b)
    hide screen battle_hud
    if _sum["result"] == "win":
        $ battle_msg = ""
        $ _won_exp, _won_gold = _sum["exp"], _sum["gold"]
        n "승리! 경험치 +[_won_exp], 골드 +[_won_gold]"
        if _sum["drops"]:
            $ _drop_names = ", ".join(DATA.items[d]["name"] for d in _sum["drops"])
            n "전리품: [_drop_names]"
        python:
            for _name, _lv, _skills in _sum["levelups"]:
                renpy.say(None, "%s 레벨 %d!%s" % (_name, _lv, (" 새 기술: " + ", ".join(_skills)) if _skills else ""))
    elif _sum["result"] == "lose":
        scene black
        with fade
        n "…눈을 떠 보니 길드 침대였다. 루비가 끌고 왔다고 한다. 골드를 절반 잃었다."
        $ here = "guild_room"
        $ tick()
    else:
        n "무사히 도망쳤다."
    $ renpy.scene()
    return _sum["result"]
