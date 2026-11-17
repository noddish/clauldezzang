## ============================================================================
## characters/martha/talk.rpy — 마르타와 대화
## ============================================================================

## 인물을 눌렀을 때 (원작 button.rpy 의 <이름>_button_dialogue). 퀘스트 단계에 따라 분기한다.
## 배경은 흐리게(원작처럼 인물이 돋보이게), 장소 안의 다른 인물은 그대로 보인다.

label martha_talk:
    scene expression location_backdrop(here, blur=True, without="martha")
    show kai at stage_left
    show martha at stage_right
    with dissolve

    if MAIN.is_state("board"):
        m happy "오, 네가 그 조카구나. 길드가 망하기 직전이라며?"
        m "마침 일이 하나 있지. 숲길에 슬라임이 늘어서 약초꾼들이 못 다닌대."
        m "치우고 오면 40골드. 해볼래?"
        me "할게요."
        $ MAIN.trigger("T_take_job")

    elif MAIN.is_state("report_martha"):
        m happy "벌써 다 치웠다고? 제법인데!"
        $ add_gold(40)
        $ MAIN.trigger("T_report")
        m "그리고… 하나 더 부탁하자. 우리 지하 창고에도 슬라임이 들어앉았거든."
        m "시간 될 때 치워 주면 회복약 두 병 줄게."
        $ MARTHA.start()

    elif MARTHA.is_state("cellar_report"):
        m happy "창고가 깨끗해졌네! 약속한 거야."
        $ add_item("potion", 2)
        $ MARTHA.trigger("T_paid")

    else:
        m "뭐 마실래? …농담이야, 넌 아직 일할 시간이잖아."

    hide martha
    hide kai
    with dissolve
    jump main_loop
