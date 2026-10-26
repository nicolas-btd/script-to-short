import html
import json
import os
import shutil
import subprocess
import sys
import threading
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from core.timeline import build_timeline
from core.renderer import render_video
from core.utils import get_project_root, log_step

PORT = 8765
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent

VIDEO_DIR = None
IMAGES_PER_PROMPT = 3

render_state = {
    "status": "idle",
    "log": "",
    "done": False,
    "file": ""
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Scene Selection and Video Render</title>
<style>
body { background: #121214; color: #f4f4f5; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; }
header { position: sticky; top: 0; z-index: 99; background: #0c0c0e; padding: 14px 24px; display: flex; gap: 16px; align-items: center; flex-wrap: wrap; border-bottom: 1px solid #27272a; }
header h1 { font-size: 17px; margin: 0; font-weight: 600; color: #fff; }
#stat { font-size: 13px; color: #a1a1aa; background: #27272a; padding: 4px 10px; border-radius: 12px; }
button { font-size: 14px; padding: 8px 16px; border-radius: 6px; border: 0; cursor: pointer; font-weight: 500; transition: background 0.15s; }
#go { background: #10b981; color: #022c22; font-weight: 600; }
#go:hover { background: #059669; }
#open_vid { display: none; background: #6366f1; color: #fff; font-weight: 600; }
#open_vid:hover { background: #4f46e5; }
#render_box { display: none; width: 100%; background: #18181b; border: 1px solid #3f3f46; border-radius: 6px; padding: 10px; margin-top: 6px; }
#render_log { font-family: monospace; font-size: 12px; color: #34d399; }
section { padding: 20px 24px; border-bottom: 1px solid #27272a; }
h2 { margin: 0 0 12px; font-size: 16px; font-weight: 500; color: #e4e4e7; }
.pair { display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }
.img-wrap { position: relative; display: inline-block; }
.badge { position: absolute; top: 8px; left: 8px; background: rgba(0,0,0,0.7); color: #fff; font-size: 12px; font-weight: 600; padding: 3px 8px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.2); pointer-events: none; }
.img { height: 48vh; max-height: 480px; border-radius: 8px; cursor: pointer; outline: 4px solid transparent; outline-offset: 2px; transition: outline-color 0.15s; display: block; }
.img:hover { outline-color: #71717a; }
.img-wrap.chosen .img { outline-color: #10b981; }
.redo { background: #27272a; color: #f87171; font-size: 13px; padding: 6px 12px; }
.redo:hover { background: #3f3f46; }
section.rejected { opacity: 0.45; }
details { margin-top: 8px; font-size: 13px; color: #a1a1aa; }
summary { cursor: pointer; }
</style>
</head>
<body>
<header>
  <h1>Scene Review</h1>
  <span id="stat">Loading...</span>
  <button id="go" onclick="finish()">Confirm and Render Video</button>
  <button id="open_vid" onclick="openVideo()">Open Final Video</button>
  <div id="render_box">
    <div id="render_log">Waiting...</div>
  </div>
</header>
<main id="container">
  __ROWS__
</main>
<script>
let state = {};

function init() {
  document.querySelectorAll('section').forEach(sec => {
    const id = sec.id.replace('p', '');
    const c = sec.getAttribute('data-choice');
    if (c) state[id] = c;
    updateUI(id);
  });
  updateStat();
}

function choose(id, v) {
  state[id] = v;
  fetch('/choose', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id, v})
  });
  updateUI(id);
  updateStat();
}

function redo(id) {
  choose(id, 'x');
}

function updateUI(id) {
  const sec = document.getElementById('p' + id);
  if (!sec) return;
  const c = state[id];
  sec.classList.toggle('rejected', c === 'x');
  sec.querySelectorAll('.img-wrap').forEach(w => {
    const v = w.getAttribute('data-v');
    w.classList.toggle('chosen', v === c);
  });
}

function updateStat() {
  const total = document.querySelectorAll('section').length;
  const chosen = Object.values(state).filter(x => x && x !== 'x').length;
  document.getElementById('stat').textContent = chosen + ' / ' + total + ' selected';
}

function finish() {
  const btn = document.getElementById('go');
  btn.disabled = true;
  btn.textContent = 'Processing...';
  document.getElementById('render_box').style.display = 'block';

  fetch('/finish', {method: 'POST'})
    .then(r => r.json())
    .then(d => {
      pollStatus();
    });
}

function pollStatus() {
  const logEl = document.getElementById('render_log');
  const timer = setInterval(() => {
    fetch('/render_status')
      .then(r => r.json())
      .then(s => {
        logEl.textContent = s.log || s.status;
        if (s.done) {
          clearInterval(timer);
          document.getElementById('go').style.display = 'none';
          document.getElementById('open_vid').style.display = 'inline-block';
        } else if (s.status === 'error') {
          clearInterval(timer);
          logEl.style.color = '#f87171';
        }
      });
  }, 1000);
}

function openVideo() {
  fetch('/open_video', {method: 'POST'});
}

window.addEventListener('keydown', e => {
  if (['1','2','3','4'].includes(e.key)) {
    const secs = Array.from(document.querySelectorAll('section'));
    const scrollY = window.scrollY + 120;
    const cur = secs.find(s => s.offsetTop + s.offsetHeight > scrollY) || secs[0];
    if (cur) {
      const id = cur.id.replace('p', '');
      choose(id, e.key);
    }
  } else if (e.key === 'x' || e.key === 'X') {
    const secs = Array.from(document.querySelectorAll('section'));
    const scrollY = window.scrollY + 120;
    const cur = secs.find(s => s.offsetTop + s.offsetHeight > scrollY) || secs[0];
    if (cur) redo(cur.id.replace('p', ''));
  }
});

init();
</script>
</body>
</html>
"""


def get_out_dir() -> Path:
    if VIDEO_DIR:
        return Path(VIDEO_DIR) / "images_candidates"
    return SCRIPT_DIR / "images_candidates"


def get_save_path() -> Path:
    if VIDEO_DIR:
        return Path(VIDEO_DIR) / "choix_images.json"
    return SCRIPT_DIR / "choix_images.json"


def load_choix() -> dict:
    p = get_save_path()
    if p.is_file():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def load_plans() -> list:
    if VIDEO_DIR:
        cand = Path(VIDEO_DIR) / "prompts.json"
        if cand.is_file():
            try:
                return json.loads(cand.read_text(encoding="utf-8"))
            except Exception:
                pass
    return []


def render_worker(video_dir: str):
    global render_state
    render_state["status"] = "running"
    render_state["log"] = "Synchronizing timeline..."
    render_state["done"] = False

    try:
        build_timeline(video_dir)
        render_state["log"] = "Rendering video frames..."
        final_mp4 = render_video(video_dir)
        render_state["status"] = "done"
        render_state["done"] = True
        render_state["file"] = final_mp4
        render_state["log"] = f"Video complete: {Path(final_mp4).name}"
    except Exception as e:
        render_state["status"] = "error"
        render_state["log"] = f"Render error: {e}"


def finish_selection() -> dict:
    choix = load_choix()
    out_dir = get_out_dir()
    v_dir = Path(VIDEO_DIR) if VIDEO_DIR else None

    ok = 0
    refaire = []
    for p in load_plans():
        i = p.get("id")
        c = choix.get(str(i), "1")
        src = out_dir / f"{i}_{c}.jpg"
        if c == "x" or not src.is_file():
            refaire.append(i)
            if v_dir:
                dst = v_dir / f"{i:02d}.jpg"
                if dst.is_file():
                    dst.unlink()
            continue

        if v_dir:
            dst = v_dir / f"{i:02d}.jpg"
            shutil.copy2(src, dst)
        ok += 1

    render_started = False
    if not refaire and v_dir:
        render_started = True
        t = threading.Thread(target=render_worker, args=(str(v_dir),), daemon=True)
        t.start()

    return {
        "ok": ok,
        "refaire": refaire,
        "render_started": render_started
    }


def build_page() -> str:
    plans = load_plans()
    out_dir = get_out_dir()
    choix = load_choix()
    rows = []

    for p in plans:
        i = p.get("id")
        anchor = html.escape(p.get("anchor", ""))
        scene = html.escape(p.get("scene", p.get("raw_scene", "")))
        selected = choix.get(str(i), "1")

        imgs_html = []
        for n in range(1, IMAGES_PER_PROMPT + 1):
            img_file = out_dir / f"{i}_{n}.jpg"
            if img_file.is_file():
                imgs_html.append(
                    f'<div class="img-wrap" data-v="{n}">'
                    f'<span class="badge">Version {n}</span>'
                    f'<img class="img" src="/candidate_img/{img_file.name}" onclick="choose({i}, \'{n}\')">'
                    f'</div>'
                )

        rows.append(
            f'<section id="p{i}" data-choice="{selected}">'
            f'<h2>Scene {i} - "{anchor}"</h2>'
            f'<div class="pair">{"".join(imgs_html)}'
            f'<button class="redo" onclick="redo({i})">Reject</button>'
            f'</div>'
            f'<details><summary>Prompt details</summary>{scene}</details>'
            f'</section>'
        )

    return HTML_TEMPLATE.replace("__ROWS__", "\n".join(rows))


class WebHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def reply(self, txt: str, ctype: str):
        b = txt.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", f"{ctype}; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self.reply(build_page(), "text/html")
        if self.path == "/render_status":
            return self.reply(json.dumps(render_state, ensure_ascii=False), "application/json")
        if self.path.startswith("/candidate_img/"):
            img_name = self.path.split("/candidate_img/", 1)[1].split("?")[0]
            img_name = Path(img_name).name
            img_path = get_out_dir() / img_name
            if img_path.is_file():
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Length", str(img_path.stat().st_size))
                self.end_headers()
                self.wfile.write(img_path.read_bytes())
                return
            self.send_error(404, "Image not found")
            return
        return super().do_GET()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b"{}"

        if self.path == "/choose":
            data = json.loads(body)
            c = load_choix()
            c[str(data.get("id"))] = str(data.get("v"))
            get_save_path().write_text(json.dumps(c, indent=2), encoding="utf-8")
            return self.reply("ok", "text/plain")

        if self.path == "/finish":
            res = finish_selection()
            return self.reply(json.dumps(res), "application/json")

        if self.path == "/open_video":
            f = render_state.get("file")
            if f and os.path.exists(f):
                if sys.platform == "darwin":
                    subprocess.run(["open", f])
                elif sys.platform.startswith("linux"):
                    subprocess.run(["xdg-open", f])
                elif sys.platform in ("win32", "cygwin"):
                    os.startfile(f)
            return self.reply("ok", "text/plain")

        self.send_error(404)


def start_server(video_dir: str):
    global VIDEO_DIR
    VIDEO_DIR = str(Path(video_dir).resolve())

    class ReusableServer(HTTPServer):
        allow_reuse_address = True

    server = None
    actual_port = PORT
    for p in range(PORT, PORT + 20):
        try:
            server = ReusableServer(("127.0.0.1", p), WebHandler)
            actual_port = p
            break
        except OSError:
            continue

    if not server:
        raise OSError(f"Could not bind web interface to any port between {PORT} and {PORT + 20}")

    url = f"http://localhost:{actual_port}/"
    log_step("SERVER", f"Candidate images directory: {get_out_dir()}")
    log_step("SERVER", f"Target video directory: {VIDEO_DIR}")
    log_step("SERVER", f"Web interface running at {url}")

    threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log_step("SERVER", "Server stopped.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m flow.choisir_web <video_dir>")
        sys.exit(1)
    start_server(sys.argv[1])
