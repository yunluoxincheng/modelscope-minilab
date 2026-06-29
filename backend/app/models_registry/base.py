"""Model metadata definition shared by registry entries."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class ModelMeta:
    """Static metadata describing one model served by the platform."""

    model_id: str
    name: str
    name_en: str
    task_type: str
    input_type: str
    output_type: str = "classification"
    description: str = ""
    enabled: bool = True
    sort_order: int = 100
    cover_url: Optional[str] = None
    supported_file_types: List[str] = field(default_factory=lambda: ["image/jpeg", "image/jpg", "image/png", "image/webp"])
    capabilities: List[str] = field(default_factory=lambda: ["predict"])
    max_upload_mb: int = 5

    def to_public_dict(self, *, max_upload_mb_override: Optional[int] = None) -> dict:
        return {
            "model_id": self.model_id,
            "name": self.name,
            "name_en": self.name_en,
            "description": self.description,
            "task_type": self.task_type,
            "input_type": self.input_type,
            "output_type": self.output_type,
            "enabled": self.enabled,
            "cover_url": self.cover_url,
        }

    def to_detail_dict(self, settings) -> dict:
        data = self.to_public_dict()
        data["supported_file_types"] = list(settings.allowed_image_types)
        data["max_upload_mb"] = settings.max_upload_mb
        data["capabilities"] = list(self.capabilities)
        return data
