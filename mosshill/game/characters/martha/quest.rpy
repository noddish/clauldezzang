## ============================================================================
## characters/martha/quest.rpy — 마르타의 위치표와 서브 퀘스트 (지하 창고)
## ============================================================================

init -4 python:
    MARTHA = Machine("martha", "마르타의 지하 창고", schedule=[
        ["tavern", "tavern", "tavern", "tavern"],
        ["tavern", "tavern", "tavern", "tavern"],
    ])
    MARTHA.state("cellar",        "선술집 지하 창고의 슬라임을 치우자.")
    MARTHA.state("cellar_report", "마르타에게 창고 청소를 보고하자.")
    MARTHA.state("done",          "")
    MARTHA.on("cellar",        "T_cleared", "cellar_report")
    MARTHA.on("cellar_report", "T_paid",    "done")
