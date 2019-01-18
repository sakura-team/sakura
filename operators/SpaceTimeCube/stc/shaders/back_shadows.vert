precision highp float;

uniform mat4 projection_mat;
uniform mat4 modelview_mat;
uniform vec3 cam_pos;

in  vec4 in_vertex;
in  vec4 in_color;
out vec4 vert_color;
out vec4 vert_cam_pos;

uniform vec4 maxs;
uniform vec4 mins;

void main() {
    vec3 size = maxs.yzw - mins.yzw;
    vec3 midl = (maxs.yzw - mins.yzw)/2.0;
    float msize = max(size.x, size.y);
    vec4 v = vec4(  (in_vertex[1]- mins.y)/msize - midl.x/size.x,
                    0,
                    -((in_vertex[2]-mins.z)/msize - midl.y/size.y),
                    1.0);
    gl_Position   = projection_mat * modelview_mat * v;
    vert_cam_pos  = projection_mat * modelview_mat * vec4(cam_pos, 1);
    vert_color = in_color;
}
