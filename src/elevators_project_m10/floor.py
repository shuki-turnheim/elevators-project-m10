import time

import pygame as pg

from .media import MediaAssets
from .screen import ScreenLayout
from .settings import Settings
from .theme import Theme


class Floor:
    def __init__(
        self,
        number: int,
        settings: Settings,
        theme: Theme,
        media: MediaAssets,
        layout: ScreenLayout,
    ):
        self.number = number
        self._settings = settings
        self._theme = theme
        self._media = media
        self._layout = layout
        self.roof_position = None
        self.button = ()
        self.button_radius = ()

        self.time_left = 0.0
        self.made_order = False
        self.clock_position = 0
        self.timer_Rect = 0
        self.start_clock = 0

    def get_roof_position(self):
        return self.roof_position

    def design(self, num_floor: int, world_height: int) -> None:
        s = self._settings
        layout = self._layout
        ox = layout.content_offset_x
        oy = layout.content_offset_y

        self.roof_position = world_height - (num_floor + 1) * s.floor_height + oy
        width_button_position = s.floor_width_position + s.floor_width_img / 2 + ox
        height_button_position = (
            self.roof_position + s.black_space_thickness + s.floor_height_img / 2
        )
        self.button = width_button_position, height_button_position
        self.button_radius = s.floor_height_img // 2.5
        self.clock_position = (
            s.floor_width_img / 4 + ox,
            self.roof_position + s.black_space_thickness + s.floor_height_img / 4,
        )
        clock_rectangle_dimensions = (
            ox,
            self.roof_position + s.black_space_thickness,
            s.timer_width,
            s.floor_height_img,
        )
        self.timer_Rect = pg.Rect(clock_rectangle_dimensions)

    def drew_floor_number(self, screen: pg.Surface, color) -> None:
        font = pg.font.Font(None, int(self._settings.floor_height_img / 2))
        number = font.render(f"{self.number}", True, color)
        text_rect = number.get_rect()
        text_rect.center = self.button
        screen.blit(number, text_rect)

    def drew_button(self, screen: pg.Surface, called_by: int) -> None:
        t = self._theme
        if called_by in (t.builder, t.order_completed):
            color = t.button_default_color
            color_number = t.numbers_default_color
        else:
            color = t.button_on_hold_color
            color_number = t.numbers_on_hold_color
        pg.draw.circle(screen, color, self.button, self.button_radius)
        self.drew_floor_number(screen, color_number)

    def drew_roof(self, screen: pg.Surface) -> None:
        s = self._settings
        ox = self._layout.content_offset_x
        line_center = self.roof_position + s.black_space_thickness / 2
        line_left_position = [s.floor_width_position + ox, line_center]
        line_right_position = [s.floor_right_side + ox, line_center]
        pg.draw.line(
            screen,
            self._theme.black_space_color,
            line_left_position,
            line_right_position,
            s.black_space_thickness,
        )

    def build_floor(self, num_floor: int, screen: pg.Surface) -> None:
        s = self._settings
        ox = self._layout.content_offset_x
        self.design(num_floor, self._layout.world_height)
        screen.blit(
            self._media.floor_image,
            (
                s.floor_width_position + ox,
                self.roof_position + s.black_space_thickness,
            ),
        )
        self.drew_button(screen, self._theme.builder)
        self.drew_roof(screen)

    def draw_timer_display(self, screen: pg.Surface, turn_on: bool) -> None:
        s = self._settings
        t = self._theme
        if turn_on:
            pg.draw.rect(screen, t.black_space_color, self.timer_Rect)
            font = pg.font.Font(None, int(s.floor_height_img / 2))
            print_format = int(self.time_left * 10) / 10
            number = font.render(f"{print_format}", True, t.button_on_hold_color)
            screen.blit(number, self.clock_position)
        else:
            pg.draw.rect(screen, t.screen_color, self.timer_Rect)

    def permission_checker(self, elevator_at_floor) -> bool:
        if self.roof_position not in elevator_at_floor:
            self.made_order = True
            return True
        return False

    def request_in_process(self, arrival_time: float, screen: pg.Surface) -> None:
        self.time_left = arrival_time
        self.start_clock = time.time()
        self.drew_button(screen, self._theme.order)
        self.draw_timer_display(screen, True)

    def finished_order(self, screen: pg.Surface) -> None:
        self.made_order = False
        self.draw_timer_display(screen, False)
        self.drew_button(screen, self._theme.order_completed)

    def display_clock(self, screen: pg.Surface) -> None:
        if self.made_order:
            current_time = time.time()
            self.time_left -= current_time - self.start_clock
            self.start_clock = time.time()
            self.draw_timer_display(screen, True)
            if self.time_left <= 0.0:
                self.finished_order(screen)
