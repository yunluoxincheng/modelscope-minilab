"""Application settings loaded from environment variables."""
from __future__ import annotations

from functools import lru_cache
from typing import Annotated, List

from pydantic import BeforeValidator, Field
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


def _csv_to_list(value):
    """Accept either a real list or a comma-separated string from .env."""
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    if isinstance(value, (list, tuple)):
        return [str(item).strip() for item in value if str(item).strip()]
    return value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "ModelScope MiniLab"
    app_name_cn: str = "智模工坊"
    env: str = Field(default="dev", description="dev/staging/prod")
    debug: bool = False
    api_prefix: str = "/api"

    database_url: str = Field(
        default="sqlite:///./minilab.db",
        description="SQLAlchemy database URL. Use sqlite:///./minilab.db for dev, mysql+pymysql://... for prod.",
    )
    redis_url: str = Field(default="redis://localhost:6379/0")

    jwt_secret: str = Field(default="dev-insecure-secret-change-me")
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24 * 7

    wechat_app_id: str = ""
    wechat_app_secret: str = ""
    wechat_auth_mock: bool = Field(
        default=False,
        description="When True, skip real WeChat code2Session exchange and trust the code as openid. NEVER enable in production.",
    )

    predict_rate_per_user_per_minute: int = 20
    predict_rate_per_ip_per_minute: int = 60
    public_rate_per_ip_per_minute: int = 120

    max_upload_mb: int = 5
    allowed_image_types: Annotated[List[str], NoDecode, BeforeValidator(_csv_to_list)] = Field(
        default_factory=lambda: ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    )

    cat_dog_ensemble_weights: str = "5:1:3"
    cat_dog_v2_path: str = "ml_assets/cat_dog/checkpoints/efficientnet_b0_v2.pth"
    cat_dog_v3_path: str = "ml_assets/cat_dog/checkpoints/efficientnet_b0_v3.pth"
    cat_dog_v4_path: str = "ml_assets/cat_dog/checkpoints/efficientnet_b0_v4.pth"
    cat_dog_img_size: int = 256
    cat_dog_threshold: float = 0.5
    cat_dog_fast_mode: bool = False
    cat_dog_enable: bool = True

    service_window_start: str = Field(default="10:00", description="HH:MM; set empty to disable.")
    service_window_end: str = Field(default="18:00")
    service_window_enforce: bool = False

    cors_allow_origins: Annotated[List[str], NoDecode, BeforeValidator(_csv_to_list)] = Field(
        default_factory=list
    )

    @property
    def ensemble_weights_list(self) -> List[float]:
        parts = [float(p) for p in self.cat_dog_ensemble_weights.split(":")]
        if len(parts) != 3 or any(w < 0 for w in parts):
            raise ValueError("cat_dog_ensemble_weights must be three non-negative numbers like 5:1:3")
        return parts

    @property
    def service_enabled(self) -> bool:
        if not self.service_window_enforce:
            return True
        if not self.service_window_start or not self.service_window_end:
            return True
        import datetime as _dt
        from datetime import timezone, timedelta

        # 固定 UTC+8 取北京时间，不依赖容器 tzdata（slim 镜像未装 zoneinfo 数据库，
        # ENV TZ=Asia/Shanghai 实际不生效，否则会按 UTC 判断导致窗口错位）。
        now = _dt.datetime.now(timezone(timedelta(hours=8))).time()
        start = _dt.datetime.strptime(self.service_window_start, "%H:%M").time()
        end = _dt.datetime.strptime(self.service_window_end, "%H:%M").time()
        return start <= now <= end


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
