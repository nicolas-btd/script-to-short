import os
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_env(target_dir: str = None) -> dict:
    candidates = []
    if target_dir:
        candidates.append(Path(target_dir) / ".env")
    candidates.append(Path.cwd() / ".env")
    candidates.append(get_project_root() / ".env")

    for candidate in candidates:
        if candidate.is_file():
            try:
                for line in candidate.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, val = line.split("=", 1)
                        key = key.strip()
                        val = val.strip().strip("\"'")
                        if key and key not in os.environ:
                            os.environ[key] = val
            except Exception:
                pass
            break
    return os.environ


def log_step(step: str, detail: str = ""):
    if detail:
        print(f"[{step}] {detail}", flush=True)
    else:
        print(f"[{step}]", flush=True)
