extends Node
## Small original procedural sound cues. No third-party sound assets.
var muted := false
var cache: Dictionary = {}

func _stream(kind: String) -> AudioStreamWAV:
	if cache.has(kind): return cache[kind]
	var duration := 0.16
	if kind in ["door", "treasure"]: duration = 0.7
	elif kind in ["skill", "key", "potion"]: duration = 0.42
	var rate := 22050
	var samples := int(rate * duration)
	var data := PackedByteArray()
	data.resize(samples * 2)
	var rng := RandomNumberGenerator.new()
	rng.seed = kind.hash()
	for i in range(samples):
		var t := float(i) / rate
		var progress := float(i) / samples
		var envelope := pow(1.0 - progress, 2.0) * minf(t * 160, 1.0)
		var sample := 0.0
		if kind in ["move", "blocked"]:
			sample = (sin(TAU * 90 * t) * 0.5 + rng.randf_range(-1, 1) * 0.5) * envelope * 0.22
		elif kind == "door":
			sample = (sin(TAU * (110 * t + 50 * t * t)) * 0.4 + rng.randf_range(-1, 1) * 0.15) * envelope * 0.18
		elif kind in ["attack", "guard", "engage"]:
			sample = (sin(TAU * 440 * t) * 0.3 + sin(TAU * 721 * t) * 0.2 + rng.randf_range(-1, 1) * 0.6) * envelope * 0.25
		else:
			var frequency := 523.25 if progress < 0.33 else (659.25 if progress < 0.66 else 783.99)
			sample = (sin(TAU * frequency * t) + sin(TAU * frequency * 2 * t) * 0.2) * envelope * 0.13
		data.encode_s16(i * 2, clampi(int(sample * 32767), -32768, 32767))
	var stream := AudioStreamWAV.new()
	stream.format = AudioStreamWAV.FORMAT_16_BITS
	stream.mix_rate = rate
	stream.data = data
	cache[kind] = stream
	return stream

func play(kind: String) -> void:
	if muted or kind in ["", "inspect", "turn"]: return
	var player := AudioStreamPlayer.new()
	player.stream = _stream(kind)
	player.volume_db = -7
	add_child(player)
	player.finished.connect(player.queue_free)
	player.play()
