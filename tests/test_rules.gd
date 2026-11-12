extends SceneTree
const Rules = preload("res://scripts/dungeon_state.gd")
var checks := 0
var failures := 0

func check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures += 1
		printerr("FAIL: ", label)

func _initialize() -> void:
	var s = Rules.new()
	check(s.position == Vector2i(4, 9), "Entrance position")
	s.move(-1)
	check(s.position == Vector2i(4, 9), "Wall blocks movement")
	for i in range(4): s.rotate(1)
	check(s.facing == 0, "Rotation wraps")
	s.position = Vector2i(4, 7)
	s.move(1)
	check(s.position == Vector2i(4, 7), "Closed door blocks entry")
	s.interact()
	check(not s.door_open, "Door requires key")
	s.position = Vector2i(5, 8)
	s.facing = 1
	s.interact()
	check(s.has_key, "Collect adjacent key")
	s.position = Vector2i(4, 7)
	s.facing = 0
	s.interact()
	check(s.door_open, "Key opens door")
	s.move(1)
	check(s.position == Vector2i(4, 6), "Enter opened doorway")
	s.move(1)
	check(s.phase == "combat" and s.position == Vector2i(4, 6), "Enemy blocks tile and starts combat")
	s.rotate(1)
	s.move(-1)
	check(s.facing == 0 and s.position == Vector2i(4, 6), "Combat locks traversal")
	s.choose(2)
	var event = s.act("skill")
	check(event.damage == 28 and s.mp[2] == 20, "Mage skill damage and mana")
	check(s.hp[0] == Rules.MAX_HP[0] - 9, "Enemy counterattack")
	var before: int = s.enemy_hp
	s.mp[2] = 0
	s.act("skill")
	check(s.enemy_hp == before and s.turn == 1, "Insufficient mana does not consume turn")
	s.choose(0)
	var potions_before: int = s.potions
	s.act("potion")
	check(s.potions == potions_before - 1 and s.hp[0] == Rules.MAX_HP[0], "Potion heals selected hero")
	s.choose(3)
	s.hp[2] = 10
	s.act("skill")
	check(s.hp[2] > 10 and s.mp[3] == 19, "Priest heals living party")
	s.choose(1)
	var guarded = s.act("guard")
	check(guarded.enemy_damage == 3 and guarded.target == 1, "Guard draws reduced counterattack")
	s.enemy_hp = 1
	var victory = s.act("attack")
	check(victory.killed and s.enemy_hp == 0 and s.phase == "explore", "Victory exits combat")
	check(s.gold == 20 and victory.enemy_damage == 0, "No retaliation after lethal hit")
	s.act("attack")
	check(s.gold == 20, "Kill reward cannot repeat")
	s.position = Vector2i(4, 2)
	s.facing = 0
	s._reveal()
	s.interact()
	check(s.chest_open and s.phase == "won" and s.gold == 100, "Chest completes expedition")
	var loot_potions: int = s.potions
	s.interact()
	check(s.gold == 100 and s.potions == loot_potions, "Chest reward cannot repeat")
	var save_path := "user://rules-test-save.json"
	check(s.save_to(save_path), "Atomic save succeeds")
	var restored = Rules.new()
	check(restored.load_from(save_path), "Valid save loads")
	check(restored.snapshot() == s.snapshot(), "Save round trip retains game state")
	DirAccess.remove_absolute(save_path)
	var invalid := FileAccess.open(save_path, FileAccess.WRITE)
	invalid.store_string('{"version":1,"position":[4,2],"hp":[],"mp":[]}')
	invalid.close()
	check(not restored.load_from(save_path), "Malformed save is rejected")
	DirAccess.remove_absolute(save_path)
	var dying = Rules.new()
	dying.phase = "combat"
	dying.hp = [1, 0, 0, 0]
	dying.selected = 0
	dying.act("attack")
	check(dying.phase == "defeat", "Party defeat is recognized")
	var old_hp: int = dying.enemy_hp
	dying.act("attack")
	check(dying.enemy_hp == old_hp, "No actions after defeat")
	var fresh = Rules.new()
	fresh.act("potion")
	check(fresh.potions == 2, "Full-health potion is not consumed")
	fresh.hp[1] = 0
	fresh.choose(1)
	check(fresh.selected == 0, "Cannot select defeated hero")
	print("RULES: %d checks, %d failures" % [checks, failures])
	quit(1 if failures else 0)
