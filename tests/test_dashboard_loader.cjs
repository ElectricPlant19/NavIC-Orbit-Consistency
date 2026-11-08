const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const {webcrypto,createHash} = require('node:crypto');
const source=fs.readFileSync('dashboard/dist/app.js','utf8').split('async function readFeed(base){')[1].split('refreshPublished();setInterval')[0];
function fixture(day,generated){
  const summary=JSON.stringify({run_id:day,generated_at:generated}),epochs='[]';
  const hash=x=>createHash('sha256').update(x).digest('hex');
  return {summary,epochs,index:JSON.stringify({summary:'summary.json',epochs:'epochs.json',summary_sha256:hash(summary),epochs_sha256:hash(epochs),artifacts:{test:'hash'}})};
}
function context(local,remote){
  const calls=[];
  const ctx={run:null,feedBase:'data/',fitArtifacts:{},TextEncoder,crypto:webcrypto,AbortController,setTimeout,clearTimeout,Date,
    toast:()=>{},load:(summary)=>{ctx.run=summary},fetch:async(url)=>{
      calls.push(url);
      if(url==='feed.json')return {ok:true,text:async()=>JSON.stringify({base_url:'https://feed.test/'})};
      const f=url.startsWith('data/')?local:remote;
      if(typeof f==='function')return f(url);
      return {ok:true,text:async()=>url.includes('latest.json')?f.index:url.endsWith('summary.json')?f.summary:f.epochs};
    }};
  vm.createContext(ctx);vm.runInContext('async function readFeed(base){'+source,ctx);
  return {ctx,calls};
}
test('bundled run renders before a stalled remote request',async()=>{
  let rejectRemote;
  const local=fixture('local','2026-11-08T12:00:00Z');
  const {ctx,calls}=context(local,()=>new Promise((resolve,reject)=>{rejectRemote=reject}));
  const pending=ctx.refreshPublished();
  for(let n=0;n<20&&!rejectRemote;n++)await new Promise(resolve=>setImmediate(resolve));
  assert.equal(ctx.run.run_id,'local');
  assert.ok(calls[0].startsWith('data/latest.json'));
  rejectRemote(new Error('offline'));await pending;
  assert.equal(ctx.run.run_id,'local');
});
test('older cached remote results cannot replace the bundled run',async()=>{
  const {ctx}=context(fixture('new','2026-11-08T12:00:00Z'),fixture('old','2026-11-08T11:00:00Z'));
  await ctx.refreshPublished();assert.equal(ctx.run.run_id,'new');
});
test('newer checksum-verified remote results replace the bundled run',async()=>{
  const {ctx}=context(fixture('old','2026-11-08T11:00:00Z'),fixture('new','2026-11-08T12:00:00Z'));
  await ctx.refreshPublished();assert.equal(ctx.run.run_id,'new');assert.equal(ctx.feedBase,'https://feed.test/');
});
test('tampered or partially cached feed leaves the current run intact',async()=>{
  const remote=fixture('tampered','2026-11-08T13:00:00Z');remote.summary+=' ';
  const {ctx}=context(fixture('valid','2026-11-08T12:00:00Z'),remote);
  await ctx.refreshPublished();assert.equal(ctx.run.run_id,'valid');
});
