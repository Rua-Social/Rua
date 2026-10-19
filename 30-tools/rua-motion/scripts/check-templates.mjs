import fs from 'node:fs/promises';import {listProjects,readProject} from '../lib/projects.mjs';import {allText} from '../public/model.js';
const dir=new URL('../public/templates/',import.meta.url),files=await fs.readdir(dir),issues=[],brands=[],copy=[];
for(const job of await listProjects()){const {project}=await readProject(job.id);if(project.brand.name&&project.brand.name.length>8)brands.push(project.brand.name);if(project.brand.font.family)brands.push(project.brand.font.family);for(const graphic of project.graphics)for(const text of allText(graphic))if(text.trim().length>=8)copy.push(text.trim());}
for(const file of files){const source=await fs.readFile(new URL(file,dir),'utf8');if(/#[0-9a-f]{3,8}\b/i.test(source))issues.push(`${file}: literal hex colour`);if(/font-family\s*:/i.test(source))issues.push(`${file}: template chooses its own font family`);for(const value of brands)if(source.toLowerCase().includes(value.toLowerCase()))issues.push(`${file}: client fact ${value}`);
 const body=file==='legacy.js'?source.slice(source.indexOf('const ease =')):source;
 const literals=[...body.matchAll(/'((?:[^'\\]|\\.)*)'|"((?:[^"\\]|\\.)*)"|`((?:[^`\\]|\\.)*)`/gs)].map(m=>(m[1]??m[2]??m[3]).replace(/\$\{[^}]*\}/g,'')).join('\n').toLowerCase();
 for(const text of copy)if(literals.includes(text.toLowerCase()))issues.push(`${file}: job phrase in template literal: ${text}`);
}
if(issues.length){console.error([...new Set(issues)].join('\n'));process.exit(1);}console.log(`${files.length} template modules: no literal hex colours, font declarations, known brand/font names or on-screen phrases of 8+ characters.`);
