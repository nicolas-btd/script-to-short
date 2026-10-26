import json
import os
import shutil
import sys
import urllib.request
from pathlib import Path

from .account_manager import (
    detect_account_name,
    get_account_dir,
    load_account_config,
    load_account_prompt_template,
    save_account_marker,
)
from .transcribe import transcribe_audio
from .utils import get_project_root, load_env, log_step
from .voice import generate_voice


def call_gemini_json(prompt: str, api_key: str, model_name: str = "gemini-2.5-flash") -> dict:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.4,
            "responseMimeType": "application/json",
            "thinkingConfig": {"thinkingBudget": 0},
            "maxOutputTokens": 16384
        }
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise RuntimeError(f"Gemini API request failed (HTTP {e.code}): {error_body}")
    except Exception as e:
        raise RuntimeError(f"Gemini API request error: {e}")

    try:
        raw_text = result["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(raw_text)
    except Exception as e:
        raise RuntimeError(f"Failed to parse Gemini JSON response: {e}")


def plan_scenes(target_dir: str, account_name: str = None, force_mode: str = None) -> dict:
    target_path = Path(target_dir).resolve()
    script_path = target_path / "script.txt"
    raw_path = target_path / "timeline_raw.json"
    scenes_path = target_path / "scenes.json"
    prompts_path = target_path / "prompts.json"

    account_name = detect_account_name(str(target_path), account_name)
    save_account_marker(str(target_path), account_name)
    acc_cfg = load_account_config(account_name, str(target_path))

    log_step("PLANNER", f"Active style profile: '{account_name}'")

    # Sync reference images if available
    acc_refs = get_account_dir(account_name) / "refs"
    flow_refs = target_path / "refs"
    if acc_refs.is_dir():
        flow_refs.mkdir(exist_ok=True)
        for rf in acc_refs.glob("*"):
            if rf.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                shutil.copy2(rf, flow_refs / rf.name)

    # 1. Voice audio preparation
    voice_path = target_path / "voix.mp3"
    if not voice_path.is_file():
        if not script_path.is_file():
            raise FileNotFoundError(
                f"Missing both audio and narration: provide either voix.mp3 or script.txt in {target_path}"
            )
        v_name = acc_cfg.get("voice", {}).get("name", "Puck")
        v_style = acc_cfg.get("voice", {}).get("style")
        generate_voice(str(target_path), voice_name=v_name, style=v_style)
    else:
        log_step("PLANNER", f"Existing voice audio detected: {voice_path.name}")

    # 2. Whisper transcription
    whisper_path = target_path / "whisper_words.json"
    if not whisper_path.is_file():
        transcribe_audio(str(target_path))
    else:
        log_step("PLANNER", f"Existing transcription detected: {whisper_path.name}")

    # Determine execution mode: Manual (Timeline input) vs Auto (Script input)
    has_predefined_timeline = raw_path.is_file() or scenes_path.is_file()
    is_manual_mode = (force_mode == "manual") or (force_mode != "auto" and has_predefined_timeline)

    # =========================================================================
    # MODE 2: TIMELINE / MANUAL INPUT (ZERO LLM CALL)
    # =========================================================================
    if is_manual_mode:
        log_step("PLANNER", "Mode: Timeline input (manual mode). Bypassing LLM generation.")

        if not raw_path.is_file() and scenes_path.is_file():
            shutil.copy2(scenes_path, raw_path)

        if not raw_path.is_file():
            raise FileNotFoundError(
                f"Manual mode selected but no timeline found: create {raw_path.name} or {scenes_path.name}"
            )

        # Build prompts.json if not already present
        from flow.build_prompts import build_prompts
        prefixes = acc_cfg.get("flow", {}).get("prefixes", {})
        build_prompts(str(target_path), custom_prefixes=prefixes)

        timeline_raw = json.loads(raw_path.read_text(encoding="utf-8"))
        log_step("PLANNER", f"Loaded {len(timeline_raw)} pre-defined scenes without LLM call.")
        return {"timeline_raw": timeline_raw}

    # =========================================================================
    # MODE 1: SCRIPT INPUT (AUTOMATIC SCENE BREAKDOWN VIA GEMINI 2.5 FLASH)
    # =========================================================================
    log_step("PLANNER", "Mode: Script input (auto mode). Splitting scenes via Gemini 2.5 Flash...")

    if not script_path.is_file():
        raise FileNotFoundError(f"Missing script file for auto mode: {script_path}")

    load_env(str(target_path))
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required for script auto mode.")

    whisper_words = json.loads(whisper_path.read_text(encoding="utf-8"))
    total_voice_dur = whisper_words[-1]["end"] if whisper_words else 60.0
    script_text = script_path.read_text(encoding="utf-8").strip()

    editing_cfg = acc_cfg.get("editing", {})
    min_dur = float(editing_cfg.get("min_scene_dur", 1.0))
    max_dur = float(editing_cfg.get("max_scene_dur", 2.2))

    prompt_template = load_account_prompt_template(account_name)
    if prompt_template:
        prompt = prompt_template.format(
            script_text=script_text,
            total_voice_dur=total_voice_dur,
            min_scene_dur=min_dur,
            max_scene_dur=max_dur
        )
    else:
        prompt = f"""You are the creative director of a viral educational short-form channel.
Full narration script:
\"\"\"
{script_text}
\"\"\"
Total voice duration: {total_voice_dur:.2f} seconds.

RULES:
1. Split this script into rapid, rhythmic visual scenes (average duration between {min_dur:.1f}s and {max_dur:.1f}s).
   Keep the pace dynamic, never exceed 2.5 seconds per scene.
2. Each scene object must contain:
   - "id": sequential integer starting at 1
   - "anchor": the exact 3 to 6 words spoken at the beginning of this scene (must match word-for-word in script)
   - "keyword": strong keyword in UPPERCASE (1 to 3 words max), only on ~30% of key scenes, null otherwise
   - "sfx": relevant sound effect ("pop", "whoosh", "tic"), or null
   - "fx": list of visual effects (e.g. ["shake"]), or []
   - "refs": ["C1"] or ["C1", "C52"]
   - "s": "man" or "obj" or "scene"
   - "scene": visual scene description in English for image generation. Minimalist, no text inside the image.
3. Also provide "cover" metadata:
   - "title_line1": Title line 1 in UPPERCASE
   - "title_line2": Title line 2 in UPPERCASE
   - "bg_color": Background color description
   - "stickman_action": Character action description in English

Respond strictly with valid JSON containing:
{{
  "timeline_raw": [...],
  "prompts": [...],
  "cover": {{...}}
}}
"""

    gemini_model = os.environ.get("GEMINI_PLANNER_MODEL", "gemini-2.5-flash")
    data = call_gemini_json(prompt, api_key, model_name=gemini_model)

    timeline_raw = data.get("timeline_raw", [])
    prompts_list = data.get("prompts", [])
    cover_data = data.get("cover", {})

    raw_path.write_text(json.dumps(timeline_raw, ensure_ascii=False, indent=2), encoding="utf-8")

    jsonl_path = target_path / "prompts.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as f:
        for p in prompts_list:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    from flow.build_prompts import build_prompts
    prefixes = acc_cfg.get("flow", {}).get("prefixes", {})
    build_prompts(str(target_path), custom_prefixes=prefixes)

    # Save cover.txt
    cover_path = target_path / "cover.txt"
    cover_text = (
        f"TITLE 1: {cover_data.get('title_line1', '')}\n"
        f"TITLE 2: {cover_data.get('title_line2', '')}\n"
        f"BG COLOR: {cover_data.get('bg_color', '')}\n"
        f"ACTION: {cover_data.get('stickman_action', '')}\n"
    )
    cover_path.write_text(cover_text, encoding="utf-8")

    # Save prompts.txt
    txt_path = target_path / "prompts.txt"
    lines = [f"# Scene Prompts - {target_path.name}\n"]
    for p in prompts_list:
        lines.append(f"### Scene {p.get('id')} - \"{p.get('anchor', '')}\"")
        lines.append(f"Refs: {', '.join(p.get('refs', []))} | Type: {p.get('s', 'scene')}")
        lines.append(f"Description: {p.get('scene', '')}\n")
    txt_path.write_text("\n".join(lines), encoding="utf-8")

    log_step("PLANNER", f"Scene planning complete: {len(timeline_raw)} scenes created.")
    return data


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m core.scene_planner <video_dir> [account_name] [auto|manual]")
        sys.exit(1)
    target = sys.argv[1]
    acc = sys.argv[2] if len(sys.argv) > 2 else None
    mode_arg = sys.argv[3] if len(sys.argv) > 3 else None
    plan_scenes(target, acc, force_mode=mode_arg)
