extends "res://scripts/hud_primitives.gd"
## Immersive, context-driven UI. Game rules remain in DungeonState.
signal layout_changed
const MapCanvas = preload("res://scripts/map_canvas.gd")
const AshSurfaces = preload("res://scripts/ash_surfaces.gd")
const TOUCH := 48.0
const GAP := 8.0
var safe_insets := Vector4.ZERO
var usable := Rect2()
var dock := Rect2()
var panel := ""
var panel_history: Array[String] = []
var panel_progress := 0.0
var panel_expansion := 0.0
var panel_tween: Tween
var expansion_tween: Tween
var panel_closing := false
var reduced_motion := false
var haptics := true
var movement_open := false
var movement_pinned := false
var movement_timeout := 0.0
var last_phase := ""
var context_fade := 1.0
var gesture_hint_time := 7.0
var panel_rect := Rect2()
var body_rect := Rect2()
var map_rect := Rect2()
var log_rect := Rect2()
var map_canvas: Control
var map_zoom := 1.0
var map_pan := Vector2.ZERO
var journal_scroll := 0.0
var selected_item := "potion"
var item_drag_rect := Rect2()
var item_target := 0
var enemy_rect := Rect2()
var target_selected := false
var combat_center := Vector2.ZERO
var enemy_head := Vector2.ZERO
var enemy_feet := Vector2.ZERO
var world_target_visible := true
var active_pointer := -99
var pointers: Dictionary = {}
var pointer_start := Vector2.ZERO
var pointer_last := Vector2.ZERO
var pointer_age := 0.0
var pointer_max_distance := 0.0
var gesture := ""
var gesture_consumed := false
var drag_position := Vector2.ZERO
var drag_target := -1
var recent_touch := 0.0
var pinch_distance := 0.0
var pinch_zoom := 1.0
var pinch_anchor := Vector2.ZERO
var last_tap_id := ""
var last_tap_time := -10.0
var drag_start_pan := Vector2.ZERO
var drag_start_scroll := 0.0
var panel_was_expanded := false
var preferences_enabled := true

func _ready() -> void:
	super._ready()
	if preferences_enabled:
		var prefs := ConfigFile.new()
		if prefs.load("user://mobile-ui.cfg") == OK:
			reduced_motion = bool(prefs.get_value("ui", "reduced_motion", false))
			haptics = bool(prefs.get_value("ui", "haptics", true))
			movement_pinned = bool(prefs.get_value("ui", "movement_pinned", false))
			muted = bool(prefs.get_value("ui", "muted", false))
	movement_open = movement_pinned
	map_canvas = MapCanvas.new()
	map_canvas.visible = false
	add_child(map_canvas)
	last_phase = phase()
	item_target = state.selected
	layout()

func layout() -> void:
	usable = Rect2(safe_insets.x, safe_insets.y, size.x - safe_insets.x - safe_insets.z, size.y - safe_insets.y - safe_insets.w)
	portrait = size.x < size.y * 0.95 or usable.size.x < 600
	compact = not portrait and size.y < 550
	# The world continues under every HUD element. No reserved footer or sidebar.
	scene_rect = Rect2(Vector2.ZERO, size)
	var fighting := phase() == "combat"
	var reserve := (180.0 if portrait else 96.0) if fighting else 92.0
	dock = Rect2(usable.position.x + 12, usable.end.y - reserve, usable.size.x - 24, reserve - 8)
	if fighting:
		party_rect = Rect2(dock.position, Vector2(dock.size.x if portrait else 320, 84))
		var action_width := 264.0 if portrait else 216.0
		footer_rect = Rect2(usable.get_center().x - action_width / 2 if portrait else usable.end.x - action_width - 12, usable.end.y - 80, action_width, 72)
	else:
		party_rect = Rect2(dock.position, Vector2(132 if portrait else 232, 84))
		footer_rect = Rect2(usable.end.x - 92, usable.end.y - 80, 80, 72)
	side_rect = Rect2()

func _button(id: String, label: String, rect: Rect2, enabled: bool = true, accent: bool = false, font_size: int = 14) -> void:
	var active := enabled and (pressed_id == id or (hover_enabled and mouse_hover_available and recent_touch <= 0 and rect.has_point(get_local_mouse_position())))
	var color := (ASH_WARM if accent or active else TEXT) if enabled else MUTED.darkened(0.25)
	if id in ["close", "panel_back"]:
		_ash_glyph(id, Rect2(rect.get_center() - Vector2.ONE * 13, Vector2.ONE * 26), color)
	else:
		_center(label, rect, font_size, color)
	if active or accent:
		_ash_underline(Vector2(rect.get_center().x - 15, rect.end.y - 8), 30, color, 0.8)
	buttons.append({"id": id, "rect": rect, "enabled": enabled})

func _action_button(id: String, label: String, detail: String, icon: int, rect: Rect2, enabled: bool, accent: bool = false) -> void:
	var kind := _ash_skill_kind(state.selected) if id == "skill" else id
	var color := ASH_TEAL if id == "skill" else (ASH_RED if id == "tactics" else TEXT)
	var alpha := 1.0 if enabled else 0.35
	var pressed := pressed_id == id and enabled
	var nudge := Vector2(0, 2 if pressed else 0)
	if rect.size.x > 150:
		_ash_glyph(kind, Rect2(rect.position + Vector2(6, 9) + nudge, Vector2.ONE * 40), color, alpha)
		_text(label, rect.position + Vector2(62, 28) + nudge, 15, Color(TEXT, alpha))
		_text(detail, rect.position + Vector2(62, 50), 11, Color(MUTED, alpha))
	else:
		var icon_size := 42.0 if id == "attack" else 32.0
		_ash_glyph(kind, Rect2(rect.get_center().x - icon_size / 2, rect.position.y + 1, icon_size, icon_size), color, alpha)
		_center(label, Rect2(rect.position + Vector2(0, 42) + nudge, Vector2(rect.size.x, 18)), 13, Color(TEXT, alpha))
		if not detail.is_empty(): _center(detail, Rect2(rect.position + Vector2(0, 59), Vector2(rect.size.x, 13)), 10, Color(MUTED, alpha))
	if pressed: _ash_underline(Vector2(rect.get_center().x - 12, rect.end.y - 3), 24, color)
	buttons.append({"id": id, "rect": rect, "enabled": enabled})

func _utility(id: String, label: String, rect: Rect2, _icon_index: int = -1) -> void:
	_ash_glyph(id, Rect2(rect.get_center().x - 13, rect.position.y + 3, 26, 26), ASH_WARM if pressed_id == id else TEXT)
	_center(label, Rect2(rect.position + Vector2(0, 30), Vector2(rect.size.x, 18)), 11, TEXT)
	buttons.append({"id": id, "rect": rect, "enabled": true})

func _draw_header() -> void:
	var at := usable.position + Vector2(16, 12)
	_text("B1", at + Vector2(0, 23), 23, TEXT)
	_ash_underline(at + Vector2(0, 31), 31, ASH_RED)
	_text("잊힌 지하묘지", at + Vector2(48, 18), 12, TEXT)
	_text("%s · 목표와 기록" % ["북", "동", "남", "서"][state.facing], at + Vector2(48, 37), 10, MUTED)
	buttons.append({"id": "journal", "rect": Rect2(at - Vector2(4, 2), Vector2(minf(194, usable.size.x - 136), 48)), "enabled": true})
	var menu_rect := Rect2(usable.end.x - 60, usable.position.y + 10, 48, 48)
	_utility("map", "지도", Rect2(menu_rect.position - Vector2(56, 0), Vector2.ONE * 48))
	_utility("menu", "메뉴", menu_rect)
	if phase() == "combat":
		var head := enemy_head if enemy_head != Vector2.ZERO else combat_center - Vector2(0, 100)
		var r := Rect2(clampf(head.x + 42, usable.position.x + 12, usable.end.x - 150), clampf(head.y - 8, usable.position.y + 72, dock.position.y - 64), 138, 54)
		_ash_hp(Rect2(r.position + Vector2(4, 9), Vector2(4, 33)), state.enemy_hp, state.enemy_max_hp, enemy_trail)
		_text("%d/%d" % [state.enemy_hp, state.enemy_max_hp], r.position + Vector2(17, 27), 19, TEXT)
		_text("경비병 · 정보 ›", r.position + Vector2(17, 46), 11, MUTED)
		buttons.append({"id": "enemy", "rect": r, "enabled": true})

func _hero_chip(index: int, rect: Rect2, id: String, selected: bool, enabled: bool = true) -> void:
	var alpha := 1.0 if shown_hp[index] > 0 else 0.35
	var image_size := minf(46, minf(rect.size.x - 32, rect.size.y - 20))
	var face_rect := Rect2(rect.position + Vector2(2, 1), Vector2.ONE * image_size)
	_face(index, face_rect, alpha)
	var x := face_rect.end.x + 4
	_ash_hp(Rect2(x, rect.position.y + 9, 4, 28), shown_hp[index], Rules.MAX_HP[index], hp_trail[index])
	_text(str(shown_hp[index]), Vector2(x + 9, rect.position.y + 30), 13, Color(TEXT, alpha))
	_text(Rules.NAMES[index], rect.position + Vector2(3, rect.size.y - 3), 11, Color(TEXT if selected else MUTED, alpha))
	if selected:
		var emphasis := 0.92 if reduced_motion else 0.88 + sin(elapsed * 2.4) * 0.12
		_ash_underline(face_rect.position + Vector2(0, image_size + 3), image_size, ASH_WARM, emphasis)
	if damaged_hero == index and hero_damage_time > 0:
		_text("-%d" % hero_damage, face_rect.position + Vector2(8, 16), 18, Color("ffd1a0"))
	buttons.append({"id": id, "rect": rect, "enabled": enabled})

func _draw_party() -> void:
	if phase() != "combat":
		var r := party_rect
		_face(state.selected, Rect2(r.position + Vector2(0, 3), Vector2(56, 56)), 1.0)
		_ash_underline(r.position + Vector2(0, 62), 54, ASH_WARM)
		_ash_hp(Rect2(r.position + Vector2(63, 12), Vector2(4, 29)), shown_hp[state.selected], Rules.MAX_HP[state.selected], hp_trail[state.selected])
		_text(str(shown_hp[state.selected]), r.position + Vector2(75, 35), 18, TEXT)
		_ash_glyph("mana", Rect2(r.position + Vector2(61, 48), Vector2.ONE * 16), ASH_TEAL)
		_text("%d/%d" % [state.mp[state.selected], Rules.MAX_MP[state.selected]], r.position + Vector2(81, 62), 12, ASH_TEAL)
		_text("원정대 ›", r.position + Vector2(2, 81), 11, MUTED)
		if not portrait:
			var offset := 0
			for i in range(4):
				if i == state.selected: continue
				_face(i, Rect2(r.position + Vector2(134 + offset * 31, 31), Vector2.ONE * 28), 0.58 if state.hp[i] > 0 else 0.25)
				offset += 1
		buttons.append({"id": "party", "rect": r, "enabled": true})
		return
	var width := (party_rect.size.x - 18) / 4
	for i in range(4):
		var rise := i * 3.0 if not portrait else 0.0
		_hero_chip(i, Rect2(party_rect.position + Vector2(i * (width + 6), rise), Vector2(width, 64)), "hero_%d" % i, state.selected == i, not busy and state.hp[i] > 0)
	var mp_at := party_rect.position + Vector2(state.selected * (width + 6) + 2, 70)
	_ash_glyph("mana", Rect2(mp_at, Vector2.ONE * 13), ASH_TEAL)
	_text("%d/%d" % [state.mp[state.selected], Rules.MAX_MP[state.selected]], mp_at + Vector2(17, 12), 12, ASH_TEAL)
	var info := Rect2(party_rect.position - Vector2(0, 48), Vector2(70, 48))
	_button("party", "원정대 ›", info, true, false, 11)

func _draw_actions() -> void:
	# No footer fill: different functions have distinct silhouettes over the world.
	_draw_party()
	if phase() == "combat":
		if busy:
			_center("경비병의 반격" if hero_damage_time > 0.85 else "행동 중…", footer_rect, 13, MUTED)
			return
		var w := (footer_rect.size.x - 24) / 3
		_action_button("skill", "스킬", "%d MP" % Rules.COST[state.selected], state.selected + 1, Rect2(footer_rect.position, Vector2(w, 72)), state.mp[state.selected] >= Rules.COST[state.selected])
		_action_button("attack", "공격", "%d 피해" % Rules.DAMAGE[state.selected], 0, Rect2(footer_rect.position + Vector2(w + 12, 0), Vector2(w, 72)), true, true)
		_action_button("tactics", "전술", "방어 · 가방", 5, Rect2(footer_rect.position + Vector2((w + 12) * 2, 0), Vector2(w, 72)), true)
	else:
		_utility("movement", "이동", Rect2(usable.get_center().x - 24, usable.end.y - 74, 48, 60))
		if state.phase == "defeat" or state.chest_open:
			_button("restart", "새 탐험", footer_rect, not busy, true, 13)
		else:
			var context: String = state.context_label()
			var glyph_rect := Rect2(footer_rect.get_center().x - 17, footer_rect.position.y + 2, 34, 34)
			_ash_glyph("inspect", glyph_rect, ASH_WARM if context != "주변 조사" else TEXT, 0.4 if busy else 1.0)
			_center(context, Rect2(footer_rect.position + Vector2(-12, 42), Vector2(footer_rect.size.x + 24, 22)), 11, MUTED if busy else TEXT)
			buttons.append({"id": "interact", "rect": footer_rect, "enabled": not busy})
		if movement_open and state.phase not in ["combat", "defeat"]:
			var pad := Rect2(usable.get_center().x - 80, usable.end.y - 218, 160, 112)
			var ids := ["strafe_left", "forward", "strafe_right", "turn_left", "back", "turn_right"]
			for i in range(6):
				var r := Rect2(pad.position + Vector2((i % 3) * 56, (i / 3) * 60), Vector2(48, 52))
				_ash_glyph(ids[i], Rect2(r.get_center() - Vector2.ONE * 13, Vector2.ONE * 26), ASH_WARM if pressed_id == ids[i] else TEXT)
				buttons.append({"id": ids[i], "rect": r, "enabled": not busy})

func _draw_scene() -> void:
	var center := combat_center if combat_center != Vector2.ZERO else scene_rect.get_center()
	var head := enemy_head if enemy_head != Vector2.ZERO else center - Vector2(0, 120)
	var feet := enemy_feet if enemy_feet != Vector2.ZERO else center + Vector2(0, 120)
	enemy_rect = Rect2(center.x - minf(100, size.x * 0.23), head.y, minf(200, size.x * 0.46), maxf(64, feet.y - head.y))
	if target_selected and phase() == "combat":
		for direction in [-1, 1]:
			var at := feet + Vector2(direction * 34, 2)
			_ash_stroke(at, at + Vector2(direction * 15, 2), TEXT, 2)
			_ash_stroke(at, at + Vector2(direction * 4, -6), TEXT, 2)
	if not busy and world_target_visible and phase() == "explore" and state.context_label() != "주변 조사":
		var marker := Rect2(center - Vector2(32, 32), Vector2(64, 64))
		_ash_glyph("inspect", Rect2(center - Vector2(14, 17), Vector2.ONE * 28), ASH_WARM)
		_center("조사", Rect2(center + Vector2(-24, 14), Vector2(48, 18)), 11, TEXT)
		buttons.append({"id": "world_interact", "rect": marker, "enabled": true})
	if effect > 0:
		draw_rect(scene_rect, Color(effect_color, effect * 0.035))
		_draw_combat_effect()
		if not damage_text.is_empty():
			var number := Rect2(center - Vector2(60, 65 + (1 - effect) * 34), Vector2(120, 42))
			_center(damage_text, number, 30, Color(1, 0.9, 0.7, effect))
	if toast_time > 0:
		var w := minf(360, usable.size.x - 40)
		var r := Rect2(usable.get_center().x - w / 2, dock.position.y - 72, w, 34)
		_center(toast, r, 11 if w < 340 else 12, Color(TEXT, minf(1, toast_time)))
	elif gesture_hint_time > 0 and phase() == "explore" and not movement_open:
		var r := Rect2(usable.position.x + 16, dock.position.y - (34 if portrait else 18), usable.size.x - 32, 24)
		_center("위아래 이동 · 좌우 회전", r, 12, Color(TEXT, minf(0.85, gesture_hint_time)))
	if state.chest_open or state.phase == "defeat":
		var r := Rect2(usable.get_center().x - minf(180, usable.size.x * 0.44), scene_rect.get_center().y - 52, minf(360, usable.size.x * 0.88), 104)
		_center("봉인을 되찾았습니다" if state.chest_open else "마지막 횃불이 꺼졌습니다", Rect2(r.position + Vector2(0, 14), Vector2(r.size.x, 35)), 21, TEXT)
		_ash_underline(r.position + Vector2(r.size.x * 0.4, 54), r.size.x * 0.2, ASH_WARM)
		_center("첫 탐험 완료 · 금화 %d" % state.gold if state.chest_open else "새 탐험으로 다시 도전할 수 있습니다", Rect2(r.position + Vector2(0, 65), Vector2(r.size.x, 28)), 12, TEXT)

func is_modal_open() -> bool:
	return not panel.is_empty()

func _sync_panel_flags() -> void:
	map_open = panel == "map"
	help_open = panel == "help"
	reset_open = panel == "reset"

func open_panel(kind: String, remember := true) -> void:
	if kind == panel and not panel_closing: return
	if is_instance_valid(panel_tween): panel_tween.kill()
	if remember and not panel.is_empty() and panel != kind: panel_history.append(panel)
	panel = kind
	panel_closing = false
	panel_progress = 0.88 if panel_progress > 0.9 else 0.0
	panel_expansion = 0
	pressed_id = ""
	tooltip_id = ""
	tooltip_time = 0
	if kind == "item": item_target = state.selected
	_sync_panel_flags()
	panel_tween = create_tween()
	panel_tween.tween_property(self, "panel_progress", 1.0, 0.01 if reduced_motion else 0.22).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)

func close_panel(immediate := false) -> void:
	if panel.is_empty(): return
	if is_instance_valid(panel_tween): panel_tween.kill()
	panel_closing = true
	pressed_id = ""
	tooltip_id = ""
	if immediate or reduced_motion:
		_finish_close()
		return
	panel_tween = create_tween()
	panel_tween.tween_property(self, "panel_progress", 0.0, 0.18).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_IN)
	panel_tween.tween_callback(_finish_close)

func _finish_close() -> void:
	panel = ""
	panel_history.clear()
	panel_progress = 0
	panel_closing = false
	map_canvas.visible = false
	_sync_panel_flags()

func dismiss_for_action() -> void:
	close_panel()
	while is_modal_open(): await get_tree().process_frame

func go_back() -> void:
	if panel.is_empty(): open_panel("menu")
	elif not panel_history.is_empty():
		var previous: String = panel_history.pop_back()
		open_panel(previous, false)
	else: close_panel()

func allows_modal_action(action: String) -> bool:
	return (panel == "tactics" and action in ["guard", "potion"]) or (panel == "item" and action.begins_with("use_potion_"))

func handle_navigation(action: String) -> bool:
	if action in ["menu", "map", "party", "bag", "journal", "settings", "help", "tactics", "enemy"]:
		if panel == action: close_panel()
		else: open_panel(action)
	elif action == "close": close_panel()
	elif action == "panel_back": go_back()
	elif action == "restart": open_panel("reset")
	elif action == "movement":
		movement_open = not movement_open
		movement_timeout = 5
	elif action == "motion": reduced_motion = not reduced_motion
	elif action == "haptics": haptics = not haptics
	elif action == "pin_movement":
		movement_pinned = not movement_pinned
		movement_open = movement_pinned
	elif action == "expand_sheet": _expand_sheet(panel_expansion < 0.5)
	elif action.begins_with("item_"):
		selected_item = action.trim_prefix("item_")
		open_panel("item")
	elif action.begins_with("target_"): item_target = int(action.trim_prefix("target_"))
	elif action == "map_plus": _zoom_map(1.25, map_rect.get_center())
	elif action == "map_minus": _zoom_map(0.8, map_rect.get_center())
	elif action == "map_reset":
		map_zoom = 1
		map_pan = Vector2.ZERO
	else: return false
	if action in ["motion", "haptics", "pin_movement"]: save_preferences()
	return true

func save_preferences() -> void:
	if not preferences_enabled: return
	var prefs := ConfigFile.new()
	for key in ["reduced_motion", "haptics", "movement_pinned", "muted"]: prefs.set_value("ui", key, get(key))
	prefs.save("user://mobile-ui.cfg")

func cancel_gestures() -> void:
	if gesture == "sheet" and not panel_closing:
		panel_progress = 1
	pointers.clear()
	active_pointer = -99
	pressed_id = ""
	gesture = ""
	gesture_consumed = false
	drag_target = -1

func _expand_sheet(expanded: bool) -> void:
	if is_instance_valid(expansion_tween): expansion_tween.kill()
	expansion_tween = create_tween()
	expansion_tween.tween_property(self, "panel_expansion", 1.0 if expanded else 0.0, 0.01 if reduced_motion else 0.22).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)

func _target_panel_rect() -> Rect2:
	if not portrait:
		var width := minf(430, usable.size.x - 24)
		return Rect2(usable.end.x - width - 12, usable.position.y + 8, width, usable.size.y - 16)
	var height := minf(usable.size.y - 24, 580 if panel in ["map", "journal", "party", "item"] else 450)
	if panel == "bag": height = lerpf(minf(430, usable.size.y * 0.7), usable.size.y - 24, panel_expansion)
	return Rect2(usable.position.x + 8, usable.end.y - height - 8, usable.size.x - 16, height)

func _draw_sheet() -> void:
	AshSurfaces.draw(self)

func _draw_tooltip() -> void:
	if tooltip_id.is_empty() or busy or is_modal_open(): return
	var description := action_description(tooltip_id)
	if description.is_empty(): return
	var w := minf(380, usable.size.x - 32)
	var r := Rect2(usable.get_center().x - w / 2, dock.position.y - 136, w, 108)
	# A local reading veil only for transient detail, with no surrounding frame.
	var points := PackedVector2Array([r.position + Vector2(8, 0), Vector2(r.end.x - 6, r.position.y + 3), r.end - Vector2(0, 6), Vector2(r.position.x, r.end.y)])
	draw_colored_polygon(points, Color(0.025, 0.035, 0.04, 0.90))
	_text(description.title, r.position + Vector2(14, 27), 15, TEXT)
	_ash_underline(r.position + Vector2(14, 35), 26, ASH_TEAL)
	_wrapped(description.body, r.position + Vector2(14, 58), w - 28, 12, 3, TEXT)

func _draw() -> void:
	if state == null or size.x < 300 or size.y < 300: return
	buttons.clear()
	layout()
	if not is_modal_open():
		_draw_scene()
		_draw_header()
		_draw_actions()
		_draw_tooltip()
	_draw_sheet()

func _pulse() -> void:
	if haptics and OS.has_feature("mobile"): Input.vibrate_handheld(16, 0.35)

func _activate(id: String) -> void:
	tooltip_id = ""
	hover_time = 0
	_pulse()
	if id in ["forward", "back", "turn_left", "turn_right", "strafe_left", "strafe_right"]: movement_timeout = 5
	if id == "party_done": close_panel(); return
	if id == "world_interact": id = "interact"
	if id.begins_with("hero_") and id == last_tap_id and elapsed - last_tap_time < 0.32:
		if panel == "party": close_panel()
		else: open_panel("party")
		last_tap_id = ""
		return
	last_tap_id = id
	last_tap_time = elapsed
	action_requested.emit(id)

func _hit(at: Vector2) -> String:
	for button in buttons:
		if button.rect.has_point(at): return button.id
	return ""

func _enabled(id: String) -> bool:
	for button in buttons:
		if button.id == id: return button.enabled
	return false

func _zoom_map(factor: float, anchor: Vector2) -> void:
	var previous := map_zoom
	map_zoom = clampf(map_zoom * factor, 1.0, 3.0)
	var local := anchor - map_rect.get_center()
	map_pan = local - (local - map_pan) * map_zoom / previous
	_clamp_map_pan()

func _clamp_map_pan() -> void:
	var limit := map_rect.size * maxf(0, map_zoom - 1) * 0.5 + Vector2.ONE * (24 if map_zoom > 1 else 0)
	map_pan.x = clampf(map_pan.x, -limit.x, limit.x)
	map_pan.y = clampf(map_pan.y, -limit.y, limit.y)

func _begin_pointer(at: Vector2, index: int) -> void:
	pointers[index] = at
	if panel == "map" and pointers.size() == 2:
		var points: Array = pointers.values()
		if not (map_rect.has_point(points[0]) and map_rect.has_point(points[1])): return
		pinch_distance = Vector2(points[0]).distance_to(points[1])
		pinch_zoom = map_zoom
		pinch_anchor = ((Vector2(points[0]) + Vector2(points[1])) / 2 - map_rect.get_center() - map_pan) / map_zoom
		gesture = "pinch"
		gesture_consumed = true
		pressed_id = ""
		return
	if active_pointer != -99 or pointers.size() > 1: return
	active_pointer = index
	pointer_start = at
	pointer_last = at
	pointer_age = 0
	pointer_max_distance = 0
	gesture_consumed = false
	long_pressed = false
	press_time = 0
	pressed_id = ""
	gesture = ""
	if panel_closing or (is_modal_open() and panel_progress < 0.98): gesture_consumed = true; return
	if is_modal_open():
		if not panel_rect.has_point(at): pressed_id = "dismiss"; return
		pressed_id = _hit(at)
		if not pressed_id.is_empty(): return
		if at.y < panel_rect.position.y + 72:
			gesture = "sheet"
			panel_was_expanded = panel_expansion > 0.5
		elif panel == "map" and map_rect.has_point(at): gesture = "map"; drag_start_pan = map_pan
		elif panel == "journal" and log_rect.has_point(at): gesture = "journal"; drag_start_scroll = journal_scroll
		elif panel == "party": gesture = "party"
		elif panel == "item" and selected_item == "potion" and item_drag_rect.has_point(at): gesture = "item_candidate"
		return
	pressed_id = _hit(at)
	if not pressed_id.is_empty(): return
	# Leave the actual OS gesture strip untouched; app edge gestures start 24px inward.
	if at.x < usable.position.x + 20 or at.x > usable.end.x - 20: gesture_consumed = true; return
	if scene_rect.has_point(at):
		gesture = "world"
		if at.y > usable.position.y + 100 and at.y < dock.position.y - 40:
			if at.x < usable.position.x + 48: gesture = "edge_left"
			elif at.x > usable.end.x - 48: gesture = "edge_right"

func _move_pointer(at: Vector2, index: int) -> void:
	if not pointers.has(index): return
	pointers[index] = at
	if gesture == "pinch":
		if pointers.size() >= 2:
			var points: Array = pointers.values()
			var a: Vector2 = points[0]
			var b: Vector2 = points[1]
			map_zoom = clampf(pinch_zoom * a.distance_to(b) / maxf(1, pinch_distance), 1, 3)
			map_pan = (a + b) / 2 - map_rect.get_center() - pinch_anchor * map_zoom
			_clamp_map_pan()
		return
	if index != active_pointer: return
	pointer_last = at
	var delta := at - pointer_start
	pointer_max_distance = maxf(pointer_max_distance, delta.length())
	if pointer_max_distance > 12:
		if pressed_id.begins_with("hero_") or pressed_id == "party": gesture = "party"
		elif pressed_id == "world_interact": gesture = "world"
		pressed_id = ""
		tooltip_id = ""
		long_pressed = true
	match gesture:
		"map": map_pan = drag_start_pan + delta; _clamp_map_pan()
		"journal": journal_scroll = maxf(0, drag_start_scroll - delta.y)
		"sheet":
			var distance := delta.y if portrait else delta.x
			panel_progress = clampf(1 - maxf(0, distance) / (panel_rect.size.y if portrait else panel_rect.size.x), 0.25, 1)
		"item_candidate":
			if pointer_age >= 0.25 and delta.length() > 12: gesture = "item_drag"
		"item_drag":
			drag_position = at
			drag_target = -1
			var id := _hit(at)
			if id.begins_with("target_"):
				var target := int(id.trim_prefix("target_"))
				if state.hp[target] > 0 and state.hp[target] < Rules.MAX_HP[target] and state.potions > 0: drag_target = target

func _end_pointer(at: Vector2, index: int, canceled := false) -> void:
	pointers.erase(index)
	if gesture == "pinch":
		if pointers.is_empty(): active_pointer = -99; gesture = ""; gesture_consumed = false
		return
	if index != active_pointer: return
	var candidate := pressed_id
	pressed_id = ""
	var delta := at - pointer_start
	var finished_gesture := gesture
	gesture = ""
	active_pointer = -99
	if canceled:
		if finished_gesture == "sheet": panel_progress = 1
		return
	if gesture_consumed: return
	if finished_gesture == "sheet":
		var distance := delta.y if portrait else delta.x
		if portrait and panel == "bag" and delta.y < -56: _expand_sheet(true)
		elif distance > 56:
			if portrait and panel == "bag" and panel_was_expanded: _expand_sheet(false)
			else: close_panel(); return
		if is_instance_valid(panel_tween): panel_tween.kill()
		panel_tween = create_tween()
		panel_tween.tween_property(self, "panel_progress", 1.0, 0.01 if reduced_motion else 0.16).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
		return
	if finished_gesture == "item_drag":
		var released_on := _hit(at)
		if released_on.begins_with("target_") and not busy:
			var target := int(released_on.trim_prefix("target_"))
			if state.potions > 0 and state.hp[target] > 0 and state.hp[target] < Rules.MAX_HP[target]: _activate("use_potion_%d" % target)
		drag_target = -1
		return
	if finished_gesture == "map":
		if pointer_max_distance < 10 and pointer_age < 0.35:
			if last_tap_id == "map_surface" and elapsed - last_tap_time < 0.32: map_zoom = 1; map_pan = Vector2.ZERO
			last_tap_id = "map_surface"; last_tap_time = elapsed
		return
	if finished_gesture == "journal": return
	if finished_gesture == "party" and absf(delta.x) > 48 and absf(delta.x) > absf(delta.y) * 1.2:
		_cycle_hero(1 if delta.x < 0 else -1)
		return
	if finished_gesture in ["world", "edge_left", "edge_right"]:
		if busy: return
		if finished_gesture == "edge_left" and delta.x > 64 and absf(delta.x) > absf(delta.y) * 1.3: _activate("map"); return
		if finished_gesture == "edge_right" and delta.x < -64 and absf(delta.x) > absf(delta.y) * 1.3: _activate("menu"); return
		if phase() in ["explore", "won"] and delta.length() >= 48:
			if absf(delta.y) > absf(delta.x) * 1.25: _activate("forward" if delta.y < 0 else "back")
			elif absf(delta.x) > absf(delta.y) * 1.25: _activate("turn_left" if delta.x < 0 else "turn_right")
			gesture_hint_time = 0
			if not movement_pinned: movement_open = false
		elif phase() == "combat" and pointer_max_distance < 12 and pointer_age < 0.45 and enemy_rect.has_point(at): target_selected = true
		return
	if not long_pressed and pointer_max_distance < 12 and not candidate.is_empty():
		if candidate == "dismiss" and not panel_rect.has_point(at): close_panel()
		elif candidate == _hit(at) and _enabled(candidate): _activate(candidate)

func _cycle_hero(direction: int) -> void:
	if busy: return
	var index: int = state.selected
	for i in range(4):
		index = posmod(index + direction, 4)
		if state.hp[index] > 0: _activate("hero_%d" % index); return

func _gui_input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		recent_touch = 1.0
		if event.pressed: _begin_pointer(event.position, event.index)
		else: _end_pointer(event.position, event.index, event.canceled)
		accept_event()
	elif event is InputEventScreenDrag:
		recent_touch = 1.0
		_move_pointer(event.position, event.index)
		accept_event()
	elif event is InputEventMouseButton:
		if recent_touch > 0: accept_event(); return
		if event.button_index == MOUSE_BUTTON_LEFT:
			if event.pressed: _begin_pointer(event.position, -1)
			else: _end_pointer(event.position, -1)
		elif event.pressed and panel == "map" and map_rect.has_point(event.position):
			if event.button_index in [MOUSE_BUTTON_WHEEL_UP, MOUSE_BUTTON_WHEEL_DOWN]: _zoom_map(1.15 if event.button_index == MOUSE_BUTTON_WHEEL_UP else 1 / 1.15, event.position)
		elif event.pressed and panel == "journal":
			journal_scroll = maxf(0, journal_scroll + (48 if event.button_index == MOUSE_BUTTON_WHEEL_DOWN else -48))
		accept_event()
	elif event is InputEventMouseMotion and active_pointer == -1:
		_move_pointer(event.position, -1)
		accept_event()

func _process(delta: float) -> void:
	recent_touch = maxf(0, recent_touch - delta)
	mouse_hover_available = recent_touch <= 0
	gesture_hint_time = maxf(0, gesture_hint_time - delta)
	if active_pointer != -99:
		pointer_age += delta
		if pointer_age >= 0.45 and pointer_max_distance < 12 and not gesture_consumed:
			if pressed_id.begins_with("hero_"):
				if not busy: action_requested.emit(pressed_id)
				open_panel("party"); gesture_consumed = true; _pulse()
			elif pressed_id.begins_with("item_"):
				var id := pressed_id
				_activate(id); gesture_consumed = true
			elif gesture in ["world", "edge_left", "edge_right"] and (phase() == "combat" or state.context_label() == "경비병과 대치") and enemy_rect.has_point(pointer_start):
				open_panel("enemy"); gesture_consumed = true; _pulse()
	if movement_open and not movement_pinned:
		movement_timeout -= delta
		if movement_timeout <= 0 and active_pointer == -99: movement_open = false
	var current_phase := phase()
	if current_phase != last_phase:
		last_phase = current_phase
		context_fade = 0
		target_selected = false
		movement_open = movement_pinned and current_phase == "explore"
		layout()
		layout_changed.emit()
	context_fade = minf(1, context_fade + delta * 5)
	super._process(delta)
