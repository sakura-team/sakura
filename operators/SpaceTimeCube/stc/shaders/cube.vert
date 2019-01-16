precision highp float;

uniform mat4 projection_mat;
uniform mat4 modelview_mat;

in vec3 in_vertex;

void main() {
    gl_Position = projection_mat * modelview_mat * vec4(in_vertex, 1.0);
}
