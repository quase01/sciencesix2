/* Optional exploration layer. Required lesson tasks and teacher exports remain in index.html. */
(() => {
 'use strict';
 const KEY='firelab-adventure-v2',adapters=new Map(),prepared=new WeakSet(),cache={};
 const cards=[
  ['mixing','물질을 섞을 때의 변화',1,'물질을 섞으면 눈에 띄는 변화가 없을 수도, 기체 같은 새로운 물질이 생길 수도 있어요. 풍선이 부푸는 현상은 연소와 구별해요.'],
  ['light','연소의 빛과 열',2,'물질이 연소하면 빛과 열이 발생해요. 전기 조명도 빛을 내지만 모두 연소인 것은 아니에요.'],
  ['oxygen','산소의 역할',3,'산소는 다른 물질의 연소를 도와요. 산소 자체가 타는 연료는 아니에요.'],
  ['triangle','연소의 세 조건',4,'탈 물질, 산소, 발화점 이상의 온도가 함께 필요해요. 한 조건을 없애면 연소를 멈출 수 있어요.'],
  ['ignition','발화점',4,'물질이 스스로 불붙기 시작하는 온도를 발화점이라고 해요. 물질과 조건에 따라 달라요.'],
  ['products','물과 이산화 탄소',5,'이 게임에서 관찰한 초의 연소 생성물은 물과 이산화 탄소예요. 물은 염화 코발트 종이를 푸른색에서 붉은색 계열로, 이산화 탄소는 석회수를 뿌옇게 바꿔요. 모든 물질의 연소 생성물이 같은 것은 아니에요.'],
  ['eco','생태계와 이산화 탄소',6,'이산화 탄소는 온실 기체예요. 배출 감축과 생태계 보호는 장기적인 변화를 도와요. 해수 온도 상승은 산호 백화, 바닷물에 녹은 이산화 탄소 증가는 해양 산성화와 관련돼요.']
 ];
 const abilities=['근처 장치 탐지','탐사 범위 증가','숨겨진 장치 감지','위험 구역 경고','과학 기록 감지','최종 탐험가 배지'];
 const theme=['#7adacb','#9fc8ff','#72ead8','#ffc078','#c7b9ff','#b9e790'];
 let active=1,switching=false,restoring=false,pendingSave=null,saveTimer=0,toastTimer=0,lastUI=0,detectedUntil=0;
 let progress={cards:[],rooms:{},abilities:[],badge:false},bot={x:1,y:1,route:[],last:null,state:'idle',until:0},audio;
 const clone=o=>JSON.parse(JSON.stringify(o)),distance=(a,b)=>Math.abs(a.x-b.x)+Math.abs(a.y-b.y),$=id=>document.getElementById(id);
 const robot=new Image();robot.dataset.asset='guide-robot';robot.src=window.FireLabAssets?.['props/guide-robot.png']||'props/guide-robot.png';
 function shown(el){return !!el&&!el.classList.contains('hidden')&&!!el.getClientRects().length;}
 function blocked(n=active){if(n!==active||window.FireLabBonus?.isOpen())return true;
  if(document.querySelector('dialog[open]'))return true;
  return [...document.querySelectorAll('.modal,[role="dialog"]')].some(shown);
 }
 function clear(){adapters.forEach(a=>a.clear());}
 function ready(){const s=adapters.get(active)?.get();return s&&['exploring','play'].includes(s.phase)&&!blocked();}
 function objects(n,s){return n===1?[{id:'lab',name:'혼합 실험대',x:9,y:7},...s.interactives]:s.stations;}
 function prepare(n){const a=adapters.get(n),s=a?.get();if(!s||prepared.has(s))return;
  const m=a.map(),gates=a.gates(),barriers=new Set(gates.map(g=>g.x));
  // Give stationary props a walkable alcove. Never carve the inter-zone gate walls.
  for(const o of objects(n,s)){o.collisionWidth=28;o.collisionHeight=18;
   for(let y=o.y-1;y<=o.y+1;y++)for(let x=o.x-1;x<=o.x+1;x++)if(y>0&&y<m.length-1&&x>0&&x<m[0].length-1&&!barriers.has(x))m[y][x]=0;
  }
  const occupied=objects(n,s),start=s.player,queue=[{x:start.x,y:start.y,d:0}],seen=new Set([start.x+','+start.y]);let portal=null;
  for(let i=0;i<queue.length;i++){const q=queue[i];if(q.d>=9&&q.d<=22&&occupied.every(o=>distance(o,q)>3)){
    const wall=[[0,-1],[1,0],[0,1],[-1,0]].map(([x,y])=>({x:q.x+x,y:q.y+y})).find(p=>p.x>1&&p.y>1&&p.x<m[0].length-2&&p.y<m.length-2&&m[p.y][p.x]===1&&!barriers.has(p.x));
    if(wall){portal=wall;break;}
   }
   for(const [dx,dy]of [[0,-1],[1,0],[0,1],[-1,0]]){const x=q.x+dx,y=q.y+dy,k=x+','+y;if(m[y]?.[x]===0&&!seen.has(k)&&!barriers.has(x)){seen.add(k);queue.push({x,y,d:q.d+1});}}
  }
  s.rpgPortal ||= portal||{x:1,y:0};prepared.add(s);
 }
 function collision(n,dx,dy){if(Math.abs(dx)+Math.abs(dy)!==1)return true;prepare(n);const s=adapters.get(n)?.get();return !!s&&objects(n,s).some(o=>o.x===s.player.x+dx&&o.y===s.player.y+dy);}
 function register(n,a){adapters.set(n,a);prepare(n);}
 function capture(n=active){const a=adapters.get(n);if(a?.get())cache[n]=a.capture();}
 function beforeSwitch(n){if(restoring)return;capture();switching=true;clear();window.FireLabBonus?.leave(true);}
 function activate(n){active=n;clear();if(cache[n])adapters.get(n).restore(cache[n]);prepare(n);switching=false;bot={x:adapters.get(n).get().player.x,y:adapters.get(n).get().player.y,route:[],last:null,state:'idle',until:0};schedule();}
 function resetting(n){if(!switching&&!restoring){delete cache[n];if(n===active)bot.last=null;}}
 function interact(n){const s=adapters.get(n)?.get();if(!s||!['play','exploring'].includes(s.phase))return false;prepare(n);
  if(distance(s.player,s.rpgPortal)<=1){clear();progress.rooms[n]||={discovered:true,solved:false,claimed:false};progress.rooms[n].discovered=true;window.FireLabBonus?.enter(n,progress.rooms[n]);feedback('비밀 탐구실 발견! 자유롭게 돌아갈 수 있어요.','joy');window.FireLabLearning?.activity(n,'선택 탐구실 발견');schedule();return true;}
  react('investigate');return false;
 }
 function unlock(id){if(!progress.cards.includes(id)){progress.cards.push(id);feedback('과학 도감에 새 카드가 기록됐어요!','joy');}progress.badge=cards.every(c=>progress.cards.includes(c[0]));schedule();}
 function answer(stage,id,correct){react(correct?'joy':'surprise');tone(correct);if(correct){const key=stage===1?'mixing':stage===2?'light':stage===3?'oxygen':stage===4?(id==='thermo'||id==='match'?'ignition':'triangle'):stage===5?'products':'eco';unlock(key);}schedule();}
 function complete(stage){if(!progress.abilities.includes(stage)){progress.abilities.push(stage);feedback('파이어봇 성장 · '+abilities[stage-1],'joy');}if(stage===4){unlock('triangle');unlock('ignition');}else unlock(cards.find(c=>c[2]===stage)[0]);schedule();}
 function reward(n){const r=progress.rooms[n];if(r&&!r.claimed){r.claimed=true;cards.filter(c=>c[2]===n).forEach(c=>unlock(c[0]));window.FireLabLearning?.activity(n,'선택 탐구 완료 · 과학 카드 수집');feedback(n===6?'지구 수호자 탐구 인증 획득!':'탐구 기록 획득! 도감에서 확인해요.','joy');schedule();}}
 function react(state){bot.state=state;bot.until=performance.now()+1800;}
 function tone(success){if($('soundLabel')?.textContent==='OFF')return;try{audio ||= new (window.AudioContext||window.webkitAudioContext)();if(audio.state==='suspended')audio.resume();const osc=audio.createOscillator(),gain=audio.createGain();osc.connect(gain);gain.connect(audio.destination);osc.type='sine';osc.frequency.setValueAtTime(success?620:220,audio.currentTime);osc.frequency.exponentialRampToValueAtTime(success?880:160,audio.currentTime+.12);gain.gain.setValueAtTime(.035,audio.currentTime);gain.gain.exponentialRampToValueAtTime(.001,audio.currentTime+.15);osc.start();osc.stop(audio.currentTime+.16);}catch{}}
 function feedback(message,state='hint'){react(state);const el=$('rpgToast');if(!el)return;el.textContent=message;el.dataset.kind=state;el.hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.hidden=true,4200);}
 function scan(){if(!ready())return;if(!progress.abilities.includes(1)){feedback('완료한 스테이지가 쌓이면 탐지 능력이 열려요. 수상한 벽은 지금도 E로 조사할 수 있어요.');return;}
  const s=adapters.get(active).get(),range=progress.abilities.includes(2)?12:6;let candidates=objects(active,s).filter(o=>distance(o,s.player)<=range&&!o.done);
  if(progress.abilities.includes(3)&&distance(s.rpgPortal,s.player)<=range)candidates.push({...s.rpgPortal,name:'수상한 벽'});
  if(progress.abilities.includes(5)&&!progress.rooms[active]?.claimed)candidates.push({...s.rpgPortal,name:'미수집 탐구 기록'});
  candidates.sort((a,b)=>distance(a,s.player)-distance(b,s.player));const q=candidates[0];
  detectedUntil=performance.now()+4000;feedback(q?`${q.name||q.label||'장치'} 신호: ${q.x>s.player.x?'오른쪽':q.x<s.player.x?'왼쪽':''}${q.y>s.player.y?' 아래':q.y<s.player.y?' 위':''} 방향. 주변을 관찰해 봐요.`:'탐지 범위 안에 새 신호가 없어요. 조금 더 탐험해 봐요.');
 }
 function draw(n,ctx,t){if(n!==active)return;prepare(n);const s=adapters.get(n)?.get();if(!s)return;const p=s.player,portal=s.rpgPortal,near=distance(p,portal)<=1;
  const portalPaint=()=>{ctx.save();const x=portal.x*38+19,y=portal.y*38+19,found=progress.rooms[n]?.discovered;ctx.fillStyle=found?'#275958':'#344457';ctx.fillRect(x-13,y-13,26,29);ctx.strokeStyle=near||t<detectedUntil?theme[n-1]:'#607582';ctx.lineWidth=2;ctx.strokeRect(x-13,y-13,26,29);ctx.font='bold 13px sans-serif';ctx.textAlign='center';ctx.fillStyle=theme[n-1];ctx.fillText(found?'✦':'⋮',x,y+5);if(near){ctx.fillStyle='#102435';ctx.fillRect(x-55,y-41,110,21);ctx.fillStyle='#fff1c7';ctx.font='11px sans-serif';ctx.fillText('E · 수상한 벽 조사',x,y-26);}ctx.restore();};
  window.FireLabWorld.enqueue(ctx,portal.y*38+39,portalPaint);
  if(!bot.last)bot.last={x:p.x,y:p.y};if(p.x!==bot.last.x||p.y!==bot.last.y){if(distance(p,bot.last)>2){bot.x=p.x;bot.y=p.y;bot.route=[];}else bot.route.push({...bot.last});bot.last={x:p.x,y:p.y};schedule();}
  if(bot.route.length){const q=bot.route[0],dx=q.x-bot.x,dy=q.y-bot.y,d=Math.hypot(dx,dy);if(d<.08){bot.x=q.x;bot.y=q.y;bot.route.shift();}else{const v=Math.min(d,.13);bot.x+=dx/d*v;bot.y+=dy/d*v;}}
  if(t>bot.until)bot.state=bot.route.length?'move':'idle';
  if(progress.abilities.includes(4)&&s.vents?.some(v=>distance(v,p)<=2)&&t>bot.until){feedback('앞쪽에 뜨거운 바닥 신호! 경로와 보호 장치를 살펴봐요.');}
  window.FireLabWorld.enqueue(ctx,bot.y*38+34,()=>paintBot(ctx,t));
  if(t-lastUI>500){lastUI=t;const status=$('rpgStatus');if(status)status.textContent=`${n}구역 · 도감 ${progress.cards.length}/${cards.length} · 탐구 ${Object.values(progress.rooms).filter(r=>r.claimed).length}/6`;if($('rpgObjective'))$('rpgObjective').textContent='현재 목표 · '+($(n===1?'missionText':`s${n}Mission`)?.textContent||'주변을 탐험하세요.');if($('rpgMapZoom')){$('rpgMapZoom').disabled=n===1;$('rpgMapZoom').title=n===1?'1구역은 전체 지도가 화면에 보입니다.':'현재 구역의 미니맵을 확대합니다.';}}
 }
 function paintBot(ctx,t,actor=bot){const bot=actor,x=bot.x*38+19,y=bot.y*38+31,bob=Math.sin(t/(bot.state==='move'?90:360))*1.5,jump=bot.state==='joy'?Math.abs(Math.sin(t/100))*5:0;ctx.save();ctx.fillStyle='#0005';ctx.beginPath();ctx.ellipse(x,y,10,4,0,0,7);ctx.fill();if(!window.FireLabWorld.sprite(ctx,robot,bot.state==='joy'?1:0,2,x,y+bob-jump,34,34)){ctx.fillStyle='#8de2d9';ctx.fillRect(x-10,y-23,20,20);ctx.fillStyle='#17364b';ctx.fillRect(x-6,y-17,4,4);ctx.fillRect(x+3,y-17,4,4);}if(['hint','surprise','investigate','joy'].includes(bot.state)){ctx.font='bold 14px sans-serif';ctx.textAlign='center';ctx.fillStyle=bot.state==='surprise'?'#ffa896':'#ffe2a3';ctx.fillText({hint:'?',surprise:'!',investigate:'…',joy:'✦'}[bot.state],x,y-39);}ctx.restore();}
 function schedule(){if(restoring||pendingSave)return;clearTimeout(saveTimer);saveTimer=setTimeout(save,600);}
 function save(){if(pendingSave||restoring)return;capture();const value={version:2,savedAt:new Date().toISOString(),active,stages:cache,progress,learning:window.FireLabLearning?.getSnapshot(),character:window.FireLabCharacter?.getSnapshot().selected};try{localStorage.setItem(KEY,JSON.stringify(value));if($('rpgSaveState'))$('rpgSaveState').textContent='이 브라우저에 자동 저장됨';}catch{if($('rpgSaveState'))$('rpgSaveState').textContent='자동 저장 불가 · 학습 결과를 파일로 저장해 주세요';}}
 function validSave(v){
  const object=x=>x&&typeof x==='object'&&!Array.isArray(x),bools=(x,count)=>Array.isArray(x)&&x.length===count&&x.every(y=>typeof y==='boolean');
  if(v?.version!==2||!Number.isInteger(v.active)||v.active<1||v.active>6||!object(v.stages)||!v.stages[v.active]||!Array.isArray(v.progress?.cards)||!v.progress.cards.every(id=>cards.some(c=>c[0]===id))||!Array.isArray(v.progress.abilities)||!v.progress.abilities.every(n=>Number.isInteger(n)&&n>=1&&n<=6)||!object(v.progress.rooms))return false;
  const learning=v.learning;if(learning?.version!==1||!object(learning.stages)||!object(learning.questions)||!Array.isArray(learning.helps)||!Array.isArray(learning.activities)||typeof learning.student!=='string')return false;
  if(!Object.values(learning.questions).every(q=>object(q)&&Number.isFinite(q.attempts)&&Number.isFinite(q.wrong)&&typeof q.solved==='boolean'))return false;
  if(!Object.values(v.progress.rooms).every(r=>object(r)&&typeof r.discovered==='boolean'&&(!r.puzzle||(object(r.puzzle)&&Array.isArray(r.puzzle.mirrors)&&r.puzzle.mirrors.length===2&&Array.isArray(r.puzzle.pipes)&&r.puzzle.pipes.length===3&&bools(r.puzzle.observed,2)&&bools(r.puzzle.lit,2)&&bools(r.puzzle.activities,4)&&Array.isArray(r.puzzle.bag)&&object(r.puzzle.slots)))))return false;
  const taskKeys=[[],['observe','light','heat','relay'],['generator','compare','valve','console'],['match','thermo','triangle','final'],['water','gas','report','restore'],['sort','impact','action','final']];
  return Object.entries(v.stages).every(([key,a])=>{const n=+key,s=a?.state,m=a?.map;if(n<1||n>6||!object(s)||!Array.isArray(m)||m.length<15||m.length>80||!m.every(row=>Array.isArray(row)&&row.length===m[0].length&&row.length<=100&&row.every(c=>c===0||c===1))||!s.player||!Number.isInteger(s.player.x)||!Number.isInteger(s.player.y)||m[s.player.y]?.[s.player.x]!==0||!Number.isFinite(s.seconds)||s.seconds<0||!['intro','lab','exploring','play','won','clear'].includes(s.phase))return false;
   if(n===1)return Array.isArray(s.items)&&s.items.length===3&&Array.isArray(s.interactives)&&object(s.experiments)&&s.exit&&s.keySpot;
   const cam=n===2?s.cam:s.camera,explored=n===2?s.visited:s.explored;if(!object(cam)||!Number.isFinite(cam.x)||!Number.isFinite(cam.y)||!object(s.tasks)||!taskKeys[n-1].every(k=>typeof s.tasks[k]==='boolean')||!Array.isArray(s.stations)||!s.stations.length||!Array.isArray(explored)||explored.length!==m.length||!Array.isArray(s.visible)||s.visible.length!==m.length)return false;
   if(n===3)return Array.isArray(s.pipe)&&s.pipe.length===3&&object(s.observed);if(n===4)return bools(s.conditions,3)&&Array.isArray(s.vents)&&object(s.matchObserved);if(n===5)return bools(s.restoreSwitches,2)&&object(s.observed);if(n===6)return Array.isArray(s.seeds)&&Array.isArray(s.sortChoices)&&s.sortChoices.length===5&&Array.isArray(s.impactAnswers);return object(s.observed);
  });
 }
 function resume(){if(!pendingSave)return;const v=pendingSave;pendingSave=null;restoring=true;Object.assign(cache,v.stages);progress=v.progress;progress.rooms||={};progress.abilities||=[];window.FireLabLearning.restore(v.learning);if(v.active>1)window['FireLabStage'+v.active].start();active=v.active;if(cache[active])adapters.get(active).restore(cache[active]);prepare(active);restoring=false;activate(active);$('rpgResume')?.remove();$('rpgDialog').close();feedback('저장한 탐험을 이어갑니다.','joy');save();}
 function modal(title,body){clear();const d=$('rpgDialog');$('rpgDialogTitle').textContent=title;$('rpgDialogBody').replaceChildren(body);d.showModal();}
 function node(tag,text,cls){const el=document.createElement(tag);el.textContent=text;if(cls)el.className=cls;return el;}
 function codex(){const wrap=node('div','','rpg-cards');for(const [id,title,stage,desc]of cards){const open=progress.cards.includes(id),article=node('article','',open?'unlocked':'locked');article.append(node('small',`${stage}구역 · ${open?'발견 완료':'미발견'}`),node('h3',open?title:'🔒 '+title),node('p',open?desc:'관련 필수 실험을 완료하거나 선택 탐구실에서 기록을 수집하세요.'));wrap.append(article);}if(progress.badge)wrap.prepend(node('p','★ 모든 과학 카드 수집 · 탐구 박사 배지','rpg-badge'));modal('과학 도감',wrap);}
 function companion(){const wrap=node('div');wrap.append(node('p','파이어봇은 지나온 길을 따라오며 관찰할 곳을 알려 줍니다. R 또는 ‘탐지’를 눌러 보세요. 과학 문제의 답은 알려 주지 않아요.'));abilities.forEach((a,i)=>wrap.append(node('p',`${progress.abilities.includes(i+1)?'✓':'🔒'} ${i+1}구역 완료 · ${a}`)));modal('파이어봇 성장 기록',wrap);}
 function storage(){const wrap=node('div');wrap.append(node('p','진행 상황, 선택 탐구, 도감과 학생 이름·학습 답변은 이 기기·이 브라우저에만 저장합니다. 서버로 전송하지 않습니다. 다른 기기나 브라우저에는 이어지지 않으며, 브라우저 데이터 삭제 시 사라집니다. 교사에게 제출할 JSON·CSV는 학습 결과 메뉴에서 저장하세요.'));
  const reset=node('button','전체 진행과 로컬 학습 기록 초기화','rpg-danger');reset.onclick=()=>{if(!confirm('6개 구역의 진행, 도감, 학생 이름과 학습 답변을 이 브라우저에서 모두 지울까요? 다운로드한 파일은 유지됩니다.'))return;localStorage.removeItem(KEY);localStorage.removeItem('firelab-character');pendingSave={};location.reload();};wrap.append(reset);modal('저장 관리',wrap);}
 function init(){
  const bar=node('nav','','rpg-toolbar');bar.setAttribute('aria-label','탐험 도구');bar.innerHTML='<div><strong>탐험 연구 노트</strong><small id="rpgStatus">선택 탐구는 필수 미션과 별개예요</small></div><div class="rpg-actions"><button id="rpgCodex">과학 도감</button><button id="rpgCompanion">파이어봇</button><button id="rpgScan">탐지 R</button><button id="rpgFocus" aria-pressed="false">정보 접기</button><button id="rpgMapZoom" aria-pressed="false">지도 확대</button><button id="rpgStorage">저장 관리</button></div><small id="rpgSaveState">이 브라우저에 자동 저장 · 서버 전송 없음</small>';
  const objective=node('p','','rpg-objective');objective.id='rpgObjective';bar.append(objective);document.querySelector('.topbar').after(bar);
  const d=document.createElement('dialog');d.id='rpgDialog';d.className='rpg-dialog';d.setAttribute('aria-labelledby','rpgDialogTitle');d.innerHTML='<header><h2 id="rpgDialogTitle"></h2><button id="rpgDialogClose" aria-label="닫기">✕</button></header><div id="rpgDialogBody"></div>';document.body.append(d);
  const toast=node('div','','rpg-toast');toast.id='rpgToast';toast.setAttribute('role','status');toast.hidden=true;document.body.append(toast);
  $('rpgDialogClose').onclick=()=>d.close();d.addEventListener('close',clear);$('rpgCodex').onclick=codex;$('rpgCompanion').onclick=companion;$('rpgScan').onclick=scan;$('rpgStorage').onclick=storage;
  $('rpgFocus').onclick=()=>{const on=document.body.classList.toggle('rpg-focus');$('rpgFocus').setAttribute('aria-pressed',on);$('rpgFocus').textContent=on?'정보 펼치기':'정보 접기';document.querySelectorAll('aside').forEach(a=>{a.parentElement.style.gridTemplateColumns=on?'minmax(0,1fr)':'';});};
  $('rpgMapZoom').onclick=()=>{const on=document.body.classList.toggle('rpg-map-zoom');$('rpgMapZoom').setAttribute('aria-pressed',on);$('rpgMapZoom').textContent=on?'지도 축소':'지도 확대';};
  try{const raw=localStorage.getItem(KEY);if(raw){const v=JSON.parse(raw);if(validSave(v)){pendingSave=v;const resumeBar=node('div','','rpg-resume');resumeBar.id='rpgResume';resumeBar.append(node('span',`${v.active}구역의 저장된 탐험이 있어요. `));const b=node('button','이어서 탐험');b.onclick=resume;const fresh=node('button','새로 시작');fresh.onclick=()=>{if(!confirm('기존 자동 저장을 새 탐험으로 바꿀까요?'))return;pendingSave=null;resumeBar.remove();save();};resumeBar.append(b,fresh);bar.after(resumeBar);}else feedback('저장 자료가 손상되어 이어 불러오지 않았어요. 새 탐험은 이용할 수 있어요.','surprise');}}catch{feedback('저장 자료를 읽을 수 없어요. 학습 결과는 파일로 보관해 주세요.','surprise');}
  document.addEventListener('keydown',e=>{if(e.target.closest?.('input,textarea,select')||(e.target.closest?.('button')&&[' ','Enter'].includes(e.key))){clear();e.stopImmediatePropagation();return;}if(e.key.toLowerCase()==='r'&&ready()){e.preventDefault();e.stopImmediatePropagation();scan();return;}if(blocked()&&!window.FireLabBonus?.isOpen()){clear();if(['arrowup','arrowdown','arrowleft','arrowright','w','a','s','d','e','q','m','r'].includes(e.key.toLowerCase())){e.stopImmediatePropagation();if(!document.querySelector('dialog[open]'))e.preventDefault();}}},true);
  $('characterPicker').addEventListener('close',()=>{if(pendingSave&&$('rpgResume'))modal('저장한 탐험을 이어갈까요?',$('rpgResume'));});
  d.addEventListener('cancel',e=>{if(pendingSave)e.preventDefault();});
  $('rpgDialogClose').addEventListener('click',()=>{if(pendingSave&&$('rpgResume'))document.querySelector('.rpg-toolbar').after($('rpgResume'));});
  document.addEventListener('click',()=>{if(!pendingSave&&d.open&&!$('rpgResume')&&$('rpgDialogTitle').textContent==='저장한 탐험을 이어갈까요?')d.close();setTimeout(schedule,0);});window.addEventListener('blur',clear);document.addEventListener('visibilitychange',()=>{clear();if(document.hidden)save();});window.addEventListener('pagehide',save);
  new MutationObserver(()=>{if(blocked())clear();}).observe(document.body,{attributes:true,attributeFilter:['class','open'],subtree:true});
  setInterval(()=>{if(!pendingSave)save();},10000);
 }
 window.FireLabRPG={register,blocked,collision,interact,draw,answer,complete,beforeSwitch,activate,resetting,prepare,save,schedule,feedback,reward,clear,scan,paintBot,botState:()=>bot.state,getStage:()=>active,getRoom:n=>progress.rooms[n],getSnapshot:()=>({active,progress:clone(progress),bot:clone(bot),stages:Object.fromEntries([...adapters].map(([n,a])=>[n,a.get()?{portal:a.get().rpgPortal,solid:objects(n,a.get()).map(o=>({x:o.x,y:o.y}))}:null]))}),getAdapter:n=>adapters.get(n),theme};
 document.addEventListener('DOMContentLoaded',init);
})();
