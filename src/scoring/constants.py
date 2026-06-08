from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Hand-tuned weights — bias toward metadata and artifact signals.
WM = 0.30
WA = 0.30
WV = 0.20
WP = 0.20

THRESHOLD_NON_COMPLIANT = 0.3
THRESHOLD_COMPLIANT = 0.7

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
PNG_WEBP_NO_EXIF_SCORE = 0.55

PHASH_MATCH_THRESHOLD = 10
AUTHENTIC_REFERENCE_DIR = PROJECT_ROOT / "qa" / "test_cases" / "authentic"
EMPTY_PROVENANCE_DEFAULT = 0.5

PLATT_ENABLED = False

SUPPORTED_MIME_TYPES = frozenset(
    {"image/jpeg", "image/png", "image/webp"}
)
