precision highp float;

uniform mat4 projection_mat;
uniform mat4 modelview_mat;

in vec4 in_vertex;

void main() {
    vec4 v = vec4(in_vertex[1]/2000, 0, in_vertex[2]/2000, 1.0);
    gl_Position = projection_mat * modelview_mat * v;
}
