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
  function preview(x,y,w,h,t){
    if(screenshot(x,y,w,h))return;
    box(x,y,w,h,12,'#F5F3F8');
    const px=x+w*.07,py=y+h*.11;
    logo(px,py,24);text(config.productName,px+34,py+18,16,ink,600,w*.45);
    text('A space for your next idea.',px,py+59,23,ink,600,w*.84);
    const gap=12,cw=(w*.86-gap*2)/3,cy=py+80,ch=h*.43;
    for(let i=0;i<3;i++){
      const enter=at(t,4.2+i*.16,5.1+i*.16),dy=(1-enter)*18;
      fade(enter,()=>{
        box(px+i*(cw+gap),cy+dy,cw,ch,10,'#fff');
        dot(px+17+i*(cw+gap),cy+19+dy,5,i===1?accent():'#C6C0D6');
        text(['Plan','Create','Share'][i],px+14+i*(cw+gap),cy+48+dy,15,ink,600,cw-24);
        const bw=cw-28;
        box(px+14+i*(cw+gap),cy+62+dy,bw,5,2,'#EBE8F0');
        box(px+14+i*(cw+gap),cy+74+dy,bw*.62,5,2,'#EBE8F0');
      });
    }
  }
  function draw(t){
    ctx.clearRect(0,0,1280,720);ctx.fillStyle=config.background;ctx.fillRect(0,0,1280,720);
    // Quiet editorial frame, with a subtle moving accent rather than a busy background.
    ctx.save();ctx.globalAlpha=.035;dot(1175,60,260,accent());dot(70,735,200,accent());ctx.restore();
    logo(56,42,32);text(config.productName,100,66,23,ink,600,390);
    text('PRODUCT / IN MOTION',1224,63,12,muted,500,260,'right');
    const firstToEditor=at(t,2.95,4.05),editorToEnd=at(t,11.15,12.3);
    const intro=at(t,-.6,.3)*(1-at(t,2.65,3.05));
    fade(intro,()=>{
      pill('FROM IDEA TO PREVIEW',66,195,205,accent(),true);
      const end=heading(config.headline,66,304+(1-at(t,-.6,.3))*16,500,66);
      text(config.subline,68,end+49,20,muted,400,490);
      segment(68,518,139,518,accent(),3);text('01 / PICK A START',68,550,12,muted,600,400);
    });
    fade(at(t,3.7,4.15)*(1-at(t,10.8,11.15)),()=>{
      text(config.editorTitle,640,125,36,ink,600,920,'center');
      text(config.editorSubtitle,640,157,16,muted,400,920,'center');
    });
    const p={x:mix(mix(653,125,firstToEditor),86,editorToEnd),y:mix(mix(195,187,firstToEditor),246,editorToEnd),w:mix(mix(557,1030,firstToEditor),472,editorToEnd),h:mix(mix(380,446,firstToEditor),290,editorToEnd)};
    ctx.save();ctx.shadowColor='#30204B13';ctx.shadowBlur=45;ctx.shadowOffsetY=18;box(p.x,p.y,p.w,p.h,22,'#fff');ctx.restore();
    box(p.x,p.y,p.w,p.h,22,null,'#E4DFE9');
    // Carry a visual anchor through the shell's reflow, without overlapping text.
    fade(Math.sin(Math.PI*firstToEditor)*(1-editorToEnd),()=>logo(p.x+p.w/2-24,p.y+p.h/2-24,48));
    fade(Math.sin(Math.PI*editorToEnd),()=>{dot(p.x+p.w/2,p.y+p.h/2,38,'#F0EBFF');check(p.x+p.w/2,p.y+p.h/2,38);});
    // Contents crossfade while the same application shell changes size and position.
    fade((1-at(t,2.85,3.15))*at(t,-.4,.4),()=>{
      text('Choose a starting point',p.x+30,p.y+47,23,ink,600,p.w-60);
      text('Good ideas deserve a head start.',p.x+30,p.y+76,14,muted,400,p.w-60);
      const cw=(p.w-84)/3;
      for(let i=0;i<3;i++){
        const x=p.x+26+i*(cw+16),y=p.y+110;
        box(x,y,cw,180,12,i===0?'#F4F0FF':'#F7F6F8',i===0?accent():line);
        if(i===0){box(x+18,y+25,cw-36,68,8,accent());box(x+28,y+39,cw-56,5,2,'#ffffffaa');box(x+28,y+53,cw-70,5,2,'#ffffff66');box(x+28,y+70,30,10,4,'#fff');}
        if(i===1){dot(x+cw/2,y+58,28,'#DCD7E8');dot(x+cw/2+15,y+58,19,accent());}
        if(i===2){for(let j=0;j<3;j++)box(x+20+j*29,y+84-j*18,18,15+j*18,4,j===2?accent():'#DCD7E8');}
        text(['Product','Story','Overview'][i],x+14,y+133,16,ink,600,cw-28);
        text(['A clear introduction','One good idea','The bigger picture'][i],x+14,y+157,11,muted,400,cw-28);
        if(i===0)fade(at(t,1.75,2.05),()=>{dot(x+cw-15,y+15,11,accent());check(x+cw-15,y+15,11,'#fff');});
      }
      text('Choose template',p.x+30,p.y+p.h-31,13,muted,500,p.w-200);
      pill('Continue →',p.x+p.w-165,p.y+p.h-58,137);
    });
    fade(at(t,3.7,4.2)*(1-at(t,10.85,11.25)),()=>{
      segment(p.x+1,p.y+53,p.x+p.w-1,p.y+53,line,1);
      dot(p.x+25,p.y+26,4,'#DAD5E1');dot(p.x+40,p.y+26,4,'#DAD5E1');dot(p.x+55,p.y+26,4,'#DAD5E1');
      text(config.projectName,p.x+85,p.y+33,14,ink,500,p.w-340);
      const exporting=at(t,9.2,10.7);
      pill(t<9.2?'Export video':t<10.7?'Exporting…':'Exported ✓',p.x+p.w-164,p.y+10,141);
      text('YOUR STYLE',p.x+23,p.y+93,11,muted,600,140);
      text('Brand color',p.x+23,p.y+128,14,ink,500,140);
      for(let i=0;i<3;i++){dot(p.x+37+i*43,p.y+158,14,[accent(),'#29272D','#C7BEE1'][i]);if(i===0){ctx.beginPath();ctx.arc(p.x+37,p.y+158,19,0,7);ctx.strokeStyle=accent();ctx.lineWidth=1.5;ctx.stroke();}}
      text('Typography',p.x+23,p.y+209,14,ink,500,140);box(p.x+23,p.y+224,126,34,7,'#F8F7FA',line);text('Aa  /  Sans',p.x+34,p.y+247,13,ink,500,105);
      text('LAYOUT',p.x+23,p.y+301,11,muted,600,140);
      box(p.x+23,p.y+317,126,37,7,'#F4F0FF');text('16:9 · Landscape',p.x+33,p.y+341,12,accent(),600,106);
      segment(p.x+173,p.y+54,p.x+173,p.y+p.h-93,line,1);
      preview(p.x+194,p.y+74,p.w-222,p.h-188,t);
      const ty=p.y+p.h-84;segment(p.x+1,ty-10,p.x+p.w-1,ty-10,line,1);
      text('TIMELINE',p.x+24,ty+13,10,muted,600,140);
      const tx=p.x+194,tw=p.w-225;
      for(let i=0;i<4;i++){box(tx+i*tw/4+2,ty+6,tw/4-6,39,6,i===1?'#DCD3FC':'#EDE8F8');text(['Intro','Product','Details','Outro'][i],tx+i*tw/4+13,ty+31,12,'#716186',500,tw/4-30);}
      const progress=clamp((t-6.7)/3.9);
      segment(tx+tw*progress,ty,tx+tw*progress,ty+50,accent(),2);dot(tx+tw*progress,ty,3,accent());
      text(`${(15*progress).toFixed(1)}s / 15.0s`,p.x+25,ty+44,12,muted,500,150);
      if(t>=9.2){box(p.x+p.w-164,p.y+47,141,3,1,'#E8E2F7');box(p.x+p.w-164,p.y+47,141*exporting,3,1,accent());}
    });
    fade(at(t,12.0,12.45),()=>{
      const cx=p.x+p.w/2,cy=p.y+86;
      dot(cx,cy,41,'#F0EBFF');check(cx,cy,42);
      text('Export complete',cx,p.y+171,27,ink,600,p.w-62,'center');
      text('product-demo.mp4',cx,p.y+207,16,muted,400,p.w-62,'center');
      text('15 SEC   /   1080P   /   READY TO SHARE',cx,p.y+248,10,muted,600,p.w-62,'center');
      pill('MADE FOR YOUR NEXT LAUNCH',655,220,251,accent(),true);
      const end=heading(config.endHeadline,655,318,550,58);
      const ctaY=Math.max(405,end+42);
      box(655,ctaY,Math.min(490,Math.max(265,String(config.cta).length*12+60)),57,12,accent());
      text(config.cta+' →',679,ctaY+37,20,'#fff',600,442);
      text(config.website,657,ctaY+100,19,muted,400,535);
    });
    // Three deliberate pointer actions: choose, style, export.
    const pointerOpacity=at(t,1,1.3)*(1-at(t,9.7,10.2))*(1-at(t,2.7,3.0)+at(t,4.1,4.4));
    if(pointerOpacity>0)fade(pointerOpacity,()=>{
      let x,y;
      if(t<3){const v=at(t,1.1,1.7);x=mix(1150,725,v);y=mix(551,377,v);}
      else if(t<5.9){const v=at(t,3.6,4.8);x=mix(725,162,v);y=mix(377,345,v);}
      else {const v=at(t,7.8,9.1);x=mix(162,1075,v);y=mix(345,213,v);}
      const pulse=(center)=>Math.max(0,1-Math.abs(t-center)/.22);
      cursor(x,y,Math.max(pulse(1.8),pulse(4.9),pulse(9.2)));
    });
    text('UI MOTION STARTER',56,680,10,muted,500,400);
    text(t<3?'01 — START':t<11.2?'02 — CUSTOMIZE':'03 — SHARE',1224,680,10,muted,500,300,'right');
    ctx.save();ctx.globalAlpha=.2;box(56,700,1168,2,1,accent());ctx.restore();box(56,700,1168*t/15,2,1,accent());
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
