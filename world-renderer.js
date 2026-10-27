/* Shared foot anchors, depth queue and fallback rendering. Original PNGs are untouched. */
(() => {
  'use strict';
  const queues=new WeakMap(), effects=new Map();
  const defs={
    's1-mixing-bench':{width:88,height:46,frames:2},
    's1-flour':{height:28,frames:1},'s1-vinegar':{height:33,frames:1},
    's1-baking-soda':{height:31,frames:1},'s1-key':{height:24,frames:1},
    'guide-robot':{height:34},'s2-firebot':{height:40}
  };
  function definition(file){return {width:48,height:45,anchorX:.5,anchorY:1,collisionWidth:28,collisionHeight:18,interactive:true,frames:2,...defs[file]};}
  function begin(ctx){queues.set(ctx,{items:[],flushing:false});}
  function enqueue(ctx,y,paint){const q=queues.get(ctx);if(!q||q.flushing)return false;q.items.push({y,paint});return true;}
  function flush(ctx){const q=queues.get(ctx);if(!q)return;q.flushing=true;q.items.sort((a,b)=>a.y-b.y).forEach(o=>o.paint());queues.delete(ctx);}
  function sprite(ctx,im,frame,frames,x,feetY,maxW,maxH){
    if(!im?.complete||!im.naturalWidth)return false;
    const file=im.dataset?.asset||im.src.split('/').pop().replace('.png','');
    const d=definition(file),cell=im.naturalWidth/frames;
    const bounds=window.FireLabPropBounds?.[file]?.[frame]||[0,0,cell,im.naturalHeight];
    const [sx,sy,w,h]=bounds,scale=Math.min(maxW/w,maxH/h);
    ctx.save();ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';
    ctx.drawImage(im,frame*cell+sx,sy,w,h,x-w*scale/2,feetY-h*scale,w*scale,h*scale);ctx.restore();return true;
  }
  function prop(ctx,im,on,x=0,y=14){const file=im.dataset?.asset||im.src.split('/').pop().replace('.png',''),d=definition(file);return sprite(ctx,im,Number(on),d.frames,x,y,d.width,d.height);}
  function highlight(ctx,o,p,t){if(!p)return;const near=Math.abs(p.x-o.x)+Math.abs(p.y-o.y)<=1;
    const x=o.x*38+19,y=o.y*38+19,optional=o.kind==='extra'||o.type==='extra'||['bot','archive','helper','poster','crate','board','terminal'].includes(o.id);
    ctx.save();ctx.font='10px sans-serif';ctx.textAlign='center';ctx.fillStyle=o.done?'#a9efd0':optional?'#9cafc0':'#ffe0a1';ctx.fillText(optional?'·':'◆',x+18,y+14);ctx.restore();if(!near)return;
    ctx.save();ctx.strokeStyle=optional?'#a9c0d0':'#ffe3a3';ctx.lineWidth=2;ctx.setLineDash(optional?[3,3]:[]);ctx.globalAlpha=.65+.2*Math.sin(t/180);ctx.beginPath();ctx.ellipse(x,y+13,18,7,0,0,Math.PI*2);ctx.stroke();ctx.globalAlpha=1;ctx.setLineDash([]);ctx.fillStyle='#112536';ctx.fillRect(x-11,y-59,22,18);ctx.font='bold 12px sans-serif';ctx.textAlign='center';ctx.fillStyle='#fff5ce';ctx.fillText('E',x,y-46);ctx.restore();
  }
  window.FireLabWorld={begin,enqueue,flush,sprite,prop,highlight,definition,effects};
})();
