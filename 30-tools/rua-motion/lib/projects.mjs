import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import {CATALOG,FPS,newGraphic,SIZES,preflight} from '../public/model.js';
export const jobsRoot=path.resolve(process.env.MOTION_JOBS_DIR||path.join(os.homedir(),'rua-motion-jobs'));
export const slug=s=>String(s).normalize('NFKD').replace(/[^a-zA-Z0-9_-]+/g,'-').replace(/^-|-$/g,'').slice(0,80)||'untitled';
export function jobDir(id){if(!/^[a-zA-Z0-9_-]{1,100}$/.test(id))throw Error('Invalid project ID');return path.join(jobsRoot,id);}
export async function contained(base,relative){if(typeof relative!=='string'||path.isAbsolute(relative))throw Error('Relative asset path required');const resolved=await fs.realpath(path.resolve(base,relative)),root=await fs.realpath(base);if(!resolved.startsWith(root+path.sep))throw Error('Asset outside project');return resolved;}
export function validate(p){const err=[]; const num=(v,min,max)=>typeof v==='number'&&Number.isFinite(v)&&v>=min&&v<=max;
 if(p.version!==1)err.push('Unsupported project version');if(typeof p.name!=='string'||!p.name.trim())err.push('Project needs a name');
 if(!p.output||![p.output.width,p.output.height].every(v=>Number.isInteger(v)&&v>=128&&v<=4096&&v%2===0)||!FPS.includes(String(p.output.fps)))err.push('Use even dimensions from 128 to 4096 and a supported frame rate');
 if(!p.brand?.colors||!['accent','secondary','highlight','alert','surface','text','ink','muted'].every(k=>/^#[\da-f]{6}$/i.test(p.brand.colors[k])))err.push('Brand roles need six-digit hex colours');
 if(p.brand?.colors&&Object.values(p.brand.colors).some(v=>!/^#[\da-f]{6}$/i.test(v)))err.push('All colour roles must be six-digit hex values');
 if(!p.brand?.font?.family||!Array.isArray(p.brand.font.files))err.push('Font family and files are required');
 if(!Array.isArray(p.graphics)||p.graphics.length<1||p.graphics.length>200)err.push('Project must have between 1 and 200 graphics');else{const ids=new Set();for(const g of p.graphics){if(!/^[\w-]+$/.test(g.id)||ids.has(g.id))err.push('Graphic IDs must be unique');ids.add(g.id);if(!CATALOG.some(c=>c.id===g.template))err.push('Unknown template');if(!num(g.duration,1,120)||!num(g.dropPoint,0,86400))err.push('Invalid duration or drop point');if(!g.slots||!g.settings)err.push('Slots and settings required');else{
 const spec=CATALOG.find(c=>c.id===g.template)?.slots;
 function sameShape(value,example){if(typeof example==='string')return typeof value==='string'&&value.length<=2000;if(typeof example==='number')return num(value,0,120);if(Array.isArray(example)){if(!Array.isArray(value)||value.length>12)return false;if(typeof example[0]==='string'&&typeof example[1]==='number')return value.length===2&&sameShape(value[0],example[0])&&sameShape(value[1],example[1]);return value.length>0&&value.every(v=>sameShape(v,example[0]));}return value&&typeof value==='object'&&Object.entries(example).every(([k,v])=>sameShape(value[k],v));}
 if(g.template==='kinetic'&&!num(g.settings.swapAt,0,120))err.push('Invalid swap time');if(g.template==='outcomes'&&!num(g.settings.outAt,0,120))err.push('Invalid exit time');
 if(spec&&!sameShape(g.slots,spec))err.push(`Invalid slots for ${g.template}`);
 if(['relationship','outcomes'].includes(g.template)){const counts=g.template==='relationship'?[g.slots.nodes?.length]:[g.slots.top?.length,g.slots.bottom?.length];if(counts.some(n=>n!==3))err.push('This layout needs three ideas');}
for(const [k,min,max] of [['pace',.5,2],['energy',0,1],['scale',.65,1.3],['scrim',0,.8]])if(!num(g.settings[k],min,max))err.push(`Invalid ${k}`);if(!['transparent','surface','gradient'].includes(g.settings.background))err.push('Invalid background');if(g.settings.blobs&&(!Array.isArray(g.settings.blobs)||g.settings.blobs.length>16||g.settings.blobs.some(b=>!Number.isInteger(b.cycles)||b.cycles<1||!p.brand.colors[b.role]||!num(b.radius,.01,10)||!num(b.alpha,0,1))))err.push('Invalid gradient blobs');}}}
 if(err.length)throw Object.assign(Error([...new Set(err)].join('; ')),{status:400});return p;
}
export async function readProject(id){const file=await contained(jobDir(id),'project.json');const data=await fs.readFile(file,'utf8');return {project:JSON.parse(data),revision:crypto.createHash('sha256').update(data).digest('hex')};}
export async function listProjects(){await fs.mkdir(jobsRoot,{recursive:true});const entries=await fs.readdir(jobsRoot,{withFileTypes:true});const result=[];for(const e of entries.filter(e=>e.isDirectory())){try{const {project}=await readProject(e.name);result.push({id:e.name,name:project.name,count:project.graphics.length,colors:project.brand.colors});}catch{}}return result.sort((a,b)=>a.name.localeCompare(b.name));}
export async function saveProject(id,p,revision){validate(p);if(p.id!==id)throw Error('Project ID mismatch');const dir=jobDir(id);await fs.mkdir(dir,{recursive:true});try{const old=await readProject(id);if(revision!==old.revision)throw Object.assign(Error('This project changed outside the studio. Reload before saving.'),{status:409});await fs.writeFile(path.join(dir,'project.previous.json'),JSON.stringify(old.project,null,2));}catch(e){if(e.code!=='ENOENT')throw e;}
 const file=path.join(dir,'project.json'),tmp=path.join(dir,`.project-${crypto.randomUUID()}.tmp`);await fs.writeFile(tmp,JSON.stringify(p,null,2)+'\n');await fs.rename(tmp,file);return readProject(id);
}
export async function createProject(name) {
  const id=slug(name)+'-'+crypto.randomUUID().slice(0,6);
  const list=await listProjects();
  const seed=list.find(p=>p.id==='studio-playground');
  const source=seed?(await readProject(seed.id)).project:null;
  const brand=source?structuredClone(source.brand):{
    name:'Starter palette',
    colors:{accent:'#B54A30',secondary:'#D19C6A',highlight:'#E8BD86',alert:'#C84D3C',surface:'#F2EDE5',text:'#FFF9F0',ink:'#292823',muted:'#CCC9BA'},
    font:{family:'Inter',files:[]}
  };
  const dir=jobDir(id);
  await fs.mkdir(path.join(dir,'brand'),{recursive:true});
  if(source){
    for(const f of brand.font.files){
      const src=await contained(jobDir(seed.id),f.path),dest='brand/'+path.basename(f.path);
      await fs.copyFile(src,path.join(dir,dest));f.path=dest;
    }
  }else{
    for(const [filename,weight]of [['interface-regular.ttf',400],['interface-semibold.ttf',600]]){
      await fs.copyFile(new URL('../public/fonts/'+filename,import.meta.url),path.join(dir,'brand',filename));
      brand.font.files.push({path:'brand/'+filename,weight,style:'normal'});
    }
  }
  delete brand.art;delete brand.logo;
  return saveProject(id,{version:1,id,name,output:{width:1920,height:1080,fps:'25'},brand,graphics:[newGraphic()],transcript:[]});
}
export async function preflightProject(p,g){const issues=preflight(p,g);for(const f of p.brand.font.files){try{await contained(jobDir(p.id),f.path);}catch{issues.push({level:'error',message:`Font file missing: ${f.path}`});}}if(!p.brand.font.files.length)issues.push({level:'error',message:'Supply local font files before rendering.'});return issues;}
