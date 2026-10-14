"""Import native-speaker recordings for the language cards.

    uv run python scripts/import_audio.py ~/Downloads/recordings/*

Each file is matched to its phrase by name — "dziękuję.m4a", "Dziekuje.mp3"
and "dziekuje (1).wav" all match "dziękuję" — then converted with ffmpeg to
``memi_kr/static/audio/<slug>.mp3``: mono MP3 (every browser plays it; Chromium
and some Firefox builds can't play the AAC in phone voice memos), silence
trimmed at both ends, and loudness evened out across the different phones.
Files that match no phrase are listed and skipped.
"""

import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from memi_kr.providers.categories import AUDIO_DIR, PHRASES, phrase_slug  # noqa: E402

TRIM = "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.1"
FILTERS = ",".join([TRIM, "areverse", TRIM, "areverse", "loudnorm=I=-16:TP=-1.5:LRA=11"])


def main(paths):
    known = {phrase_slug(polish): polish for polish in PHRASES.values()}
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    done, skipped = [], []
    for path in map(Path, paths):
        # Drop copy suffixes like " (1)" before matching.
        slug = phrase_slug(re.sub(r"\s*\(\d+\)$", "", path.stem))
        if slug not in known:
            skipped.append(path.name)
            continue
        out = AUDIO_DIR / f"{slug}.mp3"
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(path), "-af", FILTERS,
             "-ac", "1", "-ar", "44100", "-b:a", "96k", str(out)],
            check=True,
        )
        # A recording in another format for the same phrase would shadow this one.
        for old in AUDIO_DIR.glob(f"{slug}.*"):
            if old != out:
                old.unlink()
        done.append(known[slug])
        print(f"{path.name:32} -> {out.name}")
    missing = sorted(polish for slug, polish in known.items()
                     if not (AUDIO_DIR / f"{slug}.mp3").exists())
    if skipped:
        print("\nNo matching phrase (rename and rerun):", ", ".join(skipped))
    print(f"\nStill without a recording ({len(missing)}):", ", ".join(missing) or "none")


if __name__ == "__main__":
    main(sys.argv[1:])
