# script-to-short

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Gemini](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-orange.svg)](https://aistudio.google.com/)
[![FFmpeg](https://img.shields.io/badge/Render-FFmpeg-green.svg)](https://ffmpeg.org/)
[![Playwright](https://img.shields.io/badge/Automation-Playwright-red.svg)](https://playwright.dev/)

> **Automated vertical video generator (9:16) for TikTok, YouTube Shorts, and Instagram Reels from a simple text file (`script.txt`).**

---

> [!TIP]
> ### 🤖 Guide for ChatGPT, Claude & AI Assistants (and Beginners)
> If you are using an AI assistant for guidance or are entirely new to programming:
> - **Everything is explained step by step below**, from downloading the code to the final rendered video.
> - You can copy and paste this README directly into ChatGPT or Claude and ask:  
>   *“Guide me step by step through installing script-to-short and creating my first video on [Windows / macOS / Linux].”*  
> - The AI will have 100% of the technical context, exact commands, and troubleshooting instructions.

---

## Table of Contents

- [1. Overview: What does this project do?](#1-overview-what-does-this-project-do)
- [2. Step-by-Step Installation Guide (Beginner Friendly)](#2-step-by-step-installation-guide-beginner-friendly)
  - [Step 1: Download the Project](#step-1-download-the-project)
  - [Step 2: Install Python (Important Windows Warning!)](#step-2-install-python-important-windows-warning)
  - [Step 3: Install FFmpeg](#step-3-install-ffmpeg)
  - [Step 4: Get Your Free Google Gemini API Key](#step-4-get-your-free-google-gemini-api-key)
  - [Step 5: Configure the .env File](#step-5-configure-the-env-file)
  - [Step 6: Install Project Dependencies](#step-6-install-project-dependencies)
- [3. Creating Your First Video in 4 Steps](#3-creating-your-first-video-in-4-steps)
  - [Step 1: Write Your Script](#step-1-write-your-script)
  - [Step 2: Launch Chrome on Google Flow](#step-2-launch-chrome-on-google-flow)
  - [Step 3: Run the Generation Pipeline](#step-3-run-the-generation-pipeline)
  - [Step 4: Select Images on the Web Interface](#step-4-select-images-on-the-web-interface)
- [4. Web Review Interface Guide](#4-web-review-interface-guide)
  - [Automatic Variant Count Detection (x1, x2, x3, x4)](#automatic-variant-count-detection-x1-x2-x3-x4)
  - [Keyboard Shortcuts & Interactions](#keyboard-shortcuts--interactions)
  - [Targeted Regeneration (X Key)](#targeted-regeneration-x-key)
- [5. Architecture & Technical Pipeline](#5-architecture--technical-pipeline)
- [6. Two Operating Modes](#6-two-operating-modes)
  - [Mode 1: Automatic (Script + Style via Gemini)](#mode-1-automatic-script--style-via-gemini)
  - [Mode 2: Manual (Custom Prompts & Timeline, Zero LLM Calls)](#mode-2-manual-custom-prompts--timeline-zero-llm-calls)
- [7. Project File Dictionary](#7-project-file-dictionary)
- [8. Customization & Configuration](#8-customization--configuration)
  - [Configuration Priority](#configuration-priority)
  - [Complete config.json Schema](#complete-configjson-schema)
  - [Visual Styles & Art Direction (style.txt)](#visual-styles--art-direction-styletxt)
  - [Subtitle Customization](#subtitle-customization)
  - [Camera Effects & Ken Burns Zooms](#camera-effects--ken-burns-zooms)
  - [Sound Effects (SFX)](#sound-effects-sfx)
  - [Gemini AI Voices & Actor Direction](#gemini-ai-voices--actor-direction)
  - [Using Your Own Voice or External Audio](#using-your-own-voice-or-external-audio)
  - [Multi-Channel Account Profiles (accounts/)](#multi-channel-account-profiles-accounts)
- [9. Ready-to-Use Recipes & Styles](#9-ready-to-use-recipes--styles)
- [10. Complete CLI Command Reference](#10-complete-cli-command-reference)
- [11. FAQ & Troubleshooting](#11-faq--troubleshooting)
- [12. Repository Structure](#12-repository-structure)
- [13. License](#13-license)
- [14. Disclaimer & Legal Notice](#14-disclaimer--legal-notice)

---

## 1. Overview: What does this project do?

Creating engaging vertical short-form videos for TikTok, YouTube Shorts, or Instagram Reels usually requires hours of tedious work across multiple software tools:
1. Recording and cleaning up a voiceover.
2. Manually pacing and cutting the script into 1-to-2 second clips to maintain viewer retention.
3. Drafting prompts and generating dozens of visually coherent images.
4. Aligning word-by-word subtitles with dynamic colored karaoke highlighting.
5. Adding Ken Burns zoom animations, camera shake impacts, and sound effects (whoosh, pop).
6. Assembling and exporting the final 9:16 vertical video (1080x1920) at 60 fps.

**`script-to-short` automates 100% of this production workflow.**  
Simply write your text in a `script.txt` file, run the command, and let the pipeline handle the rest.

---

## 2. Step-by-Step Installation Guide (Beginner Friendly)

No prior programming experience is required. Follow these 6 steps:

### Step 1: Download the Project

Two simple options:
- **Option A (Without Git)**: Click the green **`<> Code`** button at the top of the GitHub page, then click **`Download ZIP`**. Extract the archive anywhere on your computer (e.g. into your *Documents* folder).
- **Option B (With Git)**: Open your terminal and run:
  ```bash
  git clone https://github.com/nicolas-btd/script-to-short.git
  cd script-to-short
  ```

---

### Step 2: Install Python (Important Windows Warning!)

This project requires **Python 3.10 or higher**.

- **On Windows:**
  1. Download Python from the official site: [python.org/downloads](https://www.python.org/downloads/)
  2. Launch the installer.
  3. > [!CRITICAL]
     > **CRITICAL STEP:** Check the box **`Add python.exe to PATH`** at the bottom of the very first setup screen before clicking *Install Now*. If you miss this, your terminal will not recognize the `python` command.
- **On macOS:**
  Open *Terminal* and run (using [Homebrew](https://brew.sh/)):
  ```bash
  brew install python
  ```
- **On Linux (Ubuntu/Debian):**
  ```bash
  sudo apt update && sudo apt install -y python3 python3-pip python3-venv
  ```

---

### Step 3: Install FFmpeg

FFmpeg is the multimedia engine that handles audio mixing, image animation, and final video encoding.

- **On Windows:**
  Open *PowerShell* or *Command Prompt* and run:
  ```powershell
  winget install Gyan.FFmpeg
  ```
  *(Restart your terminal after installation so FFmpeg is recognized).*
- **On macOS:**
  ```bash
  brew install ffmpeg
  ```
- **On Linux (Ubuntu/Debian):**
  ```bash
  sudo apt install -y ffmpeg
  ```

*Verification: type `ffmpeg -version` in your terminal. If version details appear, installation succeeded!*

---

### Step 4: Get Your Free Google Gemini API Key

The Gemini API generates broadcast-quality AI voiceovers and plans scenes automatically. It is **100% free**:

1. Go to **[Google AI Studio](https://aistudio.google.com/)**.
2. Sign in with any Google account.
3. Click the blue **`Get API key`** button in the left sidebar.
4. Click **`Create API key`**, then copy the generated key (starts with `AIzaSy...`).

---

### Step 5: Configure the .env File

In the project folder:
1. Locate the file named `.env.example`.
2. Duplicate or rename it to **`.env`** (with a leading dot, without `.example`).
3. Open it with any text editor (Notepad, VS Code, TextEdit).
4. Replace the placeholder with your actual Gemini API key:
   ```env
   GEMINI_API_KEY="AIzaSyYourSecretKeyHere"
   ```
5. Save the file.

---

### Step 6: Install Project Dependencies

Open your terminal in the project directory:

1. **Create and activate a virtual environment (recommended):**
   - **On macOS / Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - **On Windows:**
     ```powershell
     python -m venv .venv
     .venv\Scripts\activate
     ```
2. **Install Python packages:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Install automation browser binaries:**
   ```bash
   playwright install chromium
   ```

Setup is complete! You are ready to create your first video.

---

## 3. Creating Your First Video in 4 Steps

### Step 1: Write Your Script

Create a new folder for your project inside `videos/` (e.g. `videos/my_video/`).  
Inside, create a plain text file named **`script.txt`** and paste your narration:

```text
Did you know your brain consumes 20% of your total daily energy?
Yet, it only accounts for about 2% of your entire body weight.
When you think deeply, it burns through glucose at lightning speed.
So next time you feel exhausted after intense studying, it is completely normal!
```

*(Optional)* Add a **`style.txt`** file in the same folder to specify the visual art direction (e.g. *« Clean 2D stickman cartoon, minimalist, solid colors »* or *« Dark cinematic historical painting, dramatic lighting »*).

---

### Step 2: Launch Chrome on Google Flow

Google Flow (`flow.google.com`) is Google's web-based image generation studio. To avoid bot blocks or authentication issues, the pipeline attaches directly to your local Chrome session:

- **On macOS / Linux:**
  ```bash
  ./flow/start_chrome.sh
  ```
- **On Windows:**
  Double-click `flow\start_chrome.bat` or run:
  ```cmd
  flow\start_chrome.bat
  ```

A Google Chrome window opens.  
👉 **Inside this Chrome window:**
1. Navigate to **[flow.google.com](https://flow.google.com/)**.
2. Sign in with your Google account.
3. Open the project where you want your images generated (or create a new one).
4. **Leave this Chrome window open in the background.**

---

### Step 3: Run the Generation Pipeline

In your terminal (inside the `script-to-short` directory):

```bash
python main.py videos/my_video
```

The script will automatically:
1. 🎙️ Synthesize the narration with Gemini TTS normalized to broadcast loudness (-14 LUFS).
2. ⏱️ Extract precise word-level timestamps using Faster-Whisper.
3. 🎬 Segment the script into rapid 1-to-2 second clips and draft visual prompts.
4. 🎨 Transmit prompts to Google Flow via Chrome CDP and download all candidate variants.
5. 🌐 Automatically open your browser to the local review interface: `http://localhost:8765/`.

---

### Step 4: Select Images on the Web Interface

A review interface opens at `http://localhost:8765/`:

1. For each scene, view the spoken audio clip alongside candidate image variants.
2. **Press `1`, `2`, `3`, or `4` on your keyboard** (or click any thumbnail) to pick your preferred image.
3. If no image suits a scene, press **`X`** to mark it red ("Redo").
4. At the top, click **`✅ Validate and render video`**.
5. A live progress bar tracks timeline compilation and FFmpeg rendering.
6. Once finished, click **`▶️ Open final video`**: your completed **`video_finale.mp4`** opens, ready to post!

---

## 4. Web Review Interface Guide

The web selector (`flow/choisir_web.py`) is optimized for speed and keyboard navigation.

### Automatic Variant Count Detection (x1, x2, x3, x4)

Google Flow supports generating 1, 2, 3, or 4 variants per prompt (configured via the `🍌 Nano Banana ... crop_9_16 x4` settings menu).
- **Auto-detection in Flow**: The engine reads the active UI setting directly from the Flow page (`x1`, `x2`, `x3`, or `x4`).
- **Dynamic Web Display**: The web interface adapts layout columns on a per-scene basis to match available variants.

### Keyboard Shortcuts & Interactions

Review an entire video without touching your mouse:
- Keys **`1`**, **`2`**, **`3`**, **`4`** (numpad or top-row): Select variant and auto-scroll to the next scene.
- AZERTY keys **`&`**, **`é`**, **`"`**, **`'`**: Mapped to options 1 through 4.
- Key **`X`**: Toggles scene into "Redo" mode.
- Direct click on any thumbnail.

### Targeted Regeneration (X Key)

If one or more scenes are marked with `X` and you click *Validate*:
1. The engine re-triggers only those specific scenes in Google Flow.
2. It fetches fresh candidates while preserving all previously selected images.

---

## 5. Architecture & Technical Pipeline

The pipeline operates as a modular, automated factory:

```text
[ script.txt ] (Raw narration script)
      │
      ▼
1. core/voice.py ──────────► Gemini TTS ──────────► [ voix.mp3 ] (-14 LUFS)
      │
      ▼
2. core/transcribe.py ─────► Faster-Whisper ──────► [ whisper_words.json ] (Word-level timestamps)
      │
      ▼
3. core/scene_planner.py ──► Gemini 2.5 Flash ────► [ timeline_raw.json ] (Scene segmentation)
      │                                             [ prompts.json ]      (9:16 visual prompts)
      ▼
4. flow/flow_fast.py ──────► Google Flow (CDP) ───► [ images_candidates/ ] (1-4 variants per cut)
      │
      ▼
5. flow/choisir_web.py ────► Web Selector UI ─────► [ 01.jpg, 02.jpg... ] (Selected frames)
      │
      ▼
6. core/renderer.py ───────► Pillow + FFmpeg ─────► [ video_finale.mp4 ] (60 fps video with zooms,
                                                                          subtitles & sound effects)
```

---

## 6. Two Operating Modes

### Mode 1: Automatic (Script + Style via Gemini)

The default, fastest workflow.
- **Required Inputs:** Only `videos/<project>/script.txt` (and optionally `style.txt`).
- **AI Role:** Gemini 2.5 Flash analyzes text, splits it into dynamic 1-to-2 second clips, tailors image prompts to your art direction, and places zoom modes, camera shakes, uppercase keywords, and SFX cues.
- **Command:**
  ```bash
  python main.py videos/my_video
  ```

### Mode 2: Manual (Custom Prompts & Timeline, Zero LLM Calls)

Ideal if you generate prompts externally (ChatGPT, Claude, DeepSeek, or manual curation).
- **Recognized Inputs:**
  - `prompts.jsonl` or `prompts.json`: Exact list of image prompts with character/object references.
  - `timeline_raw.json` or `scenes.json`: Synchronization audio anchors (`anchor`), keyword overlays, and SFX markers.
- **Behavior:** When these files exist, the Gemini planning step is skipped entirely.
- **Command:**
  ```bash
  python main.py videos/my_video --mode manual
  ```

---

## 7. Project File Dictionary

Inside any project folder `videos/my_video/`, files serve specific roles:

| File | Required? | Role & Description |
| :--- | :---: | :--- |
| `script.txt` | **Yes** (Auto mode) | Plain text narration read by AI voiceover. |
| `style.txt` | No | Art direction description (e.g. 2D cartoon, 3D render, oil painting). |
| `account.txt` | No | Channel profile preset name (`cartoon`, `documentary`, `medical`, `horror`). |
| `cover.txt` | No | Suggested title and thumbnail concept for social media. |
| `desc.txt` | No | Generated video description and hashtags for TikTok / Shorts / Reels. |
| `voix.mp3` | Auto-generated | Master voiceover audio file, normalized to broadcast -14 LUFS. |
| `whisper_words.json` | Auto-generated | Millisecond-accurate word timestamps for subtitle rendering. |
| `timeline_raw.json` | Auto-generated | Scene cuts with audio sync anchors (`anchor`), SFX cues, and shake FX. |
| `prompts.json` | Auto-generated | Complete compiled prompt payload dispatched to Google Flow. |
| `prompts.txt` | Auto-generated | Human-readable prompt sheet (convenient for copy-pasting elsewhere). |
| `images_candidates/` | Auto-generated | Folder containing all downloaded image variants (`1_1.jpg`, `1_2.jpg`, etc.). |
| `choix_images.json` | Auto-generated | State file recording user selections from the web UI. |
| `01.jpg`, `02.jpg`... | Auto-generated | Final selected images, renamed in chronological playback order. |
| `timeline_finale.csv` | Auto-generated | Calculated timeline with exact durations per scene in seconds. |
| `video_finale.mp4` | **OUTPUT** | **Final 60 fps vertical video** with animated subtitles, zooms, and mixed audio! |

---

## 8. Customization & Configuration

### Configuration Priority

Settings for subtitles, visual FX, voice, and pacing resolve through a 4-tier hierarchy (higher tiers override lower tiers):

1. **CLI Flags** (`--sub-size 80`, `--voice-name Charon`, etc.)
2. **Project-level config** (`videos/<project>/config.json`)
3. **Account profile config** (`accounts/<profile>/config.json`)
4. **Engine defaults**

---

### Complete config.json Schema

Place a `config.json` inside your video project folder to customize styling:

```json
{
  "name": "my_style",
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
    "style": "A dynamic, engaging narrator voice for short-form video. Lively rhythm and crisp pronunciation."
  }
}
```

---

### Visual Styles & Art Direction (`style.txt`)

To ensure every scene adheres to a uniform visual identity, define your prompt in `videos/<project>/style.txt` or supply it via `--style`.

Battle-tested style presets:

#### 1. 2D Stickman Cartoon (Viral explainer style)
```text
Clean digital cartoon illustration in a simple stickman style. The stickman has a large perfectly round white head with a thick black outline, expressive eyes (white circles with black pupils), thin curved eyebrows and a small simple mouth. His body, arms and legs are very thin black lines, with no hands or feet drawn. Flat color background filling the whole frame, no paper texture. Objects have flat colors with thick black outlines and no shading. Vertical 9:16 format. Absolutely no text or writing anywhere in the image.
```

#### 2. Cinematic Historical Documentary
```text
Vivid cinematic digital illustration, rich atmospheric chiaroscuro lighting, detailed historical storytelling scene, dramatic depth of field, vertical 9:16 format. Absolutely no text, words, or writing anywhere in the image.
```

#### 3. 3D Medical & Scientific Render
```text
Stylized 3D animation render, clean medical and biology explainer aesthetic, smooth matte materials, simple organic shapes, soft global illumination, vertical 9:16 composition. Absolutely no text or writing anywhere in the image.
```

#### 4. Cyberpunk Anime / Manga
```text
Modern cyberpunk anime digital illustration, vibrant neon lighting, high contrast, wet reflective pavement, detailed character design, Studio Trigger inspired dynamic framing, vertical 9:16 portrait composition. Absolutely no text or writing anywhere in the image.
```

---

### Subtitle Customization

Subtitles render dynamically with word-by-word karaoke synchronization:

- **Vertical position:**
  - Bottom (recommended for TikTok/Reels, clears UI captions): `--sub-pos bottom` or `--sub-y 0.68`
  - Center (documentary style): `--sub-pos center` or `--sub-y 0.50`
  - Top: `--sub-pos top` or `--sub-y 0.22`
- **Spoken word highlight color:**
  - Vibrant yellow: `--sub-accent "#FFE600"`
  - Neon green: `--sub-accent "#00FF66"`
  - Electric cyan: `--sub-accent "#00E5FF"`
  - Disable highlighting (solid white text): `--sub-accent none`
- **Font size:** `--sub-size 65` (compact) to `--sub-size 90` (large viral impact)
- **Disable subtitles entirely:** `--no-subtitles`

---

### Camera Effects & Ken Burns Zooms

Continuous dynamic camera motion keeps static generated images lively:

- **`--zoom-mode alternate` (Default):** Alternates direction on each cut (scene 1 zooms in, scene 2 zooms out, scene 3 zooms in). Smooth and engaging.
- **`--zoom-mode in`:** All cuts zoom forward.
- **`--zoom-mode out`:** All cuts start tighter and pull back.
- **`--no-zoom`:** Completely static images.
- **`--zoom-intensity 0.12`:** Increases zoom scale factor (default: `0.08`).
- **`--no-shake`:** Disables camera shake impacts on surprise or climax moments.

---

### Sound Effects (SFX)

Subtle sound effects are inserted at transitions or keyword reveals:
- `whoosh`: Quick air swish on scene transitions.
- `pop`: Appearance of icons or focal items.
- `tic`: Countdown or clock ticking.
- Custom effects: Add any `.mp3` or `.wav` into `assets/sfx/`.

---

### Gemini AI Voices & Actor Direction

Gemini TTS offers 5 voice timbres:

| Voice | Register | Tone & Delivery | Best For |
| :--- | :--- | :--- | :--- |
| **Puck** | Male (Tenor) | Energetic, punchy, crisp diction | Cartoons, fast explainers, TikTok |
| **Charon** | Male (Bass) | Deep, solemn, resonant, gripping | Documentaries, history, horror |
| **Kore** | Female (Alto) | Warm, composed, reassuring, clear | Science, healthcare, narratives |
| **Fenrir** | Male (Baritone)| Gritty, commanding, intense, powerful | Action, fitness, trailers |
| **Aoede** | Female (Soprano)| Elegant, gentle, melodic, refined | Lifestyle, culture, education |

Select a voice with:
```bash
python main.py videos/my_video --voice-name Charon
```

---

### Using Your Own Voice or External Audio

If you record your own voiceover or use an external service (ElevenLabs, etc.):
1. Place your audio file in the project folder named **`voix.mp3`** (or `.wav`).
2. Run the pipeline with:
   ```bash
   python main.py videos/my_video --skip-voice
   ```
3. Faster-Whisper automatically ingests the file, extracts timestamps, and aligns the entire video.

---

### Multi-Channel Account Profiles (`accounts/`)

If you run multiple themed channels, organize presets under `accounts/<profile_name>/`:

- `accounts/cartoon/`: Stickman visual style, Puck voice, yellow subtitles.
- `accounts/documentary/`: Historical style, Charon voice, slow zoom, white subtitles.
- `accounts/medical/`: 3D minimalist style, Kore voice, turquoise highlight.

Apply a profile to any video:
```bash
python main.py videos/my_video --account cartoon
```

---

## 9. Ready-to-Use Recipes & Styles

#### Alex Hormozi Style (Large bold yellow dynamic subtitles)
```bash
python main.py videos/my_video \
  --sub-pos bottom \
  --sub-size 90 \
  --sub-accent "#FFE600" \
  --sub-color "#FFFFFF" \
  --zoom-intensity 0.10
```

#### Minimalist Documentary (Subtle white subtitles, slow zoom)
```bash
python main.py videos/my_video \
  --voice-name Charon \
  --sub-pos center \
  --sub-accent none \
  --sub-color "#FFFFFF" \
  --zoom-mode in \
  --zoom-intensity 0.04
```

#### Science & Medical Explainer
```bash
python main.py videos/my_video \
  --voice-name Kore \
  --sub-pos center \
  --sub-accent "#00FFC2" \
  --sub-size 75 \
  --zoom-mode in
```

#### Re-render video with new subtitle settings (without regenerating images)
```bash
python main.py videos/my_video \
  --render-only \
  --sub-accent "#FF3366" \
  --sub-y 0.65
```

---

## 10. Complete CLI Command Reference

```text
usage: main.py [-h] [--mode {auto,manual}] [--account ACCOUNT] [--skip-voice]
               [--skip-flow] [--render-only] [--web-only] [--fps FPS]
               [--sub-pos {top,center,bottom}] [--sub-y SUB_Y]
               [--sub-size SUB_SIZE] [--sub-color SUB_COLOR]
               [--sub-accent SUB_ACCENT] [--sub-align {center,left,right}]
               [--no-subtitles] [--no-zoom] [--zoom-intensity ZOOM_INTENSITY]
               [--zoom-mode {alternate,in,out,none}] [--no-shake]
               [--no-keywords] [--voice-name VOICE_NAME]
               [--voice-style VOICE_STYLE] [--style STYLE]
               video_dir
```

| Option | Valid Values | Description |
| :--- | :--- | :--- |
| `video_dir` | Directory path | **(Required)** Folder containing `script.txt` (e.g. `videos/demo`). |
| `--mode` | `auto`, `manual` | Pipeline mode: automatic (Gemini plans cuts) or manual (pre-existing JSON files). |
| `--account` | Subfolder in `accounts/` | Applies style preset from channel profile (`cartoon`, `documentary`, etc.). |
| `--style` | Quoted string | Specifies visual art direction prompt for images. |
| `--voice-name` | `Puck`, `Charon`, `Kore`, `Fenrir`, `Aoede` | Voice timbre selection. |
| `--voice-style`| Descriptive string | Actor direction prompt (cadence, emotion, intonation). |
| `--skip-voice` | Flag | Skips TTS synthesis if `voix.mp3` already exists. |
| `--skip-flow`  | Flag | Skips Flow image generation (uses existing candidates). |
| `--render-only`| Flag | Re-renders final video from existing assets without re-running earlier steps. |
| `--web-only`   | Flag | Launches only the web selection interface (`http://localhost:8765/`). |
| `--fps`        | `30`, `60` | Output frame rate (default: 30 fps; 60 fps recommended for maximum smoothness). |
| `--sub-pos`    | `top`, `center`, `bottom` | Preset vertical position for subtitles. |
| `--sub-y`      | Float between `0.0` and `1.0` | Custom vertical position from top (`0.68` = ideal for TikTok). |
| `--sub-size`   | Integer (e.g. `70`) | Subtitle font size. |
| `--sub-accent` | Hex code or `none` | Active spoken word highlight color (e.g. `"#FFE600"`, `none` for monochrome). |
| `--sub-color`  | Hex code | Inactive subtitle text color (e.g. `"#FFFFFF"`). |
| `--no-subtitles`| Flag | Disables subtitles completely. |
| `--zoom-mode`  | `alternate`, `in`, `out`, `none` | Ken Burns camera zoom direction. |
| `--zoom-intensity` | Float (e.g. `0.08`) | Zoom scale amplitude. |
| `--no-zoom`    | Flag | Disables camera zoom (static frames). |
| `--no-shake`   | Flag | Disables camera shake effects. |
| `--no-keywords`| Flag | Disables top uppercase keyword banners. |

---

## 11. FAQ & Troubleshooting

#### Q1: Terminal displays `'ffmpeg' is not recognized` or `ffmpeg: command not found`
> **Cause:** FFmpeg is not installed or not present in your system PATH.  
> **Solution:**  
> - On Windows: Open an administrator terminal and run `winget install Gyan.FFmpeg`, then restart your terminal.  
> - On macOS: Run `brew install ffmpeg`.  
> - Verify by typing `ffmpeg -version`.

#### Q2: Terminal displays `GEMINI_API_KEY environment variable is not defined`
> **Cause:** The `.env` file is missing or lacks a valid key.  
> **Solution:** Duplicate `.env.example`, rename it to `.env`, and insert: `GEMINI_API_KEY="your_actual_key"`.

#### Q3: Terminal displays `Cannot connect to host 127.0.0.1:9222` or CDP error
> **Cause:** Google Chrome was not launched with remote debugging port 9222.  
> **Solution:** Run `./flow/start_chrome.sh` (macOS/Linux) or `flow\start_chrome.bat` (Windows). Keep the opened Chrome window active.

#### Q4: Google Flow shows a CAPTCHA or prompts for confirmation
> **Cause:** Google occasionally requests human verification.  
> **Solution:** Switch to the Chrome window, solve the CAPTCHA manually, then resume your terminal command.

#### Q5: How do I change the subtitle font?
> **Solution:** Drop your font file (`.ttf` or `.otf`) into `assets/fonts/` (or `accounts/<account>/fonts/`), then set `"font": "MyFont.ttf"` in your `config.json`.

#### Q6: Generated images don't match my target theme
> **Cause:** Either the prompt in `style.txt` is too ambiguous, or Chrome is opened to an incorrect Flow project.  
> **Solution:** Verify the active Flow project in Chrome and refine your visual description in `style.txt`.

#### Q7: How do I export in 60 frames per second (60 fps)?
> **Solution:** Add `--fps 60` to your CLI command:
> ```bash
> python main.py videos/my_video --fps 60
> ```

---

## 12. Repository Structure

```text
script-to-short/
├── .env.example              # Environment variables template with explanations
├── .gitignore                # Git ignore rules (secrets, caches, heavy renders)
├── LICENSE                   # MIT License
├── README.md                 # Complete project documentation
├── requirements.txt          # Python dependencies
├── main.py                   # Unified CLI entry point
│
├── core/                     # Production engine
│   ├── voice.py              # Gemini TTS synthesis + broadcast -14 LUFS normalization
│   ├── transcribe.py         # Word-level timestamping via Faster-Whisper
│   ├── scene_planner.py      # LLM scene breakdown & prompt engineering
│   ├── timeline.py           # Audio-subtitle alignment & cut synchronizer
│   ├── renderer.py           # 60 fps video rendering engine (Pillow + FFmpeg)
│   ├── account_manager.py    # Channel profile presets & font resolution
│   └── utils.py              # Path and logging helpers
│
├── flow/                     # Google Flow browser automation
│   ├── flow_auto.py          # Playwright CDP driver for Google Flow
│   ├── flow_fast.py          # Parallel queue worker & image downloader
│   ├── choisir_web.py        # Local web selection interface (port 8765)
│   ├── build_prompts.py      # 9:16 visual prompt builder
│   ├── start_chrome.sh       # Chrome debug launcher (macOS / Linux)
│   └── start_chrome.bat      # Chrome debug launcher (Windows)
│
├── accounts/                 # Pre-configured channel profile presets
│   ├── _template/            # Starter template for new channels
│   ├── cartoon/              # 2D stickman / cartoon aesthetic
│   ├── documentary/          # Cinematic history / documentary aesthetic
│   ├── medical/              # Clean 3D biology & science aesthetic
│   └── horror/               # Atmospheric horror / mystery aesthetic
│
├── assets/
│   ├── fonts/                # Subtitle typeface storage
│   └── sfx/                  # Royalty-free sound effects (whoosh, pop, tic...)
│
└── videos/
    └── demo/                 # Ready-to-test demonstration project
```

---

## 13. License

Distributed under the **MIT License**. Free for personal and commercial use. See [LICENSE](LICENSE) for details.

---

## 14. Disclaimer & Legal Notice

> [!NOTE]
> ### ⚖️ Ethical & Legal Usage
> This project is developed for personal research, educational experimentation, and technical demonstration (Proof of Concept).
> Browser automation leverages the user's local authenticated session via Chrome DevTools Protocol (CDP) to bridge the absence of a public REST API on Google Labs.
> Users are expected to comply with the Terms of Service of third-party platforms. Official APIs (such as Vertex AI / Imagen 3) remain the recommended approach upon public availability.
