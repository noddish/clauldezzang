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
##       ("shot", 이름)          스크린샷
##       ("expect", "식", "설명") 식이 참인지 검사해 PASS/FAIL 기록
##       ("choose", 번호)        다음 선택지에서 고를 번호
##       ("shot_say", 이름)      다음에 나오는 대사 장면을 스크린샷
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
                elif kind == "log":
                    self.log(step[1])
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
