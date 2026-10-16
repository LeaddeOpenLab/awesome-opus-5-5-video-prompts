import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
import path from 'node:path';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE_PATH||'playwright');
const root=path.dirname(fileURLToPath(import.meta.url));
const qa=path.join(root,'qa');await fs.mkdir(qa,{recursive:true});
const browser=await chromium.launch({headless:true});
try{
  const page=await browser.newPage({viewport:{width:1400,height:1000}}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  const requests=[];page.on('request',r=>{if(r.url().startsWith('http'))requests.push(r.url());});
  await page.goto(pathToFileURL(path.join(root,'index.html')).href+'?render');
  await page.evaluate(()=>window.animationReady);
  for(const t of [0,1.8,3.5,4.8,7,9.4,11.7,14.2]){
    await page.evaluate(t=>window.seek(t),t);
    await page.locator('#film').screenshot({path:path.join(qa,`frame-${t}.png`)});
  }
  // A frame must be independent of playback history, including backward scrubbing.
  const direct=await page.evaluate(()=>{seek(7);return document.querySelector('canvas').toDataURL();});
  const after=await page.evaluate(()=>{seek(14);seek(1);seek(7);return document.querySelector('canvas').toDataURL();});
  assert.equal(after,direct,'Seek must be deterministic');
  await page.goto(pathToFileURL(path.join(root,'index.html')).href);
  await page.evaluate(()=>window.animationReady);
  await page.locator('#play').click();
  await page.locator('#productName').fill('灵感工作台');
  await page.locator('#endHeadline').fill('让每个好想法，都有一个好开场。');
  await page.locator('#cta').fill('开始制作你的产品演示');
  await page.locator('#accent').evaluate(el=>{el.value='#087F73';el.dispatchEvent(new Event('input',{bubbles:true}));});
  await page.evaluate(()=>seek(14.2));
  assert.equal(await page.evaluate(()=>getConfig().productName),'灵感工作台');
  await page.screenshot({path:path.join(qa,'editor-chinese.png')});
  // Upload a portrait screenshot to exercise contain-fit and configuration persistence.
  const png=await page.evaluate(()=>{const c=document.createElement('canvas');c.width=300;c.height=500;const g=c.getContext('2d');g.fillStyle='#d5eae4';g.fillRect(0,0,300,500);g.fillStyle='#087F73';g.fillRect(25,80,250,180);return c.toDataURL().split(',')[1];});
  await page.locator('#upload').setInputFiles({name:'portrait.png',mimeType:'image/png',buffer:Buffer.from(png,'base64')});
  await page.waitForFunction(()=>document.querySelector('#status').textContent.startsWith('Screenshot added'));
  await page.evaluate(()=>seek(7));
  await page.locator('#film').screenshot({path:path.join(qa,'custom-screenshot.png')});
  const downloadEvent=page.waitForEvent('download');await page.locator('#save').click();
  const download=await downloadEvent;await download.saveAs(path.join(qa,'saved-config.js'));
  const saved=await fs.readFile(path.join(qa,'saved-config.js'),'utf8');
  assert(saved.includes('灵感工作台')&&saved.includes('data:image/png;base64,'),'Saved config must include edits and screenshot');
  await page.locator('#clearImage').click();assert.equal(await page.evaluate(()=>getConfig().screenshot),'');
  await page.setViewportSize({width:390,height:844});
  await page.screenshot({path:path.join(qa,'mobile.png'),fullPage:true});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'No horizontal overflow on mobile');
  assert.deepEqual(errors,[]);assert.deepEqual(requests,[],'Preview should make no network requests');
  console.log('PASS: offline preview, deterministic seek, editable Chinese copy/color, screenshot upload, config download, mobile layout.');
}finally{await browser.close();}
