precision highp float; //High precision, critical !!!
precision highp int; //High precision, critical !!!

in  vec4 vert_color;
out vec4 fragColor;

void main() {
  if (vert_color.w == 0)
      gl_FragDepth = 2;
  else
      gl_FragDepth = gl_FragCoord.z;

  if (vert_color.w != 0.5)
      fragColor = vert_color;
  else
      fragColor = vec4(vert_color.xyz, 1.0);
}
