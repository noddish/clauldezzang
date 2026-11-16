## ============================================================================
## locations/events.rpy — 장소 진입 이벤트(enter_<장소>)와 물건 클릭
## 진입 이벤트는 (첫 방문 여부)를 인자로 받는다.
## ============================================================================

## ---------------------------------------------------------------- 길드하우스
label guild_bed:
    if tod < 2:
        think "아직 잘 시간은 아니다."
        jump main_loop
    think "오늘은 이만 자자."
    scene black
    with fade
    $ sleep_to_next_day()
    scene expression location_bg(here)
    with fade
    n "[day]일차 아침이 밝았다."
    jump main_loop

label guild_desk:
    if RUBY.is_state("flint_lost"):
        think "책상 서랍 안쪽에… 있다. 루비의 부싯돌이다."
        $ add_item("flint")
        $ RUBY.trigger("T_found")
    else:
        think "삼촌의 길드 일지다. 마지막 장에 '루비를 잘 부탁한다'라고 적혀 있다."
    jump main_loop

label guild_board:
    think "길드 의뢰판. 붙어 있는 건 '고양이 찾음 (해결됨)' 한 장뿐이다."
    jump main_loop

label guild_hearth:
    if ruby_flame:
        think "루비가 부싯돌로 피운 불이 따뜻하게 타오른다."
    else:
        think "불이 꺼진 벽난로. 부싯돌이 있어야 피울 수 있다."
    jump main_loop

label guild_pantry:
    think "찬장에 빵과 치즈가 조금 있다. 길드 재정이 눈에 보인다."
    jump main_loop

label guild_stove:
    think "화덕 위 냄비에 루비가 끓인 수프가 남아 있다."
    jump main_loop


## ---------------------------------------------------------------- 마을
label square_well:
    think "마을 우물. 동전을 던지면 소원이 이루어진다는데… 그럴 돈이 없다."
    jump main_loop

label square_notice:
    think "마을 게시판: '이끼 동굴 출입 주의 — 큰 두꺼비 목격'"
    jump main_loop

label tavern_board:
    if MAIN.is_state("board"):
        think "의뢰 게시판에 '숲길 슬라임 퇴치'가 붙어 있다. 마르타에게 물어보자."
    else:
        think "지금은 받을 만한 의뢰가 없다."
    jump main_loop

label tavern_cellar:
    think "지하 창고 문을 열자 끈적한 소리가 들린다."
    call battle("tavern_cellar")
    if _return == "win":
        $ MARTHA.trigger("T_cleared")
        $ tick()
    jump main_loop

label shop_shelf:
    think "회복약, 해독초, 철검… 상점은 M2 에서 열린다."
    jump main_loop


## ---------------------------------------------------------------- 숲과 동굴
label enter_forest(first=False):
    if MAIN.is_state("forest"):
        show ruby at stage_right
        with dissolve
        r "저기 봐, 슬라임이야! 길드장님, 첫 실전이지? 내 뒤에 바짝 붙어!"
        hide ruby
        call battle("forest")
        if _return == "win":
            $ MAIN.trigger("T_slimes_done")
            $ tick()
            show ruby happy at stage_right
            r "해냈다! 마르타한테 보고하러 가자!"
            hide ruby
    elif first:
        think "약초 냄새가 나는 숲길이다."
    return

label forest_bush:
    think "수풀을 헤쳐 봤다. (임의 조우는 M2 에서)"
    jump main_loop

label enter_cave_1(first=False):
    if first:
        think "축축하고 미끄러운 동굴이다. 벽의 이끼가 희미하게 빛난다."
        $ tick()
    return

label cave_chest:
    $ cave_chest_opened = True
    think "낡은 상자 안에 회복약이 들어 있다."
    $ add_item("potion")
    jump main_loop

label enter_cave_2(first=False):
    if MAIN.is_state("cave"):
        n "동굴 가장 안쪽, 집채만 한 두꺼비가 짐 꾸러미를 깔고 앉아 있다."
        show ruby angry at stage_right
        r "저 녀석이 핍의 짐을 깔고 앉았어! 가자!"
        hide ruby
        call battle("boss_toad")
        if _return == "win":
            $ add_item("pip_cargo")
            $ MAIN.trigger("T_boss_done")
            $ tick()
    return


## ---------------------------------------------------------------- 3일차 감사 (강제 이벤트)
label day3_inspection:
    $ here = "guild_hall"
    scene expression location_bg(here)
    with fade
    show gregor at stage_right
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
