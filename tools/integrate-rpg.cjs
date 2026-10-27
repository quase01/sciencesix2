const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..');let html=fs.readFileSync(path.join(root,'backups/pre-rpg-20261026/index.html'),'utf8');
const replace=(s,a,b)=>{if(!s.includes(a))throw Error('Missing '+a.slice(0,90));return s.replace(a,b);};
html=replace(html,'<script src="characters.js"></script>','<link rel="stylesheet" href="rpg.css">\n<script src="prop-metadata.js"></script>\n<script src="world-renderer.js"></script>\n<script src="rpg.js"></script>\n<script src="bonus-rooms.js"></script>\n<script src="characters.js"></script>');
html=html.replace('현재 열린 게임의 기록만 표시합니다. 서버 전송과 자동 저장은 없으며, 새로고침 시 기록이 지워집니다.','이 브라우저에 진행 상황과 학습 기록을 자동 저장합니다. 서버로 전송하지 않습니다. 탐험 메뉴의 ‘저장 관리’에서 전체 기록을 초기화할 수 있습니다.');
html=html.replace('데이터는 브라우저 메모리에만 유지합니다. 서버 전송·자동 저장 없음.','데이터는 브라우저 로컬 저장소에만 저장합니다. 서버 전송 없음.');
html=html.replace('window.FireLabLearning={stageStart,','window.FireLabLearning={restore:saved=>{if(saved?.version===1&&saved.questions&&saved.stages){data=JSON.parse(JSON.stringify(saved));setName(data.student||\'\');render();renderCertificate();}},stageStart,');
html=html.replace('q.attempts++;if(correct)q.solved=true;else q.wrong++;','q.attempts++;if(correct)q.solved=true;else q.wrong++;window.FireLabRPG?.answer(stage,id,correct);');
html=html.replace('data.stages[stage].seconds=Math.max(0,Math.round(Number(seconds)||0));renderCertificate();','data.stages[stage].seconds=Math.max(0,Math.round(Number(seconds)||0));renderCertificate();window.FireLabRPG?.complete(stage);');
const maps=['map','world','map','map','map','map'],sets=['heldKeys','keys','keys','keys','keys','held'],syncs=['updateUI();updatePrompt();','setVisible();syncUI();','reveal();sync();','reveal();sync();','reveal();sync();','reveal();sync();'];
html=html.replace(/<script>([\s\S]*?)<\/script>/g,(all,code)=>{
 const found=code.match(/window\.FireLabStage([2-6])\s*=/),n=found?+found[1]:code.includes('window.FireLab =')?1:0;if(!n)return all;
 code=code.replace(/im\.src=(`props\/\$\{file\}\.png`)/g,'im.dataset&&(im.dataset.asset=file);im.src=window.FireLabAssets?.[`props/${file}.png`]||$1');
 code=code.replace(/function move\(dx,dy,([^)]*)\)\{/,'function move(dx,dy,$1){if(window.FireLabRPG?.blocked('+n+'))return false;if(window.FireLabRPG?.collision('+n+',dx,dy))return false;');
 code=replace(code,'function interact(){','function interact(){if(window.FireLabRPG?.blocked('+n+'))return;if(window.FireLabRPG?.interact('+n+'))return;');
 code=replace(code,'function reset(){','function reset(){window.FireLabRPG?.resetting('+n+');');
 // Animation time stops while any dialog or bonus room is open.
 code=code.replace(/if\(state\.phase==='play'\)\{state.seconds/g,"if(state.phase==='play'&&!window.FireLabRPG?.blocked("+n+")){state.seconds");
 if(n===1)code=replace(code,"if(state.phase==='exploring'){state.seconds","if(state.phase==='exploring'&&!window.FireLabRPG?.blocked(1)){state.seconds");
 code=replace(code,'function draw(t){','function draw(t){window.FireLabWorld?.begin(ctx);');
 const start=code.indexOf('function draw(t){'),end=code.indexOf('function frame(t)',start);let draw=code.slice(start,end);
 draw=replace(draw,'drawPlayer(t);','drawPlayer(t);window.FireLabRPG?.draw('+n+',ctx,t);window.FireLabWorld?.flush(ctx);');code=code.slice(0,start)+draw+code.slice(end);
 // Frame-crop metadata removes transparent padding without editing Blender sources.
 if(n===1){code=replace(code,"function drawSprite(id,frame,frames,x,y,w,h){","function drawSprite(id,frame,frames,x,y,w,h){if(window.FireLabWorld?.sprite(ctx,sprites[id],frame,frames,x+w/2,y+h-5,w,h))return;");}
 else code=code.replace(/ctx\.drawImage\(im,on\?cell:0,0,cell,cell,-24,-26(?:\+bob)?,48,48\);/g,"window.FireLabWorld?window.FireLabWorld.prop(ctx,im,on):ctx.drawImage(im,on?cell:0,0,cell,cell,-24,-26,48,48);");
 if(n>1){code=replace(code,'function show(){','function show(){window.FireLabRPG?.beforeSwitch('+n+');');
   code=replace(code,'reset();last=0','reset();window.FireLabRPG?.activate('+n+');last=0');
 }
 if(n===2){code=replace(code,"el('playAgain').click();","window.FireLabRPG?window.FireLabRPG.activate(1):el('playAgain').click();");code=replace(code,'function hide(){','function hide(){window.FireLabRPG?.beforeSwitch(1);');}
 const modals=n===1?['startOverlay','labModal','infoModal','winModal']:['s'+n+'Start','s'+n+'Modal','s'+n+'Win'];
 const wrappers=n===1?[['wallTile','(args[1]+1)*38'],['drawLab','7*38+33'],['drawInteractive','args[0].y*38+33'],['drawItem','args[0].y*38+32'],['drawKey','state.keySpot.y*38+33'],['drawExit','state.exit.y*38+34']]:[['drawWall','(args[1]+1)*38'],['drawStation','args[0].y*38+33'],['drawExit','state.exit.y*38+34'],...(n>=3?[['drawGate','args[0].y*38+35']]:[])];
 wrappers.push(['drawPlayer','(state.player.drawY??state.player.y)*38+36']);
 let extra='\n';for(const [fn,depth]of wrappers)extra+=`const rpg_${fn}=${fn};${fn}=function(...args){const paint=()=>{rpg_${fn}(...args);${fn==='drawStation'||fn==='drawInteractive'?`window.FireLabWorld?.highlight(ctx,args[0],state.player,args[1]);`:''}};if(!window.FireLabWorld?.enqueue(ctx,${depth},paint))paint();};\n`;
 const restoreExtra=n===1?`['flour','baking'].forEach(type=>{const done=state.experiments[type],isBaking=type==='baking';elements[isBaking?'experimentBaking':'experimentFlour'].classList.toggle('done',done);elements[isBaking?'experimentBaking':'experimentFlour'].classList.toggle('reacted',done&&isBaking);elements[isBaking?'balloonBaking':'balloonFlour'].classList.toggle('inflated',done&&isBaking);elements[isBaking?'tryBaking':'tryFlour'].disabled=done;elements[isBaking?'tryBaking':'tryFlour'].textContent=done?'✓ 관찰 완료':'실험하기';elements[isBaking?'resultBaking':'resultFlour'].textContent=done?(isBaking?'기포 발생! 기체가 생기며 풍선이 부풀었어.':'눈에 띄는 변화 없음 · 풍선이 부풀지 않음'):'실험 전 · 결과를 관찰해 보세요';});elements.labConclusion.classList.toggle('hidden',!Object.values(state.experiments).every(Boolean));document.querySelectorAll('.quiz-answer').forEach(b=>{b.disabled=state.quizSolved;b.classList.toggle('correct',state.quizSolved&&b.dataset.answer==='baking');b.classList.remove('wrong');});elements.quizFeedback.textContent=state.quizSolved?'관찰 정답이 저장되어 있어요. 황금 열쇠를 찾아 출구로 이동하세요.':'';`:`document.getElementById('s${n}MiniMap').classList.toggle('hidden',${n===2?'!state.minimap':n===6?'!state.mapShown':'!state.showMap'});`;
 extra+=`window.FireLabRPG?.register(${n},{get:()=>state,map:()=>${maps[n-1]},gates:()=>${n>=3?'gates':'[]'},clear:()=>${sets[n-1]}.clear(),reset,refresh:()=>{${syncs[n-1]}},capture:()=>({state:JSON.parse(JSON.stringify(state)),map:${maps[n-1]}.map(r=>[...r])}),restore:saved=>{state=JSON.parse(JSON.stringify(saved.state));${maps[n-1]}=saved.map.map(r=>[...r]);if(state.phase==='lab')state.phase='exploring';state.modalOpen=false;state.lastStep=state.lastMove=state.moveAt=state.motionStart=0;state.player.drawX=state.player.fromX=state.player.x;state.player.drawY=state.player.fromY=state.player.y;state.player.motion=0;delete state.player.spriteGait;${sets[n-1]}.clear();${JSON.stringify(modals)}.forEach(id=>document.getElementById(id)?.classList.add('hidden'));if(state.phase==='intro')document.getElementById('${modals[0]}').classList.remove('hidden');if(['clear','won'].includes(state.phase))document.getElementById('${modals[modals.length-1]}').classList.remove('hidden');${restoreExtra}${syncs[n-1]}}});\n`;
 code=code.replace(/\}\)\(\);\s*$/m,extra+'})();');new vm.Script(code);return '<script>'+code+'</script>';
});
fs.writeFileSync(path.join(root,'index.html'),html);
let chars=fs.readFileSync(path.join(root,'backups/pre-rpg-20261026/characters.js'),'utf8');
chars=chars.replace("'캐릭터를 불러오지 못했어요. 아래 버튼을 눌러 다시 시도해 주세요.'","'이미지 대신 기본 연구원으로 계속 탐험할 수 있어요.'");
chars=chars.replace("confirm.textContent = '캐릭터 다시 불러오기 ↻';","confirm.textContent = '기본 연구원으로 준비 완료 →';");
chars=chars.replace('sheet.src = character.src;','sheet.src = window.FireLabAssets?.[character.src] || character.src;');
chars=chars.replace('if (!character?.ready) return;','if (!character?.ready) {ctx.save();ctx.fillStyle=character===characters.girl?\'#ed9bbd\':\'#80d6eb\';ctx.fillRect(x-size*.16,feetY-size*.6,size*.32,size*.4);ctx.fillStyle=\'#f4cfac\';ctx.beginPath();ctx.arc(x,feetY-size*.74,size*.14,0,Math.PI*2);ctx.fill();ctx.fillStyle=\'#26364d\';const stride=frame===1?0:frame===0?size*.08:-size*.08;ctx.fillRect(x-size*.14,feetY-size*.2+stride,size*.1,size*.2);ctx.fillRect(x+size*.04,feetY-size*.2-stride,size*.1,size*.2);ctx.restore();return;}');
chars=chars.replace('if (character?.error) { load(character); syncChoice(); return; }','');
chars=chars.replace('if (!character?.ready) return;','if (!character || (!character.ready&&!character.error)) return;');
chars=chars.replace('selected && characters[selected].ready && !dialog.open','selected && (characters[selected].ready||characters[selected].error) && !dialog.open');
chars=chars.replace('if (!character?.ready) return;','if (!character) return;');
fs.writeFileSync(path.join(root,'characters.js'),chars);console.log('Integrated graphics and six stage adapters.');
