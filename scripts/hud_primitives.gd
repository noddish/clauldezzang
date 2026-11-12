extends Control

signal action_requested(action: String)
const Rules = preload("res://scripts/dungeon_state.gd")
const View = preload("res://scripts/dungeon_view.gd")
const FONT = preload("res://assets/interface.otf")
const TITLE = preload("res://assets/title.ttf")
const ICONS = preload("res://scripts/art_assets.gd")
const INK := Color("0b171d")
const PANEL := Color("14242b")
const LINE := Color("405052")
const GOLD := Color("d6bd8e")
const TEXT := Color("e8dfcd")
const MUTED := Color("a4ada6")
const GREEN := Color("82b5ac")
const ASH_RED := Color("cf6659")
const ASH_TEAL := Color("8bc5bc")
const ASH_WARM := Color("e4c999")
const ASH_SHADOW := Color("071014")

var state
var busy := false
var muted := false
var map_open := false
var help_open := false
var reset_open := false
var portrait := false
var compact := false
var scene_rect := Rect2()
var party_rect := Rect2()
var side_rect := Rect2()
var footer_rect := Rect2()
var buttons: Array[Dictionary] = []
var elapsed := 0.0
var effect := 0.0
var effect_color := Color(1, 0.4, 0.2)
var damage_text := ""
var effect_style := ""
var feedback := ""
var feedback_time := 0.0
var icons: Array[AtlasTexture] = []
var shown_hp: Array = []
var shown_messages: Array = []
var hp_trail: Array = []
var enemy_trail := 96.0
var damaged_hero := -1
var hero_damage := 0
var hero_damage_time := 0.0
var combat_presentation := false
var pressed_id := ""
var press_time := 0.0
var long_pressed := false
var hover_id := ""
var hover_time := 0.0
var hover_enabled := true
var mouse_hover_available := true
var tooltip_from_hover := false
var tooltip_id := ""
var tooltip_time := 0.0
var toast := ""
var toast_time := 0.0
var toast_icon := 7

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	for i in range(8):
		icons.append(ICONS.icon_region(i))
	sync_state()

func sync_state() -> void:
	shown_hp = state.hp.duplicate()
	shown_messages = state.messages.duplicate()
	hp_trail = state.hp.duplicate()
	enemy_trail = float(state.enemy_hp)
	damaged_hero = -1
	hero_damage_time = 0
	toast_time = 0
	tooltip_time = 0
	tooltip_id = ""
	tooltip_from_hover = false
	effect = 0
	damage_text = ""
	combat_presentation = false

func phase() -> String:
	return "combat" if busy and combat_presentation else state.phase

func begin_event(event: Dictionary, before: Array) -> void:
	combat_presentation = event.has("actor") and (event.get("enemy_damage", 0) > 0 or event.get("damage", 0) > 0)
	shown_hp = before.duplicate()
	shown_messages = state.messages.duplicate()
	if int(event.get("enemy_damage", 0)) > 0:
		if state.phase == "defeat": shown_messages.pop_back()
		shown_messages.pop_back()
	if event.get("heal", 0) > 0:
		for i in range(4):
			if before[i] > 0 and (event.kind == "skill" or i == event.actor):
				shown_hp[i] = mini(before[i] + int(event.heal), Rules.MAX_HP[i])
	tooltip_id = ""
	tooltip_time = 0

func counter_hit(target: int, damage: int) -> void:
	shown_hp = state.hp.duplicate()
	shown_messages = state.messages.duplicate()
	damaged_hero = target
	hero_damage = damage
	hero_damage_time = 1.2
	effect_style = ""
	flash(Color("b65b4a"))

func end_event() -> void:
	shown_hp = state.hp.duplicate()
	shown_messages = state.messages.duplicate()
	combat_presentation = false

func notify(message: String, icon: int = 7) -> void:
	toast = message
	toast_time = 2.8
	toast_icon = icon

func _ornate(rect: Rect2, color: Color = GOLD) -> void:
	for side in [Vector2(1, 1), Vector2(-1, 1), Vector2(1, -1), Vector2(-1, -1)]:
		var corner: Vector2 = rect.get_center() - side * rect.size / 2
		draw_line(corner + side * Vector2(1, 1), corner + side * Vector2(13, 1), color, 2)
		draw_line(corner + side * Vector2(1, 1), corner + side * Vector2(1, 13), color, 2)
		draw_rect(Rect2(corner + side * Vector2(5, 5) - Vector2(1, 1), Vector2(2, 2)), color)

func _icon(index: int, rect: Rect2, alpha: float = 1.0) -> void:
	if icons.is_empty(): return
	draw_texture_rect(icons[index], rect, false, Color(1, 1, 1, alpha))

func _text(value: String, at: Vector2, font_size: int = 16, color: Color = TEXT, width: float = -1) -> void:
	# Local text contrast follows the glyph, not a background card.
	draw_string(FONT, at + Vector2(1, 1), value, HORIZONTAL_ALIGNMENT_LEFT, width, font_size, Color(ASH_SHADOW, color.a * 0.95))
	draw_string(FONT, at, value, HORIZONTAL_ALIGNMENT_LEFT, width, font_size, color)

func _center(value: String, rect: Rect2, font_size: int = 16, color: Color = TEXT) -> void:
	var measured := FONT.get_string_size(value, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size)
	_text(value, Vector2(rect.position.x + (rect.size.x - measured.x) / 2, rect.get_center().y + font_size * 0.36), font_size, color)

func _wrapped(value: String, at: Vector2, width: float, font_size: int = 14, max_lines: int = 3, color: Color = MUTED) -> void:
	var line := ""
	var lines: Array[String] = []
	for character in value:
		if character == "\n":
			lines.append(line)
			line = ""
		elif FONT.get_string_size(line + character, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x > width:
			lines.append(line)
			line = character
		else: line += character
	if not line.is_empty(): lines.append(line)
	for i in range(mini(max_lines, lines.size())):
		_text(lines[i], at + Vector2(0, i * (font_size + 6)), font_size, color)

func _bar(rect: Rect2, value: float, maximum: float, color: Color, trail: float = -1) -> void:
	draw_rect(rect.grow(1), Color("090e11"))
	draw_rect(rect, Color("202626"))
	if trail > value:
		draw_rect(Rect2(rect.position, Vector2(rect.size.x * clampf(trail / maximum, 0, 1), rect.size.y)), Color("d1b68c"))
	var filled := Rect2(rect.position, Vector2(rect.size.x * clampf(value / maximum, 0, 1), rect.size.y))
	draw_rect(filled, color)
	if filled.size.x > 1: draw_line(filled.position, Vector2(filled.end.x, filled.position.y), color.lightened(0.26))

func _face(index: int, rect: Rect2, alpha: float) -> void:
	var texture := View.sprite_region(index, 0)
	var source := Vector2(texture.get_size())
	var aspect := rect.size.x / rect.size.y
	var cropped := Vector2(minf(source.x, source.y * aspect), minf(source.y, source.x / aspect))
	var region := Rect2(Vector2((source.x - cropped.x) / 2, 0), cropped)
	draw_texture_rect_region(texture, rect, region, Color(1, 1, 1, alpha))

## Ash Marks primitives use visible shape independently of their touch rectangle.
## The tiny deterministic stair steps are geometry, not noise or a pixel filter.
func _ash_stroke(from: Vector2, to: Vector2, color: Color = TEXT, width: float = 2.0, pixel: float = 2.0) -> void:
	var step := maxf(1.0, pixel)
	var length := maxf(absf(to.x - from.x), absf(to.y - from.y))
	var count := maxi(1, int(ceil(length / step)))
	var thickness := maxf(step, width)
	for i in range(count + 1):
		var point := from.lerp(to, float(i) / count).snapped(Vector2.ONE * step)
		draw_rect(Rect2(point - Vector2.ONE * thickness * 0.5, Vector2.ONE * thickness), color)

func _ash_path(points: Array, rect: Rect2, color: Color, width: float = 1.5, closed: bool = false) -> void:
	var scale_factor := minf(rect.size.x, rect.size.y) / 24.0
	var step := 1.0 if scale_factor < 1.25 else 2.0
	for i in range(points.size() - 1):
		_ash_stroke(rect.position + Vector2(points[i]) * rect.size / 24.0, rect.position + Vector2(points[i + 1]) * rect.size / 24.0, color, maxf(step, width * scale_factor), step)
	if closed and points.size() > 2:
		_ash_stroke(rect.position + Vector2(points.back()) * rect.size / 24.0, rect.position + Vector2(points.front()) * rect.size / 24.0, color, maxf(step, width * scale_factor), step)

func _ash_fill(points: Array, rect: Rect2, color: Color) -> void:
	var polygon := PackedVector2Array()
	for point in points: polygon.append((rect.position + Vector2(point) * rect.size / 24.0).round())
	draw_colored_polygon(polygon, color)

func _ash_underline(at: Vector2, width: float, color: Color = TEXT, alpha: float = 1.0) -> void:
	var ink := Color(color, color.a * alpha)
	_ash_stroke(at + Vector2(1, 2), at + Vector2(maxf(1, width - 2), 2), Color(ASH_SHADOW, alpha * 0.8), 3, 1)
	_ash_stroke(at + Vector2(3, 0), at + Vector2(width * 0.38, 0), ink, 2, 1)
	_ash_stroke(at + Vector2(width * 0.38, 1), at + Vector2(width * 0.86, 1), ink, 2, 1)
	_ash_stroke(at + Vector2(width * 0.86, 0), at + Vector2(width - 2, 0), Color(ink, ink.a * 0.65), 1, 1)
	draw_rect(Rect2(at - Vector2(1, 1), Vector2(2, 2)), ink)

func _ash_hp(rect: Rect2, value: float, maximum: float, trail: float = -1) -> void:
	# Continuous bottom-filled ink, with exact numbers rendered by the caller.
	var ratio := clampf(value / maxf(1, maximum), 0, 1)
	var trailing := clampf(maxf(value, trail) / maxf(1, maximum), 0, 1)
	var height := maxi(1, int(round(rect.size.y)))
	var bands: Array[Rect2] = []
	for band in range(0, height, 2):
		var t := float(band) / height
		var taper := 0.50 if t < 0.1 or t > 0.9 else (0.77 if t < 0.22 or t > 0.78 else 1.0)
		var w := maxf(2, floorf(rect.size.x * taper))
		var x := rect.get_center().x - w / 2 + (1 if band % 10 == 0 else 0)
		var r := Rect2(roundf(x), roundf(rect.position.y + band), w, minf(2, height - band))
		bands.append(r)
	# Draw every shadow first so later bands cannot stripe over earlier ink.
	for r in bands: draw_rect(r.grow(1), Color(ASH_SHADOW, 0.8))
	for i in range(bands.size()):
		var remaining := 1.0 - float(i * 2 + 1) / height
		var ink := Color("51332f")
		if remaining < trailing and trailing > ratio: ink = Color("cdb494")
		if remaining < ratio: ink = ASH_RED
		draw_rect(bands[i], ink)

func _ash_skill_kind(hero: int) -> String:
	return ["bash", "arrows", "frost", "heal"][clampi(hero, 0, 3)]

func _ash_glyph(kind: String, rect: Rect2, color: Color = TEXT, alpha: float = 1.0) -> void:
	# Two passes: a tiny local dark edge, then open ivory/teal/red ink. No enclosing button.
	var square := Rect2(rect.get_center() - Vector2.ONE * minf(rect.size.x, rect.size.y) * 0.5, Vector2.ONE * minf(rect.size.x, rect.size.y))
	_ash_glyph_ink(kind, Rect2(square.position + Vector2(1, 2), square.size), Color(ASH_SHADOW, alpha * 0.92))
	_ash_glyph_ink(kind, square, Color(color, color.a * alpha))

func _ash_glyph_ink(kind: String, r: Rect2, ink: Color) -> void:
	match kind:
		"attack", "sword":
			_ash_fill([Vector2(8, 16), Vector2(18, 4), Vector2(22, 2), Vector2(21, 7), Vector2(11, 18)], r, ink)
			_ash_path([Vector2(5, 13), Vector2(13, 20)], r, ink, 2)
			_ash_path([Vector2(8, 17), Vector2(4, 21)], r, ink, 3)
			_ash_fill([Vector2(2, 21), Vector2(4, 19), Vector2(6, 21), Vector2(4, 23)], r, ink)
		"shield", "guard", "bash":
			_ash_path([Vector2(4, 5), Vector2(12, 2), Vector2(20, 5), Vector2(19, 14), Vector2(16, 18), Vector2(12, 22), Vector2(8, 18), Vector2(5, 14)], r, ink, 1.6, true)
			_ash_path([Vector2(12, 6), Vector2(12, 17)], r, ink, 2)
			_ash_path([Vector2(8, 11), Vector2(16, 11)], r, ink, 2)
			if kind == "bash":
				_ash_path([Vector2(0, 10), Vector2(3, 12)], r, ink, 1)
				_ash_path([Vector2(21, 9), Vector2(24, 7)], r, ink, 1)
		"arrows":
			for offset in [Vector2(-3, 0), Vector2(3, 3)]:
				_ash_path([Vector2(5, 20) + offset, Vector2(18, 5) + offset], r, ink, 1.7)
				_ash_path([Vector2(12, 6) + offset, Vector2(18, 5) + offset, Vector2(18, 11) + offset], r, ink, 1.7)
				_ash_path([Vector2(4, 15) + offset, Vector2(7, 17) + offset, Vector2(10, 18) + offset], r, ink, 1)
		"frost", "mana", "skill":
			_ash_path([Vector2(12, 1), Vector2(12, 23)], r, ink, 1.4)
			_ash_path([Vector2(1, 12), Vector2(23, 12)], r, ink, 1.4)
			_ash_path([Vector2(7, 7), Vector2(17, 17)], r, ink, 1)
			_ash_path([Vector2(7, 17), Vector2(17, 7)], r, ink, 1)
			_ash_path([Vector2(12, 6), Vector2(18, 12), Vector2(12, 18), Vector2(6, 12)], r, ink, 1.4, true)
			_ash_path([Vector2(9, 3), Vector2(12, 6), Vector2(15, 3)], r, ink, 1)
			_ash_path([Vector2(9, 21), Vector2(12, 18), Vector2(15, 21)], r, ink, 1)
		"heal":
			_ash_fill([Vector2(10, 4), Vector2(14, 4), Vector2(14, 10), Vector2(20, 10), Vector2(20, 14), Vector2(14, 14), Vector2(14, 20), Vector2(10, 20), Vector2(10, 14), Vector2(4, 14), Vector2(4, 10), Vector2(10, 10)], r, ink)
			for corner in [Vector2(4, 4), Vector2(20, 4), Vector2(4, 20), Vector2(20, 20)]:
				_ash_path([corner - Vector2(1, 0), corner + Vector2(1, 0)], r, ink, 1)
		"tactics":
			_ash_fill([Vector2(2, 17), Vector2(8, 7), Vector2(12, 5), Vector2(7, 13)], r, ink)
			_ash_fill([Vector2(7, 21), Vector2(14, 8), Vector2(18, 5), Vector2(13, 15)], r, ink)
			_ash_fill([Vector2(14, 20), Vector2(20, 10), Vector2(23, 8), Vector2(19, 16)], r, ink)
		"map":
			_ash_path([Vector2(2, 5), Vector2(8, 3), Vector2(15, 6), Vector2(22, 3), Vector2(21, 19), Vector2(15, 21), Vector2(8, 18), Vector2(2, 21)], r, ink, 1.5, true)
			_ash_path([Vector2(8, 3), Vector2(8, 18)], r, ink, 1)
			_ash_path([Vector2(15, 6), Vector2(15, 21)], r, ink, 1)
		"menu":
			for x in [4, 12, 20]:
				_ash_fill([Vector2(x, 10), Vector2(x + 2, 12), Vector2(x, 14), Vector2(x - 2, 12)], r, ink)
		"movement", "forward", "expand":
			_ash_path([Vector2(3, 12), Vector2(12, 6), Vector2(21, 12)], r, ink, 1.8)
			if kind == "movement": _ash_path([Vector2(3, 20), Vector2(12, 14), Vector2(21, 20)], r, ink, 1.8)
		"back", "collapse":
			_ash_path([Vector2(3, 8), Vector2(12, 15), Vector2(21, 8)], r, ink, 1.8)
		"turn_left", "turn_right":
			var mirror := kind == "turn_right"
			var points: Array = [Vector2(18, 20), Vector2(18, 9), Vector2(5, 9), Vector2(10, 4), Vector2(5, 9), Vector2(10, 14)]
			if mirror:
				for i in range(points.size()): points[i].x = 24 - points[i].x
			_ash_path(points, r, ink, 1.7)
		"strafe_left", "strafe_right", "panel_back":
			var mirror := kind == "strafe_right"
			var points: Array = [Vector2(20, 12), Vector2(6, 12), Vector2(12, 6), Vector2(6, 12), Vector2(12, 18)]
			if mirror:
				for i in range(points.size()): points[i].x = 24 - points[i].x
			_ash_path(points, r, ink, 1.7)
			if kind != "panel_back": _ash_path([Vector2(22 if mirror else 2, 6), Vector2(22 if mirror else 2, 18)], r, ink, 1)
		"inspect", "interact":
			_ash_path([Vector2(9, 21), Vector2(5, 16), Vector2(3, 12), Vector2(4, 10), Vector2(6, 10), Vector2(9, 13), Vector2(9, 5), Vector2(10, 4), Vector2(12, 4), Vector2(12, 11), Vector2(12, 2), Vector2(14, 2), Vector2(14, 11), Vector2(15, 4), Vector2(17, 4), Vector2(17, 12), Vector2(18, 7), Vector2(20, 7), Vector2(20, 16), Vector2(18, 21)], r, ink, 1.2, true)
		"bag", "item", "potion":
			_ash_path([Vector2(7, 3), Vector2(17, 3), Vector2(15, 8), Vector2(19, 12), Vector2(20, 19), Vector2(17, 22), Vector2(7, 22), Vector2(4, 19), Vector2(5, 12), Vector2(9, 8)], r, ink, 1.6, true)
			_ash_path([Vector2(7, 8), Vector2(17, 8)], r, ink, 1.5)
		"party":
			_ash_path([Vector2(8, 3), Vector2(13, 3), Vector2(15, 7), Vector2(12, 11), Vector2(8, 11), Vector2(6, 7)], r, ink, 1.5, true)
			_ash_path([Vector2(2, 22), Vector2(4, 16), Vector2(8, 14), Vector2(13, 14), Vector2(17, 17), Vector2(18, 22)], r, ink, 1.7)
			_ash_path([Vector2(18, 5), Vector2(21, 8), Vector2(19, 12), Vector2(22, 16), Vector2(23, 21)], r, ink, 1)
		"journal":
			_ash_path([Vector2(3, 4), Vector2(10, 5), Vector2(12, 8), Vector2(15, 5), Vector2(22, 3), Vector2(21, 20), Vector2(15, 21), Vector2(12, 23), Vector2(9, 20), Vector2(3, 19)], r, ink, 1.4, true)
			_ash_path([Vector2(12, 8), Vector2(12, 20)], r, ink, 1)
		"settings":
			for i in range(3):
				var x := 5 + i * 7
				var y := 8 if i == 1 else 16
				_ash_path([Vector2(x, 3), Vector2(x, 21)], r, ink, 1)
				_ash_fill([Vector2(x - 2, y - 2), Vector2(x + 2, y - 2), Vector2(x + 2, y + 2), Vector2(x - 2, y + 2)], r, ink)
		"close":
			_ash_path([Vector2(6, 6), Vector2(18, 18)], r, ink, 1.7)
			_ash_path([Vector2(6, 18), Vector2(18, 6)], r, ink, 1.7)
		"help":
			_ash_path([Vector2(6, 7), Vector2(7, 4), Vector2(16, 4), Vector2(18, 7), Vector2(17, 10), Vector2(12, 13), Vector2(12, 16)], r, ink, 1.6)
			_ash_fill([Vector2(11, 20), Vector2(13, 20), Vector2(13, 22), Vector2(11, 22)], r, ink)
		"restart":
			_ash_path([Vector2(5, 9), Vector2(9, 4), Vector2(17, 4), Vector2(21, 8), Vector2(21, 17), Vector2(17, 21), Vector2(9, 21), Vector2(6, 18)], r, ink, 1.6)
			_ash_path([Vector2(5, 3), Vector2(5, 9), Vector2(11, 9)], r, ink, 1.6)
		_:
			_ash_path([Vector2(12, 3), Vector2(20, 12), Vector2(12, 21), Vector2(4, 12)], r, ink, 1.5, true)

func action_description(id: String) -> Dictionary:
	match id:
		"attack": return {"title": "기본 공격", "body": "선택한 영웅이 %d 피해를 줍니다. 마나를 소모하지 않습니다." % Rules.DAMAGE[state.selected]}
		"skill":
			var descriptions := ["방패를 내리쳐 21 피해를 줍니다.", "화살이 적의 갑옷을 관통해 20 피해를 줍니다.", "날카로운 서리 창으로 28 피해를 줍니다.", "살아 있는 모든 동료의 HP를 14 회복합니다."]
			var body: String = descriptions[state.selected] + " 마나 %d 소모." % Rules.COST[state.selected]
			if state.mp[state.selected] < Rules.COST[state.selected]: body += " 현재 마나가 부족합니다."
			return {"title": Rules.SKILLS[state.selected], "body": body}
		"guard": return {"title": "방어 자세", "body": "선택한 영웅이 다음 반격을 받아 피해를 3으로 줄입니다. 마나를 3 회복합니다."}
		"potion": return {"title": "회복 물약 · %d개 보유" % state.potions, "body": "선택한 영웅의 HP를 25 회복합니다. HP가 가득하면 소모하지 않습니다."}
	return {}

func _draw_combat_effect() -> void:
	var center := scene_rect.get_center()
	var scale_factor := minf(scene_rect.size.x, scene_rect.size.y) / 400.0
	var alpha := clampf(effect * 1.4, 0, 1)
	if effect_style in ["frost", "arrows"]:
		var start := Vector2(scene_rect.position.x + scene_rect.size.x * 0.2, scene_rect.end.y - 48)
		var end := center - Vector2(-12, 25) * scale_factor
		var flight := clampf((1.0 - effect) * 6.0, 0, 1)
		var head := start.lerp(end, flight)
		var color := Color("b8eafb") if effect_style == "frost" else Color("e0c792")
		if flight < 1:
			var tail := start.lerp(head, 0.35)
			draw_line(tail, head, Color(color, alpha * 0.24), 12 * scale_factor)
			draw_line(tail, head, Color(color, alpha), 3 * scale_factor)
			_icon(3 if effect_style == "frost" else 2, Rect2(head - Vector2.ONE * 26 * scale_factor, Vector2.ONE * 52 * scale_factor), alpha)
		else:
			for i in range(11):
				var direction := Vector2.from_angle(i * TAU / 11 + 0.3)
				var point := end + direction * (12 + (1.0 - effect) * 100) * scale_factor
				var shard := PackedVector2Array([point + direction * 9 * scale_factor, point + direction.orthogonal() * 3 * scale_factor, point - direction * 7 * scale_factor, point - direction.orthogonal() * 3 * scale_factor])
				draw_colored_polygon(shard, Color(color, alpha))
			draw_arc(end, (18 + (1 - effect) * 70) * scale_factor, 0, TAU, 20, Color(color, alpha * 0.32), 2)
	elif effect_style in ["bash", "guard"]:
		var radius := (55 + (1 - effect) * 30) * scale_factor
		var color := Color("d9ba7c") if effect_style == "bash" else Color("97cad8")
		draw_arc(center, radius, 0, TAU, 24, Color(color, alpha * 0.55), 3 * scale_factor)
		_icon(1 if effect_style == "bash" else 5, Rect2(center - Vector2.ONE * 38 * scale_factor, Vector2.ONE * 76 * scale_factor), alpha)
		for i in range(8):
			var direction := Vector2.from_angle(i * TAU / 8)
			draw_line(center + direction * radius, center + direction * (radius + 12 * scale_factor), Color(color, alpha), 2)

	elif effect_style == "slash":
		var points := PackedVector2Array()
		for i in range(14):
			var t := float(i) / 13
			points.append(center + Vector2(-90 + t * 180, -90 + t * 135 + sin(t * PI) * 24) * scale_factor)
		draw_polyline(points, Color(0.9, 0.68, 0.3, alpha * 0.25), 16 * scale_factor)
		draw_polyline(points, Color(1, 0.91, 0.65, alpha), 4 * scale_factor)
	elif effect_style == "heal":
		for i in range(7):
			var point := center + Vector2(sin(i * 2.0) * 90, cos(i * 3.0) * 80 - (1 - effect) * 45) * scale_factor
			draw_line(point - Vector2(5, 0), point + Vector2(5, 0), Color(0.6, 1, 0.76, alpha), 2)
			draw_line(point - Vector2(0, 5), point + Vector2(0, 5), Color(0.6, 1, 0.76, alpha), 2)

func flash(color: Color, text: String = "") -> void:
	effect = 1.0
	effect_color = color
	damage_text = text

func _process(delta: float) -> void:
	elapsed += delta
	effect = maxf(0, effect - delta * 1.35)
	hero_damage_time = maxf(0, hero_damage_time - delta)
	toast_time = maxf(0, toast_time - delta)
	for i in range(hp_trail.size()): hp_trail[i] = move_toward(float(hp_trail[i]), float(shown_hp[i]), delta * 18)
	if state != null: enemy_trail = move_toward(enemy_trail, float(state.enemy_hp), delta * 35)
	var allow_mouse_hover := hover_enabled and mouse_hover_available
	var hover := ""
	if allow_mouse_hover:
		for button in buttons:
			if button.rect.has_point(get_local_mouse_position()):
				hover = button.id
				break
	if not allow_mouse_hover:
		hover_id = ""
		hover_time = 0
		if tooltip_from_hover:
			tooltip_id = ""
			tooltip_time = 0
			tooltip_from_hover = false
	elif hover != hover_id:
		hover_id = hover
		hover_time = 0
	else: hover_time += delta
	if not pressed_id.is_empty():
		press_time += delta
		if press_time > 0.45 and not action_description(pressed_id).is_empty():
			long_pressed = true
			tooltip_id = pressed_id
			tooltip_time = 2.5
			tooltip_from_hover = false
	elif allow_mouse_hover and hover_time > 0.5 and not action_description(hover_id).is_empty():
		tooltip_id = hover_id
		tooltip_time = 0.1
		tooltip_from_hover = true
	else:
		tooltip_time = maxf(0, tooltip_time - delta)
		if tooltip_time == 0:
			tooltip_id = ""
			tooltip_from_hover = false
	queue_redraw()
