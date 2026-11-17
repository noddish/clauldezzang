## ============================================================================
## dev/autotest.rpy — 자동 검사 (개발용, 배포판에서는 제외)
##
## 환경변수 MH_AUTOTEST=<이름> 으로 실행하면 메인 메뉴 대신 label autotest_<이름> 이
## 실행되고, 스크린샷을 MH_SHOT_DIR 에 저장한 뒤 종료한다.
##
##   MH_AUTOTEST=m0 MH_SHOT_DIR=/tmp/shots xvfb-run renpy.sh mosshill
##
## 사람이 클릭하지 않아도 화면을 확인할 수 있게 하는 장치다.
## ============================================================================

init -50 python:
    import os
    AUTOTEST = os.environ.get("MH_AUTOTEST")
    SHOT_DIR = os.environ.get("MH_SHOT_DIR", ".")

    def shot(name):
        """현재 화면을 SHOT_DIR/<name>.png 로 저장"""
        renpy.pause(0.6, hard=True)
        renpy.screenshot(os.path.join(SHOT_DIR, name + ".png"))

    def _do_shot(name):
        renpy.screenshot(os.path.join(SHOT_DIR, name + ".png"))


    def autotest_log(msg):
        with open(os.path.join(SHOT_DIR, "autotest.log"), "a") as f:
            f.write(msg + "\n")

    ## 자동 검사 중 오류가 나면 오류 화면에서 멈추지 말고 기록 후 바로 종료
    if AUTOTEST:
        if not os.path.isdir(SHOT_DIR):
            os.makedirs(SHOT_DIR)

        def _autotest_exception(short, full, traceback_fn):
            autotest_log("EXCEPTION\n" + full)
            os._exit(1)

        config.exception_handler = _autotest_exception


## 실제 대사가 나오는 중에 0.8초 뒤 스크린샷을 찍고 다음으로 넘어간다 (클릭 대신)
screen autoshot(name):
    timer 0.8 action [Function(_do_shot, name), Return(True)]


label splashscreen:
    if AUTOTEST:
        jump expression "autotest_" + AUTOTEST
    return


## ---------------------------------------------------------------- M0
init python:
    ## 그림 파일 검사: 그림이 빠졌거나, 물건 마스크 크기가 world.rpy 의 rect 와 다르면 문제
    CAST_FACES = {
        "ruby":   ["happy", "angry", "sad", "surprised", "blink", "talk"],
        "kai":    ["happy", "surprised", "sad", "angry", "talk"],
        "martha": ["happy", "angry", "surprised", "talk"],
        "pip":    ["happy", "sad", "surprised", "talk"],
        "gregor": ["happy", "angry", "talk"],
    }

    def asset_problems():
        out = []
        need = []
        for lid, loc in LOC.items():
            need.append("bg_%s_day" % loc.bg)
            if loc.night_bg:
                need.append("bg_%s_night" % loc.bg)
            for o in OBJECTS.get(lid, []):
                mask = o.mask(lid)
                if mask is None:
                    out.append("물건 마스크 없음: %s/%s" % (lid, o.id))
                elif tuple(renpy.image_size(mask)) != tuple(o.rect[2:]):
                    out.append("마스크 크기 %s ≠ rect %s: %s/%s" % (renpy.image_size(mask), o.rect[2:], lid, o.id))
        for lid, spots in NPC_SPOTS.items():
            for mid in spots:
                if npc_scene(lid, mid) is None:
                    out.append("장소 인물 그림 없음: %s/%s (images/scenes/)" % (lid, mid))
                for st in ("busy", "look"):
                    for tod in ("day", "night"):
                        if not renpy.loadable("images/scenes/scene_%s_%s_%s_%s.png" % (lid, mid, st, tod)):
                            out.append("장소 인물 그림 없음: %s/%s %s %s" % (lid, mid, st, tod))
        need += ["icon_" + i for i in DATA.items] + ["enemy_" + e for e in DATA.enemies]
        for who, faces in CAST_FACES.items():
            need += ["%s_body" % who] + ["%s_face_%s" % (who, f) for f in faces]
        out += ["그림 없음: " + n for n in need if not renpy.has_image(n)]
        return out


init python:
    def script_problems():
        """연결 검사: 등록한 이벤트·물건·인물·이동이 실제 label·장소를 가리키는가.
        원작은 이런 검사가 없어 오타 하나가 게임 진행을 멈추게 할 수 있었다."""
        out = []
        for e in EVENTS:
            if not renpy.has_label(e.label):
                out.append("이벤트 %s 의 label %s 없음" % (e.id, e.label))
            if e.at is not None and e.at not in LOC:
                out.append("이벤트 %s 의 장소 %s 없음" % (e.id, e.at))
        for lid, objs in OBJECTS.items():
            if lid not in LOC:
                out.append("물건 목록의 장소 %s 가 place() 로 등록되지 않음" % lid)
            for o in objs:
                if isinstance(o.action, Interact) and not renpy.has_label(o.action.label):
                    out.append("물건 %s/%s 의 label %s 없음" % (lid, o.id, o.action.label))
                if isinstance(o.action, MoveTo) and o.action.loc_id not in LOC:
                    out.append("물건 %s/%s 의 이동 장소 %s 없음" % (lid, o.id, o.action.loc_id))
        for lid, spots in NPC_SPOTS.items():
            for mid in spots:
                if not renpy.has_label(mid + "_talk"):
                    out.append("인물 %s 의 대화 label %s_talk 없음" % (mid, mid))
                if mid not in CHAR_NAMES:
                    out.append("인물 %s 의 이름이 CHAR_NAMES 에 없음" % mid)
        for lid, loc in LOC.items():
            if loc.parent is not None and loc.parent not in LOC:
                out.append("장소 %s 의 부모 %s 없음" % (lid, loc.parent))
        return out


label autotest_m0:
    python:
        problems = DATA.check()
        autotest_log("data check: %d problem(s)" % len(problems))
        for p in problems:
            autotest_log("  FAIL  " + p)
        autotest_log("items=%d skills=%d enemies=%d" % (len(DATA.items), len(DATA.skills), len(DATA.enemies)))
        problems = asset_problems()
        autotest_log("asset check: %d problem(s)" % len(problems))
        for p in problems:
            autotest_log("  FAIL  " + p)
        problems = script_problems()
        autotest_log("script check: %d problem(s) — 이벤트 %d개, 장소 %d곳" % (len(problems), len(EVENTS), len(LOC)))
        for p in problems:
            autotest_log("  FAIL  " + p)

    scene bg_guild_front_day
    show kai happy at Transform(xcenter=0.14, yalign=1.0)
    show martha at Transform(xcenter=0.38, yalign=1.0)
    show pip happy at Transform(xcenter=0.6, yalign=1.0)
    show gregor at Transform(xcenter=0.84, yalign=1.0)
    show screen autoshot("m0_cast")
    n "주인공과 마을 사람들."
    hide screen autoshot
    hide kai
    hide martha
    hide pip
    hide gregor

    ## 물건에 마우스를 올렸을 때 그림 (배경을 마스크 모양으로 잘라 밝게) + 밤 색조
    $ tod = 3
    scene expression location_bg("guild_hall")
    python:
        _o = [o for o in OBJECTS["guild_hall"] if o.id == "board"][0]
    show expression _o.hover_image("guild_hall") as hovertest at Transform(pos=(_o.rect[0], _o.rect[1]))
    show ruby at stage_left
    show screen autoshot("m0_night_hover")
    n "밤의 길드 홀. 의뢰판에 마우스를 올린 모습."
    hide screen autoshot
    hide hovertest
    hide ruby

    ## 장소 안 인물 (밤의 길드 홀에서 검을 닦는 루비) + 마우스를 올렸을 때 인물만 밝게
    python:
        _sc = npc_scene("guild_hall", "ruby")
    show expression _sc.look as scenetest
    show expression _sc.hover(_sc.look) as hovertest
    show screen autoshot("m0_npc_scene_hover")
    n "장소 안 인물에 마우스를 올린 모습."
    hide screen autoshot
    hide hovertest
    hide scenetest
    $ tod = 0

    scene bg_guild_hall_day
    show ruby happy at stage_right
    show screen autoshot("m0_ruby_happy")
    r "와아, 진짜 왔다! 나는 루비. 이끼발굽 길드의 마지막 멤버이자, 에이스 검사야!"
    hide screen autoshot

    show ruby angry at stage_right
    show screen autoshot("m0_ruby_angry")
    r "'3일 뒤 감사. 실적이 없으면 면허 취소.' 이게 말이 돼?!"
    hide screen autoshot

    show ruby neutral at stage_right
    show screen autoshot("m0_ruby_talk")
    r "그러니까 길드장님, 오늘부터 바로 일하자!"
    hide screen autoshot

    $ autotest_log("done")
    $ renpy.quit()


## ---------------------------------------------------------------- M1: 3일 전체 자동 플레이
## 메인 + 서브 2개를 모두 하고, 잠김 규칙(밤 숲, 저녁 상점, 의뢰 전 숲)도 확인한다.
init python:
    INNPC = "%r in [m for m, x in npcs_here(here)]"
    M1_STEPS = [
        ("log", "== 1일차 =="),
        ("shot", "m1_01_guild_hall"),
        ("expect", "here == 'guild_hall' and MAIN.is_state('board')", "인트로 후 길드 홀, 메인=board"),
        ("click", "kitchen"),
        ("expect", INNPC % "ruby", "아침 부엌에 루비"),
        ("sleep", 1.2),
        ("shot", "m1_02_kitchen_ruby"),                 # 들어오자 고개를 들어 앞을 봄
        ("talk", "ruby"),
        ("shot", "m1_02b_kitchen_after_talk"),          # 대화가 끝나면 다시 하던 일
        ("click", "back"), ("click", "door"),
        ("shot", "m1_03_map"),
        ("click", "forest"),
        ("expect", "here == 'map'", "의뢰 전에는 숲이 잠김"),
        ("click", "shop"),
        ("expect", "here == 'shop' and " + INNPC % "pip", "아침 잡화점에 핍"),
        ("talk", "pip"), ("click", "exit"),
        ("click", "tavern"),
        ("expect", INNPC % "martha", "선술집에 마르타"),
        ("shot", "m1_04_tavern"),
        ("shot_say", "m1_04b_board_think"),             # 혼잣말 — 카이가 왼쪽에 나오고 마르타는 그대로
        ("click", "board"),
        ("shot_say", "m1_05_martha_say"),               # 대화 — 흐린 배경, 카이 왼쪽 / 마르타 오른쪽
        ("talk", "martha"),
        ("expect", "MAIN.is_state('forest')", "의뢰 수락 → 메인=forest"),
        ("click", "exit"), ("click", "forest"),
        ("expect", "MAIN.is_state('report_martha') and tod == 1", "슬라임 퇴치(임시 전투) 후 오후"),
        ("click", "town"), ("click", "tavern"), ("talk", "martha"),
        ("expect", "MAIN.is_state('day1_rest') and MARTHA.is_state('cellar')", "보고 완료 + 창고 의뢰 시작"),
        ("click", "cellar"),
        ("expect", "MARTHA.is_state('cellar_report') and tod == 2", "창고 청소 후 저녁"),
        ("talk", "martha"),
        ("expect", "MARTHA.is_state('done') and has_item('potion')", "창고 보상 회복약"),
        ("click", "exit"), ("click", "guild"),
        ("expect", INNPC % "ruby", "저녁 길드 홀에 루비"),
        ("talk", "ruby"),
        ("expect", "RUBY.is_state('flint_lost')", "부싯돌 퀘스트 시작"),
        ("shot", "m1_06_hall_evening"),
        ("click", "stairs"), ("click", "desk"),
        ("expect", "RUBY.is_state('flint_return') and has_item('flint')", "책상에서 부싯돌 발견"),
        ("click", "door"), ("talk", "ruby"),
        ("expect", "RUBY.is_state('done') and bond['ruby'] >= 20 and ruby_flame", "부싯돌 반환, 신뢰도 상승, 불꽃베기 해금"),
        ("click", "stairs"), ("click", "bed"),
        ("log", "== 2일차 =="),
        ("expect", "day == 2 and tod == 0 and MAIN.is_state('pip_job')", "2일차 아침, 메인=pip_job"),
        ("click", "door"), ("click", "door"), ("click", "shop"), ("talk", "pip"),
        ("expect", "MAIN.is_state('cave')", "핍의 의뢰 수락"),
        ("click", "exit"), ("click", "forest"), ("click", "cave"),
        ("shot", "m1_07_cave"),
        ("click", "chest"),
        ("click", "deeper"),
        ("expect", "MAIN.is_state('return_cargo') and has_item('pip_cargo') and tod == 2", "두꺼비 왕(임시 전투) 후 짐 획득, 저녁"),
        ("click", "back"), ("click", "exit"), ("click", "town"),
        ("click", "shop"),
        ("expect", "here == 'map'", "저녁에는 잡화점이 닫힘"),
        ("click", "square"),
        ("expect", INNPC % "pip", "저녁 광장에 핍"),
        ("talk", "pip"),
        ("expect", "MAIN.is_state('day2_rest') and not has_item('pip_cargo')", "짐 반환"),
        ("click", "map"), ("wait",),
        ("click", "forest"),
        ("expect", "here == 'map' and tod == 3", "밤에는 숲이 잠김"),
        ("click", "guild"), ("click", "stairs"), ("click", "bed"),
        ("log", "== 3일차 =="),
        ("expect", "day == 3 and MAIN.is_state('inspection')", "3일차 아침, 메인=inspection"),
        ("shot_say", "m1_08_inspection"),
        ("wait",),
    ]

label autotest_m1:
    $ battle_seed = 7
    $ battle_speed = 0.15
    $ DRIVER.load(M1_STEPS)
    $ FINAL_CHECK = ("MAIN.is_state('end') and inspection_score == 4 and game_over", "감사 실적 4/4 로 맛보기판 종료")
    show screen autodriver
    call start
    jump autotest_finish


## ---------------------------------------------------------------- M1: 아무것도 안 하는 플레이어
## 의뢰를 하나도 안 받아도 3일차 오후에 감사가 강제로 열리고 0점이 나와야 한다.
init python:
    M1_LAZY_STEPS = [
        ("click", "stairs"),
        ("wait",), ("wait",), ("click", "bed"),
        ("expect", "day == 2 and MAIN.is_state('board')", "의뢰 안 받으면 2일차에도 메인=board"),
        ("wait",), ("wait",), ("click", "bed"),
        ("expect", "day == 3", "3일차"),
        ("wait",),
    ]

label autotest_m1_lazy:
    $ battle_seed = 7
    $ battle_speed = 0.15
    $ DRIVER.load(M1_LAZY_STEPS)
    $ FINAL_CHECK = ("MAIN.is_state('end') and inspection_score == 0 and game_over", "아무것도 안 하면 실적 0/4 로 종료")
    show screen autodriver
    call start
    jump autotest_finish


## ---------------------------------------------------------------- M2: 전투·성장·상점·소지품
## M1 경로 그대로 + 상점 구매, 소지품 화면, 전투 화면, 경험치·레벨 검사
init python:
    def _m2_steps():
        s = list(M1_STEPS)
        def after(step, *new):
            i = s.index(step) + 1
            s[i:i] = list(new)
        after(("talk", "pip"),
              ("call", "shop_buy", "pip", "potion"),
              ("expect", "gold == 20 and has_item('potion', 2)", "회복약 1개 구입 (50 → 20 골드)"),
              ("shot_ui", "m2_01_shop"), ("open", "shop_shelf"))
        after(("expect", "MAIN.is_state('forest')", "의뢰 수락 → 메인=forest"),
              ("shot_battle", "m2_02_battle_forest"))
        after(("expect", "MAIN.is_state('report_martha') and tod == 1", "슬라임 퇴치(임시 전투) 후 오후"),
              ("expect", "party['player']['exp'] > 0 and party['ruby']['exp'] > 0", "숲 전투로 경험치 획득"),
              ("shot_ui", "m2_03_inventory"), ("open", "open_inventory"))
        after(("expect", "MAIN.is_state('cave')", "핍의 의뢰 수락"),
              ("shot_battle", "m2_04_battle_boss"))
        after(("expect", "MAIN.is_state('return_cargo') and has_item('pip_cargo') and tod == 2", "두꺼비 왕(임시 전투) 후 짐 획득, 저녁"),
              ("expect", "party['player']['lv'] >= 3 and party['ruby']['lv'] >= 3", "보스 후 둘 다 레벨 3 이상"),
              ("expect", "has_item('hi_potion') and inventory.get('pip_cargo', 0) == 1", "보스 드롭 고급 회복약 + 짐은 정확히 1개"))
        return s

label autotest_m2:
    $ battle_seed = 7
    $ battle_speed = 0.15
    $ DRIVER.load(_m2_steps())
    $ FINAL_CHECK = ("MAIN.is_state('end') and inspection_score == 4", "M2 경로로 감사 4/4")
    show screen autodriver
    call start
    jump autotest_finish


## ---------------------------------------------------------------- M2: 패배 처리
label autotest_m2_lose:
    $ battle_seed = 3
    $ battle_speed = 0.15
    $ here = "cave_2"
    $ gold = 100
    $ party["player"]["hp"] = 1
    $ party["ruby"]["hp"] = 1
    show screen autodriver
    call battle("boss_toad")
    $ DRIVER.check("_return == 'lose'", "HP 1 로 보스 → 패배")
    $ DRIVER.check("here == 'guild_room' and gold == 50", "길드 침대에서 깨어남, 골드 절반")
    $ DRIVER.check("member_hp('player')[0] == member_hp('player')[1] // 2", "HP 절반으로 회복")
    jump autotest_finish


## ---------------------------------------------------------------- 화면 점검: 소지품·상점
label autotest_ui:
    python:
        battle_speed = 0.15
        MAIN._enter("board")
        here = "guild_hall"
        for _i in ("potion", "potion", "ether", "iron_sword", "lucky_charm", "slime_jelly", "flint"):
            add_item(_i, notify=False)
        party["player"]["hp"] = 30
        DRIVER.load([
            ("shot_ui", "ui_01_inventory"), ("open", "open_inventory"),
            ("call", "equip_item", "player", "iron_sword"),
            ("expect", "party['player']['equip']['weapon'] == 'iron_sword' and has_item('short_sword')", "철검 장착 → 낡은 단검은 소지품으로"),
            ("call", "use_item_field", "potion", "player"),
            ("expect", "party['player']['hp'] == 60", "회복약 사용 HP 30 → 60 (최대치에서 멈춤)"),
            ("shot_ui", "ui_02_inventory_after"), ("open", "open_inventory"),
            ("click", "door"), ("click", "shop"),
            ("call", "shop_sell", "pip", "slime_jelly"),
            ("expect", "gold == 52 and not has_item('slime_jelly')", "슬라임 젤리 판매 +2"),
            ("shot_ui", "ui_03_shop"), ("click", "shelf"),
        ])
    show screen autodriver
    jump main_loop
