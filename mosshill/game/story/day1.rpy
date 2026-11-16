## ============================================================================
## story/day1.rpy — 1일차
## M0: 시작 → 이름 입력 → 루비와 첫 만남까지만. 나머지는 M1 이후에 채운다.
## ============================================================================

label start:
    scene expression Placeholder("길드하우스 앞 — 1일차 아침")
    with fade

    n "이끼 낀 지붕, 삐걱거리는 간판. 여기가 삼촌이 남긴 모험가 길드다."

    python:
        name = renpy.input("주인공의 이름은? (최대 8글자)", default="카이", length=8)
        player_name = name.strip() or "카이"

    think "삼촌… 길드를 물려준다더니, 이건 거의 폐가잖아."

    show ruby surprised at stage_right, slide_in_right
    r "어? 혹시… 새 길드장님?!"

    show ruby happy at stage_right, double_hop
    r "와아, 진짜 왔다! 나는 루비. 이끼발굽 길드의 마지막 멤버이자, 에이스 검사야!"

    me "…멤버가 너 혼자라고?"

    show ruby sad at stage_right, droop
    r "응… 다들 도시 길드로 가 버렸거든. 그리고 이거."

    n "루비가 구겨진 편지를 내밀었다. 모험가 협회의 도장이 찍혀 있다."

    show ruby angry at stage_right, back_to_normal, shiver
    r "'3일 뒤 감사. 실적이 없으면 면허 취소.' 이게 말이 돼?!"

    me "3일…"

    show ruby neutral at stage_right, nod
    r "그러니까 길드장님, 오늘부터 바로 일하자! 의뢰는 마르타네 선술집 게시판에 있어."

    n "— M0 끝. 여기까지가 뼈대입니다. 다음 단계(M1)에서 마을과 시간 시스템이 붙습니다. —"
    return
