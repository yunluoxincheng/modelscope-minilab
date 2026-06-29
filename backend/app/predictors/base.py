"""Predictor base contract so future models share one interface."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PredictionResult:
    label: str
    label_cn: str
    confidence: float
    probabilities: Dict[str, float]
    extra: Dict[str, Any] = field(default_factory=dict)


class Predictor:
    """Generic predictor interface. Add new models by implementing this."""

    model_id: str = ""

    def predict(self, *, file_bytes: bytes, content_type: str, filename: Optional[str] = None) -> PredictionResult:
        raise NotImplementedError

    def warmup(self) -> None:  # pragma: no cover - optional hook
        return None
