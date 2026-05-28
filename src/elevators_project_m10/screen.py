from __future__ import annotations

import logging

import pygame as pg
from pydantic import BaseModel, model_validator

from .settings import Settings
from .theme import Theme

logger = logging.getLogger(__name__)


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


class ScreenLayout(BaseModel):
    world_width: int
    world_height: int
    viewport_width: int
    viewport_height: int
    content_offset_x: int
    content_offset_y: int
    needs_scroll_x: bool
    needs_scroll_y: bool

    @model_validator(mode="after")
    def viewport_fits_bounds(self) -> ScreenLayout:
        if self.viewport_width < 1 or self.viewport_height < 1:
            raise ValueError("viewport dimensions must be positive")
        return self

    @classmethod
    def from_building(
        cls,
        settings: Settings,
        elevators_count: int,
        floors_count: int,
    ) -> ScreenLayout:
        world_width = (
            elevators_count * settings.elevator_width
            + settings.floor_width
            + settings.timer_width
        )
        world_height = (
            floors_count * settings.floor_height - settings.black_space_thickness
        )

        viewport_width = _clamp(
            world_width, settings.screen_min_width, settings.screen_max_width
        )
        viewport_height = _clamp(
            world_height, settings.screen_min_height, settings.screen_max_height
        )

        needs_scroll_x = world_width > viewport_width
        needs_scroll_y = world_height > viewport_height

        content_offset_x = (
            0 if needs_scroll_x else (viewport_width - world_width) // 2
        )
        content_offset_y = (
            0 if needs_scroll_y else (viewport_height - world_height) // 2
        )

        layout = cls(
            world_width=world_width,
            world_height=world_height,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            content_offset_x=content_offset_x,
            content_offset_y=content_offset_y,
            needs_scroll_x=needs_scroll_x,
            needs_scroll_y=needs_scroll_y,
        )
        layout._warn_scroll_needed(settings, elevators_count, floors_count)
        return layout

    def _warn_scroll_needed(
        self,
        settings: Settings,
        elevators_count: int,
        floors_count: int,
    ) -> None:
        if not self.needs_scroll_x and not self.needs_scroll_y:
            return

        past_floor_threshold = floors_count > settings.scroll_floors_threshold
        past_elevator_threshold = elevators_count > settings.scroll_elevators_threshold
        if not (past_floor_threshold or past_elevator_threshold):
            return

        logger.warning(
            "Building size (%dx%d) exceeds viewport (%dx%d). "
            "Scrolling is not implemented yet (phase 2); content may be clipped. "
            "Raise SCREEN_MAX_WIDTH/SCREEN_MAX_HEIGHT in .env or reduce floors/elevators.",
            self.world_width,
            self.world_height,
            self.viewport_width,
            self.viewport_height,
        )

    def create_display(self, theme: Theme) -> pg.Surface:
        pg.init()
        screen = pg.display.set_mode((self.viewport_width, self.viewport_height))
        pg.display.set_caption("building_game")
        screen.fill(theme.screen_color)
        return screen
