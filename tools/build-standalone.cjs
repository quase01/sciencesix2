const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),out=path.join(root,'dist');fs.mkdirSync(out,{recursive:true});
let html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const assets={},files=['character1-walk.png','character2-walk.png',...fs.readdirSync(path.join(root,'props')).filter(f=>f.endsWith('.png')).map(f=>'props/'+f)];
for(const f of files)assets[f]='data:image/png;base64,'+fs.readFileSync(path.join(root,f)).toString('base64');
html=html.replace('</head>','<script>window.FireLabAssets='+JSON.stringify(assets)+';</script>\n</head>');
html=html.replace(/<link rel="stylesheet" href="([^"\s]+)"\s*\/?>/g,(_,f)=>'<style>\n'+fs.readFileSync(path.join(root,f),'utf8')+'\n</style>');
html=html.replace(/<script src="([^"\s]+)"><\/script>/g,(_,f)=>'<script>\n'+fs.readFileSync(path.join(root,f),'utf8').replace(/<\/script/gi,'<\\/script')+'\n</script>');
const file=path.join(out,'불꽃연구소-단독실행.html');fs.writeFileSync(file,html);fs.writeFileSync(path.join(out,'build-info.json'),JSON.stringify({createdAt:new Date().toISOString(),assets:files.length,bytes:Buffer.byteLength(html),sha256:crypto.createHash('sha256').update(html).digest('hex')},null,2));console.log(file+' · '+(Buffer.byteLength(html)/1024/1024).toFixed(2)+' MB · '+files.length+' embedded assets');
