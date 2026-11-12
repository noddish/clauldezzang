extends RefCounted
## Engine-independent rules. Animation and layout never change these rules.

const MAP: Array[String] = [
	"#########",
	"####T####",
	"####.####",
	"###...###",
	"###...###",
	"####E####",
	"####D####",
	"####.####",
	"##.....##",
	"####S####",
	"#########",
]
const DIRECTIONS = [Vector2i(0, -1), Vector2i(1, 0), Vector2i(0, 1), Vector2i(-1, 0)]
const NAMES = ["아린", "로언", "이든", "세라"]
const ROLES = ["수호기사", "길잡이", "마도사", "치유사"]
const SKILLS = ["방패 강타", "관통 사격", "서리 창", "치유의 빛"]
const MAX_HP = [52, 38, 32, 36]
const MAX_MP = [15, 18, 26, 24]
const DAMAGE = [12, 11, 8, 9]
const COST = [4, 4, 6, 5]
const KEY_POS = Vector2i(6, 8)
const ENEMY_POS = Vector2i(4, 5)
const CHEST_POS = Vector2i(4, 1)
const DOOR_POS = Vector2i(4, 6)
const SAVE_VERSION = 1

var position := Vector2i(4, 9)
var facing := 0
var selected := 0
var hp: Array = MAX_HP.duplicate()
var mp: Array = MAX_MP.duplicate()
var enemy_hp := 96
var enemy_max_hp := 96
var has_key := false
var door_open := false
var chest_open := false
var potions := 2
var gold := 0
var turn := 0
var phase := "explore"
var visited: Dictionary = {}
var messages: Array[String] = []

func _init() -> void:
	_reveal()
	log_message("꺼진 봉인 너머에서 금속 긁는 소리가 들립니다.")

func tile(p: Vector2i) -> String:
	if p.y < 0 or p.y >= MAP.size() or p.x < 0 or p.x >= MAP[0].length():
		return "#"
	return MAP[p.y][p.x]

func is_floor(p: Vector2i) -> bool:
	return tile(p) != "#"

func ahead() -> Vector2i:
	return position + DIRECTIONS[facing]

func objective() -> String:
	if phase == "defeat": return "탐험이 끝났습니다. 새 탐험으로 다시 도전하세요."
	if chest_open: return "봉인을 되찾았습니다. 첫 탐험을 완료했습니다."
	if enemy_hp <= 0: return "북쪽 제단의 상자를 열어 봉인을 회수하세요."
	if phase == "combat": return "경비병을 쓰러뜨리세요. 치유와 물약을 활용하세요."
	if door_open: return "열린 문 너머의 경비병을 조사하세요."
	if has_key: return "북쪽 철문을 열고 안쪽으로 진입하세요."
	return "동쪽 벽감에서 청동 열쇠를 찾으세요."

func context_label() -> String:
	if phase == "defeat": return "새 탐험"
	if phase == "combat": return "기본 공격"
	var p := ahead()
	if not has_key and (p == KEY_POS or position == KEY_POS): return "열쇠 줍기"
	if p == DOOR_POS and not door_open: return "문 열기" if has_key else "잠긴 문 조사"
	if p == ENEMY_POS and enemy_hp > 0: return "경비병과 대치"
	if p == CHEST_POS and not chest_open: return "상자 열기"
	return "주변 조사"

func choose(index: int) -> void:
	if index >= 0 and index < 4 and hp[index] > 0:
		selected = index

func rotate(amount: int) -> Dictionary:
	if phase in ["combat", "defeat"]: return {}
	facing = posmod(facing + amount, 4)
	_reveal()
	return {"kind": "turn"}

func move(amount: int, strafe: bool = false) -> Dictionary:
	if phase in ["combat", "defeat"]: return {}
	var direction: Vector2i = DIRECTIONS[posmod(facing + 1, 4)] if strafe else DIRECTIONS[facing]
	var target := position + direction * amount
	if not is_floor(target):
		return {"kind": "blocked"}
	if target == DOOR_POS and not door_open:
		log_message("철문이 길을 막고 있습니다. 열쇠가 필요합니다." if not has_key else "열쇠를 꽂아 문을 열 수 있습니다.")
		return {"kind": "blocked"}
	if target == ENEMY_POS and enemy_hp > 0:
		phase = "combat"
		facing = 0 if position.y > ENEMY_POS.y else 2
		log_message("묘지의 경비병이 녹슨 칼을 들어 올립니다.")
		return {"kind": "engage"}
	position = target
	_reveal()
	return {"kind": "move"}

func interact() -> Dictionary:
	if phase == "defeat": return {}
	if phase == "combat": return act("attack")
	var target := ahead()
	if not has_key and (target == KEY_POS or position == KEY_POS):
		has_key = true
		log_message("청동 열쇠를 얻었습니다. 북쪽 철문에 맞을 것 같습니다.")
		return {"kind": "key"}
	if target == DOOR_POS and not door_open:
		if not has_key:
			log_message("차가운 철문. 동쪽 벽감에서 희미한 빛이 보입니다.")
			return {"kind": "inspect"}
		door_open = true
		log_message("오래된 경첩이 울며 문이 열립니다.")
		return {"kind": "door"}
	if target == ENEMY_POS and enemy_hp > 0:
		phase = "combat"
		log_message("경비병과 대치했습니다. 영웅과 행동을 선택하세요.")
		return {"kind": "engage"}
	if target == CHEST_POS and not chest_open:
		if enemy_hp > 0: return {}
		chest_open = true
		gold += 80
		potions += 1
		phase = "won"
		log_message("잿불의 봉인, 금화 80개, 회복 물약을 얻었습니다.")
		return {"kind": "treasure"}
	log_message("젖은 돌 냄새와 횃불 소리만 남아 있습니다.")
	return {"kind": "inspect"}

func act(action: String) -> Dictionary:
	if phase == "defeat" or hp[selected] <= 0: return {}
	if action != "potion" and phase != "combat": return {}
	if action == "skill" and mp[selected] < COST[selected]:
		log_message("마나가 부족합니다.")
		return {"kind": "inspect"}
	if action == "potion" and potions <= 0:
		log_message("회복 물약이 없습니다.")
		return {"kind": "inspect"}
	var event := {"kind": action, "actor": selected, "damage": 0, "heal": 0, "enemy_damage": 0, "target": -1, "killed": false}
	if action == "attack":
		event.damage = DAMAGE[selected]
	elif action == "skill":
		mp[selected] -= COST[selected]
		if selected == 3:
			for i in range(4):
				if hp[i] > 0: hp[i] = mini(hp[i] + 14, MAX_HP[i])
			event.heal = 14
			log_message("세라의 치유의 빛 · 살아 있는 동료들의 생명력 +14")
		else:
			event.damage = [21, 20, 28][selected]
	elif action == "potion":
		if hp[selected] == MAX_HP[selected]:
			log_message("이미 생명력이 가득합니다.")
			return {"kind": "inspect"}
		potions -= 1
		hp[selected] = mini(hp[selected] + 25, MAX_HP[selected])
		event.heal = 25
		log_message("%s · 회복 물약으로 생명력 +25" % NAMES[selected])
	elif action == "guard":
		mp[selected] = mini(mp[selected] + 3, MAX_MP[selected])
		log_message("%s · 방어 자세, 마나 +3" % NAMES[selected])
	else:
		return {}
	if event.damage > 0:
		enemy_hp = maxi(0, enemy_hp - int(event.damage))
		log_message("%s · %s · 경비병에게 %d 피해" % [NAMES[selected], SKILLS[selected] if action == "skill" else "공격", event.damage])
	if enemy_hp <= 0:
		phase = "explore"
		event.killed = true
		gold += 20
		log_message("경비병을 쓰러뜨렸습니다. 북쪽 제단으로 향하세요. +20 금화")
	elif phase == "combat":
		var target := selected if action == "guard" else posmod(turn, 4)
		while hp[target] <= 0: target = posmod(target + 1, 4)
		var incoming := 3 if action == "guard" else 9 + (turn % 3)
		hp[target] = maxi(0, hp[target] - incoming)
		event.enemy_damage = incoming
		event.target = target
		turn += 1
		log_message("경비병의 반격 · %s에게 %d 피해" % [NAMES[target], incoming])
		if hp.all(func(v): return v <= 0):
			phase = "defeat"
			log_message("마지막 횃불이 꺼졌습니다.")
		elif hp[selected] <= 0:
			while hp[selected] <= 0: selected = posmod(selected + 1, 4)
	return event

func _reveal() -> void:
	visited["%d,%d" % [position.x, position.y]] = true
	for direction in DIRECTIONS:
		var next: Vector2i = position + direction
		visited["%d,%d" % [next.x, next.y]] = true

func log_message(message: String) -> void:
	messages.append(message)
	if messages.size() > 32: messages.pop_front()

func snapshot() -> Dictionary:
	return {"version": SAVE_VERSION, "position": [position.x, position.y], "facing": facing, "selected": selected,
		"hp": hp, "mp": mp, "enemy_hp": enemy_hp, "has_key": has_key, "door_open": door_open,
		"chest_open": chest_open, "potions": potions, "gold": gold, "turn": turn, "phase": phase, "visited": visited}

func save_to(path: String) -> bool:
	var f := FileAccess.open(path + ".tmp", FileAccess.WRITE)
	if f == null: return false
	f.store_string(JSON.stringify(snapshot()))
	f.close()
	return DirAccess.rename_absolute(path + ".tmp", path) == OK

func load_from(path: String) -> bool:
	if not FileAccess.file_exists(path): return false
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not parsed is Dictionary or parsed.get("version", 0) != SAVE_VERSION: return false
	if not parsed.get("position") is Array or parsed.position.size() != 2: return false
	var p := Vector2i(int(parsed.position[0]), int(parsed.position[1]))
	if not is_floor(p): return false
	if not parsed.get("hp") is Array or parsed.hp.size() != 4: return false
	if not parsed.get("mp") is Array or parsed.mp.size() != 4: return false
	if not parsed.get("visited", {}) is Dictionary: return false
	if parsed.get("phase", "") not in ["explore", "combat", "won", "defeat"]: return false
	position = p
	facing = posmod(int(parsed.get("facing", 0)), 4)
	selected = clampi(int(parsed.get("selected", 0)), 0, 3)
	for i in range(4):
		hp[i] = clampi(int(parsed.hp[i]), 0, MAX_HP[i])
		mp[i] = clampi(int(parsed.mp[i]), 0, MAX_MP[i])
	enemy_hp = clampi(int(parsed.get("enemy_hp", 96)), 0, enemy_max_hp)
	has_key = bool(parsed.get("has_key", false))
	door_open = bool(parsed.get("door_open", false))
	chest_open = bool(parsed.get("chest_open", false))
	potions = clampi(int(parsed.get("potions", 2)), 0, 99)
	gold = clampi(int(parsed.get("gold", 0)), 0, 99999)
	turn = maxi(0, int(parsed.get("turn", 0)))
	phase = parsed.phase
	visited = parsed.visited
	_reveal()
	if hp.all(func(v): return v <= 0): phase = "defeat"
	elif hp[selected] <= 0:
		while hp[selected] <= 0: selected = posmod(selected + 1, 4)
	if enemy_hp == 0 and phase == "combat": phase = "explore"
	log_message("이전 탐험을 이어갑니다.")
	return true
