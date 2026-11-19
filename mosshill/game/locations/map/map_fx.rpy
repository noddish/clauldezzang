## ============================================================================
## locations/map/map_fx.rpy — 지도 위를 지나가는 구름과 갈매기
##
## 원작 지도도 바닥 그림 위에 움직이는 장식(차 3대, 구름, 굴뚝 연기, 반짝임)을 얹었다.
## 원작 구름은 화면만 한 구름 그림 1장을 80초 동안 대각선으로 흘려보냈다.
## 여기서는 크기가 다른 구름 3개가 다른 속도로 흐르고, 땅에 옅은 그림자를 드리운다.
## 갈매기는 날갯짓 4장을 번갈아 보여 주며(원작의 2~3장 반복 그림과 같은 방식) 가끔 무리 지어 지나간다.
##
## 그림: images/map_fx/ — tools/art_pipeline.py mapfx (RAW/map_fx_sheet.png 한 장에서 잘라 냄)
## 저녁·밤은 다른 그림처럼 푸르스름하게(light_matrix), 밤(시간대 3)에는 갈매기가 없다.
## ============================================================================

## 갈매기 날갯짓 — 시작 장면만 다른 세 가지 (무리가 똑같이 퍼덕이지 않게)
image map_gull_a:
    "map_fx/gull_1.png"
    pause 0.09
    "map_fx/gull_2.png"
    pause 0.09
    "map_fx/gull_3.png"
    pause 0.09
    "map_fx/gull_4.png"
    pause 0.09
    repeat
image map_gull_b:
    "map_fx/gull_3.png"
    pause 0.09
    "map_fx/gull_4.png"
    pause 0.09
    "map_fx/gull_1.png"
    pause 0.09
    "map_fx/gull_2.png"
    pause 0.09
    repeat
image map_gull_c:
    "map_fx/gull_2.png"
    pause 0.11
    "map_fx/gull_3.png"
    pause 0.11
    "map_fx/gull_4.png"
    pause 0.11
    "map_fx/gull_1.png"
    pause 0.11
    repeat

init python:
    ## (그림, y 위치, 초당 이동 px, 그림자 거리) — 큰 구름일수록 느리게 (멀리 높이 떠 있는 느낌)
    MAP_CLOUDS = [
        ("map_fx/cloud_1", 20, 7.0, (60, 95)),
        ("map_fx/cloud_2", 320, 10.0, (50, 80)),
        ("map_fx/cloud_3", 540, 14.0, (40, 65)),
    ]
    MAP_FX_RIGHT = 1320          # 이 x 를 넘으면 화면 밖

    def map_cloud(name, shadow_off):
        """구름 + 땅에 드리운 그림자 한 덩어리"""
        return Fixed(
            Transform(name + "_shadow.png", xpos=shadow_off[0], ypos=shadow_off[1]),
            Transform(name + ".png", alpha=0.62),        # 반투명 — 아래 건물이 비쳐 보이게
            xysize=(360, 280))

    def map_flock():
        """갈매기 세 마리 (V자, 날아가는 쪽으로 살짝 기울임) + 땅에 비친 작은 그림자"""
        birds = [("map_gull_a", 100, 44), ("map_gull_b", 44, 8), ("map_gull_c", 38, 92)]
        parts = []
        for img, x, y in birds:
            parts.append(Transform(img, xpos=x + 30, ypos=y + 70, rotate=-12, alpha=0.18,
                                   matrixcolor=BrightnessMatrix(-1.0)))
        for img, x, y in birds:
            parts.append(Transform(img, xpos=x, ypos=y, rotate=-12))
        return Fixed(*parts, xysize=(260, 230))

    def map_cloud_plan():
        """지도를 열 때마다 구름의 처음 위치를 섞는다 → 열자마자 화면에 구름이 있다"""
        rv = []
        for name, y, speed, off in MAP_CLOUDS:
            x0 = renpy.random.randint(-300, 1100)
            rv.append((name, off, x0, y, (MAP_FX_RIGHT - x0) / speed, (MAP_FX_RIGHT + 360) / speed))
        return rv

## 구름: 처음엔 x0 에서 출발, 화면 밖으로 나가면 왼쪽 밖에서 다시
transform map_cloud_drift(x0, y, first, loop):
    subpixel True
    xpos x0 ypos y
    linear first xpos MAP_FX_RIGHT
    block:
        xpos -360
        linear loop xpos MAP_FX_RIGHT
        repeat

## 갈매기 무리: 지도를 열고 잠깐 뒤 한 번 지나가고, 그다음부터는 쉬었다 지나가기를 무작위로 (방향도 둘 중 하나)
transform map_flock_fly(delay):
    subpixel True
    alpha 0.0
    pause delay
    xzoom 1.0 xpos -220 ypos 560
    parallel:
        linear 16.0 xpos 1340 ypos 230
    parallel:
        linear 1.0 alpha 1.0
        pause 14.0
        linear 1.0 alpha 0.0
    block:
        choice:
            xzoom 1.0 xpos -220 ypos 560
            parallel:
                linear 16.0 xpos 1340 ypos 230
            parallel:
                linear 1.0 alpha 1.0
                pause 14.0
                linear 1.0 alpha 0.0
        choice:
            xzoom -1.0 xpos 1340 ypos 600
            parallel:
                linear 18.0 xpos -220 ypos 260
            parallel:
                linear 1.0 alpha 1.0
                pause 16.0
                linear 1.0 alpha 0.0
        choice:
            pause 20.0
        choice:
            pause 35.0
        repeat

transform map_fx_light:
    matrixcolor light_matrix()

screen ambient_map():
    default plan = map_cloud_plan()
    default flock_delay = renpy.random.uniform(2.0, 8.0)
    fixed at map_fx_light:
        for name, off, x0, y, first, loop in plan:
            add map_cloud(name, off) at map_cloud_drift(x0, y, first, loop)
        if tod < 3:
            add map_flock() at map_flock_fly(flock_delay)
