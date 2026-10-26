import csv
import difflib
import glob
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .account_manager import detect_account_name, load_account_config, resolve_font_path
from .utils import log_step


def clean_word(w: str) -> str:
    return re.sub(r"[^a-z0-9]", "", w.lower())


def build_timeline(target_dir: str) -> str:
    target_path = Path(target_dir).resolve()
    whisper_path = target_path / "whisper_words.json"
    script_path = target_path / "script.txt"
    timeline_raw_path = target_path / "timeline_raw.json"

    if not whisper_path.is_file():
        raise FileNotFoundError(f"Missing whisper transcription file: {whisper_path}")
    if not script_path.is_file():
        raise FileNotFoundError(f"Missing script file: {script_path}")
    if not timeline_raw_path.is_file():
        raise FileNotFoundError(f"Missing raw timeline file: {timeline_raw_path}")

    w_words = json.loads(whisper_path.read_text(encoding="utf-8"))
    script_text = script_path.read_text(encoding="utf-8")
    timeline = json.loads(timeline_raw_path.read_text(encoding="utf-8"))

    img_files = sorted(glob.glob(str(target_path / "*.jpg")))
    img_map = {}
    for p in img_files:
        base = Path(p).name
        num_str = base.split("_")[0].split(".")[0]
        if num_str.isdigit():
            img_map[int(num_str)] = p

    tokens = []
    pattern = re.compile(r"([a-zA-Z0-9àâäéèêëîïôöùûüÿçœæÀÂÄÉÈÊËÎÏÔÖÙÛÜŸÇŒÆ]+)")
    for m in pattern.finditer(script_text):
        tokens.append({
            "word": m.group(1),
            "start_char": m.start(),
            "end_char": m.end()
        })

    w_clean = [clean_word(w["word"]) for w in w_words]
    s_clean = [clean_word(t["word"]) for t in tokens]

    sm = difflib.SequenceMatcher(None, s_clean, w_clean)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for si, wj in zip(range(i1, i2), range(j1, j2)):
                tokens[si]["start"] = w_words[wj]["start"]
                tokens[si]["end"] = w_words[wj]["end"]
        elif tag == "replace":
            t_start = w_words[j1]["start"]
            t_end = w_words[j2 - 1]["end"]
            count = i2 - i1
            dt = (t_end - t_start) / max(1, count)
            for idx, si in enumerate(range(i1, i2)):
                tokens[si]["start"] = round(t_start + idx * dt, 3)
                tokens[si]["end"] = round(t_start + (idx + 1) * dt, 3)
        elif tag == "delete":
            prev_end = tokens[i1 - 1]["end"] if i1 > 0 and "end" in tokens[i1 - 1] else 0.0
            for idx, si in enumerate(range(i1, i2)):
                tokens[si]["start"] = prev_end
                tokens[si]["end"] = prev_end + 0.2

    cur_tok_idx = 0
    image_starts = {}
    unfound_anchors = []

    for item in timeline:
        item_id = item["id"]
        anchor = item.get("anchor", "")
        if anchor == "SPLIT":
            continue
        a_words = [clean_word(w) for w in re.findall(r"[a-zA-Z0-9àâäéèêëîïôöùûüÿçœæÀÂÄÉÈÊËÎÏÔÖÙÛÜŸÇŒÆ]+", anchor)]
        best_match = None
        for idx in range(cur_tok_idx, len(tokens) - len(a_words) + 1):
            sub = [clean_word(tokens[idx + k]["word"]) for k in range(len(a_words))]
            if sub == a_words:
                best_match = idx
                break
        if best_match is not None:
            raw_start = tokens[best_match]["start"]
            start_time = max(0.0, raw_start - 0.05)
            image_starts[item_id] = start_time
            cur_tok_idx = best_match + len(a_words)
        else:
            unfound_anchors.append((item_id, anchor))
            image_starts[item_id] = None

    image_starts[1] = 0.0

    total_imgs = len(timeline)
    for i in range(2, total_imgs + 1):
        prev_val = image_starts[i - 1]
        cur_val = image_starts.get(i)
        if cur_val is None or cur_val <= prev_val:
            next_valid = None
            next_idx = None
            for j in range(i + 1, total_imgs + 1):
                val_j = image_starts.get(j)
                if val_j is not None and val_j > prev_val:
                    next_valid = val_j
                    next_idx = j
                    break
            if next_valid is not None:
                step = (next_valid - prev_val) / (next_idx - (i - 1))
                image_starts[i] = round(prev_val + step, 3)
            else:
                image_starts[i] = round(prev_val + 1.0, 3)

    if tokens:
        last_word_end = tokens[-1]["end"]
        final_end = round(last_word_end + 0.1, 3)
    else:
        voix_mp3 = target_path / "voix.mp3"
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(voix_mp3)]
        audio_end = float(subprocess.check_output(cmd).decode().strip())
        final_end = round(audio_end, 3)

    starts_list = [image_starts[i] for i in range(1, total_imgs + 1)]
    ends_list = starts_list[1:] + [final_end]

    for i in range(1, total_imgs):
        dur = ends_list[i] - starts_list[i]
        if dur < 0.4:
            needed = 0.4 - dur
            starts_list[i] -= needed
            ends_list[i - 1] = starts_list[i]

    final_timeline = []
    for i in range(total_imgs):
        img_id = i + 1
        item_spec = next((item for item in timeline if item["id"] == img_id), {})
        final_timeline.append({
            "id": img_id,
            "image_path": img_map.get(img_id, str(target_path / f"{img_id:02d}.jpg")),
            "start": round(starts_list[i], 3),
            "end": round(ends_list[i], 3),
            "dur": round(ends_list[i] - starts_list[i], 3),
            "keyword": item_spec.get("keyword"),
            "sfx": item_spec.get("sfx"),
            "fx": item_spec.get("fx", []),
            "end_card": item_spec.get("end_card")
        })

    csv_path = target_path / "timeline_finale.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "start", "end", "duration"])
        for e in final_timeline:
            writer.writerow([e["id"], f"{e['start']:.2f}", f"{e['end']:.2f}", f"{e['dur']:.2f}"])

    merged_tokens = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if i + 1 < len(tokens):
            next_tok = tokens[i + 1]
            between = script_text[tok["end_char"]:next_tok["start_char"]]
            if "'" in between or "’" in between:
                merged_tokens.append({
                    "word": (tok["word"] + "'" + next_tok["word"]).upper(),
                    "clean": clean_word(tok["word"] + next_tok["word"]),
                    "start": tok["start"],
                    "end": next_tok["end"],
                    "end_char": next_tok["end_char"]
                })
                i += 2
                continue
            elif "-" in between and not between.strip(" -"):
                merged_tokens.append({
                    "word": (tok["word"] + "-" + next_tok["word"]).upper(),
                    "clean": clean_word(tok["word"] + next_tok["word"]),
                    "start": tok["start"],
                    "end": next_tok["end"],
                    "end_char": next_tok["end_char"]
                })
                i += 2
                continue
        merged_tokens.append({
            "word": tok["word"].upper(),
            "clean": clean_word(tok["word"]),
            "start": tok["start"],
            "end": tok["end"],
            "end_char": tok["end_char"]
        })
        i += 1

    acc_name = detect_account_name(str(target_path))
    acc_cfg = load_account_config(acc_name, str(target_path))
    sub_cfg = acc_cfg.get("subtitles", {})
    font_spec = sub_cfg.get("font", "Arial Rounded Bold")
    font_path = resolve_font_path(font_spec, acc_name)
    sub_size = int(sub_cfg.get("size", 70))

    try:
        f_sub = ImageFont.truetype(font_path, sub_size)
    except Exception:
        f_sub = ImageFont.load_default()

    dummy_draw = ImageDraw.Draw(Image.new("RGB", (100, 100)))
    space_w = dummy_draw.textlength(" ", font=f_sub) if hasattr(dummy_draw, "textlength") else 20.0

    subtitle_groups = []
    cur_group = []

    def calc_group_width(grp):
        if not grp:
            return 0.0
        if hasattr(dummy_draw, "textlength"):
            return sum(dummy_draw.textlength(w["word"], font=f_sub) for w in grp) + space_w * (len(grp) - 1)
        return float(len(grp) * 80)

    for idx, tok in enumerate(merged_tokens):
        ch_end = tok["end_char"]
        punct = ""
        while ch_end < len(script_text) and script_text[ch_end] in ',.!?;:—«»"…':
            punct += script_text[ch_end]
            ch_end += 1
        tok_entry = {
            "word": tok["word"] + punct,
            "clean": tok["clean"],
            "start": tok["start"],
            "end": tok["end"]
        }
        test_group = cur_group + [tok_entry]
        w = calc_group_width(test_group)

        if cur_group and (len(test_group) > 3 or w > 880):
            subtitle_groups.append({
                "start": cur_group[0]["start"],
                "end": cur_group[-1]["end"],
                "words": cur_group
            })
            cur_group = [tok_entry]
        else:
            cur_group.append(tok_entry)

        has_break_punct = bool(re.search(r"[,.!?;:…—]", punct))
        pause_after = (merged_tokens[idx + 1]["start"] - tok["end"]) if idx + 1 < len(merged_tokens) else 1.0

        if len(cur_group) >= 3 or has_break_punct or pause_after > 0.35:
            subtitle_groups.append({
                "start": cur_group[0]["start"],
                "end": cur_group[-1]["end"],
                "words": cur_group
            })
            cur_group = []

    if cur_group:
        subtitle_groups.append({
            "start": cur_group[0]["start"],
            "end": cur_group[-1]["end"],
            "words": cur_group
        })

    for idx in range(len(subtitle_groups)):
        grp = subtitle_groups[idx]
        actual_end = grp["end"]
        if idx + 1 < len(subtitle_groups):
            next_start = subtitle_groups[idx + 1]["start"]
            if 0 < next_start - actual_end < 0.22:
                grp["display_end"] = next_start
            else:
                grp["display_end"] = actual_end
        else:
            grp["display_end"] = actual_end

    processed_data = {
        "timeline": final_timeline,
        "subtitles": subtitle_groups,
        "unfound_anchors": unfound_anchors,
        "total_duration": final_end
    }

    out_json = target_path / "timeline_processed.json"
    out_json.write_text(json.dumps(processed_data, indent=2, ensure_ascii=False), encoding="utf-8")

    log_step("TIMELINE", f"Timeline calculated: {len(final_timeline)} scenes, {final_end:.2f}s total duration.")
    return str(out_json)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m core.timeline <target_dir>")
        sys.exit(1)
    build_timeline(sys.argv[1])
