from pathlib import Path
import soundfile as sf
import numpy as np
import os

DATA_ROOT = Path(".").resolve()
PROCESSED = DATA_ROOT / "data" / "processed"
SPECS = DATA_ROOT / "data" / "spectrograms"

expected_sr = 22050
expected_dur = 10.0

wav_files = list(PROCESSED.glob("**/*.wav"))
print(f"Found {len(wav_files)} WAV files under {PROCESSED}")

bad_sr = []
bad_dur = []
bad_mono = []
bad_nans = []

for p in wav_files:
    try:
        y, sr = sf.read(p, dtype='float32')
    except Exception as e:
        print(f"Failed to read {p}: {e}")
        continue
    # ensure mono
    if y.ndim > 1:
        # soundfile returns (n_samples, n_channels)
        chan = y.shape[1]
        if chan != 1:
            bad_mono.append((str(p), chan))
        # collapse for checks
        y_mono = np.mean(y, axis=1)
    else:
        y_mono = y
    # sample rate
    if int(sr) != expected_sr:
        bad_sr.append((str(p), sr))
    # duration approx
    dur = len(y_mono) / float(sr) if sr > 0 else 0.0
    if abs(dur - expected_dur) > 0.01:
        bad_dur.append((str(p), dur))
    # nans/infs
    if not np.isfinite(y_mono).all():
        bad_nans.append(str(p))

print()
print(f"Bad sample rates: {len(bad_sr)}")
if bad_sr:
    for a,b in bad_sr[:10]:
        print(a, 'sr=', b)
print()
print(f"Bad durations (not ~10s): {len(bad_dur)}")
if bad_dur:
    for a,b in bad_dur[:10]:
        print(a, 'dur=', b)
print()
print(f"Non-mono files: {len(bad_mono)}")
if bad_mono:
    for a,b in bad_mono[:10]:
        print(a, 'channels=', b)
print()
print(f"Files with non-finite samples: {len(bad_nans)}")
if bad_nans:
    for a in bad_nans[:10]:
        print(a)

# Quick spectrogram presence check for a few species
spec_missing = 0
for spec_file in wav_files[:50]:
    rel = spec_file.relative_to(PROCESSED)
    npy = SPECS / rel.with_suffix('.npy')
    if not npy.exists():
        spec_missing += 1

print()
print(f"In a quick check of first 50 WAVs, spectrogram .npy missing for: {spec_missing}")

# Summary counts per species
from collections import Counter
species_counts = Counter([p.parent.name for p in wav_files])
print('\nTop species by processed WAV count:')
for s,c in species_counts.most_common(10):
    print(f"{s}: {c}")

# Exit code: 0 if no major issues (no NaNs and all durations/sr correct), else 2
has_issues = len(bad_nans) + len(bad_dur) + len(bad_sr)
print('\nQA status: ' + ('OK' if has_issues==0 else 'ISSUES'))

if has_issues:
    raise SystemExit(2)
else:
    raise SystemExit(0)
