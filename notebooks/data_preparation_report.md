# Data Preparation Report

## Summary
Processed WAVs: 1400
Spectrograms extracted: 1400

## Spectrogram parameters
- n_mels: 64
- n_fft: 1024
- hop_length: 512
- power: 2.0

## Train/Val/Test splits
- train: 979
- val: 210
- test: 211

## Notes
- Spectrograms are saved as log-mel dB arrays (.npy) and PNG previews under data/spectrograms/preview/.
- If stratified splitting failed due to small classes, a random split was used as a fallback.