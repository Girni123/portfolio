#!/usr/bin/env python3
"""
Erzeugt verkleinerte Versionen aller Bilder (480, 800 und 1200 px breit) in assets/opt/.
Das Original (max. 1600 px) bleibt die größte Stufe.
build.py nutzt sie automatisch per srcset, der Browser lädt nur die passende Größe.

    python3 tools/optimize_images.py

Braucht macOS (nutzt das eingebaute `sips`). Nach dem Hinzufügen neuer Bilder einmal ausführen.
Bereits erzeugte Varianten werden übersprungen, solange das Original nicht neuer ist.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from build import image_size, OPT_WIDTHS, OPT_DIRS, opt_path  # noqa: E402

QUALITY = '64'  # JPEG-Qualität


def main():
    made = skipped = 0
    for d in OPT_DIRS:
        for base, _, files in os.walk(os.path.join(ROOT, d)):
            for fn in sorted(files):
                if not fn.lower().endswith(('.jpg', '.jpeg', '.png')):
                    continue
                src = os.path.join(base, fn)
                rel = '/' + os.path.relpath(src, ROOT)
                dim = image_size(src)
                if not dim:
                    continue
                for w in OPT_WIDTHS:
                    if w >= dim[0] * 0.9:
                        continue
                    out = os.path.join(ROOT, opt_path(rel, w).lstrip('/'))
                    if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(src):
                        skipped += 1
                        continue
                    os.makedirs(os.path.dirname(out), exist_ok=True)
                    args = ['sips'] + ([] if out.endswith('.png') else ['-s', 'format', 'jpeg', '-s', 'formatOptions', QUALITY])
                    args += ['--resampleWidth', str(w)]
                    subprocess.run(args + [src, '--out', out], capture_output=True, check=True)
                    made += 1
    print(f'{made} Varianten erzeugt, {skipped} schon aktuell.')


if __name__ == '__main__':
    main()
