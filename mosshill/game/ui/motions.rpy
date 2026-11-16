## ============================================================================
## motions.rpy — 그림을 더 그리지 않고 코드(ATL)로 만드는 움직임
## ============================================================================
##
## 사용법:   show ruby at 위치, 모션
##           show ruby at stage_right, hop
##
## ATL 기본 문법:
##     linear 0.3 xoffset 50     0.3초 동안 일정한 속도로 xoffset 을 50으로
##     ease   0.3 ...            천천히 시작해서 천천히 끝남 (가장 자연스러움)
##     easein / easeout          끝만 / 시작만 부드럽게
##     pause 1.0                 1초 대기
##     repeat                    처음부터 반복 (repeat 2 = 2번 더)
##     parallel:                 여러 움직임을 동시에
## ============================================================================


## ---------------------------------------------------------------- 위치 (원작 배치)
## 대화: 주인공은 왼쪽에서 오른쪽을 보고, 상대는 오른쪽에서 왼쪽을 본다.
transform stage_left:
    xcenter 0.27 yalign 1.0
transform stage_center:
    xcenter 0.5 yalign 1.0
transform stage_right:
    xcenter 0.7 yalign 1.0


## ---------------------------------------------------------------- 대기 / 감정
transform breathing:            # 숨쉬기 — 가만히 서 있어도 살아있는 느낌
    yoffset 0
    ease 1.6 yoffset 4
    ease 1.6 yoffset 0
    repeat

transform hop:                  # 깡충 — 놀람, 기쁨
    yoffset 0
    easeout 0.12 yoffset -28
    easein  0.12 yoffset 0

transform double_hop:           # 신나서 두 번 깡충
    yoffset 0
    easeout 0.10 yoffset -22
    easein  0.10 yoffset 0
    easeout 0.10 yoffset -22
    easein  0.10 yoffset 0

transform shiver:               # 부들부들 — 공포, 분노
    xoffset 0
    linear 0.05 xoffset -3
    linear 0.05 xoffset 3
    repeat 6
    linear 0.05 xoffset 0

transform nod:                  # 끄덕
    yoffset 0
    ease 0.15 yoffset 10
    ease 0.15 yoffset 0

transform droop:                # 풀죽음 — 살짝 가라앉고 어두워짐
    ease 0.5 yoffset 25 matrixcolor BrightnessMatrix(-0.15)


## ---------------------------------------------------------------- 등장 / 퇴장
transform slide_in_right:
    xoffset 400 alpha 0.0
    easein 0.45 xoffset 0 alpha 1.0

transform slide_in_left:
    xoffset -400 alpha 0.0
    easein 0.45 xoffset 0 alpha 1.0

transform fade_out_down:        # 쓰러짐 / 사라짐
    ease 0.6 yoffset 60 alpha 0.0


## ---------------------------------------------------------------- 연출
transform close_up:             # 얼굴 클로즈업
    ease 0.4 zoom 1.6 yoffset 520

transform back_to_normal:       # 클로즈업/어두움 등 해제
    ease 0.4 zoom 1.0 yoffset 0 xoffset 0 alpha 1.0 matrixcolor BrightnessMatrix(0.0)

transform silhouette:           # 실루엣 (정체를 숨길 때)
    matrixcolor BrightnessMatrix(-1.0)

transform flipped:              # 좌우 반전 (반대쪽을 보게)
    xzoom -1.0


## ---------------------------------------------------------------- 전투용
transform attack_lunge(dist=160):   # 앞으로 돌진했다가 복귀 (dist 로 거리 조절)
    xoffset 0
    easein 0.12 xoffset dist
    pause 0.05
    easeout 0.25 xoffset 0

transform hit_shake:            # 피격 흔들림
    xoffset 0
    linear 0.04 xoffset -14
    linear 0.04 xoffset 14
    repeat 3
    linear 0.04 xoffset 0

transform hit_flash:            # 피격 번쩍 (빨갛게 → 원래대로) + 흔들림 동시에
    parallel:
        matrixcolor TintMatrix("#ffffff")
        linear 0.06 matrixcolor TintMatrix("#ff5050")
        linear 0.25 matrixcolor TintMatrix("#ffffff")
    parallel:
        xoffset 0
        linear 0.04 xoffset -14
        linear 0.04 xoffset 14
        repeat 3
        linear 0.04 xoffset 0

transform heal_glow:            # 회복 (초록빛)
    matrixcolor TintMatrix("#ffffff")
    linear 0.2 matrixcolor TintMatrix("#90ff90")
    linear 0.4 matrixcolor TintMatrix("#ffffff")

transform defend_pose:          # 방어 — 살짝 웅크림
    ease 0.15 yoffset 12 xoffset -10

transform enemy_idle:           # 슬라임 출렁출렁
    yzoom 1.0 xzoom 1.0
    ease 0.6 yzoom 0.92 xzoom 1.06
    ease 0.6 yzoom 1.0 xzoom 1.0
    repeat


## ---------------------------------------------------------------- 데미지 숫자
transform damage_pop:           # 숫자가 튀어올랐다 사라짐
    alpha 0.0 yoffset 0 zoom 0.6
    parallel:
        easeout 0.15 alpha 1.0 zoom 1.2
        ease 0.1 zoom 1.0
    parallel:
        easeout 0.6 yoffset -70
    pause 0.2
    linear 0.3 alpha 0.0
