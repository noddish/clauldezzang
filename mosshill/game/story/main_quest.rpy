## ============================================================================
## story/main_quest.rpy — 메인 퀘스트 (3일). 인물별 서브 퀘스트는 characters/<이름>/quest.rpy
## 단계 문장 = HUD 퀘스트 힌트. 트리거는 대사·이벤트 label 에서 발생시킨다.
## ============================================================================

default game_over = False
default inspection_score = 0

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
