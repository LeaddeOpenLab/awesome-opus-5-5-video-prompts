import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
import path from 'node:path';
import fs from 'node:fs/promises';
import {spawn} from 'node:child_process';
import {once} from 'node:events';

// PLAYWRIGHT_MODULE_PATH is optional; normally npm install supplies playwright.
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE_PATH||'playwright');
const root=path.dirname(fileURLToPath(import.meta.url));
const output=path.resolve(root,process.argv[2]||'example.mp4');
await fs.mkdir(path.dirname(output),{recursive:true});
const browser=await chromium.launch({headless:true});
let encoder;
try{
  const page=await browser.newPage({viewport:{width:1280,height:720},deviceScaleFactor:1.5});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(path.join(root,'index.html')).href+'?render');
  await page.evaluate(()=>window.animationReady);
  const canvas=page.locator('#film');
  const temp=output.replace(/\.mp4$/i,'')+'.partial.mp4';
  encoder=spawn(process.env.FFMPEG_PATH||'ffmpeg',[
    '-y','-hide_banner','-loglevel','error','-f','image2pipe','-framerate','30','-vcodec','mjpeg','-i','pipe:0',
    '-an','-vf','scale=in_range=pc:out_range=tv,format=yuv420p','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-color_range','tv','-movflags','+faststart',temp
  ],{stdio:['pipe','ignore','pipe']});
  let stderr='';encoder.stderr.on('data',d=>stderr+=d);
  let pipeError;encoder.stdin.on('error',e=>pipeError=e);
  const done=new Promise((resolve,reject)=>{encoder.on('error',reject);encoder.on('close',code=>code===0?resolve():reject(new Error(stderr||`FFmpeg exited ${code}`)));});
  done.catch(()=>{});
  for(let frame=0;frame<450;frame++){
    if(pipeError)throw pipeError;
    await page.evaluate(t=>window.seek(t),frame/30);
    const jpeg=await canvas.screenshot({type:'jpeg',quality:95});
    if(!encoder.stdin.write(jpeg))await once(encoder.stdin,'drain');
    if(frame%90===0)console.log(`Rendering ${frame}/450 frames`);
  }
  encoder.stdin.end();await done;
  if(errors.length)throw new Error(errors.join('\n'));
  await fs.rename(temp,output);
  console.log(`Saved ${output}\n15 seconds · 1920×1080 · 30 fps · silent MP4`);
}finally{if(encoder&&!encoder.killed&&encoder.exitCode===null)encoder.kill();await browser.close();}
