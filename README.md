# script-to-short

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Gemini](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-orange.svg)](https://aistudio.google.com/)
[![FFmpeg](https://img.shields.io/badge/Render-FFmpeg-green.svg)](https://ffmpeg.org/)
[![Playwright](https://img.shields.io/badge/Automation-Playwright-red.svg)](https://playwright.dev/)

Automated pipeline transforming a single narration text file (`script.txt`) into a complete vertical 9:16 short-form video (TikTok, YouTube Shorts, Instagram Reels).

The system handles voice synthesis, word-by-word subtitle synchronization, AI scene direction, visual generation via Google Flow, an interactive candidate selector web interface, and automated 60 fps video rendering with Ken Burns camera motion and sound effects.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [CLI Reference](#cli-reference)
- [Account Style Profiles](#account-style-profiles)
- [Directory Structure](#directory-structure)
- [License](#license)

---

## Overview

Producing high-retention short-form videos requires orchestrating voice synthesis, timestamp alignment, prompt engineering, visual generation, audio mixing, and video compositing.

`script-to-short` unifies this entire workflow into a single reproducible CLI tool:
1. Generates speech using Gemini TTS and normalizes loudness to -14 LUFS standard.
2. Performs word-level transcription with Faster-Whisper.
3. Splits the script into rapid 1-2 second scenes and writes visual prompts with Gemini 2.5 Flash.
4. Generates candidate images in parallel through Google Flow via Chrome CDP.
5. Serves a local web interface (`http://localhost:8765`) to review and select visual variants.
6. Encodes the final 1080x1920 video at 30/60 fps with synchronized subtitles, pop-in keywords, camera zooms, and sound effects.

---

## Key Features

- Pure Python Core: No Node.js runtime required.
- High-Pacing Scene Direction: LLM automatically splits script into 1-2 second visual cuts.
- Subtitle Precision: Word-by-word timing with active word color highlighting.
- Cross-Platform Font Resolution: Automatically discovers system fonts on macOS, Linux, and Windows.
- Chrome CDP Automation: Controls Google Flow in an isolated profile, avoiding authentication obstacles.
- Local Web Selector: Fast keyboard navigation (`1`, `2`, `3`, `X`) to pick optimal image variants.
- Multi-Account Profiles: Switch visual presets, subtitle fonts, and voice parameters via dedicated profiles.

## Pipeline Modes

`script-to-short` supports two distinct operating modes:

### Mode 1: Script Input (Auto Mode with Gemini 2.5 Flash)
- **Input:** `videos/project/script.txt`
- **Behavior:** Gemini 2.5 Flash analyzes your script, generates scene cuts (1-2s pacing), detects key moments for sound effects (`sfx`), selects animated uppercase keywords, and writes visual prompts for Google Flow.
- **Usage:**
```bash
python main.py videos/my_project --mode auto
```

### Mode 2: Timeline Input (Manual Mode with Zero LLM Call)
- **Input:** `videos/project/timeline_raw.json` (or `scenes.json`)
- **Behavior:** Bypasses LLM generation completely. You provide your own pre-written scenes, prompts, and sound effect markers. Ideal for using other LLMs (ChatGPT, Claude, local Ollama) or writing custom prompts manually.
- **Usage:**
```bash
python main.py videos/my_project --mode manual
```

> If `timeline_raw.json` or `scenes.json` is present in the video directory, Manual Mode is automatically detected.

#### Manual Timeline Format (`timeline_raw.json` or `scenes.json`)
```json
[
  {
    "id": 1,
    "anchor": "Pourquoi les moustiques",
    "keyword": "MOUSTIQUES",
    "sfx": "whoosh",
    "fx": ["shake"],
    "refs": ["C1"],
    "s": "man",
    "scene": "A stickman looking annoyed as a tiny mosquito buzzes around him."
  },
  {
    "id": 2,
    "anchor": "Ce n'est pas une question",
    "keyword": null,
    "sfx": "pop",
    "fx": [],
    "refs": ["C1"],
    "s": "obj",
    "scene": "A sugar cube and a tube of red blood with a cross symbol."
  }
]
```

---

## Architecture

```
[ script.txt ]
      |
      v
1. core/voice.py -----------> Gemini TTS ---------> [ voix.mp3 ] (-14 LUFS)
      |
      v
2. core/transcribe.py ------> Faster-Whisper -----> [ whisper_words.json ]
      |
      v
3. core/scene_planner.py ---> Gemini 2.5 Flash ---> [ timeline_raw.json ]
      |                                             [ prompts.json ]
      v
4. flow/flow_fast.py -------> Google Flow (CDP) --> [ images_candidates/ ]
      |
      v
5. flow/choisir_web.py -----> Local Web UI -------> [ 01.jpg, 02.jpg... ]
      |
      v
6. core/renderer.py --------> Pillow + FFmpeg ----> [ video_finale.mp4 ]
```

---

## Prerequisites

- Python 3.10 or higher
- FFmpeg (with `aresample` and `loudnorm` filters)
- Google Chrome (for automated visual generation)
- Gemini API Key ([Google AI Studio](https://aistudio.google.com/))

### System Dependencies

**macOS (Homebrew):**
```bash
brew install ffmpeg python
```

**Debian / Ubuntu:**
```bash
sudo apt update
sudo apt install -y ffmpeg python3 python3-pip python3-venv
```

**Windows:**
Install Python and FFmpeg via `winget` or direct installers, and ensure `ffmpeg` is available in your system `PATH`.

---

## Installation

1. Clone this repository:
```bash
git clone https://github.com/your-username/script-to-short.git
cd script-to-short
```

2. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

4. Configure environment variables:
```bash
cp .env.example .env
```
Edit `.env` and set your `GEMINI_API_KEY`:
```env
GEMINI_API_KEY="your_api_key_here"
```

---

## Quickstart

A sample demo project is pre-configured in `videos/demo/`.

### 1. Start Chrome with remote debugging
Google Flow requires an active Google session. Launch Chrome in debug mode once:
```bash
./flow/start_chrome.sh
```
In the Chrome window that opens, navigate to [Google Flow](https://flow.google.com/), log in with your Google account, and open your generation project. Keep this window open in the background.

### 2. Run the pipeline
```bash
python main.py videos/demo
```

### 3. Review scenes and build final video
- The terminal will generate speech, transcribe words, and submit prompts to Google Flow.
- Your browser will open `http://localhost:8765/`.
- Press `1`, `2`, or `3` to choose your preferred variant for each scene.
- Click "Confirm and Render Video".
- Once rendering finishes, click "Open Final Video" to view `video_finale.mp4`.

---

## CLI Reference

```
usage: main.py [-h] [--mode {auto,manual}] [--account ACCOUNT] [--skip-voice]
               [--skip-flow] [--render-only] [--web-only] [--fps FPS]
               [--sub-pos {top,center,bottom}] [--sub-y SUB_Y]
               [--sub-size SUB_SIZE] [--sub-color SUB_COLOR]
               [--sub-accent SUB_ACCENT] [--sub-align {center,left,right}]
               [--no-subtitles] [--no-zoom] [--zoom-intensity ZOOM_INTENSITY]
               [--zoom-mode {alternate,in,out,none}] [--no-shake]
               [--no-keywords]
               video_dir

positional arguments:
  video_dir             Path to project folder containing script.txt or timeline_raw.json

options:
  -h, --help            Show this help message and exit
  --mode {auto,manual}  Pipeline mode: 'auto' (Gemini 2.5 Flash) or 'manual' (Zero LLM)
  --account ACCOUNT     Account style profile (e.g. cartoon, documentary, medical, horror)
  --skip-voice          Skip Gemini TTS generation if voix.mp3 exists
  --skip-flow           Skip Google Flow image generation
  --render-only         Directly build timeline and render final video
  --web-only            Only launch local web review interface
  --fps FPS             Output video frame rate (default: 30)

Subtitle Controls:
  --sub-pos {top,center,bottom}
                        Preset vertical subtitle position
  --sub-y SUB_Y         Custom vertical position as percent from top (e.g. 0.70 bottom, 0.50 center, 0.20 top)
  --sub-size SUB_SIZE   Subtitle font size (e.g. 60, 70, 85)
  --sub-color SUB_COLOR
                        Inactive text color (hex '#FFFFFF' or '255,255,255')
  --sub-accent SUB_ACCENT
                        Active spoken word highlight color (hex '#FFD43B', '255,212,59', or 'none' to disable)
  --sub-align {center,left,right}
                        Horizontal text alignment
  --no-subtitles        Disable subtitles completely

Visual Effect Controls:
  --no-zoom             Disable Ken Burns zoom animations (static images)
  --zoom-intensity ZOOM_INTENSITY
                        Zoom scale factor (default: 0.08)
  --zoom-mode {alternate,in,out,none}
                        Zoom motion direction
  --no-shake            Disable camera shake effects
  --no-keywords         Disable top keyword popups
```

### Examples

Run with centered subtitles and no active word highlighting:
```bash
python main.py videos/demo --sub-pos center --sub-accent none
```

Run with custom position, larger text, and static frames (no zoom):
```bash
python main.py videos/demo --sub-y 0.65 --sub-size 85 --no-zoom
```

Re-render an existing project with custom accent color and subtle zoom:
```bash
python main.py videos/demo --render-only --sub-accent "#00E6FF" --zoom-intensity 0.04
```

---

## Configuration & Customization

Settings can be customized at three levels (highest priority wins):
1. **CLI Flags** (`--sub-y`, `--sub-accent`, etc.)
2. **Project-level config** (`videos/<my_project>/config.json`)
3. **Account profile config** (`accounts/<profile>/config.json`)

### Full Configuration Reference (`config.json`)

```json
{
  "name": "custom_profile",
  "subtitles": {
    "enabled": true,
    "font": "Arial Rounded Bold",
    "size": 70,
    "position": "bottom",
    "y_percent": 0.70,
    "alignment": "center",
    "active_color": [255, 212, 59],
    "inactive_color": [255, 255, 255],
    "stroke_color": [0, 0, 0],
    "stroke_width": 6,
    "uppercase": true,
    "max_words": 3,
    "max_width": 880
  },
  "visual_fx": {
    "zoom_enabled": true,
    "zoom_intensity": 0.08,
    "zoom_mode": "alternate",
    "shake_enabled": true,
    "shake_intensity": 10.0
  },
  "editing": {
    "min_scene_dur": 1.0,
    "max_scene_dur": 2.2,
    "keyword_font_size": 150,
    "show_keywords": true,
    "sfx_pack": "cartoon"
  },
  "voice": {
    "name": "Puck",
    "style": "A dynamic, engaging narrator voice for short-form video."
  }
}
```

#### Subtitle Options
- `enabled` (bool): Toggle subtitle display on/off.
- `size` (int): Text point size.
- `position` (str): `"top"` (0.22), `"center"` (0.50), or `"bottom"` (0.75).
- `y_percent` (float): Exact vertical position from 0.0 (top) to 1.0 (bottom).
- `alignment` (str): `"center"`, `"left"`, or `"right"`.
- `active_color` (list, str, or null): Color of the current spoken word. Set to `null` or `"none"` for monochrome subtitles with zero accentuation.
- `inactive_color` (list or str): Color of non-active words (default: white).
- `max_words` (int): Maximum words grouped per subtitle line (default: 3).

#### Visual Effect Options
- `zoom_enabled` (bool): Enable or disable Ken Burns camera zooms.
- `zoom_intensity` (float): Zoom scale delta (e.g. `0.04` for subtle, `0.08` for standard, `0.15` for dramatic).
- `zoom_mode` (str):
  - `"alternate"`: Alternates zooming in and zooming out across scenes.
  - `"in"`: Every scene zooms in.
  - `"out"`: Every scene zooms out.
  - `"none"`: Completely static frames.
- `shake_enabled` (bool): Enable or disable camera shake animations on dramatic scenes.
- `shake_intensity` (float): Amplitude of camera shake in pixels (default: 10.0).

---

## Directory Structure

```
script-to-short/
|-- .env.example              # Environment variables template
|-- .gitignore                # Git exclusions (credentials, caches, heavy media)
|-- LICENSE                   # MIT License
|-- README.md                 # Project documentation
|-- requirements.txt          # Python dependencies
|-- main.py                   # Unified CLI entry point
|
|-- core/                     # Pipeline engine
|   |-- __init__.py
|   |-- voice.py              # Pure Python Gemini TTS + FFmpeg loudness normalization
|   |-- transcribe.py         # Faster-Whisper timestamp extraction
|   |-- scene_planner.py      # LLM scene breakdown and visual prompting
|   |-- timeline.py           # Subtitle alignment and cut synchronization
|   |-- renderer.py           # Pillow + FFmpeg compositing engine
|   |-- account_manager.py    # Multi-account configuration and font discovery
|   `-- utils.py              # Path resolution and logging utilities
|
|-- flow/                     # Google Flow automation
|   |-- __init__.py
|   |-- flow_auto.py          # Chrome CDP DOM driver
|   |-- flow_fast.py          # Parallel queue and asset downloader
|   |-- choisir_web.py        # Local web selector interface
|   |-- build_prompts.py      # Style prefix applicator
|   `-- start_chrome.sh       # Chrome remote debugging launcher
|
|-- accounts/                 # Pre-configured style profiles
|   |-- _template/
|   |-- cartoon/
|   |-- documentary/
|   |-- medical/
|   `-- horror/
|
|-- assets/
|   `-- sfx/                  # Royalty-free sound effects (whoosh, pop, tic)
|
`-- videos/
    `-- demo/                 # Out-of-the-box working test project
        |-- script.txt
        `-- account.txt
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
