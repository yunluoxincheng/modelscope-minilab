"""EfficientNet-B0 from-scratch cat-dog classifier definition.

Copied from the original dogsAndcatsSort/model.py training project.
The classifier outputs a single logit; sigmoid(logit) is the dog probability.
"""
from __future__ import annotations

import torch.nn as nn
from torchvision import models


class EfficientNetB0FromScratch(nn.Module):
    """From-scratch EfficientNet-B0 with a 1-logit cat-dog head."""

    def __init__(self) -> None:
        super().__init__()
        self.backbone = models.efficientnet_b0(weights=None)
        in_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(0.3, inplace=True),
            nn.Linear(in_features, 1),
        )

    def forward(self, x):
        return self.backbone(x)


def build_model() -> nn.Module:
    return EfficientNetB0FromScratch()
