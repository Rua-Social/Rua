import {XMLParser} from 'fast-xml-parser';
export function time(s,fps=25){s=String(s).trim();if(/^\d+(?:\.\d+)?ms$/.test(s))return parseFloat(s)/1000;if(/^\d+(?:\.\d+)?s$/.test(s))return parseFloat(s);if(/^\d+(?:\.\d+)?f$/.test(s))return parseFloat(s)/fps;const p=s.replace(',','.').split(':').map(Number);if(p.some(x=>!Number.isFinite(x)))throw Error(`Invalid time: ${s}`);return p.length===4?p[0]*3600+p[1]*60+p[2]+p[3]/fps:p.length===3?p[0]*3600+p[1]*60+p[2]:p.length===2?p[0]*60+p[1]:p[0];}
const clean=s=>s.replace(/<[^>]*>/g,'').replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/\s+/g,' ').trim();
export function parseTranscript(source,extension='srt'){
 const cues=[];source=source.replace(/^\uFEFF/,'').replace(/\r/g,'');
 if(['itt','ttml','xml'].includes(extension)){
  if(/<!DOCTYPE|<!ENTITY/i.test(source))throw Error('XML entities are not supported');if(/<fcpxml\b/i.test(source))throw Error('Export captions as SRT or iTT from Final Cut; FCPXML timeline import is not supported yet.');
  const doc=new XMLParser({ignoreAttributes:false,attributeNamePrefix:'@',removeNSPrefix:true,preserveOrder:true,trimValues:false}).parse(source);
  function textOf(nodes){return nodes.map(n=>n['#text']??(n.br?' ':Object.entries(n).filter(([k])=>!k.startsWith(':')).flatMap(([,v])=>Array.isArray(v)?textOf(v):[]).join(''))).join('');}
  function walk(nodes,offset=0){for(const n of nodes){for(const [k,v] of Object.entries(n)){if(!Array.isArray(v))continue;const a=n[':@']||{};if(k==='p'&&a['@begin']!==undefined){const start=offset+time(a['@begin']);const end=a['@end']!==undefined?offset+time(a['@end']):start+time(a['@dur']||'3s');cues.push({start,end,text:clean(textOf(v)),estimated:false});}else walk(v,offset+(a['@begin']?time(a['@begin']):0));}}}walk(doc);
 }else if(source.includes('-->')){for(const block of source.split(/\n\s*\n/)){const lines=block.trim().split('\n'),i=lines.findIndex(l=>l.includes('-->'));if(i<0)continue;const [a,b]=lines[i].split('-->');cues.push({start:time(a.trim()),end:time(b.trim().split(/\s/)[0]),text:clean(lines.slice(i+1).join(' ')),estimated:false});}}
 else {let cursor=0;for(const text of source.split(/\n+|(?<=[.!?])\s+/).map(clean).filter(Boolean)){const duration=Math.max(2,text.split(/\s+/).length/2.5);cues.push({start:cursor,end:cursor+duration,text,estimated:true});cursor+=duration;}}
 const valid=cues.filter(c=>c.text&&Number.isFinite(c.start)&&Number.isFinite(c.end)&&c.start>=0&&c.end>c.start).sort((a,b)=>a.start-b.start);if(!valid.length)throw Error('No readable caption cues found');return valid.map((c,i)=>({...c,id:`cue-${i+1}`}));
}
