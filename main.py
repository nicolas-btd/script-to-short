#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


def is_chrome_cdp_ready(url: str = "http://127.0.0.1:9222/json") -> bool:
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(
        description="script-to-short: Automated pipeline converting narration scripts to vertical short-form videos."
    )
    parser.add_argument("video_dir", help="Path to video project folder (e.g. videos/demo)")
    parser.add_argument(
        "--mode",
        choices=["auto", "manual"],
        default=None,
        help="Pipeline mode: 'auto' (script.txt -> Gemini 2.5 Flash) or 'manual' (timeline_raw.json / scenes.json without LLM)"
    )
    parser.add_argument("--account", help="Account style profile (e.g. cartoon, documentary, medical, horror)")
    parser.add_argument("--skip-voice", action="store_true", help="Skip Gemini TTS generation if voix.mp3 exists")
    parser.add_argument("--skip-flow", action="store_true", help="Skip Google Flow image generation")
    parser.add_argument("--render-only", action="store_true", help="Directly build timeline and render final video")
    parser.add_argument("--web-only", action="store_true", help="Only launch local web review interface")
    parser.add_argument("--fps", type=int, default=30, help="Output video frame rate (default: 30)")

    args = parser.parse_args()

    # Dynamic imports
    from core.account_manager import detect_account_name, save_account_marker
    from core.scene_planner import plan_scenes
    from core.timeline import build_timeline
    from core.renderer import render_video
    from core.utils import get_project_root, load_env, log_step
    from flow.flow_fast import run_generation
    from flow.choisir_web import start_server

    target_path = Path(args.video_dir).resolve()

    if not target_path.exists():
        target_path.mkdir(parents=True, exist_ok=True)

    load_env(str(target_path))
    account_name = detect_account_name(str(target_path), args.account)
    save_account_marker(str(target_path), account_name)

    # Detect mode display
    has_timeline = (target_path / "timeline_raw.json").is_file() or (target_path / "scenes.json").is_file()
    effective_mode = args.mode or ("manual" if has_timeline else "auto")

    print("==============================================================")
    print(f"SCRIPT-TO-SHORT PIPELINE | PROFILE: [{account_name.upper()}]")
    print(f"Target directory: {target_path}")
    print(f"Operating Mode  : {'MANUAL (Zero LLM)' if effective_mode == 'manual' else 'AUTO (Gemini 2.5 Flash)'}")
    print("==============================================================")

    if args.render_only:
        log_step("PIPELINE", "Running timeline and video render directly...")
        build_timeline(str(target_path))
        out_mp4 = render_video(str(target_path), fps=args.fps)
        print("==============================================================")
        print(f"Render completed: {out_mp4}")
        print("==============================================================")
        return

    if args.web_only:
        log_step("PIPELINE", "Opening web review interface...")
        start_server(str(target_path))
        return

    # Step 1: Voice, Whisper, and Scene Planning (Auto or Manual)
    print("\n--------------------------------------------------------------")
    print("[STEP 1/3] Scene Planning & Audio Preparation")
    print("--------------------------------------------------------------")
    plan_scenes(str(target_path), account_name, force_mode=args.mode)

    # Step 2: Google Flow Image Generation via Chrome CDP
    if not args.skip_flow:
        print("\n--------------------------------------------------------------")
        print("[STEP 2/3] Generating visual assets in Google Flow")
        print("--------------------------------------------------------------")

        if not is_chrome_cdp_ready():
            log_step("CHROME", "Chrome debugging port 9222 not detected. Attempting launch...")
            script_sh = get_project_root() / "flow" / "start_chrome.sh"
            if script_sh.is_file():
                subprocess.Popen(["bash", str(script_sh)])
                time.sleep(3)

        if not is_chrome_cdp_ready():
            print("[ERROR] Could not connect to Chrome on http://127.0.0.1:9222", file=sys.stderr)
            print("Please launch Chrome with remote debugging:", file=sys.stderr)
            print("  ./flow/start_chrome.sh", file=sys.stderr)
            print("Ensure Google Flow is opened and you are logged into your Google account.", file=sys.stderr)
            sys.exit(1)

        run_generation(str(target_path))
    else:
        log_step("PIPELINE", "Skipping Google Flow generation (--skip-flow).")

    # Step 3: Web selection and automated render
    print("\n--------------------------------------------------------------")
    print("[STEP 3/3] Opening scene review interface and render trigger")
    print("--------------------------------------------------------------")
    start_server(str(target_path))


if __name__ == "__main__":
    main()
