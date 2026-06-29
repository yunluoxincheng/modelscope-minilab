"""Predictor factory: route model_id to the right Predictor implementation."""
from __future__ import annotations

from typing import Dict

from .base import Predictor
from .cat_dog import CatDogPredictor


_registry: Dict[str, Predictor] = {}


def get_predictor(model_id: str) -> Predictor:
    if model_id not in _registry:
        if model_id == "cat-dog":
            _registry[model_id] = CatDogPredictor()
        else:
            raise KeyError(f"no predictor for model_id={model_id!r}")
    return _registry[model_id]


def reset_for_tests() -> None:
    _registry.clear()
