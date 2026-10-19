export const CATALOG = [
 {id:'chapter',name:'Chapter card',kind:'Full frame',note:'A confident opening. Type, space and a quiet accent.',icon:'Aa',slots:{eyebrow:'A new perspective',title:'Make room\nfor something good.',subtitle:'Stories worth bringing to life.'}},
 {id:'kinetic',name:'Kinetic words',kind:'Overlay',note:'Three barriers, crossed out. Two ideas to take their place.',icon:'↗',slots:{problems:[['The old way',.5],['More noise',1.5],['Standing still',2.4]],goods:[['A fresh start',5.9],['Moving forward',6.7]]}},
 {id:'relationship',name:'Connections',kind:'Overlay',note:'One central idea. Three connected possibilities.',icon:'⌘',slots:{center:'The big idea',centerAt:.3,nodes:[['People',2],['Place',3],['Purpose',4]]}},
 {id:'process',name:'Process flow',kind:'Full frame',note:'Make a complex journey feel simple.',icon:'⇢',slots:{title:'How it happens',titleAt:.2,provider:['The first step',1.2],symbol:'01',refer:['leads to',2.2],community:['Something better',3.3],items:[['Discover',4],['Explore',4.5],['Create',5],['Connect',5.5],['Share',6],['Grow',6.5]]}},
 {id:'quote',name:'Quote card',kind:'Overlay',note:'Give the words room to resonate.',icon:'“',slots:{lines:[['A small idea can be',.2],['the start of something extraordinary.',1.4]],attribution:['A voice worth hearing',2.7]}},
 {id:'outcomes',name:'Ideas & outcomes',kind:'Overlay',note:'Connect three ideas to what they make possible.',icon:'⋮',slots:{top:[['Imagine',.4],['Create',1.4],['Connect',2.4]],bottom:[['Possibility',4.5],['Progress',5.4],['Community',6.4]]}},
 {id:'lower-third',name:'Lower third',kind:'Overlay',note:'An introduction or a source, beautifully understated.',icon:'▰',slots:{label:'In conversation',text:'Name · Role or source'}},
 {id:'stat',name:'Number story',kind:'Full frame',note:'One number. A clear reason to care.',icon:'72',slots:{value:'72',suffix:'%',title:'A meaningful change.',source:'Add your source here'}},
 {id:'cta',name:'Closing invitation',kind:'Full frame',note:'An ending that opens a door.',icon:'↗',slots:{eyebrow:'The next step',title:'Let’s make\nsomething matter.',action:'Start a conversation',detail:'yourwebsite.com'}},
 {id:'gradient',name:'Living gradient',kind:'Full frame',note:'Soft colour, continuous motion. A seamless brand backdrop.',icon:'◉',slots:{}}
];
export const SIZES={'16:9':[1920,1080],'9:16':[1080,1920],'1:1':[1080,1080],'4:5':[1080,1350]};
export const FPS=['23.976','24','25','29.97','30','50','59.94','60'];
export const fpsValue=v=>({'23.976':24000/1001,'29.97':30000/1001,'59.94':60000/1001}[v]||Number(v));
export const fpsRational=v=>({'23.976':'24000/1001','29.97':'30000/1001','59.94':'60000/1001'}[v]||String(v));
export function newGraphic(template='chapter') {
 const cat=CATALOG.find(t=>t.id===template); if(!cat) throw Error('Unknown template');
 return {id:crypto.randomUUID(),template,label:cat.name,duration:template==='kinetic'?9:template==='outcomes'?8.2:8,dropPoint:0,slots:structuredClone(cat.slots),settings:{energy:1,pace:1,scale:1,scrim:['quote','outcomes'].includes(template)?.55:0,background:cat.kind==='Overlay'?'transparent':template==='gradient'?'gradient':'surface',swapAt:5.4,outAt:7.5,dither:2.5}};
}
export function defaultBlobs(ratio) {
 return [{role:'accent',cx:.2,cy:.2*ratio,radius:.8,alpha:.8,ampX:.08,ampY:.09,cycles:1,phase:0,scaleAmp:.1},{role:'secondary',cx:.8,cy:.7*ratio,radius:.85,alpha:.8,ampX:.08,ampY:.08,cycles:2,phase:1.9,scaleAmp:.12},{role:'highlight',cx:.6,cy:ratio,radius:.6,alpha:.6,ampX:.07,ampY:.04,cycles:1,phase:3.4,scaleAmp:.08}];
}
export function direction(graphic, instruction) {
 const g=structuredClone(graphic),s=g.settings,applied=[]; const text=instruction.toLowerCase();
 if(/calm|gentl|slow|quiet/.test(text)){s.energy=.35;s.pace=.65;if(g.template==='gradient'){g.duration=Math.min(120,g.duration*1.4);applied.push('Softer drift and a longer loop');}else applied.push('Softer movement and longer transitions');}
 if(/bold|punch|energetic|snapp/.test(text)){s.energy=1;s.pace=1.6;if(g.template==='gradient'){g.duration=Math.max(1,g.duration*.8);applied.push('More movement and a quicker loop');}else applied.push('Crisper, more energetic transitions');}
 if(/minimal|understat|clean/.test(text)){s.energy=.2;s.scale=.88;applied.push('Restrained motion and more breathing room');}
 if(/larger|bigger/.test(text)){s.scale=Math.min(1.3,(s.scale||1)+.1);applied.push('Larger type');}
 if(/smaller/.test(text)){s.scale=Math.max(.65,(s.scale||1)-.1);applied.push('Smaller type');}
 if(/scrim|contrast|readab/.test(text)){s.scrim=.65;applied.push('Stronger scrim behind the graphic');}
 if(/transparent|overlay/.test(text)&&!['gradient','process'].includes(g.template)){s.background='transparent';applied.push('Transparent overlay');}
 const duration=text.match(/(?:duration|last|for)\s+(\d+(?:\.\d+)?)\s*(?:s|seconds)/);if(duration){g.duration=Math.max(1,Math.min(120,+duration[1]));applied.push(`Duration ${g.duration}s`);}
 return {graphic:g,applied};
}
export function allText(g){const collect=v=>typeof v==='string'?[v]:Array.isArray(v)?v.flatMap(collect):v&&typeof v==='object'?Object.values(v).flatMap(collect):[];return collect(g.slots);}
export function contrast(a,b){const l=hex=>{const c=[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);return c[0]*.2126+c[1]*.7152+c[2]*.0722;};const x=l(a),y=l(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);}
export function preflight(project,g){const issues=[],text=allText(g).join(' '),words=text.split(/\s+/).filter(Boolean).length;const add=(level,message)=>issues.push({level,message});
 if(words/g.duration>3.5)add('warning',`${words} words in ${g.duration}s. Allow more reading time.`);
 const timed=[];function scan(v){if(Array.isArray(v)){if(typeof v[0]==='string'&&typeof v[1]==='number')timed.push(v[1]);else v.forEach(scan);}else if(v&&typeof v==='object')Object.values(v).forEach(scan);}scan(g.slots);
 if(timed.some(t=>t>=g.duration-.4))add('error','An entrance happens at or after the exit. Extend the duration or move the cue.');
 if(g.template==='kinetic'&&(g.settings.swapAt??5.4)+1.15>=g.duration)add('error','The word swap needs more time before the graphic ends.');
 if(g.template==='outcomes'&&g.settings.outAt>=g.duration)add('warning','The exit starts at or beyond the duration.');
 const ratio=contrast(project.brand.colors.text,project.brand.colors.accent);if(ratio<3)add('warning',`Text / accent contrast is ${ratio.toFixed(1)}:1. Review small type.`);
 if(g.settings.background==='transparent')add('info','Overlay contrast depends on your footage. Check the brightest shot.');
 if(allText(g).some(t=>t.length>130))add('warning','Long text: inspect wrapping and safe areas.');
 if(/\b(disconection|teh|recieve|seperate|acommodate)\b/i.test(text))add('warning','Possible spelling error. Review the on-screen copy.');
 return issues;
}
