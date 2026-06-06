#!/usr/bin/env python3
"""
Weather App — Pure Python stdlib
Generates a self-contained HTML file and opens it in your browser.
All API calls happen client-side (browser), so no external dependencies needed.
Uses: Open-Meteo (weather, free, no key) + Open-Meteo Geocoding API
"""

import http.server
import threading
import webbrowser
import os

PORT = 8766

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Weather App</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #080d18;
  --surface: #0f1624;
  --card: #141e2e;
  --card2: #111928;
  --border: rgba(255,255,255,0.07);
  --border2: rgba(255,255,255,0.12);
  --text: #dde4f0;
  --muted: #6b7a96;
  --accent: #4a93f0;
  --teal: #3dd6a3;
  --warn: #f0a832;
  --danger: #f06060;
  --purple: #9b7af5;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  font-family: 'DM Sans', sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  padding: 2.5rem 1rem 3rem;
  background-image: radial-gradient(ellipse at 20% 0%, rgba(30,60,120,0.3) 0%, transparent 60%),
                    radial-gradient(ellipse at 80% 0%, rgba(20,40,100,0.2) 0%, transparent 60%);
}
.app { max-width: 900px; margin: 0 auto; }

.header { text-align: center; margin-bottom: 2.5rem; }
.header h1 {
  font-family: 'DM Serif Display', serif;
  font-size: 2.8rem;
  font-weight: 400;
  letter-spacing: -1px;
  background: linear-gradient(135deg, #e0eaff 0%, #a0c4ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 4px;
}
.header p { color: var(--muted); font-size: 0.88rem; letter-spacing: 0.03em; }

.search-wrap {
  display: flex;
  gap: 8px;
  margin-bottom: 2.5rem;
  background: var(--surface);
  border: 1px solid var(--border2);
  border-radius: 16px;
  padding: 6px 6px 6px 16px;
  transition: border-color 0.2s;
}
.search-wrap:focus-within { border-color: rgba(74,147,240,0.4); }
.search-wrap input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  color: var(--text);
  font-family: 'DM Sans', sans-serif;
  font-size: 0.95rem;
}
.search-wrap input::placeholder { color: var(--muted); }
.btn {
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.88rem;
  font-weight: 500;
  padding: 0.6rem 1.2rem;
  transition: opacity 0.15s, transform 0.1s;
}
.btn:hover { opacity: 0.85; }
.btn:active { transform: scale(0.97); }
.btn-primary { background: var(--accent); color: #fff; }
.btn-ghost {
  background: rgba(255,255,255,0.06);
  color: var(--muted);
  padding: 0.6rem 0.8rem;
  font-size: 1rem;
}
.btn-ghost:hover { color: var(--text); background: rgba(255,255,255,0.1); }

/* States */
.state { text-align: center; padding: 4rem 1rem; display: none; }
.state.on { display: block; }
.spinner {
  width: 36px; height: 36px; margin: 0 auto 1.2rem;
  border: 2.5px solid var(--border2);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.65s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.err-ico { font-size: 2.5rem; margin-bottom: .75rem; }
.err-txt { color: var(--muted); font-size: 0.92rem; }

/* Weather */
#weather { display: none; animation: fadeIn 0.4s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }

/* Hero */
.hero {
  border-radius: 22px;
  background: linear-gradient(145deg, #132040 0%, #0b1528 60%, #0d1a33 100%);
  border: 1px solid rgba(74,147,240,0.18);
  padding: 2rem 2.2rem 1.8rem;
  margin-bottom: 1.2rem;
  position: relative;
  overflow: hidden;
}
.hero::after {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 75% 30%, rgba(74,147,240,0.08) 0%, transparent 60%);
  pointer-events: none;
}
.hero-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.4rem; }
.city-name { font-family: 'DM Serif Display', serif; font-size: 2.2rem; line-height: 1.1; }
.city-sub { color: var(--muted); font-size: 0.82rem; margin-top: 4px; }
.hero-icon { font-size: 4rem; line-height: 1; filter: drop-shadow(0 4px 12px rgba(74,147,240,0.3)); }
.hero-temp-row { display: flex; align-items: flex-end; gap: 12px; margin-bottom: 6px; }
.hero-temp { font-family: 'DM Serif Display', serif; font-size: 5.5rem; line-height: 1; color: #fff; }
.hero-temp-unit { font-size: 1.8rem; margin-bottom: 0.6rem; color: rgba(255,255,255,0.5); }
.hero-desc { color: #7aadde; font-size: 1.05rem; margin-bottom: 1.6rem; }
.hero-meta {
  display: flex; gap: 1.5rem; flex-wrap: wrap;
  border-top: 1px solid rgba(255,255,255,0.06);
  padding-top: 1.2rem;
}
.meta-item label { display: block; font-size: 0.7rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 3px; }
.meta-item span { font-size: 0.95rem; font-weight: 500; }

/* Unit toggle */
.unit-row { display: flex; justify-content: center; gap: 6px; margin-bottom: 1.2rem; }
.unit-btn { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 4px 14px; color: var(--muted); font-size: 0.85rem; cursor: pointer; transition: all 0.15s; font-family: 'DM Sans',sans-serif; }
.unit-btn.on { background: var(--accent); color: #fff; border-color: var(--accent); }

/* Layout grid */
.row { display: grid; gap: 1.2rem; margin-bottom: 1.2rem; }
.row-3 { grid-template-columns: 1fr 1fr 1fr; }
.row-2 { grid-template-columns: 2fr 1.2fr; }
@media(max-width:680px) { .row-3,.row-2 { grid-template-columns: 1fr; } }

/* Cards */
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 1.3rem 1.4rem;
}
.card-label {
  font-size: 0.68rem; font-weight: 500;
  text-transform: uppercase; letter-spacing: 0.09em;
  color: var(--muted); margin-bottom: 1rem;
}

/* Hourly */
.hourly-outer { overflow-x: auto; padding-bottom: 4px; }
.hourly { display: flex; gap: 8px; min-width: max-content; }
.h-item {
  text-align: center;
  background: var(--card2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 0.7rem 0.55rem;
  min-width: 58px;
  cursor: default;
  transition: border-color 0.15s, background 0.15s;
}
.h-item:hover { border-color: rgba(74,147,240,0.35); background: #18243a; }
.h-item.now { border-color: rgba(74,147,240,0.5); background: rgba(74,147,240,0.1); }
.h-time { font-size: 0.68rem; color: var(--muted); margin-bottom: 5px; }
.h-icon { font-size: 1.25rem; margin-bottom: 5px; }
.h-temp { font-size: 0.88rem; font-weight: 500; }
.h-rain { font-size: 0.65rem; color: #5ba3f5; margin-top: 3px; }

/* Daily */
.d-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.55rem 0.65rem; border-radius: 10px; cursor: default;
  transition: background 0.12s;
}
.d-item:hover { background: var(--surface); }
.d-item.today { background: rgba(74,147,240,0.07); }
.d-name { font-size: 0.88rem; min-width: 52px; }
.d-icon { font-size: 1.15rem; margin: 0 8px; }
.d-bar-bg { flex: 1; height: 5px; background: var(--border); border-radius: 3px; overflow: hidden; }
.d-bar { height: 100%; border-radius: 3px; background: linear-gradient(90deg, var(--accent), var(--teal)); }
.d-temps { display: flex; gap: 8px; font-size: 0.85rem; min-width: 68px; justify-content: flex-end; }
.d-lo { color: var(--muted); }

/* UV ring */
.uv-wrap { display: flex; align-items: center; gap: 1.2rem; }
.uv-ring { position: relative; flex-shrink: 0; }
.uv-ring svg { display: block; transform: rotate(-90deg); }
.uv-center { position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); text-align: center; }
.uv-center .uv-val { font-family: 'DM Serif Display',serif; font-size: 1.9rem; line-height: 1; }
.uv-center .uv-lbl { font-size: 0.68rem; color: var(--muted); }
.uv-info p { font-size: 0.82rem; color: var(--muted); line-height: 1.5; }

/* Stat tiles */
.stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.stat-tile {
  background: var(--card2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 0.9rem 1rem;
}
.stat-tile .s-label { font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.07em; color: var(--muted); margin-bottom: 4px; }
.stat-tile .s-val { font-size: 1.3rem; font-weight: 500; }
.stat-tile .s-sub { font-size: 0.72rem; color: var(--muted); margin-top: 2px; }

/* Sun arc */
.sun-card svg { display: block; margin: 0 auto 0.5rem; overflow: visible; }
.sun-row { display: flex; justify-content: space-between; font-size: 0.85rem; }
.sun-rise { color: var(--warn); }
.sun-set { color: #f09090; }

/* Aqi / alerts banner */
.alert-bar {
  background: rgba(240,168,50,0.1);
  border: 1px solid rgba(240,168,50,0.25);
  border-radius: 10px;
  padding: 0.7rem 1rem;
  font-size: 0.85rem;
  color: var(--warn);
  margin-bottom: 1.2rem;
  display: none;
}

::-webkit-scrollbar { height: 4px; width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
</style>
</head>
<body>
<div class="app">

<div class="header">
  <h1>&#9729; Weather</h1>
  <p>Live forecasts powered by Open-Meteo &mdash; no API key required</p>
</div>

<div class="search-wrap">
  <input id="city-input" type="text" placeholder="Search city &mdash; London, Tokyo, Mumbai, New York&hellip;" autocomplete="off"/>
  <button class="btn btn-ghost" id="loc-btn" title="Use my location">&#128205;</button>
  <button class="btn btn-primary" id="srch-btn">Search</button>
</div>

<div id="alert-bar" class="alert-bar"></div>

<div id="idle" class="state on"><div style="font-size:3.5rem;margin-bottom:.8rem">&#127758;</div><p style="color:var(--muted);font-size:.92rem">Search a city or tap &#128205; for your location</p></div>
<div id="loading" class="state"><div class="spinner"></div><p style="color:var(--muted);font-size:.9rem">Fetching forecast&hellip;</p></div>
<div id="error" class="state"><div class="err-ico">&#9888;&#65039;</div><p class="err-txt" id="err-txt">Something went wrong.</p></div>

<div id="weather">

  <div class="hero">
    <div class="hero-top">
      <div>
        <div class="city-name" id="w-city">-</div>
        <div class="city-sub" id="w-time">-</div>
      </div>
      <div class="hero-icon" id="w-icon">-</div>
    </div>
    <div class="hero-temp-row">
      <div class="hero-temp" id="w-temp">-</div>
      <div class="hero-temp-unit" id="w-tunit">&deg;C</div>
    </div>
    <div class="hero-desc" id="w-desc">-</div>
    <div class="hero-meta">
      <div class="meta-item"><label>Feels like</label><span id="w-fl">-</span></div>
      <div class="meta-item"><label>Humidity</label><span id="w-hum">-</span></div>
      <div class="meta-item"><label>Wind</label><span id="w-wind">-</span></div>
      <div class="meta-item"><label>Visibility</label><span id="w-vis">-</span></div>
      <div class="meta-item"><label>Precip</label><span id="w-precip">-</span></div>
    </div>
  </div>

  <div class="unit-row">
    <button class="unit-btn on" id="btn-c" onclick="setUnit('C')">&deg;C</button>
    <button class="unit-btn" id="btn-f" onclick="setUnit('F')">&deg;F</button>
  </div>

  <!-- Hourly -->
  <div class="card" style="margin-bottom:1.2rem">
    <div class="card-label">24-hour forecast</div>
    <div class="hourly-outer"><div class="hourly" id="w-hourly"></div></div>
  </div>

  <!-- Daily + UV + Stats -->
  <div class="row row-2" style="margin-bottom:1.2rem">
    <!-- Daily -->
    <div class="card">
      <div class="card-label">7-day forecast</div>
      <div id="w-daily"></div>
    </div>
    <!-- Right col -->
    <div style="display:flex;flex-direction:column;gap:1.2rem">
      <!-- UV -->
      <div class="card">
        <div class="card-label">UV Index</div>
        <div class="uv-wrap">
          <div class="uv-ring">
            <svg width="88" height="88" viewBox="0 0 88 88">
              <circle cx="44" cy="44" r="34" fill="none" stroke="rgba(255,255,255,0.07)" stroke-width="7"/>
              <circle id="uv-arc" cx="44" cy="44" r="34" fill="none" stroke="#f0a832" stroke-width="7" stroke-linecap="round" stroke-dasharray="213.6" stroke-dashoffset="213.6"/>
            </svg>
            <div class="uv-center"><div class="uv-val" id="w-uv">0</div><div class="uv-lbl" id="w-uv-lbl">Low</div></div>
          </div>
          <div class="uv-info"><p id="uv-advice">UV is low. No protection needed for most people.</p></div>
        </div>
      </div>
      <!-- Stats -->
      <div class="card">
        <div class="card-label">Atmosphere</div>
        <div class="stat-grid">
          <div class="stat-tile"><div class="s-label">Pressure</div><div class="s-val" id="w-pres">-</div><div class="s-sub">hPa</div></div>
          <div class="stat-tile"><div class="s-label">Cloud</div><div class="s-val" id="w-cloud">-</div><div class="s-sub">cover</div></div>
          <div class="stat-tile"><div class="s-label">Dew point</div><div class="s-val" id="w-dew">-</div></div>
          <div class="stat-tile"><div class="s-label">Wind dir</div><div class="s-val" id="w-wdir">-</div></div>
        </div>
      </div>
    </div>
  </div>

  <!-- Sun schedule -->
  <div class="card sun-card" style="margin-bottom:2rem">
    <div class="card-label">Sun schedule</div>
    <svg width="100%" height="80" viewBox="0 0 340 80" preserveAspectRatio="xMidYMid meet">
      <path d="M 16 68 Q 170 -10 324 68" fill="none" stroke="rgba(255,255,255,0.07)" stroke-width="1.5" stroke-dasharray="5 4"/>
      <circle id="sun-dot" cx="170" cy="26" r="9" fill="#f0a832" opacity="0.95"/>
      <text id="t-rise" x="10" y="78" fill="#f0a832" font-size="11" font-family="DM Sans,sans-serif">--:--</text>
      <text id="t-set" x="270" y="78" fill="#f09090" font-size="11" font-family="DM Sans,sans-serif">--:--</text>
      <text id="t-daylen" x="148" y="14" fill="rgba(255,255,255,0.3)" font-size="10" font-family="DM Sans,sans-serif">-- daylight</text>
    </svg>
  </div>

</div>
</div>

<script>
const WMO={0:"Clear sky",1:"Mainly clear",2:"Partly cloudy",3:"Overcast",45:"Foggy",48:"Rime fog",51:"Light drizzle",53:"Moderate drizzle",55:"Dense drizzle",61:"Slight rain",63:"Moderate rain",65:"Heavy rain",71:"Slight snow",73:"Moderate snow",75:"Heavy snow",77:"Snow grains",80:"Slight showers",81:"Moderate showers",82:"Violent showers",85:"Slight snow showers",86:"Heavy snow showers",95:"Thunderstorm",96:"Thunderstorm w/hail",99:"Thunderstorm w/heavy hail"};
const EMO={0:"&#9728;&#65039;",1:"&#127780;&#65039;",2:"&#9925;",3:"&#9729;&#65039;",45:"&#127787;&#65039;",48:"&#127787;&#65039;",51:"&#127746;",53:"&#127746;",55:"&#127747;",61:"&#127327;",63:"&#127327;",65:"&#127327;",71:"&#127784;&#65039;",73:"&#127784;&#65039;",75:"&#10052;&#65039;",77:"&#127784;&#65039;",80:"&#127746;",81:"&#127746;",82:"&#9928;&#65039;",85:"&#127784;&#65039;",86:"&#10052;&#65039;",95:"&#9928;&#65039;",96:"&#9928;&#65039;",99:"&#9928;&#65039;"};
const DAYS=["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
let raw=null,unit='C';

function q(id){return document.getElementById(id);}
function toF(c){return Math.round(c*9/5+32);}
function disp(c){return unit==='C'?Math.round(c):toF(c);}
function unitStr(){return unit==='C'?'\u00b0C':'\u00b0F';}

function show(panel){
  ['idle','loading','error'].forEach(s=>{q(s).classList.remove('on');});
  q('weather').style.display='none';
  if(panel==='weather'){q('weather').style.display='block';}
  else{q(panel).classList.add('on');}
}

function setUnit(u){
  unit=u;
  q('btn-c').classList.toggle('on',u==='C');
  q('btn-f').classList.toggle('on',u==='F');
  if(raw)render(raw);
}

function wdir(d){return["N","NE","E","SE","S","SW","W","NW"][Math.round(d/45)%8];}
function uvLabel(v){return v<=2?"Low":v<=5?"Moderate":v<=7?"High":v<=10?"Very high":"Extreme";}
function uvAdvice(v){
  if(v<=2)return "UV is low. No sun protection needed for most.";
  if(v<=5)return "Moderate UV. Wear SPF 30+ if outdoors for long.";
  if(v<=7)return "High UV. Cover up, wear SPF 50+, seek shade at midday.";
  if(v<=10)return "Very high UV. Unprotected skin burns quickly.";
  return "Extreme UV. Avoid sun exposure 10am\u20134pm.";
}

function render(d){
  raw=d;
  const c=d.current,h=d.hourly,dl=d.daily;
  const code=c.weather_code;
  q('w-city').textContent=d.city;
  q('w-time').textContent=new Date().toLocaleString([],{weekday:'long',hour:'2-digit',minute:'2-digit'});
  q('w-icon').innerHTML=EMO[code]||'\uD83C\uDF21';
  q('w-temp').textContent=disp(c.temperature_2m);
  q('w-tunit').textContent=unitStr();
  q('w-desc').textContent=WMO[code]||'Unknown';
  q('w-fl').textContent=disp(c.apparent_temperature)+unitStr();
  q('w-hum').textContent=Math.round(c.relative_humidity_2m)+'%';
  q('w-wind').textContent=Math.round(c.wind_speed_10m)+' km/h';
  q('w-vis').textContent=(c.visibility/1000).toFixed(1)+' km';
  q('w-precip').textContent=c.precipitation.toFixed(1)+' mm';

  // Hourly
  const hEl=q('w-hourly');hEl.innerHTML='';
  for(let i=0;i<24;i++){
    const t=new Date(h.time[i]);
    const rn=h.precipitation_probability?h.precipitation_probability[i]||0:0;
    const div=document.createElement('div');
    div.className='h-item'+(i===0?' now':'');
    div.innerHTML=`<div class="h-time">${i===0?'Now':t.toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})}</div>
<div class="h-icon">${EMO[h.weather_code[i]]||'\uD83C\uDF21'}</div>
<div class="h-temp">${disp(h.temperature_2m[i])}&deg;</div>
${rn>10?`<div class="h-rain">&#128167;${rn}%</div>`:''}`;
    hEl.appendChild(div);
  }

  // Daily
  const dEl=q('w-daily');dEl.innerHTML='';
  const lo=dl.temperature_2m_min,hi=dl.temperature_2m_max;
  const glo=Math.min(...lo),ghi=Math.max(...hi),span=ghi-glo||1;
  for(let i=0;i<7;i++){
    const dt=new Date(dl.time[i]);
    const bl=((lo[i]-glo)/span)*100;
    const bw=Math.max(5,((hi[i]-lo[i])/span)*100);
    const div=document.createElement('div');
    div.className='d-item'+(i===0?' today':'');
    div.innerHTML=`<span class="d-name">${i===0?'Today':DAYS[dt.getDay()]}</span>
<span class="d-icon">${EMO[dl.weather_code[i]]||'\uD83C\uDF21'}</span>
<div class="d-bar-bg"><div class="d-bar" style="margin-left:${bl.toFixed(1)}%;width:${bw.toFixed(1)}%"></div></div>
<div class="d-temps"><span class="d-lo">${disp(lo[i])}&deg;</span><span>${disp(hi[i])}&deg;</span></div>`;
    dEl.appendChild(div);
  }

  // UV
  const uv=Math.round(c.uv_index||0);
  q('w-uv').textContent=uv;q('w-uv-lbl').textContent=uvLabel(uv);q('uv-advice').textContent=uvAdvice(uv);
  const circ=2*Math.PI*34;
  const arc=q('uv-arc');
  arc.style.strokeDashoffset=Math.max(0,circ-(uv/11)*circ);
  arc.style.stroke=uv<=2?'#4a93f0':uv<=5?'#3dd6a3':uv<=7?'#f0a832':'#f06060';

  // Atmosphere
  q('w-pres').textContent=Math.round(c.surface_pressure);
  q('w-cloud').textContent=Math.round(c.cloud_cover)+'%';
  q('w-dew').textContent=disp(c.dew_point_2m)+unitStr();
  q('w-wdir').textContent=wdir(c.wind_direction_10m);

  // Sun
  const rise=new Date(dl.sunrise[0]),set=new Date(dl.sunset[0]),now=new Date();
  q('t-rise').textContent='\u2191 '+rise.toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});
  q('t-set').textContent='\u2193 '+set.toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});
  const dayLen=((set-rise)/3600000).toFixed(1);
  q('t-daylen').textContent=dayLen+'h daylight';
  const prog=Math.max(0,Math.min(1,(now-rise)/(set-rise)));
  const sx=16,sy=68,ex=324,ey=68,bx=170,by=-10;
  const t1=1-prog,p=prog;
  const qx=sx*t1*t1+2*bx*t1*p+ex*p*p;
  const qy=sy*t1*t1+2*by*t1*p+ey*p*p;
  const dot=q('sun-dot');dot.setAttribute('cx',qx.toFixed(1));dot.setAttribute('cy',qy.toFixed(1));

  // UV alert banner
  const bar=q('alert-bar');
  if(uv>=6){bar.style.display='block';bar.textContent='&#9888; High UV Index today ('+uv+'). Sun protection recommended.';}
  else{bar.style.display='none';}

  show('weather');
}

async function fetchWeather(lat,lon,city){
  show('loading');
  const fields=['temperature_2m','apparent_temperature','relative_humidity_2m','precipitation','weather_code','wind_speed_10m','wind_direction_10m','surface_pressure','cloud_cover','visibility','uv_index','dew_point_2m'].join(',');
  const hf=['temperature_2m','weather_code','precipitation_probability'].join(',');
  const df=['weather_code','temperature_2m_max','temperature_2m_min','sunrise','sunset'].join(',');
  const url=`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=${fields}&hourly=${hf}&forecast_hours=24&daily=${df}&forecast_days=7&timezone=auto`;
  try{
    const res=await fetch(url);
    if(!res.ok)throw new Error('Weather API error '+res.status);
    const d=await res.json();
    d.city=city;
    render(d);
  }catch(e){
    q('err-txt').textContent=e.message||'Failed to fetch weather.';
    show('error');
  }
}

async function geocode(name){
  show('loading');
  const url=`https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(name)}&count=1&language=en&format=json`;
  try{
    const res=await fetch(url);
    const d=await res.json();
    if(!d.results||!d.results.length)throw new Error(`City "${name}" not found. Try a different name.`);
    const r=d.results[0];
    const cityName=[r.name,r.country_code].filter(Boolean).join(', ');
    await fetchWeather(r.latitude,r.longitude,cityName);
  }catch(e){
    q('err-txt').textContent=e.message||'Geocoding failed.';
    show('error');
  }
}

q('srch-btn').onclick=()=>{const v=q('city-input').value.trim();if(v)geocode(v);};
q('city-input').onkeydown=e=>{if(e.key==='Enter'){const v=e.target.value.trim();if(v)geocode(v);}};
q('loc-btn').onclick=()=>{
  if(!navigator.geolocation){q('err-txt').textContent='Geolocation not supported by your browser.';show('error');return;}
  show('loading');
  navigator.geolocation.getCurrentPosition(
    p=>fetchWeather(p.coords.latitude,p.coords.longitude,'Your Location'),
    ()=>{q('err-txt').textContent='Location access denied.';show('error');}
  );
};
</script>
</body>
</html>"""

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML.encode())

def main():
    srv = http.server.HTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://127.0.0.1:{PORT}"
    print(f"\n  🌤  Weather App → {url}")
    print(f"  Press Ctrl+C to stop\n")
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.")
        srv.shutdown()

if __name__ == "__main__":
    main()
