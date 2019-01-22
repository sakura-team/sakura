precision highp float; //High precision, critical !!!
precision highp int; //High precision, critical !!!

uniform sampler2D floor_texture;

in  vec2    v_text_coords;
out vec4    fragColor;

void main() {
    fragColor = texture(floor_texture, v_text_coords);
}
