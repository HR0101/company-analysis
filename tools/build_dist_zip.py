#!/usr/bin/env python3
"""Build dist/company-analysis-skill.zip for Claude Desktop App / Claude.ai upload."""

from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent.parent
SKILL_NAME = "company-analysis"
SKILL_DIR = ROOT / "skills" / SKILL_NAME
OUT_ZIP = ROOT / "dist" / f"{SKILL_NAME}-skill.zip"


def build_zip() -> Path:
    OUT_ZIP.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(
        p for p in SKILL_DIR.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and not p.name.startswith(".")
    )
    with zipfile.ZipFile(OUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in files:
            rel = file_path.relative_to(SKILL_DIR).as_posix()
            arcname = f"{SKILL_NAME}/{rel}"
            info = zipfile.ZipInfo(arcname)
            info.date_time = (2026, 4, 12, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if file_path.suffix == ".py" else 0o644) << 16
            zf.writestr(info, file_path.read_bytes())
    return OUT_ZIP


if __name__ == "__main__":
    out = build_zip()
    print(f"Built {out.relative_to(ROOT)}")
