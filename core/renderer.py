import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.io import wavfile

from .account_manager import detect_account_name, load_account_config, resolve_font_path
from .utils import get_project_root, log_step


def mix_audio(target_dir: str, timeline_data: dict, output_audio_path: str):
    target_path = Path(target_dir).resolve()
    voix_mp3 = target_path / "voix.mp3"
    temp_voice_wav = target_path / "temp_voice_48k.wav"

    if not voix_mp3.is_file():
        raise FileNotFoundError(f"Missing voice audio: {voix_mp3}")

    sr = 48000
    subprocess.run([
        "ffmpeg", "-y", "-i", str(voix_mp3),
        "-ar", str(sr), "-ac", "2", str(temp_voice_wav)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    _, v_data = wavfile.read(str(temp_voice_wav))
    voice = v_data.astype(np.float32) / 32768.0

    total_dur = timeline_data["total_duration"]
    total_samples = int(math.ceil(total_dur * sr))
    audio_out = np.zeros((total_samples, 2), dtype=np.float32)

    v_len = min(len(voice), total_samples)
    audio_out[:v_len, :] = voice[:v_len, :]

    # Search for sfx in target_dir/sfx, then assets/sfx
    sfx_candidates = [
        target_path / "sfx",
        get_project_root() / "assets" / "sfx"
    ]
    sfx_dir = None
    for cand in sfx_candidates:
        if cand.is_dir():
            sfx_dir = cand
            break

    sfx_config = {}
    if sfx_dir:
        sfx_config = {
            "tic": (sfx_dir / "tic.mp3", 0.35),
            "whoosh": (sfx_dir / "whoosh.mp3", 0.35),
            "pop": (sfx_dir / "pop.mp3", 0.35),
            "rire": (sfx_dir / "rire.mp3", 0.25),
            "boing": (sfx_dir / "boing.mp3", 0.35),
            "alarme": (sfx_dir / "alarme.mp3", 0.35)
        }

    sfx_cached = {}
    for item in timeline_data.get("timeline", []):
        sfx_name = item.get("sfx")
        if not sfx_name or sfx_name not in sfx_config:
            continue
        sfx_path, vol = sfx_config[sfx_name]
        if not sfx_path.is_file():
            continue

        if sfx_name not in sfx_cached:
            temp_sfx = target_path / f"temp_sfx_{sfx_name}_48k.wav"
            subprocess.run([
                "ffmpeg", "-y", "-i", str(sfx_path),
                "-ar", str(sr), "-ac", "2", str(temp_sfx)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            _, s_data = wavfile.read(str(temp_sfx))
            sfx_cached[sfx_name] = (s_data.astype(np.float32) / 32768.0) * vol
            if temp_sfx.is_file():
                temp_sfx.unlink()

        s_audio = sfx_cached[sfx_name]
        start_idx = int(item["start"] * sr)
        end_idx = min(total_samples, start_idx + len(s_audio))
        to_add = end_idx - start_idx
        if to_add > 0:
            audio_out[start_idx:end_idx, :] += s_audio[:to_add, :]

    fade_len = int(0.05 * sr)
    if total_samples > fade_len:
        fade = np.linspace(1.0, 0.0, fade_len, dtype=np.float32)[:, np.newaxis]
        audio_out[-fade_len:, :] *= fade

    audio_out = np.clip(audio_out, -1.0, 1.0)
    out_int16 = (audio_out * 32767.0).astype(np.int16)
    wavfile.write(output_audio_path, sr, out_int16)

    if temp_voice_wav.is_file():
        temp_voice_wav.unlink()

    log_step("RENDER", f"Audio and SFX mixed: {Path(output_audio_path).name} ({len(audio_out)/sr:.2f}s)")


def render_video(target_dir: str, fps: int = 30) -> str:
    target_path = Path(target_dir).resolve()
    json_path = target_path / "timeline_processed.json"

    if not json_path.is_file():
        raise FileNotFoundError(f"Missing timeline file: {json_path}")

    data = json.loads(json_path.read_text(encoding="utf-8"))
    timeline = data["timeline"]
    subtitles = data["subtitles"]
    total_dur = data["total_duration"]

    out_audio_path = target_path / "temp_audio_final.wav"
    mix_audio(str(target_path), data, str(out_audio_path))

    account_name = detect_account_name(str(target_path))
    acc_cfg = load_account_config(account_name, str(target_path))
    sub_cfg = acc_cfg.get("subtitles", {})
    edit_cfg = acc_cfg.get("editing", {})
    show_keywords = bool(edit_cfg.get("show_keywords", True))

    log_step("RENDER", f"Visual style profile: '{account_name}' (keywords: {'enabled' if show_keywords else 'disabled'})")

    font_spec = sub_cfg.get("font", "Arial Rounded Bold")
    font_path = resolve_font_path(font_spec, account_name)

    f_sub_size = int(sub_cfg.get("size", 70))
    f_key_size = int(edit_cfg.get("keyword_font_size", 150))

    try:
        f_sub = ImageFont.truetype(font_path, f_sub_size)
    except Exception:
        f_sub = ImageFont.load_default()

    try:
        f_key = ImageFont.truetype(font_path, f_key_size)
    except Exception:
        f_key = ImageFont.load_default()

    active_color = tuple(sub_cfg.get("active_color", [255, 212, 59]))
    inactive_color = tuple(sub_cfg.get("inactive_color", [255, 255, 255]))
    stroke_color = tuple(sub_cfg.get("stroke_color", [0, 0, 0]))
    stroke_width = int(sub_cfg.get("stroke_width", 6))
    y_percent = float(sub_cfg.get("y_percent", 0.70))
    sub_y = int(1920 * y_percent)
    is_uppercase = bool(sub_cfg.get("uppercase", True))

    log_step("RENDER", f"Loading {len(timeline)} scene images...")
    img_cache = {}
    for item in timeline:
        img_id = item["id"]
        img_p = Path(item["image_path"])
        if not img_p.is_file():
            cand = target_path / img_p.name
            if cand.is_file():
                img_p = cand
        if img_p.is_file():
            img_cache[img_id] = Image.open(str(img_p)).convert("RGB")
        else:
            # Fallback blank image
            img_cache[img_id] = Image.new("RGB", (1080, 1920), (30, 30, 30))

    kw_cache = {}
    if show_keywords:
        for item in timeline:
            kw = item.get("keyword")
            if kw and kw not in kw_cache:
                kw_upper = kw.upper()
                dummy = ImageDraw.Draw(Image.new("RGBA", (100, 100)))
                bb = dummy.textbbox((0, 0), kw_upper, font=f_key, stroke_width=10)
                pad = 20
                w_box = (bb[2] - bb[0]) + pad * 2
                h_box = (bb[3] - bb[1]) + pad * 2
                kw_im = Image.new("RGBA", (w_box, h_box), (0, 0, 0, 0))
                d_kw = ImageDraw.Draw(kw_im)
                d_kw.text(
                    (pad - bb[0], pad - bb[1]),
                    kw_upper,
                    font=f_key,
                    fill=(255, 255, 255, 255),
                    stroke_width=10,
                    stroke_fill=(0, 0, 0, 255)
                )
                kw_cache[kw] = kw_im

    dummy_draw = ImageDraw.Draw(Image.new("RGB", (100, 100)))
    space_w = dummy_draw.textlength(" ", font=f_sub) if hasattr(dummy_draw, "textlength") else 20.0

    out_video_path = target_path / "video_finale.mp4"
    total_frames = int(round(total_dur * fps))

    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", "1080x1920",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",
        "-i", str(out_audio_path),
        "-c:v", "libx264",
        "-preset", "fast",
        "-b:v", "12M",
        "-maxrate", "14M",
        "-bufsize", "24M",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-shortest",
        str(out_video_path)
    ]

    log_step("RENDER", f"Encoding video: {total_frames} frames ({total_dur:.2f}s) @ {fps} fps...")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    W_base = 736.0
    H_base = W_base * 16.0 / 9.0

    cur_tl_idx = 0
    t0 = time.time()

    for frame_idx in range(total_frames):
        t = frame_idx / float(fps)

        while cur_tl_idx < len(timeline) - 1 and t >= timeline[cur_tl_idx]["end"]:
            cur_tl_idx += 1
        item = timeline[cur_tl_idx]

        t_start = item["start"]
        dur = max(0.01, item["dur"])
        prog = min(1.0, max(0.0, (t - t_start) / dur))
        ease = 0.5 - 0.5 * math.cos(math.pi * prog)

        if item["id"] % 2 == 1:
            zoom = 1.00 + 0.08 * ease
        else:
            zoom = 1.08 - 0.08 * ease

        if "shake" in item.get("fx", []):
            t_rel = t - t_start
            if 0.0 <= t_rel <= 0.4:
                decay = 1.0 - (t_rel / 0.4)
                amp = 10.0 * decay
                dx = amp * math.sin(2 * math.pi * 45.0 * t_rel)
                dy = amp * math.cos(2 * math.pi * 60.0 * t_rel)
            else:
                dx, dy = 0.0, 0.0
        else:
            dx, dy = 0.0, 0.0

        w_crop = W_base / zoom
        h_crop = H_base / zoom
        dx_src = dx * (W_base / 1080.0)
        dy_src = dy * (H_base / 1920.0)
        x0 = 384.0 + dx_src - w_crop / 2.0
        y0 = 688.0 + dy_src - h_crop / 2.0
        x1 = x0 + w_crop
        y1 = y0 + h_crop

        src_im = img_cache[item["id"]]
        frame = src_im.crop((x0, y0, x1, y1)).resize((1080, 1920), Image.Resampling.BILINEAR)

        # Keyword
        if show_keywords:
            kw = item.get("keyword")
            if kw and kw in kw_cache:
                t_rel = t - t_start
                if t_rel < 0.14:
                    s = (t_rel / 0.14) * 1.15
                elif t_rel < 0.20:
                    s = 1.15 - ((t_rel - 0.14) / 0.06) * 0.15
                else:
                    s = 1.0

                if s > 0.02:
                    kw_im = kw_cache[kw]
                    s = min(s, 960.0 / kw_im.size[0])
                    if abs(s - 1.0) < 0.01:
                        kw_w, kw_h = kw_im.size
                        kw_to_paste = kw_im
                    else:
                        kw_w = max(2, int(kw_im.size[0] * s))
                        kw_h = max(2, int(kw_im.size[1] * s))
                        kw_to_paste = kw_im.resize((kw_w, kw_h), Image.Resampling.BILINEAR)

                    kw_x = (1080 - kw_w) // 2
                    kw_y = int(1920 * 0.18) - (kw_h // 2)
                    frame.paste(kw_to_paste, (kw_x, kw_y), kw_to_paste)

        # Subtitles
        active_grp = None
        for grp in subtitles:
            if grp["start"] <= t < grp.get("display_end", grp["end"]):
                active_grp = grp
                break
            if grp["start"] > t:
                break

        if active_grp:
            words = active_grp["words"]
            format_word = (lambda s: s.upper()) if is_uppercase else (lambda s: s)
            tot_w = sum(dummy_draw.textlength(format_word(w["word"]), font=f_sub) for w in words) + space_w * (len(words) - 1)
            sub_x = (1080 - tot_w) / 2.0

            active_word_idx = -1
            for wi, w in enumerate(words):
                next_start = words[wi + 1]["start"] if wi + 1 < len(words) else w["end"]
                if w["start"] <= t < max(w["end"], next_start):
                    active_word_idx = wi
                    break

            draw_f = ImageDraw.Draw(frame)
            cur_x = sub_x
            for wi, w in enumerate(words):
                w_str = format_word(w["word"])
                is_active = (wi == active_word_idx)
                fill_color = active_color if is_active else inactive_color
                draw_f.text(
                    (cur_x, sub_y),
                    w_str,
                    font=f_sub,
                    fill=fill_color,
                    stroke_width=stroke_width,
                    stroke_fill=stroke_color
                )
                cur_x += dummy_draw.textlength(w_str, font=f_sub) + space_w

        proc.stdin.write(frame.tobytes())

        if (frame_idx + 1) % 500 == 0 or frame_idx + 1 == total_frames:
            fps_val = (frame_idx + 1) / max(0.001, (time.time() - t0))
            percent = (frame_idx + 1) / total_frames * 100.0
            log_step("RENDER", f"Frame {frame_idx + 1}/{total_frames} ({percent:.1f}%) - {fps_val:.1f} fps")

    proc.stdin.close()
    proc.wait()

    if out_audio_path.is_file():
        out_audio_path.unlink()

    log_step("RENDER", f"Final video ready: {out_video_path.name}")
    return str(out_video_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m core.renderer <video_dir>")
        sys.exit(1)
    render_video(sys.argv[1])
