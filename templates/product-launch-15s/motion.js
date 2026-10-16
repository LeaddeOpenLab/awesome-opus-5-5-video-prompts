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
  function logo(x,y,s=30){box(x,y,s,s,s*.29,accent());text(Array.from(config.productName)[0]||'G',x+s/2,y+s*.74,s*.67,'#fff',600,s*.8,'center');}
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
    frame(t,'LAUNCH / PRODUCT INTRODUCTION',t<3.7?'01 — MEET THE PRODUCT':t<10.5?'02 — THREE REASONS':'03 — TRY IT');
    fade(1-at(t,3.4,4.0),()=>{
      pill(config.releaseLabel,71,205,210,accent(),true);
      const ey=heading(config.headline,71,314,590,67);
      text(config.subline,74,ey+54,20,muted,400,550);
      fade(at(t,.2,1.2),()=>{
        ctx.save();ctx.translate(934,379+(1-at(t,.2,1.2))*60);ctx.rotate(mix(-.1,.035,at(t,.2,1.2)));
        ctx.shadowColor='#1d254a16';ctx.shadowBlur=35;box(-221,-183,442,326,23,'#fff',line);ctx.shadowBlur=0;
        if(!screenshot(-203,-165,406,290)){
          logo(-185,-146,37);text(config.productName,-133,-119,23,ink,600,300);
          box(-185,-78,369,116,12,'#F0EDFF');text(config.featureOne,-162,-10,31,accent(),600,320);
          for(let i=0;i<3;i++){box(-185+i*128,57,112,54,9,i===1?accent():'#ECEAF1');if(i===1)check(-129+i*128,84,24,'#fff');else segment(-162+i*128,84,-103+i*128,84,'#C3BDCF',4);}
        }ctx.restore();
      });
    });
    fade(at(t,3.5,4.1)*(1-at(t,10.1,10.7)),()=>{
      text(config.editorTitle,640,160,45,ink,600,1110,'center');
      text(config.editorSubtitle,640,202,19,muted,400,1100,'center');
      [config.featureOne,config.featureTwo,config.featureThree].forEach((s,i)=>{
        const v=at(t,4.1+i*.6,4.9+i*.6),x=69+i*387,y=273+(1-v)*40;
        fade(v,()=>{
          box(x,y,368,308,18,'#fff',line);text('0'+(i+1),x+26,y+38,12,muted,500,100);
          const pulse=at(t,5.8+i*.6,6.8+i*.6);
          if(i===0){for(let k=0;k<3;k++){box(x+91,y+69+k*29,185,21,5,k===0?accent():'#EAE6F6');box(x+102,y+78+k*29,Math.max(2,(140-k*33)*pulse),3,1,k===0?'#fff':'#A79BBC');}}
          if(i===1){dot(x+153,y+112,32,'#EAE6F6');dot(x+210,y+112,32,accent());segment(x+160,y+112,x+203,y+112,'white',5);}
          if(i===2){box(x+116,y+70,136,91,12,'#F0EDFF');const cy=y+128-35*pulse;segment(x+184,y+139,x+184,cy,accent(),6);segment(x+184,cy,x+166,cy+18,accent(),6);segment(x+184,cy,x+202,cy+18,accent(),6);}
          text(s,x+26,y+224,27,ink,600,316);
          text([config.detailOne,config.detailTwo,config.detailThree][i],x+26,y+262,16,muted,400,316);
        });
      });
    });
    fade(at(t,10.3,11),()=>{
      const enter=at(t,10.3,11.5);logo(610,170+(1-enter)*12,60);
      text(config.endHeadline,640,329,63,ink,600,1120,'center');
      text(config.subline,640,380,21,muted,400,1050,'center');
      cta(440,437,400);text(config.website,640,541,20,muted,400,1040,'center');
      text(config.releaseLabel,640,590,12,accent(),600,1000,'center');
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
