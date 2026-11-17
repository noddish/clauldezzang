## ============================================================================
## dev/autodrive.rpy — 자동 플레이어 (개발용)
##
## 각본(steps)대로 게임을 실제로 플레이한다:
##   - 대사창이 뜨면 자동으로 넘긴다
##   - 이름 입력창에는 "카이"
##   - 선택지는 각본의 ("choose", 번호) 로 고른다 (지정 없으면 첫 번째)
##   - 장소 화면에서는 다음 단계를 실행한다:
##       ("click", 물건 id)     지금 장소에 보이는 물건을 실제로 클릭 (안 보이면 실패)
##       ("talk", 인물 id)       지금 장소에 있는 인물을 클릭 (없으면 실패)
##       ("wait",)               시간 보내기 버튼
##       ("sleep", 초)           그냥 기다리기 (연출이 끝난 뒤 스크린샷을 찍을 때)
##       ("shot", 이름)          스크린샷
##       ("expect", "식", "설명") 식이 참인지 검사해 PASS/FAIL 기록
##       ("choose", 번호)        다음 선택지에서 고를 번호
##       ("shot_say", 이름)      다음에 나오는 대사 장면을 스크린샷
##       ("shot_battle", 이름)   다음 전투 명령 화면을 스크린샷
##       ("shot_ui", 이름)       다음에 여는 상점·소지품 화면을 스크린샷
##       ("open", 라벨)          상점·소지품 화면 열기 (자동으로 닫힘)
##       ("call", "함수", 인자…)  구매·장착 같은 동작을 직접 실행
##   전투 명령 화면에서는 mhrpg.ally_command (평범한 플레이어 흉내)로 행동한다.
## ============================================================================

init -45 python:
    import time as _time

    class AutoDriver(object):
        def __init__(self):
            self.steps = []
            self.i = 0
            self.passed = 0
            self.failed = 0
            self.next_choice = None
            self.last_action = 0.0
            self.say_shot = None
            self.say_seen = None
            self.battle_shot = None
            self.ui_shot = None
            self.ui_seen = None
            self.battles = 0

        def load(self, steps):
            self.steps = list(steps)
            self.i = 0

        def log(self, msg):
            autotest_log(msg)

        def check(self, expr, desc):
            try:
                ok = bool(eval(expr, store.__dict__))
            except Exception as e:
                ok = False
                desc += " (오류: %r)" % e
            if ok:
                self.passed += 1
                self.log("  PASS  " + desc)
            else:
                self.failed += 1
                self.log("  FAIL  " + desc + "   [" + expr + "]  here=%s day=%s tod=%s main=%s"
                         % (store.here, store.day, store.tod, MAIN.current))

        def tick(self):
            """0.1초마다 호출. 값을 돌려주면 현재 상호작용이 그 값으로 끝난다."""
            now = _time.time()
            if renpy.get_screen("say"):
                if self.say_shot:
                    if self.say_seen is None:
                        self.say_seen = now
                    if now - self.say_seen < 0.6:
                        return None
                    _do_shot(self.say_shot)
                    self.log("  shot  " + self.say_shot)
                    self.say_shot = None
                    self.say_seen = None
                return True
            if renpy.get_screen("input"):
                return "카이"
            ch = renpy.get_screen("choice")
            if ch:
                items = ch.scope["items"]
                n = self.next_choice or 0
                self.next_choice = None
                self.log("  choose %d: %s" % (n, items[n].caption))
                return items[n].action()
            bc = renpy.get_screen("battle_command")
            if bc:
                if self.battle_shot:
                    if self.ui_seen is None:
                        self.ui_seen = now
                    if now - self.ui_seen < 0.6:
                        return None
                    _do_shot(self.battle_shot)
                    self.log("  shot  " + self.battle_shot)
                    self.battle_shot = None
                    self.ui_seen = None
                b, actor = bc.scope["b"], bc.scope["actor"]
                return mhrpg.ally_command(b, actor)       # 평범한 플레이어처럼 행동
            for scr in ("shop_view", "inventory_view"):
                if renpy.get_screen(scr):
                    if self.ui_seen is None:
                        self.ui_seen = now
                    if now - self.ui_seen < 0.6:
                        return None
                    if self.ui_shot:
                        _do_shot(self.ui_shot)
                        self.log("  shot  " + self.ui_shot)
                        self.ui_shot = None
                    self.ui_seen = None
                    return True                            # 화면 닫기
            if not renpy.get_screen("location_view"):
                return None
            if now - self.last_action < 0.7:     # 화면 전환(dissolve)이 끝날 때까지
                return None
            while self.i < len(self.steps):
                step = self.steps[self.i]
                self.i += 1
                kind = step[0]
                if kind == "shot":
                    _do_shot(step[1])
                    self.log("  shot  " + step[1])
                elif kind == "expect":
                    self.check(step[1], step[2])
                elif kind == "choose":
                    self.next_choice = step[1]
                elif kind == "shot_say":
                    self.say_shot = step[1]
                elif kind == "shot_battle":
                    self.battle_shot = step[1]
                elif kind == "shot_ui":
                    self.ui_shot = step[1]
                elif kind == "call":                       # 파이썬 함수 직접 실행 (구매·장착 등)
                    self.log("call  %s%r" % (step[1], tuple(step[2:])))
                    eval(step[1], store.__dict__)(*step[2:])
                elif kind == "log":
                    self.log(step[1])
                elif kind == "sleep":                      # 다음 단계까지 step[1] 초 기다리기
                    self.last_action = now + step[1] - 0.7
                    return None
                else:
                    self.last_action = now
                    return self.act(step)
            self.log("steps finished but game still running — stopping")
            renpy.jump("autotest_finish")

        def act(self, step):
            kind = step[0]
            if kind == "click":
                for o in visible_objects(store.here):
                    if o.id == step[1]:
                        self.log("click %s/%s (%s)" % (store.here, o.id, o.tip))
                        return o.action()
                self.failed += 1
                self.log("  FAIL  보이는 물건 없음: %s/%s" % (store.here, step[1]))
                return None
            if kind == "talk":
                if step[1] in [mid for mid, x in npcs_here(store.here)]:
                    self.log("talk %s @ %s" % (step[1], store.here))
                    return TalkTo(step[1])()
                self.failed += 1
                self.log("  FAIL  여기 없는 인물: %s @ %s (%s)" % (step[1], store.here, TODS[store.tod]))
                return None
            if kind == "open":                             # 라벨로 이동해 화면 열기 (상점·소지품)
                self.log("open  " + step[1])
                renpy.jump(step[1])
            if kind == "wait":
                self.log("wait  %s" % TODS[store.tod])
                return WaitTick()()
            raise Exception("unknown step %r" % (step,))

    DRIVER = AutoDriver()
    FINAL_CHECK = None      # 게임이 끝난 뒤 검사할 (식, 설명)


screen autodriver():
    zorder 1000
    timer 0.1 repeat True action Function(DRIVER.tick)


label autotest_finish:
    $ DRIVER.check(FINAL_CHECK[0], FINAL_CHECK[1]) if FINAL_CHECK else None
    $ autotest_log("RESULT  pass=%d fail=%d  day=%d tod=%s main=%s score=%s" % (
        DRIVER.passed, DRIVER.failed, day, TODS[tod], MAIN.current, inspection_score))
    $ autotest_log("quest_log:")
    python:
        for row in quest_log:
            autotest_log("  %s" % (row,))
    $ autotest_log("done")
    $ renpy.quit()
