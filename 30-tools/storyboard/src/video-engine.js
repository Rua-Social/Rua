/* Local storyboard animatic renderer. Uses browser encoders; no media leaves the page. */
(function () {
  'use strict';
  const clamp=(value,min,max)=>Math.min(max,Math.max(min,value));
  const number=(value,fallback)=>Number.isFinite(Number(value))?Number(value):fallback;
  const AudioContextClass=window.AudioContext || window.webkitAudioContext;
  const abortError=()=>new DOMException('Video export cancelled.','AbortError');
  function getFormats(){
    if(!window.MediaRecorder || !HTMLCanvasElement.prototype.captureStream)return [];
    const candidates=[
      {id:'mp4-h264',label:'MP4 · H.264 / AAC',extension:'mp4',types:['video/mp4;codecs=avc1.640034,mp4a.40.2','video/mp4;codecs=avc1,mp4a.40.2','video/mp4;codecs=avc1.640028,mp4a.40.2']},
      {id:'webm-vp9',label:'WebM · VP9 / Opus',extension:'webm',types:['video/webm;codecs=vp9,opus']},
      {id:'webm-vp8',label:'WebM · VP8 / Opus',extension:'webm',types:['video/webm;codecs=vp8,opus']}
    ];
    return candidates.map(format=>{const mimeType=format.types.find(type=>{try{return MediaRecorder.isTypeSupported(type);}catch{return false;}});return mimeType?{id:format.id,label:format.label,extension:format.extension,mimeType}:null;}).filter(Boolean);
  }
  function imageSource(shot,assets){
    if(shot.customImage)return {url:shot.customImage,cell:null};
    if(Number.isInteger(shot.imageIndex)&&shot.imageIndex>=0&&shot.imageIndex<32){
      const key=`board-${String.fromCharCode(97+Math.floor(shot.imageIndex/8))}`;
      return {url:assets[key]||assets[key+'.png']||assets['assets/'+key+'.png']||'assets/'+key+'.png',cell:shot.imageIndex%8};
    }
    return null;
  }
  function loadImage(url){return new Promise((resolve,reject)=>{const img=new Image();img.onload=()=>resolve(img);img.onerror=()=>reject(new Error('A storyboard image could not be loaded. Reattach the image before exporting.'));img.src=url;});}
  function peaks(buffer){
    const result=new Array(256).fill(0),length=buffer.length;
    for(let channel=0;channel<buffer.numberOfChannels;channel++){
      const data=buffer.getChannelData(channel);
      for(let bin=0;bin<result.length;bin++){
        const start=Math.floor(bin*length/result.length),end=Math.floor((bin+1)*length/result.length);
        // Sample at most 2048 values per bin so long tracks do not stall the interface.
        const step=Math.max(1,Math.floor((end-start)/2048));
        for(let i=start;i<end;i+=step)result[bin]=Math.max(result[bin],Math.abs(data[i]));
      }
    }
    return result;
  }
  function timecode(time,fps){
    const frames=Math.max(0,Math.floor(time*fps+0.00001));
    return [Math.floor(frames/fps/3600),Math.floor(frames/fps/60)%60,Math.floor(frames/fps)%60,frames%fps].map(n=>String(n).padStart(2,'0')).join(':');
  }
  function lines(ctx,value,x,y,maxWidth,lineHeight,maxLines){
    const words=String(value||'').trim().split(/\s+/).filter(Boolean);
    let line='',lineCount=0;
    for(let i=0;i<words.length;i++){
      const next=line?line+' '+words[i]:words[i];
      if(ctx.measureText(next).width>maxWidth&&line){
        if(lineCount===maxLines-1){while(ctx.measureText(line+'…').width>maxWidth&&line.length)line=line.slice(0,-1);ctx.fillText(line+'…',x,y+lineCount*lineHeight);return;}
        ctx.fillText(line,x,y+lineCount*lineHeight);lineCount++;line=words[i];
      }else line=next;
    }
    if(line)ctx.fillText(line,x,y+lineCount*lineHeight);
  }
  function contain(ctx,img,sx,sy,sw,sh,x,y,w,h){const scale=Math.min(w/sw,h/sh);const dw=sw*scale,dh=sh*scale;ctx.drawImage(img,sx,sy,sw,sh,x+(w-dw)/2,y+(h-dh)/2,dw,dh);}
  function audioRange(audio,bufferDuration,boardDuration){
    const input=audio||{};
    const trimIn=clamp(number(input.trimIn,0),0,bufferDuration);
    const trimOut=clamp(input.trimOut==null?bufferDuration:number(input.trimOut,bufferDuration),trimIn,bufferDuration);
    const offset=clamp(number(input.offset,0),0,boardDuration);
    const duration=Math.max(0,Math.min(trimOut-trimIn,boardDuration-offset));
    let fadeIn=clamp(number(input.fadeIn,0),0,duration),fadeOut=clamp(number(input.fadeOut,0),0,duration);
    // Long fades meet in the middle instead of scheduling contradictory gain ramps.
    if(fadeIn+fadeOut>duration&&duration>0){const scale=duration/(fadeIn+fadeOut);fadeIn*=scale;fadeOut*=scale;}
    return {trimIn,trimOut,offset,duration,fadeIn,fadeOut,gain:Math.pow(10,clamp(number(input.gainDb,0),-60,0)/20)};
  }
  async function finishWebM(blob,seconds){
    // Chromium records a live WebM segment without Duration. Add it to the small
    // Info header so saved review copies have a finite duration in media players.
    const bytes=new Uint8Array(await blob.slice(0,262144).arrayBuffer());
    const read=(offset,id=false)=>{
      const first=bytes[offset];if(!first)return null;
      let n=1,mask=128;while(!(first&mask)&&n<=8){mask>>=1;n++;}
      if(n>8||offset+n>bytes.length)return null;
      let value=id?first:first&(mask-1),unknown=!id&&value===mask-1;
      for(let i=1;i<n;i++){value=value*256+bytes[offset+i];unknown=unknown&&bytes[offset+i]===255;}
      return {value,n,unknown};
    };
    const element=offset=>{const id=read(offset,true);if(!id)return null;const size=read(offset+id.n);if(!size)return null;return {id:id.value,start:offset,sizeAt:offset+id.n,sizeLength:size.n,size:size.value,unknown:size.unknown,data:offset+id.n+size.n,end:offset+id.n+size.n+size.value};};
    const sizeBytes=(value,n)=>{if(value>=Math.pow(2,7*n)-1)return null;const out=new Uint8Array(n);for(let i=n-1;i>=0;i--){out[i]=value%256;value=Math.floor(value/256);}out[0]|=1<<(8-n);return out;};
    const ebml=element(0),segment=ebml&&element(ebml.end);
    if(!segment||segment.id!==0x18538067||!segment.unknown)return blob;
    let info=null;
    for(let at=segment.data;at<bytes.length;){const el=element(at);if(!el||el.unknown||el.end>bytes.length)return blob;if(el.id===0x114d9b74)return blob; // A SeekHead would need offset rewriting.
      if(el.id===0x1549a966){info=el;break;}at=el.end;}
    if(!info)return blob;
    let scale=1000000;
    for(let at=info.data;at<info.end;){const el=element(at);if(!el||el.unknown||el.end>info.end)return blob;if(el.id===0x4489)return blob;if(el.id===0x2ad7b1){scale=0;for(let i=el.data;i<el.end;i++)scale=scale*256+bytes[i];}at=el.end;}
    const size=sizeBytes(info.size+11,info.sizeLength);if(!size||!scale)return blob;
    const duration=new Uint8Array(11);duration.set([0x44,0x89,0x88]);new DataView(duration.buffer).setFloat64(3,seconds*1e9/scale,false);
    return new Blob([blob.slice(0,info.sizeAt),size,blob.slice(info.data,info.end),duration,blob.slice(info.end)],{type:blob.type});
  }
  async function prepare(board,assets,audioBlob){
    const shots=(board?.shots||[]).map(shot=>({...shot,duration:number(shot.duration,0)}));
    if(!shots.length||shots.some(shot=>shot.duration<=0))throw new Error('The storyboard needs panels with positive durations before it can be exported.');
    const duration=shots.reduce((sum,shot)=>sum+shot.duration,0);
    if(!Number.isFinite(duration))throw new Error('The board duration is invalid.');
    const imagePromises=new Map();
    const sourceList=shots.map(shot=>{const source=imageSource(shot,assets||{});if(source&&!imagePromises.has(source.url))imagePromises.set(source.url,loadImage(source.url));return source;});
    const images=new Map();
    let audioBuffer=null;
    const decode=async()=>{
      if(!audioBlob)return;
      if(!AudioContextClass)throw new Error('This browser cannot decode the music. Try a current desktop browser, or export without music.');
      let context;
      try{
        const Offline=window.OfflineAudioContext||window.webkitOfflineAudioContext;
        context=Offline?new Offline(2,1,48000):new AudioContextClass();
        audioBuffer=await context.decodeAudioData(await audioBlob.arrayBuffer());
      }catch(error){throw new Error('This browser could not read the music file. Try an MP3, WAV or AAC file, or export without music.');}
      finally{if(context?.close)await context.close().catch(()=>{});}
    };
    await Promise.all([decode(),...Array.from(imagePromises,async([url,promise])=>images.set(url,await promise))]);
    const starts=[];let sum=0;for(const shot of shots){starts.push(sum);sum+=shot.duration;}
    let disposed=false,activeExport=null;
    function draw(canvas,time,settings={}){
      if(disposed)throw new Error('This export session has closed. Reopen the video exporter.');
      const ctx=canvas.getContext('2d',{alpha:false});if(!ctx)throw new Error('Canvas rendering is unavailable in this browser.');
      const w=canvas.width,h=canvas.height,s=w/1920;
      let index=shots.length-1;const at=clamp(number(time,0),0,duration);
      for(let i=0;i<shots.length;i++){if(at<starts[i]+shots[i].duration){index=i;break;}}
      const shot=shots[index],review=settings.layout==='review';
      ctx.save();ctx.fillStyle='#111713';ctx.fillRect(0,0,w,h);ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';
      const frame=review?{x:w*.035,y:h*.135,w:w*.64,h:w*.64*9/16}:{x:0,y:0,w,h};
      ctx.fillStyle='#080b09';ctx.fillRect(frame.x,frame.y,frame.w,frame.h);
      const source=sourceList[index],img=source&&images.get(source.url);
      if(img){
        const sw=source.cell==null?img.naturalWidth:img.naturalWidth/2,sh=source.cell==null?img.naturalHeight:img.naturalHeight/4;
        contain(ctx,img,source.cell==null?0:(source.cell%2)*sw,source.cell==null?0:Math.floor(source.cell/2)*sh,sw,sh,frame.x,frame.y,frame.w,frame.h);
      }else{
        ctx.fillStyle='#788579';ctx.font=`${36*s}px sans-serif`;ctx.textAlign='center';ctx.fillText('FRAME TO FOLLOW',frame.x+frame.w/2,frame.y+frame.h/2);ctx.textAlign='left';
      }
      if(shot.endTitle||shot.endSubtitle){
        ctx.save();ctx.beginPath();ctx.rect(frame.x,frame.y,frame.w,frame.h);ctx.clip();
        const shade=ctx.createLinearGradient(0,frame.y+frame.h*.25,0,frame.y+frame.h);shade.addColorStop(0,'rgba(0,0,0,0)');shade.addColorStop(.6,'rgba(0,0,0,.58)');shade.addColorStop(1,'rgba(0,0,0,.74)');ctx.fillStyle=shade;ctx.fillRect(frame.x,frame.y,frame.w,frame.h);
        ctx.fillStyle='#fff9e9';ctx.textAlign='center';ctx.shadowColor='rgba(0,0,0,.7)';ctx.shadowBlur=8*s;
        let size=frame.w*.046;ctx.font=`600 ${size}px Georgia,serif`;while(shot.endTitle&&ctx.measureText(shot.endTitle).width>frame.w*.88&&size>14*s){size-=s;ctx.font=`600 ${size}px Georgia,serif`;}
        if(shot.endTitle)ctx.fillText(shot.endTitle,frame.x+frame.w/2,frame.y+frame.h*.70);
        if(shot.endSubtitle){ctx.font=`${frame.w*.025}px Georgia,serif`;ctx.fillText(shot.endSubtitle,frame.x+frame.w/2,frame.y+frame.h*.79,frame.w*.88);}
        ctx.restore();
      }
      if(settings.burnIn){
        const pad=frame.w*.02,fs=frame.w*.018,barHeight=fs*2.3;
        ctx.fillStyle='rgba(5,10,7,.76)';ctx.fillRect(frame.x,frame.y+frame.h-barHeight,frame.w,barHeight);
        ctx.fillStyle='#fff';ctx.font=`${fs}px ui-monospace,Menlo,monospace`;ctx.textBaseline='middle';ctx.fillText(`${shot.id}  ·  ${index+1}/${shots.length}`,frame.x+pad,frame.y+frame.h-barHeight/2);
        ctx.textAlign='right';ctx.fillText(timecode(at,clamp(Math.round(number(settings.fps,25)),1,60)),frame.x+frame.w-pad,frame.y+frame.h-barHeight/2);ctx.textAlign='left';ctx.textBaseline='alphabetic';
      }
      if(review){
        ctx.fillStyle='#a7bba6';ctx.font=`500 ${22*s}px sans-serif`;ctx.fillText(String(window.STORYBOARD_CONFIG?.brand || 'Rua').toUpperCase()+'  /  DIRECTOR’S STORYBOARD',w*.035,h*.058);
        ctx.textAlign='right';ctx.font=`${20*s}px sans-serif`;ctx.fillText(`${index+1} / ${shots.length}`,w*.965,h*.058);ctx.textAlign='left';
        ctx.fillStyle='#faf7ef';ctx.font=`600 ${34*s}px Georgia,serif`;lines(ctx,`${shot.id} · ${shot.title}`,w*.035,h*.105,w*.92,40*s,1);
        ctx.fillStyle='#c4cec2';ctx.font=`${25*s}px sans-serif`;lines(ctx,shot.framing||'Framing to be confirmed',w*.035,h*.835,w*.64,33*s,3);
        const rx=w*.715,rw=w*.25;
        for(const section of [{label:'ACTION',text:shot.action,y:.18,lines:7},{label:'CAMERA',text:shot.camera,y:.47,lines:4},{label:'SOUND',text:shot.sound,y:.68,lines:5}]){
          ctx.fillStyle='#a7bba6';ctx.font=`600 ${18*s}px sans-serif`;ctx.fillText(section.label,rx,h*section.y);
          ctx.fillStyle='#f4f3eb';ctx.font=`${24*s}px sans-serif`;lines(ctx,section.text||'—',rx,h*section.y+34*s,rw,32*s,section.lines);
        }
        ctx.fillStyle='#829180';ctx.font=`${18*s}px sans-serif`;ctx.fillText('Illustrative previs · Timing and coverage remain provisional',w*.035,h*.965);
      }
      ctx.restore();
      return {index,shotId:shot.id,time:at};
    }
    async function exportVideo(settings={},options={}){
      if(disposed)throw new Error('This export session has closed. Reopen the video exporter.');
      if(activeExport)throw new Error('An export is already running.');
      if(options.signal?.aborted)throw abortError();
      if(document.hidden)throw new Error('Keep this tab visible while the video exports.');
      const format=getFormats().find(item=>item.id===settings.formatId);
      if(!format)throw new Error('The selected video format is not supported by this browser. Choose one of the available formats.');
      const width=Math.round(number(settings.width,1920)),height=Math.round(number(settings.height,1080)),fps=Math.round(number(settings.fps,25));
      if(width<320||width>3840||height<180||height>2160||width%2||height%2||Math.abs(width/height-16/9)>.005||fps<1||fps>60)throw new Error('Choose a supported 16:9 size up to 3840 × 2160 and frame rate from 1 to 60 fps.');
      const canvas=document.createElement('canvas');canvas.width=width;canvas.height=height;draw(canvas,0,settings);
      let stream=canvas.captureStream(0),videoTrack=stream.getVideoTracks()[0];
      if(!videoTrack?.requestFrame){stream.getTracks().forEach(track=>track.stop());stream=canvas.captureStream(fps);videoTrack=stream.getVideoTracks()[0];}
      let context=null,source=null,silence=null,gain=null,destination=null,recorder=null,raf=0,stopTimer=0,stopGuard=0,settled=false,failed=null;
      const range=audioRange(settings.audio,audioBuffer?.duration||0,duration);
      const withAudio=Boolean(settings.audio?.enabled&&audioBuffer&&range.duration>0);
      let cancelled;
      const cancelPromise=new Promise((resolve,reject)=>{cancelled=reject;});
      // Consume the cancellation promise immediately; race below may attach a little later.
      cancelPromise.catch(()=>{});
      function cleanup(){
        cancelAnimationFrame(raf);clearTimeout(stopTimer);clearTimeout(stopGuard);
        document.removeEventListener('visibilitychange',onVisibility);options.signal?.removeEventListener('abort',onAbort);
        if(context)context.removeEventListener('statechange',onContextState);
        try{source?.stop();}catch{}try{silence?.stop();}catch{}try{source?.disconnect();silence?.disconnect();gain?.disconnect();destination?.disconnect();}catch{}
        stream.getTracks().forEach(track=>track.stop());
        if(context&&context.state!=='closed')context.close().catch(()=>{});
        canvas.width=1;canvas.height=1;activeExport=null;
      }
      function fail(error){
        if(settled||failed)return;failed=error;cancelAnimationFrame(raf);clearTimeout(stopTimer);
        try{source?.stop();}catch{}
        if(recorder&&recorder.state!=='inactive'){try{recorder.stop();}catch{}}
        cancelled(error);
      }
      function onAbort(){fail(abortError());}
      function onVisibility(){if(document.hidden)fail(new Error('Export stopped because the tab was hidden. Keep this tab visible and start the export again.'));}
      function onContextState(){if(context?.state!=='running')fail(new Error('The audio engine was interrupted. Keep this tab active and start the export again.'));}
      activeExport={cancel:onAbort};
      document.addEventListener('visibilitychange',onVisibility);options.signal?.addEventListener('abort',onAbort,{once:true});
      const report=(elapsed,message='Rendering video…')=>{try{options.onProgress?.({elapsed,duration,remaining:Math.max(0,duration-elapsed),progress:clamp(elapsed/duration,0,1),message});}catch{}};
      try{
        if(withAudio){
          if(!AudioContextClass)throw new Error('Audio export is not available in this browser.');
          // resume() begins synchronously while the Export button still has user activation.
          context=new AudioContextClass({sampleRate:48000});
          await Promise.race([context.resume(),cancelPromise]);
          if(context.state!=='running')throw new Error('Allow audio playback in this browser, then start export again.');
          destination=context.createMediaStreamDestination();gain=context.createGain();gain.connect(destination);
          // Keep the audio graph active through any silent tail after the selected music.
          silence=context.createConstantSource();silence.offset.value=0;silence.connect(destination);silence.start();
          source=context.createBufferSource();source.buffer=audioBuffer;source.connect(gain);
          destination.stream.getAudioTracks().forEach(track=>stream.addTrack(track));
          context.addEventListener('statechange',onContextState);
        }
        if(options.signal?.aborted)throw abortError();
        const chunks=[];
        try{recorder=new MediaRecorder(stream,{mimeType:format.mimeType,videoBitsPerSecond:clamp(number(settings.videoMbps,12),1,100)*1000000,...(withAudio?{audioBitsPerSecond:clamp(number(settings.audioKbps,192),64,320)*1000}:{})});}
        catch(error){throw new Error('The browser could not start this encoder. Try 1080p or 720p, a lower bitrate, or another available format.');}
        const result=new Promise((resolve,reject)=>{
          recorder.ondataavailable=event=>{if(event.data?.size)chunks.push(event.data);};
          recorder.onerror=event=>fail(new Error(`The video encoder stopped${event.error?.message?': '+event.error.message:'. Try a smaller size or a different format.'}`));
          recorder.onstop=()=>{
            clearTimeout(stopGuard);
            if(failed){reject(failed);return;}
            const mimeType=recorder.mimeType||format.mimeType;
            const blob=new Blob(chunks,{type:mimeType});
            if(!blob.size){reject(new Error('The encoder returned an empty video. Try a smaller size or a different format.'));return;}
            const extension=/mp4/i.test(mimeType)?'mp4':/webm/i.test(mimeType)?'webm':format.extension;
            resolve({blob,extension,mimeType,duration});
          };
          const beginTimeline=()=>{
            if(failed)return;
            const startTime=performance.now(),audioClockStart=context?.currentTime;let lastFrame=-1,lastReport=-1;
            const elapsedTime=now=>Math.max(0,withAudio?context.currentTime-audioClockStart:(now-startTime)/1000);
            if(withAudio){
              const begin=audioClockStart,end=begin+range.offset+range.duration,level=range.gain,start=begin+range.offset;
              gain.gain.setValueAtTime(range.fadeIn?0:level,start);
              if(range.fadeIn)gain.gain.linearRampToValueAtTime(level,start+range.fadeIn);
              if(range.fadeOut){gain.gain.setValueAtTime(level,end-range.fadeOut);gain.gain.linearRampToValueAtTime(0,end);}
              source.start(start,range.trimIn,range.duration);
            }
            videoTrack?.requestFrame?.();
            report(0);
            const tick=now=>{
              if(failed||settled)return;
              const elapsed=Math.min(duration,elapsedTime(now)),frameNumber=Math.floor(elapsed*fps);
              if(frameNumber!==lastFrame){draw(canvas,Math.min(elapsed,Math.max(0,duration-.00001)),settings);videoTrack?.requestFrame?.();lastFrame=frameNumber;}
              if(elapsed-lastReport>=.15){report(elapsed);lastReport=elapsed;}
              if(elapsed<duration)raf=requestAnimationFrame(tick);
            };
            raf=requestAnimationFrame(tick);
            const finishWhenDue=()=>{
              if(failed||settled)return;
              const remaining=duration-elapsedTime(performance.now());
              if(remaining>.006){stopTimer=setTimeout(finishWhenDue,Math.max(4,remaining*1000));return;}
              cancelAnimationFrame(raf);report(duration,'Finalising video…');
              try{recorder.stop();stopGuard=setTimeout(()=>fail(new Error('The encoder did not finish. Try a smaller size or a different format.')),15000);}catch(error){fail(error);}
            };
            stopTimer=setTimeout(finishWhenDue,duration*1000);
          };
          // The start event can arrive late while the encoder warms up. Anchor picture
          // and sound to the start() call so that startup latency cannot shift the cue.
          try{recorder.start(1000);beginTimeline();}catch(error){fail(new Error('The encoder could not begin recording. Try a smaller size or another available format.'));}
        });
        const output=await Promise.race([result,cancelPromise]);
        if(output.extension==='webm')output.blob=await finishWebM(output.blob,duration);
        if(options.signal?.aborted)throw abortError();
        settled=true;report(duration,'Video ready');return output;
      }finally{settled=true;cleanup();}
    }
    return {duration,audioDuration:audioBuffer?.duration||0,waveform:audioBuffer?peaks(audioBuffer):[],draw,export:exportVideo,dispose(){if(disposed)return;activeExport?.cancel();disposed=true;images.clear();audioBuffer=null;}};
  }
  window.StoryboardVideoEngine=Object.freeze({getFormats,prepare});
})();
