const {chromium}=require('./browser/node_modules/playwright-core');
const {pathToFileURL}=require('node:url'),path=require('node:path'),fs=require('node:fs'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true});
 const results=[];
 try{
  for(const mode of ['desktop','secondary-cta','mobile','missing-intro','standalone','reduced-motion']){
   const context=await browser.newContext(mode==='mobile'?{viewport:{width:390,height:844},isMobile:true,hasTouch:true}:{viewport:{width:1440,height:900},reducedMotion:mode==='reduced-motion'?'reduce':'no-preference'});
   const page=await context.newPage(),errors=[],requests=[];
   page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(r.resourceType()!=='document'&&!r.url().startsWith('data:'))requests.push(r.url());});
   if(mode==='missing-intro')await page.route('**/intro.png',r=>r.abort());
   await page.goto(pathToFileURL(path.join(root,mode==='standalone'?'dist/불꽃연구소-단독실행.html':'index.html')).href);
   await page.waitForFunction(()=>FireLabIntro.isOpen());
   assert.equal(await page.evaluate(()=>FireLabCharacter.getSnapshot().open),false);
   assert.equal(await page.evaluate(()=>FireLab.getSnapshot().phase),'intro');
   await page.keyboard.press('Escape');assert.equal(await page.evaluate(()=>FireLabIntro.isOpen()),true);
   if(mode==='missing-intro')await page.locator('.intro-art.is-missing').waitFor();
   if(mode==='desktop'||mode==='mobile')await page.screenshot({path:path.join(root,`tests/artifacts/intro-${mode}.png`)});
   const button=page.locator(mode==='secondary-cta'?'#introChoose':'#introStart');
   if(mode==='desktop'){await button.focus();await page.keyboard.press('Enter');}
   else if(mode==='mobile')await button.tap();else await button.click();
   assert.equal(await page.evaluate(()=>FireLabIntro.isOpen()),false);
   assert.equal(await page.evaluate(()=>FireLabCharacter.getSnapshot().open),true);
   const card=page.locator('[data-character="girl"]');
   if(mode==='desktop'||mode==='reduced-motion'){
    await page.mouse.move(0,0);const before=await card.boundingBox();const shadow=await card.evaluate(el=>getComputedStyle(el).boxShadow);await card.hover();await page.waitForTimeout(260);const after=await card.boundingBox();
    if(mode==='desktop'){assert(Math.abs(before.y-after.y-5)<.2);assert.notEqual(await card.evaluate(el=>getComputedStyle(el).boxShadow),shadow);}
    else assert(Math.abs(before.y-after.y)<.2);
    if(mode==='desktop')await page.screenshot({path:path.join(root,'tests/artifacts/character-hover.png')});
   }
   await card.click();await page.locator('#characterConfirm').click();
   assert.equal(await page.evaluate(()=>FireLabCharacter.getSnapshot().selected),'girl');
   await page.locator('[data-change-character]').first().click();assert.equal(await page.evaluate(()=>FireLabIntro.isOpen()),false);assert.equal(await page.evaluate(()=>FireLabCharacter.getSnapshot().open),true);await page.locator('#characterConfirm').click();
   await page.locator('#startBtn').click();assert.equal(await page.evaluate(()=>FireLab.getSnapshot().phase),'exploring');
   if(mode==='standalone')assert.deepEqual(requests,[]);
   assert.deepEqual(errors,[]);results.push({mode,passed:true,errors});console.log(mode+' intro flow passed');await context.close();
  }
  fs.writeFileSync(path.join(root,'tests/artifacts/intro-results.json'),JSON.stringify(results,null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
