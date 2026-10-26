import json
import os
import sys
from pathlib import Path

from .utils import get_project_root, log_step

DEFAULT_ACCOUNT = "cartoon"

DEFAULT_CONFIG = {
    "name": "cartoon",
    "subtitles": {
        "font": "Arial Rounded Bold",
        "size": 70,
        "active_color": [255, 212, 59],
        "inactive_color": [255, 255, 255],
        "stroke_color": [0, 0, 0],
        "stroke_width": 6,
        "y_percent": 0.70,
        "uppercase": True
    },
    "editing": {
        "min_scene_dur": 1.0,
        "max_scene_dur": 2.2,
        "keyword_font_size": 150,
        "show_keywords": True,
        "sfx_pack": "cartoon"
    },
    "voice": {
        "name": "Puck",
        "style": (
            "A dynamic, engaging narrator voice for short-form video. "
            "Lively rhythm and crisp pronunciation with natural pacing."
        )
    },
    "flow": {
        "prefixes": {}
    }
}


def get_accounts_root() -> Path:
    return get_project_root() / "accounts"


def list_accounts() -> list:
    root = get_accounts_root()
    if not root.is_dir():
        return []
    return [
        d.name for d in root.iterdir()
        if d.is_dir() and not d.name.startswith((".", "_"))
    ]


def detect_account_name(target_dir: str, explicit_account: str = None) -> str:
    if explicit_account:
        return explicit_account

    target_path = Path(target_dir).resolve()
    marker_file = target_path / "account.txt"

    if marker_file.is_file():
        try:
            acc = marker_file.read_text(encoding="utf-8").strip()
            if acc:
                return acc
        except Exception:
            pass

    known_accounts = list_accounts()
    parent_dir = target_path.parent.name
    grandparent_dir = target_path.parent.parent.name

    if grandparent_dir.lower() == "videos" and parent_dir in known_accounts:
        return parent_dir

    if parent_dir in known_accounts:
        return parent_dir

    base_name = target_path.name.lower()
    for acc in known_accounts:
        if base_name.startswith(acc.lower()):
            return acc

    return DEFAULT_ACCOUNT


def get_account_dir(account_name: str) -> Path:
    return get_accounts_root() / account_name


def load_account_config(account_name: str, video_dir: str = None) -> dict:
    acc_dir = get_account_dir(account_name)
    config_path = acc_dir / "config.json"

    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    cfg["name"] = account_name

    if config_path.is_file():
        try:
            user_cfg = json.loads(config_path.read_text(encoding="utf-8"))
            for k, v in user_cfg.items():
                if isinstance(v, dict) and k in cfg and isinstance(cfg[k], dict):
                    cfg[k].update(v)
                else:
                    cfg[k] = v
        except Exception as e:
            log_step("ACCOUNT", f"Warning: Failed to load {config_path}: {e}")

    if video_dir:
        vid_cfg_path = Path(video_dir) / "config.json"
        if vid_cfg_path.is_file():
            try:
                vid_cfg = json.loads(vid_cfg_path.read_text(encoding="utf-8"))
                for k, v in vid_cfg.items():
                    if isinstance(v, dict) and k in cfg and isinstance(cfg[k], dict):
                        cfg[k].update(v)
                    else:
                        cfg[k] = v
            except Exception as e:
                log_step("ACCOUNT", f"Warning: Failed to load {vid_cfg_path}: {e}")

    return cfg


def load_account_prompt_template(account_name: str) -> str:
    acc_dir = get_account_dir(account_name)
    prompt_file = acc_dir / "prompt.txt"
    if prompt_file.is_file():
        try:
            return prompt_file.read_text(encoding="utf-8").strip()
        except Exception as e:
            log_step("ACCOUNT", f"Warning: Failed to load {prompt_file}: {e}")
    return ""


def save_account_marker(target_dir: str, account_name: str):
    target_path = Path(target_dir).resolve()
    marker_file = target_path / "account.txt"
    try:
        marker_file.write_text(f"{account_name}\n", encoding="utf-8")
    except Exception:
        pass


def resolve_font_path(font_spec: str, account_name: str = None) -> str:
    if not font_spec:
        font_spec = "Arial Rounded Bold"

    if os.path.isabs(font_spec) and os.path.exists(font_spec):
        return font_spec

    # 1. Check account font folder
    if account_name:
        acc_fonts = get_account_dir(account_name) / "fonts"
        if acc_fonts.is_dir():
            cand = acc_fonts / font_spec
            if cand.is_file():
                return str(cand)
            for ext in [".ttf", ".otf", ".ttc"]:
                if (acc_fonts / f"{font_spec}{ext}").is_file():
                    return str(acc_fonts / f"{font_spec}{ext}")

    # 2. Check global assets/fonts folder
    assets_fonts = get_project_root() / "assets" / "fonts"
    if assets_fonts.is_dir():
        cand = assets_fonts / font_spec
        if cand.is_file():
            return str(cand)
        for ext in [".ttf", ".otf", ".ttc"]:
            if (assets_fonts / f"{font_spec}{ext}").is_file():
                return str(assets_fonts / f"{font_spec}{ext}")

    # 3. System font directories across OS
    system_dirs = []
    if sys.platform == "darwin":
        system_dirs = [
            Path("/System/Library/Fonts/Supplemental"),
            Path("/System/Library/Fonts"),
            Path("/Library/Fonts"),
            Path.home() / "Library/Fonts"
        ]
    elif sys.platform.startswith("linux"):
        system_dirs = [
            Path("/usr/share/fonts"),
            Path("/usr/local/share/fonts"),
            Path.home() / ".fonts",
            Path.home() / ".local/share/fonts"
        ]
    elif sys.platform in ("win32", "cygwin"):
        windir = os.environ.get("WINDIR", "C:\\Windows")
        system_dirs = [Path(windir) / "Fonts"]

    spec_clean = font_spec.lower().replace(".ttf", "").replace(".otf", "").replace(".ttc", "").strip()

    for directory in system_dirs:
        if not directory.is_dir():
            continue
        try:
            for item in directory.rglob("*"):
                if item.is_file() and item.suffix.lower() in [".ttf", ".otf", ".ttc"]:
                    if item.stem.lower() == spec_clean or spec_clean in item.stem.lower():
                        return str(item)
        except Exception:
            continue

    # 4. Fallback search for any clean sans-serif font
    fallbacks = [
        "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf"
    ]
    for fb in fallbacks:
        if os.path.exists(fb):
            return fb

    return font_spec
