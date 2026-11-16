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


## 실제 대사가 나오는 중에 0.8초 뒤 스크린샷을 찍고 다음으로 넘어간다 (클릭 대신)
screen autoshot(name):
    timer 0.8 action [Function(_do_shot, name), Return(True)]


label splashscreen:
    if AUTOTEST:
        jump expression "autotest_" + AUTOTEST
    return


## ---------------------------------------------------------------- M0
label autotest_m0:
    python:
        problems = DATA.check()
        autotest_log("data check: %d problem(s)" % len(problems))
        for p in problems:
            autotest_log("  " + p)
        autotest_log("items=%d skills=%d enemies=%d" % (len(DATA.items), len(DATA.skills), len(DATA.enemies)))

    scene expression Placeholder("길드하우스 앞 — 1일차 아침")
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
