import base64
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

from .utils import load_env, log_step


def generate_voice(target_dir: str, voice_name: str = "Puck", style: str = None) -> str:
    target_path = Path(target_dir).resolve()
    script_path = target_path / "script.txt"
    out_mp3 = target_path / "voix.mp3"
    temp_wav = target_path / "temp_voice_raw.wav"

    if not script_path.is_file():
        raise FileNotFoundError(f"Missing script file: {script_path}")

    load_env(str(target_path))
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not defined.")

    # Resolve account voice settings if not explicitly specified
    from .account_manager import detect_account_name, load_account_config
    account_name = detect_account_name(str(target_path))
    acc_cfg = load_account_config(account_name, str(target_path))
    voice_cfg = acc_cfg.get("voice", {})

    if not voice_name:
        voice_name = voice_cfg.get("name", "Puck")

    env_voice = os.environ.get("GEMINI_VOICE") or os.environ.get("GEMINI_VOICE_FR")
    if env_voice:
        voice_name = env_voice

    if not style:
        style = voice_cfg.get("style") or os.environ.get("GEMINI_VOICE_STYLE")
    if not style:
        style = (
            "A dynamic, engaging narrator voice for short-form video. "
            "Lively rhythm and clear pronunciation, with natural pacing."
        )

    model_name = os.environ.get("GEMINI_TTS_MODEL", "gemini-2.5-flash")

    text = script_path.read_text(encoding="utf-8").strip()
    log_step("VOICE", f"Generating audio with voice '{voice_name}' (model: '{model_name}')")
    log_step("VOICE", f"Acting style prompt: \"{style[:80]}...\"")

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": text,
                        "speech_metadata": {"style": style}
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {"voiceName": voice_name}
                }
            }
        }
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise RuntimeError(f"Gemini TTS request failed (HTTP {e.code}): {error_body}")
    except Exception as e:
        raise RuntimeError(f"Gemini TTS request error: {e}")

    try:
        b64_data = data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
    except (KeyError, IndexError):
        raise RuntimeError(f"Unexpected response payload from Gemini TTS: {json.dumps(data)}")

    raw_audio = base64.b64decode(b64_data)
    temp_wav.write_bytes(raw_audio)

    log_step("VOICE", "Normalizing audio with FFmpeg to -14 LUFS...")
    cmd_ffmpeg = [
        "ffmpeg", "-y",
        "-i", str(temp_wav),
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
        "-ar", "48000",
        "-b:a", "192k",
        str(out_mp3)
    ]

    res = subprocess.run(cmd_ffmpeg, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if temp_wav.exists():
        temp_wav.unlink()

    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg normalization failed: {res.stderr.decode('utf-8', errors='ignore')}")

    log_step("VOICE", f"Normalized speech saved to {out_mp3.name}")
    return str(out_mp3)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m core.voice <video_dir> [voice_name]")
        sys.exit(1)
    target = sys.argv[1]
    voice = sys.argv[2] if len(sys.argv) > 2 else "Puck"
    generate_voice(target, voice)
