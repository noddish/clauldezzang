extends Control
## Chalk paths over the world; clipping and gestures retain the original map behavior.
const Rules = preload("res://scripts/dungeon_state.gd")
var state
var zoom := 1.0
var pan := Vector2.ZERO

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	clip_contents = true

func _draw() -> void:
	if state == null: return
	var cell := minf((size.x - 28) / 9.0, (size.y - 28) / 11.0) * zoom
	var origin := (size - Vector2(9, 11) * cell) / 2 + pan
	for y in range(11):
		for x in range(9):
			var p := Vector2i(x, y)
			if not state.is_floor(p): continue
			var known: bool = state.visited.has("%d,%d" % [x, y])
			var center := origin + (Vector2(x, y) + Vector2.ONE * 0.5) * cell
			var ink := Color("c7c8b8") if known else Color("566365")
			for direction in [Vector2i.RIGHT, Vector2i.DOWN]:
				if state.is_floor(p + direction):
					var end := center + Vector2(direction) * cell
					draw_line(center + Vector2(1, 1), end + Vector2(1, 1), Color("071115"), 4)
					draw_line(center, end, ink, 2)
			draw_rect(Rect2(center - Vector2.ONE * 2, Vector2.ONE * 4), ink)
			if p == Rules.KEY_POS and not state.has_key:
				draw_line(center - Vector2(4, 0), center + Vector2(4, 0), Color("e5d3a5"), 2)
				draw_line(center, center + Vector2(0, 5), Color("e5d3a5"), 2)
			if p == Rules.DOOR_POS and not state.door_open:
				draw_line(center - Vector2(6, 2), center + Vector2(6, 2), Color("e5d3a5"), 3)
			if p == Rules.ENEMY_POS and state.enemy_hp > 0:
				draw_line(center - Vector2(3, 5), center + Vector2(3, -5), Color("db7567"), 3)
			if p == Rules.CHEST_POS and not state.chest_open:
				draw_rect(Rect2(center - Vector2(4, 3), Vector2(8, 6)), Color("e5d3a5"), false, 2)
	var at := origin + (Vector2(state.position) + Vector2.ONE * 0.5) * cell
	var forward := Vector2(Rules.DIRECTIONS[state.facing])
	var side := forward.orthogonal()
	var points := PackedVector2Array([at + forward * cell * 0.48, at - forward * cell * 0.32 + side * cell * 0.34, at - forward * cell * 0.16, at - forward * cell * 0.32 - side * cell * 0.34])
	draw_colored_polygon(points, Color("f1e5c9"))
