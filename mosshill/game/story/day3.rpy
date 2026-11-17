## ============================================================================
## story/day3.rpy — 3일차 오후, 감사관의 실적 감사 (강제 이벤트 → 게임 끝)
## ============================================================================

init -5 python:
    event("day3_inspection", "day3_inspection", on="idle", priority=100,
          when=lambda: store.day >= LAST_DAY and store.tod >= 1 and not MAIN.is_state("end"))

label day3_inspection:
    $ here = "guild_hall"
    scene expression location_backdrop(here, blur=True)
    with fade
    show kai at stage_left
    show gregor at stage_right
    with dissolve
    g "모험가 협회 감사관 그레고르다. 이끼발굽 길드의 실적을 보고하게."

    python:
        inspection_score = sum([
            MAIN.reached("report_martha"),     # 숲 슬라임 퇴치
            MAIN.reached("day2_rest"),         # 핍의 짐 회수 (두꺼비 왕)
            MARTHA.is_state("done"),           # 선술집 창고
            RUBY.is_state("done"),             # 길드원 돌보기
        ])

    if inspection_score >= 3:
        show gregor happy at stage_right
        g "사흘 만에 이 정도라니. 면허는 유지다. 앞으로를 기대하지."
    elif inspection_score >= 1:
        g "부족하지만 가능성은 보이는군. 한 달 유예를 주겠다."
    else:
        show gregor angry at stage_right
        g "실적이 전혀 없군. 유감이지만…"

    $ MAIN._enter("end")
    n "— 맛보기판 M1 끝. 실적 [inspection_score]/4 —"
    $ game_over = True
    return
