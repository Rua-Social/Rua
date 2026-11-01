/* Browser-local director's storyboard. No external services. */
(async function () {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const CONFIG = window.STORYBOARD_CONFIG || {};
  const STORAGE_KEY = window.STORYBOARD_STORAGE_KEY || 'rua-directors-board-v1';
  const STATUSES = ['Proposed', 'Needs decision', 'Approved'];
  const SEQUENCE_COLORS = ['#929e8a', '#738675', '#ae8b5f', '#4d6952'];
  const ASSETS = window.STORYBOARD_ASSETS || {};
  // Keep large embedded atlases out of CSS custom properties, which have browser size limits.
  // ASSETS stays intact so exported HTML remains self-contained; Blob URLs live for this page.
  function atlasRuntimeURL(value){
    const match=typeof value==='string' && value.match(/^data:([^;,]+);base64,([\s\S]*)$/);
    if(!match)return value;
    const binary=atob(match[2]);
    const bytes=new Uint8Array(binary.length);
    for(let i=0;i<binary.length;i++)bytes[i]=binary.charCodeAt(i);
    return URL.createObjectURL(new Blob([bytes],{type:match[1]}));
  }
  for(let i=0;i<4;i++){
    const key=`board-${String.fromCharCode(97+i)}`;
    const value=ASSETS[key] || ASSETS[key+'.png'] || ASSETS['assets/'+key+'.png'] || 'assets/'+key+'.png';
    document.documentElement.style.setProperty(`--atlas-${i}`,`url("${atlasRuntimeURL(value)}")`);
  }
  const clone = (value) => JSON.parse(JSON.stringify(value));
  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const text = (value) => typeof value === 'string' ? value : value == null ? '' : typeof value === 'object' ? JSON.stringify(value) : String(value);
  const safeURL = (value) => { try { const url = new URL(value); return ['https:', 'http:'].includes(url.protocol) ? url.href : ''; } catch { return ''; } };
  const mmss = (seconds, precise = true) => { const rounded = precise ? Math.round(seconds * 10) / 10 : Math.round(seconds); const mins = Math.floor(rounded / 60); const secs = rounded - mins * 60; return `${String(mins).padStart(2,'0')}:${precise && secs % 1 ? secs.toFixed(1).padStart(4,'0') : String(Math.round(secs)).padStart(2,'0')}`; };
  const durationLabel = (seconds) => `${Number(seconds.toFixed(1))}s`;
  const slug = (value) => text(value).toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
  const exportPrefix = text(CONFIG.exportPrefix || 'Rua').replace(/[\\/:*?"<>|\u0000-\u001f]/g,'-').trim().slice(0,120) || 'Rua';
  const fallback = {title:'Storyboard',subtitle:'Director’s working board',runtime:0,version:'Rough storyboard',format:'16:9 master',summary:'',sequences:[{id:'A',title:'Sequence',description:''}],shots:[],decisions:[],references:[],workflow:[],glossary:[]};
  let initial = clone(window.STORYBOARD_DATA || fallback);
  let state = clone(initial);
  let view = 'board';
  let sequenceFilter = 'all';
  let statusFilter = 'all';
  let editingId = null;
  let activeModal = null;
  let returnFocus = null;
  let saveTimer = null;
  let saveChain = Promise.resolve();
  let saveRevision = 0;
  let toastTimer = null;
  let presentIndex = 0;
  let playing = false;
  let elapsedInShot = 0;
  let previousTick = 0;
  let previewTimer = null;
  let tempAudio = null;
  let audioObjectURL = null;
  let tempAudioName = '';
  let tempAudioBlob = null;
  let audioSaveChain = Promise.resolve();
  let videoExport = null;
  let exportReturnFocus = null;
  let audioPlayPending = false;
  let audioPlaybackFailed = false;
  let resetInProgress = false;
  let db = null;

  function normalize(data) {
    const result = clone(data);
    result.title = text(result.title || fallback.title);
    result.subtitle = text(result.subtitle || fallback.subtitle);
    result.version = text(result.version || fallback.version);
    result.format = text(result.format || '16:9 master');
    result.summary = text(result.summary || fallback.summary);
    result.audioStartSeconds = Number.isFinite(Number(result.audioStartSeconds)) && Number(result.audioStartSeconds)>=0 ? Number(result.audioStartSeconds) : 3;
    result.sequences = Array.isArray(result.sequences) ? result.sequences : [];
    result.sequences = result.sequences.map((seq, i) => ({...seq,id:text(seq.id || String.fromCharCode(65+i)),title:text(seq.title || 'Sequence'),description:text(seq.description)}));
    if (!result.sequences.length) result.sequences = clone(fallback.sequences);
    result.shots = (Array.isArray(result.shots) ? result.shots : []).map((shot, i) => ({...shot,id:text(shot.id || `S${String(i+1).padStart(2,'0')}`),sequence:text(shot.sequence || result.sequences[0].id),title:text(shot.title || 'Untitled panel'),duration:Number.isFinite(Number(shot.duration)) && Number(shot.duration)>0 ? Number(shot.duration) : 2,framing:text(shot.framing),action:text(shot.action),camera:text(shot.camera),sound:text(shot.sound),transition:text(shot.transition),continuity:text(shot.continuity),decision:text(shot.decision),provenance:text(shot.provenance),notes:text(shot.notes),endTitle:text(shot.endTitle),endSubtitle:text(shot.endSubtitle),status:STATUSES.includes(shot.status) ? shot.status : 'Proposed',priority:shot.priority==='Optional' ? 'Optional':'Essential',imageIndex:Number.isInteger(shot.imageIndex) ? shot.imageIndex : -1}));
    for (const key of ['decisions','references','workflow','glossary']) if (!Array.isArray(result[key])) result[key]=[];
    result.decisions=result.decisions.map(d=>({...d,sourceStatus:text(d.sourceStatus || (!['Open','In discussion','Agreed','Resolved','Approved'].includes(d.status) ? d.status : ''))}));
    result.schemaVersion=1;
    return result;
  }
  state=normalize(state); initial=normalize(initial);

  function validateImport(candidate) {
    if (candidate?.project) candidate=candidate.project;
    if (!candidate || typeof candidate!=='object' || !Array.isArray(candidate.shots)) throw new Error('This file does not contain a storyboard shots array.');
    if (!candidate.shots.length || candidate.shots.length>250) throw new Error('A board must contain between 1 and 250 panels.');
    if (!Array.isArray(candidate.sequences) || !candidate.sequences.length || candidate.sequences.length>20) throw new Error('The file must include 1–20 sequences.');
    const seqIds=new Set();
    for(const seq of candidate.sequences){if(!seq || typeof seq.id!=='string' || !seq.id.trim() || seqIds.has(seq.id)) throw new Error('Each sequence needs a unique text ID.');seqIds.add(seq.id);}
    const ids=new Set();
    for(const shot of candidate.shots){
      if(!shot || typeof shot!=='object' || typeof shot.id!=='string' || !shot.id.trim() || ids.has(shot.id)) throw new Error('Each panel needs a unique text ID.');
      ids.add(shot.id);
      if(!seqIds.has(shot.sequence)) throw new Error(`Panel ${shot.id} refers to an unknown sequence.`);
      if(!Number.isFinite(Number(shot.duration)) || Number(shot.duration)<.2 || Number(shot.duration)>600) throw new Error(`Panel ${shot.id} needs a duration between 0.2 and 600 seconds.`);
      if(shot.customImage && !/^data:image\/(png|jpeg|webp);base64,[A-Za-z0-9+/=]+$/.test(shot.customImage)) throw new Error(`Panel ${shot.id} has an unsupported image. Use JPG, PNG or WebP.`);
      for(const key of ['title','framing','action','camera','sound','transition','continuity','decision','provenance','notes','endTitle','endSubtitle']) if(shot[key]!=null && (typeof shot[key]!=='string' || shot[key].length>30000)) throw new Error(`Panel ${shot.id} has an invalid ${key} field.`);
    }
    for (const key of ['decisions','references','workflow','glossary']) if(candidate[key] && (!Array.isArray(candidate[key]) || candidate[key].length>200)) throw new Error(`The ${key} list is not valid.`);
    return normalize(candidate);
  }

  async function openDatabase() {
    if (!('indexedDB' in window)) return null;
    return new Promise((resolve) => {
      try {
        const request=indexedDB.open(text(CONFIG.databaseName || 'rua-storyboard'),1);
        request.onupgradeneeded=()=>{if(!request.result.objectStoreNames.contains('boards')) request.result.createObjectStore('boards');};
        request.onsuccess=()=>resolve(request.result);
        request.onerror=()=>resolve(null);
        request.onblocked=()=>resolve(null);
      } catch { resolve(null); }
    });
  }
  async function dbRead() {
    if(!db) return null;
    return new Promise((resolve)=>{try{const req=db.transaction('boards','readonly').objectStore('boards').get(STORAGE_KEY);req.onsuccess=()=>resolve(req.result || null);req.onerror=()=>resolve(null);}catch{resolve(null);}});
  }
  async function dbWrite(value) {
    if(!db) return false;
    return new Promise((resolve)=>{try{const tx=db.transaction('boards','readwrite');tx.objectStore('boards').put(value,STORAGE_KEY);tx.oncomplete=()=>resolve(true);tx.onerror=()=>resolve(false);tx.onabort=()=>resolve(false);}catch{resolve(false);}});
  }
  function showStorageWarning(message) {$('storage-warning').textContent=message;$('storage-warning').hidden=false;}
  function setSaveLabel(message,unsaved=false){$('save-label').textContent=message;document.querySelector('.save-state').classList.toggle('unsaved',unsaved);$('drawer-save-label').textContent=unsaved?'Saving changes…':'Changes saved on this browser';}
  function scheduleSave() {
    saveRevision++;
    setSaveLabel('Saving changes…',true);
    clearTimeout(saveTimer);
    saveTimer=setTimeout(()=>{
      const revision=saveRevision;
      state.savedAt=Date.now();
      const snapshot=clone(state);
      saveChain=saveChain.then(async()=>{
        let localOK=false;
        try {localStorage.setItem(STORAGE_KEY,JSON.stringify(snapshot));localOK=true;} catch {}
        const idbOK=await dbWrite(snapshot);
        if(localOK || idbOK){
          if(revision===saveRevision) setSaveLabel('Saved on this browser');
          $('storage-warning').hidden=true;
        }else{
          setSaveLabel('Not saved — export a backup',true);
          $('drawer-save-label').textContent='Not saved — export a JSON backup';
          showStorageWarning('Your browser could not save these changes, possibly because storage is full or disabled. The current board is still here. Export an editable JSON backup before closing this page.');
        }
      }).catch(()=>showStorageWarning('Saving failed. Export an editable JSON backup before closing this page.'));
    },350);
  }
  function toast(message,ms=3500){clearTimeout(toastTimer);$('toast').textContent=message;$('toast').hidden=false;toastTimer=setTimeout(()=>$('toast').hidden=true,ms);}
  const sequence=(id)=>state.sequences.find(s=>s.id===id) || {id,title:'Sequence'};
  const seqColor=(id)=>SEQUENCE_COLORS[Math.max(0,state.sequences.findIndex(s=>s.id===id))%SEQUENCE_COLORS.length];
  const total=()=>state.shots.reduce((sum,shot)=>sum+shot.duration,0);
  const before=(index)=>state.shots.slice(0,index).reduce((sum,shot)=>sum+shot.duration,0);
  const visibleShots=()=>state.shots.filter(shot=>(sequenceFilter==='all'||shot.sequence===sequenceFilter)&&(statusFilter==='all'||shot.status===statusFilter));
  function assetValue(key){return ASSETS[key] || ASSETS[`${key}.png`] || ASSETS[`assets/${key}.png`] || `assets/${key}.png`;}
  function frameStyle(shot) {
    if(shot.customImage) return `background-image:url("${shot.customImage}");background-size:cover;background-position:center`;
    if(shot.imageIndex<0 || shot.imageIndex>31) return '';
    const atlas=`board-${String.fromCharCode(97+Math.floor(shot.imageIndex/8))}`;
    const cell=shot.imageIndex%8;
    return `background-image:var(--atlas-${Math.floor(shot.imageIndex/8)});background-size:200% 400%;background-position:${cell%2*100}% ${Math.floor(cell/2)/3*100}%`;
  }
  function frameClasses(shot){return `frame${shot.customImage?' custom-frame':shot.imageIndex<0?' no-image':''}`;}
  function frameOverlay(shot){return shot.endTitle||shot.endSubtitle?`<div class="frame-title-overlay" aria-hidden="true">${shot.endTitle?`<strong>${esc(shot.endTitle)}</strong>`:''}${shot.endSubtitle?`<span>${esc(shot.endSubtitle)}</span>`:''}</div>`:'';}
  function frameDescription(shot){return `Illustrative frame: ${shot.title}. ${shot.action}${shot.endTitle?' On-screen title: '+shot.endTitle+'.':''}${shot.endSubtitle?' '+shot.endSubtitle+'.':''}`;}
  function setFrame(element,shot){element.className=element.className.replace(/\s(custom-frame|no-image)/g,'');if(shot.customImage)element.classList.add('custom-frame');else if(shot.imageIndex<0)element.classList.add('no-image');element.style.cssText=frameStyle(shot);element.setAttribute('aria-label',frameDescription(shot));element.innerHTML=frameOverlay(shot);}

  function renderBranding() {
    const staleSource=!!initial.sourceRevision&&state.sourceRevision!==initial.sourceRevision;
    $('source-warning').hidden=!staleSource;
    $('source-warning').textContent=staleSource?'These browser edits came from a different file version. Use Export → Save complete project to preserve them before Restore original board loads the rebuilt file. To keep these edits in the project source, import that saved HTML with the Rua storyboard command, then rebuild.':'';
    const brand=text(CONFIG.brand || 'Rua');
    document.title=`${state.title} · Director’s storyboard`;
    $('brand-home').firstChild.textContent=brand.toUpperCase();
    $('brand-home').setAttribute('aria-label',`${brand} storyboard home`);
    $('brand-strapline').textContent=text(CONFIG.strapline || 'Director’s storyboard');
    $('studio-signature').firstChild.textContent=text(CONFIG.studio || 'Rua');
    $('studio-byline').textContent=text(CONFIG.byline || 'Director’s workspace');
    $('project-eyebrow').textContent=text(CONFIG.eyebrow || 'Storyboard');
    const lines=Array.isArray(CONFIG.heroTitleLines)&&state.title===initial.title?CONFIG.heroTitleLines.filter(line=>typeof line==='string'):[];
    $('film-title').replaceChildren();
    if(lines.length){
      lines.forEach((line,i)=>{
        if(i)$('film-title').append(document.createElement('br'));
        const node=document.createElement(i?'em':'span');node.textContent=line;$('film-title').append(node);
      });
    }else $('film-title').textContent=state.title;
    $('hero-deck').textContent=text(CONFIG.heroDeck || state.subtitle);
    $('arc-heading').textContent=text(CONFIG.arcHeading || 'The film, panel by panel.');
    $('workflow-intro').textContent=text(CONFIG.workflowIntro || 'Work through the staging, record decisions, then test the timing against the chosen track.');
    const principles=Array.isArray(CONFIG.principles)?CONFIG.principles.filter(item=>item&&typeof item==='object'):[];
    $('principle-grid').hidden=!principles.length;
    $('principle-grid').replaceChildren(...principles.map((principle,i)=>{
      const article=document.createElement('article'),number=document.createElement('span'),title=document.createElement('h3'),detail=document.createElement('p');
      number.className='principle-number';number.textContent=String(i+1).padStart(2,'0');
      title.textContent=text(principle.title);detail.textContent=text(principle.detail);
      article.append(number,title,detail);return article;
    }));
    $('footer-brand').textContent=brand.toUpperCase();
    $('footer-title').textContent=state.title.toUpperCase();
    $('project-footer').textContent=text(CONFIG.footer || 'Director’s working storyboard · Rua');
    $('presentation-brand').firstChild.textContent=brand.toUpperCase()+' ';
    $('presentation-film-title').textContent=state.title.toUpperCase();
    $('presentation-version').textContent=state.version;
  }
  function renderSummary() {
    const seconds=total();
    $('total-runtime').textContent=mmss(seconds);
    $('shot-count').textContent=String(state.shots.length).padStart(2,'0');
    $('version-label').textContent=state.version;
    const min=CONFIG.runtimeMin!=null&&Number.isFinite(Number(CONFIG.runtimeMin))&&Number(CONFIG.runtimeMin)>=0?Number(CONFIG.runtimeMin):null;
    const max=CONFIG.runtimeMax!=null&&Number.isFinite(Number(CONFIG.runtimeMax))&&Number(CONFIG.runtimeMax)>0?Number(CONFIG.runtimeMax):null;
    const brief=min!=null&&max!=null?`${min}–${max} sec brief`:max!=null?`${max} sec maximum`:min!=null?`${min} sec minimum`:'';
    $('format-label').textContent=state.format+(brief?' · '+brief:'');
    $('runtime-note').textContent=max!=null&&seconds>max?`${durationLabel(seconds-max)} over the ${max}-second treatment ceiling. Trim panels or agree a longer cut.`:min!=null&&seconds<min?`${durationLabel(min-seconds)} below the ${min}-second treatment floor. Timings remain provisional.`:(brief?`Within the ${brief}. `:'')+'Timing is provisional until the track is chosen.';
    $('runtime-note').classList.toggle('over-budget',max!=null&&seconds>max);
    const open=state.decisions.filter(d=>!['Agreed','Resolved','Approved'].includes(d.status)).length;
    document.querySelector('.decision-count').textContent=open;
  }
  function renderTimeline(){
    $('arc-timeline').innerHTML=state.sequences.map(seq=>{const secs=state.shots.filter(s=>s.sequence===seq.id).reduce((n,s)=>n+s.duration,0);return `<button class="timeline-sequence${sequenceFilter===seq.id?' active':''}" data-filter-sequence="${esc(seq.id)}" style="flex-grow:${Math.max(secs,5)};--seq-color:${seqColor(seq.id)}" aria-label="Show ${esc(seq.title)}, ${durationLabel(secs)}"><span class="timeline-bar"></span><span class="timeline-label"><strong>${esc(seq.id)} · ${esc(seq.title)}</strong><span>${durationLabel(secs)}</span></span></button>`;}).join('');
  }
  function renderFilters(){
    $('sequence-filters').innerHTML=`<button class="filter-button${sequenceFilter==='all'?' active':''}" data-filter-sequence="all" aria-pressed="${sequenceFilter==='all'}">All panels</button>`+state.sequences.map(seq=>`<button class="filter-button${sequenceFilter===seq.id?' active':''}" data-filter-sequence="${esc(seq.id)}" aria-pressed="${sequenceFilter===seq.id}">${esc(seq.id)} · ${esc(seq.title)}</button>`).join('');
    $('status-filter').value=statusFilter;
  }
  function renderCards(){
    const shots=visibleShots();
    $('filter-summary').textContent=`${shots.length} of ${state.shots.length} panels${sequenceFilter!=='all'?' · '+sequence(sequenceFilter).description:''}${statusFilter!=='all'?' · '+statusFilter:''}`;
    $('empty-state').hidden=shots.length>0;
    $('storyboard-grid').innerHTML=shots.map(shot=>{
      const position=state.shots.findIndex(s=>s.id===shot.id);const start=before(position);const seq=sequence(shot.sequence);
      return `<article class="shot-card" tabindex="0" role="button" data-shot-id="${esc(shot.id)}" aria-label="Edit ${esc(shot.id)}: ${esc(shot.title)}, ${durationLabel(shot.duration)}, ${esc(shot.status)}" style="--seq-color:${seqColor(shot.sequence)}"><div class="shot-card-head"><span class="shot-id"><span class="sequence-dot"></span>${esc(shot.id)}</span><span>${esc(seq.id)} · ${esc(seq.title)}</span><span class="shot-position">${String(position+1).padStart(2,'0')}</span></div>${shot.notes?'<div class="shot-note-mark">NOTE ADDED</div>':''}<div class="${frameClasses(shot)}" role="img" aria-label="${esc(frameDescription(shot))}" style="${esc(frameStyle(shot))}">${frameOverlay(shot)}${shot.priority==='Optional'?'<span class="frame-badge">OPTIONAL BEAT</span>':''}</div><div class="shot-body"><div class="shot-framing">${esc(shot.framing||'Framing to decide')}</div><h3>${esc(shot.title)}</h3><p class="shot-action">${esc(shot.action||'Add the action and blocking for this panel.')}</p><div class="shot-footer"><span class="shot-time">${mmss(start)}–${mmss(start+shot.duration)}<span class="shot-duration">${durationLabel(shot.duration)}</span></span><span class="status-pill ${slug(shot.status)}">${esc(shot.status)}</span></div></div></article>`;
    }).join('');
  }
  function renderNotes(){
    $('project-summary').textContent=state.summary;
    $('decisions-list').innerHTML=state.decisions.map((d,i)=>`<article class="decision-card"><div class="decision-card-head"><h3>${esc(d.title)}</h3><select class="decision-status" data-decision-index="${i}" aria-label="Status for ${esc(d.title)}">${[...new Set([d.status||'Open','Open','In discussion','Agreed'])].map(status=>`<option${d.status===status?' selected':''}>${esc(status)}</option>`).join('')}</select></div><div class="decision-owner">${esc(d.owner||'Director / client')}</div><p>${esc(d.detail)}</p>${d.sourceStatus?`<p class="source-status"><strong>Source status:</strong> ${esc(d.sourceStatus)}</p>`:''}<label>Decision / feedback<textarea rows="2" data-decision-note="${i}" aria-label="Notes for ${esc(d.title)}" placeholder="Record the outcome or a question…">${esc(d.notes||'')}</textarea></label></article>`).join('');
    $('references-list').innerHTML=state.references.map(ref=>{const url=safeURL(ref.url);return `<div class="reference-item">${url?`<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(ref.label)} <span aria-hidden="true">↗</span></a>`:`<strong>${esc(ref.label)}</strong>`}<p>${esc(ref.note)}</p></div>`;}).join('');
    $('glossary-list').innerHTML=state.glossary.map(g=>`<dt>${esc(g.term)}</dt><dd>${esc(g.definition)}</dd>`).join('');
    $('workflow-list').innerHTML=state.workflow.map(w=>`<li><h3>${esc(w.title)}</h3><p>${esc(w.detail)}</p></li>`).join('');
  }
  function renderAll(){$('audio-start').value=state.audioStartSeconds;renderBranding();renderSummary();renderTimeline();renderFilters();renderCards();renderNotes();}
  function setView(next){
    view=next;
    ['board','notes','workflow'].forEach(name=>{const active=name===view;$(name+'-view').hidden=!active;document.querySelectorAll(`[data-view="${name}"]`).forEach(button=>{if(button.classList.contains('nav-button')){button.classList.toggle('active',active);if(active)button.setAttribute('aria-current','page');else button.removeAttribute('aria-current');}});});
    if(view!=='board') window.scrollTo({top:document.querySelector('.workspace-toolbar').offsetTop-20,behavior:'smooth'});
  }
  function filterBySequence(id){sequenceFilter=id;renderFilters();renderTimeline();renderCards();}
  function lockBackground(locked){document.querySelector('main').inert=locked;document.querySelector('.masthead').inert=locked;document.querySelector('.site-footer').inert=locked;document.body.style.overflow=locked?'hidden':'';}
  function openDrawer(id){
    const shot=state.shots.find(s=>s.id===id);if(!shot)return;
    if(activeModal!=='drawer')returnFocus=document.activeElement;
    editingId=id;activeModal='drawer';$('drawer-backdrop').hidden=false;$('shot-drawer').hidden=false;lockBackground(true);populateDrawer();$('shot-drawer').scrollTop=0;$('close-drawer').focus();
  }
  function populateDrawer(){
    const shot=state.shots.find(s=>s.id===editingId);if(!shot)return;
    $('drawer-id').textContent=`PANEL ${shot.id} · ${state.shots.findIndex(s=>s.id===shot.id)+1} OF ${state.shots.length}`;
    $('drawer-title').textContent=shot.title;setFrame($('drawer-frame'),shot);
    $('edit-sequence').innerHTML=state.sequences.map(seq=>`<option value="${esc(seq.id)}">${esc(seq.id+' · '+seq.title)}</option>`).join('');
    for(const key of ['title','sequence','duration','status','priority','framing','action','camera','sound','transition','continuity','decision','notes','endTitle','endSubtitle'])$('edit-'+key).value=shot[key]??'';
    $('edit-provenance').textContent=shot.provenance || 'Added by the director in this working board.';
    $('restore-frame').hidden=!shot.customImage;
    updateMoveButtons();
  }
  function updateMoveButtons(){const index=state.shots.findIndex(s=>s.id===editingId);$('move-earlier').disabled=index<=0;$('move-later').disabled=index>=state.shots.length-1;}
  function closeDrawer(){
    if(activeModal!=='drawer')return;
    const closingId=editingId;
    $('shot-drawer').hidden=true;$('drawer-backdrop').hidden=true;editingId=null;activeModal=null;lockBackground(false);
    const returnedCard=Array.from(document.querySelectorAll('[data-shot-id]')).find(el=>el.dataset.shotId===closingId);
    if(returnFocus?.isConnected)returnFocus.focus();else if(returnedCard)returnedCard.focus();else $('add-shot').focus();
  }
  function nextId(){let n=1;while(state.shots.some(s=>s.id===`S${String(n).padStart(2,'0')}`))n++;return `S${String(n).padStart(2,'0')}`;}
  function addShot(){
    const id=nextId();const seq=sequenceFilter==='all'?state.sequences[state.sequences.length-1].id:sequenceFilter;
    const shot={id,sequence:seq,title:'New panel',duration:2,framing:'',action:'',camera:'',sound:'',transition:'',continuity:'',decision:'',provenance:'Director-added panel. Proposed staging; check against the treatment and recce.',status:'Proposed',priority:'Essential',imageIndex:-1,notes:''};
    const lastInSeq=state.shots.map(s=>s.sequence).lastIndexOf(seq);state.shots.splice(lastInSeq+1,0,shot);statusFilter='all';renderAll();scheduleSave();openDrawer(id);$('edit-title').focus();$('edit-title').select();
  }
  function moveShot(delta){
    const index=state.shots.findIndex(s=>s.id===editingId);const target=index+delta;if(target<0||target>=state.shots.length)return;
    [state.shots[index],state.shots[target]]=[state.shots[target],state.shots[index]];renderSummary();renderTimeline();renderCards();populateDrawer();scheduleSave();toast(`Panel moved ${delta<0?'earlier':'later'} in the film.`);
  }
  function duplicateShot(){const index=state.shots.findIndex(s=>s.id===editingId);if(index<0)return;const copy=clone(state.shots[index]);copy.id=nextId();copy.title+=' · alternate';copy.status='Proposed';state.shots.splice(index+1,0,copy);editingId=copy.id;renderAll();populateDrawer();scheduleSave();toast('Panel duplicated. Both versions count toward the runtime.');}
  function deleteShot(){const index=state.shots.findIndex(s=>s.id===editingId);if(index<0)return;if(state.shots.length===1){toast('Keep at least one panel in the board.');return;}if(!window.confirm(`Delete ${state.shots[index].id}: ${state.shots[index].title}? Export a backup first if you want to keep this version.`))return;state.shots.splice(index,1);closeDrawer();renderAll();scheduleSave();toast('Panel deleted.');}

  function presentationRender(){
    if(!state.shots.length)return;presentIndex=Math.min(Math.max(presentIndex,0),state.shots.length-1);const shot=state.shots[presentIndex];const seq=sequence(shot.sequence);
    setFrame($('present-frame'),shot);$('present-sequence').textContent=`${seq.id} · ${seq.title} / ${shot.id}`;$('present-title').textContent=shot.title;$('present-framing').textContent=shot.framing+(shot.camera?' · '+shot.camera:'');$('present-action').textContent=shot.action||'Action to decide.';$('present-sound').textContent=shot.sound||'Sound to decide.';$('present-counter').textContent=`${String(presentIndex+1).padStart(2,'0')} / ${String(state.shots.length).padStart(2,'0')}`;$('present-frame-label').textContent=`${shot.id} · ${durationLabel(shot.duration)} · ILLUSTRATIVE FRAME`;$('present-prev').disabled=presentIndex===0;$('present-next').disabled=presentIndex===state.shots.length-1;updateProgress();
    requestAnimationFrame(fitPresentationFrame);
  }
  function fitPresentationFrame(){if(activeModal!=='presentation')return;const stage=$('present-frame').parentElement;const cs=getComputedStyle(stage);const maxW=stage.clientWidth-parseFloat(cs.paddingLeft)-parseFloat(cs.paddingRight);if(window.innerWidth<=540){$('present-frame').style.width='100%';$('present-frame').style.height='auto';return;}const maxH=stage.clientHeight-parseFloat(cs.paddingTop)-parseFloat(cs.paddingBottom);const w=Math.min(maxW,maxH*16/9);$('present-frame').style.width=w+'px';$('present-frame').style.height=w*9/16+'px';}
  function updateProgress(){const seconds=before(presentIndex)+elapsedInShot;const percent=total()?Math.min(100,seconds/total()*100):0;$('present-time').textContent=`${mmss(seconds)} / ${mmss(total())}`;$('present-progress').firstElementChild.style.width=percent+'%';$('present-progress').setAttribute('aria-valuenow',String(Math.round(percent)));}
  function openPresentation(){if(!state.shots.length){toast('Add a panel first.');return;}closeDrawer();returnFocus=document.activeElement;activeModal='presentation';presentIndex=0;elapsedInShot=0;$('presentation').hidden=false;lockBackground(true);presentationRender();$('close-presentation').focus();}
  function closePresentation(){if(activeModal!=='presentation')return;pausePreview();$('presentation').hidden=true;activeModal=null;lockBackground(false);if(returnFocus?.isConnected)returnFocus.focus();else $('present-button').focus();}
  function setPresentationIndex(index){const wasPlaying=playing;pausePreview();presentIndex=Math.max(0,Math.min(index,state.shots.length-1));elapsedInShot=0;presentationRender();syncAudio();if(wasPlaying)playPreview();}
  function audioMix() {
    const mix=state.videoExportSettings?.audio || {};
    return {enabled:mix.enabled!==false,trimIn:Math.max(0,Number(mix.trimIn)||0),trimOut:mix.trimOut==null?null:Math.max(0,Number(mix.trimOut)||0),offset:state.audioStartSeconds,gainDb:Math.max(-60,Math.min(0,Number(mix.gainDb)||0)),fadeIn:Math.max(0,Number(mix.fadeIn)||0),fadeOut:Math.max(0,Number(mix.fadeOut)||0)};
  }
  function syncAudio(seek=true){
    if(!tempAudio)return;
    const mix=audioMix();
    const boardTime=before(presentIndex)+elapsedInShot;
    const sourceEnd=Math.min(mix.trimOut??Infinity,Number.isFinite(tempAudio.duration)?tempAudio.duration:Infinity);
    const audibleEnd=Math.min(total(),mix.offset+Math.max(0,sourceEnd-mix.trimIn));
    const audibleDuration=Math.max(0,audibleEnd-mix.offset);
    const trackTime=boardTime-mix.offset+mix.trimIn;
    if(!mix.enabled||boardTime<mix.offset||boardTime>=audibleEnd){tempAudio.pause();if(seek)try{tempAudio.currentTime=mix.trimIn;}catch{}return;}
    const fadeIn=Math.min(mix.fadeIn,audibleDuration);
    const fadeOut=Math.min(mix.fadeOut,audibleDuration);
    const envelope=Math.min(1,fadeIn?(boardTime-mix.offset)/fadeIn:1,fadeOut?(audibleEnd-boardTime)/fadeOut:1);
    tempAudio.volume=Math.max(0,Math.min(1,Math.pow(10,mix.gainDb/20)*envelope));
    try{if(seek||Math.abs(tempAudio.currentTime-trackTime)>.75)tempAudio.currentTime=Math.max(0,trackTime);}catch{}
    if(playing&&tempAudio.paused&&!audioPlayPending&&!audioPlaybackFailed){
      const audio=tempAudio;audioPlayPending=true;
      audio.play().catch(()=>{if(tempAudio===audio){audioPlaybackFailed=true;toast('The audio could not play. Pause and play again, or try another audio file.');}}).finally(()=>{audioPlayPending=false;});
    }
  }
  function playPreview(){
    if(playing)return;
    if(presentIndex===state.shots.length-1 && elapsedInShot>=state.shots[presentIndex].duration){presentIndex=0;elapsedInShot=0;presentationRender();}
    playing=true;previousTick=performance.now();$('play-preview').textContent='Ⅱ Pause';$('play-preview').setAttribute('aria-label','Pause timed board preview');
    audioPlaybackFailed=false;syncAudio();
    previewTimer=setInterval(()=>{
      const now=performance.now();elapsedInShot+=(now-previousTick)/1000;previousTick=now;
      while(elapsedInShot>=state.shots[presentIndex].duration){
        const duration=state.shots[presentIndex].duration;
        if(presentIndex===state.shots.length-1){elapsedInShot=duration;pausePreview();updateProgress();return;}
        elapsedInShot-=duration;presentIndex++;presentationRender();
      }
      syncAudio(false);updateProgress();
    },100);
  }
  function pausePreview(){playing=false;clearInterval(previewTimer);previewTimer=null;if(tempAudio)tempAudio.pause();$('play-preview').textContent='▶ Play';$('play-preview').setAttribute('aria-label','Play timed board preview');}
  function releaseAudio(){
    pausePreview();
    if(tempAudio){tempAudio.pause();tempAudio.src='';tempAudio=null;}
    if(audioObjectURL){URL.revokeObjectURL(audioObjectURL);audioObjectURL=null;}
    tempAudioBlob=null;tempAudioName='';audioPlayPending=false;audioPlaybackFailed=false;
  }
  function updateAudioLabel(saved=true){
    $('clear-audio').hidden=!tempAudioBlob;
    $('audio-label').textContent=tempAudioBlob?`Temp track: ${tempAudioName} · ${saved?'saved on this browser':'attached for this session'} · included in video export`:'Timed board preview — music not attached';
    $('load-audio').textContent=tempAudioBlob?'Change audio':'＋ Temp audio';
    if($('music-status'))$('music-status').textContent=tempAudioBlob?'Temp music attached':'Music pending';
  }
  function showAudioWarning(message=''){$('audio-warning').textContent=message;$('audio-warning').hidden=!message;}
  function persistAudio(value){
    audioSaveChain=audioSaveChain.then(()=>new Promise(resolve=>{
      if(!db){resolve(false);return;}
      try{const tx=db.transaction('boards','readwrite');const store=tx.objectStore('boards');
        store.put(value||{removed:true},STORAGE_KEY+':audio');
        tx.oncomplete=()=>resolve(true);tx.onerror=()=>resolve(false);tx.onabort=()=>resolve(false);
      }catch{resolve(false);}
    }));
    return audioSaveChain;
  }
  async function attachAudio(blob,name,persist=true){
    if(!(blob instanceof Blob)||!blob.size)throw new Error('Choose a non-empty MP3, WAV or M4A file.');
    if(blob.size>200*1024*1024)throw new Error('Choose a temp track smaller than 200 MB.');
    releaseAudio();tempAudioBlob=blob;tempAudioName=name||'Temp soundtrack';
    audioObjectURL=URL.createObjectURL(blob);tempAudio=new Audio(audioObjectURL);tempAudio.preload='auto';
    tempAudio.addEventListener('error',()=>toast('This audio format could not play. Try an MP3 or WAV file.',6000));
    updateAudioLabel(!persist);
    if(persist){
      const ok=await persistAudio({blob,name:tempAudioName});
      if(tempAudioBlob===blob){updateAudioLabel(ok);showAudioWarning(ok?'':'This track is attached for this session, but browser storage could not keep it. Save a complete project before closing this page.');}
      return ok;
    }
    return true;
  }
  async function clearAudio(){
    releaseAudio();updateAudioLabel();$('audio-input').value='';
    const removed=await persistAudio(null);
    showAudioWarning(removed?'':'The track was removed for this session, but browser storage could not save its removal. Save a complete project before closing; the old track may return when you reopen this file.');
    return removed;
  }
  function embeddedAudioBlob(value){
    const match=typeof value==='string'&&value.match(/^data:([^;,]*);base64,([A-Za-z0-9+/=]+)$/);
    if(!match)throw new Error('The bundled soundtrack could not be read.');
    const binary=atob(match[2]),bytes=new Uint8Array(binary.length);
    for(let i=0;i<binary.length;i++)bytes[i]=binary.charCodeAt(i);
    return new Blob([bytes],{type:match[1]||'application/octet-stream'});
  }
  async function restoreAudio(){
    const stored=db?await new Promise(resolve=>{try{const req=db.transaction('boards','readonly').objectStore('boards').get(STORAGE_KEY+':audio');req.onsuccess=()=>resolve(req.result);req.onerror=()=>resolve(null);}catch{resolve(null);}}):null;
    if(stored?.removed)return;
    try{
      if(stored?.blob instanceof Blob)await attachAudio(stored.blob,stored.name,false);
      else if(window.STORYBOARD_AUDIO?.data)await attachAudio(embeddedAudioBlob(window.STORYBOARD_AUDIO.data),window.STORYBOARD_AUDIO.name,true);
    }catch{toast('The saved soundtrack could not be restored. Choose the track again.');}
  }
  function initializeVideoExport(){
    if(!window.StoryboardVideoExport)return;
    videoExport=window.StoryboardVideoExport.init({
      getBoard:()=>clone(state),assets:ASSETS,
      getAudio:()=>tempAudioBlob?{blob:tempAudioBlob,name:tempAudioName}:null,
      setAudio:(blob,name)=>attachAudio(blob,name),clearAudio,
      getSettings:()=>({...clone(state.videoExportSettings||{}),audio:{...clone(state.videoExportSettings?.audio||{}),offset:state.audioStartSeconds}}),
      saveSettings:(settings)=>{state.videoExportSettings=clone(settings);state.audioStartSeconds=Math.max(0,Number(settings.audio?.offset)||0);$('audio-start').value=state.audioStartSeconds;scheduleSave();},
      pausePresentation:pausePreview,
      onOpen:()=>{exportReturnFocus=document.activeElement;closeDrawer();closePresentation();activeModal='export';lockBackground(true);$('export-menu').hidden=true;$('export-button').setAttribute('aria-expanded','false');},
      onClose:()=>{activeModal=null;lockBackground(false);if(exportReturnFocus?.isConnected&&exportReturnFocus.offsetParent!==null)exportReturnFocus.focus();else $('export-button').focus();},
      toast
    });
  }

  function download(content,type,name){const blob=new Blob([content],{type});const url=URL.createObjectURL(blob);const anchor=document.createElement('a');anchor.href=url;anchor.download=name;document.body.appendChild(anchor);anchor.click();anchor.remove();setTimeout(()=>URL.revokeObjectURL(url),2000);}
  function exportJSON(){download(JSON.stringify({...state,exportedAt:new Date().toISOString()},null,2),'application/json',`${exportPrefix}-Storyboard-${new Date().toISOString().slice(0,10)}.json`);toast('Editable backup exported, including your uploaded frames.');}
  async function textResource(path){const res=await fetch(path);if(!res.ok)throw new Error(`Could not read ${path}`);return res.text();}
  async function imageAsDataURL(path){const res=await fetch(path);if(!res.ok)throw new Error(`Could not read ${path}`);const blob=await res.blob();return new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result);reader.onerror=reject;reader.readAsDataURL(blob);});}
  const embeddedJSON=(value)=>JSON.stringify(value).replace(/</g,'\\u003c').replace(/\u2028/g,'\\u2028').replace(/\u2029/g,'\\u2029');
  async function exportHTML(includeAudio=false){
    const button=$(includeAudio?'export-project':'export-html');button.disabled=true;
    const snapshot=clone(state),track=includeAudio&&tempAudioBlob?{blob:tempAudioBlob,name:tempAudioName}:null;
    toast(includeAudio?'Saving your complete project, including attached music…':'Preparing a single-file presentation…',12000);
    try{
      let css=window.STORYBOARD_CSS || Array.from(document.styleSheets).map(sheet=>{try{return Array.from(sheet.cssRules).map(rule=>rule.cssText).join('\n');}catch{return '';}}).join('\n');
      if(!css.trim())css=await textResource('styles.css');
      let js=window.STORYBOARD_APP_SOURCE || document.querySelector('script[data-storyboard-app]')?.textContent;
      if(!js)js=await textResource('app.js');
      const videoScripts=await Promise.all(['video-engine','video-export'].map(async name=>({name,source:document.querySelector(`script[data-storyboard-${name}]`)?.textContent || await textResource(name+'.js')})));
      const bundledAudio=track?{name:track.name,data:await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result);reader.onerror=()=>reject(new Error('The soundtrack could not be read.'));reader.readAsDataURL(track.blob);})}:null;
      const assets={};
      for(const [key,value] of Object.entries(ASSETS)) assets[key]=value.startsWith('data:')?value:await imageAsDataURL(value);
      const root=document.documentElement.cloneNode(true);
      root.removeAttribute('style');
      root.querySelectorAll('script').forEach(node=>node.remove());
      root.querySelectorAll('link[rel="stylesheet"],style').forEach(node=>node.remove());
      const style=document.createElement('style');style.textContent=css;root.querySelector('head').appendChild(style);
      root.querySelector('#video-export-dialog')?.remove();
      const clonedBody=root.querySelector('body');clonedBody.style.overflow='';
      root.querySelectorAll('[inert]').forEach(node=>node.removeAttribute('inert'));
      ['shot-drawer','drawer-backdrop','presentation','toast','storage-warning','audio-warning','source-warning','export-menu'].forEach(id=>{const el=root.querySelector('#'+id);if(el)el.hidden=true;});
      root.querySelector('#storyboard-grid').innerHTML='';root.querySelector('#print-board').innerHTML='';
      root.querySelector('#export-html').disabled=false;root.querySelector('#export-project').disabled=false;root.querySelector('#export-button').setAttribute('aria-expanded','false');
      root.querySelector('#reset-board').disabled=false;
      root.querySelector('#clear-audio').hidden=true;root.querySelector('#audio-label').textContent='Timed board preview — music not attached';root.querySelector('#load-audio').textContent='＋ Temp audio';
      const payload=document.createElement('script');payload.textContent=`window.STORYBOARD_CONFIG=${embeddedJSON(CONFIG)};window.STORYBOARD_STORAGE_KEY=${embeddedJSON((slug(exportPrefix)||'storyboard')+'-shared-'+Date.now()+'-'+Math.random().toString(36).slice(2,8))};window.STORYBOARD_DATA=${embeddedJSON(snapshot)};window.STORYBOARD_ASSETS=${embeddedJSON(assets)};window.STORYBOARD_AUDIO=${embeddedJSON(bundledAudio)};`;
      clonedBody.appendChild(payload);
      if(root.querySelector('#music-status'))root.querySelector('#music-status').textContent='Music pending';
      for(const item of videoScripts){const script=document.createElement('script');script.setAttribute('data-storyboard-'+item.name,'');script.textContent=item.source.replace(/<\/script/gi,'<\\/script');clonedBody.appendChild(script);}
      const program=document.createElement('script');program.setAttribute('data-storyboard-app','');program.textContent=js.replace(/<\/script/gi,'<\\/script');clonedBody.appendChild(program);
      download('<!doctype html>\n'+root.outerHTML,'text/html',`${exportPrefix}-${includeAudio?'Complete-Project':'Storyboard-Presentation'}-${new Date().toISOString().replace(/[:.]/g,'-')}.html`);
      toast(includeAudio?(track?'Complete project saved: board, images, music and export settings. Open that HTML file to continue anywhere.':'Complete project saved: board, images and export settings. No music was attached.'): 'Shareable HTML exported. It includes the board and frames; temp audio is not included.',8000);
      return true;
    }catch(error){toast('HTML export could not read the local assets. Use the bundled standalone file, or export a JSON backup.',8000);console.error('Standalone export:',error);return false;}finally{button.disabled=false;}
  }
  async function restoreOriginalBoard(){
    if(resetInProgress||!window.confirm('Restore this file’s board and music, including no music if the file has none? Your current board, images, music and settings will first download as a complete-project HTML backup.'))return;
    resetInProgress=true;$('reset-board').disabled=true;lockBackground(true);
    const previousAudio=tempAudioBlob?{blob:tempAudioBlob,name:tempAudioName}:null;
    try{
      const fileAudio=window.STORYBOARD_AUDIO?.data?{blob:embeddedAudioBlob(window.STORYBOARD_AUDIO.data),name:window.STORYBOARD_AUDIO.name}:null;
      if(fileAudio&&(!fileAudio.blob.size||fileAudio.blob.size>200*1024*1024))throw new Error('The file’s bundled soundtrack is empty or larger than 200 MB.');
      if(!await exportHTML(true)){toast('Restore stopped because the complete-project backup could not be created. Your current board and music are unchanged.',8000);return;}
      const audioSaved=fileAudio?await attachAudio(fileAudio.blob,fileAudio.name,true):await clearAudio();
      if(!audioSaved){
        if(previousAudio)await attachAudio(previousAudio.blob,previousAudio.name,false);
        else{releaseAudio();updateAudioLabel();}
        showAudioWarning('Restore stopped because browser storage could not save the file’s music state. Your previous board and music remain here, and a complete-project backup was downloaded.');
        toast('Restore stopped. Your previous board and music were kept.',8000);return;
      }
      state=clone(initial);sequenceFilter='all';statusFilter='all';renderAll();scheduleSave();
      toast('File board and music restored. Your previous project was downloaded as a complete HTML backup.',8000);
    }catch(error){showAudioWarning('Restore stopped: '+error.message);toast('Restore stopped. Your current project has not been replaced.',8000);}
    finally{resetInProgress=false;$('reset-board').disabled=false;lockBackground(false);}
  }
  function renderPrintBoard(){
    const pages=[];
    for(let i=0;i<state.shots.length;i+=4){
      pages.push(`<section class="print-page"><div class="print-page-header"><strong>${esc(state.title)}</strong><span>${esc(state.version)} · ${mmss(total())} · ${Math.floor(i/4)+1}/${Math.ceil(state.shots.length/4)}</span></div><div class="print-grid">${state.shots.slice(i,i+4).map((shot,j)=>`<article class="print-shot"><div class="${frameClasses(shot)}" style="${esc(frameStyle(shot))}">${frameOverlay(shot)}</div><div class="print-shot-body"><div class="print-meta">${esc(shot.id)} · ${esc(sequence(shot.sequence).title)} · ${mmss(before(i+j))}–${mmss(before(i+j)+shot.duration)} · ${durationLabel(shot.duration)} · ${esc(shot.status)}</div><h3>${esc(shot.title)}</h3><div class="print-meta">${esc(shot.framing)}</div><p>${esc(shot.action)}</p><p class="print-small"><strong>Camera:</strong> ${esc(shot.camera)}</p><p class="print-small"><strong>Sound:</strong> ${esc(shot.sound)}</p>${shot.decision?`<p class="print-small"><strong>Decision:</strong> ${esc(shot.decision)}</p>`:''}${shot.notes?`<p class="print-small"><strong>Notes:</strong> ${esc(shot.notes)}</p>`:''}</div></article>`).join('')}</div><p class="print-footnote">${esc(CONFIG.studio || "Rua")} · Illustrative frames / proposed staging / ${tempAudioBlob?"music attached":"music pending"}. Printed ${new Date().toLocaleDateString('en-IE')}. All panels included, regardless of screen filters.</p></section>`);
    }
    pages.push(`<section class="print-page print-notes"><div class="print-page-header"><strong>Director’s decisions</strong><span>${esc(state.title)} · ${esc(state.version)}</span></div>${state.decisions.map(d=>`<article class="print-decision"><h3>${esc(d.title)} · ${esc(d.status||'Open')}</h3><p><strong>${esc(d.owner||'Director / client')}</strong></p><p>${esc(d.detail)}</p>${d.sourceStatus?`<p><strong>Source status:</strong> ${esc(d.sourceStatus)}</p>`:''}${d.notes?`<p><strong>Outcome / notes:</strong> ${esc(d.notes)}</p>`:''}</article>`).join('')}</section>`);
    $('print-board').innerHTML=pages.join('');
  }

  async function processImage(file){
    if(!['image/jpeg','image/png','image/webp'].includes(file.type))throw new Error('Choose a JPG, PNG or WebP image.');
    if(file.size>30*1024*1024)throw new Error('Choose an image smaller than 30 MB.');
    const data=await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result);reader.onerror=()=>reject(new Error('The image could not be read.'));reader.readAsDataURL(file);});
    return new Promise((resolve,reject)=>{const img=new Image();img.onload=()=>{try{const scale=Math.min(1,1800/Math.max(img.width,img.height));const canvas=document.createElement('canvas');canvas.width=Math.round(img.width*scale);canvas.height=Math.round(img.height*scale);const ctx=canvas.getContext('2d');ctx.fillStyle='#f4f1e8';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.drawImage(img,0,0,canvas.width,canvas.height);resolve(canvas.toDataURL('image/jpeg',.88));}catch{reject(new Error('The image could not be prepared.'));}};img.onerror=()=>reject(new Error('The image could not be decoded.'));img.src=data;});
  }

  document.addEventListener('click',(event)=>{
    const target=event.target.closest('[data-view]');if(target)setView(target.dataset.view);
    const filter=event.target.closest('[data-filter-sequence]');if(filter)filterBySequence(filter.dataset.filterSequence);
    const card=event.target.closest('[data-shot-id]');if(card)openDrawer(card.dataset.shotId);
    if(!event.target.closest('.export-menu-wrap')){$('export-menu').hidden=true;$('export-button').setAttribute('aria-expanded','false');}
  });
  $('storyboard-grid').addEventListener('keydown',(event)=>{const card=event.target.closest('[data-shot-id]');if(card&&['Enter',' '].includes(event.key)){event.preventDefault();openDrawer(card.dataset.shotId);}});
  $('status-filter').addEventListener('change',event=>{statusFilter=event.target.value;renderCards();});
  $('clear-filters').addEventListener('click',()=>{statusFilter='all';filterBySequence('all');});
  $('add-shot').addEventListener('click',addShot);
  $('close-drawer').addEventListener('click',closeDrawer);$('done-editing').addEventListener('click',closeDrawer);$('drawer-backdrop').addEventListener('click',closeDrawer);
  $('shot-form').addEventListener('submit',event=>event.preventDefault());
  $('shot-form').addEventListener('input',event=>{
    const key=event.target.name;if(!key||!editingId)return;const shot=state.shots.find(s=>s.id===editingId);if(!shot)return;
    if(key==='duration'){const value=Number(event.target.value);if(!event.target.value||!Number.isFinite(value)||value<.2||value>600)return;shot.duration=Math.round(value*10)/10;}else shot[key]=event.target.value;
    if(key==='title')$('drawer-title').textContent=shot.title;
    if(key==='endTitle'||key==='endSubtitle')setFrame($('drawer-frame'),shot);
    renderSummary();renderTimeline();renderCards();scheduleSave();
  });
  $('edit-duration').addEventListener('blur',event=>{const shot=state.shots.find(s=>s.id===editingId);if(shot)event.target.value=shot.duration;});
  $('move-earlier').addEventListener('click',()=>moveShot(-1));$('move-later').addEventListener('click',()=>moveShot(1));$('duplicate-shot').addEventListener('click',duplicateShot);$('delete-shot').addEventListener('click',deleteShot);
  $('replace-frame').addEventListener('click',()=>$('frame-input').click());
  $('frame-input').addEventListener('change',async event=>{const file=event.target.files[0];const id=editingId;if(!file||!id)return;try{const data=await processImage(file);const shot=state.shots.find(s=>s.id===id);if(!shot)return;shot.customImage=data;shot.customImageName=file.name;if(editingId===id){setFrame($('drawer-frame'),shot);$('restore-frame').hidden=false;}renderCards();scheduleSave();toast('Frame replaced. Export a JSON backup to keep a portable copy.');}catch(error){toast(error.message,6000);}finally{event.target.value='';}});
  $('restore-frame').addEventListener('click',()=>{const shot=state.shots.find(s=>s.id===editingId);if(!shot)return;delete shot.customImage;delete shot.customImageName;setFrame($('drawer-frame'),shot);$('restore-frame').hidden=true;renderCards();scheduleSave();});
  $('decisions-list').addEventListener('change',event=>{if(event.target.dataset.decisionIndex!==undefined){state.decisions[Number(event.target.dataset.decisionIndex)].status=event.target.value;renderSummary();scheduleSave();}});
  $('decisions-list').addEventListener('input',event=>{if(event.target.dataset.decisionNote!==undefined){state.decisions[Number(event.target.dataset.decisionNote)].notes=event.target.value;scheduleSave();}});
  $('present-button').addEventListener('click',openPresentation);$('close-presentation').addEventListener('click',closePresentation);$('present-prev').addEventListener('click',()=>setPresentationIndex(presentIndex-1));$('present-next').addEventListener('click',()=>setPresentationIndex(presentIndex+1));$('play-preview').addEventListener('click',()=>playing?pausePreview():playPreview());
  $('load-audio').addEventListener('click',()=>$('audio-input').click());$('clear-audio').addEventListener('click',clearAudio);
  $('audio-input').addEventListener('change',async event=>{
    const file=event.target.files[0];if(!file)return;
    if(!file.type.startsWith('audio/')&&!/\.(mp3|m4a|wav|aac|aif|aiff|ogg|flac)$/i.test(file.name)){toast('Choose an audio file such as MP3, WAV or M4A.');return;}
    try{await attachAudio(file,file.name);if(state.videoExportSettings?.audio){state.videoExportSettings.audio.trimIn=0;state.videoExportSettings.audio.trimOut=null;state.videoExportSettings.audio.enabled=true;scheduleSave();}toast(`Temp audio attached locally. It starts at ${mmss(state.audioStartSeconds)} of the board.`);}catch(error){toast(error.message,6000);}finally{event.target.value='';}
  });
  $('audio-start').addEventListener('change',event=>{const value=Number(event.target.value);if(!event.target.value||!Number.isFinite(value)||value<0||value>600){event.target.value=state.audioStartSeconds;return;}state.audioStartSeconds=Math.round(value*10)/10;if(state.videoExportSettings?.audio)state.videoExportSettings.audio.offset=state.audioStartSeconds;event.target.value=state.audioStartSeconds;audioPlaybackFailed=false;syncAudio();scheduleSave();});
  window.addEventListener('resize',fitPresentationFrame);
  document.addEventListener('visibilitychange',()=>{if(document.hidden&&playing)pausePreview();});
  document.addEventListener('keydown',event=>{
    if(activeModal==='export')return;
    if(event.key==='Escape'){if(activeModal==='drawer')closeDrawer();else if(activeModal==='presentation')closePresentation();else{$('export-menu').hidden=true;$('export-button').setAttribute('aria-expanded','false');}return;}
    if(activeModal==='presentation' && !['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)){if(event.key==='ArrowRight'){event.preventDefault();setPresentationIndex(presentIndex+1);}else if(event.key==='ArrowLeft'){event.preventDefault();setPresentationIndex(presentIndex-1);}else if(event.key===' '){event.preventDefault();playing?pausePreview():playPreview();}}
    if(event.key==='Tab'&&activeModal){const container=$(activeModal==='drawer'?'shot-drawer':'presentation');const focusable=Array.from(container.querySelectorAll('button:not(:disabled),a[href],input,select,textarea,[tabindex="0"]')).filter(el=>!el.hidden&&el.offsetParent!==null);const first=focusable[0],last=focusable[focusable.length-1];if(event.shiftKey&&document.activeElement===first){event.preventDefault();last?.focus();}else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first?.focus();}}
  });
  $('export-button').addEventListener('click',()=>{$('export-menu').hidden=!$('export-menu').hidden;$('export-button').setAttribute('aria-expanded',String(!$('export-menu').hidden));});
  for(const id of ['export-video','present-export-video'])$(id)?.addEventListener('click',()=>videoExport?videoExport.open():toast('Video export is still loading. Try again in a moment.'));
  $('export-project').addEventListener('click',()=>{$('export-menu').hidden=true;exportHTML(true);});
  $('export-json').addEventListener('click',()=>{$('export-menu').hidden=true;exportJSON();});$('export-html').addEventListener('click',()=>{$('export-menu').hidden=true;exportHTML();});$('print-button').addEventListener('click',()=>{$('export-menu').hidden=true;renderPrintBoard();window.print();});
  $('import-button').addEventListener('click',()=>$('json-input').click());
  $('json-input').addEventListener('change',async event=>{const file=event.target.files[0];if(!file)return;try{if(file.size>100*1024*1024)throw new Error('The backup is too large. Please choose a file smaller than 100 MB.');const candidate=validateImport(JSON.parse(await file.text()));exportJSON();state=candidate;sequenceFilter='all';statusFilter='all';renderAll();scheduleSave();toast(`Imported ${state.shots.length} panels. Your previous edited board was backed up if needed.`,6000);}catch(error){toast('Import stopped: '+error.message,8000);}finally{event.target.value='';}});
  $('reset-board').addEventListener('click',restoreOriginalBoard);
  window.addEventListener('beforeprint',renderPrintBoard);
  window.addEventListener('beforeunload',()=>{try{state.savedAt=Date.now();localStorage.setItem(STORAGE_KEY,JSON.stringify(state));}catch{}});

  db=await openDatabase();
  let local=null;try{const saved=localStorage.getItem(STORAGE_KEY);if(saved)local=JSON.parse(saved);}catch{}
  const indexed=await dbRead();
  const saved=[local,indexed].filter(Boolean).sort((a,b)=>(b.savedAt||0)-(a.savedAt||0))[0];
  if(saved){try{state=validateImport(saved);}catch{showStorageWarning('A previous browser save could not be read. The original board is loaded; import a JSON backup if you have one.');}}
  renderAll();setView('board');
  await restoreAudio();
  initializeVideoExport();
  if(!state.shots.length)showStorageWarning('The storyboard data has not loaded yet. Keep storyboard-data.js alongside this page, or import an editable backup.');
  if(!saved) scheduleSave();
})();
