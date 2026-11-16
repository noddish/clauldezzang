## ============================================================================
## battle.rpy — 아주 작은 턴제 전투 (연출 위주 예제)
## ============================================================================
## 구조:
##   1) 계산은 순수 Python (Fighter 클래스)          ← 화면과 분리
##   2) 행동 선택은 screen (battle_ui)                ← 버튼
##   3) 연출은 show ... at 모션                       ← motions.rpy
## 실제 게임에서는 1)을 rpg/ 폴더로 분리하고 스킬/아이템을 데이터로 빼면 된다.
## ============================================================================

init python:
    class Fighter(object):
        def __init__(self, name, hp, atk, df):
            self.name = name
            self.max_hp = self.hp = hp
            self.atk = atk
            self.df = df
            self.guarding = False

        @property
        def alive(self):
            return self.hp > 0

        def take(self, raw):
            dmg = max(1, raw - self.df)
            if self.guarding:
                dmg = max(1, dmg // 2)
            self.hp = max(0, self.hp - dmg)
            return dmg


## 데미지 숫자 표시용 (text 를 이미지처럼 띄움)
screen damage_number(amount, xpos, color="#ffffff"):
    text "[amount]" at damage_pop:
        xpos xpos ypos 0.35 xanchor 0.5
        size 64 bold True color color outlines [(4, "#000000", 0, 0)]
    timer 1.2 action Hide("damage_number")


screen battle_ui(hero_f, enemy_f):
    ## 상단 HP 바
    frame:
        xalign 0.03 yalign 0.03 xsize 360 padding (16, 12)
        vbox:
            text "레온  HP [hero_f.hp]/[hero_f.max_hp]" size 24
            bar value hero_f.hp range hero_f.max_hp xsize 320
    frame:
        xalign 0.97 yalign 0.03 xsize 360 padding (16, 12)
        vbox:
            text "슬라임  HP [enemy_f.hp]/[enemy_f.max_hp]" size 24
            bar value enemy_f.hp range enemy_f.max_hp xsize 320

    ## 하단 명령
    frame:
        xalign 0.5 yalign 0.97 padding (20, 14)
        hbox:
            spacing 24
            textbutton "공격" action Return("attack")
            textbutton "방어" action Return("guard")
            textbutton "회복" action Return("heal")


label battle_slime:
    $ hero_f = Fighter("레온", 30, 9, 2)
    $ enemy_f = Fighter("슬라임", 28, 7, 1)

    scene bg_field
    show hero armor a_sword normal_brows blink neutral at stage_left, breathing
    show slime at stage_right, enemy_idle
    with fade

    while hero_f.alive and enemy_f.alive:
        $ hero_f.guarding = False
        call screen battle_ui(hero_f, enemy_f)
        $ cmd = _return

        ## -------- 플레이어 턴
        if cmd == "attack":
            show hero angry_brows frown at stage_left, attack_lunge(220)
            pause 0.15
            $ dmg = enemy_f.take(hero_f.atk + renpy.random.randint(0, 3))
            show slime_hurt as slime at stage_right, hit_flash
            hide screen damage_number
            show screen damage_number(dmg, 0.75)
            pause 0.5
            show slime at stage_right, enemy_idle
        elif cmd == "guard":
            $ hero_f.guarding = True
            show hero sad_brows blink neutral at stage_left, defend_pose
            pause 0.3
        else:
            $ heal = 8
            $ hero_f.hp = min(hero_f.max_hp, hero_f.hp + heal)
            show hero happy_eyes smile at stage_left, heal_glow
            hide screen damage_number
            show screen damage_number("+%d" % heal, 0.25, "#7dff7d")
            pause 0.6

        if not enemy_f.alive:
            show slime at stage_right, fade_out_down
            pause 0.7
            return "win"

        ## -------- 적 턴
        show slime at stage_right, attack_lunge(-200)
        pause 0.15
        $ dmg = hero_f.take(enemy_f.atk + renpy.random.randint(0, 3))
        show hero up_brows wide_eyes open at stage_left, hit_flash
        hide screen damage_number
        show screen damage_number(dmg, 0.25, "#ff8080")
        with small_shake
        pause 0.5
        show slime at stage_right, enemy_idle
        show hero normal_brows blink neutral at stage_left, breathing

    return "lose"
