shader_type canvas_item;
render_mode unshaded;

void fragment() {
	vec4 image = texture(TEXTURE, UV);
	float edge = pow(length((UV - 0.5) * vec2(1.22, 1.0)), 1.7);
	vec3 color = (image.rgb - 0.5) * 1.045 + 0.5;
	color *= 1.0 - edge * 0.42;
	COLOR = vec4(color, image.a);
}
