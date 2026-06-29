"""Cat-Dog EfficientNet-B0 v2/v3/v4 weighted ensemble predictor."""
from __future__ import annotations

import io
import logging
import os
import threading
import time
from typing import List, Optional

import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

from ..core.errors import InvalidImageError
from ..core.settings import Settings, get_settings
from .base import PredictionResult, Predictor

log = logging.getLogger(__name__)

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


class CatDogPredictor(Predictor):
    """Loads EfficientNet-B0 v2/v3/v4 once and ensembles their dog probabilities."""

    model_id = "cat-dog"

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self._lock = threading.Lock()
        self._models: List[torch.nn.Module] = []
        self._weights: List[float] = []
        self._device: torch.device = torch.device("cpu")
        self._transform = transforms.Compose(
            [
                transforms.Resize((self.settings.cat_dog_img_size, self.settings.cat_dog_img_size)),
                transforms.ToTensor(),
                transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
            ]
        )
        self._loaded = False

    def _resolve_path(self, candidate: str) -> str:
        # Resolve relative paths against backend/ root (cwd at runtime).
        if os.path.isabs(candidate) and os.path.exists(candidate):
            return candidate
        if os.path.exists(candidate):
            return candidate
        # Backend root is two levels up from this file (app/predictors -> backend/).
        backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        tried = [
            candidate,
            os.path.join(backend_root, candidate),
            os.path.join(backend_root, "ml_assets", "cat_dog", "checkpoints", os.path.basename(candidate)),
        ]
        for path in tried:
            if os.path.exists(path):
                return path
        raise FileNotFoundError(f"checkpoint not found: {candidate}")

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        with self._lock:
            if self._loaded:
                return
            from ml_assets.cat_dog.model import build_model  # backend/ is on sys.path

            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self._device = device
            weights = self.settings.ensemble_weights_list

            candidates: List[tuple[float, str]] = [
                (weights[0], self.settings.cat_dog_v2_path),
                (weights[1], self.settings.cat_dog_v3_path),
                (weights[2], self.settings.cat_dog_v4_path),
            ]
            if self.settings.cat_dog_fast_mode:
                log.warning("cat_dog_fast_mode enabled: using only EfficientNet-B0 v2")
                candidates = candidates[:1]

            loaded: List[torch.nn.Module] = []
            loaded_weights: List[float] = []
            for weight, path in candidates:
                resolved = self._resolve_path(path)
                net = build_model().to(device)
                state = torch.load(resolved, map_location=device, weights_only=True)
                net.load_state_dict(state)
                net.eval()
                loaded.append(net)
                loaded_weights.append(weight)
                log.info("loaded cat_dog checkpoint weight=%s path=%s", weight, resolved)

            total = sum(loaded_weights) or 1.0
            self._weights = [w / total for w in loaded_weights]
            self._models = loaded
            self._loaded = True

    def _preprocess(self, file_bytes: bytes) -> torch.Tensor:
        try:
            img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        except Exception as exc:
            raise InvalidImageError() from exc
        return self._transform(img).unsqueeze(0).to(self._device)

    def predict(
        self,
        *,
        file_bytes: bytes,
        content_type: str,
        filename: Optional[str] = None,
    ) -> PredictionResult:
        self._ensure_loaded()
        start = time.perf_counter()
        tensor = self._preprocess(file_bytes)
        with torch.inference_mode():
            dog_probs: List[float] = []
            for net in self._models:
                logits = net(tensor).squeeze(-1)
                dog_probs.append(float(torch.sigmoid(logits).item()))

        weighted_dog = sum(p * w for p, w in zip(dog_probs, self._weights))
        weighted_cat = max(0.0, 1.0 - weighted_dog)
        threshold = self.settings.cat_dog_threshold
        is_dog = weighted_dog >= threshold
        label = "dog" if is_dog else "cat"
        label_cn = "狗" if is_dog else "猫"
        confidence = max(weighted_dog, weighted_cat)
        latency_ms = int((time.perf_counter() - start) * 1000)
        return PredictionResult(
            label=label,
            label_cn=label_cn,
            confidence=confidence,
            probabilities={"cat": weighted_cat, "dog": weighted_dog},
            extra={
                "latency_ms": latency_ms,
                "per_model_dog_prob": dog_probs,
            },
        )


_singleton: Optional[CatDogPredictor] = None


def get_cat_dog_predictor() -> CatDogPredictor:
    global _singleton
    if _singleton is None:
        _singleton = CatDogPredictor()
    return _singleton
