// Text is inserted as textContent; brand values arrive as roles.
export function editorial(root,g,C,{width:W,height:H,energy,pace,fontScale,logo}){
 const portrait=H>W,scale=Math.min(W/1920,H/1080),unit=portrait?W/1080:scale;
 const el=(tag,text,style,parent=root)=>{const n=document.createElement(tag);if(text)n.textContent=text;Object.assign(n.style,style);parent.append(n);return n;};
 const animate=(n,at=.2,type='up')=>n.animate([{opacity:0,transform:type==='up'?`translateY(${35*energy*unit}px)`:`scale(${1-.15*energy})`},{opacity:1,transform:'none'}],{delay:at*1000,duration:850/pace,fill:'both',easing:'cubic-bezier(.16,1,.3,1)'});
 const text=(copy,size,weight=500)=>el('div',copy,{fontSize:`${size*unit*fontScale}px`,fontWeight:weight,lineHeight:'1.08',letterSpacing:'-.045em',whiteSpace:'pre-line'});
 const margin=portrait?80*unit:140*unit;const wrap=el('div','',{position:'absolute',inset:`${margin}px`,display:'flex',flexDirection:'column',justifyContent:'center',alignItems:'flex-start'});
 const add=(copy,size,weight,style={})=>{const n=text(copy,size,weight);Object.assign(n.style,style);wrap.append(n);return n;};
 if(logo){el('img','',{position:'absolute',right:`${margin}px`,top:`${margin}px`,maxWidth:`${180*unit}px`,maxHeight:`${90*unit}px`,objectFit:'contain'}).src=logo;}
 const color=g.settings.background==='transparent'?C.text:C.ink;wrap.style.color=color;
 const rule=el('div','',{width:`${80*unit}px`,height:`${7*unit}px`,background:C.accent,marginBottom:`${45*unit}px`},wrap);animate(rule,.1);
 if(['chapter','cta'].includes(g.template)){
 const eyebrow=add(g.slots.eyebrow,22,600,{letterSpacing:'.17em',textTransform:'uppercase',color:C.accent,marginBottom:`${28*unit}px`});animate(eyebrow,.1);
 const title=add(g.slots.title,portrait?100:132,650,{maxWidth:'100%'});animate(title,.3);
 const foot=add(g.slots.subtitle||g.slots.action,portrait?32:34,450,{marginTop:`${42*unit}px`,letterSpacing:'-.015em',lineHeight:'1.4',maxWidth:'85%'});animate(foot,.7);
 if(g.template==='cta'){foot.style.background=C.accent;foot.style.color=C.text;foot.style.borderRadius=`${60*unit}px`;foot.style.padding=`${22*unit}px ${36*unit}px`;const detail=add(g.slots.detail,25,500,{marginTop:`${28*unit}px`,letterSpacing:'0'});animate(detail,1);}
 const orb=el('div','',{position:'absolute',width:`${360*unit}px`,height:`${360*unit}px`,border:`${2*unit}px solid ${C.accent}`,borderRadius:'50%',right:`${-130*unit}px`,bottom:`${-130*unit}px`,opacity:'.3'});animate(orb,0,'scale');
 }else if(g.template==='stat'){
 const row=el('div','',{display:'flex',alignItems:'baseline',color:C.accent},wrap);const value=text(g.slots.value,portrait?220:300,650);row.append(value);const suffix=text(g.slots.suffix,110,500);row.append(suffix);animate(row,.2);
 animate(add(g.slots.title,portrait?64:80,550,{marginTop:`${20*unit}px`,maxWidth:'90%'}),.65);
 animate(add(g.slots.source,24,400,{marginTop:`${45*unit}px`,letterSpacing:'0',opacity:'.7'}),1);
 }
 root.animate([{opacity:1},{opacity:0}],{delay:(g.duration-.5)*1000,duration:500,fill:'forwards'});
}
export function reflow(root,g,C,options){
 const {width:W,height:H,energy,pace,fontScale}=options;const u=W/1080;
 const make=(text,size,bg,color=C.text)=>{const n=document.createElement('div');n.textContent=text;Object.assign(n.style,{fontSize:`${size*u*fontScale}px`,fontWeight:600,lineHeight:'1.2',color,background:bg||'transparent',borderRadius:`${50*u}px`,padding:bg?`${16*u}px ${32*u}px`:'0',maxWidth:'100%',overflowWrap:'anywhere',boxSizing:'border-box'});return n;};
 const box=document.createElement('div');Object.assign(box.style,{position:'absolute',inset:`${H*.09}px ${W*.09}px`,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',gap:`${28*u}px`,textAlign:'center'});root.append(box);
 const enter=(node,at)=>{box.append(node);node.animate([{opacity:0,transform:`translateY(${28*energy*u}px)`},{opacity:1,transform:'none'}],{delay:at*1000,duration:600/pace,fill:'both',easing:'cubic-bezier(.2,.8,.2,1)'});return node;};
 if(g.template==='quote'){enter(make('“',160,C.highlight,C.ink),0);g.slots.lines.forEach(([s,t])=>enter(make(s,54),t));enter(make(g.slots.attribution[0],30,undefined,C.highlight),g.slots.attribution[1]);}
 if(g.template==='lower-third'){box.style.justifyContent='flex-end';box.style.alignItems='stretch';box.style.textAlign='left';const n=make(g.slots.text,36,C.accent);const label=make(g.slots.label,22,undefined,C.highlight);n.prepend(label);enter(n,.1);}
 if(g.template==='relationship'){enter(make(g.slots.center,58,C.accent),g.slots.centerAt);g.slots.nodes.forEach(([s,t],i)=>enter(make('↳ '+s,42,[C.highlight,C.alert,C.muted][i%3],C.ink),t));}
 if(g.template==='outcomes'){g.slots.top.forEach(([s,t],i)=>{const n=enter(make(s,48),t);const bottom=g.slots.bottom[i];if(bottom){const b=make('↓\n'+bottom[0],38,C.accent);n.append(b);b.animate([{opacity:0},{opacity:1}],{delay:bottom[1]*1000,duration:500/pace,fill:'both'});}});}
 if(g.template==='kinetic'){
 const bad=document.createElement('div');Object.assign(bad.style,{display:'flex',flexDirection:'column',alignItems:'center',gap:`${22*u}px`});box.append(bad);
 g.slots.problems.forEach(([s,t],i)=>{const n=enter(make(s,64,C.ink),t);bad.append(n);const strike=document.createElement('div');Object.assign(strike.style,{height:`${6*u}px`,background:C.alert,marginTop:`${-40*u}px`,transformOrigin:'left'});n.append(strike);strike.animate([{transform:'scaleX(0)'},{transform:'scaleX(1)'}],{delay:((g.settings.swapAt??5.4)+i*.15)*1000,duration:350,fill:'both'});});
 bad.animate([{opacity:1},{opacity:0}],{delay:((g.settings.swapAt??5.4)+.7)*1000,duration:450,fill:'forwards'});
 const goods=document.createElement('div');Object.assign(goods.style,{position:'absolute',inset:'0',display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',gap:`${22*u}px`});box.append(goods);g.slots.goods.forEach(([s,t])=>{const n=enter(make(s,70,C.accent),t);goods.append(n);});}
 if(g.template==='process'){enter(make(g.slots.title,64,undefined,C.accent),g.slots.titleAt);enter(make(g.slots.provider[0],40,C.accent),g.slots.provider[1]);enter(make('↓ '+g.slots.refer[0],28,undefined,C.ink),g.slots.refer[1]);enter(make(g.slots.community[0],40,C.highlight,C.ink),g.slots.community[1]);const items=document.createElement('div');Object.assign(items.style,{display:'flex',flexWrap:'wrap',gap:`${12*u}px`,justifyContent:'center'});box.append(items);g.slots.items.forEach(([s,t])=>{const n=enter(make(s,26,C.text,C.ink),t);items.append(n);});}
 root.animate([{opacity:1},{opacity:0}],{delay:((g.template==='outcomes'?Math.min(g.settings.outAt,g.duration-.5):g.duration-.5))*1000,duration:500,fill:'forwards'});
}
