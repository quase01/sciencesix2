// Decode the actual RGBA PNG sheets to measure each frame's visible body.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const root=path.resolve(__dirname,'..'),out={};
for(const file of fs.readdirSync(path.join(root,'props')).filter(f=>f.endsWith('.png'))){
 const b=fs.readFileSync(path.join(root,'props',file));let p=8,w,h,channels,parts=[];
 while(p<b.length){const n=b.readUInt32BE(p),type=b.toString('ascii',p+4,p+8),d=b.subarray(p+8,p+8+n);if(type==='IHDR'){w=d.readUInt32BE(0);h=d.readUInt32BE(4);if(d[8]!==8||![2,6].includes(d[9]))throw Error(file+' unsupported PNG');channels=d[9]===6?4:3;}if(type==='IDAT')parts.push(d);p+=n+12;}
 const raw=zlib.inflateSync(Buffer.concat(parts)),stride=w*channels,rows=[];let pos=0;
 const paeth=(a,b,c)=>{const q=a+b-c,A=Math.abs(q-a),B=Math.abs(q-b),C=Math.abs(q-c);return A<=B&&A<=C?a:B<=C?b:c;};
 for(let y=0;y<h;y++){const filter=raw[pos++],r=Buffer.from(raw.subarray(pos,pos+stride));pos+=stride;for(let i=0;i<stride;i++){const a=i>=channels?r[i-channels]:0,b=rows[y-1]?.[i]||0,c=i>=channels?(rows[y-1]?.[i-channels]||0):0;r[i]=(r[i]+[0,a,b,Math.floor((a+b)/2),paeth(a,b,c)][filter])&255;}rows.push(r);}
 const frames=w===192?1:2,cw=w/frames,bs=[];
 for(let f=0;f<frames;f++){let l=cw,r=0,t=h,bot=0;for(let y=0;y<h;y++)for(let x=0;x<cw;x++){if(channels===3||rows[y][(x+f*cw)*channels+3]>100){l=Math.min(l,x);r=Math.max(r,x);t=Math.min(t,y);bot=Math.max(bot,y);}}bs.push([l,t,r-l+1,bot-t+1]);}out[file.slice(0,-4)]=bs;
}
fs.writeFileSync(path.join(root,'prop-metadata.js'),'window.FireLabPropBounds='+JSON.stringify(out)+';\n');console.log(Object.keys(out).length+' measured sheets');
