import argparse
import os
import pickle
from pathlib import Path

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    from PIL import Image
except ImportError as exc:  # pragma: no cover - optional runtime
    raise SystemExit(
        "Missing dependencies for image indexing. Install sentence-transformers and pillow."
    ) from exc


def load_images(folder: Path):
    for path in folder.glob("**/*"):
        if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            yield path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--media-dir", default="media", help="Folder with product images")
    parser.add_argument("--output", default="media/image_index.pkl")
    args = parser.parse_args()

    media_dir = Path(args.media_dir)
    model = SentenceTransformer("clip-ViT-B-32")

    embeddings = []
    files = []
    for image_path in load_images(media_dir):
        try:
            image = Image.open(image_path)
            embedding = model.encode(image)
            embeddings.append(embedding)
            files.append(str(image_path))
        except Exception as exc:
            print(f"Skip {image_path}: {exc}")

    data = {"files": files, "embeddings": np.array(embeddings)}
    with open(args.output, "wb") as handle:
        pickle.dump(data, handle)
    print(f"Indexed {len(files)} images -> {args.output}")


if __name__ == "__main__":
    main()
