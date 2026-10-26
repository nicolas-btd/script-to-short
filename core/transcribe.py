import json
import sys
from pathlib import Path

from .utils import log_step


def transcribe_audio(target_dir: str, model_size: str = "base", language: str = "fr") -> str:
    from faster_whisper import WhisperModel

    target_path = Path(target_dir).resolve()
    voice_path = target_path / "voix.mp3"
    out_words_path = target_path / "whisper_words.json"

    if not voice_path.is_file():
        raise FileNotFoundError(f"Missing voice file: {voice_path}")

    log_step("WHISPER", f"Transcribing audio with faster-whisper (model='{model_size}', language='{language}')...")

    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(voice_path), language=language, word_timestamps=True)

    words = []
    for segment in segments:
        for w in segment.words:
            words.append({
                "word": w.word.strip(),
                "start": round(w.start, 3),
                "end": round(w.end, 3),
                "probability": round(w.probability, 3)
            })

    out_words_path.write_text(json.dumps(words, ensure_ascii=False, indent=2), encoding="utf-8")
    log_step("WHISPER", f"Transcription complete: {len(words)} words saved to {out_words_path.name}")
    return str(out_words_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m core.transcribe <video_dir> [model_size] [language]")
        sys.exit(1)
    target = sys.argv[1]
    m_size = sys.argv[2] if len(sys.argv) > 2 else "base"
    lang = sys.argv[3] if len(sys.argv) > 3 else "fr"
    transcribe_audio(target, m_size, lang)
