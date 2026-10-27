import json
import sys
from pathlib import Path

STICK = (
    "Clean digital cartoon illustration in a simple stickman style. The stickman has a large perfectly round "
    "white head with a thick black outline, expressive eyes (white circles with black pupils), thin curved "
    "eyebrows and a small simple mouth. His body, arms and legs are very thin black lines, with no hands or "
    "feet drawn, just line ends."
)
FLATSTYLE = "Clean digital cartoon illustration in a simple flat style."
FLAT = (
    "Full-color flat background filling the whole frame, no paper texture. Objects have flat colors with thick "
    "black outlines and no shading. Minimalist details, lots of empty space, soft muted colors. Vertical 9:16 "
    "format. Absolutely no text or writing anywhere in the image."
)
FLOOR = (
    "The character stands firmly on a simple light wooden floor at the bottom of the frame, with a clean horizontal "
    "ground line separating the wooden floor from the colored wall background, exactly like the floor in the reference image C1."
)
NEW = "Create a completely new composition and background as described."

DEFAULT_PREFIXES = {
    "man": f"{STICK} {FLOOR} {FLAT} Same character and style as the reference image. Use the reference image only for the character design and drawing style. {NEW}",
    "brain": f"{FLATSTYLE} {FLAT} Same pink brain mascot and drawing style as the reference image. Use the reference image only for the character design and drawing style. {NEW}",
    "duo": f"{STICK} {FLOOR} {FLAT} Same stickman and same pink brain mascot as the reference images, same drawing style. Use the reference images only for the character designs and drawing style. {NEW}",
    "obj": f"{FLATSTYLE} {FLAT} Same drawing style as the reference image. Use the reference image only for the drawing style. No stickman in this image. {NEW}",
    "scene": f"{FLATSTYLE} {FLAT} {NEW}"
}


def build_prompts(target_dir: str, custom_prefixes: dict = None, visual_style: str = None) -> str:
    target_path = Path(target_dir).resolve()
    jsonl_path = target_path / "prompts.jsonl"
    json_path = target_path / "prompts.json"
    raw_timeline_path = target_path / "timeline_raw.json"
    scenes_path = target_path / "scenes.json"

    from core.account_manager import detect_account_name, resolve_visual_style
    account_name = detect_account_name(str(target_path))
    if not visual_style:
        visual_style = resolve_visual_style(str(target_path))

    prefixes = {}
    if account_name == "cartoon" and not (target_path / "style.txt").is_file():
        prefixes = dict(DEFAULT_PREFIXES)
    elif visual_style:
        clean_style = visual_style.strip().rstrip(".")
        base_prefix = f"{clean_style}. Vertical 9:16 portrait format. Absolutely no text, letters, numbers, or watermarks anywhere in the image."
        for st in ["scene", "man", "obj", "character", "subject", "perso"]:
            prefixes[st] = base_prefix
    else:
        prefixes = dict(DEFAULT_PREFIXES)

    if custom_prefixes:
        prefixes.update(custom_prefixes)

    cand_prefixes = target_path / "account_prefixes.json"
    if cand_prefixes.is_file():
        try:
            extra = json.loads(cand_prefixes.read_text(encoding="utf-8"))
            prefixes.update(extra)
        except Exception:
            pass

    items = []
    # 1. If prompts.json already exists and contains prompts, return it directly
    if json_path.is_file():
        try:
            existing = json.loads(json_path.read_text(encoding="utf-8"))
            if existing and any(it.get("prompt") or it.get("scene") for it in existing):
                if not jsonl_path.is_file():
                    with open(jsonl_path, "w", encoding="utf-8") as f:
                        for it in existing:
                            f.write(json.dumps(it, ensure_ascii=False) + "\n")
                txt_path = target_path / "prompts.txt"
                if not txt_path.is_file():
                    with open(txt_path, "w", encoding="utf-8") as f:
                        for it in existing:
                            p_str = it.get("prompt") or it.get("scene") or ""
                            f.write(f"=== Plan {it.get('id')} ===\n{p_str}\n\n")
                return str(json_path)
        except Exception:
            pass

    if jsonl_path.is_file():
        for line in jsonl_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    items.append(json.loads(line))
                except Exception:
                    pass
    elif raw_timeline_path.is_file():
        try:
            raw_items = json.loads(raw_timeline_path.read_text(encoding="utf-8"))
            if any(it.get("scene") or it.get("prompt") for it in raw_items):
                items = raw_items
        except Exception:
            pass
    if not items and scenes_path.is_file():
        try:
            items = json.loads(scenes_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    if not items:
        raise FileNotFoundError(
            f"No prompts source found in {target_path} (expected prompts.json, prompts.jsonl, timeline_raw.json with scenes, or scenes.json)"
        )

    records = []
    for item in items:
        s_type = item.get("s", "man")
        prefix = prefixes.get(s_type, prefixes.get("scene", ""))
        scene = item.get("scene", "").strip()

        # If user already wrote a full prompt in scene or prompt key
        if "prompt" in item and item["prompt"]:
            full_prompt = item["prompt"]
        else:
            full_prompt = f"{prefix} {scene}".strip() if prefix else scene

        records.append({
            "id": item.get("id"),
            "prompt": full_prompt,
            "refs": item.get("refs", []),
            "anchor": item.get("anchor", ""),
            "keyword": item.get("keyword"),
            "sfx": item.get("sfx"),
            "fx": item.get("fx", []),
            "raw_scene": scene,
            "type": s_type
        })

    json_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(json_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m flow.build_prompts <target_dir>")
        sys.exit(1)
    build_prompts(sys.argv[1])
