precision highp float; //High precision, critical !!!
precision highp int; //High precision, critical !!!

in vec4 vert_color;
out vec4 fragColor;

void main() {
    vec4 tmp = vert_color;
    fragColor = vec4(1, 1, 1, 1);
}
