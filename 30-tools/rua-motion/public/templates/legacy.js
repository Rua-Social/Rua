// Ported from the reference graphics engine; geometry preserved at 1920×1080.
// Values arrive through brand roles and job slots. No network dependencies.
export function legacy(root, graphic, C, {art = '', energy = 1, pace = 1} = {}) {
const rgba = (hex,a) => `rgb(${parseInt(hex.slice(1,3),16)} ${parseInt(hex.slice(3,5),16)} ${parseInt(hex.slice(5,7),16)} / ${a})`;
const names = {kinetic:'G1',relationship:'G2',process:'G3',quote:'G4',outcomes:'G5','lower-third':'G6'};
const escape = value => typeof value === 'string' ? value.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])) : Array.isArray(value) ? value.map(escape) : value && typeof value === 'object' ? Object.fromEntries(Object.entries(value).map(([k,v])=>[k,escape(v)])) : value;
const ID = names[graphic.template];
const P = {[ID]: {...escape(graphic.slots), duration:graphic.duration, swapAt:graphic.settings.swapAt, outAt:graphic.settings.outAt}};
const ease = 'cubic-bezier(.2,.8,.2,1)';
const el = (html, parent = root) => { const t = document.createElement('template'); t.innerHTML = html.trim(); const n = t.content.firstChild; parent.appendChild(n); return n; };
const A = (node, kf, start, dur = 0.6, easing = ease) => node.animate(kf, { delay: start * 1000, duration: dur * 1000 / pace, fill: 'both', easing });
const fadeUp = (n, t, d = 0.6, y = 30) => A(n, [{ opacity: 0, transform: `translateY(${y * energy}px)` }, { opacity: 1, transform: 'none' }], t, d);
const pop = (n, t, d = 0.5) => A(n, [{ opacity: 0, transform: `scale(${1 - .4 * energy})` }, { opacity: 1, transform: 'scale(1.06)', offset: .7 }, { opacity: 1, transform: 'scale(1)' }], t, d);
const fadeOut = (n, t, d = 0.4) => A(n, [{ opacity: 1 }, { opacity: 0 }], t, d, 'ease-in');
const draw = (path, t, d = 0.5) => { const L = path.getTotalLength(); path.style.strokeDasharray = L; return A(path, [{ strokeDashoffset: L }, { strokeDashoffset: 0 }], t, d, 'ease-in-out'); };
const svg = (w = 1920, h = 1080) => el(`<svg class="abs" style="left:0;top:0" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}"></svg>`);
const line = (s, x1, y1, x2, y2, color, w = 4) => { const p = document.createElementNS('http://www.w3.org/2000/svg', 'path'); p.setAttribute('d', `M${x1} ${y1} L${x2} ${y2}`); p.setAttribute('stroke', color); p.setAttribute('stroke-width', w); p.setAttribute('stroke-linecap', 'round'); p.setAttribute('fill', 'none'); s.appendChild(p); return p; };

const G = {
  G1() { 
    const p = P.G1, wrap = el(`<div class="abs" style="left:150px;top:0;height:1080px;display:flex;flex-direction:column;justify-content:center;gap:22px"></div>`);
    const bad = el(`<div style="display:flex;flex-direction:column;gap:22px;align-items:flex-start"></div>`, wrap);
    p.problems.forEach(([w, t], i) => {
      const r = el(`<div class="pill" style="position:relative;font-size:82px;background:${rgba(C.panel||C.ink,.55)};color:${C.text}">${w}<span class="abs" style="left:28px;right:28px;top:52%;height:8px;background:${C.alert};border-radius:4px;transform-origin:left"></span></div>`, bad);
      fadeUp(r, t, 0.55, 24); A(r.querySelector('span'), [{ transform: 'scaleX(0)' }, { transform: 'scaleX(1)' }], p.swapAt + i * 0.15, 0.35);
    });
    A(bad, [{ opacity: 1, transform: 'none' }, { opacity: 0, transform: 'translateY(-30px)' }], p.swapAt + 0.7, 0.45, 'ease-in');
    const good = el(`<div class="abs" style="left:150px;top:0;height:1080px;display:flex;flex-direction:column;justify-content:center;gap:22px;align-items:flex-start"></div>`);
    p.goods.forEach(([w, t]) => pop(el(`<div class="pill" style="font-size:96px;background:${C.accent}">${w}</div>`, good), t, 0.55));
    fadeOut(root, p.duration - 0.4);
  },

  G2() { 
    const p = P.G2, cx = 960, cy = 560, s = svg();
    const pos = [[600, 830, C.highlight, C.ink], [960, 230, C.alert, C.text], [1320, 830, C.muted, C.ink]];
    p.nodes.forEach(([w, t], i) => {
      const [x, y, bg, fg] = pos[i]; draw(line(s, cx, cy, x, y, C.text, 5), t - 0.45, 0.45);
      const n = el(`<div class="abs pill" style="left:${x}px;top:${y}px;transform:translate(-50%,-50%);font-size:60px;background:${bg};color:${fg}">${w}</div>`);
      const inner = el(`<div></div>`); 
      n.remove(); inner.className = 'abs'; inner.style.cssText = `left:${x}px;top:${y}px;width:0;height:0`; root.appendChild(inner);
      n.style.left = '0'; n.style.top = '0'; inner.appendChild(n); pop(inner, t);
    });
    const c = el(`<div class="abs" style="left:${cx}px;top:${cy}px;width:0;height:0"><div class="abs" style="width:300px;height:300px;left:-150px;top:-150px;border-radius:50%;background:${C.accent};display:flex;align-items:center;justify-content:center;text-align:center;font-size:44px;font-weight:600;line-height:1.15;box-shadow:0 10px 40px ${rgba(C.shadow||C.ink,.35)}">${p.center.replace(' ', '<br>')}</div></div>`);
    pop(c, p.centerAt, 0.6);
    fadeOut(root, p.duration - 0.4);
  },

  G3() { 
    const p = P.G3;
    el(`<div class="abs" style="inset:0;background:${C.surface}"></div>`);
    el(`<div class="abs" style="right:0;top:0;width:420px;height:1080px;background:url(${art}) right center/cover;-webkit-mask-image:linear-gradient(to right,transparent,${C.ink} 70%)"></div>`);
    const title = el(`<div class="abs" style="left:140px;top:110px;color:${C.accent};font-size:84px;font-weight:700;letter-spacing:-1px">${p.title}<div style="width:140px;height:8px;border-radius:4px;background:${C.highlight};margin-top:10px"></div></div>`);
    fadeUp(title, p.titleAt, 0.7);
    const s = svg(), y0 = 470, x1 = 330, x2 = 1050;
    
    const prov = el(`<div class="abs" style="left:${x1}px;top:${y0}px;width:0;height:0"><div class="abs" style="left:-100px;top:-100px;width:200px;height:200px;border-radius:50%;background:${C.accent};display:flex;align-items:center;justify-content:center;font-size:84px;font-weight:700;color:${C.text}">${p.symbol || ""}<span style="font-size:56px;margin-top:34px">${p.symbolSuffix || ""}</span></div><div class="abs" style="left:-200px;width:400px;top:118px;text-align:center;color:${C.ink};font-size:36px;font-weight:600">${p.provider[0]}</div></div>`);
    pop(prov, p.provider[1]);
    
    const ar = line(s, x1 + 130, y0, x2 - 140, y0, C.ink, 5); draw(ar, p.refer[1], 0.8);
    const head = line(s, x2 - 160, y0 - 20, x2 - 138, y0, C.ink, 5), head2 = line(s, x2 - 160, y0 + 20, x2 - 138, y0, C.ink, 5);
    [head, head2].forEach(h => A(h, [{ opacity: 0 }, { opacity: 1 }], p.refer[1] + 0.75, 0.15));
    fadeUp(el(`<div class="abs" style="left:${(x1 + x2) / 2 - 150}px;width:300px;top:${y0 - 70}px;text-align:center;color:${C.ink};font-size:34px;font-style:italic">${p.refer[0]}</div>`), p.refer[1] + 0.3, 0.5, 12);
    
    const people = `<svg width="130" height="90" viewBox="0 0 130 90"><g fill="${C.text}"><circle cx="30" cy="25" r="15"/><circle cx="65" cy="20" r="17"/><circle cx="100" cy="25" r="15"/><path d="M5 85c0-18 11-32 25-32s25 14 25 32z"/><path d="M75 85c0-18 11-32 25-32s25 14 25 32z"/><path d="M35 88c0-22 13-36 30-36s30 14 30 36z"/></g></svg>`;
    const com = el(`<div class="abs" style="left:${x2}px;top:${y0}px;width:0;height:0"><div class="abs" style="left:-100px;top:-100px;width:200px;height:200px;border-radius:50%;background:${C.highlight};display:flex;align-items:center;justify-content:center">${people}</div><div class="abs" style="left:-220px;width:440px;top:118px;text-align:center;color:${C.ink};font-size:36px;font-weight:600">${p.community[0]}</div></div>`);
    pop(com, p.community[1]);
    
    const dots = [C.accent, C.alert, C.highlight, C.secondary, C.alert, C.accent], yI = 880;
    const row = el(`<div class="abs" style="left:140px;width:1360px;top:${yI - 32}px;display:flex;justify-content:space-between"></div>`);
    p.items.forEach(([w, t], i) => {
      const chip = el(`<div class="pill" style="background:${C.text};color:${C.ink};font-size:30px;padding:10px 24px;box-shadow:0 6px 18px ${rgba(C.shadow||C.ink,.12)}"><span style="display:inline-block;width:14px;height:14px;border-radius:50%;background:${dots[i]};margin-right:10px;vertical-align:middle"></span>${w}</div>`, row);
      pop(chip, t, 0.45);
    });
    [...row.children].forEach((chip, i) => { 
      const measured = chip.getBoundingClientRect(), base = root.getBoundingClientRect(), factor = base.width / 1920, r = {left:(measured.left-base.left)/factor, top:(measured.top-base.top)/factor, width:measured.width/factor}, t = p.items[i][1];
      draw(line(s, x2, y0 + 175, r.left + r.width / 2, r.top - 8, rgba(C.ink,.45), 3), t - 0.35, 0.35);
    });
  },

  G4() { 
    const p = P.G4, v = el(`<div class="vignette"></div>`); A(v, [{ opacity: 0 }, { opacity: 1 }], 0, 0.5);
    const box = el(`<div class="abs shadow" style="left:0;right:0;top:0;bottom:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center"></div>`);
    fadeUp(el(`<div style="font-size:220px;line-height:.6;height:110px;color:${C.highlight};font-weight:700">“</div>`, box), 0, 0.5, 10);
    p.lines.forEach(([t0, t]) => fadeUp(el(`<div style="font-size:70px;font-weight:500;line-height:1.25">${t0}</div>`, box), t, 0.7, 20));
    fadeUp(el(`<div style="margin-top:34px;font-size:40px;font-style:italic;color:${C.highlight}">— ${p.attribution[0]}</div>`, box), p.attribution[1], 0.6, 12);
    fadeOut(root, p.duration - 0.5, 0.5);
  },

  G5() { 
    const p = P.G5, v = el(`<div class="vignette"></div>`); A(v, [{ opacity: 0 }, { opacity: 1 }], 0, 0.5);
    const xs = [480, 960, 1440], s = svg();
    p.top.forEach(([w, t], i) => fadeUp(el(`<div class="abs shadow" style="left:${xs[i] - 250}px;width:500px;top:380px;text-align:center;font-size:76px;font-weight:600">${w}</div>`), t, 0.6, 24));
    p.bottom.forEach(([w, t], i) => {
      draw(line(s, xs[i], 500, xs[i], 590, C.highlight, 5), t - 0.35, 0.35);
      const b = el(`<div class="abs" style="left:${xs[i]}px;top:650px;width:0;height:0"><div class="abs pill" style="transform:translate(-50%,-50%);font-size:54px;background:${C.accent}">${w}</div></div>`);
      pop(b, t, 0.5);
    });
    fadeOut(root, p.outAt, 0.6);
  },

  G6() { 
    const p = P.G6;
    const lt = el(`<div class="abs" style="left:110px;bottom:110px;display:flex;align-items:stretch;overflow:hidden">
      <div style="width:10px;background:${C.highlight}"></div>
      <div class="panel" style="background:${rgba(C.accent,.94)};padding:16px 34px 18px">
        <div style="font-size:22px;letter-spacing:4px;text-transform:uppercase;color:${C.highlight};font-weight:600">${p.label}</div>
        <div style="font-size:34px;font-weight:500;margin-top:2px">${p.text}</div></div></div>`);
    A(lt, [{ clipPath: 'inset(0 100% 0 0)' }, { clipPath: 'inset(0 0% 0 0)' }], 0.1, 0.7);
    A(lt.querySelector('.panel'), [{ opacity: 0 }, { opacity: 1 }], 0.35, 0.5);
    fadeOut(root, p.duration - 0.45, 0.45);
  },
};


G[ID]();
}
