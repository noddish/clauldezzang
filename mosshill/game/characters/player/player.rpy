## ============================================================================
## characters/player/player.rpy — 주인공
## 그림은 M3 에서 만든다 (기획서 7장: 480x720, 3/4 측면, 오른쪽을 바라봄).
## ============================================================================

default player_name = "카이"

## 이름은 대사창에 [player_name] 으로 들어간다
define me = Character("[player_name]", color="#ffd38a")
## 생각 (괄호 독백)
define think = Character("[player_name]", color="#ffd38a", what_prefix="( ", what_suffix=" )", what_italic=True)
## 해설
define n = Character(None, what_italic=True)
