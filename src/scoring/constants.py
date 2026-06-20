from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Hand-tuned weights — provenance-heavy after golden-set calibration (Jun 2026).
WM = 0.20
WA = 0.20
WV = 0.15
WP = 0.45

THRESHOLD_NON_COMPLIANT = 0.3
THRESHOLD_COMPLIANT = 0.7

# Post-weight rules in scorer.py (see compute_authenticity_score).
PROVENANCE_MATCH_MIN = 0.90
PROVENANCE_MATCH_SCORE_FLOOR = 0.82
SYNTHETIC_PROFILE_PROVENANCE_MAX = 0.25
SYNTHETIC_PROFILE_METADATA_MAX = 0.50
SYNTHETIC_PROFILE_SCORE_CAP = 0.28

DEEPFAKE_MODEL_ID = "dima806/deepfake_vs_real_image_detection"
MODEL_INPUT_SIZE = 224

EDITING_SOFTWARE_TAGS = (
    "photoshop",
    "gimp",
    "stable diffusion",
    "midjourney",
    "dall-e",
    "dalle",
    "adobe",
    "lightroom",
    "canva",
    "affinity",
)

REQUIRED_EXIF_FIELDS = ("DateTimeOriginal", "Make", "Model")

# Sub-score weights inside signal extractors
ARTIFACT_CNN_WEIGHT = 0.5
ARTIFACT_FFT_WEIGHT = 0.25
ARTIFACT_NOISE_WEIGHT = 0.25

METADATA_PRESENCE_WEIGHT = 0.35
METADATA_FIELDS_WEIGHT = 0.35
METADATA_SOFTWARE_WEIGHT = 0.20
METADATA_TIMESTAMP_WEIGHT = 0.10

NO_EXIF_CAP = 0.4
PNG_WEBP_NO_EXIF_SCORE = 0.35

PHASH_MATCH_THRESHOLD = 10
AUTHENTIC_REFERENCE_DIR = PROJECT_ROOT / "qa" / "test_cases" / "authentic"
EMPTY_PROVENANCE_DEFAULT = 0.5

PLATT_ENABLED = False

SUPPORTED_MIME_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})
