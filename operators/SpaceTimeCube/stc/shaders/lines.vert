precision highp float;

uniform mat4 projection_mat;
uniform mat4 modelview_mat;

in vec3 in_vertex;
in vec2 in_text_coords;

uniform vec4 maxs;
uniform vec4 mins;
uniform float cube_height;

void main() {
    /*vec2 size = maxs.yz - mins.yz;
    vec4 v = vec4(in_vertex, 1.0);
    v.y *= cube_height;
    if (size.x > size.y)
        v.z *= size.y/size.x;
    else
        v.x *= size.x/size.y;
    v.y -= cube_height/2;
    gl_Position = projection_mat * modelview_mat * v;
    */

    vec2 midl = (maxs.yz + mins.yz)/2.0;
    vec2 size = maxs.yz - mins.yz;
    float msize = max(size.x, size.y);

    vec4 v = vec4((in_vertex.y - midl.x)/msize,
                  (in_vertex[0]- mins.x)/(maxs.x - mins.x)*cube_height -cube_height/2.0,
                  -(in_vertex.z - midl.y)/msize,
                  1.0);
    gl_Position = projection_mat * modelview_mat * v;

}
