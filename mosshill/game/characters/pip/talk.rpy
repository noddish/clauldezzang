## ============================================================================
## characters/pip/talk.rpy — 핍과 대화
## ============================================================================

## 인물을 눌렀을 때 (원작 button.rpy 의 <이름>_button_dialogue). 퀘스트 단계에 따라 분기한다.
## 배경은 흐리게(원작처럼 인물이 돋보이게), 장소 안의 다른 인물은 그대로 보인다.

label pip_talk:
    scene expression location_backdrop(here, blur=True, without="pip")
    show kai at stage_left
    show pip at stage_right
    with dissolve

    if MAIN.is_state("pip_job"):
        p surprised "아이고 길드장님! 마침 잘 왔어요!"
        p "어제 짐마차가 이끼 동굴 앞을 지나다 짐 하나를 떨어뜨렸는데, 두꺼비 놈이 물고 들어갔지 뭐예요!"
        p "찾아 주시면 80골드! 협회 실적에도 딱이죠?"
        $ MAIN.trigger("T_take_cave")

    elif MAIN.is_state("return_cargo") and has_item("pip_cargo"):
        p happy "제 짐! 두꺼비 침 범벅이지만… 무사하네요!"
        $ remove_item("pip_cargo")
        $ add_gold(80)
        $ MAIN.trigger("T_cargo")

    else:
        p "어서 오세요~ 물건 구경은 진열장에서! 슬라임 젤리나 고블린 송곳니도 사들여요."

    hide pip
    hide kai
    with dissolve
    jump main_loop
