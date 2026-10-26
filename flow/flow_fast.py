import difflib
import json
import os
import re
import shutil
import sys
import time
from itertools import islice
from pathlib import Path

from playwright.sync_api import sync_playwright

from . import flow_auto as fa

CFG, S = fa.CFG, fa.S
MAXP = int(CFG.get("max_parallel", 2))
GAP = float(CFG.get("launch_gap_s", 2))
TIMEOUT = float(CFG.get("gen_timeout_s", 180))
MAXF = int(CFG.get("max_failures", 3))
RPC = CFG.get("gen_rpc", "ogiZ0b")
IMG_PREFIX = "https://flow-content.google/image/"
GEN = []


def norm(t: str) -> str:
    return re.sub(r"\s+", " ", t or "").strip().lower()


def pkey(p: dict) -> str:
    k = norm(p.get("prompt", ""))
    return k[-120:] if k else k


def img_id(url: str) -> str:
    m = re.search(r"/image/([^?]+)", url)
    return m.group(1) if m else url


def done(out: Path, i: int) -> bool:
    num_img = int(CFG.get("images_per_prompt", 3))
    return all(any(out.glob(f"{i}_{n}.*")) for n in range(1, num_img + 1))


def dep_ids(p: dict) -> list:
    return [int(str(r)[1:]) for r in p.get("refs", []) if str(r).startswith("@")]


def strings(o, acc):
    if isinstance(o, str):
        acc.append(o)
    elif isinstance(o, list):
        for x in o:
            strings(x, acc)
    return acc


def parse_gen(body: str) -> list:
    res = []
    for line in body.splitlines():
        if "wrb.fr" not in line or RPC not in line:
            continue
        try:
            outer = json.loads(line)
        except Exception:
            continue
        for it in outer:
            if not (isinstance(it, list) and len(it) > 2 and it[1] == RPC and isinstance(it[2], str)):
                continue
            inner = json.loads(it[2])
            medias = inner[0] if inner and isinstance(inner[0], list) else []
            for m in medias:
                ss = strings(m, [])
                urls = [s for s in ss if s.startswith(IMG_PREFIX)]
                if urls:
                    res.append((ss, urls[0]))
    return res


def get_paths(target_dir: str = None):
    v_dir = target_dir or CFG.get("video_dir", "")
    p_file = CFG.get("prompts_file", "prompts.json")
    if not os.path.isabs(p_file) and v_dir:
        cand = Path(v_dir) / p_file
        if cand.is_file():
            p_file = str(cand)
    out_cfg = CFG.get("out_dir", "")
    if out_cfg and os.path.isabs(out_cfg):
        out = Path(out_cfg)
    elif v_dir:
        out = Path(v_dir) / "images_candidates"
    else:
        out = Path(out_cfg or "images_candidates")
    return Path(p_file), out


def launch(page, p: dict, refs: list):
    fa.clear_chips(page)
    fa.type_prompt(page, p.get("prompt", ""))
    fa.attach_refs(page, refs)
    gen = page.locator(S["generate_button"])
    if not gen.is_enabled():
        raise RuntimeError("Generate button is disabled.")
    gen.click()


def download(page, url: str, path: Path):
    err = None
    for attempt in range(4):
        try:
            r = page.context.request.get(url, timeout=30000)
            if r.ok:
                path.write_bytes(r.body())
                return
            err = f"HTTP {r.status}"
        except Exception as e:
            err = str(e).splitlines()[0]
        fa.log(f"Download retry {attempt + 1}/3 ({err[:60]})")
        page.wait_for_timeout(2000 * (attempt + 1))
    raise RuntimeError(f"Download failed: {err}")


def run_generation(target_dir: str = None, only_ids: list = None):
    prompts_path, out = get_paths(target_dir)
    if not prompts_path.is_file():
        raise FileNotFoundError(f"Missing prompts file: {prompts_path}")

    prompts = json.loads(prompts_path.read_text(encoding="utf-8"))
    out.mkdir(parents=True, exist_ok=True)

    only_set = set(map(str, only_ids)) if only_ids else set()
    todo = [
        p for p in prompts
        if (not only_set or str(p.get("id")) in only_set) and not done(out, p.get("id"))
    ]
    todo = list(islice(todo, int(CFG.get("max_per_run", 100))))

    if not todo:
        fa.log(f"All images already exist in {out}")
        return

    total = len(todo)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(CFG["cdp_url"])
        page = fa.flow_page(browser)
        page.bring_to_front()
        page.on("response", lambda r: GEN.append(r) if ("rpcids=" + RPC) in r.url else None)

        lib = sorted({str(r) for p in todo for r in p.get("refs", []) if not str(r).startswith("@")})
        if lib:
            miss = fa.missing_refs(page, lib)
            if miss:
                raise RuntimeError("Missing reference items in Flow project: " + ", ".join(miss))
        fa.log(f"{total} scene(s) to generate ({MAXP} parallel workers).")

        queue, flying, seen, failed = list(todo), {}, set(), []
        fails, ok, last, t_start = 0, 0, 0.0, time.time()

        while queue or flying:
            while GEN:
                r = GEN.pop(0)
                try:
                    found = parse_gen(r.text())
                except Exception:
                    continue
                got, orphans = {}, []
                for ss, url in found:
                    iid = img_id(url)
                    if iid in seen:
                        continue
                    best_pid, best_score = None, 0.0
                    for pid, v in flying.items():
                        p_norm = norm(v[0].get("prompt", ""))
                        for s in ss:
                            s_norm = norm(s)
                            if not s_norm:
                                continue
                            if s_norm == p_norm or s_norm in p_norm or p_norm in s_norm:
                                score = 1.0
                            else:
                                score = difflib.SequenceMatcher(None, p_norm, s_norm).ratio()
                            if score > best_score:
                                best_score = score
                                best_pid = pid
                    owner = best_pid if best_score >= 0.75 else None
                    if owner is None:
                        orphans.append(url)
                    else:
                        got.setdefault(owner, []).append(url)

                if orphans and not got and len(flying) == 1:
                    got[next(iter(flying))] = orphans

                for pid, urls in got.items():
                    p, _, t0 = flying.pop(pid)
                    try:
                        paths = []
                        num_img = int(CFG.get("images_per_prompt", 3))
                        for n, u in enumerate(urls[:num_img], 1):
                            f = out / f"{pid}_{n}.jpg"
                            download(page, u, f)
                            paths.append(f)
                        ok += 1
                        fails = 0
                        fa.log(f"Scene {pid} completed in {time.time() - t0:.1f}s ({len(paths)} images).")
                    except Exception as e:
                        failed.append(pid)
                        fa.log(f"Error downloading scene {pid}: {e}")

            now = time.time()
            for pid in list(flying):
                if now - flying[pid][2] > TIMEOUT:
                    flying.pop(pid)
                    failed.append(pid)
                    fails += 1
                    fa.log(f"Scene {pid} timed out after {TIMEOUT:.0f}s.")

            if fa.captcha_visible(page):
                raise RuntimeError("Captcha detected in Chrome. Please solve it and restart.")

            if fails >= MAXF and queue:
                fa.log(f"Stopped new submissions after {fails} consecutive failures.")
                failed.extend(q.get("id") for q in queue)
                queue.clear()

            if queue and len(flying) < MAXP and now - last >= GAP:
                p = next((q for q in queue if all(done(out, d) for d in dep_ids(q))), None)
                if p is None and not flying:
                    fa.log("Blocked scenes (missing dependency): " + " ".join(str(q.get("id")) for q in queue))
                    failed.extend(q.get("id") for q in queue)
                    queue.clear()
                elif p is not None:
                    queue.remove(p)
                    pid = p.get("id")
                    try:
                        refs = p.get("refs", [])
                        launch(page, p, refs)
                        flying[pid] = (p, pkey(p), time.time())
                        fa.log(f"Submitted scene {pid} ({total - len(queue)}/{total}) | active: {len(flying)}")
                    except Exception as e:
                        fails += 1
                        failed.append(pid)
                        fa.log(f"Error submitting scene {pid}: {e}")
                    last = time.time()
            page.wait_for_timeout(400)

        dt = time.time() - t_start
        fa.log(f"Generation completed: {ok}/{total} scenes finished in {dt / 60:.1f} min.")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].isdigit() else None
    ids = [int(x) for x in sys.argv[1:] if x.isdigit()]
    run_generation(target, ids)
