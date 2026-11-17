## ============================================================================
## core/data.rpy — game/data/*.json 읽기
##
## 숫자와 내용(아이템, 스킬, 적, 조우표, 상점, 레벨업 표)은 JSON 에 두고
## 코드는 이름(id)으로만 찾는다. → 밸런스 조정할 때 코드를 건드리지 않는다.
##
##   DATA.items["potion"]["name"]     → "회복약"
##   DATA.enemies["slime"]["hp"]      → 18
## ============================================================================

init -100 python:
    import json

    class _GameData(object):
        FILES = ("items", "skills", "enemies", "encounters", "shops", "levels")

        def __init__(self):
            for name in self.FILES:
                with renpy.open_file("data/%s.json" % name, encoding="utf-8") as f:
                    setattr(self, name, json.load(f))

        def check(self):
            """데이터끼리 서로 가리키는 id 가 실제로 있는지 검사. 문제 목록을 돌려준다."""
            problems = []
            for eid, e in self.enemies.items():
                for d in e.get("drops", []):
                    if d["item"] not in self.items:
                        problems.append("적 %s 의 드롭 아이템 %s 없음" % (eid, d["item"]))
                for s in e.get("skills", []):
                    if s not in self.skills:
                        problems.append("적 %s 의 스킬 %s 없음" % (eid, s))
            for eid, e in self.enemies.items():
                for d in e.get("drops", []):
                    if self.items[d["item"]]["type"] == "key":
                        problems.append("적 %s 가 중요 아이템 %s 를 드롭함 (퀘스트 아이템은 이벤트에서 줄 것)" % (eid, d["item"]))
            for zone, table in self.encounters.items():
                for group in table["groups"]:
                    for eid in group["enemies"]:
                        if eid not in self.enemies:
                            problems.append("조우표 %s 의 적 %s 없음" % (zone, eid))
            for shop, s in self.shops.items():
                for iid in s["stock"]:
                    if iid not in self.items:
                        problems.append("상점 %s 의 품목 %s 없음" % (shop, iid))
            for who, table in self.levels.items():
                for lv, row in table.items():
                    for s in row.get("learn", []):
                        if s not in self.skills:
                            problems.append("%s 레벨 %s 스킬 %s 없음" % (who, lv, s))
            return problems

    DATA = _GameData()
