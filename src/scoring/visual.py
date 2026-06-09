import cv2
import numpy as np
from typing import cast

from .preprocess import PreprocessedImage


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _pil_to_bgr(image) -> np.ndarray:
    rgb = np.asarray(image.convert("RGB"))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def _lighting_uniformity_score(bgr: np.ndarray) -> float:
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    if h < 4 or w < 4:
        return 0.5

    grid = 3
    cell_h, cell_w = h // grid, w // grid
    means = []
    for row in range(grid):
        for col in range(grid):
            y0, y1 = row * cell_h, (row + 1) * cell_h
            x0, x1 = col * cell_w, (col + 1) * cell_w
            region = gray[y0:y1, x0:x1]
            if region.size:
                means.append(float(region.mean()))

    if len(means) < 2:
        return 0.5

    variance = float(np.var(means))
    # High variance across regions suggests inconsistent lighting / compositing.
    return _clamp(1.0 - min(variance / 2500.0, 1.0))


def _shadow_direction_score(bgr: np.ndarray) -> float:
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.sqrt(gx**2 + gy**2)
    angles = np.arctan2(gy, gx)

    mask = magnitude > np.percentile(magnitude, 75)
    if not mask.any():
        return 0.6

    hist, _ = np.histogram(angles[mask], bins=8, range=(-np.pi, np.pi))
    hist = hist.astype(np.float64)
    hist /= hist.sum() + 1e-6

    # Concentrated orientation histogram => consistent shadows.
    entropy = -np.sum(hist * np.log(hist + 1e-9))
    max_entropy = np.log(8)
    consistency = 1.0 - (entropy / max_entropy)
    return _clamp(0.4 + consistency * 0.6)


def _edge_blending_score(bgr: np.ndarray) -> float:
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 80, 160)
    if edges.sum() == 0:
        return 0.7

    edge_pixels = edges > 0
    local_var = cv2.GaussianBlur(
        cast(np.ndarray, (gray.astype(np.float32) - cv2.GaussianBlur(gray, (0, 0), 3)) ** 2),
        (0, 0),
        3,
    )
    edge_variance = float(local_var[edge_pixels].mean()) if edge_pixels.any() else 0.0

    # Spikes along edges can indicate blending artifacts.
    if edge_variance > 500.0:
        return _clamp(1.0 - (edge_variance - 500.0) / 1500.0)
    return _clamp(0.6 + edge_variance / 1000.0)


def score_visual(preprocessed: PreprocessedImage) -> float:
    bgr = _pil_to_bgr(preprocessed.original_image)
    lighting = _lighting_uniformity_score(bgr)
    shadow = _shadow_direction_score(bgr)
    blending = _edge_blending_score(bgr)
    return _clamp((lighting + shadow + blending) / 3.0)
