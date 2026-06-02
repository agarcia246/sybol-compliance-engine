# qa/test_cases/ — Youssef

Create four subfolders here and populate them with labeled images:

authentic/
  Real camera photos with EXIF metadata intact.
  These should score 0.8–1.0 → complianceStatus: compliant.

ai_generated/
  Outputs from Midjourney, DALL·E, or Stable Diffusion.
  These should score 0.0–0.3 → complianceStatus: non-compliant.

edited/
  Real photos that have been Photoshopped, filtered, or composited.
  These should score 0.3–0.7 → complianceStatus: review.

corrupted/
  Malformed files, wrong extensions, unsupported formats.
  Used for TC-004 — system should return a clean error, not crash.

Aim for at least 5–10 images per category.
Label each image clearly in the filename so the category is obvious.
You can start this now — it does not depend on anyone else's work.
