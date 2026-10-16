/* Original, deterministic animation. Edit config.js for copy and colors.
   Every frame comes from seek(seconds); no accumulated animation state. */
(() => {
  const canvas = document.querySelector('#film'), ctx = canvas.getContext('2d');
  ctx.setTransform(1.5,0,0,1.5,0,0); // Draw in 1280×720 units, render at native 1080p.
  const defaults = structuredClone(window.PRODUCT_CONFIG);
  let config = {...defaults}, shot = null, imageGeneration = 0;
  const ink = '#25252B', muted = '#817D88', line = '#EAE7EE';
  const clamp = (v, a=0, b=1) => Math.min(b, Math.max(a, v));
  const ease = v => {v=clamp(v); return v*v*v*(v*(v*6-15)+10);};
  const at = (t,a,b) => ease((t-a)/(b-a));
  const mix = (a,b,v) => a+(b-a)*v;
  const fade = (v,fn) => {if(v<=0)return;ctx.save();ctx.globalAlpha*=clamp(v);fn();ctx.restore();};
  const accent = () => config.accent;
  function box(x,y,w,h,r=16,fill='#fff',stroke=null){
    ctx.beginPath();ctx.roundRect(x,y,Math.max(0,w),Math.max(0,h),Math.max(0,Math.min(r,w/2,h/2)));
    if(fill){ctx.fillStyle=fill;ctx.fill();}if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=1;ctx.stroke();}
  }
  function dot(x,y,r,color){ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fillStyle=color;ctx.fill();}
  function segment(x,y,x2,y2,color,width=2){ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x2,y2);ctx.strokeStyle=color;ctx.lineWidth=width;ctx.lineCap='round';ctx.stroke();}
  function text(s,x,y,size=20,color=ink,weight=500,max=1100,align='left'){
    s=String(s); ctx.textBaseline='alphabetic';ctx.textAlign=align;
    ctx.font=`${weight} ${size}px Arial, "PingFang SC", sans-serif`;
    while(ctx.measureText(s).width>max && size>10){size-=0.5;ctx.font=`${weight} ${size}px Arial, "PingFang SC", sans-serif`;}
    ctx.fillStyle=color;ctx.fillText(s,x,y);ctx.textAlign='left';
  }
  function heading(s,x,y,w,size=62){
    const words=String(s).includes(' ')?String(s).split(' '):Array.from(String(s));
    const sep=String(s).includes(' ')?' ':'';
    let lines=[],row='';ctx.font=`600 ${size}px Arial, "PingFang SC", sans-serif`;
    for(const word of words){const candidate=row?row+sep+word:word;if(ctx.measureText(candidate).width>w&&row){lines.push(row);row=word;}else row=candidate;}if(row)lines.push(row);
    if(lines.length>2&&size>24)return heading(s,x,y,w,size-4);
    lines.forEach((l,i)=>text(l,x,y+i*size*1.12,size,ink,600,w));
    return y+(lines.length-1)*size*1.12;
  }
  function pill(s,x,y,w,color=accent(),light=false){box(x,y,w,36,18,light?'#fff':color,light?line:null);text(s,x+w/2,y+24,13,light?muted:'#fff',600,w-22,'center');}
  function check(x,y,s,color=accent()){segment(x-s*.35,y,x-s*.06,y+s*.27,color,s*.13);segment(x-s*.06,y+s*.27,x+s*.44,y-s*.32,color,s*.13);}
  function logo(x,y,s=30){box(x,y,s,s,s*.29,accent());segment(x+s*.27,y+s*.73,x+s*.27,y+s*.28,'#fff',s*.11);segment(x+s*.27,y+s*.28,x+s*.73,y+s*.28,'#fff',s*.11);segment(x+s*.27,y+s*.49,x+s*.58,y+s*.49,'#fff',s*.11);}
  function cursor(x,y,click=0){
    ctx.save();ctx.translate(x,y);ctx.scale(1-click*.1,1-click*.1);ctx.shadowColor='#0003';ctx.shadowBlur=5;ctx.shadowOffsetY=3;
    ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(0,26);ctx.lineTo(7,20);ctx.lineTo(13,32);ctx.lineTo(18,29);ctx.lineTo(12,17);ctx.lineTo(22,17);ctx.closePath();ctx.fillStyle=ink;ctx.fill();ctx.strokeStyle='white';ctx.lineWidth=2;ctx.stroke();ctx.restore();
    if(click>0){ctx.save();ctx.globalAlpha=click*.3;ctx.beginPath();ctx.arc(x,y,20+18*(1-click),0,7);ctx.strokeStyle=accent();ctx.lineWidth=2;ctx.stroke();ctx.restore();}
  }
  function screenshot(x,y,w,h){
    if(!shot)return false;
    const scale=Math.min(w/shot.naturalWidth,h/shot.naturalHeight),iw=shot.naturalWidth*scale,ih=shot.naturalHeight*scale;
    ctx.save();box(x,y,w,h,10,'#F2F0F5');ctx.beginPath();ctx.roundRect(x,y,w,h,10);ctx.clip();ctx.drawImage(shot,x+(w-iw)/2,y+(h-ih)/2,iw,ih);ctx.restore();return true;
  }

  function frame(t,label,step){
    ctx.clearRect(0,0,1280,720);ctx.fillStyle=config.background;ctx.fillRect(0,0,1280,720);
    logo(56,42,32);text(config.productName,100,66,23,ink,600,390);
    text(label,1224,63,12,muted,500,330,'right');
    text('15-SECOND STARTER / LEADDE OPEN LAB',56,680,10,muted,500,440);
    text(step,1224,680,10,muted,500,420,'right');
    box(56,700,1168,2,1,'#E4E0E8');box(56,700,1168*t/15,2,1,accent());
  }
  function cta(x,y,w){box(x,y,w,54,12,accent());text(config.cta+' →',x+w/2,y+35,19,'#fff',600,w-35,'center');}

  function draw(t){
    frame(t,'FEATURE / BEFORE & AFTER',t<4?'01 — THE PROBLEM':t<10.8?'02 — ONE ACTION':'03 — THE RESULT');
    const end=at(t,10.5,11.25);
    fade(1-end,()=>{
      text(t<4?config.headline:config.editorTitle,640,140,43,ink,600,1120,'center');
      text(t<4?config.subline:config.editorSubtitle,640,176,18,muted,400,1100,'center');
      const x=110,y=221,w=1060;
      box(x,y,w,365,18,'#fff',line);
      text(config.projectName,x+28,y+39,17,ink,600,600);
      pill('Sort by priority',x+w-214,y+14,184);
      segment(x,y+63,x+w,y+63,line,1);
      text('TASK',x+30,y+91,11,muted,600,400);text('PRIORITY',x+760,y+91,11,muted,600,150);
      const sort=at(t,5.4,7.4),dest=[2,0,3,1];
      const labels=[config.taskOne,config.taskTwo,config.taskThree,config.taskFour];
      const levels=['LOW','HIGH','LOW','HIGH'];
      for(let i=0;i<4;i++){
        const yy=y+111+mix(i,dest[i],sort)*55;
        const selected=i===1||i===3;
        box(x+17,yy,w-34,47,9,selected&&sort>.02?'#E9F4F1':'#F8F8F9');
        box(x+32,yy+15,16,16,4,'#fff','#D7DDE0');
        if(selected&&sort>.9)check(x+40,yy+23,12);
        text(labels[i],x+65,yy+31,18,ink,500,650);
        dot(x+771,yy+24,4,selected?accent():'#B4BAC1');
        text(levels[i],x+787,yy+29,11,selected?accent():muted,600,120);
        text('⋮',x+w-44,yy+30,19,muted);
      }
      fade(at(t,2.8,3.2)*(1-at(t,6.2,6.5)),()=>{
        const v=at(t,3.3,4.7);cursor(mix(820,1040,v),mix(528,256,v),Math.max(0,1-Math.abs(t-5.15)/.23));
      });
      fade(at(t,7.7,8.2),()=>{dot(640,621,13,accent());check(640,621,14,'#fff');text(config.resultNote,665,628,18,ink,500,490);});
    });
    fade(end,()=>{
      pill('ONE ACTION. CLEARER WORK.',70,218,260,accent(),true);
      const ey=heading(config.endHeadline,70,320,530,61);
      text(config.resultNote,72,ey+47,18,muted,400,510);
      cta(72,Math.max(470,ey+83),340);text(config.website,72,Math.max(470,ey+83)+90,17,muted,400,510);
      box(674,207,530,377,20,'#fff',line);
      if(!screenshot(696,229,486,333)){
        text(config.projectName,704,257,20,ink,600,450);
        text('FOCUS VIEW',704,287,11,muted,600,450);
        [config.taskTwo,config.taskFour].forEach((s,i)=>{box(701,310+i*82,474,65,10,'#E9F4F1');dot(726,342+i*82,11,accent());check(726,342+i*82,12,'#fff');text(s,752,349+i*82,18,ink,500,395);});
        text('The right work, first.',704,530,17,muted,400,450);
      }
    });
  }
  let time=0,playing=!new URLSearchParams(location.search).has('render'),last=performance.now();
  if(new URLSearchParams(location.search).has('render'))document.body.classList.add('render');
  const slider=document.querySelector('#time'),clock=document.querySelector('#clock'),play=document.querySelector('#play'),status=document.querySelector('#status');
  window.seek = seconds => {time=clamp(Number(seconds)||0,0,15);draw(time);slider.value=time;clock.textContent=time.toFixed(1)+' / 15 s';return time;};
  function sync(){document.querySelectorAll('[data-field]').forEach(el=>el.value=config[el.dataset.field]??'');document.documentElement.style.setProperty('--accent',config.accent);}
  window.setConfig = async patch => {
    config={...config,...patch};sync();
    if(Object.hasOwn(patch,'screenshot')){
      const generation=++imageGeneration;shot=null;
      if(config.screenshot){
        const im=new Image();
        try{await new Promise((resolve,reject)=>{im.onload=resolve;im.onerror=()=>reject(new Error('Screenshot could not be loaded.'));im.src=config.screenshot;});if(generation===imageGeneration)shot=im;}
        catch(e){if(generation===imageGeneration){config.screenshot='';status.textContent=e.message;}throw e;}
      }
    }
    window.seek(time);return {...config};
  };
  window.getConfig=()=>structuredClone(config);
  window.animationReady=window.setConfig(config);
  document.querySelectorAll('[data-field]').forEach(el=>el.addEventListener('input',()=>{window.setConfig({[el.dataset.field]:el.value});status.textContent='Preview updated. Save config.js to keep changes.';}));
  play.onclick=()=>{playing=!playing;if(playing&&time>=15)time=0;play.textContent=playing?'Pause':'Play';};
  slider.oninput=()=>{playing=false;play.textContent='Play';window.seek(slider.value);};
  document.querySelector('#replay').onclick=()=>{window.seek(0);playing=true;play.textContent='Pause';};
  document.querySelector('#reset').onclick=()=>{window.setConfig(structuredClone(defaults)).catch(()=>{});status.textContent='Reset to saved config.js.';};
  document.querySelector('#clearImage').onclick=()=>{window.setConfig({screenshot:''});document.querySelector('#upload').value='';status.textContent='Screenshot removed.';};
  document.querySelector('#upload').onchange=async e=>{
    const file=e.target.files[0];if(!file)return;
    const reader=new FileReader();reader.onload=()=>window.setConfig({screenshot:reader.result}).then(()=>status.textContent='Screenshot added. Save config.js to include it.').catch(()=>{});reader.readAsDataURL(file);
  };
  document.querySelector('#save').onclick=()=>{
    const blob=new Blob(['// Saved from the UI Motion Starter preview.\nwindow.PRODUCT_CONFIG = '+JSON.stringify(config,null,2)+';\n'],{type:'text/javascript'});
    const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='config.js';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status.textContent='Replace the template’s config.js with this download, then refresh.';
  };
  function loop(now){const dt=Math.min((now-last)/1000,.1);last=now;if(playing){window.seek(time+dt);if(time>=15){playing=false;play.textContent='Play';}}requestAnimationFrame(loop);}
  sync();window.seek(0);play.textContent=playing?'Pause':'Play';requestAnimationFrame(loop);
})();
