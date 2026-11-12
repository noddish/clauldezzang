extends RefCounted
## Ash Marks surfaces share navigation and input geometry, not a universal card skin.
const Rules = preload("res://scripts/dungeon_state.gd")
const View = preload("res://scripts/dungeon_view.gd")
const IVORY := Color("e8e2d2")
const MUTED := Color("a5afa9")
const ASH := Color("89958f")
const RED := Color("be6858")
const TEAL := Color("91c8c1")
const WARM := Color("d3b58b")

static func draw(h) -> void:
	h.map_canvas.visible = h.panel == "map" and h.panel_progress > 0
	if h.panel.is_empty(): return
	h.buttons.clear()
	# One scene scrim is modal focus. The actual content is mostly unframed.
	var shade := 0.79 if h.panel in ["menu", "party", "enemy"] else 0.72
	h.draw_rect(Rect2(Vector2.ZERO, h.size), Color(0.006, 0.012, 0.016, shade * h.panel_progress))
	h.panel_rect = h._target_panel_rect()
	var travel := Vector2(0, h.panel_rect.size.y + 20) if h.portrait else Vector2(h.panel_rect.size.x + 20, 0)
	h.panel_rect.position += travel * (1 - h.panel_progress)
	var r: Rect2 = h.panel_rect
	if h.panel in ["settings", "help", "reset"]:
		# Reading controls intentionally get a quiet, matte support surface.
		_wash(h, r, 0.70)
	elif h.panel in ["journal", "item"]:
		_wash(h, Rect2(r.position + Vector2(4, 64), r.size - Vector2(8, 68)), 0.37)
	elif h.panel == "bag":
		# Irregular ground below loose inventory objects; no slot cards.
		_wash(h, Rect2(r.position + Vector2(8, 94), Vector2(r.size.x - 16, minf(190, r.size.y - 108))), 0.28)
	if h.portrait:
		h._ash_stroke(Vector2(r.get_center().x - 17, r.position.y + 10), Vector2(r.get_center().x + 16, r.position.y + 10), Color(IVORY, 0.6), 2)
	else:
		# A visible handle invites an inward/outward drag without enclosing the view.
		h._ash_stroke(r.position + Vector2(3, 26), r.position + Vector2(3, 48), Color(IVORY, 0.5), 2)
	var titles := {"menu": "원정의 흔적", "map": "탐험 지도", "party": "원정대", "bag": "소지품", "item": "아이템", "journal": "목표와 기록", "settings": "설정", "help": "터치와 조작", "reset": "새 탐험", "tactics": "다음 행동", "enemy": "묘지의 경비병"}
	var title_x: float = r.position.x + (58 if not h.panel_history.is_empty() else 18)
	h._text(titles.get(h.panel, ""), Vector2(title_x, r.position.y + 44), 19, IVORY)
	h._ash_underline(Vector2(title_x, r.position.y + 55), 32, RED, 0.85)
	if not h.panel_history.is_empty(): _glyph_button(h, "panel_back", "panel_back", "", Rect2(r.position + Vector2(6, 18), Vector2.ONE * 48), IVORY)
	_glyph_button(h, "close", "close", "", Rect2(r.end.x - 58, r.position.y + 18, 48, 48), IVORY)
	h.body_rect = Rect2(r.position + Vector2(18, 78), Vector2(r.size.x - 36, r.size.y - 94))
	match h.panel:
		"menu": _menu(h)
		"settings": _settings(h)
		"map": _map(h)
		"party": _party(h)
		"bag": _bag(h)
		"item": _item(h)
		"tactics": _tactics(h)
		"journal": _journal(h)
		"enemy": _enemy(h)
		"help": _help(h)
		"reset": _reset(h)
	if h.gesture == "item_drag":
		h._icon(6, Rect2(h.drag_position - Vector2(22, 50), Vector2(44, 44)), 0.95)
		h._center("손을 떼어 사용" if h.drag_target >= 0 else "회복할 동료에게 끌어 놓으세요", Rect2(r.position.x + 12, r.end.y - 24, r.size.x - 24, 18), 11, TEAL)

static func _wash(h, r: Rect2, opacity: float) -> void:
	# A few hard, irregular edges keep this closer to a shadow than an app card.
	var points := PackedVector2Array([
		r.position + Vector2(0, 7), r.position + Vector2(r.size.x * 0.31, 3),
		r.position + Vector2(r.size.x * 0.72, 0), Vector2(r.end.x - 3, r.position.y + 9),
		r.end - Vector2(0, 6), r.position + Vector2(r.size.x * 0.55, r.size.y),
		Vector2(r.position.x + 4, r.end.y - 4)])
	h.draw_colored_polygon(points, Color(0.025, 0.044, 0.052, opacity))

static func _glyph_button(h, id: String, kind: String, label: String, r: Rect2, color: Color = IVORY, enabled: bool = true) -> void:
	var alpha := 1.0 if enabled else 0.36
	var offset := Vector2(0, 1) if h.pressed_id == id else Vector2.ZERO
	var icon_size := 28.0 if label.is_empty() else 30.0
	var icon_y := r.get_center().y - icon_size * 0.5 if label.is_empty() else r.position.y + 3
	h._ash_glyph(kind, Rect2(r.get_center().x - icon_size * 0.5, icon_y, icon_size, icon_size), color, alpha)
	if not label.is_empty(): h._center(label, Rect2(r.position + Vector2(0, 34) + offset, Vector2(r.size.x, 20)), 12, Color(color, alpha))
	if h.pressed_id == id: h._ash_underline(Vector2(r.get_center().x - 11, r.end.y - 2), 22, color, alpha)
	h.buttons.append({"id": id, "rect": r, "enabled": enabled})

static func _menu(h) -> void:
	var r: Rect2 = h.body_rect
	# Portrait + equipment establish the main destinations; other entries read as notes.
	var hero: int = h.state.selected
	var primary_w := (r.size.x - 20) * 0.5
	var first := Rect2(r.position, Vector2(primary_w, 94))
	var second := Rect2(r.position + Vector2(primary_w + 20, 0), Vector2(primary_w, 94))
	h._face(hero, Rect2(first.get_center().x - 26, first.position.y, 52, 56), 1.0)
	h._center("원정대", Rect2(first.position + Vector2(0, 63), Vector2(first.size.x, 24)), 14, IVORY)
	h._ash_glyph("bag", Rect2(second.get_center().x - 21, second.position.y + 10, 42, 42), IVORY)
	h._center("가방", Rect2(second.position + Vector2(0, 63), Vector2(second.size.x, 24)), 14, IVORY)
	h.buttons.append({"id": "party", "rect": first, "enabled": true})
	h.buttons.append({"id": "bag", "rect": second, "enabled": true})
	var w := (r.size.x - 18) / 2
	var ids := ["map", "journal", "settings", "help"]
	var labels := ["지도", "목표 · 기록", "설정", "조작 안내"]
	for i in range(4):
		var at := r.position + Vector2((i % 2) * (w + 18), 110 + (i / 2) * 58)
		var target := Rect2(at, Vector2(w, 50))
		h._ash_glyph(["map", "journal", "settings", "inspect"][i], Rect2(at + Vector2(3, 10), Vector2(24, 24)), MUTED)
		h._text(labels[i], at + Vector2(38, 29), 13, IVORY)
		h.buttons.append({"id": ids[i], "rect": target, "enabled": true})
	if r.size.y > 265: h._text("행동 후 자동 저장", Vector2(r.position.x + 3, r.end.y - 8), 10, MUTED)

static func _settings(h) -> void:
	var r: Rect2 = h.body_rect
	var ids := ["sound", "motion", "haptics", "pin_movement", "layout", "restart"]
	var labels := ["소리", "모션 줄이기", "진동", "이동 버튼 고정", "가로 · 세로 전환", "새 탐험…"]
	var values := [not h.muted, h.reduced_motion, h.haptics, h.movement_pinned]
	var vertical: bool = r.size.y >= 320
	var w: float = r.size.x if vertical else (r.size.x - 22) * 0.5
	for i in range(6):
		var at := r.position + (Vector2(0, i * 51) if vertical else Vector2((i % 2) * (w + 22), (i / 2) * 69))
		var target := Rect2(at, Vector2(w, 48))
		h._text(labels[i], at + Vector2(1, 25), 13 if vertical else 12, RED if i == 5 else IVORY)
		if i < 4:
			var end := at + Vector2(w - 4, 25)
			h._text("켬" if values[i] else "끔", end - Vector2(22, 0), 11, TEAL if values[i] else MUTED)
			h._ash_stroke(end + Vector2(-22, 7), end + Vector2(0 if values[i] else -14, 7), TEAL if values[i] else MUTED, 2)
		elif i == 4:
			h._ash_glyph("turn_right", Rect2(at + Vector2(w - 26, 7), Vector2(22, 22)), MUTED)
		h.buttons.append({"id": ids[i], "rect": target, "enabled": true})
	if r.size.y > 330: h._text("화면 방향은 기기 회전으로 바뀝니다.", Vector2(r.position.x, r.end.y - 8), 10, MUTED)

static func _map(h) -> void:
	var r: Rect2 = h.body_rect
	h.map_rect = Rect2(r.position, Vector2(r.size.x, maxf(120, r.size.y - 78)))
	h._clamp_map_pan()
	h.map_canvas.position = h.map_rect.position
	h.map_canvas.size = h.map_rect.size
	h.map_canvas.state = h.state
	h.map_canvas.zoom = h.map_zoom
	h.map_canvas.pan = h.map_pan
	h.map_canvas.queue_redraw()
	var y := r.end.y - 48
	h._button("map_minus", "−", Rect2(r.position.x, y, 48, 48), true, false, 24)
	h._button("map_reset", "위치 맞춤", Rect2(r.position.x + 56, y, r.size.x - 112, 48), true, false, 12)
	h._button("map_plus", "+", Rect2(r.end.x - 48, y, 48, 48), true, false, 24)
	h._center("끌어서 이동 · 핀치 확대 · 두 번 탭해 초기화", Rect2(r.position.x, y - 25, r.size.x, 20), 10, MUTED)

static func _party(h) -> void:
	var r: Rect2 = h.body_rect
	var w := (r.size.x - 18) / 4
	for i in range(4):
		h._hero_chip(i, Rect2(r.position + Vector2(i * (w + 6), 0), Vector2(w, 64)), "hero_%d" % i, h.state.selected == i, not h.busy and h.state.hp[i] > 0)
	var i: int = h.state.selected
	var y := r.position.y + 90
	h._face(i, Rect2(r.position.x, y - 12, 96, 112), 1.0)
	h._text("%s · %s" % [Rules.NAMES[i], Rules.ROLES[i]], Vector2(r.position.x + 110, y + 6), 15, IVORY)
	h._ash_underline(Vector2(r.position.x + 110, y + 15), 24, WARM, 0.85)
	h._text("HP %d/%d   MP %d/%d" % [h.shown_hp[i], Rules.MAX_HP[i], h.state.mp[i], Rules.MAX_MP[i]], Vector2(r.position.x + 110, y + 40), 12, IVORY)
	h._wrapped(h.action_description("skill").body, Vector2(r.position.x + 110, y + 65), r.size.x - 112, 12, 3, MUTED)
	h._button("party_done", "%s 선택 완료" % Rules.NAMES[i], Rect2(r.position.x, r.end.y - 52, r.size.x, 52), not h.busy, true, 14)
	if r.size.y > 300: h._text("좌우로 밀어 전환 · 두 번 탭해 완료", Vector2(r.position.x + 2, r.end.y - 68), 10, MUTED)

static func _bag(h) -> void:
	var r: Rect2 = h.body_rect
	h._text("금화 %d" % h.state.gold, r.position + Vector2(2, 18), 13, WARM)
	var names: Array[String] = ["potion"]
	if h.state.has_key: names.append("key")
	if h.state.chest_open: names.append("seal")
	var w := (r.size.x - 16) / 3
	for i in range(names.size()):
		var name: String = names[i]
		var item := Rect2(r.position + Vector2(i * (w + 8), 36), Vector2(w, 100))
		var image_r := Rect2(item.get_center().x - 25, item.position.y + 6, 50, 50)
		if name == "potion": h._icon(6, image_r)
		elif name == "key": h.draw_texture_rect(View.sprite_region(3, 3), image_r, false)
		else: h.draw_texture_rect(View.prop_region(6), image_r, false)
		# Only a small ash mark grounds each object, rather than enclosing it in a slot.
		h._ash_underline(Vector2(item.get_center().x - 13, item.position.y + 63), 26, ASH, 0.55)
		h._center(("물약 ×%d" % h.state.potions) if name == "potion" else ("청동 열쇠" if name == "key" else "잿불의 봉인"), Rect2(item.position + Vector2(0, 70), Vector2(w, 24)), 11, IVORY)
		h.buttons.append({"id": "item_" + name, "rect": item, "enabled": true})
	h._wrapped("물건을 탭하거나 길게 눌러 설명과 사용 대상을 확인하세요.", r.position + Vector2(2, 167), r.size.x - 4, 12, 3, MUTED)
	if h.portrait: h._button("expand_sheet", "가방 축소 ↓" if h.panel_expansion > 0.5 else "가방 펼치기 ↑", Rect2(r.position.x, r.end.y - 52, r.size.x, 52), true, false, 13)

static func _item(h) -> void:
	var r: Rect2 = h.body_rect
	if h.selected_item != "potion":
		var is_key: bool = h.selected_item == "key"
		var texture = View.sprite_region(3, 3) if is_key else View.prop_region(6)
		h.draw_texture_rect(texture, Rect2(r.position, Vector2(56, 56)), false)
		h._text("청동 열쇠" if is_key else "잿불의 봉인", r.position + Vector2(72, 30), 19, IVORY)
		h._wrapped("북쪽 철문 앞에서 조사하면 열쇠를 사용할 수 있습니다." if is_key else "제단에서 회수한 봉인입니다. 첫 원정을 완료했습니다.", r.position + Vector2(0, 93), r.size.x, 14, 4, MUTED)
		h._button("map", "지도에서 경로 확인", Rect2(r.position.x, r.end.y - 52, r.size.x, 52), true, true, 14)
		return
	h.item_drag_rect = Rect2(r.position, Vector2(64, 64))
	h._icon(6, h.item_drag_rect.grow(-5))
	h._text("회복 물약 ×%d" % h.state.potions, r.position + Vector2(78, 23), 16, IVORY)
	h._text("한 명의 HP +25", r.position + Vector2(78, 46), 13, TEAL)
	var target_y := maxf(r.position.y + 98, r.end.y - 136)
	var w := (r.size.x - 18) / 4
	h._text("회복할 동료 선택", Vector2(r.position.x, target_y - 12), 12, MUTED)
	for i in range(4):
		var target := Rect2(r.position.x + i * (w + 6), target_y, w, 64)
		h._hero_chip(i, target, "target_%d" % i, h.item_target == i or h.drag_target == i, h.state.hp[i] > 0)
		if h.gesture == "item_drag" and h.drag_target == i:
			h._ash_underline(Vector2(target.position.x + 4, target.end.y - 1), target.size.x - 8, TEAL)
	var index: int = h.item_target
	var can_use: bool = not h.busy and h.state.potions > 0 and h.state.hp[index] > 0 and h.state.hp[index] < Rules.MAX_HP[index] and h.state.phase != "defeat"
	var label := "%s에게 사용" % Rules.NAMES[index] if can_use else ("물약이 없습니다" if h.state.potions <= 0 else "회복이 필요하지 않습니다")
	h._button("use_potion_%d" % index, label, Rect2(r.position.x, r.end.y - 52, r.size.x, 52), can_use, true, 14)
	if r.size.y > 280:
		h._wrapped("아이콘을 잠시 누른 뒤 동료에게 끌어 놓아도 사용할 수 있습니다." + (" 전투 중에는 사용 후 적이 반격합니다." if h.phase() == "combat" else ""), r.position + Vector2(0, 87), r.size.x, 11, 2, MUTED)

static func _tactics(h) -> void:
	var r: Rect2 = h.body_rect
	var w := (r.size.x - 26) * 0.5
	# Two free symbols rather than a second row of full-width action cards.
	_glyph_button(h, "guard", "guard", "방어", Rect2(r.position + Vector2(0, 10), Vector2(w, 76)), IVORY, not h.busy and h.state.phase == "combat")
	_glyph_button(h, "bag", "bag", "아이템", Rect2(r.position + Vector2(w + 26, 10), Vector2(w, 76)), IVORY)
	h._wrapped("반격 피해 3\nMP +3", r.position + Vector2(2, 108), w - 4, 12, 3, TEAL)
	h._wrapped("회복 물약 ×%d\n대상을 골라 사용" % h.state.potions, r.position + Vector2(w + 28, 108), w - 4, 12, 3, MUTED)
	h._wrapped("방어하면 현재 영웅이 다음 반격을 대신 받습니다.", r.position + Vector2(2, 192), r.size.x - 4, 11, 2, MUTED)

static func _journal(h) -> void:
	var r: Rect2 = h.body_rect
	h._text("꺼진 봉인", r.position + Vector2(0, 20), 16, IVORY)
	h._wrapped(h.state.objective(), r.position + Vector2(0, 47), r.size.x, 12, 2, IVORY)
	h._text("남겨진 기록 · 위아래로 밀기", r.position + Vector2(0, 97), 11, MUTED)
	h.log_rect = Rect2(r.position + Vector2(0, 112), Vector2(r.size.x, r.size.y - 112))
	var max_scroll := maxf(0, h.shown_messages.size() * 58 - h.log_rect.size.y)
	h.journal_scroll = clampf(h.journal_scroll, 0, max_scroll)
	for i in range(h.shown_messages.size()):
		var y: float = h.log_rect.position.y + i * 58 - h.journal_scroll
		if y < h.log_rect.position.y or y + 52 > h.log_rect.end.y: continue
		h._ash_stroke(Vector2(h.log_rect.position.x, y + 10), Vector2(h.log_rect.position.x + 4, y + 10), RED if i == 0 else ASH, 2)
		h._wrapped(h.shown_messages[h.shown_messages.size() - 1 - i], Vector2(h.log_rect.position.x + 14, y + 17), h.log_rect.size.x - 22, 11, 2, IVORY if i == 0 else MUTED)

static func _enemy(h) -> void:
	var r: Rect2 = h.body_rect
	var picture := Rect2(r.position, Vector2(116, minf(150, r.size.y - 60)))
	h.draw_texture_rect(View.sprite_region(0, 1), picture, false)
	h._ash_hp(Rect2(r.position + Vector2(124, 5), Vector2(4, 35)), h.state.enemy_hp, h.state.enemy_max_hp, h.enemy_trail)
	h._text("HP %d/%d" % [h.state.enemy_hp, h.state.enemy_max_hp], r.position + Vector2(140, 27), 14, IVORY)
	h._wrapped("청동 갑옷을 두른 묘지의 경비병. 행동 후 9~11 피해로 반격합니다. 방어하면 피해는 3입니다.", r.position + Vector2(140, 57), r.size.x - 140, 12, 5, MUTED)
	h._button("close", "전투로 돌아가기" if h.phase() == "combat" else "탐험으로 돌아가기", Rect2(r.position.x, r.end.y - 52, r.size.x, 52), true, true, 14)

static func _help(h) -> void:
	var r: Rect2 = h.body_rect
	var rows := ["탐험: 위/아래 스와이프 → 전진/후진", "탐험: 좌/우 스와이프 → 좌/우 회전", "대상 탭: 조사 · 적 길게 누르기: 정보", "파티 영역 좌우 밀기: 영웅 전환", "지도: 끌기 · 핀치 확대 · 두 번 탭 초기화", "패널: 손잡이로 닫기 · × 또는 뒤로가기", "이동·지도·메뉴 버튼으로도 조작 가능", "PC: W/S 이동 · A/D 회전 · Q/E 옆걸음"]
	var spacing := minf(31, (r.size.y - 10) / rows.size())
	for i in range(rows.size()): h._text(rows[i], r.position + Vector2(0, 17 + i * spacing), 10 if r.size.x < 350 else 11, IVORY)

static func _reset(h) -> void:
	var r: Rect2 = h.body_rect
	h._wrapped("현재 진행을 초기화하고 입구에서 새 탐험을 시작합니다.", r.position + Vector2(0, 26), r.size.x, 16, 4, IVORY)
	h._button("confirm_restart", "진행을 초기화하고 시작", Rect2(r.position.x, r.end.y - 116, r.size.x, 52), not h.busy, true, 13)
	h._button("close", "계속 탐험하기", Rect2(r.position.x, r.end.y - 52, r.size.x, 52), true, false, 14)
