@app.route("/")
def home():
    return """<!DOCTYPE html>
<html><head><title>Movie Graph Explorer</title>
<style>
body{font-family:sans-serif;background:#0f0f1a;color:#e0e0e0;margin:0}
header{background:#1a1a2e;padding:20px 32px;border-bottom:1px solid #2a2a4a}
h1{color:#00d4aa;margin:0}
.container{max-width:1100px;margin:0 auto;padding:24px 20px}
.search-box{display:flex;gap:12px;margin-bottom:24px}
input{flex:1;padding:12px 16px;border-radius:10px;border:1px solid #2a2a4a;background:#1a1a2e;color:#fff;font-size:1rem;outline:none}
button{padding:12px 24px;background:#00d4aa;color:#0f0f1a;border:none;border-radius:10px;font-weight:700;cursor:pointer}
.genre-bar{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px}
.chip{padding:6px 14px;border-radius:20px;border:1px solid #2a2a4a;background:#1a1a2e;color:#aaa;cursor:pointer;font-size:0.85rem}
.chip:hover,.chip.active{background:#00d4aa;color:#0f0f1a;border-color:#00d4aa}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px}
.card{background:#1a1a2e;border:1px solid #2a2a4a;border-radius:12px;padding:16px;cursor:pointer}
.card:hover{border-color:#00d4aa}
.card h3{color:#fff;margin:0 0 6px}
.meta{color:#888;font-size:0.8rem}
.badge{padding:2px 8px;border-radius:8px;background:#16213e;color:#00d4aa;font-size:0.75rem}
.rating{float:right;color:#ffd700}
.empty{text-align:center;padding:60px;color:#555}
.loading{text-align:center;padding:40px;color:#00d4aa}
.modal-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.7);z-index:100;align-items:center;justify-content:center}
.modal-overlay.open{display:flex}
.modal{background:#1a1a2e;border:1px solid #2a2a4a;border-radius:16px;padding:28px;max-width:580px;width:90%;max-height:80vh;overflow-y:auto;position:relative}
.modal h2{color:#00d4aa}
.close{position:absolute;top:14px;right:18px;cursor:pointer;color:#888;font-size:1.4rem}
.st{font-size:0.8rem;text-transform:uppercase;color:#00d4aa;margin:16px 0 8px}
.actor-chips{display:flex;flex-wrap:wrap;gap:6px}
.actor-chip{padding:5px 12px;border:1px solid #2a2a4a;border-radius:16px;font-size:0.82rem;cursor:pointer}
.actor-chip:hover{border-color:#00d4aa;color:#00d4aa}
</style></head>
<body>
<header><h1>🎬 Movie Graph Explorer</h1><p style="color:#888;margin:4px 0 0">Powered by CognoDB graph database</p></header>
<div class="container">
<div class="search-box">
<input id="q" placeholder="Search movies..." onkeydown="if(event.key==='Enter')search()"/>
<button onclick="search()">Search</button>
</div>
<div class="genre-bar" id="genres"></div>
<div id="results"><div class="loading">Loading...</div></div>
</div>
<div class="modal-overlay" id="overlay" onclick="if(event.target===this)close_()">
<div class="modal"><span class="close" onclick="close_()">✕</span><div id="mc"></div></div>
</div>
<script>
async function search(){
  const q=document.getElementById('q').value;
  document.getElementById('results').innerHTML='<div class="loading">Loading...</div>';
  const r=await fetch('/api/movies/search?q='+encodeURIComponent(q));
  const d=await r.json();
  renderMovies(d,q?'Results for "'+q+'"':'All Movies');
}
async function loadGenres(){
  const r=await fetch('/api/genres');
  const genres=await r.json();
  document.getElementById('genres').innerHTML=genres.map(g=>'<div class="chip" onclick="byGenre(\''+g+'\',this)">'+g+'</div>').join('');
}
async function byGenre(g,el){
  document.querySelectorAll('.chip').forEach(c=>c.classList.remove('active'));
  el.classList.add('active');
  document.getElementById('results').innerHTML='<div class="loading">Loading...</div>';
  const r=await fetch('/api/genres/'+encodeURIComponent(g));
  const d=await r.json();
  renderMovies(d,'Genre: '+g);
}
function renderMovies(movies,title){
  if(!movies.length){document.getElementById('results').innerHTML='<div class="empty">No movies found</div>';return;}
  document.getElementById('results').innerHTML='<p style="color:#888;margin-bottom:12px">'+title+' — '+movies.length+' found</p><div class="grid">'+movies.map(m=>'<div class="card" onclick="openMovie(\''+m.title.replace(/\'/g,"\\'")+'\')" ><div class="rating">⭐'+m.rating+'</div><h3>'+m.title+'</h3><p class="meta">'+m.year+'</p><span class="badge">'+(m.genre||'—')+'</span></div>').join('')+'</div>';
}
async function openMovie(title){
  document.getElementById('overlay').classList.add('open');
  document.getElementById('mc').innerHTML='<div class="loading">Loading...</div>';
  const [dr,sr]=await Promise.all([fetch('/api/movies/'+encodeURIComponent(title)),fetch('/api/movies/'+encodeURIComponent(title)+'/similar')]);
  const detail=await dr.json();const similar=await sr.json();
  document.getElementById('mc').innerHTML='<h2>'+detail.title+'</h2><p class="meta">'+detail.year+' | <span class="badge">'+detail.genre+'</span> | ⭐'+detail.rating+'</p><p class="st">Cast</p><div class="actor-chips">'+(detail.actors||[]).map(a=>'<span class="actor-chip" onclick="openActor(\''+a.replace(/\'/g,"\\'")+'\')" >'+a+'</span>').join('')+'</div><p class="st">Similar Movies</p>'+(similar.length?'<div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(160px,1fr))">'+similar.map(m=>'<div class="card" onclick="openMovie(\''+m.title.replace(/\'/g,"\\'")+'\')" ><div class="rating">⭐'+m.rating+'</div><h3>'+m.title+'</h3><p style="color:#00d4aa;font-size:0.75rem">'+m.sharedActors+' shared</p></div>').join('')+'</div>':'<p style="color:#555">None found</p>');
}
async function openActor(name){
  document.getElementById('mc').innerHTML='<div class="loading">Loading...</div>';
  const r=await fetch('/api/actors/'+encodeURIComponent(name));
  const d=await r.json();
  document.getElementById('mc').innerHTML='<h2>🎭 '+d.actor+'</h2><p class="st">Movies</p><div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(160px,1fr))">'+(d.movies||[]).map(m=>'<div class="card" onclick="openMovie(\''+m.title.replace(/\'/g,"\\'")+'\')" ><h3>'+m.title+'</h3><p class="meta">'+m.year+'</p><span class="badge">'+m.genre+'</span></div>').join('')+'</div>';
}
function close_(){document.getElementById('overlay').classList.remove('open');}
loadGenres();search();
</script></body></html>"""
