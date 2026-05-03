#!/usr/bin/env python3
"""
Beckhoff Package Browser
========================
Start: python beckhoff_packages.py
Open:  http://localhost:8765
"""

import json
import os
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import base64
import gzip
import re

PORT = 8765

# ── HTML / CSS / JS frontend ─────────────────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Beckhoff Package Browser</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  :root{
    --bg:#0d1117;--bg-card:#161b22;--bg-hover:#1f2937;--border:#30363d;
    --accent:#00b4d8;--accent2:#0077b6;--text:#e6edf3;--text-muted:#7d8590;
    --text-dim:#484f58;--green:#3fb950;--amber:#d29922;--red:#f85149;
    --font:'Segoe UI',system-ui,sans-serif;--mono:'Consolas','Courier New',monospace;
  }
  body{background:var(--bg);color:var(--text);font-family:var(--font);font-size:14px;min-height:100vh}

  /* header */
  header{background:linear-gradient(135deg,#0a0f1a,#0d1117 60%,#091220);border-bottom:1px solid var(--border);padding:20px 32px;display:flex;align-items:center;gap:20px}
  .logo{display:flex;align-items:center;gap:12px}
  .logo-icon{width:40px;height:40px;background:var(--accent2);border-radius:8px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
  .logo-icon svg{width:22px;height:22px;fill:white}
  .logo-text h1{font-size:18px;font-weight:600;letter-spacing:-.3px}
  .logo-text p{font-size:12px;color:var(--text-muted);margin-top:1px}
  .platform-badge{margin-left:auto;background:#1a2233;border:1px solid var(--accent2);color:var(--accent);font-size:11px;font-family:var(--mono);padding:4px 10px;border-radius:20px}

  /* login */
  #login-section{max-width:480px;margin:60px auto;padding:0 16px}
  .panel{background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:32px}
  .panel h2{font-size:16px;font-weight:600;margin-bottom:6px}
  .panel p.sub{font-size:13px;color:var(--text-muted);margin-bottom:24px;line-height:1.5}
  .field{margin-bottom:16px}
  .field label{display:block;font-size:12px;color:var(--text-muted);margin-bottom:6px;letter-spacing:.3px}
  .field input,.field select{width:100%;background:var(--bg);border:1px solid var(--border);border-radius:6px;color:var(--text);font-family:var(--font);font-size:13px;padding:9px 12px;outline:none;transition:border-color .15s}
  .field input:focus,.field select:focus{border-color:var(--accent)}
  .field select option{background:#1a1f2e}
  .row2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
  .btn-primary{width:100%;padding:10px;margin-top:8px;background:var(--accent2);color:white;border:none;border-radius:6px;font-size:14px;font-family:var(--font);cursor:pointer;font-weight:500;transition:background .15s;display:flex;align-items:center;justify-content:center;gap:8px}
  .btn-primary:hover{background:var(--accent)}
  .btn-primary:disabled{opacity:.5;cursor:not-allowed}
  .divider{display:flex;align-items:center;gap:12px;margin:24px 0;color:var(--text-dim);font-size:12px}
  .divider::before,.divider::after{content:'';flex:1;border-top:1px solid var(--border)}
  .upload-alt{position:relative;border:1.5px dashed var(--border);border-radius:8px;padding:20px;text-align:center;cursor:pointer;transition:border-color .2s,background .2s}
  .upload-alt:hover{border-color:var(--accent);background:rgba(0,180,216,.04)}
  .upload-alt input{position:absolute;inset:0;opacity:0;cursor:pointer;width:100%;height:100%}
  .upload-alt p{font-size:13px;color:var(--text-muted);pointer-events:none}
  .upload-alt strong{color:var(--text)}
  #status-box{margin-top:20px;border-radius:8px;padding:14px 16px;font-size:13px;line-height:1.7;display:none}
  #status-box.info{background:rgba(0,119,182,.12);border:1px solid rgba(0,119,182,.3);color:#58a6ff}
  #status-box.error{background:rgba(248,81,73,.1);border:1px solid rgba(248,81,73,.3);color:var(--red)}
  #status-box.success{background:rgba(63,185,80,.1);border:1px solid rgba(63,185,80,.3);color:var(--green)}
  .spinner{display:inline-block;width:14px;height:14px;border:2px solid rgba(255,255,255,.2);border-top-color:white;border-radius:50%;animation:spin .7s linear infinite;flex-shrink:0}
  @keyframes spin{to{transform:rotate(360deg)}}

  /* toolbar */
  .toolbar{padding:16px 32px;display:flex;gap:12px;align-items:center;background:var(--bg);border-bottom:1px solid var(--border);flex-wrap:wrap}
  .search-wrap{flex:1;min-width:200px;position:relative}
  .search-wrap svg{position:absolute;left:11px;top:50%;transform:translateY(-50%);width:15px;height:15px;fill:var(--text-muted);pointer-events:none}
  .search-wrap input{width:100%;background:var(--bg-card);border:1px solid var(--border);border-radius:6px;color:var(--text);font-family:var(--font);font-size:13px;padding:8px 12px 8px 34px;outline:none;transition:border-color .15s}
  .search-wrap input:focus{border-color:var(--accent)}
  .toolbar select{background:var(--bg-card);border:1px solid var(--border);border-radius:6px;color:var(--text);font-family:var(--font);font-size:13px;padding:8px 12px;outline:none;cursor:pointer;min-width:140px}
  .toolbar select option{background:#1a1f2e}
  .toolbar select:focus{border-color:var(--accent)}
  .btn-logout{background:transparent;border:1px solid var(--border);color:var(--text-muted);border-radius:6px;padding:7px 14px;font-size:12px;font-family:var(--font);cursor:pointer;transition:border-color .15s,color .15s;white-space:nowrap}
  .btn-logout:hover{border-color:var(--red);color:var(--red)}

  /* stats */
  .stats-bar{padding:10px 32px;background:var(--bg-card);border-bottom:1px solid var(--border);display:flex;gap:24px;align-items:center;font-size:12px;flex-wrap:wrap}
  .stat{color:var(--text-muted)}.stat strong{color:var(--text);font-weight:600}
  .stat-sep{color:var(--border)}

  /* table */
  .table-container{padding:0 32px 32px;overflow-x:auto}
  table{width:100%;border-collapse:collapse;table-layout:fixed}
  thead{position:sticky;top:0;z-index:10}
  thead th{background:var(--bg-card);padding:10px 14px;text-align:left;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.8px;color:var(--text-muted);border-bottom:1px solid var(--border);cursor:pointer;user-select:none;white-space:nowrap}
  thead th:hover{color:var(--text)}
  th .sort-arrow{margin-left:5px;opacity:.3;font-size:10px}
  th.sorted .sort-arrow{opacity:1;color:var(--accent)}
  tbody tr{border-bottom:1px solid rgba(48,54,61,.5);transition:background .1s}
  tbody tr:hover{background:var(--bg-hover)}
  td{padding:10px 14px;vertical-align:middle;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .col-pkg{width:28%}.col-ver{width:14%}.col-sec{width:11%}.col-arch{width:8%}.col-size{width:9%}.col-desc{width:30%}
  .pkg-name{font-family:var(--mono);font-size:12.5px;color:var(--accent);font-weight:500}
  .version-badge{display:inline-block;font-family:var(--mono);font-size:11.5px;background:rgba(0,119,182,.12);color:#58a6ff;padding:2px 7px;border-radius:4px;border:1px solid rgba(88,166,255,.2);white-space:nowrap}
  .section-badge{display:inline-block;font-size:11px;padding:2px 7px;border-radius:4px;background:rgba(60,185,80,.1);color:var(--green);border:1px solid rgba(60,185,80,.2)}
  .arch-badge{display:inline-block;font-size:11px;font-family:var(--mono);padding:2px 6px;border-radius:4px;background:rgba(210,153,34,.1);color:var(--amber);border:1px solid rgba(210,153,34,.2)}
  .size-text{color:var(--text-muted);font-size:12px;font-family:var(--mono)}
  .desc-text{color:var(--text-muted);font-size:12.5px}
  .detail-row{display:none}
  .detail-row.open{display:table-row}
  .detail-row td{padding:16px 20px;background:rgba(22,27,34,.7);font-size:13px;white-space:normal}
  .detail-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}
  .detail-field label{display:block;font-size:10px;text-transform:uppercase;letter-spacing:.7px;color:var(--text-dim);margin-bottom:3px}
  .detail-field value{font-size:12.5px;color:var(--text);font-family:var(--mono);word-break:break-all}
  .detail-desc{margin-top:12px;padding-top:12px;border-top:1px solid var(--border);color:var(--text-muted);font-size:13px;line-height:1.6;white-space:pre-wrap;font-family:var(--font)}
  tbody tr.data-row{cursor:pointer}
  .no-results{padding:32px;text-align:center;color:var(--text-muted);font-size:13px}
  @media(max-width:700px){
    header,.toolbar,.stats-bar,.table-container{padding-left:16px;padding-right:16px}
    .col-arch,.col-size{display:none}
  }
</style>
</head>
<body>

<header>
  <div class="logo">
    <div class="logo-icon">
      <svg viewBox="0 0 24 24"><path d="M4 4h16v2H4V4zm0 4h10v2H4V8zm0 4h16v2H4v-2zm0 4h10v2H4v-2z"/></svg>
    </div>
    <div class="logo-text">
      <h1>Beckhoff Package Browser</h1>
      <p>deb.beckhoff.com — via lokale Python proxy</p>
    </div>
  </div>
  <div class="platform-badge" id="platform-label">ARM64</div>
</header>

<!-- LOGIN -->
<div id="login-section">
  <div class="panel">
    <h2>Verbinden met package server</h2>
    <p class="sub">Vul je Beckhoff-accountgegevens in. De Python server haalt het bestand op en geeft het door aan de browser — geen CORS-problemen.</p>
    <div class="field">
      <label>Gebruikersnaam</label>
      <input type="text" id="inp-user" placeholder="gebruikersnaam" autocomplete="username">
    </div>
    <div class="field">
      <label>Wachtwoord</label>
      <input type="password" id="inp-pass" placeholder="••••••••" autocomplete="current-password">
    </div>
    <div class="row2">
      <div class="field">
        <label>Distributie</label>
        <select id="inp-dist">
          <option value="trixie-stable">trixie-stable</option>
          <option value="trixie-testing">trixie-testing</option>
          <option value="bookworm-stable">bookworm-stable</option>
        </select>
      </div>
      <div class="field">
        <label>Architectuur</label>
        <select id="inp-arch">
          <option value="binary-arm64">arm64</option>
          <option value="binary-amd64">amd64</option>
          <option value="binary-all">all</option>
        </select>
      </div>
    </div>
    <button class="btn-primary" id="btn-fetch" onclick="fetchPackages()">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round"><path d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M8 12l4 4 4-4M12 4v12"/></svg>
      Ophalen van server
    </button>
    <div id="status-box"></div>
    <div class="divider">of laad lokaal bestand</div>
    <div class="upload-alt" id="dropzone">
      <input type="file" id="file-input" accept=".txt,.gz,text/*">
      <p><strong>Sleep Packages-bestand</strong> hierop, of klik om te bladeren</p>
    </div>
  </div>
</div>

<!-- MAIN VIEW -->
<div id="main-view" style="display:none">
  <div class="toolbar">
    <div class="search-wrap">
      <svg viewBox="0 0 24 24"><path d="M10 2a8 8 0 105.293 14.293l4.707 4.707 1.414-1.414-4.707-4.707A8 8 0 0010 2zm0 2a6 6 0 110 12A6 6 0 0110 4z"/></svg>
      <input type="text" id="search" placeholder="Zoeken op naam of beschrijving…" oninput="render()">
    </div>
    <select id="filter-section" onchange="render()"><option value="">Alle secties</option></select>
    <select id="filter-arch-tbl" onchange="render()"><option value="">Alle architecturen</option></select>
    <select id="sort-by" onchange="render()">
      <option value="name">Sorteren: Naam</option>
      <option value="version">Sorteren: Versie</option>
      <option value="section">Sorteren: Sectie</option>
      <option value="size">Sorteren: Grootte</option>
    </select>
    <button class="btn-logout" onclick="logout()">↩ Nieuw bestand</button>
  </div>
  <div class="stats-bar" id="stats-bar"></div>
  <div class="table-container">
    <table>
      <thead>
        <tr>
          <th class="col-pkg sorted" onclick="setSort('name')">Pakket <span class="sort-arrow" id="arr-name">▲</span></th>
          <th class="col-ver" onclick="setSort('version')">Versie <span class="sort-arrow" id="arr-version">▲</span></th>
          <th class="col-sec" onclick="setSort('section')">Sectie <span class="sort-arrow" id="arr-section">▲</span></th>
          <th class="col-arch">Arch.</th>
          <th class="col-size" onclick="setSort('size')">Grootte <span class="sort-arrow" id="arr-size">▲</span></th>
          <th class="col-desc">Beschrijving</th>
        </tr>
      </thead>
      <tbody id="tbody"></tbody>
    </table>
    <div id="no-results" class="no-results" style="display:none">Geen resultaten gevonden.</div>
  </div>
</div>

<script>
let packages=[], sortField='name', sortAsc=true, openRow=null;

// File drag/drop
const dropzone=document.getElementById('dropzone');
const fileInput=document.getElementById('file-input');
dropzone.addEventListener('dragover',e=>{e.preventDefault();dropzone.style.borderColor='var(--accent)'});
dropzone.addEventListener('dragleave',()=>dropzone.style.borderColor='');
dropzone.addEventListener('drop',e=>{e.preventDefault();dropzone.style.borderColor='';if(e.dataTransfer.files[0])readFile(e.dataTransfer.files[0])});
fileInput.addEventListener('change',e=>{if(e.target.files[0])readFile(e.target.files[0])});

function readFile(file){
  const r=new FileReader();
  r.onload=e=>parsePackages(e.target.result);
  r.readAsText(file);
}

// Fetch via Python proxy
async function fetchPackages(){
  const user=document.getElementById('inp-user').value.trim();
  const pass=document.getElementById('inp-pass').value;
  const dist=document.getElementById('inp-dist').value;
  const arch=document.getElementById('inp-arch').value;
  if(!user||!pass){showStatus('Vul gebruikersnaam en wachtwoord in.','error');return}

  const btn=document.getElementById('btn-fetch');
  btn.disabled=true;
  btn.innerHTML='<span class="spinner"></span> Ophalen…';
  showStatus('Verbinden met deb.beckhoff.com…','info');

  try{
    const resp=await fetch(`/fetch?user=${encodeURIComponent(user)}&pass=${encodeURIComponent(pass)}&dist=${encodeURIComponent(dist)}&arch=${encodeURIComponent(arch)}`);
    const data=await resp.json();

    if(!resp.ok||data.error){
      showStatus('❌ '+data.error,'error');
      return;
    }

    const archLabel=arch.replace('binary-','').toUpperCase();
    document.getElementById('platform-label').textContent=archLabel+' · '+dist;
    showStatus('✓ '+data.packages_count+' pakketten opgehaald!','success');
    setTimeout(()=>parsePackages(data.content),400);

  }catch(err){
    showStatus('❌ Kon de Python server niet bereiken: '+err.message,'error');
  }finally{
    btn.disabled=false;
    btn.innerHTML='<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round"><path d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M8 12l4 4 4-4M12 4v12"/></svg> Ophalen van server';
  }
}

function showStatus(html,type){
  const b=document.getElementById('status-box');
  b.innerHTML=html; b.className=type; b.style.display='block';
}

function parsePackages(text){
  packages=[];
  for(const block of text.split(/\n\n+/)){
    if(!block.trim())continue;
    const pkg={};
    let desc='',inDesc=false;
    for(const line of block.split('\n')){
      if(inDesc){if(line.startsWith(' ')){desc+=line.slice(1)+'\n';continue}else inDesc=false}
      const c=line.indexOf(': ');
      if(c===-1)continue;
      const key=line.slice(0,c).toLowerCase().trim();
      const val=line.slice(c+2).trim();
      if(key==='description'){desc=val+'\n';inDesc=true;pkg.descTitle=val}
      else pkg[key]=val;
    }
    pkg.descFull=desc.trim();
    if(pkg.package)packages.push(pkg);
  }

  const sections=[...new Set(packages.map(p=>p.section).filter(Boolean))].sort();
  const archs=[...new Set(packages.map(p=>p.architecture).filter(Boolean))].sort();

  const ss=document.getElementById('filter-section');
  ss.innerHTML='<option value="">Alle secties</option>';
  sections.forEach(s=>{const o=document.createElement('option');o.value=s;o.textContent=s;ss.appendChild(o)});

  const as=document.getElementById('filter-arch-tbl');
  as.innerHTML='<option value="">Alle architecturen</option>';
  archs.forEach(a=>{const o=document.createElement('option');o.value=a;o.textContent=a;as.appendChild(o)});

  document.getElementById('login-section').style.display='none';
  document.getElementById('main-view').style.display='block';
  render();
}

function logout(){
  packages=[];openRow=null;
  document.getElementById('main-view').style.display='none';
  document.getElementById('login-section').style.display='block';
  document.getElementById('status-box').style.display='none';
  document.getElementById('inp-pass').value='';
  document.getElementById('search').value='';
}

function fmtSize(s){
  if(!s)return'—';const b=parseInt(s);if(isNaN(b))return s;
  if(b>1048576)return(b/1048576).toFixed(1)+' MB';
  if(b>1024)return Math.round(b/1024)+' KB';
  return b+' B';
}

function setSort(field){
  sortAsc=sortField===field?!sortAsc:true;sortField=field;
  ['name','version','section','size'].forEach(f=>{
    const el=document.getElementById('arr-'+f);if(!el)return;
    el.textContent=sortField===f?(sortAsc?'▲':'▼'):'▲';
    el.style.opacity=sortField===f?'1':'0.3';
  });
  document.querySelectorAll('thead th').forEach(th=>th.classList.remove('sorted'));
  const idx={name:0,version:1,section:2,size:4};
  if(idx[field]!==undefined)document.querySelectorAll('thead th')[idx[field]].classList.add('sorted');
  render();
}

function render(){
  const q=document.getElementById('search').value.toLowerCase();
  const sec=document.getElementById('filter-section').value;
  const arch=document.getElementById('filter-arch-tbl').value;

  let filtered=packages.filter(p=>{
    if(sec&&p.section!==sec)return false;
    if(arch&&p.architecture!==arch)return false;
    if(q)return(p.package||'').toLowerCase().includes(q)||(p.descFull||'').toLowerCase().includes(q)||(p.version||'').toLowerCase().includes(q);
    return true;
  });

  filtered.sort((a,b)=>{
    let va,vb;
    if(sortField==='size'){va=parseInt(a.size)||0;vb=parseInt(b.size)||0}
    else{va=(a[sortField==='name'?'package':sortField]||'').toLowerCase();vb=(b[sortField==='name'?'package':sortField]||'').toLowerCase()}
    return va<vb?(sortAsc?-1:1):va>vb?(sortAsc?1:-1):0;
  });

  const tbody=document.getElementById('tbody');
  tbody.innerHTML='';
  document.getElementById('no-results').style.display=filtered.length===0?'block':'none';

  document.getElementById('stats-bar').innerHTML=
    `<span class="stat"><strong>${filtered.length}</strong> van <strong>${packages.length}</strong> pakketten</span>
     <span class="stat-sep">·</span>
     <span class="stat"><strong>${new Set(filtered.map(p=>p.section).filter(Boolean)).size}</strong> secties</span>`;

  filtered.forEach(p=>{
    const tr=document.createElement('tr');
    tr.className='data-row';
    tr.innerHTML=`
      <td class="col-pkg"><span class="pkg-name">${esc(p.package)}</span></td>
      <td class="col-ver"><span class="version-badge">${esc(p.version||'—')}</span></td>
      <td class="col-sec">${p.section?`<span class="section-badge">${esc(p.section)}</span>`:'—'}</td>
      <td class="col-arch">${p.architecture?`<span class="arch-badge">${esc(p.architecture)}</span>`:'—'}</td>
      <td class="col-size"><span class="size-text">${fmtSize(p.size)}</span></td>
      <td class="col-desc"><span class="desc-text" title="${esc(p.descFull)}">${esc(p.descTitle||'')}</span></td>`;

    const det=document.createElement('tr');
    det.className='detail-row';
    det.innerHTML=`<td colspan="6">
      <div class="detail-grid">
        ${df('Package',p.package)}${df('Version',p.version)}${df('Architecture',p.architecture)}
        ${df('Section',p.section)}${df('Installed-Size',p['installed-size']?p['installed-size']+' KB':null)}
        ${df('Size',fmtSize(p.size))}${df('Depends',p.depends)}${df('Maintainer',p.maintainer)}
        ${df('Filename',p.filename)}
      </div>
      ${p.descFull?`<div class="detail-desc">${esc(p.descFull)}</div>`:''}
    </td>`;

    tr.addEventListener('click',()=>{
      const isOpen=det.classList.contains('open');
      if(openRow&&openRow!==det)openRow.classList.remove('open');
      det.classList.toggle('open',!isOpen);
      openRow=!isOpen?det:null;
    });

    tbody.appendChild(tr);
    tbody.appendChild(det);
  });
}

function df(label,val){
  if(!val)return'';
  return`<div class="detail-field"><label>${esc(label)}</label><value>${esc(val)}</value></div>`;
}

function esc(s){
  if(!s)return'';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

document.getElementById('inp-pass').addEventListener('keydown',e=>{if(e.key==='Enter')fetchPackages()});
</script>
</body>
</html>
"""


# ── HTTP handler ──────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        # Quiet logging — only print errors
        if args and str(args[1]) not in ('200', '304'):
            print(f"  {args[0]}  {args[1]}", flush=True)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == '/':
            self._send_html(HTML.encode())

        elif parsed.path == '/fetch':
            self._handle_fetch(parsed.query)

        else:
            self._send_json({'error': 'Not found'}, 404)

    # ── proxy fetch ──────────────────────────────────────────────────────────

    def _handle_fetch(self, query_string):
        params = parse_qs(query_string)
        user = params.get('user', [''])[0]
        pw   = params.get('pass', [''])[0]
        dist = params.get('dist', ['trixie-stable'])[0]
        arch = params.get('arch', ['binary-arm64'])[0]

        # Basic input validation
        if not user or not pw:
            self._send_json({'error': 'Gebruikersnaam en wachtwoord zijn verplicht.'}, 400)
            return

        # Whitelist allowed values to prevent path traversal
        allowed_dists = {'trixie-stable', 'trixie-testing', 'bookworm-stable'}
        allowed_archs = {'binary-arm64', 'binary-amd64', 'binary-all'}
        if dist not in allowed_dists or arch not in allowed_archs:
            self._send_json({'error': 'Ongeldige distributie of architectuur.'}, 400)
            return

        url = f'https://deb.beckhoff.com/debian/dists/{dist}/main/{arch}/Packages'
        credentials = base64.b64encode(f'{user}:{pw}'.encode()).decode()

        print(f"\n  → Ophalen: {url}", flush=True)

        try:
            req = Request(url, headers={
                'Authorization': f'Basic {credentials}',
                'User-Agent': 'BeckhoffPackageBrowser/1.0',
                'Accept-Encoding': 'gzip',
            })
            with urlopen(req, timeout=30) as resp:
                raw = resp.read()
                # Decompress if gzip
                if resp.headers.get('Content-Encoding') == 'gzip' or raw[:2] == b'\x1f\x8b':
                    raw = gzip.decompress(raw)
                content = raw.decode('utf-8', errors='replace')

            if 'Package:' not in content:
                self._send_json({'error': 'Onverwacht antwoord van de server — geen geldig Packages-bestand.'}, 502)
                return

            # Count packages
            count = content.count('\nPackage:') + (1 if content.startswith('Package:') else 0)
            print(f"  ✓ {count} pakketten ontvangen", flush=True)
            self._send_json({'content': content, 'packages_count': count})

        except HTTPError as e:
            if e.code == 401:
                self._send_json({'error': 'Authenticatie mislukt (401). Controleer gebruikersnaam en wachtwoord.'}, 401)
            elif e.code == 403:
                self._send_json({'error': f'Toegang geweigerd (403). Je account heeft mogelijk geen toegang tot {dist}/{arch}.'}, 403)
            elif e.code == 404:
                self._send_json({'error': f'Bestand niet gevonden (404). Controleer distributie en architectuur: {dist}/{arch}.'}, 404)
            else:
                self._send_json({'error': f'HTTP fout {e.code}: {e.reason}'}, 502)

        except URLError as e:
            self._send_json({'error': f'Netwerkfout: {e.reason}. Controleer je internetverbinding.'}, 502)

        except TimeoutError:
            self._send_json({'error': 'Timeout — de server reageert niet. Probeer opnieuw.'}, 504)

        except Exception as e:
            self._send_json({'error': f'Onverwachte fout: {e}'}, 500)

    # ── helpers ──────────────────────────────────────────────────────────────

    def _send_html(self, data: bytes):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(data))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, obj: dict, status: int = 200):
        data = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(data))
        self.end_headers()
        self.wfile.write(data)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    server = HTTPServer(('127.0.0.1', PORT), Handler)
    url = f'http://localhost:{PORT}'

    print(f"""
  ╔══════════════════════════════════════════════╗
  ║     Beckhoff Package Browser                 ║
  ╠══════════════════════════════════════════════╣
  ║  Open in browser:  {url:<26}║
  ║  Stoppen:          Ctrl+C                    ║
  ╚══════════════════════════════════════════════╝
""", flush=True)

    # Open browser automatically after a short delay
    def open_browser():
        import time; time.sleep(0.5)
        webbrowser.open(url)

    threading.Thread(target=open_browser, daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n  Server gestopt.', flush=True)
        server.server_close()


if __name__ == '__main__':
    main()
