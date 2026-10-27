const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.join(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'characters.js'), 'utf8');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');

function setup(withStages = false) {
  const nodes = new Map(), draws = [], pending = new Map();
  let nextId = 0, now = 1000;
  const events = {};
  const ctx = new Proxy({
    drawImage(...args) { draws.push(args); },
    measureText() { return { width: 20 }; },
    createLinearGradient() { return { addColorStop() {} }; },
    createRadialGradient() { return { addColorStop() {} }; }
  }, { get: (target, key) => target[key] ?? (() => {}) });
  function node(id = '') {
    const classes = new Set(['hidden']);
    return {
      id, tagName: 'DIV', dataset: {}, style: {}, attrs: {}, handlers: {}, children: new Map(),
      width: 722, height: 570, open: false,
      classList: {
        add: (...items) => items.forEach(item => classes.add(item)),
        remove: (...items) => items.forEach(item => classes.delete(item)),
        contains: item => classes.has(item),
        toggle(item, value = !classes.has(item)) { value ? classes.add(item) : classes.delete(item); }
      },
      setAttribute(key, value) { this.attrs[key] = value; },
      addEventListener(type, fn) { (this.handlers[type] ||= []).push(fn); },
      click() { (this.handlers.click || []).forEach(fn => fn({ target: this })); },
      focus() { document.activeElement = this; },
      matches() { return false; }, closest() { return null; }, scrollIntoView() {},
      showModal() { this.open = true; }, close() { this.open = false; },
      getContext() { return ctx; },
      querySelector(selector) {
        if (!this.children.has(selector)) this.children.set(selector, node());
        return this.children.get(selector);
      },
      querySelectorAll() { return []; }
    };
  }
  function get(id) { if (!nodes.has(id)) nodes.set(id, node(id)); return nodes.get(id); }
  const cards = ['boy', 'girl'].map(id => { const card = node(id); card.dataset.character = id; return card; });
  get('characterPicker').querySelectorAll = () => cards;
  get('.main-grid').classList.remove('hidden');
  const document = {
    body: get('body'), activeElement: get('body'),
    getElementById: get, querySelector: get, querySelectorAll: () => [], createElement: () => node(),
    addEventListener(type, fn) { (events[type] ||= []).push(fn); }
  };
  const env = {
    document, window: { addEventListener() {}, scrollTo() {} }, console,
    performance: { now: () => now }, matchMedia: () => ({ matches: false }),
    localStorage: { getItem() { return null; }, setItem() {} },
    Image: class {
      naturalWidth = 1086; naturalHeight = 1448;
      set src(value) { this.source = value; this.onload(); }
    },
    requestAnimationFrame(fn) { const id = ++nextId; pending.set(id, fn); return id; },
    cancelAnimationFrame(id) { pending.delete(id); },
    setTimeout: () => 1, clearTimeout() {}, setInterval: () => 1, clearInterval() {}, confirm: () => true
  };
  const context = vm.createContext(env);
  vm.runInContext(source, context);
  if (withStages) {
    for (const [, script] of html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)) {
      if (script.includes('function drawPlayer')) vm.runInContext(script, context);
    }
  }
  return {
    env, get, ctx, draws, character: env.window.FireLabCharacter,
    select(id) { env.window.FireLabCharacter.open(); cards.find(c => c.dataset.character === id).click(); get('characterConfirm').click(); },
    tick(t) { now = t; const callbacks = [...pending.values()]; pending.clear(); callbacks.forEach(fn => fn(t)); },
    key(type, key) {
      const event = { key, target: document.body, preventDefault() {}, stopImmediatePropagation() { this.stopped = true; } };
      for (const fn of events[type] || []) { fn(event); if (event.stopped) break; }
    },
    draw(player, t, motion, duration = 110) {
      draws.length = 0;
      env.window.FireLabCharacter.draw(ctx, player, t, 50, 50, motion, duration);
      return draws.at(-1);
    }
  };
}

for (const gender of ['boy', 'girl']) {
  test(`${gender}: separate taps alternate feet and settle to standing`, () => {
    const f = setup(); f.select(gender);
    const p = { face: 2 };
    const first = f.draw(p, 1000, 1000).slice(1, 5);
    for (let t = 1050; t <= 1500; t += 50) f.draw(p, t, 1000);
    const idle = f.draw(p, 1900, 1000).slice(1, 5);
    assert.equal(p.spriteGait.settled, true);
    const opposite = f.draw(p, 2000, 2000).slice(1, 5);
    assert.notDeepEqual(first, opposite);
    assert.notDeepEqual(first, idle);
    for (let t = 2050; t <= 2500; t += 50) f.draw(p, t, 2000);
    assert.deepEqual(f.draw(p, 2700, 2000).slice(1, 5), idle);
    assert.deepEqual(f.draw(p, 3000, 3000).slice(1, 5), first);
  });

  test(`${gender}: all directions retain gait and a constant sprite scale`, () => {
    const f = setup(); f.select(gender);
    const p = { face: 2 };
    f.draw(p, 1000, 1000);
    const sampledRows = new Set(), scales = new Set();
    for (let i = 1; i <= 32; i++) {
      p.face = Math.floor(i / 8) % 4;
      const d = f.draw(p, 1000 + i * 25, 1000 + i * 25);
      sampledRows.add(Math.floor((d[2] + d[4] / 2) / 362));
      scales.add(Number((d[7] / d[3]).toFixed(8)));
    }
    assert.equal(sampledRows.size, 4);
    assert.equal(scales.size, 1);
    assert.equal(p.spriteGait.settled, false);
  });

  test(`${gender}: moving and rendering work in all six stages`, () => {
    const f = setup(true); f.select(gender);
    for (let stage = 1; stage <= 6; stage++) {
      const api = f.env.window[stage === 1 ? 'FireLab' : `FireLabStage${stage}`];
      if (stage > 1) api.start();
      assert.equal(api.getSnapshot().phase, 'intro');
      assert.equal(api.move(1, 0, 1000), false);
      f.get(stage === 1 ? 'startBtn' : `s${stage}Ready`).click();
      const before = api.getSnapshot();
      const dir = [[1, 0], [0, 1], [-1, 0], [0, -1]].find(([dx, dy]) => before.map[before.player.y + dy]?.[before.player.x + dx] === 0);
      const t = 2000 + stage * 500;
      assert.equal(api.move(...dir, t), true);
      assert.equal(api.getSnapshot().player.x, before.player.x + dir[0]);
      assert.equal(api.getSnapshot().player.y, before.player.y + dir[1]);
      f.draws.length = 0; f.tick(t + 45);
      assert.ok(f.draws.some(d => d[0].source === `character${gender === 'boy' ? 1 : 2}-walk.png`));
    }
  });
}

test('stage 1 held movement continues without OS keyboard repeat', () => {
  const f = setup(true); f.select('boy'); f.get('startBtn').click(); f.tick(1000);
  const api = f.env.window.FireLab;
  const before = api.getSnapshot();
  const [key, dx, dy] = [['ArrowRight', 1, 0], ['ArrowDown', 0, 1], ['ArrowLeft', -1, 0], ['ArrowUp', 0, -1]]
    .find(([, dx, dy]) => before.map[before.player.y + dy]?.[before.player.x + dx] === 0);
  f.key('keydown', key);
  const first = api.getSnapshot();
  f.tick(1100);
  const second = api.getSnapshot();
  const canContinue = first.map[first.player.y + dy]?.[first.player.x + dx] === 0;
  assert.equal(second.player.x, first.player.x + (canContinue ? dx : 0));
  assert.equal(second.player.y, first.player.y + (canContinue ? dy : 0));
  f.key('keyup', key); f.tick(1300);
  assert.deepEqual(api.getSnapshot().player, second.player);
});

test('PNG assets exist and all embedded game scripts compile', () => {
  for (const file of ['character1-walk.png', 'character2-walk.png']) {
    const data = fs.readFileSync(path.join(root, file));
    assert.equal(data.subarray(1, 4).toString(), 'PNG');
    assert.equal(data.readUInt32BE(16), 1086);
    assert.equal(data.readUInt32BE(20), 1448);
  }
  for (const [, script] of html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)) new vm.Script(script);
});
