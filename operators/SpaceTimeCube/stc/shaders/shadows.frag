precision highp float; //High precision, critical !!!
precision highp int; //High precision, critical !!!

in  vec4 vert_color;
out vec4 fragColor;

void main() {
    fragColor = vec4(0, 0, 0, vert_color.w);
}
