extends Node3D
signal counter_impact(target: int, damage: int)
## A tiny 3D stage with painted pixel textures and billboarded actors.

const Rules = preload("res://scripts/dungeon_state.gd")
const CELL := 2.6
const WALL_H := 3.6
const ArtAssets = preload("res://scripts/art_assets.gd")

var state
var camera: Camera3D
var camera_rig: Node3D
var door: Node3D
var enemy: Sprite3D
var chest: Sprite3D
var key_sprite: Sprite3D
var torch_lights: Array[OmniLight3D] = []
var flames: Array[Sprite3D] = []
var flame_frames: Array[AtlasTexture] = []
var time := 0.0
var animating := false
var enemy_base := Vector3.ZERO
var stone: ShaderMaterial
var floor_material: ShaderMaterial
var wood: ShaderMaterial
var stone_variants: Array[ShaderMaterial] = []
var dust: Array[MeshInstance3D] = []

static func sprite_region(column: int, row: int) -> AtlasTexture:
	return ArtAssets.sprite_region(column, row)

func _pixel_material(texture: Texture2D, tint: Color, world_aligned := false) -> ShaderMaterial:
	var mat := ShaderMaterial.new()
	mat.shader = preload("res://scripts/pixel_lighting.gdshader")
	mat.set_shader_parameter("albedo_tex", texture)
	mat.set_shader_parameter("tint", tint)
	mat.set_shader_parameter("world_aligned", world_aligned)
	return mat

func _material(column: int, row: int, tint: Color = Color.WHITE) -> ShaderMaterial:
	return _pixel_material(ArtAssets.material_texture(column, row), tint)

func _plain(color: Color, unshaded: bool = false) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.roughness = 0.9
	if unshaded: mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	return mat

func _crypt_material(column: int, row: int, tint := Color.WHITE) -> ShaderMaterial:
	return _pixel_material(ArtAssets.crypt_texture(column, row), tint, true)

static func prop_region(index: int) -> AtlasTexture:
	return ArtAssets.prop_region(index)

func _prop(index: int, pos: Vector3, height: float, yaw: float = 0, billboard: bool = false, parent: Node3D = null) -> Sprite3D:
	var sprite := Sprite3D.new()
	sprite.texture = prop_region(index)
	sprite.pixel_size = height / sprite.texture.get_height()
	sprite.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	sprite.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	sprite.alpha_scissor_threshold = 0.3
	sprite.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y if billboard else BaseMaterial3D.BILLBOARD_DISABLED
	sprite.modulate = Color(0.72, 0.77, 0.8) if index not in [2, 4, 6] else Color.WHITE
	sprite.position = pos
	sprite.rotation.y = yaw
	(parent if parent != null else self).add_child(sprite)
	return sprite

func _arch(pos: Vector3) -> void:
	for side in [-1, 1]:
		_box(self, pos + Vector3(side * 1.16, 1.08, 0), Vector3(0.25, 2.16, 0.33), stone)
		_box(self, pos + Vector3(side * 1.16, 0.13, 0), Vector3(0.38, 0.26, 0.43), stone)
		_box(self, pos + Vector3(side * 1.16, 2.13, 0), Vector3(0.38, 0.18, 0.43), stone)
	for i in range(9):
		var angle := float(i) * PI / 8
		var segment := _box(self, pos + Vector3(cos(angle) * 1.16, 2.15 + sin(angle) * 1.14, 0), Vector3(0.44, 0.28, 0.35), stone)
		segment.rotation.z = angle + PI / 2

func _set_dressing() -> void:
	_arch(grid_position(Vector2i(4, 8)) + Vector3(0, 0, 0.9))
	_arch(grid_position(Vector2i(4, 5)) + Vector3(0, 0, -0.9))
	_prop(0, grid_position(Vector2i(4, 7)) + Vector3(1.18, 2.05, -0.15), 1.85, -PI / 2)
	_prop(0, grid_position(Vector2i(4, 5)) + Vector3(-1.18, 2.1, 0), 1.7, PI / 2)
	_prop(1, grid_position(Vector2i(4, 8)) + Vector3(-0.7, 2.9, 0.85), 1.1)
	_prop(1, grid_position(Vector2i(4, 3)) + Vector3(1.0, 3.0, 0.8), 1.2)
	_prop(2, grid_position(Vector2i(4, 5)) + Vector3(1.16, 2.0, 0), 1.65, -PI / 2)
	_prop(2, grid_position(Vector2i(2, 8)) + Vector3(-1.17, 1.7, 0), 1.6, PI / 2)
	for p in [Vector2i(4, 5), Vector2i(2, 8)]:
		var light := OmniLight3D.new()
		light.position = grid_position(p) + Vector3(0.8 if p.x == 4 else -0.8, 1.7, 0)
		light.light_color = Color("4ab8b0")
		light.light_energy = 1.6
		light.omni_range = 3.6
		add_child(light)
		# Small near-floor bounce directly below the glowing window.
		_bounce_light(grid_position(p) + Vector3(0.82 if p.x == 4 else -0.82, 0.36, 0.2), Color("4ab8b0"), 1.0)
	_prop(3, grid_position(Vector2i(4, 7)) + Vector3(-0.83, 0.19, 0), 0.55, 0, true)
	_prop(3, grid_position(Vector2i(3, 3)) + Vector3(-0.65, 0.24, 0), 0.7, 0, true)
	_prop(4, grid_position(Vector2i(4, 7)) + Vector3(0.75, 0.33, 0.8), 0.7, 0, true)
	_prop(4, grid_position(Vector2i(4, 1)) + Vector3(-0.75, 0.35, 0.1), 0.7, 0, true)
	_prop(5, grid_position(Vector2i(6, 8)) + Vector3(0.65, 0.38, -0.4), 0.85, 0, true)
	_prop(5, grid_position(Vector2i(5, 3)) + Vector3(0.8, 0.4, 0.5), 0.9, 0, true)
	_prop(7, grid_position(Vector2i(4, 8)) + Vector3(-0.86, 0.12, -0.4), 0.45, 0, true)
	_prop(7, grid_position(Vector2i(4, 4)) + Vector3(0.8, 0.14, 0.2), 0.5, 0, true)
	_prop(6, Vector3(1.0, 1.65, 0.083), 0.62, 0, false, door)
	var mote_material := _plain(Color("b0b1a1"), true)
	for i in range(18):
		var mote := _box(self, Vector3.ZERO, Vector3.ONE * (0.009 if i % 2 else 0.014), mote_material)
		dust.append(mote)

func _actor_shadow() -> void:
	var gradient := Gradient.new()
	gradient.colors = PackedColorArray([Color(0, 0, 0, 0.65), Color(0, 0, 0, 0)])
	var texture := GradientTexture2D.new()
	texture.gradient = gradient
	texture.width = 64
	texture.height = 64
	texture.fill = GradientTexture2D.FILL_RADIAL
	texture.fill_from = Vector2(0.5, 0.5)
	texture.fill_to = Vector2(1, 0.5)
	var material := StandardMaterial3D.new()
	material.albedo_texture = texture
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	var mesh := PlaneMesh.new()
	mesh.size = Vector2(1.75, 1.1)
	var shadow := MeshInstance3D.new()
	shadow.mesh = mesh
	shadow.material_override = material
	shadow.position = grid_position(Rules.ENEMY_POS) + Vector3(0, 0.012, 0.03)
	add_child(shadow)

func _box(parent: Node3D, pos: Vector3, dimensions: Vector3, material: Material) -> MeshInstance3D:
	var instance := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = dimensions
	instance.mesh = mesh
	instance.material_override = material
	instance.position = pos
	parent.add_child(instance)
	return instance

func _sprite(parent: Node3D, pos: Vector3, column: int, row: int, world_height: float) -> Sprite3D:
	var actor := Sprite3D.new()
	actor.texture = sprite_region(column, row)
	actor.pixel_size = world_height / maxf(1.0, actor.texture.get_height())
	actor.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	actor.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	actor.no_depth_test = false
	actor.shaded = false
	actor.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	actor.alpha_scissor_threshold = 0.1
	actor.position = pos
	parent.add_child(actor)
	return actor

func grid_position(p: Vector2i) -> Vector3:
	return Vector3(p.x * CELL, 0, p.y * CELL)

func build(rules) -> void:
	state = rules
	for i in range(4):
		flame_frames.append(ArtAssets.torch_region(i))
	stone = _crypt_material(0, 0)
	for i in range(4):
		stone_variants.append(_crypt_material(1 if i == 2 else 0, 0, Color(0.90 + i * 0.025, 0.93 + i * 0.018, 0.95 + i * 0.01)))
	floor_material = _crypt_material(0, 1, Color(0.77, 0.81, 0.86))
	wood = _material(0, 1)
	var ceiling_material := _crypt_material(1, 1, Color(0.58, 0.63, 0.69))
	var trim := _crypt_material(0, 0, Color(0.6, 0.65, 0.7))
	var environment_node := WorldEnvironment.new()
	var environment := Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color("111a1b")
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color("9bb6d4")
	environment.ambient_light_energy = 0.65
	environment.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	environment.fog_enabled = true
	environment.fog_light_color = Color("14232e")
	environment.fog_density = 0.033
	environment_node.environment = environment
	add_child(environment_node)
	for y in range(Rules.MAP.size()):
		for x in range(Rules.MAP[0].length()):
			var p := Vector2i(x, y)
			if not state.is_floor(p): continue
			var at := grid_position(p)
			var floor_node := _box(self, at + Vector3(0, -0.09, 0), Vector3(CELL, 0.18, CELL), floor_material)
			floor_node.rotation.y = posmod(x * 3 + y, 4) * PI / 2
			_box(self, at + Vector3(0, WALL_H + 0.07, 0), Vector3(CELL, 0.14, CELL), ceiling_material)
			for direction in Rules.DIRECTIONS:
				if state.is_floor(p + direction): continue
				var normal := Vector3(direction.x, 0, direction.y)
				var dimensions := Vector3(0.16, WALL_H, CELL) if direction.x != 0 else Vector3(CELL, WALL_H, 0.16)
				_box(self, at + normal * (CELL / 2) + Vector3(0, WALL_H / 2, 0), dimensions, stone_variants[posmod(x * 13 + y * 7 + direction.x, 4)])
				var base_dim := Vector3(0.24, 0.22, CELL) if direction.x != 0 else Vector3(CELL, 0.22, 0.24)
				_box(self, at + normal * (CELL / 2 - 0.025) + Vector3(0, 0.11, 0), base_dim, trim)
				_box(self, at + normal * (CELL / 2 - 0.025) + Vector3(0, 3.38, 0), base_dim, trim)
	_build_door()
	enemy_base = grid_position(Rules.ENEMY_POS) + Vector3(0, 1.18, 0)
	enemy = _sprite(self, enemy_base, 0, 1, ArtAssets.ENEMY_WORLD_HEIGHT)
	_actor_shadow()
	chest = _sprite(self, grid_position(Rules.CHEST_POS) + Vector3(0, 0.56, 0), 0, 3, ArtAssets.CHEST_WORLD_HEIGHT)
	key_sprite = _sprite(self, grid_position(Rules.KEY_POS) + Vector3(0, 1.05, 0), 3, 3, ArtAssets.KEY_WORLD_HEIGHT)
	var altar := _material(1, 1)
	_box(self, grid_position(Vector2i(4, 1)) + Vector3(0, 1.8, -1.16), Vector3(2.1, 2.8, 0.1), altar)
	_box(self, grid_position(Rules.KEY_POS) + Vector3(0, 0.35, 0), Vector3(0.8, 0.7, 0.8), stone)
	for spec in [[4, 8, -1], [4, 7, 1], [4, 5, -1], [3, 3, -1], [5, 3, 1], [4, 1, 1]]:
		_add_torch(grid_position(Vector2i(spec[0], spec[1])) + Vector3(float(spec[2]) * 1.08, 1.9, 0))
	for p in [Vector2i(3, 4), Vector2i(5, 4), Vector2i(3, 3), Vector2i(5, 3)]:
		var at := grid_position(p) + Vector3(0.8 if p.x == 3 else -0.8, 0, 0)
		_box(self, at + Vector3(0, 1.8, 0), Vector3(0.36, 3.6, 0.36), stone)
		_box(self, at + Vector3(0, 0.15, 0), Vector3(0.58, 0.3, 0.58), trim)
		_box(self, at + Vector3(0, 3.1, 0), Vector3(0.58, 0.3, 0.58), trim)
	_set_dressing()
	camera_rig = Node3D.new()
	add_child(camera_rig)
	camera = Camera3D.new()
	camera.fov = 65
	camera.near = 0.05
	camera.far = 45
	camera.position.y = 1.56
	camera_rig.add_child(camera)
	camera.current = true
	var lantern := OmniLight3D.new()
	lantern.light_color = Color("cad2d0")
	lantern.light_energy = 0.28
	lantern.omni_range = 4.0
	lantern.position = Vector3(0, 1.7, -0.25)
	camera_rig.add_child(lantern)
	sync_immediate()

func _build_door() -> void:
	var at := grid_position(Rules.DOOR_POS) + Vector3(0, 0, CELL / 2 - 0.05)
	_box(self, at + Vector3(-1.15, 1.8, 0), Vector3(0.32, 3.6, 0.5), stone)
	_box(self, at + Vector3(1.15, 1.8, 0), Vector3(0.32, 3.6, 0.5), stone)
	_box(self, at + Vector3(0, 3.2, 0), Vector3(2.6, 0.8, 0.5), stone)
	door = Node3D.new()
	door.position = at + Vector3(-1, 0, 0)
	add_child(door)
	_box(door, Vector3(1, 1.4, 0), Vector3(2, 2.8, 0.13), wood)
	_box(door, Vector3(1.72, 1.35, 0.1), Vector3(0.12, 0.25, 0.08), _plain(Color("aa854d")))

func _bounce_light(at: Vector3, color: Color, energy: float) -> void:
	var light := OmniLight3D.new()
	light.position = at
	light.light_color = color
	light.light_energy = energy
	light.omni_range = 1.4
	add_child(light)

func _add_torch(at: Vector3) -> void:
	var glow := OmniLight3D.new()
	glow.position = at + Vector3(0, 0.15, 0)
	glow.light_color = Color("ff9f47")
	glow.light_energy = 2.6
	glow.omni_range = 3.6
	add_child(glow)
	torch_lights.append(glow)
	_bounce_light(Vector3(at.x, 0.36, at.z + 0.15), Color("ff9f47"), 0.8)
	var flame := Sprite3D.new()
	flame.texture = flame_frames[0]
	flame.pixel_size = ArtAssets.TORCH_WORLD_HEIGHT / maxf(1.0, flame.texture.get_height())
	flame.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	flame.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	flame.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	flame.position = at - Vector3(0, 0.23, 0)
	add_child(flame)
	flames.append(flame)

func sync_immediate() -> void:
	camera_rig.position = grid_position(state.position)
	camera_rig.rotation.y = -float(state.facing) * PI / 2
	door.rotation.y = -1.48 if state.door_open else 0.0
	enemy.visible = state.enemy_hp > 0
	chest.texture = sprite_region(1 if state.chest_open else 0, 3)
	key_sprite.visible = not state.has_key

func play(event: Dictionary) -> void:
	animating = true
	var kind: String = event.get("kind", "")
	if kind in ["move", "turn", "engage"]:
		var tween := create_tween().set_parallel(true)
		tween.tween_property(camera_rig, "position", grid_position(state.position), 0.25).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		var current_yaw := camera_rig.rotation.y
		var target := current_yaw + wrapf(-float(state.facing) * PI / 2 - current_yaw, -PI, PI)
		tween.tween_property(camera_rig, "rotation:y", target, 0.24).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		if kind == "move":
			var bob := create_tween()
			bob.tween_property(camera, "position:y", 1.61, 0.11)
			bob.tween_property(camera, "position:y", 1.56, 0.14)
		await tween.finished
	elif kind == "door":
		var tween := create_tween()
		tween.tween_property(door, "rotation:y", -1.48, 0.75).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
		await tween.finished
	elif kind == "key":
		key_sprite.visible = false
	elif kind == "treasure":
		chest.texture = sprite_region(1, 3)
	elif kind in ["attack", "skill", "guard", "potion"]:
		if int(event.get("damage", 0)) > 0:
			enemy.texture = sprite_region(3, 1)
			enemy.modulate = Color(1.5, 0.65, 0.55)
			var hit := create_tween()
			hit.tween_property(enemy, "position:z", enemy_base.z - 0.13, 0.09)
			hit.tween_property(enemy, "position:z", enemy_base.z, 0.14)
			await hit.finished
			enemy.modulate = Color.WHITE
		if event.get("killed", false):
			enemy.texture = sprite_region(2, 2)
			await get_tree().create_timer(0.2).timeout
			enemy.texture = sprite_region(3, 2)
			await get_tree().create_timer(0.5).timeout
			enemy.visible = false
		elif int(event.get("enemy_damage", 0)) > 0:
			await get_tree().create_timer(0.18).timeout
			enemy.texture = sprite_region(1, 1)
			await get_tree().create_timer(0.19).timeout
			enemy.texture = sprite_region(2, 1)
			var strike := create_tween()
			strike.tween_property(enemy, "position:z", enemy_base.z + 0.4, 0.1)
			await strike.finished
			counter_impact.emit(int(event.target), int(event.enemy_damage))
			var shake := create_tween()
			shake.tween_property(camera, "h_offset", 0.035, 0.035)
			shake.tween_property(camera, "h_offset", -0.025, 0.05)
			shake.tween_property(camera, "h_offset", 0.0, 0.07)
			var retreat := create_tween()
			retreat.tween_property(enemy, "position:z", enemy_base.z, 0.21).set_trans(Tween.TRANS_SINE)
			await retreat.finished
			enemy.texture = sprite_region(0, 1)
		else:
			await get_tree().create_timer(0.25).timeout
	animating = false

func _process(delta: float) -> void:
	time += delta
	for i in range(torch_lights.size()):
		var pulse := sin(time * 9.0 + i * 2.0) * 0.08 + sin(time * 17.0 + i) * 0.045
		torch_lights[i].light_energy = 2.6 + pulse
		flames[i].texture = flame_frames[(int(time * 7) + i) % 4]
	if is_instance_valid(enemy) and enemy.visible and not animating:
		enemy.position.y = enemy_base.y + sin(time * 2.4) * 0.016
		enemy.texture = sprite_region(0, 1)
		enemy.scale.y = 1.0 + sin(time * 2.4) * 0.004
	if is_instance_valid(key_sprite) and key_sprite.visible:
		key_sprite.position.y = 1.05 + sin(time * 2.3) * 0.055
	if is_instance_valid(camera_rig):
		for i in range(dust.size()):
			var local := Vector3(sin(i * 13.1 + time * 0.09) * 1.05, 0.5 + fposmod(i * 0.37 + time * 0.035, 2.5), -1.4 - fposmod(i * 0.73, 4.8))
			dust[i].position = camera_rig.position + local.rotated(Vector3.UP, camera_rig.rotation.y)
