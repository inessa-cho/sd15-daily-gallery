from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_ID = os.getenv("MODEL_ID", "runwayml/stable-diffusion-v1-5")
SUBJECTS_FILE = Path(os.getenv("SUBJECTS_FILE", BASE_DIR / "subjects.json"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", BASE_DIR / "output"))
ARCHIVE_DIR = OUTPUT_DIR / "archive"
IMAGE_COUNT = int(os.getenv("IMAGE_COUNT", "5"))
WIDTH = int(os.getenv("WIDTH", "512"))
HEIGHT = int(os.getenv("HEIGHT", "512"))
STEPS = int(os.getenv("STEPS", "28"))
GUIDANCE_SCALE = float(os.getenv("GUIDANCE_SCALE", "7.5"))
MODEL_CACHE_DIR = Path(os.getenv("HF_HOME", BASE_DIR / "model-cache" / "huggingface"))
