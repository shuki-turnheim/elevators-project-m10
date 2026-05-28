from collections import deque
import time

import pygame as pg

from .media import MediaAssets
from .screen import ScreenLayout
from .settings import Settings
from .theme import Theme


class Elevator:
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
        self.screen_color = theme.screen_color
        self._media = media
        self._layout = layout
        self.width_position = 0
        self.position = 0
        self.current_location = 0

        self.que = deque()
        self.absolute_stop = 0
        self.departure = 0
        self.operation_duration = 0
        self.dst = 0
        self.in_travel = False
        self.stand_by = False
        self.stop_time = 0
        self.start_clock = 0

    def Recolor_screen(self, screen: pg.Surface) -> None:
        rect = pg.Rect(
            self.width_position,
            self.current_location,
            self._settings.elevator_width,
            self._settings.height_elevator,
        )
        screen.fill(self.screen_color, rect)

    def update_location(self, screen: pg.Surface) -> None:
        self.position = self.width_position, self.current_location
        self.Recolor_screen(screen)
        screen.blit(self._media.elevator_image, self.position)

    def build_elevator(self, num_elevator: int, screen: pg.Surface) -> None:
        layout = self._layout
        s = self._settings
        self.width_position = (
            num_elevator * s.elevator_width
            + s.floor_width
            + s.timer_width
            + layout.content_offset_x
        )
        world_bottom = layout.world_height - s.height_elevator
        self.height_position = world_bottom + layout.content_offset_y
        self.current_location = self.height_position
        self.update_location(screen)

    def arrival_time(self, dst: int) -> float:
        dst_distance = abs(self.absolute_stop - dst) / 2
        return self.operation_duration + dst_distance - self.elapsed_time()

    def send_order(self, dst: int) -> None:
        new_travel_duration = (
            abs(dst - self.absolute_stop) / 2 + self._settings.stand_by_seconds
        )
        self.operation_duration += new_travel_duration
        if not self.que:
            self.start_clock = time.time()
        self.que.append(dst)
        self.absolute_stop = self.que[-1]
        self.dst = self.que[0]
        if self.stop_time == 0:
            self.in_travel = True

    def elapsed_time(self) -> float:
        if self.start_clock != 0:
            return time.time() - self.start_clock
        return 0

    def find_direction(self, dest_y: int) -> float:
        return (dest_y - self.current_location) / abs(dest_y - self.current_location)

    def steps(self, dest_y: int) -> None:
        mov_direction = self.find_direction(dest_y)
        step_size = 2
        vector = mov_direction * step_size
        self.current_location += vector
        if dest_y != self.current_location and mov_direction != self.find_direction(dest_y):
            self.current_location = dest_y

    def travel(self, dest_y: int, screen: pg.Surface) -> None:
        if dest_y != self.current_location:
            self.steps(dest_y)
            self.Recolor_screen(screen)
            self.update_location(screen)
        else:
            self.stop_time = time.time()
            self.in_travel = False
            pg.mixer.music.load(self._media.ding_path)
            pg.mixer.music.play()

    def finish_order(self, dest_y: int, current_time: float) -> None:
        settings = self._settings
        if (
            dest_y == self.current_location
            and settings.stand_by_seconds
            <= current_time - self.stop_time
            < current_time
        ):
            self.stop_time = 0
            ended_travel_duration = (
                abs(self.departure - self.dst) / 2 + settings.stand_by_seconds
            )
            self.operation_duration -= ended_travel_duration
            self.departure = self.que.popleft()
            if self.que:
                self.dst = self.que[0]
                self.in_travel = True
                self.start_clock = time.time()
            else:
                self.start_clock = 0
