import html
import json
import shutil
from datetime import datetime
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Orbit Files", page_icon="🪐", layout="wide")

ROOT = Path("workspace").resolve()      # every action stays inside this folder
TRASH = ROOT / ".trash"                 # deleted items go here first (restorable)
ROOT.mkdir(exist_ok=True)

# =================================================================== THEME
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;700;800&family=DM+Sans:wght@400;500;700&display=swap');
    @property --ang { syntax: '<angle>'; initial-value: 0deg; inherits: false; }

    :root {
        color-scheme: dark;
        --bg:#070A18; --panel:rgba(255,255,255,.05); --line:rgba(255,255,255,.11);
        --text:#EAEEFF; --muted:#8E99CC;
        --violet:#7C5CFF; --cyan:#22D3EE; --pink:#FF5C93; --amber:#FFC24B; --lime:#6BF2A5;
    }
    html, body, .stApp, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--text); }

    /* animated aurora */
    .stApp {
        background:
            radial-gradient(600px 420px at 12% 8%,  rgba(124,92,255,.42), transparent 70%),
            radial-gradient(560px 420px at 88% 6%,  rgba(34,211,238,.28), transparent 70%),
            radial-gradient(620px 460px at 55% 98%, rgba(255,92,147,.20), transparent 70%),
            var(--bg);
        background-size: 160% 160%, 160% 160%, 160% 160%, 100% 100%;
        background-attachment: fixed;
        animation: aurora 22s ease-in-out infinite alternate;
    }
    @keyframes aurora {
        0%   { background-position: 0% 0%,   100% 0%,   50% 100%, 0 0; }
        100% { background-position: 40% 30%, 60% 40%,   20% 70%,  0 0; }
    }
    header[data-testid="stHeader"] { background: transparent; }
    .block-container { padding-top: 1.8rem; max-width: 1180px; }
    h1,h2,h3,h4 { font-family:'Sora',sans-serif !important; color:var(--text) !important; letter-spacing:-.02em; }
    p, label, li, [data-testid="stWidgetLabel"] p { color:var(--text); }
    [data-testid="stCaptionContainer"], small { color:var(--muted) !important; }

    /* sidebar */
    [data-testid="stSidebar"] { background:rgba(8,11,28,.82); backdrop-filter:blur(16px); border-right:1px solid var(--line); }
    .brand { font-family:'Sora',sans-serif; font-weight:800; font-size:1.5rem; letter-spacing:-.03em; }
    .brand i { font-style:normal; background:linear-gradient(135deg,var(--violet),var(--cyan));
               -webkit-background-clip:text; background-clip:text; color:transparent; }
    [data-testid="stSidebar"] [role="radiogroup"] label {
        background:var(--panel); border:1px solid var(--line); border-radius:12px;
        padding:.55rem .85rem; margin-bottom:.4rem; width:100%; transition:.18s;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover { border-color:var(--violet); transform:translateX(3px); }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        background:linear-gradient(135deg, rgba(124,92,255,.40), rgba(34,211,238,.24));
        border-color:var(--violet); box-shadow:0 0 22px rgba(124,92,255,.35);
    }
    [data-testid="stSidebar"] [role="radiogroup"] label > div:first-child { display:none; }

    /* hero with spinning gradient border */
    .hero {
        position:relative; overflow:hidden; border-radius:24px; padding:2.1rem 2.3rem; margin-bottom:1.4rem;
        border:2px solid transparent;
        background:
            linear-gradient(135deg,#121838,#0A0F28) padding-box,
            conic-gradient(from var(--ang), var(--violet), var(--cyan), var(--pink), var(--amber), var(--violet)) border-box;
        animation: spin 7s linear infinite;
    }
    @keyframes spin { to { --ang: 360deg; } }
    .hero:after {
        content:""; position:absolute; right:-70px; top:-70px; width:270px; height:270px; border-radius:50%;
        background:radial-gradient(circle at 30% 30%, rgba(255,255,255,.35), transparent 58%),
                   linear-gradient(135deg,var(--violet),var(--pink));
        opacity:.55; animation: float 7s ease-in-out infinite alternate;
    }
    @keyframes float { to { transform: translate(-18px, 14px) scale(1.06); } }
    .hero h1 { font-size:2.6rem; margin:0; font-weight:800; line-height:1.1; }
    .hero h1 span {
        background:linear-gradient(90deg,var(--cyan),var(--violet),var(--pink),var(--cyan));
        background-size:250% 100%; -webkit-background-clip:text; background-clip:text; color:transparent;
        animation: shimmer 6s linear infinite;
    }
    @keyframes shimmer { to { background-position:250% 0; } }
    .hero p { color:var(--muted); margin:.5rem 0 .9rem; max-width:520px; position:relative; z-index:1; }
    .chip { display:inline-flex; align-items:center; gap:.5rem; padding:.28rem .75rem; border-radius:99px;
            background:rgba(255,255,255,.07); border:1px solid var(--line); font-size:.8rem; position:relative; z-index:1; }
    .dot { width:8px; height:8px; border-radius:50%; background:var(--lime); box-shadow:0 0 0 0 rgba(107,242,165,.7); animation:pulse 1.8s infinite; }
    @keyframes pulse { 70% { box-shadow:0 0 0 9px rgba(107,242,165,0); } 100% { box-shadow:0 0 0 0 rgba(107,242,165,0); } }

    /* stats */
    .stats { display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:14px; margin-bottom:1.2rem; }
    .stat { position:relative; overflow:hidden; background:var(--panel); border:1px solid var(--line); border-radius:18px;
            padding:1.05rem 1.2rem; backdrop-filter:blur(10px); }
    .stat:before { content:""; position:absolute; left:0; top:0; bottom:0; width:4px; background:var(--c); box-shadow:0 0 18px var(--c); }
    .stat b { font-family:'Sora',sans-serif; font-size:1.75rem; display:block; color:var(--c); }
    .stat span { color:var(--muted); font-size:.85rem; }

    /* panels */
    .panel { background:var(--panel); border:1px solid var(--line); border-radius:18px; padding:1.1rem 1.3rem; backdrop-filter:blur(10px); height:100%; }
    .panel h4 { margin:0 0 .8rem; font-size:1rem; }
    .donutwrap { display:flex; align-items:center; gap:1.4rem; flex-wrap:wrap; }
    .donutwrap svg { width:150px; height:150px; filter:drop-shadow(0 0 12px rgba(124,92,255,.35)); }
    .legend div { display:flex; align-items:center; gap:.5rem; font-size:.88rem; margin:.28rem 0; }
    .legend i { width:10px; height:10px; border-radius:3px; display:inline-block; }
    .log div { font-size:.86rem; padding:.42rem 0; border-bottom:1px dashed var(--line); display:flex; gap:.7rem; }
    .log div:last-child { border-bottom:0; }
    .log time { color:var(--muted); font-variant-numeric:tabular-nums; }

    /* cards */
    .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(215px,1fr)); gap:14px; margin-top:.8rem; }
    .card { position:relative; background:var(--panel); border:1px solid var(--line); border-radius:18px; padding:1rem; transition:.2s; overflow:hidden; }
    .card:before { content:""; position:absolute; inset:0; opacity:0; transition:.25s;
                   background:radial-gradient(260px 120px at 50% 0%, rgba(124,92,255,.28), transparent 70%); }
    .card:hover { transform:translateY(-4px); border-color:var(--violet); box-shadow:0 14px 34px rgba(124,92,255,.30); }
    .card:hover:before { opacity:1; }
    .card .ico { position:relative; font-size:1.7rem; width:48px; height:48px; display:grid; place-items:center; border-radius:14px; margin-bottom:.75rem; }
    .card.folder .ico { background:rgba(255,194,75,.16); box-shadow:inset 0 0 0 1px rgba(255,194,75,.35); }
    .card.file   .ico { background:rgba(34,211,238,.14); box-shadow:inset 0 0 0 1px rgba(34,211,238,.32); }
    .card .nm { position:relative; font-weight:700; word-break:break-all; }
    .card .meta { position:relative; color:var(--muted); font-size:.8rem; margin-top:.25rem; }
    .empty { text-align:center; padding:3rem 1rem; color:var(--muted); border:1.5px dashed var(--line); border-radius:20px; }

    /* tree */
    .tree { font-family:'DM Sans',sans-serif; }
    .tree ul { list-style:none; margin:0; padding-left:1.15rem; border-left:1px dashed rgba(255,255,255,.2); }
    .tree > ul { border-left:0; padding-left:0; }
    .tree li { padding:.22rem 0 .22rem .55rem; }
    .tree .d { color:var(--amber); font-weight:700; }
    .tree .f { color:var(--text); }
    .tree .s { color:var(--muted); font-size:.78rem; margin-left:.5rem; }

    /* inputs */
    .stTextInput input, .stTextArea textarea, [data-baseweb="select"] > div {
        background:rgba(255,255,255,.06) !important; color:var(--text) !important;
        border:1px solid var(--line) !important; border-radius:12px !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus { border-color:var(--violet) !important; box-shadow:0 0 0 3px rgba(124,92,255,.28) !important; }
    [data-baseweb="popover"] ul, [data-baseweb="menu"] { background:#10152E !important; }
    [data-baseweb="popover"] li { color:var(--text) !important; }
    [data-testid="stFileUploaderDropzone"] { background:var(--panel); border:1.5px dashed var(--violet); border-radius:18px; }
    [data-testid="stFileUploaderDropzone"] button { background:rgba(255,255,255,.08) !important; color:var(--text) !important; border:1px solid var(--line) !important; }

    /* buttons: primary = gradient, secondary = danger */
    [data-testid="stBaseButton-primary"], [data-testid="stDownloadButton"] button {
        background:linear-gradient(135deg,var(--violet),var(--cyan)); color:#fff; border:0; border-radius:12px;
        font-weight:700; padding:.55rem 1.3rem; transition:.18s;
    }
    [data-testid="stBaseButton-primary"]:hover, [data-testid="stDownloadButton"] button:hover {
        transform:translateY(-2px); box-shadow:0 10px 26px rgba(124,92,255,.5); color:#fff;
    }
    [data-testid="stBaseButton-secondary"] {
        background:rgba(255,92,147,.14); color:var(--pink); border:1px solid rgba(255,92,147,.5);
        border-radius:12px; font-weight:700; padding:.55rem 1.3rem;
    }
    [data-testid="stBaseButton-secondary"]:hover { background:var(--pink); color:#fff; }
    [data-testid="stBaseButton-secondary"]:disabled { opacity:.35; }

    /* tabs / alerts */
    .stTabs [data-baseweb="tab-list"] { gap:6px; border-bottom:1px solid var(--line); }
    .stTabs [data-baseweb="tab"] { color:var(--muted); padding:.5rem 1rem; }
    .stTabs [aria-selected="true"] { color:var(--cyan) !important; }
    .stTabs [data-baseweb="tab-highlight"] { background:linear-gradient(90deg,var(--violet),var(--cyan)); height:3px; }
    [data-testid="stAlert"] { background:var(--panel); border:1px solid var(--line); border-radius:14px; }
    hr { border-color:var(--line); }
    @media (prefers-reduced-motion: reduce) { .stApp, .hero, .hero:after, .hero h1 span, .dot { animation:none !important; } }
    </style>
    """,
    unsafe_allow_html=True,
)

# =================================================================== 3D CSS
st.markdown(
    """
    <style>
    /* rotating 3D cube in the hero */
    .cube-wrap { position:absolute; right:78px; top:50%; margin-top:-70px; width:140px; height:140px; perspective:700px; z-index:2; }
    .cube { width:100%; height:100%; position:relative; transform-style:preserve-3d; animation:cube 16s linear infinite; }
    .cube span {
        position:absolute; width:140px; height:140px; display:grid; place-items:center; font-size:3rem;
        border:1px solid rgba(255,255,255,.4);
        background:linear-gradient(135deg, rgba(124,92,255,.45), rgba(34,211,238,.28));
        box-shadow:inset 0 0 34px rgba(255,255,255,.14), 0 0 30px rgba(124,92,255,.35);
    }
    .cube span:nth-child(1) { transform:rotateY(0deg)   translateZ(70px); }
    .cube span:nth-child(2) { transform:rotateY(90deg)  translateZ(70px); }
    .cube span:nth-child(3) { transform:rotateY(180deg) translateZ(70px); }
    .cube span:nth-child(4) { transform:rotateY(-90deg) translateZ(70px); }
    .cube span:nth-child(5) { transform:rotateX(90deg)  translateZ(70px); }
    .cube span:nth-child(6) { transform:rotateX(-90deg) translateZ(70px); }
    @keyframes cube { from { transform:rotateX(-22deg) rotateY(0deg); } to { transform:rotateX(-22deg) rotateY(360deg); } }
    @media (max-width: 820px) { .cube-wrap { display:none; } }

    /* tilting 3D cards */
    .grid { perspective:1100px; }
    .card { overflow:visible !important; transform-style:preserve-3d; }
    .card:before { border-radius:inherit; }
    .card:hover { transform: translateY(-6px) rotateX(9deg) rotateY(-11deg) translateZ(22px) !important; }
    .card .ico { transition:transform .25s; }
    .card:hover .ico { transform: translateZ(42px) scale(1.08); }
    .card:hover .nm { transform: translateZ(26px); }
    .card .nm { transition:transform .25s; }

    /* 3D stat tiles */
    .stats { perspective:900px; }
    .stat { transition:.25s; transform-style:preserve-3d; }
    .stat:hover { transform: rotateX(8deg) rotateY(8deg) translateZ(14px); box-shadow:0 18px 40px rgba(0,0,0,.45); }

    iframe { border-radius:22px; border:1px solid rgba(255,255,255,.14); box-shadow:0 20px 60px rgba(124,92,255,.25); }
    </style>
    """,
    unsafe_allow_html=True,
)

# three.js scene: folders and files floating in space around the workspace core
UNIVERSE_TEMPLATE = """
<!doctype html><html><head><meta charset="utf-8">
<style>
  html,body{margin:0;height:100%;overflow:hidden;background:radial-gradient(ellipse at 50% 40%,#141a42 0%,#070A18 70%);font-family:'DM Sans',system-ui,sans-serif;color:#EAEEFF}
  #tip{position:absolute;pointer-events:none;padding:6px 10px;border-radius:10px;background:rgba(10,14,34,.92);border:1px solid rgba(255,255,255,.2);font-size:12px;display:none;white-space:nowrap}
  #hud{position:absolute;left:14px;bottom:12px;font-size:12px;color:#9aa6d8;line-height:1.6}
  #hud i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:6px}
  #info{position:absolute;right:14px;top:14px;min-width:190px;padding:12px 14px;border-radius:14px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.16);backdrop-filter:blur(8px);font-size:13px}
  #info b{display:block;font-size:15px;margin-bottom:4px;word-break:break-all}
  #empty{position:absolute;inset:0;display:none;place-items:center;color:#9aa6d8;font-size:15px}
</style></head><body>
<div id="tip"></div><div id="empty">The workspace is empty. Create something to see it float here.</div>
<div id="info"><b>Drag to orbit</b>Scroll to zoom<br>Click a node for details</div>
<div id="hud"><i style="background:#FFC24B"></i>Folder &nbsp;<i style="background:#22D3EE"></i>Docs &nbsp;<i style="background:#7C5CFF"></i>Code &nbsp;<i style="background:#6BF2A5"></i>Data &nbsp;<i style="background:#FF5C93"></i>Media</div>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
const DATA = __DATA__;
const W = () => window.innerWidth, H = () => window.innerHeight;
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x070A18, 0.018);
const camera = new THREE.PerspectiveCamera(55, W()/H(), 0.1, 500);
const renderer = new THREE.WebGLRenderer({antialias:true, alpha:true});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(W(), H());
document.body.appendChild(renderer.domElement);
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; controls.autoRotate = true; controls.autoRotateSpeed = 0.9;

scene.add(new THREE.AmbientLight(0xffffff, 0.55));
const l1 = new THREE.PointLight(0x7C5CFF, 1.6, 90); l1.position.set(14, 12, 10); scene.add(l1);
const l2 = new THREE.PointLight(0x22D3EE, 1.4, 90); l2.position.set(-14, -8, -10); scene.add(l2);
const l3 = new THREE.PointLight(0xFF5C93, 1.0, 90); l3.position.set(0, 14, -14); scene.add(l3);

// star field
{
  const n = 900, pos = new Float32Array(n*3);
  for (let i=0;i<n;i++){ const r=60+Math.random()*120, a=Math.random()*6.283, b=Math.acos(2*Math.random()-1);
    pos[i*3]=r*Math.sin(b)*Math.cos(a); pos[i*3+1]=r*Math.cos(b); pos[i*3+2]=r*Math.sin(b)*Math.sin(a); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos,3));
  scene.add(new THREE.Points(g, new THREE.PointsMaterial({color:0xaab8ff,size:0.55,transparent:true,opacity:.8})));
}

function label(text, color){
  const c = document.createElement('canvas'); c.width = 512; c.height = 96;
  const x = c.getContext('2d'); x.font = '700 44px sans-serif'; x.textAlign = 'center'; x.textBaseline = 'middle';
  x.shadowColor = color; x.shadowBlur = 14; x.fillStyle = '#fff';
  x.fillText(text.length > 22 ? text.slice(0,21)+'…' : text, 256, 48);
  const s = new THREE.Sprite(new THREE.SpriteMaterial({map:new THREE.CanvasTexture(c), transparent:true, depthWrite:false}));
  s.scale.set(5.2, 0.98, 1); return s;
}

// ---- build tree from flat paths
const root = {p:'', k:'root', kids:[], pos:new THREE.Vector3()};
const byPath = new Map([['', root]]);
DATA.sort((a,b) => a.p.split('/').length - b.p.split('/').length);
DATA.forEach(n => {
  const i = n.p.lastIndexOf('/'); const parent = byPath.get(i < 0 ? '' : n.p.slice(0,i)) || root;
  n.kids = []; n.parent = parent; parent.kids.push(n); byPath.set(n.p, n);
});
function layout(node, depth){
  const N = node.kids.length, R = ([8, 5, 3.8][depth] || 3.4) + N*0.06;
  node.kids.forEach((c,i) => {
    const y = N === 1 ? 0.2 : 1 - (i + 0.5) / N * 2, r = Math.sqrt(Math.max(0, 1 - y*y)), th = i * 2.399963 + depth;
    c.pos = node.pos.clone().add(new THREE.Vector3(Math.cos(th)*r, y, Math.sin(th)*r).multiplyScalar(R));
  });
  node.kids.forEach(c => { if (c.k === 'folder') layout(c, depth + 1); });
}
layout(root, 0);

const GROUPS = [
  [['.py','.js','.html','.css','.json','.ts','.java','.c','.cpp'], 0x7C5CFF],
  [['.txt','.md','.pdf','.docx'], 0x22D3EE],
  [['.csv','.xlsx','.xls'], 0x6BF2A5],
  [['.png','.jpg','.jpeg','.gif','.webp','.mp3','.mp4'], 0xFF5C93],
];
const colorOf = e => (GROUPS.find(g => g[0].includes(e)) || [0, 0xFFC24B])[1];

const spinners = [], pickables = [];
function mat(color, em){ return new THREE.MeshStandardMaterial({color, emissive:color, emissiveIntensity:em, roughness:.35, metalness:.25}); }

// core
const core = new THREE.Group();
core.add(new THREE.Mesh(new THREE.IcosahedronGeometry(1.6, 1), mat(0x7C5CFF, .7)));
core.add(new THREE.Mesh(new THREE.IcosahedronGeometry(2.3, 1), new THREE.MeshBasicMaterial({color:0x22D3EE, wireframe:true, transparent:true, opacity:.45})));
const coreLabel = label('workspace', '#7C5CFF'); coreLabel.position.set(0, 3.5, 0);
scene.add(core, coreLabel); spinners.push({m:core, s:.006, base:0, ph:0});

const lineMat = c => new THREE.LineBasicMaterial({color:c, transparent:true, opacity:.4});
let maxR = 10, idx = 0;

(function build(node){
  node.kids.forEach(n => {
    idx++;
    const g = new THREE.Group();
    if (n.k === 'folder') {
      g.add(new THREE.Mesh(new THREE.BoxGeometry(1.7, 1.15, 1.0), mat(0xFFC24B, .35)));
      const tab = new THREE.Mesh(new THREE.BoxGeometry(.7, .22, 1.0), mat(0xFFD98A, .35)); tab.position.set(-.5, .68, 0); g.add(tab);
      const lb = label(n.p.split('/').pop(), '#FFC24B'); lb.position.set(0, 1.6, 0); g.add(lb);
    } else {
      const sc = .75 + Math.min(1.1, Math.log10(Math.max(n.s, 10)) / 6 * 1.4);
      const tablet = new THREE.Mesh(new THREE.BoxGeometry(.8*sc, 1.05*sc, .14), mat(colorOf(n.e), .55));
      g.add(tablet);
      const edge = new THREE.LineSegments(new THREE.EdgesGeometry(tablet.geometry), new THREE.LineBasicMaterial({color:0xffffff, transparent:true, opacity:.55}));
      g.add(edge);
    }
    g.position.copy(n.pos); g.userData.node = n; n.obj = g; scene.add(g);
    g.traverse(o => { if (o.isMesh) pickables.push(o); });
    spinners.push({m:g, s: n.k === 'folder' ? .008 : .014, base: n.pos.y, ph: idx * .7});
    maxR = Math.max(maxR, n.pos.length());
    const pts = [n.parent.pos, n.pos];
    scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), lineMat(n.k === 'folder' ? 0xFFC24B : 0x7C5CFF)));
    build(n);
  });
})(root);

if (!DATA.length) document.getElementById('empty').style.display = 'grid';
camera.position.set(0, maxR*.55, Math.max(20, maxR*2.3));

// ---- interaction
const ray = new THREE.Raycaster(), mouse = new THREE.Vector2(), tip = document.getElementById('tip'), info = document.getElementById('info');
let hover = null, selected = null;
function nodeOf(obj){ while (obj && !obj.userData.node) obj = obj.parent; return obj ? obj.userData.node : null; }
function fmt(n){ return n < 1024 ? n+' B' : n < 1048576 ? (n/1024).toFixed(1)+' KB' : (n/1048576).toFixed(1)+' MB'; }
function pick(ev){
  const r = renderer.domElement.getBoundingClientRect();
  mouse.set(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1);
  ray.setFromCamera(mouse, camera);
  const hit = ray.intersectObjects(pickables, false)[0];
  return hit ? nodeOf(hit.object) : null;
}
renderer.domElement.addEventListener('pointermove', ev => {
  hover = pick(ev);
  controls.autoRotate = !hover;
  renderer.domElement.style.cursor = hover ? 'pointer' : 'grab';
  if (hover) { tip.style.display = 'block'; tip.style.left = ev.clientX + 14 + 'px'; tip.style.top = ev.clientY + 14 + 'px';
    tip.textContent = (hover.k === 'folder' ? '📁 ' : '📄 ') + hover.p; } else tip.style.display = 'none';
});
renderer.domElement.addEventListener('click', ev => {
  const n = pick(ev); selected = n; if (!n) return;
  info.innerHTML = '<b>' + (n.k === 'folder' ? '📁 ' : '📄 ') + n.p.split('/').pop() + '</b>' +
    'Path: ' + n.p + '<br>' + (n.k === 'folder' ? 'Contains ' + n.kids.length + ' item(s)' : 'Size: ' + fmt(n.s) + '<br>Type: ' + (n.e || 'none'));
});
addEventListener('resize', () => { camera.aspect = W()/H(); camera.updateProjectionMatrix(); renderer.setSize(W(), H()); });

const clock = new THREE.Clock();
(function loop(){
  requestAnimationFrame(loop);
  const t = clock.getElapsedTime();
  spinners.forEach(s => { s.m.rotation.y += s.s; if (s.m !== core) s.m.position.y = s.base + Math.sin(t*1.1 + s.ph) * .22; });
  DATA.forEach(n => { if (n.obj) { const target = (n === hover || n === selected) ? 1.35 : 1; n.obj.scale.lerp(new THREE.Vector3(target,target,target), .15); } });
  core.scale.setScalar(1 + Math.sin(t*2) * .04);
  controls.update(); renderer.render(scene, camera);
})();
</script></body></html>
"""


def universe_html(folder_paths: list[Path], file_paths: list[Path]) -> str:
    nodes = [{"p": rel(p), "k": "folder", "s": 0, "e": ""} for p in folder_paths]
    nodes += [{"p": rel(p), "k": "file", "s": p.stat().st_size, "e": p.suffix.lower()} for p in file_paths]
    data = json.dumps(nodes).replace("</", "<\\/")
    return UNIVERSE_TEMPLATE.replace("__DATA__", data)


# =================================================================== HELPERS
ICONS = {
    ".py": "🐍", ".txt": "📄", ".md": "📝", ".json": "🧾", ".csv": "📊", ".xlsx": "📊",
    ".pdf": "📕", ".png": "🖼️", ".jpg": "🖼️", ".jpeg": "🖼️", ".gif": "🖼️", ".webp": "🖼️",
    ".html": "🌐", ".css": "🎨", ".js": "⚡", ".zip": "🗜️", ".mp3": "🎵", ".mp4": "🎬",
}
GROUPS = {
    "Code": ({".py", ".js", ".html", ".css", ".json", ".ts", ".java", ".c", ".cpp"}, "#7C5CFF"),
    "Docs": ({".txt", ".md", ".pdf", ".docx"}, "#22D3EE"),
    "Data": ({".csv", ".xlsx", ".xls"}, "#6BF2A5"),
    "Media": ({".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp3", ".mp4"}, "#FF5C93"),
    "Other": (set(), "#FFC24B"),
}
LANG = {".py": "python", ".js": "javascript", ".json": "json", ".html": "html", ".css": "css", ".md": "markdown"}
IMAGES = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


def safe_path(name: str) -> Path | None:
    """Resolve a user-supplied name inside ROOT, or None if it would escape ROOT."""
    name = name.strip()
    if not name:
        return None
    p = (ROOT / name).resolve()
    if p != ROOT and ROOT not in p.parents:
        return None
    if ".trash" in p.relative_to(ROOT).parts:
        return None
    return p


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def visible(p: Path) -> bool:
    return ".trash" not in p.relative_to(ROOT).parts


def human_size(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


def flash(ok: bool, msg: str):
    """Log + toast after the page refreshes, so every list is up to date."""
    st.session_state["flash"] = (ok, msg)
    if ok:
        st.session_state.setdefault("log", []).insert(0, (datetime.now().strftime("%H:%M"), msg))
        st.session_state["log"] = st.session_state["log"][:8]
    st.rerun()


# ---- trash (soft delete) -------------------------------------------------
def load_idx() -> dict:
    try:
        return json.loads((TRASH / "index.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_idx(idx: dict):
    TRASH.mkdir(exist_ok=True)
    (TRASH / "index.json").write_text(json.dumps(idx, indent=2), encoding="utf-8")


def move_to_trash(name: str, kind: str):
    idx = load_idx()
    tid = datetime.now().strftime("%Y%m%d%H%M%S%f")
    TRASH.mkdir(exist_ok=True)
    shutil.move(str(ROOT / name), str(TRASH / tid))
    idx[tid] = {"orig": name, "kind": kind, "when": datetime.now().strftime("%d %b %H:%M")}
    save_idx(idx)


# ---- html builders ---------------------------------------------------------
def donut_html(file_paths: list[Path]) -> str:
    counts = {g: 0 for g in GROUPS}
    for p in file_paths:
        ext = p.suffix.lower()
        counts[next((g for g, (exts, _) in GROUPS.items() if ext in exts), "Other")] += 1
    total = sum(counts.values())
    if total == 0:
        return '<div class="panel"><h4>File types</h4><div class="empty">No files yet</div></div>'
    circles, legend, cum = [], [], 0.0
    for g, n in counts.items():
        if n == 0:
            continue
        pct = n / total * 100
        color = GROUPS[g][1]
        circles.append(
            f'<circle cx="21" cy="21" r="15.9155" fill="none" stroke="{color}" stroke-width="5" '
            f'stroke-dasharray="{pct:.2f} {100 - pct:.2f}" stroke-dashoffset="{25 - cum:.2f}"/>'
        )
        legend.append(f'<div><i style="background:{color}"></i>{g} · {n}</div>')
        cum += pct
    svg = (
        '<svg viewBox="0 0 42 42">'
        '<circle cx="21" cy="21" r="15.9155" fill="none" stroke="rgba(255,255,255,.07)" stroke-width="5"/>'
        + "".join(circles)
        + f'<text x="21" y="22.5" text-anchor="middle" fill="#EAEEFF" font-size="7" font-weight="700" '
        f'font-family="Sora,sans-serif">{total}</text></svg>'
    )
    return (
        f'<div class="panel"><h4>File types</h4><div class="donutwrap">{svg}'
        f'<div class="legend">{"".join(legend)}</div></div></div>'
    )


def log_html() -> str:
    rows = st.session_state.get("log", [])
    body = "".join(f"<div><time>{t}</time><span>{html.escape(m)}</span></div>" for t, m in rows)
    body = body or '<div style="color:var(--muted)">Actions you take will show up here.</div>'
    return f'<div class="panel"><h4>Recent activity</h4><div class="log">{body}</div></div>'


def tree_html(base: Path) -> str:
    items = sorted(
        (p for p in base.iterdir() if p.name != ".trash"),
        key=lambda p: (p.is_file(), p.name.lower()),
    )
    out = ["<ul>"]
    for p in items:
        name = html.escape(p.name)
        if p.is_dir():
            out.append(f'<li><span class="d">📁 {name}</span>{tree_html(p)}</li>')
        else:
            icon = ICONS.get(p.suffix.lower(), "📄")
            out.append(f'<li><span class="f">{icon} {name}</span><span class="s">{human_size(p.stat().st_size)}</span></li>')
    out.append("</ul>")
    return "".join(out)


# =================================================================== DATA
if "flash" in st.session_state:
    ok, msg = st.session_state.pop("flash")
    st.toast(msg, icon="✅" if ok else "⚠️")

folder_paths = sorted((p for p in ROOT.rglob("*") if p.is_dir() and visible(p)), key=lambda p: rel(p).lower())
file_paths = sorted((p for p in ROOT.rglob("*") if p.is_file() and visible(p)), key=lambda p: rel(p).lower())
folders = [rel(p) for p in folder_paths]
files = [rel(p) for p in file_paths]
trash_idx = {k: v for k, v in load_idx().items() if (TRASH / k).exists()}

# =================================================================== SIDEBAR
PAGES = {
    "🧭  Explorer": "explorer",
    "🌌  3D Universe": "universe",
    "🌳  Tree view": "tree",
    "📁  Folders": "folders",
    "📄  Files": "files",
    "⬆️  Upload": "upload",
    f"🗑️  Trash ({len(trash_idx)})": "trash",
}
with st.sidebar:
    st.markdown('<div class="brand">🪐 Orbit<i>Files</i></div>', unsafe_allow_html=True)
    st.caption("Your tiny file universe")
    st.write("")
    page = PAGES[st.radio("Navigate", list(PAGES), label_visibility="collapsed")]
    st.divider()
    st.caption(f"{len(folders)} folders · {len(files)} files")

st.markdown(
    f"""
    <div class="hero">
      <h1>Manage files<br><span>at light speed</span></h1>
      <p>Create, browse, edit and clean up folders and files without touching the terminal.</p>
      <span class="chip"><i class="dot"></i> {html.escape(ROOT.name)}/ · live</span>
      <div class="cube-wrap"><div class="cube"><span>📁</span><span>🐍</span><span>📊</span><span>🖼️</span><span>📄</span><span>🌐</span></div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =================================================================== EXPLORER
if page == "explorer":
    total = sum(p.stat().st_size for p in file_paths)
    latest = max((p.stat().st_mtime for p in file_paths), default=None)
    latest_txt = datetime.fromtimestamp(latest).strftime("%d %b, %H:%M") if latest else "—"
    st.markdown(
        f"""
        <div class="stats">
          <div class="stat" style="--c:#22D3EE"><b>{len(folders)}</b><span>Folders</span></div>
          <div class="stat" style="--c:#FFC24B"><b>{len(files)}</b><span>Files</span></div>
          <div class="stat" style="--c:#FF5C93"><b>{human_size(total)}</b><span>Total size</span></div>
          <div class="stat" style="--c:#A99BFF"><b>{latest_txt}</b><span>Last change</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    left, right = st.columns(2)
    left.markdown(donut_html(file_paths), unsafe_allow_html=True)
    right.markdown(log_html(), unsafe_allow_html=True)

    st.write("")
    c1, c2, c3 = st.columns([3, 2, 2])
    query = c1.text_input("Search", placeholder="🔎  Search by name…", label_visibility="collapsed")
    show = c2.radio("Show", ["All", "Folders", "Files"], horizontal=True, label_visibility="collapsed")
    order = c3.selectbox("Sort", ["Name", "Newest", "Largest"], label_visibility="collapsed")

    def sort_key(p: Path):
        if order == "Newest":
            return -p.stat().st_mtime
        if order == "Largest":
            return -(p.stat().st_size if p.is_file() else 0)
        return rel(p).lower()

    cards = []
    if show in ("All", "Folders"):
        for p in sorted((p for p in folder_paths if query.lower() in rel(p).lower()), key=sort_key):
            n = sum(1 for _ in p.iterdir())
            cards.append(
                f'<div class="card folder"><div class="ico">📁</div><div class="nm">{html.escape(rel(p))}</div>'
                f'<div class="meta">{n} item{"s" if n != 1 else ""}</div></div>'
            )
    if show in ("All", "Files"):
        for p in sorted((p for p in file_paths if query.lower() in rel(p).lower()), key=sort_key):
            s = p.stat()
            when = datetime.fromtimestamp(s.st_mtime).strftime("%d %b %Y")
            cards.append(
                f'<div class="card file"><div class="ico">{ICONS.get(p.suffix.lower(), "📄")}</div>'
                f'<div class="nm">{html.escape(rel(p))}</div><div class="meta">{human_size(s.st_size)} · {when}</div></div>'
            )
    if cards:
        st.markdown(f'<div class="grid">{"".join(cards)}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="empty">🌌 Nothing here yet.<br>Create a folder or file from the sidebar to get started.</div>',
            unsafe_allow_html=True,
        )

# =================================================================== TREE
elif page == "tree":
    st.subheader("Workspace tree")
    if not folders and not files:
        st.markdown('<div class="empty">The workspace is empty.</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="panel tree"><div class="d" style="margin-bottom:.5rem">🪐 {html.escape(ROOT.name)}/</div>'
            f"{tree_html(ROOT)}</div>",
            unsafe_allow_html=True,
        )

# =================================================================== FOLDERS
elif page == "folders":
    t1, t2, t3 = st.tabs(["✨ Create", "✏️ Rename", "🗑️ Delete"])

    with t1:
        name = st.text_input("Folder name", placeholder="projects/2026", key="new_folder")
        st.caption("Tip: use / to create nested folders in one go.")
        if st.button("Create folder", type="primary"):
            p = safe_path(name)
            if p is None or p == ROOT:
                st.error("Enter a valid folder name.")
            elif p.exists():
                st.error(f"'{name}' already exists. Choose another name.")
            else:
                p.mkdir(parents=True)
                flash(True, f"Created folder {name}")

    with t2:
        if not folders:
            st.info("No folders yet. Create one first.")
        else:
            old = st.selectbox("Folder to rename", folders, key="ren_folder_old")
            new = st.text_input("New name", key="ren_folder_new")
            if st.button("Rename folder", type="primary"):
                new_p = safe_path(new)
                if new_p is None or new_p == ROOT:
                    st.error("Enter a valid new name.")
                elif new_p.exists():
                    st.error(f"'{new}' already exists. Choose another name.")
                else:
                    new_p.parent.mkdir(parents=True, exist_ok=True)
                    (ROOT / old).rename(new_p)
                    flash(True, f"Renamed {old} to {new}")

    with t3:
        if not folders:
            st.info("No folders to delete.")
        else:
            target = st.selectbox("Folder to delete", folders, key="del_folder")
            st.info("The folder moves to Trash, so you can restore it later.")
            if st.button("Move folder to Trash"):
                move_to_trash(target, "folder")
                flash(True, f"Moved folder {target} to Trash")

# =================================================================== FILES
elif page == "files":
    t1, t2, t3, t4 = st.tabs(["✨ Create", "👀 Preview", "✏️ Edit", "🗑️ Delete"])

    with t1:
        name = st.text_input("File name with extension", placeholder="notes.txt", key="new_file")
        data = st.text_area("Content", height=180, key="new_file_data")
        if st.button("Create file", type="primary"):
            p = safe_path(name)
            if p is None or p == ROOT:
                st.error("Enter a file name with extension, e.g. notes.txt")
            elif p.exists():
                st.error(f"'{name}' already exists. Choose another name.")
            else:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(data, encoding="utf-8")
                flash(True, f"Created file {name}")

    with t2:
        if not files:
            st.info("No files yet. Create one first.")
        else:
            sel = st.selectbox("File to preview", files, key="read_file")
            path, ext = ROOT / sel, (ROOT / sel).suffix.lower()
            s = path.stat()
            st.caption(f"{human_size(s.st_size)} · modified {datetime.fromtimestamp(s.st_mtime):%d %b %Y, %H:%M}")
            if ext in IMAGES:
                st.image(str(path))
            elif ext == ".csv":
                try:
                    import pandas as pd
                    st.dataframe(pd.read_csv(path))
                except Exception:
                    st.warning("Couldn't read this CSV.")
            else:
                try:
                    text = path.read_text(encoding="utf-8")
                    st.code(text or "(empty file)", language=LANG.get(ext))
                except UnicodeDecodeError:
                    st.warning("This file isn't plain text, so it can't be previewed.")
            st.download_button("Download", path.read_bytes(), file_name=path.name)

    with t3:
        if not files:
            st.info("No files to edit.")
        else:
            sel = st.selectbox("File to edit", files, key="upd_file")
            action = st.radio("What do you want to do?", ["Edit content", "Rename", "Append"], horizontal=True)
            path = ROOT / sel

            if action == "Edit content":
                try:
                    current = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    st.warning("This file isn't plain text, so it can't be edited here.")
                else:
                    new_text = st.text_area("Content", current, height=260, key=f"edit_{sel}")
                    st.caption(f"{len(new_text.splitlines())} lines · {len(new_text)} characters")
                    if st.button("Save changes", type="primary"):
                        path.write_text(new_text, encoding="utf-8")
                        flash(True, f"Saved {sel}")
            elif action == "Rename":
                new = st.text_input("New file name", key="upd_new_name")
                if st.button("Rename file", type="primary"):
                    new_p = safe_path(new)
                    if new_p is None or new_p == ROOT:
                        st.error("Enter a valid new name.")
                    elif new_p.exists():
                        st.error(f"'{new}' already exists. Choose another name.")
                    else:
                        new_p.parent.mkdir(parents=True, exist_ok=True)
                        path.rename(new_p)
                        flash(True, f"Renamed {sel} to {new}")
            else:
                data = st.text_area("Text to add at the end", height=140, key="upd_app")
                if st.button("Append to file", type="primary"):
                    with open(path, "a", encoding="utf-8") as f:
                        f.write(" " + data)
                    flash(True, f"Appended to {sel}")

    with t4:
        if not files:
            st.info("No files to delete.")
        else:
            target = st.selectbox("File to delete", files, key="del_file")
            st.info("The file moves to Trash, so you can restore it later.")
            if st.button("Move file to Trash"):
                move_to_trash(target, "file")
                flash(True, f"Moved {target} to Trash")

# =================================================================== UPLOAD
elif page == "upload":
    st.subheader("Upload files")
    dest = st.selectbox("Save into", ["(workspace root)"] + folders)
    uploads = st.file_uploader("Drop files here", accept_multiple_files=True)
    if uploads and st.button("Save uploads", type="primary"):
        base = ROOT if dest.startswith("(") else ROOT / dest
        for up in uploads:
            (base / Path(up.name).name).write_bytes(up.getbuffer())
        flash(True, f"Uploaded {len(uploads)} file(s)")

# =================================================================== 3D UNIVERSE
elif page == "universe":
    st.subheader("3D Universe")
    st.caption("Drag to orbit · scroll to zoom · hover or click any folder or file. Needs internet for the 3D engine.")
    components.html(universe_html(folder_paths, file_paths), height=640)

# =================================================================== TRASH
else:
    st.subheader("Trash")
    if not trash_idx:
        st.markdown('<div class="empty">🧹 Trash is empty.</div>', unsafe_allow_html=True)
    else:
        labels = {
            k: f'{"📁" if v["kind"] == "folder" else "📄"}  {v["orig"]}  ·  deleted {v["when"]}'
            for k, v in trash_idx.items()
        }
        tid = st.selectbox("Item", list(labels), format_func=labels.get)
        a, b, c = st.columns(3)
        if a.button("Restore", type="primary"):
            info = trash_idx[tid]
            dest = ROOT / info["orig"]
            if dest.exists():
                dest = dest.with_name(f"{dest.stem} (restored){dest.suffix}" if info["kind"] == "file" else f"{dest.name} (restored)")
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(TRASH / tid), str(dest))
            idx = load_idx()
            idx.pop(tid, None)
            save_idx(idx)
            flash(True, f"Restored {info['orig']}")
        if b.button("Delete forever"):
            item = TRASH / tid
            shutil.rmtree(item) if item.is_dir() else item.unlink()
            idx = load_idx()
            idx.pop(tid, None)
            save_idx(idx)
            flash(True, "Deleted permanently")
        if c.button("Empty trash"):
            shutil.rmtree(TRASH, ignore_errors=True)
            flash(True, "Trash emptied")
