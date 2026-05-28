from __future__ import annotations

from pathlib import Path

from pydantic import Field, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    elevators_count: int = Field(1, validation_alias="ELEVATORS_COUNT")
    floors_count: int = Field(12, validation_alias="FLOORS_COUNT")

    assets_media_dir: str = Field("assets/media", validation_alias="ASSETS_MEDIA_DIR")
    ding_sound: str = Field("ding.mp3", validation_alias="DING_SOUND")
    floor_image: str = Field("wall.png", validation_alias="FLOOR_IMAGE")
    elevator_image: str = Field("elv.png", validation_alias="ELEVATOR_IMAGE")

    floor_width_img: int = Field(100, validation_alias="FLOOR_WIDTH_IMG")
    black_space_thickness: int = Field(7, validation_alias="BLACK_SPACE_THICKNESS")
    elevator_width: int = Field(60, validation_alias="ELEVATOR_WIDTH")
    stand_by_seconds: float = Field(2.0, validation_alias="STAND_BY_SECONDS")

    screen_min_width: int = Field(640, validation_alias="SCREEN_MIN_WIDTH")
    screen_min_height: int = Field(480, validation_alias="SCREEN_MIN_HEIGHT")
    screen_max_width: int = Field(1920, validation_alias="SCREEN_MAX_WIDTH")
    screen_max_height: int = Field(1080, validation_alias="SCREEN_MAX_HEIGHT")

    scroll_floors_threshold: int = Field(20, validation_alias="SCROLL_FLOORS_THRESHOLD")
    scroll_elevators_threshold: int = Field(
        4, validation_alias="SCROLL_ELEVATORS_THRESHOLD"
    )

    @model_validator(mode="after")
    def screen_bounds_valid(self) -> Settings:
        if self.screen_min_width > self.screen_max_width:
            raise ValueError("SCREEN_MIN_WIDTH must be <= SCREEN_MAX_WIDTH")
        if self.screen_min_height > self.screen_max_height:
            raise ValueError("SCREEN_MIN_HEIGHT must be <= SCREEN_MAX_HEIGHT")
        return self

    @property
    def media_dir(self) -> Path:
        return PROJECT_ROOT / self.assets_media_dir

    def media_path(self, filename: str) -> Path:
        return self.media_dir / filename

    @computed_field
    @property
    def floor_width(self) -> int:
        return self.floor_width_img

    @computed_field
    @property
    def floor_height_img(self) -> int:
        return ((self.floor_width_img // 3) * 2) - self.black_space_thickness

    @computed_field
    @property
    def floor_height(self) -> int:
        return self.floor_height_img + self.black_space_thickness

    @computed_field
    @property
    def timer_width(self) -> int:
        return self.floor_height

    @computed_field
    @property
    def floor_right_side(self) -> int:
        return self.timer_width + self.floor_width

    @computed_field
    @property
    def floor_width_position(self) -> int:
        return self.timer_width

    @computed_field
    @property
    def height_elevator(self) -> int:
        return self.floor_height
