import {legacy} from './templates/legacy.js';
import {editorial,reflow} from './templates/editorial.js';
import {gradient} from './templates/gradient.js';
import {fpsValue,defaultBlobs} from './model.js';
const rgba=(hex,a)=>`rgb(${parseInt(hex.slice(1,3),16)} ${parseInt(hex.slice(3,5),16)} ${parseInt(hex.slice(5,7),16)} / ${a})`;
const loadedFonts=new Map();
export function fontFamily(project){let hash=2166136261;for(const c of JSON.stringify(project.brand.font)){hash=Math.imul(hash^c.charCodeAt(0),16777619);}return `motion-${project.id}-${(hash>>>0).toString(16)}`;}
export async function loadFonts(project,assetBase){
 const family=fontFamily(project);const key=family+JSON.stringify(project.brand.font);
 if(!project.brand.font.files.length)throw Error('No local font supplied. Add a font in Brand.');
 if(!loadedFonts.has(key)){const promise=Promise.all(project.brand.font.files.map(async f=>{const font=new FontFace(family,`url("${assetBase+f.path.split('/').map(encodeURIComponent).join('/')}")`,{weight:String(f.weight||400),style:f.style||'normal'});await font.load();document.fonts.add(font);}));loadedFonts.set(key,promise);promise.catch(()=>loadedFonts.delete(key));}
 await loadedFonts.get(key);await document.fonts.ready;return family;
}
export async function compose(host,project,graphic,{assetBase=`/assets/${project.id}/`,width=project.output.width,height=project.output.height,isCurrent=()=>true}={}){
 const family=await loadFonts(project,assetBase);if(!isCurrent())return null;const C=project.brand.colors,s=graphic.settings;
 const shadow=host.shadowRoot||host.attachShadow({mode:'open'});host._dispose?.();shadow.replaceChildren();
 const style=document.createElement('style');style.textContent=`:host{display:block;width:100%;height:100%}*{box-sizing:border-box}.stage{position:relative;width:${width}px;height:${height}px;overflow:hidden;background:transparent;font-family:"${family}";color:${C.text}}.abs{position:absolute}.pill{display:inline-block;border-radius:999px;padding:8px 40px 10px;font-weight:600;white-space:nowrap}.shadow{text-shadow:0 2px 18px ${rgba(C.shadow||C.ink,.55)},0 1px 3px ${rgba(C.shadow||C.ink,.5)}}.vignette{position:absolute;inset:0;background:radial-gradient(ellipse 70% 60% at 50% 50%,${rgba(C.scrim||C.ink,s.scrim)},transparent 75%)}.design{position:absolute;inset:0;transform-origin:center center} .stage img{object-fit:contain}`;shadow.append(style);
 const stage=document.createElement('div');stage.className='stage';shadow.append(stage);
 const full=graphic.template==='process'||s.background!=='transparent';if(full)stage.style.background=C.surface;
 let gl=null;if(graphic.template==='gradient'||s.background==='gradient'){const canvas=document.createElement('canvas');Object.assign(canvas.style,{position:'absolute',inset:'0'});stage.append(canvas);gl=gradient(canvas,project.brand,{width,height,duration:graphic.duration,fps:fpsValue(project.output.fps),dither:s.dither??2.5,blobs:(s.blobs||defaultBlobs(height/width)).map(b=>({...b,ampX:b.ampX*s.energy,ampY:b.ampY*s.energy,scaleAmp:b.scaleAmp*s.energy}))});}
 const root=document.createElement('div');root.className='design';stage.append(root);
 const opts={width,height,energy:s.energy,pace:s.pace,fontScale:s.scale,logo:project.brand.logo?assetBase+project.brand.logo:undefined};
 if(graphic.template!=='gradient'){
 if(['chapter','stat','cta'].includes(graphic.template)){if(s.background==='transparent'&&s.scrim){const scrim=document.createElement('div');scrim.className='vignette';root.append(scrim);}editorial(root,graphic,C,opts);}
 else if(width/height<1.5){if(s.scrim){const scrim=document.createElement('div');scrim.className='vignette';stage.insertBefore(scrim,root);}reflow(root,graphic,C,opts);}
 else{root.style.width='1920px';root.style.height='1080px';root.style.inset='auto';root.style.left=`${width/2}px`;root.style.top=`${height/2}px`;root.style.transform=`translate(-50%,-50%) scale(${Math.min(width/1920,height/1080)*s.scale})`;legacy(root,graphic,C,{art:project.brand.art?assetBase+project.brand.art:'',energy:s.energy,pace:s.pace});}
 }
 const anims=shadow.getAnimations();const seek=t=>{for(const a of anims){a.pause();a.currentTime=t*1000;}gl?.seek(t);};seek(0);
 const images=[...shadow.querySelectorAll('img')];await Promise.all(images.map(img=>img.decode().catch(()=>{throw Error('A project image could not load');})));
 host._dispose=()=>{anims.forEach(a=>a.cancel());gl?.dispose();};
 const inspect=()=>{const bounds=stage.getBoundingClientRect(),texts=[...root.querySelectorAll('div')].filter(n=>[...n.childNodes].some(c=>c.nodeType===3&&c.textContent.trim()));return texts.filter(n=>{const r=n.getBoundingClientRect();return r.left<bounds.left-1||r.right>bounds.right+1||r.top<bounds.top-1||r.bottom>bounds.bottom+1;}).map(n=>n.textContent.slice(0,100));};
 return {seek,stage,inspect,dispose:host._dispose};
}
