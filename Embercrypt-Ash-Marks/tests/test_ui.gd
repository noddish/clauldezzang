extends SceneTree
## Integration checks use actual viewport-dispatched ScreenTouch/ScreenDrag events.
const Rules = preload("res://scripts/dungeon_state.gd")
var failures := 0
var checks := 0
var game
var h

func check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures += 1
		printerr("FAIL UI: ", label)

func _initialize() -> void:
	_run.call_deferred()

func settle(seconds := 0.30) -> void:
	await create_timer(seconds).timeout
	await RenderingServer.frame_post_draw

func rect(id: String) -> Rect2:
	for button in h.buttons:
		if button.id == id: return button.rect
	check(false, "Button exists: " + id)
	return Rect2(0, 0, 48, 48)

func has_button(id: String) -> bool:
	for b in h.buttons:
		if b.id == id: return true
	return false

func touch(at: Vector2, down: bool, index := 0, canceled := false) -> void:
	var event := InputEventScreenTouch.new()
	event.position = at * game.ui_scale
	event.pressed = down
	event.index = index
	event.canceled = canceled
	root.push_input(event)

func drag(at: Vector2, index := 0) -> void:
	var event := InputEventScreenDrag.new()
	event.position = at * game.ui_scale
	event.index = index
	root.push_input(event)

func tap_at(at: Vector2, delay := 0.30) -> void:
	touch(at, true)
	await process_frame
	touch(at, false)
	await settle(delay)

func tap(id: String, delay := 0.30) -> void:
	await RenderingServer.frame_post_draw
	await tap_at(rect(id).get_center(), delay)

func swipe(at: Vector2, delta: Vector2, delay := 0.30) -> void:
	touch(at, true)
	await process_frame
	drag(at + delta * 0.5)
	await process_frame
	drag(at + delta)
	touch(at + delta, false)
	await settle(delay)

func hold(id: String) -> void:
	var at := rect(id).get_center()
	touch(at, true)
	await settle(0.56)
	touch(at, false)
	await settle(0.08)

func open(kind: String) -> void:
	h.open_panel(kind)
	await settle()

func shut() -> void:
	h.close_panel(true)
	await settle(0.04)

func fresh(combat := false) -> void:
	await shut()
	game.state = Rules.new()
	h.state = game.state
	game.dungeon.state = game.state
	if combat:
		game.state.position = Vector2i(4, 6)
		game.state.phase = "combat"
		game.state.has_key = true
		game.state.door_open = true
	h.sync_state()
	game.dungeon.sync_immediate()
	await settle()

func assert_targets(label: String) -> void:
	var inside := true
	var large := true
	var overlap := false
	for i in range(h.buttons.size()):
		var a: Dictionary = h.buttons[i]
		if not h.usable.encloses(a.rect): inside = false; printerr("OUTSIDE ", label, " ", a.id, " ", a.rect)
		if a.rect.size.x < 48 or a.rect.size.y < 48: large = false; printerr("SMALL ", label, " ", a.id, " ", a.rect)
		for j in range(i):
			if a.rect.intersects(h.buttons[j].rect): overlap = true; printerr("OVERLAP ", label, " ", a.id, " / ", h.buttons[j].id)
	check(inside and large and not overlap, label + " has separate, visible >=48 logical-pixel touch areas")

func assert_scene_coverage(label: String) -> void:
	# The world must extend behind the HUD; no canvas area is reserved as a footer.
	var logical_full: bool = h.scene_rect.position.is_equal_approx(Vector2.ZERO) and h.scene_rect.size.is_equal_approx(h.size)
	var rendered_full: bool = game.picture.position.is_equal_approx(Vector2.ZERO) and game.picture.size.is_equal_approx(game.size)
	check(logical_full and rendered_full, label + " renders the world across the full logical and physical canvas")

func _run() -> void:
	root.size = Vector2i(844, 390)
	game = load("res://main.tscn").instantiate()
	root.add_child(game)
	h = game.hud
	await settle(0.6)
	assert_scene_coverage("Exploration")
	check(h.scene_rect.size.y / h.size.y > 0.8 and not has_button("forward") and not has_button("guard"), "Exploration keeps >80% scene and hides unneeded controls")
	var center := Vector2(420, 180)
	await swipe(center, Vector2(0, -80))
	check(game.state.position == Vector2i(4, 8), "Native swipe moves exactly one cell")
	await swipe(center, Vector2(0, 80))
	check(game.state.position == Vector2i(4, 9), "Down swipe moves back")
	await swipe(center, Vector2(80, 0))
	check(game.state.facing == 1, "Right swipe rotates clockwise")
	await swipe(center, Vector2(-80, 0))
	check(game.state.facing == 0, "Left swipe rotates counterclockwise")
	await swipe(center, Vector2(20, -20))
	await swipe(center, Vector2(70, -70))
	check(game.state.position == Vector2i(4, 9) and game.state.facing == 0, "Small and diagonal gestures cancel")
	await tap("movement")
	check(has_button("forward") and has_button("strafe_left") and has_button("strafe_right"), "Visible fallback exposes all six traversal actions")
	var at := rect("forward").get_center()
	var outside: Vector2 = Vector2(h.usable.get_center().x, h.usable.position.y + 80)
	touch(at, true)
	drag(outside)
	touch(outside, false)
	await settle()
	check(game.state.position == Vector2i(4, 9), "Release outside button cancels movement")
	touch(at, true)
	touch(at + Vector2(50, 0), true, 1)
	touch(at, false)
	touch(at + Vector2(50, 0), false, 1)
	await settle()
	check(game.state.position == Vector2i(4, 8), "Secondary touch does not create a second movement")
	var event := InputEventMouseButton.new()
	event.button_index = MOUSE_BUTTON_LEFT
	event.position = at
	event.pressed = true
	root.push_input(event)
	event = event.duplicate(); event.pressed = false; root.push_input(event)
	await settle()
	check(game.state.position == Vector2i(4, 8), "Emulated mouse after touch cannot duplicate input")
	h.movement_timeout = 0.01
	await settle()
	check(not h.movement_open, "Unused movement pad auto collapses")
	await tap("map")
	check(h.panel == "map" and not has_button("forward"), "Map opens as modal overlay")
	var previous: Vector2i = game.state.position
	game._action("forward")
	await swipe(center, Vector2(0, -80))
	check(game.state.position == previous, "Modal blocks world pointer and keyboard actions")
	await tap("map_plus")
	check(h.map_zoom > 1, "Visible map zoom alternative")
	var mc: Vector2 = h.map_rect.get_center()
	await swipe(mc, Vector2(30, 20))
	check(h.map_pan.length() > 0, "Map drag pans without moving player")
	await tap("map_reset")
	touch(mc - Vector2(30, 0), true, 0)
	touch(mc + Vector2(30, 0), true, 1)
	drag(mc - Vector2(65, 0), 0)
	drag(mc + Vector2(65, 0), 1)
	touch(mc - Vector2(65, 0), false, 0)
	touch(mc + Vector2(65, 0), false, 1)
	await settle()
	check(h.map_zoom > 2 and h.active_pointer == -99, "Native two-finger pinch zoom and release")
	await tap_at(mc, 0.06)
	await tap_at(mc, 0.08)
	check(h.map_zoom == 1 and h.map_pan == Vector2.ZERO, "Map double tap resets view")
	await tap("close")
	check(h.panel.is_empty(), "Visible close returns to scene")
	await swipe(Vector2(30, 180), Vector2(90, 0))
	check(h.panel == "map", "Inset edge swipe opens map")
	await tap_at(Vector2(250, 180))
	check(h.panel.is_empty(), "Outside tap dismisses panel without world action")
	await swipe(Vector2(4, 180), Vector2(90, 0))
	check(h.panel.is_empty() and game.state.facing == 0, "System edge strip does not trigger game gestures")
	await tap("menu")
	await tap("party")
	check(h.panel_history == ["menu"], "Nested panel remembers origin")
	await swipe(h.body_rect.position + Vector2(180, 140), Vector2(-90, 0))
	check(game.state.selected == 1, "Party sheet swipe changes hero without a turn")
	await tap("hero_2", 0.08)
	await tap("hero_2", 0.08)
	await settle()
	check(game.state.selected == 2 and h.panel.is_empty() and game.state.turn == 0, "Party double tap confirms selection only")
	await open("menu")
	await tap("settings")
	h.go_back()
	await settle()
	check(h.panel == "menu", "Back restores previous panel")
	var handle: Vector2 = h.panel_rect.position + Vector2(140, 30)
	touch(handle, true)
	await process_frame
	drag(handle + Vector2(70, 0))
	await settle(0.05)
	touch(handle + Vector2(70, 0), false, 0, true)
	await settle()
	check(h.panel == "menu" and h.panel_progress >= 0.98 and h.active_pointer == -99, "Canceled native sheet drag restores an interactive panel")
	await shut()
	await open("menu")
	await swipe(h.panel_rect.position + Vector2(140, 30), Vector2(95, 0))
	check(h.panel.is_empty(), "Landscape drawer handle swipe dismisses")
	game.state.position = Vector2i(5, 8); game.state.facing = 1
	game.dungeon.sync_immediate()
	await settle()
	check(has_button("world_interact"), "Nearby key has touch target at world projection")
	await tap("world_interact")
	check(game.state.has_key, "World object tap collects key using original rules")
	await fresh(true)
	assert_scene_coverage("Combat")
	check(h.scene_rect.size.y / h.size.y > 0.7 and has_button("attack") and not has_button("movement"), "Combat changes HUD and preserves >70% scene")
	# World-anchored information must follow its target rather than the screen header.
	var enemy_info_before := rect("enemy").get_center()
	var enemy_x: float = game.dungeon.enemy.position.x
	game.dungeon.enemy.position.x += 0.25
	await settle(0.08)
	check(absf(rect("enemy").get_center().x - enemy_info_before.x) > 1.0, "Enemy information follows the projected target position")
	game.dungeon.enemy.position.x = enemy_x
	await settle(0.08)
	var attack_at := rect("attack").get_center()
	touch(attack_at, true)
	await process_frame
	game._notification(Node.NOTIFICATION_APPLICATION_FOCUS_OUT)
	touch(attack_at, false)
	await settle(0.08)
	check(game.state.turn == 0 and game.state.enemy_hp == 96 and h.active_pointer == -99, "Focus loss cancels a held native action without firing on release")
	await tap_at(h.combat_center)
	check(h.target_selected and game.state.turn == 0, "Enemy tap selects without attacking")
	touch(h.combat_center, true)
	await settle(0.56)
	touch(h.combat_center, false)
	await settle()
	check(h.panel == "enemy" and game.state.turn == 0, "Enemy long press inspects without consuming turn")
	await tap("close")
	await tap("hero_2")
	await hold("skill")
	check(h.tooltip_id == "skill" and game.state.mp[2] == 26, "Long press skill explains without casting")
	await tap("skill", 0.10)
	check(game.state.mp[2] == 20 and game.state.enemy_hp == 68, "Short tap casts original mage skill")
	check(h.shown_hp[0] == 52 and game.state.hp[0] == 43 and not h.shown_messages.back().contains("반격"), "HP and combat log wait for counterattack impact")
	check(game.busy and not has_button("attack"), "Animation hides action controls and locks input")
	game._action("skill")
	check(game.state.mp[2] == 20 and game.state.turn == 1, "Busy state rejects duplicate combat action")
	await settle(0.95)
	check(h.shown_hp[0] == 43 and h.shown_messages.back().contains("반격") and not game.busy, "Impact syncs state and actions unlock")
	game.state.mp[2] = 0
	await tap("skill")
	check(game.state.enemy_hp == 68 and game.state.turn == 1, "Disabled skill cannot cast")
	await tap("tactics")
	var turn_before: int = game.state.turn
	await tap("guard", 0.03)
	game._action("guard")
	game._action("attack")
	var back_event := InputEventKey.new()
	back_event.keycode = KEY_ESCAPE; back_event.pressed = true
	root.push_input(back_event)
	game._notification(Node.NOTIFICATION_WM_GO_BACK_REQUEST)
	await settle(1.05)
	check(game.state.turn == turn_before + 1 and game.state.hp[2] == 29 and h.panel.is_empty(), "Guard sheet closes despite concurrent back/duplicate commands, executing only once")
	await open("bag")
	await hold("item_potion")
	await settle()
	check(h.panel == "item", "Long press inventory item opens detail")
	await tap("target_0")
	var stock: int = game.state.potions
	await tap("use_potion_0", 1.10)
	check(game.state.potions == stock - 1 and game.state.hp[0] == 52 and h.panel.is_empty(), "Visible potion target and use preserves combat turn rules")
	await fresh()
	game.state.hp[1] = 10; h.sync_state()
	await open("bag")
	await tap("item_potion")
	var start: Vector2 = h.item_drag_rect.get_center()
	var dest := rect("target_1").get_center()
	touch(start, true); await settle(0.30)
	drag(start + Vector2(20, 0)); drag(dest)
	touch(dest, false)
	await settle(0.70)
	check(game.state.hp[1] == 35 and game.state.potions == 1, "Hold-drag potion to wounded hero heals once")
	await open("item")
	start = h.item_drag_rect.get_center()
	touch(start, true); await settle(0.30)
	drag(start + Vector2(20, 0)); drag(rect("target_1").get_center())
	touch(h.body_rect.get_center(), false)
	await settle()
	check(game.state.potions == 1 and game.state.hp[1] == 35, "Drag release outside valid target does not use item")
	await tap("target_0")
	await tap("use_potion_0")
	check(game.state.potions == 1, "Full HP target cannot consume potion")
	await shut()
	root.size = Vector2i(390, 844)
	await settle()
	await open("bag")
	await swipe(h.panel_rect.position + Vector2(130, 25), Vector2(0, -85))
	check(h.panel_expansion > 0.98, "Portrait bag handle expands to full height")
	await swipe(h.panel_rect.position + Vector2(130, 25), Vector2(0, 85))
	check(h.panel_expansion < 0.02 and h.panel == "bag", "Expanded bag swipe collapses before closing")
	await swipe(h.panel_rect.position + Vector2(130, 25), Vector2(0, 85))
	check(h.panel.is_empty(), "Collapsed bottom sheet swipe dismisses")
	for i in range(14): game.state.log_message("기록 %d" % i)
	h.end_event()
	await open("journal")
	await swipe(h.log_rect.get_center(), Vector2(0, -100))
	check(h.journal_scroll > 0, "Journal scroll reveals older entries")
	await shut()
	await open("settings")
	await tap("motion")
	check(h.reduced_motion, "Reduced motion setting is available")
	await tap("pin_movement")
	await shut()
	h.movement_timeout = 0
	await settle()
	check(h.movement_open and h.movement_pinned, "Pinned movement remains discoverable")
	h.movement_pinned = false; h.movement_open = false
	await open("reset")
	await tap("close")
	check(game.state.potions == 1, "Cancel reset preserves game")
	await open("reset")
	await tap("confirm_restart")
	check(game.state.potions == 2 and game.state.position == Vector2i(4, 9), "Explicit restart confirmation resets game")
	# Real input paths across layouts; bounds checks include every available panel.
	for dimensions in [Vector2i(360, 640), Vector2i(390, 844), Vector2i(640, 360), Vector2i(844, 390), Vector2i(1280, 760)]:
		root.size = dimensions
		await settle(0.15)
		await fresh()
		assert_scene_coverage(str(dimensions) + " explore")
		assert_targets(str(dimensions) + " explore")
		await tap("movement", 0.03)
		assert_targets(str(dimensions) + " movement")
		await fresh(true)
		assert_scene_coverage(str(dimensions) + " combat")
		assert_targets(str(dimensions) + " combat")
		for kind in ["menu", "party", "bag", "item", "map", "journal", "settings", "help", "tactics", "enemy", "reset"]:
			await open(kind)
			assert_targets(str(dimensions) + " " + kind)
		await shut()
	# Density simulation: same 390x844 logical canvas at 2x pixels.
	root.size = Vector2i(780, 1688)
	game.scale_override = 2
	game._update_layout()
	await fresh()
	assert_scene_coverage("2x density")
	check(h.size == Vector2(390, 844), "Density conversion retains logical mobile dimensions")
	await tap("map")
	check(h.panel == "map", "Viewport touch coordinates transform correctly at 2x density")
	await shut()
	h.safe_insets = Vector4(24, 32, 20, 28)
	h.layout()
	await settle(0.05)
	assert_scene_coverage("Notch and home indicator")
	assert_targets("Notch and home indicator exploration")
	await open("map")
	assert_targets("Notch and home indicator map")
	await shut()
	# Desktop mouse path is still available after the touch suppression window.
	await settle(1.1)
	at = rect("menu").get_center() * game.ui_scale
	event = InputEventMouseButton.new(); event.button_index = MOUSE_BUTTON_LEFT; event.position = at; event.pressed = true; root.push_input(event)
	event = event.duplicate(); event.pressed = false; root.push_input(event)
	await settle()
	check(h.panel == "menu", "Desktop mouse fallback works with density scaling")
	print("UI: %d checks, %d failures" % [checks, failures])
	quit(1 if failures else 0)
