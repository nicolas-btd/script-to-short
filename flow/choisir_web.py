import json, os, sys, shutil, html, webbrowser, threading, subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8765

# Détermination des chemins
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
PIPELINE_DIR = os.path.join(PROJECT_DIR, "pipeline")
CORE_DIR = os.path.join(PROJECT_DIR, "core")

def get_render_scripts():
    timeline_s = os.path.join(CORE_DIR, "timeline.py") if os.path.exists(os.path.join(CORE_DIR, "timeline.py")) else os.path.join(PIPELINE_DIR, "build_timeline.py")
    render_s = os.path.join(CORE_DIR, "renderer.py") if os.path.exists(os.path.join(CORE_DIR, "renderer.py")) else os.path.join(PIPELINE_DIR, "render_video.py")
    return timeline_s, render_s

cfg_path = os.path.join(SCRIPT_DIR, "config.json")
cfg = json.load(open(cfg_path)) if os.path.exists(cfg_path) else {}

IMAGES_PER_PROMPT = int(cfg.get("images_per_prompt", 3))

# Répertoire vidéo cible (ex: videos/stickman2)
VIDEO_DIR = cfg.get("video_dir", "")
if VIDEO_DIR and not os.path.isabs(VIDEO_DIR):
    VIDEO_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, VIDEO_DIR))

def get_out_dir():
    out_cfg = cfg.get("out_dir", "")
    if out_cfg and os.path.isabs(out_cfg):
        return out_cfg
    if VIDEO_DIR:
        if out_cfg and not out_cfg.startswith("images_"):
            return os.path.join(VIDEO_DIR, out_cfg)
        return os.path.join(VIDEO_DIR, "images_candidates")
    return os.path.join(SCRIPT_DIR, out_cfg or "images_candidates")

# État global du rendu vidéo en arrière-plan
render_state = {
    "status": "idle",   # idle, running, done, error
    "log": "",
    "done": False,
    "file": ""
}

TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Choix des images · Montage Vidéo</title>
<style>
body{background:#18181b;color:#f4f4f5;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;margin:0}
header{position:sticky;top:0;z-index:99;background:#09090b;padding:14px 24px;display:flex;gap:18px;align-items:center;flex-wrap:wrap;border-bottom:1px solid #27272a;box-shadow:0 4px 12px rgba(0,0,0,0.5)}
header b{font-size:18px;color:#fafafa;letter-spacing:-0.5px}
#stat{font-size:14px;color:#a1a1aa;background:#27272a;padding:4px 10px;border-radius:20px}
button{font-size:15px;padding:9px 18px;border-radius:8px;border:0;cursor:pointer;font-weight:600;transition:all 0.15s ease}
#go{background:#22c55e;color:#052e16}
#go:hover{background:#16a34a}
#copy{display:none;background:#3b82f6;color:#fff}
#open_vid{display:none;background:#a855f7;color:#fff}
#res{width:100%;margin:4px 0 0;white-space:pre-wrap;font-size:14px;color:#4ade80;line-height:1.4;max-height:80px;overflow-y:auto}
#render_box{display:none;width:100%;background:#18181b;border:1px solid #3f3f46;border-radius:8px;padding:12px;margin-top:6px}
#render_bar{height:6px;width:0%;background:#a855f7;border-radius:4px;transition:width 0.3s ease;margin-top:6px}
section{padding:24px;border-bottom:1px solid #27272a}
h2{margin:0 0 14px;font-size:20px;color:#e4e4e7}
.pair{display:flex;gap:18px;align-items:center;flex-wrap:wrap}
.img-wrap{position:relative;display:inline-block}
.badge{position:absolute;top:10px;left:10px;background:rgba(0,0,0,0.75);backdrop-filter:blur(4px);color:#fff;font-size:13px;font-weight:700;padding:4px 9px;border-radius:6px;pointer-events:none;border:1px solid rgba(255,255,255,0.2);z-index:2;transition:all 0.15s ease}
.img{height:50vh;max-height:520px;border-radius:12px;cursor:pointer;outline:6px solid transparent;outline-offset:4px;transition:transform 0.15s, outline-color 0.15s;box-shadow:0 6px 16px rgba(0,0,0,0.4);display:block}
.img:hover{outline-color:#71717a;transform:scale(1.01)}
.miss{width:28vh;max-width:290px;height:50vh;max-height:520px;display:flex;align-items:center;justify-content:center;background:#27272a;color:#ef4444;border:2px dashed #7f1d1d;cursor:default;text-align:center;font-weight:600;border-radius:12px}
section[data-choice="1"] .img[data-n="1"],
section[data-choice="2"] .img[data-n="2"],
section[data-choice="3"] .img[data-n="3"],
section[data-choice="4"] .img[data-n="4"]{outline-color:#22c55e;transform:scale(1.01)}
section[data-choice="1"] .img-wrap:has(.img[data-n="1"]) .badge,
section[data-choice="2"] .img-wrap:has(.img[data-n="2"]) .badge,
section[data-choice="3"] .img-wrap:has(.img[data-n="3"]) .badge{background:#22c55e;color:#052e16}
section[data-choice="x"]{background:#2a1215}
.redo{background:#27272a;color:#d4d4d8}
.redo:hover{background:#3f3f46}
section[data-choice="x"] .redo{background:#ef4444;color:#fff}
details{margin-top:10px;color:#71717a;font-size:13px;max-width:900px}
summary{cursor:pointer;color:#a1a1aa}
</style></head><body>
<header>
  <b>Dossier : __OUT__</b>
  <span id="stat"></span>
  <span style="font-size:13px;color:#71717a;margin-left:auto">Touches 1, 2, 3 ou clic · X pour refaire</span>
  <button id="go" onclick="finish()">✅ Valider et lancer le montage</button>
  <button id="copy">📋 Copier la commande</button>
  <button id="open_vid" onclick="openVideo()">▶️ Ouvrir la vidéo finale</button>
  <div id="render_box">
    <div id="render_text" style="font-size:14px;font-weight:600;color:#c084fc"></div>
    <div id="render_bar"></div>
  </div>
  <pre id="res"></pre>
</header>
__ROWS__
<script>
function send(id, v, jump){
  const s = document.getElementById('p' + id);
  s.dataset.choice = v;
  fetch('/choose', {method: 'POST', body: JSON.stringify({id: id, v: v})});
  count();
  const n = s.nextElementSibling;
  if (jump && n && n.tagName === 'SECTION') n.scrollIntoView({behavior: 'smooth', block: 'start'});
}
function pick(img){ send(img.dataset.id, img.dataset.n, true); }
function redo(id){
  const s = document.getElementById('p' + id);
  send(id, s.dataset.choice === 'x' ? '1' : 'x', false);
}
function count(){
  const all = document.querySelectorAll('section');
  let x = 0;
  all.forEach(s => { if (s.dataset.choice === 'x') x++; });
  document.getElementById('stat').textContent = all.length + ' plans · ' + x + ' à refaire';
}

let pollTimer = null;
async function finish(){
  document.getElementById('go').disabled = true;
  document.getElementById('go').textContent = '⏳ Traitement...';
  const r = await fetch('/finish', {method: 'POST'});
  const d = await r.json();
  document.getElementById('res').textContent = d.msg;
  const b = document.getElementById('copy');
  if (d.cmd) {
    b.style.display = 'inline-block';
    b.textContent = '📋 Copier la commande';
    b.onclick = () => { navigator.clipboard.writeText(d.cmd); b.textContent = 'Copié ✓'; };
  } else { b.style.display = 'none'; }

  if (d.render_started) {
    document.getElementById('render_box').style.display = 'block';
    if (!pollTimer) pollTimer = setInterval(pollRender, 1000);
  } else {
    document.getElementById('go').disabled = false;
    document.getElementById('go').textContent = '✅ Valider et lancer le montage';
  }
}

async function pollRender(){
  try {
    const r = await fetch('/render_status');
    const d = await r.json();
    const box = document.getElementById('render_box');
    const text = document.getElementById('render_text');
    const bar = document.getElementById('render_bar');
    const openBtn = document.getElementById('open_vid');

    if (d.status === 'running') {
      box.style.display = 'block';
      text.textContent = '🎬 ' + (d.log || 'Montage en cours...');
      const match = d.log.match(/\\((\\d+\\.\\d+)%\\)/);
      if (match) bar.style.width = match[1] + '%';
    } else if (d.status === 'done') {
      clearInterval(pollTimer);
      pollTimer = null;
      box.style.display = 'block';
      bar.style.width = '100%';
      bar.style.background = '#22c55e';
      text.style.color = '#4ade80';
      text.textContent = '🎉 ' + d.log;
      openBtn.style.display = 'inline-block';
      document.getElementById('go').disabled = false;
      document.getElementById('go').textContent = '✅ Montage terminé !';
    } else if (d.status === 'error') {
      clearInterval(pollTimer);
      pollTimer = null;
      text.style.color = '#ef4444';
      text.textContent = '❌ ' + d.log;
      document.getElementById('go').disabled = false;
      document.getElementById('go').textContent = '⚠️ Réessayer';
    }
  } catch(e) {}
}

async function openVideo(){
  await fetch('/open_video', {method: 'POST'});
}

count();

window.addEventListener('keydown', (e) => {
  if (['1', '2', '3', '4', '&', 'é', '"', "'"].includes(e.key)) {
    let n = e.key;
    if (e.key === '&') n = '1';
    if (e.key === 'é') n = '2';
    if (e.key === '"') n = '3';
    if (e.key === "'") n = '4';
    const sections = Array.from(document.querySelectorAll('section'));
    const mid = window.innerHeight / 2;
    const current = sections.find(s => {
      const r = s.getBoundingClientRect();
      return r.top <= mid && r.bottom >= mid;
    }) || sections[0];
    if (current) {
      const id = current.id.replace('p', '');
      send(id, n, true);
    }
  } else if (e.key === 'x' || e.key === 'X') {
    const sections = Array.from(document.querySelectorAll('section'));
    const mid = window.innerHeight / 2;
    const current = sections.find(s => {
      const r = s.getBoundingClientRect();
      return r.top <= mid && r.bottom >= mid;
    }) || sections[0];
    if (current) {
      const id = current.id.replace('p', '');
      redo(id);
    }
  }
});
</script></body></html>"""

def get_save_path():
    if VIDEO_DIR and os.path.isdir(VIDEO_DIR):
        return os.path.join(VIDEO_DIR, "choix_images.json")
    out_dir = get_out_dir()
    return os.path.join(out_dir, "choix_images.json")

def load_plans():
    p_file = (
        os.path.join(VIDEO_DIR, "prompts.jsonl")
        if VIDEO_DIR and os.path.exists(os.path.join(VIDEO_DIR, "prompts.jsonl"))
        else (
            cfg.get("prompts_file")
            if cfg.get("prompts_file") and os.path.exists(cfg.get("prompts_file"))
            else os.path.join(SCRIPT_DIR, "prompts.jsonl")
        )
    )
    if not os.path.exists(p_file):
        return []
    plans = (json.loads(l) for l in open(p_file) if l.strip())
    return sorted(plans, key=lambda p: p.get("id"))

def load_choix():
    save_path = get_save_path()
    if os.path.exists(save_path):
        return json.load(open(save_path))
    if VIDEO_DIR:
        legacy_v = os.path.join(VIDEO_DIR, "choix.json")
        if os.path.exists(legacy_v):
            return json.load(open(legacy_v))
    return {}

def default_choice(i):
    out_dir = get_out_dir()
    for n in range(1, IMAGES_PER_PROMPT + 1):
        if os.path.exists(os.path.join(out_dir, f"{i}_{n}.jpg")):
            return str(n)
    return "x"

def img_tag(i, n):
    out_dir = get_out_dir()
    f_name = f"{i}_{n}.jpg"
    full_path = os.path.join(out_dir, f_name)
    if not os.path.exists(full_path):
        return f'<div class="img-wrap"><span class="badge">#{n}</span><div class="img miss">{i}_{n}<br>manquante</div></div>'
    t = int(os.path.getmtime(full_path))
    return f'<div class="img-wrap"><span class="badge">#{n}</span><img class="img" src="/candidate_img/{f_name}?t={t}" data-id="{i}" data-n="{n}" title="Option {n} (clic ou touche {n})" onclick="pick(this)"></div>'

def page():
    choix = load_choix()
    out_dir = get_out_dir()
    rows = list()
    for p in load_plans():
        i = p.get("id")
        c = choix.get(str(i)) or default_choice(i)
        a = html.escape(p.get("anchor", ""))
        s = html.escape(p.get("scene", ""))
        existing_n = [n for n in range(1, IMAGES_PER_PROMPT + 1) if os.path.exists(os.path.join(out_dir, f"{i}_{n}.jpg"))]
        if existing_n:
            imgs_html = "".join(img_tag(i, n) for n in existing_n)
        else:
            imgs_html = f'<div class="img miss">Plan {i}<br>aucune image</div>'
        rows.append(
            f'<section id="p{i}" data-choice="{c}"><h2>{i} · « {a} »</h2>'
            f'<div class="pair">{imgs_html}'
            f'<button class="redo" onclick="redo({i})">✗ À refaire</button></div>'
            f'<details><summary>scène</summary>{s}</details></section>'
        )
    return TEMPLATE.replace("__ROWS__", "".join(rows)).replace("__OUT__", os.path.basename(out_dir))

def render_worker(video_dir):
    global render_state
    render_state["status"] = "running"
    render_state["log"] = "Calage de la timeline en cours..."
    render_state["done"] = False

    try:
        t_script, r_script = get_render_scripts()
        # 1. Timeline
        cmd1 = [sys.executable, t_script, video_dir]
        subprocess.run(cmd1, check=True)

        # 2. Rendu vidéo
        render_state["log"] = "Démarrage du moteur de rendu vidéo..."
        cmd2 = [sys.executable, r_script, video_dir]
        proc = subprocess.Popen(cmd2, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        for line in proc.stdout:
            line_str = line.strip()
            if "Rendu image" in line_str:
                render_state["log"] = line_str
            elif "Audio mixé" in line_str:
                render_state["log"] = "🔊 Audio et bruitages mixés"
            elif "Chargement" in line_str:
                render_state["log"] = line_str

        proc.wait()
        if proc.returncode == 0:
            final_mp4 = os.path.join(video_dir, "video_finale.mp4")
            render_state["status"] = "done"
            render_state["done"] = True
            render_state["file"] = final_mp4
            render_state["log"] = f"Vidéo finale prête : {os.path.basename(final_mp4)}"
        else:
            render_state["status"] = "error"
            render_state["log"] = f"Erreur de rendu vidéo (code {proc.returncode})"
    except Exception as e:
        render_state["status"] = "error"
        render_state["log"] = f"Erreur : {e}"

def finish():
    choix = load_choix()
    out_dir = get_out_dir()
    if VIDEO_DIR:
        os.makedirs(VIDEO_DIR, exist_ok=True)
    else:
        final_dir = os.path.join(SCRIPT_DIR, f"{os.path.basename(out_dir)}_final")
        os.makedirs(final_dir, exist_ok=True)

    ok, refaire = 0, list()
    for p in load_plans():
        i = p.get("id")
        c = choix.get(str(i)) or default_choice(i)
        src = os.path.join(out_dir, f"{i}_{c}.jpg")
        if c == "x" or not os.path.exists(src):
            refaire.append(i)
            if VIDEO_DIR:
                video_dst = os.path.join(VIDEO_DIR, f"{i:02d}.jpg")
                if os.path.exists(video_dst):
                    os.remove(video_dst)
            continue
        if VIDEO_DIR:
            video_dst = os.path.join(VIDEO_DIR, f"{i:02d}.jpg")
            shutil.copy2(src, video_dst)
        else:
            final_dst = os.path.join(final_dir, f"{i}.jpg")
            shutil.copy2(src, final_dst)
        ok += 1

    if VIDEO_DIR:
        msg = f"✅ {ok} images copiées dans {os.path.basename(VIDEO_DIR)}/"
    else:
        msg = f"✅ {ok} images copiées dans {os.path.basename(final_dir)}/"

    cmd = ""
    render_started = False
    if refaire:
        ids = " ".join(str(i) for i in refaire)
        rm_files = [os.path.join(out_dir, f"{i}_{n}.jpg") for i in refaire for n in range(1, IMAGES_PER_PROMPT + 1)]
        rm = " ".join(f'"{f}"' for f in rm_files)
        cmd = f"rm -f {rm} && python flow_fast.py {ids}"
        msg += f"\n❌ À refaire : {ids}\n{cmd}"
    else:
        if VIDEO_DIR:
            msg += "\n🎬 Lancement automatique du montage de la vidéo finale..."
            render_started = True
            t = threading.Thread(target=render_worker, args=(VIDEO_DIR,), daemon=True)
            t.start()

    return json.dumps({
        "msg": msg,
        "cmd": cmd,
        "render_started": render_started
    }, ensure_ascii=False)

class H(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SCRIPT_DIR, **kwargs)

    def log_message(self, *a):
        pass

    def reply(self, txt, ctype):
        b = txt.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self.reply(page(), "text/html")
        if self.path == "/render_status":
            return self.reply(json.dumps(render_state, ensure_ascii=False), "application/json")
        if self.path.startswith("/candidate_img/"):
            img_name = self.path.split("/candidate_img/", 1)[1].split("?")[0]
            img_name = os.path.basename(img_name)
            img_path = os.path.join(get_out_dir(), img_name)
            if os.path.exists(img_path):
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Length", str(os.path.getsize(img_path)))
                self.end_headers()
                with open(img_path, "rb") as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_error(404, "Image introuvable")
                return
        return super().do_GET()

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n) if n else b"{}"
        if self.path == "/choose":
            d = json.loads(body)
            c = load_choix()
            c[str(d.get("id"))] = str(d.get("v"))
            save_path = get_save_path()
            json.dump(c, open(save_path, "w"), indent=2)
            return self.reply("ok", "text/plain")
        if self.path == "/finish":
            return self.reply(finish(), "application/json")
        if self.path == "/open_video":
            if render_state.get("file") and os.path.exists(render_state["file"]):
                subprocess.run(["open", render_state["file"]])
            return self.reply("ok", "text/plain")
        self.send_error(404)

def start_server(video_dir=None):
    global VIDEO_DIR
    if video_dir:
        VIDEO_DIR = os.path.abspath(video_dir)

    server = None
    actual_port = PORT
    for p in range(PORT, PORT + 10):
        try:
            class ReusableServer(HTTPServer):
                allow_reuse_address = True
            server = ReusableServer(("127.0.0.1", p), H)
            actual_port = p
            break
        except OSError:
            continue
    if not server:
        raise OSError(f"Impossible de lier le serveur web sur les ports {PORT} à {PORT + 10}")

    url = f"http://localhost:{actual_port}/"
    out_dir = get_out_dir()
    print("==================================================")
    print("CHOIX DES IMAGES & MONTAGE VIDEO")
    print(f"Images candidates : {out_dir}")
    if VIDEO_DIR:
        print(f"Video cible : {VIDEO_DIR}")
    print(f"Sauvegarde : {get_save_path()}")
    print(f"Interface web : {url}")
    print("==================================================")

    def _open():
        try:
            if sys.platform == "darwin":
                subprocess.Popen(["open", url])
            else:
                webbrowser.open(url)
        except Exception:
            webbrowser.open(url)

    threading.Timer(0.8, _open).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nArrete. Choix sauvegardes dans", get_save_path())

if __name__ == "__main__":
    candidate = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else None
    start_server(candidate)
