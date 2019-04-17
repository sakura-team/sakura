precision highp float; //High precision, critical !!!
precision highp int; //High precision, critical !!!

in vec3 v_color;

out vec4 fragColor;

void main() {
    fragColor = vec4(v_color, 1);
}
