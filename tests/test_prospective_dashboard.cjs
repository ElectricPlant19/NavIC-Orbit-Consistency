const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const {webcrypto,createHash}=require('node:crypto');
const source=fs.readFileSync('dashboard/dist/prospective.js','utf8');
const verification=fs.readFileSync('dashboard/dist/fresh.js','utf8').split('async function verifiedFreshFile')[1].split('async function readFresh')[0];
function context(){
  const elements={};
  const ctx={TextEncoder,crypto:webcrypto,Date,URL,console,
    $:id=>elements[id]??=( {innerHTML:'',textContent:'',hidden:false,disabled:false} ),
    escapeHTML:x=>String(x),fmt:(x,n=2)=>x==null?'—':Number(x).toFixed(n)};
  vm.createContext(ctx);vm.runInContext('async function verifiedFreshFile'+verification+source,ctx);
  return {ctx,elements};
}
test('prospective feed verifies checksums and never replaces a newer report with older data',async()=>{
  const {ctx}=context();ctx.renderTracking=()=>{};
  let report={generated_at:'2020-01-01T02:00:00Z',issue_count:3};
  ctx.feedText=async url=>{
    const text=JSON.stringify(report),hash=createHash('sha256').update(text).digest('hex');
    return url.includes('latest.json')?JSON.stringify({summary:'summary.json',summary_sha256:hash,artifacts:{}}):text;
  };
  await ctx.readTracking('local/');
  report={generated_at:'2020-01-01T01:00:00Z',issue_count:1};await ctx.readTracking('remote/');
  assert.equal(vm.runInContext('trackingReport.issue_count',ctx),3);
  assert.equal(vm.runInContext('trackingBase',ctx),'local/');
  report={generated_at:'2020-01-01T03:00:00Z',issue_count:6};await ctx.readTracking('remote/');
  assert.equal(vm.runInContext('trackingReport.issue_count',ctx),6);
});
test('tampered prospective artifact cannot replace the displayed archive',async()=>{
  const {ctx}=context();ctx.renderTracking=()=>{};
  vm.runInContext("trackingReport={generated_at:'2020-01-01T01:00:00Z',issue_count:3}",ctx);
  ctx.feedText=async url=>url.includes('latest.json')?JSON.stringify({summary:'summary.json',summary_sha256:'bad'}):JSON.stringify({generated_at:'2020-01-01T02:00:00Z'});
  await assert.rejects(ctx.readTracking('remote/'),/checksum/);
  assert.equal(vm.runInContext('trackingReport.issue_count',ctx),3);
});
test('chart preserves missing epochs and splits the latest-GP line at element changes',()=>{
  const {ctx,elements}=context();
  const point=(id)=>({separation_km:1,element_id:id});
  const rows=[{utc:'a',forecast_age_hours:.1,ours:point('a'),frozen_gp:point('a'),latest_gp:point('a')},
    {utc:'b',forecast_age_hours:.2,ours:point('a'),frozen_gp:point('a'),latest_gp:point('b')},
    {utc:'c',forecast_age_hours:.3,ours:null,frozen_gp:null,latest_gp:null},
    {utc:'d',forecast_age_hours:.4,ours:point('a'),frozen_gp:point('a'),latest_gp:point('b')}];
  vm.runInContext('trackingDetail='+JSON.stringify({issue:{policy:{step_seconds:360}},rows}),ctx);
  ctx.renderTrackingChart();
  const paths=[...elements['track-chart'].innerHTML.matchAll(/<path d="([^"]*)"/g)].map(m=>m[1]);
  assert.equal(paths.length,3);
  assert.equal((paths[0].match(/M/g)||[]).length,2);
  assert.equal((paths[2].match(/M/g)||[]).length,3);
  assert.equal(elements['track-empty'].hidden,true);
});
test('waiting archive renders no invented curve',()=>{
  const {ctx,elements}=context();ctx.renderTrackingChart();
  assert.equal(elements['track-empty'].hidden,false);
  assert.ok(!elements['track-chart'].innerHTML.includes('<circle'));
});
test('selected-issue CSV preserves absent reference and GP values as gaps',()=>{
  const {ctx}=context();
  const text=ctx.trackingEpochCSV({issue:{issue_id:'id',prn:'I10',issued_at:'2020-01-01T00:00:00Z'},
    rows:[{utc:'2020-01-01T00:05:00Z',forecast_age_hours:1/12,model_age_hours:1/12,
           ours:null,frozen_gp:null,latest_gp:null,reference:null,flags:['later_reference_missing']}]});
  const lines=text.trim().split('\n');
  assert.equal(lines.length,4);
  assert.ok(lines[1].includes('"ours","","","",""'));
  assert.ok(lines[3].includes('"later_reference_missing"'));
});
