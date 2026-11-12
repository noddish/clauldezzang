extends RefCounted
## Individually authored pixel-art PNGs, exposed through the existing atlas API.
## The scene and HUD retain their established indices and layout rectangles.

const ROOT := "res://assets/pixel16/"
const SPRITE_FILES = [
	["portraits/warrior.png", "portraits/ranger.png", "portraits/mage.png", "portraits/priest.png"],
	["enemy/idle.png", "enemy/anticipation.png", "enemy/strike.png", "enemy/hit.png"],
	["enemy/idle_alt.png", "enemy/anticipation_alt.png", "enemy/dying.png", "enemy/dead.png"],
	["items/chest_closed.png", "items/chest_open.png", "items/potion.png", "items/key.png"],
]
const PROP_FILES = ["banner", "cobweb", "window", "bones", "candles", "urn", "medallion", "rubble"]
const ICON_FILES = ["attack", "bash", "arrows", "frost", "heal", "guard", "potion", "compass"]
const MATERIAL_FILES = ["wall_plain", "floor", "door", "altar"]
const CRYPT_FILES = ["wall_plain", "wall_runes", "floor", "vault"]

# Legacy world quad dimensions, independent of the new source resolution.
const ENEMY_WORLD_HEIGHT := 313.0 * 0.0075
const CHEST_WORLD_HEIGHT := 313.0 * 0.0039
const KEY_WORLD_HEIGHT := 313.0 * 0.0028
const TORCH_WORLD_HEIGHT := 724.0 * 0.0015

static var texture_cache: Dictionary = {}
static var region_cache: Dictionary = {}

static func _texture(relative_path: String) -> Texture2D:
	if texture_cache.has(relative_path): return texture_cache[relative_path]
	var texture: Texture2D = load(ROOT + relative_path) as Texture2D
	if texture == null:
		push_error("Missing individual pixel-art texture: " + ROOT + relative_path)
		return null
	texture_cache[relative_path] = texture
	return texture

static func _full_region(relative_path: String) -> AtlasTexture:
	if region_cache.has(relative_path): return region_cache[relative_path]
	var texture := _texture(relative_path)
	var region := AtlasTexture.new()
	if texture == null: return region
	region.atlas = texture
	region.region = Rect2(Vector2.ZERO, texture.get_size())
	region.filter_clip = true
	region_cache[relative_path] = region
	return region

static func sprite_region(column: int, row: int) -> AtlasTexture:
	return _full_region(SPRITE_FILES[row][column])

static func prop_region(index: int) -> AtlasTexture:
	return _full_region("props/%s.png" % PROP_FILES[index])

static func icon_region(index: int) -> AtlasTexture:
	return _full_region("icons/%s.png" % ICON_FILES[index])

static func torch_region(index: int) -> AtlasTexture:
	return _full_region("torches/torch_%d.png" % index)

static func material_texture(column: int, row: int) -> Texture2D:
	return _texture("environment/%s.png" % MATERIAL_FILES[row * 2 + column])

static func crypt_texture(column: int, row: int) -> Texture2D:
	return _texture("environment/%s.png" % CRYPT_FILES[row * 2 + column])
