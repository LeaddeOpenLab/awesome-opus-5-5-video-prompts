/* ORBIT: a Codex-authored visual adaptation of Leadde's Product Launch template.
   15 s / 1920x1080 / deterministic Canvas 2D. Fictional product UI. */
(() => {
  const canvas=document.querySelector('#film'),ctx=canvas.getContext('2d');
  ctx.setTransform(1.5,0,0,1.5,0,0);
  const defaults=structuredClone(window.PRODUCT_CONFIG);
  let config={...defaults},shot=null,imageGeneration=0;
  const C={cream:'#F2EFE6',ink:'#11120F',muted:'#8D9185',line:'#30332B'};
  const clamp=(v,a=0,b=1)=>Math.min(b,Math.max(a,v));
  const ease=v=>{v=clamp(v);return v*v*v*(v*(v*6-15)+10);};
  const out=v=>1-Math.pow(1-clamp(v),3);
  const at=(t,a,b)=>ease((t-a)/(b-a));
  const mix=(a,b,p)=>a+(b-a)*p;
  const accent=()=>config.accent;
  const fade=(v,fn)=>{if(v<=0)return;ctx.save();ctx.globalAlpha*=clamp(v);fn();ctx.restore();};
  function box(x,y,w,h,r,fill,stroke){ctx.beginPath();ctx.roundRect(x,y,Math.max(0,w),Math.max(0,h),r);if(fill){ctx.fillStyle=fill;ctx.fill();}if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=1;ctx.stroke();}}
  function dot(x,y,r,color){ctx.beginPath();ctx.arc(x,y,Math.max(0,r),0,Math.PI*2);ctx.fillStyle=color;ctx.fill();}
  function line(x,y,x2,y2,color,w=1){ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x2,y2);ctx.strokeStyle=color;ctx.lineWidth=w;ctx.stroke();}
  function text(s,x,y,size=20,color=C.cream,weight=500,max=1100,align='left'){
    s=String(s);ctx.textBaseline='alphabetic';ctx.textAlign=align;
    ctx.font=`${weight} ${size}px "Helvetica Neue", Arial, "PingFang SC", sans-serif`;
    while(ctx.measureText(s).width>max&&size>10){size-=.5;ctx.font=`${weight} ${size}px "Helvetica Neue", Arial, "PingFang SC", sans-serif`;}
    ctx.fillStyle=color;ctx.fillText(s,x,y);ctx.textAlign='left';
  }
  function mono(s,x,y,size=12,color=C.muted,align='left'){ctx.font=`500 ${size}px Menlo,monospace`;ctx.textAlign=align;ctx.fillStyle=color;ctx.fillText(s,x,y);ctx.textAlign='left';}
  function arrow(x,y,s,color){line(x-s,y+s,x+s,y-s,color,3);line(x-s,y-s,x+s,y-s,color,3);line(x+s,y-s,x+s,y+s,color,3);}
  function orbit(x,y,r,t,color,fill=false){
    ctx.save();ctx.translate(x,y);ctx.rotate(-.42);
    if(fill)dot(0,0,r*.66,color);
    ctx.strokeStyle=color;ctx.lineWidth=2.3;
    for(let i=0;i<3;i++){ctx.beginPath();ctx.ellipse(0,0,r,r*(.31+i*.22),i*.64+t*.12,0,Math.PI*2);ctx.stroke();}
    const a=t*.65;dot(Math.cos(a)*r,Math.sin(a)*r*.56,Math.max(4,r*.042),color);ctx.restore();
  }
  function background(t,dark=true){
    ctx.fillStyle=dark?config.background:C.cream;ctx.fillRect(0,0,1280,720);
    ctx.fillStyle=dark?'#ffffff0a':'#11120f12';
    for(let x=32;x<1280;x+=32)for(let y=32;y<720;y+=32)ctx.fillRect(x,y,1,1);
  }
  function chrome(t,dark=true,label='DESIGNED TO MOVE'){
    const fg=dark?C.cream:C.ink,sub=dark?C.muted:'#66695F';
    orbit(73,58,15,t,accent());text(config.productName,101,66,20,fg,700,320);
    mono(label,1208,63,11,sub,'right');
    line(64,650,1216,650,dark?C.line:'#D5D4CB');
    mono('LEADDE OPEN LAB / CODEX EDITION',64,681,10,sub);
    mono('FICTIONAL PRODUCT',640,681,10,sub,'center');
    mono(String(Math.floor(clamp(t,0,14.99))).padStart(2,'0')+' / 15',1216,681,11,sub,'right');
    box(64,649,1152*t/15,2,0,accent());
  }
  function screenshot(x,y,w,h){if(!shot)return false;const s=Math.min(w/shot.naturalWidth,h/shot.naturalHeight);ctx.save();ctx.beginPath();ctx.roundRect(x,y,w,h,10);ctx.clip();ctx.drawImage(shot,x+(w-shot.naturalWidth*s)/2,y+(h-shot.naturalHeight*s)/2,shot.naturalWidth*s,shot.naturalHeight*s);ctx.restore();return true;}
  function intro(t){
    background(t);chrome(t,true,'A HOME FOR YOUR NEXT BIG IDEA');
    const p=out(t/1.0);
    ctx.save();ctx.beginPath();ctx.rect(64,126,870,328);ctx.clip();
    text(config.headline,65,280+(1-p)*110,142,C.cream,750,850);
    text('for the spark.',69,420+(1-out((t-.18)/1.1))*150,112,C.cream,400,840);
    ctx.restore();
    fade(at(t,.4,1.0),()=>{
      mono(config.releaseLabel,70,158,13,accent());
      text(config.subline,72,492,23,'#A4A89B',400,680);
      box(72,538,192,40,20,null,'#4C5044');mono('A NEW WAY TO NOTE',168,563,10,C.cream,'center');
    });
    ctx.save();ctx.beginPath();ctx.rect(880,112,400,520);ctx.clip();
    const scale=.74+.26*p;orbit(1083,350,209*scale,t,accent());
    dot(1083,350,62*scale,accent());
    ctx.restore();
    // A small floating idea slips into the orbit, foreshadowing the product cards.
    fade(at(t,.7,1.25),()=>{ctx.save();ctx.translate(1015+Math.sin(t)*15,507+Math.cos(t)*8);ctx.rotate(-.1);box(-87,-34,174,68,10,C.cream);mono('a good thought_',-65,5,11,C.ink);ctx.restore();});
  }
  function brand(t){
    ctx.fillStyle=accent();ctx.fillRect(0,0,1280,720);
    const local=t-3.0;
    mono('MEET YOUR NEW SPACE',64,87,13,C.ink);
    ctx.save();ctx.translate(640,365);ctx.scale(1+.04*Math.sin(clamp(local/1.4)*Math.PI),1);
    text(config.productName,0,65,230,C.ink,800,1120,'center');ctx.restore();
    line(68,525,1212,525,'#11120f55');text('Less scattered. More connected.',71,576,31,C.ink,500,900);
    arrow(1174,570,20,C.ink);mono('01 / CAPTURE THE MOMENT',70,667,11,C.ink);
  }
  function drawCard(i,t){
    const start=4.8+i*.22,p=out((t-start)/.78);
    if(p===0)return;
    const x=64+i*390,w=372,h=326,y=283+(1-p)*125;
    ctx.save();ctx.translate(x+w/2,y+h/2);ctx.rotate((1-p)*(i-1)*.1);ctx.globalAlpha*=p;
    const dark=i===1;
    ctx.shadowColor='#11120f16';ctx.shadowBlur=24;ctx.shadowOffsetY=12;
    box(-w/2,-h/2,w,h,18,dark?C.ink:'#FFFFFF');ctx.shadowBlur=0;ctx.shadowOffsetY=0;
    ctx.translate(-w/2,-h/2);
    mono('0'+(i+1),25,33,11,dark?C.muted:'#777C70');
    const a=accent();
    if(i===0){
      if(!screenshot(22,48,328,157)){
        const k=at(t,5.3,6.3);
        [[-6,0],[3,1],[0,2]].forEach(([angle,j])=>{
          const yy=59+j*37;
          ctx.save();ctx.translate(184,yy+19);ctx.rotate(angle*Math.PI/180);
          box(-130,-17,260,34,6,j===2?a:'#F0F0E9');
          dot(-111,0,3,j===2?C.ink:'#A4A99A');
          const labels=['The next big thing','A spark worth keeping','Start here.'];
          text(labels[j],-98,5,13,C.ink,500,205);
          ctx.restore();
        });
        line(58,182,58+250*k,182,'#DBDCD2',2);
      }
    }
    if(i===1){
      const ax=82,ay=86,bx=289,by=143,cx=163,cy=177;
      const q=at(t,5.7,7.2);
      line(ax,ay,mix(ax,bx,q),mix(ay,by,q),'#5A5F4D',1.5);
      line(ax,ay,mix(ax,cx,q),mix(ay,cy,q),'#5A5F4D',1.5);
      line(cx,cy,mix(cx,bx,q),mix(cy,by,q),'#5A5F4D',1.5);
      for(let j=0;j<3;j++){let k=(t*.33+j*.33)%1;dot(mix(ax,bx,k),mix(ay,by,k),3,a);}
      dot(ax,ay,25,a);dot(bx,by,32,C.cream);dot(cx,cy,21,'#303629');
      text('+',ax,ay+8,25,C.ink,400,40,'center');orbit(bx,by,17,t,C.ink);
      box(124,49,114,25,12,'#272C22');mono('a new angle',181,66,9,C.cream,'center');
    }
    if(i===2){
      const p2=at(t,6.5,8.1);
      box(61,60,250,143,11,'#F0F0E9');
      box(74,72,224,10,5,'#DFE2D7');
      box(74,92,224,73,6,accent());
      text('A little idea.',89,123,21,C.ink,650,190);
      text('A bigger world.',89,147,21,C.ink,650,190);
      box(192,176,105,18,9,C.ink);mono('PUBLISHED',244,189,8,C.cream,'center');
      const px=269-39*p2,py=218-30*p2;
      ctx.beginPath();ctx.moveTo(px,py);ctx.lineTo(px,py+19);ctx.lineTo(px+5,py+14);ctx.lineTo(px+12,py+12);ctx.closePath();ctx.fillStyle=C.ink;ctx.fill();ctx.strokeStyle=C.cream;ctx.lineWidth=1.2;ctx.stroke();
      fade(at(t,7.6,8),()=>{dot(312,65,15,C.ink);line(306,65,311,70,C.cream,2);line(311,70,319,60,C.cream,2);});
    }
    text([config.featureOne,config.featureTwo,config.featureThree][i],25,265,43,dark?C.cream:C.ink,700,320);
    text([config.detailOne,config.detailTwo,config.detailThree][i],27,300,16,dark?C.muted:'#707668',400,318);
    ctx.restore();
  }
  function features(t){
    background(t,false);chrome(t,false,'ONE SPACE. THREE POSSIBILITIES.');
    const p=out((t-4.45)/.6);
    fade(p,()=>{text(config.editorTitle,64,184+(1-p)*24,65,C.ink,650,1140);text(config.editorSubtitle,68,228,21,'#6B7063',400,1060);});
    for(let i=0;i<3;i++)drawCard(i,t);
  }
  function ending(t){
    background(t);chrome(t,true,'YOUR NEXT CHAPTER STARTS HERE');
    const p=out((t-11.3)/.85);
    ctx.save();ctx.translate(640,304+(1-p)*75);
    fade(p,()=>{text(config.productName,0,70,192,C.cream,750,1060,'center');});
    ctx.restore();
    fade(at(t,11.7,12.3),()=>{
      text(config.endHeadline,640,458,42,C.cream,500,1110,'center');
      box(450,499,380,52,26,accent());text(config.cta,640,532,15,C.ink,700,320,'center');
      mono('EDIT THE COPY. CHANGE THE COLOR. MAKE IT YOURS.',640,594,10,C.muted,'center');
    });
    fade(p,()=>{orbit(640,157,39,t,accent());});
  }
  function draw(t){
    // Entire frames derive from t; no frame-to-frame simulation or random calls.
    if(t<3){intro(t);}
    else if(t<4.45){brand(t);}
    else if(t<11.3){features(t);}
    else{ending(t);}
    // Directional wipes join the three layouts without a blank transition frame.
    if(t>2.65&&t<3.3){const p=at(t,2.65,3.3);ctx.fillStyle=accent();if(t<3)ctx.fillRect(1280*(1-p*2),0,1280,720);else ctx.fillRect(-1280*((p-.5)*2),0,1280,720);}
    if(t>4.15&&t<4.75){const p=at(t,4.15,4.75);ctx.fillStyle=C.cream;if(t<4.45)ctx.fillRect(0,720*(1-p*2),1280,720);else ctx.fillRect(0,-720*((p-.5)*2),1280,720);}
    if(t>10.65&&t<11.8){
      const p=at(t,10.65,11.8);
      ctx.save();ctx.translate(640,360);ctx.rotate(.18*(1-p));
      const radius=t<11.3?mix(0,980,at(t,10.65,11.3)):mix(980,0,at(t,11.3,11.8));
      dot(0,0,radius,accent());ctx.restore();
    }
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
    const blob=new Blob(['// Saved from the ORBIT Codex edition preview.\nwindow.PRODUCT_CONFIG = '+JSON.stringify(config,null,2)+';\n'],{type:'text/javascript'});
    const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='config.js';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status.textContent='Replace the template’s config.js with this download, then refresh.';
  };
  function loop(now){const dt=Math.min((now-last)/1000,.1);last=now;if(playing){window.seek(time+dt);if(time>=15){playing=false;play.textContent='Play';}}requestAnimationFrame(loop);}
  sync();window.seek(0);play.textContent=playing?'Pause':'Play';requestAnimationFrame(loop);
})();
