## ============================================================================
## story/quests.rpy — 퀘스트 단계와 NPC 위치표 (원작 characters/*_fsm.rpy 에 해당)
##
## 단계 문장 = HUD 퀘스트 힌트. 트리거는 대사·이벤트 label 에서 발생시킨다.
## ============================================================================

init -4 python:

    ## ---------------------------------------------------------------- 메인 (3일)
    MAIN = Machine("main", "길드 면허를 지켜라", initial="intro")
    MAIN.state("intro",          "길드 앞에서 루비를 만났다.")
    MAIN.state("board",          "선술집 '졸린 곰'의 의뢰 게시판에서 일을 받자.")
    MAIN.state("forest",         "숲길의 슬라임을 퇴치하자.")
    MAIN.state("report_martha",  "선술집의 마르타에게 퇴치를 보고하자.")
    MAIN.state("day1_rest",      "오늘은 길드로 돌아가 쉬자. (내 방 침대)")
    MAIN.state("pip_job",        "잡화점의 핍이 찾는다던데? 가 보자.")
    MAIN.state("cave",           "이끼 동굴 깊은 곳에서 핍의 짐을 찾자.")
    MAIN.state("return_cargo",   "찾은 짐을 핍에게 돌려주자.")
    MAIN.state("day2_rest",      "내일 오후에 감사관이 온다. 푹 쉬어 두자.")
    MAIN.state("inspection",     "오후에 감사관이 온다. 길드 홀에서 기다리자.")
    MAIN.state("end",            "")

    MAIN.on("intro",         "T_intro_done",  "board")
    MAIN.on("board",         "T_take_job",    "forest")
    MAIN.on("forest",        "T_slimes_done", "report_martha")
    MAIN.on("report_martha", "T_report",      "day1_rest")
    MAIN.on("day1_rest",     "T_all_sleep",   "pip_job")
    MAIN.on("pip_job",       "T_take_cave",   "cave")
    MAIN.on("cave",          "T_boss_done",   "return_cargo")
    MAIN.on("return_cargo",  "T_cargo",       "day2_rest")
    MAIN.on("day2_rest",     "T_all_sleep",   "inspection")
    MAIN.on("inspection",    "T_inspected",   "end")

    ## ---------------------------------------------------------------- 루비 (서브: 부싯돌)
    ## 위치표: 아침 부엌 / 오후 주인공과 동행(화면에 없음) / 저녁 길드 홀 / 밤 자기 방
    RUBY = Machine("ruby", "루비의 부싯돌", schedule=[
        ["guild_kitchen", None, "guild_hall", None],
        ["guild_kitchen", None, "guild_hall", None],
    ])
    RUBY.state("flint_lost",   "루비가 부싯돌을 잃어버렸다. 내 방 책상 근처를 찾아보자.")
    RUBY.state("flint_return", "부싯돌을 찾았다! 저녁에 길드 홀의 루비에게 돌려주자.")
    RUBY.state("done",         "")
    RUBY.on("flint_lost",   "T_found",  "flint_return")
    RUBY.on("flint_return", "T_return", "done")

    ## ---------------------------------------------------------------- 마르타 (서브: 지하 창고)
    MARTHA = Machine("martha", "마르타의 지하 창고", schedule=[
        ["tavern", "tavern", "tavern", "tavern"],
        ["tavern", "tavern", "tavern", "tavern"],
    ])
    MARTHA.state("cellar",        "선술집 지하 창고의 슬라임을 치우자.")
    MARTHA.state("cellar_report", "마르타에게 창고 청소를 보고하자.")
    MARTHA.state("done",          "")
    MARTHA.on("cellar",        "T_cleared", "cellar_report")
    MARTHA.on("cellar_report", "T_paid",    "done")

    ## ---------------------------------------------------------------- 핍 (위치만. 의뢰는 메인에 포함)
    PIP = Machine("pip", "", schedule=[
        ["shop", "shop", "square", None],
        ["shop", "shop", "square", None],
    ])

    CHAR_NAMES = {"ruby": "루비", "martha": "마르타", "pip": "핍", "gregor": "그레고르"}

    ## ---------------------------------------------------------------- 강제 이벤트
    def pending_event():
        """메인 루프가 장소 화면을 띄우기 전에 확인하는 강제 이벤트"""
        if store.day >= LAST_DAY and store.tod >= 1 and not MAIN.is_state("end"):
            return "day3_inspection"
        return None

default game_over = False
default ruby_flame = False          # 불꽃베기 해금 (부싯돌 퀘스트 보상, M2 에서 사용)
default inspection_score = 0
