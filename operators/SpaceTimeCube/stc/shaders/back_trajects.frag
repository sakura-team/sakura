precision highp float; //High precision, critical !!!
precision highp int; //High precision, critical !!!

in  vec4 geom_color;
out vec4 fragColor;

void main() {
  if (geom_color.w == 0.5)
      fragColor = vec4(geom_color.xyz, 1.0);
  else
      fragColor = vec4(1, 1, 1, geom_color.w);
}
