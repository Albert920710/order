from io import BytesIO
from pathlib import Path

import numpy as np
from fastapi import APIRouter, Depends, UploadFile, File
from PIL import Image
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session

from ..auth import require_role
from ..database import get_db
from ..models import ProductAttributeOption, ProductImage

router = APIRouter(prefix="/api/search", tags=["search"])
INDEX_PATH = Path("media/image_index.pkl")
MODEL_NAME = "clip-ViT-B-32"
_model = None
_index_cache = None
_index_mtime = None
TOP_K = 6


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def load_index():
    global _index_cache, _index_mtime
    if not INDEX_PATH.exists():
        return None
    mtime = INDEX_PATH.stat().st_mtime
    if _index_cache is None or _index_mtime != mtime:
        import pickle

        with INDEX_PATH.open("rb") as handle:
            _index_cache = pickle.load(handle)
        _index_mtime = mtime
    return _index_cache


def normalize_paths(paths):
    normalized = []
    for path in paths:
        path_obj = Path(path)
        if path_obj.is_absolute():
            try:
                path_obj = path_obj.relative_to(Path.cwd())
            except ValueError:
                pass
        if path_obj.parts and path_obj.parts[0] == "media":
            normalized.append(f"/{'/'.join(path_obj.parts)}")
        else:
            normalized.append(f"/media/{path_obj.name}")
    return normalized


def load_images(folder: Path):
    for path in folder.glob("**/*"):
        if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            yield path


@router.post("/image")
async def search_by_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(require_role("sales", "admin")),
):
    index_data = load_index()
    if not index_data:
        return {
            "message": "索引服务未启动，请先由管理员完成索引",
            "matches": [],
        }
    embeddings = index_data.get("embeddings")
    files = index_data.get("files", [])
    if embeddings is None or len(files) == 0:
        return {"message": "索引中没有图片，请重新构建索引", "matches": []}

    image_bytes = await file.read()
    try:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
    except Exception:
        return {"message": "无法解析图片，请更换文件后重试", "matches": []}

    model = get_model()
    query = model.encode(image)
    query = query / np.linalg.norm(query)
    vectors = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    scores = np.dot(vectors, query)
    top_indices = np.argsort(scores)[::-1][:TOP_K]

    normalized_urls = normalize_paths([files[i] for i in top_indices])
    option_matches = (
        db.query(ProductAttributeOption)
        .filter(ProductAttributeOption.image_url.in_(normalized_urls))
        .all()
    )
    image_matches = (
        db.query(ProductImage).filter(ProductImage.image_url.in_(normalized_urls)).all()
    )
    option_map = {option.image_url: option for option in option_matches}
    image_map = {image.image_url: image for image in image_matches}

    matches = []
    for idx in top_indices:
        url = normalize_paths([files[idx]])[0]
        if url in option_map:
            option = option_map[url]
            matches.append(
                {
                    "id": option.id,
                    "label": option.label,
                    "image_url": option.image_url,
                    "attribute_id": option.attribute_id,
                    "score": float(scores[idx]),
                    "type": "option",
                }
            )
        if url in image_map:
            image = image_map[url]
            matches.append(
                {
                    "id": image.id,
                    "image_url": image.image_url,
                    "product_id": image.product_id,
                    "score": float(scores[idx]),
                    "type": "product",
                }
            )
    return {"message": "ok", "matches": matches}


@router.post("/index")
def build_index(user=Depends(require_role("admin"))):
    media_dir = Path("media")
    if not media_dir.exists():
        return {"message": "media 目录不存在", "total_images": 0, "status": "failed"}
    try:
        model = get_model()
        embeddings = []
        files = []
        for image_path in load_images(media_dir):
            try:
                image = Image.open(image_path).convert("RGB")
                embedding = model.encode(image)
                embeddings.append(embedding)
                files.append(str(image_path))
            except Exception:
                continue
        data = {"files": files, "embeddings": np.array(embeddings)}
        import pickle

        INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        with INDEX_PATH.open("wb") as handle:
            pickle.dump(data, handle)
        return {
            "message": "索引完成",
            "total_images": len(files),
            "status": "completed",
        }
    except Exception as exc:
        return {"message": f"索引失败: {exc}", "total_images": 0, "status": "failed"}
