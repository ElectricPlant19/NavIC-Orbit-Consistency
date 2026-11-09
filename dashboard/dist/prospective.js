let trackingReport=null,trackingBase='prospective/',trackingArtifacts={},trackingDetail=null,trackingSat='all',trackingIssue='',trackingVersion='';
const legacyTrackingVersion='v1-position-6h';
function trackingVersions(){return trackingReport.versions?.length?trackingReport.versions:[{model_version:legacyTrackingVersion,label:'V1 · six-hour position fit (control)',fleet:trackingReport.fleet,satellites:trackingReport.satellites}]}
function trackingSelection(){return trackingVersions().find(v=>v.model_version===trackingVersion)||trackingVersions()[0]}
const trackCohorts=[['ours','Our frozen OMM','#078c7c'],['frozen_gp','GP frozen at issue','#c38a37'],['latest_gp','Latest GP received by epoch','#5675b8']];
async function readTracking(base){
  const index=JSON.parse(await feedText(base+'latest.json?check='+Date.now()));
  const report=JSON.parse(await verifiedFreshFile(base,index.summary,index.summary_sha256));
  if(trackingReport&&Date.parse(trackingReport.generated_at)>=Date.parse(report.generated_at))return;
  trackingReport=report;trackingBase=base;trackingArtifacts=index.artifacts||{};renderTracking();
}
async function refreshTracking(){
  if(!trackingReport){try{await readTracking('prospective/')}catch(error){$('track-state').textContent='No prospective archive loaded yet. Future scores are never fabricated.'}}
  try{const config=JSON.parse(await feedText('feed.json'));await readTracking(new URL('../prospective/',config.base_url).href)}
  catch(error){if(!trackingReport)$('track-state').textContent='Prospective archive unavailable. Existing daily and recent experiments remain separate.'}
}
function trackingAggregate(){const selected=trackingSelection();return trackingSat==='all'?selected.fleet:selected.satellites.find(s=>s.prn===trackingSat)}
function renderTracking(){
  const report=trackingReport;
  if(!trackingVersions().some(v=>v.model_version===trackingVersion))trackingVersion=trackingVersions()[0].model_version;
  const selected=trackingSelection(),issues=report.issues.filter(i=>(i.model_version||legacyTrackingVersion)===trackingVersion);
  $('track-version').innerHTML=trackingVersions().map(v=>`<option value="${escapeHTML(v.model_version)}">${escapeHTML(v.label)}</option>`).join('');
  $('track-version').value=trackingVersion;
  $('track-version').onchange=e=>{trackingVersion=e.target.value;trackingIssue='';trackingSat='all';renderTracking()};
  $('track-state').textContent=`Updated ${report.generated_at} · first actual issue ${report.first_issue_utc||'pending'} · ${report.policy.horizon_hours} h watch · ${report.policy.step_seconds/60} min samples`;
  $('track-version-note').textContent=selected.label+' · Cards, age bins and issues below use this version only. V2 remains experimental; replay improvements do not establish future performance. The recent-input retrospective panel above remains V1.';
  $('track-count').textContent=issues.length;
  $('track-scored').textContent=selected.fleet.ours?.epochs||0;
  $('track-pending').textContent=issues.reduce((n,i)=>n+i.pending_epochs,0);
  $('track-reviewed').textContent=issues.filter(i=>i.status==='Review').length;
  $('track-satellite').innerHTML='<option value="all">All satellites</option>'+selected.satellites.map(s=>`<option value="${escapeHTML(s.prn)}">${escapeHTML(s.prn)}</option>`).join('');
  if(!selected.satellites.some(s=>s.prn===trackingSat))trackingSat='all';
  $('track-satellite').value=trackingSat;
  $('track-satellite').onchange=e=>{trackingSat=e.target.value;trackingIssue='';renderTrackingTables()};
  $('track-issue').onchange=e=>{trackingIssue=e.target.value;loadTrackingDetail()};
  $('track-csv').disabled=!trackingArtifacts['statistics.csv'];
  $('track-csv').onclick=async()=>{const base=trackingBase,digest=trackingArtifacts['statistics.csv'];try{download('NAVIC-PROSPECTIVE-'+report.generated_at.replaceAll(':','-')+'.csv',await verifiedFreshFile(base,'statistics.csv',digest),'text/csv')}catch(e){toast(e.message)}};
  $('track-report').disabled=false;$('track-report').onclick=async()=>{try{showDialog('Prospective validation method and archive',await verifiedFreshFile(trackingBase,'report.md',trackingArtifacts['report.md']))}catch(e){toast(e.message)}};
  $('track-notes').textContent=report.notes.join(' ');
  $('track-attempts').textContent='Last issue check: '+report.last_issuance_attempts.map(a=>`${a.prn||'Fleet'}${a.model_version?' / '+a.model_version:''}: ${a.status}${a.reason?' ('+a.reason+')':''}`).join(' · ');
  renderTrackingTables();
}
function renderTrackingTables(){
  const issues=trackingReport.issues.filter(i=>(i.model_version||legacyTrackingVersion)===trackingVersion&&(trackingSat==='all'||i.prn===trackingSat));
  const aggregate=trackingAggregate();
  $('track-age').innerHTML=(aggregate?.age_bins||[]).map(b=>`<tr><td>${b.start_hours}–${b.end_hours} h</td><td class="number">${b.frozen_pair.common_epochs}</td><td class="number">${fmt(b.frozen_pair.ours?.rms_km,3)} / ${fmt(b.frozen_pair.baseline?.rms_km,3)}</td><td>${b.frozen_pair.rms_reduction_percent==null?'—':fmt(b.frozen_pair.rms_reduction_percent,1)+'%'}</td><td class="number">${b.latest_pair.common_epochs}</td><td class="number">${fmt(b.latest_pair.ours?.rms_km,3)} / ${fmt(b.latest_pair.baseline?.rms_km,3)}</td><td>${b.latest_pair.rms_reduction_percent==null?'—':fmt(b.latest_pair.rms_reduction_percent,1)+'%'}</td></tr>`).join('');
  $('track-rows').innerHTML=issues.map(i=>`<tr class="clickable" tabindex="0" data-track-id="${escapeHTML(i.issue_id)}" aria-label="Inspect prospective issue ${escapeHTML(i.issue_id)}"><td><strong>${escapeHTML(i.prn)}</strong><small class="fit-subname">${escapeHTML(i.name)}</small></td><td class="number">${escapeHTML(i.issued_at.replace('T',' ').replace('Z',''))}</td><td>${i.reference_epochs} / ${i.expected_due_epochs}<small class="fit-subname">${i.pending_epochs} pending · ${fmt(i.reference_coverage_percent,1)}% coverage</small></td><td class="number">${fmt(i.ours?.rms_km,3)} / ${fmt(i.ours?.max_km,3)}</td><td class="number">${fmt(i.frozen_pair.ours?.rms_km,3)} / ${fmt(i.frozen_pair.baseline?.rms_km,3)}<small class="fit-subname">${i.frozen_pair.common_epochs} matched</small></td><td class="number">${fmt(i.latest_pair.ours?.rms_km,3)} / ${fmt(i.latest_pair.baseline?.rms_km,3)}<small class="fit-subname">${i.latest_pair.common_epochs} matched</small></td><td><span class="status ${i.status==='Review'?'review':i.status==='Complete'?'close':'tracking'}">${escapeHTML(i.status)}</span></td></tr>`).join('')||'<tr><td colspan="7" class="empty-row">No models issued yet. The archive will begin when usable fitting data arrive.</td></tr>';
  if(!issues.some(i=>i.issue_id===trackingIssue))trackingIssue=issues.find(i=>i.ours)?.issue_id||issues[0]?.issue_id||'';
  $('track-issue').innerHTML=issues.map(i=>`<option value="${escapeHTML(i.issue_id)}">${escapeHTML(i.prn+' · '+i.issued_at+' · '+i.status)}</option>`).join('')||'<option value="">No issued model</option>';
  $('track-issue').value=trackingIssue;
  document.querySelectorAll('[data-track-id]').forEach(row=>{const inspect=()=>{trackingIssue=row.dataset.trackId;$('track-issue').value=trackingIssue;loadTrackingDetail()};row.onclick=inspect;row.onkeydown=e=>{if(e.key==='Enter')inspect()}});
  loadTrackingDetail();
}
async function loadTrackingDetail(){
  const key=trackingIssue,base=trackingBase,name='series/'+key+'.json',digest=trackingArtifacts[name];
  trackingDetail=null;$('track-omm').disabled=true;$('track-detail').disabled=true;$('track-epochs').disabled=true;
  $('track-chart-note').textContent=key?'Loading archived issue and checksum-verified scores…':'No issued model to inspect.';renderTrackingChart();
  if(!key)return;
  try{
    const detail=JSON.parse(await verifiedFreshFile(base,name,digest));
    if(trackingIssue!==key||trackingBase!==base)return;
    trackingDetail=detail;renderTrackingChart();
    const issue=detail.issue,summary=detail.summary;
    $('track-chart-note').textContent=`${issue.model_version||legacyTrackingVersion} · Frozen at ${issue.issued_at} · element epoch ${issue.model_epoch_utc}. ${summary.reference_epochs} later-message scores; ${summary.pending_epochs} due epochs still pending. ${summary.reasons.join(', ')}`;
    $('track-omm').disabled=false;$('track-omm').onclick=()=>download('NAVIC-PROSPECTIVE-'+issue.issue_id+'.omm.json',JSON.stringify([issue.omm],null,2)+'\n');
    $('track-epochs').disabled=false;$('track-epochs').onclick=()=>download('NAVIC-PROSPECTIVE-'+issue.issue_id+'-epochs.csv',trackingEpochCSV(detail),'text/csv');
    $('track-detail').disabled=false;$('track-detail').onclick=()=>showDialog('Frozen model, GP baseline and validation provenance',detail);
    $('track-rtn').innerHTML=trackCohorts.map(([cohort,label])=>{
      const valid=detail.rows.filter(r=>r[cohort]);
      const rms=axis=>valid.length?Math.sqrt(valid.reduce((n,r)=>n+r[cohort][axis]**2,0)/valid.length):null;
      const distances=valid.map(r=>r[cohort].separation_km).sort((a,b)=>a-b);const mean=valid.length?distances.reduce((a,b)=>a+b,0)/valid.length:null;const total=valid.length?Math.sqrt(distances.reduce((a,b)=>a+b*b,0)/valid.length):null;const maximum=distances.at(-1);return `<tr><td>${label}</td><td>${valid.length}</td><td class="number">${fmt(total,3)} / ${fmt(mean,3)} / ${fmt(maximum,3)}</td><td class="number">${fmt(rms('radial_km'),3)}</td><td class="number">${fmt(rms('along_km'),3)}</td><td class="number">${fmt(rms('cross_km'),3)}</td></tr>`;
    }).join('');
  }catch(e){$('track-chart-note').textContent=e.message}
}
function renderTrackingChart(){
  const data=trackingDetail?.rows||[],values=data.flatMap(r=>trackCohorts.map(([c])=>r[c]?.separation_km).filter(v=>v!=null));
  $('track-empty').hidden=values.length>0;
  const left=58,right=1040,top=20,bottom=220,high=Math.max(1,...values)*1.08;
  const horizon=Math.max(1,...data.map(r=>r.forecast_age_hours)),x=h=>left+(right-left)*h/horizon,y=v=>bottom-(bottom-top)*v/high;
  let html='';
  for(let n=0;n<=4;n++){const yy=top+(bottom-top)*n/4;html+=`<line x1="${left}" x2="${right}" y1="${yy}" y2="${yy}" stroke="#e4ece7" stroke-dasharray="3 4"/><text x="${left-10}" y="${yy+3}" text-anchor="end" fill="#81938b" font-size="10">${fmt(high*(1-n/4),2)}</text><text x="${left+(right-left)*n/4}" y="${bottom+24}" text-anchor="middle" fill="#81938b" font-size="10">${fmt(horizon*n/4,1)} h</text>`}
  for(const [cohort,,color] of trackCohorts){let path='',last=null,lastElement=null;for(const row of data){const point=row[cohort];if(!point){last=null;continue}const split=last===null||(row.forecast_age_hours-last)*3600>(trackingDetail.issue.policy.step_seconds*1.5)||(cohort==='latest_gp'&&point.element_id!==lastElement);path+=(split?'M':'L')+x(row.forecast_age_hours).toFixed(2)+','+y(point.separation_km).toFixed(2);html+=`<circle cx="${x(row.forecast_age_hours)}" cy="${y(point.separation_km)}" r="2" fill="${color}"><title>${escapeHTML(row.utc+' · '+cohort+' · '+fmt(point.separation_km,4)+' km')}</title></circle>`;last=row.forecast_age_hours;lastElement=point.element_id}html+=`<path d="${path}" fill="none" stroke="${color}" stroke-width="2"/>`}
  $('track-chart').innerHTML=html;
  $('track-legend').innerHTML=trackCohorts.map(([,label,color])=>`<span class="legend-item"><i style="--c:${color}"></i>${label}</span>`).join('');
}

function trackingEpochCSV(detail){
  const keys=['issue_id','model_version','prn','issued_at','utc','forecast_age_hours','model_age_hours','cohort','separation_km','radial_km','along_km','cross_km','gp_age_hours','gp_element_id','gp_snapshot_sha256','reference_record_id','reference_snapshot_sha256','reference_toc_utc','reference_first_received_at','flags'];
  const cell=v=>'"'+String(v??'').replaceAll('"','""')+'"';
  const lines=[keys.map(cell).join(',')];
  for(const row of detail.rows)for(const [cohort] of trackCohorts){const m=row[cohort]||{},ref=row.reference||{};lines.push([detail.issue.issue_id,detail.issue.model_version||legacyTrackingVersion,detail.issue.prn,detail.issue.issued_at,row.utc,row.forecast_age_hours,row.model_age_hours,cohort,m.separation_km,m.radial_km,m.along_km,m.cross_km,m.age_hours,m.element_id,m.snapshot_sha256,ref.record_id,ref.snapshot_sha256,ref.toc_utc,ref.first_received_at,row.flags.join(';')].map(cell).join(','))}
  return lines.join('\n')+'\n';
}
