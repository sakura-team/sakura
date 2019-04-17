precision highp float;

uniform mat4 projection_mat;
uniform mat4 modelview_mat;

in vec3 in_vertex;
in vec3 in_color;

uniform vec4 maxs;
uniform vec4 mins;
uniform float cube_height;

out vec3 v_color;

void main() {
    vec2 size = maxs.yz - mins.yz;
    vec4 v = vec4(in_vertex, 1.0);
    v.y = v.y*cube_height - cube_height/2;
    if (size.x > size.y)
        v.z *= size.y/size.x;
    else
        v.x *= size.x/size.y;
    gl_Position = projection_mat * modelview_mat * v;
    v_color = in_color;
}
