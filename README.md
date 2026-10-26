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
- [Pipeline Modes](#pipeline-modes)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [CLI Reference](#cli-reference)
- [Configuration & Customization](#configuration--customization)
  - [Configuration Precedence](#configuration-precedence)
  - [Full Configuration Schema](#full-configuration-schema)
  - [Subtitle Customization](#subtitle-customization)
  - [Visual Effects & Camera Motion](#visual-effects--camera-motion)
  - [Editing & Graphic Elements](#editing--graphic-elements)
  - [Voice Synthesis & Acting Direction](#voice-synthesis--acting-direction)
  - [Account Style Profiles](#account-style-profiles)
  - [Common Recipes & CLI Presets](#common-recipes--cli-presets)
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

### CLI Reference

```
usage: main.py [-h] [--mode {auto,manual}] [--account ACCOUNT] [--skip-voice]
               [--skip-flow] [--render-only] [--web-only] [--fps FPS]
               [--sub-pos {top,center,bottom}] [--sub-y SUB_Y]
               [--sub-size SUB_SIZE] [--sub-color SUB_COLOR]
               [--sub-accent SUB_ACCENT] [--sub-align {center,left,right}]
               [--no-subtitles] [--no-zoom] [--zoom-intensity ZOOM_INTENSITY]
               [--zoom-mode {alternate,in,out,none}] [--no-shake]
               [--no-keywords] [--voice-name VOICE_NAME]
               [--voice-style VOICE_STYLE]
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
                        Preset vertical subtitle position (top=0.22, center=0.50, bottom=0.75)
  --sub-y SUB_Y         Custom vertical position as percent from top (e.g. 0.70 bottom, 0.50 center, 0.20 top)
  --sub-size SUB_SIZE   Subtitle font size in points (e.g. 60, 70, 85)
  --sub-color SUB_COLOR
                        Inactive text color (hex '#FFFFFF' or comma-separated '255,255,255')
  --sub-accent SUB_ACCENT
                        Active spoken word highlight color (hex '#FFD43B', '255,212,59', or 'none' to disable)
  --sub-align {center,left,right}
                        Horizontal text alignment
  --no-subtitles        Disable subtitles completely

Visual Effect Controls:
  --no-zoom             Disable Ken Burns zoom animations (render static images)
  --zoom-intensity ZOOM_INTENSITY
                        Zoom scale delta factor (default: 0.08)
  --zoom-mode {alternate,in,out,none}
                        Camera motion direction across consecutive cuts
  --no-shake            Disable camera shake effects
  --no-keywords         Disable top keyword popups

Voice Controls:
  --voice-name VOICE_NAME
                        Gemini TTS base voice timbre (e.g. Puck, Charon, Kore, Fenrir, Aoede)
  --voice-style VOICE_STYLE
                        Natural language prompt directing AI vocal delivery, cadence, and tone
```

---

## Configuration & Customization

Every visual, typographic, auditory, and structural aspect of the pipeline can be tailored to match your channel branding.

### Configuration Precedence

Settings are resolved through a 4-tier hierarchy. Higher tiers override lower tiers:

```
[ Tier 1: CLI Flags ] (--sub-y, --sub-accent, --voice-name, etc.)
       |
       v
[ Tier 2: Project Config ] (videos/<project_folder>/config.json)
       |
       v
[ Tier 3: Account Profile Config ] (accounts/<account_name>/config.json)
       |
       v
[ Tier 4: Global Engine Defaults ] (built into core modules)
```

> Supplying CLI flags automatically persists those overrides into `videos/<project_folder>/config.json`. This ensures that subsequent re-renders (via `--render-only` or the web review UI) preserve your exact custom settings.

---

### Full Configuration Schema

Below is the complete reference schema for `config.json`:

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
    "style": "A dynamic, engaging narrator voice for short-form video. Lively rhythm and crisp pronunciation with natural pacing."
  },
  "flow": {
    "prefixes": {}
  }
}
```

---

### Subtitle Customization

Subtitles are generated at word-level accuracy from Whisper timestamps, with real-time word highlighting.

#### Subtitle Parameter Reference

| Key | CLI Equivalent | Type | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `enabled` | `--no-subtitles` | boolean | `true` | When `false`, completely disables subtitle overlay rendering. |
| `font` | N/A | string | `"Arial Rounded Bold"` | Font family or filename. Automatically resolved across OS (see below). |
| `size` | `--sub-size` | integer | `70` | Subtitle font size in points (recommended range: 55 to 90). |
| `position` | `--sub-pos` | string | `"bottom"` | Preset vertical position: `"top"`, `"center"`, or `"bottom"`. |
| `y_percent` | `--sub-y` | float | `0.70` | Exact vertical position as a ratio from top (`0.0` = top, `1.0` = bottom). |
| `alignment` | `--sub-align` | string | `"center"` | Horizontal alignment of words on screen: `"center"`, `"left"`, or `"right"`. |
| `active_color` | `--sub-accent` | hex / RGB / null | `[255, 212, 59]` | Color highlighting the word currently being spoken. Set to `none` / `null` for monochrome. |
| `inactive_color` | `--sub-color` | hex / RGB | `[255, 255, 255]` | Color of words in the active card that are not currently being spoken. |
| `stroke_color` | N/A | hex / RGB | `[0, 0, 0]` | Border outline color around glyphs for contrast over light backgrounds. |
| `stroke_width` | N/A | integer | `6` | Thickness of character outline in pixels (recommended: 4 to 8). |
| `uppercase` | N/A | boolean | `true` | When `true`, automatically converts all subtitle text to uppercase for legibility. |
| `max_words` | N/A | integer | `3` | Maximum number of words displayed concurrently on screen per card. |
| `max_width` | N/A | integer | `880` | Maximum pixel width on the 1080px canvas before wrapping to a new line. |

#### Color Format Options

Colors can be specified in any of the following formats:
- Hexadecimal strings: `"#FFD43B"`, `"#00E6FF"`, `"#FFFFFF"`
- Comma-separated strings: `"255,212,59"`, `"0,230,255"`
- RGB JSON arrays: `[255, 212, 59]`, `[0, 230, 255]`

#### Disabling Word Highlighting (Monochrome Mode)

To render clean, uniform monochrome subtitles without any active word accentuation:
- Via CLI: `--sub-accent none` (or `--sub-accent null`, `--sub-accent off`)
- In `config.json`: `"active_color": null`

```bash
# Uniform white text with black outline, centered
python main.py videos/my_project --sub-pos center --sub-accent none --sub-color "#FFFFFF"
```

#### Vertical Positioning & Safe Zones

Short-form platforms (TikTok, YouTube Shorts, Instagram Reels) overlay UI elements that can obscure subtitles:
- **Top Safe Zone (`0.18` to `0.25`):** Clear of header search bars. Preset `--sub-pos top` resolves to `0.22`.
- **Center Zone (`0.45` to `0.55`):** Unobstructed by any interface overlay. Preset `--sub-pos center` resolves to `0.50`.
- **Bottom Safe Zone (`0.65` to `0.72`):** Sits directly above platform caption boxes, usernames, and audio tags. Preset `--sub-pos bottom` resolves to `0.75`. For TikTok specifically, `--sub-y 0.68` is optimal.

```bash
# Position subtitles at exactly 65% height
python main.py videos/my_project --sub-y 0.65
```

#### Word Grouping & Hormozi Style

- **Standard Grouping (`max_words: 3`):** Groups 2 to 3 words together with active word tracking. Balanced reading rhythm.
- **Single-Word Pacing (`max_words: 1`):** Flash-cuts one single word at a time in rapid succession. Pair with a larger font size (`size: 85`):

```json
{
  "subtitles": {
    "size": 85,
    "max_words": 1,
    "y_percent": 0.60,
    "active_color": [255, 230, 0]
  }
}
```

#### Cross-Platform Font Discovery

Fonts are resolved dynamically in this order:
1. Account fonts folder: `accounts/<account_name>/fonts/<font_name>.ttf`
2. Global asset folder: `assets/fonts/<font_name>.ttf`
3. Operating system system directories:
   - macOS: `/System/Library/Fonts/Supplemental`, `/Library/Fonts`, `~/Library/Fonts`
   - Linux: `/usr/share/fonts`, `/usr/local/share/fonts`, `~/.fonts`
   - Windows: `C:\Windows\Fonts`
4. Fallback to bundled sans-serif defaults if no exact match is found.

To use custom branding typography, drop your `.ttf` or `.otf` file into `accounts/<my_account>/fonts/` and set `"font": "MyCustomFont.ttf"` in `config.json`.

---

### Visual Effects & Camera Motion

Static vertical images quickly lose viewer attention. The built-in compositor applies subtle, high-frame-rate Ken Burns camera motion and directional impact shakes.

#### Visual FX Parameter Reference

| Key | CLI Equivalent | Type | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `zoom_enabled` | `--no-zoom` | boolean | `true` | When `false`, images remain completely static without scaling. |
| `zoom_intensity` | `--zoom-intensity` | float | `0.08` | Total scale delta applied over the scene duration. |
| `zoom_mode` | `--zoom-mode` | string | `"alternate"` | Directional zoom pattern across cuts: `alternate`, `in`, `out`, or `none`. |
| `shake_enabled` | `--no-shake` | boolean | `true` | Enables camera shake on scenes flagged with `"fx": ["shake"]`. |
| `shake_intensity` | N/A | float | `10.0` | Maximum camera pixel offset during shake frames. |

#### Ken Burns Zoom Modes Explained

- **`alternate` (Default):** Alternates zoom directions on every cut. Scene 1 zooms slowly in (1.00 -> 1.08), Scene 2 starts zoomed and pulls slowly out (1.08 -> 1.00), Scene 3 zooms in. Creates continuous visual motion without jarring jumps.
- **`in`:** Every single scene starts at standard scale and pushes slowly in toward the center.
- **`out`:** Every scene starts punchy and slightly zoomed, then pulls back to reveal the scene context.
- **`none`:** Completely static camera frames. Equivalent to passing `--no-zoom`.

#### Zoom Intensity Guidelines

- **Subtle (`0.03` - `0.05`):** Recommended for corporate, medical, or documentary channels where motion should be imperceptible but active.
- **Standard (`0.08`):** Balanced motion suited for explainer videos and storytelling.
- **Energetic (`0.12` - `0.16`):** High-speed dramatic zooms suited for cartoons, action, or gaming.

```bash
# Subtle zoom in for documentary
python main.py videos/my_project --zoom-mode in --zoom-intensity 0.04

# Completely static presentation
python main.py videos/my_project --no-zoom
```

#### Camera Shakes

Dramatic moments flagged in the timeline (e.g. unexpected revelations, loud explosions, or comedic fails) trigger horizontal and vertical camera shakes:
- Defined per scene in `timeline_raw.json`: `"fx": ["shake"]`.
- The engine applies a decaying sinusoidal offset over the first 0.3 seconds of the cut, synchronized with sound effects.
- Disable globally via `--no-shake` or `"shake_enabled": false`.

---

### Editing & Graphic Elements

#### Editing Parameter Reference

| Key | CLI Equivalent | Type | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `show_keywords` | `--no-keywords` | boolean | `true` | When `true`, displays bold uppercase animated keyword banners at the top of the screen. |
| `keyword_font_size` | N/A | integer | `150` | Font size for top-screen keyword banners in pixels. |
| `min_scene_dur` | N/A | float | `1.0` | Minimum cut duration in seconds for automated scene planning. |
| `max_scene_dur` | N/A | float | `2.2` | Maximum cut duration in seconds before forcing a scene transition. |
| `sfx_pack` | N/A | string | `"cartoon"` | Subdirectory under `assets/sfx/` containing audio samples. |

#### Top Keyword Banners

When a scene defines a `"keyword"` (e.g. `"keyword": "VIRUS"`), the engine renders an impact text banner at 15% screen height with a dark background plaque and pop-in animation.
- Useful for reinforcing key terms and capturing silent scrolling viewers.
- Disable via `--no-keywords` or `"show_keywords": false`.

#### Sound Effects (SFX) Mixing

Sound cues are automatically aligned with visual cuts and mixed into the narration audio at broadcast loudness standards:
- Cues are referenced by name in the timeline: `"sfx": "whoosh"`, `"sfx": "pop"`, `"sfx": "tic"`, `"sfx": "rire"`, `"sfx": "boing"`, `"sfx": "alarme"`.
- Sound assets reside in `assets/sfx/`. Custom WAV or MP3 files can be added directly to this directory.
- The mixing engine applies individual gain levels (e.g. 0.35 volume factor) to ensure SFX punch through without masking the spoken dialogue.

---

### Voice Synthesis & Acting Direction

Narration audio can be produced automatically via Gemini TTS or imported from third-party recordings.

#### Voice Parameter Reference

| Key | CLI Equivalent | Environment Variable | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `name` | `--voice-name` | `GEMINI_VOICE` | `"Puck"` | Gemini TTS base vocal timbre. |
| `style` | `--voice-style` | `GEMINI_VOICE_STYLE` | (Dynamic) | Natural language prompt conditioning delivery cadence, pitch, and emotional tone. |
| N/A | N/A | `GEMINI_TTS_MODEL` | `"gemini-2.5-flash"` | Gemini model used for multimodal audio generation. |

#### Available Gemini TTS Voice Timbres

| Voice Name | Gender / Register | Acoustic Characteristics | Recommended Channel Types |
| :--- | :--- | :--- | :--- |
| `Puck` | Male / Tenor | Energetic, modern, punchy, crisp articulation | Stickman, cartoons, tech explainers, viral hooks |
| `Charon` | Male / Bass | Deep, solemn, resonant, cinematic gravity | History documentaries, true crime, horror, mysteries |
| `Kore` | Female / Alto | Warm, empathetic, articulate, calm | Science, health, medical, wellness, storytelling |
| `Fenrir` | Male / Baritone | Gravelly, intense, authoritative, commanding | Action, fitness, military history, trailer teasers |
| `Aoede` | Female / Soprano | Sophisticated, smooth, expressive, melodic | Lifestyle, luxury, literature, culture, educational |

#### Directing the AI Voice Actor (`style` Prompt)

Unlike legacy text-to-speech tools that only take speed and pitch sliders, Gemini TTS processes a natural language acting direction prompt. This prompt conditions the vocal model on accent, breath control, emotional state, and pause rhythm.

Tested acting prompts:

**Cartoon & Explainer (French):**
```
A dynamic, engaging French male explainer voice for TikTok. Lively rhythm and crisp pronunciation, but with softer rounded vocal attacks, warmer tone, and relaxed natural pacing.
```

**Cinematic History Documentary (English):**
```
A grave, solemn narrator speaking with contemplative authority. Measured cadence, resonant low frequencies, and deliberate pauses between major revelations.
```

**Medical & Scientific (French or English):**
```
A calm, articulate medical professional explaining complex biology with clarity, empathy, and steady reassurance. Crisp diction without sounding clinical or robotic.
```

**True Crime & Mystery:**
```
A low, suspenseful narration hovering near a whisper. Tense pacing, subtle breathiness, and sudden sharp emphasis on critical clues.
```

#### Using External Pre-Recorded Audio

If you record your own voice or use third-party tools (ElevenLabs, Kokoro, Cartesia, OpenAI TTS):
1. Place your audio file as `videos/<my_project>/voix.mp3` (or `.wav`).
2. Run the pipeline with `--skip-voice` (or without flags; existing audio is auto-detected):
   ```bash
   python main.py videos/my_project --skip-voice
   ```
3. Faster-Whisper automatically reads your audio file, extracts exact word-level timestamps, and perfectly synchronizes subtitles and scene cuts.

---

### Account Style Profiles

Accounts group brand assets, typography, color palettes, visual defaults, and prompt guidelines into reusable directories under `accounts/<account_name>/`:

```
accounts/
|-- cartoon/                  # Yellow accents, Arial Rounded Bold, Puck voice, cartoon SFX
|   |-- config.json
|   `-- prompt.txt
|-- documentary/              # Monochrome/subtle accents, Charon voice, slow push zoom
|   |-- config.json
|   `-- prompt.txt
|-- medical/                  # Cyan/turquoise accents, Kore voice, steady pacing
|   |-- config.json
|   `-- prompt.txt
|-- horror/                   # Blood red accents, camera shakes, suspenseful Charon voice
|   |-- config.json
|   `-- prompt.txt
`-- _template/                # Clean boilerplate for creating new channel profiles
    |-- config.json
    `-- prompt.txt
```

#### Creating a New Account Profile

1. Copy the boilerplate template:
   ```bash
   cp -r accounts/_template accounts/my_channel
   ```
2. Edit `accounts/my_channel/config.json` to define your brand colors, preferred voice, subtitle placement, and zoom defaults.
3. Edit `accounts/my_channel/prompt.txt` with your channel's artistic image prompt prefix (e.g. "Flat vector 2D minimalist illustration with bold outlines...").
4. (Optional) Place your custom brand font into `accounts/my_channel/fonts/`.
5. Run projects under your new profile:
   ```bash
   python main.py videos/my_project --account my_channel
   ```

---

### Common Recipes & CLI Presets

#### 1. Hormozi Viral Style
Single large word on screen, rapid cuts, punchy yellow accent, bottom center placement:
```bash
python main.py videos/demo \
  --sub-pos bottom \
  --sub-size 90 \
  --sub-accent "#FFE600" \
  --sub-color "#FFFFFF" \
  --zoom-intensity 0.10 \
  --zoom-mode alternate
```

#### 2. Minimalist Monochrome (No Highlight)
Centered clean white subtitles with zero word highlighting, static camera frames:
```bash
python main.py videos/demo \
  --sub-pos center \
  --sub-accent none \
  --sub-color "#F0F0F0" \
  --no-zoom
```

#### 3. Cinematic Documentary
Deep authoritative male voice, subtle camera push-in, top-positioned subtitles:
```bash
python main.py videos/demo \
  --voice-name Charon \
  --sub-pos top \
  --sub-accent "#00E6FF" \
  --zoom-mode in \
  --zoom-intensity 0.04
```

#### 4. Educational / Medical Explainer
Calm female voice, turquoise highlight, centered subtitles:
```bash
python main.py videos/demo \
  --voice-name Kore \
  --sub-pos center \
  --sub-accent "#00FFC2" \
  --sub-size 75 \
  --zoom-mode in
```

#### 5. Fast Subtitle & Color Re-Render
Re-render the final video without re-generating speech or downloading new images:
```bash
python main.py videos/demo \
  --render-only \
  --sub-accent "#FF3366" \
  --sub-y 0.65
```

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
