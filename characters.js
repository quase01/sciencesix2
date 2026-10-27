(() => {
  'use strict';
  const characters = {
    boy: { name: '남자 연구원', src: 'character1-walk.png', referenceHeight: 350, frames: [
      [[109,6,251,348,249],[458,5,164,350,537],[724,6,280,348,861]],
      [[95,364,265,347,218],[464,364,163,348,546],[733,363,288,349,876]],
      [[122,720,202,341,226],[452,720,179,335,540],[755,721,209,341,859]],
      [[120,1066,196,354,212],[449,1066,185,349,540],[766,1067,194,353,857]]
    ] },
    girl: { name: '여자 연구원', src: 'character2-walk.png', referenceHeight: 350, frames: [
      [[95,26,258,338,239],[434,23,244,341,561],[757,27,257,338,899]],
      [[89,384,273,340,205],[447,384,249,339,562],[770,384,268,339,887]],
      [[96,730,240,331,212],[439,735,234,326,558],[787,733,231,328,901]],
      [[61,1071,281,347,235],[432,1071,247,347,573],[761,1071,274,347,936]]
    ] }
  };
  // Game facing: up, right, down, left. Sheet rows: right, left, up, down.
  const rowForFace = [2, 0, 3, 1];
  // Left step -> feet together -> right step -> feet together.
  const walkSequence = [0, 1, 2, 1];
  const walkFrameMs = 100;
  const storageKey = 'firelab-character';
  const dialog = document.getElementById('characterPicker');
  const confirm = document.getElementById('characterConfirm');
  const status = document.getElementById('characterStatus');
  const cards = [...dialog.querySelectorAll('[data-character]')];
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  let selected = null, pending = null, returnFocus = null, previewRequest = 0;
  try { if (characters[localStorage.getItem(storageKey)]) pending = localStorage.getItem(storageKey); } catch (_) {}

  function syncChoice() {
    for (const card of cards) {
      const active = card.dataset.character === pending;
      card.setAttribute('aria-pressed', String(active));
      card.querySelector('.character-choice').textContent = active ? '✓ 선택됨' : '선택하기';
    }
    const character = characters[pending];
    confirm.disabled = !character?.ready;
    confirm.textContent = character ? `${character.name}으로 준비 완료 →` : '캐릭터를 선택해 주세요';
    status.textContent = !character ? '함께 탐험할 캐릭터를 골라 주세요.'
      : character.error ? '이미지 대신 기본 연구원으로 계속 탐험할 수 있어요.'
      : character.ready ? `${character.name} 선택! 모든 스테이지에서 함께 탐험해요.`
      : '캐릭터를 불러오는 중이에요…';
    if (character?.error) {
      confirm.disabled = false;
      confirm.textContent = '기본 연구원으로 준비 완료 →';
    }
  }

  function load(character) {
    character.ready = false;
    character.error = false;
    const sheet = new Image();
    character.image = sheet;
    sheet.onload = () => { character.ready = true; syncChoice(); };
    sheet.onerror = () => { character.error = true; syncChoice(); };
    sheet.src = window.FireLabAssets?.[character.src] || character.src;
  }

  function paint(ctx, character, face, frame, x, feetY, size) {
    if (!character?.ready) {ctx.save();ctx.fillStyle=character===characters.girl?'#ed9bbd':'#80d6eb';ctx.fillRect(x-size*.16,feetY-size*.6,size*.32,size*.4);ctx.fillStyle='#f4cfac';ctx.beginPath();ctx.arc(x,feetY-size*.74,size*.14,0,Math.PI*2);ctx.fill();ctx.fillStyle='#26364d';const stride=frame===1?0:frame===0?size*.08:-size*.08;ctx.fillRect(x-size*.14,feetY-size*.2+stride,size*.1,size*.2);ctx.fillRect(x+size*.04,feetY-size*.2-stride,size*.1,size*.2);ctx.restore();return;}
    const sheet = character.image;
    // The artwork is not an exact grid: use per-frame bounds to keep hair and feet intact.
    // Use one scale per character and fixed torso anchors; never stretch each pose to fit.
    const [sx, sy, w, h, anchorX] = character.frames[rowForFace[face]][frame];
    const scale = size / character.referenceHeight;
    ctx.save();
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(sheet, sx, sy, w, h,
      x - (anchorX - sx) * scale, feetY - h * scale, w * scale, h * scale);
    ctx.restore();
  }

  function previews(t) {
    if (!dialog.open) { previewRequest = 0; return; }
    const face = reducedMotion.matches ? 2 : [2, 1, 0, 3][Math.floor(t / 1800) % 4];
    const frame = reducedMotion.matches ? 1 : walkSequence[Math.floor(t / walkFrameMs) % 4];
    cards.forEach(card => {
      const canvas = card.querySelector('canvas'), ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = '#07142866';
      ctx.beginPath();ctx.ellipse(100, 180, 48, 9, 0, 0, Math.PI * 2);ctx.fill();
      paint(ctx, characters[card.dataset.character], face, frame, 100, 184, 174);
    });
    previewRequest = requestAnimationFrame(previews);
  }

  function open() {
    if (dialog.open) return;
    returnFocus = document.activeElement;
    pending = selected || pending;
    syncChoice();
    dialog.showModal();
    document.body.classList.add('choosing-character');
    (cards.find(card => card.dataset.character === pending) || cards[0]).focus();
    if (!previewRequest) previewRequest = requestAnimationFrame(previews);
  }

  function close() {
    dialog.close();
    document.body.classList.remove('choosing-character');
    cancelAnimationFrame(previewRequest);previewRequest = 0;
    const target = returnFocus?.matches('button') ? returnFocus : document.getElementById('startBtn');
    target.focus({ preventScroll: true });
  }

  cards.forEach(card => card.addEventListener('click', () => {
    pending = card.dataset.character;
    syncChoice();
  }));
  confirm.addEventListener('click', () => {
    const character = characters[pending];
    
    if (!character || (!character.ready&&!character.error)) return;
    selected = pending;
    try { localStorage.setItem(storageKey, selected); } catch (_) {}
    document.querySelectorAll('[data-change-character]').forEach(button => {
      button.textContent = `${character.name} · 캐릭터 바꾸기`;
    });
    close();
  });
  dialog.addEventListener('cancel', event => {
    event.preventDefault();
    if (selected) close();
  });
  // Let native Tab/Enter/Space button actions work without sending them to the game.
  document.addEventListener('keydown', event => {
    if (!dialog.open) {
      if (event.target.closest?.('[data-change-character]') && [' ', 'Enter'].includes(event.key)) event.stopImmediatePropagation();
      return;
    }
    event.stopImmediatePropagation();
    if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(event.key)) {
      event.preventDefault();
      pending = pending === 'boy' ? 'girl' : 'boy';
      syncChoice();
      cards.find(card => card.dataset.character === pending).focus();
    }
  }, true);
  document.addEventListener('click', event => {
    if (event.target.closest('[data-change-character]')) open();
  });

  window.FireLabCharacter = {
    open,
    ensureSelected() {
      if (selected && (characters[selected].ready||characters[selected].error) && !dialog.open) return true;
      open();return false;
    },
    draw(ctx, player, t, x, y, motion, duration = 115) {
      const character = characters[selected || pending];
      if (!character) return;
      // Keep left/right foot phase across tiles and direction changes. A short tap
      // finishes on the next neutral pose; the next tap starts with the other foot.
      const gait = player.spriteGait ||= { phase: 3, lastTime: t, settled: true };
      const delta = Math.max(0, Math.min(60, t - gait.lastTime));
      gait.lastTime = t;
      const walking = motion > 0 && t >= motion && t - motion < duration;
      if (walking) {
        if (gait.settled) gait.phase = (gait.phase + 1) % 4;
        else gait.phase = (gait.phase + delta / walkFrameMs) % 4;
        gait.settled = false;
      } else if (!gait.settled) {
        if (Math.floor(gait.phase) % 2 === 1) {
          gait.phase = Math.floor(gait.phase);
          gait.settled = true;
        } else {
          const nextRest = Math.floor(gait.phase) + 1;
          gait.phase = Math.min(nextRest, gait.phase + delta / walkFrameMs);
          if (gait.phase === nextRest) gait.settled = true;
        }
      }
      const frame = walkSequence[Math.floor(gait.phase) % 4];
      ctx.save();
      ctx.fillStyle = '#06132670';ctx.beginPath();ctx.ellipse(x, y + 13, 13, 5, 0, 0, Math.PI * 2);ctx.fill();
      paint(ctx, character, player.face ?? 2, frame, x, y + 17, 49);
      ctx.restore();
    },
    getSnapshot: () => ({ selected, pending, open: dialog.open, ready: !!characters[selected]?.ready })
  };
  Object.values(characters).forEach(load);
  open();
})();
