"""Built-in model registry entries. Adding a new model = adding a row here + a predictor."""
from __future__ import annotations

from .base import ModelMeta


CAT_DOG = ModelMeta(
    model_id="cat-dog",
    name="猫狗图像二分类",
    name_en="Cat-Dog Classifier",
    task_type="image_classification",
    input_type="image",
    output_type="classification",
    description="上传一张猫或狗的照片，模型判断它属于哪一类。",
    enabled=True,
    sort_order=10,
    capabilities=["predict"],
    supported_file_types=["image/jpeg", "image/jpg", "image/png", "image/webp"],
    max_upload_mb=5,
)


ALL_MODELS: list[ModelMeta] = [CAT_DOG]


def default_models() -> list[ModelMeta]:
    return [m for m in ALL_MODELS]
