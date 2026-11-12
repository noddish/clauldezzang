shader_type spatial;
render_mode specular_disabled;

// Authored material shades stay sharp. Only local light contribution is stepped.
uniform sampler2D albedo_tex : source_color, filter_nearest, repeat_enable;
uniform vec4 tint : source_color = vec4(1.0);
uniform bool world_aligned = false;
uniform float tile_world_size = 2.6;
varying vec3 world_position;
varying vec3 world_normal;

void vertex() {
	world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	world_normal = normalize(MODEL_NORMAL_MATRIX * NORMAL);
}

void fragment() {
	vec2 surface_uv = UV;
	if (world_aligned) {
		vec3 axis = abs(world_normal);
		if (axis.y > axis.x && axis.y > axis.z) {
			surface_uv = world_position.xz / tile_world_size;
		} else if (axis.x > axis.z) {
			surface_uv = vec2(world_position.z, -world_position.y) / tile_world_size;
		} else {
			surface_uv = vec2(world_position.x, -world_position.y) / tile_world_size;
		}
	}
	ALBEDO = texture(albedo_tex, surface_uv).rgb * tint.rgb;
	ROUGHNESS = 1.0;
}

void light() {
	float diffuse = max(dot(NORMAL, LIGHT), 0.0) * ATTENUATION;
	// More resolution in dark reflections; four steps, no smooth colored halo.
	float stepped = floor(sqrt(clamp(diffuse, 0.0, 1.0)) * 4.0) / 4.0;
	stepped *= stepped;
	DIFFUSE_LIGHT += LIGHT_COLOR * stepped / PI;
}
