let fittedRows=[],fitArtifacts={},fitSelection='all';
async function fitArtifact(name){
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),15000);
  try{
    const response=await fetch(feedBase+name,{cache:'no-store',signal:controller.signal});
    if(!response.ok)throw Error('Fitting artifact unavailable');
    const bytes=await response.arrayBuffer();
    if(!fitArtifacts[name])throw Error('Artifact checksum unavailable for this run');
    const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');
    if(hash!==fitArtifacts[name])throw Error('Fitting artifact does not match this run; refresh after feed update');
    return new TextDecoder().decode(bytes);
  }finally{clearTimeout(timer)}
}
function renderGenerator(){
  const generator=run?.generator;
  $('generator').hidden=!generator?.enabled;
  if(!generator?.enabled)return;
  const cfg=generator.settings;
  $('fit-description').textContent=`${cfg.train_hours} h fitting → ${24-cfg.train_hours} h later validation · ${cfg.sample_seconds} s samples · ${generator.accepted_count} accepted / ${generator.satellites.length} attempted`;
  $('fit-window').textContent=`FIT: ${generator.train_start_utc} to ${generator.train_end_exclusive_utc} (exclusive). HOLDOUT: ${generator.validation_start_utc} to ${generator.validation_end_exclusive_utc} (exclusive).`;
  $('fit-rows').innerHTML=generator.satellites.map(s=>`<tr data-fit-prn="${escapeHTML(s.prn)}" class="clickable" tabindex="0" aria-label="Inspect fitted model ${escapeHTML(s.prn)}"><td><strong>${escapeHTML(s.prn)}</strong><small class="fit-subname">${escapeHTML(s.name)}</small></td><td><span class="orbit-badge">${escapeHTML(s.orbit_class)}</span></td><td class="number">${fmt(s.fit?.rms_km,3)}</td><td class="number">${fmt(s.holdout?.rms_km,3)}</td><td class="number">${fmt(s.holdout?.max_km,3)}</td><td><span class="status ${s.status==='Accepted'?'close':'review'}">${escapeHTML(s.status)}</span></td></tr>`).join('');
  $('fit-satellite').innerHTML='<option value="all">All fitted models</option>'+generator.satellites.map(s=>`<option value="${escapeHTML(s.prn)}">${escapeHTML(s.prn)} · ${escapeHTML(s.name)}</option>`).join('');
  $('fit-download').disabled=generator.accepted_count===0||!fitArtifacts['generated.omm.json'];
  $('fit-diagnostics').onclick=()=>showDialog('Broadcast-derived SGP4 fitting',generator);
  $('fit-download').onclick=async()=>{try{download(`NAVIC-BROADCAST-FIT-${run.run_id}.omm.json`,await fitArtifact('generated.omm.json'))}catch(e){toast(e.message)}};
  $('fit-satellite').onchange=e=>{fitSelection=e.target.value;renderFitChart()};
  document.querySelectorAll('[data-fit-prn]').forEach(tr=>{
    const inspect=()=>{const satellite=generator.satellites.find(s=>s.prn===tr.dataset.fitPrn);fitSelection=satellite.prn;$('fit-satellite').value=fitSelection;renderFitChart();showDialog(`${satellite.prn} fit and held-out validation`,satellite)};
    tr.onclick=inspect;tr.onkeydown=e=>{if(e.key==='Enter')inspect()};
  });
  const current=run.run_id;fittedRows=[];fitSelection='all';renderFitChart();
  $('fit-chart-note').textContent='Loading checksum-verified fit and validation residuals…';
  fitArtifact('fitted_epochs.json').then(text=>{if(run.run_id!==current)return;fittedRows=JSON.parse(text);renderFitChart();$('fit-chart-note').textContent='Solid: fitting samples · dashed: later held-out samples · model parameters frozen at split';}).catch(e=>{if(run.run_id===current)$('fit-chart-note').textContent=e.message});
}
function renderFitChart(){
  if(!run?.generator?.enabled)return;
  const g=run.generator,left=55,right=1040,top=16,bottom=190,span=right-left;
  const active=g.satellites.filter(s=>fitSelection==='all'||s.prn===fitSelection);
  const values=fittedRows.filter(r=>r.separation_km!=null&&active.some(s=>s.prn===r.prn));
  const high=Math.max(1,...values.map(r=>r.separation_km))*1.08;
  const begin=Date.parse(g.train_start_utc),end=Date.parse(g.validation_end_exclusive_utc);
  const x=t=>left+(Date.parse(t)-begin)/(end-begin)*span,y=v=>bottom-v/high*(bottom-top);
  const split=x(g.validation_start_utc);
  let html=`<rect x="${split}" y="${top}" width="${right-split}" height="${bottom-top}" fill="#fff8ea"/><line x1="${split}" x2="${split}" y1="${top}" y2="${bottom}" stroke="#c6a66d" stroke-dasharray="4 4"/><text x="${split+7}" y="${top+12}" fill="#ad8f56" font-size="9">HELD-OUT VALIDATION</text>`;
  for(let n=0;n<5;n++){const yy=top+(bottom-top)*n/4;html+=`<line x1="${left}" x2="${right}" y1="${yy}" y2="${yy}" stroke="#e4ece7" stroke-dasharray="3 4"/><text x="${left-10}" y="${yy+3}" text-anchor="end" fill="#91a497" font-size="9">${fmt(high*(1-n/4),1)}</text>`}
  for(let h=0;h<=24;h+=3)html+=`<text x="${left+span*h/24}" y="${bottom+24}" text-anchor="middle" fill="#91a497" font-size="9">${String(h).padStart(2,'0')}:00</text>`;
  active.forEach(s=>{const index=g.satellites.indexOf(s),data=fittedRows.filter(r=>r.prn===s.prn);for(const partition of ['fit','holdout']){let path='',last=null;for(const row of data){if(row.partition!==partition||row.separation_km==null){last=null;continue}const time=Date.parse(row.utc);path+=(last===null||time-last>g.settings.sample_seconds*1500?'M':'L')+x(row.utc).toFixed(2)+','+y(row.separation_km).toFixed(2);last=time}html+=`<path d="${path}" fill="none" stroke="${colors[index%colors.length]}" stroke-width="1.8" ${partition==='holdout'?'stroke-dasharray="5 3"':''}/>`}});
  $('fit-chart').innerHTML=html;$('fit-chart').setAttribute('aria-label',`Fitted SGP4 minus broadcast separation in km; ${g.settings.train_hours} hour fitting and later held-out validation`);
  $('fit-legend').innerHTML=active.map(s=>`<span class="legend-item"><i style="--c:${colors[g.satellites.indexOf(s)%colors.length]}"></i>${escapeHTML(s.prn)}</span>`).join('');
}
