precision highp float;

uniform mat4 projection_mat;
uniform mat4 modelview_mat;
uniform vec4 maxs;
uniform vec4 mins;

in  vec3 in_vertex;
in  vec2 in_text_coords;
out vec2 v_text_coords;

void main() {
    vec2 size = maxs.yz - mins.yz;
    vec4 v = vec4(in_vertex, 1.0);
    if (size.x > size.y)
        v.z *= size.y/size.x;
    else
        v.x *= size.x/size.y;
    v.y -= .5;
    gl_Position = projection_mat * modelview_mat * v;

    v_text_coords = in_text_coords;
}
