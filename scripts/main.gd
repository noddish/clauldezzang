extends Control

const Rules = preload("res://scripts/dungeon_state.gd")
const DungeonView = preload("res://scripts/dungeon_view.gd")
const HUD = preload("res://scripts/hud.gd")
const Sound = preload("res://scripts/sound.gd")
const SAVE_PATH := "user://expedition-v1.json"

var state
var dungeon: Node3D
var viewport: SubViewport
var picture: TextureRect
var hud: Control
var sound: Node
var busy := false
var action_pending := false
var test_mode := false
var capture_path := ""
var scenario := ""
var walkthrough := false
var ui_scale := 1.0
var scale_override := 0.0
var panel_preview := ""
var last_layout_size := Vector2.ZERO

func _ready() -> void:
	get_tree().quit_on_go_back = false
	var args := OS.get_cmdline_user_args()
	for arg in args:
		if arg.begins_with("--capture="): capture_path = arg.trim_prefix("--capture=")
		if arg.begins_with("--scenario="): scenario = arg.trim_prefix("--scenario=")
		if arg == "--walkthrough": walkthrough = true
		if arg.begins_with("--panel="): panel_preview = arg.trim_prefix("--panel=")
		if arg.begins_with("--ui-scale="): scale_override = float(arg.trim_prefix("--ui-scale="))
		if arg.begins_with("--size="):
			var dimensions := arg.trim_prefix("--size=").split("x")
			if dimensions.size() == 2: get_window().size = Vector2i(maxi(360, int(dimensions[0])), maxi(360, int(dimensions[1])))
	test_mode = "--fresh" in args or not capture_path.is_empty() or walkthrough
	if "--portrait" in args: get_window().size = Vector2i(480, 900)
	if "--phone" in args: get_window().size = Vector2i(844, 390)
	state = Rules.new()
	if not test_mode: state.load_from(SAVE_PATH)
	_setup_scenario()
	var backdrop := ColorRect.new()
	backdrop.color = Color("0c1519")
	backdrop.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	backdrop.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(backdrop)
	viewport = SubViewport.new()
	viewport.size = Vector2i(640, 440)
	viewport.own_world_3d = true
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	viewport.positional_shadow_atlas_size = 0
	viewport.msaa_3d = Viewport.MSAA_DISABLED
	add_child(viewport)
	dungeon = DungeonView.new()
	viewport.add_child(dungeon)
	dungeon.build(state)
	dungeon.counter_impact.connect(_counter_impact)
	picture = TextureRect.new()
	picture.texture = viewport.get_texture()
	picture.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	picture.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	picture.stretch_mode = TextureRect.STRETCH_SCALE
	var scene_material := ShaderMaterial.new()
	scene_material.shader = preload("res://scripts/scene_finish.gdshader")
	picture.material = scene_material
	picture.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(picture)
	hud = HUD.new()
	hud.state = state
	hud.preferences_enabled = not test_mode
	add_child(hud)
	hud.action_requested.connect(_action)
	hud.layout_changed.connect(_update_layout)
	sound = Sound.new()
	sound.muted = hud.muted
	add_child(sound)
	resized.connect(_update_layout)
	_update_layout.call_deferred()
	if walkthrough: _run_walkthrough.call_deferred()
	elif not capture_path.is_empty(): _capture.call_deferred()

func _setup_scenario() -> void:
	if scenario in ["combat", "treasure", "spell"]:
		state.has_key = true
		state.door_open = true
		state.position = Vector2i(4, 6)
		state.facing = 0
		state.phase = "combat"
		state._reveal()
	if scenario == "treasure":
		state.enemy_hp = 0
		state.position = Vector2i(4, 2)
		state.phase = "explore"
		state.gold = 20
		state._reveal()

func _update_layout() -> void:
	if not is_instance_valid(hud): return
	if size != last_layout_size: hud.cancel_gestures()
	last_layout_size = size
	ui_scale = maxf(1.0, minf(size.x, size.y) / 390.0) if OS.has_feature("mobile") else 1.0
	if scale_override > 0: ui_scale = scale_override
	hud.scale = Vector2.ONE * ui_scale
	hud.size = size / ui_scale
	hud.safe_insets = Vector4.ZERO
	if OS.has_feature("mobile"):
		var safe := DisplayServer.get_display_safe_area()
		if safe.size.x > 0 and safe.size.y > 0:
			hud.safe_insets = Vector4(maxf(0, safe.position.x), maxf(0, safe.position.y), maxf(0, size.x - safe.end.x), maxf(0, size.y - safe.end.y)) / ui_scale
	hud.layout()
	picture.position = hud.scene_rect.position * ui_scale
	picture.size = hud.scene_rect.size * ui_scale
	var width := clampi(int(hud.scene_rect.size.x * 0.75), 320, 720)
	var height := maxi(180, int(width * hud.scene_rect.size.y / hud.scene_rect.size.x))
	viewport.size = Vector2i(width, height)
	# Keep the corridor and enemy readable in tall portrait viewports.
	var aspect: float = hud.scene_rect.size.x / hud.scene_rect.size.y
	dungeon.camera.fov = maxf(65.0, rad_to_deg(2.0 * atan(tan(deg_to_rad(58.0) / 2.0) / aspect)))

func _process(_delta: float) -> void:
	if not is_instance_valid(hud) or not is_instance_valid(dungeon): return
	hud.world_target_visible = false
	hud.combat_center = hud.scene_rect.get_center()
	hud.enemy_head = Vector2.ZERO
	hud.enemy_feet = Vector2.ZERO
	var context: String = state.context_label()
	if hud.phase() != "combat" and context not in ["열쇠 줍기", "문 열기", "잠긴 문 조사", "상자 열기", "경비병과 대치"]: return
	var focus: Vector3 = dungeon.enemy.global_position
	match context:
		"열쇠 줍기": focus = dungeon.key_sprite.global_position
		"문 열기", "잠긴 문 조사": focus = dungeon.door.to_global(Vector3(1, 1.4, 0))
		"상자 열기": focus = dungeon.chest.global_position
	if dungeon.camera.is_position_behind(focus): return
	var point: Vector2 = dungeon.camera.unproject_position(focus)
	hud.combat_center = hud.scene_rect.position + point * hud.scene_rect.size / Vector2(viewport.size)
	if hud.phase() == "combat" or context == "경비병과 대치":
		var half_height: float = DungeonView.ArtAssets.ENEMY_WORLD_HEIGHT * 0.5
		hud.enemy_head = dungeon.camera.unproject_position(dungeon.enemy.global_position + Vector3.UP * half_height) * hud.scene_rect.size / Vector2(viewport.size)
		hud.enemy_feet = dungeon.camera.unproject_position(dungeon.enemy.global_position - Vector3.UP * half_height) * hud.scene_rect.size / Vector2(viewport.size)
	hud.world_target_visible = hud.scene_rect.grow(-32).has_point(hud.combat_center)

func _action(action: String) -> void:
	if action_pending: return
	if hud.handle_navigation(action): return
	if action == "sound":
		sound.muted = not sound.muted
		hud.muted = sound.muted
		hud.save_preferences()
		return
	if action == "layout":
		if OS.has_feature("web") or OS.has_feature("mobile"):
			state.log_message("기기를 회전하면 화면 배치가 바뀝니다.")
		else:
			get_window().size = Vector2i(1280, 760) if hud.portrait else Vector2i(480, 900)
		return
	if busy: return
	if action == "confirm_restart":
		if hud.panel != "reset": return
		action_pending = true
		await hud.dismiss_for_action()
		action_pending = false
		state = Rules.new()
		hud.state = state
		hud.sync_state()
		dungeon.free()
		dungeon = DungeonView.new()
		viewport.add_child(dungeon)
		dungeon.build(state)
		dungeon.counter_impact.connect(_counter_impact)
		_update_layout()
		_save()
		return
	if action.begins_with("hero_"):
		if hud.is_modal_open() and hud.panel != "party": return
		state.choose(int(action.trim_prefix("hero_")))
		_save()
		return
	if hud.is_modal_open():
		if not hud.allows_modal_action(action): return
		action_pending = true
		await hud.dismiss_for_action()
		action_pending = false
		if busy: return
	if action.begins_with("use_potion_"):
		var target := int(action.trim_prefix("use_potion_"))
		if target < 0 or target >= 4 or state.hp[target] <= 0 or state.hp[target] >= Rules.MAX_HP[target] or state.potions <= 0: return
		state.choose(target)
		action = "potion"
	var before_hp: Array = state.hp.duplicate()
	var event: Dictionary = {}
	match action:
		"forward": event = state.move(1)
		"back": event = state.move(-1)
		"turn_left": event = state.rotate(-1)
		"turn_right": event = state.rotate(1)
		"strafe_left": event = state.move(-1, true)
		"strafe_right": event = state.move(1, true)
		"interact": event = state.interact()
		"attack", "skill", "guard", "potion": event = state.act(action)
	if event.is_empty(): return
	busy = true
	hud.busy = true
	hud.begin_event(event, before_hp)
	_save()
	sound.play(event.get("kind", ""))
	if int(event.get("damage", 0)) > 0:
		hud.effect_style = ["bash", "arrows", "frost", "heal"][int(event.actor)] if event.kind == "skill" else "slash"
		hud.flash(Color("87c9df") if event.kind == "skill" else Color("e5b47f"), str(event.damage))
	elif int(event.get("heal", 0)) > 0:
		hud.effect_style = "heal"
		hud.flash(Color("81cba1"), "+%d" % event.heal)
	elif event.kind in ["key", "treasure"]:
		hud.effect_style = ""
		hud.flash(Color("dfbd75"))
	elif event.kind == "guard":
		hud.effect_style = "guard"
		hud.flash(Color("8cb5c1"))
	if event.kind == "key": hud.notify("청동 열쇠를 얻었습니다")
	elif event.kind == "door": hud.notify("봉인된 문이 열렸습니다")
	elif event.kind == "engage": hud.notify("경비병과 대치했습니다", 0)
	await dungeon.play(event)
	hud.end_event()
	busy = false
	hud.busy = false
	if event.has("actor") and not state.messages.is_empty(): hud.notify(state.messages.back(), 5 if event.kind == "guard" else 0)

func _counter_impact(target: int, damage: int) -> void:
	hud.counter_hit(target, damage)
	sound.play("attack")

func _unhandled_key_input(event: InputEvent) -> void:
	if not event is InputEventKey or not event.pressed or event.echo: return
	if action_pending:
		get_viewport().set_input_as_handled()
		return
	var mapping := {KEY_W: "forward", KEY_UP: "forward", KEY_S: "back", KEY_DOWN: "back",
		KEY_A: "turn_left", KEY_LEFT: "turn_left", KEY_D: "turn_right", KEY_RIGHT: "turn_right",
		KEY_Q: "strafe_left", KEY_E: "strafe_right", KEY_SPACE: "interact", KEY_ENTER: "interact",
		KEY_J: "attack", KEY_K: "skill", KEY_G: "guard", KEY_H: "potion", KEY_M: "map", KEY_F1: "help", KEY_F2: "layout",
		KEY_1: "hero_0", KEY_2: "hero_1", KEY_3: "hero_2", KEY_4: "hero_3"}
	if event.keycode == KEY_ESCAPE:
		hud.go_back()
		get_viewport().set_input_as_handled()
	elif mapping.has(event.keycode):
		_action(mapping[event.keycode])
		get_viewport().set_input_as_handled()

func _save() -> void:
	if not test_mode and not state.save_to(SAVE_PATH):
		state.log_message("저장 공간을 확인하세요. 진행을 저장하지 못했습니다.")

func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_GO_BACK_REQUEST and is_instance_valid(hud) and not action_pending: hud.go_back()
	if what in [NOTIFICATION_WM_CLOSE_REQUEST, NOTIFICATION_APPLICATION_FOCUS_OUT, NOTIFICATION_APPLICATION_PAUSED]:
		if state != null: _save()
		if is_instance_valid(hud): hud.cancel_gestures()

func _capture() -> void:
	hud.hover_enabled = false
	await get_tree().create_timer(1.5).timeout
	if not panel_preview.is_empty():
		hud.open_panel(panel_preview)
		await get_tree().create_timer(0.35).timeout
	if scenario == "spell":
		state.choose(2)
		_action("skill")
		await get_tree().create_timer(0.16).timeout
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	var error := image.save_png(capture_path)
	print("CAPTURE ", capture_path, " status=", error)
	while busy: await get_tree().create_timer(0.1).timeout
	get_tree().quit(0 if error == OK else 1)

func _run_walkthrough() -> void:
	await get_tree().create_timer(0.4).timeout
	for action in ["forward", "turn_right", "forward", "interact", "turn_left", "strafe_left", "forward", "interact", "forward", "forward", "interact"]:
		await _action(action)
	# Start at 4,9 -> 4,8 -> 5,8, take adjacent key -> 4,8 -> 4,7 -> door -> 4,6 -> fight.
	assert(state.phase == "combat", "Walkthrough must enter combat")
	for hero in [2, 0, 1, 2]:
		state.choose(hero)
		await _action("skill")
	assert(state.enemy_hp == 0, "Four skills should defeat the sentinel")
	while state.position.y > 2: await _action("forward")
	await _action("interact")
	assert(state.chest_open and state.gold == 100, "Reward must be granted exactly once")
	print("WALKTHROUGH PASS: key, door, combat, treasure, 100 gold")
	if not capture_path.is_empty(): await _capture()
	else:
		await get_tree().create_timer(1.2).timeout
		get_tree().quit()
