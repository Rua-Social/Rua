/* Rec.709 legality check on the composited colours.
   Run after changing colours or blueAlphaCap in params.js.   */

const P = require('./params.js');

const KR = 0.2126, KG = 0.7152, KB = 0.0722;
const WHITE = [255, 255, 255];

function analyse(rgb) {
  const [r, g, b] = rgb.map(v => v / 255);
  const y  = KR * r + KG * g + KB * b;
  const cb = (b - y) / (2 * (1 - KB));
  const cr = (r - y) / (2 * (1 - KR));
  return {
    y8:  16 + 219 * y,
    cb8: 128 + 224 * cb,
    cr8: 128 + 224 * cr,
    exc: (Math.max(Math.abs(cb), Math.abs(cr)) / 0.5) * 100,
  };
}

const over = (base, col, a) => base.map((v, i) => v * (1 - a) + col[i] * a);
const hex  = c => '#' + c.map(v => Math.round(v).toString(16).padStart(2, '0')
                                   .toUpperCase()).join('');

console.log('\nRec.709 legality - composited over white base');
console.log('legal luma 16-235, legal chroma 16-240\n');
console.log('COLOUR            ALPHA  COMPOSITE    Y      Cb     Cr    CHROMA%  VERDICT');
console.log('-'.repeat(82));

let worst = 0;

for (const b of P.blobs) {
  const rgb = P.colours[b.colour].split(',').map(s => +s.trim());
  let a = b.alpha;
  if (b.colour === 'blue') a = Math.min(a, P.blueAlphaCap);

  const comp = over(WHITE, rgb, a);
  const m = analyse(comp);
  worst = Math.max(worst, m.exc);

  const illegal = m.y8 < 16 || m.y8 > 235 ||
                  m.cb8 < 16 || m.cb8 > 240 ||
                  m.cr8 < 16 || m.cr8 > 240;

  let verdict = 'ok';
  if (illegal) verdict = 'ILLEGAL';
  else if (m.exc > 90) verdict = 'TIGHT - overshoot risk';
  else if (m.exc > 85) verdict = 'watch';

  console.log(
    `${b.colour.padEnd(16)} ${a.toFixed(2).padStart(5)}  ${hex(comp)}  ` +
    `${m.y8.toFixed(0).padStart(5)} ${m.cb8.toFixed(0).padStart(6)} ` +
    `${m.cr8.toFixed(0).padStart(6)} ${m.exc.toFixed(1).padStart(8)}%  ${verdict}`
  );
}

console.log('-'.repeat(82));
console.log(`\nWorst chroma excursion: ${worst.toFixed(1)}%`);
if (worst > 90) {
  console.log('RISK. Encoder ringing on hard edges can push this illegal.');
  console.log('     Lower blueAlphaCap in params.js and re-run.');
} else {
  console.log('Headroom is fine. Safe to deliver.');
}
console.log('');
