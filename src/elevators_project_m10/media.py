from __future__ import annotations
from dataclasses import dataclass

import pygame as pg

from elevators_project_m10.settings import Settings


@dataclass(frozen=True)
class MediaAssets:
    floor_image: pg.Surface
    elevator_image: pg.Surface
    ding_path: str

    @classmethod
    def load(cls, settings: Settings) -> MediaAssets:
        floor_img = pg.image.load(str(settings.media_path(settings.floor_image)))
        floor_surface = pg.transform.scale(
            floor_img, (settings.floor_width_img, settings.floor_height_img)
        )

        elevator_img = pg.image.load(str(settings.media_path(settings.elevator_image)))
        elevator_surface = pg.transform.scale(
            elevator_img, (settings.elevator_width, settings.height_elevator)
        )

        return cls(
            floor_image=floor_surface,
            elevator_image=elevator_surface,
            ding_path=str(settings.media_path(settings.ding_sound)),
        )
