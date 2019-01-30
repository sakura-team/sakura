precision highp float;
layout(lines_adjacency) in;                     //Input primitive
layout(triangle_strip, max_vertices = 6) out;   //Output primitive, with its number of vertices

in  vec4 v_color[];
in  vec4 vert_color[];
in  vec4 vert_cam_pos[];
out vec4 geom_color;

uniform float pixel_size;
uniform float cam_near;
uniform int nb_pixels;

void main() {

    //float thickness = gl_in[1].gl_Position.z*pixel_size*nb_pixels/camera_near;
    float d = gl_in[1].gl_Position.z - vert_cam_pos[1].z;
    float thickness = nb_pixels/1.5*pixel_size*d/cam_near;

    vec2 v1 = gl_in[2].gl_Position.xy - gl_in[1].gl_Position.xy;
    vec2 n1 = normalize(vec2(-v1.y, v1.x));

    vec2 v2 = gl_in[3].gl_Position.xy - gl_in[2].gl_Position.xy;
    vec2 n2 = normalize(vec2(-v2.y, v2.x));

    gl_Position = gl_in[1].gl_Position;
    gl_Position.xy += n1*thickness/2;
    geom_color = vert_color[1];
    EmitVertex();

    gl_Position = gl_in[1].gl_Position;
    gl_Position.xy -= n1*thickness/2;
    geom_color = vert_color[1];
    EmitVertex();

    gl_Position = gl_in[2].gl_Position;
    gl_Position.xy += n1*thickness/2;
    geom_color = vert_color[1];
    EmitVertex();

    gl_Position = gl_in[2].gl_Position;
    gl_Position.xy -= n1*thickness/2;
    geom_color = vert_color[1];
    EmitVertex();

    gl_Position = gl_in[2].gl_Position;
    gl_Position.xy += n2*thickness/2;
    geom_color = vert_color[1];
    EmitVertex();

    gl_Position = gl_in[2].gl_Position;
    gl_Position.xy -= n2*thickness/2;
    geom_color = vert_color[1];
    EmitVertex();

    EndPrimitive();
}
