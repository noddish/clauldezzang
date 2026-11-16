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
        ("shot", "m1_02_kitchen_ruby"),
        ("talk", "ruby"),
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
        ("shot_say", "m1_05_martha_say"),
        ("talk", "martha"),
        ("expect", "MAIN.is_state('forest')", "의뢰 수락 → 메인=forest"),
        ("click", "exit"), ("click", "forest"),
        ("expect", "MAIN.is_state('report_martha') and tod == 1", "슬라임 퇴치(임시 전투) 후 오후"),
        ("click", "town"), ("click", "tavern"), ("talk", "martha"),
        ("expect", "MAIN.is_state('day1_rest') and MARTHA.is_state('cellar')", "보고 완료 + 창고 의뢰 시작"),
        ("click", "cellar"),
        ("expect", "MARTHA.is_state('cellar_report') and tod == 2", "창고 청소 후 저녁"),
        ("talk", "martha"),
        ("expect", "MARTHA.is_state('done') and has_item('potion', 2)", "창고 보상 회복약 2"),
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
    $ DRIVER.load(M1_LAZY_STEPS)
    $ FINAL_CHECK = ("MAIN.is_state('end') and inspection_score == 0 and game_over", "아무것도 안 하면 실적 0/4 로 종료")
    show screen autodriver
    call start
    jump autotest_finish
