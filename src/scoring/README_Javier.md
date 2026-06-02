# src/scoring/ — Javier

This folder is the full media scoring pipeline. You own everything here.

Input
Image file — JPEG, PNG, or WebP.

Step 1 — Preprocessing
- Resize to 224×224 for model input
- Convert to RGB
- Extract EXIF with ExifRead BEFORE any transformation
- Preserve original resolution for hashing

Step 2 — Signal Extraction
Extract four signals independently:

m — Metadata integrity
Check for missing EXIF fields, editing software tags (Photoshop, GIMP,
Stable Diffusion), and timestamp anomalies.

a — Generative artifact detection
Run HuggingFace CNN (dima806/deepfake_vs_real_image_detection),
FFT frequency analysis, and noise residual analysis.

v — Visual consistency
OpenCV checks: lighting uniformity, shadow direction, edge blending artifacts.
FACIAL LANDMARKS ARE EXPLICITLY EXCLUDED — do not add them under any
circumstances. Reason: GDPR Art. 4(14) biometric data classification +
AI Act Art. 5 prohibited practices.

p — Provenance
pHash comparison against known authentic dataset using imagehash.
NO third-party reverse image lookup. Reason: GDPR Arts. 28 and 44
joint controllership risk.

Step 3 — Feature Vector
Assemble X = [m, a, v, p]

Step 4 — Scoring
S = wm·m + wa·a + wv·v + wp·p
Calibrate with Platt scaling.

Step 5 — Interpret
0.0–0.3 → non-compliant
0.3–0.7 → review
0.7–1.0 → compliant

Output
- Float score 0.0 → 1.0
- Signal breakdown [m, a, v, p]
- complianceStatus
- SHA-256 hash of original file before resizing

Hand the output to the credentials folder once scoring is working.
