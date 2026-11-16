## ============================================================================
## characters/npcs.rpy — 마르타, 핍, 그레고르 (M3 전까지 임시 실루엣)
##
## 표정 속성(happy, angry …)을 지금부터 대본에 써 둘 수 있게 layeredimage 로 정의한다.
## M3 에서 그림이 생기면 always/attribute 의 이미지만 바꾸면 된다.
## ============================================================================

init -40 python:
    def PlaceholderSprite(name, color, height=640):
        """480x720 캔버스 바닥에 붙은 실루엣 + 이름"""
        body = Frame(Solid(color), 0, 0)
        return Fixed(
            Transform(body, xsize=300, ysize=height, xalign=0.5, yalign=1.0),
            Transform(Solid(color), xsize=150, ysize=150, xalign=0.5, ypos=720 - height - 120),
            Text(name, size=34, color="#ffffff", xalign=0.5, ypos=720 - height + 60),
            Text("임시", size=20, color="#ffffffaa", xalign=0.5, ypos=720 - height + 104),
            xysize=(480, 720),
        )

layeredimage martha:
    always PlaceholderSprite("마르타", "#8a5a44")
    group face:
        attribute neutral default Null()
        attribute happy Null()
        attribute angry Null()
        attribute surprised Null()
    group talking:
        attribute speaking Null()     # 말할 때 자동으로 붙는 속성 (M3 에서 입 움직임 그림)

layeredimage pip:
    always PlaceholderSprite("핍", "#5a7a3a", height=470)
    group face:
        attribute neutral default Null()
        attribute happy Null()
        attribute sad Null()
        attribute surprised Null()
    group talking:
        attribute speaking Null()

layeredimage gregor:
    always PlaceholderSprite("그레고르", "#3a4a6a", height=660)
    group face:
        attribute neutral default Null()
        attribute happy Null()
        attribute angry Null()
    group talking:
        attribute speaking Null()

define m = Character("마르타", image="martha", color="#e8a87c")
define p = Character("핍", image="pip", color="#a8d86a")
define g = Character("그레고르", image="gregor", color="#9fb4e8")
