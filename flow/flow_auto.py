import base64
import json
import os
import random
import re
import sys
import time
from pathlib import Path

DEFAULT_SELECTORS = {
    "prompt_box": "div[role=\"textbox\"][aria-label^=\"Que voulez-vous\"]",
    "add_refs_button": "button[aria-label=\"Ajouter des ingrédients au champ du prompt\"]",
    "refs_search": "input[aria-label=\"Rechercher des éléments\"]",
    "ref_option": "button[role=\"option\"]",
    "add_refs_confirm": "button:has-text(\"au prompt\")",
    "generate_button": "button[aria-label=\"Lancer la génération\"]",
    "ref_chip": "button[aria-label=\"Ingrédient\"]"
}

DEFAULT_CFG = {
    "cdp_url": "http://127.0.0.1:9222",
    "prompts_file": "prompts.json",
    "out_dir": "images_candidates",
    "images_per_prompt": 3,
    "gen_timeout_s": 150,
    "pause_min_s": 3,
    "pause_max_s": 6,
    "max_per_run": 100,
    "max_failures": 3,
    "max_parallel": 2,
    "launch_gap_s": 2,
    "gen_rpc": "ogiZ0b",
    "selectors": DEFAULT_SELECTORS
}


def load_config(config_path: str = None) -> dict:
    cfg = dict(DEFAULT_CFG)
    candidates = []
    if config_path:
        candidates.append(Path(config_path))
    candidates.append(Path.cwd() / "config.json")
    candidates.append(Path(__file__).parent / "config.json")

    for cand in candidates:
        if cand.is_file():
            try:
                user_cfg = json.loads(cand.read_text(encoding="utf-8"))
                for k, v in user_cfg.items():
                    if isinstance(v, dict) and k in cfg and isinstance(cfg[k], dict):
                        cfg[k].update(v)
                    else:
                        cfg[k] = v
                break
            except Exception:
                pass
    return cfg


CFG = load_config()
S = CFG["selectors"]
RESP = []


def log(msg: str):
    print(f"[{time.strftime('%H:%M:%S')}] [FLOW] {msg}", flush=True)


def flow_page(browser):
    candidates = []
    for ctx in browser.contexts:
        for p in ctx.pages:
            if "flow" in p.url and "google" in p.url:
                candidates.append(p)
    if not candidates:
        raise RuntimeError("No Google Flow tab found. Open your Flow project in Chrome (port 9222) and retry.")

    for p in reversed(candidates):
        try:
            if "/project/" in p.url and p.evaluate("() => document.visibilityState") == "visible":
                return p
        except Exception:
            pass

    for p in reversed(candidates):
        try:
            if p.evaluate("() => document.visibilityState") == "visible":
                return p
        except Exception:
            pass

    for p in reversed(candidates):
        if "/project/" in p.url:
            return p

    return candidates[-1]


def ref_pattern(name: str):
    return re.compile(r"(^|\s)" + re.escape(name) + r"(\.(jpe?g|png|webp|gif|heic|heif))?(?=\s|Image|$)", re.I)


def find_ref_file(name: str, target_dir: str = None) -> Path:
    exts = (".jpg", ".png", ".webp", ".jpeg", ".gif")
    candidates = []

    if target_dir:
        td = Path(target_dir).resolve()
        for ext in exts:
            candidates.append(td / "refs" / f"{name}{ext}")
            candidates.append(td / f"{name}{ext}")

    flow_dir = Path(__file__).resolve().parent
    for ext in exts:
        candidates.append(flow_dir / "refs" / f"{name}{ext}")

    repo_root = flow_dir.parent
    accounts_dir = repo_root / "accounts"
    if accounts_dir.is_dir():
        for acc in accounts_dir.iterdir():
            if acc.is_dir():
                for ext in exts:
                    candidates.append(acc / "refs" / f"{name}{ext}")

    flow_auto_refs = repo_root.parent / "flow-auto" / "refs"
    if flow_auto_refs.is_dir():
        for ext in exts:
            candidates.append(flow_auto_refs / f"{name}{ext}")

    for cand in candidates:
        if cand.is_file():
            return cand.resolve()

    return None


def picker_open(page):
    s = page.locator(S["refs_search"])
    return s.count() > 0 and s.first.is_visible()


def open_picker(page):
    if not picker_open(page):
        page.click(S["add_refs_button"])
        page.wait_for_selector(S["refs_search"], timeout=10000)
        page.wait_for_timeout(800)


def search_ref(page, name: str):
    open_picker(page)
    s = page.locator(S["refs_search"])
    s.click()
    s.fill("")
    page.wait_for_timeout(200)
    s.fill(name)
    page.wait_for_timeout(600)

    pat = ref_pattern(name)
    opts = page.locator(S["ref_option"]).filter(has_text=pat)
    if opts.count() == 0:
        opts = page.locator(S["ref_option"]).filter(has_text=re.compile(rf"\b{re.escape(name)}\b", re.I))
    if opts.count() == 0:
        page.wait_for_timeout(600)
        opts = page.locator(S["ref_option"]).filter(has_text=pat)
    return opts


def clear_chips(page):
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)
    chips = page.locator(S["ref_chip"])
    for _ in range(12):
        if chips.count() == 0:
            return
        try:
            chips.first.click(timeout=3000, force=True)
        except Exception:
            page.keyboard.press("Escape")
            page.wait_for_timeout(300)
            if chips.count() == 0:
                return
            chips.first.click(timeout=3000, force=True)
        page.wait_for_timeout(600)
    raise RuntimeError("Failed to clear prompt reference chips.")


def missing_refs(page, names: list, target_dir: str = None) -> list:
    clear_chips(page)
    open_picker(page)

    missing = []
    for n in names:
        opts = search_ref(page, n)
        if opts.count() == 0:
            missing.append(n)

    if not missing:
        page.keyboard.press("Escape")
        page.wait_for_timeout(400)
        return []

    to_upload = []
    for n in missing:
        fpath = find_ref_file(n, target_dir)
        if fpath:
            to_upload.append(str(fpath))
        else:
            log(f"Warning: Reference file for '{n}' not found on disk.")

    if to_upload:
        log(f"Auto-importing missing reference image(s): {', '.join(Path(p).name for p in to_upload)}")
        s_inp = page.locator(S["refs_search"])
        if s_inp.count() and s_inp.first.is_visible():
            s_inp.click()
            s_inp.fill("")
            page.wait_for_timeout(300)

        upload_btn = page.locator("button:has-text(\"Importer\")")
        if upload_btn.count() and upload_btn.first.is_visible():
            try:
                with page.expect_file_chooser(timeout=8000) as fc_info:
                    upload_btn.first.click()
                fc_info.value.set_files(to_upload)

                page.wait_for_timeout(1500)
                t0 = time.time()
                while time.time() - t0 < 45:
                    spinners = page.locator("mat-spinner, .cdk-visually-hidden:has-text(\"Importation en cours\")")
                    if spinners.count() == 0:
                        page.wait_for_timeout(1000)
                        if spinners.count() == 0:
                            break
                    page.wait_for_timeout(500)
            except Exception as e:
                log(f"Warning: Reference import error: {e}")
        else:
            log("Warning: 'Importer' button not found or not visible.")

    still_missing = []
    for n in names:
        opts = search_ref(page, n)
        if opts.count() == 0:
            page.wait_for_timeout(1500)
            opts = search_ref(page, n)
            if opts.count() == 0:
                still_missing.append(n)
            else:
                log(f"Reference '{n}' verified and ready.")
        else:
            log(f"Reference '{n}' verified and ready.")

    page.keyboard.press("Escape")
    page.wait_for_timeout(400)
    return still_missing


def type_prompt(page, text: str):
    clear_chips(page)
    box = page.locator(S["prompt_box"])
    box.click()
    try:
        box.fill(text)
    except Exception:
        page.keyboard.press("ControlOrMeta+A")
        page.keyboard.press("Backspace")
        page.keyboard.type(text, delay=5)
    page.wait_for_timeout(400)
    if text[:25] not in box.inner_text():
        box.click()
        page.keyboard.press("ControlOrMeta+A")
        page.keyboard.press("Backspace")
        page.keyboard.type(text, delay=5)
        page.wait_for_timeout(300)


def attach_refs(page, refs: list, target_dir: str = None):
    chips = page.locator(S["ref_chip"])
    for name in refs:
        before = chips.count()
        open_picker(page)
        opt = search_ref(page, name)
        if opt.count() == 0:
            missing_refs(page, [name], target_dir)
            open_picker(page)
            opt = search_ref(page, name)
        if opt.count() == 0:
            page.keyboard.press("Escape")
            raise RuntimeError(f"Reference '{name}' not found in project library.")
        opt.first.click()
        page.wait_for_timeout(800)
        confirm = page.locator(S["add_refs_confirm"]).filter(has_text=re.compile(r"(Ajouter \d+ élément|au prompt|to prompt)", re.I))
        if confirm.count() and confirm.first.is_visible():
            confirm.first.click()
            page.wait_for_timeout(800)
        if picker_open(page):
            page.keyboard.press("Escape")
            page.wait_for_timeout(400)
        if chips.count() != before + 1:
            raise RuntimeError(f"Reference '{name}' failed to attach ({chips.count()} chip(s) instead of {before + 1})")
    log(f"Attached references: {chips.count()}")


def captcha_visible(page) -> bool:
    for f in page.locator("iframe[src*=\"recaptcha\"][src*=\"bframe\"]").all():
        b = f.bounding_box()
        if b and b["width"] > 100 and b["y"] >= 0 and f.is_visible():
            return True
    return False
