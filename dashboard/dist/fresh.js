let freshReport=null,freshBase='fresh/',freshArtifacts={};
async function verifiedFreshFile(base,name,digest){
  const text=await feedText(base+name);
  const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(text)))].map(x=>x.toString(16).padStart(2,'0')).join('');
  if(!digest||hash!==digest)throw Error('Current-day artifact checksum mismatch; keeping the previous assessment');
  return text;
}
async function readFresh(base){
  const index=JSON.parse(await feedText(base+'latest.json?check='+Date.now()));
  const report=JSON.parse(await verifiedFreshFile(base,index.summary,index.summary_sha256));
  if(freshReport&&Date.parse(freshReport.generated_at)>=Date.parse(report.generated_at))return;
  freshReport=report;freshBase=base;freshArtifacts=index.artifacts||{};renderFresh();
}
async function refreshFresh(){
  if(!freshReport){try{await readFresh('fresh/')}catch(error){$('fresh-state').textContent='No current-day acquisition result loaded yet.'}}
  try{const config=JSON.parse(await feedText('feed.json'));await readFresh(new URL('../fresh/',config.base_url).href)}
  catch(error){if(!freshReport)$('fresh-state').textContent='Current-day acquisition unavailable. The completed daily run remains separate.'}
}
function renderFresh(){
  const a=freshReport.acquisition,q=a.freshness,b=freshReport.benchmark;
  $('fresh-state').textContent=`Checked ${q.checked_at} · ${q.usable_satellites} / ${q.satellites_present} present satellites usable under the analysis policy`;
  $('fresh-source').textContent=a.selected_input.source.split('/').pop();$('fresh-source').href=a.selected_input.source;
  $('fresh-http').textContent=`HTTP ${a.selected_input.http_status||'cached'} · server modified ${a.selected_input.server_last_modified||'not supplied'} · first received ${a.selected_input.first_received_at||a.selected_input.retrieved_at}`;
  $('fresh-quality').innerHTML=q.satellites.map(s=>`<tr><td><strong>${escapeHTML(s.prn)}</strong></td><td class="number">${escapeHTML(s.toe_utc.slice(11,19))}</td><td class="number">${fmt(s.toe_age_seconds/60,1)}</td><td class="number">${s.iodec}</td><td class="number">${s.health} / ${s.ura_m}</td><td><span class="status ${s.usable_now?'close':'review'}">${s.usable_now?'Usable':'Gap'}</span><small class="fit-subname">${escapeHTML(s.flags.join(', '))}</small></td></tr>`).join('');
  $('fresh-validity').textContent=`Validity cutoff: ±${q.validity_limit_seconds/3600} h around toe. ${q.validity_status}. A new download or repeated message is not necessarily a new ephemeris.`;
  $('fresh-benchmark-window').textContent=b.forecast_origin_utc?`Retrospective check: ${b.forecast_origin_utc} → ${b.validation_end_utc} · ${b.train_hours} h fitting · control inputs end ${b.delayed_input_hours} h earlier`:'Acquisition only; no benchmark requested.';
  $('fresh-results').innerHTML=(b.satellites||[]).map(s=>{
    const recent=s.models?.fresh?.validation,old=s.models?.delayed?.validation,gp=s.standard_gp?.metrics;
    return `<tr class="clickable" tabindex="0" data-fresh-prn="${escapeHTML(s.prn)}" aria-label="Inspect freshness experiment ${escapeHTML(s.prn)}"><td><strong>${escapeHTML(s.prn)}</strong><small class="fit-subname">${escapeHTML(s.name)}</small></td><td class="number">${fmt(recent?.rms_km,3)}</td><td class="number">${fmt(old?.rms_km,3)}</td><td class="number">${fmt(gp?.rms_km,3)}<small class="fit-subname">${gp?'GP age '+fmt(s.standard_gp.age_at_issue_hours,1)+' h':'No eligible snapshot'}</small></td><td class="number">${recent?.epochs||0}</td><td>${s.comparison?`<span class="status ${s.comparison.rms_reduction_percent>0?'close':'review'}">${fmt(s.comparison.rms_reduction_percent,1)}%</span>`:'—'}</td></tr>`;
  }).join('')||'<tr><td colspan="6" class="empty-row">No benchmark requested.</td></tr>';
  document.querySelectorAll('[data-fresh-prn]').forEach(row=>{const inspect=()=>showDialog(`${row.dataset.freshPrn} input-recency experiment`,b.satellites.find(s=>s.prn===row.dataset.freshPrn));row.onclick=inspect;row.onkeydown=e=>{if(e.key==='Enter')inspect()}});
  $('fresh-report').disabled=false;$('fresh-report').onclick=async()=>{try{showDialog('Current-day acquisition and recency report',await verifiedFreshFile(freshBase,'report.md',freshArtifacts['report.md']))}catch(e){toast(e.message)}};
  $('fresh-manifest').disabled=false;$('fresh-manifest').onclick=()=>showDialog('Current-day acquisition manifest',freshReport);
}
