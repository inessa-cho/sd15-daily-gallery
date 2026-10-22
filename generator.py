from __future__ import annotations

import json
import os
import random
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import torch
from diffusers import StableDiffusionPipeline

from config import (
    ARCHIVE_DIR,
    GUIDANCE_SCALE,
    HEIGHT,
    IMAGE_COUNT,
    MODEL_CACHE_DIR,
    MODEL_ID,
    OUTPUT_DIR,
    STEPS,
    SUBJECTS_FILE,
    WIDTH,
)

TIMEZONE = ZoneInfo(os.getenv("TZ", "Asia/Seoul"))


def load_subjects() -> list[dict]:
    payload = json.loads(SUBJECTS_FILE.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise RuntimeError("subjects.json must contain a non-empty JSON array")
    required = {"slug", "name", "category", "prompt", "negative_prompt"}
    valid = [item for item in payload if isinstance(item, dict) and required <= item.keys()]
    if not valid:
        raise RuntimeError("subjects.json contains no valid prompt entries")
    return valid


def choose_subjects(subjects: list[dict], count: int) -> list[dict]:
    if len(subjects) >= count:
        return random.sample(subjects, count)
    return [random.choice(subjects) for _ in range(count)]


def atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def build_pipeline() -> StableDiffusionPipeline:
    MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    pipe = StableDiffusionPipeline.from_pretrained(
        MODEL_ID,
        cache_dir=str(MODEL_CACHE_DIR),
        torch_dtype=torch.float32,
        safety_checker=None,
        requires_safety_checker=False,
    )
    pipe.enable_attention_slicing()
    pipe.enable_vae_slicing()
    return pipe.to("cpu")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now(TIMEZONE)
    date_key = now.strftime("%Y-%m-%d")
    generated_at = now.isoformat()
    archive_day = ARCHIVE_DIR / date_key
    archive_day.mkdir(parents=True, exist_ok=True)

    subjects = choose_subjects(load_subjects(), IMAGE_COUNT)
    pipe = build_pipeline()
    items: list[dict] = []

    for index, subject in enumerate(subjects, start=1):
        seed = random.SystemRandom().randint(0, 2**32 - 1)
        generator = torch.Generator(device="cpu").manual_seed(seed)
        print(f"[INFO] {index}/{IMAGE_COUNT}: {subject['name']} (seed={seed})", flush=True)

        image = pipe(
            prompt=subject["prompt"],
            negative_prompt=subject["negative_prompt"],
            width=WIDTH,
            height=HEIGHT,
            num_inference_steps=STEPS,
            guidance_scale=GUIDANCE_SCALE,
            generator=generator,
        ).images[0]

        filename = f"image-{index}.webp"
        output_path = OUTPUT_DIR / filename
        temp_path = OUTPUT_DIR / f".{filename}.tmp.webp"
        image.save(temp_path, format="WEBP", quality=92, method=6)
        os.replace(temp_path, output_path)
        shutil.copy2(output_path, archive_day / filename)

        items.append(
            {
                "image": filename,
                "slug": subject["slug"],
                "name": subject["name"],
                "category": subject["category"],
                "prompt": subject["prompt"],
                "negativePrompt": subject["negative_prompt"],
                "seed": seed,
                "model": MODEL_ID,
                "generatedAt": generated_at,
            }
        )

    manifest = {
        "date": date_key,
        "generatedAt": generated_at,
        "imageCount": len(items),
        "items": items,
    }
    atomic_write_json(OUTPUT_DIR / "latest.json", manifest)
    atomic_write_json(archive_day / "latest.json", manifest)
    print(f"[INFO] completed: {len(items)} images", flush=True)


if __name__ == "__main__":
    main()
