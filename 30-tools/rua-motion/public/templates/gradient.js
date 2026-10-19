// Single-pass float compositing and triangular dither, retained from the reference engine.
export function gradient(cv, brand, P) {
cv.width=P.width; cv.height=P.height;
const rgb = hex => [1,3,5].map(i=>parseInt(hex.slice(i,i+2),16)/255);
const gl = cv.getContext('webgl2', {
  alpha: false,
  antialias: false,
  depth: false,
  premultipliedAlpha: false,
  preserveDrawingBuffer: true,   
  colorSpace: 'srgb',
});
if (!gl) throw new Error('WebGL2 unavailable');

const MAXB = 16;

const VS = `#version 300 es
in vec2 p;
void main() { gl_Position = vec4(p, 0.0, 1.0); }`;

const FS = `#version 300 es
precision highp float;
out vec4 fragColour;

uniform vec3 uBase;
uniform vec2  uRes;
uniform float uT;          
uniform int   uCount;
uniform float uDither;     


uniform vec3  uCol[${MAXB}];
uniform float uAlpha[${MAXB}];
uniform vec2  uC[${MAXB}];
uniform float uRadius[${MAXB}];
uniform vec2  uAmp[${MAXB}];
uniform float uCycles[${MAXB}];
uniform float uPhase[${MAXB}];
uniform float uScaleAmp[${MAXB}];

const float TAU = 6.283185307179586;


float falloff(float t) {
  if (t >= 0.82) return 0.0;
  if (t < 0.28) return mix(1.0,  0.62, t / 0.28);
  if (t < 0.50) return mix(0.62, 0.24, (t - 0.28) / 0.22);
  if (t < 0.68) return mix(0.24, 0.06, (t - 0.50) / 0.18);
  return               mix(0.06, 0.0,  (t - 0.68) / 0.14);
}


float ign(vec2 v) {
  return fract(52.9829189 * fract(dot(v, vec2(0.06711056, 0.00583715))));
}


float triDither(float u) {
  float v = 2.0 * u - 1.0;
  return sign(v) * (1.0 - sqrt(max(0.0, 1.0 - abs(v))));
}

void main() {
  vec2 frag = gl_FragCoord.xy;
  
  vec2 px = vec2(frag.x, uRes.y - frag.y);

  float W = uRes.x;                 
  vec3 c = uBase;               

  for (int i = 0; i < ${MAXB}; i++) {
    if (i >= uCount) break;

    float ang = TAU * uCycles[i] * uT + uPhase[i];
    vec2  d   = vec2(uAmp[i].x * sin(ang), uAmp[i].y * cos(ang)) * W;
    float sc  = 1.0 + uScaleAmp[i] * sin(ang + 1.1);

    
    vec2  centre = uC[i] * W + d;

    
    float r = uRadius[i] * W * sc * 1.41421356;

    float t = distance(px, centre) / r;
    float a = uAlpha[i] * falloff(t);

    c = c * (1.0 - a) + uCol[i] * a;   
  }

  
  
  if (uDither > 0.0) {
    c += triDither(ign(frag)) * uDither / 255.0;
  }

  fragColour = vec4(c, 1.0);
}`;

function compile(type, src) {
  const s = gl.createShader(type);
  gl.shaderSource(s, src);
  gl.compileShader(s);
  if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
    throw new Error(gl.getShaderInfoLog(s));
  }
  return s;
}

const prog = gl.createProgram();
gl.attachShader(prog, compile(gl.VERTEX_SHADER, VS));
gl.attachShader(prog, compile(gl.FRAGMENT_SHADER, FS));
gl.linkProgram(prog);
if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
  throw new Error(gl.getProgramInfoLog(prog));
}
gl.useProgram(prog);

const vao = gl.createVertexArray();
gl.bindVertexArray(vao);
const buf = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, buf);
gl.bufferData(gl.ARRAY_BUFFER,
  new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
const loc = gl.getAttribLocation(prog, 'p');
gl.enableVertexAttribArray(loc);
gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

const U = n => gl.getUniformLocation(prog, n);


const blobs = P.blobs.slice(0, MAXB);
const col = [], alpha = [], cc = [], rad = [], amp = [], cyc = [], pha = [], sca = [];
for (const b of blobs) {
  const components = rgb(brand.colors[b.role]);
  let a = b.alpha;
  a = Math.min(a, b.alphaCap ?? 1);
  col.push(...components);
  alpha.push(a);
  cc.push(b.cx, b.cy);
  rad.push(b.radius);
  amp.push(b.ampX, b.ampY);
  cyc.push(b.cycles);
  pha.push(b.phase);
  sca.push(b.scaleAmp);
}

gl.viewport(0, 0, P.width, P.height);
gl.uniform3fv(U('uBase'), rgb(brand.colors.surface));
gl.uniform2f(U('uRes'), P.width, P.height);
gl.uniform1i(U('uCount'), blobs.length);
gl.uniform1f(U('uDither'), P.dither === undefined ? 1.0 : P.dither);
gl.uniform3fv(U('uCol'), new Float32Array(col));
gl.uniform1fv(U('uAlpha'), new Float32Array(alpha));
gl.uniform2fv(U('uC'), new Float32Array(cc));
gl.uniform1fv(U('uRadius'), new Float32Array(rad));
gl.uniform2fv(U('uAmp'), new Float32Array(amp));
gl.uniform1fv(U('uCycles'), new Float32Array(cyc));
gl.uniform1fv(U('uPhase'), new Float32Array(pha));
gl.uniform1fv(U('uScaleAmp'), new Float32Array(sca));

const uT = U('uT');


function drawFrame(i) {
  const total = Math.round(P.fps * P.duration);
  gl.uniform1f(uT, (i % total) / total);
  gl.drawArrays(gl.TRIANGLES, 0, 3);
  gl.finish();
}



return {seek: t=>drawFrame(Math.round(t*P.fps)), dispose:()=>{gl.deleteBuffer(buf);gl.deleteVertexArray(vao);gl.deleteProgram(prog);gl.getExtension('WEBGL_lose_context')?.loseContext();}};
}
