import fs from 'node:fs/promises';import path from 'node:path';import {jobsRoot,saveProject} from '../lib/projects.mjs';import {newGraphic} from '../public/model.js';
const id='studio-playground';try{await fs.access(path.join(jobsRoot,id,'project.json'));console.log('Playground already exists');process.exit(0);}catch{}
const dir=path.join(jobsRoot,id,'brand');await fs.mkdir(dir,{recursive:true});
const files=[];for(const [name,weight] of [['Regular',400],['Medium',500],['SemiBold',600],['Bold',700]]){const filename=`Manrope-${name}.ttf`;await fs.copyFile('/Library/Fonts/'+filename,path.join(dir,filename));files.push({path:'brand/'+filename,weight,style:'normal'});}
const brand={name:'Studio palette',colors:{accent:'#B54A30',secondary:'#D19C6A',highlight:'#E8BD86',alert:'#C84D3C',surface:'#F2EDE5',text:'#FFF9F0',ink:'#292823',muted:'#CCC9BA'},font:{family:'Manrope',files}};
const graphics=['chapter','quote','kinetic','stat','relationship','process','outcomes','lower-third','cta','gradient'].map(t=>newGraphic(t));
graphics[0].slots={eyebrow:'An independent motion studio',title:'Good stories\ndeserve to move.',subtitle:'A little intention. A lot of possibility.'};graphics[0].label='Good stories deserve to move';for(let i=0;i<graphics.length;i++)graphics[i].dropPoint=i*9;
await saveProject(id,{version:1,id,name:'The Motion Playground',output:{width:1920,height:1080,fps:'25'},brand,graphics,transcript:[]});console.log('Created '+path.join(jobsRoot,id));
