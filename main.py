#!/usr/bin/env python3
import argparse
import json
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

    # Subtitle Customization
    sub_group = parser.add_argument_group("Subtitle Controls")
    sub_group.add_argument("--sub-pos", choices=["top", "center", "bottom"], help="Preset vertical subtitle position")
    sub_group.add_argument("--sub-y", type=float, help="Custom vertical position as percent from top (e.g. 0.70 bottom, 0.50 center, 0.20 top)")
    sub_group.add_argument("--sub-size", type=int, help="Subtitle font size (e.g. 60, 70, 85)")
    sub_group.add_argument("--sub-color", help="Inactive text color (hex '#FFFFFF' or '255,255,255')")
    sub_group.add_argument("--sub-accent", help="Active spoken word highlight color (hex '#FFD43B', '255,212,59', or 'none' to disable)")
    sub_group.add_argument("--sub-align", choices=["center", "left", "right"], help="Horizontal text alignment")
    sub_group.add_argument("--no-subtitles", action="store_true", help="Disable subtitles completely")

    # Visual Effects Customization
    fx_group = parser.add_argument_group("Visual Effect Controls")
    fx_group.add_argument("--no-zoom", action="store_true", help="Disable Ken Burns zoom animations (static images)")
    fx_group.add_argument("--zoom-intensity", type=float, help="Zoom scale factor (default: 0.08)")
    fx_group.add_argument("--zoom-mode", choices=["alternate", "in", "out", "none"], help="Zoom motion direction")
    fx_group.add_argument("--no-shake", action="store_true", help="Disable camera shake effects")
    fx_group.add_argument("--no-keywords", action="store_true", help="Disable top keyword popups")

    # Voice Controls
    voice_group = parser.add_argument_group("Voice Controls")
    voice_group.add_argument("--voice-name", help="Gemini TTS voice timbre (e.g. Puck, Charon, Kore, Fenrir, Aoede)")
    voice_group.add_argument("--voice-style", help="Natural language prompt directing the AI voice actor cadence and tone")

    # Visual Style Direction
    style_group = parser.add_argument_group("Visual Style Direction")
    style_group.add_argument(
        "--style",
        "--visual-style",
        dest="visual_style",
        help="Target visual style / art direction prompt (e.g. 'Dark cinematic documentary, 8k', 'Clean 2D stickman cartoon')"
    )

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

    # Build and persist CLI overrides into project config.json if supplied
    cli_overrides = {"subtitles": {}, "visual_fx": {}, "editing": {}, "voice": {}}
    if args.no_subtitles:
        cli_overrides["subtitles"]["enabled"] = False
    if args.sub_pos:
        cli_overrides["subtitles"]["position"] = args.sub_pos
    if args.sub_y is not None:
        cli_overrides["subtitles"]["y_percent"] = args.sub_y
    if args.sub_size is not None:
        cli_overrides["subtitles"]["size"] = args.sub_size
    if args.sub_color:
        cli_overrides["subtitles"]["inactive_color"] = args.sub_color
    if args.sub_accent is not None:
        cli_overrides["subtitles"]["active_color"] = None if args.sub_accent.lower() in ("none", "null", "false", "no", "off") else args.sub_accent
    if args.sub_align:
        cli_overrides["subtitles"]["alignment"] = args.sub_align

    if args.no_zoom:
        cli_overrides["visual_fx"]["zoom_enabled"] = False
    if args.zoom_intensity is not None:
        cli_overrides["visual_fx"]["zoom_intensity"] = args.zoom_intensity
    if args.zoom_mode:
        cli_overrides["visual_fx"]["zoom_mode"] = args.zoom_mode
    if args.no_shake:
        cli_overrides["visual_fx"]["shake_enabled"] = False

    if args.no_keywords:
        cli_overrides["editing"]["show_keywords"] = False

    if args.voice_name:
        cli_overrides["voice"]["name"] = args.voice_name
    if args.voice_style:
        cli_overrides["voice"]["style"] = args.voice_style

    if args.visual_style:
        cli_overrides["visual_style"] = args.visual_style

    # Clean empty override dictionaries
    cli_overrides = {k: v for k, v in cli_overrides.items() if v}

    if cli_overrides:
        cfg_file = target_path / "config.json"
        existing_cfg = {}
        if cfg_file.is_file():
            try:
                existing_cfg = json.loads(cfg_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        for section, vals in cli_overrides.items():
            if isinstance(vals, dict):
                if section not in existing_cfg or not isinstance(existing_cfg[section], dict):
                    existing_cfg[section] = {}
                existing_cfg[section].update(vals)
            else:
                existing_cfg[section] = vals
        cfg_file.write_text(json.dumps(existing_cfg, indent=2, ensure_ascii=False), encoding="utf-8")
        log_step("CONFIG", f"Updated project overrides in {cfg_file.name}")

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
        out_mp4 = render_video(str(target_path), fps=args.fps, cli_overrides=cli_overrides)
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
    plan_scenes(str(target_path), account_name, force_mode=args.mode, visual_style=args.visual_style)

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
